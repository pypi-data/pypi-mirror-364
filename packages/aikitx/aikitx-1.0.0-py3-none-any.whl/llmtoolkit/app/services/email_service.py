"""
Email Service

Manages email operations including SMTP configuration, email sending,
and AI-powered email generation. Integrates with ModelService for
intelligent email composition and reply generation. Supports both SMTP
and Gmail OAuth 2.0 authentication methods.
"""

import logging
import smtplib
import os
import time
import json
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from typing import Dict, Any, Optional, List
from pathlib import Path
from datetime import datetime, timedelta

from llmtoolkit.app.core.event_bus import EventBus

# Gmail OAuth imports (optional - will be imported when needed)
try:
    from llmtoolkit.app.services.gmail_client import GmailClient, GmailAuthError, GmailAPIError
    from llmtoolkit.app.services.gmail_oauth_errors import (
        GmailOAuthError, GmailOAuthErrorType, GmailOAuthErrorHandler,
        create_credentials_error, create_network_error, create_rate_limit_error,
        create_auth_expired_error
    )
    GMAIL_AVAILABLE = True
except ImportError:
    GMAIL_AVAILABLE = False
    GmailClient = None
    GmailAuthError = Exception
    GmailAPIError = Exception
    GmailOAuthError = Exception
    GmailOAuthErrorType = None
    GmailOAuthErrorHandler = None

# Secure storage imports (optional - will be imported when needed)
try:
    from llmtoolkit.app.utils.secure_storage import SecureStorage, SecureStorageError
    SECURE_STORAGE_AVAILABLE = True
except ImportError:
    SECURE_STORAGE_AVAILABLE = False
    SecureStorage = None
    SecureStorageError = Exception


class EmailAuthError(Exception):
    """Exception raised for email authentication errors."""
    pass


class EmailConfigError(Exception):
    """Exception raised for email configuration errors."""
    pass


class EmailService:
    """Service for managing email operations and AI-powered email generation."""
    
    def __init__(self, event_bus: EventBus = None, config_manager=None, model_service=None):
        """
        Initialize the email service.
        
        Args:
            event_bus: EventBus instance for communication
            config_manager: Configuration manager for settings
            model_service: ModelService instance for AI text generation
        """
        self.logger = logging.getLogger("gguf_loader.email_service")
        self.event_bus = event_bus
        self.config_manager = config_manager
        self.model_service = model_service
        
        # Email configuration storage
        self.email_config: Dict[str, Any] = {}
        
        # Authentication method: "smtp" or "gmail_oauth"
        self.auth_method: str = "smtp"
        
        # Gmail OAuth client (initialized when needed)
        self.gmail_client: Optional[GmailClient] = None
        
        # Email caching for Gmail API
        self._email_cache: Dict[str, Any] = {}
        self._cache_expiry_minutes = 5  # Cache emails for 5 minutes
        self._last_fetch_time: Optional[datetime] = None
        self._rate_limit_delay = 1.0  # Minimum delay between API calls (seconds)
        self._last_api_call_time: Optional[datetime] = None
        
        # Default SMTP settings
        self.default_smtp_port = 587
        self.default_use_tls = True
        self.default_use_ssl = False
        
        # Subscribe to events if event bus is available
        if self.event_bus:
            self.event_bus.subscribe("email.config_changed", self._on_config_changed)
            self.event_bus.subscribe("email.send_request", self._on_send_request)
        
        # Load existing configuration if available
        self._load_email_config()
        
        self.logger.info("EmailService initialized")
    
    def authenticate_gmail_oauth(self, credentials_path: str, token_path: str = "token.json") -> tuple[bool, str]:
        """
        Authenticate with Gmail using OAuth 2.0 with comprehensive error handling.
        
        Args:
            credentials_path: Path to credentials.json file
            token_path: Path to store/load token.json file
            
        Returns:
            Tuple of (success, user_friendly_message)
        """
        try:
            if not GMAIL_AVAILABLE:
                error_msg = "Gmail OAuth not available. Please install required dependencies: google-auth, google-auth-oauthlib, google-api-python-client"
                self.logger.error(error_msg)
                return False, error_msg
            
            self.logger.info(f"Authenticating Gmail OAuth with credentials: {credentials_path}")
            
            # Initialize Gmail client (this will validate credentials file)
            self.gmail_client = GmailClient(credentials_path, token_path)
            
            # Authenticate with comprehensive error handling
            if self.gmail_client.authenticate():
                # Update authentication method
                self.auth_method = "gmail_oauth"
                
                # Get user profile to verify authentication
                profile = self.gmail_client.get_user_profile()
                oauth_email = profile.get('emailAddress', 'Unknown')
                
                # Update email configuration
                self.email_config.update({
                    'auth_method': 'gmail_oauth',
                    'credentials_path': credentials_path,
                    'token_path': token_path,
                    'oauth_email': oauth_email,
                    'oauth_authenticated': True
                })
                
                success_msg = f"Gmail OAuth authentication successful for {oauth_email}"
                self.logger.info(success_msg)
                return True, success_msg
            else:
                error_msg = "Gmail OAuth authentication failed"
                self.logger.error(error_msg)
                return False, error_msg
                
        except GmailOAuthError as e:
            # Use the comprehensive error handling
            user_friendly_msg = e.get_user_friendly_message()
            self.logger.error(f"Gmail OAuth error: {user_friendly_msg}")
            
            # Log detailed error information for debugging
            if GMAIL_AVAILABLE and GmailOAuthErrorHandler:
                error_handler = GmailOAuthErrorHandler()
                error_report = error_handler.create_error_report(e)
                self.logger.debug(f"Detailed error report: {error_report}")
            
            return False, user_friendly_msg
            
        except GmailAuthError as e:
            # Handle legacy errors
            error_msg = f"Gmail authentication error: {str(e)}"
            self.logger.error(error_msg)
            return False, error_msg
            
        except Exception as e:
            # Create comprehensive error from generic exception
            if GMAIL_AVAILABLE and GmailOAuthErrorHandler:
                error_handler = GmailOAuthErrorHandler()
                oauth_error = error_handler.create_error_from_exception(e, "Gmail OAuth authentication")
                user_friendly_msg = oauth_error.get_user_friendly_message()
                self.logger.error(f"Unexpected error during Gmail authentication: {user_friendly_msg}")
                return False, user_friendly_msg
            else:
                error_msg = f"Unexpected error during Gmail authentication: {str(e)}"
                self.logger.error(error_msg)
                return False, error_msg
    
    def test_gmail_connection(self) -> dict:
        """
        Test Gmail OAuth connection.
        
        Returns:
            Dictionary with test results
        """
        try:
            if not GMAIL_AVAILABLE:
                return {
                    'success': False,
                    'error': 'Gmail OAuth not available',
                    'details': 'Please install required dependencies: google-auth, google-auth-oauthlib, google-api-python-client'
                }
            
            if not self.gmail_client:
                return {
                    'success': False,
                    'error': 'Gmail client not initialized',
                    'details': 'Please authenticate with Gmail OAuth first'
                }
            
            self.logger.info("Testing Gmail connection")
            return self.gmail_client.test_connection()
            
        except Exception as e:
            self.logger.error(f"Error testing Gmail connection: {e}")
            return {
                'success': False,
                'error': str(e),
                'details': 'Gmail connection test failed'
            }
    
    def _determine_send_method(self) -> str:
        """
        Determine which email sending method to use.
        
        Returns:
            "gmail_api" or "smtp"
        """
        if (self.auth_method == "gmail_oauth" and 
            self.gmail_client and 
            self.email_config.get('oauth_authenticated', False)):
            return "gmail_api"
        else:
            return "smtp"
    
    def _send_via_gmail_api(self, to: str, subject: str, body: str) -> bool:
        """
        Send email using Gmail API.
        
        Args:
            to: Recipient email address
            subject: Email subject
            body: Email body content
            
        Returns:
            True if email was sent successfully, False otherwise
        """
        try:
            if not self.gmail_client:
                self.logger.error("Gmail client not initialized")
                return False
            
            self.logger.info(f"Sending email via Gmail API to {to}")
            
            # Send email using Gmail client
            success = self.gmail_client.send_email(to, subject, body)
            
            if success:
                self.logger.info(f"Email sent successfully via Gmail API to {to}")
                
                # Publish successful email sent event
                if self.event_bus:
                    import datetime
                    self.event_bus.publish("email.sent", {
                        "to": to,
                        "subject": subject,
                        "body_length": len(body),
                        "method": "gmail_api",
                        "timestamp": datetime.datetime.now().isoformat(),
                        "success": True
                    })
                
                return True
            else:
                self.logger.error(f"Failed to send email via Gmail API to {to}")
                return False
                
        except GmailAPIError as e:
            self.logger.error(f"Gmail API error sending email: {e}")
            
            # Publish email send error event
            if self.event_bus:
                self.event_bus.publish("email.send_error", {
                    "to": to,
                    "subject": subject,
                    "error": f"Gmail API error: {str(e)}",
                    "method": "gmail_api"
                })
            
            return False
        except Exception as e:
            self.logger.error(f"Unexpected error sending email via Gmail API: {e}")
            
            # Publish email send error event
            if self.event_bus:
                self.event_bus.publish("email.send_error", {
                    "to": to,
                    "subject": subject,
                    "error": f"Unexpected error: {str(e)}",
                    "method": "gmail_api"
                })
            
            return False
    
    def _load_email_config(self) -> None:
        """Load email configuration from config manager with support for both authentication types."""
        if self.config_manager:
            try:
                self.email_config = self.config_manager.get_value("email_config", {})
                
                # Migrate configuration if needed
                if self.email_config:
                    self.email_config = self._migrate_config_if_needed(self.email_config)
                
                # Load authentication method
                self.auth_method = self.email_config.get('auth_method', 'smtp')
                
                # Validate and handle configuration based on authentication method
                if self.auth_method == 'gmail_oauth':
                    self._handle_gmail_oauth_config_loading()
                elif self.auth_method == 'smtp':
                    self._handle_smtp_config_loading()
                
                self.logger.info(f"Email configuration loaded from config manager (auth method: {self.auth_method})")
            except Exception as e:
                self.logger.warning(f"Failed to load email configuration: {e}")
                self.email_config = {}
                self.auth_method = 'smtp'  # Fallback to SMTP
    
    def _handle_gmail_oauth_config_loading(self) -> None:
        """Handle Gmail OAuth configuration loading with validation and token refresh."""
        try:
            # Validate Gmail OAuth configuration
            is_valid, validation_message = self._validate_gmail_oauth_config(self.email_config)
            
            if not is_valid:
                self.logger.warning(f"Invalid Gmail OAuth configuration: {validation_message}")
                self._fallback_to_smtp("Invalid Gmail OAuth configuration")
                return
            
            # Load secure tokens if available
            if SECURE_STORAGE_AVAILABLE:
                self._load_secure_oauth_tokens()
            
            # Attempt to initialize Gmail client and refresh tokens if needed
            if self._initialize_gmail_client_with_refresh():
                self.logger.info("Gmail OAuth configuration loaded and validated successfully")
            else:
                self.logger.warning("Failed to initialize Gmail client, falling back to SMTP")
                self._fallback_to_smtp("Gmail client initialization failed")
                
        except Exception as e:
            self.logger.error(f"Error handling Gmail OAuth configuration: {e}")
            self._fallback_to_smtp(f"Gmail OAuth error: {str(e)}")
    
    def _handle_smtp_config_loading(self) -> None:
        """Handle SMTP configuration loading with validation."""
        try:
            # Validate SMTP configuration
            is_valid, validation_message = self.validate_smtp_config(self.email_config)
            
            if not is_valid:
                self.logger.warning(f"Invalid SMTP configuration: {validation_message}")
                # Don't fallback for SMTP - just log the warning
                # User will need to reconfigure SMTP settings
            else:
                self.logger.info("SMTP configuration loaded and validated successfully")
                
        except Exception as e:
            self.logger.error(f"Error handling SMTP configuration: {e}")
    
    def _initialize_gmail_client_with_refresh(self) -> bool:
        """
        Initialize Gmail client and handle automatic token refresh.
        
        Returns:
            True if Gmail client is successfully initialized, False otherwise
        """
        try:
            if not GMAIL_AVAILABLE:
                self.logger.error("Gmail OAuth not available - missing dependencies")
                return False
            
            # Get credentials path from both structured and flat config
            credentials_path = ""
            token_path = "token.json"
            
            # Check structured config first
            oauth_config = self.email_config.get('gmail_oauth_config', {})
            if oauth_config and isinstance(oauth_config, dict):
                credentials_path = oauth_config.get('credentials_path', '')
                token_path = oauth_config.get('token_path', 'token.json')
            
            # Fallback to top-level fields
            if not credentials_path:
                credentials_path = self.email_config.get('credentials_path', '')
            if not token_path or token_path == 'token.json':
                token_path = self.email_config.get('token_path', 'token.json')
            
            if not credentials_path or not Path(credentials_path).exists():
                self.logger.error(f"Credentials file not found: {credentials_path}")
                return False
            
            # Initialize Gmail client
            self.gmail_client = GmailClient(credentials_path, token_path)
            
            # Check if we have existing tokens and try to refresh if needed
            if Path(token_path).exists():
                self.logger.info("Existing token found, attempting automatic refresh if needed")
                
                try:
                    # Try to authenticate (this will handle token refresh automatically)
                    if self.gmail_client.authenticate():
                        # Verify the client is working by testing connection
                        test_result = self.gmail_client.test_connection()
                        if test_result.get('success', False):
                            self.logger.info("Gmail client initialized and token refresh successful")
                            return True
                        else:
                            self.logger.warning(f"Gmail client test failed: {test_result.get('error', 'Unknown error')}")
                            return False
                    else:
                        self.logger.warning("Gmail authentication failed during initialization")
                        return False
                        
                except GmailAuthError as e:
                    self.logger.warning(f"Gmail authentication error during initialization: {e}")
                    return False
                except Exception as e:
                    self.logger.error(f"Unexpected error during Gmail client initialization: {e}")
                    return False
            else:
                self.logger.info("No existing token found - Gmail client initialized but not authenticated")
                # Client is initialized but not authenticated - user will need to authenticate
                return True
                
        except Exception as e:
            self.logger.error(f"Failed to initialize Gmail client: {e}")
            return False
    
    def _validate_gmail_oauth_config(self, config: Dict[str, Any]) -> tuple[bool, str]:
        """
        Validate Gmail OAuth configuration for loading.
        
        Args:
            config: Gmail OAuth configuration dictionary
            
        Returns:
            Tuple of (is_valid, error_message)
        """
        try:
            # Check if Gmail OAuth is available
            if not GMAIL_AVAILABLE:
                return False, "Gmail OAuth not available - missing required dependencies"
            
            # Handle both structured and flat configuration formats
            credentials_path = ""
            oauth_email = ""
            
            # Check for structured OAuth config first
            oauth_config = config.get('gmail_oauth_config', {})
            if oauth_config and isinstance(oauth_config, dict):
                credentials_path = oauth_config.get('credentials_path', '')
                oauth_email = oauth_config.get('oauth_email', '')
            
            # Fallback to top-level fields (backward compatibility)
            if not credentials_path:
                credentials_path = config.get('credentials_path', '')
            if not oauth_email:
                oauth_email = config.get('oauth_email', '')
            
            # Validate credentials file path
            if not credentials_path:
                return False, "Credentials file path is required for Gmail OAuth"
            
            credentials_file = Path(credentials_path)
            if not credentials_file.exists():
                return False, f"Credentials file not found: {credentials_path}"
            
            # Validate credentials file format
            try:
                import json
                with open(credentials_file, 'r') as f:
                    cred_data = json.load(f)
                
                # Check for required OAuth fields in credentials
                if 'installed' not in cred_data and 'web' not in cred_data:
                    return False, "Invalid credentials.json format - missing OAuth client configuration"
                
                # Get client config
                client_config = cred_data.get('installed') or cred_data.get('web')
                if not client_config:
                    return False, "Invalid credentials.json format - no client configuration found"
                
                # Check for required OAuth fields
                required_oauth_fields = ['client_id', 'client_secret']
                for field in required_oauth_fields:
                    if field not in client_config:
                        return False, f"Invalid credentials.json format - missing {field}"
                        
            except json.JSONDecodeError:
                return False, "Invalid credentials.json format - not valid JSON"
            except Exception as e:
                return False, f"Error reading credentials file: {str(e)}"
            
            # Validate OAuth email if provided
            if oauth_email:
                if "@" not in oauth_email:
                    return False, "Invalid OAuth email address format"
            
            self.logger.debug("Gmail OAuth configuration validation passed")
            return True, "Gmail OAuth configuration is valid"
            
        except Exception as e:
            error_msg = f"Error validating Gmail OAuth configuration: {str(e)}"
            self.logger.error(error_msg)
            return False, error_msg
    
    def _fallback_to_smtp(self, reason: str) -> None:
        """
        Fallback to SMTP authentication when OAuth tokens are invalid or expired.
        
        Args:
            reason: Reason for fallback
        """
        try:
            self.logger.warning(f"Falling back to SMTP authentication: {reason}")
            
            # Check if SMTP configuration is available
            smtp_config = self.email_config.get('smtp_config', {})
            if not smtp_config:
                # Check for top-level SMTP fields (backward compatibility)
                smtp_fields = ['smtp_server', 'email_address', 'password']
                has_smtp_config = any(self.email_config.get(field) for field in smtp_fields)
                
                if not has_smtp_config:
                    self.logger.warning("No SMTP configuration available for fallback")
                    self.auth_method = 'smtp'  # Set to SMTP but configuration is incomplete
                    return
            
            # Switch to SMTP authentication
            self.auth_method = 'smtp'
            
            # Clear Gmail client
            self.gmail_client = None
            
            # Validate SMTP configuration
            is_valid, validation_message = self.validate_smtp_config(self.email_config)
            if is_valid:
                self.logger.info("Successfully fell back to SMTP authentication")
            else:
                self.logger.warning(f"SMTP fallback configuration is invalid: {validation_message}")
            
            # Publish fallback event
            if self.event_bus:
                self.event_bus.publish("email.auth_fallback", {
                    "from": "gmail_oauth",
                    "to": "smtp",
                    "reason": reason,
                    "smtp_valid": is_valid
                })
                
        except Exception as e:
            self.logger.error(f"Error during SMTP fallback: {e}")
            self.auth_method = 'smtp'  # Ensure we're in a known state
    
    def _load_secure_oauth_tokens(self) -> None:
        """Load OAuth tokens from secure storage."""
        try:
            oauth_email = self.email_config.get('oauth_email', '')
            if not oauth_email:
                self.logger.debug("No OAuth email found in configuration")
                return
            
            secure_storage = SecureStorage()
            
            # Load credentials path from secure storage
            credentials_path = secure_storage.retrieve_credentials_path('gmail_oauth', oauth_email)
            if credentials_path:
                self.email_config['credentials_path'] = credentials_path
                self.logger.debug(f"Loaded credentials path from secure storage for {oauth_email}")
            
            # Load OAuth tokens from secure storage
            tokens = secure_storage.retrieve_token('gmail_oauth', oauth_email)
            if tokens:
                # Initialize Gmail client with loaded tokens if available
                if credentials_path and Path(credentials_path).exists():
                    try:
                        self.gmail_client = GmailClient(credentials_path)
                        if hasattr(self.gmail_client, 'set_tokens'):
                            self.gmail_client.set_tokens(tokens)
                            self.logger.info(f"Gmail client initialized with secure tokens for {oauth_email}")
                    except Exception as e:
                        self.logger.warning(f"Failed to initialize Gmail client with secure tokens: {e}")
                
                self.logger.debug(f"Loaded OAuth tokens from secure storage for {oauth_email}")
            
        except Exception as e:
            self.logger.warning(f"Failed to load secure OAuth tokens: {e}")
    
    def _save_email_config(self) -> None:
        """Save email configuration to config manager."""
        if self.config_manager:
            try:
                self.config_manager.set_value("email_config", self.email_config)
                self.logger.info("Email configuration saved to config manager")
            except Exception as e:
                self.logger.error(f"Failed to save email configuration: {e}")
    
    def _on_config_changed(self, config_data: Dict[str, Any]) -> None:
        """Handle email configuration change event."""
        self.logger.info("Email configuration changed via event")
        self.email_config.update(config_data)
        self._save_email_config()
        
        # Publish configuration updated event
        if self.event_bus:
            self.event_bus.publish("email.config_updated", self.email_config)
    
    def _on_send_request(self, send_data: Dict[str, Any]) -> None:
        """Handle email send request event."""
        try:
            to = send_data.get("to", "")
            subject = send_data.get("subject", "")
            body = send_data.get("body", "")
            
            success = self.send_email_smtp(to, subject, body)
            
            if self.event_bus:
                if success:
                    self.event_bus.publish("email.sent", send_data)
                else:
                    self.event_bus.publish("email.send_failed", send_data)
                    
        except Exception as e:
            self.logger.error(f"Error handling send request: {e}")
            if self.event_bus:
                self.event_bus.publish("email.send_error", str(e))
    
    def get_email_config(self) -> Dict[str, Any]:
        """
        Get current email configuration.
        
        Returns:
            Dictionary containing email configuration
        """
        return self.email_config.copy()
    
    def save_email_config(self, config: Dict[str, Any]) -> tuple[bool, str]:
        """
        Save email configuration with support for both SMTP and Gmail OAuth authentication.
        
        Args:
            config: Email configuration dictionary
            
        Returns:
            Tuple of (success, message)
        """
        try:
            # Determine authentication method
            auth_method = config.get('auth_method', 'smtp')
            self.logger.info(f"Saving email configuration with auth method: {auth_method}")
            
            # Validate configuration based on authentication method
            if auth_method == 'gmail_oauth':
                is_valid, validation_message = self.validate_gmail_oauth_config(config)
            else:
                is_valid, validation_message = self.validate_smtp_config(config)
            
            if not is_valid:
                self.logger.error(f"Invalid {auth_method} configuration provided: {validation_message}")
                return False, validation_message
            
            # Migrate existing SMTP-only configuration if needed
            migrated_config = self._migrate_config_if_needed(config)
            
            # Handle secure token storage for Gmail OAuth
            if auth_method == 'gmail_oauth':
                success, message = self._handle_oauth_token_storage(migrated_config)
                if not success:
                    return False, message
            
            # Update internal configuration
            self.email_config.update(migrated_config)
            
            # Update authentication method
            self.auth_method = auth_method
            
            # Save to config manager
            self._save_email_config()
            
            # Publish configuration updated event
            if self.event_bus:
                self.event_bus.publish("email.config_updated", self.email_config)
            
            success_msg = f"Email configuration saved successfully using {auth_method} authentication"
            self.logger.info(success_msg)
            return True, success_msg
            
        except Exception as e:
            error_msg = f"Error saving email configuration: {str(e)}"
            self.logger.error(error_msg)
            return False, error_msg
    
    def validate_smtp_config(self, config: Dict[str, Any]) -> tuple[bool, str]:
        """
        Validate SMTP configuration with detailed error messages.
        
        Args:
            config: SMTP configuration dictionary
            
        Returns:
            Tuple of (is_valid, error_message)
        """
        try:
            # Check required fields
            required_fields = {
                "smtp_server": "SMTP server address",
                "email_address": "Email address", 
                "password": "Password"
            }
            
            for field, display_name in required_fields.items():
                if not config.get(field):
                    error_msg = f"Missing required field: {display_name}"
                    self.logger.error(error_msg)
                    return False, error_msg
            
            # Validate email address format (comprehensive validation)
            email = config.get("email_address", "").strip()
            if not email:
                error_msg = "Email address cannot be empty"
                self.logger.error(error_msg)
                return False, error_msg
            
            if "@" not in email:
                error_msg = "Email address must contain @ symbol"
                self.logger.error(error_msg)
                return False, error_msg
            
            # More thorough email validation
            email_parts = email.split("@")
            if len(email_parts) != 2:
                error_msg = "Email address format is invalid"
                self.logger.error(error_msg)
                return False, error_msg
            
            local_part, domain = email_parts
            if not local_part or not domain:
                error_msg = "Email address format is invalid"
                self.logger.error(error_msg)
                return False, error_msg
            
            # Check domain part has at least one dot and valid characters
            if "." not in domain or domain.startswith(".") or domain.endswith("."):
                error_msg = "Email domain format is invalid"
                self.logger.error(error_msg)
                return False, error_msg
            
            # Check for invalid characters in local part
            invalid_chars = ['<', '>', '(', ')', '[', ']', '\\', ',', ';', ':', '"']
            if any(char in local_part for char in invalid_chars):
                error_msg = "Email address contains invalid characters"
                self.logger.error(error_msg)
                return False, error_msg
            
            # Validate port number
            port = config.get("port", self.default_smtp_port)
            if not isinstance(port, int) or port <= 0 or port > 65535:
                error_msg = f"Port number must be between 1 and 65535 (current: {port})"
                self.logger.error(error_msg)
                return False, error_msg
            
            # Validate server address
            server = config.get("smtp_server", "").strip()
            if not server:
                error_msg = "SMTP server address cannot be empty"
                self.logger.error(error_msg)
                return False, error_msg
            
            # Check for valid server format (basic check)
            if " " in server or server.startswith(".") or server.endswith("."):
                error_msg = "SMTP server address format is invalid"
                self.logger.error(error_msg)
                return False, error_msg
            
            # Validate password strength (basic check)
            password = config.get("password", "")
            if len(password) < 6:
                error_msg = "Password must be at least 6 characters long"
                self.logger.error(error_msg)
                return False, error_msg
            
            self.logger.debug("SMTP configuration validation passed")
            return True, "Configuration is valid"
            
        except Exception as e:
            error_msg = f"Error validating SMTP configuration: {str(e)}"
            self.logger.error(error_msg)
            return False, error_msg
    
    def validate_gmail_oauth_config(self, config: Dict[str, Any]) -> tuple[bool, str]:
        """
        Validate Gmail OAuth configuration with detailed error messages.
        
        Args:
            config: Gmail OAuth configuration dictionary
            
        Returns:
            Tuple of (is_valid, error_message)
        """
        try:
            # Check if this is an already authenticated OAuth configuration
            oauth_authenticated = config.get("oauth_authenticated", False)
            oauth_email = config.get("oauth_email", "").strip()
            
            # If OAuth is already authenticated, we can be more lenient with validation
            if oauth_authenticated and oauth_email:
                self.logger.info(f"Validating already authenticated OAuth config for {oauth_email}")
                
                # For authenticated configs, we just need basic validation
                if "@" not in oauth_email:
                    error_msg = "OAuth email address must contain @ symbol"
                    self.logger.error(error_msg)
                    return False, error_msg
                
                # Credentials path is optional for already authenticated configs
                credentials_path = config.get("credentials_path", "").strip()
                if credentials_path:
                    # If credentials path is provided, validate it exists
                    credentials_file = Path(credentials_path)
                    if not credentials_file.exists():
                        self.logger.warning(f"Credentials file not found: {credentials_path}, but OAuth is already authenticated")
                        # Don't fail validation for authenticated configs with missing credentials file
                
                self.logger.info("OAuth configuration validation passed (already authenticated)")
                return True, "Valid authenticated OAuth configuration"
            
            # For non-authenticated configs, we need strict validation
            self.logger.info("Validating non-authenticated OAuth config - strict validation required")
            
            # Check required fields for Gmail OAuth
            required_fields = {
                "credentials_path": "Credentials file path"
            }
            
            for field, display_name in required_fields.items():
                if not config.get(field):
                    error_msg = f"Missing required field: {display_name}"
                    self.logger.error(error_msg)
                    return False, error_msg
            
            # Validate credentials file path
            credentials_path = config.get("credentials_path", "").strip()
            if not credentials_path:
                error_msg = "Credentials file path cannot be empty"
                self.logger.error(error_msg)
                return False, error_msg
            
            # Check if credentials file exists
            credentials_file = Path(credentials_path)
            if not credentials_file.exists():
                error_msg = f"Credentials file not found: {credentials_path}"
                self.logger.error(error_msg)
                return False, error_msg
            
            # Validate credentials file format (basic JSON check)
            try:
                import json
                with open(credentials_file, 'r') as f:
                    cred_data = json.load(f)
                
                # Check for required OAuth fields in credentials
                if 'installed' not in cred_data and 'web' not in cred_data:
                    error_msg = "Invalid credentials.json format - missing OAuth client configuration"
                    self.logger.error(error_msg)
                    return False, error_msg
                
                # Get client config (either 'installed' for desktop apps or 'web' for web apps)
                client_config = cred_data.get('installed') or cred_data.get('web')
                if not client_config:
                    error_msg = "Invalid credentials.json format - no client configuration found"
                    self.logger.error(error_msg)
                    return False, error_msg
                
                # Check for required OAuth fields
                required_oauth_fields = ['client_id', 'client_secret']
                for field in required_oauth_fields:
                    if field not in client_config:
                        error_msg = f"Invalid credentials.json format - missing {field}"
                        self.logger.error(error_msg)
                        return False, error_msg
                
            except json.JSONDecodeError as e:
                error_msg = f"Invalid credentials.json format - not valid JSON: {str(e)}"
                self.logger.error(error_msg)
                return False, error_msg
            except Exception as e:
                error_msg = f"Error reading credentials file: {str(e)}"
                self.logger.error(error_msg)
                return False, error_msg
            
            # Validate OAuth email address format (if provided)
            oauth_email = config.get("oauth_email", "").strip()
            if oauth_email:  # Only validate if provided
                if "@" not in oauth_email:
                    error_msg = "OAuth email address must contain @ symbol"
                    self.logger.error(error_msg)
                    return False, error_msg
                
                # More thorough email validation
                email_parts = oauth_email.split("@")
                if len(email_parts) != 2:
                    error_msg = "OAuth email address format is invalid"
                    self.logger.error(error_msg)
                    return False, error_msg
                
                local_part, domain = email_parts
                if not local_part or not domain:
                    error_msg = "OAuth email address format is invalid"
                    self.logger.error(error_msg)
                    return False, error_msg
            
            # Check domain part has at least one dot and valid characters
            if "." not in domain or domain.startswith(".") or domain.endswith("."):
                error_msg = "OAuth email domain format is invalid"
                self.logger.error(error_msg)
                return False, error_msg
            
            # Validate token path if provided
            token_path = config.get("token_path", "")
            if token_path:
                token_file = Path(token_path)
                # Check if token directory is writable
                token_dir = token_file.parent
                if not token_dir.exists():
                    try:
                        token_dir.mkdir(parents=True, exist_ok=True)
                    except Exception as e:
                        error_msg = f"Cannot create token directory: {str(e)}"
                        self.logger.error(error_msg)
                        return False, error_msg
                
                if not os.access(token_dir, os.W_OK):
                    error_msg = f"Token directory is not writable: {token_dir}"
                    self.logger.error(error_msg)
                    return False, error_msg
            
            self.logger.debug("Gmail OAuth configuration validation passed")
            return True, "Gmail OAuth configuration is valid"
            
        except Exception as e:
            error_msg = f"Error validating Gmail OAuth configuration: {str(e)}"
            self.logger.error(error_msg)
            return False, error_msg
    
    def _migrate_config_if_needed(self, config: Dict[str, Any]) -> Dict[str, Any]:
        """
        Migrate existing SMTP-only configuration to support dual authentication.
        
        Args:
            config: Configuration dictionary to migrate
            
        Returns:
            Migrated configuration dictionary
        """
        try:
            migrated_config = config.copy()
            
            # Check if this is an existing SMTP-only configuration
            if 'auth_method' not in migrated_config:
                self.logger.info("Migrating SMTP-only configuration to dual authentication format")
                
                # Set default authentication method to SMTP for existing configs
                migrated_config['auth_method'] = 'smtp'
                
                # Ensure SMTP configuration is properly structured
                smtp_fields = ['smtp_server', 'port', 'email_address', 'password', 'use_tls', 'use_ssl']
                smtp_config = {}
                
                for field in smtp_fields:
                    if field in migrated_config:
                        smtp_config[field] = migrated_config[field]
                
                # Create structured configuration
                migrated_config['smtp_config'] = smtp_config
                
                # Initialize Gmail OAuth config section (empty)
                migrated_config['gmail_oauth_config'] = {
                    'credentials_path': '',
                    'token_path': '',
                    'oauth_email': '',
                    'oauth_authenticated': False
                }
                
                self.logger.info("Successfully migrated SMTP configuration to dual authentication format")
            
            # Ensure both config sections exist
            if 'smtp_config' not in migrated_config:
                migrated_config['smtp_config'] = {}
            
            if 'gmail_oauth_config' not in migrated_config:
                migrated_config['gmail_oauth_config'] = {
                    'credentials_path': '',
                    'token_path': '',
                    'oauth_email': '',
                    'oauth_authenticated': False
                }
            
            # Preserve backward compatibility by keeping top-level SMTP fields
            auth_method = migrated_config.get('auth_method', 'smtp')
            if auth_method == 'smtp':
                smtp_config = migrated_config.get('smtp_config', {})
                # Check if smtp_config is a dictionary before iterating
                if isinstance(smtp_config, dict):
                    for field, value in smtp_config.items():
                        migrated_config[field] = value
            
            return migrated_config
            
        except Exception as e:
            self.logger.error(f"Error migrating configuration: {e}")
            # Return original config if migration fails
            return config
    
    def _handle_oauth_token_storage(self, config: Dict[str, Any]) -> tuple[bool, str]:
        """
        Handle secure storage of OAuth tokens.
        
        Args:
            config: Configuration dictionary containing OAuth information
            
        Returns:
            Tuple of (success, message)
        """
        try:
            if not SECURE_STORAGE_AVAILABLE:
                self.logger.warning("Secure storage not available, tokens will be stored in plain text")
                return True, "OAuth configuration saved (secure storage not available)"
            
            oauth_email = config.get('oauth_email', '')
            if not oauth_email:
                error_msg = "OAuth email required for secure token storage"
                self.logger.error(error_msg)
                return False, error_msg
            
            # Initialize secure storage
            secure_storage = SecureStorage()
            
            # Store credentials path securely if provided
            credentials_path = config.get('credentials_path', '')
            if credentials_path:
                success = secure_storage.store_credentials_path('gmail_oauth', oauth_email, credentials_path)
                if not success:
                    error_msg = "Failed to store credentials path securely"
                    self.logger.error(error_msg)
                    return False, error_msg
            
            # If we have existing tokens from Gmail client, store them securely
            if self.gmail_client and hasattr(self.gmail_client, 'get_tokens'):
                try:
                    tokens = self.gmail_client.get_tokens()
                    if tokens:
                        success = secure_storage.store_token('gmail_oauth', oauth_email, tokens)
                        if not success:
                            error_msg = "Failed to store OAuth tokens securely"
                            self.logger.error(error_msg)
                            return False, error_msg
                        
                        self.logger.info(f"OAuth tokens stored securely for {oauth_email}")
                except Exception as e:
                    self.logger.warning(f"Could not retrieve tokens from Gmail client: {e}")
            
            # Remove sensitive information from config that will be saved to regular storage
            config_copy = config.copy()
            gmail_oauth_config = config_copy.get('gmail_oauth_config', {})
            
            # Keep only non-sensitive OAuth configuration
            gmail_oauth_config['credentials_path'] = ''  # Don't store path in regular config
            gmail_oauth_config['oauth_authenticated'] = config.get('oauth_authenticated', False)
            gmail_oauth_config['oauth_email'] = oauth_email
            
            success_msg = f"OAuth configuration and tokens stored securely for {oauth_email}"
            self.logger.info(success_msg)
            return True, success_msg
            
        except SecureStorageError as e:
            error_msg = f"Secure storage error: {str(e)}"
            self.logger.error(error_msg)
            return False, error_msg
        except Exception as e:
            error_msg = f"Error handling OAuth token storage: {str(e)}"
            self.logger.error(error_msg)
            return False, error_msg
    
    def _handle_oauth_token_storage(self, config: Dict[str, Any]) -> tuple[bool, str]:
        """
        Handle secure storage of OAuth tokens.
        
        Args:
            config: Configuration dictionary containing OAuth information
            
        Returns:
            Tuple of (success, message)
        """
        try:
            if not SECURE_STORAGE_AVAILABLE:
                self.logger.warning("Secure storage not available, tokens will be stored in plain text")
                return True, "OAuth configuration saved (secure storage not available)"
            
            oauth_email = config.get('oauth_email', '')
            if not oauth_email:
                error_msg = "OAuth email required for secure token storage"
                self.logger.error(error_msg)
                return False, error_msg
            
            # Initialize secure storage
            secure_storage = SecureStorage()
            
            # Store credentials path securely if provided
            credentials_path = config.get('credentials_path', '')
            if credentials_path:
                success = secure_storage.store_credentials_path('gmail_oauth', oauth_email, credentials_path)
                if not success:
                    error_msg = "Failed to store credentials path securely"
                    self.logger.error(error_msg)
                    return False, error_msg
            
            # If we have existing tokens from Gmail client, store them securely
            if self.gmail_client and hasattr(self.gmail_client, 'get_tokens'):
                try:
                    tokens = self.gmail_client.get_tokens()
                    if tokens:
                        success = secure_storage.store_token('gmail_oauth', oauth_email, tokens)
                        if not success:
                            error_msg = "Failed to store OAuth tokens securely"
                            self.logger.error(error_msg)
                            return False, error_msg
                        
                        self.logger.info(f"OAuth tokens stored securely for {oauth_email}")
                except Exception as e:
                    self.logger.warning(f"Could not retrieve tokens from Gmail client: {e}")
            
            # Remove sensitive information from config that will be saved to regular storage
            config_copy = config.copy()
            gmail_oauth_config = config_copy.get('gmail_oauth_config', {})
            
            # Keep only non-sensitive OAuth configuration
            gmail_oauth_config['credentials_path'] = ''  # Don't store path in regular config
            gmail_oauth_config['oauth_authenticated'] = config.get('oauth_authenticated', False)
            gmail_oauth_config['oauth_email'] = oauth_email
            
            success_msg = f"OAuth configuration and tokens stored securely for {oauth_email}"
            self.logger.info(success_msg)
            return True, success_msg
            
        except SecureStorageError as e:
            error_msg = f"Secure storage error: {str(e)}"
            self.logger.error(error_msg)
            return False, error_msg
        except Exception as e:
            error_msg = f"Error handling OAuth token storage: {str(e)}"
            self.logger.error(error_msg)
            return False, error_msg
    
    def send_email(self, to: str, subject: str, body: str, smtp_config: Dict[str, Any] = None) -> bool:
        """
        Send email using the configured method (Gmail API or SMTP) with automatic fallback.
        
        Args:
            to: Recipient email address
            subject: Email subject
            body: Email body content
            smtp_config: Optional SMTP configuration (uses saved config if not provided)
            
        Returns:
            True if email was sent successfully, False otherwise
        """
        try:
            # Determine which sending method to use
            send_method = self._determine_send_method()
            
            self.logger.info(f"Attempting to send email using method: {send_method}")
            
            # Try primary method first
            if send_method == "gmail_api":
                success = self._send_via_gmail_api(to, subject, body)
                if success:
                    return True
                else:
                    # Fallback to SMTP if Gmail API fails
                    self.logger.warning("Gmail API send failed, falling back to SMTP")
                    return self.send_email_smtp(to, subject, body, smtp_config)
            else:
                # Use SMTP method
                return self.send_email_smtp(to, subject, body, smtp_config)
                
        except Exception as e:
            self.logger.error(f"Error in send_email: {e}")
            return False
    
    def send_email_smtp(self, to: str, subject: str, body: str, smtp_config: Dict[str, Any] = None) -> bool:
        """
        Send email using SMTP (placeholder implementation with enhanced error handling).
        
        Args:
            to: Recipient email address
            subject: Email subject
            body: Email body content
            smtp_config: Optional SMTP configuration (uses saved config if not provided)
            
        Returns:
            True if email was sent successfully, False otherwise
        """
        try:
            # Validate input parameters
            if not to or not to.strip():
                self.logger.error("Recipient email address is required")
                if self.event_bus:
                    self.event_bus.publish("email.send_error", {
                        "to": to,
                        "subject": subject,
                        "error": "Recipient email address is required"
                    })
                return False
            
            if not subject or not subject.strip():
                self.logger.error("Email subject is required")
                if self.event_bus:
                    self.event_bus.publish("email.send_error", {
                        "to": to,
                        "subject": subject,
                        "error": "Email subject is required"
                    })
                return False
            
            if not body or not body.strip():
                self.logger.error("Email body is required")
                if self.event_bus:
                    self.event_bus.publish("email.send_error", {
                        "to": to,
                        "subject": subject,
                        "error": "Email body is required"
                    })
                return False
            
            # Use provided config or fall back to saved config
            config = smtp_config or self.email_config
            
            if not config:
                self.logger.error("No SMTP configuration available")
                if self.event_bus:
                    self.event_bus.publish("email.send_error", {
                        "to": to,
                        "subject": subject,
                        "error": "No SMTP configuration available. Please configure email settings first."
                    })
                return False
            
            # Validate configuration
            is_valid, validation_message = self.validate_smtp_config(config)
            if not is_valid:
                self.logger.error(f"Invalid SMTP configuration: {validation_message}")
                if self.event_bus:
                    self.event_bus.publish("email.send_error", {
                        "to": to,
                        "subject": subject,
                        "error": f"Invalid SMTP configuration: {validation_message}"
                    })
                return False
            
            # Validate recipient email format
            if "@" not in to or "." not in to.split("@")[1]:
                self.logger.error(f"Invalid recipient email format: {to}")
                if self.event_bus:
                    self.event_bus.publish("email.send_error", {
                        "to": to,
                        "subject": subject,
                        "error": f"Invalid recipient email format: {to}"
                    })
                return False
            
            # Additional email validation
            email_parts = to.split("@")
            if len(email_parts) != 2 or not email_parts[0] or not email_parts[1]:
                self.logger.error(f"Invalid recipient email format: {to}")
                if self.event_bus:
                    self.event_bus.publish("email.send_error", {
                        "to": to,
                        "subject": subject,
                        "error": f"Invalid recipient email format: {to}"
                    })
                return False
            
            # Extract configuration values
            smtp_server = config.get("smtp_server")
            port = config.get("port", self.default_smtp_port)
            email_address = config.get("email_address")
            password = config.get("password")
            use_tls = config.get("use_tls", self.default_use_tls)
            use_ssl = config.get("use_ssl", self.default_use_ssl)
            
            self.logger.info(f"Attempting to send email to {to} via {smtp_server}:{port}")
            
            # PLACEHOLDER IMPLEMENTATION WITH ENHANCED SIMULATION
            # In a real implementation, this would:
            # 1. Create SMTP connection: smtp.SMTP(smtp_server, port)
            # 2. Start TLS if required: smtp.starttls()
            # 3. Authenticate with credentials: smtp.login(email_address, password)
            # 4. Create MIMEText message with proper headers
            # 5. Send the email: smtp.send_message(msg)
            # 6. Handle specific SMTP errors and retries
            # 7. Close connection: smtp.quit()
            
            # Simulate potential connection issues (for testing error handling)
            import random
            import time
            
            # Add small delay to simulate network operation
            time.sleep(0.5)
            
            # Simulate occasional failures for testing (10% failure rate)
            if random.random() < 0.1:
                error_msg = "Simulated SMTP connection timeout"
                self.logger.error(f"PLACEHOLDER ERROR: {error_msg}")
                if self.event_bus:
                    self.event_bus.publish("email.send_error", {
                        "to": to,
                        "subject": subject,
                        "error": error_msg
                    })
                return False
            
            # Log the placeholder operation with detailed information
            self.logger.info(f"PLACEHOLDER: Successfully sent email to {to}")
            self.logger.info(f"PLACEHOLDER: Subject: {subject}")
            self.logger.info(f"PLACEHOLDER: Body length: {len(body)} characters")
            self.logger.info(f"PLACEHOLDER: Using server: {smtp_server}:{port}")
            self.logger.info(f"PLACEHOLDER: From: {email_address}")
            self.logger.info(f"PLACEHOLDER: TLS enabled: {use_tls}")
            
            # Publish successful email sent event with detailed information
            if self.event_bus:
                import datetime
                self.event_bus.publish("email.sent", {
                    "to": to,
                    "subject": subject,
                    "body_length": len(body),
                    "from": email_address,
                    "smtp_server": smtp_server,
                    "timestamp": datetime.datetime.now().isoformat(),
                    "success": True
                })
            
            return True
            
        except Exception as e:
            self.logger.error(f"Unexpected error sending email: {e}")
            
            # Publish email send error event with detailed error information
            if self.event_bus:
                self.event_bus.publish("email.send_error", {
                    "to": to,
                    "subject": subject,
                    "error": f"Unexpected error: {str(e)}",
                    "error_type": type(e).__name__
                })
            
            return False
    
    def generate_reply(self, original_email: Dict[str, Any], model_service=None) -> str:
        """
        Generate AI-powered email reply using the loaded model.
        
        Args:
            original_email: Dictionary containing original email data
            model_service: ModelService instance for text generation (optional, uses self.model_service if not provided)
            
        Returns:
            Generated reply text
        """
        try:
            self.logger.info("Generating AI-powered email reply")
            
            # Use provided model service or fall back to instance model service
            service = model_service or self.model_service
            
            if not service:
                self.logger.warning("No model service available, using fallback reply")
                return "Thank you for your email. I will review your message and get back to you soon.\n\nBest regards"
            
            # Extract email information
            sender = original_email.get("sender", "Unknown")
            subject = original_email.get("subject", "No Subject")
            body = original_email.get("body", "")
            
            self.logger.info(f"Generating reply to email from {sender}")
            self.logger.info(f"Original subject: {subject}")
            
            # Create a prompt for reply generation
            system_prompt = """You are a professional email assistant. Generate a concise, professional email reply based on the original email content. 
Keep the reply brief but helpful. Use a professional tone and include appropriate greetings and closings.
Do not include subject lines or email headers in your response - only the email body content."""
            
            # Build the prompt with original email context
            prompt = f"""Please write a professional email reply to the following email:

From: {sender}
Subject: {subject}

Original Email:
{body}

Reply:"""
            
            # Try to use the actual model service for generation
            try:
                # Check if BackendManager has a model loaded
                if hasattr(service, 'backend_manager') and service.backend_manager and service.backend_manager.current_backend:
                    self.logger.info("Using BackendManager for email reply generation")
                    
                    # Use a synchronous approach by creating a simple generation thread
                    # This is a simplified version of what ChatService does
                    import threading
                    import time
                    
                    generated_text = None
                    generation_error = None
                    generation_complete = threading.Event()
                    
                    def on_generation_finished(text):
                        nonlocal generated_text
                        generated_text = text
                        generation_complete.set()
                    
                    def on_generation_error(error):
                        nonlocal generation_error
                        generation_error = error
                        generation_complete.set()
                    
                    # Connect to model service signals temporarily
                    service.generation_finished.connect(on_generation_finished)
                    service.generation_error.connect(on_generation_error)
                    
                    try:
                        # Start async generation
                        success = service.generate_text_async(
                            prompt=prompt,
                            system_prompt=system_prompt,
                            temperature=0.7,
                            max_tokens=300,
                            top_p=0.9,
                            top_k=40,
                            repeat_penalty=1.1
                        )
                        
                        if success:
                            # Wait for generation to complete (with timeout)
                            if generation_complete.wait(timeout=30):  # 30 second timeout
                                if generated_text and generated_text.strip():
                                    reply_text = generated_text.strip()
                                    self.logger.info(f"AI reply generated using model: {reply_text[:100]}...")
                                    
                                    # Publish reply generated event
                                    if self.event_bus:
                                        self.event_bus.publish("email.reply_generated", {
                                            "original_sender": sender,
                                            "original_subject": subject,
                                            "reply_length": len(reply_text)
                                        })
                                    
                                    return reply_text
                                elif generation_error:
                                    self.logger.error(f"Model generation error: {generation_error}")
                                else:
                                    self.logger.warning("Model generated empty reply")
                            else:
                                self.logger.warning("Model generation timed out")
                        else:
                            self.logger.warning("Failed to start model generation")
                    
                    finally:
                        # Disconnect signals
                        try:
                            service.generation_finished.disconnect(on_generation_finished)
                            service.generation_error.disconnect(on_generation_error)
                        except:
                            pass  # Ignore disconnect errors
                
                # Fallback to template-based approach if model generation fails
                self.logger.info("Using template-based fallback for email reply")
                if "meeting" in subject.lower():
                    reply_text = f"Thank you for your email about the meeting. I will review the details and get back to you with my availability.\n\nBest regards"
                elif "thank" in subject.lower():
                    reply_text = f"You're very welcome! I'm glad I could help. Please don't hesitate to reach out if you need anything else.\n\nBest regards"
                elif "question" in subject.lower() or "?" in body:
                    reply_text = f"Thank you for your question. I will look into this and provide you with a detailed response shortly.\n\nBest regards"
                elif "follow up" in subject.lower():
                    reply_text = f"Thank you for following up. I will review the status and update you accordingly.\n\nBest regards"
                else:
                    reply_text = f"Thank you for your email regarding '{subject}'. I have received your message and will review it carefully.\n\nI will get back to you soon with a detailed response.\n\nBest regards"
                
                self.logger.info(f"Template reply generated: {reply_text[:100]}...")
                
                # Publish reply generated event
                if self.event_bus:
                    self.event_bus.publish("email.reply_generated", {
                        "original_sender": sender,
                        "original_subject": subject,
                        "reply_length": len(reply_text)
                    })
                
                return reply_text
                    
            except Exception as model_error:
                self.logger.error(f"Model generation failed: {model_error}")
                return "Thank you for your email. I will review your message and get back to you soon.\n\nBest regards"
            
        except Exception as e:
            self.logger.error(f"Error generating email reply: {e}")
            return "Thank you for your email. I will review your message and get back to you soon.\n\nBest regards"
    
    def generate_draft(self, to: str, subject: str, context: str = "", model_service=None) -> str:
        """
        Generate AI-powered email draft using the loaded model.
        
        Args:
            to: Recipient email address
            subject: Email subject
            context: Additional context for generation
            model_service: ModelService instance for text generation (optional, uses self.model_service if not provided)
            
        Returns:
            Generated draft text
        """
        try:
            self.logger.info("Generating AI-powered email draft")
            
            # Use provided model service or fall back to instance model service
            service = model_service or self.model_service
            
            if not service:
                self.logger.warning("No model service available, using fallback draft")
                recipient_name = to.split('@')[0] if '@' in to else "there"
                return f"Dear {recipient_name},\n\nI hope this email finds you well. I am writing to you regarding {subject.lower()}.\n\n[Please add your message content here]\n\nBest regards"
            
            self.logger.info(f"Generating draft for {to}")
            self.logger.info(f"Subject: {subject}")
            self.logger.info(f"Context: {context}")
            
            # Create a prompt for draft generation
            system_prompt = """You are a professional email assistant. Generate a professional email draft based on the recipient, subject, and context provided.
Write a complete email body that is professional, clear, and appropriate for business communication.
Do not include subject lines or email headers in your response - only the email body content.
Include appropriate greetings and professional closings."""
            
            # Build the prompt with context
            recipient_name = to.split('@')[0] if '@' in to else "there"
            prompt = f"""Please write a professional email draft with the following details:

To: {to}
Subject: {subject}
Context: {context}

Write a professional email body addressing {recipient_name} about {subject}.

Email body:"""
            
            # Try to use the actual model service for generation
            try:
                # Check if BackendManager has a model loaded
                if hasattr(service, 'backend_manager') and service.backend_manager and service.backend_manager.current_backend:
                    self.logger.info("Using BackendManager for email draft generation")
                    
                    # Use a synchronous approach by creating a simple generation thread
                    # This is a simplified version of what ChatService does
                    import threading
                    import time
                    
                    generated_text = None
                    generation_error = None
                    generation_complete = threading.Event()
                    
                    def on_generation_finished(text):
                        nonlocal generated_text
                        generated_text = text
                        generation_complete.set()
                    
                    def on_generation_error(error):
                        nonlocal generation_error
                        generation_error = error
                        generation_complete.set()
                    
                    # Connect to model service signals temporarily
                    service.generation_finished.connect(on_generation_finished)
                    service.generation_error.connect(on_generation_error)
                    
                    try:
                        # Start async generation
                        success = service.generate_text_async(
                            prompt=prompt,
                            system_prompt=system_prompt,
                            temperature=0.8,  # Slightly more creative for drafts
                            max_tokens=400,   # Longer length for email drafts
                            top_p=0.9,
                            top_k=40,
                            repeat_penalty=1.1
                        )
                        
                        if success:
                            # Wait for generation to complete (with timeout)
                            if generation_complete.wait(timeout=30):  # 30 second timeout
                                if generated_text and generated_text.strip():
                                    draft_text = generated_text.strip()
                                    self.logger.info(f"AI draft generated using model: {draft_text[:100]}...")
                                    
                                    # Publish draft generated event
                                    if self.event_bus:
                                        self.event_bus.publish("email.draft_generated", {
                                            "to": to,
                                            "subject": subject,
                                            "draft_length": len(draft_text)
                                        })
                                    
                                    return draft_text
                                elif generation_error:
                                    self.logger.error(f"Model generation error: {generation_error}")
                                else:
                                    self.logger.warning("Model generated empty draft")
                            else:
                                self.logger.warning("Model generation timed out")
                        else:
                            self.logger.warning("Failed to start model generation")
                    
                    finally:
                        # Disconnect signals
                        try:
                            service.generation_finished.disconnect(on_generation_finished)
                            service.generation_error.disconnect(on_generation_error)
                        except:
                            pass  # Ignore disconnect errors
                
                # Fallback to template-based approach if model generation fails
                self.logger.info("Using template-based fallback for email draft")
                if "meeting" in subject.lower() or "schedule" in subject.lower():
                    draft_text = f"Dear {recipient_name},\n\nI hope this email finds you well. I would like to schedule a meeting with you regarding {subject.lower()}.\n\nPlease let me know your availability for the coming week, and I will send you a calendar invitation.\n\nLooking forward to hearing from you.\n\nBest regards"
                elif "follow up" in subject.lower() or "followup" in subject.lower():
                    draft_text = f"Dear {recipient_name},\n\nI wanted to follow up on our previous conversation regarding {subject.lower()}.\n\nPlease let me know if you need any additional information from my side, or if there are any next steps I should be aware of.\n\nThank you for your time.\n\nBest regards"
                elif "thank" in subject.lower():
                    draft_text = f"Dear {recipient_name},\n\nI wanted to take a moment to thank you for {subject.lower()}.\n\nYour assistance has been invaluable, and I truly appreciate the time and effort you put into helping me.\n\nPlease don't hesitate to reach out if there's anything I can do to return the favor.\n\nWith gratitude"
                elif "proposal" in subject.lower() or "project" in subject.lower():
                    draft_text = f"Dear {recipient_name},\n\nI hope you are doing well. I am reaching out to discuss a potential opportunity regarding {subject.lower()}.\n\nI believe this could be mutually beneficial, and I would love to explore how we might work together on this.\n\nWould you be available for a brief call this week to discuss the details?\n\nBest regards"
                elif context and len(context.strip()) > 0:
                    draft_text = f"Dear {recipient_name},\n\nI hope this email finds you well. I am writing to you regarding {subject.lower()}.\n\n{context}\n\nPlease let me know if you have any questions or if there is additional information I can provide.\n\nBest regards"
                else:
                    # Generic professional template
                    draft_text = f"Dear {recipient_name},\n\nI hope this email finds you well. I am writing to you regarding {subject.lower()}.\n\nI would appreciate the opportunity to discuss this matter with you further. Please let me know if you have any questions or if there is additional information I can provide.\n\nThank you for your time and consideration.\n\nBest regards"
                
                self.logger.info(f"Template draft generated: {draft_text[:100]}...")
                
                # Publish draft generated event
                if self.event_bus:
                    self.event_bus.publish("email.draft_generated", {
                        "to": to,
                        "subject": subject,
                        "draft_length": len(draft_text)
                    })
                
                return draft_text
                    
            except Exception as model_error:
                self.logger.error(f"Model generation failed: {model_error}")
                return f"Dear {recipient_name},\n\nI hope this email finds you well. I am writing to you regarding {subject.lower()}.\n\n[Please add your message content here]\n\nBest regards"
            
        except Exception as e:
            self.logger.error(f"Error generating email draft: {e}")
            return "Dear there,\n\nI hope this email finds you well.\n\n[Please add your message content here]\n\nBest regards"
    
    def test_smtp_connection(self, config: Dict[str, Any] = None) -> bool:
        """
        Test SMTP connection (placeholder implementation).
        
        Args:
            config: Optional SMTP configuration (uses saved config if not provided)
            
        Returns:
            True if connection test successful, False otherwise
        """
        try:
            # Use provided config or fall back to saved config
            test_config = config or self.email_config
            
            if not test_config:
                self.logger.error("No SMTP configuration available for testing")
                return False
            
            # Validate configuration
            is_valid, validation_message = self.validate_smtp_config(test_config)
            if not is_valid:
                self.logger.error(f"Invalid SMTP configuration for testing: {validation_message}")
                return False
            
            smtp_server = test_config.get("smtp_server")
            port = test_config.get("port", self.default_smtp_port)
            
            self.logger.info(f"Testing SMTP connection to {smtp_server}:{port}")
            
            # PLACEHOLDER IMPLEMENTATION
            # In a real implementation, this would:
            # 1. Attempt to connect to SMTP server
            # 2. Test authentication
            # 3. Return actual connection status
            
            self.logger.info(f"PLACEHOLDER: Connection test to {smtp_server}:{port} successful")
            
            # Publish connection test event
            if self.event_bus:
                self.event_bus.publish("email.connection_tested", {
                    "server": smtp_server,
                    "port": port,
                    "success": True
                })
            
            return True
            
        except Exception as e:
            self.logger.error(f"Error testing SMTP connection: {e}")
            
            # Publish connection test failure event
            if self.event_bus:
                self.event_bus.publish("email.connection_test_failed", {
                    "error": str(e)
                })
            
            return False
    
    def _fetch_gmail_emails(self, max_results: int = 10, use_cache: bool = True) -> List[Dict[str, Any]]:
        """
        Fetch emails from Gmail API using GmailClient with caching and error handling.
        
        Args:
            max_results: Maximum number of emails to fetch (default: 10)
            use_cache: Whether to use cached results if available (default: True)
            
        Returns:
            List of email dictionaries in internal format
            
        Raises:
            GmailAPIError: If Gmail API operations fail
            GmailAuthError: If authentication fails
        """
        try:
            # Check if Gmail client is available and authenticated
            if not self.gmail_client:
                raise GmailAPIError("Gmail client not initialized. Please authenticate with Gmail OAuth first.")
            
            # Check cache if enabled
            if use_cache and self._is_cache_valid():
                self.logger.info(f"Returning {len(self._email_cache.get('emails', []))} cached emails")
                return self._email_cache.get('emails', [])
            
            # Implement rate limiting
            self._enforce_rate_limit()
            
            self.logger.info(f"Fetching up to {max_results} emails from Gmail API")
            
            # Fetch emails from Gmail API
            gmail_emails = self.gmail_client.fetch_unread_emails(max_results=max_results)
            
            # Convert Gmail API format to internal email format
            internal_emails = []
            for gmail_email in gmail_emails:
                try:
                    internal_email = self._convert_gmail_to_internal_format(gmail_email)
                    # Only add if conversion was successful (no error field)
                    if 'error' not in internal_email:
                        internal_emails.append(internal_email)
                    else:
                        self.logger.warning(f"Skipping email {gmail_email.get('id', 'unknown')} due to conversion error: {internal_email.get('error')}")
                except Exception as e:
                    self.logger.warning(f"Failed to convert email {gmail_email.get('id', 'unknown')}: {e}")
                    continue
            
            # Update cache
            self._update_email_cache(internal_emails)
            
            # Update last fetch time
            self._last_fetch_time = datetime.now()
            
            self.logger.info(f"Successfully fetched {len(internal_emails)} emails from Gmail API")
            
            # Publish email fetched event
            if self.event_bus:
                self.event_bus.publish("email.gmail_fetched", {
                    "count": len(internal_emails),
                    "timestamp": self._last_fetch_time.isoformat(),
                    "cached": False
                })
            
            return internal_emails
            
        except GmailAPIError as e:
            # Handle specific Gmail API errors
            error_msg = f"Gmail API error fetching emails: {str(e)}"
            self.logger.error(error_msg)
            
            # Check for rate limiting errors
            if "quota" in str(e).lower() or "rate" in str(e).lower():
                self.logger.warning("Gmail API rate limit or quota exceeded, implementing backoff")
                self._handle_rate_limit_error()
            
            # Publish error event
            if self.event_bus:
                self.event_bus.publish("email.gmail_fetch_error", {
                    "error": str(e),
                    "error_type": "api_error",
                    "timestamp": datetime.now().isoformat()
                })
            
            raise
            
        except GmailAuthError as e:
            # Handle authentication errors
            error_msg = f"Gmail authentication error: {str(e)}"
            self.logger.error(error_msg)
            
            # Publish auth error event
            if self.event_bus:
                self.event_bus.publish("email.gmail_auth_error", {
                    "error": str(e),
                    "timestamp": datetime.now().isoformat()
                })
            
            raise
            
        except Exception as e:
            # Handle unexpected errors
            error_msg = f"Unexpected error fetching Gmail emails: {str(e)}"
            self.logger.error(error_msg)
            
            # Publish general error event
            if self.event_bus:
                self.event_bus.publish("email.gmail_fetch_error", {
                    "error": str(e),
                    "error_type": "unexpected_error",
                    "timestamp": datetime.now().isoformat()
                })
            
            raise GmailAPIError(error_msg)
    
    def _convert_gmail_to_internal_format(self, gmail_email: Dict[str, Any]) -> Dict[str, Any]:
        """
        Convert Gmail API email format to internal email format.
        
        Args:
            gmail_email: Email dictionary from Gmail API
            
        Returns:
            Email dictionary in internal format
        """
        try:
            # Parse timestamp from Gmail internal date (milliseconds since epoch)
            timestamp_ms = int(gmail_email.get('timestamp', '0'))
            timestamp_dt = datetime.fromtimestamp(timestamp_ms / 1000) if timestamp_ms > 0 else datetime.now()
            
            # Extract sender name and email from "Name <email@domain.com>" format
            sender_raw = gmail_email.get('sender', 'Unknown Sender')
            sender_name, sender_email = self._parse_email_address(sender_raw)
            
            # Extract recipient name and email
            to_raw = gmail_email.get('to', '')
            to_name, to_email = self._parse_email_address(to_raw)
            
            # Convert to internal format
            internal_email = {
                # Core email data
                'id': gmail_email.get('id', ''),
                'thread_id': gmail_email.get('thread_id', ''),
                'subject': gmail_email.get('subject', 'No Subject'),
                'body': gmail_email.get('body', ''),
                'snippet': gmail_email.get('snippet', ''),
                
                # Sender information
                'sender': sender_email,
                'sender_name': sender_name,
                'sender_display': sender_raw,
                
                # Recipient information
                'to': to_email,
                'to_name': to_name,
                'to_display': to_raw,
                
                # Timestamps
                'date': gmail_email.get('date', ''),
                'timestamp': timestamp_dt.isoformat(),
                'received_time': timestamp_dt,
                
                # Status flags
                'unread': gmail_email.get('unread', False),
                'starred': False,  # Could be extended to check for STARRED label
                'important': False,  # Could be extended to check for IMPORTANT label
                
                # Gmail-specific data
                'labels': gmail_email.get('labels', []),
                'gmail_id': gmail_email.get('id', ''),
                'gmail_thread_id': gmail_email.get('thread_id', ''),
                
                # Internal metadata
                'source': 'gmail_api',
                'fetched_at': datetime.now().isoformat(),
                'auth_method': 'gmail_oauth'
            }
            
            return internal_email
            
        except Exception as e:
            self.logger.error(f"Error converting Gmail email to internal format: {e}")
            # Return minimal email data to prevent complete failure
            return {
                'id': gmail_email.get('id', 'unknown'),
                'subject': gmail_email.get('subject', 'Error parsing email'),
                'sender': gmail_email.get('sender', 'Unknown'),
                'body': f"Error parsing email: {str(e)}",
                'timestamp': datetime.now().isoformat(),
                'unread': True,
                'source': 'gmail_api',
                'error': str(e)
            }
    
    def _parse_email_address(self, email_string: str) -> tuple[str, str]:
        """
        Parse email address string to extract name and email.
        
        Args:
            email_string: Email string in format "Name <email@domain.com>" or "email@domain.com"
            
        Returns:
            Tuple of (name, email)
        """
        try:
            if not email_string:
                return "Unknown", ""
            
            email_string = email_string.strip()
            
            # Check for "Name <email@domain.com>" format
            if '<' in email_string and '>' in email_string:
                # Extract name and email
                name_part = email_string.split('<')[0].strip()
                email_part = email_string.split('<')[1].split('>')[0].strip()
                
                # Clean up name (remove quotes if present)
                name_part = name_part.strip('"').strip("'").strip()
                
                return name_part or "Unknown", email_part
            else:
                # Just email address
                return "", email_string
                
        except Exception as e:
            self.logger.warning(f"Error parsing email address '{email_string}': {e}")
            return "Unknown", email_string
    
    def _is_cache_valid(self) -> bool:
        """
        Check if the email cache is still valid.
        
        Returns:
            True if cache is valid, False otherwise
        """
        if not self._email_cache or 'timestamp' not in self._email_cache:
            return False
        
        cache_time = datetime.fromisoformat(self._email_cache['timestamp'])
        expiry_time = cache_time + timedelta(minutes=self._cache_expiry_minutes)
        
        return datetime.now() < expiry_time
    
    def _update_email_cache(self, emails: List[Dict[str, Any]]) -> None:
        """
        Update the email cache with new emails.
        
        Args:
            emails: List of email dictionaries to cache
        """
        self._email_cache = {
            'emails': emails,
            'timestamp': datetime.now().isoformat(),
            'count': len(emails)
        }
        
        self.logger.debug(f"Email cache updated with {len(emails)} emails")
    
    def _enforce_rate_limit(self) -> None:
        """
        Enforce rate limiting for Gmail API calls.
        """
        if self._last_api_call_time:
            time_since_last_call = datetime.now() - self._last_api_call_time
            min_delay = timedelta(seconds=self._rate_limit_delay)
            
            if time_since_last_call < min_delay:
                sleep_time = (min_delay - time_since_last_call).total_seconds()
                self.logger.debug(f"Rate limiting: sleeping for {sleep_time:.2f} seconds")
                time.sleep(sleep_time)
        
        self._last_api_call_time = datetime.now()
    
    def _handle_rate_limit_error(self) -> None:
        """
        Handle rate limit errors by increasing delay and clearing cache.
        """
        # Increase rate limit delay
        self._rate_limit_delay = min(self._rate_limit_delay * 2, 60.0)  # Max 60 seconds
        
        # Clear cache to prevent stale data
        self._email_cache = {}
        
        self.logger.warning(f"Rate limit error handled, new delay: {self._rate_limit_delay} seconds")
    
    def clear_email_cache(self) -> None:
        """
        Clear the email cache manually.
        """
        self._email_cache = {}
        self._last_fetch_time = None
        self.logger.info("Email cache cleared manually")
        
        # Publish cache cleared event
        if self.event_bus:
            self.event_bus.publish("email.cache_cleared", {
                "timestamp": datetime.now().isoformat(),
                "manual": True
            })
    
    def get_cached_email_count(self) -> int:
        """
        Get the number of emails currently in cache.
        
        Returns:
            Number of cached emails
        """
        return len(self._email_cache.get('emails', []))
    
    def is_cache_expired(self) -> bool:
        """
        Check if the email cache has expired.
        
        Returns:
            True if cache is expired, False otherwise
        """
        return not self._is_cache_valid()
    
    def mark_gmail_as_read(self, email_id: str) -> tuple[bool, str]:
        """
        Mark a Gmail email as read using Gmail API.
        
        Args:
            email_id: Gmail message ID to mark as read
            
        Returns:
            Tuple of (success, message)
        """
        try:
            if not self.gmail_client:
                error_msg = "Gmail client not initialized. Please authenticate with Gmail OAuth first."
                self.logger.error(error_msg)
                return False, error_msg
            
            if self.auth_method != "gmail_oauth":
                error_msg = "Gmail OAuth authentication required for marking emails as read"
                self.logger.error(error_msg)
                return False, error_msg
            
            self.logger.info(f"Marking Gmail email {email_id} as read")
            
            # Implement rate limiting
            self._enforce_rate_limit()
            
            # Mark email as read using Gmail client
            success = self.gmail_client.mark_as_read(email_id)
            
            if success:
                success_msg = f"Email {email_id} marked as read successfully"
                self.logger.info(success_msg)
                
                # Update cache if email exists in cache
                self._update_email_status_in_cache(email_id, {'unread': False})
                
                # Publish email marked as read event
                if self.event_bus:
                    self.event_bus.publish("email.marked_as_read", {
                        "email_id": email_id,
                        "timestamp": datetime.now().isoformat(),
                        "method": "gmail_api"
                    })
                
                return True, success_msg
            else:
                error_msg = f"Failed to mark email {email_id} as read"
                self.logger.error(error_msg)
                return False, error_msg
                
        except GmailAPIError as e:
            error_msg = f"Gmail API error marking email as read: {str(e)}"
            self.logger.error(error_msg)
            
            # Publish error event
            if self.event_bus:
                self.event_bus.publish("email.mark_read_error", {
                    "email_id": email_id,
                    "error": str(e),
                    "error_type": "api_error",
                    "timestamp": datetime.now().isoformat()
                })
            
            return False, error_msg
            
        except Exception as e:
            error_msg = f"Unexpected error marking email as read: {str(e)}"
            self.logger.error(error_msg)
            
            # Publish error event
            if self.event_bus:
                self.event_bus.publish("email.mark_read_error", {
                    "email_id": email_id,
                    "error": str(e),
                    "error_type": "unexpected_error",
                    "timestamp": datetime.now().isoformat()
                })
            
            return False, error_msg
    
    def add_gmail_label(self, email_id: str, label_name: str) -> tuple[bool, str]:
        """
        Add a label to a Gmail email.
        
        Args:
            email_id: Gmail message ID
            label_name: Name of the label to add
            
        Returns:
            Tuple of (success, message)
        """
        try:
            if not self.gmail_client:
                error_msg = "Gmail client not initialized. Please authenticate with Gmail OAuth first."
                self.logger.error(error_msg)
                return False, error_msg
            
            if self.auth_method != "gmail_oauth":
                error_msg = "Gmail OAuth authentication required for email labeling"
                self.logger.error(error_msg)
                return False, error_msg
            
            self.logger.info(f"Adding label '{label_name}' to Gmail email {email_id}")
            
            # Implement rate limiting
            self._enforce_rate_limit()
            
            # Add label using Gmail client
            success = self.gmail_client.add_label(email_id, label_name)
            
            if success:
                success_msg = f"Label '{label_name}' added to email {email_id} successfully"
                self.logger.info(success_msg)
                
                # Update cache if email exists in cache
                self._add_label_to_cache(email_id, label_name)
                
                # Publish email labeled event
                if self.event_bus:
                    self.event_bus.publish("email.labeled", {
                        "email_id": email_id,
                        "label": label_name,
                        "action": "add",
                        "timestamp": datetime.now().isoformat(),
                        "method": "gmail_api"
                    })
                
                return True, success_msg
            else:
                error_msg = f"Failed to add label '{label_name}' to email {email_id}"
                self.logger.error(error_msg)
                return False, error_msg
                
        except GmailAPIError as e:
            error_msg = f"Gmail API error adding label: {str(e)}"
            self.logger.error(error_msg)
            
            # Publish error event
            if self.event_bus:
                self.event_bus.publish("email.label_error", {
                    "email_id": email_id,
                    "label": label_name,
                    "action": "add",
                    "error": str(e),
                    "error_type": "api_error",
                    "timestamp": datetime.now().isoformat()
                })
            
            return False, error_msg
            
        except Exception as e:
            error_msg = f"Unexpected error adding label: {str(e)}"
            self.logger.error(error_msg)
            
            # Publish error event
            if self.event_bus:
                self.event_bus.publish("email.label_error", {
                    "email_id": email_id,
                    "label": label_name,
                    "action": "add",
                    "error": str(e),
                    "error_type": "unexpected_error",
                    "timestamp": datetime.now().isoformat()
                })
            
            return False, error_msg
    
    def remove_gmail_label(self, email_id: str, label_name: str) -> tuple[bool, str]:
        """
        Remove a label from a Gmail email.
        
        Args:
            email_id: Gmail message ID
            label_name: Name of the label to remove
            
        Returns:
            Tuple of (success, message)
        """
        try:
            if not self.gmail_client:
                error_msg = "Gmail client not initialized. Please authenticate with Gmail OAuth first."
                self.logger.error(error_msg)
                return False, error_msg
            
            if self.auth_method != "gmail_oauth":
                error_msg = "Gmail OAuth authentication required for email labeling"
                self.logger.error(error_msg)
                return False, error_msg
            
            self.logger.info(f"Removing label '{label_name}' from Gmail email {email_id}")
            
            # Implement rate limiting
            self._enforce_rate_limit()
            
            # Remove label using Gmail client
            success = self.gmail_client.remove_label(email_id, label_name)
            
            if success:
                success_msg = f"Label '{label_name}' removed from email {email_id} successfully"
                self.logger.info(success_msg)
                
                # Update cache if email exists in cache
                self._remove_label_from_cache(email_id, label_name)
                
                # Publish email label removed event
                if self.event_bus:
                    self.event_bus.publish("email.labeled", {
                        "email_id": email_id,
                        "label": label_name,
                        "action": "remove",
                        "timestamp": datetime.now().isoformat(),
                        "method": "gmail_api"
                    })
                
                return True, success_msg
            else:
                error_msg = f"Failed to remove label '{label_name}' from email {email_id}"
                self.logger.error(error_msg)
                return False, error_msg
                
        except GmailAPIError as e:
            error_msg = f"Gmail API error removing label: {str(e)}"
            self.logger.error(error_msg)
            
            # Publish error event
            if self.event_bus:
                self.event_bus.publish("email.label_error", {
                    "email_id": email_id,
                    "label": label_name,
                    "action": "remove",
                    "error": str(e),
                    "error_type": "api_error",
                    "timestamp": datetime.now().isoformat()
                })
            
            return False, error_msg
            
        except Exception as e:
            error_msg = f"Unexpected error removing label: {str(e)}"
            self.logger.error(error_msg)
            
            # Publish error event
            if self.event_bus:
                self.event_bus.publish("email.label_error", {
                    "email_id": email_id,
                    "label": label_name,
                    "action": "remove",
                    "error": str(e),
                    "error_type": "unexpected_error",
                    "timestamp": datetime.now().isoformat()
                })
            
            return False, error_msg
    
    def batch_mark_emails_as_read(self, email_ids: List[str]) -> Dict[str, Any]:
        """
        Mark multiple Gmail emails as read in batch.
        
        Args:
            email_ids: List of Gmail message IDs to mark as read
            
        Returns:
            Dictionary with batch operation results
        """
        try:
            if not email_ids:
                return {
                    'success': True,
                    'total': 0,
                    'successful': 0,
                    'failed': 0,
                    'errors': [],
                    'message': 'No emails to process'
                }
            
            if not self.gmail_client:
                error_msg = "Gmail client not initialized. Please authenticate with Gmail OAuth first."
                self.logger.error(error_msg)
                return {
                    'success': False,
                    'total': len(email_ids),
                    'successful': 0,
                    'failed': len(email_ids),
                    'errors': [error_msg],
                    'message': error_msg
                }
            
            if self.auth_method != "gmail_oauth":
                error_msg = "Gmail OAuth authentication required for batch email operations"
                self.logger.error(error_msg)
                return {
                    'success': False,
                    'total': len(email_ids),
                    'successful': 0,
                    'failed': len(email_ids),
                    'errors': [error_msg],
                    'message': error_msg
                }
            
            self.logger.info(f"Batch marking {len(email_ids)} emails as read")
            
            successful_ids = []
            failed_ids = []
            errors = []
            
            # Process emails in batches to respect rate limits
            batch_size = 10  # Process 10 emails at a time
            for i in range(0, len(email_ids), batch_size):
                batch = email_ids[i:i + batch_size]
                
                for email_id in batch:
                    try:
                        # Implement rate limiting for each request
                        self._enforce_rate_limit()
                        
                        success = self.gmail_client.mark_as_read(email_id)
                        
                        if success:
                            successful_ids.append(email_id)
                            # Update cache if email exists in cache
                            self._update_email_status_in_cache(email_id, {'unread': False})
                        else:
                            failed_ids.append(email_id)
                            errors.append(f"Failed to mark email {email_id} as read")
                            
                    except GmailAPIError as e:
                        failed_ids.append(email_id)
                        error_msg = f"Gmail API error for email {email_id}: {str(e)}"
                        errors.append(error_msg)
                        self.logger.error(error_msg)
                        
                    except Exception as e:
                        failed_ids.append(email_id)
                        error_msg = f"Unexpected error for email {email_id}: {str(e)}"
                        errors.append(error_msg)
                        self.logger.error(error_msg)
                
                # Small delay between batches to be respectful to the API
                if i + batch_size < len(email_ids):
                    time.sleep(0.5)
            
            # Prepare results
            total = len(email_ids)
            successful = len(successful_ids)
            failed = len(failed_ids)
            overall_success = failed == 0
            
            result = {
                'success': overall_success,
                'total': total,
                'successful': successful,
                'failed': failed,
                'successful_ids': successful_ids,
                'failed_ids': failed_ids,
                'errors': errors,
                'message': f"Batch operation completed: {successful}/{total} emails marked as read"
            }
            
            self.logger.info(f"Batch mark as read completed: {successful}/{total} successful")
            
            # Publish batch operation event
            if self.event_bus:
                self.event_bus.publish("email.batch_marked_as_read", {
                    "total": total,
                    "successful": successful,
                    "failed": failed,
                    "timestamp": datetime.now().isoformat(),
                    "method": "gmail_api"
                })
            
            return result
            
        except Exception as e:
            error_msg = f"Unexpected error in batch mark as read operation: {str(e)}"
            self.logger.error(error_msg)
            
            # Publish error event
            if self.event_bus:
                self.event_bus.publish("email.batch_operation_error", {
                    "operation": "mark_as_read",
                    "total": len(email_ids) if email_ids else 0,
                    "error": str(e),
                    "timestamp": datetime.now().isoformat()
                })
            
            return {
                'success': False,
                'total': len(email_ids) if email_ids else 0,
                'successful': 0,
                'failed': len(email_ids) if email_ids else 0,
                'errors': [error_msg],
                'message': error_msg
            }
    
    def batch_add_labels(self, email_ids: List[str], label_names: List[str]) -> Dict[str, Any]:
        """
        Add labels to multiple Gmail emails in batch.
        
        Args:
            email_ids: List of Gmail message IDs
            label_names: List of label names to add
            
        Returns:
            Dictionary with batch operation results
        """
        try:
            if not email_ids or not label_names:
                return {
                    'success': True,
                    'total': 0,
                    'successful': 0,
                    'failed': 0,
                    'errors': [],
                    'message': 'No emails or labels to process'
                }
            
            if not self.gmail_client:
                error_msg = "Gmail client not initialized. Please authenticate with Gmail OAuth first."
                self.logger.error(error_msg)
                return {
                    'success': False,
                    'total': len(email_ids),
                    'successful': 0,
                    'failed': len(email_ids),
                    'errors': [error_msg],
                    'message': error_msg
                }
            
            if self.auth_method != "gmail_oauth":
                error_msg = "Gmail OAuth authentication required for batch email operations"
                self.logger.error(error_msg)
                return {
                    'success': False,
                    'total': len(email_ids),
                    'successful': 0,
                    'failed': len(email_ids),
                    'errors': [error_msg],
                    'message': error_msg
                }
            
            self.logger.info(f"Batch adding labels {label_names} to {len(email_ids)} emails")
            
            successful_operations = []
            failed_operations = []
            errors = []
            
            # Process emails in batches to respect rate limits
            batch_size = 5  # Smaller batch size for label operations
            for i in range(0, len(email_ids), batch_size):
                batch = email_ids[i:i + batch_size]
                
                for email_id in batch:
                    for label_name in label_names:
                        try:
                            # Implement rate limiting for each request
                            self._enforce_rate_limit()
                            
                            success = self.gmail_client.add_label(email_id, label_name)
                            
                            if success:
                                successful_operations.append(f"{email_id}:{label_name}")
                                # Update cache if email exists in cache
                                self._add_label_to_cache(email_id, label_name)
                            else:
                                failed_operations.append(f"{email_id}:{label_name}")
                                errors.append(f"Failed to add label '{label_name}' to email {email_id}")
                                
                        except GmailAPIError as e:
                            failed_operations.append(f"{email_id}:{label_name}")
                            error_msg = f"Gmail API error adding label '{label_name}' to email {email_id}: {str(e)}"
                            errors.append(error_msg)
                            self.logger.error(error_msg)
                            
                        except Exception as e:
                            failed_operations.append(f"{email_id}:{label_name}")
                            error_msg = f"Unexpected error adding label '{label_name}' to email {email_id}: {str(e)}"
                            errors.append(error_msg)
                            self.logger.error(error_msg)
                
                # Small delay between batches to be respectful to the API
                if i + batch_size < len(email_ids):
                    time.sleep(0.5)
            
            # Prepare results
            total_operations = len(email_ids) * len(label_names)
            successful = len(successful_operations)
            failed = len(failed_operations)
            overall_success = failed == 0
            
            result = {
                'success': overall_success,
                'total_operations': total_operations,
                'successful': successful,
                'failed': failed,
                'successful_operations': successful_operations,
                'failed_operations': failed_operations,
                'errors': errors,
                'message': f"Batch label operation completed: {successful}/{total_operations} operations successful"
            }
            
            self.logger.info(f"Batch add labels completed: {successful}/{total_operations} successful")
            
            # Publish batch operation event
            if self.event_bus:
                self.event_bus.publish("email.batch_labeled", {
                    "action": "add",
                    "labels": label_names,
                    "email_count": len(email_ids),
                    "total_operations": total_operations,
                    "successful": successful,
                    "failed": failed,
                    "timestamp": datetime.now().isoformat(),
                    "method": "gmail_api"
                })
            
            return result
            
        except Exception as e:
            error_msg = f"Unexpected error in batch add labels operation: {str(e)}"
            self.logger.error(error_msg)
            
            # Publish error event
            if self.event_bus:
                self.event_bus.publish("email.batch_operation_error", {
                    "operation": "add_labels",
                    "email_count": len(email_ids) if email_ids else 0,
                    "labels": label_names if label_names else [],
                    "error": str(e),
                    "timestamp": datetime.now().isoformat()
                })
            
            return {
                'success': False,
                'total_operations': len(email_ids) * len(label_names) if email_ids and label_names else 0,
                'successful': 0,
                'failed': len(email_ids) * len(label_names) if email_ids and label_names else 0,
                'errors': [error_msg],
                'message': error_msg
            }
    
    def batch_remove_labels(self, email_ids: List[str], label_names: List[str]) -> Dict[str, Any]:
        """
        Remove labels from multiple Gmail emails in batch.
        
        Args:
            email_ids: List of Gmail message IDs
            label_names: List of label names to remove
            
        Returns:
            Dictionary with batch operation results
        """
        try:
            if not email_ids or not label_names:
                return {
                    'success': True,
                    'total': 0,
                    'successful': 0,
                    'failed': 0,
                    'errors': [],
                    'message': 'No emails or labels to process'
                }
            
            if not self.gmail_client:
                error_msg = "Gmail client not initialized. Please authenticate with Gmail OAuth first."
                self.logger.error(error_msg)
                return {
                    'success': False,
                    'total': len(email_ids),
                    'successful': 0,
                    'failed': len(email_ids),
                    'errors': [error_msg],
                    'message': error_msg
                }
            
            if self.auth_method != "gmail_oauth":
                error_msg = "Gmail OAuth authentication required for batch email operations"
                self.logger.error(error_msg)
                return {
                    'success': False,
                    'total': len(email_ids),
                    'successful': 0,
                    'failed': len(email_ids),
                    'errors': [error_msg],
                    'message': error_msg
                }
            
            self.logger.info(f"Batch removing labels {label_names} from {len(email_ids)} emails")
            
            successful_operations = []
            failed_operations = []
            errors = []
            
            # Process emails in batches to respect rate limits
            batch_size = 5  # Smaller batch size for label operations
            for i in range(0, len(email_ids), batch_size):
                batch = email_ids[i:i + batch_size]
                
                for email_id in batch:
                    for label_name in label_names:
                        try:
                            # Implement rate limiting for each request
                            self._enforce_rate_limit()
                            
                            success = self.gmail_client.remove_label(email_id, label_name)
                            
                            if success:
                                successful_operations.append(f"{email_id}:{label_name}")
                                # Update cache if email exists in cache
                                self._remove_label_from_cache(email_id, label_name)
                            else:
                                failed_operations.append(f"{email_id}:{label_name}")
                                errors.append(f"Failed to remove label '{label_name}' from email {email_id}")
                                
                        except GmailAPIError as e:
                            failed_operations.append(f"{email_id}:{label_name}")
                            error_msg = f"Gmail API error removing label '{label_name}' from email {email_id}: {str(e)}"
                            errors.append(error_msg)
                            self.logger.error(error_msg)
                            
                        except Exception as e:
                            failed_operations.append(f"{email_id}:{label_name}")
                            error_msg = f"Unexpected error removing label '{label_name}' from email {email_id}: {str(e)}"
                            errors.append(error_msg)
                            self.logger.error(error_msg)
                
                # Small delay between batches to be respectful to the API
                if i + batch_size < len(email_ids):
                    time.sleep(0.5)
            
            # Prepare results
            total_operations = len(email_ids) * len(label_names)
            successful = len(successful_operations)
            failed = len(failed_operations)
            overall_success = failed == 0
            
            result = {
                'success': overall_success,
                'total_operations': total_operations,
                'successful': successful,
                'failed': failed,
                'successful_operations': successful_operations,
                'failed_operations': failed_operations,
                'errors': errors,
                'message': f"Batch label removal completed: {successful}/{total_operations} operations successful"
            }
            
            self.logger.info(f"Batch remove labels completed: {successful}/{total_operations} successful")
            
            # Publish batch operation event
            if self.event_bus:
                self.event_bus.publish("email.batch_labeled", {
                    "action": "remove",
                    "labels": label_names,
                    "email_count": len(email_ids),
                    "total_operations": total_operations,
                    "successful": successful,
                    "failed": failed,
                    "timestamp": datetime.now().isoformat(),
                    "method": "gmail_api"
                })
            
            return result
            
        except Exception as e:
            error_msg = f"Unexpected error in batch remove labels operation: {str(e)}"
            self.logger.error(error_msg)
            
            # Publish error event
            if self.event_bus:
                self.event_bus.publish("email.batch_operation_error", {
                    "operation": "remove_labels",
                    "email_count": len(email_ids) if email_ids else 0,
                    "labels": label_names if label_names else [],
                    "error": str(e),
                    "timestamp": datetime.now().isoformat()
                })
            
            return {
                'success': False,
                'total_operations': len(email_ids) * len(label_names) if email_ids and label_names else 0,
                'successful': 0,
                'failed': len(email_ids) * len(label_names) if email_ids and label_names else 0,
                'errors': [error_msg],
                'message': error_msg
            }
    
    def _update_email_status_in_cache(self, email_id: str, status_updates: Dict[str, Any]) -> None:
        """
        Update email status in cache.
        
        Args:
            email_id: Gmail message ID
            status_updates: Dictionary of status fields to update
        """
        try:
            if not self._email_cache or 'emails' not in self._email_cache:
                return
            
            emails = self._email_cache['emails']
            for email in emails:
                if email.get('gmail_id') == email_id or email.get('id') == email_id:
                    email.update(status_updates)
                    self.logger.debug(f"Updated email {email_id} status in cache: {status_updates}")
                    break
                    
        except Exception as e:
            self.logger.warning(f"Failed to update email status in cache: {e}")
    
    def _add_label_to_cache(self, email_id: str, label_name: str) -> None:
        """
        Add label to email in cache.
        
        Args:
            email_id: Gmail message ID
            label_name: Label name to add
        """
        try:
            if not self._email_cache or 'emails' not in self._email_cache:
                return
            
            emails = self._email_cache['emails']
            for email in emails:
                if email.get('gmail_id') == email_id or email.get('id') == email_id:
                    labels = email.get('labels', [])
                    if label_name not in labels:
                        labels.append(label_name)
                        email['labels'] = labels
                        self.logger.debug(f"Added label '{label_name}' to email {email_id} in cache")
                    break
                    
        except Exception as e:
            self.logger.warning(f"Failed to add label to email in cache: {e}")
    
    def _remove_label_from_cache(self, email_id: str, label_name: str) -> None:
        """
        Remove label from email in cache.
        
        Args:
            email_id: Gmail message ID
            label_name: Label name to remove
        """
        try:
            if not self._email_cache or 'emails' not in self._email_cache:
                return
            
            emails = self._email_cache['emails']
            for email in emails:
                if email.get('gmail_id') == email_id or email.get('id') == email_id:
                    labels = email.get('labels', [])
                    if label_name in labels:
                        labels.remove(label_name)
                        email['labels'] = labels
                        self.logger.debug(f"Removed label '{label_name}' from email {email_id} in cache")
                    break
                    
        except Exception as e:
            self.logger.warning(f"Failed to remove label from email in cache: {e}")