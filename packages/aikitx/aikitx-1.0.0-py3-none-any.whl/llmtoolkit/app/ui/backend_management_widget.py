"""
Backend Management Widget

This module provides UI components for backend management including:
- Backend selection interface
- Real-time GPU utilization display
- Backend status indicators and health monitoring
- Diagnostic and troubleshooting UI components
"""

import logging
import time
from typing import Dict, Any, Optional, List
from pathlib import Path

from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QGroupBox, QFormLayout,
    QComboBox, QLabel, QPushButton, QProgressBar, QTextEdit,
    QTableWidget, QTableWidgetItem, QTabWidget, QScrollArea,
    QFrame, QSizePolicy, QSpacerItem, QCheckBox, QSpinBox,
    QMessageBox, QDialog, QDialogButtonBox, QListWidget,
    QListWidgetItem, QSplitter, QGridLayout
)
from PySide6.QtCore import Qt, QTimer, Signal, Slot, QThread
from PySide6.QtGui import QFont, QColor, QPalette, QIcon

from llmtoolkit.app.core.backend_manager import BackendManager
from llmtoolkit.app.core.hardware_detector import HardwareDetector
from llmtoolkit.app.core.monitoring import monitoring_manager, SystemMetrics, PerformanceMetrics
from llmtoolkit.app.ui.mixins.theme_mixin import DialogThemeMixin


class BackendStatusIndicator(QWidget):
    """Widget to display backend status with color-coded indicators."""
    
    def __init__(self, backend_name: str, parent=None):
        super().__init__(parent)
        self.backend_name = backend_name
        self.status = "unknown"
        self._init_ui()
    
    def _init_ui(self):
        """Initialize the UI components."""
        layout = QHBoxLayout(self)
        layout.setContentsMargins(5, 5, 5, 5)
        
        # Status indicator (colored circle)
        self.status_indicator = QLabel("●")
        self.status_indicator.setFixedSize(16, 16)
        self.status_indicator.setAlignment(Qt.AlignCenter)
        layout.addWidget(self.status_indicator)
        
        # Backend name
        self.name_label = QLabel(self.backend_name)
        self.name_label.setFont(QFont("", 9, QFont.Bold))
        layout.addWidget(self.name_label)
        
        # Status text
        self.status_label = QLabel("Unknown")
        self.status_label.setFont(QFont("", 8))
        layout.addWidget(self.status_label)
        
        layout.addStretch()
        
        # Set initial status
        self.update_status("unknown", "Unknown")
    
    def update_status(self, status: str, message: str = ""):
        """Update the status indicator."""
        self.status = status
        
        # Update status indicator color
        if status == "available":
            self.status_indicator.setStyleSheet("color: #4CAF50; font-size: 12px;")  # Green
            self.status_label.setText("Available")
        elif status == "unavailable":
            self.status_indicator.setStyleSheet("color: #F44336; font-size: 12px;")  # Red
            self.status_label.setText("Unavailable")
        elif status == "loading":
            self.status_indicator.setStyleSheet("color: #FF9800; font-size: 12px;")  # Orange
            self.status_label.setText("Loading...")
        elif status == "error":
            self.status_indicator.setStyleSheet("color: #F44336; font-size: 12px;")  # Red
            self.status_label.setText("Error")
        else:
            self.status_indicator.setStyleSheet("color: #9E9E9E; font-size: 12px;")  # Gray
            self.status_label.setText("Unknown")
        
        if message:
            self.status_label.setToolTip(message)


class GPUUtilizationWidget(QWidget):
    """Widget to display real-time GPU utilization."""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.gpu_metrics = []
        self._init_ui()
        
        # Timer for updates
        self.update_timer = QTimer()
        self.update_timer.timeout.connect(self.update_metrics)
        self.update_timer.start(1000)  # Update every second
    
    def _init_ui(self):
        """Initialize the UI components."""
        layout = QVBoxLayout(self)
        
        # Title
        title_label = QLabel("GPU Utilization")
        title_label.setFont(QFont("", 10, QFont.Bold))
        layout.addWidget(title_label)
        
        # Scroll area for GPU cards
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setMaximumHeight(200)
        
        self.gpu_container = QWidget()
        self.gpu_layout = QVBoxLayout(self.gpu_container)
        
        scroll_area.setWidget(self.gpu_container)
        layout.addWidget(scroll_area)
        
        # No GPU message
        self.no_gpu_label = QLabel("No GPU detected or monitoring unavailable")
        self.no_gpu_label.setAlignment(Qt.AlignCenter)
        self.no_gpu_label.setStyleSheet("color: #666; font-style: italic;")
        layout.addWidget(self.no_gpu_label)
        
        self.no_gpu_label.hide()  # Initially hidden
    
    def update_metrics(self):
        """Update GPU metrics display."""
        try:
            # Get current system metrics
            current_metrics = monitoring_manager.system_monitor.get_current_metrics()
            if current_metrics and current_metrics.gpu_metrics:
                self.gpu_metrics = current_metrics.gpu_metrics
                self._update_gpu_display()
                self.no_gpu_label.hide()
            else:
                self._show_no_gpu()
        except Exception as e:
            logging.getLogger("ui.backend_management").debug(f"Error updating GPU metrics: {e}")
            self._show_no_gpu()
    
    def _update_gpu_display(self):
        """Update the GPU display with current metrics."""
        # Clear existing widgets
        for i in reversed(range(self.gpu_layout.count())):
            child = self.gpu_layout.itemAt(i).widget()
            if child:
                child.setParent(None)
        
        # Add GPU cards
        for gpu in self.gpu_metrics:
            gpu_card = self._create_gpu_card(gpu)
            self.gpu_layout.addWidget(gpu_card)
        
        self.gpu_layout.addStretch()
    
    def _create_gpu_card(self, gpu_info: Dict[str, Any]) -> QWidget:
        """Create a card widget for a single GPU."""
        card = QFrame()
        card.setFrameStyle(QFrame.Box)
        card.setStyleSheet("""
            QFrame {
                border: 1px solid #ddd;
                border-radius: 4px;
                padding: 8px;
                margin: 2px;
                background-color: #f9f9f9;
            }
        """)
        
        layout = QVBoxLayout(card)
        layout.setSpacing(4)
        
        # GPU name and type
        name_label = QLabel(f"{gpu_info.get('name', 'Unknown GPU')} ({gpu_info.get('type', 'unknown').upper()})")
        name_label.setFont(QFont("", 9, QFont.Bold))
        layout.addWidget(name_label)
        
        # Utilization bar
        util_layout = QHBoxLayout()
        util_layout.addWidget(QLabel("GPU:"))
        
        gpu_util_bar = QProgressBar()
        gpu_util_bar.setMaximum(100)
        gpu_util_bar.setValue(int(gpu_info.get('utilization_percent', 0)))
        gpu_util_bar.setFormat(f"{gpu_info.get('utilization_percent', 0):.1f}%")
        util_layout.addWidget(gpu_util_bar)
        
        layout.addLayout(util_layout)
        
        # Memory usage bar
        if 'memory_used_mb' in gpu_info and 'memory_total_mb' in gpu_info:
            mem_layout = QHBoxLayout()
            mem_layout.addWidget(QLabel("VRAM:"))
            
            memory_bar = QProgressBar()
            memory_bar.setMaximum(gpu_info['memory_total_mb'])
            memory_bar.setValue(gpu_info['memory_used_mb'])
            
            used_gb = gpu_info['memory_used_mb'] / 1024
            total_gb = gpu_info['memory_total_mb'] / 1024
            memory_bar.setFormat(f"{used_gb:.1f}GB / {total_gb:.1f}GB")
            
            mem_layout.addWidget(memory_bar)
            layout.addLayout(mem_layout)
        
        # Additional info
        info_layout = QHBoxLayout()
        
        if 'temperature_c' in gpu_info and gpu_info['temperature_c'] > 0:
            temp_label = QLabel(f"🌡️ {gpu_info['temperature_c']}°C")
            temp_label.setFont(QFont("", 8))
            info_layout.addWidget(temp_label)
        
        if 'power_usage_w' in gpu_info and gpu_info['power_usage_w'] > 0:
            power_label = QLabel(f"[PERF] {gpu_info['power_usage_w']:.1f}W")
            power_label.setFont(QFont("", 8))
            info_layout.addWidget(power_label)
        
        info_layout.addStretch()
        layout.addLayout(info_layout)
        
        return card
    
    def _show_no_gpu(self):
        """Show no GPU message."""
        # Clear existing widgets
        for i in reversed(range(self.gpu_layout.count())):
            child = self.gpu_layout.itemAt(i).widget()
            if child:
                child.setParent(None)
        
        self.no_gpu_label.show()


class BackendDiagnosticsDialog(QDialog, DialogThemeMixin):
    """Dialog for backend diagnostics and troubleshooting."""
    
    def __init__(self, backend_manager: BackendManager, parent=None):
        super().__init__(parent)
        self.backend_manager = backend_manager
        self.setWindowTitle("Backend Diagnostics")
        self.setMinimumSize(800, 600)
        self._init_ui()
        # Apply theme if available
        if hasattr(self, 'apply_theme'):
            self.apply_theme()
    
    def _init_ui(self):
        """Initialize the UI components."""
        layout = QVBoxLayout(self)
        
        # Create tab widget
        tab_widget = QTabWidget()
        
        # Backend Status Tab
        status_tab = self._create_status_tab()
        tab_widget.addTab(status_tab, "Backend Status")
        
        # System Info Tab
        system_tab = self._create_system_tab()
        tab_widget.addTab(system_tab, "System Information")
        
        # Performance Tab
        performance_tab = self._create_performance_tab()
        tab_widget.addTab(performance_tab, "Performance Metrics")
        
        layout.addWidget(tab_widget)
        
        # Buttons
        button_layout = QHBoxLayout()
        
        refresh_button = QPushButton("Refresh All")
        refresh_button.clicked.connect(self.refresh_diagnostics)
        button_layout.addWidget(refresh_button)
        
        button_layout.addStretch()
        
        close_button = QPushButton("Close")
        close_button.clicked.connect(self.accept)
        button_layout.addWidget(close_button)
        
        layout.addLayout(button_layout)
        
        # Initial load
        self.refresh_diagnostics()
    
    def _create_status_tab(self) -> QWidget:
        """Create the backend status tab."""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        
        # Backend status table
        self.status_table = QTableWidget()
        self.status_table.setColumnCount(5)
        self.status_table.setHorizontalHeaderLabels([
            "Backend", "Status", "GPU Support", "Dependencies", "Performance Score"
        ])
        self.status_table.horizontalHeader().setStretchLastSection(True)
        
        layout.addWidget(self.status_table)
        
        return widget
    
    def _create_system_tab(self) -> QWidget:
        """Create the system information tab."""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        
        # System info text
        self.system_info_text = QTextEdit()
        self.system_info_text.setReadOnly(True)
        self.system_info_text.setFont(QFont("Consolas", 9))
        
        layout.addWidget(self.system_info_text)
        
        return widget
    
    def _create_performance_tab(self) -> QWidget:
        """Create the performance metrics tab."""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        
        # Performance metrics table
        self.performance_table = QTableWidget()
        self.performance_table.setColumnCount(6)
        self.performance_table.setHorizontalHeaderLabels([
            "Backend", "Operations", "Success Rate", "Avg Duration", "Avg Memory", "Last Used"
        ])
        self.performance_table.horizontalHeader().setStretchLastSection(True)
        
        layout.addWidget(self.performance_table)
        
        return widget
    
    def refresh_diagnostics(self):
        """Refresh all diagnostic information."""
        self._update_backend_status()
        self._update_system_info()
        self._update_performance_metrics()
    
    def _update_backend_status(self):
        """Update backend status table."""
        try:
            # Get backend statistics
            stats = self.backend_manager.get_statistics()
            
            self.status_table.setRowCount(len(stats))
            
            for row, (backend_name, backend_stats) in enumerate(stats.items()):
                # Backend name
                self.status_table.setItem(row, 0, QTableWidgetItem(backend_name))
                
                # Status
                status = "Available" if backend_stats['available'] else "Unavailable"
                status_item = QTableWidgetItem(status)
                if backend_stats['available']:
                    status_item.setBackground(QColor(200, 255, 200))  # Light green
                else:
                    status_item.setBackground(QColor(255, 200, 200))  # Light red
                self.status_table.setItem(row, 1, status_item)
                
                # GPU Support (placeholder)
                self.status_table.setItem(row, 2, QTableWidgetItem("CUDA, ROCm"))
                
                # Dependencies (placeholder)
                self.status_table.setItem(row, 3, QTableWidgetItem("Installed"))
                
                # Performance Score
                success_rate = backend_stats['success_rate'] * 100
                score_item = QTableWidgetItem(f"{success_rate:.1f}%")
                if success_rate >= 80:
                    score_item.setBackground(QColor(200, 255, 200))  # Light green
                elif success_rate >= 50:
                    score_item.setBackground(QColor(255, 255, 200))  # Light yellow
                else:
                    score_item.setBackground(QColor(255, 200, 200))  # Light red
                self.status_table.setItem(row, 4, score_item)
            
        except Exception as e:
            logging.getLogger("ui.backend_management").error(f"Error updating backend status: {e}")
    
    def _update_system_info(self):
        """Update system information display."""
        try:
            # Get hardware info
            hw_info = self.backend_manager.get_hardware_info()
            
            info_text = f"""System Information:
Platform: {hw_info.platform if hasattr(hw_info, 'platform') else 'Unknown'}
CPU Cores: {hw_info.cpu_cores}
Total RAM: {hw_info.total_ram} MB
GPU Count: {hw_info.gpu_count}
Total VRAM: {hw_info.total_vram} MB
Recommended Backend: {hw_info.recommended_backend or 'None'}

GPU Devices:
"""
            
            for i, device in enumerate(hw_info.gpu_devices):
                info_text += f"  GPU {i}: {device.get('name', 'Unknown')} ({device.get('memory_total', 0)} MB)\n"
            
            # Add monitoring info
            current_metrics = monitoring_manager.system_monitor.get_current_metrics()
            if current_metrics:
                info_text += f"""
Current System Metrics:
CPU Usage: {current_metrics.cpu_usage_percent:.1f}%
Memory Usage: {current_metrics.memory_usage_mb} MB / {current_metrics.memory_total_mb} MB
Memory Available: {current_metrics.memory_available_mb} MB
Disk Usage: {current_metrics.disk_usage_percent:.1f}%
"""
            
            self.system_info_text.setPlainText(info_text)
            
        except Exception as e:
            self.system_info_text.setPlainText(f"Error loading system information: {e}")
    
    def _update_performance_metrics(self):
        """Update performance metrics table."""
        try:
            # Get performance statistics
            perf_stats = monitoring_manager.performance_monitor.get_backend_stats()
            
            self.performance_table.setRowCount(len(perf_stats))
            
            for row, (backend_name, stats) in enumerate(perf_stats.items()):
                # Backend name
                self.performance_table.setItem(row, 0, QTableWidgetItem(backend_name))
                
                # Operations count
                self.performance_table.setItem(row, 1, QTableWidgetItem(str(stats['total_operations'])))
                
                # Success rate
                success_rate = (stats['successful_operations'] / max(stats['total_operations'], 1)) * 100
                self.performance_table.setItem(row, 2, QTableWidgetItem(f"{success_rate:.1f}%"))
                
                # Average duration
                avg_duration = stats['average_duration'] * 1000  # Convert to ms
                self.performance_table.setItem(row, 3, QTableWidgetItem(f"{avg_duration:.1f}ms"))
                
                # Average memory
                avg_memory = stats['average_memory_usage']
                self.performance_table.setItem(row, 4, QTableWidgetItem(f"{avg_memory:.1f}MB"))
                
                # Last used
                if stats['last_operation']:
                    last_used = time.strftime("%H:%M:%S", time.localtime(stats['last_operation']))
                    self.performance_table.setItem(row, 5, QTableWidgetItem(last_used))
                else:
                    self.performance_table.setItem(row, 5, QTableWidgetItem("Never"))
            
        except Exception as e:
            logging.getLogger("ui.backend_management").error(f"Error updating performance metrics: {e}")


class BackendManagementWidget(QWidget):
    """Main widget for backend management settings."""
    
    backend_changed = Signal(str)  # Emitted when backend selection changes
    
    def __init__(self, config_manager, parent=None):
        super().__init__(parent)
        self.logger = logging.getLogger("ui.backend_management")
        self.config_manager = config_manager
        
        # Initialize backend manager
        self.hardware_detector = HardwareDetector()
        self.backend_manager = BackendManager(self.hardware_detector)
        
        self._init_ui()
        self._load_settings()
        
        # Start monitoring
        monitoring_manager.start()
        self.backend_manager.start_monitoring()
    
    def _init_ui(self):
        """Initialize the UI components."""
        layout = QVBoxLayout(self)
        
        # Backend Selection Group
        selection_group = QGroupBox("Backend Selection")
        selection_layout = QFormLayout(selection_group)
        
        # Current backend dropdown
        self.backend_combo = QComboBox()
        self.backend_combo.currentTextChanged.connect(self._on_backend_changed)
        selection_layout.addRow("Active Backend:", self.backend_combo)
        
        # Auto-selection checkbox
        self.auto_select_check = QCheckBox("Automatically select best backend")
        self.auto_select_check.setChecked(True)
        self.auto_select_check.toggled.connect(self._on_auto_select_toggled)
        selection_layout.addRow("", self.auto_select_check)
        
        # Hardware preference
        self.hardware_combo = QComboBox()
        self.hardware_combo.addItems(["Auto", "GPU Preferred", "CPU Only"])
        selection_layout.addRow("Hardware Preference:", self.hardware_combo)
        
        layout.addWidget(selection_group)
        
        # Backend Status Group
        status_group = QGroupBox("Backend Status")
        status_layout = QVBoxLayout(status_group)
        
        # Backend status indicators
        self.status_container = QWidget()
        self.status_layout = QVBoxLayout(self.status_container)
        status_layout.addWidget(self.status_container)
        
        # Refresh button
        refresh_layout = QHBoxLayout()
        refresh_button = QPushButton("Refresh Status")
        refresh_button.clicked.connect(self._refresh_backend_status)
        refresh_layout.addWidget(refresh_button)
        refresh_layout.addStretch()
        
        diagnostics_button = QPushButton("Advanced Diagnostics...")
        diagnostics_button.clicked.connect(self._show_diagnostics)
        refresh_layout.addWidget(diagnostics_button)
        
        status_layout.addLayout(refresh_layout)
        
        layout.addWidget(status_group)
        
        # GPU Utilization Group
        gpu_group = QGroupBox("GPU Utilization")
        gpu_layout = QVBoxLayout(gpu_group)
        
        self.gpu_widget = GPUUtilizationWidget()
        gpu_layout.addWidget(self.gpu_widget)
        
        layout.addWidget(gpu_group)
        
        # Backend Configuration Group
        config_group = QGroupBox("Backend Configuration")
        config_layout = QFormLayout(config_group)
        
        # GPU layers
        self.gpu_layers_spin = QSpinBox()
        self.gpu_layers_spin.setRange(-1, 100)
        self.gpu_layers_spin.setValue(-1)
        self.gpu_layers_spin.setSpecialValueText("Auto")
        config_layout.addRow("GPU Layers:", self.gpu_layers_spin)
        
        # Context size
        self.context_size_spin = QSpinBox()
        self.context_size_spin.setRange(512, 32768)
        self.context_size_spin.setValue(4096)
        self.context_size_spin.setSingleStep(512)
        config_layout.addRow("Context Size:", self.context_size_spin)
        
        # Batch size
        self.batch_size_spin = QSpinBox()
        self.batch_size_spin.setRange(1, 2048)
        self.batch_size_spin.setValue(512)
        config_layout.addRow("Batch Size:", self.batch_size_spin)
        
        layout.addWidget(config_group)
        
        # Add stretch
        layout.addStretch()
        
        # Initialize backend status indicators
        self._init_backend_status()
    
    def _init_backend_status(self):
        """Initialize backend status indicators."""
        # Clear existing indicators
        for i in reversed(range(self.status_layout.count())):
            child = self.status_layout.itemAt(i).widget()
            if child:
                child.setParent(None)
        
        # Get available backends
        available_backends = self.backend_manager.get_available_backends()
        all_backends = ['ctransformers', 'transformers', 'llamafile', 'llama-cpp-python']
        
        # Create status indicators
        self.status_indicators = {}
        for backend_name in all_backends:
            indicator = BackendStatusIndicator(backend_name)
            self.status_indicators[backend_name] = indicator
            self.status_layout.addWidget(indicator)
            
            # Update status
            if backend_name in available_backends:
                indicator.update_status("available", "Backend is available and ready")
            else:
                status = self.backend_manager.get_backend_status(backend_name)
                error_msg = status.error_message if status else "Unknown error"
                indicator.update_status("unavailable", error_msg)
        
        # Update backend combo
        self.backend_combo.clear()
        self.backend_combo.addItem("Auto-select")
        self.backend_combo.addItems(available_backends)
    
    def _load_settings(self):
        """Load current settings from configuration."""
        # Backend selection
        current_backend = self.config_manager.get_value("backend.current", "auto")
        if current_backend == "auto":
            self.backend_combo.setCurrentText("Auto-select")
            self.auto_select_check.setChecked(True)
        else:
            self.backend_combo.setCurrentText(current_backend)
            self.auto_select_check.setChecked(False)
        
        # Hardware preference
        hardware_pref = self.config_manager.get_value("backend.hardware_preference", "auto")
        if hardware_pref == "gpu":
            self.hardware_combo.setCurrentText("GPU Preferred")
        elif hardware_pref == "cpu":
            self.hardware_combo.setCurrentText("CPU Only")
        else:
            self.hardware_combo.setCurrentText("Auto")
        
        # Configuration
        self.gpu_layers_spin.setValue(self.config_manager.get_value("backend.gpu_layers", -1))
        self.context_size_spin.setValue(self.config_manager.get_value("backend.context_size", 4096))
        self.batch_size_spin.setValue(self.config_manager.get_value("backend.batch_size", 512))
    
    def save_settings(self):
        """Save settings to configuration."""
        # Backend selection
        if self.auto_select_check.isChecked():
            self.config_manager.set_value("backend.current", "auto")
        else:
            current_backend = self.backend_combo.currentText()
            if current_backend != "Auto-select":
                self.config_manager.set_value("backend.current", current_backend)
        
        # Hardware preference
        hardware_text = self.hardware_combo.currentText()
        if hardware_text == "GPU Preferred":
            self.config_manager.set_value("backend.hardware_preference", "gpu")
        elif hardware_text == "CPU Only":
            self.config_manager.set_value("backend.hardware_preference", "cpu")
        else:
            self.config_manager.set_value("backend.hardware_preference", "auto")
        
        # Configuration
        self.config_manager.set_value("backend.gpu_layers", self.gpu_layers_spin.value())
        self.config_manager.set_value("backend.context_size", self.context_size_spin.value())
        self.config_manager.set_value("backend.batch_size", self.batch_size_spin.value())
    
    def _on_backend_changed(self, backend_name: str):
        """Handle backend selection change."""
        if backend_name and backend_name != "Auto-select":
            self.auto_select_check.setChecked(False)
            self.backend_changed.emit(backend_name)
    
    def _on_auto_select_toggled(self, checked: bool):
        """Handle auto-select toggle."""
        if checked:
            self.backend_combo.setCurrentText("Auto-select")
        
        # Enable/disable backend combo
        self.backend_combo.setEnabled(not checked)
    
    def _refresh_backend_status(self):
        """Refresh backend availability status."""
        self.backend_manager.refresh_backend_availability()
        self._init_backend_status()
    
    def _show_diagnostics(self):
        """Show advanced diagnostics dialog."""
        dialog = BackendDiagnosticsDialog(self.backend_manager, self)
        dialog.exec()
    
    def cleanup(self):
        """Clean up resources."""
        if hasattr(self, 'backend_manager'):
            self.backend_manager.stop_monitoring()
            self.backend_manager.cleanup()
        
        monitoring_manager.stop()