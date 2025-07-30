"""
Example integration of the comprehensive error handling system.

This module demonstrates how to integrate the error handling system
with the existing backend manager and application components.
"""

import logging
from typing import Optional, Dict, Any

from .backend_manager import BackendManager
from .error_handling import initialize_error_handling, get_error_handler
from .error_integration import initialize_error_integration, error_handling_context
from .error_messages import generate_user_friendly_message
from .model_backends import GenerationConfig

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("error_handling_example")


class EnhancedBackendManager:
    """
    Enhanced backend manager with comprehensive error handling.
    
    This class wraps the existing BackendManager with error handling capabilities.
    """
    
    def __init__(self):
        # Initialize the original backend manager
        self.backend_manager = BackendManager()
        
        # Initialize error handling system
        self.error_handler = initialize_error_handling(self.backend_manager, analytics_enabled=True)
        self.error_integration = initialize_error_integration(self.backend_manager)
        
        # Set up error notification callback
        self.error_handler.add_notification_callback(self._handle_error_notification)
        
        logger.info("Enhanced backend manager initialized with error handling")
    
    def _handle_error_notification(self, classified_error):
        """Handle error notifications by generating user-friendly messages."""
        user_message = generate_user_friendly_message(classified_error)
        
        # Log the user-friendly message
        logger.warning(f"User Notification: {user_message.title}")
        logger.info(f"Severity: {user_message.severity}")
        logger.info(f"Message: {user_message.message}")
        
        # Log available solutions
        if user_message.solutions:
            logger.info("Available solutions:")
            for i, solution in enumerate(user_message.solutions, 1):
                logger.info(f"  {i}. {solution['title']} (Success rate: {solution['success_probability']})")
                if solution['automatic']:
                    logger.info(f"     → This solution was attempted automatically")
    
    def load_model_safely(self, model_path: str, backend_name: Optional[str] = None, **kwargs):
        """
        Load a model with comprehensive error handling.
        
        Args:
            model_path: Path to the model file
            backend_name: Specific backend to use (None for auto-selection)
            **kwargs: Additional arguments for model loading
            
        Returns:
            LoadingResult with success status and details
        """
        try:
            with error_handling_context(
                backend_name=backend_name,
                model_path=model_path,
                operation="model_loading",
                config=kwargs
            ):
                result = self.backend_manager.load_model(model_path, backend_name, **kwargs)
                
                if result.success:
                    logger.info(f"Model loaded successfully using {result.backend_used}")
                else:
                    logger.error(f"Model loading failed: {result.error_message}")
                
                return result
                
        except Exception as e:
            logger.error(f"Unexpected error during model loading: {e}")
            raise
    
    def generate_text_safely(self, prompt: str, config: GenerationConfig) -> Optional[str]:
        """
        Generate text with comprehensive error handling.
        
        Args:
            prompt: Input text prompt
            config: Generation configuration
            
        Returns:
            Generated text or None if failed
        """
        try:
            backend_name = getattr(self.backend_manager.current_backend, 'config', {}).get('name', 'unknown')
            
            with error_handling_context(
                backend_name=backend_name,
                operation="text_generation",
                config=config.__dict__ if hasattr(config, '__dict__') else str(config)
            ):
                result = self.backend_manager.generate_text(prompt, config)
                logger.info(f"Text generated successfully ({len(result)} characters)")
                return result
                
        except Exception as e:
            logger.error(f"Text generation failed: {e}")
            return None
    
    def get_system_health_dashboard(self) -> Dict[str, Any]:
        """
        Get a comprehensive system health dashboard.
        
        Returns:
            Dictionary with system health information
        """
        # Get basic health report
        health_report = self.error_handler.get_system_health_report()
        
        # Add backend statistics
        backend_stats = self.backend_manager.get_statistics()
        
        # Add recovery statistics
        recovery_stats = self.error_handler.recovery_manager.get_recovery_statistics()
        
        # Add error analytics if available
        analytics_data = {}
        if self.error_handler.analytics:
            analytics_data = {
                'error_trends': self.error_handler.analytics.get_error_trends(),
                'solution_effectiveness': self.error_handler.analytics.get_solution_effectiveness(),
                'recommendations': self.error_handler.analytics.generate_improvement_recommendations()
            }
        
        dashboard = {
            'system_health': health_report,
            'backend_statistics': backend_stats,
            'recovery_statistics': recovery_stats,
            'analytics': analytics_data,
            'recent_errors': [
                {
                    'id': error.error_id,
                    'title': error.title,
                    'category': error.category.value,
                    'severity': error.severity.value,
                    'timestamp': error.timestamp.isoformat(),
                    'recovery_attempted': error.recovery_attempted,
                    'recovery_successful': error.recovery_successful
                }
                for error in self.error_handler.get_error_history(5)
            ]
        }
        
        return dashboard
    
    def export_error_report(self, file_path: str = "error_report.json") -> bool:
        """
        Export a comprehensive error report.
        
        Args:
            file_path: Path to save the report
            
        Returns:
            True if successful, False otherwise
        """
        return self.error_integration.export_comprehensive_report(file_path)
    
    def cleanup(self):
        """Clean up resources."""
        self.backend_manager.cleanup()
        logger.info("Enhanced backend manager cleaned up")


def demonstrate_error_handling():
    """Demonstrate the error handling system in action."""
    logger.info("=== Error Handling System Demonstration ===")
    
    # Create enhanced backend manager
    enhanced_manager = EnhancedBackendManager()
    
    # Demonstrate model loading with error handling
    logger.info("\n1. Demonstrating model loading with error handling...")
    try:
        # This will likely fail since the model doesn't exist
        result = enhanced_manager.load_model_safely("nonexistent_model.gguf")
        if result and result.success:
            logger.info("Model loaded successfully!")
        else:
            logger.info("Model loading failed as expected")
    except Exception as e:
        logger.info(f"Caught exception: {e}")
    
    # Demonstrate text generation with error handling
    logger.info("\n2. Demonstrating text generation with error handling...")
    try:
        # This will fail since no model is loaded
        config = GenerationConfig(max_tokens=50, temperature=0.7)
        result = enhanced_manager.generate_text_safely("Hello, world!", config)
        if result:
            logger.info(f"Generated text: {result}")
        else:
            logger.info("Text generation failed as expected")
    except Exception as e:
        logger.info(f"Caught exception: {e}")
    
    # Show system health dashboard
    logger.info("\n3. System Health Dashboard:")
    dashboard = enhanced_manager.get_system_health_dashboard()
    
    logger.info(f"System Status: {dashboard['system_health']['status']}")
    logger.info(f"Total Errors: {dashboard['system_health']['error_count']}")
    logger.info(f"Recovery Rate: {dashboard['system_health']['recovery_rate']:.2%}")
    
    if dashboard['recent_errors']:
        logger.info("Recent Errors:")
        for error in dashboard['recent_errors']:
            logger.info(f"  - {error['title']} ({error['severity']})")
    
    # Export error report
    logger.info("\n4. Exporting comprehensive error report...")
    if enhanced_manager.export_error_report("demo_error_report.json"):
        logger.info("Error report exported successfully")
    else:
        logger.info("Failed to export error report")
    
    # Cleanup
    enhanced_manager.cleanup()
    logger.info("\n=== Demonstration Complete ===")


if __name__ == "__main__":
    demonstrate_error_handling()