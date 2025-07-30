"""
Model Manager

This module contains the ModelManager class, which is responsible for
maintaining a registry of loaded models, providing model switching functionality,
and implementing memory management features.
"""

import os
import logging
import psutil
from pathlib import Path
from typing import Dict, List, Optional, Tuple, Set, Any, Union
from datetime import datetime, timedelta

from PySide6.QtCore import QObject, Signal, QTimer

from llmtoolkit.app.models.gguf_model import GGUFModel
from llmtoolkit.app.core.model_loader import ModelLoader


class ModelManager(QObject):
    """
    Manages GGUF models in the application.
    
    This class is responsible for:
    - Maintaining a registry of loaded models
    - Providing model switching functionality
    - Implementing memory management features
    """
    
    # Signals
    model_added_signal = Signal(str)  # model_id
    model_removed_signal = Signal(str)  # model_id
    model_switched_signal = Signal(str)  # model_id
    memory_warning_signal = Signal(float, float)  # used_percentage, available_mb
    model_loading_progress_signal = Signal(str, int)  # file_path, progress_percentage
    
    def __init__(self, event_bus=None, config_manager=None, parent=None):
        """
        Initialize the ModelManager.
        
        Args:
            event_bus: Optional event bus for publishing events
            config_manager: Optional configuration manager
            parent: Parent QObject
        """
        super().__init__(parent)
        self.logger = logging.getLogger("gguf_loader.model_manager")
        self.event_bus = event_bus
        self.config_manager = config_manager
        
        # Initialize model registry
        self.models: Dict[str, GGUFModel] = {}
        self.current_model_id: Optional[str] = None
        
        # Create model loader
        self.model_loader = ModelLoader(event_bus=event_bus, parent=self)
        
        # Connect signals
        self.model_loader.model_loaded_signal.connect(self._on_model_loaded)
        self.model_loader.error_signal.connect(self._on_model_loading_error)
        self.model_loader.progress_signal.connect(self._on_loading_progress)
        
        # Memory management settings
        self.max_memory_usage = 0  # 0 means no limit
        self.unload_inactive = True
        self.inactive_timeout = timedelta(minutes=30)
        
        # Memory monitoring timer
        self.memory_timer = QTimer()
        self.memory_timer.timeout.connect(self._check_memory_usage)
        self.memory_timer.start(30000)  # Check every 30 seconds
        
        # Loading strategies for different file sizes
        self._loading_strategies = {}
        
        # Load settings from configuration
        self._load_settings()
        
        self.logger.info("ModelManager initialized")
    
    def _load_settings(self):
        """Load settings from configuration."""
        if self.config_manager:
            self.max_memory_usage = self.config_manager.get_value("max_memory_usage", 0)
            self.unload_inactive = self.config_manager.get_value("unload_inactive", True)
            inactive_minutes = self.config_manager.get_value("inactive_timeout_minutes", 30)
            self.inactive_timeout = timedelta(minutes=inactive_minutes)
    
    def set_loading_strategy(self, file_path: str, load_type: str, use_compression: bool = False):
        """
        Store the recommended loading strategy for a model file.
        
        Args:
            file_path: Path to the model file
            load_type: Type of loading to use (full, memory_mapped, lazy)
            use_compression: Whether to use compression
        """
        self._loading_strategies[file_path] = {
            "load_type": load_type,
            "use_compression": use_compression
        }
    
    def load_model(self, file_path: str) -> None:
        """
        Load a model asynchronously.
        
        Args:
            file_path: Path to the model file
        """
        self.logger.info(f"Loading model: {file_path}")
        
        # Check if model is already loaded
        for model in self.models.values():
            if model.file_path == file_path:
                self.logger.info(f"Model already loaded: {file_path}")
                self.switch_model(model.id)
                return
        
        # Check if model is already being loaded
        if self.model_loader.is_loading(file_path):
            self.logger.info(f"Model already being loaded: {file_path}")
            return
        
        # Check memory usage before loading
        if not self._check_memory_before_load(file_path):
            return
        
        # Get loading strategy if available
        load_type = None
        use_compression = False
        hardware_settings = {}
        
        if file_path in self._loading_strategies:
            strategy = self._loading_strategies[file_path]
            load_type = strategy.get("load_type")
            use_compression = strategy.get("use_compression", False)
            
            self.logger.info(f"Using loading strategy: {load_type}")
        
        # Load the model
        self.model_loader.load_model(file_path, load_type, use_compression)
    
    def load_model_sync(self, file_path: str) -> Optional[str]:
        """
        Load a model synchronously.
        
        Args:
            file_path: Path to the model file
            
        Returns:
            Model ID if successful, None otherwise
        """
        self.logger.info(f"Loading model synchronously: {file_path}")
        
        # Check if model is already loaded
        for model in self.models.values():
            if model.file_path == file_path:
                self.logger.info(f"Model already loaded: {file_path}")
                self.switch_model(model.id)
                return model.id
        
        # Check memory usage before loading
        if not self._check_memory_before_load(file_path):
            return None
        
        # Get loading strategy if available
        load_type = None
        use_compression = False
        hardware_settings = {}
        
        if file_path in self._loading_strategies:
            strategy = self._loading_strategies[file_path]
            load_type = strategy.get("load_type")
            use_compression = strategy.get("use_compression", False)
            
            self.logger.info(f"Using loading strategy: {load_type}")
        
        # Load the model using the synchronous method
        model, error = self.model_loader.load_model_sync(file_path, load_type, use_compression, hardware_settings)
        
        if model:
            # Add the model to the registry
            self._add_model(model)
            return model.id
        else:
            # Handle error
            self.logger.error(f"Error loading model: {error}")
            if self.event_bus:
                self.event_bus.publish("model.error", error, file_path)
            return None
    
    def cancel_model_loading(self, file_path: str) -> bool:
        """
        Cancel loading a model.
        
        Args:
            file_path: Path to the model file
            
        Returns:
            True if loading was cancelled, False otherwise
        """
        return self.model_loader.cancel_loading(file_path)
    
    def unload_model(self, model_id: str) -> bool:
        """
        Unload a model.
        
        Args:
            model_id: ID of the model to unload
            
        Returns:
            True if the model was unloaded successfully, False otherwise
        """
        if model_id not in self.models:
            self.logger.warning(f"Model not found: {model_id}")
            return False
        
        model = self.models[model_id]
        self.logger.info(f"Unloading model: {model.name}")
        
        # Unload the model
        if not model.unload():
            self.logger.error(f"Error unloading model: {model.name}")
            return False
        
        # Remove from registry
        del self.models[model_id]
        
        # Update current model if needed
        if self.current_model_id == model_id:
            self.current_model_id = None
            
            # Switch to another model if available
            if self.models:
                next_model_id = next(iter(self.models.keys()))
                self.switch_model(next_model_id)
        
        # Emit signal
        self.model_removed_signal.emit(model_id)
        
        # Publish event
        if self.event_bus:
            self.event_bus.publish("model.unloaded", model_id)
        
        return True
    
    def switch_model(self, model_id: str) -> bool:
        """
        Switch to a different model.
        
        Args:
            model_id: ID of the model to switch to
            
        Returns:
            True if the switch was successful, False otherwise
        """
        if model_id not in self.models:
            self.logger.error(f"Model not found: {model_id}")
            return False
        
        if self.current_model_id == model_id:
            self.logger.info(f"Already using model: {model_id}")
            return True
        
        model = self.models[model_id]
        self.logger.info(f"Switching to model: {model.name}")
        
        # Update current model
        old_model_id = self.current_model_id
        self.current_model_id = model_id
        
        # Update last accessed time
        model.access()
        
        # Emit signal
        self.model_switched_signal.emit(model_id)
        
        # Publish event
        if self.event_bus:
            self.event_bus.publish("model.switched", model_id, old_model_id)
        
        return True
    
    def get_model(self, model_id: str) -> Optional[GGUFModel]:
        """
        Get a model by ID.
        
        Args:
            model_id: ID of the model
            
        Returns:
            The model if found, None otherwise
        """
        return self.models.get(model_id)
    
    def get_current_model(self) -> Optional[GGUFModel]:
        """
        Get the currently selected model.
        
        Returns:
            The current model, or None if no model is selected
        """
        if self.current_model_id:
            return self.models.get(self.current_model_id)
        return None
    
    def get_models(self) -> Dict[str, GGUFModel]:
        """
        Get all loaded models.
        
        Returns:
            Dictionary of model_id -> GGUFModel
        """
        return self.models.copy()
    
    def get_model_count(self) -> int:
        """
        Get the number of loaded models.
        
        Returns:
            Number of loaded models
        """
        return len(self.models)
    
    def get_total_memory_usage(self) -> int:
        """
        Get the total memory usage of all loaded models.
        
        Returns:
            Total memory usage in bytes
        """
        return sum(model.memory_usage for model in self.models.values())
    
    def unload_all_models(self) -> bool:
        """
        Unload all models.
        
        Returns:
            True if all models were unloaded successfully, False otherwise
        """
        success = True
        
        # Make a copy of the keys to avoid modifying the dictionary during iteration
        model_ids = list(self.models.keys())
        
        for model_id in model_ids:
            if not self.unload_model(model_id):
                success = False
        
        return success
    
    def unload_inactive_models(self) -> int:
        """
        Unload models that haven't been accessed recently.
        
        Returns:
            Number of models unloaded
        """
        if not self.unload_inactive:
            return 0
        
        count = 0
        now = datetime.now()
        
        # Make a copy of the keys to avoid modifying the dictionary during iteration
        model_ids = list(self.models.keys())
        
        for model_id in model_ids:
            # Skip the current model
            if model_id == self.current_model_id:
                continue
            
            model = self.models[model_id]
            
            # Check if the model has been accessed recently
            if model.last_accessed and (now - model.last_accessed) > self.inactive_timeout:
                self.logger.info(f"Unloading inactive model: {model.name}")
                if self.unload_model(model_id):
                    count += 1
        
        return count
    
    def get_loading_models(self) -> List[str]:
        """
        Get a list of models that are currently being loaded.
        
        Returns:
            List of file paths
        """
        return self.model_loader.get_active_loaders()
    
    def is_loading_model(self, file_path: str) -> bool:
        """
        Check if a model is currently being loaded.
        
        Args:
            file_path: Path to the model file
            
        Returns:
            True if the model is being loaded, False otherwise
        """
        return self.model_loader.is_loading(file_path)
    
    def _add_model(self, model: GGUFModel) -> None:
        """
        Add a model to the registry.
        
        Args:
            model: The model to add
        """
        self.logger.info(f"Adding model to registry: {model.name}")
        
        # Add to registry
        self.models[model.id] = model
        
        # Set as current model if no current model
        if not self.current_model_id:
            self.current_model_id = model.id
        
        # Emit signal
        self.model_added_signal.emit(model.id)
        
        # Publish event
        if self.event_bus:
            self.event_bus.publish("model.added", model.id, model.name)
    
    def _on_model_loaded(self, model: GGUFModel) -> None:
        """
        Handle model loaded event from ModelLoader.
        
        Args:
            model: The loaded model
        """
        self._add_model(model)
    
    def _on_model_loading_error(self, file_path: str, error: str) -> None:
        """
        Handle model loading error event from ModelLoader.
        
        Args:
            file_path: Path to the model file
            error: Error message
        """
        self.logger.error(f"Error loading model {file_path}: {error}")
        
        # Error is already published by ModelLoader
    
    def _on_loading_progress(self, file_path: str, progress: int) -> None:
        """
        Handle loading progress event from ModelLoader.
        
        Args:
            file_path: Path to the model file
            progress: Progress percentage (0-100)
        """
        # Emit signal
        self.model_loading_progress_signal.emit(file_path, progress)
    
    def _check_memory_usage(self) -> None:
        """Check memory usage and unload models if necessary."""
        try:
            # Get system memory info
            memory = psutil.virtual_memory()
            used_percentage = memory.percent
            available_mb = memory.available / (1024 * 1024)
            
            # Check if memory usage is high
            if used_percentage > 80:  # Warning threshold
                self.logger.warning(f"High memory usage: {used_percentage:.1f}% used, {available_mb:.1f} MB available")
                
                # Emit warning signal
                self.memory_warning_signal.emit(used_percentage, available_mb)
                
                # Publish event
                if self.event_bus:
                    self.event_bus.publish("model.memory_warning", used_percentage, available_mb)
                
                # Try to free up memory by unloading inactive models
                unloaded_count = self.unload_inactive_models()
                if unloaded_count > 0:
                    self.logger.info(f"Unloaded {unloaded_count} inactive models to free up memory")
            
            # Check if memory usage is critical
            if used_percentage > 90:  # Critical threshold
                self.logger.error(f"Critical memory usage: {used_percentage:.1f}% used, {available_mb:.1f} MB available")
                
                # Publish critical event
                if self.event_bus:
                    self.event_bus.publish("model.memory_critical", used_percentage, available_mb)
                
                # If still critical, unload the current model as a last resort
                if used_percentage > 95 and available_mb < 100:  # Extreme critical
                    if self.current_model_id:
                        self.logger.warning("Emergency unload of current model due to critical memory usage")
                        self.unload_model(self.current_model_id)
                        
                        # Publish emergency unload event
                        if self.event_bus:
                            self.event_bus.publish("model.emergency_unload", self.current_model_id)
        
        except Exception as e:
            self.logger.error(f"Error checking memory usage: {e}")
    
    def _check_memory_before_load(self, file_path: str) -> bool:
        """
        Check if there's enough memory to load a model.
        
        Args:
            file_path: Path to the model file
            
        Returns:
            True if there's enough memory, False otherwise
        """
        try:
            # Get system memory info
            memory = psutil.virtual_memory()
            available_bytes = memory.available
            
            # Get file size
            file_size = os.path.getsize(file_path)
            
            # Estimate required memory (1.2x file size)
            required_bytes = int(file_size * 1.2)
            
            # Check if there's enough memory
            if required_bytes > available_bytes:
                self.logger.warning(f"Not enough memory to load model: {file_path}")
                self.logger.warning(f"Required: {required_bytes / (1024 * 1024):.2f} MB, Available: {available_bytes / (1024 * 1024):.2f} MB")
                
                # Try to free up memory by unloading inactive models
                unloaded_count = self.unload_inactive_models()
                if unloaded_count > 0:
                    self.logger.info(f"Unloaded {unloaded_count} inactive models to free up memory")
                
                # Check again
                memory = psutil.virtual_memory()
                available_bytes = memory.available
                
                if required_bytes > available_bytes:
                    error_message = (f"Still not enough memory to load model: {file_path}. "
                                   f"Required: {required_bytes / (1024 * 1024):.2f} MB, "
                                   f"Available: {available_bytes / (1024 * 1024):.2f} MB")
                    
                    self.logger.error(error_message)
                    
                    # Publish event
                    if self.event_bus:
                        self.event_bus.publish("model.error", error_message, file_path)
                    
                    return False
            
            return True
            
        except Exception as e:
            self.logger.error(f"Error getting file size: {file_path}: {e}")
            # Assume there's enough memory if we can't check
            return True