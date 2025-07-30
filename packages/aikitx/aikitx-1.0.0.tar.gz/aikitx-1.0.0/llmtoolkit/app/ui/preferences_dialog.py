"""
Preferences Dialog

This module contains the PreferencesDialog class, which allows users to
customize application settings.
"""

import os
import logging
from pathlib import Path
from typing import Dict, Any, Optional, List, Tuple

from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QTabWidget, QWidget,
    QLabel, QLineEdit, QComboBox, QCheckBox, QSpinBox,
    QPushButton, QFileDialog, QGroupBox, QFormLayout,
    QDialogButtonBox, QColorDialog, QSlider, QRadioButton,
    QButtonGroup, QSpacerItem, QSizePolicy, QListWidget,
    QListWidgetItem, QStackedWidget, QToolButton, QTextEdit
)
from PySide6.QtCore import Qt, Signal, Slot, QSize, QSettings
from PySide6.QtGui import QFont, QIcon, QColor, QPalette

from llmtoolkit.app.ui.backend_management_widget import BackendManagementWidget

class GeneralSettingsWidget(QWidget):
    """Widget for general application settings."""
    
    def __init__(self, config_manager, parent=None):
        """
        Initialize the general settings widget.
        
        Args:
            config_manager: The application configuration manager
            parent: Parent widget
        """
        super().__init__(parent)
        self.logger = logging.getLogger("gguf_loader.ui.preferences.general")
        self.config_manager = config_manager
        
        # Create layout
        layout = QVBoxLayout(self)
        
        # Create theme group
        theme_group = QGroupBox("Theme")
        theme_layout = QVBoxLayout(theme_group)
        
        # Create theme radio buttons
        self.system_theme_radio = QRadioButton("System Theme")
        theme_layout.addWidget(self.system_theme_radio)
        
        self.light_theme_radio = QRadioButton("Light Theme")
        theme_layout.addWidget(self.light_theme_radio)
        
        self.dark_theme_radio = QRadioButton("Dark Theme")
        theme_layout.addWidget(self.dark_theme_radio)
        
        # Create theme button group
        self.theme_group = QButtonGroup(self)
        self.theme_group.addButton(self.system_theme_radio, 0)
        self.theme_group.addButton(self.light_theme_radio, 1)
        self.theme_group.addButton(self.dark_theme_radio, 2)
        
        layout.addWidget(theme_group)
        
        # Create startup group
        startup_group = QGroupBox("Startup")
        startup_layout = QVBoxLayout(startup_group)
        
        self.show_splash_check = QCheckBox("Show splash screen on startup")
        startup_layout.addWidget(self.show_splash_check)
        
        self.restore_session_check = QCheckBox("Restore previous session")
        startup_layout.addWidget(self.restore_session_check)
        
        self.check_updates_check = QCheckBox("Check for updates on startup")
        startup_layout.addWidget(self.check_updates_check)
        
        layout.addWidget(startup_group)
        
        # Create logging group
        logging_group = QGroupBox("Logging")
        logging_layout = QFormLayout(logging_group)
        
        self.log_level_combo = QComboBox()
        self.log_level_combo.addItem("Debug", "DEBUG")
        self.log_level_combo.addItem("Info", "INFO")
        self.log_level_combo.addItem("Warning", "WARNING")
        self.log_level_combo.addItem("Error", "ERROR")
        self.log_level_combo.addItem("Critical", "CRITICAL")
        logging_layout.addRow("Log Level:", self.log_level_combo)
        
        layout.addWidget(logging_group)
        
        # Add spacer
        layout.addStretch()
        
        # Load current settings
        self._load_settings()
    
    def _load_settings(self):
        """Load current settings from configuration."""
        # Theme
        theme = self.config_manager.get_value("theme", "system")
        if theme == "system":
            self.system_theme_radio.setChecked(True)
        elif theme == "light":
            self.light_theme_radio.setChecked(True)
        elif theme == "dark":
            self.dark_theme_radio.setChecked(True)
        
        # Startup
        self.show_splash_check.setChecked(self.config_manager.get_value("show_splash", True))
        self.restore_session_check.setChecked(self.config_manager.get_value("restore_session", True))
        self.check_updates_check.setChecked(self.config_manager.get_value("check_updates", True))
        
        # Logging
        log_level = self.config_manager.get_value("log_level", "INFO")
        index = self.log_level_combo.findData(log_level)
        if index >= 0:
            self.log_level_combo.setCurrentIndex(index)
    
    def save_settings(self):
        """Save settings to configuration."""
        # Theme
        theme_id = self.theme_group.checkedId()
        if theme_id == 0:
            self.config_manager.set_value("theme", "system")
        elif theme_id == 1:
            self.config_manager.set_value("theme", "light")
        elif theme_id == 2:
            self.config_manager.set_value("theme", "dark")
        
        # Startup
        self.config_manager.set_value("show_splash", self.show_splash_check.isChecked())
        self.config_manager.set_value("restore_session", self.restore_session_check.isChecked())
        self.config_manager.set_value("check_updates", self.check_updates_check.isChecked())
        
        # Logging
        log_level = self.log_level_combo.currentData()
        self.config_manager.set_value("log_level", log_level)

class ModelSettingsWidget(QWidget):
    """Widget for model-related settings."""
    
    def __init__(self, config_manager, parent=None):
        """
        Initialize the model settings widget.
        
        Args:
            config_manager: The application configuration manager
            parent: Parent widget
        """
        super().__init__(parent)
        self.logger = logging.getLogger("gguf_loader.ui.preferences.model")
        self.config_manager = config_manager
        
        # Initialize GPU detector
        self.gpu_detector = None
        self.gpu_capabilities = None
        
        # Create layout
        layout = QVBoxLayout(self)
        
        # Create directories group
        directories_group = QGroupBox("Directories")
        directories_layout = QFormLayout(directories_group)
        
        # Default model directory
        model_dir_layout = QHBoxLayout()
        self.model_dir_edit = QLineEdit()
        model_dir_layout.addWidget(self.model_dir_edit)
        
        browse_button = QToolButton()
        browse_button.setText("...")
        browse_button.clicked.connect(self._on_browse_model_dir)
        model_dir_layout.addWidget(browse_button)
        
        directories_layout.addRow("Default Model Directory:", model_dir_layout)
        
        layout.addWidget(directories_group)
        
        # Create hardware acceleration group (LM Studio-like)
        hardware_group = QGroupBox("Hardware Acceleration")
        hardware_layout = QVBoxLayout(hardware_group)
        
        # GPU detection status
        detection_layout = QHBoxLayout()
        self.gpu_status_label = QLabel("Detecting GPU...")
        detection_layout.addWidget(self.gpu_status_label)
        
        self.detect_gpu_button = QPushButton("Refresh")
        self.detect_gpu_button.clicked.connect(self._on_detect_gpus)
        detection_layout.addWidget(self.detect_gpu_button)
        
        detection_layout.addStretch()
        hardware_layout.addLayout(detection_layout)
        
        # Processing unit selection
        processing_layout = QHBoxLayout()
        processing_layout.addWidget(QLabel("Processing Unit:"))
        
        self.auto_radio = QRadioButton("Auto (Recommended)")
        self.cpu_radio = QRadioButton("CPU Only")
        self.gpu_radio = QRadioButton("GPU Preferred")
        
        self.processing_group = QButtonGroup(self)
        self.processing_group.addButton(self.auto_radio, 0)
        self.processing_group.addButton(self.cpu_radio, 1)
        self.processing_group.addButton(self.gpu_radio, 2)
        
        processing_layout.addWidget(self.auto_radio)
        processing_layout.addWidget(self.cpu_radio)
        processing_layout.addWidget(self.gpu_radio)
        processing_layout.addStretch()
        
        hardware_layout.addLayout(processing_layout)
        
        # GPU Layers slider (simplified)
        gpu_layers_layout = QHBoxLayout()
        gpu_layers_layout.addWidget(QLabel("GPU Layers:"))
        
        self.gpu_layers_slider = QSlider(Qt.Horizontal)
        self.gpu_layers_slider.setMinimum(0)
        self.gpu_layers_slider.setMaximum(100)
        self.gpu_layers_slider.setValue(35)  # Default value
        self.gpu_layers_slider.setTickPosition(QSlider.TicksBelow)
        self.gpu_layers_slider.setTickInterval(10)
        gpu_layers_layout.addWidget(self.gpu_layers_slider)
        
        self.gpu_layers_label = QLabel("35")
        gpu_layers_layout.addWidget(self.gpu_layers_label)
        
        # Connect slider to label
        self.gpu_layers_slider.valueChanged.connect(lambda v: self.gpu_layers_label.setText(str(v)))
        
        hardware_layout.addLayout(gpu_layers_layout)
        
        # Add info label
        info_label = QLabel("Auto mode will use GPU if available, CPU otherwise. Adjust GPU layers to balance speed and memory usage.")
        info_label.setWordWrap(True)
        info_label.setStyleSheet("color: #666; font-size: 10px;")
        hardware_layout.addWidget(info_label)
        
        # Create stacked widget for CPU/GPU specific settings
        self.hardware_stack = QStackedWidget()
        
        # CPU Settings Widget
        cpu_widget = QWidget()
        cpu_layout = QFormLayout(cpu_widget)
        
        self.cpu_threads_spin = QSpinBox()
        self.cpu_threads_spin.setRange(1, 64)
        self.cpu_threads_spin.setValue(4)
        cpu_layout.addRow("CPU Threads:", self.cpu_threads_spin)
        
        self.cpu_memory_spin = QSpinBox()
        self.cpu_memory_spin.setRange(0, 128 * 1024)  # 0 to 128 GB
        self.cpu_memory_spin.setSingleStep(1024)  # 1 GB steps
        self.cpu_memory_spin.setSuffix(" MB")
        self.cpu_memory_spin.setSpecialValueText("Auto")
        cpu_layout.addRow("CPU Memory Limit:", self.cpu_memory_spin)
        
        self.hardware_stack.addWidget(cpu_widget)
        
        # GPU Settings Widget
        gpu_widget = QWidget()
        gpu_layout = QFormLayout(gpu_widget)
        
        self.gpu_layers_spin = QSpinBox()
        self.gpu_layers_spin.setRange(0, 100)
        self.gpu_layers_spin.setValue(35)
        self.gpu_layers_spin.setSpecialValueText("Auto")
        gpu_layout.addRow("GPU Layers:", self.gpu_layers_spin)
        
        self.gpu_memory_spin = QSpinBox()
        self.gpu_memory_spin.setRange(0, 64 * 1024)  # 0 to 64 GB
        self.gpu_memory_spin.setSingleStep(512)  # 512 MB steps
        self.gpu_memory_spin.setSuffix(" MB")
        self.gpu_memory_spin.setSpecialValueText("Auto")
        gpu_layout.addRow("GPU Memory Limit:", self.gpu_memory_spin)
        
        self.gpu_device_combo = QComboBox()
        self.gpu_device_combo.addItem("Auto-detect", -1)
        self.gpu_device_combo.addItem("GPU 0", 0)
        self.gpu_device_combo.addItem("GPU 1", 1)
        self.gpu_device_combo.addItem("GPU 2", 2)
        self.gpu_device_combo.addItem("GPU 3", 3)
        gpu_layout.addRow("GPU Device:", self.gpu_device_combo)
        
        self.hardware_stack.addWidget(gpu_widget)
        
        hardware_layout.addWidget(self.hardware_stack)
        
        # Connect radio buttons to stack switching
        self.cpu_radio.toggled.connect(self._on_processing_unit_changed)
        self.gpu_radio.toggled.connect(self._on_processing_unit_changed)
        
        layout.addWidget(hardware_group)
        
        # Create system prompts group
        prompts_group = QGroupBox("System Prompts")
        prompts_layout = QVBoxLayout(prompts_group)
        
        # Chat system prompt
        chat_prompt_label = QLabel("Chat System Prompt:")
        chat_prompt_label.setStyleSheet("font-weight: bold;")
        prompts_layout.addWidget(chat_prompt_label)
        
        self.chat_system_prompt = QTextEdit()
        self.chat_system_prompt.setMaximumHeight(100)
        self.chat_system_prompt.setPlaceholderText("Enter system prompt for chat conversations...")
        prompts_layout.addWidget(self.chat_system_prompt)
        
        # Summarization system prompt
        summary_prompt_label = QLabel("Summarization System Prompt:")
        summary_prompt_label.setStyleSheet("font-weight: bold;")
        prompts_layout.addWidget(summary_prompt_label)
        
        self.summary_system_prompt = QTextEdit()
        self.summary_system_prompt.setMaximumHeight(100)
        self.summary_system_prompt.setPlaceholderText("Enter system prompt for document summarization...")
        prompts_layout.addWidget(self.summary_system_prompt)
        
        # Reset prompts button
        reset_prompts_layout = QHBoxLayout()
        reset_prompts_layout.addStretch()
        
        reset_chat_button = QPushButton("Reset Chat Prompt")
        reset_chat_button.clicked.connect(self._on_reset_chat_prompt)
        reset_prompts_layout.addWidget(reset_chat_button)
        
        reset_summary_button = QPushButton("Reset Summary Prompt")
        reset_summary_button.clicked.connect(self._on_reset_summary_prompt)
        reset_prompts_layout.addWidget(reset_summary_button)
        
        prompts_layout.addLayout(reset_prompts_layout)
        
        layout.addWidget(prompts_group)
        
        # Create recent files group
        recent_group = QGroupBox("Recent Files")
        recent_layout = QFormLayout(recent_group)
        
        self.max_recent_spin = QSpinBox()
        self.max_recent_spin.setRange(0, 50)
        self.max_recent_spin.setSingleStep(5)
        recent_layout.addRow("Maximum Recent Files:", self.max_recent_spin)
        
        clear_recent_button = QPushButton("Clear Recent Files")
        clear_recent_button.clicked.connect(self._on_clear_recent)
        recent_layout.addRow("", clear_recent_button)
        
        layout.addWidget(recent_group)
        
        # Add spacer
        layout.addStretch()
        
        # Load current settings
        self._load_settings()
        
        # Initialize GPU detection
        self._initialize_gpu_detection()
    
    def _load_settings(self):
        """Load current settings from configuration."""
        # Directories
        self.model_dir_edit.setText(self.config_manager.get_value("default_model_dir", ""))
        
        # Hardware acceleration
        processing_unit = self.config_manager.get_value("processing_unit", "auto")
        if processing_unit == "cpu":
            self.cpu_radio.setChecked(True)
            self.hardware_stack.setCurrentIndex(0)
        elif processing_unit == "gpu":
            self.gpu_radio.setChecked(True)
            self.hardware_stack.setCurrentIndex(1)
        else:  # auto
            self.auto_radio.setChecked(True)
            self.hardware_stack.setCurrentIndex(0)  # Default to CPU settings view
        
        # CPU settings
        self.cpu_threads_spin.setValue(self.config_manager.get_value("cpu_threads", 4))
        self.cpu_memory_spin.setValue(self.config_manager.get_value("cpu_memory_limit", 0))
        
        # GPU settings
        self.gpu_layers_spin.setValue(self.config_manager.get_value("gpu_layers", 35))
        self.gpu_memory_spin.setValue(self.config_manager.get_value("gpu_memory_limit", 0))
        gpu_device = self.config_manager.get_value("gpu_device", -1)
        index = self.gpu_device_combo.findData(gpu_device)
        if index >= 0:
            self.gpu_device_combo.setCurrentIndex(index)
        
        # System prompts
        default_chat_prompt = "You are a helpful AI assistant. Please provide accurate, helpful, and concise responses."
        default_summary_prompt = "You are an AI assistant specialized in document summarization. Please provide clear, accurate summaries that capture the key points and main ideas."
        
        self.chat_system_prompt.setPlainText(
            self.config_manager.get_value("chat_system_prompt", default_chat_prompt)
        )
        self.summary_system_prompt.setPlainText(
            self.config_manager.get_value("summary_system_prompt", default_summary_prompt)
        )
        
        # Recent files
        self.max_recent_spin.setValue(self.config_manager.get_value("max_recent_models", 10))
    
    def save_settings(self):
        """Save settings to configuration."""
        # Directories
        self.config_manager.set_value("default_model_dir", self.model_dir_edit.text())
        
        # Hardware acceleration
        if self.auto_radio.isChecked():
            processing_unit = "auto"
        elif self.cpu_radio.isChecked():
            processing_unit = "cpu"
        else:
            processing_unit = "gpu"
        self.config_manager.set_value("processing_unit", processing_unit)
        
        # GPU layers (simplified)
        gpu_layers = self.gpu_layers_slider.value()
        self.config_manager.set_value("gpu_layers", gpu_layers)
        
        # CPU settings
        self.config_manager.set_value("cpu_threads", self.cpu_threads_spin.value())
        self.config_manager.set_value("cpu_memory_limit", self.cpu_memory_spin.value())
        
        # GPU settings (legacy compatibility)
        self.config_manager.set_value("gpu_layers", self.gpu_layers_spin.value())
        self.config_manager.set_value("gpu_memory_limit", self.gpu_memory_spin.value())
        self.config_manager.set_value("gpu_device", self.gpu_device_combo.currentData())
        
        # System prompts
        self.config_manager.set_value("chat_system_prompt", self.chat_system_prompt.toPlainText())
        self.config_manager.set_value("summary_system_prompt", self.summary_system_prompt.toPlainText())
        
        # Recent files
        self.config_manager.set_value("max_recent_models", self.max_recent_spin.value())
    
    def _on_browse_model_dir(self):
        """Handle browse button click for model directory."""
        directory = QFileDialog.getExistingDirectory(
            self,
            "Select Default Model Directory",
            self.model_dir_edit.text() or str(Path.home())
        )
        
        if directory:
            self.model_dir_edit.setText(directory)
    
    def _on_clear_recent(self):
        """Handle clear recent files button click."""
        self.config_manager.set_value("recent_models", [])
    
    def _on_processing_unit_changed(self):
        """Handle processing unit radio button change."""
        if self.cpu_radio.isChecked():
            self.hardware_stack.setCurrentIndex(0)
        else:
            self.hardware_stack.setCurrentIndex(1)
    
    def _on_reset_chat_prompt(self):
        """Reset chat system prompt to default."""
        default_prompt = "You are a helpful AI assistant. Please provide accurate, helpful, and concise responses."
        self.chat_system_prompt.setPlainText(default_prompt)
    
    def _on_reset_summary_prompt(self):
        """Reset summary system prompt to default."""
        default_prompt = "You are an AI assistant specialized in document summarization. Please provide clear, accurate summaries that capture the key points and main ideas."
        self.summary_system_prompt.setPlainText(default_prompt)
    
    def _initialize_gpu_detection(self):
        """Initialize GPU detection."""
        try:
            from llmtoolkit.app.core.gpu_acceleration import GPUAcceleration
            self.gpu_accel = GPUAcceleration(config_manager=self.config_manager)
            
            # Start GPU detection in background
            self._detect_gpus_async()
            
        except ImportError as e:
            self.logger.warning(f"GPU acceleration not available: {e}")
            self.gpu_status_label.setText("GPU detection not available")
            self.detect_gpu_button.setEnabled(False)
    
    def _detect_gpus_async(self):
        """Detect GPUs asynchronously."""
        try:
            self.gpu_status_label.setText("Detecting GPU...")
            self.detect_gpu_button.setEnabled(False)
            
            # Perform detection
            has_gpu = self.gpu_accel.detect_gpu()
            
            # Update UI with results
            self._update_gpu_ui()
            
        except Exception as e:
            self.logger.error(f"GPU detection failed: {e}")
            self.gpu_status_label.setText("GPU detection failed")
        finally:
            self.detect_gpu_button.setEnabled(True)
    
    def _update_gpu_ui(self):
        """Update GPU-related UI elements."""
        if not hasattr(self, 'gpu_accel'):
            return
        
        # Update status label
        if self.gpu_accel.has_gpu:
            status_text = self.gpu_accel.get_status_message()
            self.gpu_status_label.setText(status_text)
            self.gpu_status_label.setStyleSheet("color: green;")
        else:
            self.gpu_status_label.setText("No compatible GPU detected - CPU only")
            self.gpu_status_label.setStyleSheet("color: orange;")
        
        # Update processing unit options based on GPU availability
        if self.gpu_accel.has_gpu:
            self.auto_radio.setText("Auto (GPU Recommended)")
            self.gpu_radio.setEnabled(True)
            self.gpu_layers_slider.setEnabled(True)
        else:
            self.auto_radio.setText("Auto (CPU Only)")
            self.gpu_radio.setEnabled(False)
            self.gpu_layers_slider.setEnabled(False)
        
        # Load current GPU layers setting
        gpu_layers = self.config_manager.get_value("gpu_layers", 35)
        self.gpu_layers_slider.setValue(gpu_layers)
        self.gpu_layers_label.setText(str(gpu_layers))
    
    def _update_device_combo(self):
        """Update the device combo box based on selected backend."""
        self.gpu_device_combo.clear()
        
        if not self.gpu_capabilities or not self.gpu_capabilities.devices:
            return
        
        current_backend = self.gpu_backend_combo.currentData()
        if not current_backend:
            return
        
        # Add devices for the selected backend
        from llmtoolkit.app.core.gpu_detector import GPUBackend
        try:
            backend_enum = GPUBackend(current_backend)
            devices = [d for d in self.gpu_capabilities.devices if d.backend == backend_enum]
            
            for device in devices:
                device_text = f"{device.name} ({device.memory_total} MB)"
                self.gpu_device_combo.addItem(device_text, device.id)
                
        except ValueError:
            pass  # Invalid backend
    
    def _on_detect_gpus(self):
        """Handle detect GPUs button click."""
        self._detect_gpus_async()
    
    def _on_backend_changed(self):
        """Handle GPU backend selection change."""
        self._update_device_combo()
    
    def _on_install_gpu_support(self):
        """Handle install GPU support button click."""
        if not self.gpu_capabilities:
            return
        
        from llmtoolkit.app.ui.gpu_installation_dialog import GPUInstallationDialog
        
        # Check if any backends need installation
        available_backends = []
        for backend_name, available in self.gpu_capabilities.dependencies_status.items():
            if not available:
                available_backends.append(backend_name)
        
        if not available_backends:
            from PySide6.QtWidgets import QMessageBox
            QMessageBox.information(
                self, 
                "GPU Support", 
                "All available GPU backends are already installed.\n\n"
                "If you're still having issues, try restarting the application or checking your GPU drivers."
            )
            return
        
        # Show comprehensive installation dialog
        dialog = GPUInstallationDialog(self.gpu_detector, self)
        result = dialog.exec()
        
        # Re-detect GPUs after dialog closes
        if result == QDialog.Accepted or True:  # Always re-detect
            self._detect_gpus_async()

class AddonSettingsWidget(QWidget):
    """Widget for addon-related settings."""
    
    def __init__(self, config_manager, parent=None):
        """
        Initialize the addon settings widget.
        
        Args:
            config_manager: The application configuration manager
            parent: Parent widget
        """
        super().__init__(parent)
        self.logger = logging.getLogger("gguf_loader.ui.preferences.addon")
        self.config_manager = config_manager
        
        # Create layout
        layout = QVBoxLayout(self)
        
        # Create directories group
        directories_group = QGroupBox("Directories")
        directories_layout = QFormLayout(directories_group)
        
        # Addon directory
        addon_dir_layout = QHBoxLayout()
        self.addon_dir_edit = QLineEdit()
        addon_dir_layout.addWidget(self.addon_dir_edit)
        
        browse_button = QToolButton()
        browse_button.setText("...")
        browse_button.clicked.connect(self._on_browse_addon_dir)
        addon_dir_layout.addWidget(browse_button)
        
        directories_layout.addRow("Addon Directory:", addon_dir_layout)
        
        layout.addWidget(directories_group)
        
        # Create security group
        security_group = QGroupBox("Security")
        security_layout = QVBoxLayout(security_group)
        
        self.verify_addons_check = QCheckBox("Verify addons before installation")
        security_layout.addWidget(self.verify_addons_check)
        
        self.sandbox_addons_check = QCheckBox("Run addons in sandbox mode")
        security_layout.addWidget(self.sandbox_addons_check)
        
        self.allow_network_check = QCheckBox("Allow addons to access network")
        security_layout.addWidget(self.allow_network_check)
        
        layout.addWidget(security_group)
        
        # Create updates group
        updates_group = QGroupBox("Updates")
        updates_layout = QVBoxLayout(updates_group)
        
        self.auto_update_check = QCheckBox("Automatically update addons")
        updates_layout.addWidget(self.auto_update_check)
        
        layout.addWidget(updates_group)
        
        # Add spacer
        layout.addStretch()
        
        # Load current settings
        self._load_settings()
    
    def _load_settings(self):
        """Load current settings from configuration."""
        # Directories
        self.addon_dir_edit.setText(self.config_manager.get_value("addon_dir", ""))
        
        # Security
        self.verify_addons_check.setChecked(self.config_manager.get_value("verify_addons", True))
        self.sandbox_addons_check.setChecked(self.config_manager.get_value("sandbox_addons", True))
        self.allow_network_check.setChecked(self.config_manager.get_value("allow_addon_network", False))
        
        # Updates
        self.auto_update_check.setChecked(self.config_manager.get_value("auto_update_addons", False))
    
    def save_settings(self):
        """Save settings to configuration."""
        # Directories
        self.config_manager.set_value("addon_dir", self.addon_dir_edit.text())
        
        # Security
        self.config_manager.set_value("verify_addons", self.verify_addons_check.isChecked())
        self.config_manager.set_value("sandbox_addons", self.sandbox_addons_check.isChecked())
        self.config_manager.set_value("allow_addon_network", self.allow_network_check.isChecked())
        
        # Updates
        self.config_manager.set_value("auto_update_addons", self.auto_update_check.isChecked())
    
    def _on_browse_addon_dir(self):
        """Handle browse button click for addon directory."""
        directory = QFileDialog.getExistingDirectory(
            self,
            "Select Addon Directory",
            self.addon_dir_edit.text() or str(Path.home())
        )
        
        if directory:
            self.addon_dir_edit.setText(directory)

class AdvancedSettingsWidget(QWidget):
    """Widget for advanced application settings."""
    
    def __init__(self, config_manager, parent=None):
        """
        Initialize the advanced settings widget.
        
        Args:
            config_manager: The application configuration manager
            parent: Parent widget
        """
        super().__init__(parent)
        self.logger = logging.getLogger("gguf_loader.ui.preferences.advanced")
        self.config_manager = config_manager
        
        # Create layout
        layout = QVBoxLayout(self)
        
        # Create performance group
        performance_group = QGroupBox("Performance")
        performance_layout = QFormLayout(performance_group)
        
        self.thread_count_spin = QSpinBox()
        self.thread_count_spin.setRange(1, 64)
        performance_layout.addRow("Thread Count:", self.thread_count_spin)
        
        self.cache_size_spin = QSpinBox()
        self.cache_size_spin.setRange(0, 10 * 1024)  # 0 to 10 GB
        self.cache_size_spin.setSingleStep(128)  # 128 MB steps
        self.cache_size_spin.setSuffix(" MB")
        self.cache_size_spin.setSpecialValueText("No Cache")
        performance_layout.addRow("Cache Size:", self.cache_size_spin)
        
        layout.addWidget(performance_group)
        
        # Create experimental group
        experimental_group = QGroupBox("Experimental Features")
        experimental_layout = QVBoxLayout(experimental_group)
        
        self.enable_experimental_check = QCheckBox("Enable experimental features")
        experimental_layout.addWidget(self.enable_experimental_check)
        
        layout.addWidget(experimental_group)
        
        # Create reset group
        reset_group = QGroupBox("Reset")
        reset_layout = QVBoxLayout(reset_group)
        
        reset_button = QPushButton("Reset All Settings to Defaults")
        reset_button.clicked.connect(self._on_reset_settings)
        reset_layout.addWidget(reset_button)
        
        layout.addWidget(reset_group)
        
        # Add spacer
        layout.addStretch()
        
        # Load current settings
        self._load_settings()
    
    def _load_settings(self):
        """Load current settings from configuration."""
        # Performance
        self.thread_count_spin.setValue(self.config_manager.get_value("thread_count", 4))
        self.cache_size_spin.setValue(self.config_manager.get_value("cache_size", 1024))
        
        # Experimental
        self.enable_experimental_check.setChecked(self.config_manager.get_value("enable_experimental", False))
    
    def save_settings(self):
        """Save settings to configuration."""
        # Performance
        self.config_manager.set_value("thread_count", self.thread_count_spin.value())
        self.config_manager.set_value("cache_size", self.cache_size_spin.value())
        
        # Experimental
        self.config_manager.set_value("enable_experimental", self.enable_experimental_check.isChecked())
    
    def _on_reset_settings(self):
        """Handle reset settings button click."""
        from PySide6.QtWidgets import QMessageBox
        
        result = QMessageBox.question(
            self,
            "Reset Settings",
            "Are you sure you want to reset all settings to their default values?",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No
        )
        
        if result == QMessageBox.Yes:
            self.config_manager.reset_to_defaults()
            self._load_settings()

class PreferencesDialog(QDialog):
    """
    Dialog for customizing application preferences.
    
    This dialog allows users to customize various aspects of the application,
    including appearance, behavior, and performance settings.
    """
    
    def __init__(self, config_manager, parent=None):
        """
        Initialize the preferences dialog.
        
        Args:
            config_manager: The application configuration manager
            parent: Parent widget
        """
        super().__init__(parent)
        self.logger = logging.getLogger("gguf_loader.ui.preferences")
        self.config_manager = config_manager
        
        # Set dialog properties
        self.setWindowTitle("Preferences")
        self.resize(600, 500)
        self.setModal(True)
        
        # Create layout
        layout = QVBoxLayout(self)
        
        # Create tab widget
        self.tab_widget = QTabWidget()
        
        # Create general settings tab
        self.general_widget = GeneralSettingsWidget(config_manager)
        self.tab_widget.addTab(self.general_widget, "General")
        
        # Create model settings tab
        self.model_widget = ModelSettingsWidget(config_manager)
        self.tab_widget.addTab(self.model_widget, "Models")
        
        # Create backend management tab
        self.backend_widget = BackendManagementWidget(config_manager)
        self.tab_widget.addTab(self.backend_widget, "Backend Management")
        
        # Create addon settings tab
        self.addon_widget = AddonSettingsWidget(config_manager)
        self.tab_widget.addTab(self.addon_widget, "Addons")
        
        # Create advanced settings tab
        self.advanced_widget = AdvancedSettingsWidget(config_manager)
        self.tab_widget.addTab(self.advanced_widget, "Advanced")
        
        layout.addWidget(self.tab_widget)
        
        # Create button box
        button_box = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel | QDialogButtonBox.Apply)
        button_box.accepted.connect(self.accept)
        button_box.rejected.connect(self.reject)
        button_box.button(QDialogButtonBox.Apply).clicked.connect(self._on_apply)
        
        layout.addWidget(button_box)
        
        self.logger.info("Preferences dialog initialized")
    
    def accept(self):
        """Handle dialog acceptance."""
        self._save_settings()
        super().accept()
    
    def _on_apply(self):
        """Handle apply button click."""
        self._save_settings()
    
    def _save_settings(self):
        """Save all settings."""
        self.general_widget.save_settings()
        self.model_widget.save_settings()
        self.backend_widget.save_settings()
        self.addon_widget.save_settings()
        self.advanced_widget.save_settings()
        
        # Save configuration to disk
        self.config_manager.save()
        
        self.logger.info("Preferences saved")
    
    def closeEvent(self, event):
        """Handle dialog close event."""
        # Clean up backend management widget
        if hasattr(self, 'backend_widget'):
            self.backend_widget.cleanup()
        super().closeEvent(event)