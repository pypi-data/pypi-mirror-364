"""
Error Handling Integration

This module provides integration utilities to connect the comprehensive error
handling system with the existing backend manager and other components.
"""

import logging
import functools
from typing import Any, Callable, Dict, Optional, TypeVar, Union
from contextlib import contextmanager

from .error_handling import (
    ComprehensiveErrorHandler, ErrorContext, ClassifiedError, 
    initialize_error_handling, get_error_handler
)
from .error_messages import generate_user_friendly_message, generate_error_report
from .model_backends import BackendError, InstallationError, HardwareError, ModelLoadingError

# Type variable for decorated functions
F = TypeVar('F', bound=Callable[..., Any])


class ErrorHandlingIntegration:
    """Integrates error handling with the backend manager and other components."""
    
    def __init__(self, backend_manager=None):
        self.logger = logging.getLogger("error.integration")
        self.backend_manager = backend_manager
        self.error_handler = initialize_error_handling(backend_manager, analytics_enabled=True)
        
        # Set up error handler callbacks
        self.error_handler.add_notification_callback(self._log_error_notification)
        
        # Track integration status
        self._integration_active = True
    
    def _log_error_notification(self, classified_error: ClassifiedError):
        """Log error notifications for debugging."""
        user_message = generate_user_friendly_message(classified_error)
        self.logger.info(f"Error notification: {user_message.title} - {user_message.severity}")
    
    def integrate_with_backend_manager(self, backend_manager):
        """Integrate error handling with the backend manager."""
        self.backend_manager = backend_manager
        self.error_handler.backend_manager = backend_manager
        self.error_handler.recovery_manager.backend_manager = backend_manager
        
        # Wrap backend manager methods with error handling
        self._wrap_backend_manager_methods()
        
        self.logger.info("Error handling integrated with backend manager")
    
    def _wrap_backend_manager_methods(self):
        """Wrap backend manager methods with error handling."""
        if not self.backend_manager:
            return
        
        # Wrap load_model method
        original_load_model = self.backend_manager.load_model
        self.backend_manager.load_model = self._wrap_load_model(original_load_model)
        
        # Wrap generate_text method
        original_generate_text = self.backend_manager.generate_text
        self.backend_manager.generate_text = self._wrap_generate_text(original_generate_text)
        
        # Wrap switch_backend method
        original_switch_backend = self.backend_manager.switch_backend
        self.backend_manager.switch_backend = self._wrap_switch_backend(original_switch_backend)
    
    def _wrap_load_model(self, original_method):
        """Wrap the load_model method with error handling."""
        @functools.wraps(original_method)
        def wrapper(model_path: str, backend_name: Optional[str] = None, **kwargs):
            try:
                return original_method(model_path, backend_name, **kwargs)
            except Exception as e:
                context = ErrorContext(
                    backend_name=backend_name,
                    model_path=model_path,
                    operation="model_loading",
                    config=kwargs
                )
                classified_error = self.error_handler.handle_error(e, context)
                
                # If recovery was successful, try again
                if classified_error.recovery_successful:
                    try:
                        return original_method(model_path, backend_name, **kwargs)
                    except Exception as retry_error:
                        # If retry fails, handle the new error
                        retry_context = ErrorContext(
                            backend_name=backend_name,
                            model_path=model_path,
                            operation="model_loading_retry",
                            config=kwargs
                        )
                        self.error_handler.handle_error(retry_error, retry_context, attempt_recovery=False)
                
                # Re-raise the original exception
                raise e
        
        return wrapper
    
    def _wrap_generate_text(self, original_method):
        """Wrap the generate_text method with error handling."""
        @functools.wraps(original_method)
        def wrapper(prompt: str, config, **kwargs):
            try:
                return original_method(prompt, config, **kwargs)
            except Exception as e:
                backend_name = getattr(self.backend_manager.current_backend, 'config', {}).get('name', 'unknown')
                context = ErrorContext(
                    backend_name=backend_name,
                    operation="text_generation",
                    config=config.__dict__ if hasattr(config, '__dict__') else str(config),
                    additional_context={'prompt_length': len(prompt)}
                )
                classified_error = self.error_handler.handle_error(e, context)
                
                # If recovery was successful, try again
                if classified_error.recovery_successful:
                    try:
                        return original_method(prompt, config, **kwargs)
                    except Exception:
                        pass  # Don't retry generation errors multiple times
                
                # Re-raise the original exception
                raise e
        
        return wrapper
    
    def _wrap_switch_backend(self, original_method):
        """Wrap the switch_backend method with error handling."""
        @functools.wraps(original_method)
        def wrapper(backend_name: str, reload_model: bool = True, **kwargs):
            try:
                return original_method(backend_name, reload_model, **kwargs)
            except Exception as e:
                context = ErrorContext(
                    backend_name=backend_name,
                    operation="backend_switch",
                    config={'reload_model': reload_model, **kwargs}
                )
                self.error_handler.handle_error(e, context)
                
                # Re-raise the original exception
                raise e
        
        return wrapper
    
    def get_system_health_status(self) -> Dict[str, Any]:
        """Get comprehensive system health status."""
        health_report = self.error_handler.get_system_health_report()
        
        # Add backend-specific information
        if self.backend_manager:
            backend_stats = self.backend_manager.get_statistics()
            health_report['backend_statistics'] = backend_stats
            
            # Add current backend info
            current_backend_info = self.backend_manager.get_current_backend_info()
            if current_backend_info:
                health_report['current_backend'] = current_backend_info
        
        return health_report
    
    def export_comprehensive_report(self, file_path: str) -> bool:
        """Export a comprehensive system and error report."""
        try:
            report = {
                'system_health': self.get_system_health_status(),
                'error_analytics': self.error_handler.analytics.get_error_trends() if self.error_handler.analytics else {},
                'recovery_statistics': self.error_handler.recovery_manager.get_recovery_statistics(),
                'recent_errors': [
                    generate_error_report(error, include_system_info=False)
                    for error in self.error_handler.get_error_history(10)
                ]
            }
            
            # Add backend monitoring report if available
            if self.backend_manager and hasattr(self.backend_manager, 'get_monitoring_report'):
                report['backend_monitoring'] = self.backend_manager.get_monitoring_report()
            
            import json
            with open(file_path, 'w') as f:
                json.dump(report, f, indent=2, default=str)
            
            return True
        except Exception as e:
            self.logger.error(f"Failed to export comprehensive report: {e}")
            return False


# Decorator functions for easy integration
def handle_backend_errors(backend_name: Optional[str] = None, operation: str = "unknown"):
    """Decorator to handle backend errors automatically."""
    def decorator(func: F) -> F:
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            try:
                return func(*args, **kwargs)
            except Exception as e:
                context = ErrorContext(
                    backend_name=backend_name,
                    operation=operation,
                    config=kwargs
                )
                get_error_handler().handle_error(e, context)
                raise e
        return wrapper
    return decorator


def handle_model_errors(model_path: Optional[str] = None, backend_name: Optional[str] = None):
    """Decorator to handle model-related errors automatically."""
    def decorator(func: F) -> F:
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            try:
                return func(*args, **kwargs)
            except Exception as e:
                context = ErrorContext(
                    backend_name=backend_name,
                    model_path=model_path,
                    operation="model_operation",
                    config=kwargs
                )
                get_error_handler().handle_error(e, context)
                raise e
        return wrapper
    return decorator


@contextmanager
def error_handling_context(backend_name: Optional[str] = None, 
                          operation: str = "unknown",
                          model_path: Optional[str] = None,
                          config: Optional[Dict[str, Any]] = None):
    """Context manager for error handling."""
    try:
        yield
    except Exception as e:
        context = ErrorContext(
            backend_name=backend_name,
            model_path=model_path,
            operation=operation,
            config=config
        )
        get_error_handler().handle_error(e, context)
        raise e


# Global integration instance
_integration_instance: Optional[ErrorHandlingIntegration] = None


def initialize_error_integration(backend_manager=None) -> ErrorHandlingIntegration:
    """Initialize the global error handling integration."""
    global _integration_instance
    _integration_instance = ErrorHandlingIntegration(backend_manager)
    return _integration_instance


def get_error_integration() -> Optional[ErrorHandlingIntegration]:
    """Get the global error handling integration instance."""
    return _integration_instance


# Utility functions for common error handling patterns
def safe_backend_operation(operation_func: Callable, backend_name: str, 
                          operation_name: str, **kwargs) -> Any:
    """Safely execute a backend operation with error handling."""
    with error_handling_context(backend_name=backend_name, operation=operation_name, config=kwargs):
        return operation_func(**kwargs)


def safe_model_operation(operation_func: Callable, model_path: str, 
                        backend_name: str, operation_name: str, **kwargs) -> Any:
    """Safely execute a model operation with error handling."""
    with error_handling_context(
        backend_name=backend_name, 
        model_path=model_path, 
        operation=operation_name, 
        config=kwargs
    ):
        return operation_func(**kwargs)


def log_error_with_context(logger: logging.Logger, error: Exception, 
                          context: Dict[str, Any], level: str = "ERROR"):
    """Log an error with comprehensive context information."""
    error_context = ErrorContext(
        backend_name=context.get('backend_name'),
        model_path=context.get('model_path'),
        operation=context.get('operation', 'unknown'),
        config=context.get('config'),
        additional_context=context
    )
    
    classified_error = get_error_handler().handle_error(error, error_context, attempt_recovery=False)
    user_message = generate_user_friendly_message(classified_error)
    
    log_method = getattr(logger, level.lower(), logger.error)
    log_method(f"{user_message.title}: {user_message.message}")


def get_error_summary() -> Dict[str, Any]:
    """Get a summary of recent errors and system health."""
    error_handler = get_error_handler()
    integration = get_error_integration()
    
    summary = {
        'system_health': error_handler.get_system_health_report(),
        'recent_errors': len(error_handler.get_error_history(10)),
        'recovery_stats': error_handler.recovery_manager.get_recovery_statistics()
    }
    
    if integration:
        backend_health = integration.get_system_health_status()
        summary['backend_health'] = backend_health
    
    return summary