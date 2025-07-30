"""
Enhanced Backend Manager with Routing System Integration

This module provides an enhanced BackendManager that integrates with the Backend Routing System
for intelligent backend selection based on model format and hardware capabilities.
"""

import logging
import time
from typing import Dict, List, Optional, Tuple, Any, Callable
from dataclasses import dataclass, field
from pathlib import Path

from .backend_manager import BackendManager, BackendStatus
from .backend_routing_system import BackendRoutingSystem, LoadingPlan, FallbackAttempt, ModelInfo
from .universal_format_detector import ModelFormat
from .model_backends import (
    BackendType, BackendConfig, HardwareInfo, LoadingResult, 
    GenerationConfig, ModelBackend, BackendRegistry, backend_registry,
    BackendError, InstallationError, HardwareError, ModelLoadingError
)
from .hardware_detector import HardwareDetector
from .monitoring import monitoring_manager
from .logging_config import log_with_context, log_performance


@dataclass
class EnhancedLoadingResult(LoadingResult):
    """Enhanced loading result with routing information."""
    format_type: ModelFormat = ModelFormat.UNKNOWN
    fallback_attempts: List[FallbackAttempt] = field(default_factory=list)
    optimization_applied: List[str] = field(default_factory=list)
    routing_confidence: float = 0.0
    loading_plan: Optional[LoadingPlan] = None


class EnhancedBackendManager(BackendManager):
    """
    Enhanced backend manager with intelligent routing system integration.
    
    This class extends the base BackendManager to include:
    - Automatic format detection and backend routing
    - Intelligent backend selection based on model characteristics
    - Enhanced fallback logic with format awareness
    - Performance tracking and optimization suggestions
    """
    
    def __init__(self, hardware_detector: Optional[HardwareDetector] = None):
        """
        Initialize the enhanced backend manager.
        
        Args:
            hardware_detector: Hardware detector instance (creates new if None)
        """
        super().__init__(hardware_detector)
        
        # Initialize routing system
        self.routing_system = BackendRoutingSystem(self.hardware_detector)
        
        # Enhanced tracking
        self.loading_plans: Dict[str, LoadingPlan] = {}  # model_path -> LoadingPlan
        self.format_cache: Dict[str, ModelFormat] = {}  # model_path -> format
        
        self.logger.info("Enhanced backend manager initialized with routing system")
    
    def load_model_with_routing(self, model_path: str, preferred_backend: Optional[str] = None, 
                              **kwargs) -> EnhancedLoadingResult:
        """
        Load a model using intelligent routing system.
        
        Args:
            model_path: Path to model file/directory or HF model ID
            preferred_backend: Preferred backend name (optional)
            **kwargs: Additional arguments for model loading
            
        Returns:
            EnhancedLoadingResult with detailed routing information
        """
        self.logger.info(f"Loading model with routing: {model_path}")
        
        try:
            # Create loading plan using routing system
            loading_plan = self.routing_system.route_model_loading(model_path, preferred_backend)
            self.loading_plans[model_path] = loading_plan
            
            self.logger.info(
                f"Created loading plan: primary={loading_plan.primary_backend}, "
                f"fallbacks={loading_plan.fallback_backends}, "
                f"format={loading_plan.format_type.value}, "
                f"confidence={loading_plan.confidence:.3f}"
            )
            
            # Cache format detection result
            self.format_cache[model_path] = loading_plan.format_type
            
            # Apply optimization suggestions
            optimization_applied = self._apply_optimizations(loading_plan, kwargs)
            
            # Try primary backend first
            fallback_attempts = []
            backends_to_try = [loading_plan.primary_backend] + loading_plan.fallback_backends
            
            for i, backend_name in enumerate(backends_to_try):
                is_fallback = i > 0
                
                if is_fallback:
                    self.logger.info(f"Attempting fallback to backend: {backend_name}")
                    if self.on_fallback_triggered:
                        prev_backend = backends_to_try[i-1]
                        self.on_fallback_triggered(prev_backend, backend_name, "Primary backend failed")
                
                # Update progress
                if self.on_loading_progress:
                    progress = 20 + (i * 60 // len(backends_to_try))
                    self.on_loading_progress(f"Trying {backend_name}...", progress)
                
                # Attempt to load with this backend
                attempt_start = time.time()
                result = self._attempt_backend_loading(
                    backend_name, model_path, loading_plan, **kwargs
                )
                attempt_time = time.time() - attempt_start
                
                # Record fallback attempt
                fallback_attempt = FallbackAttempt(
                    backend_name=backend_name,
                    attempt_time=attempt_start,
                    success=result.success,
                    error_message=result.error_message,
                    load_time=attempt_time
                )
                fallback_attempts.append(fallback_attempt)
                
                # Update routing system performance history
                self.routing_system.update_performance_history(
                    backend_name, attempt_time, result.success
                )
                
                if result.success:
                    # Success! Create enhanced result
                    enhanced_result = EnhancedLoadingResult(
                        success=True,
                        backend_used=result.backend_used,
                        hardware_used=result.hardware_used,
                        load_time=result.load_time,
                        memory_usage=result.memory_usage,
                        error_message=None,
                        model_info=result.model_info,
                        format_type=loading_plan.format_type,
                        fallback_attempts=fallback_attempts,
                        optimization_applied=optimization_applied,
                        routing_confidence=loading_plan.confidence,
                        loading_plan=loading_plan
                    )
                    
                    self.logger.info(
                        f"Successfully loaded model with {backend_name} "
                        f"(format: {loading_plan.format_type.value}, "
                        f"attempts: {len(fallback_attempts)}, "
                        f"load_time: {result.load_time:.2f}s)"
                    )
                    
                    return enhanced_result
                else:
                    self.logger.warning(
                        f"Backend {backend_name} failed to load model: {result.error_message}"
                    )
            
            # All backends failed
            error_summary = self._create_failure_summary(fallback_attempts, loading_plan)
            
            return EnhancedLoadingResult(
                success=False,
                backend_used="none",
                hardware_used="none",
                load_time=0.0,
                memory_usage=0,
                error_message=error_summary,
                model_info={},
                format_type=loading_plan.format_type,
                fallback_attempts=fallback_attempts,
                optimization_applied=optimization_applied,
                routing_confidence=loading_plan.confidence,
                loading_plan=loading_plan
            )
            
        except Exception as e:
            self.logger.error(f"Error in routing-based model loading: {e}")
            return EnhancedLoadingResult(
                success=False,
                backend_used="none",
                hardware_used="none",
                load_time=0.0,
                memory_usage=0,
                error_message=f"Routing system error: {e}",
                model_info={},
                format_type=ModelFormat.UNKNOWN,
                fallback_attempts=[],
                optimization_applied=[],
                routing_confidence=0.0,
                loading_plan=None
            )
    
    def _attempt_backend_loading(self, backend_name: str, model_path: str, 
                               loading_plan: LoadingPlan, **kwargs) -> LoadingResult:
        """Attempt to load model with a specific backend."""
        try:
            # Check if backend is available
            if backend_name not in self.get_available_backends():
                return LoadingResult(
                    success=False,
                    backend_used=backend_name,
                    hardware_used="none",
                    load_time=0.0,
                    error_message=f"Backend not available: {backend_name}"
                )
            
            # Apply hardware configuration from loading plan
            if backend_name in self.configs:
                config = self.configs[backend_name]
                hw_config = loading_plan.hardware_config
                
                # Update config with routing recommendations
                config.gpu_enabled = hw_config.get('gpu_enabled', config.gpu_enabled)
                config.gpu_layers = hw_config.get('gpu_layers', config.gpu_layers)
                config.threads = hw_config.get('threads', config.threads)
                config.context_size = hw_config.get('context_size', config.context_size)
                config.batch_size = hw_config.get('batch_size', config.batch_size)
            
            # Get or create backend instance
            backend = self._get_backend_instance(backend_name)
            
            # Update backend status
            status = self.backend_status[backend_name]
            status.load_attempts += 1
            
            # Attempt to load the model
            start_time = time.time()
            
            # Handle different model formats appropriately
            if loading_plan.format_type == ModelFormat.HUGGINGFACE:
                # For HF models, we might need to handle model ID differently
                result = backend.load_model(model_path, **kwargs)
            else:
                # For file-based models, validate path first
                if not Path(model_path).exists():
                    return LoadingResult(
                        success=False,
                        backend_used=backend_name,
                        hardware_used="none",
                        load_time=0.0,
                        error_message=f"Model file does not exist: {model_path}"
                    )
                result = backend.load_model(model_path, **kwargs)
            
            load_time = time.time() - start_time
            
            if result.success:
                # Update success tracking
                status.success_count += 1
                status.average_load_time = (
                    status.average_load_time * (status.success_count - 1) + load_time
                ) / status.success_count
                
                # Set as current backend
                if self.current_backend and self.current_backend != backend:
                    self._unload_current_model()
                
                self.current_backend = backend
                self.current_model_path = model_path
                
                # Notify about backend change
                if self.on_backend_changed:
                    self.on_backend_changed(backend_name, model_path)
            else:
                status.failure_count += 1
            
            return result
            
        except Exception as e:
            # Update failure tracking
            if backend_name in self.backend_status:
                self.backend_status[backend_name].failure_count += 1
            
            return LoadingResult(
                success=False,
                backend_used=backend_name,
                hardware_used="none",
                load_time=0.0,
                error_message=f"Backend error: {e}"
            )
    
    def _apply_optimizations(self, loading_plan: LoadingPlan, kwargs: Dict[str, Any]) -> List[str]:
        """Apply optimization suggestions from the loading plan."""
        applied_optimizations = []
        
        for suggestion in loading_plan.optimization_suggestions:
            if "GPU acceleration" in suggestion and "gpu_layers" not in kwargs:
                kwargs["gpu_layers"] = loading_plan.hardware_config.get("gpu_layers", -1)
                applied_optimizations.append("Enabled GPU acceleration")
            
            elif "memory mapping" in suggestion and "use_mmap" not in kwargs:
                kwargs["use_mmap"] = True
                applied_optimizations.append("Enabled memory mapping")
            
            elif "quantization" in suggestion and "quantization" not in kwargs:
                # This would depend on backend support
                applied_optimizations.append("Quantization recommended (manual configuration needed)")
            
            elif "CPU-only mode" in suggestion:
                kwargs["gpu_layers"] = 0
                applied_optimizations.append("Forced CPU-only mode due to memory constraints")
        
        return applied_optimizations
    
    def _create_failure_summary(self, fallback_attempts: List[FallbackAttempt], 
                              loading_plan: LoadingPlan) -> str:
        """Create a comprehensive failure summary."""
        summary_parts = [
            f"Failed to load {loading_plan.format_type.value} model with all available backends."
        ]
        
        # Add attempt details
        for attempt in fallback_attempts:
            summary_parts.append(
                f"- {attempt.backend_name}: {attempt.error_message}"
            )
        
        # Add suggestions
        if loading_plan.optimization_suggestions:
            summary_parts.append("\nSuggestions:")
            for suggestion in loading_plan.optimization_suggestions:
                summary_parts.append(f"- {suggestion}")
        
        return "\n".join(summary_parts)
    
    def get_model_format(self, model_path: str) -> Optional[ModelFormat]:
        """Get the detected format for a model."""
        return self.format_cache.get(model_path)
    
    def get_loading_plan(self, model_path: str) -> Optional[LoadingPlan]:
        """Get the loading plan for a model."""
        return self.loading_plans.get(model_path)
    
    def get_backend_recommendations(self, model_path: str) -> Dict[str, Any]:
        """Get backend recommendations for a model."""
        try:
            loading_plan = self.routing_system.route_model_loading(model_path)
            
            # Get capability scores for all compatible backends
            compatible_backends = self.routing_system.get_backend_for_format(loading_plan.format_type)
            hardware_info = self.hardware_detector.get_hardware_info()
            
            recommendations = {}
            for backend_name in compatible_backends:
                capability_score = self.routing_system.assess_backend_capability(
                    backend_name, loading_plan.model_info, hardware_info
                )
                recommendations[backend_name] = {
                    'total_score': capability_score.total_score,
                    'format_compatibility': capability_score.format_compatibility,
                    'hardware_compatibility': capability_score.hardware_compatibility,
                    'performance_score': capability_score.performance_score,
                    'reliability_score': capability_score.reliability_score,
                    'capabilities': [cap.value for cap in capability_score.capabilities],
                    'limitations': capability_score.limitations,
                    'recommendations': capability_score.recommendations
                }
            
            return {
                'format_type': loading_plan.format_type.value,
                'recommended_backend': loading_plan.primary_backend,
                'fallback_backends': loading_plan.fallback_backends,
                'backend_scores': recommendations,
                'optimization_suggestions': loading_plan.optimization_suggestions,
                'confidence': loading_plan.confidence
            }
            
        except Exception as e:
            self.logger.error(f"Error getting backend recommendations: {e}")
            return {'error': str(e)}
    
    def get_routing_statistics(self) -> Dict[str, Any]:
        """Get comprehensive routing and backend statistics."""
        base_stats = self.get_statistics()
        routing_stats = self.routing_system.get_routing_statistics()
        
        return {
            'backend_manager': base_stats,
            'routing_system': routing_stats,
            'format_cache': {
                path: fmt.value for path, fmt in self.format_cache.items()
            },
            'active_loading_plans': len(self.loading_plans)
        }
    
    def clear_cache(self):
        """Clear routing caches."""
        self.format_cache.clear()
        self.loading_plans.clear()
        self.logger.info("Cleared routing caches")
    
    # Override the original load_model method to use routing by default
    def load_model(self, model_path: str, backend_name: Optional[str] = None, 
                  use_routing: bool = True, **kwargs) -> LoadingResult:
        """
        Load a model with optional routing system integration.
        
        Args:
            model_path: Path to the model file
            backend_name: Specific backend to use (None for auto-selection)
            use_routing: Whether to use the routing system (default: True)
            **kwargs: Additional arguments for model loading
            
        Returns:
            LoadingResult (or EnhancedLoadingResult if using routing)
        """
        if use_routing:
            return self.load_model_with_routing(model_path, backend_name, **kwargs)
        else:
            # Fall back to original implementation
            return super().load_model(model_path, backend_name, **kwargs)