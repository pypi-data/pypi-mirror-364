"""
LLM Toolkit - A comprehensive toolkit for working with Large Language Models

This package provides an intuitive GUI interface for model loading, chat interactions,
document summarization, and email automation with support for multiple model backends.
"""

__version__ = "1.0.0"
__author__ = "Hussein Nazary"
__email__ = "hussainnazary2@gmail.com"
__license__ = "MIT"
__description__ = "A comprehensive toolkit for working with Large Language Models"
__url__ = "https://github.com/hussainnazary2/LLM-Toolkit"

# Package metadata
__all__ = [
    "__version__",
    "__author__", 
    "__email__",
    "__license__",
    "__description__",
    "__url__",
    "main",
    "get_version_info",
]

import sys
import logging
from typing import Dict, Any, Optional

# Set up basic logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger(__name__)


def get_version_info() -> Dict[str, Any]:
    """
    Get comprehensive version and system information.
    
    Returns:
        Dictionary containing version and system details
    """
    import platform
    
    version_info = {
        "llmtoolkit_version": __version__,
        "python_version": sys.version,
        "platform": platform.platform(),
        "architecture": platform.architecture()[0],
        "processor": platform.processor(),
    }
    
    # Try to get dependency versions
    try:
        import PySide6
        version_info["pyside6_version"] = PySide6.__version__
    except ImportError:
        version_info["pyside6_version"] = "Not installed"
    
    try:
        import ctransformers
        version_info["ctransformers_version"] = getattr(ctransformers, '__version__', 'unknown')
    except ImportError:
        version_info["ctransformers_version"] = "Not installed"
    
    try:
        import llama_cpp
        version_info["llama_cpp_python_version"] = getattr(llama_cpp, '__version__', 'unknown')
    except ImportError:
        version_info["llama_cpp_python_version"] = "Not installed"
    
    # Optional dependencies
    try:
        import transformers
        version_info["transformers_version"] = transformers.__version__
    except ImportError:
        version_info["transformers_version"] = "Not installed (optional)"
    
    try:
        import torch
        version_info["torch_version"] = torch.__version__
    except ImportError:
        version_info["torch_version"] = "Not installed (optional)"
    
    return version_info


def main(args: Optional[list] = None) -> int:
    """
    Main entry point for programmatic access to LLM Toolkit.
    
    Args:
        args: Optional command line arguments
        
    Returns:
        Exit code (0 for success, non-zero for error)
    """
    try:
        from .cli import main as cli_main
        return cli_main(args)
    except ImportError as e:
        logger.error(f"Failed to import CLI module: {e}")
        return 1
    except Exception as e:
        logger.error(f"Unexpected error in main: {e}")
        return 1


def print_version_info():
    """Print formatted version information to stdout."""
    info = get_version_info()
    
    print(f"LLM Toolkit v{info['llmtoolkit_version']}")
    print(f"Python {info['python_version']}")
    print(f"Platform: {info['platform']}")
    print(f"Architecture: {info['architecture']}")
    
    print("\nDependencies:")
    print(f"  PySide6: {info['pyside6_version']}")
    print(f"  ctransformers: {info['ctransformers_version']}")
    print(f"  llama-cpp-python: {info['llama_cpp_python_version']}")
    print(f"  transformers: {info['transformers_version']}")
    print(f"  torch: {info['torch_version']}")


# Ensure the package can be imported safely
try:
    # Test critical imports
    import PySide6
    logger.debug("PySide6 import successful")
except ImportError as e:
    logger.warning(f"PySide6 not available: {e}")

# Package initialization complete
logger.debug(f"LLM Toolkit v{__version__} package initialized")