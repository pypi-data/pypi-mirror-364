"""
User-Friendly Error Messages and Reporting

This module provides utilities for generating user-friendly error messages
and actionable solutions for common errors in the GGUF loader application.
"""

import logging
from typing import Dict, List, Optional, Any
from dataclasses import dataclass
from pathlib import Path

from .error_handling import (
    ClassifiedError, ErrorCategory, ErrorSeverity, ErrorSolution, RecoveryAction
)


@dataclass
class UserMessage:
    """A user-friendly error message with actionable information."""
    title: str
    message: str
    severity: str
    solutions: List[Dict[str, Any]]
    technical_details: Optional[str] = None
    error_id: Optional[str] = None


class ErrorMessageGenerator:
    """Generates user-friendly error messages from classified errors."""
    
    def __init__(self):
        self.logger = logging.getLogger("error.messages")
        self._message_templates = self._initialize_message_templates()
    
    def generate_user_message(self, classified_error: ClassifiedError) -> UserMessage:
        """
        Generate a user-friendly message from a classified error.
        
        Args:
            classified_error: The classified error to generate a message for
            
        Returns:
            UserMessage with user-friendly information
        """
        # Get base message template
        template = self._message_templates.get(
            classified_error.category, 
            self._message_templates[ErrorCategory.UNKNOWN]
        )
        
        # Customize message based on specific error
        title = self._customize_title(classified_error, template['title'])
        message = self._customize_message(classified_error, template['message'])
        
        # Convert solutions to user-friendly format
        solutions = self._format_solutions(classified_error.solutions)
        
        # Determine severity display
        severity_display = self._get_severity_display(classified_error.severity)
        
        # Include technical details if needed
        technical_details = self._generate_technical_details(classified_error)
        
        return UserMessage(
            title=title,
            message=message,
            severity=severity_display,
            solutions=solutions,
            technical_details=technical_details,
            error_id=classified_error.error_id
        )
    
    def _customize_title(self, error: ClassifiedError, template_title: str) -> str:
        """Customize the title based on the specific error."""
        # Replace placeholders in template
        title = template_title
        
        if error.context.backend_name:
            title = title.replace("{backend}", error.context.backend_name)
        
        if error.context.model_path:
            model_name = Path(error.context.model_path).name
            title = title.replace("{model}", model_name)
        
        return title
    
    def _customize_message(self, error: ClassifiedError, template_message: str) -> str:
        """Customize the message based on the specific error."""
        message = template_message
        
        # Replace common placeholders
        if error.context.backend_name:
            message = message.replace("{backend}", error.context.backend_name)
        
        if error.context.model_path:
            model_name = Path(error.context.model_path).name
            message = message.replace("{model}", model_name)
        
        if error.context.operation:
            message = message.replace("{operation}", error.context.operation)
        
        # Add specific error information
        error_str = str(error.original_error)
        if len(error_str) < 200:  # Only include if not too long
            message += f"\n\nSpecific error: {error_str}"
        
        return message
    
    def _format_solutions(self, solutions: List[ErrorSolution]) -> List[Dict[str, Any]]:
        """Format solutions for user display."""
        formatted_solutions = []
        
        for solution in solutions:
            formatted_solution = {
                'title': solution.title,
                'description': solution.description,
                'steps': solution.steps,
                'estimated_time': solution.estimated_time,
                'difficulty': self._get_difficulty_level(solution),
                'automatic': solution.automatic,
                'requires_restart': solution.requires_restart,
                'success_probability': f"{int(solution.success_probability * 100)}%"
            }
            formatted_solutions.append(formatted_solution)
        
        # Sort by automatic first, then by success probability
        formatted_solutions.sort(
            key=lambda x: (not x['automatic'], -float(x['success_probability'].rstrip('%')))
        )
        
        return formatted_solutions
    
    def _get_difficulty_level(self, solution: ErrorSolution) -> str:
        """Determine the difficulty level of a solution."""
        if solution.automatic:
            return "Easy (Automatic)"
        elif solution.action_type == RecoveryAction.MANUAL_INTERVENTION:
            if solution.requires_restart:
                return "Advanced"
            else:
                return "Intermediate"
        elif solution.action_type in [RecoveryAction.RETRY, RecoveryAction.RECONFIGURE]:
            return "Easy"
        else:
            return "Intermediate"
    
    def _get_severity_display(self, severity: ErrorSeverity) -> str:
        """Get user-friendly severity display."""
        severity_map = {
            ErrorSeverity.LOW: "Minor Issue",
            ErrorSeverity.MEDIUM: "Moderate Issue",
            ErrorSeverity.HIGH: "Serious Issue",
            ErrorSeverity.CRITICAL: "Critical Error"
        }
        return severity_map.get(severity, "Unknown")
    
    def _generate_technical_details(self, error: ClassifiedError) -> str:
        """Generate technical details for advanced users."""
        details = []
        
        details.append(f"Error ID: {error.error_id}")
        details.append(f"Category: {error.category.value}")
        details.append(f"Severity: {error.severity.value}")
        details.append(f"Timestamp: {error.timestamp.isoformat()}")
        
        if error.context.backend_name:
            details.append(f"Backend: {error.context.backend_name}")
        
        if error.context.operation:
            details.append(f"Operation: {error.context.operation}")
        
        if error.context.model_path:
            details.append(f"Model Path: {error.context.model_path}")
        
        details.append(f"Exception Type: {type(error.original_error).__name__}")
        details.append(f"Exception Message: {str(error.original_error)}")
        
        return "\n".join(details)
    
    def _initialize_message_templates(self) -> Dict[ErrorCategory, Dict[str, str]]:
        """Initialize message templates for each error category."""
        return {
            ErrorCategory.INSTALLATION: {
                'title': "Installation Problem with {backend}",
                'message': "There's an issue with the {backend} backend installation. This usually means a required dependency is missing or incompatible. Don't worry - this can typically be fixed by reinstalling the backend or updating your dependencies."
            },
            ErrorCategory.HARDWARE: {
                'title': "Hardware Acceleration Issue",
                'message': "Your system is having trouble with GPU acceleration. This might be due to outdated drivers, incompatible hardware, or configuration issues. The application can still work using CPU mode while you resolve this."
            },
            ErrorCategory.MEMORY: {
                'title': "Memory Shortage",
                'message': "Your system doesn't have enough memory to complete this operation. This often happens with large models or when other applications are using too much RAM. Try closing other programs or using a smaller model."
            },
            ErrorCategory.NETWORK: {
                'title': "Network Connection Problem",
                'message': "There's an issue connecting to the internet or downloading required files. This might be temporary - check your internet connection and try again in a moment."
            },
            ErrorCategory.FILESYSTEM: {
                'title': "File Access Problem",
                'message': "The application can't access a required file or folder. This might be due to missing files, permission issues, or the file being in use by another program."
            },
            ErrorCategory.CONFIGURATION: {
                'title': "Configuration Error",
                'message': "There's an issue with the application settings. This can usually be fixed by resetting to default settings or adjusting the configuration."
            },
            ErrorCategory.MODEL_LOADING: {
                'title': "Model Loading Failed",
                'message': "The application couldn't load the model file '{model}'. This might be due to a corrupted file, incompatible format, or insufficient system resources."
            },
            ErrorCategory.GENERATION: {
                'title': "Text Generation Error",
                'message': "An error occurred while generating text. This might be temporary - try adjusting your prompt or generation settings."
            },
            ErrorCategory.BACKEND: {
                'title': "Backend Error in {backend}",
                'message': "The {backend} backend encountered an unexpected error during {operation}. This might be resolved by switching to a different backend or restarting the application."
            },
            ErrorCategory.UNKNOWN: {
                'title': "Unexpected Error",
                'message': "An unexpected error occurred. While this isn't a common issue, there are still some steps you can try to resolve it."
            }
        }


class ErrorReportGenerator:
    """Generates comprehensive error reports for debugging and support."""
    
    def __init__(self):
        self.logger = logging.getLogger("error.reports")
    
    def generate_error_report(self, classified_error: ClassifiedError, 
                            include_system_info: bool = True) -> Dict[str, Any]:
        """
        Generate a comprehensive error report.
        
        Args:
            classified_error: The classified error to report on
            include_system_info: Whether to include system information
            
        Returns:
            Dictionary containing the error report
        """
        report = {
            'error_info': {
                'id': classified_error.error_id,
                'timestamp': classified_error.timestamp.isoformat(),
                'category': classified_error.category.value,
                'severity': classified_error.severity.value,
                'title': classified_error.title,
                'description': classified_error.description
            },
            'exception_details': {
                'type': type(classified_error.original_error).__name__,
                'message': str(classified_error.original_error),
                'traceback': self._get_traceback_info(classified_error.original_error)
            },
            'context': {
                'backend_name': classified_error.context.backend_name,
                'model_path': classified_error.context.model_path,
                'operation': classified_error.context.operation,
                'config': classified_error.context.config,
                'additional_context': classified_error.context.additional_context
            },
            'solutions': [
                {
                    'title': sol.title,
                    'description': sol.description,
                    'action_type': sol.action_type.value,
                    'steps': sol.steps,
                    'estimated_time': sol.estimated_time,
                    'success_probability': sol.success_probability,
                    'automatic': sol.automatic,
                    'requires_restart': sol.requires_restart
                }
                for sol in classified_error.solutions
            ],
            'recovery_info': {
                'attempted': classified_error.recovery_attempted,
                'successful': classified_error.recovery_successful
            }
        }
        
        if include_system_info:
            report['system_info'] = self._collect_system_info()
        
        return report
    
    def _get_traceback_info(self, error: Exception) -> Optional[str]:
        """Get traceback information from an exception."""
        try:
            import traceback
            return traceback.format_exception(type(error), error, error.__traceback__)
        except Exception:
            return None
    
    def _collect_system_info(self) -> Dict[str, Any]:
        """Collect system information for the report."""
        try:
            import sys
            import platform
            import psutil
            
            return {
                'platform': platform.platform(),
                'python_version': sys.version,
                'cpu_count': psutil.cpu_count(),
                'memory_total_gb': round(psutil.virtual_memory().total / (1024**3), 1),
                'memory_available_gb': round(psutil.virtual_memory().available / (1024**3), 1),
                'memory_usage_percent': psutil.virtual_memory().percent,
                'gpu_available': self._check_gpu_availability()
            }
        except Exception as e:
            return {'error': f"Failed to collect system info: {e}"}
    
    def _check_gpu_availability(self) -> bool:
        """Check if GPU is available."""
        try:
            import torch
            return torch.cuda.is_available() and torch.cuda.device_count() > 0
        except ImportError:
            try:
                import tensorflow as tf
                return len(tf.config.list_physical_devices('GPU')) > 0
            except ImportError:
                return False
    
    def export_report_to_file(self, report: Dict[str, Any], file_path: str) -> bool:
        """Export error report to a file."""
        try:
            import json
            with open(file_path, 'w') as f:
                json.dump(report, f, indent=2, default=str)
            return True
        except Exception as e:
            self.logger.error(f"Failed to export error report: {e}")
            return False


# Convenience functions
def generate_user_friendly_message(classified_error: ClassifiedError) -> UserMessage:
    """Generate a user-friendly message from a classified error."""
    generator = ErrorMessageGenerator()
    return generator.generate_user_message(classified_error)


def generate_error_report(classified_error: ClassifiedError, 
                         include_system_info: bool = True) -> Dict[str, Any]:
    """Generate a comprehensive error report."""
    generator = ErrorReportGenerator()
    return generator.generate_error_report(classified_error, include_system_info)