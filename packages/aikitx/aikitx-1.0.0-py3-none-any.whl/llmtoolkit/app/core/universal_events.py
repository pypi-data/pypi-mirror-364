"""
Universal Model Integration Event System

This module defines enhanced event types and data structures for the universal
model loading system integration. It extends the existing event bus with new
event types specifically designed for universal model loading, resource monitoring,
and performance feedback.

Requirements addressed: 1.1, 2.1, 4.1, 4.2
"""

from dataclasses import dataclass, field
from typing import Dict, Any, Optional, List
from enum import Enum

from .universal_format_detector import ModelFormat
from .backend_routing_system import LoadingPlan
from .universal_metadata_extractor import UnifiedMetadata
from .enhanced_error_reporting import ErrorAnalysis


class UniversalEventType:
    """Event types for universal model integration."""
    
    # Universal model loading events
    UNIVERSAL_LOADING_STARTED = "universal.model.loading_started"
    UNIVERSAL_PROGRESS_UPDATED = "universal.model.progress_updated"
    UNIVERSAL_FORMAT_DETECTED = "universal.model.format_detected"
    UNIVERSAL_BACKEND_SELECTED = "universal.model.backend_selected"
    UNIVERSAL_MODEL_LOADED = "universal.model.loaded"
    UNIVERSAL_LOADING_FAILED = "universal.model.loading_failed"
    UNIVERSAL_MODEL_UNLOADED = "universal.model.unloaded"
    
    # Resource monitoring events
    RESOURCE_MONITOR_STARTED = "resource.monitor.started"
    RESOURCE_MONITOR_UPDATED = "resource.monitor.updated"
    RESOURCE_MONITOR_GPU_REQUESTED = "resource.monitor.gpu_requested"
    RESOURCE_MONITOR_GPU_DATA = "resource.monitor.gpu_data"
    RESOURCE_MONITOR_STOPPED = "resource.monitor.stopped"
    
    # Performance events
    PERFORMANCE_METRICS_UPDATED = "performance.metrics_updated"
    PERFORMANCE_WARNING = "performance.warning"
    PERFORMANCE_OPTIMIZATION_SUGGESTED = "performance.optimization_suggested"
    
    # Tab integration events
    TAB_MODEL_STATUS_CHANGED = "tab.model_status_changed"
    TAB_CAPABILITIES_UPDATED = "tab.capabilities_updated"
    TAB_ERROR_OCCURRED = "tab.error_occurred"
    TAB_DISABLE_AI_FEATURES = "tab.disable_ai_features"
    TAB_SHOW_FORMAT_ERROR = "tab.show_format_error"


class LoadingStage(Enum):
    """Stages of the universal loading pipeline."""
    INITIALIZING = "initializing"
    DETECTING_FORMAT = "detecting_format"
    VALIDATING_MODEL = "validating_model"
    CHECKING_MEMORY = "checking_memory"
    CREATING_PLAN = "creating_plan"
    EXTRACTING_METADATA = "extracting_metadata"
    LOADING_MODEL = "loading_model"
    FINALIZING = "finalizing"
    COMPLETED = "completed"
    FAILED = "failed"


@dataclass
class UniversalLoadingProgress:
    """Progress information for universal model loading."""
    stage: LoadingStage
    progress: int  # 0-100
    message: str
    details: Optional[str] = None
    elapsed_time: float = 0.0
    estimated_remaining: Optional[float] = None
    backend_info: Optional[str] = None
    memory_usage: Optional[int] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for event publishing."""
        return {
            'stage': self.stage.value,
            'progress': self.progress,
            'message': self.message,
            'details': self.details,
            'elapsed_time': self.elapsed_time,
            'estimated_remaining': self.estimated_remaining,
            'backend_info': self.backend_info,
            'memory_usage': self.memory_usage
        }


@dataclass
class UniversalModelInfo:
    """Comprehensive model information from universal loading system."""
    model_path: str
    format_type: ModelFormat
    backend_used: str
    hardware_used: str
    metadata: UnifiedMetadata
    capabilities: List[str]
    performance_metrics: Dict[str, Any]
    memory_usage: int
    optimization_applied: List[str] = field(default_factory=list)
    fallback_attempts: List[str] = field(default_factory=list)
    warnings: List[str] = field(default_factory=list)
    load_time: float = 0.0
    loading_plan: Optional[LoadingPlan] = None
    
    def get_display_name(self) -> str:
        """Get user-friendly model name."""
        return self.metadata.model_name or self.model_path.split('/')[-1]
        
    def get_capability_description(self) -> str:
        """Get human-readable capability description."""
        return ", ".join(self.capabilities) if self.capabilities else "Standard text generation"
        
    def get_performance_summary(self) -> str:
        """Get performance summary for display."""
        memory_gb = self.memory_usage / 1024 if self.memory_usage else 0
        return f"Load time: {self.load_time:.1f}s, Memory: {memory_gb:.1f}GB"
    
    def get_backend_info(self) -> str:
        """Get backend information for display."""
        return f"{self.backend_used} ({self.hardware_used})"
    
    def has_capability(self, capability: str) -> bool:
        """Check if model has a specific capability."""
        return capability.lower() in [cap.lower() for cap in self.capabilities]
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for event publishing."""
        return {
            'model_path': self.model_path,
            'format_type': self.format_type.value,
            'backend_used': self.backend_used,
            'hardware_used': self.hardware_used,
            'capabilities': self.capabilities,
            'performance_metrics': self.performance_metrics,
            'memory_usage': self.memory_usage,
            'optimization_applied': self.optimization_applied,
            'fallback_attempts': self.fallback_attempts,
            'warnings': self.warnings,
            'load_time': self.load_time,
            'display_name': self.get_display_name(),
            'capability_description': self.get_capability_description(),
            'performance_summary': self.get_performance_summary(),
            'backend_info': self.get_backend_info()
        }


@dataclass
class ResourceMetrics:
    """Real-time system resource metrics for event publishing."""
    timestamp: float
    cpu_usage: float  # Percentage
    memory_usage: int  # MB
    memory_total: int  # MB
    backend_name: Optional[str]
    model_active: bool
    gpu_available: bool
    gpu_metrics: List[Dict[str, Any]] = field(default_factory=list)
    
    def get_memory_percentage(self) -> float:
        """Get memory usage as percentage."""
        return (self.memory_usage / self.memory_total) * 100 if self.memory_total > 0 else 0
        
    def format_memory_display(self) -> str:
        """Format memory for display."""
        return f"{self.memory_usage/1024:.1f}GB/{self.memory_total/1024:.1f}GB"
    
    def get_cpu_display(self) -> str:
        """Format CPU usage for display."""
        return f"{self.cpu_usage:.1f}%"
    
    def get_gpu_summary(self) -> str:
        """Get GPU summary for display."""
        if not self.gpu_available or not self.gpu_metrics:
            return "No GPU"
        
        gpu_count = len(self.gpu_metrics)
        if gpu_count == 1:
            gpu_info = self.gpu_metrics[0]
            usage = gpu_info.get('utilization', {}).get('gpu', 0)
            return f"GPU: {usage}%"
        else:
            return f"{gpu_count} GPUs available"
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for event publishing."""
        return {
            'timestamp': self.timestamp,
            'cpu_usage': self.cpu_usage,
            'memory_usage': self.memory_usage,
            'memory_total': self.memory_total,
            'memory_percentage': self.get_memory_percentage(),
            'backend_name': self.backend_name,
            'model_active': self.model_active,
            'gpu_available': self.gpu_available,
            'gpu_count': len(self.gpu_metrics),
            'gpu_metrics': self.gpu_metrics,
            'memory_display': self.format_memory_display(),
            'cpu_display': self.get_cpu_display(),
            'gpu_summary': self.get_gpu_summary()
        }


@dataclass
class PerformanceMetrics:
    """Performance metrics for model operations."""
    operation_type: str  # "loading", "inference", "memory_check", etc.
    duration: float  # seconds
    memory_peak: int  # MB
    cpu_usage_avg: float  # percentage
    gpu_usage_avg: Optional[float] = None  # percentage
    throughput: Optional[float] = None  # tokens/second or similar
    latency: Optional[float] = None  # seconds
    quality_score: Optional[float] = None  # 0-1
    additional_metrics: Dict[str, Any] = field(default_factory=dict)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for event publishing."""
        return {
            'operation_type': self.operation_type,
            'duration': self.duration,
            'memory_peak': self.memory_peak,
            'cpu_usage_avg': self.cpu_usage_avg,
            'gpu_usage_avg': self.gpu_usage_avg,
            'throughput': self.throughput,
            'latency': self.latency,
            'quality_score': self.quality_score,
            'additional_metrics': self.additional_metrics
        }


@dataclass
class PerformanceWarning:
    """Warning about performance issues."""
    warning_type: str  # "high_memory", "slow_inference", "gpu_underutilized", etc.
    severity: str  # "low", "medium", "high", "critical"
    message: str
    details: Optional[str] = None
    suggested_actions: List[str] = field(default_factory=list)
    affected_components: List[str] = field(default_factory=list)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for event publishing."""
        return {
            'warning_type': self.warning_type,
            'severity': self.severity,
            'message': self.message,
            'details': self.details,
            'suggested_actions': self.suggested_actions,
            'affected_components': self.affected_components
        }


@dataclass
class OptimizationSuggestion:
    """Suggestion for performance optimization."""
    suggestion_type: str  # "memory_optimization", "backend_switch", "hardware_upgrade", etc.
    priority: str  # "low", "medium", "high"
    title: str
    description: str
    expected_improvement: Optional[str] = None
    implementation_steps: List[str] = field(default_factory=list)
    requirements: List[str] = field(default_factory=list)
    estimated_effort: Optional[str] = None  # "low", "medium", "high"
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for event publishing."""
        return {
            'suggestion_type': self.suggestion_type,
            'priority': self.priority,
            'title': self.title,
            'description': self.description,
            'expected_improvement': self.expected_improvement,
            'implementation_steps': self.implementation_steps,
            'requirements': self.requirements,
            'estimated_effort': self.estimated_effort
        }


@dataclass
class TabModelStatus:
    """Model status information for tab integration."""
    model_loaded: bool
    model_info: Optional[UniversalModelInfo] = None
    loading_progress: Optional[UniversalLoadingProgress] = None
    error_info: Optional[ErrorAnalysis] = None
    capabilities_available: List[str] = field(default_factory=list)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for event publishing."""
        return {
            'model_loaded': self.model_loaded,
            'model_info': self.model_info.to_dict() if self.model_info else None,
            'loading_progress': self.loading_progress.to_dict() if self.loading_progress else None,
            'error_info': self.error_info.__dict__ if self.error_info else None,
            'capabilities_available': self.capabilities_available
        }


class UniversalEventPublisher:
    """
    Helper class for publishing universal model integration events.
    
    This class provides convenient methods for publishing events with proper
    data structures and ensures consistent event naming and data formats.
    """
    
    def __init__(self, event_bus):
        """Initialize with event bus reference."""
        self.event_bus = event_bus
    
    def publish_loading_started(self, model_path: str, loading_plan: Optional[LoadingPlan] = None):
        """Publish universal model loading started event."""
        data = {'model_path': model_path}
        if loading_plan:
            data['loading_plan'] = loading_plan.__dict__
        
        self.event_bus.publish(UniversalEventType.UNIVERSAL_LOADING_STARTED, data)
    
    def publish_progress_updated(self, progress: UniversalLoadingProgress):
        """Publish loading progress update event."""
        self.event_bus.publish(UniversalEventType.UNIVERSAL_PROGRESS_UPDATED, progress.to_dict())
    
    def publish_format_detected(self, model_path: str, format_type: ModelFormat, metadata: Dict[str, Any] = None):
        """Publish format detection event."""
        data = {
            'model_path': model_path,
            'format_type': format_type.value,
            'metadata': metadata or {}
        }
        self.event_bus.publish(UniversalEventType.UNIVERSAL_FORMAT_DETECTED, data)
    
    def publish_backend_selected(self, backend_name: str, reason: str, confidence: float = 1.0):
        """Publish backend selection event."""
        data = {
            'backend_name': backend_name,
            'reason': reason,
            'confidence': confidence
        }
        self.event_bus.publish(UniversalEventType.UNIVERSAL_BACKEND_SELECTED, data)
    
    def publish_model_loaded(self, loading_result):
        """Publish model loaded event with comprehensive information."""
        # Convert loading result to UniversalModelInfo
        model_info = UniversalModelInfo(
            model_path=loading_result.model_path,
            format_type=loading_result.format_type,
            backend_used=loading_result.backend_used,
            hardware_used=loading_result.hardware_used,
            metadata=loading_result.metadata,
            capabilities=self._extract_capabilities(loading_result),
            performance_metrics=loading_result.performance_metrics,
            memory_usage=loading_result.memory_usage,
            optimization_applied=loading_result.optimization_applied,
            fallback_attempts=loading_result.fallback_attempts,
            warnings=loading_result.warnings,
            load_time=loading_result.load_time,
            loading_plan=loading_result.loading_plan
        )
        
        self.event_bus.publish(UniversalEventType.UNIVERSAL_MODEL_LOADED, model_info.to_dict())
    
    def publish_loading_failed(self, error_message: str, error_analysis: ErrorAnalysis):
        """Publish loading failed event."""
        data = {
            'error_message': error_message,
            'error_analysis': error_analysis.__dict__ if error_analysis else None
        }
        self.event_bus.publish(UniversalEventType.UNIVERSAL_LOADING_FAILED, data)
    
    def publish_model_unloaded(self, model_path: str, cleanup_info: Dict[str, Any] = None):
        """Publish model unloaded event."""
        data = {
            'model_path': model_path,
            'cleanup_info': cleanup_info or {}
        }
        self.event_bus.publish(UniversalEventType.UNIVERSAL_MODEL_UNLOADED, data)
    
    def publish_resource_metrics(self, metrics: ResourceMetrics):
        """Publish resource monitoring update event."""
        self.event_bus.publish(UniversalEventType.RESOURCE_MONITOR_UPDATED, metrics.to_dict())
    
    def publish_gpu_data(self, gpu_metrics: List[Dict[str, Any]]):
        """Publish GPU metrics event."""
        data = {
            'timestamp': time.time(),
            'gpu_metrics': gpu_metrics
        }
        self.event_bus.publish(UniversalEventType.RESOURCE_MONITOR_GPU_DATA, data)
    
    def publish_performance_metrics(self, metrics: PerformanceMetrics):
        """Publish performance metrics update event."""
        self.event_bus.publish(UniversalEventType.PERFORMANCE_METRICS_UPDATED, metrics.to_dict())
    
    def publish_performance_warning(self, warning: PerformanceWarning):
        """Publish performance warning event."""
        self.event_bus.publish(UniversalEventType.PERFORMANCE_WARNING, warning.to_dict())
    
    def publish_optimization_suggestion(self, suggestion: OptimizationSuggestion):
        """Publish optimization suggestion event."""
        self.event_bus.publish(UniversalEventType.PERFORMANCE_OPTIMIZATION_SUGGESTED, suggestion.to_dict())
    
    def publish_tab_model_status(self, status: TabModelStatus):
        """Publish tab model status change event."""
        self.event_bus.publish(UniversalEventType.TAB_MODEL_STATUS_CHANGED, status.to_dict())
    
    def publish_tab_capabilities_updated(self, capabilities: List[str], tab_name: str = None):
        """Publish tab capabilities update event."""
        data = {
            'capabilities': capabilities,
            'tab_name': tab_name
        }
        self.event_bus.publish(UniversalEventType.TAB_CAPABILITIES_UPDATED, data)
    
    def publish_tab_error(self, error_message: str, tab_name: str, error_type: str = "general"):
        """Publish tab error event."""
        data = {
            'error_message': error_message,
            'tab_name': tab_name,
            'error_type': error_type
        }
        self.event_bus.publish(UniversalEventType.TAB_ERROR_OCCURRED, data)
    
    def _extract_capabilities(self, loading_result) -> List[str]:
        """Extract model capabilities from loading result."""
        capabilities = []
        
        # Basic capability based on format
        if loading_result.format_type in [ModelFormat.GGUF, ModelFormat.SAFETENSORS, 
                                        ModelFormat.PYTORCH_BIN, ModelFormat.HUGGINGFACE]:
            capabilities.append("text-generation")
        
        # Add capabilities based on metadata
        if hasattr(loading_result, 'metadata') and loading_result.metadata:
            if hasattr(loading_result.metadata, 'model_type'):
                if loading_result.metadata.model_type:
                    capabilities.append(loading_result.metadata.model_type)
            
            # Check for specific model architectures
            if hasattr(loading_result.metadata, 'architecture'):
                arch = loading_result.metadata.architecture
                if arch:
                    if 'llama' in arch.lower():
                        capabilities.extend(["chat", "instruction-following"])
                    elif 'gpt' in arch.lower():
                        capabilities.extend(["chat", "completion"])
                    elif 'bert' in arch.lower():
                        capabilities.extend(["embedding", "classification"])
        
        # Add backend-specific capabilities
        if loading_result.backend_used:
            if 'gpu' in loading_result.hardware_used.lower():
                capabilities.append("gpu-accelerated")
            if 'cpu' in loading_result.hardware_used.lower():
                capabilities.append("cpu-optimized")
        
        return list(set(capabilities))  # Remove duplicates


# Import time for timestamp generation
import time