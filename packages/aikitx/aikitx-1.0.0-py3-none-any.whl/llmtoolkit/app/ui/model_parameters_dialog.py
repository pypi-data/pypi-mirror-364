"""
Model Parameters Dialog

This module provides a dialog for configuring model generation parameters
such as temperature, max tokens, top-p, top-k, and other sampling settings.
"""

import logging
from typing import Dict, Any

from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, 
    QSlider, QSpinBox, QDoubleSpinBox, QGroupBox, QFormLayout,
    QTextEdit, QCheckBox, QMessageBox
)
from PySide6.QtCore import Qt, Signal, Slot
from PySide6.QtGui import QFont


class ModelParametersDialog(QDialog):
    """
    Dialog for configuring model generation parameters.
    
    Features:
    - Temperature control for randomness
    - Max tokens for response length
    - Top-p and Top-k sampling parameters
    - Repetition penalty settings
    - Stop sequences configuration
    - Parameter presets
    """
    
    # Signals
    parameters_changed = Signal(dict)  # Emitted when parameters change
    
    # Parameter presets
    PRESETS = {
        "Balanced": {
            "temperature": 0.7,
            "max_tokens": 512,
            "top_p": 0.9,
            "top_k": 40,
            "repeat_penalty": 1.1,
            "stop_sequences": ["Human:", "User:", "Assistant:"]
        },
        "Creative": {
            "temperature": 0.9,
            "max_tokens": 1024,
            "top_p": 0.95,
            "top_k": 50,
            "repeat_penalty": 1.05,
            "stop_sequences": ["Human:", "User:"]
        },
        "Precise": {
            "temperature": 0.3,
            "max_tokens": 256,
            "top_p": 0.8,
            "top_k": 20,
            "repeat_penalty": 1.15,
            "stop_sequences": ["Human:", "User:", "Assistant:", "\n\n"]
        },
        "Conversational": {
            "temperature": 0.8,
            "max_tokens": 512,
            "top_p": 0.9,
            "top_k": 40,
            "repeat_penalty": 1.1,
            "stop_sequences": ["Human:", "User:"]
        }
    }
    
    def __init__(self, config_manager, current_params: Dict[str, Any] = None, parent=None):
        """
        Initialize the model parameters dialog.
        
        Args:
            config_manager: Configuration manager for saving settings
            current_params: Current model parameters
            parent: Parent widget
        """
        super().__init__(parent)
        
        self.logger = logging.getLogger("gguf_loader.ui.model_parameters_dialog")
        self.config_manager = config_manager
        self.current_params = current_params or self.PRESETS["Balanced"].copy()
        
        # Set dialog properties
        self.setWindowTitle("Model Parameters Configuration")
        self.setModal(True)
        self.setMinimumSize(600, 700)
        
        # Initialize UI
        self._init_ui()
        
        # Load current settings
        self._load_settings()
        
        self.logger.info("Model parameters dialog initialized")
    
    def _init_ui(self):
        """Initialize the user interface."""
        layout = QVBoxLayout(self)
        layout.setSpacing(15)
        layout.setContentsMargins(20, 20, 20, 20)
        
        # Title
        title_label = QLabel("Model Parameters Configuration")
        title_font = QFont()
        title_font.setPointSize(14)
        title_font.setBold(True)
        title_label.setFont(title_font)
        layout.addWidget(title_label)
        
        # Presets section
        presets_group = self._create_presets_group()
        layout.addWidget(presets_group)
        
        # Parameters section
        params_group = self._create_parameters_group()
        layout.addWidget(params_group)
        
        # Stop sequences section
        stop_group = self._create_stop_sequences_group()
        layout.addWidget(stop_group)
        
        # Button layout
        button_layout = QHBoxLayout()
        button_layout.addStretch()
        
        # Reset button
        reset_button = QPushButton("Reset to Defaults")
        reset_button.clicked.connect(self._reset_to_defaults)
        button_layout.addWidget(reset_button)
        
        # Cancel button
        cancel_button = QPushButton("Cancel")
        cancel_button.clicked.connect(self.reject)
        button_layout.addWidget(cancel_button)
        
        # Apply button
        self.apply_button = QPushButton("Apply")
        self.apply_button.setDefault(True)
        self.apply_button.setStyleSheet("""
            QPushButton {
                background-color: #0078d4;
                color: white;
                border: none;
                border-radius: 4px;
                padding: 8px 16px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #106ebe;
            }
        """)
        self.apply_button.clicked.connect(self._apply_changes)
        button_layout.addWidget(self.apply_button)
        
        layout.addLayout(button_layout)
    
    def _create_presets_group(self):
        """Create the presets group."""
        group = QGroupBox("Parameter Presets")
        layout = QHBoxLayout(group)
        
        for preset_name in self.PRESETS.keys():
            button = QPushButton(preset_name)
            button.setStyleSheet("""
                QPushButton {
                    padding: 8px 16px;
                    border: 2px solid #dee2e6;
                    border-radius: 6px;
                    background-color: white;
                    font-weight: bold;
                }
                QPushButton:hover {
                    background-color: #f8f9fa;
                    border-color: #0078d4;
                }
                QPushButton:pressed {
                    background-color: #e9ecef;
                }
            """)
            button.clicked.connect(lambda checked, name=preset_name: self._load_preset(name))
            layout.addWidget(button)
        
        return group
    
    def _create_parameters_group(self):
        """Create the parameters configuration group."""
        group = QGroupBox("Generation Parameters")
        layout = QFormLayout(group)
        
        # Temperature
        temp_layout = QHBoxLayout()
        self.temperature_slider = QSlider(Qt.Horizontal)
        self.temperature_slider.setRange(1, 200)  # 0.01 to 2.00
        self.temperature_slider.setValue(70)  # 0.7 default
        self.temperature_spinbox = QDoubleSpinBox()
        self.temperature_spinbox.setRange(0.01, 2.0)
        self.temperature_spinbox.setSingleStep(0.01)
        self.temperature_spinbox.setDecimals(2)
        self.temperature_spinbox.setValue(0.7)
        
        # Connect temperature controls
        self.temperature_slider.valueChanged.connect(
            lambda v: self.temperature_spinbox.setValue(v / 100.0)
        )
        self.temperature_spinbox.valueChanged.connect(
            lambda v: self.temperature_slider.setValue(int(v * 100))
        )
        
        temp_layout.addWidget(self.temperature_slider)
        temp_layout.addWidget(self.temperature_spinbox)
        layout.addRow("Temperature (randomness):", temp_layout)
        
        # Max Tokens
        self.max_tokens_spinbox = QSpinBox()
        self.max_tokens_spinbox.setRange(1, 4096)
        self.max_tokens_spinbox.setValue(512)
        layout.addRow("Max Tokens (response length):", self.max_tokens_spinbox)
        
        # Top-p
        top_p_layout = QHBoxLayout()
        self.top_p_slider = QSlider(Qt.Horizontal)
        self.top_p_slider.setRange(1, 100)  # 0.01 to 1.00
        self.top_p_slider.setValue(90)  # 0.9 default
        self.top_p_spinbox = QDoubleSpinBox()
        self.top_p_spinbox.setRange(0.01, 1.0)
        self.top_p_spinbox.setSingleStep(0.01)
        self.top_p_spinbox.setDecimals(2)
        self.top_p_spinbox.setValue(0.9)
        
        # Connect top-p controls
        self.top_p_slider.valueChanged.connect(
            lambda v: self.top_p_spinbox.setValue(v / 100.0)
        )
        self.top_p_spinbox.valueChanged.connect(
            lambda v: self.top_p_slider.setValue(int(v * 100))
        )
        
        top_p_layout.addWidget(self.top_p_slider)
        top_p_layout.addWidget(self.top_p_spinbox)
        layout.addRow("Top-p (nucleus sampling):", top_p_layout)
        
        # Top-k
        self.top_k_spinbox = QSpinBox()
        self.top_k_spinbox.setRange(1, 100)
        self.top_k_spinbox.setValue(40)
        layout.addRow("Top-k (token selection):", self.top_k_spinbox)
        
        # Repeat Penalty
        repeat_layout = QHBoxLayout()
        self.repeat_penalty_slider = QSlider(Qt.Horizontal)
        self.repeat_penalty_slider.setRange(100, 150)  # 1.0 to 1.5
        self.repeat_penalty_slider.setValue(110)  # 1.1 default
        self.repeat_penalty_spinbox = QDoubleSpinBox()
        self.repeat_penalty_spinbox.setRange(1.0, 1.5)
        self.repeat_penalty_spinbox.setSingleStep(0.01)
        self.repeat_penalty_spinbox.setDecimals(2)
        self.repeat_penalty_spinbox.setValue(1.1)
        
        # Connect repeat penalty controls
        self.repeat_penalty_slider.valueChanged.connect(
            lambda v: self.repeat_penalty_spinbox.setValue(v / 100.0)
        )
        self.repeat_penalty_spinbox.valueChanged.connect(
            lambda v: self.repeat_penalty_slider.setValue(int(v * 100))
        )
        
        repeat_layout.addWidget(self.repeat_penalty_slider)
        repeat_layout.addWidget(self.repeat_penalty_spinbox)
        layout.addRow("Repeat Penalty (reduce repetition):", repeat_layout)
        
        return group
    
    def _create_stop_sequences_group(self):
        """Create the stop sequences configuration group."""
        group = QGroupBox("Stop Sequences")
        layout = QVBoxLayout(group)
        
        # Description
        desc_label = QLabel("Enter stop sequences (one per line) to control when generation stops:")
        desc_label.setStyleSheet("color: #6c757d; font-size: 12px;")
        layout.addWidget(desc_label)
        
        # Stop sequences editor
        self.stop_sequences_editor = QTextEdit()
        self.stop_sequences_editor.setMaximumHeight(100)
        self.stop_sequences_editor.setPlaceholderText("Human:\nUser:\nAssistant:")
        self.stop_sequences_editor.setStyleSheet("""
            QTextEdit {
                border: 2px solid #dee2e6;
                border-radius: 6px;
                padding: 10px;
                font-family: 'Courier New', monospace;
                font-size: 12px;
                background-color: white;
            }
            QTextEdit:focus {
                border-color: #0078d4;
            }
        """)
        layout.addWidget(self.stop_sequences_editor)
        
        return group
    
    def _load_settings(self):
        """Load current settings."""
        # Load saved parameters or use defaults
        saved_params = self.config_manager.get_value("model_parameters", self.PRESETS["Balanced"])
        
        # Update UI controls
        self.temperature_spinbox.setValue(saved_params.get("temperature", 0.7))
        self.max_tokens_spinbox.setValue(saved_params.get("max_tokens", 512))
        self.top_p_spinbox.setValue(saved_params.get("top_p", 0.9))
        self.top_k_spinbox.setValue(saved_params.get("top_k", 40))
        self.repeat_penalty_spinbox.setValue(saved_params.get("repeat_penalty", 1.1))
        
        # Load stop sequences
        stop_sequences = saved_params.get("stop_sequences", ["Human:", "User:", "Assistant:"])
        self.stop_sequences_editor.setText("\n".join(stop_sequences))
    
    def _load_preset(self, preset_name: str):
        """Load a parameter preset."""
        if preset_name not in self.PRESETS:
            return
        
        preset = self.PRESETS[preset_name]
        
        # Update UI controls
        self.temperature_spinbox.setValue(preset["temperature"])
        self.max_tokens_spinbox.setValue(preset["max_tokens"])
        self.top_p_spinbox.setValue(preset["top_p"])
        self.top_k_spinbox.setValue(preset["top_k"])
        self.repeat_penalty_spinbox.setValue(preset["repeat_penalty"])
        
        # Update stop sequences
        self.stop_sequences_editor.setText("\n".join(preset["stop_sequences"]))
        
        self.logger.info(f"Loaded preset: {preset_name}")
    
    def _reset_to_defaults(self):
        """Reset to default parameters."""
        self._load_preset("Balanced")
        self.logger.info("Reset to default parameters")
    
    def _apply_changes(self):
        """Apply the changes and close dialog."""
        # Collect parameters
        parameters = {
            "temperature": self.temperature_spinbox.value(),
            "max_tokens": self.max_tokens_spinbox.value(),
            "top_p": self.top_p_spinbox.value(),
            "top_k": self.top_k_spinbox.value(),
            "repeat_penalty": self.repeat_penalty_spinbox.value(),
            "stop_sequences": [
                seq.strip() for seq in self.stop_sequences_editor.toPlainText().split("\n")
                if seq.strip()
            ]
        }
        
        # Validate parameters
        if parameters["temperature"] <= 0:
            QMessageBox.warning(self, "Invalid Parameter", "Temperature must be greater than 0.")
            return
        
        if parameters["max_tokens"] <= 0:
            QMessageBox.warning(self, "Invalid Parameter", "Max tokens must be greater than 0.")
            return
        
        # Save to configuration
        self.config_manager.set_value("model_parameters", parameters)
        
        # Emit signal
        self.parameters_changed.emit(parameters)
        
        self.logger.info(f"Applied model parameters: {parameters}")
        self.accept()
    
    def get_current_parameters(self) -> Dict[str, Any]:
        """Get the current parameters."""
        return {
            "temperature": self.temperature_spinbox.value(),
            "max_tokens": self.max_tokens_spinbox.value(),
            "top_p": self.top_p_spinbox.value(),
            "top_k": self.top_k_spinbox.value(),
            "repeat_penalty": self.repeat_penalty_spinbox.value(),
            "stop_sequences": [
                seq.strip() for seq in self.stop_sequences_editor.toPlainText().split("\n")
                if seq.strip()
            ]
        }