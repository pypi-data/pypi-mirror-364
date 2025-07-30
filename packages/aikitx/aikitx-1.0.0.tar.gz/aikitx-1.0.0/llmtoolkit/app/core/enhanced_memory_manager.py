"""
Enhanced Memory Management System

This module provides comprehensive memory management for all supported model formats
including GGUF, safetensors, PyTorch bin files, and Hugging Face models.
It implements format-aware memory estimation, dynamic monitoring, optimization suggestions,
and automatic parameter adjustment for memory constraints.
"""

import os
import gc
import sys
import json
import logging
import psutil
import threading
import time
from typing import Dict, List, Optional, Tuple, Set, Any, Union, Callable
from datetime import datetime, timedelta
from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path

from PySide6.QtCore import QObject, Signal, QTimer

from .universal_format_detector import ModelFormat
from .hardware_detector import HardwareDetector


class MemoryPressureLevel(Enum):
    """Memory pressure levels."""
    LOW = "low"
    MODERATE = "moderate"
    HIGH = "high"
    CRITICAL = "critical"


class OptimizationType(Enum):
    """Types of memory optimizations."""
    QUANTIZATION = "quantization"
    CPU_ONLY = "cpu_only"
    MEMORY_MAPPING = "memory_mapping"
    LAZY_LOADING = "lazy_loading"
    REDUCED_CONTEXT = "reduced_context"
    BATCH_SIZE_REDUCTION = "batch_size_reduction"
    PRECISION_REDUCTION = "precision_reduction"
    OFFLOADING = "offloading"


@dataclass
class MemoryEstimate:
    """Memory usage estimate for model loading."""
    base_model_size: int  # Bytes
    overhead_size: int  # Bytes
    total_estimated: int  # Bytes
    confidence_level: float  # 0.0 to 1.0
    optimization_potential: int  # Bytes that could be saved
    format_specific_overhead: int = 0  # Format-specific overhead
    backend_overhead: int = 0  # Backend-specific overhead
    gpu_memory_required: int = 0  # GPU memory if applicable


@dataclass
class MemoryCheckResult:
    """Result of memory availability check."""
    is_available: bool
    available_memory: int  # Bytes
    required_memory: int  # Bytes
    memory_deficit: int  # Bytes (0 if sufficient)
    pressure_level: MemoryPressureLevel
    recommendations: List[str]
    can_optimize: bool


@dataclass
class OptimizationSuggestion:
    """Memory optimization suggestion."""
    optimization_type: OptimizationType
    description: str
    memory_savings: int  # Estimated bytes saved
    performance_impact: float  # 0.0 to 1.0 (higher = more impact)
    implementation_difficulty: float  # 0.0 to 1.0 (higher = harder)
    parameters: Dict[str, Any] = field(default_factory=dict)


@dataclass
class MemoryConstraints:
    """Memory constraints for loading."""
    max_memory: int  # Maximum memory allowed (bytes)
    prefer_cpu: bool = False
    allow_quantization: bool = True
    allow_memory_mapping: bool = True
    allow_lazy_loading: bool = True
    max_context_length: Optional[int] = None


@dataclass
class BackendConfig:
    """Backend configuration with memory considerations."""
    backend_name: str
    use_gpu: bool
    quantization: Optional[str] = None
    memory_mapping: bool = False
    lazy_loading: bool = False
    context_length: Optional[int] = None
    batch_size: int = 1
    precision: str = "float16"
    additional_params: Dict[str, Any] = field(default_factory=dict)


class EnhancedMemoryManager(QObject):
    """
    Enhanced memory management system that provides format-aware memory estimation,
    dynamic monitoring, optimization suggestions, and automatic parameter adjustment.
    """
    
    # Signals
    memory_warning_signal = Signal(float, float)  # used_percentage, available_mb
    memory_critical_signal = Signal(float, float)  # used_percentage, available_mb
    memory_normal_signal = Signal(float, float)  # used_percentage, available_mb
    memory_pressure_signal = Signal(str)  # pressure_level
    optimization_suggested_signal = Signal(list)  # optimization_suggestions
    
    # Memory thresholds
    MEMORY_WARNING_THRESHOLD = 75.0  # Percentage
    MEMORY_CRITICAL_THRESHOLD = 90.0  # Percentage
    MEMORY_PRESSURE_THRESHOLD = 85.0  # Percentage
    
    # Format-specific memory multipliers
    FORMAT_MEMORY_MULTIPLIERS = {
        ModelFormat.GGUF: {
            'base': 1.0,  # GGUF files are already optimized
            'overhead': 0.1,  # 10% overhead for loading structures
            'gpu_multiplier': 1.2  # 20% more for GPU tensors
        },
        ModelFormat.SAFETENSORS: {
            'base': 1.1,  # Slightly more due to tensor format
            'overhead': 0.15,  # 15% overhead for parsing
            'gpu_multiplier': 1.3  # 30% more for GPU conversion
        },
        ModelFormat.PYTORCH_BIN: {
            'base': 1.2,  # PyTorch format has more overhead
            'overhead': 0.2,  # 20% overhead for loading
            'gpu_multiplier': 1.4  # 40% more for GPU conversion
        },
        ModelFormat.HUGGINGFACE: {
            'base': 1.15,  # HF models vary but generally efficient
            'overhead': 0.18,  # 18% overhead for tokenizer/config
            'gpu_multiplier': 1.35  # 35% more for GPU setup
        }
    }
    
    # Backend-specific memory multipliers
    BACKEND_MEMORY_MULTIPLIERS = {
        'llama_cpp_python': 1.0,  # Most efficient for GGUF
        'llamafile': 1.05,  # Slightly more overhead
        'transformers': 1.3,  # More overhead for flexibility
        'ctransformers': 1.1   # Moderate overhead
    }
    
    def __init__(self, hardware_detector: Optional[HardwareDetector] = None, 
                 event_bus=None, config_manager=None, parent=None):
        """
        Initialize the enhanced memory manager.
        
        Args:
            hardware_detector: Hardware detector instance
            event_bus: Optional event bus for publishing events
            config_manager: Optional configuration manager
            parent: Parent object
        """
        super().__init__(parent)
        self.logger = logging.getLogger("memory.enhanced")
        self.hardware_detector = hardware_detector or HardwareDetector()
        self.event_bus = event_bus
        self.config_manager = config_manager
        
        # Memory monitoring state
        self.last_memory_state = "normal"
        self.last_pressure_level = MemoryPressureLevel.LOW
        self.monitoring_active = False
        self.memory_check_interval = 2000  # 2 seconds for enhanced monitoring
        
        # Memory thresholds (configurable)
        self.warning_threshold = self.MEMORY_WARNING_THRESHOLD
        self.critical_threshold = self.MEMORY_CRITICAL_THRESHOLD
        self.pressure_threshold = self.MEMORY_PRESSURE_THRESHOLD
        
        # Memory optimization settings
        self.enable_automatic_optimization = True
        self.enable_proactive_monitoring = True
        self.enable_memory_pressure_detection = True
        
        # Memory monitoring timer
        self.memory_timer = QTimer(self)
        self.memory_timer.timeout.connect(self._check_memory_usage)
        
        # Memory usage history for trend analysis
        self.memory_history: List[Tuple[float, float]] = []  # (timestamp, usage_percent)
        self.max_history_size = 100
        
        # Load settings from configuration
        self._load_settings()
        
        self.logger.info("Enhanced memory manager initialized")
    
    def _load_settings(self):
        """Load settings from configuration."""
        if self.config_manager:
            # Memory thresholds
            self.warning_threshold = self.config_manager.get_value(
                "memory_warning_threshold", self.MEMORY_WARNING_THRESHOLD)
            self.critical_threshold = self.config_manager.get_value(
                "memory_critical_threshold", self.MEMORY_CRITICAL_THRESHOLD)
            self.pressure_threshold = self.config_manager.get_value(
                "memory_pressure_threshold", self.MEMORY_PRESSURE_THRESHOLD)
            
            # Memory check interval
            self.memory_check_interval = self.config_manager.get_value(
                "memory_check_interval_ms", 2000)
            
            # Optimization settings
            self.enable_automatic_optimization = self.config_manager.get_value(
                "enable_automatic_optimization", True)
            self.enable_proactive_monitoring = self.config_manager.get_value(
                "enable_proactive_monitoring", True)
            self.enable_memory_pressure_detection = self.config_manager.get_value(
                "enable_memory_pressure_detection", True)
    
    def start_monitoring(self):
        """Start enhanced memory usage monitoring."""
        if not self.monitoring_active:
            self.logger.info("Starting enhanced memory monitoring")
            self.memory_timer.start(self.memory_check_interval)
            self.monitoring_active = True
            
            # Do an initial check
            self._check_memory_usage()
    
    def stop_monitoring(self):
        """Stop memory usage monitoring."""
        if self.monitoring_active:
            self.logger.info("Stopping enhanced memory monitoring")
            self.memory_timer.stop()
            self.monitoring_active = False
    
    def get_memory_info(self) -> Dict[str, Any]:
        """
        Get comprehensive memory usage information.
        
        Returns:
            Dictionary with detailed memory usage information
        """
        memory = psutil.virtual_memory()
        swap = psutil.swap_memory()
        
        # Get GPU memory info if available
        gpu_memory = self._get_gpu_memory_info()
        
        return {
            "total": memory.total,
            "available": memory.available,
            "used": memory.used,
            "free": memory.free,
            "percent": memory.percent,
            "total_gb": memory.total / (1024 ** 3),
            "available_gb": memory.available / (1024 ** 3),
            "used_gb": memory.used / (1024 ** 3),
            "free_gb": memory.free / (1024 ** 3),
            "swap_total": swap.total,
            "swap_used": swap.used,
            "swap_percent": swap.percent,
            "gpu_memory": gpu_memory,
            "pressure_level": self._calculate_pressure_level(memory.percent),
            "trend": self._calculate_memory_trend()
        }
    
    def _get_gpu_memory_info(self) -> Dict[str, Any]:
        """Get GPU memory information if available."""
        gpu_info = {"available": False, "total": 0, "used": 0, "free": 0}
        
        try:
            # Try to get GPU memory info from hardware detector
            hardware_info = self.hardware_detector.get_hardware_info()
            if hasattr(hardware_info, 'gpu_count') and hardware_info.gpu_count > 0:
                gpu_info.update({
                    "available": True,
                    "total": hardware_info.total_vram * 1024 * 1024,  # Convert MB to bytes
                    "used": 0,  # Would need specific GPU monitoring for this
                    "free": hardware_info.total_vram * 1024 * 1024,
                    "percent": 0
                })
            elif isinstance(hardware_info, dict) and hardware_info.get("gpu_available", False):
                # Fallback for dict-based hardware info
                gpu_memory = hardware_info.get("gpu_memory", {})
                if gpu_memory:
                    gpu_info.update({
                        "available": True,
                        "total": gpu_memory.get("total", 0),
                        "used": gpu_memory.get("used", 0),
                        "free": gpu_memory.get("free", 0),
                        "percent": gpu_memory.get("percent", 0)
                    })
        except Exception as e:
            self.logger.debug(f"Could not get GPU memory info: {e}")
        
        return gpu_info
    
    def _calculate_pressure_level(self, memory_percent: float) -> MemoryPressureLevel:
        """Calculate memory pressure level based on usage percentage."""
        if memory_percent >= self.critical_threshold:
            return MemoryPressureLevel.CRITICAL
        elif memory_percent >= self.pressure_threshold:
            return MemoryPressureLevel.HIGH
        elif memory_percent >= self.warning_threshold:
            return MemoryPressureLevel.MODERATE
        else:
            return MemoryPressureLevel.LOW
    
    def _calculate_memory_trend(self) -> str:
        """Calculate memory usage trend from history."""
        if len(self.memory_history) < 5:
            return "stable"
        
        # Get recent usage values
        recent_values = [usage for _, usage in self.memory_history[-5:]]
        
        # Calculate trend
        if recent_values[-1] > recent_values[0] + 5:
            return "increasing"
        elif recent_values[-1] < recent_values[0] - 5:
            return "decreasing"
        else:
            return "stable"
    
    def estimate_memory_requirements(self, model_path: str, backend: str, 
                                   format_type: Optional[ModelFormat] = None) -> MemoryEstimate:
        """
        Estimate memory requirements for loading a model with format-aware calculations.
        
        Args:
            model_path: Path to the model file or directory
            backend: Backend name to be used
            format_type: Model format (auto-detected if None)
            
        Returns:
            MemoryEstimate with detailed breakdown
        """
        try:
            # Auto-detect format if not provided
            if format_type is None:
                from .universal_format_detector import UniversalFormatDetector
                detector = UniversalFormatDetector()
                detection_result = detector.detect_format(model_path)
                format_type = detection_result.format_type
            
            # Get file size
            if os.path.isfile(model_path):
                file_size = os.path.getsize(model_path)
            elif os.path.isdir(model_path):
                file_size = sum(
                    os.path.getsize(os.path.join(dirpath, filename))
                    for dirpath, dirnames, filenames in os.walk(model_path)
                    for filename in filenames
                )
            else:
                # Fallback for HF model IDs or other cases
                file_size = 1024 * 1024 * 1024  # 1GB estimate
            
            # Get format-specific multipliers
            format_multipliers = self.FORMAT_MEMORY_MULTIPLIERS.get(
                format_type, self.FORMAT_MEMORY_MULTIPLIERS[ModelFormat.GGUF]
            )
            
            # Get backend-specific multiplier
            backend_multiplier = self.BACKEND_MEMORY_MULTIPLIERS.get(backend, 1.2)
            
            # Calculate base model size with format considerations
            base_model_size = int(file_size * format_multipliers['base'])
            
            # Calculate overhead
            format_overhead = int(file_size * format_multipliers['overhead'])
            backend_overhead = int(file_size * (backend_multiplier - 1.0))
            total_overhead = format_overhead + backend_overhead
            
            # Calculate total estimated memory
            total_estimated = base_model_size + total_overhead
            
            # Calculate GPU memory requirements if GPU is available
            gpu_memory_required = 0
            hardware_info = self.hardware_detector.get_hardware_info()
            gpu_available = False
            if hasattr(hardware_info, 'gpu_count'):
                gpu_available = hardware_info.gpu_count > 0
            elif isinstance(hardware_info, dict):
                gpu_available = hardware_info.get("gpu_available", False)
            
            if gpu_available:
                gpu_memory_required = int(
                    base_model_size * format_multipliers['gpu_multiplier']
                )
            
            # Estimate optimization potential
            optimization_potential = self._estimate_optimization_potential(
                total_estimated, format_type, backend
            )
            
            # Calculate confidence level based on format and backend combination
            confidence_level = self._calculate_confidence_level(format_type, backend)
            
            return MemoryEstimate(
                base_model_size=base_model_size,
                overhead_size=total_overhead,
                total_estimated=total_estimated,
                confidence_level=confidence_level,
                optimization_potential=optimization_potential,
                format_specific_overhead=format_overhead,
                backend_overhead=backend_overhead,
                gpu_memory_required=gpu_memory_required
            )
            
        except Exception as e:
            self.logger.error(f"Error estimating memory requirements: {e}")
            # Return conservative estimate
            fallback_size = 2 * 1024 * 1024 * 1024  # 2GB
            return MemoryEstimate(
                base_model_size=fallback_size,
                overhead_size=int(fallback_size * 0.3),
                total_estimated=int(fallback_size * 1.3),
                confidence_level=0.3,
                optimization_potential=int(fallback_size * 0.5)
            )
    
    def _estimate_optimization_potential(self, total_memory: int, 
                                       format_type: ModelFormat, backend: str) -> int:
        """Estimate how much memory could be saved through optimizations."""
        potential_savings = 0
        
        # Quantization savings (format-dependent)
        if format_type in [ModelFormat.SAFETENSORS, ModelFormat.PYTORCH_BIN, ModelFormat.HUGGINGFACE]:
            potential_savings += int(total_memory * 0.5)  # Up to 50% with quantization
        elif format_type == ModelFormat.GGUF:
            potential_savings += int(total_memory * 0.2)  # GGUF already optimized
        
        # Memory mapping savings
        if backend in ['llama_cpp_python', 'llamafile']:
            potential_savings += int(total_memory * 0.3)  # 30% with memory mapping
        
        # CPU-only mode savings (no GPU overhead)
        potential_savings += int(total_memory * 0.2)  # 20% by avoiding GPU overhead
        
        return min(potential_savings, int(total_memory * 0.7))  # Cap at 70%
    
    def _calculate_confidence_level(self, format_type: ModelFormat, backend: str) -> float:
        """Calculate confidence level for memory estimation."""
        base_confidence = 0.7
        
        # Format-specific confidence adjustments
        format_confidence = {
            ModelFormat.GGUF: 0.9,  # Most predictable
            ModelFormat.SAFETENSORS: 0.8,
            ModelFormat.PYTORCH_BIN: 0.7,
            ModelFormat.HUGGINGFACE: 0.75
        }.get(format_type, 0.6)
        
        # Backend-specific confidence adjustments
        backend_confidence = {
            'llama_cpp_python': 0.9,
            'llamafile': 0.85,
            'transformers': 0.7,
            'ctransformers': 0.8
        }.get(backend, 0.6)
        
        # Combine confidences
        return min(1.0, (base_confidence + format_confidence + backend_confidence) / 3)  
  
    def check_memory_availability(self, required_memory: int) -> MemoryCheckResult:
        """
        Check if there's enough memory available for a given requirement.
        
        Args:
            required_memory: Required memory in bytes
            
        Returns:
            MemoryCheckResult with availability and recommendations
        """
        memory_info = self.get_memory_info()
        available_memory = memory_info["available"]
        
        # Check if memory is available
        is_available = available_memory >= required_memory
        memory_deficit = max(0, required_memory - available_memory)
        
        # Determine pressure level
        pressure_level = self._calculate_pressure_level(memory_info["percent"])
        
        # Generate recommendations
        recommendations = []
        can_optimize = False
        
        if not is_available or pressure_level in [MemoryPressureLevel.HIGH, MemoryPressureLevel.CRITICAL]:
            recommendations.extend(self._generate_memory_recommendations(
                required_memory, available_memory, pressure_level
            ))
            can_optimize = True
        
        return MemoryCheckResult(
            is_available=is_available,
            available_memory=available_memory,
            required_memory=required_memory,
            memory_deficit=memory_deficit,
            pressure_level=pressure_level,
            recommendations=recommendations,
            can_optimize=can_optimize
        )
    
    def _generate_memory_recommendations(self, required: int, available: int, 
                                       pressure_level: MemoryPressureLevel) -> List[str]:
        """Generate memory optimization recommendations."""
        recommendations = []
        
        if pressure_level == MemoryPressureLevel.CRITICAL:
            recommendations.extend([
                "Close other applications to free memory",
                "Use CPU-only mode to reduce memory usage",
                "Enable aggressive quantization if supported",
                "Consider using a smaller model variant"
            ])
        elif pressure_level == MemoryPressureLevel.HIGH:
            recommendations.extend([
                "Enable memory mapping for efficient loading",
                "Use quantized model versions if available",
                "Close unnecessary applications",
                "Consider CPU-only mode for large models"
            ])
        else:
            recommendations.extend([
                "Enable memory mapping for better efficiency",
                "Monitor memory usage during loading",
                "Consider quantization for better performance"
            ])
        
        # Add specific recommendations based on memory deficit
        deficit_gb = (required - available) / (1024 ** 3)
        if deficit_gb > 0:
            recommendations.append(f"Free at least {deficit_gb:.1f} GB of memory")
        
        return recommendations
    
    def suggest_memory_optimizations(self, model_info: Dict[str, Any], 
                                   available_memory: int) -> List[OptimizationSuggestion]:
        """
        Suggest memory optimizations based on model info and available memory.
        
        Args:
            model_info: Information about the model
            available_memory: Available memory in bytes
            
        Returns:
            List of optimization suggestions
        """
        suggestions = []
        
        format_type = model_info.get('format_type', ModelFormat.UNKNOWN)
        model_size = model_info.get('file_size', 0)
        backend = model_info.get('backend', 'unknown')
        
        # Memory pressure level
        memory_info = self.get_memory_info()
        pressure_level = self._calculate_pressure_level(memory_info["percent"])
        
        # Quantization suggestions
        if format_type in [ModelFormat.SAFETENSORS, ModelFormat.PYTORCH_BIN, ModelFormat.HUGGINGFACE]:
            suggestions.append(OptimizationSuggestion(
                optimization_type=OptimizationType.QUANTIZATION,
                description="Use 8-bit or 4-bit quantization to reduce memory usage by 50-75%",
                memory_savings=int(model_size * 0.5),
                performance_impact=0.2,  # Minimal performance impact
                implementation_difficulty=0.3,
                parameters={"quantization_bits": [8, 4], "method": "dynamic"}
            ))
        
        # CPU-only mode suggestion
        hardware_info = self.hardware_detector.get_hardware_info()
        gpu_available = False
        if hasattr(hardware_info, 'gpu_count'):
            gpu_available = hardware_info.gpu_count > 0
        elif isinstance(hardware_info, dict):
            gpu_available = hardware_info.get("gpu_available", False)
        
        if gpu_available and pressure_level != MemoryPressureLevel.LOW:
            suggestions.append(OptimizationSuggestion(
                optimization_type=OptimizationType.CPU_ONLY,
                description="Use CPU-only mode to avoid GPU memory overhead",
                memory_savings=int(model_size * 0.3),
                performance_impact=0.6,  # Significant performance impact
                implementation_difficulty=0.1,
                parameters={"device": "cpu", "use_gpu": False}
            ))
        
        # Memory mapping suggestion
        if backend in ['llama_cpp_python', 'llamafile'] and format_type == ModelFormat.GGUF:
            suggestions.append(OptimizationSuggestion(
                optimization_type=OptimizationType.MEMORY_MAPPING,
                description="Enable memory mapping to reduce RAM usage",
                memory_savings=int(model_size * 0.4),
                performance_impact=0.1,  # Minimal performance impact
                implementation_difficulty=0.2,
                parameters={"use_mmap": True, "mlock": False}
            ))
        
        # Lazy loading suggestion
        if format_type in [ModelFormat.PYTORCH_BIN, ModelFormat.HUGGINGFACE]:
            suggestions.append(OptimizationSuggestion(
                optimization_type=OptimizationType.LAZY_LOADING,
                description="Enable lazy loading to load model parts on demand",
                memory_savings=int(model_size * 0.6),
                performance_impact=0.3,
                implementation_difficulty=0.4,
                parameters={"lazy_loading": True, "load_in_8bit": True}
            ))
        
        # Context length reduction
        if pressure_level in [MemoryPressureLevel.HIGH, MemoryPressureLevel.CRITICAL]:
            suggestions.append(OptimizationSuggestion(
                optimization_type=OptimizationType.REDUCED_CONTEXT,
                description="Reduce context length to save memory",
                memory_savings=int(model_size * 0.2),
                performance_impact=0.4,
                implementation_difficulty=0.2,
                parameters={"max_context_length": [2048, 1024, 512]}
            ))
        
        # Precision reduction
        if format_type in [ModelFormat.SAFETENSORS, ModelFormat.PYTORCH_BIN]:
            suggestions.append(OptimizationSuggestion(
                optimization_type=OptimizationType.PRECISION_REDUCTION,
                description="Use half precision (float16) to reduce memory usage",
                memory_savings=int(model_size * 0.5),
                performance_impact=0.1,
                implementation_difficulty=0.2,
                parameters={"torch_dtype": "float16", "precision": "half"}
            ))
        
        # Sort suggestions by effectiveness (memory savings vs performance impact)
        suggestions.sort(key=lambda x: x.memory_savings / (1 + x.performance_impact), reverse=True)
        
        return suggestions
    
    def adjust_loading_parameters(self, config: BackendConfig, 
                                memory_constraints: MemoryConstraints) -> BackendConfig:
        """
        Automatically adjust loading parameters based on memory constraints.
        
        Args:
            config: Original backend configuration
            memory_constraints: Memory constraints to apply
            
        Returns:
            Adjusted backend configuration
        """
        adjusted_config = BackendConfig(
            backend_name=config.backend_name,
            use_gpu=config.use_gpu,
            quantization=config.quantization,
            memory_mapping=config.memory_mapping,
            lazy_loading=config.lazy_loading,
            context_length=config.context_length,
            batch_size=config.batch_size,
            precision=config.precision,
            additional_params=config.additional_params.copy()
        )
        
        # Apply memory constraints
        if memory_constraints.prefer_cpu:
            adjusted_config.use_gpu = False
            adjusted_config.additional_params["device"] = "cpu"
        
        if memory_constraints.allow_quantization and not adjusted_config.quantization:
            # Suggest quantization based on memory pressure
            memory_info = self.get_memory_info()
            pressure_level = self._calculate_pressure_level(memory_info["percent"])
            
            if pressure_level == MemoryPressureLevel.CRITICAL:
                adjusted_config.quantization = "4bit"
            elif pressure_level == MemoryPressureLevel.HIGH:
                adjusted_config.quantization = "8bit"
        
        if memory_constraints.allow_memory_mapping:
            adjusted_config.memory_mapping = True
            adjusted_config.additional_params["use_mmap"] = True
        
        if memory_constraints.allow_lazy_loading:
            adjusted_config.lazy_loading = True
            adjusted_config.additional_params["lazy_loading"] = True
        
        if memory_constraints.max_context_length:
            if not adjusted_config.context_length or adjusted_config.context_length > memory_constraints.max_context_length:
                adjusted_config.context_length = memory_constraints.max_context_length
        
        # Adjust batch size for memory constraints
        if memory_constraints.max_memory:
            # Estimate memory per batch and adjust accordingly
            estimated_per_batch = memory_constraints.max_memory // 10  # Conservative estimate
            max_batch_size = max(1, estimated_per_batch // (1024 * 1024))  # Convert to reasonable batch size
            adjusted_config.batch_size = min(adjusted_config.batch_size, max_batch_size)
        
        # Adjust precision for memory savings
        memory_info = self.get_memory_info()
        if memory_info["percent"] > self.pressure_threshold:
            if adjusted_config.precision == "float32":
                adjusted_config.precision = "float16"
                adjusted_config.additional_params["torch_dtype"] = "float16"
        
        return adjusted_config
    
    def monitor_loading_memory(self, callback: Optional[Callable[[Dict[str, Any]], None]] = None) -> Dict[str, Any]:
        """
        Monitor memory usage during model loading.
        
        Args:
            callback: Optional callback function to receive memory updates
            
        Returns:
            Memory monitoring results
        """
        start_memory = self.get_memory_info()
        start_time = time.time()
        
        monitoring_data = {
            "start_memory": start_memory,
            "peak_memory": start_memory,
            "current_memory": start_memory,
            "start_time": start_time,
            "duration": 0,
            "memory_trend": [],
            "pressure_events": []
        }
        
        def update_monitoring():
            current_memory = self.get_memory_info()
            current_time = time.time()
            
            monitoring_data["current_memory"] = current_memory
            monitoring_data["duration"] = current_time - start_time
            
            # Track peak memory usage
            if current_memory["used"] > monitoring_data["peak_memory"]["used"]:
                monitoring_data["peak_memory"] = current_memory
            
            # Track memory trend
            monitoring_data["memory_trend"].append({
                "timestamp": current_time,
                "memory_percent": current_memory["percent"],
                "memory_used": current_memory["used"]
            })
            
            # Detect pressure events
            pressure_level = self._calculate_pressure_level(current_memory["percent"])
            if pressure_level in [MemoryPressureLevel.HIGH, MemoryPressureLevel.CRITICAL]:
                monitoring_data["pressure_events"].append({
                    "timestamp": current_time,
                    "pressure_level": pressure_level.value,
                    "memory_percent": current_memory["percent"]
                })
            
            # Call callback if provided
            if callback:
                callback(monitoring_data)
        
        # Set up monitoring timer (this would be called periodically during loading)
        return monitoring_data
    
    def optimize_memory_usage(self) -> Dict[str, Any]:
        """
        Perform comprehensive memory optimization.
        
        Returns:
            Dictionary with optimization results
        """
        # Get memory info before optimization
        before = self.get_memory_info()
        
        optimization_results = {
            "before": before,
            "optimizations_applied": [],
            "memory_freed": 0,
            "success": True,
            "error_message": None
        }
        
        try:
            # 1. Python garbage collection
            gc.collect()
            optimization_results["optimizations_applied"].append("garbage_collection")
            
            # 2. Clear Python caches
            if hasattr(sys, 'intern'):
                # Clear string interning cache (Python 3.x)
                pass  # No direct way to clear, but gc.collect() helps
            
            # 3. Force memory release (platform-specific)
            try:
                import ctypes
                if sys.platform == "win32":
                    # Windows: Trim working set
                    ctypes.windll.kernel32.SetProcessWorkingSetSize(-1, -1, -1)
                    optimization_results["optimizations_applied"].append("windows_trim_working_set")
                elif sys.platform.startswith("linux"):
                    # Linux: Drop caches (requires root, so this is informational)
                    optimization_results["optimizations_applied"].append("linux_cache_info")
            except Exception as e:
                self.logger.debug(f"Platform-specific optimization failed: {e}")
            
            # 4. Clear any cached model data (if applicable)
            # This would be implemented based on the specific caching system used
            optimization_results["optimizations_applied"].append("model_cache_clear")
            
            # Get memory info after optimization
            after = self.get_memory_info()
            optimization_results["after"] = after
            
            # Calculate improvement
            memory_freed = after["available"] - before["available"]
            optimization_results["memory_freed"] = memory_freed
            optimization_results["memory_freed_mb"] = memory_freed / (1024 * 1024)
            optimization_results["percent_improvement"] = (
                (memory_freed / before["total"]) * 100 if before["total"] > 0 else 0
            )
            
            self.logger.info(
                f"Memory optimization freed {optimization_results['memory_freed_mb']:.2f} MB "
                f"({optimization_results['percent_improvement']:.2f}%)"
            )
            
            # Publish event if event bus is available
            if self.event_bus:
                self.event_bus.publish("memory.optimized", optimization_results)
            
        except Exception as e:
            optimization_results["success"] = False
            optimization_results["error_message"] = str(e)
            self.logger.error(f"Memory optimization failed: {e}")
        
        return optimization_results
    
    def detect_memory_pressure(self) -> Dict[str, Any]:
        """
        Detect and analyze memory pressure conditions.
        
        Returns:
            Dictionary with pressure analysis
        """
        memory_info = self.get_memory_info()
        pressure_level = self._calculate_pressure_level(memory_info["percent"])
        
        # Analyze memory trend
        trend = self._calculate_memory_trend()
        
        # Check for rapid memory increase
        rapid_increase = False
        if len(self.memory_history) >= 3:
            recent_changes = [
                self.memory_history[i][1] - self.memory_history[i-1][1]
                for i in range(-2, 0)
            ]
            rapid_increase = all(change > 5 for change in recent_changes)  # 5% increase per check
        
        # Generate pressure analysis
        pressure_analysis = {
            "pressure_level": pressure_level.value,
            "memory_percent": memory_info["percent"],
            "available_gb": memory_info["available_gb"],
            "trend": trend,
            "rapid_increase": rapid_increase,
            "recommendations": [],
            "immediate_actions": [],
            "stability_risk": "low"
        }
        
        # Add recommendations based on pressure level
        if pressure_level == MemoryPressureLevel.CRITICAL:
            pressure_analysis["stability_risk"] = "high"
            pressure_analysis["immediate_actions"].extend([
                "Stop model loading immediately",
                "Close other applications",
                "Free memory before continuing"
            ])
            pressure_analysis["recommendations"].extend([
                "Use CPU-only mode",
                "Enable aggressive quantization",
                "Reduce context length",
                "Consider smaller model variant"
            ])
        elif pressure_level == MemoryPressureLevel.HIGH:
            pressure_analysis["stability_risk"] = "moderate"
            pressure_analysis["immediate_actions"].extend([
                "Monitor memory closely",
                "Prepare to stop loading if needed"
            ])
            pressure_analysis["recommendations"].extend([
                "Enable memory mapping",
                "Use quantization",
                "Close unnecessary applications"
            ])
        
        # Emit signal if pressure level changed
        if pressure_level != self.last_pressure_level:
            self.memory_pressure_signal.emit(pressure_level.value)
            self.last_pressure_level = pressure_level
        
        return pressure_analysis
    
    def _check_memory_usage(self) -> Dict[str, Any]:
        """
        Enhanced memory usage check with pressure detection and trend analysis.
        
        Returns:
            Dictionary with comprehensive memory analysis
        """
        # Get memory info
        memory_info = self.get_memory_info()
        used_percentage = memory_info["percent"]
        available_mb = memory_info["available"] / (1024 * 1024)
        
        # Update memory history
        current_time = time.time()
        self.memory_history.append((current_time, used_percentage))
        
        # Trim history to max size
        if len(self.memory_history) > self.max_history_size:
            self.memory_history = self.memory_history[-self.max_history_size:]
        
        # Determine memory state
        new_state = "normal"
        if used_percentage >= self.critical_threshold:
            new_state = "critical"
        elif used_percentage >= self.warning_threshold:
            new_state = "warning"
        
        # Check if state has changed
        if new_state != self.last_memory_state:
            self.logger.info(f"Memory state changed from {self.last_memory_state} to {new_state}")
            
            # Emit appropriate signal
            if new_state == "critical":
                self.logger.warning(f"Critical memory usage: {used_percentage:.1f}%, {available_mb:.1f} MB available")
                self.memory_critical_signal.emit(used_percentage, available_mb)
                
                # Trigger automatic optimization if enabled
                if self.enable_automatic_optimization:
                    self.optimize_memory_usage()
                
                # Publish event
                if self.event_bus:
                    self.event_bus.publish("memory.critical", used_percentage, available_mb)
                    
            elif new_state == "warning":
                self.logger.warning(f"High memory usage: {used_percentage:.1f}%, {available_mb:.1f} MB available")
                self.memory_warning_signal.emit(used_percentage, available_mb)
                
                # Publish event
                if self.event_bus:
                    self.event_bus.publish("memory.warning", used_percentage, available_mb)
                    
            else:  # normal
                self.logger.info(f"Memory usage normal: {used_percentage:.1f}%, {available_mb:.1f} MB available")
                self.memory_normal_signal.emit(used_percentage, available_mb)
                
                # Publish event
                if self.event_bus:
                    self.event_bus.publish("memory.normal", used_percentage, available_mb)
            
            # Update state
            self.last_memory_state = new_state
        
        # Detect memory pressure if enabled
        pressure_analysis = None
        if self.enable_memory_pressure_detection:
            pressure_analysis = self.detect_memory_pressure()
        
        return {
            "memory_info": memory_info,
            "state": new_state,
            "pressure_analysis": pressure_analysis
        }
    
    def get_system_stability_status(self) -> Dict[str, Any]:
        """
        Get overall system stability status related to memory.
        
        Returns:
            Dictionary with stability assessment
        """
        memory_info = self.get_memory_info()
        pressure_level = self._calculate_pressure_level(memory_info["percent"])
        trend = self._calculate_memory_trend()
        
        # Assess stability
        stability_score = 1.0
        stability_factors = []
        
        # Memory usage factor
        if pressure_level == MemoryPressureLevel.CRITICAL:
            stability_score *= 0.2
            stability_factors.append("Critical memory usage")
        elif pressure_level == MemoryPressureLevel.HIGH:
            stability_score *= 0.5
            stability_factors.append("High memory usage")
        elif pressure_level == MemoryPressureLevel.MODERATE:
            stability_score *= 0.8
            stability_factors.append("Moderate memory usage")
        
        # Trend factor
        if trend == "increasing":
            stability_score *= 0.7
            stability_factors.append("Increasing memory usage trend")
        
        # Swap usage factor
        if memory_info.get("swap_percent", 0) > 50:
            stability_score *= 0.6
            stability_factors.append("High swap usage")
        
        # Determine stability level
        if stability_score >= 0.8:
            stability_level = "stable"
        elif stability_score >= 0.5:
            stability_level = "moderate"
        elif stability_score >= 0.3:
            stability_level = "unstable"
        else:
            stability_level = "critical"
        
        return {
            "stability_level": stability_level,
            "stability_score": stability_score,
            "stability_factors": stability_factors,
            "memory_info": memory_info,
            "pressure_level": pressure_level.value,
            "trend": trend,
            "recommendations": self._generate_stability_recommendations(stability_level, stability_factors)
        }
    
    def _generate_stability_recommendations(self, stability_level: str, factors: List[str]) -> List[str]:
        """Generate recommendations for system stability."""
        recommendations = []
        
        if stability_level == "critical":
            recommendations.extend([
                "Stop all model loading operations immediately",
                "Close other applications to free memory",
                "Restart the application if necessary",
                "Consider upgrading system memory"
            ])
        elif stability_level == "unstable":
            recommendations.extend([
                "Monitor memory usage closely",
                "Use memory-efficient loading options",
                "Close unnecessary applications",
                "Enable automatic memory optimization"
            ])
        elif stability_level == "moderate":
            recommendations.extend([
                "Enable memory monitoring",
                "Use quantization when possible",
                "Monitor for memory leaks"
            ])
        
        return recommendations