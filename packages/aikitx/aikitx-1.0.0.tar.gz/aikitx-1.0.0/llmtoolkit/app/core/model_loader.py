"""
Model Loader

This module contains the ModelLoader class, which is responsible for loading
GGUF model files, validating them, and reporting progress for large files.
"""

import os
import logging
import threading
import time
from pathlib import Path
from typing import Dict, Any, Optional, List, Tuple, Callable, Union

from PySide6.QtCore import QObject, Signal, Slot, QThread, QMutex, QWaitCondition, QTimer

from llmtoolkit.app.models.gguf_model import GGUFModel, ModelValidationError

class LoaderThread(QThread):
    """Thread for loading models in the background."""
    
    # Signals
    progress_signal = Signal(int)  # Progress percentage (0-100)
    success_signal = Signal(object)  # GGUFModel object
    error_signal = Signal(str)  # Error message
    
    def __init__(self, file_path: str, load_type=None, use_compression=False, parent=None):
        """
        Initialize the loader thread.
        
        Args:
            file_path: Path to the model file to load
            load_type: Type of loading to use (full, mmap, lazy), or None to use default
            use_compression: Whether to use compression
            parent: Parent object
        """
        super().__init__(parent)
        self.file_path = file_path
        self.load_type = load_type  # Can be None, "full", "mmap", or "lazy"
        self.use_compression = use_compression
        self.logger = logging.getLogger("gguf_loader.model_loader.thread")
        self.cancelled = False
    
    def run(self):
        """Run the thread."""
        try:
            # Get file info for progress estimation
            file_size = os.path.getsize(self.file_path)
            is_large_file = file_size > 100 * 1024 * 1024  # > 100MB
            
            # Report initial progress
            self.progress_signal.emit(5)
            if self.cancelled:
                return
            
            # Create model object
            model = GGUFModel(file_path=self.file_path)
            
            # Validate the model using enhanced validation
            is_valid, error = model.validate()
            if not is_valid:
                self.error_signal.emit(error)
                return
            
            # Report progress after validation
            self.progress_signal.emit(15)
            if self.cancelled:
                return
            
            # Extract metadata with progress reporting for large files
            if is_large_file:
                self.logger.info(f"Extracting metadata from large file ({file_size / (1024*1024):.1f} MB)")
            
            if not model.extract_metadata():
                self.error_signal.emit("Failed to extract model metadata")
                return
            
            # Report progress after metadata extraction
            self.progress_signal.emit(35)
            if self.cancelled:
                return
            
            # Map load type to GGUFModel constants
            if self.load_type == "memory_mapped":
                load_type = GGUFModel.LOAD_TYPE_MEMORY_MAPPED
            elif self.load_type == "lazy":
                load_type = GGUFModel.LOAD_TYPE_LAZY
            else:
                load_type = GGUFModel.LOAD_TYPE_FULL
            
            # Report progress before loading
            self.progress_signal.emit(40)
            if self.cancelled:
                return
            
            # Load the model with the specified loading strategy
            # For large files, provide more granular progress updates
            if is_large_file:
                self.logger.info(f"Loading large model using {load_type} strategy")
                
                # Simulate progress during loading for large files
                for progress in range(45, 85, 5):
                    if self.cancelled:
                        return
                    self.progress_signal.emit(progress)
                    time.sleep(0.1)  # Small delay to show progress
            
            if not model.load(load_type):
                self.error_signal.emit(f"Failed to load model using {load_type} strategy")
                return
            
            # Report progress after loading
            self.progress_signal.emit(85)
            if self.cancelled:
                return
            
            # Save metadata for future use
            model.save_metadata()
            
            # Report near completion
            self.progress_signal.emit(95)
            if self.cancelled:
                return
            
            # Final validation that model is properly loaded
            if not model.loaded:
                self.error_signal.emit("Model loading completed but model is not in loaded state")
                return
            
            # Report completion
            self.progress_signal.emit(100)
            
            # Log success with details
            self.logger.info(f"Model loaded successfully: {model.name} "
                           f"({model.get_size_str()}, {load_type} loading, "
                           f"memory usage: {model.memory_usage / (1024*1024):.1f} MB)")
            
            # Emit success signal with the loaded model
            self.success_signal.emit(model)
            
        except Exception as e:
            self.logger.exception(f"Error loading model: {e}")
            self.error_signal.emit(str(e))
    
    def cancel(self):
        """Cancel the loading operation."""
        self.cancelled = True

class ModelLoader(QObject):
    """
    Handles loading GGUF model files.
    
    This class is responsible for:
    - Loading GGUF model files
    - Validating the GGUF format
    - Reporting progress for large files
    """
    
    # Signals
    progress_signal = Signal(str, int)  # (file_path, progress_percentage)
    model_loaded_signal = Signal(object)  # GGUFModel object
    error_signal = Signal(str, str)  # (file_path, error_message)
    
    def __init__(self, event_bus=None, recovery_manager=None, parent=None):
        """
        Initialize the model loader.
        
        Args:
            event_bus: Optional event bus for publishing events
            recovery_manager: Optional recovery manager for handling errors
            parent: Parent object
        """
        super().__init__(parent)
        self.logger = logging.getLogger("gguf_loader.model_loader")
        self.event_bus = event_bus
        self.recovery_manager = recovery_manager
        self.active_loaders = {}  # file_path -> LoaderThread
        
        # Track failed loading attempts for retry
        self.failed_attempts = {}  # file_path -> count
    
    def load_model(self, file_path: str, load_type: str = None, use_compression: bool = False) -> None:
        """
        Load a GGUF model asynchronously.
        
        Args:
            file_path: Path to the model file
            load_type: Type of loading to use (full, memory_mapped, lazy), or None to use default
            use_compression: Whether to use compression
        """
        self.logger.info(f"Loading model: {file_path} (load_type: {load_type}, compression: {use_compression})")
        
        # Check if file exists
        if not os.path.exists(file_path):
            error_msg = f"File not found: {file_path}"
            self.logger.error(error_msg)
            self.error_signal.emit(file_path, error_msg)
            if self.event_bus:
                self.event_bus.publish("model.error", error_msg, file_path)
            return
        
        # Check if already loading
        if file_path in self.active_loaders:
            self.logger.warning(f"Already loading model: {file_path}")
            return
        
        # Save state for potential recovery
        if self.recovery_manager:
            state = {
                "operation": "model_load",
                "file_path": file_path,
                "load_type": load_type,
                "use_compression": use_compression,
                "timestamp": time.time()
            }
            self.recovery_manager.save_state(f"model_load_{os.path.basename(file_path)}", state)
        
        # Create and start loader thread
        loader_thread = LoaderThread(file_path, load_type, use_compression)
        
        # Connect signals
        loader_thread.progress_signal.connect(
            lambda progress: self._on_progress(file_path, progress))
        loader_thread.success_signal.connect(
            lambda model: self._on_success(file_path, model))
        loader_thread.error_signal.connect(
            lambda error: self._on_error(file_path, error))
        
        # Store and start the thread
        self.active_loaders[file_path] = loader_thread
        loader_thread.start()
    
    def validate_gguf_format(self, file_path: str) -> Tuple[bool, Optional[str]]:
        """
        Validate GGUF file format and integrity.
        
        Args:
            file_path: Path to the GGUF file
            
        Returns:
            Tuple of (is_valid, error_message)
        """
        try:
            # Check if file exists
            if not os.path.exists(file_path):
                return False, f"File does not exist: {file_path}"
            
            # Check file extension
            if not file_path.lower().endswith('.gguf'):
                return False, f"File does not have .gguf extension: {file_path}"
            
            # Check file size (minimum size for a valid GGUF file)
            file_size = os.path.getsize(file_path)
            if file_size < 16:  # Minimum size for GGUF header
                return False, f"File too small to be a valid GGUF file: {file_size} bytes"
            
            # Check GGUF magic bytes and basic header structure
            with open(file_path, 'rb') as f:
                # Read magic bytes (4 bytes)
                magic = f.read(4)
                if magic != b'GGUF':
                    return False, f"Invalid GGUF magic bytes: {magic}"
                
                # Read version (4 bytes, little-endian uint32)
                version_bytes = f.read(4)
                if len(version_bytes) != 4:
                    return False, "Incomplete GGUF header: missing version"
                
                version = int.from_bytes(version_bytes, byteorder='little')
                if version < 1 or version > 3:  # Support GGUF versions 1-3
                    return False, f"Unsupported GGUF version: {version}"
                
                # Read tensor count (8 bytes, little-endian uint64)
                tensor_count_bytes = f.read(8)
                if len(tensor_count_bytes) != 8:
                    return False, "Incomplete GGUF header: missing tensor count"
                
                tensor_count = int.from_bytes(tensor_count_bytes, byteorder='little')
                if tensor_count > 10000:  # Reasonable upper limit
                    return False, f"Suspicious tensor count: {tensor_count}"
                
                # Read metadata count (8 bytes, little-endian uint64)
                metadata_count_bytes = f.read(8)
                if len(metadata_count_bytes) != 8:
                    return False, "Incomplete GGUF header: missing metadata count"
                
                metadata_count = int.from_bytes(metadata_count_bytes, byteorder='little')
                if metadata_count > 1000:  # Reasonable upper limit
                    return False, f"Suspicious metadata count: {metadata_count}"
            
            return True, None
            
        except Exception as e:
            return False, f"Error validating GGUF format: {e}"
    
    def get_file_info(self, file_path: str) -> Dict[str, Any]:
        """
        Get detailed file information for progress reporting.
        
        Args:
            file_path: Path to the file
            
        Returns:
            Dictionary containing file information
        """
        try:
            stat = os.stat(file_path)
            return {
                'size': stat.st_size,
                'size_mb': stat.st_size / (1024 * 1024),
                'modified_time': stat.st_mtime,
                'is_large': stat.st_size > 100 * 1024 * 1024,  # > 100MB
                'estimated_load_time': self._estimate_load_time(stat.st_size)
            }
        except Exception as e:
            self.logger.error(f"Error getting file info: {e}")
            return {}
    
    def _estimate_load_time(self, file_size: int) -> float:
        """
        Estimate loading time based on file size.
        
        Args:
            file_size: Size of the file in bytes
            
        Returns:
            Estimated loading time in seconds
        """
        # Rough estimates based on typical SSD performance
        # These are very approximate and will vary based on hardware
        mb_size = file_size / (1024 * 1024)
        
        if mb_size < 100:
            return 1.0  # Small models load quickly
        elif mb_size < 1000:
            return mb_size * 0.05  # ~50ms per MB
        else:
            return mb_size * 0.1   # Larger models take longer per MB
    
    def load_model_sync(self, file_path: str, load_type: str = None, use_compression: bool = False, hardware_settings: Dict[str, Any] = None) -> Tuple[Optional[GGUFModel], Optional[str]]:
        """
        Load a GGUF model synchronously.
        
        Args:
            file_path: Path to the model file
            load_type: Type of loading to use (full, memory_mapped, lazy), or None to use default
            use_compression: Whether to use compression
            hardware_settings: Hardware acceleration settings
            
        Returns:
            Tuple of (model, error_message), where model is None if loading failed
        """
        self.logger.info(f"Loading model synchronously: {file_path} (load_type: {load_type}, compression: {use_compression})")
        
        if hardware_settings:
            self.logger.info(f"Using hardware acceleration with backend: {hardware_settings.get('backend', 'unknown')}")
        
        try:
            # Check if file exists
            if not os.path.exists(file_path):
                return None, f"File not found: {file_path}"
            
            # Enhanced GGUF format validation
            is_valid, error = self.validate_gguf_format(file_path)
            if not is_valid:
                return None, error
            
            # Create model object
            model = GGUFModel(file_path=file_path)
            
            # Validate the model
            is_valid, error = model.validate()
            if not is_valid:
                return None, error
            
            # Extract metadata
            if not model.extract_metadata():
                return None, "Failed to extract model metadata"
            
            # Map load type to GGUFModel constants
            if load_type == "memory_mapped":
                model_load_type = GGUFModel.LOAD_TYPE_MEMORY_MAPPED
            elif load_type == "lazy":
                model_load_type = GGUFModel.LOAD_TYPE_LAZY
            else:
                model_load_type = GGUFModel.LOAD_TYPE_FULL
            
            # Apply hardware settings to the model
            if hardware_settings:
                model.hardware_settings = hardware_settings
            
            # Load the model with the specified loading strategy
            if not model.load(model_load_type):
                return None, f"Failed to load model using {load_type} strategy"
            
            # Save metadata for future use
            model.save_metadata()
            
            return model, None
            
        except Exception as e:
            self.logger.exception(f"Error loading model: {e}")
            return None, str(e)
    
    def cancel_loading(self, file_path: str) -> bool:
        """
        Cancel loading a model.
        
        Args:
            file_path: Path to the model file
            
        Returns:
            True if loading was cancelled, False if the model wasn't being loaded
        """
        if file_path in self.active_loaders:
            loader_thread = self.active_loaders[file_path]
            loader_thread.cancel()
            loader_thread.wait()  # Wait for thread to finish
            del self.active_loaders[file_path]
            self.logger.info(f"Cancelled loading model: {file_path}")
            return True
        return False
    
    def is_loading(self, file_path: str) -> bool:
        """
        Check if a model is currently being loaded.
        
        Args:
            file_path: Path to the model file
            
        Returns:
            True if the model is being loaded, False otherwise
        """
        return file_path in self.active_loaders
    
    def get_active_loaders(self) -> List[str]:
        """
        Get a list of models that are currently being loaded.
        
        Returns:
            List of file paths
        """
        return list(self.active_loaders.keys())
    
    def _on_progress(self, file_path: str, progress: int) -> None:
        """
        Handle progress update from loader thread.
        
        Args:
            file_path: Path to the model file
            progress: Progress percentage (0-100)
        """
        self.logger.debug(f"Loading progress for {file_path}: {progress}%")
        self.progress_signal.emit(file_path, progress)
        
        # Publish event if event bus is available
        if self.event_bus:
            self.event_bus.publish("model.loading.progress", file_path, progress)
    
    def _on_success(self, file_path: str, model: GGUFModel) -> None:
        """
        Handle successful model loading.
        
        Args:
            file_path: Path to the model file
            model: Loaded GGUFModel object
        """
        self.logger.info(f"Model loaded successfully: {file_path}")
        
        # Remove from active loaders
        if file_path in self.active_loaders:
            del self.active_loaders[file_path]
        
        # Reset failed attempts counter
        if file_path in self.failed_attempts:
            del self.failed_attempts[file_path]
        
        # Clear recovery state and restore features if needed
        if self.recovery_manager:
            # Clear the state for this model
            self.recovery_manager.clear_state(f"model_load_{os.path.basename(file_path)}")
            
            # If model loading feature was degraded, restore it
            if self.recovery_manager.is_feature_degraded("model_loading"):
                self.recovery_manager.restore_feature("model_loading")
        
        # Emit signal
        self.model_loaded_signal.emit(model)
        
        # Publish event if event bus is available
        if self.event_bus:
            self.event_bus.publish("model.loaded", model.id, model.name, model)
    
    def _on_error(self, file_path: str, error: str) -> None:
        """
        Handle error during model loading.
        
        Args:
            file_path: Path to the model file
            error: Error message
        """
        self.logger.error(f"Error loading model {file_path}: {error}")
        
        # Remove from active loaders
        if file_path in self.active_loaders:
            del self.active_loaders[file_path]
        
        # Track failed attempts for this file
        if file_path not in self.failed_attempts:
            self.failed_attempts[file_path] = 1
        else:
            self.failed_attempts[file_path] += 1
        
        # Check if we should retry
        if self.recovery_manager and self.failed_attempts[file_path] <= 3:
            # Only retry for certain types of errors that might be transient
            if any(transient_err in error.lower() for transient_err in 
                  ["timeout", "connection", "io error", "temporary"]):
                
                self.logger.info(f"Attempting automatic retry for {file_path} (attempt {self.failed_attempts[file_path]})")
                
                # Publish retry event
                if self.event_bus:
                    self.event_bus.publish("model.loading.retry", {
                        "file_path": file_path,
                        "attempt": self.failed_attempts[file_path],
                        "error": error
                    })
                
                # Use recovery manager to retry with exponential backoff
                retry_delay = 1.0 * (2 ** (self.failed_attempts[file_path] - 1))  # 1s, 2s, 4s
                
                # Schedule retry
                QTimer.singleShot(int(retry_delay * 1000), lambda: self.load_model(file_path))
                return
            
        # If we're not retrying or max retries reached, handle the error
        
        # Clear state if we have a recovery manager
        if self.recovery_manager:
            self.recovery_manager.clear_state(f"model_load_{os.path.basename(file_path)}")
            
            # If this is a critical model, mark the feature as degraded
            if self._is_critical_model(file_path):
                self.recovery_manager.degrade_feature(
                    "model_loading",
                    f"Failed to load critical model: {os.path.basename(file_path)}"
                )
        
        # Emit signal
        self.error_signal.emit(file_path, error)
        
        # Publish event if event bus is available
        if self.event_bus:
            self.event_bus.publish("model.error", error, file_path)
    
    def _is_critical_model(self, file_path: str) -> bool:
        """
        Determine if a model is critical for application functionality.
        
        Args:
            file_path: Path to the model file
            
        Returns:
            True if the model is critical, False otherwise
        """
        # This is a placeholder implementation
        # In a real application, this would check against a list of critical models
        # or use some other criteria to determine if the model is critical
        
        # For now, we'll consider all models non-critical
        return False