"""
Resource Management Module for LLM Toolkit

This module provides centralized resource management using importlib.resources
for proper package resource access when installed via pip.
"""

import json
import logging
from pathlib import Path
from typing import Optional, Dict, Any, Union
import sys

# Import the appropriate resources module based on Python version
if sys.version_info >= (3, 9):
    from importlib import resources
else:
    import importlib_resources as resources

from PySide6.QtGui import QPixmap, QIcon
from PySide6.QtCore import QStandardPaths

logger = logging.getLogger(__name__)


class ResourceManager:
    """
    Centralized resource manager for accessing package resources.
    
    This class provides methods to access icons, configuration files,
    and other resources bundled with the package using importlib.resources.
    """
    
    def __init__(self):
        self._resource_cache = {}
        self._user_config_dir = None
        self._setup_user_directories()
    
    def _setup_user_directories(self):
        """Set up user-specific directories for configuration and data."""
        # Use QStandardPaths for platform-appropriate directories
        config_dir = QStandardPaths.writableLocation(QStandardPaths.AppConfigLocation)
        if not config_dir:
            # Fallback to manual platform detection
            import os
            if sys.platform == "win32":
                config_dir = Path(os.environ.get("APPDATA", "")) / "llmtoolkit"
            elif sys.platform == "darwin":
                config_dir = Path.home() / "Library" / "Application Support" / "llmtoolkit"
            else:
                config_dir = Path.home() / ".config" / "llmtoolkit"
        else:
            config_dir = Path(config_dir)
        
        self._user_config_dir = config_dir
        self._user_config_dir.mkdir(parents=True, exist_ok=True)
        logger.debug(f"User config directory: {self._user_config_dir}")
    
    def get_resource_path(self, resource_name: str, resource_type: str = "") -> Optional[Path]:
        """
        Get the path to a resource file using importlib.resources.
        
        Args:
            resource_name: Name of the resource file
            resource_type: Type/subdirectory of resource (e.g., 'icons', 'themes')
            
        Returns:
            Path to the resource file, or None if not found
        """
        try:
            if resource_type:
                package_name = f"llmtoolkit.resources.{resource_type}"
            else:
                package_name = "llmtoolkit.resources"
            
            # Use importlib.resources to get the resource
            if sys.version_info >= (3, 9):
                resource_files = resources.files(package_name)
                resource_path = resource_files / resource_name
                if resource_path.is_file():
                    return Path(str(resource_path))
            else:
                # For Python < 3.9, use the older API
                with resources.path(package_name, resource_name) as resource_path:
                    if resource_path.exists():
                        return resource_path
            
            logger.warning(f"Resource not found: {resource_name} in {package_name}")
            return None
            
        except Exception as e:
            logger.error(f"Error accessing resource {resource_name}: {e}")
            return None
    
    def get_resource_content(self, resource_name: str, resource_type: str = "") -> Optional[bytes]:
        """
        Get the content of a resource file as bytes.
        
        Args:
            resource_name: Name of the resource file
            resource_type: Type/subdirectory of resource
            
        Returns:
            Resource content as bytes, or None if not found
        """
        try:
            if resource_type:
                package_name = f"llmtoolkit.resources.{resource_type}"
            else:
                package_name = "llmtoolkit.resources"
            
            # Use importlib.resources to read the resource
            if sys.version_info >= (3, 9):
                resource_files = resources.files(package_name)
                resource_file = resource_files / resource_name
                if resource_file.is_file():
                    return resource_file.read_bytes()
            else:
                # For Python < 3.9, use the older API
                return resources.read_binary(package_name, resource_name)
            
            logger.warning(f"Resource not found: {resource_name} in {package_name}")
            return None
            
        except Exception as e:
            logger.error(f"Error reading resource {resource_name}: {e}")
            return None
    
    def get_resource_text(self, resource_name: str, resource_type: str = "", encoding: str = "utf-8") -> Optional[str]:
        """
        Get the content of a resource file as text.
        
        Args:
            resource_name: Name of the resource file
            resource_type: Type/subdirectory of resource
            encoding: Text encoding to use
            
        Returns:
            Resource content as string, or None if not found
        """
        try:
            if resource_type:
                package_name = f"llmtoolkit.resources.{resource_type}"
            else:
                package_name = "llmtoolkit.resources"
            
            # Use importlib.resources to read the resource
            if sys.version_info >= (3, 9):
                resource_files = resources.files(package_name)
                resource_file = resource_files / resource_name
                if resource_file.is_file():
                    return resource_file.read_text(encoding=encoding)
            else:
                # For Python < 3.9, use the older API
                return resources.read_text(package_name, resource_name, encoding=encoding)
            
            logger.warning(f"Resource not found: {resource_name} in {package_name}")
            return None
            
        except Exception as e:
            logger.error(f"Error reading resource {resource_name}: {e}")
            return None
    
    def get_json_resource(self, resource_name: str, resource_type: str = "") -> Optional[Dict[str, Any]]:
        """
        Load a JSON resource file.
        
        Args:
            resource_name: Name of the JSON resource file
            resource_type: Type/subdirectory of resource
            
        Returns:
            Parsed JSON data, or None if not found or invalid
        """
        try:
            content = self.get_resource_text(resource_name, resource_type)
            if content:
                return json.loads(content)
            return None
        except json.JSONDecodeError as e:
            logger.error(f"Error parsing JSON resource {resource_name}: {e}")
            return None
    
    def get_icon(self, icon_name: str) -> Optional[QIcon]:
        """
        Load an icon resource as QIcon.
        
        Args:
            icon_name: Name of the icon file
            
        Returns:
            QIcon object, or None if not found
        """
        cache_key = f"icon_{icon_name}"
        if cache_key in self._resource_cache:
            return self._resource_cache[cache_key]
        
        try:
            # Try to get icon from resources
            icon_content = self.get_resource_content(icon_name, "icons")
            if icon_content:
                pixmap = QPixmap()
                if pixmap.loadFromData(icon_content):
                    icon = QIcon(pixmap)
                    self._resource_cache[cache_key] = icon
                    return icon
            
            # Fallback: try to load from root resources
            icon_content = self.get_resource_content(icon_name)
            if icon_content:
                pixmap = QPixmap()
                if pixmap.loadFromData(icon_content):
                    icon = QIcon(pixmap)
                    self._resource_cache[cache_key] = icon
                    return icon
            
            logger.warning(f"Icon not found: {icon_name}")
            return None
            
        except Exception as e:
            logger.error(f"Error loading icon {icon_name}: {e}")
            return None
    
    def get_pixmap(self, image_name: str, resource_type: str = "icons") -> Optional[QPixmap]:
        """
        Load an image resource as QPixmap.
        
        Args:
            image_name: Name of the image file
            resource_type: Type/subdirectory of resource
            
        Returns:
            QPixmap object, or None if not found
        """
        cache_key = f"pixmap_{resource_type}_{image_name}"
        if cache_key in self._resource_cache:
            return self._resource_cache[cache_key]
        
        try:
            image_content = self.get_resource_content(image_name, resource_type)
            if image_content:
                pixmap = QPixmap()
                if pixmap.loadFromData(image_content):
                    self._resource_cache[cache_key] = pixmap
                    return pixmap
            
            logger.warning(f"Image not found: {image_name} in {resource_type}")
            return None
            
        except Exception as e:
            logger.error(f"Error loading image {image_name}: {e}")
            return None
    
    def get_default_config(self) -> Dict[str, Any]:
        """
        Load the default configuration.
        
        Returns:
            Default configuration dictionary
        """
        config = self.get_json_resource("default_config.json")
        if config is None:
            # Fallback default configuration
            logger.warning("Could not load default_config.json, using fallback")
            config = {
                "theme": "default",
                "recent_models": [],
                "window_size": [1200, 800],
                "default_model_dir": "",
                "addon_dir": "addons",
                "log_level": "INFO",
                "default_temperature": 0.7,
                "default_max_tokens": 2048,
                "default_system_prompt": "You are a helpful AI assistant."
            }
        return config
    
    def get_sample_prompts(self) -> Dict[str, Any]:
        """
        Load the sample prompts.
        
        Returns:
            Sample prompts dictionary
        """
        prompts = self.get_json_resource("sample_prompts.json")
        if prompts is None:
            # Fallback sample prompts
            logger.warning("Could not load sample_prompts.json, using fallback")
            prompts = {
                "prompts": [
                    {
                        "name": "Default Assistant",
                        "prompt": "You are a helpful AI assistant."
                    }
                ]
            }
        return prompts
    
    def get_user_config_dir(self) -> Path:
        """
        Get the user configuration directory.
        
        Returns:
            Path to user configuration directory
        """
        return self._user_config_dir
    
    def clear_cache(self):
        """Clear the resource cache."""
        self._resource_cache.clear()
        logger.debug("Resource cache cleared")


# Global resource manager instance
_resource_manager = None


def get_resource_manager() -> ResourceManager:
    """
    Get the global resource manager instance.
    
    Returns:
        ResourceManager instance
    """
    global _resource_manager
    if _resource_manager is None:
        _resource_manager = ResourceManager()
    return _resource_manager


# Convenience functions for common resource access patterns
def get_icon(icon_name: str) -> Optional[QIcon]:
    """Get an icon resource."""
    return get_resource_manager().get_icon(icon_name)


def get_pixmap(image_name: str, resource_type: str = "icons") -> Optional[QPixmap]:
    """Get a pixmap resource."""
    return get_resource_manager().get_pixmap(image_name, resource_type)


def get_default_config() -> Dict[str, Any]:
    """Get the default configuration."""
    return get_resource_manager().get_default_config()


def get_sample_prompts() -> Dict[str, Any]:
    """Get the sample prompts."""
    return get_resource_manager().get_sample_prompts()


def get_user_config_dir() -> Path:
    """Get the user configuration directory."""
    return get_resource_manager().get_user_config_dir()