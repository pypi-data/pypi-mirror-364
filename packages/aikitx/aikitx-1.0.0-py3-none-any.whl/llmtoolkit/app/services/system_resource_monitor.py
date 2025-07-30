"""
System Resource Monitor Service

This module provides a service for monitoring system resources including
CPU, memory, and GPU usage. It integrates with the existing GPUMonitor
and provides real-time metric updates through the event bus.

Features:
- Real-time CPU and memory monitoring
- Integration with existing GPUMonitor for GPU metrics
- Event-based metric publishing
- Resource metrics data structure
- Performance monitoring integration
"""

import logging
import time
import threading
from typing import Optional, Dict, Any, Callable, List
from dataclasses import dataclass

import psutil
from PySide6.QtCore import QObject, QTimer, Signal

from llmtoolkit.app.core.event_bus import EventBus
from llmtoolkit.app.core.monitoring import GPUMonitor
from llmtoolkit.app.core.universal_events import (
    ResourceMetrics, UniversalEventPublisher, UniversalEventType
)


# ResourceMetrics is now imported from universal_events


class SystemResourceMonitor(QObject):
    """
    Monitors system resources and provides real-time updates.
    
    This service integrates with the existing GPUMonitor and provides
    comprehensive system resource monitoring through the event bus.
    """
    
    # Signals
    metrics_updated = Signal(ResourceMetrics)
    gpu_metrics_available = Signal(dict)
    monitoring_started = Signal()
    monitoring_stopped = Signal()
    
    def __init__(self, event_bus: EventBus, parent=None):
        """
        Initialize the system resource monitor.
        
        Args:
            event_bus: Application event bus
            parent: Parent QObject
        """
        super().__init__(parent)
        
        self.logger = logging.getLogger("gguf_loader.services.system_resource_monitor")
        self.event_bus = event_bus
        self.event_publisher = UniversalEventPublisher(event_bus) if event_bus else None
        
        # Monitoring state
        self.monitoring_active = False
        self.current_backend_name: Optional[str] = None
        self.model_active = False
        
        # Update timer for metrics collection
        self.update_timer = QTimer()
        self.update_timer.timeout.connect(self._collect_metrics)
        self.update_timer.setInterval(2000)  # 2 seconds as per requirements
        
        # GPU monitor integration
        self.gpu_monitor = GPUMonitor()
        
        # Metrics history for analysis
        self.metrics_history: List[ResourceMetrics] = []
        self.max_history_size = 300  # 10 minutes at 2-second intervals
        
        # Connect to model loading events
        self._connect_events()
        
        self.logger.info("System resource monitor initialized")
    
    def _connect_events(self):
        """Connect to model loading and unloading events."""
        # Universal model loading events
        self.event_bus.subscribe("universal.model.loaded", self._on_model_loaded)
        self.event_bus.subscribe("universal.model.unloaded", self._on_model_unloaded)
        self.event_bus.subscribe("universal.model.loading_failed", self._on_model_loading_failed)
        
        # Legacy model events for backward compatibility
        self.event_bus.subscribe("model.loaded", self._on_legacy_model_loaded)
        self.event_bus.subscribe("model.unloaded", self._on_legacy_model_unloaded)
        
        # Resource monitoring control events
        self.event_bus.subscribe("resource.monitor.start", self._on_start_monitoring_request)
        self.event_bus.subscribe("resource.monitor.stop", self._on_stop_monitoring_request)
        self.event_bus.subscribe("resource.monitor.gpu_requested", self._on_gpu_details_requested)
    
    def start_monitoring(self):
        """Start resource monitoring."""
        if self.monitoring_active:
            self.logger.warning("Resource monitoring already active")
            return
        
        self.monitoring_active = True
        self.update_timer.start()
        
        # Publish monitoring started event
        self.event_bus.publish("resource.monitor.started")
        self.monitoring_started.emit()
        
        self.logger.info("Resource monitoring started")
    
    def stop_monitoring(self):
        """Stop resource monitoring."""
        if not self.monitoring_active:
            return
        
        self.monitoring_active = False
        self.update_timer.stop()
        
        # Publish monitoring stopped event
        self.event_bus.publish("resource.monitor.stopped")
        self.monitoring_stopped.emit()
        
        self.logger.info("Resource monitoring stopped")
    
    def _collect_metrics(self):
        """Collect system metrics and publish updates."""
        try:
            # Collect basic system metrics
            cpu_usage = psutil.cpu_percent(interval=None)
            memory_info = psutil.virtual_memory()
            memory_usage_mb = memory_info.used // (1024 * 1024)
            memory_total_mb = memory_info.total // (1024 * 1024)
            
            # Collect GPU metrics
            gpu_metrics = []
            gpu_available = False
            
            try:
                gpu_metrics = self.gpu_monitor.get_gpu_metrics()
                gpu_available = len(gpu_metrics) > 0
            except Exception as e:
                self.logger.debug(f"Error collecting GPU metrics: {e}")
            
            # Create metrics object
            metrics = ResourceMetrics(
                timestamp=time.time(),
                cpu_usage=cpu_usage,
                memory_usage=memory_usage_mb,
                memory_total=memory_total_mb,
                backend_name=self.current_backend_name,
                model_active=self.model_active,
                gpu_available=gpu_available,
                gpu_metrics=gpu_metrics
            )
            
            # Add to history
            self._add_to_history(metrics)
            
            # Emit signal
            self.metrics_updated.emit(metrics)
            
            # Publish event using both old and new event systems
            self.event_bus.publish("resource.monitor.updated", metrics.to_dict())
            if self.event_publisher:
                self.event_publisher.publish_resource_metrics(metrics)
            
            # Publish GPU metrics separately if available
            if gpu_available:
                self.event_bus.publish("resource.monitor.gpu_data", {
                    'timestamp': metrics.timestamp,
                    'gpu_metrics': gpu_metrics
                })
                if self.event_publisher:
                    self.event_publisher.publish_gpu_data(gpu_metrics)
                self.gpu_metrics_available.emit({'gpu_metrics': gpu_metrics})
            
        except Exception as e:
            self.logger.error(f"Error collecting system metrics: {e}")
    
    def _add_to_history(self, metrics: ResourceMetrics):
        """Add metrics to history with size limit."""
        self.metrics_history.append(metrics)
        
        # Trim history if too large
        if len(self.metrics_history) > self.max_history_size:
            self.metrics_history = self.metrics_history[-self.max_history_size:]
    
    def get_current_metrics(self) -> Optional[ResourceMetrics]:
        """Get the most recent metrics."""
        return self.metrics_history[-1] if self.metrics_history else None
    
    def get_metrics_history(self, duration_seconds: int = 300) -> List[ResourceMetrics]:
        """
        Get metrics history for the specified duration.
        
        Args:
            duration_seconds: Duration in seconds (default: 5 minutes)
            
        Returns:
            List of ResourceMetrics within the time range
        """
        if not self.metrics_history:
            return []
        
        cutoff_time = time.time() - duration_seconds
        return [m for m in self.metrics_history if m.timestamp >= cutoff_time]
    
    def get_average_metrics(self, duration_seconds: int = 60) -> Optional[Dict[str, float]]:
        """
        Get average metrics over the specified duration.
        
        Args:
            duration_seconds: Duration in seconds (default: 1 minute)
            
        Returns:
            Dictionary with average metrics or None if no data
        """
        history = self.get_metrics_history(duration_seconds)
        
        if not history:
            return None
        
        total_cpu = sum(m.cpu_usage for m in history)
        total_memory_pct = sum(m.get_memory_percentage() for m in history)
        count = len(history)
        
        return {
            'avg_cpu_usage': total_cpu / count,
            'avg_memory_percentage': total_memory_pct / count,
            'sample_count': count,
            'duration_seconds': duration_seconds
        }
    
    def get_gpu_details(self) -> Dict[str, Any]:
        """Get detailed GPU information."""
        try:
            gpu_metrics = self.gpu_monitor.get_gpu_metrics()
            
            return {
                'timestamp': time.time(),
                'gpu_count': len(gpu_metrics),
                'gpu_available': len(gpu_metrics) > 0,
                'gpu_metrics': gpu_metrics,
                'monitoring_active': self.monitoring_active
            }
        except Exception as e:
            self.logger.error(f"Error getting GPU details: {e}")
            return {
                'timestamp': time.time(),
                'gpu_count': 0,
                'gpu_available': False,
                'gpu_metrics': [],
                'error': str(e)
            }
    
    def _get_current_backend(self) -> Optional[str]:
        """Get the current backend name."""
        return self.current_backend_name
    
    def _is_model_active(self) -> bool:
        """Check if a model is currently active."""
        return self.model_active
    
    # Event handlers
    def _on_model_loaded(self, loading_result):
        """Handle universal model loaded event."""
        try:
            backend_name = getattr(loading_result, 'backend_used', 'Unknown')
            self.current_backend_name = backend_name
            self.model_active = True
            
            # Start monitoring when model is loaded
            if not self.monitoring_active:
                self.start_monitoring()
            
            self.logger.info(f"Model loaded - backend: {backend_name}")
            
        except Exception as e:
            self.logger.error(f"Error handling model loaded event: {e}")
    
    def _on_model_unloaded(self, *args):
        """Handle universal model unloaded event."""
        self.current_backend_name = None
        self.model_active = False
        
        # Stop monitoring when model is unloaded
        self.stop_monitoring()
        
        self.logger.info("Model unloaded - monitoring stopped")
    
    def _on_model_loading_failed(self, *args):
        """Handle universal model loading failed event."""
        self.current_backend_name = None
        self.model_active = False
        
        # Stop monitoring on loading failure
        self.stop_monitoring()
        
        self.logger.info("Model loading failed - monitoring stopped")
    
    def _on_legacy_model_loaded(self, backend_name, model_info=None):
        """Handle legacy model loaded event for backward compatibility."""
        self.current_backend_name = backend_name
        self.model_active = True
        
        if not self.monitoring_active:
            self.start_monitoring()
        
        self.logger.info(f"Legacy model loaded - backend: {backend_name}")
    
    def _on_legacy_model_unloaded(self, *args):
        """Handle legacy model unloaded event for backward compatibility."""
        self.current_backend_name = None
        self.model_active = False
        self.stop_monitoring()
        
        self.logger.info("Legacy model unloaded - monitoring stopped")
    
    def _on_start_monitoring_request(self, *args):
        """Handle external request to start monitoring."""
        self.start_monitoring()
    
    def _on_stop_monitoring_request(self, *args):
        """Handle external request to stop monitoring."""
        self.stop_monitoring()
    
    def _on_gpu_details_requested(self, *args):
        """Handle request for GPU details."""
        gpu_details = self.get_gpu_details()
        self.event_bus.publish("resource.monitor.gpu_data", gpu_details)
    
    def get_performance_summary(self) -> Dict[str, Any]:
        """Get a performance summary for the current session."""
        current_metrics = self.get_current_metrics()
        avg_metrics = self.get_average_metrics(300)  # 5 minutes
        
        summary = {
            'monitoring_active': self.monitoring_active,
            'model_active': self.model_active,
            'current_backend': self.current_backend_name,
            'metrics_history_count': len(self.metrics_history)
        }
        
        if current_metrics:
            summary.update({
                'current_cpu_usage': current_metrics.cpu_usage,
                'current_memory_usage_gb': current_metrics.memory_usage / 1024,
                'current_memory_percentage': current_metrics.get_memory_percentage(),
                'gpu_available': current_metrics.gpu_available,
                'gpu_count': len(current_metrics.gpu_metrics)
            })
        
        if avg_metrics:
            summary.update({
                'avg_cpu_usage_5min': avg_metrics['avg_cpu_usage'],
                'avg_memory_percentage_5min': avg_metrics['avg_memory_percentage']
            })
        
        return summary