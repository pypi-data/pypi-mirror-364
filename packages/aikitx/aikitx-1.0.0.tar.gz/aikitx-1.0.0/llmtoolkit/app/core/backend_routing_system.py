"""
Backend Routing System

This module provides intelligent backend selection based on model format and hardware capabilities.
It implements format-to-backend mapping, backend capability assessment, and automatic fallback logic.
"""

import logging
import time
from typing import Dict, List, Optional, Tuple, Any, Set
from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path

from .universal_format_detector import ModelFormat, UniversalFormatDetector, FormatDetectionResult
from .model_backends import BackendType, BackendConfig, HardwareInfo, LoadingResult, ModelBackend
from .hardware_detector import HardwareDetector
from .monitoring import monitoring_manager


class BackendCapability(Enum):
    """Backend capability types."""
    GGUF_SUPPORT = "gguf_support"
    SAFETENSORS_SUPPORT = "safetensors_support"
    PYTORCH_SUPPORT = "pytorch_support"
    HUGGINGFACE_SUPPORT = "huggingface_support"
    GPU_ACCELERATION = "gpu_acceleration"
    CPU_OPTIMIZATION = "cpu_optimization"
    MEMORY_MAPPING = "memory_mapping"
    QUANTIZATION = "quantization"
    STREAMING = "streaming"


@dataclass
class CapabilityScore:
    """Score for backend capability assessment."""
    backend_name: str
    format_compatibility: float  # 0.0 to 1.0
    hardware_compatibility: float  # 0.0 to 1.0
    performance_score: float  # 0.0 to 1.0
    reliability_score: float  # 0.0 to 1.0
    total_score: float  # Weighted combination
    capabilities: Set[BackendCapability] = field(default_factory=set)
    limitations: List[str] = field(default_factory=list)
    recommendations: List[str] = field(default_factory=list)


@dataclass
class ModelInfo:
    """Information about a model for routing decisions."""
    format_type: ModelFormat
    file_path: Optional[str]
    file_size: int
    estimated_memory: int  # MB
    architecture: Optional[str] = None
    quantization: Optional[str] = None
    context_length: Optional[int] = None
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class LoadingPlan:
    """Plan for loading a model with backend selection and fallbacks."""
    primary_backend: str
    fallback_backends: List[str]
    format_type: ModelFormat
    model_info: ModelInfo
    memory_requirements: int  # MB
    optimization_suggestions: List[str]
    hardware_config: Dict[str, Any]
    confidence: float  # 0.0 to 1.0


@dataclass
class FallbackAttempt:
    """Record of a fallback attempt during loading."""
    backend_name: str
    attempt_time: float
    success: bool
    error_message: Optional[str]
    load_time: float


class BackendRoutingSystem:
    """
    Intelligent backend routing system that selects optimal backends based on
    model format, hardware capabilities, and performance characteristics.
    """
    
    def __init__(self, hardware_detector: Optional[HardwareDetector] = None):
        """
        Initialize the backend routing system.
        
        Args:
            hardware_detector: Hardware detector instance (creates new if None)
        """
        self.logger = logging.getLogger("backend.routing")
        self.hardware_detector = hardware_detector or HardwareDetector()
        self.format_detector = UniversalFormatDetector()
        
        # Backend capability definitions
        self._initialize_backend_capabilities()
        
        # Format to backend mappings with priorities
        self._initialize_format_mappings()
        
        # Performance tracking
        self.performance_history: Dict[str, List[float]] = {}
        self.reliability_history: Dict[str, List[bool]] = {}
        
        # Configuration
        self.fallback_enabled = True
        self.max_fallback_attempts = 3
        self.performance_weight = 0.3
        self.reliability_weight = 0.3
        self.compatibility_weight = 0.4
    
    def _initialize_backend_capabilities(self):
        """Initialize backend capability definitions."""
        self.backend_capabilities = {
            BackendType.CTRANSFORMERS.value: {
                BackendCapability.GGUF_SUPPORT,
                BackendCapability.GPU_ACCELERATION,
                BackendCapability.CPU_OPTIMIZATION,
                BackendCapability.QUANTIZATION,
                BackendCapability.MEMORY_MAPPING
            },
            BackendType.TRANSFORMERS.value: {
                BackendCapability.SAFETENSORS_SUPPORT,
                BackendCapability.PYTORCH_SUPPORT,
                BackendCapability.HUGGINGFACE_SUPPORT,
                BackendCapability.GPU_ACCELERATION,
                BackendCapability.STREAMING
            },
            BackendType.LLAMAFILE.value: {
                BackendCapability.GGUF_SUPPORT,
                BackendCapability.CPU_OPTIMIZATION,
                BackendCapability.MEMORY_MAPPING,
                BackendCapability.QUANTIZATION
            },
            BackendType.LLAMA_CPP_PYTHON.value: {
                BackendCapability.GGUF_SUPPORT,
                BackendCapability.GPU_ACCELERATION,
                BackendCapability.CPU_OPTIMIZATION,
                BackendCapability.MEMORY_MAPPING,
                BackendCapability.QUANTIZATION,
                BackendCapability.STREAMING
            }
        }
    
    def _initialize_format_mappings(self):
        """Initialize format to backend mappings with priorities."""
        self.format_mappings = {
            ModelFormat.GGUF: [
                (BackendType.CTRANSFORMERS.value, 1.0),
                (BackendType.LLAMA_CPP_PYTHON.value, 0.9),
                (BackendType.LLAMAFILE.value, 0.8)
            ],
            ModelFormat.SAFETENSORS: [
                (BackendType.TRANSFORMERS.value, 1.0)
            ],
            ModelFormat.PYTORCH_BIN: [
                (BackendType.TRANSFORMERS.value, 1.0)
            ],
            ModelFormat.HUGGINGFACE: [
                (BackendType.TRANSFORMERS.value, 1.0)
            ]
        }
    
    def get_optimal_backend(self, model_info: ModelInfo, hardware_info: HardwareInfo) -> str:
        """
        Get the optimal backend for a model and hardware combination.
        
        Args:
            model_info: Information about the model
            hardware_info: Hardware information
            
        Returns:
            Name of the optimal backend
        """
        self.logger.info(f"Finding optimal backend for {model_info.format_type.value} model")
        
        # Get compatible backends for the format
        compatible_backends = self.get_backend_for_format(model_info.format_type)
        
        if not compatible_backends:
            self.logger.warning(f"No backends support format: {model_info.format_type.value}")
            return None
        
        # Score each backend
        backend_scores = []
        for backend_name in compatible_backends:
            score = self.assess_backend_capability(backend_name, model_info, hardware_info)
            backend_scores.append((backend_name, score))
        
        # Sort by total score (descending)
        backend_scores.sort(key=lambda x: x[1].total_score, reverse=True)
        
        optimal_backend = backend_scores[0][0]
        optimal_score = backend_scores[0][1]
        
        self.logger.info(
            f"Selected {optimal_backend} with score {optimal_score.total_score:.3f} "
            f"(format: {optimal_score.format_compatibility:.3f}, "
            f"hardware: {optimal_score.hardware_compatibility:.3f}, "
            f"performance: {optimal_score.performance_score:.3f})"
        )
        
        return optimal_backend
    
    def get_backend_for_format(self, format_type: ModelFormat) -> List[str]:
        """
        Get list of backends that support a specific format.
        
        Args:
            format_type: Model format type
            
        Returns:
            List of backend names that support the format
        """
        if format_type not in self.format_mappings:
            self.logger.warning(f"No backend mapping for format: {format_type.value}")
            return []
        
        # Return backends sorted by priority
        backends = [backend for backend, _ in self.format_mappings[format_type]]
        return backends
    
    def assess_backend_capability(self, backend_name: str, model_info: ModelInfo, 
                                hardware_info: HardwareInfo) -> CapabilityScore:
        """
        Assess a backend's capability for a specific model and hardware combination.
        
        Args:
            backend_name: Name of the backend to assess
            model_info: Information about the model
            hardware_info: Hardware information
            
        Returns:
            CapabilityScore with detailed assessment
        """
        # Get backend capabilities
        capabilities = self.backend_capabilities.get(backend_name, set())
        
        # Assess format compatibility
        format_compatibility = self._assess_format_compatibility(
            backend_name, model_info.format_type, capabilities
        )
        
        # Assess hardware compatibility
        hardware_compatibility = self._assess_hardware_compatibility(
            backend_name, hardware_info, capabilities
        )
        
        # Assess performance score
        performance_score = self._assess_performance_score(
            backend_name, model_info, hardware_info
        )
        
        # Assess reliability score
        reliability_score = self._assess_reliability_score(backend_name)
        
        # Calculate total weighted score
        total_score = (
            format_compatibility * self.compatibility_weight +
            hardware_compatibility * self.compatibility_weight +
            performance_score * self.performance_weight +
            reliability_score * self.reliability_weight
        )
        
        # Generate limitations and recommendations
        limitations = self._generate_limitations(backend_name, model_info, hardware_info, capabilities)
        recommendations = self._generate_recommendations(backend_name, model_info, hardware_info, capabilities)
        
        return CapabilityScore(
            backend_name=backend_name,
            format_compatibility=format_compatibility,
            hardware_compatibility=hardware_compatibility,
            performance_score=performance_score,
            reliability_score=reliability_score,
            total_score=total_score,
            capabilities=capabilities,
            limitations=limitations,
            recommendations=recommendations
        )
    
    def _assess_format_compatibility(self, backend_name: str, format_type: ModelFormat, 
                                   capabilities: Set[BackendCapability]) -> float:
        """Assess format compatibility score."""
        format_capability_map = {
            ModelFormat.GGUF: BackendCapability.GGUF_SUPPORT,
            ModelFormat.SAFETENSORS: BackendCapability.SAFETENSORS_SUPPORT,
            ModelFormat.PYTORCH_BIN: BackendCapability.PYTORCH_SUPPORT,
            ModelFormat.HUGGINGFACE: BackendCapability.HUGGINGFACE_SUPPORT
        }
        
        required_capability = format_capability_map.get(format_type)
        if required_capability and required_capability in capabilities:
            # Check if this backend is in the preferred list for this format
            if format_type in self.format_mappings:
                for backend, priority in self.format_mappings[format_type]:
                    if backend == backend_name:
                        return priority
            return 0.5  # Supports format but not preferred
        
        return 0.0  # Does not support format
    
    def _assess_hardware_compatibility(self, backend_name: str, hardware_info: HardwareInfo, 
                                     capabilities: Set[BackendCapability]) -> float:
        """Assess hardware compatibility score."""
        score = 0.5  # Base score
        
        # GPU acceleration bonus
        if (hardware_info.gpu_count > 0 and 
            BackendCapability.GPU_ACCELERATION in capabilities):
            score += 0.3
        
        # CPU optimization bonus for systems without GPU
        if (hardware_info.gpu_count == 0 and 
            BackendCapability.CPU_OPTIMIZATION in capabilities):
            score += 0.2
        
        # Memory mapping bonus for large models
        if BackendCapability.MEMORY_MAPPING in capabilities:
            score += 0.1
        
        # Quantization support bonus
        if BackendCapability.QUANTIZATION in capabilities:
            score += 0.1
        
        return min(score, 1.0)
    
    def _assess_performance_score(self, backend_name: str, model_info: ModelInfo, 
                                hardware_info: HardwareInfo) -> float:
        """Assess performance score based on historical data."""
        if backend_name not in self.performance_history:
            return 0.5  # Default score for new backends
        
        history = self.performance_history[backend_name]
        if not history:
            return 0.5
        
        # Calculate average performance (lower load time = higher score)
        avg_load_time = sum(history) / len(history)
        
        # Normalize to 0-1 scale (assuming 30 seconds is very slow)
        performance_score = max(0.0, 1.0 - (avg_load_time / 30.0))
        
        return performance_score
    
    def _assess_reliability_score(self, backend_name: str) -> float:
        """Assess reliability score based on success rate."""
        if backend_name not in self.reliability_history:
            return 0.5  # Default score for new backends
        
        history = self.reliability_history[backend_name]
        if not history:
            return 0.5
        
        # Calculate success rate
        success_rate = sum(1 for success in history if success) / len(history)
        return success_rate
    
    def _generate_limitations(self, backend_name: str, model_info: ModelInfo, 
                            hardware_info: HardwareInfo, capabilities: Set[BackendCapability]) -> List[str]:
        """Generate list of limitations for the backend."""
        limitations = []
        
        # Check for missing GPU support
        if (hardware_info.gpu_count > 0 and 
            BackendCapability.GPU_ACCELERATION not in capabilities):
            limitations.append("No GPU acceleration support")
        
        # Check for memory constraints
        if model_info.estimated_memory > hardware_info.total_ram * 0.8:
            if BackendCapability.MEMORY_MAPPING not in capabilities:
                limitations.append("May not handle large models efficiently")
        
        # Check for format-specific limitations
        if model_info.format_type == ModelFormat.HUGGINGFACE:
            if BackendCapability.HUGGINGFACE_SUPPORT not in capabilities:
                limitations.append("No direct Hugging Face integration")
        
        return limitations
    
    def _generate_recommendations(self, backend_name: str, model_info: ModelInfo, 
                                hardware_info: HardwareInfo, capabilities: Set[BackendCapability]) -> List[str]:
        """Generate recommendations for optimal usage."""
        recommendations = []
        
        # GPU recommendations
        if (hardware_info.gpu_count > 0 and 
            BackendCapability.GPU_ACCELERATION in capabilities):
            recommendations.append("Enable GPU acceleration for better performance")
        
        # Memory recommendations
        if model_info.estimated_memory > hardware_info.total_ram * 0.6:
            if BackendCapability.QUANTIZATION in capabilities:
                recommendations.append("Consider using quantization to reduce memory usage")
            if BackendCapability.MEMORY_MAPPING in capabilities:
                recommendations.append("Memory mapping will be used for efficient loading")
        
        # Format-specific recommendations
        if model_info.format_type == ModelFormat.GGUF:
            if BackendCapability.QUANTIZATION in capabilities:
                recommendations.append("GGUF format supports efficient quantization")
        
        return recommendations
    
    def route_model_loading(self, input_path: str, preferred_backend: Optional[str] = None) -> LoadingPlan:
        """
        Create a comprehensive loading plan for a model.
        
        Args:
            input_path: Path to model file/directory or HF model ID
            preferred_backend: Preferred backend name (optional)
            
        Returns:
            LoadingPlan with routing decisions and fallback strategy
        """
        self.logger.info(f"Creating loading plan for: {input_path}")
        
        # Detect model format
        detection_result = self.format_detector.detect_format(input_path)
        
        if detection_result.format_type == ModelFormat.UNKNOWN:
            raise ValueError(f"Could not detect model format: {detection_result.error_message}")
        
        # Create model info
        model_info = self._create_model_info(detection_result)
        
        # Get hardware info
        hardware_info = self.hardware_detector.get_hardware_info()
        
        # Determine primary backend
        if preferred_backend:
            # Validate preferred backend supports the format
            compatible_backends = self.get_backend_for_format(model_info.format_type)
            if preferred_backend in compatible_backends:
                primary_backend = preferred_backend
            else:
                self.logger.warning(
                    f"Preferred backend {preferred_backend} doesn't support {model_info.format_type.value}, "
                    f"falling back to optimal selection"
                )
                primary_backend = self.get_optimal_backend(model_info, hardware_info)
        else:
            primary_backend = self.get_optimal_backend(model_info, hardware_info)
        
        if not primary_backend:
            raise ValueError(f"No backend available for format: {model_info.format_type.value}")
        
        # Create fallback chain
        fallback_backends = self._create_fallback_chain(
            model_info.format_type, primary_backend, hardware_info
        )
        
        # Generate optimization suggestions
        optimization_suggestions = self._generate_optimization_suggestions(
            model_info, hardware_info, primary_backend
        )
        
        # Create hardware configuration
        hardware_config = self._create_hardware_config(primary_backend, hardware_info)
        
        # Calculate confidence based on format detection and backend compatibility
        confidence = self._calculate_loading_confidence(
            detection_result, primary_backend, model_info, hardware_info
        )
        
        return LoadingPlan(
            primary_backend=primary_backend,
            fallback_backends=fallback_backends,
            format_type=model_info.format_type,
            model_info=model_info,
            memory_requirements=model_info.estimated_memory,
            optimization_suggestions=optimization_suggestions,
            hardware_config=hardware_config,
            confidence=confidence
        )
    
    def _create_model_info(self, detection_result: FormatDetectionResult) -> ModelInfo:
        """Create ModelInfo from detection result."""
        file_size = 0
        estimated_memory = 0
        
        if detection_result.file_path:
            try:
                file_size = Path(detection_result.file_path).stat().st_size
                estimated_memory = int(file_size / (1024 * 1024) * 1.5)  # 50% overhead
            except:
                pass
        elif detection_result.directory_analysis:
            file_size = detection_result.directory_analysis.total_size
            estimated_memory = int(file_size / (1024 * 1024) * 1.5)
        
        # Extract metadata
        metadata = detection_result.metadata or {}
        architecture = metadata.get('architecture')
        quantization = metadata.get('quantization')
        context_length = metadata.get('context_length')
        
        return ModelInfo(
            format_type=detection_result.format_type,
            file_path=detection_result.file_path,
            file_size=file_size,
            estimated_memory=estimated_memory,
            architecture=architecture,
            quantization=quantization,
            context_length=context_length,
            metadata=metadata
        )
    
    def _create_fallback_chain(self, format_type: ModelFormat, primary_backend: str, 
                             hardware_info: HardwareInfo) -> List[str]:
        """Create fallback backend chain."""
        if not self.fallback_enabled:
            return []
        
        compatible_backends = self.get_backend_for_format(format_type)
        
        # Remove primary backend from fallbacks
        fallback_backends = [b for b in compatible_backends if b != primary_backend]
        
        # Limit to max attempts
        return fallback_backends[:self.max_fallback_attempts]
    
    def _generate_optimization_suggestions(self, model_info: ModelInfo, hardware_info: HardwareInfo, 
                                         backend_name: str) -> List[str]:
        """Generate optimization suggestions."""
        suggestions = []
        
        # Memory optimization
        if model_info.estimated_memory > hardware_info.total_ram * 0.8:
            suggestions.append("Model may exceed available RAM - consider using CPU-only mode")
            suggestions.append("Enable memory mapping if supported by backend")
        
        # GPU optimization
        if hardware_info.gpu_count > 0:
            suggestions.append("GPU acceleration available - ensure GPU layers are enabled")
            if model_info.estimated_memory > hardware_info.total_vram:
                suggestions.append("Model larger than VRAM - consider hybrid CPU/GPU loading")
        
        # Format-specific suggestions
        if model_info.format_type == ModelFormat.GGUF:
            suggestions.append("GGUF format supports efficient quantization")
        elif model_info.format_type == ModelFormat.SAFETENSORS:
            suggestions.append("Safetensors format provides fast and secure loading")
        
        return suggestions
    
    def _create_hardware_config(self, backend_name: str, hardware_info: HardwareInfo) -> Dict[str, Any]:
        """Create hardware configuration for the backend."""
        config = {
            'gpu_enabled': hardware_info.gpu_count > 0,
            'gpu_layers': -1 if hardware_info.gpu_count > 0 else 0,
            'threads': hardware_info.cpu_cores,
            'context_size': 4096,
            'batch_size': 512
        }
        
        # Backend-specific optimizations
        if backend_name == BackendType.CTRANSFORMERS.value:
            # For ctransformers, keep -1 for auto-detect when GPU is available
            if config['gpu_layers'] == -1:
                config['gpu_layers'] = -1  # Keep auto-detect
            else:
                config['gpu_layers'] = 0  # CPU only
        elif backend_name == BackendType.TRANSFORMERS.value:
            config['device'] = 'cuda' if hardware_info.gpu_count > 0 else 'cpu'
        
        return config
    
    def _calculate_loading_confidence(self, detection_result: FormatDetectionResult, 
                                    backend_name: str, model_info: ModelInfo, 
                                    hardware_info: HardwareInfo) -> float:
        """Calculate confidence in loading success."""
        # Base confidence from format detection
        confidence = detection_result.confidence
        
        # Adjust based on backend capability
        capability_score = self.assess_backend_capability(backend_name, model_info, hardware_info)
        confidence *= capability_score.total_score
        
        # Adjust based on memory requirements
        memory_ratio = model_info.estimated_memory / hardware_info.total_ram
        if memory_ratio > 0.9:
            confidence *= 0.5  # High memory usage reduces confidence
        elif memory_ratio > 0.7:
            confidence *= 0.8
        
        return min(confidence, 1.0)
    
    def update_performance_history(self, backend_name: str, load_time: float, success: bool):
        """Update performance and reliability history."""
        # Update performance history
        if backend_name not in self.performance_history:
            self.performance_history[backend_name] = []
        
        self.performance_history[backend_name].append(load_time)
        
        # Keep only recent history (last 20 attempts)
        if len(self.performance_history[backend_name]) > 20:
            self.performance_history[backend_name] = self.performance_history[backend_name][-20:]
        
        # Update reliability history
        if backend_name not in self.reliability_history:
            self.reliability_history[backend_name] = []
        
        self.reliability_history[backend_name].append(success)
        
        # Keep only recent history (last 50 attempts)
        if len(self.reliability_history[backend_name]) > 50:
            self.reliability_history[backend_name] = self.reliability_history[backend_name][-50:]
    
    def get_routing_statistics(self) -> Dict[str, Any]:
        """Get routing system statistics."""
        stats = {
            'backend_capabilities': {
                backend: list(caps) for backend, caps in self.backend_capabilities.items()
            },
            'format_mappings': {
                fmt.value: mappings for fmt, mappings in self.format_mappings.items()
            },
            'performance_history': {
                backend: {
                    'average_load_time': sum(times) / len(times) if times else 0,
                    'sample_count': len(times)
                }
                for backend, times in self.performance_history.items()
            },
            'reliability_history': {
                backend: {
                    'success_rate': sum(1 for s in successes if s) / len(successes) if successes else 0,
                    'sample_count': len(successes)
                }
                for backend, successes in self.reliability_history.items()
            },
            'configuration': {
                'fallback_enabled': self.fallback_enabled,
                'max_fallback_attempts': self.max_fallback_attempts,
                'performance_weight': self.performance_weight,
                'reliability_weight': self.reliability_weight,
                'compatibility_weight': self.compatibility_weight
            }
        }
        
        return stats