#!/usr/bin/env python3
"""
llm toolkit - Main Entry Point

This is the main entry point for llm toolkit.
It initializes the application, sets up logging, and launches the UI.

Command-line arguments:
    --debug: Enable debug logging
    --log-file PATH: Specify a custom log file path
    --model PATH: Open a model file on startup (supports GGUF, safetensors, PyTorch, HF model IDs)
    --version: Show version information and exit
    --help: Show help message and exit
"""

import sys
import logging
import os
import argparse
import traceback
from pathlib import Path
from typing import Optional, List, Dict, Any

# Add the project root to the Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Import application components
from llmtoolkit.app.core.app_controller import ApplicationController
from llmtoolkit import __version__

# Application constants
APP_NAME = "llm toolkit"
APP_VERSION = __version__
APP_AUTHOR = "llm toolkit Team"
APP_CONFIG_DIR = Path.home() / ".llm-toolkit"
APP_LOG_DIR = APP_CONFIG_DIR / "logs"

def parse_arguments() -> argparse.Namespace:
    """
    Parse command-line arguments.
    
    Returns:
        Parsed command-line arguments
    """
    parser = argparse.ArgumentParser(description=f"{APP_NAME} - A universal desktop application for AI model files")
    
    parser.add_argument("--debug", action="store_true", help="Enable debug logging")
    parser.add_argument("--log-file", type=str, help="Specify a custom log file path")
    parser.add_argument("--model", type=str, help="Open a model file on startup (GGUF, safetensors, PyTorch, or HF model ID)")
    parser.add_argument("--version", action="store_true", help="Show version information and exit")
    
    return parser.parse_args()

def setup_logging(debug: bool = False, log_file: Optional[str] = None) -> logging.Logger:
    """
    Configure the application logging system.
    
    Args:
        debug: Whether to enable debug logging
        log_file: Optional custom log file path
        
    Returns:
        Configured logger
    """
    # Create log directory if it doesn't exist
    if not log_file:
        APP_LOG_DIR.mkdir(parents=True, exist_ok=True)
        log_file = APP_LOG_DIR / "app.log"
    else:
        log_path = Path(log_file)
        log_path.parent.mkdir(parents=True, exist_ok=True)
    
    # Set log level
    log_level = logging.DEBUG if debug else logging.INFO
    
    # Configure logging
    log_format = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    logging.basicConfig(
        level=log_level,
        format=log_format,
        handlers=[
            logging.StreamHandler(),
            logging.FileHandler(log_file, mode="a")
        ]
    )
    
    # Create logger
    logger = logging.getLogger("llm_toolkit")
    logger.info(f"Logging system initialized (level: {logging.getLevelName(log_level)})")
    
    if debug:
        logger.debug("Debug logging enabled")
    
    return logger

def show_version() -> None:
    """Display version information and exit."""
    print(f"{APP_NAME} v{APP_VERSION}")
    print(f"Python {sys.version}")
    sys.exit(0)

def main() -> int:
    """
    Main application entry point.
    
    Returns:
        Exit code (0 for success, non-zero for error)
    """
    # Parse command-line arguments
    args = parse_arguments()
    
    # Show version if requested
    if args.version:
        show_version()
    
    # Set up logging
    logger = setup_logging(debug=args.debug, log_file=args.log_file)
    
    try:
        # Log system information
        logger.info(f"Starting {APP_NAME} v{APP_VERSION}")
        logger.info(f"Python version: {sys.version}")
        logger.info(f"Operating system: {sys.platform}")
        
        # Create application controller with startup options
        startup_options = {
            "initial_model": args.model
        }
        
        # Create the application controller
        app_controller = ApplicationController(startup_options)
        
        # Check if we should show the splash screen
        show_splash = not args.debug  # Skip splash in debug mode
        
        if show_splash:
            # Import and show splash screen
            from llmtoolkit.app.ui.splash_screen import SplashScreen
            splash = SplashScreen()
            
            # Use the splash screen to show startup progress
            SplashScreen.simulate_startup(splash, app_controller)
            
            # Run the application (main window is already shown by splash)
            exit_code = app_controller.app.exec()
        else:
            # Run normally without splash screen
            exit_code = app_controller.run()
        
        logger.info(f"Application exited with code {exit_code}")
        return exit_code
        
    except KeyboardInterrupt:
        logger.info("Application terminated by user (KeyboardInterrupt)")
        return 0
        
    except Exception as e:
        logger.critical(f"Unhandled exception: {e}")
        logger.critical(f"Exception details: {traceback.format_exc()}")
        
        # In a real application, we might show an error dialog here
        print(f"Error: {e}", file=sys.stderr)
        print(f"Full traceback:\n{traceback.format_exc()}", file=sys.stderr)
        return 1

if __name__ == "__main__":
    sys.exit(main())