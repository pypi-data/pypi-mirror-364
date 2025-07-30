"""
Command Line Interface for LLM Toolkit

This module provides the main entry point for the llmtoolkit command line interface.
"""

import sys
import argparse
import logging
from pathlib import Path
from typing import Optional, List

from .platform_utils import get_platform_manager, setup_platform_environment

# Package metadata - define locally to avoid circular imports
__version__ = "1.0.0"
__description__ = "A comprehensive toolkit for working with Large Language Models"

def print_version_info():
    """Print formatted version information to stdout."""
    pm = get_platform_manager()
    system_info = pm.get_system_info()
    
    print(f"LLM Toolkit v{__version__}")
    print(f"Python {system_info['python_version']} ({system_info['python_implementation']})")
    print(f"Platform: {system_info['system']} {system_info['release']} ({system_info['architecture']})")
    print(f"Machine: {system_info['machine']}")
    
    # GUI availability
    gui_available, gui_error = pm.check_gui_availability()
    gui_status = "Available" if gui_available else f"Not available ({gui_error})"
    print(f"GUI: {gui_status}")
    
    print("\nDependencies:")
    dependencies = [
        ('PySide6', 'PySide6'),
        ('ctransformers', 'ctransformers'),
        ('llama-cpp-python', 'llama_cpp'),
        ('psutil', 'psutil'),
        ('PyYAML', 'yaml'),
        ('requests', 'requests'),
    ]
    
    for dep_name, import_name in dependencies:
        try:
            module = __import__(import_name)
            version = getattr(module, '__version__', 'unknown')
            print(f"  {dep_name}: {version}")
        except ImportError:
            print(f"  {dep_name}: Not installed")
    
    print(f"\nDirectories:")
    print(f"  Config: {pm.get_config_directory()}")
    print(f"  Data: {pm.get_data_directory()}")
    print(f"  Cache: {pm.get_cache_directory()}")


def create_parser() -> argparse.ArgumentParser:
    """
    Create and configure the argument parser.
    
    Returns:
        Configured ArgumentParser instance
    """
    parser = argparse.ArgumentParser(
        prog="llmtoolkit",
        description=__description__,
        epilog="For more information, visit: https://github.com/hussainnazary2/LLM-Toolkit"
    )
    
    parser.add_argument(
        "--version",
        action="version",
        version=f"llmtoolkit {__version__}"
    )
    
    parser.add_argument(
        "--version-info",
        action="store_true",
        help="Show detailed version and system information"
    )
    
    parser.add_argument(
        "--model",
        type=str,
        metavar="PATH",
        help="Load a specific model file on startup (supports GGUF, GGML, PyTorch, HF model IDs)"
    )
    
    parser.add_argument(
        "--debug",
        action="store_true",
        help="Enable debug logging"
    )
    
    parser.add_argument(
        "--log-file",
        type=str,
        metavar="PATH",
        help="Specify a custom log file path"
    )
    
    parser.add_argument(
        "--no-gui",
        action="store_true",
        help="Run in headless mode (for testing/debugging)"
    )
    
    parser.add_argument(
        "--config-dir",
        type=str,
        metavar="PATH",
        help="Specify custom configuration directory"
    )
    
    return parser


def setup_logging(debug: bool = False, log_file: Optional[str] = None) -> None:
    """
    Set up logging configuration.
    
    Args:
        debug: Enable debug level logging
        log_file: Optional log file path
    """
    level = logging.DEBUG if debug else logging.INFO
    
    # Configure root logger
    logging.basicConfig(
        level=level,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[]
    )
    
    # Console handler
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(level)
    console_formatter = logging.Formatter('%(levelname)s - %(message)s')
    console_handler.setFormatter(console_formatter)
    
    # File handler if specified
    handlers = [console_handler]
    if log_file:
        try:
            file_handler = logging.FileHandler(log_file)
            file_handler.setLevel(level)
            file_formatter = logging.Formatter(
                '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
            )
            file_handler.setFormatter(file_formatter)
            handlers.append(file_handler)
        except Exception as e:
            print(f"Warning: Could not create log file {log_file}: {e}")
    
    # Configure root logger with handlers
    root_logger = logging.getLogger()
    root_logger.handlers.clear()
    for handler in handlers:
        root_logger.addHandler(handler)


def validate_arguments(args: argparse.Namespace) -> bool:
    """
    Validate command line arguments.
    
    Args:
        args: Parsed arguments
        
    Returns:
        True if arguments are valid, False otherwise
    """
    # Validate model path if provided
    if args.model:
        model_path = Path(args.model)
        if not model_path.exists() and not args.model.startswith(('http://', 'https://')):
            # Check if it might be a Hugging Face model ID
            if '/' not in args.model:
                print(f"Warning: Model path '{args.model}' does not exist and doesn't appear to be a valid Hugging Face model ID")
                return False
    
    # Validate log file path if provided
    if args.log_file:
        log_path = Path(args.log_file)
        try:
            log_path.parent.mkdir(parents=True, exist_ok=True)
        except Exception as e:
            print(f"Error: Cannot create log file directory: {e}")
            return False
    
    # Validate config directory if provided
    if args.config_dir:
        config_path = Path(args.config_dir)
        try:
            config_path.mkdir(parents=True, exist_ok=True)
        except Exception as e:
            print(f"Error: Cannot create config directory: {e}")
            return False
    
    return True


def run_gui(args: argparse.Namespace) -> int:
    """
    Launch the GUI application.
    
    Args:
        args: Parsed command line arguments
        
    Returns:
        Exit code
    """
    pm = get_platform_manager()
    
    # Check GUI availability
    gui_available, gui_error = pm.check_gui_availability()
    if not gui_available:
        logging.error(f"GUI not available: {gui_error}")
        print(f"Error: GUI not available on this platform: {gui_error}")
        print("Try running with --no-gui flag for headless mode.")
        return 1
    
    try:
        # Import GUI components
        from .app.main import run_application
        
        # Use platform-specific config directory if not specified
        config_dir = args.config_dir
        if not config_dir:
            config_dir = str(pm.get_config_directory())
        
        # Prepare application arguments
        app_args = {
            'model_path': args.model,
            'debug': args.debug,
            'config_dir': config_dir,
        }
        
        # Launch the application
        return run_application(**app_args)
        
    except ImportError as e:
        logging.error(f"Failed to import GUI components: {e}")
        print("Error: GUI components not available. Please check your installation.")
        print("Missing dependencies may include: PySide6, Qt6")
        return 1
    except Exception as e:
        logging.error(f"Failed to start GUI application: {e}")
        print(f"Error: Failed to start application: {e}")
        return 1


def main(argv: Optional[List[str]] = None) -> int:
    """
    Main entry point for the CLI.
    
    Args:
        argv: Optional command line arguments (defaults to sys.argv)
        
    Returns:
        Exit code (0 for success, non-zero for error)
    """
    if argv is None:
        argv = sys.argv[1:]
    
    try:
        # Set up platform environment early
        setup_platform_environment()
        
        # Parse arguments
        parser = create_parser()
        args = parser.parse_args(argv)
        
        # Handle version info request
        if args.version_info:
            print_version_info()
            return 0
        
        # Set up logging
        setup_logging(debug=args.debug, log_file=args.log_file)
        
        logger = logging.getLogger(__name__)
        pm = get_platform_manager()
        
        logger.info(f"Starting LLM Toolkit v{__version__}")
        logger.info(f"Platform: {pm.system} ({pm.get_platform_info()['architecture']})")
        
        # Validate arguments
        if not validate_arguments(args):
            return 1
        
        # Handle no-gui mode
        if args.no_gui:
            logger.info("Running in headless mode")
            print("LLM Toolkit running in headless mode (no GUI)")
            print("This mode is primarily for testing and debugging.")
            return 0
        
        # Launch GUI application
        logger.info("Launching GUI application")
        return run_gui(args)
        
    except KeyboardInterrupt:
        print("\nInterrupted by user")
        return 130
    except Exception as e:
        logging.error(f"Unexpected error: {e}")
        print(f"Error: {e}")
        return 1


if __name__ == "__main__":
    sys.exit(main())