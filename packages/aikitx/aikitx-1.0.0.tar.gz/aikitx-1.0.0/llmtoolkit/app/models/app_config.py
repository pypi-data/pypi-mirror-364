"""
Application Configuration Model

This module defines the AppConfig class, which represents the application configuration.
"""

import os
import json
import jsonschema
from typing import Dict, List, Tuple, Any, Optional, Union, Set

# Configuration schema version
CONFIG_VERSION = "1.0.0"

# JSON Schema for configuration validation
CONFIG_SCHEMA = {
    "type": "object",
    "properties": {
        "version": {"type": "string"},
        "theme": {"type": "string"},
        "window_size": {
            "type": "array",
            "items": {"type": "integer"},
            "minItems": 2,
            "maxItems": 2
        },
        "window_position": {
            "type": "array",
            "items": {"type": "integer"},
            "minItems": 2,
            "maxItems": 2
        },
        "window_maximized": {"type": "boolean"},
        "default_model_dir": {"type": "string"},
        "recent_models": {
            "type": "array",
            "items": {"type": "string"}
        },
        "max_recent_models": {"type": "integer", "minimum": 1},

        "log_level": {"type": "string", "enum": ["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"]},
        "use_hardware_acceleration": {"type": "boolean"},
        "max_memory_usage": {"type": "integer", "minimum": 0},
        "default_temperature": {"type": "number", "minimum": 0.0, "maximum": 2.0},
        "default_max_tokens": {"type": "integer", "minimum": 1},
        "default_system_prompt": {"type": "string"},
        "ai_settings": {
            "type": "object",
            "properties": {
                "temperature": {"type": "number", "minimum": 0.0, "maximum": 2.0},
                "max_tokens": {"type": "integer", "minimum": 1},
                "system_prompt": {"type": "string"},
                "top_p": {"type": "number", "minimum": 0.0, "maximum": 1.0},
                "top_k": {"type": "integer", "minimum": 0},
                "repeat_penalty": {"type": "number", "minimum": 0.0}
            }
        }
    },
    "required": ["version"]
}

class AppConfig:
    """
    Application configuration data model.
    
    This class stores all application settings and preferences.
    """
    
    def __init__(self):
        """Initialize with default configuration values."""
        # Version information
        self.version = CONFIG_VERSION
        
        # UI settings
        self.theme = "system"  # "system", "light", "dark", or custom theme name
        self.window_size = (1024, 768)
        self.window_position = (100, 100)
        self.window_maximized = False
        
        # Model settings
        self.default_model_dir = ""
        self.recent_models = []  # List of recently opened model paths
        self.max_recent_models = 10
        

        
        # Performance settings
        self.log_level = "INFO"
        self.use_hardware_acceleration = True
        self.max_memory_usage = 0  # 0 means no limit
        
        # Backend configuration settings
        self.backend_config_path = ""  # Path to backend configuration file
        self.auto_optimize_backends = True  # Automatically optimize backend configs for hardware
        self.backend_switching_mode = "immediate"  # "immediate", "on_next_load", "manual"
        
        # AI settings
        self.default_temperature = 0.7
        self.default_max_tokens = 2048
        self.default_system_prompt = "You are a helpful AI assistant."
        self.ai_settings = {
            "temperature": 0.7,
            "max_tokens": 2048,
            "system_prompt": "You are a helpful AI assistant.",
            "top_p": 0.9,
            "top_k": 40,
            "repeat_penalty": 1.1
        }
        
        # Internal state (not persisted)
        self._modified = False
        self._loaded_from = None
    
    def to_dict(self) -> Dict[str, Any]:
        """
        Convert configuration to a dictionary.
        
        Returns:
            Dictionary representation of the configuration
        """
        return {
            "version": self.version,
            "theme": self.theme,
            "window_size": self.window_size,
            "window_position": self.window_position,
            "window_maximized": self.window_maximized,
            "default_model_dir": self.default_model_dir,
            "recent_models": self.recent_models,
            "max_recent_models": self.max_recent_models,

            "log_level": self.log_level,
            "use_hardware_acceleration": self.use_hardware_acceleration,
            "max_memory_usage": self.max_memory_usage,
            "default_temperature": self.default_temperature,
            "default_max_tokens": self.default_max_tokens,
            "default_system_prompt": self.default_system_prompt,
            "ai_settings": self.ai_settings,
            "backend_config_path": self.backend_config_path,
            "auto_optimize_backends": self.auto_optimize_backends,
            "backend_switching_mode": self.backend_switching_mode
        }
    
    def update_from_dict(self, config_dict: Dict[str, Any]) -> None:
        """
        Update configuration from a dictionary.
        
        Args:
            config_dict: Dictionary containing configuration values
        """
        # Update only keys that exist in the dictionary
        for key, value in config_dict.items():
            if hasattr(self, key):
                # Convert lists to tuples for window_size and window_position
                if key in ["window_size", "window_position"] and isinstance(value, list):
                    value = tuple(value)
                setattr(self, key, value)
    
    def add_recent_model(self, model_path: str) -> None:
        """
        Add a model path to the recent models list.
        
        Args:
            model_path: Path to the model file
        """
        # Remove if already in list
        if model_path in self.recent_models:
            self.recent_models.remove(model_path)
        
        # Add to the beginning of the list
        self.recent_models.insert(0, model_path)
        
        # Trim list if needed
        if len(self.recent_models) > self.max_recent_models:
            self.recent_models = self.recent_models[:self.max_recent_models]
        
        # Mark as modified
        self._modified = True
    
    def validate(self) -> Tuple[bool, Optional[str]]:
        """
        Validate the configuration against the schema.
        
        Returns:
            Tuple of (is_valid, error_message)
        """
        try:
            # Convert to dictionary for validation
            config_dict = self.to_dict()
            
            # Convert tuples to lists for JSON schema validation
            if "window_size" in config_dict and isinstance(config_dict["window_size"], tuple):
                config_dict["window_size"] = list(config_dict["window_size"])
            if "window_position" in config_dict and isinstance(config_dict["window_position"], tuple):
                config_dict["window_position"] = list(config_dict["window_position"])
            
            # Validate against schema
            jsonschema.validate(instance=config_dict, schema=CONFIG_SCHEMA)
            return True, None
        except jsonschema.exceptions.ValidationError as e:
            return False, str(e)
    
    def migrate_from_version(self, old_version: str, config_dict: Dict[str, Any]) -> Dict[str, Any]:
        """
        Migrate configuration from an older version.
        
        Args:
            old_version: The version of the configuration to migrate from
            config_dict: The configuration dictionary to migrate
            
        Returns:
            Migrated configuration dictionary
        """
        # Handle version migrations
        if old_version == "1.0.0":
            # No migration needed for same version
            return config_dict
        
        # Add future version migrations here
        # For example:
        # if old_version == "1.0.0" and CONFIG_VERSION == "1.1.0":
        #     # Migrate from 1.0.0 to 1.1.0
        #     if "new_field" not in config_dict:
        #         config_dict["new_field"] = "default_value"
        
        # Update version
        config_dict["version"] = CONFIG_VERSION
        return config_dict
    
    def reset_to_defaults(self) -> None:
        """Reset all configuration values to defaults."""
        # Create a new instance with default values
        defaults = AppConfig()
        
        # Copy all attributes except internal state
        for key, value in defaults.__dict__.items():
            if not key.startswith("_"):
                setattr(self, key, value)
        
        # Mark as modified
        self._modified = True
    
    def is_modified(self) -> bool:
        """
        Check if the configuration has been modified since loading.
        
        Returns:
            True if the configuration has been modified, False otherwise
        """
        return self._modified
    
    def mark_saved(self) -> None:
        """Mark the configuration as saved (not modified)."""
        self._modified = False
    
    def get_ai_setting(self, key: str, default: Any = None) -> Any:
        """
        Get an AI setting value.
        
        Args:
            key: The AI setting key
            default: Default value to return if key is not found
            
        Returns:
            The AI setting value, or default if not found
        """
        return self.ai_settings.get(key, default)
    
    def set_ai_setting(self, key: str, value: Any) -> None:
        """
        Set an AI setting value.
        
        Args:
            key: The AI setting key
            value: The value to set
        """
        self.ai_settings[key] = value
        self._modified = True
    
    def update_ai_settings(self, settings: Dict[str, Any]) -> None:
        """
        Update multiple AI settings at once.
        
        Args:
            settings: Dictionary of AI settings to update
        """
        self.ai_settings.update(settings)
        self._modified = True
    
    def reset_ai_settings_to_defaults(self) -> None:
        """Reset AI settings to default values."""
        defaults = AppConfig()
        self.ai_settings = defaults.ai_settings.copy()
        self.default_temperature = defaults.default_temperature
        self.default_max_tokens = defaults.default_max_tokens
        self.default_system_prompt = defaults.default_system_prompt
        self._modified = True