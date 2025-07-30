"""
Universal Model Selection Dialog

This dialog provides a unified interface for selecting models from different sources:
- Local files (GGUF, safetensors, PyTorch bin)
- Local directories (multi-file models)
- Hugging Face model IDs
- Recent models and favorites

Requirements addressed: 1.1, 1.2, 1.5, 1.6
"""

import os
import json
import logging
import time
from pathlib import Path
from typing import Dict, Any, Optional, List, Tuple

from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, 
    QFileDialog, QLineEdit, QComboBox, QTabWidget, QWidget,
    QListWidget, QListWidgetItem, QTextEdit, QProgressBar,
    QMessageBox, QGroupBox, QCheckBox, QSpinBox, QFormLayout,
    QSplitter, QTreeWidget, QTreeWidgetItem, QHeaderView
)
from PySide6.QtCore import Qt, Signal, QThread, QTimer
from PySide6.QtGui import QIcon, QFont, QPixmap

from ..core.universal_format_detector import ModelFormat, FormatDetectionResult
from ..services.universal_model_loader import UniversalModelLoader
from ..core.universal_events import UniversalLoadingProgress
from ..services.huggingface_integration import HuggingFaceIntegration
from ..ui.theme_manager import ThemeManager


class ModelValidationThread(QThread):
    """Thread for validating model paths without blocking UI."""
    
    validation_completed = Signal(str, bool, str)  # path, is_valid, message
    
    def __init__(self, model_loader: UniversalModelLoader, model_path: str):
        super().__init__()
        self.model_loader = model_loader
        self.model_path = model_path
    
    def run(self):
        """Run validation in background thread."""
        try:
            is_valid, error_message = self.model_loader.validate_model_path(self.model_path)
            self.validation_completed.emit(self.model_path, is_valid, error_message or "")
        except Exception as e:
            self.validation_completed.emit(self.model_path, False, str(e))


class HuggingFaceSearchThread(QThread):
    """Thread for searching Hugging Face models."""
    
    search_completed = Signal(list)  # List of model results
    search_failed = Signal(str)  # Error message
    
    def __init__(self, hf_integration: HuggingFaceIntegration, query: str):
        super().__init__()
        self.hf_integration = hf_integration
        self.query = query
    
    def run(self):
        """Run HF search in background thread."""
        try:
            # This would need to be implemented in HuggingFaceIntegration
            # For now, return empty results
            results = []
            self.search_completed.emit(results)
        except Exception as e:
            self.search_failed.emit(str(e))


class UniversalModelDialog(QDialog):
    """
    Universal model selection dialog supporting multiple model sources.
    
    Features:
    - File browser for local models
    - Directory browser for multi-file models
    - Hugging Face model ID input and search
    - Recent models list
    - Model validation and format detection
    - Backend recommendations
    """
    
    model_selected = Signal(str, ModelFormat)  # model_path, format
    
    def __init__(self, model_loader: UniversalModelLoader, config_manager, parent=None):
        """
        Initialize the universal model dialog.
        
        Args:
            model_loader: Universal model loader instance
            config_manager: Configuration manager
            parent: Parent widget
        """
        super().__init__(parent)
        
        self.logger = logging.getLogger("universal_model_dialog")
        self.model_loader = model_loader
        self.config_manager = config_manager
        self.hf_integration = HuggingFaceIntegration()
        
        # Dialog state
        self.selected_model_path = ""
        self.detected_format = ModelFormat.UNKNOWN
        self.validation_thread = None
        self.search_thread = None
        
        # Recent models (loaded from config)
        self.recent_models = self._load_recent_models()
        
        # Setup UI
        self.setWindowTitle("Select Model")
        self.setModal(True)
        self.resize(800, 600)
        
        self._init_ui()
        self._connect_signals()
        
        # Load saved state
        self._load_dialog_state()
    
    def _init_ui(self):
        """Initialize the user interface."""
        layout = QVBoxLayout(self)
        layout.setSpacing(10)
        
        # Create tab widget for different model sources
        self.tab_widget = QTabWidget()
        layout.addWidget(self.tab_widget)
        
        # Tab 1: Local Files
        self._create_local_files_tab()
        
        # Tab 2: Hugging Face
        self._create_huggingface_tab()
        
        # Tab 3: Recent Models
        self._create_recent_models_tab()
        
        # Model information panel
        self._create_model_info_panel()
        layout.addWidget(self.model_info_group)
        
        # Validation status
        self.validation_label = QLabel("No model selected")
        self.validation_label.setStyleSheet("color: gray;")
        layout.addWidget(self.validation_label)
        
        # Progress bar for validation/loading
        self.progress_bar = QProgressBar()
        self.progress_bar.setVisible(False)
        layout.addWidget(self.progress_bar)
        
        # Dialog buttons
        button_layout = QHBoxLayout()
        
        self.validate_button = QPushButton("Validate Model")
        self.validate_button.clicked.connect(self._validate_current_model)
        self.validate_button.setEnabled(False)
        button_layout.addWidget(self.validate_button)
        
        button_layout.addStretch()
        
        self.cancel_button = QPushButton("Cancel")
        self.cancel_button.clicked.connect(self.reject)
        button_layout.addWidget(self.cancel_button)
        
        self.select_button = QPushButton("Select Model")
        self.select_button.clicked.connect(self._select_model)
        self.select_button.setEnabled(False)
        self.select_button.setDefault(True)
        button_layout.addWidget(self.select_button)
        
        layout.addLayout(button_layout)
    
    def _create_local_files_tab(self):
        """Create the local files tab."""
        tab = QWidget()
        layout = QVBoxLayout(tab)
        
        # File selection section
        file_group = QGroupBox("Select Model File or Directory")
        file_layout = QVBoxLayout(file_group)
        
        # Path input
        path_layout = QHBoxLayout()
        
        self.path_input = QLineEdit()
        self.path_input.setPlaceholderText("Enter path to model file or directory...")
        self.path_input.textChanged.connect(self._on_path_changed)
        path_layout.addWidget(self.path_input)
        
        self.browse_file_button = QPushButton("Browse File...")
        self.browse_file_button.clicked.connect(self._browse_file)
        path_layout.addWidget(self.browse_file_button)
        
        self.browse_dir_button = QPushButton("Browse Directory...")
        self.browse_dir_button.clicked.connect(self._browse_directory)
        path_layout.addWidget(self.browse_dir_button)
        
        file_layout.addLayout(path_layout)
        
        # Supported formats info
        formats_label = QLabel(
            "Supported formats: GGUF (.gguf), Safetensors (.safetensors), "
            "PyTorch (.bin, .pt, .pth), Multi-file model directories"
        )
        formats_label.setStyleSheet("color: gray; font-size: 10px;")
        formats_label.setWordWrap(True)
        file_layout.addWidget(formats_label)
        
        layout.addWidget(file_group)
        
        # Quick access to common directories
        quick_access_group = QGroupBox("Quick Access")
        quick_layout = QVBoxLayout(quick_access_group)
        
        # Common model directories
        common_dirs = [
            ("Models folder", os.path.expanduser("~/models")),
            ("Downloads", os.path.expanduser("~/Downloads")),
            ("Desktop", os.path.expanduser("~/Desktop")),
        ]
        
        for name, path in common_dirs:
            if os.path.exists(path):
                button = QPushButton(f"{name} ({path})")
                button.clicked.connect(lambda checked, p=path: self._set_directory(p))
                quick_layout.addWidget(button)
        
        layout.addWidget(quick_access_group)
        
        # Model files list (for directories with multiple models)
        self.model_files_group = QGroupBox("Available Models")
        model_files_layout = QVBoxLayout(self.model_files_group)
        
        self.model_files_list = QListWidget()
        self.model_files_list.itemClicked.connect(self._on_model_file_selected)
        model_files_layout.addWidget(self.model_files_list)
        
        self.model_files_group.setVisible(False)  # Hidden by default
        layout.addWidget(self.model_files_group)
        
        layout.addStretch()
        
        self.tab_widget.addTab(tab, "Local Files")
    
    def _create_huggingface_tab(self):
        """Create the Hugging Face tab."""
        tab = QWidget()
        layout = QVBoxLayout(tab)
        
        # Model ID input section
        id_group = QGroupBox("Hugging Face Model ID")
        id_layout = QVBoxLayout(id_group)
        
        # Model ID input
        id_input_layout = QHBoxLayout()
        
        self.hf_input = QLineEdit()
        self.hf_input.setPlaceholderText("Enter Hugging Face model ID (e.g., microsoft/DialoGPT-medium)")
        self.hf_input.textChanged.connect(self._on_hf_input_changed)
        id_input_layout.addWidget(self.hf_input)
        
        self.hf_validate_button = QPushButton("Validate")
        self.hf_validate_button.clicked.connect(self._validate_hf_model)
        self.hf_validate_button.setEnabled(False)
        id_input_layout.addWidget(self.hf_validate_button)
        
        id_layout.addLayout(id_input_layout)
        
        # Examples
        examples_label = QLabel(
            "Examples: microsoft/DialoGPT-medium, huggingface/CodeBERTa-small-v1, "
            "deepseek-ai/deepseek-coder-6.7b-instruct"
        )
        examples_label.setStyleSheet("color: gray; font-size: 10px;")
        examples_label.setWordWrap(True)
        id_layout.addWidget(examples_label)
        
        layout.addWidget(id_group)
        
        # Search section (placeholder for future implementation)
        search_group = QGroupBox("Search Models")
        search_layout = QVBoxLayout(search_group)
        
        search_input_layout = QHBoxLayout()
        
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Search Hugging Face models...")
        self.search_input.setEnabled(False)  # Disabled for now
        search_input_layout.addWidget(self.search_input)
        
        self.search_button = QPushButton("Search")
        self.search_button.setEnabled(False)  # Disabled for now
        search_input_layout.addWidget(self.search_button)
        
        search_layout.addLayout(search_input_layout)
        
        # Search results (placeholder)
        self.search_results = QListWidget()
        self.search_results.setEnabled(False)
        search_layout.addWidget(self.search_results)
        
        # Note about search feature
        search_note = QLabel("Note: Model search feature will be available in a future update.")
        search_note.setStyleSheet("color: gray; font-style: italic;")
        search_layout.addWidget(search_note)
        
        layout.addWidget(search_group)
        
        # Authentication section
        auth_group = QGroupBox("Authentication")
        auth_layout = QVBoxLayout(auth_group)
        
        auth_status = QLabel("Authentication status: Not configured")
        auth_status.setStyleSheet("color: orange;")
        auth_layout.addWidget(auth_status)
        
        auth_button = QPushButton("Configure Authentication")
        auth_button.setEnabled(False)  # Placeholder
        auth_layout.addWidget(auth_button)
        
        layout.addWidget(auth_group)
        
        layout.addStretch()
        
        self.tab_widget.addTab(tab, "Hugging Face")
    
    def _create_recent_models_tab(self):
        """Create the recent models tab."""
        tab = QWidget()
        layout = QVBoxLayout(tab)
        
        # Recent models list
        recent_group = QGroupBox("Recently Used Models")
        recent_layout = QVBoxLayout(recent_group)
        
        self.recent_list = QListWidget()
        self.recent_list.itemClicked.connect(self._on_recent_item_clicked)
        recent_layout.addWidget(self.recent_list)
        
        # Populate recent models
        self._populate_recent_models()
        
        # Clear recent button
        clear_button = QPushButton("Clear Recent Models")
        clear_button.clicked.connect(self._clear_recent_models)
        recent_layout.addWidget(clear_button)
        
        layout.addWidget(recent_group)
        
        # Favorites section (placeholder)
        favorites_group = QGroupBox("Favorite Models")
        favorites_layout = QVBoxLayout(favorites_group)
        
        self.favorites_list = QListWidget()
        favorites_layout.addWidget(self.favorites_list)
        
        favorites_note = QLabel("Favorites feature will be available in a future update.")
        favorites_note.setStyleSheet("color: gray; font-style: italic;")
        favorites_layout.addWidget(favorites_note)
        
        layout.addWidget(favorites_group)
        
        self.tab_widget.addTab(tab, "Recent & Favorites")
    
    def _create_model_info_panel(self):
        """Create the model information panel."""
        self.model_info_group = QGroupBox("Model Information")
        layout = QFormLayout(self.model_info_group)
        
        # Model details
        self.format_label = QLabel("Not detected")
        layout.addRow("Format:", self.format_label)
        
        self.size_label = QLabel("Unknown")
        layout.addRow("Size:", self.size_label)
        
        self.backend_label = QLabel("Not determined")
        layout.addRow("Recommended Backend:", self.backend_label)
        
        self.memory_label = QLabel("Unknown")
        layout.addRow("Memory Required:", self.memory_label)
        
        # Additional info text area
        self.info_text = QTextEdit()
        self.info_text.setMaximumHeight(100)
        self.info_text.setReadOnly(True)
        self.info_text.setPlaceholderText("Additional model information will appear here...")
        layout.addRow("Details:", self.info_text)
    
    def _connect_signals(self):
        """Connect internal signals."""
        # Model loader signals
        self.model_loader.format_detected.connect(self._on_format_detected)
        self.model_loader.progress_updated.connect(self._on_progress_updated)
    
    def _browse_file(self):
        """Browse for a model file."""
        file_dialog = QFileDialog(self)
        file_dialog.setFileMode(QFileDialog.ExistingFile)
        file_dialog.setNameFilters([
            "All Model Files (*.gguf *.safetensors *.bin *.pt *.pth)",
            "GGUF Files (*.gguf)",
            "Safetensors Files (*.safetensors)",
            "PyTorch Files (*.bin *.pt *.pth)",
            "All Files (*)"
        ])
        
        if file_dialog.exec():
            selected_files = file_dialog.selectedFiles()
            if selected_files:
                self.path_input.setText(selected_files[0])
    
    def _browse_directory(self):
        """Browse for a model directory."""
        directory = QFileDialog.getExistingDirectory(
            self, "Select Model Directory"
        )
        
        if directory:
            self.path_input.setText(directory)
    
    def _set_directory(self, directory: str):
        """Set the directory path."""
        self.path_input.setText(directory)
    
    def _populate_model_files(self, directory: str):
        """Populate the model files list for a directory."""
        self.model_files_list.clear()
        
        try:
            # Supported model file extensions
            model_extensions = {'.gguf', '.safetensors', '.bin', '.pt', '.pth'}
            
            model_files = []
            for item in os.listdir(directory):
                item_path = os.path.join(directory, item)
                if os.path.isfile(item_path):
                    # Check if it's a model file
                    _, ext = os.path.splitext(item.lower())
                    if ext in model_extensions:
                        # Get file size
                        try:
                            size_bytes = os.path.getsize(item_path)
                            if size_bytes > 1024 * 1024 * 1024:  # > 1GB
                                size_str = f"{size_bytes / (1024**3):.1f} GB"
                            else:
                                size_str = f"{size_bytes / (1024**2):.1f} MB"
                        except:
                            size_str = "Unknown size"
                        
                        model_files.append((item, item_path, size_str, ext))
            
            if model_files:
                # Sort by file size (largest first)
                model_files.sort(key=lambda x: os.path.getsize(x[1]) if os.path.exists(x[1]) else 0, reverse=True)
                
                for filename, filepath, size_str, ext in model_files:
                    item = QListWidgetItem()
                    item.setText(f"{filename}\n{size_str} • {ext.upper()[1:]} format")
                    item.setData(Qt.UserRole, filepath)
                    self.model_files_list.addItem(item)
                
                self.model_files_group.setVisible(True)
                
                # Update the group title with count
                self.model_files_group.setTitle(f"Available Models ({len(model_files)} found)")
            else:
                self.model_files_group.setVisible(False)
                
        except Exception as e:
            self.logger.warning(f"Error populating model files: {e}")
            self.model_files_group.setVisible(False)
    
    def _on_model_file_selected(self, item: QListWidgetItem):
        """Handle model file selection from the list."""
        model_path = item.data(Qt.UserRole)
        if model_path:
            self.selected_model_path = model_path
            self.path_input.setText(model_path)
            # Auto-validate the selected file
            QTimer.singleShot(100, self._auto_validate)
    
    def _on_path_changed(self, path: str):
        """Handle path input changes."""
        self.selected_model_path = path.strip()
        self._update_ui_state()
        
        # Check if it's a directory and populate model files
        if self.selected_model_path and os.path.isdir(self.selected_model_path):
            self._populate_model_files(self.selected_model_path)
        elif self.selected_model_path and os.path.isfile(self.selected_model_path):
            # If it's a file, keep the model files list visible if it was showing the parent directory
            parent_dir = os.path.dirname(self.selected_model_path)
            if self.model_files_group.isVisible():
                # Keep the list visible but don't repopulate to avoid clearing selection
                pass
            else:
                self.model_files_group.setVisible(False)
        else:
            self.model_files_group.setVisible(False)
        
        if self.selected_model_path:
            # Auto-validate after a short delay
            QTimer.singleShot(500, self._auto_validate)
    
    def _on_hf_input_changed(self, model_id: str):
        """Handle HF model ID input changes."""
        self.selected_model_path = model_id.strip()
        self.hf_validate_button.setEnabled(bool(self.selected_model_path))
        self._update_ui_state()
    
    def _on_recent_item_clicked(self, item: QListWidgetItem):
        """Handle recent model item click."""
        model_path = item.data(Qt.UserRole)
        if model_path:
            self.selected_model_path = model_path
            self.path_input.setText(model_path)
            self.tab_widget.setCurrentIndex(0)  # Switch to local files tab
    
    def _auto_validate(self):
        """Auto-validate the current model path."""
        if self.selected_model_path and not self.validation_thread:
            self._validate_current_model()
    
    def _validate_current_model(self):
        """Validate the currently selected model."""
        if not self.selected_model_path:
            return
        
        # Start validation in background thread
        self.validation_thread = ModelValidationThread(
            self.model_loader, self.selected_model_path
        )
        self.validation_thread.validation_completed.connect(self._on_validation_completed)
        self.validation_thread.finished.connect(self._on_validation_finished)
        
        # Update UI
        self.validation_label.setText("Validating model...")
        self.validation_label.setStyleSheet("color: orange;")
        self.progress_bar.setVisible(True)
        self.progress_bar.setRange(0, 0)  # Indeterminate
        self.validate_button.setEnabled(False)
        
        self.validation_thread.start()
    
    def _validate_hf_model(self):
        """Validate Hugging Face model ID."""
        if self.hf_input.text().strip():
            self.selected_model_path = self.hf_input.text().strip()
            self._validate_current_model()
    
    def _on_validation_completed(self, model_path: str, is_valid: bool, message: str):
        """Handle validation completion."""
        if model_path != self.selected_model_path:
            return  # Outdated validation result
        
        if is_valid:
            self.validation_label.setText("✓ Model is valid")
            self.validation_label.setStyleSheet("color: green;")
            self.select_button.setEnabled(True)
            
            # Get format info and update UI
            format_info = self.model_loader.get_format_info(model_path)
            if format_info:
                # Set the detected format so _select_model works
                self.detected_format = format_info.format_type
                self._update_model_info(format_info)
            else:
                # Fallback: try to detect format directly
                try:
                    detection_result = self.model_loader.format_detector.detect_format(model_path)
                    self.detected_format = detection_result.format_type
                except:
                    self.detected_format = ModelFormat.GGUF  # Default fallback
        else:
            self.validation_label.setText(f"✗ {message}")
            self.validation_label.setStyleSheet("color: red;")
            self.select_button.setEnabled(False)
            self.detected_format = ModelFormat.UNKNOWN
            self._clear_model_info()
    
    def _on_validation_finished(self):
        """Handle validation thread completion."""
        self.progress_bar.setVisible(False)
        self.validate_button.setEnabled(True)
        self.validation_thread = None
    
    def _on_format_detected(self, model_path: str, format_type: ModelFormat):
        """Handle format detection signal."""
        if model_path == self.selected_model_path:
            self.detected_format = format_type
    
    def _on_progress_updated(self, progress: UniversalLoadingProgress):
        """Handle progress updates."""
        if self.progress_bar.isVisible():
            if progress.progress >= 0:
                self.progress_bar.setRange(0, 100)
                self.progress_bar.setValue(progress.progress)
            self.validation_label.setText(progress.message)
    
    def _update_model_info(self, format_info: FormatDetectionResult):
        """Update model information display."""
        # Format
        self.format_label.setText(format_info.format_type.value.upper())
        
        # Size
        if format_info.metadata and 'file_size' in format_info.metadata:
            size_bytes = format_info.metadata['file_size']
            size_mb = size_bytes / (1024 * 1024)
            if size_mb > 1024:
                size_str = f"{size_mb / 1024:.1f} GB"
            else:
                size_str = f"{size_mb:.1f} MB"
            self.size_label.setText(size_str)
        
        # Backend recommendation
        try:
            recommendations = self.model_loader.get_backend_recommendations(self.selected_model_path)
            if 'recommended_backend' in recommendations:
                self.backend_label.setText(recommendations['recommended_backend'])
            
            # Memory estimate
            if 'memory_estimate' in recommendations:
                memory_mb = recommendations['memory_estimate'] / (1024 * 1024)
                self.memory_label.setText(f"~{memory_mb:.0f} MB")
        except Exception as e:
            self.logger.warning(f"Could not get backend recommendations: {e}")
        
        # Additional details
        details = []
        if format_info.confidence < 1.0:
            details.append(f"Detection confidence: {format_info.confidence:.1%}")
        
        if format_info.metadata:
            if 'version' in format_info.metadata:
                details.append(f"Version: {format_info.metadata['version']}")
            if 'tensor_count' in format_info.metadata:
                details.append(f"Tensors: {format_info.metadata['tensor_count']}")
        
        self.info_text.setText("\n".join(details))
    
    def _clear_model_info(self):
        """Clear model information display."""
        self.format_label.setText("Not detected")
        self.size_label.setText("Unknown")
        self.backend_label.setText("Not determined")
        self.memory_label.setText("Unknown")
        self.info_text.clear()
    
    def _update_ui_state(self):
        """Update UI state based on current selection."""
        has_selection = bool(self.selected_model_path)
        self.validate_button.setEnabled(has_selection)
        
        if not has_selection:
            self.validation_label.setText("No model selected")
            self.validation_label.setStyleSheet("color: gray;")
            self.select_button.setEnabled(False)
            self._clear_model_info()
    
    def _select_model(self):
        """Select the current model and close dialog."""
        if self.selected_model_path and self.detected_format != ModelFormat.UNKNOWN:
            # Add to recent models
            self._add_to_recent_models(self.selected_model_path, self.detected_format)
            
            # Emit selection signal
            self.model_selected.emit(self.selected_model_path, self.detected_format)
            
            # Save dialog state
            self._save_dialog_state()
            
            self.accept()
    
    def _populate_recent_models(self):
        """Populate the recent models list."""
        self.recent_list.clear()
        
        for model_info in self.recent_models:
            item = QListWidgetItem()
            
            # Format display text
            path = model_info['path']
            format_type = model_info.get('format', 'unknown')
            last_used = model_info.get('last_used', 'unknown')
            
            display_text = f"{Path(path).name}\n{path}\nFormat: {format_type} | Last used: {last_used}"
            
            item.setText(display_text)
            item.setData(Qt.UserRole, path)
            
            self.recent_list.addItem(item)
    
    def _add_to_recent_models(self, model_path: str, format_type: ModelFormat):
        """Add a model to recent models list."""
        # Remove if already exists
        self.recent_models = [m for m in self.recent_models if m['path'] != model_path]
        
        # Add to beginning
        self.recent_models.insert(0, {
            'path': model_path,
            'format': format_type.value,
            'last_used': time.strftime('%Y-%m-%d %H:%M')
        })
        
        # Keep only last 10
        self.recent_models = self.recent_models[:10]
        
        # Save to config
        self._save_recent_models()
    
    def _clear_recent_models(self):
        """Clear recent models list."""
        self.recent_models.clear()
        self.recent_list.clear()
        self._save_recent_models()
    
    def _load_recent_models(self) -> List[Dict[str, Any]]:
        """Load recent models from configuration."""
        try:
            return self.config_manager.get('ui.recent_models', [])
        except Exception as e:
            self.logger.warning(f"Could not load recent models: {e}")
            return []
    
    def _save_recent_models(self):
        """Save recent models to configuration."""
        try:
            self.config_manager.set('ui.recent_models', self.recent_models)
        except Exception as e:
            self.logger.warning(f"Could not save recent models: {e}")
    
    def _load_dialog_state(self):
        """Load dialog state from configuration."""
        try:
            state = self.config_manager.get('ui.model_dialog_state', {})
            
            # Restore tab selection
            if 'current_tab' in state:
                self.tab_widget.setCurrentIndex(state['current_tab'])
            
            # Restore window geometry
            if 'geometry' in state:
                self.restoreGeometry(state['geometry'])
                
        except Exception as e:
            self.logger.warning(f"Could not load dialog state: {e}")
    
    def _save_dialog_state(self):
        """Save dialog state to configuration."""
        try:
            state = {
                'current_tab': self.tab_widget.currentIndex(),
                'geometry': self.saveGeometry()
            }
            self.config_manager.set('ui.model_dialog_state', state)
        except Exception as e:
            self.logger.warning(f"Could not save dialog state: {e}")