"""
Gmail OAuth 2.0 Client

This module provides a GmailClient class that handles Gmail OAuth 2.0 authentication
and Gmail API operations including fetching emails, sending emails, and marking emails as read.

Dependencies:
- google-auth
- google-auth-oauthlib  
- google-api-python-client

Usage:
    client = GmailClient(credentials_path="credentials.json", token_path="token.json")
    emails = client.fetch_unread_emails()
    success = client.send_email("recipient@example.com", "Subject", "Body")
    client.mark_as_read("email_id")
"""

import os
import json
import logging
import base64
import time
from typing import List, Dict, Optional, Any
from pathlib import Path

try:
    from google.auth.transport.requests import Request
    from google.oauth2.credentials import Credentials
    from google_auth_oauthlib.flow import InstalledAppFlow
    from googleapiclient.discovery import build
    from googleapiclient.errors import HttpError
    from email.mime.text import MIMEText
    from email.mime.multipart import MIMEMultipart
except ImportError as e:
    raise ImportError(
        f"Missing required Google API dependencies: {e}\n"
        "Install with: pip install google-auth google-auth-oauthlib google-api-python-client"
    )

# Import comprehensive error handling
from llmtoolkit.app.services.gmail_oauth_errors import (
    GmailOAuthError, GmailOAuthErrorType, GmailOAuthErrorHandler,
    create_credentials_error, create_network_error, create_rate_limit_error,
    create_auth_expired_error
)


class GmailAuthError(GmailOAuthError):
    """Exception raised for Gmail authentication errors (legacy compatibility)."""
    def __init__(self, message: str, original_error: Exception = None):
        super().__init__(
            error_type=GmailOAuthErrorType.UNKNOWN_ERROR,
            message=message,
            original_error=original_error
        )


class GmailAPIError(GmailOAuthError):
    """Exception raised for Gmail API operation errors (legacy compatibility)."""
    def __init__(self, message: str, original_error: Exception = None):
        super().__init__(
            error_type=GmailOAuthErrorType.GMAIL_API_ERROR,
            message=message,
            original_error=original_error
        )


class GmailClient:
    """
    Gmail OAuth 2.0 client for email operations.
    
    This class handles OAuth 2.0 authentication with Gmail and provides methods
    for fetching unread emails, sending emails, and marking emails as read.
    Includes comprehensive error handling with retry logic.
    """
    
    # Gmail API scopes
    SCOPES = [
        'https://www.googleapis.com/auth/gmail.readonly',
        'https://www.googleapis.com/auth/gmail.send',
        'https://www.googleapis.com/auth/gmail.modify'
    ]
    
    def __init__(self, credentials_path: str, token_path: str = "token.json"):
        """
        Initialize the Gmail client.
        
        Args:
            credentials_path: Path to the credentials.json file from Google Cloud Console
            token_path: Path to store/load the token.json file (default: "token.json")
        """
        self.logger = logging.getLogger("gmail_client")
        self.credentials_path = Path(credentials_path)
        self.token_path = Path(token_path)
        self.credentials: Optional[Credentials] = None
        self.service = None
        
        # Initialize error handler with retry logic
        self.error_handler = GmailOAuthErrorHandler()
        
        # Validate credentials file exists
        if not self.credentials_path.exists():
            raise create_credentials_error(
                str(credentials_path), 
                f"Credentials file not found: {credentials_path}"
            )
        
        # Validate credentials file format
        self._validate_credentials_file()
        
        self.logger.info(f"GmailClient initialized with credentials: {credentials_path}")
    
    def _validate_credentials_file(self) -> None:
        """Validate the credentials file format."""
        try:
            with open(self.credentials_path, 'r') as f:
                cred_data = json.load(f)
            
            # Check for required OAuth fields
            if 'installed' not in cred_data and 'web' not in cred_data:
                raise create_credentials_error(
                    str(self.credentials_path),
                    "Invalid credentials.json format - missing OAuth client configuration"
                )
            
            # Get client config
            client_config = cred_data.get('installed') or cred_data.get('web')
            if not client_config:
                raise create_credentials_error(
                    str(self.credentials_path),
                    "Invalid credentials.json format - no client configuration found"
                )
            
            # Check for required OAuth fields
            required_fields = ['client_id', 'client_secret']
            for field in required_fields:
                if field not in client_config:
                    raise create_credentials_error(
                        str(self.credentials_path),
                        f"Invalid credentials.json format - missing {field}"
                    )
                    
        except json.JSONDecodeError as e:
            raise create_credentials_error(
                str(self.credentials_path),
                f"Invalid credentials.json format - not valid JSON: {str(e)}"
            )
        except GmailOAuthError:
            raise  # Re-raise our custom errors
        except Exception as e:
            raise create_credentials_error(
                str(self.credentials_path),
                f"Error reading credentials file: {str(e)}"
            )
    
    def authenticate(self) -> bool:
        """
        Authenticate with Gmail using OAuth 2.0 with comprehensive error handling.
        
        Returns:
            True if authentication successful, False otherwise
            
        Raises:
            GmailOAuthError: If authentication fails with specific error type
        """
        operation_id = "gmail_authenticate"
        
        try:
            self.logger.info("Starting Gmail OAuth 2.0 authentication")
            
            # Load existing token if available
            if self.token_path.exists():
                self.logger.debug(f"Loading existing token from {self.token_path}")
                try:
                    self.credentials = Credentials.from_authorized_user_file(
                        str(self.token_path), self.SCOPES
                    )
                except Exception as e:
                    self.logger.warning(f"Failed to load existing token: {e}")
                    # Create error but don't raise - we'll try OAuth flow
                    error = self.error_handler.create_error_from_exception(
                        e, "Loading existing token"
                    )
                    self.logger.debug(f"Token loading error: {error.get_user_friendly_message()}")
            
            # If there are no valid credentials, run OAuth flow
            if not self.credentials or not self.credentials.valid:
                if self.credentials and self.credentials.expired and self.credentials.refresh_token:
                    self.logger.info("Refreshing expired credentials")
                    try:
                        self.credentials.refresh(Request())
                        self.logger.info("Credentials refreshed successfully")
                        self.error_handler.reset_retry_count(operation_id)
                    except Exception as e:
                        self.logger.warning(f"Failed to refresh credentials: {e}")
                        
                        # Create specific error for token refresh failure
                        refresh_error = GmailOAuthError(
                            error_type=GmailOAuthErrorType.TOKEN_REFRESH_FAILED,
                            message="Unable to refresh Gmail authentication",
                            details=f"Token refresh failed: {str(e)}",
                            original_error=e
                        )
                        
                        # Check if we should retry token refresh
                        if self.error_handler.should_retry(refresh_error, f"{operation_id}_refresh"):
                            self.error_handler.record_retry_attempt(f"{operation_id}_refresh")
                            delay = self.error_handler.get_retry_delay(refresh_error, f"{operation_id}_refresh")
                            self.logger.info(f"Retrying token refresh in {delay:.1f} seconds")
                            time.sleep(delay)
                            
                            try:
                                self.credentials.refresh(Request())
                                self.logger.info("Credentials refreshed successfully on retry")
                                self.error_handler.reset_retry_count(f"{operation_id}_refresh")
                            except Exception as retry_e:
                                self.logger.error(f"Token refresh retry failed: {retry_e}")
                                self.credentials = None
                        else:
                            self.credentials = None
                
                # Run OAuth flow if refresh failed or no credentials
                if not self.credentials or not self.credentials.valid:
                    self.logger.info("Running OAuth 2.0 flow")
                    try:
                        flow = InstalledAppFlow.from_client_secrets_file(
                            str(self.credentials_path), self.SCOPES
                        )
                        
                        # Use local server for OAuth callback
                        self.credentials = flow.run_local_server(
                            port=8080,
                            prompt='consent',
                            authorization_prompt_message='Please visit this URL to authorize the application: {url}',
                            success_message='The auth flow is complete; you may close this window.',
                            open_browser=True
                        )
                        self.logger.info("OAuth 2.0 flow completed successfully")
                        self.error_handler.reset_retry_count(operation_id)
                        
                    except Exception as e:
                        # Create specific OAuth flow error
                        oauth_error = self._create_oauth_flow_error(e)
                        self.logger.error(f"OAuth flow failed: {oauth_error.get_user_friendly_message()}")
                        raise oauth_error
            
            # Save credentials for future use
            self._save_credentials()
            
            # Build Gmail service
            try:
                self.service = build('gmail', 'v1', credentials=self.credentials)
                self.logger.info("Gmail service initialized successfully")
            except Exception as e:
                service_error = GmailOAuthError(
                    error_type=GmailOAuthErrorType.GMAIL_API_ERROR,
                    message="Failed to initialize Gmail service",
                    details=f"Service initialization error: {str(e)}",
                    original_error=e
                )
                self.logger.error(f"Service initialization failed: {service_error.get_user_friendly_message()}")
                raise service_error
            
            return True
            
        except GmailOAuthError:
            raise  # Re-raise our custom errors
        except Exception as e:
            # Create generic authentication error
            auth_error = self.error_handler.create_error_from_exception(
                e, "Gmail authentication"
            )
            self.logger.error(f"Gmail authentication failed: {auth_error.get_user_friendly_message()}")
            raise auth_error
    
    def _create_oauth_flow_error(self, exception: Exception) -> GmailOAuthError:
        """
        Create a specific OAuth flow error based on the exception.
        
        Args:
            exception: The original exception from OAuth flow
            
        Returns:
            GmailOAuthError with appropriate error type
        """
        exception_str = str(exception).lower()
        
        # Check for specific OAuth flow errors
        if "cancelled" in exception_str or "access_denied" in exception_str:
            return GmailOAuthError(
                error_type=GmailOAuthErrorType.OAUTH_FLOW_CANCELLED,
                message="Gmail authentication was cancelled",
                details="User cancelled the OAuth authorization process",
                original_error=exception
            )
        
        if "invalid_client" in exception_str:
            return GmailOAuthError(
                error_type=GmailOAuthErrorType.INVALID_CREDENTIALS,
                message="Invalid Gmail application credentials",
                details="OAuth client credentials are invalid or misconfigured",
                original_error=exception
            )
        
        if "redirect_uri" in exception_str:
            return GmailOAuthError(
                error_type=GmailOAuthErrorType.INVALID_REDIRECT_URI,
                message="Invalid OAuth redirect URI configuration",
                details="OAuth redirect URI is not properly configured",
                original_error=exception
            )
        
        if "scope" in exception_str:
            return GmailOAuthError(
                error_type=GmailOAuthErrorType.MISSING_OAUTH_SCOPES,
                message="Missing required OAuth scopes",
                details="OAuth configuration is missing required Gmail scopes",
                original_error=exception
            )
        
        # Default to generic OAuth error
        return self.error_handler.create_error_from_exception(
            exception, "OAuth flow"
        )
    
    def _create_api_error_from_http_error(self, http_error: HttpError, context: str) -> GmailOAuthError:
        """
        Create a specific API error from an HttpError.
        
        Args:
            http_error: The HttpError from Gmail API
            context: Context about when the error occurred
            
        Returns:
            GmailOAuthError with appropriate error type
        """
        status_code = http_error.resp.status
        error_content = str(http_error.content) if http_error.content else ""
        error_reason = getattr(http_error, 'reason', '')
        
        # Extract retry-after header for rate limiting
        retry_after = None
        if hasattr(http_error, 'resp') and hasattr(http_error.resp, 'headers'):
            retry_after_header = http_error.resp.headers.get('Retry-After')
            if retry_after_header:
                try:
                    retry_after = int(retry_after_header)
                except ValueError:
                    pass
        
        # Classify based on HTTP status code
        if status_code == 401:
            return GmailOAuthError(
                error_type=GmailOAuthErrorType.INVALID_TOKEN,
                message="Gmail authentication has expired",
                details=f"Authentication error during {context}: {error_reason}",
                original_error=http_error
            )
        
        elif status_code == 403:
            if "quota" in error_content.lower() or "limit" in error_content.lower():
                if "rate" in error_content.lower():
                    return GmailOAuthError(
                        error_type=GmailOAuthErrorType.RATE_LIMIT_EXCEEDED,
                        message="Gmail API rate limit exceeded",
                        details=f"Rate limit exceeded during {context}",
                        original_error=http_error,
                        retry_after=retry_after
                    )
                else:
                    return GmailOAuthError(
                        error_type=GmailOAuthErrorType.QUOTA_EXCEEDED,
                        message="Gmail API quota exceeded",
                        details=f"Quota exceeded during {context}",
                        original_error=http_error
                    )
            elif "permission" in error_content.lower() or "scope" in error_content.lower():
                return GmailOAuthError(
                    error_type=GmailOAuthErrorType.INSUFFICIENT_PERMISSIONS,
                    message="Insufficient permissions for Gmail access",
                    details=f"Permission denied during {context}: {error_reason}",
                    original_error=http_error
                )
            else:
                return GmailOAuthError(
                    error_type=GmailOAuthErrorType.GMAIL_API_ERROR,
                    message="Gmail API access forbidden",
                    details=f"Access forbidden during {context}: {error_reason}",
                    original_error=http_error
                )
        
        elif status_code == 404:
            return GmailOAuthError(
                error_type=GmailOAuthErrorType.GMAIL_API_ERROR,
                message="Gmail resource not found",
                details=f"Resource not found during {context}: {error_reason}",
                original_error=http_error
            )
        
        elif status_code == 429:
            return GmailOAuthError(
                error_type=GmailOAuthErrorType.RATE_LIMIT_EXCEEDED,
                message="Gmail API rate limit exceeded",
                details=f"Too many requests during {context}",
                original_error=http_error,
                retry_after=retry_after
            )
        
        elif 500 <= status_code < 600:
            return GmailOAuthError(
                error_type=GmailOAuthErrorType.GOOGLE_SERVER_ERROR,
                message="Gmail servers are experiencing issues",
                details=f"Server error ({status_code}) during {context}: {error_reason}",
                original_error=http_error
            )
        
        # Default to generic API error
        return GmailOAuthError(
            error_type=GmailOAuthErrorType.GMAIL_API_ERROR,
            message=f"Gmail API error during {context}",
            details=f"HTTP {status_code}: {error_reason}",
            original_error=http_error,
            error_code=str(status_code)
        )
    
    def _save_credentials(self) -> None:
        """Save credentials to token file."""
        try:
            with open(self.token_path, 'w') as token_file:
                token_file.write(self.credentials.to_json())
            self.logger.debug(f"Credentials saved to {self.token_path}")
        except Exception as e:
            self.logger.error(f"Failed to save credentials: {e}")
    
    def _ensure_authenticated(self) -> None:
        """Ensure the client is authenticated before API calls."""
        if not self.service or not self.credentials or not self.credentials.valid:
            if not self.authenticate():
                raise GmailAuthError("Failed to authenticate with Gmail")
    
    def fetch_unread_emails(self, max_results: int = 10) -> List[Dict[str, Any]]:
        """
        Fetch unread emails from Gmail with comprehensive error handling and retry logic.
        
        Args:
            max_results: Maximum number of emails to fetch (default: 10)
            
        Returns:
            List of email dictionaries with keys: id, subject, sender, body, timestamp
            
        Raises:
            GmailOAuthError: If API call fails with specific error type
        """
        operation_id = "fetch_unread_emails"
        
        def _perform_fetch():
            self._ensure_authenticated()
            self.logger.info(f"Fetching up to {max_results} unread emails")
            
            # Search for unread emails
            results = self.service.users().messages().list(
                userId='me',
                q='is:unread',
                maxResults=max_results
            ).execute()
            
            messages = results.get('messages', [])
            self.logger.info(f"Found {len(messages)} unread emails")
            
            emails = []
            for message in messages:
                try:
                    # Get full message details with individual error handling
                    msg = self.service.users().messages().get(
                        userId='me',
                        id=message['id'],
                        format='full'
                    ).execute()
                    
                    # Extract email data
                    email_data = self._parse_email_message(msg)
                    emails.append(email_data)
                    
                except HttpError as e:
                    # Handle individual email fetch errors
                    error = self._create_api_error_from_http_error(e, f"fetching email {message['id']}")
                    self.logger.warning(f"Failed to fetch email {message['id']}: {error.get_user_friendly_message()}")
                    continue
                except Exception as e:
                    self.logger.warning(f"Unexpected error fetching email {message['id']}: {e}")
                    continue
            
            self.logger.info(f"Successfully fetched {len(emails)} emails")
            return emails
        
        # Implement retry logic for the entire operation
        while True:
            try:
                result = _perform_fetch()
                self.error_handler.reset_retry_count(operation_id)
                return result
                
            except HttpError as e:
                # Create specific API error
                api_error = self._create_api_error_from_http_error(e, "fetching unread emails")
                
                # Check if we should retry
                if self.error_handler.should_retry(api_error, operation_id):
                    self.error_handler.record_retry_attempt(operation_id)
                    delay = self.error_handler.get_retry_delay(api_error, operation_id)
                    self.logger.info(f"Retrying email fetch in {delay:.1f} seconds due to: {api_error.get_user_friendly_message()}")
                    time.sleep(delay)
                    continue
                else:
                    self.logger.error(f"Gmail API error fetching emails: {api_error.get_user_friendly_message()}")
                    raise api_error
                    
            except GmailOAuthError as e:
                # Check if we should retry OAuth errors
                if self.error_handler.should_retry(e, operation_id):
                    self.error_handler.record_retry_attempt(operation_id)
                    delay = self.error_handler.get_retry_delay(e, operation_id)
                    self.logger.info(f"Retrying email fetch in {delay:.1f} seconds due to: {e.get_user_friendly_message()}")
                    time.sleep(delay)
                    continue
                else:
                    self.logger.error(f"OAuth error fetching emails: {e.get_user_friendly_message()}")
                    raise e
                    
            except Exception as e:
                # Create generic error
                generic_error = self.error_handler.create_error_from_exception(
                    e, "fetching unread emails"
                )
                self.logger.error(f"Unexpected error fetching emails: {generic_error.get_user_friendly_message()}")
                raise generic_error
    
    def _parse_email_message(self, message: Dict) -> Dict[str, Any]:
        """
        Parse Gmail API message into a simplified email dictionary.
        
        Args:
            message: Gmail API message object
            
        Returns:
            Dictionary with email data
        """
        headers = {h['name']: h['value'] for h in message['payload'].get('headers', [])}
        
        # Extract body text
        body = self._extract_email_body(message['payload'])
        
        # Create email data dictionary
        email_data = {
            'id': message['id'],
            'thread_id': message['threadId'],
            'subject': headers.get('Subject', 'No Subject'),
            'sender': headers.get('From', 'Unknown Sender'),
            'to': headers.get('To', ''),
            'date': headers.get('Date', ''),
            'body': body,
            'snippet': message.get('snippet', ''),
            'unread': 'UNREAD' in message.get('labelIds', []),
            'timestamp': message.get('internalDate', '0')
        }
        
        return email_data
    
    def _extract_email_body(self, payload: Dict) -> str:
        """
        Extract email body text from Gmail API payload.
        
        Args:
            payload: Gmail API message payload
            
        Returns:
            Email body text
        """
        body = ""
        
        if 'parts' in payload:
            # Multi-part message
            for part in payload['parts']:
                if part['mimeType'] == 'text/plain':
                    data = part['body'].get('data', '')
                    if data:
                        body = base64.urlsafe_b64decode(data).decode('utf-8')
                        break
                elif part['mimeType'] == 'text/html' and not body:
                    # Fallback to HTML if no plain text
                    data = part['body'].get('data', '')
                    if data:
                        body = base64.urlsafe_b64decode(data).decode('utf-8')
        else:
            # Single part message
            if payload['mimeType'] in ['text/plain', 'text/html']:
                data = payload['body'].get('data', '')
                if data:
                    body = base64.urlsafe_b64decode(data).decode('utf-8')
        
        return body.strip()
    
    def send_email(self, to: str, subject: str, body: str, from_email: str = None) -> bool:
        """
        Send an email using Gmail API with comprehensive error handling and retry logic.
        
        Args:
            to: Recipient email address
            subject: Email subject
            body: Email body content
            from_email: Sender email (optional, uses authenticated user's email)
            
        Returns:
            True if email sent successfully, False otherwise
            
        Raises:
            GmailOAuthError: If API call fails with specific error type
        """
        operation_id = f"send_email_{to}"
        
        def _perform_send():
            self._ensure_authenticated()
            self.logger.info(f"Sending email to {to} with subject: {subject}")
            
            # Create message
            message = MIMEText(body)
            message['to'] = to
            message['subject'] = subject
            if from_email:
                message['from'] = from_email
            
            # Encode message
            raw_message = base64.urlsafe_b64encode(message.as_bytes()).decode('utf-8')
            
            # Send email
            send_result = self.service.users().messages().send(
                userId='me',
                body={'raw': raw_message}
            ).execute()
            
            message_id = send_result.get('id')
            self.logger.info(f"Email sent successfully with ID: {message_id}")
            return True
        
        # Implement retry logic for email sending
        while True:
            try:
                result = _perform_send()
                self.error_handler.reset_retry_count(operation_id)
                return result
                
            except HttpError as e:
                # Create specific API error
                api_error = self._create_api_error_from_http_error(e, f"sending email to {to}")
                
                # Check if we should retry
                if self.error_handler.should_retry(api_error, operation_id):
                    self.error_handler.record_retry_attempt(operation_id)
                    delay = self.error_handler.get_retry_delay(api_error, operation_id)
                    self.logger.info(f"Retrying email send in {delay:.1f} seconds due to: {api_error.get_user_friendly_message()}")
                    time.sleep(delay)
                    continue
                else:
                    self.logger.error(f"Gmail API error sending email: {api_error.get_user_friendly_message()}")
                    raise api_error
                    
            except GmailOAuthError as e:
                # Check if we should retry OAuth errors
                if self.error_handler.should_retry(e, operation_id):
                    self.error_handler.record_retry_attempt(operation_id)
                    delay = self.error_handler.get_retry_delay(e, operation_id)
                    self.logger.info(f"Retrying email send in {delay:.1f} seconds due to: {e.get_user_friendly_message()}")
                    time.sleep(delay)
                    continue
                else:
                    self.logger.error(f"OAuth error sending email: {e.get_user_friendly_message()}")
                    raise e
                    
            except Exception as e:
                # Create generic error
                generic_error = self.error_handler.create_error_from_exception(
                    e, f"sending email to {to}"
                )
                self.logger.error(f"Unexpected error sending email: {generic_error.get_user_friendly_message()}")
                raise generic_error
    
    def mark_as_read(self, email_id: str) -> bool:
        """
        Mark an email as read with comprehensive error handling and retry logic.
        
        Args:
            email_id: Gmail message ID
            
        Returns:
            True if marked as read successfully, False otherwise
            
        Raises:
            GmailOAuthError: If API call fails with specific error type
        """
        operation_id = f"mark_as_read_{email_id}"
        
        def _perform_mark_read():
            self._ensure_authenticated()
            self.logger.info(f"Marking email {email_id} as read")
            
            # Remove UNREAD label
            self.service.users().messages().modify(
                userId='me',
                id=email_id,
                body={'removeLabelIds': ['UNREAD']}
            ).execute()
            
            self.logger.info(f"Email {email_id} marked as read successfully")
            return True
        
        # Implement retry logic for marking as read
        while True:
            try:
                result = _perform_mark_read()
                self.error_handler.reset_retry_count(operation_id)
                return result
                
            except HttpError as e:
                # Create specific API error
                api_error = self._create_api_error_from_http_error(e, f"marking email {email_id} as read")
                
                # Check if we should retry
                if self.error_handler.should_retry(api_error, operation_id):
                    self.error_handler.record_retry_attempt(operation_id)
                    delay = self.error_handler.get_retry_delay(api_error, operation_id)
                    self.logger.info(f"Retrying mark as read in {delay:.1f} seconds due to: {api_error.get_user_friendly_message()}")
                    time.sleep(delay)
                    continue
                else:
                    self.logger.error(f"Gmail API error marking email as read: {api_error.get_user_friendly_message()}")
                    raise api_error
                    
            except GmailOAuthError as e:
                # Check if we should retry OAuth errors
                if self.error_handler.should_retry(e, operation_id):
                    self.error_handler.record_retry_attempt(operation_id)
                    delay = self.error_handler.get_retry_delay(e, operation_id)
                    self.logger.info(f"Retrying mark as read in {delay:.1f} seconds due to: {e.get_user_friendly_message()}")
                    time.sleep(delay)
                    continue
                else:
                    self.logger.error(f"OAuth error marking email as read: {e.get_user_friendly_message()}")
                    raise e
                    
            except Exception as e:
                # Create generic error
                generic_error = self.error_handler.create_error_from_exception(
                    e, f"marking email {email_id} as read"
                )
                self.logger.error(f"Unexpected error marking email as read: {generic_error.get_user_friendly_message()}")
                raise generic_error
    
    def get_user_profile(self) -> Dict[str, Any]:
        """
        Get the authenticated user's Gmail profile.
        
        Returns:
            Dictionary with user profile information
            
        Raises:
            GmailAPIError: If API call fails
        """
        try:
            self._ensure_authenticated()
            self.logger.info("Fetching user profile")
            
            profile = self.service.users().getProfile(userId='me').execute()
            
            self.logger.info(f"User profile fetched: {profile.get('emailAddress', 'Unknown')}")
            return profile
            
        except HttpError as e:
            self.logger.error(f"Gmail API error fetching profile: {e}")
            raise GmailAPIError(f"Failed to fetch profile: {str(e)}")
        except Exception as e:
            self.logger.error(f"Unexpected error fetching profile: {e}")
            raise GmailAPIError(f"Unexpected error: {str(e)}")
    
    def test_connection(self) -> Dict[str, Any]:
        """
        Test the Gmail connection and return status information.
        
        Returns:
            Dictionary with connection test results
        """
        try:
            self.logger.info("Testing Gmail connection")
            
            # Authenticate
            if not self.authenticate():
                return {
                    'success': False,
                    'error': 'Authentication failed',
                    'details': 'Could not authenticate with Gmail'
                }
            
            # Get user profile to test API access
            profile = self.get_user_profile()
            
            return {
                'success': True,
                'email_address': profile.get('emailAddress', 'Unknown'),
                'messages_total': profile.get('messagesTotal', 0),
                'threads_total': profile.get('threadsTotal', 0),
                'history_id': profile.get('historyId', 'Unknown')
            }
            
        except Exception as e:
            self.logger.error(f"Connection test failed: {e}")
            return {
                'success': False,
                'error': str(e),
                'details': 'Gmail connection test failed'
            }
    
    def add_label(self, email_id: str, label_name: str) -> bool:
        """
        Add a label to an email.
        
        Args:
            email_id: Gmail message ID
            label_name: Name of the label to add
            
        Returns:
            True if label added successfully, False otherwise
            
        Raises:
            GmailAPIError: If API call fails
        """
        try:
            self._ensure_authenticated()
            self.logger.info(f"Adding label '{label_name}' to email {email_id}")
            
            # Get or create label ID
            label_id = self._get_or_create_label_id(label_name)
            if not label_id:
                raise GmailAPIError(f"Failed to get or create label: {label_name}")
            
            # Add label to message
            self.service.users().messages().modify(
                userId='me',
                id=email_id,
                body={'addLabelIds': [label_id]}
            ).execute()
            
            self.logger.info(f"Label '{label_name}' added to email {email_id} successfully")
            return True
            
        except HttpError as e:
            self.logger.error(f"Gmail API error adding label: {e}")
            raise GmailAPIError(f"Failed to add label: {str(e)}")
        except Exception as e:
            self.logger.error(f"Unexpected error adding label: {e}")
            raise GmailAPIError(f"Unexpected error: {str(e)}")
    
    def remove_label(self, email_id: str, label_name: str) -> bool:
        """
        Remove a label from an email.
        
        Args:
            email_id: Gmail message ID
            label_name: Name of the label to remove
            
        Returns:
            True if label removed successfully, False otherwise
            
        Raises:
            GmailAPIError: If API call fails
        """
        try:
            self._ensure_authenticated()
            self.logger.info(f"Removing label '{label_name}' from email {email_id}")
            
            # Get label ID
            label_id = self._get_label_id(label_name)
            if not label_id:
                self.logger.warning(f"Label '{label_name}' not found, cannot remove")
                return True  # Consider it successful if label doesn't exist
            
            # Remove label from message
            self.service.users().messages().modify(
                userId='me',
                id=email_id,
                body={'removeLabelIds': [label_id]}
            ).execute()
            
            self.logger.info(f"Label '{label_name}' removed from email {email_id} successfully")
            return True
            
        except HttpError as e:
            self.logger.error(f"Gmail API error removing label: {e}")
            raise GmailAPIError(f"Failed to remove label: {str(e)}")
        except Exception as e:
            self.logger.error(f"Unexpected error removing label: {e}")
            raise GmailAPIError(f"Unexpected error: {str(e)}")
    
    def _get_label_id(self, label_name: str) -> Optional[str]:
        """
        Get the ID of a label by name.
        
        Args:
            label_name: Name of the label
            
        Returns:
            Label ID if found, None otherwise
        """
        try:
            # Get all labels
            results = self.service.users().labels().list(userId='me').execute()
            labels = results.get('labels', [])
            
            # Find label by name
            for label in labels:
                if label['name'] == label_name:
                    return label['id']
            
            return None
            
        except Exception as e:
            self.logger.error(f"Error getting label ID for '{label_name}': {e}")
            return None
    
    def _get_or_create_label_id(self, label_name: str) -> Optional[str]:
        """
        Get the ID of a label by name, creating it if it doesn't exist.
        
        Args:
            label_name: Name of the label
            
        Returns:
            Label ID if found or created, None if creation failed
        """
        try:
            # First try to get existing label
            label_id = self._get_label_id(label_name)
            if label_id:
                return label_id
            
            # Create new label if it doesn't exist
            self.logger.info(f"Creating new label: {label_name}")
            
            label_object = {
                'name': label_name,
                'messageListVisibility': 'show',
                'labelListVisibility': 'labelShow'
            }
            
            created_label = self.service.users().labels().create(
                userId='me',
                body=label_object
            ).execute()
            
            label_id = created_label['id']
            self.logger.info(f"Created new label '{label_name}' with ID: {label_id}")
            return label_id
            
        except HttpError as e:
            self.logger.error(f"Gmail API error creating label '{label_name}': {e}")
            return None
        except Exception as e:
            self.logger.error(f"Unexpected error creating label '{label_name}': {e}")
            return None
    
    def get_labels(self) -> List[Dict[str, Any]]:
        """
        Get all labels for the authenticated user.
        
        Returns:
            List of label dictionaries
            
        Raises:
            GmailAPIError: If API call fails
        """
        try:
            self._ensure_authenticated()
            self.logger.info("Fetching user labels")
            
            results = self.service.users().labels().list(userId='me').execute()
            labels = results.get('labels', [])
            
            self.logger.info(f"Found {len(labels)} labels")
            return labels
            
        except HttpError as e:
            self.logger.error(f"Gmail API error fetching labels: {e}")
            raise GmailAPIError(f"Failed to fetch labels: {str(e)}")
        except Exception as e:
            self.logger.error(f"Unexpected error fetching labels: {e}")
            raise GmailAPIError(f"Unexpected error: {str(e)}")
    
    def batch_modify_messages(self, email_ids: List[str], add_labels: List[str] = None, remove_labels: List[str] = None) -> bool:
        """
        Batch modify multiple messages with label operations.
        
        Args:
            email_ids: List of Gmail message IDs
            add_labels: List of label names to add (optional)
            remove_labels: List of label names to remove (optional)
            
        Returns:
            True if batch operation successful, False otherwise
            
        Raises:
            GmailAPIError: If API call fails
        """
        try:
            self._ensure_authenticated()
            
            if not email_ids:
                return True
            
            add_label_ids = []
            remove_label_ids = []
            
            # Convert label names to IDs
            if add_labels:
                for label_name in add_labels:
                    label_id = self._get_or_create_label_id(label_name)
                    if label_id:
                        add_label_ids.append(label_id)
            
            if remove_labels:
                for label_name in remove_labels:
                    label_id = self._get_label_id(label_name)
                    if label_id:
                        remove_label_ids.append(label_id)
            
            # Prepare batch modify request
            body = {
                'ids': email_ids
            }
            
            if add_label_ids:
                body['addLabelIds'] = add_label_ids
            
            if remove_label_ids:
                body['removeLabelIds'] = remove_label_ids
            
            self.logger.info(f"Batch modifying {len(email_ids)} messages")
            
            # Execute batch modify
            self.service.users().messages().batchModify(
                userId='me',
                body=body
            ).execute()
            
            self.logger.info(f"Batch modify completed for {len(email_ids)} messages")
            return True
            
        except HttpError as e:
            self.logger.error(f"Gmail API error in batch modify: {e}")
            raise GmailAPIError(f"Failed to batch modify messages: {str(e)}")
        except Exception as e:
            self.logger.error(f"Unexpected error in batch modify: {e}")
            raise GmailAPIError(f"Unexpected error: {str(e)}")


# Example usage and testing
if __name__ == "__main__":
    # Set up logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    # Example usage (requires credentials.json file)
    try:
        # Initialize client
        client = GmailClient("credentials.json", "token.json")
        
        # Test connection
        test_result = client.test_connection()
        print(f"Connection test: {test_result}")
        
        if test_result['success']:
            # Fetch unread emails
            emails = client.fetch_unread_emails(max_results=5)
            print(f"Found {len(emails)} unread emails")
            
            for email in emails:
                print(f"- {email['subject']} from {email['sender']}")
            
            # Example: Send a test email (uncomment to test)
            # success = client.send_email(
            #     to="test@example.com",
            #     subject="Test Email from Gmail API",
            #     body="This is a test email sent using the Gmail API."
            # )
            # print(f"Email sent: {success}")
            
            # Example: Mark first email as read (uncomment to test)
            # if emails:
            #     success = client.mark_as_read(emails[0]['id'])
            #     print(f"Email marked as read: {success}")
        
    except Exception as e:
        print(f"Error: {e}")