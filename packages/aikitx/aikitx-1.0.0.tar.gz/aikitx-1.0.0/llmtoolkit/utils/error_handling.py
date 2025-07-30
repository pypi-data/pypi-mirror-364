"""
Error Handling Utilities

This module provides a comprehensive error handling framework for the GGUF Loader application,
implementing layered error handling, user-friendly error messages, and a logging system.
"""

import logging
import traceback
import sys
import os
import json
import datetime
from typing import Optional, Callable, Any, Dict, List, Union
from functools import wraps
from PySide6.QtWidgets import QMessageBox

# Import custom exceptions
from .exceptions import GGUFLoaderError, UIError, CoreError, ModelError, AddonError, FileSystemError

# Configure logging
def setup_logging(log_dir="logs", log_level=logging.INFO):
    """
    Set up the logging system for the application.
    
    Args:
        log_dir: Directory to store log files
        log_level: Logging level
    """
    if not os.path.exists(log_dir):
        os.makedirs(log_dir)
        
    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    log_file = os.path.join(log_dir, f"gguf_loader_{timestamp}.log")
    
    # Configure root logger
    root_logger = logging.getLogger()
    root_logger.setLevel(log_level)
    
    # File handler for all logs
    file_handler = logging.FileHandler(log_file)
    file_handler.setLevel(log_level)
    file_formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    file_handler.setFormatter(file_formatter)
    root_logger.addHandler(file_handler)
    
    # Console handler for warnings and above with UTF-8 encoding
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(logging.WARNING)
    
    # Set encoding to UTF-8 to handle Unicode characters
    if hasattr(console_handler.stream, 'reconfigure'):
        try:
            console_handler.stream.reconfigure(encoding='utf-8')
        except:
            pass
    
    # Use a formatter that avoids Unicode characters for Windows compatibility
    console_formatter = logging.Formatter(
        '%(levelname)s - %(message)s'
    )
    console_handler.setFormatter(console_formatter)
    root_logger.addHandler(console_handler)
    
    # Create specific loggers
    create_logger("gguf_loader.ui", log_level)
    create_logger("gguf_loader.core", log_level)
    create_logger("gguf_loader.model", log_level)
    create_logger("gguf_loader.addon", log_level)
    create_logger("gguf_loader.file", log_level)
    
    return root_logger

def create_logger(name, log_level=logging.INFO):
    """Create a named logger with the specified log level."""
    logger = logging.getLogger(name)
    logger.setLevel(log_level)
    return logger

# Default logger
logger = logging.getLogger("gguf_loader.utils.error")

class ErrorCategory:
    """Enumeration of error categories."""
    FILE = "file_error"
    MODEL = "model_error"
    ADDON = "addon_error"
    CONFIG = "config_error"
    UI = "ui_error"
    RUNTIME = "runtime_error"

class ErrorSeverity:
    """Enumeration of error severity levels."""
    INFO = "info"
    WARNING = "warning"
    ERROR = "error"
    CRITICAL = "critical"

def format_exception(e: Exception) -> str:
    """
    Format an exception into a readable string.
    
    Args:
        e: The exception to format
        
    Returns:
        Formatted exception string
    """
    return f"{type(e).__name__}: {str(e)}"

def get_traceback_str(e: Exception) -> str:
    """
    Get a string representation of an exception's traceback.
    
    Args:
        e: The exception
        
    Returns:
        String representation of the traceback
    """
    return "".join(traceback.format_exception(type(e), e, e.__traceback__))

def log_exception(e: Exception, category: str = ErrorCategory.RUNTIME, context: str = "", 
                 severity: str = ErrorSeverity.ERROR) -> None:
    """
    Log an exception with category, context information, and severity.
    
    Args:
        e: The exception to log
        category: Error category
        context: Additional context information
        severity: Error severity level
    """
    error_message = format_exception(e)
    if context:
        error_message = f"{context}: {error_message}"
    
    log_message = f"[{category}] {error_message}"
    
    # Get the appropriate logger based on category
    if category == ErrorCategory.UI:
        log = logging.getLogger("gguf_loader.ui")
    elif category == ErrorCategory.MODEL:
        log = logging.getLogger("gguf_loader.model")
    elif category == ErrorCategory.ADDON:
        log = logging.getLogger("gguf_loader.addon")
    elif category == ErrorCategory.FILE:
        log = logging.getLogger("gguf_loader.file")
    elif category == ErrorCategory.CONFIG:
        log = logging.getLogger("gguf_loader.core")
    else:
        log = logger
    
    # Log at the appropriate level
    if severity == ErrorSeverity.INFO:
        log.info(log_message)
    elif severity == ErrorSeverity.WARNING:
        log.warning(log_message)
    elif severity == ErrorSeverity.CRITICAL:
        log.critical(log_message)
        log.critical(get_traceback_str(e))
    else:  # Default to ERROR
        log.error(log_message)
        log.debug(get_traceback_str(e))
    
    # Record error in error history
    record_error(e, category, context, severity)

# Error history for tracking and analysis
_error_history: List[Dict] = []
_max_error_history = 100

def record_error(e: Exception, category: str, context: str, severity: str) -> None:
    """Record an error in the error history."""
    global _error_history
    
    error_record = {
        "timestamp": datetime.datetime.now().isoformat(),
        "type": type(e).__name__,
        "message": str(e),
        "category": category,
        "context": context,
        "severity": severity
    }
    
    _error_history.append(error_record)
    
    # Trim history if it gets too long
    if len(_error_history) > _max_error_history:
        _error_history = _error_history[-_max_error_history:]

def get_error_history() -> List[Dict]:
    """Get the error history."""
    return _error_history

def clear_error_history() -> None:
    """Clear the error history."""
    global _error_history
    _error_history = []

def safe_call(func: Callable, *args, **kwargs) -> tuple[bool, Any, Optional[Exception]]:
    """
    Safely call a function and catch any exceptions.
    
    Args:
        func: The function to call
        *args, **kwargs: Arguments to pass to the function
        
    Returns:
        Tuple of (success, result, exception)
    """
    try:
        result = func(*args, **kwargs)
        return True, result, None
    except Exception as e:
        return False, None, e

def error_handler(category: str = ErrorCategory.RUNTIME, show_ui_error: bool = False):
    """
    Decorator for handling exceptions in functions.
    
    Args:
        category: Error category
        show_ui_error: Whether to show a UI error dialog
        
    Returns:
        Decorated function
    """
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            try:
                return func(*args, **kwargs)
            except Exception as e:
                context = f"Error in {func.__name__}"
                log_exception(e, category, context)
                
                if show_ui_error:
                    show_error_dialog(e, category)
                
                # Re-raise custom exceptions, wrap others in appropriate custom exception
                if isinstance(e, GGUFLoaderError):
                    raise
                
                if category == ErrorCategory.UI:
                    raise UIError(str(e)) from e
                elif category == ErrorCategory.MODEL:
                    raise ModelError(str(e)) from e
                elif category == ErrorCategory.ADDON:
                    raise AddonError(str(e)) from e
                elif category == ErrorCategory.FILE:
                    raise FileSystemError(str(e)) from e
                elif category == ErrorCategory.CONFIG:
                    raise CoreError(str(e)) from e
                else:
                    raise GGUFLoaderError(str(e)) from e
                
        return wrapper
    return decorator

def user_friendly_error_message(e: Exception, category: str = ErrorCategory.RUNTIME) -> str:
    """
    Get a user-friendly error message for an exception.
    
    Args:
        e: The exception
        category: Error category
        
    Returns:
        User-friendly error message
    """
    # First check if it's one of our custom exceptions
    if isinstance(e, GGUFLoaderError):
        return e.message
    
    # Map standard exception types to user-friendly messages
    if isinstance(e, FileNotFoundError):
        return "The specified file could not be found."
    elif isinstance(e, PermissionError):
        return "You don't have permission to access the specified file or directory."
    elif isinstance(e, MemoryError):
        return "Not enough memory to complete the operation."
    elif isinstance(e, OSError):
        return f"System error: {str(e)}"
    elif isinstance(e, ValueError):
        return f"Invalid value: {str(e)}"
    elif isinstance(e, TypeError):
        return f"Type error: {str(e)}"
    elif isinstance(e, KeyError):
        return "A required configuration key is missing."
    elif isinstance(e, ImportError):
        return "Failed to import a required module."
    
    # Category-specific messages
    if category == ErrorCategory.FILE:
        return f"File operation failed: {str(e)}"
    elif category == ErrorCategory.MODEL:
        return f"Model operation failed: {str(e)}"
    elif category == ErrorCategory.ADDON:
        return f"Addon operation failed: {str(e)}"
    elif category == ErrorCategory.CONFIG:
        return f"Configuration error: {str(e)}"
    elif category == ErrorCategory.UI:
        return f"UI operation failed: {str(e)}"
    
    # Generic message
    return f"An error occurred: {str(e)}"

def show_error_dialog(e: Exception, category: str = ErrorCategory.RUNTIME, 
                  context: str = "", error_manager=None) -> None:
    """
    Show an error dialog with a user-friendly message.
    
    Args:
        e: The exception
        category: Error category
        context: Error context
        error_manager: Reference to the error manager (optional)
    """
    friendly_message = user_friendly_error_message(e, category)
    
    # First show a simple message box with the friendly message
    # Determine severity based on exception type
    if isinstance(e, (MemoryError, OSError)) or category in (ErrorCategory.MODEL, ErrorCategory.ADDON):
        icon = QMessageBox.Critical
        title = "Critical Error"
    else:
        icon = QMessageBox.Warning
        title = "Warning"
    
    # Create and show the message box
    msg_box = QMessageBox()
    msg_box.setIcon(icon)
    msg_box.setWindowTitle(title)
    msg_box.setText(friendly_message)
    
    # Add a "Details" button to show the detailed error dialog
    msg_box.setStandardButtons(QMessageBox.Ok | QMessageBox.Help)
    msg_box.button(QMessageBox.Help).setText("Details")
    
    result = msg_box.exec()
    
    # If the user clicked "Details", show the detailed error dialog
    if result == QMessageBox.Help:
        # Import here to avoid circular imports
        from llmtoolkit.app.ui.error_dialog import ErrorDetailsDialog
        
        # Create and show the detailed error dialog
        dialog = ErrorDetailsDialog(e, category, context, msg_box.parentWidget(), error_manager)
        dialog.exec()

def export_error_logs(file_path: str) -> bool:
    """
    Export error logs to a JSON file.
    
    Args:
        file_path: Path to save the error logs
        
    Returns:
        True if successful, False otherwise
    """
    try:
        with open(file_path, 'w') as f:
            json.dump(_error_history, f, indent=2)
        return True
    except Exception as e:
        log_exception(e, ErrorCategory.FILE, "Failed to export error logs")
        return False