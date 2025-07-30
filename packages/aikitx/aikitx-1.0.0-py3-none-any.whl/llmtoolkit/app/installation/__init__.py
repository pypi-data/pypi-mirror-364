"""
Installation and setup utilities for backend management.

This module provides utilities for:
- Backend installation and dependency management
- Installation validation and testing
- Troubleshooting and repair tools
- Setup script management
"""

from .backend_installer import BackendInstaller
from .dependency_detector import DependencyDetector
from .installation_validator import InstallationValidator
from .troubleshooter import BackendTroubleshooter
from .setup_manager import SetupManager

__all__ = [
    'BackendInstaller',
    'DependencyDetector', 
    'InstallationValidator',
    'BackendTroubleshooter',
    'SetupManager'
]