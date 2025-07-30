"""
Runtime Configuration Switching System

This module provides runtime switching capabilities for backend configurations,
allowing users to change backend settings and preferences without restarting
the application.
"""

import logging
import time
from typing import Dict, List, Optional, Any, Callable, Tuple
from dataclasses import dataclass
from enum import Enum

from .backend_config_manager import BackendConfigManager, BackendPreferences
from .model_backends import BackendConfig, BackendType
from .backend_manager import BackendManager


class SwitchingMode(Enum):
    """Modes for configuration switching."""
    IMMEDIATE = "immediate"  # Apply changes immediately
    ON_NEXT_LOAD = "on_next_load"  # Apply changes on next model load
    MANUAL = "manual"  # Require manual application


@dataclass
class ConfigChange:
    """Represents a configuration change."""
    change_type: str  # "backend_config", "preferences", "fallback_order"
    target: str  # Backend name or "global"
    old_value: Any
    new_value: Any
    timestamp: float
    applied: bool = False
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization."""
        return {
            'change_type': self.change_type,
            'target': self.target,
            'old_value': self.old_value,
            'new_value': self.new_value,
            'timestamp': self.timestamp,
            'applied': self.applied
        }


class RuntimeConfigSwitcher:
    """Manages runtime configuration switching for backends."""
    
    def __init__(self, config_manager: BackendConfigManager, backend_manager: BackendManager):
        """
        Initialize the runtime configuration switcher.
        
        Args:
            config_manager: Backend configuration manager
            backend_manager: Backend manager instance
        """
        self.logger = logging.getLogger("backend.runtime_switcher")
        self.config_manager = config_manager
        self.backend_manager = backend_manager
        
        # Switching state
        self.switching_mode = SwitchingMode.IMMEDIATE
        self.pending_changes: List[ConfigChange] = []
        self.change_history: List[ConfigChange] = []
        self.max_history_size = 100
        
        # Callbacks
        self.on_config_changed: Optional[Callable[[ConfigChange], None]] = None
        self.on_switch_completed: Optional[Callable[[List[ConfigChange]], None]] = None
        self.on_switch_failed: Optional[Callable[[List[ConfigChange], str], None]] = None
        
        # Register for configuration changes
        self.config_manager.register_change_callback(self._on_config_manager_change)
        
        # State tracking
        self.is_switching = False
        self.last_switch_time = 0.0
    
    def set_switching_mode(self, mode: SwitchingMode) -> bool:
        """
        Set the configuration switching mode.
        
        Args:
            mode: Switching mode to use
            
        Returns:
            True if successful, False otherwise
        """
        try:
            old_mode = self.switching_mode
            self.switching_mode = mode
            
            self.logger.info(f"Switching mode changed from {old_mode.value} to {mode.value}")
            
            # If switching to immediate mode, apply any pending changes
            if mode == SwitchingMode.IMMEDIATE and self.pending_changes:
                self.apply_pending_changes()
            
            return True
            
        except Exception as e:
            self.logger.error(f"Error setting switching mode: {e}")
            return False
    
    def switch_backend_config(self, backend_name: str, new_config: BackendConfig, 
                            apply_immediately: Optional[bool] = None) -> bool:
        """
        Switch configuration for a specific backend.
        
        Args:
            backend_name: Name of the backend to configure
            new_config: New configuration to apply
            apply_immediately: Override switching mode for this change
            
        Returns:
            True if successful, False otherwise
        """
        try:
            # Get current configuration
            old_config = self.config_manager.get_backend_config(backend_name)
            
            # Create change record
            change = ConfigChange(
                change_type="backend_config",
                target=backend_name,
                old_value=old_config.to_dict() if old_config else None,
                new_value=new_config.to_dict(),
                timestamp=time.time()
            )
            
            # Determine if we should apply immediately
            should_apply = (
                apply_immediately if apply_immediately is not None 
                else self.switching_mode == SwitchingMode.IMMEDIATE
            )
            
            if should_apply:
                return self._apply_backend_config_change(change)
            else:
                # Add to pending changes
                self.pending_changes.append(change)
                self.logger.info(f"Backend config change for {backend_name} added to pending changes")
                return True
                
        except Exception as e:
            self.logger.error(f"Error switching backend config: {e}")
            return False
    
    def switch_preferences(self, new_preferences: BackendPreferences, 
                          apply_immediately: Optional[bool] = None) -> bool:
        """
        Switch user preferences.
        
        Args:
            new_preferences: New preferences to apply
            apply_immediately: Override switching mode for this change
            
        Returns:
            True if successful, False otherwise
        """
        try:
            # Get current preferences
            old_preferences = self.config_manager.get_preferences()
            
            # Create change record
            change = ConfigChange(
                change_type="preferences",
                target="global",
                old_value=old_preferences.to_dict(),
                new_value=new_preferences.to_dict(),
                timestamp=time.time()
            )
            
            # Determine if we should apply immediately
            should_apply = (
                apply_immediately if apply_immediately is not None 
                else self.switching_mode == SwitchingMode.IMMEDIATE
            )
            
            if should_apply:
                return self._apply_preferences_change(change)
            else:
                # Add to pending changes
                self.pending_changes.append(change)
                self.logger.info("Preferences change added to pending changes")
                return True
                
        except Exception as e:
            self.logger.error(f"Error switching preferences: {e}")
            return False
    
    def switch_fallback_order(self, new_order: List[str], 
                            apply_immediately: Optional[bool] = None) -> bool:
        """
        Switch fallback order for backends.
        
        Args:
            new_order: New fallback order to apply
            apply_immediately: Override switching mode for this change
            
        Returns:
            True if successful, False otherwise
        """
        try:
            # Get current fallback order
            old_order = self.config_manager.get_fallback_order()
            
            # Create change record
            change = ConfigChange(
                change_type="fallback_order",
                target="global",
                old_value=old_order,
                new_value=new_order,
                timestamp=time.time()
            )
            
            # Determine if we should apply immediately
            should_apply = (
                apply_immediately if apply_immediately is not None 
                else self.switching_mode == SwitchingMode.IMMEDIATE
            )
            
            if should_apply:
                return self._apply_fallback_order_change(change)
            else:
                # Add to pending changes
                self.pending_changes.append(change)
                self.logger.info("Fallback order change added to pending changes")
                return True
                
        except Exception as e:
            self.logger.error(f"Error switching fallback order: {e}")
            return False
    
    def apply_pending_changes(self) -> bool:
        """
        Apply all pending configuration changes.
        
        Returns:
            True if all changes were applied successfully, False otherwise
        """
        if not self.pending_changes:
            self.logger.info("No pending changes to apply")
            return True
        
        self.logger.info(f"Applying {len(self.pending_changes)} pending configuration changes")
        
        try:
            self.is_switching = True
            applied_changes = []
            failed_changes = []
            
            # Apply changes in chronological order
            self.pending_changes.sort(key=lambda c: c.timestamp)
            
            for change in self.pending_changes:
                try:
                    success = self._apply_change(change)
                    if success:
                        change.applied = True
                        applied_changes.append(change)
                        self.logger.info(f"Applied {change.change_type} change for {change.target}")
                    else:
                        failed_changes.append(change)
                        self.logger.error(f"Failed to apply {change.change_type} change for {change.target}")
                        
                except Exception as e:
                    failed_changes.append(change)
                    self.logger.error(f"Error applying change: {e}")
            
            # Update history and clear pending changes
            self.change_history.extend(applied_changes)
            self._trim_history()
            
            # Clear successfully applied changes from pending
            self.pending_changes = failed_changes
            
            # Update switch time
            self.last_switch_time = time.time()
            
            # Notify callbacks
            if applied_changes and self.on_switch_completed:
                self.on_switch_completed(applied_changes)
            
            if failed_changes and self.on_switch_failed:
                error_msg = f"Failed to apply {len(failed_changes)} changes"
                self.on_switch_failed(failed_changes, error_msg)
            
            success = len(failed_changes) == 0
            self.logger.info(f"Configuration switching completed. Success: {success}")
            
            return success
            
        except Exception as e:
            self.logger.error(f"Error applying pending changes: {e}")
            return False
        finally:
            self.is_switching = False
    
    def _apply_change(self, change: ConfigChange) -> bool:
        """Apply a single configuration change."""
        if change.change_type == "backend_config":
            return self._apply_backend_config_change(change)
        elif change.change_type == "preferences":
            return self._apply_preferences_change(change)
        elif change.change_type == "fallback_order":
            return self._apply_fallback_order_change(change)
        else:
            self.logger.error(f"Unknown change type: {change.change_type}")
            return False
    
    def _apply_backend_config_change(self, change: ConfigChange) -> bool:
        """Apply a backend configuration change."""
        try:
            backend_name = change.target
            new_config = BackendConfig.from_dict(change.new_value)
            
            # Update configuration manager
            success = self.config_manager.set_backend_config(backend_name, new_config)
            if not success:
                return False
            
            # Update backend manager configuration
            if backend_name in self.backend_manager.configs:
                self.backend_manager.configs[backend_name] = new_config
                
                # If this backend is currently active, we may need to reload
                if (self.backend_manager.current_backend and 
                    self.backend_manager.current_backend.config.name == backend_name):
                    
                    # Check if the change requires a reload
                    if self._requires_model_reload(change.old_value, change.new_value):
                        self.logger.info(f"Backend config change requires model reload for {backend_name}")
                        # Note: We don't automatically reload here to avoid disrupting the user
                        # The UI should handle this based on user preference
            
            return True
            
        except Exception as e:
            self.logger.error(f"Error applying backend config change: {e}")
            return False
    
    def _apply_preferences_change(self, change: ConfigChange) -> bool:
        """Apply a preferences change."""
        try:
            new_preferences = BackendPreferences.from_dict(change.new_value)
            
            # Update configuration manager
            success = self.config_manager.set_preferences(new_preferences)
            if not success:
                return False
            
            # Update backend manager fallback order if preferred backend changed
            old_prefs = BackendPreferences.from_dict(change.old_value)
            if old_prefs.preferred_backend != new_preferences.preferred_backend:
                self._update_backend_manager_fallback_order()
            
            return True
            
        except Exception as e:
            self.logger.error(f"Error applying preferences change: {e}")
            return False
    
    def _apply_fallback_order_change(self, change: ConfigChange) -> bool:
        """Apply a fallback order change."""
        try:
            new_order = change.new_value
            
            # Update configuration manager
            success = self.config_manager.set_fallback_order(new_order)
            if not success:
                return False
            
            # Update backend manager fallback order
            self.backend_manager.fallback_order = new_order
            
            return True
            
        except Exception as e:
            self.logger.error(f"Error applying fallback order change: {e}")
            return False
    
    def _requires_model_reload(self, old_config: Dict[str, Any], new_config: Dict[str, Any]) -> bool:
        """Check if a configuration change requires reloading the model."""
        # Changes that require model reload
        reload_keys = {
            'gpu_enabled', 'gpu_layers', 'context_size', 'batch_size', 'threads'
        }
        
        for key in reload_keys:
            if old_config.get(key) != new_config.get(key):
                return True
        
        return False
    
    def _update_backend_manager_fallback_order(self):
        """Update the backend manager's fallback order based on current configuration."""
        fallback_order = self.config_manager.get_fallback_order()
        self.backend_manager.fallback_order = fallback_order
    
    def revert_change(self, change_index: int) -> bool:
        """
        Revert a specific change from the history.
        
        Args:
            change_index: Index of the change to revert (from change_history)
            
        Returns:
            True if successful, False otherwise
        """
        try:
            if change_index < 0 or change_index >= len(self.change_history):
                self.logger.error(f"Invalid change index: {change_index}")
                return False
            
            change = self.change_history[change_index]
            
            # Create reverse change
            reverse_change = ConfigChange(
                change_type=change.change_type,
                target=change.target,
                old_value=change.new_value,
                new_value=change.old_value,
                timestamp=time.time()
            )
            
            # Apply the reverse change
            success = self._apply_change(reverse_change)
            if success:
                reverse_change.applied = True
                self.change_history.append(reverse_change)
                self._trim_history()
                self.logger.info(f"Reverted {change.change_type} change for {change.target}")
            
            return success
            
        except Exception as e:
            self.logger.error(f"Error reverting change: {e}")
            return False
    
    def clear_pending_changes(self) -> bool:
        """
        Clear all pending changes without applying them.
        
        Returns:
            True if successful, False otherwise
        """
        try:
            count = len(self.pending_changes)
            self.pending_changes.clear()
            self.logger.info(f"Cleared {count} pending changes")
            return True
            
        except Exception as e:
            self.logger.error(f"Error clearing pending changes: {e}")
            return False
    
    def get_pending_changes(self) -> List[ConfigChange]:
        """Get list of pending changes."""
        return self.pending_changes.copy()
    
    def get_change_history(self) -> List[ConfigChange]:
        """Get list of applied changes."""
        return self.change_history.copy()
    
    def _on_config_manager_change(self, key: str, old_value: Any, new_value: Any):
        """Handle configuration manager changes."""
        # Create change record for history tracking
        change = ConfigChange(
            change_type="external",
            target=key,
            old_value=old_value,
            new_value=new_value,
            timestamp=time.time(),
            applied=True
        )
        
        self.change_history.append(change)
        self._trim_history()
        
        # Notify callback
        if self.on_config_changed:
            self.on_config_changed(change)
    
    def _trim_history(self):
        """Trim change history to maximum size."""
        if len(self.change_history) > self.max_history_size:
            # Keep the most recent changes
            self.change_history = self.change_history[-self.max_history_size:]
    
    def get_status(self) -> Dict[str, Any]:
        """Get current status of the runtime switcher."""
        return {
            'switching_mode': self.switching_mode.value,
            'is_switching': self.is_switching,
            'pending_changes_count': len(self.pending_changes),
            'history_count': len(self.change_history),
            'last_switch_time': self.last_switch_time,
            'pending_changes': [change.to_dict() for change in self.pending_changes],
            'recent_history': [
                change.to_dict() for change in self.change_history[-10:]
            ]
        }
    
    def create_configuration_preset(self, name: str, description: str = "") -> bool:
        """
        Create a configuration preset from current settings.
        
        Args:
            name: Name of the preset
            description: Optional description
            
        Returns:
            True if successful, False otherwise
        """
        try:
            # Get current configuration
            current_config = self.config_manager.config_set.to_dict()
            
            # Add preset metadata
            preset_data = {
                'name': name,
                'description': description,
                'created_at': time.time(),
                'configuration': current_config
            }
            
            # Save preset (this would typically go to a presets file)
            preset_path = self.config_manager.config_path.parent / f"preset_{name}.json"
            
            import json
            with open(preset_path, 'w') as f:
                json.dump(preset_data, f, indent=2)
            
            self.logger.info(f"Configuration preset '{name}' created at {preset_path}")
            return True
            
        except Exception as e:
            self.logger.error(f"Error creating configuration preset: {e}")
            return False
    
    def load_configuration_preset(self, name: str, apply_immediately: bool = True) -> bool:
        """
        Load a configuration preset.
        
        Args:
            name: Name of the preset to load
            apply_immediately: Whether to apply the preset immediately
            
        Returns:
            True if successful, False otherwise
        """
        try:
            preset_path = self.config_manager.config_path.parent / f"preset_{name}.json"
            
            if not preset_path.exists():
                self.logger.error(f"Preset not found: {name}")
                return False
            
            # Load preset data
            import json
            with open(preset_path, 'r') as f:
                preset_data = json.load(f)
            
            # Extract configuration
            config_data = preset_data['configuration']
            
            if apply_immediately:
                # Apply configuration directly by updating the config manager
                from .backend_config_manager import BackendConfigSet
                preset_config = BackendConfigSet.from_dict(config_data)
                
                # Update backend configurations
                for backend_name, config in preset_config.backend_configs.items():
                    self.config_manager.set_backend_config(backend_name, config)
                
                # Update preferences
                self.config_manager.set_preferences(preset_config.preferences)
                
                # Update fallback order if specified
                if preset_config.custom_fallback_order:
                    self.config_manager.set_fallback_order(preset_config.custom_fallback_order)
                
                self.logger.info(f"Preset '{name}' applied immediately")
                return True
            else:
                # Create pending changes for each configuration item
                from .backend_config_manager import BackendConfigSet
                preset_config = BackendConfigSet.from_dict(config_data)
                
                # Add backend config changes
                for backend_name, config in preset_config.backend_configs.items():
                    self.switch_backend_config(backend_name, config, apply_immediately=False)
                
                # Add preferences change
                self.switch_preferences(preset_config.preferences, apply_immediately=False)
                
                # Add fallback order change if specified
                if preset_config.custom_fallback_order:
                    self.switch_fallback_order(preset_config.custom_fallback_order, apply_immediately=False)
                
                self.logger.info(f"Preset '{name}' loaded as pending changes")
                return True
            
        except Exception as e:
            self.logger.error(f"Error loading configuration preset: {e}")
            return False