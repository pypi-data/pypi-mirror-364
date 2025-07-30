"""
Memory Manager

This module contains the MemoryManager class, which is responsible for
implementing efficient memory management strategies for large GGUF models.
"""

import os
import logging
import psutil
import threading
import time
from typing import Dict, List, Optional, Tuple, Set, Any, Union
from datetime import datetime, timedelta

from PySide6.QtCore import QObject, Signal, Slot, QTimer

class MemoryManager(QObject):
    """
    Manages memory for large GGUF models.
    
    This class is responsible for:
    - Monitoring system memory usage
    - Implementing memory optimization strategies
    - Providing memory usage statistics
    - Managing memory thresholds and alerts
    """
    
    # Signals
    memory_warning_signal = Signal(float, float)  # used_percentage, available_mb
    memory_critical_signal = Signal(float, float)  # used_percentage, available_mb
    memory_normal_signal = Signal(float, float)  # used_percentage, available_mb
    
    # Memory threshold levels
    MEMORY_WARNING_THRESHOLD = 75.0  # Percentage
    MEMORY_CRITICAL_THRESHOLD = 90.0  # Percentage
    
    def __init__(self, event_bus=None, config_manager=None, parent=None):
        """
        Initialize the memory manager.
        
        Args:
            event_bus: Optional event bus for publishing events
            config_manager: Optional configuration manager
            parent: Parent object
        """
        super().__init__(parent)
        self.logger = logging.getLogger("gguf_loader.memory_manager")
        self.event_bus = event_bus
        self.config_manager = config_manager
        
        # Memory monitoring state
        self.last_memory_state = "normal"  # "normal", "warning", "critical"
        self.monitoring_active = False
        self.memory_check_interval = 5000  # 5 seconds by default
        
        # Memory thresholds
        self.warning_threshold = self.MEMORY_WARNING_THRESHOLD
        self.critical_threshold = self.MEMORY_CRITICAL_THRESHOLD
        
        # Memory optimization settings
        self.enable_memory_mapping = True
        self.enable_lazy_loading = True
        self.enable_compression = False
        self.compression_level = 1  # 1-9, higher is more compression but slower
        
        # Memory monitoring timer
        self.memory_timer = QTimer(self)
        self.memory_timer.timeout.connect(self._check_memory_usage)
        
        # Load settings from configuration
        self._load_settings()
        
        self.logger.info("Memory manager initialized")
    
    def _load_settings(self):
        """Load settings from configuration."""
        if self.config_manager:
            # Memory thresholds
            self.warning_threshold = self.config_manager.get_value(
                "memory_warning_threshold", self.MEMORY_WARNING_THRESHOLD)
            self.critical_threshold = self.config_manager.get_value(
                "memory_critical_threshold", self.MEMORY_CRITICAL_THRESHOLD)
            
            # Memory check interval
            self.memory_check_interval = self.config_manager.get_value(
                "memory_check_interval_ms", 5000)
            
            # Memory optimization settings
            self.enable_memory_mapping = self.config_manager.get_value(
                "enable_memory_mapping", True)
            self.enable_lazy_loading = self.config_manager.get_value(
                "enable_lazy_loading", True)
            self.enable_compression = self.config_manager.get_value(
                "enable_compression", False)
            self.compression_level = self.config_manager.get_value(
                "compression_level", 1)
    
    def start_monitoring(self):
        """Start memory usage monitoring."""
        if not self.monitoring_active:
            self.logger.info("Starting memory monitoring")
            self.memory_timer.start(self.memory_check_interval)
            self.monitoring_active = True
            
            # Do an initial check
            self._check_memory_usage()
    
    def stop_monitoring(self):
        """Stop memory usage monitoring."""
        if self.monitoring_active:
            self.logger.info("Stopping memory monitoring")
            self.memory_timer.stop()
            self.monitoring_active = False
    
    def get_memory_info(self) -> Dict[str, Any]:
        """
        Get current memory usage information.
        
        Returns:
            Dictionary with memory usage information
        """
        memory = psutil.virtual_memory()
        
        return {
            "total": memory.total,
            "available": memory.available,
            "used": memory.used,
            "free": memory.free,
            "percent": memory.percent,
            "total_gb": memory.total / (1024 ** 3),
            "available_gb": memory.available / (1024 ** 3),
            "used_gb": memory.used / (1024 ** 3),
            "free_gb": memory.free / (1024 ** 3)
        }
    
    def estimate_model_memory_usage(self, file_path: str, load_type: str = "full") -> int:
        """
        Estimate memory usage for loading a model.
        
        Args:
            file_path: Path to the model file
            load_type: Type of loading ("full", "memory_mapped", "lazy")
            
        Returns:
            Estimated memory usage in bytes
        """
        try:
            # Get file size
            file_size = os.path.getsize(file_path)
            
            # Estimate based on load type
            if load_type == "memory_mapped":
                # Memory mapped files use less memory initially
                return int(file_size * 0.3)  # 30% of file size initially
            elif load_type == "lazy":
                # Lazy loading uses even less memory initially
                return int(file_size * 0.1)  # 10% of file size initially
            else:  # "full"
                # Full loading uses more memory due to data structures
                return int(file_size * 1.2)  # 120% of file size
                
        except Exception as e:
            self.logger.error(f"Error estimating memory usage: {e}")
            # Return a conservative estimate
            return 1024 * 1024 * 1024  # 1 GB
    
    def check_memory_availability(self, required_bytes: int) -> Tuple[bool, Dict[str, Any]]:
        """
        Check if there's enough memory available for a given requirement.
        
        Args:
            required_bytes: Required memory in bytes
            
        Returns:
            Tuple of (is_available, memory_info)
        """
        memory_info = self.get_memory_info()
        
        # Check if there's enough memory
        is_available = memory_info["available"] >= required_bytes
        
        return is_available, memory_info
    
    def suggest_load_strategy(self, file_path: str) -> Dict[str, Any]:
        """
        Suggest the best loading strategy for a model based on current memory conditions.
        
        Args:
            file_path: Path to the model file
            
        Returns:
            Dictionary with loading strategy recommendations
        """
        try:
            # Get file size
            file_size = os.path.getsize(file_path)
            
            # Get current memory info
            memory_info = self.get_memory_info()
            
            # Calculate available memory percentage
            available_percent = (memory_info["available"] / memory_info["total"]) * 100
            
            # Determine the best strategy
            if available_percent > 50 and memory_info["available"] > file_size * 1.5:
                # Plenty of memory available, use full loading for best performance
                strategy = "full"
                reason = "Sufficient memory available for optimal performance"
            elif self.enable_memory_mapping and available_percent > 25:
                # Moderate memory available, use memory mapping
                strategy = "memory_mapped"
                reason = "Memory mapping provides a good balance of performance and memory usage"
            elif self.enable_lazy_loading:
                # Limited memory, use lazy loading
                strategy = "lazy"
                reason = "Lazy loading minimizes initial memory usage"
            else:
                # Fall back to memory mapping if lazy loading is disabled
                strategy = "memory_mapped"
                reason = "Memory mapping selected as lazy loading is disabled"
            
            # If compression is enabled and memory is tight, suggest compression
            use_compression = self.enable_compression and available_percent < 30
            
            return {
                "strategy": strategy,
                "reason": reason,
                "use_compression": use_compression,
                "compression_level": self.compression_level if use_compression else 0,
                "estimated_memory_usage": self.estimate_model_memory_usage(file_path, strategy),
                "memory_info": memory_info
            }
            
        except Exception as e:
            self.logger.error(f"Error suggesting load strategy: {e}")
            # Return a conservative strategy
            return {
                "strategy": "memory_mapped",
                "reason": "Error occurred, using safe default strategy",
                "use_compression": self.enable_compression,
                "compression_level": self.compression_level if self.enable_compression else 0,
                "estimated_memory_usage": 0,
                "memory_info": self.get_memory_info()
            }
    
    def optimize_memory_usage(self) -> Dict[str, Any]:
        """
        Attempt to optimize memory usage by releasing caches and unused resources.
        
        Returns:
            Dictionary with optimization results
        """
        # Get memory info before optimization
        before = self.get_memory_info()
        
        # Perform Python garbage collection
        import gc
        gc.collect()
        
        # Release memory back to the OS if possible
        if hasattr(gc, 'mem_free'):
            gc.mem_free()
        
        # Get memory info after optimization
        after = self.get_memory_info()
        
        # Calculate improvement
        memory_freed = after["available"] - before["available"]
        percent_improvement = (memory_freed / before["total"]) * 100 if before["total"] > 0 else 0
        
        result = {
            "memory_freed": memory_freed,
            "memory_freed_mb": memory_freed / (1024 * 1024),
            "percent_improvement": percent_improvement,
            "before": before,
            "after": after
        }
        
        self.logger.info(f"Memory optimization freed {result['memory_freed_mb']:.2f} MB ({percent_improvement:.2f}%)")
        
        # Publish event if event bus is available
        if self.event_bus:
            self.event_bus.publish("memory.optimized", result)
        
        return result
    
    def _check_memory_usage(self) -> Dict[str, Any]:
        """
        Check current memory usage and emit signals if thresholds are crossed.
        
        Returns:
            Dictionary with memory usage information
        """
        # Get memory info
        memory_info = self.get_memory_info()
        used_percentage = memory_info["percent"]
        available_mb = memory_info["available"] / (1024 * 1024)
        
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
        
        return memory_info