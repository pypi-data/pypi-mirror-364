"""
Backend Configuration Management System

This module provides comprehensive configuration management for model backends,
including storage, validation, migration, and runtime switching capabilities.
"""

import json
import logging
import os
import shutil
import time
from pathlib import Path
from typing import Dict, List, Optional, Any, Tuple, Callable, Union
from dataclasses import dataclass, field, asdict
from enum import Enum

from .model_backends import BackendType, BackendConfig, HardwareInfo, HardwareType
from .hardware_detector import HardwareDetector


class ConfigVersion(Enum):
    """Configuration version enumeration."""
    V1_0_0 = "1.0.0"
    V1_1_0 = "1.1.0"
    CURRENT = V1_1_0


@dataclass
class BackendPreferences:
    """User preferences for backend selection and behavior."""
    preferred_backend: Optional[str] = None
    auto_fallback_enabled: bool = True
    gpu_preference: str = "auto"  # "auto", "gpu", "cpu"
    performance_priority: str = "balanced"  # "speed", "memory", "balanced"
    allow_experimental: bool = False
    max_load_time: float = 60.0  # Maximum time to wait for model loading
    retry_failed_backends: bool = True
    notification_level: str = "normal"  # "silent", "normal", "verbose"
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization."""
        return asdict(self)
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'BackendPreferences':
        """Create from dictionary."""
        return cls(**{k: v for k, v in data.items() if k in cls.__annotations__})


@dataclass
class BackendConfigSet:
    """Complete configuration set for all backends."""
    version: str = ConfigVersion.CURRENT.value
    preferences: BackendPreferences = field(default_factory=BackendPreferences)
    backend_configs: Dict[str, BackendConfig] = field(default_factory=dict)
    hardware_overrides: Dict[str, Any] = field(default_factory=dict)
    custom_fallback_order: Optional[List[str]] = None
    last_modified: float = field(default_factory=time.time)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization."""
        return {
            'version': self.version,
            'preferences': self.preferences.to_dict(),
            'backend_configs': {k: v.to_dict() for k, v in self.backend_configs.items()},
            'hardware_overrides': self.hardware_overrides,
            'custom_fallback_order': self.custom_fallback_order,
            'last_modified': self.last_modified
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'BackendConfigSet':
        """Create from dictionary."""
        config_set = cls()
        config_set.version = data.get('version', ConfigVersion.CURRENT.value)
        
        if 'preferences' in data:
            config_set.preferences = BackendPreferences.from_dict(data['preferences'])
        
        if 'backend_configs' in data:
            config_set.backend_configs = {
                k: BackendConfig.from_dict(v) 
                for k, v in data['backend_configs'].items()
            }
        
        config_set.hardware_overrides = data.get('hardware_overrides', {})
        config_set.custom_fallback_order = data.get('custom_fallback_order')
        config_set.last_modified = data.get('last_modified', time.time())
        
        return config_set


class BackendConfigManager:
    """Manages backend configurations, preferences, and migrations."""
    
    def __init__(self, config_path: Path, hardware_detector: Optional[HardwareDetector] = None):
        """
        Initialize the backend configuration manager.
        
        Args:
            config_path: Path to the backend configuration file
            hardware_detector: Hardware detector instance
        """
        self.logger = logging.getLogger("backend.config")
        self.config_path = config_path
        self.hardware_detector = hardware_detector or HardwareDetector()
        
        # Configuration state
        self.config_set = BackendConfigSet()
        self.is_loaded = False
        self.auto_save = True
        self._last_save_time = 0
        self._save_interval = 5  # Minimum seconds between auto-saves
        
        # Change tracking
        self.change_callbacks: List[Callable[[str, Any, Any], None]] = []
        self.validation_callbacks: List[Callable[[BackendConfigSet], Tuple[bool, Optional[str]]]] = []
        
        # Migration handlers
        self.migration_handlers: Dict[str, Callable[[Dict[str, Any]], Dict[str, Any]]] = {
            "1.0.0": self._migrate_from_v1_0_0,
        }
        
        # Initialize with defaults
        self._initialize_default_configs()
    
    def _initialize_default_configs(self):
        """Initialize default configurations for all known backends."""
        try:
            # Get hardware info for optimal defaults
            hw_info = self.hardware_detector.get_hardware_info()
        except Exception as e:
            self.logger.warning(f"Failed to get hardware info, using defaults: {e}")
            hw_info = HardwareInfo()
        
        # Create default configs for each backend type
        for backend_type in BackendType:
            try:
                config = self._create_default_backend_config(backend_type, hw_info)
                self.config_set.backend_configs[backend_type.value] = config
            except Exception as e:
                self.logger.warning(f"Failed to create config for {backend_type.value}: {e}")
                # Create basic config as fallback
                config = BackendConfig(name=backend_type.value)
                self.config_set.backend_configs[backend_type.value] = config
        
        # Set default preferences based on hardware
        try:
            self.config_set.preferences = self._create_default_preferences(hw_info)
        except Exception as e:
            self.logger.warning(f"Failed to create preferences, using defaults: {e}")
            self.config_set.preferences = BackendPreferences()
        
        self.logger.info("Initialized default backend configurations")
    
    def _create_default_backend_config(self, backend_type: BackendType, hw_info: HardwareInfo) -> BackendConfig:
        """Create default configuration for a specific backend."""
        # Base configuration
        config = BackendConfig(name=backend_type.value)
        
        # Hardware-specific optimizations
        if hw_info.gpu_count > 0 and hw_info.total_vram > 4096:  # 4GB+ VRAM
            config.gpu_enabled = True
            config.gpu_layers = -1  # Auto-detect
        elif hw_info.gpu_count > 0:
            config.gpu_enabled = True
            config.gpu_layers = 20  # Conservative layer count for lower VRAM
        else:
            config.gpu_enabled = False
            config.gpu_layers = 0
        
        # Backend-specific optimizations
        if backend_type == BackendType.CTRANSFORMERS:
            config.priority = 1
            config.context_size = 4096
            config.batch_size = 512
        elif backend_type == BackendType.TRANSFORMERS:
            config.priority = 2
            config.context_size = 2048  # More conservative for transformers
            config.batch_size = 256
        elif backend_type == BackendType.LLAMAFILE:
            config.priority = 3
            config.context_size = 4096
            config.batch_size = 512
            config.gpu_enabled = True  # llamafile handles GPU detection automatically
        elif backend_type == BackendType.LLAMA_CPP_PYTHON:
            config.priority = 4  # Lower priority due to installation issues
            config.context_size = 4096
            config.batch_size = 512
        
        # CPU thread optimization
        if hw_info.cpu_cores > 0:
            config.threads = min(hw_info.cpu_cores, 8)  # Cap at 8 threads for stability
        
        return config
    
    def _create_default_preferences(self, hw_info: HardwareInfo) -> BackendPreferences:
        """Create default preferences based on hardware."""
        preferences = BackendPreferences()
        
        # Set GPU preference based on available hardware
        if hw_info.gpu_count > 0:
            preferences.gpu_preference = "auto"
            preferences.performance_priority = "speed"
        else:
            preferences.gpu_preference = "cpu"
            preferences.performance_priority = "memory"
        
        # Set preferred backend based on hardware recommendation
        if hw_info.recommended_backend:
            preferences.preferred_backend = hw_info.recommended_backend
        
        return preferences
    
    def load(self) -> bool:
        """
        Load configuration from disk.
        
        Returns:
            True if configuration was loaded successfully, False otherwise
        """
        try:
            # Create config directory if it doesn't exist
            os.makedirs(os.path.dirname(self.config_path), exist_ok=True)
            
            # Check if config file exists
            if not os.path.exists(self.config_path):
                self.logger.info(f"Backend configuration file not found at {self.config_path}, creating default")
                self._create_default_config_file()
                self.is_loaded = True
                return True
            
            # Load config from file
            with open(self.config_path, 'r') as f:
                config_data = json.load(f)
            
            # Check if we need to migrate the configuration
            current_version = config_data.get('version', '1.0.0')
            if current_version != ConfigVersion.CURRENT.value:
                self.logger.info(f"Migrating backend configuration from version {current_version} to {ConfigVersion.CURRENT.value}")
                
                # Create a backup before migration
                backup_path = f"{self.config_path}.{current_version}.bak"
                shutil.copy2(self.config_path, backup_path)
                self.logger.info(f"Configuration backup created at {backup_path}")
                
                # Migrate the configuration
                config_data = self._migrate_configuration(current_version, config_data)
            
            # Validate the configuration
            is_valid, error = self._validate_config_data(config_data)
            if not is_valid:
                self.logger.warning(f"Invalid backend configuration: {error}")
                self.logger.warning("Using default configuration")
                self._create_default_config_file()
                self.is_loaded = True
                return False
            
            # Update config set with loaded data
            self.config_set = BackendConfigSet.from_dict(config_data)
            
            # Ensure all known backends have configurations
            self._ensure_all_backends_configured()
            
            self.is_loaded = True
            self.logger.info(f"Backend configuration loaded from {self.config_path}")
            return True
            
        except Exception as e:
            self.logger.error(f"Error loading backend configuration: {e}")
            self._create_default_config_file()
            self.is_loaded = True
            return False
    
    def save(self) -> bool:
        """
        Save configuration to disk.
        
        Returns:
            True if configuration was saved successfully, False otherwise
        """
        try:
            # Update last modified timestamp
            self.config_set.last_modified = time.time()
            
            # Create config directory if it doesn't exist
            os.makedirs(os.path.dirname(self.config_path), exist_ok=True)
            
            # Save config to file
            with open(self.config_path, 'w') as f:
                json.dump(self.config_set.to_dict(), f, indent=2)
            
            # Update state
            self._last_save_time = time.time()
            
            self.logger.info(f"Backend configuration saved to {self.config_path}")
            return True
            
        except Exception as e:
            self.logger.error(f"Error saving backend configuration: {e}")
            return False
    
    def auto_save_if_needed(self) -> bool:
        """
        Save configuration if auto-save is enabled and enough time has passed.
        
        Returns:
            True if configuration was saved, False otherwise
        """
        if not self.auto_save:
            return False
            
        # Check if enough time has passed since last save
        current_time = time.time()
        if current_time - self._last_save_time < self._save_interval:
            return False
            
        return self.save()
    
    def _create_default_config_file(self):
        """Create and save a default configuration file."""
        self.save()
    
    def _ensure_all_backends_configured(self):
        """Ensure all known backend types have configurations."""
        hw_info = self.hardware_detector.get_hardware_info()
        
        for backend_type in BackendType:
            if backend_type.value not in self.config_set.backend_configs:
                config = self._create_default_backend_config(backend_type, hw_info)
                self.config_set.backend_configs[backend_type.value] = config
                self.logger.info(f"Added default configuration for {backend_type.value}")
    
    def get_backend_config(self, backend_name: str) -> Optional[BackendConfig]:
        """
        Get configuration for a specific backend.
        
        Args:
            backend_name: Name of the backend
            
        Returns:
            BackendConfig object or None if not found
        """
        return self.config_set.backend_configs.get(backend_name)
    
    def set_backend_config(self, backend_name: str, config: BackendConfig) -> bool:
        """
        Set configuration for a specific backend.
        
        Args:
            backend_name: Name of the backend
            config: Configuration to set
            
        Returns:
            True if successful, False otherwise
        """
        try:
            old_config = self.config_set.backend_configs.get(backend_name)
            self.config_set.backend_configs[backend_name] = config
            
            # Notify change callbacks
            self._notify_change(f"backend_config.{backend_name}", old_config, config)
            
            # Auto-save if enabled
            self.auto_save_if_needed()
            
            return True
            
        except Exception as e:
            self.logger.error(f"Error setting backend configuration: {e}")
            return False
    
    def get_preferences(self) -> BackendPreferences:
        """Get user preferences."""
        return self.config_set.preferences
    
    def set_preferences(self, preferences: BackendPreferences) -> bool:
        """
        Set user preferences.
        
        Args:
            preferences: Preferences to set
            
        Returns:
            True if successful, False otherwise
        """
        try:
            old_preferences = self.config_set.preferences
            self.config_set.preferences = preferences
            
            # Notify change callbacks
            self._notify_change("preferences", old_preferences, preferences)
            
            # Auto-save if enabled
            self.auto_save_if_needed()
            
            return True
            
        except Exception as e:
            self.logger.error(f"Error setting preferences: {e}")
            return False
    
    def get_fallback_order(self) -> List[str]:
        """
        Get the fallback order for backends.
        
        Returns:
            List of backend names in fallback order
        """
        if self.config_set.custom_fallback_order:
            return self.config_set.custom_fallback_order.copy()
        
        # Generate fallback order based on priorities and preferences
        configs = list(self.config_set.backend_configs.values())
        configs.sort(key=lambda c: c.priority)
        
        return [c.name for c in configs if c.enabled]
    
    def set_fallback_order(self, backend_names: List[str]) -> bool:
        """
        Set custom fallback order for backends.
        
        Args:
            backend_names: List of backend names in desired order
            
        Returns:
            True if successful, False otherwise
        """
        try:
            # Validate that all backend names are known
            known_backends = set(self.config_set.backend_configs.keys())
            for name in backend_names:
                if name not in known_backends:
                    self.logger.error(f"Unknown backend in fallback order: {name}")
                    return False
            
            old_order = self.config_set.custom_fallback_order
            self.config_set.custom_fallback_order = backend_names.copy()
            
            # Notify change callbacks
            self._notify_change("fallback_order", old_order, backend_names)
            
            # Auto-save if enabled
            self.auto_save_if_needed()
            
            return True
            
        except Exception as e:
            self.logger.error(f"Error setting fallback order: {e}")
            return False
    
    def reset_fallback_order(self) -> bool:
        """
        Reset fallback order to default (based on priorities).
        
        Returns:
            True if successful, False otherwise
        """
        try:
            old_order = self.config_set.custom_fallback_order
            self.config_set.custom_fallback_order = None
            
            # Notify change callbacks
            self._notify_change("fallback_order", old_order, None)
            
            # Auto-save if enabled
            self.auto_save_if_needed()
            
            return True
            
        except Exception as e:
            self.logger.error(f"Error resetting fallback order: {e}")
            return False
    
    def optimize_for_hardware(self) -> bool:
        """
        Optimize all backend configurations for current hardware.
        
        Returns:
            True if successful, False otherwise
        """
        try:
            self.logger.info("Optimizing backend configurations for current hardware")
            
            # Get current hardware info
            hw_info = self.hardware_detector.get_hardware_info()
            
            # Update each backend configuration
            for backend_name, config in self.config_set.backend_configs.items():
                old_config = BackendConfig.from_dict(config.to_dict())  # Deep copy
                
                # Apply hardware-specific optimizations
                if hw_info.gpu_count > 0 and hw_info.total_vram > 4096:
                    config.gpu_enabled = True
                    config.gpu_layers = -1  # Auto-detect
                elif hw_info.gpu_count > 0:
                    config.gpu_enabled = True
                    config.gpu_layers = min(20, config.gpu_layers) if config.gpu_layers > 0 else 20
                else:
                    config.gpu_enabled = False
                    config.gpu_layers = 0
                
                # Optimize thread count
                if hw_info.cpu_cores > 0:
                    config.threads = min(hw_info.cpu_cores, 8)
                
                # Optimize context size based on available memory
                if hw_info.total_ram > 16384:  # 16GB+ RAM
                    config.context_size = min(config.context_size, 8192)
                elif hw_info.total_ram > 8192:  # 8GB+ RAM
                    config.context_size = min(config.context_size, 4096)
                else:  # Less than 8GB RAM
                    config.context_size = min(config.context_size, 2048)
                
                # Notify if configuration changed
                if config.to_dict() != old_config.to_dict():
                    self._notify_change(f"backend_config.{backend_name}", old_config, config)
            
            # Update preferences based on hardware
            old_preferences = BackendPreferences.from_dict(self.config_set.preferences.to_dict())
            
            if hw_info.gpu_count > 0:
                self.config_set.preferences.gpu_preference = "auto"
                self.config_set.preferences.performance_priority = "speed"
            else:
                self.config_set.preferences.gpu_preference = "cpu"
                self.config_set.preferences.performance_priority = "memory"
            
            if hw_info.recommended_backend:
                self.config_set.preferences.preferred_backend = hw_info.recommended_backend
            
            # Notify if preferences changed
            if self.config_set.preferences.to_dict() != old_preferences.to_dict():
                self._notify_change("preferences", old_preferences, self.config_set.preferences)
            
            # Auto-save if enabled
            self.auto_save_if_needed()
            
            self.logger.info("Hardware optimization completed")
            return True
            
        except Exception as e:
            self.logger.error(f"Error optimizing for hardware: {e}")
            return False
    
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
                json.dump(self.config_set.to_dict(), f, indent=2)
            
            self.logger.info(f"Backend configuration exported to {export_path}")
            return True
            
        except Exception as e:
            self.logger.error(f"Error exporting backend configuration: {e}")
            return False
    
    def import_config(self, import_path: Path, merge: bool = False) -> bool:
        """
        Import configuration from a file.
        
        Args:
            import_path: Path to import the configuration from
            merge: If True, merge with existing config; if False, replace entirely
            
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
                import_data = json.load(f)
            
            # Validate the configuration
            is_valid, error = self._validate_config_data(import_data)
            if not is_valid:
                self.logger.error(f"Invalid configuration in import file: {error}")
                return False
            
            # Create a backup of the current configuration
            backup_path = f"{self.config_path}.backup"
            self.export_config(backup_path)
            
            # Import the configuration
            old_config_set = BackendConfigSet.from_dict(self.config_set.to_dict())  # Deep copy
            imported_config_set = BackendConfigSet.from_dict(import_data)
            
            if merge:
                # Merge configurations
                self._merge_config_sets(imported_config_set)
            else:
                # Replace entirely
                self.config_set = imported_config_set
            
            # Ensure all backends are configured
            self._ensure_all_backends_configured()
            
            # Save the imported configuration
            if not self.save():
                # Restore from backup if save failed
                self.config_set = old_config_set
                return False
            
            # Notify about the change
            self._notify_change("config_set", old_config_set, self.config_set)
            
            self.logger.info(f"Backend configuration imported from {import_path}")
            return True
            
        except Exception as e:
            self.logger.error(f"Error importing backend configuration: {e}")
            return False
    
    def _merge_config_sets(self, imported_config: BackendConfigSet):
        """Merge imported configuration with current configuration."""
        # Merge backend configurations
        for backend_name, config in imported_config.backend_configs.items():
            self.config_set.backend_configs[backend_name] = config
        
        # Update preferences (imported takes precedence)
        self.config_set.preferences = imported_config.preferences
        
        # Update hardware overrides
        self.config_set.hardware_overrides.update(imported_config.hardware_overrides)
        
        # Update fallback order if specified
        if imported_config.custom_fallback_order:
            self.config_set.custom_fallback_order = imported_config.custom_fallback_order
    
    def reset_to_defaults(self) -> bool:
        """
        Reset all configurations to defaults.
        
        Returns:
            True if the reset was successful, False otherwise
        """
        try:
            # Create a backup of the current configuration
            backup_path = f"{self.config_path}.backup"
            self.export_config(backup_path)
            
            # Store old config for change notification
            old_config_set = BackendConfigSet.from_dict(self.config_set.to_dict())
            
            # Reset to defaults
            self._initialize_default_configs()
            
            # Save the default configuration
            if not self.save():
                # Restore from backup if save failed
                self.config_set = old_config_set
                return False
            
            # Notify about the change
            self._notify_change("config_set", old_config_set, self.config_set)
            
            self.logger.info("Backend configuration reset to defaults")
            return True
            
        except Exception as e:
            self.logger.error(f"Error resetting backend configuration: {e}")
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
    
    def _validate_config_data(self, config_data: Dict[str, Any]) -> Tuple[bool, Optional[str]]:
        """
        Validate configuration data.
        
        Args:
            config_data: Configuration data to validate
            
        Returns:
            Tuple of (is_valid, error_message)
        """
        try:
            # Basic structure validation
            if not isinstance(config_data, dict):
                return False, "Configuration must be a dictionary"
            
            # Version validation
            if 'version' not in config_data:
                return False, "Configuration version is required"
            
            # Try to create config set from data
            config_set = BackendConfigSet.from_dict(config_data)
            
            # Run custom validation callbacks
            for validator in self.validation_callbacks:
                is_valid, error = validator(config_set)
                if not is_valid:
                    return False, error
            
            return True, None
            
        except Exception as e:
            return False, f"Configuration validation error: {e}"
    
    def get_config_summary(self) -> Dict[str, Any]:
        """
        Get a summary of the current configuration.
        
        Returns:
            Dictionary with configuration summary
        """
        enabled_backends = [
            name for name, config in self.config_set.backend_configs.items()
            if config.enabled
        ]
        
        gpu_enabled_backends = [
            name for name, config in self.config_set.backend_configs.items()
            if config.gpu_enabled
        ]
        
        return {
            'version': self.config_set.version,
            'backend_count': len(self.config_set.backend_configs),
            'enabled_backends': enabled_backends,
            'gpu_enabled_backends': gpu_enabled_backends,
            'preferred_backend': self.config_set.preferences.preferred_backend,
            'gpu_preference': self.config_set.preferences.gpu_preference,
            'performance_priority': self.config_set.preferences.performance_priority,
            'fallback_order': self.get_fallback_order(),
            'last_modified': self.config_set.last_modified
        }
    
    def _migrate_configuration(self, from_version: str, config_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Migrate configuration from an older version.
        
        Args:
            from_version: The version to migrate from
            config_data: The configuration data to migrate
            
        Returns:
            Migrated configuration data
        """
        current_data = config_data.copy()
        
        # Apply migration handlers in sequence
        for version, handler in self.migration_handlers.items():
            if version == from_version:
                current_data = handler(current_data)
                break
        
        # Update version to current
        current_data['version'] = ConfigVersion.CURRENT.value
        
        return current_data
    
    def _migrate_from_v1_0_0(self, config_data: Dict[str, Any]) -> Dict[str, Any]:
        """Migrate configuration from version 1.0.0."""
        migrated = config_data.copy()
        
        # Add new fields introduced in v1.1.0
        if 'preferences' not in migrated:
            migrated['preferences'] = BackendPreferences().to_dict()
        
        if 'hardware_overrides' not in migrated:
            migrated['hardware_overrides'] = {}
        
        # Migrate old backend configs if they exist in a different format
        if 'backends' in migrated and 'backend_configs' not in migrated:
            migrated['backend_configs'] = migrated.pop('backends')
        
        # Ensure all backend configs have the new fields
        for backend_name, config in migrated.get('backend_configs', {}).items():
            if 'custom_args' not in config:
                config['custom_args'] = {}
            if 'threads' not in config:
                config['threads'] = -1
        
        self.logger.info("Migrated configuration from v1.0.0 to v1.1.0")
        return migrated
    
    def get_config_summary(self) -> Dict[str, Any]:
        """Get a summary of the current configuration."""
        return {
            'version': self.config_set.version,
            'backend_count': len(self.config_set.backend_configs),
            'enabled_backends': [
                name for name, config in self.config_set.backend_configs.items() 
                if config.enabled
            ],
            'preferred_backend': self.config_set.preferences.preferred_backend,
            'gpu_preference': self.config_set.preferences.gpu_preference,
            'auto_fallback': self.config_set.preferences.auto_fallback_enabled,
            'custom_fallback_order': self.config_set.custom_fallback_order is not None,
            'last_modified': self.config_set.last_modified,
            'is_loaded': self.is_loaded
        }