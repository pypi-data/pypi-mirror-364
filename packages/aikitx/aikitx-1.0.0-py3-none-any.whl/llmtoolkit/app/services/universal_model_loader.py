"""
Universal Model Loader Service

This service integrates all components into a cohesive multi-format loading system
that handles GGUF, safetensors, PyTorch bin files, and Hugging Face models through
intelligent backend selection and comprehensive error handling.

Requirements addressed: 1.1, 1.2, 1.5, 1.6, 2.6
"""

import logging
import time
import asyncio
from pathlib import Path
from typing import Dict, Any, Optional, List, Callable, Union, Tuple
from dataclasses import dataclass, field
from enum import Enum

from PySide6.QtCore import QObject, Signal, QThread, QTimer, QMutex, QMutexLocker

from ..core.universal_format_detector import (
    UniversalFormatDetector, ModelFormat, FormatDetectionResult
)
from ..core.backend_routing_system import (
    BackendRoutingSystem, LoadingPlan, ModelInfo
)
from ..core.enhanced_backend_manager import (
    EnhancedBackendManager, EnhancedLoadingResult
)
from ..core.enhanced_memory_manager import (
    EnhancedMemoryManager, MemoryCheckResult, MemoryConstraints
)
from ..core.enhanced_error_reporting import (
    EnhancedErrorReportingEngine, ErrorAnalysis, LoadingContext
)
from ..core.universal_metadata_extractor import (
    UniversalMetadataExtractor, UnifiedMetadata
)
from ..core.universal_events import (
    UniversalEventPublisher, UniversalLoadingProgress, UniversalModelInfo,
    LoadingStage, UniversalEventType
)
from ..core.hardware_detector import HardwareDetector
from ..core.monitoring import monitoring_manager
from .huggingface_integration import HuggingFaceIntegration


# LoadingStage and UniversalLoadingProgress are imported from universal_events


@dataclass
class UniversalLoadingResult:
    """Comprehensive result of universal model loading."""
    success: bool
    model_path: str
    format_type: ModelFormat
    backend_used: str
    hardware_used: str
    load_time: float
    memory_usage: int
    metadata: UnifiedMetadata
    loading_plan: LoadingPlan
    error_analysis: Optional[ErrorAnalysis] = None
    optimization_applied: List[str] = field(default_factory=list)
    fallback_attempts: List[str] = field(default_factory=list)
    warnings: List[str] = field(default_factory=list)
    performance_metrics: Dict[str, Any] = field(default_factory=dict)


class ModelLoadingWorker(QThread):
    """Worker thread for model loading to prevent UI freezing."""
    
    # Signals
    loading_progress = Signal(UniversalLoadingProgress)
    loading_completed = Signal(UniversalLoadingResult)
    loading_failed = Signal(str, object)  # error_message, error_analysis
    
    def __init__(self, loader, model_path: str, preferred_backend: Optional[str] = None,
                 memory_constraints: Optional[MemoryConstraints] = None, **kwargs):
        super().__init__()
        self.loader = loader
        self.model_path = model_path
        self.preferred_backend = preferred_backend
        self.memory_constraints = memory_constraints
        self.kwargs = kwargs
        self._cancelled = False
    
    def run(self):
        """Run the model loading in background thread."""
        try:
            # Execute loading pipeline
            result = self.loader._execute_loading_pipeline_sync(
                self.model_path, self.preferred_backend, self.memory_constraints, **self.kwargs
            )
            
            if not self._cancelled:
                self.loading_completed.emit(result)
        except Exception as e:
            if not self._cancelled:
                self.loading_failed.emit(str(e), None)
    
    def cancel(self):
        """Cancel the loading operation."""
        self._cancelled = True
        self.requestInterruption()


class UniversalModelLoader(QObject):
    """
    Universal model loader service that orchestrates the entire loading pipeline.
    
    This service integrates all components to provide:
    - Automatic format detection and validation
    - Intelligent backend selection and routing
    - Memory management and optimization
    - Comprehensive error handling and reporting
    - Progress tracking and user feedback
    - Metadata extraction and caching
    """
    
    # Signals for UI integration
    loading_started = Signal(str)  # model_path
    progress_updated = Signal(UniversalLoadingProgress)
    loading_completed = Signal(UniversalLoadingResult)
    loading_failed = Signal(str, ErrorAnalysis)  # error_message, analysis
    format_detected = Signal(str, ModelFormat)  # model_path, format
    backend_selected = Signal(str, str)  # backend_name, reason
    memory_check_completed = Signal(MemoryCheckResult)
    metadata_extracted = Signal(UnifiedMetadata)
    
    def __init__(self, event_bus=None, parent=None):
        """Initialize the universal model loader."""
        super().__init__(parent)
        
        self.logger = logging.getLogger("universal_model_loader")
        
        # Event system integration
        self.event_bus = event_bus
        self.event_publisher = UniversalEventPublisher(event_bus) if event_bus else None
        
        # Initialize core components
        self.format_detector = UniversalFormatDetector()
        self.hardware_detector = HardwareDetector()
        self.routing_system = BackendRoutingSystem(self.hardware_detector)
        self.backend_manager = EnhancedBackendManager(self.hardware_detector)
        self.memory_manager = EnhancedMemoryManager(self.hardware_detector)
        self.error_reporter = EnhancedErrorReportingEngine()
        self.metadata_extractor = UniversalMetadataExtractor()
        # Try to initialize HuggingFace integration, but make it optional
        try:
            self.hf_integration = HuggingFaceIntegration()
            self.logger.info("HuggingFace integration enabled")
        except ImportError as e:
            self.logger.warning(f"HuggingFace integration disabled: {e}")
            self.hf_integration = None
        
        # Loading state
        self.current_loading: Optional[str] = None
        self.loading_start_time: Optional[float] = None
        self.loading_cache: Dict[str, UniversalLoadingResult] = {}
        
        # Configuration
        self.enable_caching = True
        self.enable_progress_tracking = True
        self.enable_optimization = True
        self.max_cache_size = 10
        
        # Connect internal signals
        self._connect_component_signals()
        
        # Threading support
        self.loading_worker = None
        self.loading_mutex = QMutex()
        
        self.logger.info("Universal model loader initialized")
    
    def _connect_component_signals(self):
        """Connect signals from internal components."""
        # Backend manager signals
        self.backend_manager.on_loading_progress = self._on_backend_progress
        self.backend_manager.on_backend_changed = self._on_backend_changed
        self.backend_manager.on_fallback_triggered = self._on_fallback_triggered
        
        # Memory manager signals
        self.memory_manager.memory_pressure_signal.connect(self._on_memory_pressure_changed)
        self.memory_manager.optimization_suggested_signal.connect(self._on_optimization_suggested)
    
    def load_model(self, model_path: str, preferred_backend: Optional[str] = None,
                  memory_constraints: Optional[MemoryConstraints] = None,
                  **kwargs):
        """
        Load a model using the universal loading pipeline in a background thread.
        
        Args:
            model_path: Path to model file/directory or HF model ID
            preferred_backend: Preferred backend name (optional)
            memory_constraints: Memory constraints for loading (optional)
            **kwargs: Additional loading parameters
        """
        self.logger.info(f"Starting universal model loading: {model_path}")
        
        # Thread safety check
        with QMutexLocker(self.loading_mutex):
            # Check if already loading
            if self.current_loading:
                raise RuntimeError(f"Already loading model: {self.current_loading}")
            
            # Check cache first
            if self.enable_caching and model_path in self.loading_cache:
                cached_result = self.loading_cache[model_path]
                self.logger.info(f"Returning cached result for: {model_path}")
                self.loading_completed.emit(cached_result)
                return
            
            # Initialize loading state
            self.current_loading = model_path
            self.loading_start_time = time.time()
        
        # Emit loading started signal and publish event
        self.loading_started.emit(model_path)
        if self.event_publisher:
            self.event_publisher.publish_loading_started(model_path)
        
        # Create and start worker thread
        self.loading_worker = ModelLoadingWorker(
            self, model_path, preferred_backend, memory_constraints, **kwargs
        )
        
        # Connect worker signals
        self.loading_worker.loading_progress.connect(self.progress_updated.emit)
        self.loading_worker.loading_completed.connect(self._on_worker_completed)
        self.loading_worker.loading_failed.connect(self._on_worker_failed)
        
        # Start loading in background thread
        self.loading_worker.start()
    
    def _on_worker_completed(self, result: UniversalLoadingResult):
        """Handle worker thread completion."""
        with QMutexLocker(self.loading_mutex):
            # Cache successful results
            if result.success and self.enable_caching:
                self._cache_result(self.current_loading, result)
            
            # Reset loading state
            self.current_loading = None
            self.loading_start_time = None
            
            # Clean up worker
            if self.loading_worker:
                self.loading_worker.deleteLater()
                self.loading_worker = None
        
        # Emit completion signal and publish event
        self.loading_completed.emit(result)
        if self.event_publisher and result.success:
            self.event_publisher.publish_model_loaded(result)
    
    def _on_worker_failed(self, error_message: str, error_analysis):
        """Handle worker thread failure."""
        with QMutexLocker(self.loading_mutex):
            # Reset loading state
            self.current_loading = None
            self.loading_start_time = None
            
            # Clean up worker
            if self.loading_worker:
                self.loading_worker.deleteLater()
                self.loading_worker = None
        
        # Emit failure signal and publish event
        self.loading_failed.emit(error_message, error_analysis)
        if self.event_publisher:
            self.event_publisher.publish_loading_failed(error_message, error_analysis)
    
    def cancel_loading(self):
        """Cancel the current loading operation."""
        with QMutexLocker(self.loading_mutex):
            if self.loading_worker and self.loading_worker.isRunning():
                self.loading_worker.cancel()
                self.loading_worker.wait(5000)  # Wait up to 5 seconds
                
                # Reset state
                self.current_loading = None
                self.loading_start_time = None
                
                if self.loading_worker:
                    self.loading_worker.deleteLater()
                    self.loading_worker = None
    
    def _execute_loading_pipeline_sync(self, model_path: str, preferred_backend: Optional[str] = None,
                                     memory_constraints: Optional[MemoryConstraints] = None,
                                     **kwargs) -> UniversalLoadingResult:
        """
        Execute the loading pipeline synchronously (called from worker thread).
        
        Args:
            model_path: Path to model file/directory or HF model ID
            preferred_backend: Preferred backend name (optional)
            memory_constraints: Memory constraints for loading (optional)
            **kwargs: Additional loading parameters
            
        Returns:
            UniversalLoadingResult with comprehensive loading information
        """
        try:
            # Execute loading pipeline
            result = self._execute_loading_pipeline(
                model_path, preferred_backend, memory_constraints, **kwargs
            )
            
            return result
            
        except Exception as e:
            # Handle unexpected errors
            self.logger.error(f"Unexpected error in loading pipeline: {e}")
            
            error_analysis = self.error_reporter.analyze_loading_error(
                e, LoadingContext(
                    model_path=model_path,
                    operation="universal_loading",
                    additional_context={"preferred_backend": preferred_backend}
                )
            )
            
            # Return failure result
            return UniversalLoadingResult(
                success=False,
                model_path=model_path,
                format_type=ModelFormat.UNKNOWN,
                backend_used="none",
                hardware_used="none",
                load_time=0,
                memory_usage=0,
                metadata=UnifiedMetadata(
                    format_type=ModelFormat.UNKNOWN,
                    model_name=Path(model_path).name
                ),
                loading_plan=None,
                error_analysis=error_analysis
            )
            
            return result
            
        except Exception as e:
            # Handle unexpected errors
            self.logger.error(f"Unexpected error in loading pipeline: {e}")
            
            error_analysis = self.error_reporter.analyze_loading_error(
                e, LoadingContext(
                    model_path=model_path,
                    operation="universal_loading",
                    additional_context={"preferred_backend": preferred_backend}
                )
            )
            
            # Emit failure signal
            self.loading_failed.emit(str(e), error_analysis)
            
            # Return failure result
            return UniversalLoadingResult(
                success=False,
                model_path=model_path,
                format_type=ModelFormat.UNKNOWN,
                backend_used="none",
                hardware_used="none",
                load_time=time.time() - self.loading_start_time,
                memory_usage=0,
                metadata=UnifiedMetadata(
                    format_type=ModelFormat.UNKNOWN,
                    model_name=Path(model_path).name
                ),
                loading_plan=None,
                error_analysis=error_analysis
            )
        
        finally:
            # Clean up loading state
            self.current_loading = None
            self.loading_start_time = None
    
    def _execute_loading_pipeline(self, model_path: str, preferred_backend: Optional[str],
                                memory_constraints: Optional[MemoryConstraints],
                                **kwargs) -> UniversalLoadingResult:
        """Execute the complete loading pipeline."""
        
        # Stage 1: Format Detection
        self._update_progress(LoadingStage.DETECTING_FORMAT, 10, "Detecting model format...")
        
        detection_result = self.format_detector.detect_format(model_path)
        
        if detection_result.format_type == ModelFormat.UNKNOWN:
            raise ValueError(f"Could not detect model format: {detection_result.error_message}")
        
        self.format_detected.emit(model_path, detection_result.format_type)
        if self.event_publisher:
            self.event_publisher.publish_format_detected(
                model_path, detection_result.format_type, detection_result.metadata
            )
        self.logger.info(f"Detected format: {detection_result.format_type.value}")
        
        # Stage 2: Model Validation
        self._update_progress(LoadingStage.VALIDATING_MODEL, 20, "Validating model...")
        
        if not detection_result.confidence > 0.5:
            self.logger.warning(f"Low confidence in format detection: {detection_result.confidence}")
        
        # Stage 3: Memory Check
        self._update_progress(LoadingStage.CHECKING_MEMORY, 30, "Checking memory requirements...")
        
        # Estimate memory requirements
        memory_estimate = self.memory_manager.estimate_memory_requirements(
            model_path, detection_result.format_type
        )
        
        # Check memory availability
        memory_check = self.memory_manager.check_memory_availability(
            memory_estimate.total_estimated
        )
        
        self.memory_check_completed.emit(memory_check)
        
        if not memory_check.is_available and not memory_check.can_optimize:
            raise RuntimeError(f"Insufficient memory: {memory_check.memory_deficit} bytes deficit")
        
        # Stage 4: Create Loading Plan
        self._update_progress(LoadingStage.CREATING_PLAN, 40, "Creating loading plan...")
        
        loading_plan = self.routing_system.route_model_loading(model_path, preferred_backend)
        
        self.backend_selected.emit(loading_plan.primary_backend, "Optimal backend selected")
        if self.event_publisher:
            self.event_publisher.publish_backend_selected(
                loading_plan.primary_backend, "Optimal backend selected", loading_plan.confidence
            )
        self.logger.info(f"Selected backend: {loading_plan.primary_backend}")
        
        # Stage 5: Extract Metadata (parallel with loading preparation)
        self._update_progress(LoadingStage.EXTRACTING_METADATA, 50, "Extracting metadata...")
        
        try:
            metadata = self.metadata_extractor.extract_metadata(
                model_path, detection_result.format_type
            )
            self.metadata_extracted.emit(metadata)
        except Exception as e:
            self.logger.warning(f"Metadata extraction failed: {e}")
            metadata = UnifiedMetadata(
                format_type=detection_result.format_type,
                model_name=Path(model_path).name,
                file_size=detection_result.metadata.get('file_size', 0)
            )
        
        # Stage 6: Apply Memory Optimizations
        if memory_check.can_optimize and self.enable_optimization:
            self._update_progress(LoadingStage.LOADING_MODEL, 60, "Applying optimizations...")
            
            optimizations = self.memory_manager.suggest_memory_optimizations(
                loading_plan.model_info, memory_check.available_memory
            )
            
            # Apply optimizations to loading parameters
            for optimization in optimizations:
                if optimization.optimization_type.value in kwargs:
                    continue  # Don't override user-specified parameters
                
                # Apply optimization parameters
                kwargs.update(optimization.parameters)
        
        # Stage 7: Load Model
        self._update_progress(LoadingStage.LOADING_MODEL, 70, "Loading model...")
        
        # Use enhanced backend manager for loading
        enhanced_result = self.backend_manager.load_model_with_routing(
            model_path, preferred_backend, **kwargs
        )
        
        if not enhanced_result.success:
            # Create error analysis
            error_analysis = self.error_reporter.analyze_loading_error(
                Exception(enhanced_result.error_message),
                LoadingContext(
                    model_format=detection_result.format_type,
                    model_path=model_path,
                    backend_name=loading_plan.primary_backend,
                    operation="model_loading"
                )
            )
            
            raise RuntimeError(f"Model loading failed: {enhanced_result.error_message}")
        
        # Stage 8: Finalization
        self._update_progress(LoadingStage.FINALIZING, 90, "Finalizing...")
        
        # Calculate performance metrics
        total_load_time = time.time() - self.loading_start_time
        performance_metrics = {
            'total_load_time': total_load_time,
            'backend_load_time': enhanced_result.load_time,
            'format_detection_time': 0.1,  # Approximate
            'metadata_extraction_time': 0.1,  # Approximate
            'memory_check_time': 0.05,  # Approximate
            'routing_time': 0.05  # Approximate
        }
        
        # Create comprehensive result
        result = UniversalLoadingResult(
            success=True,
            model_path=model_path,
            format_type=detection_result.format_type,
            backend_used=enhanced_result.backend_used,
            hardware_used=enhanced_result.hardware_used,
            load_time=total_load_time,
            memory_usage=enhanced_result.memory_usage,
            metadata=metadata,
            loading_plan=loading_plan,
            optimization_applied=enhanced_result.optimization_applied,
            fallback_attempts=[attempt.backend_name for attempt in enhanced_result.fallback_attempts],
            performance_metrics=performance_metrics
        )
        
        # Stage 9: Completion
        self._update_progress(LoadingStage.COMPLETED, 100, "Loading completed successfully!")
        
        self.logger.info(
            f"Successfully loaded {detection_result.format_type.value} model "
            f"with {enhanced_result.backend_used} in {total_load_time:.2f}s"
        )
        
        return result
    
    def _update_progress(self, stage: LoadingStage, progress: int, message: str, details: str = None):
        """Update loading progress."""
        if not self.enable_progress_tracking:
            return
        
        elapsed_time = time.time() - self.loading_start_time if self.loading_start_time else 0.0
        
        progress_info = UniversalLoadingProgress(
            stage=stage,
            progress=progress,
            message=message,
            details=details,
            elapsed_time=elapsed_time
        )
        
        self.progress_updated.emit(progress_info)
        if self.event_publisher:
            self.event_publisher.publish_progress_updated(progress_info)
        self.logger.debug(f"Progress: {progress}% - {message}")
    
    def _cache_result(self, model_path: str, result: UniversalLoadingResult):
        """Cache a successful loading result."""
        if len(self.loading_cache) >= self.max_cache_size:
            # Remove oldest entry
            oldest_key = next(iter(self.loading_cache))
            del self.loading_cache[oldest_key]
        
        self.loading_cache[model_path] = result
        self.logger.debug(f"Cached loading result for: {model_path}")
    
    def clear_cache(self):
        """Clear the loading cache."""
        self.loading_cache.clear()
        self.logger.info("Cleared loading cache")
    
    def get_supported_formats(self) -> List[ModelFormat]:
        """Get list of supported model formats."""
        return [
            ModelFormat.GGUF,
            ModelFormat.SAFETENSORS,
            ModelFormat.PYTORCH_BIN,
            ModelFormat.HUGGINGFACE
        ]
    
    def get_available_backends(self) -> List[str]:
        """Get list of available backends."""
        return self.backend_manager.get_available_backends()
    
    def get_format_info(self, model_path: str) -> Optional[FormatDetectionResult]:
        """Get format detection information for a model."""
        try:
            return self.format_detector.detect_format(model_path)
        except Exception as e:
            self.logger.error(f"Error detecting format for {model_path}: {e}")
            return None
    
    def get_backend_recommendations(self, model_path: str) -> Dict[str, Any]:
        """Get backend recommendations for a model."""
        return self.backend_manager.get_backend_recommendations(model_path)
    
    def validate_model_path(self, model_path: str) -> Tuple[bool, Optional[str]]:
        """Validate a model path or HF model ID."""
        try:
            detection_result = self.format_detector.detect_format(model_path)
            
            if detection_result.format_type == ModelFormat.UNKNOWN:
                return False, detection_result.error_message
            
            if detection_result.format_type == ModelFormat.HUGGINGFACE:
                # Additional HF validation
                if detection_result.hf_validation and not detection_result.hf_validation.is_valid:
                    return False, detection_result.hf_validation.error_message
            
            return True, None
            
        except Exception as e:
            return False, str(e)
    
    def get_loading_statistics(self) -> Dict[str, Any]:
        """Get comprehensive loading statistics."""
        return {
            'cache_size': len(self.loading_cache),
            'cache_hit_rate': 0.0,  # Would need to track hits/misses
            'supported_formats': [fmt.value for fmt in self.get_supported_formats()],
            'available_backends': self.get_available_backends(),
            'backend_manager_stats': self.backend_manager.get_routing_statistics(),
            'memory_manager_stats': self.memory_manager.get_statistics(),
            'current_loading': self.current_loading
        }
    
    # Signal handlers for component integration
    def _on_backend_progress(self, message: str, progress: int):
        """Handle backend loading progress."""
        if self.current_loading:
            # Adjust progress to fit within loading stage range (70-90%)
            adjusted_progress = 70 + (progress * 20 // 100)
            self._update_progress(LoadingStage.LOADING_MODEL, adjusted_progress, message)
    
    def _on_backend_changed(self, backend_name: str, model_path: str):
        """Handle backend change notification."""
        self.backend_selected.emit(backend_name, f"Backend changed to {backend_name}")
    
    def _on_fallback_triggered(self, from_backend: str, to_backend: str, reason: str):
        """Handle fallback trigger notification."""
        self.backend_selected.emit(to_backend, f"Fallback from {from_backend}: {reason}")
    
    def _on_memory_pressure_changed(self, pressure_level):
        """Handle memory pressure changes."""
        if pressure_level.value in ['high', 'critical']:
            self.logger.warning(f"Memory pressure: {pressure_level.value}")
    
    def _on_optimization_suggested(self, suggestions):
        """Handle optimization suggestions."""
        self.logger.info(f"Memory optimizations suggested: {len(suggestions)} options")