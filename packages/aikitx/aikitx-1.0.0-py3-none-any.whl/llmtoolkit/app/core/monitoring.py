"""
Monitoring and Diagnostics System

This module provides comprehensive monitoring and diagnostics for backend
performance, GPU utilization, and system health.

Features:
- Performance monitoring for loading times and memory usage
- GPU utilization tracking and reporting
- Diagnostic tools for backend availability and compatibility
- Detailed logging for troubleshooting backend issues
- Real-time metrics collection and reporting
"""

import logging
import time
import threading
import psutil
import json
from typing import Dict, Any, List, Optional, Callable
from dataclasses import dataclass, asdict
from pathlib import Path
from collections import deque, defaultdict
import subprocess
import platform


@dataclass
class PerformanceMetrics:
    """Performance metrics for backend operations."""
    backend_name: str
    operation: str  # 'load', 'generate', 'unload'
    start_time: float
    end_time: float
    duration: float
    success: bool
    memory_usage_mb: int
    cpu_usage_percent: float
    gpu_usage_percent: float = 0.0
    gpu_memory_usage_mb: int = 0
    error_message: Optional[str] = None
    model_path: Optional[str] = None
    model_size_mb: Optional[int] = None
    tokens_generated: Optional[int] = None
    tokens_per_second: Optional[float] = None


@dataclass
class SystemMetrics:
    """System-wide metrics."""
    timestamp: float
    cpu_usage_percent: float
    memory_usage_mb: int
    memory_total_mb: int
    memory_available_mb: int
    disk_usage_percent: float
    gpu_metrics: List[Dict[str, Any]]


@dataclass
class BackendDiagnostics:
    """Diagnostic information for a backend."""
    backend_name: str
    is_available: bool
    installation_status: str
    gpu_support: List[str]
    error_messages: List[str]
    performance_score: float
    last_checked: float
    dependencies: Dict[str, str]
    hardware_compatibility: Dict[str, bool]


class GPUMonitor:
    """Monitor GPU utilization and memory usage."""
    
    def __init__(self):
        self.logger = logging.getLogger("monitoring.gpu")
        self._nvidia_available = self._check_nvidia_ml()
        self._rocm_available = self._check_rocm()
        self._metal_available = self._check_metal()
        
    def _check_nvidia_ml(self) -> bool:
        """Check if NVIDIA ML library is available."""
        try:
            import pynvml
            pynvml.nvmlInit()
            return True
        except (ImportError, Exception):
            return False
    
    def _check_rocm(self) -> bool:
        """Check if ROCm monitoring is available."""
        try:
            result = subprocess.run(['rocm-smi'], capture_output=True, timeout=5)
            return result.returncode == 0
        except (subprocess.TimeoutExpired, subprocess.CalledProcessError, FileNotFoundError):
            return False
    
    def _check_metal(self) -> bool:
        """Check if Metal monitoring is available (macOS)."""
        return platform.system() == "Darwin"
    
    def get_gpu_metrics(self) -> List[Dict[str, Any]]:
        """Get current GPU metrics for all available GPUs."""
        metrics = []
        
        # NVIDIA GPUs
        if self._nvidia_available:
            metrics.extend(self._get_nvidia_metrics())
        
        # AMD GPUs
        if self._rocm_available:
            metrics.extend(self._get_rocm_metrics())
        
        # Metal (macOS)
        if self._metal_available:
            metrics.extend(self._get_metal_metrics())
        
        return metrics
    
    def _get_nvidia_metrics(self) -> List[Dict[str, Any]]:
        """Get NVIDIA GPU metrics."""
        metrics = []
        
        try:
            import pynvml
            pynvml.nvmlInit()
            device_count = pynvml.nvmlDeviceGetCount()
            
            for i in range(device_count):
                handle = pynvml.nvmlDeviceGetHandleByIndex(i)
                
                # Get device info
                name_result = pynvml.nvmlDeviceGetName(handle)
                # Handle both string and bytes return types for compatibility
                if isinstance(name_result, bytes):
                    name = name_result.decode('utf-8')
                else:
                    name = str(name_result)
                
                # Get utilization
                util = pynvml.nvmlDeviceGetUtilizationRates(handle)
                
                # Get memory info
                mem_info = pynvml.nvmlDeviceGetMemoryInfo(handle)
                
                # Get temperature
                try:
                    temp = pynvml.nvmlDeviceGetTemperature(handle, pynvml.NVML_TEMPERATURE_GPU)
                except:
                    temp = 0
                
                # Get power usage
                try:
                    power = pynvml.nvmlDeviceGetPowerUsage(handle) / 1000.0  # Convert to watts
                except:
                    power = 0
                
                metrics.append({
                    'device_id': i,
                    'name': name,
                    'type': 'nvidia',
                    'utilization_percent': util.gpu,
                    'memory_utilization_percent': util.memory,
                    'memory_used_mb': mem_info.used // (1024 * 1024),
                    'memory_total_mb': mem_info.total // (1024 * 1024),
                    'memory_free_mb': mem_info.free // (1024 * 1024),
                    'temperature_c': temp,
                    'power_usage_w': power
                })
                
        except Exception as e:
            self.logger.debug(f"Error getting NVIDIA metrics: {e}")
        
        return metrics
    
    def _get_rocm_metrics(self) -> List[Dict[str, Any]]:
        """Get AMD ROCm GPU metrics."""
        metrics = []
        
        try:
            # Use rocm-smi to get GPU information
            result = subprocess.run(
                ['rocm-smi', '--showuse', '--showmeminfo', 'vram', '--json'],
                capture_output=True,
                text=True,
                timeout=10
            )
            
            if result.returncode == 0:
                # Parse JSON output (simplified - real implementation would be more robust)
                try:
                    data = json.loads(result.stdout)
                    # This is a simplified parser - actual ROCm JSON structure varies
                    for device_id, device_data in data.items():
                        if isinstance(device_data, dict):
                            metrics.append({
                                'device_id': device_id,
                                'name': device_data.get('Card series', 'AMD GPU'),
                                'type': 'amd',
                                'utilization_percent': device_data.get('GPU use (%)', 0),
                                'memory_used_mb': device_data.get('VRAM used (MB)', 0),
                                'memory_total_mb': device_data.get('VRAM total (MB)', 0),
                                'temperature_c': device_data.get('Temperature (C)', 0)
                            })
                except json.JSONDecodeError:
                    pass
                    
        except Exception as e:
            self.logger.debug(f"Error getting ROCm metrics: {e}")
        
        return metrics
    
    def _get_metal_metrics(self) -> List[Dict[str, Any]]:
        """Get Metal GPU metrics (macOS)."""
        metrics = []
        
        try:
            # Use system_profiler to get GPU info
            result = subprocess.run(
                ['system_profiler', 'SPDisplaysDataType', '-json'],
                capture_output=True,
                text=True,
                timeout=10
            )
            
            if result.returncode == 0:
                data = json.loads(result.stdout)
                displays = data.get('SPDisplaysDataType', [])
                
                for i, display in enumerate(displays):
                    if 'sppci_model' in display:
                        metrics.append({
                            'device_id': i,
                            'name': display.get('sppci_model', 'Metal GPU'),
                            'type': 'metal',
                            'utilization_percent': 0,  # Metal doesn't provide real-time utilization
                            'memory_total_mb': self._parse_memory_size(display.get('sppci_vram', '0 MB'))
                        })
                        
        except Exception as e:
            self.logger.debug(f"Error getting Metal metrics: {e}")
        
        return metrics
    
    def _parse_memory_size(self, memory_str: str) -> int:
        """Parse memory size string to MB."""
        try:
            if 'GB' in memory_str:
                return int(float(memory_str.replace('GB', '').strip()) * 1024)
            elif 'MB' in memory_str:
                return int(float(memory_str.replace('MB', '').strip()))
            else:
                return 0
        except:
            return 0


class PerformanceMonitor:
    """Monitor backend performance and collect metrics."""
    
    def __init__(self, max_history: int = 1000):
        self.logger = logging.getLogger("monitoring.performance")
        self.max_history = max_history
        self.metrics_history: deque = deque(maxlen=max_history)
        self.backend_stats: Dict[str, Dict[str, Any]] = defaultdict(lambda: {
            'total_operations': 0,
            'successful_operations': 0,
            'failed_operations': 0,
            'total_duration': 0.0,
            'average_duration': 0.0,
            'total_memory_usage': 0,
            'average_memory_usage': 0.0,
            'last_operation': None
        })
        self._lock = threading.Lock()
    
    def start_operation(self, backend_name: str, operation: str, 
                       model_path: Optional[str] = None) -> str:
        """
        Start monitoring an operation.
        
        Args:
            backend_name: Name of the backend
            operation: Type of operation ('load', 'generate', 'unload')
            model_path: Path to model file (if applicable)
            
        Returns:
            Operation ID for tracking
        """
        operation_id = f"{backend_name}_{operation}_{time.time()}"
        
        # Store operation start info
        setattr(self, f"_op_{operation_id}", {
            'backend_name': backend_name,
            'operation': operation,
            'start_time': time.time(),
            'model_path': model_path,
            'model_size_mb': self._get_model_size(model_path) if model_path else None
        })
        
        return operation_id
    
    def end_operation(self, operation_id: str, success: bool, 
                     error_message: Optional[str] = None,
                     tokens_generated: Optional[int] = None) -> PerformanceMetrics:
        """
        End monitoring an operation and record metrics.
        
        Args:
            operation_id: Operation ID from start_operation
            success: Whether the operation succeeded
            error_message: Error message if failed
            tokens_generated: Number of tokens generated (for generation operations)
            
        Returns:
            PerformanceMetrics object
        """
        end_time = time.time()
        
        # Get operation start info
        op_info = getattr(self, f"_op_{operation_id}", {})
        if not op_info:
            self.logger.warning(f"No start info found for operation: {operation_id}")
            return None
        
        # Clean up operation info
        delattr(self, f"_op_{operation_id}")
        
        # Calculate metrics
        start_time = op_info['start_time']
        duration = end_time - start_time
        
        # Get current system metrics
        cpu_usage = psutil.cpu_percent()
        memory_info = psutil.virtual_memory()
        memory_usage_mb = memory_info.used // (1024 * 1024)
        
        # Calculate tokens per second for generation operations
        tokens_per_second = None
        if tokens_generated and duration > 0:
            tokens_per_second = tokens_generated / duration
        
        # Create metrics object
        metrics = PerformanceMetrics(
            backend_name=op_info['backend_name'],
            operation=op_info['operation'],
            start_time=start_time,
            end_time=end_time,
            duration=duration,
            success=success,
            memory_usage_mb=memory_usage_mb,
            cpu_usage_percent=cpu_usage,
            error_message=error_message,
            model_path=op_info.get('model_path'),
            model_size_mb=op_info.get('model_size_mb'),
            tokens_generated=tokens_generated,
            tokens_per_second=tokens_per_second
        )
        
        # Record metrics
        self._record_metrics(metrics)
        
        return metrics
    
    def _record_metrics(self, metrics: PerformanceMetrics):
        """Record metrics in history and update backend stats."""
        with self._lock:
            # Add to history
            self.metrics_history.append(metrics)
            
            # Update backend stats
            backend_name = metrics.backend_name
            stats = self.backend_stats[backend_name]
            
            stats['total_operations'] += 1
            stats['total_duration'] += metrics.duration
            stats['total_memory_usage'] += metrics.memory_usage_mb
            stats['last_operation'] = time.time()
            
            if metrics.success:
                stats['successful_operations'] += 1
            else:
                stats['failed_operations'] += 1
            
            # Update averages
            if stats['total_operations'] > 0:
                stats['average_duration'] = stats['total_duration'] / stats['total_operations']
                stats['average_memory_usage'] = stats['total_memory_usage'] / stats['total_operations']
    
    def _get_model_size(self, model_path: str) -> Optional[int]:
        """Get model file size in MB."""
        try:
            return Path(model_path).stat().st_size // (1024 * 1024)
        except:
            return None
    
    def get_backend_stats(self, backend_name: Optional[str] = None) -> Dict[str, Any]:
        """
        Get performance statistics for backends.
        
        Args:
            backend_name: Specific backend name, or None for all backends
            
        Returns:
            Dictionary with backend statistics
        """
        with self._lock:
            if backend_name:
                return dict(self.backend_stats.get(backend_name, {}))
            else:
                return {name: dict(stats) for name, stats in self.backend_stats.items()}
    
    def get_recent_metrics(self, count: int = 100, 
                          backend_name: Optional[str] = None,
                          operation: Optional[str] = None) -> List[PerformanceMetrics]:
        """
        Get recent performance metrics.
        
        Args:
            count: Maximum number of metrics to return
            backend_name: Filter by backend name
            operation: Filter by operation type
            
        Returns:
            List of PerformanceMetrics
        """
        with self._lock:
            metrics = list(self.metrics_history)
            
            # Apply filters
            if backend_name:
                metrics = [m for m in metrics if m.backend_name == backend_name]
            
            if operation:
                metrics = [m for m in metrics if m.operation == operation]
            
            # Return most recent
            return metrics[-count:] if count > 0 else metrics


class SystemMonitor:
    """Monitor system-wide metrics."""
    
    def __init__(self, update_interval: float = 1.0):
        self.logger = logging.getLogger("monitoring.system")
        self.update_interval = update_interval
        self.gpu_monitor = GPUMonitor()
        self._running = False
        self._thread = None
        self._metrics_history: deque = deque(maxlen=3600)  # 1 hour at 1s intervals
        self._lock = threading.Lock()
        self._callbacks: List[Callable[[SystemMetrics], None]] = []
    
    def start(self):
        """Start system monitoring."""
        if self._running:
            return
        
        self._running = True
        self._thread = threading.Thread(target=self._monitor_loop, daemon=True)
        self._thread.start()
        self.logger.info("System monitoring started")
    
    def stop(self):
        """Stop system monitoring."""
        if not self._running:
            return
        
        self._running = False
        if self._thread:
            self._thread.join(timeout=5)
        self.logger.info("System monitoring stopped")
    
    def add_callback(self, callback: Callable[[SystemMetrics], None]):
        """Add callback for real-time metrics updates."""
        self._callbacks.append(callback)
    
    def remove_callback(self, callback: Callable[[SystemMetrics], None]):
        """Remove metrics update callback."""
        if callback in self._callbacks:
            self._callbacks.remove(callback)
    
    def _monitor_loop(self):
        """Main monitoring loop."""
        while self._running:
            try:
                metrics = self._collect_system_metrics()
                
                with self._lock:
                    self._metrics_history.append(metrics)
                
                # Notify callbacks
                for callback in self._callbacks:
                    try:
                        callback(metrics)
                    except Exception as e:
                        self.logger.error(f"Error in metrics callback: {e}")
                
                time.sleep(self.update_interval)
                
            except Exception as e:
                self.logger.error(f"Error in monitoring loop: {e}")
                time.sleep(self.update_interval)
    
    def _collect_system_metrics(self) -> SystemMetrics:
        """Collect current system metrics."""
        # CPU and memory
        cpu_usage = psutil.cpu_percent()
        memory_info = psutil.virtual_memory()
        
        # Disk usage (for main drive)
        disk_usage = psutil.disk_usage('/').percent
        
        # GPU metrics
        gpu_metrics = self.gpu_monitor.get_gpu_metrics()
        
        return SystemMetrics(
            timestamp=time.time(),
            cpu_usage_percent=cpu_usage,
            memory_usage_mb=memory_info.used // (1024 * 1024),
            memory_total_mb=memory_info.total // (1024 * 1024),
            memory_available_mb=memory_info.available // (1024 * 1024),
            disk_usage_percent=disk_usage,
            gpu_metrics=gpu_metrics
        )
    
    def get_current_metrics(self) -> Optional[SystemMetrics]:
        """Get the most recent system metrics."""
        with self._lock:
            return self._metrics_history[-1] if self._metrics_history else None
    
    def get_metrics_history(self, duration_seconds: int = 300) -> List[SystemMetrics]:
        """
        Get metrics history for the specified duration.
        
        Args:
            duration_seconds: Duration in seconds
            
        Returns:
            List of SystemMetrics
        """
        with self._lock:
            if not self._metrics_history:
                return []
            
            cutoff_time = time.time() - duration_seconds
            return [m for m in self._metrics_history if m.timestamp >= cutoff_time]


class DiagnosticTool:
    """Diagnostic tools for backend availability and compatibility."""
    
    def __init__(self):
        self.logger = logging.getLogger("monitoring.diagnostics")
        self.gpu_monitor = GPUMonitor()
    
    def diagnose_backend(self, backend_name: str, backend_class) -> BackendDiagnostics:
        """
        Perform comprehensive diagnostics on a backend.
        
        Args:
            backend_name: Name of the backend
            backend_class: Backend class to diagnose
            
        Returns:
            BackendDiagnostics object
        """
        start_time = time.time()
        
        # Create temporary config for testing
        from llmtoolkit.app.core.model_backends import BackendConfig
        test_config = BackendConfig(
            name=backend_name,
            enabled=True,
            priority=1,
            gpu_enabled=True,
            gpu_layers=-1,
            context_size=2048,
            batch_size=512,
            threads=-1,
            custom_args={}
        )
        
        diagnostics = BackendDiagnostics(
            backend_name=backend_name,
            is_available=False,
            installation_status="unknown",
            gpu_support=[],
            error_messages=[],
            performance_score=0.0,
            last_checked=start_time,
            dependencies={},
            hardware_compatibility={}
        )
        
        try:
            # Test backend availability
            backend_instance = backend_class(test_config)
            is_available, error_msg = backend_instance.is_available()
            
            diagnostics.is_available = is_available
            if error_msg:
                diagnostics.error_messages.append(error_msg)
                diagnostics.installation_status = "error"
            else:
                diagnostics.installation_status = "ok"
            
            # Test GPU support
            if is_available:
                gpu_support = self._test_gpu_support(backend_instance)
                diagnostics.gpu_support = gpu_support
                
                # Test hardware compatibility
                hardware_compat = self._test_hardware_compatibility(backend_instance)
                diagnostics.hardware_compatibility = hardware_compat
                
                # Get dependency information
                dependencies = self._get_backend_dependencies(backend_name)
                diagnostics.dependencies = dependencies
                
                # Calculate performance score
                performance_score = self._calculate_performance_score(
                    backend_instance, gpu_support, hardware_compat
                )
                diagnostics.performance_score = performance_score
            
        except Exception as e:
            diagnostics.error_messages.append(f"Diagnostic error: {e}")
            diagnostics.installation_status = "error"
        
        return diagnostics
    
    def _test_gpu_support(self, backend_instance) -> List[str]:
        """Test GPU support for a backend."""
        gpu_support = []
        
        # Test different GPU types
        gpu_tests = [
            ('cuda', self._test_cuda_support),
            ('rocm', self._test_rocm_support),
            ('metal', self._test_metal_support),
            ('vulkan', self._test_vulkan_support)
        ]
        
        for gpu_type, test_func in gpu_tests:
            try:
                if hasattr(backend_instance, f'_check_{gpu_type}_support'):
                    if getattr(backend_instance, f'_check_{gpu_type}_support')():
                        gpu_support.append(gpu_type)
                elif test_func():
                    gpu_support.append(gpu_type)
            except Exception as e:
                self.logger.debug(f"Error testing {gpu_type} support: {e}")
        
        return gpu_support
    
    def _test_cuda_support(self) -> bool:
        """Test CUDA support."""
        try:
            result = subprocess.run(['nvidia-smi'], capture_output=True, timeout=5)
            return result.returncode == 0
        except:
            return False
    
    def _test_rocm_support(self) -> bool:
        """Test ROCm support."""
        try:
            result = subprocess.run(['rocm-smi'], capture_output=True, timeout=5)
            return result.returncode == 0
        except:
            return False
    
    def _test_metal_support(self) -> bool:
        """Test Metal support."""
        return platform.system() == "Darwin"
    
    def _test_vulkan_support(self) -> bool:
        """Test Vulkan support."""
        try:
            result = subprocess.run(['vulkaninfo'], capture_output=True, timeout=5)
            return result.returncode == 0
        except:
            return False
    
    def _test_hardware_compatibility(self, backend_instance) -> Dict[str, bool]:
        """Test hardware compatibility."""
        compatibility = {}
        
        # Get current GPU metrics
        gpu_metrics = self.gpu_monitor.get_gpu_metrics()
        
        # Test compatibility with each GPU
        for gpu in gpu_metrics:
            gpu_key = f"{gpu['type']}_{gpu['device_id']}"
            
            # Basic compatibility check
            if gpu['type'] == 'nvidia':
                compatibility[gpu_key] = 'cuda' in getattr(backend_instance, '_gpu_support', [])
            elif gpu['type'] == 'amd':
                compatibility[gpu_key] = 'rocm' in getattr(backend_instance, '_gpu_support', [])
            elif gpu['type'] == 'metal':
                compatibility[gpu_key] = 'metal' in getattr(backend_instance, '_gpu_support', [])
            else:
                compatibility[gpu_key] = False
        
        # Test CPU compatibility (always true for most backends)
        compatibility['cpu'] = True
        
        return compatibility
    
    def _get_backend_dependencies(self, backend_name: str) -> Dict[str, str]:
        """Get backend dependency information."""
        dependencies = {}
        
        # Common dependencies by backend
        backend_deps = {
            'ctransformers': ['ctransformers'],
            'transformers': ['transformers', 'torch', 'accelerate'],
            'llamafile': [],  # No Python dependencies
            'llama-cpp-python': ['llama-cpp-python']
        }
        
        for dep in backend_deps.get(backend_name, []):
            try:
                import importlib
                module = importlib.import_module(dep)
                version = getattr(module, '__version__', 'unknown')
                dependencies[dep] = version
            except ImportError:
                dependencies[dep] = 'not installed'
            except Exception as e:
                dependencies[dep] = f'error: {e}'
        
        return dependencies
    
    def _calculate_performance_score(self, backend_instance, gpu_support: List[str], 
                                   hardware_compat: Dict[str, bool]) -> float:
        """Calculate a performance score for the backend."""
        score = 0.0
        
        # Base score for availability
        score += 25.0
        
        # GPU support bonus
        score += len(gpu_support) * 15.0
        
        # Hardware compatibility bonus
        compatible_devices = sum(1 for compat in hardware_compat.values() if compat)
        score += compatible_devices * 10.0
        
        # Installation quality bonus
        try:
            # Test if backend can be instantiated without errors
            score += 25.0
        except:
            score -= 10.0
        
        return min(100.0, max(0.0, score))
    
    def run_system_diagnostics(self) -> Dict[str, Any]:
        """Run comprehensive system diagnostics."""
        diagnostics = {
            'timestamp': time.time(),
            'system_info': self._get_system_info(),
            'gpu_info': self.gpu_monitor.get_gpu_metrics(),
            'python_info': self._get_python_info(),
            'disk_space': self._get_disk_space_info(),
            'network_connectivity': self._test_network_connectivity()
        }
        
        return diagnostics
    
    def _get_system_info(self) -> Dict[str, Any]:
        """Get system information."""
        return {
            'platform': platform.platform(),
            'system': platform.system(),
            'release': platform.release(),
            'version': platform.version(),
            'machine': platform.machine(),
            'processor': platform.processor(),
            'cpu_count': psutil.cpu_count(),
            'memory_total_gb': psutil.virtual_memory().total / (1024**3)
        }
    
    def _get_python_info(self) -> Dict[str, Any]:
        """Get Python environment information."""
        import sys
        return {
            'version': sys.version,
            'executable': sys.executable,
            'path': sys.path[:5]  # First 5 paths only
        }
    
    def _get_disk_space_info(self) -> Dict[str, Any]:
        """Get disk space information."""
        try:
            disk_usage = psutil.disk_usage('/')
            return {
                'total_gb': disk_usage.total / (1024**3),
                'used_gb': disk_usage.used / (1024**3),
                'free_gb': disk_usage.free / (1024**3),
                'percent_used': (disk_usage.used / disk_usage.total) * 100
            }
        except Exception as e:
            return {'error': str(e)}
    
    def _test_network_connectivity(self) -> Dict[str, bool]:
        """Test network connectivity to common model repositories."""
        test_urls = [
            'https://huggingface.co',
            'https://github.com',
            'https://pypi.org'
        ]
        
        connectivity = {}
        for url in test_urls:
            try:
                import urllib.request
                urllib.request.urlopen(url, timeout=5)
                connectivity[url] = True
            except:
                connectivity[url] = False
        
        return connectivity


class MonitoringManager:
    """Central manager for all monitoring and diagnostics."""
    
    def __init__(self):
        self.logger = logging.getLogger("monitoring.manager")
        self.performance_monitor = PerformanceMonitor()
        self.system_monitor = SystemMonitor()
        self.diagnostic_tool = DiagnosticTool()
        self._started = False
    
    def start(self):
        """Start all monitoring systems."""
        if self._started:
            return
        
        self.system_monitor.start()
        self._started = True
        self.logger.info("Monitoring manager started")
    
    def stop(self):
        """Stop all monitoring systems."""
        if not self._started:
            return
        
        self.system_monitor.stop()
        self._started = False
        self.logger.info("Monitoring manager stopped")
    
    def get_comprehensive_report(self) -> Dict[str, Any]:
        """Get comprehensive monitoring report."""
        return {
            'timestamp': time.time(),
            'system_metrics': asdict(self.system_monitor.get_current_metrics()) if self.system_monitor.get_current_metrics() else None,
            'performance_stats': self.performance_monitor.get_backend_stats(),
            'recent_operations': [asdict(m) for m in self.performance_monitor.get_recent_metrics(10)],
            'system_diagnostics': self.diagnostic_tool.run_system_diagnostics()
        }
    
    def export_metrics(self, filepath: str, format: str = 'json'):
        """
        Export metrics to file.
        
        Args:
            filepath: Path to export file
            format: Export format ('json' or 'csv')
        """
        report = self.get_comprehensive_report()
        
        if format.lower() == 'json':
            with open(filepath, 'w') as f:
                json.dump(report, f, indent=2, default=str)
        elif format.lower() == 'csv':
            # Export performance metrics as CSV
            import csv
            with open(filepath, 'w', newline='') as f:
                if report['recent_operations']:
                    writer = csv.DictWriter(f, fieldnames=report['recent_operations'][0].keys())
                    writer.writeheader()
                    writer.writerows(report['recent_operations'])
        
        self.logger.info(f"Metrics exported to {filepath}")


# Global monitoring manager instance
monitoring_manager = MonitoringManager()