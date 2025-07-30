"""
Main application runner for LLM Toolkit.

This module provides the main entry point for launching the GUI application.
"""

import sys
import os
import logging
from pathlib import Path
from typing import Optional

# Add the current directory to Python path for imports
current_dir = Path(__file__).parent.parent.parent
if str(current_dir) not in sys.path:
    sys.path.insert(0, str(current_dir))


def setup_application_environment(config_dir: Optional[str] = None) -> None:
    """
    Set up the application environment and paths.
    
    Args:
        config_dir: Optional custom configuration directory
    """
    # Use resource manager to get proper user config directory
    from llmtoolkit.resource_manager import get_user_config_dir
    
    if config_dir:
        config_path = Path(config_dir)
        # Create config directory if it doesn't exist
        config_path.mkdir(parents=True, exist_ok=True)
        # Set environment variable for the application to use
        os.environ["LLMTOOLKIT_CONFIG_DIR"] = str(config_path)
    else:
        # Use the resource manager's user config directory
        config_path = get_user_config_dir()
        # Set environment variable for the application to use
        os.environ["LLMTOOLKIT_CONFIG_DIR"] = str(config_path)
    
    logging.info(f"Configuration directory: {config_path}")


def run_application(
    model_path: Optional[str] = None,
    debug: bool = False,
    config_dir: Optional[str] = None
) -> int:
    """
    Run the LLM Toolkit GUI application.
    
    Args:
        model_path: Optional path to model file to load on startup
        debug: Enable debug mode
        config_dir: Optional custom configuration directory
        
    Returns:
        Exit code (0 for success, non-zero for error)
    """
    logger = logging.getLogger(__name__)
    
    try:
        # Set up application environment
        setup_application_environment(config_dir)
        
        # Import Qt application components
        from PySide6.QtWidgets import QApplication
        from PySide6.QtCore import Qt
        from PySide6.QtGui import QIcon
        
        # Create QApplication instance
        app = QApplication(sys.argv)
        app.setApplicationName("LLM Toolkit")
        app.setApplicationVersion("1.0.0")
        app.setOrganizationName("LLM Toolkit")
        
        # Set application icon if available
        try:
            from llmtoolkit.resource_manager import get_icon
            app_icon = get_icon("icon.ico")
            if app_icon:
                app.setWindowIcon(app_icon)
        except Exception as e:
            logger.debug(f"Could not set application icon: {e}")
        
        # Import and create the main application components
        logger.info("Initializing application components...")
        
        # Import the actual application controller
        from llmtoolkit.app.core.app_controller import ApplicationController
        from llmtoolkit.app.ui.splash_screen import SplashScreen
        
        # Create splash screen
        splash = SplashScreen()
        splash.show()
        app.processEvents()
        
        # Create application controller with startup options
        startup_options = {
            'model_path': model_path,
            'debug': debug,
            'config_dir': config_dir
        }
        app_controller = ApplicationController(startup_options)
        
        # Initialize the application
        splash.update_progress(50, "Initializing components...")
        app.processEvents()
        
        try:
            app_controller.initialize_components()
        except Exception as e:
            splash.close()
            logger.error(f"Failed to initialize application: {e}")
            return 1
        
        # Load initial model if specified
        if model_path:
            splash.update_progress(75, f"Loading model: {Path(model_path).name}")
            app.processEvents()
            # Schedule model loading after UI is shown
            from PySide6.QtCore import QTimer
            QTimer.singleShot(100, lambda: app_controller.load_initial_model(model_path))
        
        # Complete initialization and show main window
        splash.update_progress(100, "Starting application...")
        app.processEvents()
        
        # Show the main window and close splash
        if app_controller.main_window is not None:
            app_controller.main_window.show()
            splash.finish(app_controller.main_window)
        else:
            splash.close()
            logger.error("Main window was not created")
            return 1
        
        logger.info("Application started successfully")
        
        # Run the application event loop
        return app.exec()
        
    except ImportError as e:
        logger.error(f"Failed to import required GUI components: {e}")
        print(f"Error: Missing GUI dependencies. Please ensure PySide6 is installed: {e}")
        return 1
    except Exception as e:
        logger.error(f"Failed to start application: {e}")
        print(f"Error: Failed to start application: {e}")
        return 1


if __name__ == "__main__":
    # Allow running this module directly for testing
    import argparse
    
    parser = argparse.ArgumentParser()
    parser.add_argument("--model", help="Model path")
    parser.add_argument("--debug", action="store_true", help="Debug mode")
    parser.add_argument("--config-dir", help="Config directory")
    
    args = parser.parse_args()
    
    sys.exit(run_application(
        model_path=args.model,
        debug=args.debug,
        config_dir=args.config_dir
    ))