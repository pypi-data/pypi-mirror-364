"""
Advanced Logging Configuration for Backend Troubleshooting

This module provides comprehensive logging configuration for backend operations,
performance monitoring, and troubleshooting.

Features:
- Structured logging with context information
- Performance-aware logging levels
- Backend-specific log filtering
- Log aggregation and analysis
- Real-time log streaming
"""

import logging
import logging.handlers
import json
import time
import threading
from typing import Dict, Any, Optional, List, Callable
from pathlib import Path
from dataclasses import dataclass, asdict
from collections import deque
import traceback


@dataclass
class LogEntry:
    """Structured log entry with context information."""
    timestamp: float
    level: str
    logger_name: str
    message: str
    backend_name: Optional[str] = None
    operation: Optional[str] = None
    model_path: Optional[str] = None
    duration_ms: Optional[float] = None
    memory_usage_mb: Optional[int] = None
    gpu_usage_percent: Optional[float] = None
    tokens_generated: Optional[int] = None
    error_type: Optional[str] = None
    stack_trace: Optional[str] = None
    thread_id: Optional[int] = None
    process_id: Optional[int] = None
    extra_context: Optional[Dict[str, Any]] = None


class ContextualFormatter(logging.Formatter):
    """Custom formatter that includes context information."""
    
    def __init__(self, include_context: bool = True):
        super().__init__()
        self.include_context = include_context
    
    def format(self, record: logging.LogRecord) -> str:
        # Base formatting
        timestamp = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(record.created))
        level = record.levelname
        logger_name = record.name
        message = record.getMessage()
        
        # Build base log line
        log_line = f"[{timestamp}] {level:8} {logger_name:20} | {message}"
        
        if not self.include_context:
            return log_line
        
        # Add context information if available
        context_parts = []
        
        # Backend context
        if hasattr(record, 'backend_name') and record.backend_name:
            context_parts.append(f"backend={record.backend_name}")
        
        # Operation context
        if hasattr(record, 'operation') and record.operation:
            context_parts.append(f"op={record.operation}")
        
        # Performance context
        if hasattr(record, 'duration_ms') and record.duration_ms is not None:
            context_parts.append(f"duration={record.duration_ms:.1f}ms")
        
        if hasattr(record, 'memory_usage_mb') and record.memory_usage_mb is not None:
            context_parts.append(f"memory={record.memory_usage_mb}MB")
        
        if hasattr(record, 'gpu_usage_percent') and record.gpu_usage_percent is not None:
            context_parts.append(f"gpu={record.gpu_usage_percent:.1f}%")
        
        # Model context
        if hasattr(record, 'model_path') and record.model_path:
            model_name = Path(record.model_path).name
            context_parts.append(f"model={model_name}")
        
        # Thread/process context
        if hasattr(record, 'thread_id') and record.thread_id:
            context_parts.append(f"thread={record.thread_id}")
        
        # Add context to log line
        if context_parts:
            context_str = " | ".join(context_parts)
            log_line += f" | {context_str}"
        
        # Add exception information
        if record.exc_info:
            log_line += "\n" + self.formatException(record.exc_info)
        
        return log_line


class JSONFormatter(logging.Formatter):
    """JSON formatter for structured logging."""
    
    def format(self, record: logging.LogRecord) -> str:
        log_entry = {
            'timestamp': record.created,
            'level': record.levelname,
            'logger': record.name,
            'message': record.getMessage(),
            'module': record.module,
            'function': record.funcName,
            'line': record.lineno
        }
        
        # Add context fields
        context_fields = [
            'backend_name', 'operation', 'model_path', 'duration_ms',
            'memory_usage_mb', 'gpu_usage_percent', 'error_type',
            'thread_id', 'process_id', 'extra_context'
        ]
        
        for field in context_fields:
            if hasattr(record, field):
                value = getattr(record, field)
                if value is not None:
                    log_entry[field] = value
        
        # Add exception information
        if record.exc_info:
            log_entry['exception'] = self.formatException(record.exc_info)
        
        return json.dumps(log_entry, default=str)


class PerformanceLogFilter(logging.Filter):
    """Filter that adds performance context to log records."""
    
    def __init__(self):
        super().__init__()
        self._operation_contexts = {}
        self._lock = threading.Lock()
    
    def filter(self, record: logging.LogRecord) -> bool:
        # Add thread and process IDs
        record.thread_id = threading.get_ident()
        record.process_id = os.getpid() if 'os' in globals() else None
        
        # Try to extract performance context from message or logger
        self._add_performance_context(record)
        
        return True
    
    def _add_performance_context(self, record: logging.LogRecord):
        """Add performance context to log record."""
        # Check if this is a backend-related log
        logger_parts = record.name.split('.')
        
        if 'backend' in logger_parts:
            # Extract backend name
            try:
                backend_idx = logger_parts.index('backend')
                if backend_idx + 1 < len(logger_parts):
                    record.backend_name = logger_parts[backend_idx + 1]
            except ValueError:
                pass
        
        # Check for operation context in message
        message = record.getMessage().lower()
        
        if 'loading' in message or 'load' in message:
            record.operation = 'load'
        elif 'generating' in message or 'generate' in message:
            record.operation = 'generate'
        elif 'unloading' in message or 'unload' in message:
            record.operation = 'unload'
        
        # Extract timing information from message
        import re
        
        # Look for duration patterns
        duration_match = re.search(r'(\d+\.?\d*)\s*(ms|milliseconds?)', message)
        if duration_match:
            record.duration_ms = float(duration_match.group(1))
        
        duration_match = re.search(r'(\d+\.?\d*)\s*s(?:econds?)?', message)
        if duration_match:
            record.duration_ms = float(duration_match.group(1)) * 1000
        
        # Look for memory usage patterns
        memory_match = re.search(r'(\d+)\s*mb', message)
        if memory_match:
            record.memory_usage_mb = int(memory_match.group(1))
        
        # Look for GPU usage patterns
        gpu_match = re.search(r'gpu.*?(\d+\.?\d*)%', message)
        if gpu_match:
            record.gpu_usage_percent = float(gpu_match.group(1))


class LogAggregator:
    """Aggregates and analyzes log entries for troubleshooting."""
    
    def __init__(self, max_entries: int = 10000):
        self.max_entries = max_entries
        self.log_entries: deque = deque(maxlen=max_entries)
        self.error_patterns: Dict[str, int] = {}
        self.performance_stats: Dict[str, List[float]] = {}
        self._lock = threading.Lock()
        self._callbacks: List[Callable[[LogEntry], None]] = []
    
    def add_log_entry(self, record: logging.LogRecord):
        """Add a log entry to the aggregator."""
        entry = LogEntry(
            timestamp=record.created,
            level=record.levelname,
            logger_name=record.name,
            message=record.getMessage(),
            backend_name=getattr(record, 'backend_name', None),
            operation=getattr(record, 'operation', None),
            model_path=getattr(record, 'model_path', None),
            duration_ms=getattr(record, 'duration_ms', None),
            memory_usage_mb=getattr(record, 'memory_usage_mb', None),
            gpu_usage_percent=getattr(record, 'gpu_usage_percent', None),
            error_type=getattr(record, 'error_type', None),
            stack_trace=self._get_stack_trace(record),
            thread_id=getattr(record, 'thread_id', None),
            process_id=getattr(record, 'process_id', None),
            extra_context=getattr(record, 'extra_context', None)
        )
        
        with self._lock:
            self.log_entries.append(entry)
            
            # Update error patterns
            if record.levelname in ['ERROR', 'CRITICAL']:
                error_key = f"{entry.backend_name or 'unknown'}:{entry.operation or 'unknown'}"
                self.error_patterns[error_key] = self.error_patterns.get(error_key, 0) + 1
            
            # Update performance stats
            if entry.duration_ms is not None and entry.operation:
                stats_key = f"{entry.backend_name or 'unknown'}:{entry.operation}"
                if stats_key not in self.performance_stats:
                    self.performance_stats[stats_key] = []
                self.performance_stats[stats_key].append(entry.duration_ms)
                
                # Keep only recent performance data
                if len(self.performance_stats[stats_key]) > 1000:
                    self.performance_stats[stats_key] = self.performance_stats[stats_key][-1000:]
        
        # Notify callbacks
        for callback in self._callbacks:
            try:
                callback(entry)
            except Exception as e:
                # Avoid logging errors in log processing
                pass
    
    def _get_stack_trace(self, record: logging.LogRecord) -> Optional[str]:
        """Extract stack trace from log record."""
        if record.exc_info:
            return ''.join(traceback.format_exception(*record.exc_info))
        return None
    
    def add_callback(self, callback: Callable[[LogEntry], None]):
        """Add callback for real-time log processing."""
        self._callbacks.append(callback)
    
    def remove_callback(self, callback: Callable[[LogEntry], None]):
        """Remove log processing callback."""
        if callback in self._callbacks:
            self._callbacks.remove(callback)
    
    def get_recent_logs(self, count: int = 100, 
                       level: Optional[str] = None,
                       backend_name: Optional[str] = None,
                       operation: Optional[str] = None) -> List[LogEntry]:
        """Get recent log entries with optional filtering."""
        with self._lock:
            entries = list(self.log_entries)
        
        # Apply filters
        if level:
            entries = [e for e in entries if e.level == level]
        
        if backend_name:
            entries = [e for e in entries if e.backend_name == backend_name]
        
        if operation:
            entries = [e for e in entries if e.operation == operation]
        
        # Return most recent
        return entries[-count:] if count > 0 else entries
    
    def get_error_summary(self) -> Dict[str, Any]:
        """Get summary of error patterns."""
        with self._lock:
            return {
                'error_patterns': dict(self.error_patterns),
                'total_errors': sum(self.error_patterns.values()),
                'unique_error_types': len(self.error_patterns)
            }
    
    def get_performance_summary(self) -> Dict[str, Any]:
        """Get performance statistics summary."""
        with self._lock:
            summary = {}
            
            for key, durations in self.performance_stats.items():
                if durations:
                    summary[key] = {
                        'count': len(durations),
                        'average_ms': sum(durations) / len(durations),
                        'min_ms': min(durations),
                        'max_ms': max(durations),
                        'recent_average_ms': sum(durations[-10:]) / min(10, len(durations))
                    }
            
            return summary
    
    def analyze_issues(self) -> Dict[str, Any]:
        """Analyze logs for common issues and patterns."""
        with self._lock:
            entries = list(self.log_entries)
        
        analysis = {
            'timestamp': time.time(),
            'total_entries': len(entries),
            'issues_found': [],
            'recommendations': []
        }
        
        # Analyze error patterns
        error_entries = [e for e in entries if e.level in ['ERROR', 'CRITICAL']]
        if error_entries:
            analysis['issues_found'].append({
                'type': 'errors',
                'count': len(error_entries),
                'description': f"Found {len(error_entries)} error entries"
            })
        
        # Analyze performance issues
        slow_operations = []
        for entry in entries:
            if entry.duration_ms and entry.duration_ms > 30000:  # > 30 seconds
                slow_operations.append(entry)
        
        if slow_operations:
            analysis['issues_found'].append({
                'type': 'slow_operations',
                'count': len(slow_operations),
                'description': f"Found {len(slow_operations)} slow operations (>30s)"
            })
        
        # Analyze memory usage
        high_memory_entries = [e for e in entries if e.memory_usage_mb and e.memory_usage_mb > 8192]  # > 8GB
        if high_memory_entries:
            analysis['issues_found'].append({
                'type': 'high_memory',
                'count': len(high_memory_entries),
                'description': f"Found {len(high_memory_entries)} high memory usage entries (>8GB)"
            })
        
        # Generate recommendations
        if error_entries:
            analysis['recommendations'].append("Review error logs for backend installation or configuration issues")
        
        if slow_operations:
            analysis['recommendations'].append("Consider optimizing GPU layers or switching to a faster backend")
        
        if high_memory_entries:
            analysis['recommendations'].append("Monitor memory usage and consider using smaller models or CPU mode")
        
        return analysis


class LoggingHandler(logging.Handler):
    """Custom logging handler that integrates with the monitoring system."""
    
    def __init__(self, aggregator: LogAggregator):
        super().__init__()
        self.aggregator = aggregator
    
    def emit(self, record: logging.LogRecord):
        """Emit a log record to the aggregator."""
        try:
            self.aggregator.add_log_entry(record)
        except Exception:
            # Avoid recursive logging errors
            pass


class LoggingManager:
    """Central manager for logging configuration and monitoring."""
    
    def __init__(self, log_dir: Optional[str] = None):
        self.log_dir = Path(log_dir) if log_dir else Path("logs")
        self.log_dir.mkdir(exist_ok=True)
        
        self.aggregator = LogAggregator()
        self.performance_filter = PerformanceLogFilter()
        self._configured = False
        self._handlers = []
    
    def configure_logging(self, 
                         level: str = "INFO",
                         enable_console: bool = True,
                         enable_file: bool = True,
                         enable_json: bool = False,
                         enable_aggregation: bool = True):
        """
        Configure comprehensive logging for the application.
        
        Args:
            level: Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
            enable_console: Enable console logging
            enable_file: Enable file logging
            enable_json: Enable JSON structured logging
            enable_aggregation: Enable log aggregation for analysis
        """
        if self._configured:
            return
        
        # Set root logger level
        root_logger = logging.getLogger()
        root_logger.setLevel(getattr(logging, level.upper()))
        
        # Clear existing handlers
        root_logger.handlers.clear()
        
        # Console handler
        if enable_console:
            console_handler = logging.StreamHandler()
            console_handler.setLevel(getattr(logging, level.upper()))
            console_handler.setFormatter(ContextualFormatter(include_context=True))
            console_handler.addFilter(self.performance_filter)
            root_logger.addHandler(console_handler)
            self._handlers.append(console_handler)
        
        # File handler
        if enable_file:
            file_handler = logging.handlers.RotatingFileHandler(
                self.log_dir / "backend.log",
                maxBytes=10*1024*1024,  # 10MB
                backupCount=5
            )
            file_handler.setLevel(getattr(logging, level.upper()))
            file_handler.setFormatter(ContextualFormatter(include_context=True))
            file_handler.addFilter(self.performance_filter)
            root_logger.addHandler(file_handler)
            self._handlers.append(file_handler)
        
        # JSON handler for structured logging
        if enable_json:
            json_handler = logging.handlers.RotatingFileHandler(
                self.log_dir / "backend.json",
                maxBytes=10*1024*1024,  # 10MB
                backupCount=5
            )
            json_handler.setLevel(getattr(logging, level.upper()))
            json_handler.setFormatter(JSONFormatter())
            json_handler.addFilter(self.performance_filter)
            root_logger.addHandler(json_handler)
            self._handlers.append(json_handler)
        
        # Aggregation handler
        if enable_aggregation:
            agg_handler = LoggingHandler(self.aggregator)
            agg_handler.setLevel(logging.DEBUG)  # Capture all levels for analysis
            agg_handler.addFilter(self.performance_filter)
            root_logger.addHandler(agg_handler)
            self._handlers.append(agg_handler)
        
        # Configure specific loggers
        self._configure_backend_loggers()
        
        self._configured = True
        logging.info("Logging system configured successfully")
    
    def _configure_backend_loggers(self):
        """Configure specific loggers for different components."""
        # Backend loggers
        backend_loggers = [
            'backend.manager',
            'backend.ctransformers',
            'backend.transformers',
            'backend.llamafile',
            'backend.llama_cpp_python'
        ]
        
        for logger_name in backend_loggers:
            logger = logging.getLogger(logger_name)
            logger.setLevel(logging.DEBUG)
        
        # Monitoring loggers
        monitoring_loggers = [
            'monitoring.performance',
            'monitoring.system',
            'monitoring.gpu',
            'monitoring.diagnostics'
        ]
        
        for logger_name in monitoring_loggers:
            logger = logging.getLogger(logger_name)
            logger.setLevel(logging.INFO)
        
        # Reduce verbosity of external libraries
        external_loggers = [
            'urllib3',
            'requests',
            'transformers',
            'torch'
        ]
        
        for logger_name in external_loggers:
            logger = logging.getLogger(logger_name)
            logger.setLevel(logging.WARNING)
    
    def get_log_analysis(self) -> Dict[str, Any]:
        """Get comprehensive log analysis."""
        return {
            'error_summary': self.aggregator.get_error_summary(),
            'performance_summary': self.aggregator.get_performance_summary(),
            'issue_analysis': self.aggregator.analyze_issues(),
            'recent_errors': [asdict(e) for e in self.aggregator.get_recent_logs(10, level='ERROR')],
            'recent_warnings': [asdict(e) for e in self.aggregator.get_recent_logs(10, level='WARNING')]
        }
    
    def export_logs(self, filepath: str, format: str = 'json', 
                   hours: int = 24, level: Optional[str] = None):
        """
        Export logs to file.
        
        Args:
            filepath: Output file path
            format: Export format ('json' or 'text')
            hours: Number of hours of logs to export
            level: Log level filter
        """
        cutoff_time = time.time() - (hours * 3600)
        entries = [e for e in self.aggregator.log_entries if e.timestamp >= cutoff_time]
        
        if level:
            entries = [e for e in entries if e.level == level]
        
        if format.lower() == 'json':
            with open(filepath, 'w') as f:
                json.dump([asdict(e) for e in entries], f, indent=2, default=str)
        else:
            with open(filepath, 'w') as f:
                for entry in entries:
                    timestamp = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(entry.timestamp))
                    f.write(f"[{timestamp}] {entry.level:8} {entry.logger_name:20} | {entry.message}\n")
                    if entry.stack_trace:
                        f.write(f"{entry.stack_trace}\n")
        
        logging.info(f"Exported {len(entries)} log entries to {filepath}")
    
    def cleanup(self):
        """Clean up logging resources."""
        if not self._configured:
            return
        
        # Remove all handlers
        root_logger = logging.getLogger()
        for handler in self._handlers:
            root_logger.removeHandler(handler)
            handler.close()
        
        self._handlers.clear()
        self._configured = False
        logging.info("Logging system cleaned up")


# Global logging manager instance
logging_manager = LoggingManager()


# Convenience functions for adding context to logs
def log_with_context(logger: logging.Logger, level: str, message: str, 
                    backend_name: Optional[str] = None,
                    operation: Optional[str] = None,
                    model_path: Optional[str] = None,
                    duration_ms: Optional[float] = None,
                    memory_usage_mb: Optional[int] = None,
                    gpu_usage_percent: Optional[float] = None,
                    tokens_generated: Optional[int] = None,
                    extra_context: Optional[Dict[str, Any]] = None):
    """Log a message with performance and context information."""
    record = logger.makeRecord(
        logger.name, getattr(logging, level.upper()), 
        "", 0, message, (), None
    )
    
    # Add context attributes
    if backend_name:
        record.backend_name = backend_name
    if operation:
        record.operation = operation
    if model_path:
        record.model_path = model_path
    if duration_ms is not None:
        record.duration_ms = duration_ms
    if memory_usage_mb is not None:
        record.memory_usage_mb = memory_usage_mb
    if gpu_usage_percent is not None:
        record.gpu_usage_percent = gpu_usage_percent
    if tokens_generated is not None:
        record.tokens_generated = tokens_generated
    if extra_context:
        record.extra_context = extra_context
    
    logger.handle(record)


def log_performance(logger: logging.Logger, backend_name: str, operation: str, 
                   duration_ms: float, success: bool = True, 
                   error_message: Optional[str] = None, **kwargs):
    """Log performance information for an operation."""
    level = "INFO" if success else "ERROR"
    message = f"{operation} completed in {duration_ms:.1f}ms"
    
    if not success and error_message:
        message += f" - Error: {error_message}"
    
    log_with_context(
        logger, level, message,
        backend_name=backend_name,
        operation=operation,
        duration_ms=duration_ms,
        **kwargs
    )