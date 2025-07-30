"""
Model Backend Abstraction Layer

This module provides the abstract base classes and interfaces for different
model inference backends, enabling easy switching between llama-cpp-python,
ctransformers, transformers, and other backends.
"""

import logging
import time
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from enum import Enum
from typing import Dict, Any, Optional, List, Tuple, Union
from pathlib import Path


class BackendType(Enum):
    """Enumeration of supported backend types."""
    CTRANSFORMERS = "ctransformers"
    TRANSFORMERS = "transformers"
    LLAMAFILE = "llamafile"
    LLAMA_CPP_PYTHON = "llama-cpp-python"


class HardwareType(Enum):
    """Enumeration of hardware acceleration types."""
    CPU = "cpu"
    CUDA = "cuda"
    ROCM = "rocm"
    METAL = "metal"
    VULKAN = "vulkan"
    OPENCL = "opencl"
    MPS = "mps"  # Apple Metal Performance Shaders


@dataclass
class BackendConfig:
    """Configuration for a specific backend."""
    name: str
    enabled: bool = True
    priority: int = 0
    gpu_enabled: bool = True
    gpu_layers: int = -1  # -1 means auto-detect
    context_size: int = 4096
    batch_size: int = 512
    threads: int = -1  # -1 means auto-detect
    custom_args: Dict[str, Any] = field(default_factory=dict)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization."""
        return {
            'name': self.name,
            'enabled': self.enabled,
            'priority': self.priority,
            'gpu_enabled': self.gpu_enabled,
            'gpu_layers': self.gpu_layers,
            'context_size': self.context_size,
            'batch_size': self.batch_size,
            'threads': self.threads,
            'custom_args': self.custom_args
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'BackendConfig':
        """Create from dictionary."""
        return cls(
            name=data['name'],
            enabled=data.get('enabled', True),
            priority=data.get('priority', 0),
            gpu_enabled=data.get('gpu_enabled', True),
            gpu_layers=data.get('gpu_layers', -1),
            context_size=data.get('context_size', 4096),
            batch_size=data.get('batch_size', 512),
            threads=data.get('threads', -1),
            custom_args=data.get('custom_args', {})
        )


@dataclass
class HardwareInfo:
    """Information about available hardware."""
    gpu_count: int = 0
    gpu_devices: List[Dict[str, Any]] = field(default_factory=list)
    total_vram: int = 0  # Total VRAM in MB
    cpu_cores: int = 0
    total_ram: int = 0  # Total RAM in MB
    recommended_backend: Optional[str] = None
    supported_hardware: List[HardwareType] = field(default_factory=list)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization."""
        return {
            'gpu_count': self.gpu_count,
            'gpu_devices': self.gpu_devices,
            'total_vram': self.total_vram,
            'cpu_cores': self.cpu_cores,
            'total_ram': self.total_ram,
            'recommended_backend': self.recommended_backend,
            'supported_hardware': [hw.value for hw in self.supported_hardware]
        }


@dataclass
class LoadingResult:
    """Result of model loading operation."""
    success: bool
    backend_used: str
    hardware_used: str
    load_time: float
    memory_usage: int = 0  # Memory usage in MB
    error_message: Optional[str] = None
    model_info: Dict[str, Any] = field(default_factory=dict)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization."""
        return {
            'success': self.success,
            'backend_used': self.backend_used,
            'hardware_used': self.hardware_used,
            'load_time': self.load_time,
            'memory_usage': self.memory_usage,
            'error_message': self.error_message,
            'model_info': self.model_info
        }


@dataclass
class GenerationConfig:
    """Configuration for text generation."""
    max_tokens: int = 512
    temperature: float = 0.7
    top_p: float = 0.9
    top_k: int = 40
    repeat_penalty: float = 1.1
    seed: int = -1
    stop_sequences: List[str] = field(default_factory=list)
    stream: bool = False
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for backend-specific usage."""
        return {
            'max_tokens': self.max_tokens,
            'temperature': self.temperature,
            'top_p': self.top_p,
            'top_k': self.top_k,
            'repeat_penalty': self.repeat_penalty,
            'seed': self.seed if self.seed >= 0 else None,
            'stop': self.stop_sequences if self.stop_sequences else None,
            'stream': self.stream
        }


class BackendError(Exception):
    """Base class for backend errors."""
    pass


class InstallationError(BackendError):
    """Backend installation or dependency issues."""
    pass


class HardwareError(BackendError):
    """Hardware acceleration issues."""
    pass


class ModelLoadingError(BackendError):
    """Model loading specific issues."""
    pass


class ModelBackend(ABC):
    """Abstract base class for model backends."""
    
    def __init__(self, config: BackendConfig):
        """Initialize the backend with configuration."""
        self.config = config
        self.logger = logging.getLogger(f"backend.{config.name}")
        self.model = None
        self.model_path = None
        self.hardware_info = None
        self.is_loaded = False
        self.load_time = 0.0
        self.memory_usage = 0
    
    @abstractmethod
    def is_available(self) -> Tuple[bool, Optional[str]]:
        """
        Check if this backend is available on the system.
        
        Returns:
            Tuple of (is_available, error_message)
        """
        pass
    
    @abstractmethod
    def load_model(self, model_path: str, **kwargs) -> LoadingResult:
        """
        Load a model from the given path.
        
        Args:
            model_path: Path to the model file
            **kwargs: Additional backend-specific arguments
            
        Returns:
            LoadingResult with success status and details
        """
        pass
    
    @abstractmethod
    def generate_text(self, prompt: str, config: GenerationConfig) -> str:
        """
        Generate text from the given prompt.
        
        Args:
            prompt: Input text prompt
            config: Generation configuration
            
        Returns:
            Generated text
            
        Raises:
            ModelLoadingError: If no model is loaded
            BackendError: If generation fails
        """
        pass
    
    @abstractmethod
    def unload_model(self) -> bool:
        """
        Unload the current model.
        
        Returns:
            True if successful, False otherwise
        """
        pass
    
    @abstractmethod
    def get_hardware_info(self) -> HardwareInfo:
        """
        Get information about hardware acceleration.
        
        Returns:
            HardwareInfo object with current hardware status
        """
        pass
    
    def get_backend_type(self) -> BackendType:
        """Get the backend type."""
        return BackendType(self.config.name)
    
    def get_model_info(self) -> Dict[str, Any]:
        """Get information about the currently loaded model."""
        base_info = {
            'backend': self.config.name,
            'config': self.config.to_dict()
        }
        
        if self.is_loaded:
            base_info.update({
                'model_path': self.model_path,
                'load_time': self.load_time,
                'memory_usage': self.memory_usage,
                'hardware_info': self.hardware_info.to_dict() if self.hardware_info else None,
            })
        
        return base_info
    
    def validate_model_path(self, model_path: str) -> Tuple[bool, Optional[str]]:
        """
        Validate that the model path exists and is accessible.
        
        Args:
            model_path: Path to validate
            
        Returns:
            Tuple of (is_valid, error_message)
        """
        try:
            path = Path(model_path)
            if not path.exists():
                return False, f"Model file does not exist: {model_path}"
            
            if not path.is_file():
                return False, f"Path is not a file: {model_path}"
            
            if path.stat().st_size == 0:
                return False, f"Model file is empty: {model_path}"
            
            return True, None
            
        except Exception as e:
            return False, f"Error validating model path: {e}"
    
    def _measure_load_time(self, func):
        """Decorator to measure loading time."""
        def wrapper(*args, **kwargs):
            start_time = time.time()
            result = func(*args, **kwargs)
            self.load_time = time.time() - start_time
            return result
        return wrapper


class BackendRegistry:
    """Registry for managing available backends."""
    
    def __init__(self):
        """Initialize the backend registry."""
        self.backends: Dict[str, type] = {}
        self.configs: Dict[str, BackendConfig] = {}
        self.logger = logging.getLogger("backend.registry")
    
    def register_backend(self, backend_type: BackendType, backend_class: type):
        """
        Register a backend implementation.
        
        Args:
            backend_type: Type of backend
            backend_class: Backend implementation class
        """
        if not issubclass(backend_class, ModelBackend):
            raise ValueError(f"Backend class must inherit from ModelBackend")
        
        self.backends[backend_type.value] = backend_class
        self.logger.info(f"Registered backend: {backend_type.value}")
    
    def get_backend(self, backend_type: BackendType, config: BackendConfig) -> ModelBackend:
        """
        Get a backend instance.
        
        Args:
            backend_type: Type of backend to create
            config: Configuration for the backend
            
        Returns:
            Backend instance
            
        Raises:
            ValueError: If backend type is not registered
        """
        if backend_type.value not in self.backends:
            raise ValueError(f"Backend not registered: {backend_type.value}")
        
        backend_class = self.backends[backend_type.value]
        return backend_class(config)
    
    def list_available_backends(self) -> List[Tuple[BackendType, bool, Optional[str]]]:
        """
        List all registered backends and their availability.
        
        Returns:
            List of tuples (backend_type, is_available, error_message)
        """
        available_backends = []
        
        for backend_name, backend_class in self.backends.items():
            try:
                # Create a temporary config for availability check
                temp_config = BackendConfig(name=backend_name)
                backend = backend_class(temp_config)
                is_available, error = backend.is_available()
                available_backends.append((BackendType(backend_name), is_available, error))
            except Exception as e:
                available_backends.append((BackendType(backend_name), False, str(e)))
        
        return available_backends
    
    def get_default_configs(self) -> Dict[str, BackendConfig]:
        """Get default configurations for all registered backends."""
        default_configs = {}
        
        for backend_name in self.backends.keys():
            default_configs[backend_name] = BackendConfig(
                name=backend_name,
                priority=self._get_default_priority(backend_name)
            )
        
        return default_configs
    
    def _get_default_priority(self, backend_name: str) -> int:
        """Get default priority for a backend (lower number = higher priority)."""
        priority_map = {
            BackendType.CTRANSFORMERS.value: 1,
            BackendType.TRANSFORMERS.value: 2,
            BackendType.LLAMAFILE.value: 3,
            BackendType.LLAMA_CPP_PYTHON.value: 4
        }
        return priority_map.get(backend_name, 99)


# Global backend registry instance
backend_registry = BackendRegistry()