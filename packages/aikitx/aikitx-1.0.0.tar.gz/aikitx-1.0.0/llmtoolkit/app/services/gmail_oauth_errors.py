"""
Gmail OAuth Error Handling

This module provides comprehensive error handling for Gmail OAuth 2.0 flows,
including specific error types, user-friendly messages, retry logic, and
error recovery suggestions.
"""

import logging
import time
from typing import Dict, Any, List, Optional, Tuple
from enum import Enum
from dataclasses import dataclass


class GmailOAuthErrorType(Enum):
    """Enumeration of Gmail OAuth error types."""
    
    # Authentication Errors
    INVALID_CREDENTIALS = "invalid_credentials"
    OAUTH_FLOW_CANCELLED = "oauth_flow_cancelled"
    TOKEN_REFRESH_FAILED = "token_refresh_failed"
    INVALID_TOKEN = "invalid_token"
    EXPIRED_TOKEN = "expired_token"
    
    # API Errors
    RATE_LIMIT_EXCEEDED = "rate_limit_exceeded"
    QUOTA_EXCEEDED = "quota_exceeded"
    INSUFFICIENT_PERMISSIONS = "insufficient_permissions"
    API_DISABLED = "api_disabled"
    
    # Network Errors
    NETWORK_TIMEOUT = "network_timeout"
    CONNECTION_ERROR = "connection_error"
    DNS_RESOLUTION_ERROR = "dns_resolution_error"
    
    # Configuration Errors
    MISSING_CREDENTIALS_FILE = "missing_credentials_file"
    INVALID_CREDENTIALS_FORMAT = "invalid_credentials_format"
    MISSING_OAUTH_SCOPES = "missing_oauth_scopes"
    INVALID_REDIRECT_URI = "invalid_redirect_uri"
    
    # Server Errors
    GMAIL_API_ERROR = "gmail_api_error"
    GOOGLE_SERVER_ERROR = "google_server_error"
    SERVICE_UNAVAILABLE = "service_unavailable"
    
    # Unknown/Generic Errors
    UNKNOWN_ERROR = "unknown_error"


@dataclass
class RetryConfig:
    """Configuration for retry logic."""
    max_attempts: int = 3
    base_delay: float = 1.0  # Base delay in seconds
    max_delay: float = 60.0  # Maximum delay in seconds
    exponential_base: float = 2.0  # Exponential backoff base
    jitter: bool = True  # Add random jitter to delays


class GmailOAuthError(Exception):
    """
    Comprehensive Gmail OAuth error with specific error types and recovery suggestions.
    
    This exception class provides detailed error information, user-friendly messages,
    and actionable recovery suggestions for Gmail OAuth 2.0 operations.
    """
    
    def __init__(
        self,
        error_type: GmailOAuthErrorType,
        message: str,
        details: Optional[str] = None,
        original_error: Optional[Exception] = None,
        retry_after: Optional[int] = None,
        error_code: Optional[str] = None
    ):
        """
        Initialize Gmail OAuth error.
        
        Args:
            error_type: Type of OAuth error
            message: User-friendly error message
            details: Additional error details
            original_error: Original exception that caused this error
            retry_after: Seconds to wait before retrying (for rate limiting)
            error_code: Specific error code from API response
        """
        self.error_type = error_type
        self.message = message
        self.details = details
        self.original_error = original_error
        self.retry_after = retry_after
        self.error_code = error_code
        self.timestamp = time.time()
        
        # Create full error message
        full_message = f"[{error_type.value}] {message}"
        if details:
            full_message += f" - {details}"
        
        super().__init__(full_message)
    
    def is_retryable(self) -> bool:
        """
        Check if this error is retryable.
        
        Returns:
            True if the error can be retried, False otherwise
        """
        retryable_errors = {
            GmailOAuthErrorType.RATE_LIMIT_EXCEEDED,
            GmailOAuthErrorType.NETWORK_TIMEOUT,
            GmailOAuthErrorType.CONNECTION_ERROR,
            GmailOAuthErrorType.DNS_RESOLUTION_ERROR,
            GmailOAuthErrorType.GOOGLE_SERVER_ERROR,
            GmailOAuthErrorType.SERVICE_UNAVAILABLE,
            GmailOAuthErrorType.TOKEN_REFRESH_FAILED
        }
        return self.error_type in retryable_errors
    
    def get_user_friendly_message(self) -> str:
        """
        Get a user-friendly error message.
        
        Returns:
            User-friendly error message
        """
        return self.message
    
    def get_recovery_suggestions(self) -> List[str]:
        """
        Get actionable recovery suggestions for this error.
        
        Returns:
            List of recovery suggestions
        """
        return GmailOAuthErrorHandler.get_recovery_suggestions(self.error_type)


class GmailOAuthErrorHandler:
    """
    Handler for Gmail OAuth errors with retry logic and recovery suggestions.
    """
    
    def __init__(self, retry_config: Optional[RetryConfig] = None):
        """
        Initialize the error handler.
        
        Args:
            retry_config: Configuration for retry logic
        """
        self.logger = logging.getLogger("gmail_oauth_error_handler")
        self.retry_config = retry_config or RetryConfig()
        self._retry_counts: Dict[str, int] = {}
    
    @staticmethod
    def create_error_from_exception(
        exception: Exception,
        context: str = ""
    ) -> GmailOAuthError:
        """
        Create a GmailOAuthError from a generic exception.
        
        Args:
            exception: Original exception
            context: Additional context about when the error occurred
            
        Returns:
            GmailOAuthError instance
        """
        error_type, message, details = GmailOAuthErrorHandler._classify_exception(exception)
        
        if context:
            details = f"{context}: {details}" if details else context
        
        return GmailOAuthError(
            error_type=error_type,
            message=message,
            details=details,
            original_error=exception
        )
    
    @staticmethod
    def _classify_exception(exception: Exception) -> Tuple[GmailOAuthErrorType, str, str]:
        """
        Classify a generic exception into a specific OAuth error type.
        
        Args:
            exception: Exception to classify
            
        Returns:
            Tuple of (error_type, user_message, details)
        """
        exception_str = str(exception).lower()
        exception_type = type(exception).__name__
        
        # Network-related errors
        if "timeout" in exception_str or "timed out" in exception_str:
            return (
                GmailOAuthErrorType.NETWORK_TIMEOUT,
                "Connection timed out while connecting to Gmail",
                f"Network timeout: {str(exception)}"
            )
        
        if "connection" in exception_str and ("refused" in exception_str or "failed" in exception_str):
            return (
                GmailOAuthErrorType.CONNECTION_ERROR,
                "Unable to connect to Gmail servers",
                f"Connection error: {str(exception)}"
            )
        
        if "dns" in exception_str or "name resolution" in exception_str:
            return (
                GmailOAuthErrorType.DNS_RESOLUTION_ERROR,
                "Unable to resolve Gmail server address",
                f"DNS error: {str(exception)}"
            )
        
        # OAuth-specific errors
        if "invalid_grant" in exception_str or "invalid grant" in exception_str:
            return (
                GmailOAuthErrorType.INVALID_TOKEN,
                "Your Gmail authentication has expired",
                "OAuth token is invalid or expired"
            )
        
        if "access_denied" in exception_str or "cancelled" in exception_str:
            return (
                GmailOAuthErrorType.OAUTH_FLOW_CANCELLED,
                "Gmail authentication was cancelled",
                "User cancelled the OAuth flow"
            )
        
        if "invalid_client" in exception_str:
            return (
                GmailOAuthErrorType.INVALID_CREDENTIALS,
                "Invalid Gmail application credentials",
                "OAuth client credentials are invalid"
            )
        
        # Rate limiting and quota errors
        if "rate limit" in exception_str or "quota" in exception_str:
            if "exceeded" in exception_str:
                return (
                    GmailOAuthErrorType.RATE_LIMIT_EXCEEDED,
                    "Gmail API rate limit exceeded",
                    "Too many requests to Gmail API"
                )
            else:
                return (
                    GmailOAuthErrorType.QUOTA_EXCEEDED,
                    "Gmail API quota exceeded",
                    "Daily quota limit reached"
                )
        
        # Permission errors
        if "insufficient" in exception_str and "permission" in exception_str:
            return (
                GmailOAuthErrorType.INSUFFICIENT_PERMISSIONS,
                "Insufficient permissions for Gmail access",
                "OAuth scopes do not include required permissions"
            )
        
        # File-related errors
        if "filenotfounderror" in exception_type.lower() or "no such file" in exception_str:
            return (
                GmailOAuthErrorType.MISSING_CREDENTIALS_FILE,
                "Gmail credentials file not found",
                f"Credentials file missing: {str(exception)}"
            )
        
        if "json" in exception_str and ("decode" in exception_str or "parse" in exception_str):
            return (
                GmailOAuthErrorType.INVALID_CREDENTIALS_FORMAT,
                "Invalid Gmail credentials file format",
                "Credentials file is not valid JSON"
            )
        
        # Server errors
        if "500" in exception_str or "502" in exception_str or "503" in exception_str:
            return (
                GmailOAuthErrorType.GOOGLE_SERVER_ERROR,
                "Gmail servers are experiencing issues",
                f"Server error: {str(exception)}"
            )
        
        if "service unavailable" in exception_str:
            return (
                GmailOAuthErrorType.SERVICE_UNAVAILABLE,
                "Gmail service is temporarily unavailable",
                "Service unavailable error"
            )
        
        # Default to unknown error
        return (
            GmailOAuthErrorType.UNKNOWN_ERROR,
            "An unexpected error occurred with Gmail",
            f"Unknown error: {str(exception)}"
        )
    
    @staticmethod
    def get_user_friendly_message(error_type: GmailOAuthErrorType) -> str:
        """
        Get a user-friendly message for an error type.
        
        Args:
            error_type: Type of OAuth error
            
        Returns:
            User-friendly error message
        """
        messages = {
            GmailOAuthErrorType.INVALID_CREDENTIALS: "Your Gmail application credentials are invalid. Please check your credentials.json file.",
            GmailOAuthErrorType.OAUTH_FLOW_CANCELLED: "Gmail authentication was cancelled. Please try again to complete the setup.",
            GmailOAuthErrorType.TOKEN_REFRESH_FAILED: "Unable to refresh your Gmail authentication. Please re-authenticate with Gmail.",
            GmailOAuthErrorType.INVALID_TOKEN: "Your Gmail authentication has expired. Please sign in again.",
            GmailOAuthErrorType.EXPIRED_TOKEN: "Your Gmail authentication has expired. Please sign in again.",
            
            GmailOAuthErrorType.RATE_LIMIT_EXCEEDED: "Too many requests to Gmail. Please wait a moment and try again.",
            GmailOAuthErrorType.QUOTA_EXCEEDED: "Gmail API quota exceeded. Please try again later or check your quota limits.",
            GmailOAuthErrorType.INSUFFICIENT_PERMISSIONS: "Insufficient permissions to access Gmail. Please check your OAuth scopes.",
            GmailOAuthErrorType.API_DISABLED: "Gmail API is disabled for your project. Please enable it in Google Cloud Console.",
            
            GmailOAuthErrorType.NETWORK_TIMEOUT: "Connection to Gmail timed out. Please check your internet connection and try again.",
            GmailOAuthErrorType.CONNECTION_ERROR: "Unable to connect to Gmail servers. Please check your internet connection.",
            GmailOAuthErrorType.DNS_RESOLUTION_ERROR: "Unable to resolve Gmail server address. Please check your DNS settings.",
            
            GmailOAuthErrorType.MISSING_CREDENTIALS_FILE: "Gmail credentials file not found. Please select a valid credentials.json file.",
            GmailOAuthErrorType.INVALID_CREDENTIALS_FORMAT: "Invalid credentials file format. Please download a new credentials.json from Google Cloud Console.",
            GmailOAuthErrorType.MISSING_OAUTH_SCOPES: "Missing required OAuth scopes. Please check your application configuration.",
            GmailOAuthErrorType.INVALID_REDIRECT_URI: "Invalid redirect URI configuration. Please check your OAuth settings.",
            
            GmailOAuthErrorType.GMAIL_API_ERROR: "Gmail API returned an error. Please try again later.",
            GmailOAuthErrorType.GOOGLE_SERVER_ERROR: "Google servers are experiencing issues. Please try again later.",
            GmailOAuthErrorType.SERVICE_UNAVAILABLE: "Gmail service is temporarily unavailable. Please try again later.",
            
            GmailOAuthErrorType.UNKNOWN_ERROR: "An unexpected error occurred. Please check the application logs for more details."
        }
        
        return messages.get(error_type, "An unknown error occurred with Gmail authentication.")
    
    @staticmethod
    def get_recovery_suggestions(error_type: GmailOAuthErrorType) -> List[str]:
        """
        Get actionable recovery suggestions for an error type.
        
        Args:
            error_type: Type of OAuth error
            
        Returns:
            List of recovery suggestions
        """
        suggestions = {
            GmailOAuthErrorType.INVALID_CREDENTIALS: [
                "Download a new credentials.json file from Google Cloud Console",
                "Ensure the credentials file is for a Desktop application type",
                "Verify that Gmail API is enabled in your Google Cloud project",
                "Check that the OAuth consent screen is properly configured"
            ],
            
            GmailOAuthErrorType.OAUTH_FLOW_CANCELLED: [
                "Click 'Authenticate with Google' again to restart the process",
                "Make sure to complete all steps in the browser window",
                "Allow all requested permissions for Gmail access",
                "Check if popup blockers are preventing the authentication window"
            ],
            
            GmailOAuthErrorType.TOKEN_REFRESH_FAILED: [
                "Click 'Authenticate with Google' to sign in again",
                "Clear any existing authentication tokens",
                "Ensure your internet connection is stable",
                "Check if your Google account password has changed recently"
            ],
            
            GmailOAuthErrorType.INVALID_TOKEN: [
                "Re-authenticate with Gmail by clicking 'Authenticate with Google'",
                "Clear browser cookies for Google accounts",
                "Try signing out and back into your Google account",
                "Check if two-factor authentication is required"
            ],
            
            GmailOAuthErrorType.RATE_LIMIT_EXCEEDED: [
                "Wait a few minutes before trying again",
                "Reduce the frequency of Gmail operations",
                "Check your Google Cloud Console for quota limits",
                "Consider upgrading your API quota if needed"
            ],
            
            GmailOAuthErrorType.QUOTA_EXCEEDED: [
                "Wait until your daily quota resets (usually at midnight Pacific Time)",
                "Check your quota usage in Google Cloud Console",
                "Consider requesting a quota increase",
                "Optimize your application to use fewer API calls"
            ],
            
            GmailOAuthErrorType.INSUFFICIENT_PERMISSIONS: [
                "Ensure your OAuth scopes include Gmail read/write permissions",
                "Re-authenticate to grant additional permissions",
                "Check your Google Cloud Console OAuth configuration",
                "Verify the consent screen includes all necessary scopes"
            ],
            
            GmailOAuthErrorType.API_DISABLED: [
                "Enable Gmail API in Google Cloud Console",
                "Go to APIs & Services > Library and search for Gmail API",
                "Click Enable on the Gmail API page",
                "Wait a few minutes for the API to become active"
            ],
            
            GmailOAuthErrorType.NETWORK_TIMEOUT: [
                "Check your internet connection",
                "Try again with a more stable network connection",
                "Disable VPN if you're using one",
                "Check if firewall is blocking the connection"
            ],
            
            GmailOAuthErrorType.CONNECTION_ERROR: [
                "Verify your internet connection is working",
                "Try accessing Gmail in a web browser",
                "Check if corporate firewall is blocking Gmail access",
                "Restart your network connection"
            ],
            
            GmailOAuthErrorType.MISSING_CREDENTIALS_FILE: [
                "Download credentials.json from Google Cloud Console",
                "Go to APIs & Services > Credentials",
                "Create or download OAuth 2.0 Client ID credentials",
                "Save the file and select it in the application"
            ],
            
            GmailOAuthErrorType.INVALID_CREDENTIALS_FORMAT: [
                "Download a fresh credentials.json file",
                "Ensure the file hasn't been modified or corrupted",
                "Verify the file contains valid JSON format",
                "Create new OAuth credentials if the file is damaged"
            ],
            
            GmailOAuthErrorType.GOOGLE_SERVER_ERROR: [
                "Wait a few minutes and try again",
                "Check Google Workspace Status page for outages",
                "Try again during off-peak hours",
                "Contact Google Support if the issue persists"
            ],
            
            GmailOAuthErrorType.SERVICE_UNAVAILABLE: [
                "Wait a few minutes and retry the operation",
                "Check if Gmail is experiencing outages",
                "Try accessing Gmail directly in a web browser",
                "Monitor Google's service status page"
            ],
            
            GmailOAuthErrorType.UNKNOWN_ERROR: [
                "Check the application logs for more detailed error information",
                "Try restarting the application",
                "Ensure all dependencies are properly installed",
                "Contact support with the error details if the issue persists"
            ]
        }
        
        return suggestions.get(error_type, [
            "Try the operation again",
            "Check your internet connection",
            "Restart the application if the problem persists"
        ])
    
    def should_retry(self, error: GmailOAuthError, operation_id: str) -> bool:
        """
        Determine if an operation should be retried based on the error and retry history.
        
        Args:
            error: The OAuth error that occurred
            operation_id: Unique identifier for the operation
            
        Returns:
            True if the operation should be retried, False otherwise
        """
        # Check if error is retryable
        if not error.is_retryable():
            return False
        
        # Check retry count
        current_attempts = self._retry_counts.get(operation_id, 0)
        if current_attempts >= self.retry_config.max_attempts:
            return False
        
        return True
    
    def get_retry_delay(self, error: GmailOAuthError, operation_id: str) -> float:
        """
        Calculate the delay before retrying an operation.
        
        Args:
            error: The OAuth error that occurred
            operation_id: Unique identifier for the operation
            
        Returns:
            Delay in seconds before retrying
        """
        # Use retry_after from error if available (for rate limiting)
        if error.retry_after:
            return float(error.retry_after)
        
        # Calculate exponential backoff delay
        attempt = self._retry_counts.get(operation_id, 0)
        delay = min(
            self.retry_config.base_delay * (self.retry_config.exponential_base ** attempt),
            self.retry_config.max_delay
        )
        
        # Add jitter if enabled
        if self.retry_config.jitter:
            import random
            delay *= (0.5 + random.random() * 0.5)  # Add 0-50% jitter
        
        return delay
    
    def record_retry_attempt(self, operation_id: str) -> None:
        """
        Record a retry attempt for an operation.
        
        Args:
            operation_id: Unique identifier for the operation
        """
        self._retry_counts[operation_id] = self._retry_counts.get(operation_id, 0) + 1
        self.logger.debug(f"Recorded retry attempt {self._retry_counts[operation_id]} for operation {operation_id}")
    
    def reset_retry_count(self, operation_id: str) -> None:
        """
        Reset the retry count for an operation (called on success).
        
        Args:
            operation_id: Unique identifier for the operation
        """
        if operation_id in self._retry_counts:
            del self._retry_counts[operation_id]
            self.logger.debug(f"Reset retry count for operation {operation_id}")
    
    def create_error_report(self, error: GmailOAuthError) -> Dict[str, Any]:
        """
        Create a detailed error report for logging or debugging.
        
        Args:
            error: The OAuth error
            
        Returns:
            Dictionary containing error report
        """
        return {
            "error_type": error.error_type.value,
            "message": error.message,
            "details": error.details,
            "error_code": error.error_code,
            "timestamp": error.timestamp,
            "is_retryable": error.is_retryable(),
            "original_error_type": type(error.original_error).__name__ if error.original_error else None,
            "original_error_message": str(error.original_error) if error.original_error else None,
            "recovery_suggestions": error.get_recovery_suggestions()
        }


# Convenience functions for common error scenarios
def create_credentials_error(file_path: str, details: str = None) -> GmailOAuthError:
    """Create an error for invalid credentials file."""
    return GmailOAuthError(
        error_type=GmailOAuthErrorType.INVALID_CREDENTIALS,
        message="Invalid Gmail credentials file",
        details=details or f"Credentials file issue: {file_path}"
    )


def create_network_error(operation: str, original_error: Exception = None) -> GmailOAuthError:
    """Create an error for network-related issues."""
    return GmailOAuthError(
        error_type=GmailOAuthErrorType.CONNECTION_ERROR,
        message=f"Network error during {operation}",
        details="Please check your internet connection",
        original_error=original_error
    )


def create_rate_limit_error(retry_after: int = None) -> GmailOAuthError:
    """Create an error for rate limiting."""
    return GmailOAuthError(
        error_type=GmailOAuthErrorType.RATE_LIMIT_EXCEEDED,
        message="Gmail API rate limit exceeded",
        details="Too many requests in a short time period",
        retry_after=retry_after
    )


def create_auth_expired_error() -> GmailOAuthError:
    """Create an error for expired authentication."""
    return GmailOAuthError(
        error_type=GmailOAuthErrorType.EXPIRED_TOKEN,
        message="Gmail authentication has expired",
        details="Please re-authenticate with Gmail"
    )