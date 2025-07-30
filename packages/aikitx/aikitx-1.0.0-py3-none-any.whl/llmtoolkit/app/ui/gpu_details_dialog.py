"""
GPU Details Dialog

This module provides a dialog for displaying detailed GPU usage information
with auto-refresh functionality and user-friendly formatting.

Features:
- Detailed GPU information display
- Auto-refresh every 5 seconds
- User-friendly metric formatting
- Handles cases where GPU is not available
- Dark theme integration
"""

import logging
import time
from typing import Dict, Any, List, Optional

from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, 
    QTextEdit, QFrame, QScrollArea, QWidget, QGroupBox,
    QGridLayout, QProgressBar, QCheckBox
)
from PySide6.QtCore import Qt, QTimer, Signal
from PySide6.QtGui import QFont

from llmtoolkit.app.core.monitoring import GPUMonitor
from llmtoolkit.app.ui.theme_manager import ThemeManager


class GPUDetailsDialog(QDialog):
    """
    Dialog showing detailed GPU usage information.
    
    Features:
    - Real-time GPU metrics display
    - Auto-refresh every 5 seconds
    - User-friendly formatting
    - Handles GPU unavailable cases
    - Dark theme integration
    """
    
    # Signals
    refresh_requested = Signal()
    auto_refresh_toggled = Signal(bool)
    
    def __init__(self, gpu_monitor: GPUMonitor, parent=None):
        """
        Initialize the GPU details dialog.
        
        Args:
            gpu_monitor: GPUMonitor instance for collecting metrics
            parent: Parent widget
        """
        super().__init__(parent)
        
        self.logger = logging.getLogger("gguf_loader.ui.gpu_details_dialog")
        self.gpu_monitor = gpu_monitor
        
        # Initialize theme manager
        self.theme_manager = ThemeManager()
        
        # Auto-refresh state
        self.auto_refresh_enabled = True
        self.last_refresh_time = 0
        
        # Set dialog properties
        self.setWindowTitle("GPU Usage Details")
        self.setModal(True)
        self.setMinimumSize(600, 500)
        self.resize(700, 600)
        
        # Auto-refresh timer (5 seconds as per requirements)
        self.refresh_timer = QTimer()
        self.refresh_timer.timeout.connect(self._refresh_gpu_info)
        self.refresh_timer.setInterval(5000)  # 5 seconds
        
        # Initialize UI
        self._init_ui()
        
        # Apply theme
        self._apply_theme()
        
        # Start auto-refresh
        self._start_auto_refresh()
        
        # Initial data load
        self._refresh_gpu_info()
        
        self.logger.info("GPU details dialog initialized")
    
    def _init_ui(self):
        """Initialize the user interface."""
        layout = QVBoxLayout(self)
        layout.setSpacing(15)
        layout.setContentsMargins(20, 20, 20, 20)
        
        # Header section
        self._create_header_section(layout)
        
        # Control section
        self._create_control_section(layout)
        
        # GPU information section
        self._create_gpu_info_section(layout)
        
        # Button section
        self._create_button_section(layout)
    
    def _create_header_section(self, layout: QVBoxLayout):
        """Create the header section with title and status."""
        header_layout = QHBoxLayout()
        
        # Title
        title_label = QLabel("GPU Usage Details")
        title_font = QFont()
        title_font.setPointSize(16)
        title_font.setBold(True)
        title_label.setFont(title_font)
        header_layout.addWidget(title_label)
        
        header_layout.addStretch()
        
        # Status indicator
        self.status_label = QLabel("Checking...")
        self.status_label.setStyleSheet("color: #9ca3af;")
        header_layout.addWidget(self.status_label)
        
        layout.addLayout(header_layout)
        
        # Separator
        separator = QFrame()
        separator.setFrameShape(QFrame.HLine)
        separator.setFrameShadow(QFrame.Sunken)
        layout.addWidget(separator)
    
    def _create_control_section(self, layout: QVBoxLayout):
        """Create the control section with refresh options."""
        control_layout = QHBoxLayout()
        
        # Auto-refresh checkbox
        self.auto_refresh_checkbox = QCheckBox("Auto-refresh (5 seconds)")
        self.auto_refresh_checkbox.setChecked(True)
        self.auto_refresh_checkbox.toggled.connect(self._toggle_auto_refresh)
        control_layout.addWidget(self.auto_refresh_checkbox)
        
        control_layout.addStretch()
        
        # Last updated label
        self.last_updated_label = QLabel("Last updated: Never")
        self.last_updated_label.setStyleSheet("color: #9ca3af; font-size: 12px;")
        control_layout.addWidget(self.last_updated_label)
        
        # Manual refresh button
        self.refresh_button = QPushButton("Refresh Now")
        self.refresh_button.clicked.connect(self._refresh_gpu_info)
        control_layout.addWidget(self.refresh_button)
        
        layout.addLayout(control_layout)
    
    def _create_gpu_info_section(self, layout: QVBoxLayout):
        """Create the GPU information display section."""
        # Model GPU usage status section
        self.model_gpu_status = QGroupBox("Current Model GPU Usage")
        model_status_layout = QVBoxLayout(self.model_gpu_status)
        
        self.model_gpu_label = QLabel("Checking model GPU usage...")
        self.model_gpu_label.setStyleSheet("color: #9ca3af; padding: 10px;")
        self.model_gpu_label.setWordWrap(True)
        model_status_layout.addWidget(self.model_gpu_label)
        
        layout.addWidget(self.model_gpu_status)
        
        # Scroll area for GPU hardware information
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        scroll_area.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        
        # Container widget for GPU information
        self.gpu_container = QWidget()
        self.gpu_layout = QVBoxLayout(self.gpu_container)
        self.gpu_layout.setSpacing(15)
        
        # Initial placeholder
        self.no_gpu_label = QLabel("No GPU information available")
        self.no_gpu_label.setAlignment(Qt.AlignCenter)
        self.no_gpu_label.setStyleSheet("color: #9ca3af; font-size: 14px; padding: 40px;")
        self.gpu_layout.addWidget(self.no_gpu_label)
        
        scroll_area.setWidget(self.gpu_container)
        layout.addWidget(scroll_area)
    
    def _create_button_section(self, layout: QVBoxLayout):
        """Create the button section."""
        button_layout = QHBoxLayout()
        button_layout.addStretch()
        
        # Close button
        close_button = QPushButton("Close")
        close_button.setDefault(True)
        close_button.clicked.connect(self.accept)
        button_layout.addWidget(close_button)
        
        layout.addLayout(button_layout)
    
    def _start_auto_refresh(self):
        """Start the auto-refresh timer."""
        if self.auto_refresh_enabled:
            self.refresh_timer.start()
            self.logger.debug("Auto-refresh started")
    
    def _stop_auto_refresh(self):
        """Stop the auto-refresh timer."""
        self.refresh_timer.stop()
        self.logger.debug("Auto-refresh stopped")
    
    def _toggle_auto_refresh(self, enabled: bool):
        """Toggle auto-refresh functionality."""
        self.auto_refresh_enabled = enabled
        
        if enabled:
            self._start_auto_refresh()
        else:
            self._stop_auto_refresh()
        
        self.auto_refresh_toggled.emit(enabled)
        self.logger.info(f"Auto-refresh {'enabled' if enabled else 'disabled'}")
    
    def _refresh_gpu_info(self):
        """Refresh GPU information display."""
        try:
            self.refresh_requested.emit()
            
            # Get GPU metrics
            gpu_metrics = self.gpu_monitor.get_gpu_metrics()
            
            # Update status
            current_time = time.time()
            self.last_refresh_time = current_time
            
            if gpu_metrics:
                self.status_label.setText(f"Found {len(gpu_metrics)} GPU(s)")
                self.status_label.setStyleSheet("color: #10b981;")  # Success color
            else:
                self.status_label.setText("No GPUs detected")
                self.status_label.setStyleSheet("color: #f59e0b;")  # Warning color
            
            # Update last updated time
            time_str = time.strftime("%H:%M:%S", time.localtime(current_time))
            self.last_updated_label.setText(f"Last updated: {time_str}")
            
            # Update model GPU usage status
            self._update_model_gpu_status(gpu_metrics)
            
            # Update GPU information display
            self._update_gpu_display(gpu_metrics)
            
            self.logger.debug(f"GPU information refreshed - found {len(gpu_metrics)} GPUs")
            
        except Exception as e:
            self.logger.error(f"Error refreshing GPU information: {e}")
            self.status_label.setText("Error retrieving GPU data")
            self.status_label.setStyleSheet("color: #ef4444;")  # Error color
            self._show_error_display(str(e))
    
    def _update_model_gpu_status(self, gpu_metrics: List[Dict[str, Any]]):
        """Update the model GPU usage status."""
        if not gpu_metrics:
            # No GPU hardware detected
            self.model_gpu_label.setText(
                "🔍 Hardware Detection: No GPU detected\n\n"
                "This means no dedicated GPU hardware was found in your system. "
                "Your current model is running on CPU only.\n\n"
                "If you have a GPU but it's not detected, check:\n"
                "• GPU drivers are properly installed\n"
                "• GPU monitoring libraries are available"
            )
            self.model_gpu_label.setStyleSheet("color: #f59e0b; padding: 10px;")  # Warning color
        else:
            # GPU hardware detected - check if it's being used
            total_gpu_usage = sum(gpu.get('utilization_percent', 0) for gpu in gpu_metrics)
            avg_gpu_usage = total_gpu_usage / len(gpu_metrics) if gpu_metrics else 0
            
            if avg_gpu_usage > 5:  # Threshold for "in use"
                self.model_gpu_label.setText(
                    f"[OK] Hardware Detection: {len(gpu_metrics)} GPU(s) detected\n"
                    f"[GPU] Current Usage: GPU is actively being used (avg {avg_gpu_usage:.1f}% utilization)\n\n"
                    "Your current model appears to be using GPU acceleration."
                )
                self.model_gpu_label.setStyleSheet("color: #10b981; padding: 10px;")  # Success color
            else:
                self.model_gpu_label.setText(
                    f"[OK] Hardware Detection: {len(gpu_metrics)} GPU(s) detected\n"
                    f"💤 Current Usage: GPU is idle (avg {avg_gpu_usage:.1f}% utilization)\n\n"
                    "Your current model may be running on CPU instead of GPU. "
                    "This could be due to:\n"
                    "• Model backend doesn't support GPU\n"
                    "• GPU acceleration is disabled in settings\n"
                    "• Model is too small to benefit from GPU"
                )
                self.model_gpu_label.setStyleSheet("color: #06b6d4; padding: 10px;")  # Info color
    
    def _update_gpu_display(self, gpu_metrics: List[Dict[str, Any]]):
        """Update the GPU information display."""
        # Clear existing widgets
        self._clear_gpu_display()
        
        if not gpu_metrics:
            self._show_no_gpu_display()
            return
        
        # Create GPU information widgets
        for i, gpu_info in enumerate(gpu_metrics):
            gpu_widget = self._create_gpu_widget(i, gpu_info)
            self.gpu_layout.addWidget(gpu_widget)
        
        # Add stretch to push content to top
        self.gpu_layout.addStretch()
    
    def _clear_gpu_display(self):
        """Clear all widgets from the GPU display."""
        while self.gpu_layout.count():
            child = self.gpu_layout.takeAt(0)
            if child.widget():
                child.widget().deleteLater()
    
    def _show_no_gpu_display(self):
        """Show message when no GPUs are available."""
        no_gpu_widget = QWidget()
        no_gpu_layout = QVBoxLayout(no_gpu_widget)
        no_gpu_layout.setAlignment(Qt.AlignCenter)
        
        # Icon or placeholder
        icon_label = QLabel("🚫")
        icon_label.setAlignment(Qt.AlignCenter)
        icon_label.setStyleSheet("font-size: 48px; margin: 20px;")
        no_gpu_layout.addWidget(icon_label)
        
        # Message
        message_label = QLabel("No GPU detected")
        message_label.setAlignment(Qt.AlignCenter)
        message_label.setStyleSheet("font-size: 16px; font-weight: bold; color: #9ca3af; margin-bottom: 10px;")
        no_gpu_layout.addWidget(message_label)
        
        # Explanation
        explanation_label = QLabel(
            "This means no GPU hardware was detected in your system.\n\n"
            "Possible reasons:\n"
            "• No dedicated GPU is installed (using integrated graphics)\n"
            "• GPU drivers are not properly installed\n"
            "• GPU monitoring libraries are missing (NVIDIA ML, ROCm)\n"
            "• GPU is not supported by the monitoring system\n\n"
            "Note: This shows hardware detection, not whether your\n"
            "current model is using GPU acceleration."
        )
        explanation_label.setAlignment(Qt.AlignCenter)
        explanation_label.setStyleSheet("color: #9ca3af; font-size: 12px; line-height: 1.4;")
        explanation_label.setWordWrap(True)
        no_gpu_layout.addWidget(explanation_label)
        
        self.gpu_layout.addWidget(no_gpu_widget)
    
    def _show_error_display(self, error_message: str):
        """Show error message when GPU data retrieval fails."""
        error_widget = QWidget()
        error_layout = QVBoxLayout(error_widget)
        error_layout.setAlignment(Qt.AlignCenter)
        
        # Error icon
        icon_label = QLabel("[WARN]")
        icon_label.setAlignment(Qt.AlignCenter)
        icon_label.setStyleSheet("font-size: 48px; margin: 20px;")
        error_layout.addWidget(icon_label)
        
        # Error message
        error_label = QLabel("Error retrieving GPU information")
        error_label.setAlignment(Qt.AlignCenter)
        error_label.setStyleSheet("font-size: 16px; font-weight: bold; color: #ef4444; margin-bottom: 10px;")
        error_layout.addWidget(error_label)
        
        # Error details
        details_label = QLabel(f"Details: {error_message}")
        details_label.setAlignment(Qt.AlignCenter)
        details_label.setStyleSheet("color: #9ca3af; font-size: 12px;")
        details_label.setWordWrap(True)
        error_layout.addWidget(details_label)
        
        self.gpu_layout.addWidget(error_widget)
    
    def _create_gpu_widget(self, index: int, gpu_info: Dict[str, Any]) -> QWidget:
        """Create a widget displaying information for a single GPU."""
        # Main group box
        group_box = QGroupBox(f"GPU {index}: {gpu_info.get('name', 'Unknown GPU')}")
        group_box.setStyleSheet("""
            QGroupBox {
                font-weight: bold;
                border: 2px solid #404040;
                border-radius: 8px;
                margin-top: 10px;
                padding-top: 10px;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 5px 0 5px;
            }
        """)
        
        layout = QGridLayout(group_box)
        layout.setSpacing(10)
        
        row = 0
        
        # GPU Type and Device ID
        self._add_info_row(layout, row, "Type:", gpu_info.get('type', 'Unknown').upper())
        row += 1
        
        self._add_info_row(layout, row, "Device ID:", str(gpu_info.get('device_id', 'N/A')))
        row += 1
        
        # Utilization
        if 'utilization_percent' in gpu_info:
            utilization = gpu_info['utilization_percent']
            self._add_progress_row(layout, row, "GPU Utilization:", utilization, "%")
            row += 1
        
        # Memory information
        if 'memory_used_mb' in gpu_info and 'memory_total_mb' in gpu_info:
            used_mb = gpu_info['memory_used_mb']
            total_mb = gpu_info['memory_total_mb']
            
            if total_mb > 0:
                memory_percent = (used_mb / total_mb) * 100
                memory_text = f"{used_mb:,} MB / {total_mb:,} MB"
                self._add_progress_row(layout, row, "Memory Usage:", memory_percent, "%", memory_text)
                row += 1
            else:
                self._add_info_row(layout, row, "Memory Used:", f"{used_mb:,} MB")
                row += 1
        
        # Memory utilization (separate from memory usage)
        if 'memory_utilization_percent' in gpu_info:
            mem_util = gpu_info['memory_utilization_percent']
            self._add_progress_row(layout, row, "Memory Utilization:", mem_util, "%")
            row += 1
        
        # Temperature
        if 'temperature_c' in gpu_info:
            temp = gpu_info['temperature_c']
            temp_color = self._get_temperature_color(temp)
            self._add_info_row(layout, row, "Temperature:", f"{temp}°C", temp_color)
            row += 1
        
        # Power usage
        if 'power_usage_w' in gpu_info:
            power = gpu_info['power_usage_w']
            self._add_info_row(layout, row, "Power Usage:", f"{power:.1f} W")
            row += 1
        
        # Free memory (if available)
        if 'memory_free_mb' in gpu_info:
            free_mb = gpu_info['memory_free_mb']
            self._add_info_row(layout, row, "Free Memory:", f"{free_mb:,} MB")
            row += 1
        
        return group_box
    
    def _add_info_row(self, layout: QGridLayout, row: int, label: str, value: str, color: str = None):
        """Add an information row to the grid layout."""
        label_widget = QLabel(label)
        label_widget.setStyleSheet("font-weight: bold; color: #d1d5db;")
        
        value_widget = QLabel(str(value))
        if color:
            value_widget.setStyleSheet(f"color: {color};")
        else:
            value_widget.setStyleSheet("color: #ffffff;")
        
        layout.addWidget(label_widget, row, 0)
        layout.addWidget(value_widget, row, 1)
    
    def _add_progress_row(self, layout: QGridLayout, row: int, label: str, 
                         value: float, unit: str, text_override: str = None):
        """Add a progress bar row to the grid layout."""
        label_widget = QLabel(label)
        label_widget.setStyleSheet("font-weight: bold; color: #d1d5db;")
        
        # Progress bar
        progress_bar = QProgressBar()
        progress_bar.setMinimum(0)
        progress_bar.setMaximum(100)
        progress_bar.setValue(int(value))
        progress_bar.setTextVisible(True)
        
        # Set progress bar color based on value
        if value >= 90:
            color = "#ef4444"  # Red for high usage
        elif value >= 70:
            color = "#f59e0b"  # Orange for medium-high usage
        elif value >= 50:
            color = "#10b981"  # Green for medium usage
        else:
            color = "#06b6d4"  # Blue for low usage
        
        progress_bar.setStyleSheet(f"""
            QProgressBar {{
                border: 2px solid #404040;
                border-radius: 5px;
                text-align: center;
                background-color: #2d2d30;
            }}
            QProgressBar::chunk {{
                background-color: {color};
                border-radius: 3px;
            }}
        """)
        
        # Custom text if provided
        if text_override:
            progress_bar.setFormat(f"{text_override} ({value:.1f}{unit})")
        else:
            progress_bar.setFormat(f"{value:.1f}{unit}")
        
        layout.addWidget(label_widget, row, 0)
        layout.addWidget(progress_bar, row, 1)
    
    def _get_temperature_color(self, temperature: float) -> str:
        """Get color for temperature display based on value."""
        if temperature >= 85:
            return "#ef4444"  # Red for very hot
        elif temperature >= 75:
            return "#f59e0b"  # Orange for hot
        elif temperature >= 65:
            return "#10b981"  # Green for warm
        else:
            return "#06b6d4"  # Blue for cool
    
    def _apply_theme(self):
        """Apply dark theme to the dialog."""
        try:
            # Get theme colors
            colors = self.theme_manager.get_colors()
            
            # Apply dialog theme
            dialog_style = f"""
                QDialog {{
                    background-color: {colors["background"]};
                    color: {colors["text"]};
                }}
                
                QLabel {{
                    color: {colors["text"]};
                }}
                
                QPushButton {{
                    background-color: {colors["surface"]};
                    color: {colors["text"]};
                    border: 2px solid {colors["border"]};
                    border-radius: 6px;
                    padding: 8px 16px;
                    font-weight: bold;
                    min-width: 80px;
                }}
                
                QPushButton:hover {{
                    background-color: {colors["border"]};
                }}
                
                QPushButton:pressed {{
                    background-color: {colors["primary"]};
                    color: white;
                }}
                
                QCheckBox {{
                    color: {colors["text"]};
                    spacing: 8px;
                }}
                
                QCheckBox::indicator {{
                    width: 16px;
                    height: 16px;
                    border: 2px solid {colors["border"]};
                    border-radius: 3px;
                    background-color: {colors["surface"]};
                }}
                
                QCheckBox::indicator:checked {{
                    background-color: {colors["primary"]};
                    border-color: {colors["primary"]};
                }}
                
                QScrollArea {{
                    border: 1px solid {colors["border"]};
                    border-radius: 6px;
                    background-color: {colors["surface"]};
                }}
                
                QFrame[frameShape="4"] {{
                    color: {colors["border"]};
                }}
            """
            
            self.setStyleSheet(dialog_style)
            
        except Exception as e:
            self.logger.error(f"Failed to apply theme to GPU details dialog: {e}")
    
    def closeEvent(self, event):
        """Handle dialog close event."""
        # Stop auto-refresh when dialog is closed
        self._stop_auto_refresh()
        super().closeEvent(event)
        self.logger.info("GPU details dialog closed")
    
    def showEvent(self, event):
        """Handle dialog show event."""
        # Start auto-refresh when dialog is shown
        if self.auto_refresh_enabled:
            self._start_auto_refresh()
        super().showEvent(event)
        self.logger.info("GPU details dialog shown")