"""
Application Controller

This module contains the ApplicationController class, which is responsible for
coordinating the application's components and managing the application lifecycle.

The ApplicationController acts as the central coordinator for the application,
managing the initialization and interaction of all components, handling the
application lifecycle, and providing a service registry for dependency injection.
"""

import logging
import sys
import os
import time
import traceback
import importlib
from enum import Enum, auto
from pathlib import Path
from typing import Dict, Any, Optional, List, Callable, Type, TypeVar, Generic, Set

from PySide6.QtWidgets import QApplication, QMessageBox, QSplashScreen
from PySide6.QtCore import QTimer, QObject, Signal, Qt
from PySide6.QtGui import QIcon



from llmtoolkit.app.core.event_bus import EventBus
from llmtoolkit.app.core.config_manager import ConfigManager
from llmtoolkit.app.core.error_manager import ErrorManager
from llmtoolkit.app.core.recovery_manager import RecoveryManager
from llmtoolkit.app.core.model_service import ModelService
from llmtoolkit.app.ui.main_window import MainWindow

from llmtoolkit.utils.error_handling import ErrorCategory, ErrorSeverity, setup_logging
from llmtoolkit.utils.exceptions import GGUFLoaderError

# Type variable for service registration
T = TypeVar('T')

class AppState(Enum):
    """Application state enumeration."""
    INITIALIZING = auto()
    STARTING = auto()
    RUNNING = auto()
    STOPPING = auto()
    STOPPED = auto()
    ERROR = auto()

class ServiceRegistry:
    """
    Service registry for dependency injection.
    
    This class provides a simple dependency injection container for registering
    and retrieving services.
    """
    
    def __init__(self):
        """Initialize the service registry."""
        self._services: Dict[Type, Any] = {}
        self._factories: Dict[Type, Callable[[], Any]] = {}
    
    def register(self, service_type: Type[T], instance: T) -> None:
        """
        Register a service instance.
        
        Args:
            service_type: Type of the service
            instance: Service instance
        """
        self._services[service_type] = instance
    
    def register_factory(self, service_type: Type[T], factory: Callable[[], T]) -> None:
        """
        Register a service factory.
        
        Args:
            service_type: Type of the service
            factory: Factory function that creates the service
        """
        self._factories[service_type] = factory
    
    def get(self, service_type: Type[T]) -> Optional[T]:
        """
        Get a service instance.
        
        Args:
            service_type: Type of the service
            
        Returns:
            Service instance, or None if not found
        """
        # Check if service is already instantiated
        if service_type in self._services:
            return self._services[service_type]
        
        # Check if we have a factory for this service
        if service_type in self._factories:
            # Create the service using the factory
            instance = self._factories[service_type]()
            # Register the instance
            self._services[service_type] = instance
            return instance
        
        return None
    
    def has(self, service_type: Type[T]) -> bool:
        """
        Check if a service is registered.
        
        Args:
            service_type: Type of the service
            
        Returns:
            True if the service is registered, False otherwise
        """
        return service_type in self._services or service_type in self._factories
    
    def clear(self) -> None:
        """Clear all registered services."""
        self._services.clear()
        self._factories.clear()

class ApplicationController:
    """
    Main application controller that coordinates all components.
    
    This class is responsible for:
    - Initializing the application components
    - Managing the application lifecycle
    - Coordinating between UI and business logic
    - Providing a service registry for dependency injection
    - Handling startup options
    """
    
    def __init__(self, startup_options: Optional[Dict[str, Any]] = None):
        """
        Initialize the application controller and its components.
        
        Args:
            startup_options: Optional dictionary of startup options
        """
        # Get user configuration directory from resource manager
        from llmtoolkit.resource_manager import get_user_config_dir
        user_config_dir = get_user_config_dir()
        
        # Set up logging system using user config directory
        log_dir = user_config_dir / "logs"
        self.root_logger = setup_logging(str(log_dir))
        
        self.logger = logging.getLogger("llmtoolkit.controller")
        self.logger.info("Initializing ApplicationController")
        
        # Store startup options
        self.startup_options = startup_options or {}
        
        # Initialize application state
        self.state = AppState.INITIALIZING
        
        # Create service registry
        self.services = ServiceRegistry()
        
        # Create or get the Qt application
        self.app = QApplication.instance()
        if self.app is None:
            self.app = QApplication(sys.argv)
        self.app.setApplicationName("LLM Toolkit")
        self.app.setOrganizationName("KiroDeveloper")
        self.app.setApplicationVersion("0.1.0")
        
        # Set application icon for taskbar and window using resource manager
        try:
            from llmtoolkit.resource_manager import get_icon
            app_icon = get_icon("icon.ico")
            if app_icon:
                self.app.setWindowIcon(app_icon)
        except Exception as e:
            self.logger.debug(f"Could not set application icon: {e}")
        
        # Set application style
        self.app.setStyle("Fusion")
        
        # Initialize core components
        self.event_bus = EventBus()
        self.services.register(EventBus, self.event_bus)
        
        # Initialize error manager
        self.error_manager = ErrorManager(self.event_bus)
        self.services.register(ErrorManager, self.error_manager)
        
        # Use user config directory from resource manager
        config_dir = user_config_dir
        self.config_manager = ConfigManager(config_dir / "config.json")
        self.services.register(ConfigManager, self.config_manager)
        
        # Initialize recovery manager
        self.recovery_manager = RecoveryManager(self.event_bus, self.config_manager)
        self.services.register(RecoveryManager, self.recovery_manager)
        
        # Initialize performance-optimized backend manager
        from llmtoolkit.app.core.performance_integration import PerformanceIntegratedBackendManager
        self.backend_manager = PerformanceIntegratedBackendManager()
        self.backend_manager.start_monitoring()
        self.services.register(PerformanceIntegratedBackendManager, self.backend_manager)
        
        # Initialize model service with backend manager
        self.model_service = ModelService(self.event_bus, backend_manager=self.backend_manager, config_manager=self.config_manager)
        self.services.register(ModelService, self.model_service)
        
        # Initialize chat service
        from llmtoolkit.app.services.chat_service import ChatService
        self.chat_service = ChatService(self.model_service, self.event_bus, self.config_manager)
        self.services.register(ChatService, self.chat_service)
        
        # Initialize summarization service
        # NOTE: Disabled - now handled by performance-optimized backend bridge in MainWindow
        # from llmtoolkit.app.services.summarization_service import SummarizationService
        # self.summarization_service = SummarizationService(self.model_service, self.event_bus, self.config_manager)
        # self.services.register(SummarizationService, self.summarization_service)
        self.summarization_service = None  # Placeholder for backward compatibility
        
        # Initialize email service
        from llmtoolkit.app.services.email_service import EmailService
        self.email_service = EmailService(self.event_bus, self.config_manager, self.model_service)
        self.services.register(EmailService, self.email_service)
        
        # Initialize UI components
        self.main_window = None
        
        # Register application shutdown handler
        self.app.aboutToQuit.connect(self._handle_application_quit)
        
        # Set up global exception handler
        sys.excepthook = self._global_exception_handler
    
    def run(self) -> int:
        """
        Run the application.
        
        Returns:
            Exit code
        """
        try:
            # Initialize components
            self.initialize_components()
            
            # Show main window
            if self.main_window:
                self.main_window.show()
                self.state = AppState.RUNNING
                self.logger.info("Application started successfully")
            else:
                self.logger.error("Main window not created")
                return 1
            
            # Run the Qt event loop
            return self.app.exec()
            
        except Exception as e:
            self.logger.exception(f"Error running application: {e}")
            return 1
    
    def _handle_application_quit(self):
        """Handle application quit event."""
        self.logger.info("Application quit event received")
        self.shutdown()
    
    def initialize_components(self):
        """Initialize and connect all application components."""
        self.logger.info("Initializing application components")
        self.state = AppState.STARTING
        
        try:
            # Load configuration
            self.logger.info("Loading configuration...")
            if not self.config_manager.load():
                self.logger.warning("Failed to load configuration, using defaults")
            else:
                self.logger.info("Configuration loaded successfully")
            
            # Create main window
            self.logger.info("Creating main window...")
            try:
                self.main_window = MainWindow(self.event_bus, self.config_manager, self.email_service, self.backend_manager)
                self.logger.info("Main window created successfully")
            except Exception as e:
                self.logger.error(f"Failed to create main window: {e}")
                self.logger.error(f"Exception details: {traceback.format_exc()}")
                self.main_window = None
                raise
            self.services.register(MainWindow, self.main_window)
            
            # Connect signals and slots
            self.logger.info("Setting up signal connections...")
            self.setup_signal_connections()
            
            # Publish application initialized event
            self.logger.info("Publishing app.initialized event...")
            self.event_bus.publish("app.initialized")
            
            self.state = AppState.RUNNING
            self.logger.info("Application components initialized successfully")
            return True
            
        except Exception as e:
            self.logger.exception(f"Error initializing components: {e}")
            self.state = AppState.ERROR
            return False
    

    
    def setup_signal_connections(self):
        """Set up signal connections between components."""
        # Connect application exit signal
        self.event_bus.subscribe("app.exit", self.handle_exit)
        
        # Connect model loading signals
        self.event_bus.subscribe("model.loaded", self.handle_model_loaded)
        self.event_bus.subscribe("model.error", self.handle_model_error)
        
        # Note: chat.send is now handled by MainWindow's backend bridge
        # self.event_bus.subscribe("chat.send", self.handle_chat_message)
        
        # Connect summarization signals
        self.event_bus.subscribe("summarization.request", self.handle_summarization_request)
        self.event_bus.subscribe("summarization.file_request", self.handle_summarization_file_request)
        
        # Connect async summarization signals
        # NOTE: Disabled - now handled by performance-optimized backend bridge in MainWindow
        # self.event_bus.subscribe("summarization.text_async_request", self.handle_summarization_text_async_request)
        # self.event_bus.subscribe("summarization.file_async_request", self.handle_summarization_file_async_request)
    
    def handle_exit(self, exit_code=0):
        """
        Handle application exit request.
        
        Args:
            exit_code: Exit code to return
        """
        self.logger.info(f"Exit requested with code {exit_code}")
        
        # Initiate shutdown sequence
        self.shutdown()
        
        # Exit the application
        self.app.exit(exit_code)
    
    def shutdown(self):
        """
        Perform application shutdown sequence.
        
        This method is responsible for cleanly shutting down all application
        components and releasing resources.
        """
        if self.state == AppState.STOPPED:
            return
            
        self.logger.info("Shutting down application")
        self.state = AppState.STOPPING
        
        try:
            # Publish shutdown event
            self.event_bus.publish("app.shutdown")
            
            # Save configuration
            self.config_manager.save()
            
            # Shutdown event bus
            self.event_bus.shutdown()
            
            # Clear service registry
            self.services.clear()
            
            self.state = AppState.STOPPED
            self.logger.info("Application shutdown complete")
            
        except Exception as e:
            self.logger.exception(f"Error during shutdown: {e}")
            self.state = AppState.ERROR
    
    def handle_model_loaded(self, model_id, model_name):
        """
        Handle model loaded event.
        
        Args:
            model_id: ID of the loaded model
            model_name: Name of the loaded model
        """
        self.logger.info(f"Model loaded: {model_name} (ID: {model_id})")
        
        # Update window title
        if self.main_window:
            self.main_window.setWindowTitle(f"LLM Toolkit - {model_name}")
    
    def _global_exception_handler(self, exc_type, exc_value, exc_traceback):
        """
        Global exception handler for uncaught exceptions.
        
        Args:
            exc_type: Exception type
            exc_value: Exception value
            exc_traceback: Exception traceback
        """
        # Don't handle KeyboardInterrupt
        if issubclass(exc_type, KeyboardInterrupt):
            sys.__excepthook__(exc_type, exc_value, exc_traceback)
            return
            
        # Log the exception
        self.logger.critical("Uncaught exception", exc_info=(exc_type, exc_value, exc_traceback))
        
        # Handle the exception with the error manager
        if hasattr(self, 'error_manager'):
            self.error_manager.handle_error(
                exc_value,
                category=ErrorCategory.RUNTIME,
                context="Uncaught exception",
                severity=ErrorSeverity.CRITICAL,
                show_ui=True
            )
    
    def handle_model_error(self, error_message, file_path=None):
        """
        Handle model error event.
        
        Args:
            error_message: Error message
            file_path: Path to the model file that caused the error
        """
        self.logger.error(f"Model error: {error_message}")
        
        # Create a model error exception
        from utils.exceptions import ModelLoadError
        error = ModelLoadError(error_message)
        
        # Use the error manager to handle the error
        context = f"Loading model from {file_path}" if file_path else "Loading model"
        self.error_manager.handle_error(
            error,
            category=ErrorCategory.MODEL,
            context=context,
            show_ui=True
        )
    
    def handle_chat_message(self, event_data):
        """
        Handle chat message event from UI.
        
        Args:
            event_data: Dictionary containing message and conversation_id
        """
        try:
            message = event_data.get("message", "")
            conversation_id = event_data.get("conversation_id", "main_chat")
            
            self.logger.info(f"Processing chat message: {message[:50]}...")
            
            # Notify UI that generation is starting
            self.event_bus.publish("chat.generating")
            
            # Send message to chat service asynchronously
            success = self.chat_service.send_message_async(message)
            
            if not success:
                # Publish error if generation couldn't start
                self.event_bus.publish("chat.error", "Failed to start response generation. Please check if a model is loaded.")
                self.logger.error("Chat service failed to start generation")
                
        except Exception as e:
            self.logger.error(f"Error handling chat message: {e}")
            self.event_bus.publish("chat.error", f"Error processing message: {str(e)}")
    
    def handle_summarization_request(self, event_data):
        """
        Handle summarization request event from UI.
        
        Args:
            event_data: Dictionary containing text and options
        """
        try:
            text = event_data.get("text", "")
            options = event_data.get("options", {})
            style = options.get("style", "concise")
            
            self.logger.info(f"Processing text summarization request...")
            
            # Validate input
            if not text or not text.strip():
                error_msg = "No text provided for summarization"
                self.logger.error(error_msg)
                self.event_bus.publish("summarization.error", error_msg)
                return
            
            # Notify UI that summarization is starting
            try:
                self.event_bus.publish("summarization.generating")
            except Exception as e:
                self.logger.error(f"Failed to publish summarization.generating event: {e}")
            
            # Process text summarization
            summary = self.summarization_service.summarize_text(text, style)
            
            if summary:
                # Publish successful response - send just the summary string to match UI expectations
                try:
                    self.event_bus.publish("summarization.completed", summary)
                    self.logger.info(f"Text summarization completed: {summary[:50]}...")
                except Exception as e:
                    self.logger.error(f"Failed to publish summarization.completed event: {e}")
                    # Try to notify UI of the communication error
                    try:
                        self.event_bus.publish("summarization.error", "Event communication error occurred")
                    except:
                        pass  # If we can't even publish error events, log it
                        self.logger.critical("Complete event communication failure")
            else:
                # Publish error
                error_msg = "Failed to generate summary. Please check if a model is loaded."
                self.logger.error("Summarization service returned no response")
                try:
                    self.event_bus.publish("summarization.error", error_msg)
                except Exception as e:
                    self.logger.error(f"Failed to publish summarization.error event: {e}")
                
        except Exception as e:
            self.logger.error(f"Error handling summarization request: {e}")
            try:
                self.event_bus.publish("summarization.error", f"Error processing summarization: {str(e)}")
            except Exception as pub_error:
                self.logger.error(f"Failed to publish error event: {pub_error}")
                # If we can't publish events, the UI won't know about the error
                # This is a critical communication failure
    
    def handle_summarization_file_request(self, event_data):
        """
        Handle file summarization request event from UI.
        
        Args:
            event_data: Dictionary containing file_path and options
        """
        try:
            file_path = event_data.get("file_path", "")
            options = event_data.get("options", {})
            style = options.get("style", "concise")
            
            # Validate input
            if not file_path:
                error_msg = "No file path provided for summarization"
                self.logger.error(error_msg)
                try:
                    self.event_bus.publish("summarization.error", error_msg)
                except Exception as e:
                    self.logger.error(f"Failed to publish summarization.error event: {e}")
                return
            
            self.logger.info(f"Processing file summarization request: {file_path}")
            
            # Notify UI that summarization is starting
            try:
                self.event_bus.publish("summarization.generating")
            except Exception as e:
                self.logger.error(f"Failed to publish summarization.generating event: {e}")
            
            # Process file summarization
            summary = self.summarization_service.summarize_file(file_path, style)
            
            if summary:
                # Publish successful response - send just the summary string to match UI expectations
                try:
                    self.event_bus.publish("summarization.completed", summary)
                    self.logger.info(f"File summarization completed: {summary[:50]}...")
                except Exception as e:
                    self.logger.error(f"Failed to publish summarization.completed event: {e}")
                    # Try to notify UI of the communication error
                    try:
                        self.event_bus.publish("summarization.error", "Event communication error occurred")
                    except:
                        pass  # If we can't even publish error events, log it
                        self.logger.critical("Complete event communication failure")
            else:
                # Publish error
                error_msg = "Failed to generate summary. Please check if a model is loaded."
                self.logger.error("Summarization service returned no response")
                try:
                    self.event_bus.publish("summarization.error", error_msg)
                except Exception as e:
                    self.logger.error(f"Failed to publish summarization.error event: {e}")
                
        except Exception as e:
            self.logger.error(f"Error handling file summarization request: {e}")
            try:
                self.event_bus.publish("summarization.error", f"Error processing file summarization: {str(e)}")
            except Exception as pub_error:
                self.logger.error(f"Failed to publish error event: {pub_error}")
                # If we can't publish events, the UI won't know about the error
                # This is a critical communication failure
    
    def handle_summarization_text_async_request(self, event_data):
        """
        Handle async text summarization request event from UI.
        
        Args:
            event_data: Dictionary containing text and style
        """
        try:
            text = event_data.get("text", "")
            style = event_data.get("style", "concise")
            
            self.logger.info(f"Processing async text summarization request with style: {style}")
            
            # NOTE: Summarization now handled by performance-optimized backend bridge in MainWindow
            error_msg = "Summarization service disabled - handled by performance-optimized backend"
            self.logger.info(error_msg)
            # Don't publish error - let the main window bridge handle it
                
        except Exception as e:
            self.logger.error(f"Error handling async text summarization request: {e}")
            self.event_bus.publish("summarization.error", f"Error starting text summarization: {str(e)}")
    
    def handle_summarization_file_async_request(self, event_data):
        """
        Handle async file summarization request event from UI.
        
        Args:
            event_data: Dictionary containing file_path, style, and encoding
        """
        try:
            file_path = event_data.get("file_path", "")
            style = event_data.get("style", "concise")
            encoding = event_data.get("encoding", "utf-8")
            
            self.logger.info(f"Processing async file summarization request: {file_path}")
            
            # NOTE: File summarization now handled by performance-optimized backend bridge in MainWindow
            error_msg = "File summarization service disabled - handled by performance-optimized backend"
            self.logger.info(error_msg)
            # Don't publish error - let the main window bridge handle it
                
        except Exception as e:
            self.logger.error(f"Error handling async file summarization request: {e}")
            self.event_bus.publish("summarization.error", f"Error starting file summarization: {str(e)}")
    
    def process_startup_options(self):
        """Process startup options after the UI is initialized."""
        # Check if we should load an initial model
        initial_model = self.startup_options.get("initial_model")
        if initial_model:
            self.logger.info(f"Loading initial model: {initial_model}")
            
            # Use a timer to load the model after the UI is shown
            QTimer.singleShot(100, lambda: self.load_initial_model(initial_model))
    
    def load_initial_model(self, model_path):
        """
        Load an initial model.
        
        Args:
            model_path: Path to the model file
        """
        if not os.path.exists(model_path):
            self.logger.error(f"Initial model not found: {model_path}")
            QMessageBox.warning(
                self.main_window,
                "Model Not Found",
                f"The specified model file was not found:\n{model_path}"
            )
            return
        
        # Load the model through the main window
        if self.main_window:
            self.main_window._load_model(model_path)
    
    def run(self):
        """
        Run the application main loop.
        
        Returns:
            Exit code (0 for success, non-zero for error)
        """
        try:
            # Initialize components
            if not self.initialize_components():
                self.logger.error("Failed to initialize components")
                return 1
            
            # Check if main window was created
            if self.main_window is None:
                self.logger.error("Main window was not created during initialization")
                return 1
            
            # Show the main window
            self.main_window.show()
            
            # Process startup options
            self.process_startup_options()
            
            # Run the application
            self.logger.info("Entering application main loop")
            return self.app.exec()
            
        except Exception as e:
            self.logger.exception(f"Error running application: {e}")
            
            # Use error manager if available
            if hasattr(self, 'error_manager'):
                self.error_manager.handle_error(
                    e,
                    category=ErrorCategory.RUNTIME,
                    context="Application startup",
                    severity=ErrorSeverity.CRITICAL,
                    show_ui=True
                )
            else:
                # Fallback to basic error message if error manager isn't available
                error_message = f"An unexpected error occurred:\n\n{str(e)}"
                QMessageBox.critical(None, "Application Error", error_message)
            
            return 1