"""
Universal Loading Monitor

This module provides comprehensive logging and monitoring for the universal loading pipeline,
tracking performance metrics, error patterns, and system health across all formats and backends.

Requirements addressed: 1.1, 1.2, 1.5, 1.6, 2.6
"""

import logging
import time
import json
import threading
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, Any, Optional, List, Callable
from dataclasses import dataclass, field, asdict
from enum import Enum
from collections import defaultdict, deque

from PySide6.QtCore import QObject, Signal, QTimer

from .universal_format_detector import ModelFormat
from .backend_routing_system import LoadingPlan
from .monitoring import monitoring_manager


class MonitoringEvent(Enum):
    """Types of monitoring events."""
    LOADING_STARTED = "loading_started"
    LOADING_COMPLETED = "loading_completed"
    LOADING_FAILED = "loading_failed"
    FORMAT_DETECTED = "format_detected"
    BACKEND_SELECTED = "backend_selected"
    BACKEND_FALLBACK = "backend_fallback"
    MEMORY_CHECK = "memory_check"
    OPTIMIZATION_APPLIED = "optimization_applied"
    ERROR_OCCURRED = "error_occurred"
    PERFORMANCE_METRIC = "performance_metric"


@dataclass
class LoadingMetrics:
    """Comprehensive metrics for a loading operation."""
    model_path: str
    format_type: ModelFormat
    backend_used: str
    success: bool
    start_time: float
    end_time: float
    total_duration: float
    
    # Stage timings
    format_detection_time: float = 0.0
    validation_time: float = 0.0
    memory_check_time: float = 0.0
    routing_time: float = 0.0
    metadata_extraction_time: float = 0.0
    backend_loading_time: float = 0.0
    
    # Resource usage
    memory_usage_mb: int = 0
    cpu_usage_percent: float = 0.0
    gpu_usage_percent: float = 0.0
    
    # Model characteristics
    model_size_mb: int = 0
    parameter_count: Optional[int] = None
    quantization: Optional[str] = None
    
    # Backend information
    fallback_attempts: List[str] = field(default_factory=list)
    optimization_applied: List[str] = field(default_factory=list)
    
    # Error information
    error_message: Optional[str] = None
    error_category: Optional[str] = None
    
    # Additional context
    hardware_info: Dict[str, Any] = field(default_factory=dict)
    config_info: Dict[str, Any] = field(default_factory=dict)


@dataclass
class SystemHealthMetrics:
    """System health metrics."""
    timestamp: float
    cpu_usage: float
    memory_usage: float
    gpu_usage: float
    disk_usage: float
    active_loadings: int
    cache_hit_rate: float
    error_rate: float


@dataclass
class PerformanceStats:
    """Performance statistics for analysis."""
    format_type: ModelFormat
    backend_name: str
    
    # Timing statistics
    avg_load_time: float = 0.0
    min_load_time: float = float('inf')
    max_load_time: float = 0.0
    std_load_time: float = 0.0
    
    # Success statistics
    total_attempts: int = 0
    successful_loads: int = 0
    success_rate: float = 0.0
    
    # Resource statistics
    avg_memory_usage: float = 0.0
    avg_cpu_usage: float = 0.0
    
    # Recent performance (last 10 loads)
    recent_load_times: deque = field(default_factory=lambda: deque(maxlen=10))
    recent_success_rate: float = 0.0


class UniversalLoadingMonitor(QObject):
    """
    Comprehensive monitoring system for the universal loading pipeline.
    
    Features:
    - Real-time performance tracking
    - Error pattern analysis
    - System health monitoring
    - Historical data collection
    - Performance optimization insights
    - Alerting for critical issues
    """
    
    # Signals for real-time monitoring
    metrics_updated = Signal(LoadingMetrics)
    health_updated = Signal(SystemHealthMetrics)
    performance_alert = Signal(str, str)  # alert_type, message
    
    def __init__(self, parent=None):
        """Initialize the universal loading monitor."""
        super().__init__(parent)
        
        self.logger = logging.getLogger("universal_loading_monitor")
        
        # Metrics storage
        self.loading_metrics: List[LoadingMetrics] = []
        self.performance_stats: Dict[str, PerformanceStats] = {}  # format_backend -> stats
        self.system_health_history: deque = deque(maxlen=1000)
        self.error_patterns: Dict[str, int] = defaultdict(int)
        
        # Active monitoring
        self.active_loadings: Dict[str, float] = {}  # model_path -> start_time
        self.monitoring_enabled = True
        self.max_history_size = 10000
        
        # Performance thresholds for alerts
        self.performance_thresholds = {
            'max_load_time': 300.0,  # 5 minutes
            'min_success_rate': 0.8,  # 80%
            'max_memory_usage': 0.9,  # 90% of available
            'max_error_rate': 0.2  # 20%
        }
        
        # Health monitoring timer
        self.health_timer = QTimer()
        self.health_timer.timeout.connect(self._collect_system_health)
        self.health_timer.start(5000)  # Every 5 seconds
        
        # Cleanup timer
        self.cleanup_timer = QTimer()
        self.cleanup_timer.timeout.connect(self._cleanup_old_data)
        self.cleanup_timer.start(300000)  # Every 5 minutes
        
        self.logger.info("Universal loading monitor initialized")
    
    def start_loading_monitoring(self, model_path: str, format_type: ModelFormat,
                               loading_plan: LoadingPlan) -> str:
        """
        Start monitoring a loading operation.
        
        Args:
            model_path: Path to the model being loaded
            format_type: Detected format type
            loading_plan: Loading plan from routing system
            
        Returns:
            Monitoring session ID
        """
        if not self.monitoring_enabled:
            return ""
        
        session_id = f"{model_path}_{int(time.time())}"
        start_time = time.time()
        
        # Record active loading
        self.active_loadings[session_id] = start_time
        
        # Create initial metrics
        metrics = LoadingMetrics(
            model_path=model_path,
            format_type=format_type,
            backend_used=loading_plan.primary_backend,
            success=False,  # Will be updated on completion
            start_time=start_time,
            end_time=0.0,
            total_duration=0.0,
            model_size_mb=loading_plan.model_info.file_size // (1024 * 1024),
            parameter_count=loading_plan.model_info.metadata.get('parameters'),
            quantization=loading_plan.model_info.metadata.get('quantization'),
            hardware_info=self._get_hardware_snapshot(),
            config_info=self._get_config_snapshot(loading_plan)
        )
        
        self.logger.info(f"Started monitoring loading: {session_id}")
        return session_id
    
    def record_stage_timing(self, session_id: str, stage: str, duration: float):
        """Record timing for a specific loading stage."""
        if not self.monitoring_enabled or session_id not in self.active_loadings:
            return
        
        # Find the metrics for this session
        metrics = self._find_active_metrics(session_id)
        if not metrics:
            return
        
        # Update stage timing
        if stage == "format_detection":
            metrics.format_detection_time = duration
        elif stage == "validation":
            metrics.validation_time = duration
        elif stage == "memory_check":
            metrics.memory_check_time = duration
        elif stage == "routing":
            metrics.routing_time = duration
        elif stage == "metadata_extraction":
            metrics.metadata_extraction_time = duration
        elif stage == "backend_loading":
            metrics.backend_loading_time = duration
        
        self.logger.debug(f"Recorded {stage} timing: {duration:.3f}s for {session_id}")
    
    def record_resource_usage(self, session_id: str, memory_mb: int, 
                            cpu_percent: float = 0.0, gpu_percent: float = 0.0):
        """Record resource usage during loading."""
        if not self.monitoring_enabled or session_id not in self.active_loadings:
            return
        
        metrics = self._find_active_metrics(session_id)
        if metrics:
            metrics.memory_usage_mb = memory_mb
            metrics.cpu_usage_percent = cpu_percent
            metrics.gpu_usage_percent = gpu_percent
    
    def record_backend_fallback(self, session_id: str, from_backend: str, 
                              to_backend: str, reason: str):
        """Record a backend fallback event."""
        if not self.monitoring_enabled or session_id not in self.active_loadings:
            return
        
        metrics = self._find_active_metrics(session_id)
        if metrics:
            metrics.fallback_attempts.append(f"{from_backend} -> {to_backend}: {reason}")
            metrics.backend_used = to_backend  # Update to final backend
        
        self.logger.info(f"Recorded fallback: {from_backend} -> {to_backend} ({reason})")
    
    def record_optimization(self, session_id: str, optimization: str):
        """Record an applied optimization."""
        if not self.monitoring_enabled or session_id not in self.active_loadings:
            return
        
        metrics = self._find_active_metrics(session_id)
        if metrics:
            metrics.optimization_applied.append(optimization)
        
        self.logger.debug(f"Recorded optimization: {optimization}")
    
    def complete_loading_monitoring(self, session_id: str, success: bool,
                                  error_message: Optional[str] = None,
                                  error_category: Optional[str] = None):
        """
        Complete monitoring for a loading operation.
        
        Args:
            session_id: Monitoring session ID
            success: Whether loading was successful
            error_message: Error message if failed
            error_category: Error category if failed
        """
        if not self.monitoring_enabled or session_id not in self.active_loadings:
            return
        
        end_time = time.time()
        start_time = self.active_loadings[session_id]
        total_duration = end_time - start_time
        
        # Find or create metrics
        metrics = self._find_active_metrics(session_id)
        if not metrics:
            # Create minimal metrics if not found
            metrics = LoadingMetrics(
                model_path=session_id.split('_')[0],
                format_type=ModelFormat.UNKNOWN,
                backend_used="unknown",
                success=success,
                start_time=start_time,
                end_time=end_time,
                total_duration=total_duration
            )
        
        # Update completion info
        metrics.success = success
        metrics.end_time = end_time
        metrics.total_duration = total_duration
        metrics.error_message = error_message
        metrics.error_category = error_category
        
        # Store completed metrics
        self.loading_metrics.append(metrics)
        
        # Update performance statistics
        self._update_performance_stats(metrics)
        
        # Check for performance alerts
        self._check_performance_alerts(metrics)
        
        # Record error patterns
        if not success and error_category:
            self.error_patterns[error_category] += 1
        
        # Clean up active loading
        del self.active_loadings[session_id]
        
        # Emit metrics update
        self.metrics_updated.emit(metrics)
        
        self.logger.info(
            f"Completed monitoring: {session_id} "
            f"(success: {success}, duration: {total_duration:.2f}s)"
        )
    
    def get_performance_summary(self, format_type: Optional[ModelFormat] = None,
                              backend_name: Optional[str] = None,
                              time_window_hours: int = 24) -> Dict[str, Any]:
        """
        Get performance summary for analysis.
        
        Args:
            format_type: Filter by format type (optional)
            backend_name: Filter by backend name (optional)
            time_window_hours: Time window for analysis
            
        Returns:
            Performance summary dictionary
        """
        cutoff_time = time.time() - (time_window_hours * 3600)
        
        # Filter metrics
        filtered_metrics = [
            m for m in self.loading_metrics
            if m.start_time >= cutoff_time
        ]
        
        if format_type:
            filtered_metrics = [m for m in filtered_metrics if m.format_type == format_type]
        
        if backend_name:
            filtered_metrics = [m for m in filtered_metrics if m.backend_used == backend_name]
        
        if not filtered_metrics:
            return {'error': 'No data available for the specified criteria'}
        
        # Calculate summary statistics
        total_loads = len(filtered_metrics)
        successful_loads = sum(1 for m in filtered_metrics if m.success)
        success_rate = successful_loads / total_loads if total_loads > 0 else 0.0
        
        load_times = [m.total_duration for m in filtered_metrics if m.success]
        avg_load_time = sum(load_times) / len(load_times) if load_times else 0.0
        min_load_time = min(load_times) if load_times else 0.0
        max_load_time = max(load_times) if load_times else 0.0
        
        # Format distribution
        format_distribution = defaultdict(int)
        for m in filtered_metrics:
            format_distribution[m.format_type.value] += 1
        
        # Backend distribution
        backend_distribution = defaultdict(int)
        for m in filtered_metrics:
            backend_distribution[m.backend_used] += 1
        
        # Error analysis
        error_distribution = defaultdict(int)
        for m in filtered_metrics:
            if not m.success and m.error_category:
                error_distribution[m.error_category] += 1
        
        # Resource usage
        memory_usage = [m.memory_usage_mb for m in filtered_metrics if m.memory_usage_mb > 0]
        avg_memory_usage = sum(memory_usage) / len(memory_usage) if memory_usage else 0.0
        
        return {
            'time_window_hours': time_window_hours,
            'total_loads': total_loads,
            'successful_loads': successful_loads,
            'success_rate': success_rate,
            'performance': {
                'avg_load_time': avg_load_time,
                'min_load_time': min_load_time,
                'max_load_time': max_load_time,
                'avg_memory_usage_mb': avg_memory_usage
            },
            'distributions': {
                'formats': dict(format_distribution),
                'backends': dict(backend_distribution),
                'errors': dict(error_distribution)
            },
            'recent_trends': self._calculate_trends(filtered_metrics)
        }
    
    def get_system_health_status(self) -> Dict[str, Any]:
        """Get current system health status."""
        if not self.system_health_history:
            return {'status': 'no_data'}
        
        latest = self.system_health_history[-1]
        
        # Calculate health score (0-100)
        health_score = 100
        
        if latest.cpu_usage > 80:
            health_score -= 20
        elif latest.cpu_usage > 60:
            health_score -= 10
        
        if latest.memory_usage > 90:
            health_score -= 30
        elif latest.memory_usage > 70:
            health_score -= 15
        
        if latest.error_rate > 0.2:
            health_score -= 25
        elif latest.error_rate > 0.1:
            health_score -= 10
        
        # Determine status
        if health_score >= 80:
            status = 'healthy'
        elif health_score >= 60:
            status = 'warning'
        else:
            status = 'critical'
        
        return {
            'status': status,
            'health_score': max(0, health_score),
            'metrics': asdict(latest),
            'recommendations': self._generate_health_recommendations(latest)
        }
    
    def export_metrics(self, file_path: str, format: str = 'json'):
        """
        Export metrics to file.
        
        Args:
            file_path: Output file path
            format: Export format ('json' or 'csv')
        """
        try:
            if format.lower() == 'json':
                data = {
                    'loading_metrics': [asdict(m) for m in self.loading_metrics],
                    'performance_stats': {
                        key: asdict(stats) for key, stats in self.performance_stats.items()
                    },
                    'system_health': [asdict(h) for h in self.system_health_history],
                    'error_patterns': dict(self.error_patterns),
                    'export_timestamp': time.time()
                }
                
                with open(file_path, 'w') as f:
                    json.dump(data, f, indent=2, default=str)
            
            elif format.lower() == 'csv':
                import csv
                
                with open(file_path, 'w', newline='') as f:
                    if self.loading_metrics:
                        writer = csv.DictWriter(f, fieldnames=asdict(self.loading_metrics[0]).keys())
                        writer.writeheader()
                        for metrics in self.loading_metrics:
                            writer.writerow(asdict(metrics))
            
            self.logger.info(f"Exported metrics to {file_path} ({format})")
            
        except Exception as e:
            self.logger.error(f"Failed to export metrics: {e}")
    
    def _find_active_metrics(self, session_id: str) -> Optional[LoadingMetrics]:
        """Find metrics for an active loading session."""
        # For now, create a new metrics object if not found
        # In a more sophisticated implementation, we'd maintain active metrics
        return None
    
    def _get_hardware_snapshot(self) -> Dict[str, Any]:
        """Get current hardware information snapshot."""
        try:
            import psutil
            
            return {
                'cpu_count': psutil.cpu_count(),
                'memory_total': psutil.virtual_memory().total,
                'memory_available': psutil.virtual_memory().available,
                'disk_usage': psutil.disk_usage('/').percent
            }
        except ImportError:
            return {}
    
    def _get_config_snapshot(self, loading_plan: LoadingPlan) -> Dict[str, Any]:
        """Get configuration snapshot for the loading plan."""
        return {
            'primary_backend': loading_plan.primary_backend,
            'fallback_backends': loading_plan.fallback_backends,
            'memory_requirements': loading_plan.memory_requirements,
            'hardware_config': loading_plan.hardware_config,
            'confidence': loading_plan.confidence
        }
    
    def _update_performance_stats(self, metrics: LoadingMetrics):
        """Update performance statistics with new metrics."""
        key = f"{metrics.format_type.value}_{metrics.backend_used}"
        
        if key not in self.performance_stats:
            self.performance_stats[key] = PerformanceStats(
                format_type=metrics.format_type,
                backend_name=metrics.backend_used
            )
        
        stats = self.performance_stats[key]
        stats.total_attempts += 1
        
        if metrics.success:
            stats.successful_loads += 1
            stats.recent_load_times.append(metrics.total_duration)
            
            # Update timing statistics
            if metrics.total_duration < stats.min_load_time:
                stats.min_load_time = metrics.total_duration
            if metrics.total_duration > stats.max_load_time:
                stats.max_load_time = metrics.total_duration
            
            # Update averages
            stats.avg_load_time = (
                (stats.avg_load_time * (stats.successful_loads - 1) + metrics.total_duration)
                / stats.successful_loads
            )
            
            stats.avg_memory_usage = (
                (stats.avg_memory_usage * (stats.successful_loads - 1) + metrics.memory_usage_mb)
                / stats.successful_loads
            )
        
        # Update success rate
        stats.success_rate = stats.successful_loads / stats.total_attempts
        stats.recent_success_rate = (
            sum(1 for t in stats.recent_load_times) / len(stats.recent_load_times)
            if stats.recent_load_times else 0.0
        )
    
    def _check_performance_alerts(self, metrics: LoadingMetrics):
        """Check for performance alerts based on metrics."""
        # Check load time threshold
        if metrics.success and metrics.total_duration > self.performance_thresholds['max_load_time']:
            self.performance_alert.emit(
                'slow_loading',
                f"Slow loading detected: {metrics.total_duration:.1f}s for {metrics.model_path}"
            )
        
        # Check memory usage
        if metrics.memory_usage_mb > 0:
            try:
                import psutil
                memory_percent = metrics.memory_usage_mb / (psutil.virtual_memory().total / (1024 * 1024))
                if memory_percent > self.performance_thresholds['max_memory_usage']:
                    self.performance_alert.emit(
                        'high_memory',
                        f"High memory usage: {memory_percent:.1%} for {metrics.model_path}"
                    )
            except ImportError:
                pass
        
        # Check success rate for backend
        key = f"{metrics.format_type.value}_{metrics.backend_used}"
        if key in self.performance_stats:
            stats = self.performance_stats[key]
            if (stats.total_attempts >= 5 and 
                stats.success_rate < self.performance_thresholds['min_success_rate']):
                self.performance_alert.emit(
                    'low_success_rate',
                    f"Low success rate: {stats.success_rate:.1%} for {key}"
                )
    
    def _collect_system_health(self):
        """Collect system health metrics."""
        try:
            import psutil
            
            health = SystemHealthMetrics(
                timestamp=time.time(),
                cpu_usage=psutil.cpu_percent(),
                memory_usage=psutil.virtual_memory().percent,
                gpu_usage=0.0,  # Would need GPU monitoring library
                disk_usage=psutil.disk_usage('/').percent,
                active_loadings=len(self.active_loadings),
                cache_hit_rate=0.0,  # Would need cache statistics
                error_rate=self._calculate_recent_error_rate()
            )
            
            self.system_health_history.append(health)
            self.health_updated.emit(health)
            
        except ImportError:
            # psutil not available
            pass
        except Exception as e:
            self.logger.warning(f"Failed to collect system health: {e}")
    
    def _calculate_recent_error_rate(self) -> float:
        """Calculate recent error rate (last hour)."""
        cutoff_time = time.time() - 3600  # 1 hour
        
        recent_metrics = [
            m for m in self.loading_metrics
            if m.start_time >= cutoff_time
        ]
        
        if not recent_metrics:
            return 0.0
        
        failed_count = sum(1 for m in recent_metrics if not m.success)
        return failed_count / len(recent_metrics)
    
    def _calculate_trends(self, metrics: List[LoadingMetrics]) -> Dict[str, Any]:
        """Calculate performance trends from metrics."""
        if len(metrics) < 2:
            return {}
        
        # Sort by time
        sorted_metrics = sorted(metrics, key=lambda m: m.start_time)
        
        # Split into two halves for trend calculation
        mid_point = len(sorted_metrics) // 2
        first_half = sorted_metrics[:mid_point]
        second_half = sorted_metrics[mid_point:]
        
        # Calculate averages for each half
        first_avg_time = sum(m.total_duration for m in first_half if m.success) / len(first_half)
        second_avg_time = sum(m.total_duration for m in second_half if m.success) / len(second_half)
        
        first_success_rate = sum(1 for m in first_half if m.success) / len(first_half)
        second_success_rate = sum(1 for m in second_half if m.success) / len(second_half)
        
        return {
            'load_time_trend': 'improving' if second_avg_time < first_avg_time else 'degrading',
            'success_rate_trend': 'improving' if second_success_rate > first_success_rate else 'degrading',
            'load_time_change_percent': ((second_avg_time - first_avg_time) / first_avg_time * 100) if first_avg_time > 0 else 0,
            'success_rate_change_percent': ((second_success_rate - first_success_rate) / first_success_rate * 100) if first_success_rate > 0 else 0
        }
    
    def _generate_health_recommendations(self, health: SystemHealthMetrics) -> List[str]:
        """Generate health recommendations based on current metrics."""
        recommendations = []
        
        if health.cpu_usage > 80:
            recommendations.append("High CPU usage detected. Consider closing other applications.")
        
        if health.memory_usage > 90:
            recommendations.append("High memory usage detected. Consider using smaller models or enabling memory optimizations.")
        
        if health.error_rate > 0.2:
            recommendations.append("High error rate detected. Check model files and backend configurations.")
        
        if health.active_loadings > 3:
            recommendations.append("Multiple concurrent loadings detected. Consider loading models sequentially.")
        
        return recommendations
    
    def _cleanup_old_data(self):
        """Clean up old monitoring data to prevent memory leaks."""
        # Keep only recent metrics
        if len(self.loading_metrics) > self.max_history_size:
            self.loading_metrics = self.loading_metrics[-self.max_history_size:]
        
        # Clean up old error patterns (keep only last 24 hours)
        cutoff_time = time.time() - 86400  # 24 hours
        
        # This is a simplified cleanup - in practice, we'd need timestamps for error patterns
        if len(self.error_patterns) > 100:
            # Keep only the most frequent errors
            sorted_errors = sorted(self.error_patterns.items(), key=lambda x: x[1], reverse=True)
            self.error_patterns = dict(sorted_errors[:50])
        
        self.logger.debug("Completed monitoring data cleanup")