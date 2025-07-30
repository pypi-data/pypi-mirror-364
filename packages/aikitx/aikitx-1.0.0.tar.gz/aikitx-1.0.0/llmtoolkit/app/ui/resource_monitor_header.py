"""
Resource Monitor Header

This module provides a resource monitoring header component that displays
real-time system metrics including CPU, RAM usage, and GPU details.

Features:
- Real-time CPU and RAM display updated every 2 seconds
- GPU details button that opens detailed GPU usage dialog
- Positioned below model loading section with matching width
- Integrated with universal model loading system
"""

import logging
import time
from typing import Optional, Dict, Any

from PySide6.QtWidgets import (
    QWidget, QHBoxLayout, QLabel, QPushButton, QVBoxLayout,
    QDialog, QTextEdit, QProgressBar, QFrame
)
from PySide6.QtCore import QTimer, Signal, Qt
from PySide6.QtGui import QFont

from llmtoolkit.app.core.event_bus import EventBus
from llmtoolkit.app.core.monitoring import GPUMonitor, SystemMetrics
from llmtoolkit.app.ui.theme_manager import ThemeManager
from llmtoolkit.app.ui.gpu_details_dialog import GPUDetailsDialog


class ResourceMonitorHeader(QWidget):
    """
    Resource monitoring header that displays real-time system metrics.
    Positioned below the model loading section with matching width.
    """
    
    # Signals
    gpu_details_requested = Signal()
    
    def __init__(self, event_bus: EventBus, theme_manager: ThemeManager, parent=None):
        """
        Initialize the resource monitor header.
        
        Args:
            event_bus: Application event bus
            theme_manager: Theme manager for styling
            parent: Parent widget
        """
        super().__init__(parent)
        
        self.logger = logging.getLogger("gguf_loader.ui.resource_monitor_header")
        self.event_bus = event_bus
        self.theme_manager = theme_manager
        
        # Resource monitoring components
        self.gpu_monitor = GPUMonitor()
        self.current_backend_name: Optional[str] = None
        self.model_active = False
        
        # Update timer for live metrics (2 seconds as per requirements)
        self.update_timer = QTimer()
        self.update_timer.timeout.connect(self._update_metrics)
        self.update_timer.setInterval(2000)  # 2 seconds
        
        # GPU details dialog
        self.gpu_details_dialog: Optional['GPUDetailsDialog'] = None
        
        # Initialize UI
        self._init_ui()
        
        # Connect to universal model loading events
        self._connect_events()
        
        # Initially hidden until model is loaded
        self.hide()
        
        self.logger.info("Resource monitor header initialized")
    
    def _init_ui(self):
        """Initialize the user interface."""
        # Main layout
        layout = QHBoxLayout(self)
        layout.setContentsMargins(10, 5, 10, 5)
        layout.setSpacing(15)
        
        # Create frame for better visual separation
        frame = QFrame()
        frame.setFrameStyle(QFrame.Box | QFrame.Raised)
        frame.setLineWidth(1)
        frame_layout = QHBoxLayout(frame)
        frame_layout.setContentsMargins(10, 5, 10, 5)
        frame_layout.setSpacing(15)
        
        # Backend name label
        self.backend_label = QLabel("Backend: Not loaded")
        self.backend_label.setObjectName("backend_label")
        font = QFont()
        font.setBold(True)
        self.backend_label.setFont(font)
        frame_layout.addWidget(self.backend_label)
        
        # Separator
        separator1 = QLabel("|")
        separator1.setObjectName("separator")
        frame_layout.addWidget(separator1)
        
        # RAM usage label
        self.ram_label = QLabel("RAM: --GB/--GB")
        self.ram_label.setObjectName("ram_label")
        frame_layout.addWidget(self.ram_label)
        
        # Separator
        separator2 = QLabel("|")
        separator2.setObjectName("separator")
        frame_layout.addWidget(separator2)
        
        # CPU usage label
        self.cpu_label = QLabel("CPU: --%")
        self.cpu_label.setObjectName("cpu_label")
        frame_layout.addWidget(self.cpu_label)
        
        # Stretch to push GPU button to the right
        frame_layout.addStretch()
        
        # GPU details button (always shown, text indicates availability)
        self.gpu_button = QPushButton("GPU Details")
        self.gpu_button.setObjectName("gpu_details_button")
        self.gpu_button.clicked.connect(self._show_gpu_details)
        frame_layout.addWidget(self.gpu_button)
        
        layout.addWidget(frame)
        
        # Apply theme styling
        self._apply_theme_styling()
        
        # Check for GPU availability
        self._check_gpu_availability()
    
    def _apply_theme_styling(self):
        """Apply theme styling to the header components."""
        colors = self.theme_manager.get_colors()
        
        # Main frame styling
        self.setStyleSheet(f"""
            QFrame {{
                background-color: {colors['surface']};
                border: 1px solid {colors['border']};
                border-radius: 5px;
            }}
            
            QLabel#backend_label {{
                color: {colors['primary']};
                font-weight: bold;
            }}
            
            QLabel#ram_label, QLabel#cpu_label {{
                color: {colors['text']};
                font-family: monospace;
            }}
            
            QLabel#separator {{
                color: {colors['text_secondary']};
            }}
            
            QPushButton#gpu_details_button {{
                background-color: {colors['primary']};
                color: white;
                border: none;
                padding: 5px 10px;
                border-radius: 3px;
                font-weight: bold;
            }}
            
            QPushButton#gpu_details_button:hover {{
                background-color: {colors['primary']};
                opacity: 0.8;
            }}
            
            QPushButton#gpu_details_button:pressed {{
                background-color: {colors['primary']};
                opacity: 0.6;
            }}
        """)
    
    def _connect_events(self):
        """Connect to universal model loading events."""
        self.event_bus.subscribe("universal.model.loaded", self._on_universal_model_loaded)
        self.event_bus.subscribe("universal.model.unloaded", self._on_universal_model_unloaded)
        self.event_bus.subscribe("universal.model.loading_failed", self._on_universal_loading_failed)
        
        # Also connect to legacy model events for backward compatibility
        self.event_bus.subscribe("model.loaded", self._on_legacy_model_loaded)
        self.event_bus.subscribe("model.unloaded", self._on_legacy_model_unloaded)
    
    def _check_gpu_availability(self):
        """Check if GPU is available and update button text accordingly."""
        try:
            gpu_metrics = self.gpu_monitor.get_gpu_metrics()
            gpu_available = len(gpu_metrics) > 0
            
            # Always show the button, but update text based on availability
            self.gpu_button.setVisible(True)
            
            if gpu_available:
                self.gpu_button.setText(f"GPU Details ({len(gpu_metrics)})")
                self.logger.info(f"GPU detected: {len(gpu_metrics)} GPU(s) available")
            else:
                self.gpu_button.setText("GPU Details (None)")
                self.logger.info("No GPU detected")
                
        except Exception as e:
            self.logger.warning(f"Error checking GPU availability: {e}")
            self.gpu_button.setText("GPU Details (Error)")
            self.gpu_button.setVisible(True)  # Still show button to display error info
    
    def show_model_loaded(self, backend_name: str):
        """
        Show header when model is loaded.
        
        Args:
            backend_name: Name of the backend being used
        """
        self.current_backend_name = backend_name
        self.model_active = True
        
        # Update backend label
        self.backend_label.setText(f"Backend: {backend_name}")
        
        # Show the header
        self.show()
        
        # Start metrics updates
        self.update_timer.start()
        
        self.logger.info(f"Resource monitor header shown for backend: {backend_name}")
    
    def hide_model_unloaded(self):
        """Hide header when model is unloaded."""
        self.current_backend_name = None
        self.model_active = False
        
        # Stop metrics updates
        self.update_timer.stop()
        
        # Hide the header
        self.hide()
        
        self.logger.info("Resource monitor header hidden - model unloaded")
    
    def _update_metrics(self):
        """Update CPU and RAM metrics every 2 seconds."""
        try:
            import psutil
            
            # Get CPU usage
            cpu_usage = psutil.cpu_percent(interval=None)
            
            # Get memory usage
            memory_info = psutil.virtual_memory()
            memory_used_gb = memory_info.used / (1024**3)
            memory_total_gb = memory_info.total / (1024**3)
            
            # Update labels
            self.cpu_label.setText(f"CPU: {cpu_usage:.0f}%")
            self.ram_label.setText(f"RAM: {memory_used_gb:.1f}GB/{memory_total_gb:.1f}GB")
            
            # Publish resource metrics event
            self.event_bus.publish("resource.monitor.updated", {
                'timestamp': time.time(),
                'cpu_usage': cpu_usage,
                'memory_used_gb': memory_used_gb,
                'memory_total_gb': memory_total_gb,
                'backend_name': self.current_backend_name,
                'model_active': self.model_active
            })
            
        except Exception as e:
            self.logger.error(f"Error updating metrics: {e}")
            self.cpu_label.setText("CPU: Error")
            self.ram_label.setText("RAM: Error")
    
    def _show_gpu_details(self):
        """Show GPU usage details dialog."""
        try:
            if self.gpu_details_dialog is None:
                self.gpu_details_dialog = GPUDetailsDialog(
                    self.gpu_monitor,
                    self
                )
            
            self.gpu_details_dialog.show()
            self.gpu_details_dialog.raise_()
            self.gpu_details_dialog.activateWindow()
            
            # Emit signal for external handling if needed
            self.gpu_details_requested.emit()
            
        except Exception as e:
            self.logger.error(f"Error showing GPU details: {e}")
    
    def _on_universal_model_loaded(self, loading_result):
        """Handle universal model loaded event."""
        try:
            backend_name = getattr(loading_result, 'backend_used', 'Unknown')
            self.show_model_loaded(backend_name)
        except Exception as e:
            self.logger.error(f"Error handling universal model loaded event: {e}")
    
    def _on_universal_model_unloaded(self, *args):
        """Handle universal model unloaded event."""
        self.hide_model_unloaded()
    
    def _on_universal_loading_failed(self, *args):
        """Handle universal model loading failed event."""
        self.hide_model_unloaded()
    
    def _on_legacy_model_loaded(self, backend_name, model_info=None):
        """Handle legacy model loaded event for backward compatibility."""
        self.show_model_loaded(backend_name)
    
    def _on_legacy_model_unloaded(self, *args):
        """Handle legacy model unloaded event for backward compatibility."""
        self.hide_model_unloaded()


