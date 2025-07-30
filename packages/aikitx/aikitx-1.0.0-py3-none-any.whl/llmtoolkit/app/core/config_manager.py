"""
Configuration Manager

This module handles application configuration loading, saving, and access.
It supports configuration validation, versioning, and migration.
"""

import json
import logging
import os
import shutil
import time
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple, Callable, Set, Union

from llmtoolkit.app.models.app_config import AppConfig, CONFIG_VERSION

class ConfigChangeEvent:
    """Event data for configuration changes."""
    
    def __init__(self, key: str, old_value: Any, new_value: Any):
        """
        Initialize a configuration change event.
        
        Args:
            key: The configuration key that changed
            old_value: The previous value
            new_value: The new value
        """
        self.key = key
        self.old_value = old_value
        self.new_value = new_value

class ConfigManager:
    """
    Manages application configuration.
    
    This class is responsible for:
    - Loading configuration from disk
    - Saving configuration to disk
    - Providing access to configuration values
    - Notifying subscribers of configuration changes
    - Validating configuration data
    - Migrating configuration between versions
    """
    
    def __init__(self, config_path: Path, system_config_path: Optional[Path] = None):
        """
        Initialize the configuration manager.
        
        Args:
            config_path: Path to the user configuration file
            system_config_path: Optional path to system-wide configuration file
        """
        self.logger = logging.getLogger("gguf_loader.config")
        self.config_path = config_path
        self.system_config_path = system_config_path
        self.config = AppConfig()
        self.change_callbacks: List[Callable[[str, Any, Any], None]] = []
        self.auto_save = True
        self._last_save_time = 0
        self._save_interval = 5  # Minimum seconds between auto-saves
    
    def load(self) -> bool:
        """
        Load configuration from disk.
        
        Returns:
            True if configuration was loaded successfully, False otherwise
        """
        try:
            # Create config directory if it doesn't exist
            os.makedirs(os.path.dirname(self.config_path), exist_ok=True)
            
            # First try to load system-wide configuration if available
            system_config = {}
            if self.system_config_path and os.path.exists(self.system_config_path):
                try:
                    with open(self.system_config_path, 'r') as f:
                        system_config = json.load(f)
                    self.logger.info(f"System configuration loaded from {self.system_config_path}")
                except Exception as e:
                    self.logger.warning(f"Error loading system configuration: {e}")
            
            # Check if user config file exists
            if not os.path.exists(self.config_path):
                self.logger.info(f"Configuration file not found at {self.config_path}, creating default")
                self._create_default_config()
                return True
            
            # Load user config from file
            with open(self.config_path, 'r') as f:
                user_config = json.load(f)
            
            # Check if we need to migrate the configuration
            if "version" in user_config and user_config["version"] != CONFIG_VERSION:
                self.logger.info(f"Migrating configuration from version {user_config['version']} to {CONFIG_VERSION}")
                # Create a backup before migration
                backup_path = f"{self.config_path}.{user_config['version']}.bak"
                shutil.copy2(self.config_path, backup_path)
                self.logger.info(f"Configuration backup created at {backup_path}")
                
                # Migrate the configuration
                user_config = self.config.migrate_from_version(user_config["version"], user_config)
            
            # Merge system and user configurations (user takes precedence)
            config_data = {**system_config, **user_config}
            
            # Validate the configuration
            is_valid, error = self._validate_config(config_data)
            if not is_valid:
                self.logger.warning(f"Invalid configuration: {error}")
                self.logger.warning("Using default configuration")
                self._create_default_config()
                return False
            
            # Update config object with loaded data
            self.config.update_from_dict(config_data)
            self.config._loaded_from = str(self.config_path)
            self.config._modified = False
            
            self.logger.info(f"Configuration loaded from {self.config_path}")
            return True
            
        except Exception as e:
            self.logger.error(f"Error loading configuration: {e}")
            self._create_default_config()
            return False
    
    def _validate_config(self, config_data: Dict[str, Any]) -> Tuple[bool, Optional[str]]:
        """
        Validate configuration data against the schema.
        
        Args:
            config_data: Configuration data to validate
            
        Returns:
            Tuple of (is_valid, error_message)
        """
        # Create a temporary AppConfig to validate
        temp_config = AppConfig()
        temp_config.update_from_dict(config_data)
        return temp_config.validate()
    
    def save(self) -> bool:
        """
        Save configuration to disk.
        
        Returns:
            True if configuration was saved successfully, False otherwise
        """
        try:
            # Create config directory if it doesn't exist
            os.makedirs(os.path.dirname(self.config_path), exist_ok=True)
            
            # Save config to file
            with open(self.config_path, 'w') as f:
                json.dump(self.config.to_dict(), f, indent=2)
            
            # Update state
            self.config._modified = False
            self._last_save_time = time.time()
            
            self.logger.info(f"Configuration saved to {self.config_path}")
            return True
            
        except Exception as e:
            self.logger.error(f"Error saving configuration: {e}")
            return False
    
    def auto_save_if_needed(self) -> bool:
        """
        Save configuration if auto-save is enabled and changes have been made.
        
        Returns:
            True if configuration was saved, False otherwise
        """
        if not self.auto_save or not self.config.is_modified():
            return False
            
        # Check if enough time has passed since last save
        current_time = time.time()
        if current_time - self._last_save_time < self._save_interval:
            return False
            
        return self.save()
    
    def _create_default_config(self):
        """Create and save a default configuration."""
        # Config is already initialized with defaults
        self.save()
        # Set the loaded_from path so get_modified_keys works correctly
        self.config._loaded_from = str(self.config_path)
    
    def get_value(self, key: str, default: Any = None) -> Any:
        """
        Get a configuration value.
        
        Args:
            key: The configuration key
            default: Default value to return if key is not found
            
        Returns:
            The configuration value, or default if not found
        """
        return getattr(self.config, key, default)
    
    def set_value(self, key: str, value: Any) -> bool:
        """
        Set a configuration value.
        
        Args:
            key: The configuration key
            value: The value to set
            
        Returns:
            True if value was set successfully, False otherwise
        """
        try:
            old_value = getattr(self.config, key, None)
            setattr(self.config, key, value)
            
            # Notify subscribers if value changed
            if old_value != value:
                self._notify_change(key, old_value, value)
                self.config._modified = True
                
                # Auto-save if enabled
                self.auto_save_if_needed()
            
            return True
            
        except AttributeError:
            self.logger.error(f"Invalid configuration key: {key}")
            return False
    
    def register_change_callback(self, callback: Callable[[str, Any, Any], None]) -> None:
        """
        Register a callback to be notified of configuration changes.
        
        Args:
            callback: Function to call when configuration changes
        """
        if callback not in self.change_callbacks:
            self.change_callbacks.append(callback)
    
    def unregister_change_callback(self, callback: Callable[[str, Any, Any], None]) -> None:
        """
        Unregister a change notification callback.
        
        Args:
            callback: The callback to unregister
        """
        if callback in self.change_callbacks:
            self.change_callbacks.remove(callback)
    
    def _notify_change(self, key: str, old_value: Any, new_value: Any) -> None:
        """
        Notify subscribers of a configuration change.
        
        Args:
            key: The configuration key that changed
            old_value: The previous value
            new_value: The new value
        """
        for callback in self.change_callbacks:
            try:
                callback(key, old_value, new_value)
            except Exception as e:
                self.logger.error(f"Error in configuration change callback: {e}")
    
    def export_config(self, export_path: Path) -> bool:
        """
        Export the current configuration to a file.
        
        Args:
            export_path: Path to export the configuration to
            
        Returns:
            True if the export was successful, False otherwise
        """
        try:
            # Create directory if it doesn't exist
            os.makedirs(os.path.dirname(export_path), exist_ok=True)
            
            # Export config to file
            with open(export_path, 'w') as f:
                json.dump(self.config.to_dict(), f, indent=2)
            
            self.logger.info(f"Configuration exported to {export_path}")
            return True
            
        except Exception as e:
            self.logger.error(f"Error exporting configuration: {e}")
            return False
    
    def import_config(self, import_path: Path) -> bool:
        """
        Import configuration from a file.
        
        Args:
            import_path: Path to import the configuration from
            
        Returns:
            True if the import was successful, False otherwise
        """
        try:
            # Check if file exists
            if not os.path.exists(import_path):
                self.logger.error(f"Import file not found: {import_path}")
                return False
            
            # Load config from file
            with open(import_path, 'r') as f:
                config_data = json.load(f)
            
            # Validate the configuration
            is_valid, error = self._validate_config(config_data)
            if not is_valid:
                self.logger.error(f"Invalid configuration in import file: {error}")
                return False
            
            # Create a backup of the current configuration
            backup_path = f"{self.config_path}.backup"
            self.export_config(backup_path)
            
            # Update config object with imported data
            old_config = self.config.to_dict()
            self.config.update_from_dict(config_data)
            self.config._modified = True
            
            # Save the imported configuration
            if not self.save():
                # Restore from backup if save failed
                with open(backup_path, 'r') as f:
                    backup_data = json.load(f)
                self.config.update_from_dict(backup_data)
                return False
            
            # Notify subscribers of all changed values
            for key, new_value in config_data.items():
                if key in old_config and old_config[key] != new_value:
                    self._notify_change(key, old_config.get(key), new_value)
            
            self.logger.info(f"Configuration imported from {import_path}")
            return True
            
        except Exception as e:
            self.logger.error(f"Error importing configuration: {e}")
            return False
    
    def reset_to_defaults(self) -> bool:
        """
        Reset configuration to default values.
        
        Returns:
            True if the reset was successful, False otherwise
        """
        try:
            # Create a backup of the current configuration
            backup_path = f"{self.config_path}.backup"
            self.export_config(backup_path)
            
            # Reset to defaults
            self.config.reset_to_defaults()
            
            # Save the default configuration
            if not self.save():
                # Restore from backup if save failed
                self.import_config(backup_path)
                return False
            
            self.logger.info("Configuration reset to defaults")
            return True
            
        except Exception as e:
            self.logger.error(f"Error resetting configuration: {e}")
            return False
    
    def get_all_keys(self) -> List[str]:
        """
        Get all configuration keys.
        
        Returns:
            List of configuration keys
        """
        return [key for key in self.config.__dict__ if not key.startswith('_')]
    
    def get_modified_keys(self) -> List[str]:
        """
        Get keys that have been modified since loading.
        
        Returns:
            List of modified keys
        """
        if not hasattr(self.config, '_loaded_from') or not self.config._loaded_from:
            return []
            
        try:
            # Load original config from file
            with open(self.config._loaded_from, 'r') as f:
                original_data = json.load(f)
            
            # Get current config
            current_data = self.config.to_dict()
            
            # Find modified keys
            modified_keys = []
            for key in self.get_all_keys():
                if key in original_data and key in current_data:
                    original_value = original_data[key]
                    current_value = current_data[key]
                    
                    # Convert tuples to lists for comparison (JSON serialization converts tuples to lists)
                    if isinstance(current_value, tuple):
                        current_value = list(current_value)
                    if isinstance(original_value, tuple):
                        original_value = list(original_value)
                    
                    if original_value != current_value:
                        modified_keys.append(key)
            
            return modified_keys
            
        except Exception as e:
            self.logger.error(f"Error getting modified keys: {e}")
            return [] 
   
    # Compatibility methods for legacy code
    def get(self, key: str, default: Any = None) -> Any:
        """
        Get a configuration value (compatibility method).
        
        Args:
            key: Configuration key
            default: Default value if key not found
            
        Returns:
            Configuration value or default
        """
        return self.get_value(key, default)
    
    def set(self, key: str, value: Any) -> bool:
        """
        Set a configuration value (compatibility method).
        
        Args:
            key: Configuration key
            value: Value to set
            
        Returns:
            True if value was set successfully, False otherwise
        """
        return self.set_value(key, value)
    
    def get_all_values(self) -> Dict[str, Any]:
        """
        Get all configuration values as a dictionary.
        
        Returns:
            Dictionary of all configuration values
        """
        try:
            return self.config.to_dict()
        except Exception as e:
            self.logger.error(f"Error getting all values: {e}")
            return {}