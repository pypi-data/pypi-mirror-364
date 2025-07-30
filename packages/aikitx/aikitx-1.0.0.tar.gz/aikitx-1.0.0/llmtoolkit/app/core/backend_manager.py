"""
Backend Manager with Fallback Logic

This module provides the BackendManager class that handles backend lifecycle,
automatic fallback, and intelligent backend selection based on hardware and
model requirements.
"""

import logging
import time
from typing import Dict, List, Optional, Tuple, Any, Callable
from dataclasses import dataclass
from pathlib import Path

from .model_backends import (
    BackendType, BackendConfig, HardwareInfo, LoadingResult, 
    GenerationConfig, ModelBackend, BackendRegistry, backend_registry,
    BackendError, InstallationError, HardwareError, ModelLoadingError
)
from .hardware_detector import HardwareDetector
from .monitoring import monitoring_manager, PerformanceMetrics
from .logging_config import log_with_context, log_performance


@dataclass
class BackendStatus:
    """Status information for a backend."""
    name: str
    available: bool
    error_message: Optional[str]
    last_checked: float
    load_attempts: int = 0
    success_count: int = 0
    failure_count: int = 0
    average_load_time: float = 0.0


class BackendManager:
    """Manages available backends and handles fallback logic."""
    
    def __init__(self, hardware_detector: Optional[HardwareDetector] = None):
        """
        Initialize the backend manager.
        
        Args:
            hardware_detector: Hardware detector instance (creates new if None)
        """
        self.logger = logging.getLogger("backend.manager")
        self.hardware_detector = hardware_detector or HardwareDetector()
        self.registry = backend_registry
        
        # Initialize monitoring
        self.monitoring_manager = monitoring_manager
        self.performance_monitor = monitoring_manager.performance_monitor
        
        # Register backends if not already registered
        self._ensure_backends_registered()
        
        # Backend management
        self.backends: Dict[str, ModelBackend] = {}
        self.backend_status: Dict[str, BackendStatus] = {}
        self.current_backend: Optional[ModelBackend] = None
        self.current_model_path: Optional[str] = None
        
        # Configuration
        self.configs: Dict[str, BackendConfig] = {}
        self.fallback_order = [
            BackendType.CTRANSFORMERS.value,
            BackendType.TRANSFORMERS.value,
            BackendType.LLAMAFILE.value,
            BackendType.LLAMA_CPP_PYTHON.value
        ]
        
        # Callbacks
        self.on_backend_changed: Optional[Callable[[str, str], None]] = None
        self.on_fallback_triggered: Optional[Callable[[str, str, str], None]] = None
        self.on_loading_progress: Optional[Callable[[str, int], None]] = None
        
        # Initialize
        self._initialize_configs()
        self._detect_available_backends()
    
    def _ensure_backends_registered(self):
        """Ensure all backends are registered with the registry."""
        try:
            # Import and register backends
            from llmtoolkit.app.backends.ctransformers_backend import CtransformersBackend
            from llmtoolkit.app.backends.transformers_backend import TransformersBackend
            from llmtoolkit.app.backends.llamafile_backend import LlamafileBackend
            from llmtoolkit.app.backends.llama_cpp_python_backend import LlamaCppPythonBackend
            
            # Register backends if not already registered
            backends_to_register = [
                (BackendType.CTRANSFORMERS, CtransformersBackend),
                (BackendType.TRANSFORMERS, TransformersBackend),
                (BackendType.LLAMAFILE, LlamafileBackend),
                (BackendType.LLAMA_CPP_PYTHON, LlamaCppPythonBackend),
            ]
            
            for backend_type, backend_class in backends_to_register:
                if backend_type.value not in self.registry.backends:
                    try:
                        self.registry.register_backend(backend_type, backend_class)
                        self.logger.info(f"Registered backend: {backend_type.value}")
                    except Exception as e:
                        self.logger.warning(f"Failed to register backend {backend_type.value}: {e}")
                        
        except ImportError as e:
            self.logger.warning(f"Some backends could not be imported: {e}")
    
    def _initialize_configs(self):
        """Initialize default configurations for all backends."""
        default_configs = self.registry.get_default_configs()
        
        for backend_name, config in default_configs.items():
            # Get optimal settings based on hardware
            hw_info = self.hardware_detector.get_hardware_info()
            optimal_settings = self.hardware_detector.get_optimal_settings(backend_name, 4096)  # Assume 4GB model
            
            # Update config with optimal settings
            config.gpu_enabled = optimal_settings.get('gpu_enabled', True)
            config.gpu_layers = optimal_settings.get('gpu_layers', -1)
            config.context_size = optimal_settings.get('context_size', 4096)
            config.batch_size = optimal_settings.get('batch_size', 512)
            config.threads = optimal_settings.get('threads', -1)
            
            self.configs[backend_name] = config
            self.logger.info(f"Initialized config for {backend_name}: GPU={config.gpu_enabled}, Layers={config.gpu_layers}")
    
    def _detect_available_backends(self):
        """Detect which backends are available on the system."""
        available_backends = self.registry.list_available_backends()
        
        for backend_type, is_available, error_message in available_backends:
            status = BackendStatus(
                name=backend_type.value,
                available=is_available,
                error_message=error_message,
                last_checked=time.time()
            )
            self.backend_status[backend_type.value] = status
            
            if is_available:
                self.logger.info(f"Backend available: {backend_type.value}")
            else:
                self.logger.warning(f"Backend unavailable: {backend_type.value} - {error_message}")
    
    def get_available_backends(self) -> List[str]:
        """
        Get list of available backend names.
        
        Returns:
            List of available backend names
        """
        return [name for name, status in self.backend_status.items() if status.available]
    
    def get_backend_status(self, backend_name: str) -> Optional[BackendStatus]:
        """
        Get status for a specific backend.
        
        Args:
            backend_name: Name of the backend
            
        Returns:
            BackendStatus object or None if not found
        """
        return self.backend_status.get(backend_name)
    
    def get_best_backend(self, model_size_mb: int = 4096, hardware_preference: str = 'auto') -> Optional[str]:
        """
        Get the best available backend for the given requirements.
        
        Args:
            model_size_mb: Size of the model in MB
            hardware_preference: Hardware preference ('auto', 'gpu', 'cpu')
            
        Returns:
            Best backend name or None if none available
        """
        available_backends = self.get_available_backends()
        if not available_backends:
            return None
        
        # Get hardware info for decision making
        hw_info = self.hardware_detector.get_hardware_info()
        
        # If hardware preference is specified, filter accordingly
        if hardware_preference == 'cpu':
            # Prefer backends that work well on CPU
            preferred_order = [BackendType.LLAMAFILE.value, BackendType.CTRANSFORMERS.value]
        elif hardware_preference == 'gpu':
            # Prefer GPU-accelerated backends
            if hw_info.gpu_count > 0:
                preferred_order = [BackendType.CTRANSFORMERS.value, BackendType.TRANSFORMERS.value]
            else:
                self.logger.warning("GPU preference specified but no GPUs detected")
                preferred_order = self.fallback_order
        else:
            # Auto selection based on hardware
            if hw_info.recommended_backend:
                preferred_order = [hw_info.recommended_backend] + [
                    b for b in self.fallback_order if b != hw_info.recommended_backend
                ]
            else:
                preferred_order = self.fallback_order
        
        # Find the first available backend in preferred order
        for backend_name in preferred_order:
            if backend_name in available_backends:
                # Check if backend can handle the model size
                if self._can_handle_model_size(backend_name, model_size_mb):
                    return backend_name
        
        # Fallback to any available backend
        return available_backends[0] if available_backends else None
    
    def _can_handle_model_size(self, backend_name: str, model_size_mb: int) -> bool:
        """Check if a backend can handle a model of the given size."""
        hw_info = self.hardware_detector.get_hardware_info()
        
        # Estimate memory requirements (model size + overhead)
        estimated_memory_mb = int(model_size_mb * 1.5)  # 50% overhead
        
        # Check if we have enough system RAM
        if estimated_memory_mb > hw_info.total_ram * 0.8:  # Don't use more than 80% of RAM
            return False
        
        # For GPU backends, check VRAM
        config = self.configs.get(backend_name)
        if config and config.gpu_enabled and hw_info.total_vram > 0:
            if estimated_memory_mb > hw_info.total_vram * 0.9:  # Don't use more than 90% of VRAM
                # Can still work in CPU mode
                self.logger.info(f"Model too large for GPU, will use CPU mode for {backend_name}")
        
        return True
    
    def load_model(self, model_path: str, backend_name: Optional[str] = None, **kwargs) -> LoadingResult:
        """
        Load a model using the specified or best available backend.
        
        Args:
            model_path: Path to the model file
            backend_name: Specific backend to use (None for auto-selection)
            **kwargs: Additional arguments for model loading
            
        Returns:
            LoadingResult with success status and details
        """
        # Validate model path
        if not Path(model_path).exists():
            return LoadingResult(
                success=False,
                backend_used="none",
                hardware_used="none",
                load_time=0.0,
                error_message=f"Model file does not exist: {model_path}"
            )
        
        # Get model size for backend selection
        model_size_mb = Path(model_path).stat().st_size // (1024 * 1024)
        
        # Determine which backend to use
        if backend_name:
            if backend_name not in self.get_available_backends():
                return LoadingResult(
                    success=False,
                    backend_used=backend_name,
                    hardware_used="none",
                    load_time=0.0,
                    error_message=f"Requested backend not available: {backend_name}"
                )
            backends_to_try = [backend_name]
        else:
            # Auto-select best backend and create fallback chain
            best_backend = self.get_best_backend(model_size_mb)
            if not best_backend:
                return LoadingResult(
                    success=False,
                    backend_used="none",
                    hardware_used="none",
                    load_time=0.0,
                    error_message="No backends available"
                )
            
            # Create fallback chain starting with best backend
            available = self.get_available_backends()
            backends_to_try = [best_backend] + [b for b in self.fallback_order if b in available and b != best_backend]
        
        # Try backends in order until one succeeds
        last_error = None
        for backend_name in backends_to_try:
            try:
                log_with_context(
                    self.logger, "INFO", f"Attempting to load model with {backend_name}",
                    backend_name=backend_name, operation="load", model_path=model_path
                )
                
                # Start performance monitoring
                operation_id = self.performance_monitor.start_operation(
                    backend_name, "load", model_path
                )
                
                # Update progress callback
                if self.on_loading_progress:
                    self.on_loading_progress(f"Trying {backend_name}...", 10)
                
                # Get or create backend instance
                backend = self._get_backend_instance(backend_name)
                
                # Update backend status
                status = self.backend_status[backend_name]
                status.load_attempts += 1
                
                # Attempt to load the model
                start_time = time.time()
                result = backend.load_model(model_path, **kwargs)
                load_time = time.time() - start_time
                
                if result.success:
                    # Success! Update status and set as current backend
                    status.success_count += 1
                    status.average_load_time = (status.average_load_time * (status.success_count - 1) + load_time) / status.success_count
                    
                    # End performance monitoring
                    self.performance_monitor.end_operation(operation_id, True)
                    
                    # Unload previous model if different backend
                    if self.current_backend and self.current_backend != backend:
                        self._unload_current_model()
                    
                    self.current_backend = backend
                    self.current_model_path = model_path
                    
                    # Notify about backend change
                    if self.on_backend_changed:
                        self.on_backend_changed(backend_name, model_path)
                    
                    log_performance(
                        self.logger, backend_name, "load", load_time * 1000,
                        success=True, model_path=model_path,
                        memory_usage_mb=result.memory_usage
                    )
                    
                    return result
                else:
                    # This backend failed, try next one
                    status.failure_count += 1
                    last_error = result.error_message
                    
                    # End performance monitoring with failure
                    self.performance_monitor.end_operation(
                        operation_id, False, result.error_message
                    )
                    
                    log_performance(
                        self.logger, backend_name, "load", load_time * 1000,
                        success=False, error_message=result.error_message,
                        model_path=model_path
                    )
                    
                    # Notify about fallback
                    if len(backends_to_try) > 1 and self.on_fallback_triggered:
                        next_backend = backends_to_try[backends_to_try.index(backend_name) + 1] if backends_to_try.index(backend_name) + 1 < len(backends_to_try) else "none"
                        self.on_fallback_triggered(backend_name, next_backend, result.error_message)
            
            except Exception as e:
                # Unexpected error with this backend
                status = self.backend_status.get(backend_name)
                if status:
                    status.failure_count += 1
                
                # End performance monitoring with error
                if 'operation_id' in locals():
                    self.performance_monitor.end_operation(operation_id, False, str(e))
                
                last_error = str(e)
                log_with_context(
                    self.logger, "ERROR", f"Unexpected error with backend {backend_name}: {e}",
                    backend_name=backend_name, operation="load", model_path=model_path
                )
        
        # All backends failed
        return LoadingResult(
            success=False,
            backend_used="none",
            hardware_used="none",
            load_time=0.0,
            error_message=f"All backends failed. Last error: {last_error}"
        )
    
    def _get_backend_instance(self, backend_name: str) -> ModelBackend:
        """Get or create a backend instance."""
        if backend_name not in self.backends:
            config = self.configs[backend_name]
            backend_type = BackendType(backend_name)
            self.backends[backend_name] = self.registry.get_backend(backend_type, config)
        
        return self.backends[backend_name]
    
    def generate_text(self, prompt: str, config: GenerationConfig) -> str:
        """
        Generate text using the current backend.
        
        Args:
            prompt: Input text prompt
            config: Generation configuration
            
        Returns:
            Generated text
            
        Raises:
            ModelLoadingError: If no model is loaded
        """
        if not self.current_backend:
            raise ModelLoadingError("No model is currently loaded")
        
        # Start performance monitoring
        backend_name = self.current_backend.config.name
        operation_id = self.performance_monitor.start_operation(
            backend_name, "generate", self.current_model_path
        )
        
        try:
            start_time = time.time()
            result = self.current_backend.generate_text(prompt, config)
            duration = time.time() - start_time
            
            # Estimate tokens generated (rough approximation)
            tokens_generated = len(result.split()) if result else 0
            
            # End performance monitoring
            self.performance_monitor.end_operation(
                operation_id, True, tokens_generated=tokens_generated
            )
            
            log_performance(
                self.logger, backend_name, "generate", duration * 1000,
                success=True, tokens_generated=tokens_generated
            )
            
            return result
            
        except Exception as e:
            # End performance monitoring with error
            self.performance_monitor.end_operation(operation_id, False, str(e))
            
            log_performance(
                self.logger, backend_name, "generate", 0,
                success=False, error_message=str(e)
            )
            
            raise
    
    def unload_model(self) -> bool:
        """
        Unload the current model.
        
        Returns:
            True if successful, False otherwise
        """
        return self._unload_current_model()
    
    def _unload_current_model(self) -> bool:
        """Unload the current model."""
        if self.current_backend:
            backend_name = self.current_backend.config.name
            
            # Start performance monitoring
            operation_id = self.performance_monitor.start_operation(
                backend_name, "unload", self.current_model_path
            )
            
            try:
                start_time = time.time()
                success = self.current_backend.unload_model()
                duration = time.time() - start_time
                
                if success:
                    self.current_backend = None
                    self.current_model_path = None
                    
                    # End performance monitoring
                    self.performance_monitor.end_operation(operation_id, True)
                    
                    log_performance(
                        self.logger, backend_name, "unload", duration * 1000,
                        success=True
                    )
                else:
                    # End performance monitoring with failure
                    self.performance_monitor.end_operation(
                        operation_id, False, "Unload operation returned False"
                    )
                    
                    log_performance(
                        self.logger, backend_name, "unload", duration * 1000,
                        success=False, error_message="Unload operation returned False"
                    )
                
                return success
                
            except Exception as e:
                duration = time.time() - start_time if 'start_time' in locals() else 0
                
                # End performance monitoring with error
                self.performance_monitor.end_operation(operation_id, False, str(e))
                
                log_performance(
                    self.logger, backend_name, "unload", duration * 1000,
                    success=False, error_message=str(e)
                )
                
                return False
        return True
    
    def switch_backend(self, backend_name: str, reload_model: bool = True) -> bool:
        """
        Switch to a different backend.
        
        Args:
            backend_name: Name of the backend to switch to
            reload_model: Whether to reload the current model with the new backend
            
        Returns:
            True if successful, False otherwise
        """
        if backend_name not in self.get_available_backends():
            self.logger.error(f"Backend not available: {backend_name}")
            return False
        
        # Store current model path for reloading
        current_model = self.current_model_path
        
        # Unload current model
        if not self._unload_current_model():
            self.logger.warning("Failed to unload current model, continuing anyway")
        
        # If we should reload the model, do it with the new backend
        if reload_model and current_model:
            result = self.load_model(current_model, backend_name)
            return result.success
        
        return True
    
    def get_current_backend_info(self) -> Optional[Dict[str, Any]]:
        """Get information about the current backend."""
        if not self.current_backend:
            return None
        
        return self.current_backend.get_model_info()
    
    def get_hardware_info(self) -> HardwareInfo:
        """Get current hardware information."""
        return self.hardware_detector.get_hardware_info()
    
    def refresh_backend_availability(self):
        """Refresh the availability status of all backends."""
        self.logger.info("Refreshing backend availability...")
        self._detect_available_backends()
    
    def get_statistics(self) -> Dict[str, Any]:
        """Get usage statistics for all backends."""
        stats = {}
        
        for name, status in self.backend_status.items():
            stats[name] = {
                'available': status.available,
                'load_attempts': status.load_attempts,
                'success_count': status.success_count,
                'failure_count': status.failure_count,
                'success_rate': status.success_count / max(status.load_attempts, 1),
                'average_load_time': status.average_load_time,
                'last_checked': status.last_checked
            }
        
        return stats
    
    def get_monitoring_report(self) -> Dict[str, Any]:
        """Get comprehensive monitoring report."""
        return {
            'backend_statistics': self.get_statistics(),
            'performance_stats': self.performance_monitor.get_backend_stats(),
            'system_metrics': self.monitoring_manager.system_monitor.get_current_metrics(),
            'hardware_info': self.get_hardware_info(),
            'recent_operations': [
                {
                    'backend_name': m.backend_name,
                    'operation': m.operation,
                    'duration_ms': m.duration,
                    'success': m.success,
                    'timestamp': m.start_time,
                    'memory_usage_mb': m.memory_usage_mb,
                    'error_message': m.error_message
                }
                for m in self.performance_monitor.get_recent_metrics(20)
            ]
        }
    
    def start_monitoring(self):
        """Start the monitoring system."""
        self.monitoring_manager.start()
        log_with_context(
            self.logger, "INFO", "Backend monitoring started",
            operation="monitoring"
        )
    
    def stop_monitoring(self):
        """Stop the monitoring system."""
        self.monitoring_manager.stop()
        log_with_context(
            self.logger, "INFO", "Backend monitoring stopped",
            operation="monitoring"
        )
    
    def cleanup(self):
        """Clean up resources and unload models."""
        self.logger.info("Cleaning up backend manager...")
        
        # Unload current model
        self._unload_current_model()
        
        # Clean up all backend instances
        for backend in self.backends.values():
            try:
                backend.unload_model()
            except Exception as e:
                self.logger.warning(f"Error cleaning up backend: {e}")
        
        self.backends.clear()
        self.logger.info("Backend manager cleanup complete")