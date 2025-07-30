"""
Error Manager

This module provides a centralized error management system for the GGUF Loader application.
It integrates with the event bus to broadcast error events and manages error handling strategies.
"""

import logging
import traceback
from typing import Dict, Any, Optional, List, Callable
from functools import partial

from llmtoolkit.utils.error_handling import (
    ErrorCategory, ErrorSeverity, log_exception, 
    user_friendly_error_message, show_error_dialog,
    get_error_history, clear_error_history, export_error_logs
)
from llmtoolkit.utils.exceptions import GGUFLoaderError

logger = logging.getLogger("gguf_loader.core.error_manager")

class ErrorManager:
    """
    Centralized error management system for the application.
    
    This class provides:
    - Integration with the event bus for error broadcasting
    - Layered error handling strategies
    - Error recovery mechanisms
    - Error reporting and analysis
    """
    
    def __init__(self, event_bus=None):
        """
        Initialize the error manager.
        
        Args:
            event_bus: Application event bus for broadcasting error events
        """
        self.event_bus = event_bus
        self._retry_strategies = {}
        self._error_handlers = {}
        self._max_retry_attempts = 3
        
        # Register default error handlers
        self._register_default_handlers()
    
    def set_event_bus(self, event_bus):
        """Set the event bus after initialization."""
        self.event_bus = event_bus
    
    def handle_error(self, error: Exception, category: str = ErrorCategory.RUNTIME, 
                    context: str = "", severity: str = ErrorSeverity.ERROR, 
                    show_ui: bool = False, retry_info: Dict = None) -> bool:
        """
        Handle an error using the appropriate strategy.
        
        Args:
            error: The exception to handle
            category: Error category
            context: Additional context information
            severity: Error severity level
            show_ui: Whether to show a UI error dialog
            retry_info: Information for retry mechanism (if applicable)
            
        Returns:
            True if error was handled successfully, False otherwise
        """
        # Log the error
        log_exception(error, category, context, severity)
        
        # Broadcast error event if event bus is available
        if self.event_bus:
            self.event_bus.publish("error.occurred", {
                "error": error,
                "category": category,
                "context": context,
                "severity": severity
            })
        
        # Check if we should retry
        if retry_info and self._should_retry(error, category, retry_info):
            return self._handle_retry(error, category, retry_info)
        
        # Check for specific error handlers
        error_type = type(error).__name__
        if error_type in self._error_handlers:
            handled = self._error_handlers[error_type](error, category, context)
            if handled:
                return True
        
        # Check for category handlers
        if category in self._error_handlers:
            handled = self._error_handlers[category](error, category, context)
            if handled:
                return True
        
        # Show UI error if requested
        if show_ui:
            show_error_dialog(error, category)
        
        # Default handling
        return False
    
    def register_error_handler(self, error_type_or_category: str, 
                              handler: Callable[[Exception, str, str], bool]) -> None:
        """
        Register a custom error handler.
        
        Args:
            error_type_or_category: Exception type name or error category
            handler: Function that handles the error
        """
        self._error_handlers[error_type_or_category] = handler
    
    def register_retry_strategy(self, error_type_or_category: str, 
                               retry_func: Callable[[Exception, Dict], bool]) -> None:
        """
        Register a retry strategy for specific errors.
        
        Args:
            error_type_or_category: Exception type name or error category
            retry_func: Function that implements the retry logic
        """
        self._retry_strategies[error_type_or_category] = retry_func
    
    def get_recent_errors(self, limit: int = 10, 
                         category: Optional[str] = None) -> List[Dict]:
        """
        Get recent errors, optionally filtered by category.
        
        Args:
            limit: Maximum number of errors to return
            category: Optional category filter
            
        Returns:
            List of error records
        """
        history = get_error_history()
        
        if category:
            history = [e for e in history if e["category"] == category]
            
        return history[-limit:]
    
    def export_error_report(self, file_path: str) -> bool:
        """
        Export error history to a file.
        
        Args:
            file_path: Path to save the error report
            
        Returns:
            True if successful, False otherwise
        """
        return export_error_logs(file_path)
    
    def clear_error_history(self) -> None:
        """Clear the error history."""
        clear_error_history()
    
    def _register_default_handlers(self) -> None:
        """Register default error handlers."""
        # File not found handler
        self.register_error_handler("FileNotFoundError", 
                                   self._handle_file_not_found)
        
        # Permission error handler
        self.register_error_handler("PermissionError",
                                   self._handle_permission_error)
        
        # Memory error handler
        self.register_error_handler("MemoryError",
                                   self._handle_memory_error)
        
        # Network error handlers
        self.register_retry_strategy("ConnectionError",
                                    self._retry_network_operation)
        self.register_retry_strategy("TimeoutError",
                                    self._retry_network_operation)
    
    def _handle_file_not_found(self, error: Exception, category: str, context: str) -> bool:
        """Handle file not found errors."""
        logger.info(f"Handling file not found error: {error}")
        # Implement specific handling logic
        return False  # Return True if fully handled
    
    def _handle_permission_error(self, error: Exception, category: str, context: str) -> bool:
        """Handle permission errors."""
        logger.info(f"Handling permission error: {error}")
        # Implement specific handling logic
        return False  # Return True if fully handled
    
    def _handle_memory_error(self, error: Exception, category: str, context: str) -> bool:
        """Handle memory errors."""
        logger.warning(f"Handling memory error: {error}")
        
        # Broadcast critical memory warning
        if self.event_bus:
            self.event_bus.publish("system.memory.critical", {
                "error": error,
                "context": context
            })
            
        return False  # Return True if fully handled
    
    def _should_retry(self, error: Exception, category: str, retry_info: Dict) -> bool:
        """
        Determine if an operation should be retried.
        
        Args:
            error: The exception
            category: Error category
            retry_info: Retry information
            
        Returns:
            True if should retry, False otherwise
        """
        # Check if we've exceeded max retries
        attempt = retry_info.get("attempt", 0)
        if attempt >= self._max_retry_attempts:
            return False
        
        # Check if we have a retry strategy for this error
        error_type = type(error).__name__
        if error_type in self._retry_strategies:
            return True
            
        # Check if we have a retry strategy for this category
        if category in self._retry_strategies:
            return True
            
        return False
    
    def _handle_retry(self, error: Exception, category: str, retry_info: Dict) -> bool:
        """
        Handle retry logic for an error.
        
        Args:
            error: The exception
            category: Error category
            retry_info: Retry information
            
        Returns:
            True if retry was successful, False otherwise
        """
        error_type = type(error).__name__
        retry_func = None
        
        # Get the appropriate retry strategy
        if error_type in self._retry_strategies:
            retry_func = self._retry_strategies[error_type]
        elif category in self._retry_strategies:
            retry_func = self._retry_strategies[category]
        
        if retry_func:
            # Update retry attempt count
            retry_info["attempt"] = retry_info.get("attempt", 0) + 1
            
            # Execute retry strategy
            return retry_func(error, retry_info)
            
        return False
    
    def _retry_network_operation(self, error: Exception, retry_info: Dict) -> bool:
        """
        Retry a network operation.
        
        Args:
            error: The exception
            retry_info: Retry information
            
        Returns:
            True if retry was successful, False otherwise
        """
        if "operation" not in retry_info:
            logger.error("Cannot retry network operation: missing operation function")
            return False
            
        operation = retry_info["operation"]
        args = retry_info.get("args", [])
        kwargs = retry_info.get("kwargs", {})
        
        try:
            # Execute the operation again
            logger.info(f"Retrying network operation (attempt {retry_info['attempt']})")
            operation(*args, **kwargs)
            return True
        except Exception as e:
            logger.warning(f"Retry failed: {e}")
            return False