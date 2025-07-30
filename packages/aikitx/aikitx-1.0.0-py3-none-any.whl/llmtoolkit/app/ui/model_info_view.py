"""
Model Information View

This module contains the ModelInfoView class, which displays detailed information
about a loaded GGUF model, including metadata, memory usage, and provides a
model switching interface.
"""

import os
import logging
from pathlib import Path
from typing import Dict, List, Optional, Any, Tuple

from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QTabWidget, QScrollArea, QFormLayout, QGroupBox, QComboBox,
    QProgressBar, QSplitter, QTreeWidget, QTreeWidgetItem,
    QTableWidget, QTableWidgetItem, QHeaderView, QSizePolicy,
    QSpacerItem, QFrame
)
from PySide6.QtCore import Qt, Signal, Slot, QSize, QTimer
from PySide6.QtGui import QFont, QIcon, QColor, QPalette

class MemoryUsageWidget(QWidget):
    """Widget for displaying memory usage information."""
    
    def __init__(self, parent=None):
        """Initialize the memory usage widget."""
        super().__init__(parent)
        self.logger = logging.getLogger("gguf_loader.ui.memory_usage")
        
        # Create layout
        layout = QVBoxLayout(self)
        
        # Create memory usage progress bar
        self.memory_label = QLabel("Memory Usage:")
        layout.addWidget(self.memory_label)
        
        self.memory_progress = QProgressBar()
        self.memory_progress.setRange(0, 100)
        self.memory_progress.setValue(0)
        layout.addWidget(self.memory_progress)
        
        # Create detailed memory information
        memory_group = QGroupBox("Memory Details")
        memory_layout = QFormLayout(memory_group)
        
        self.total_memory_label = QLabel("0 MB")
        memory_layout.addRow("Total Memory:", self.total_memory_label)
        
        self.used_memory_label = QLabel("0 MB")
        memory_layout.addRow("Used Memory:", self.used_memory_label)
        
        self.model_memory_label = QLabel("0 MB")
        memory_layout.addRow("Model Size:", self.model_memory_label)
        
        self.available_memory_label = QLabel("0 MB")
        memory_layout.addRow("Available Memory:", self.available_memory_label)
        
        layout.addWidget(memory_group)
        
        # Add spacer
        layout.addStretch()
    
    def update_memory_usage(self, used_mb: float, total_mb: float, model_mb: float):
        """
        Update the memory usage display.
        
        Args:
            used_mb: Used memory in MB
            total_mb: Total memory in MB
            model_mb: Model size in MB
        """
        # Update progress bar
        if total_mb > 0:
            percentage = min(100, int((used_mb / total_mb) * 100))
            self.memory_progress.setValue(percentage)
            
            # Set color based on usage
            if percentage < 60:
                self.memory_progress.setStyleSheet("QProgressBar::chunk { background-color: green; }")
            elif percentage < 80:
                self.memory_progress.setStyleSheet("QProgressBar::chunk { background-color: orange; }")
            else:
                self.memory_progress.setStyleSheet("QProgressBar::chunk { background-color: red; }")
        else:
            self.memory_progress.setValue(0)
        
        # Update labels
        self.total_memory_label.setText(f"{total_mb:.2f} MB")
        self.used_memory_label.setText(f"{used_mb:.2f} MB")
        self.model_memory_label.setText(f"{model_mb:.2f} MB")
        self.available_memory_label.setText(f"{max(0, total_mb - used_mb):.2f} MB")

class ModelSwitcherWidget(QWidget):
    """Widget for switching between loaded models."""
    
    # Signal emitted when a model is selected
    model_selected = Signal(str)  # model_id
    
    def __init__(self, parent=None):
        """Initialize the model switcher widget."""
        super().__init__(parent)
        self.logger = logging.getLogger("gguf_loader.ui.model_switcher")
        
        # Create layout
        layout = QVBoxLayout(self)
        
        # Create model selector
        selector_layout = QHBoxLayout()
        
        selector_layout.addWidget(QLabel("Current Model:"))
        
        self.model_combo = QComboBox()
        self.model_combo.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        self.model_combo.currentIndexChanged.connect(self._on_model_changed)
        selector_layout.addWidget(self.model_combo)
        
        layout.addLayout(selector_layout)
        
        # Create buttons
        button_layout = QHBoxLayout()
        
        self.unload_button = QPushButton("Unload")
        self.unload_button.clicked.connect(self._on_unload)
        button_layout.addWidget(self.unload_button)
        
        self.reload_button = QPushButton("Reload")
        self.reload_button.clicked.connect(self._on_reload)
        button_layout.addWidget(self.reload_button)
        
        layout.addLayout(button_layout)
        
        # Add separator
        separator = QFrame()
        separator.setFrameShape(QFrame.HLine)
        separator.setFrameShadow(QFrame.Sunken)
        layout.addWidget(separator)
        
        # Initialize state
        self.models = {}  # id -> name
        self._update_ui()
    
    def add_model(self, model_id: str, model_name: str):
        """
        Add a model to the switcher.
        
        Args:
            model_id: Unique identifier for the model
            model_name: Display name for the model
        """
        self.models[model_id] = model_name
        self._update_ui()
    
    def remove_model(self, model_id: str):
        """
        Remove a model from the switcher.
        
        Args:
            model_id: Unique identifier for the model
        """
        if model_id in self.models:
            del self.models[model_id]
            self._update_ui()
    
    def set_current_model(self, model_id: str):
        """
        Set the current model.
        
        Args:
            model_id: Unique identifier for the model
        """
        if model_id in self.models:
            index = list(self.models.keys()).index(model_id)
            self.model_combo.setCurrentIndex(index)
    
    def get_current_model(self) -> str:
        """
        Get the current model ID.
        
        Returns:
            Current model ID, or empty string if no model is selected
        """
        index = self.model_combo.currentIndex()
        if index >= 0 and index < len(self.models):
            return list(self.models.keys())[index]
        return ""
    
    def _update_ui(self):
        """Update the UI based on the current state."""
        # Save current selection
        current_id = self.get_current_model()
        
        # Clear and repopulate combo box
        self.model_combo.clear()
        
        for model_id, model_name in self.models.items():
            self.model_combo.addItem(model_name, model_id)
        
        # Restore selection if possible
        if current_id and current_id in self.models:
            self.set_current_model(current_id)
        
        # Update button states
        has_models = len(self.models) > 0
        self.unload_button.setEnabled(has_models)
        self.reload_button.setEnabled(has_models)
    
    def _on_model_changed(self, index: int):
        """
        Handle model selection change.
        
        Args:
            index: New selection index
        """
        if index >= 0 and index < len(self.models):
            model_id = list(self.models.keys())[index]
            self.model_selected.emit(model_id)
    
    def _on_unload(self):
        """Handle unload button click."""
        model_id = self.get_current_model()
        if model_id:
            # Emit signal with empty string to indicate unload
            self.model_selected.emit("")
    
    def _on_reload(self):
        """Handle reload button click."""
        model_id = self.get_current_model()
        if model_id:
            # Re-emit the same model ID to trigger a reload
            self.model_selected.emit(model_id)

class ModelMetadataWidget(QWidget):
    """Widget for displaying model metadata."""
    
    def __init__(self, parent=None):
        """Initialize the model metadata widget."""
        super().__init__(parent)
        self.logger = logging.getLogger("gguf_loader.ui.model_metadata")
        
        # Create layout
        layout = QVBoxLayout(self)
        
        # Create scroll area for metadata
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setFrameShape(QFrame.NoFrame)
        
        # Create content widget
        self.content_widget = QWidget()
        self.content_layout = QVBoxLayout(self.content_widget)
        
        # Add basic info group
        self.basic_group = QGroupBox("Basic Information")
        basic_layout = QFormLayout(self.basic_group)
        
        self.name_label = QLabel("-")
        basic_layout.addRow("Name:", self.name_label)
        
        self.size_label = QLabel("-")
        basic_layout.addRow("Size:", self.size_label)
        
        self.path_label = QLabel("-")
        basic_layout.addRow("Path:", self.path_label)
        
        self.format_label = QLabel("-")
        basic_layout.addRow("Format:", self.format_label)
        
        self.content_layout.addWidget(self.basic_group)
        
        # Add model parameters group
        self.params_group = QGroupBox("Model Parameters")
        self.params_layout = QFormLayout(self.params_group)
        self.content_layout.addWidget(self.params_group)
        
        # Add metadata group
        self.metadata_group = QGroupBox("Additional Metadata")
        self.metadata_layout = QVBoxLayout(self.metadata_group)
        
        self.metadata_table = QTableWidget(0, 2)
        self.metadata_table.setHorizontalHeaderLabels(["Key", "Value"])
        self.metadata_table.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeToContents)
        self.metadata_table.horizontalHeader().setSectionResizeMode(1, QHeaderView.Stretch)
        self.metadata_table.verticalHeader().setVisible(False)
        self.metadata_layout.addWidget(self.metadata_table)
        
        self.content_layout.addWidget(self.metadata_group)
        
        # Add content widget to scroll area
        scroll_area.setWidget(self.content_widget)
        layout.addWidget(scroll_area)
    
    def update_metadata(self, metadata: Dict[str, Any]):
        """
        Update the metadata display.
        
        Args:
            metadata: Dictionary of model metadata
        """
        # Update basic info
        self.name_label.setText(metadata.get("name", "-"))
        self.size_label.setText(metadata.get("size_str", "-"))
        self.path_label.setText(metadata.get("path", "-"))
        self.format_label.setText(metadata.get("format", "GGUF"))
        
        # Update parameters
        # Clear existing parameters
        while self.params_layout.rowCount() > 0:
            self.params_layout.removeRow(0)
        
        # Add parameters
        params = metadata.get("parameters", {})
        for key, value in params.items():
            self.params_layout.addRow(f"{key}:", QLabel(str(value)))
        
        # Update metadata table
        self.metadata_table.setRowCount(0)
        
        # Add metadata
        other_metadata = metadata.get("metadata", {})
        self.metadata_table.setRowCount(len(other_metadata))
        
        for i, (key, value) in enumerate(other_metadata.items()):
            key_item = QTableWidgetItem(key)
            key_item.setFlags(key_item.flags() & ~Qt.ItemIsEditable)
            
            value_item = QTableWidgetItem(str(value))
            value_item.setFlags(value_item.flags() & ~Qt.ItemIsEditable)
            
            self.metadata_table.setItem(i, 0, key_item)
            self.metadata_table.setItem(i, 1, value_item)

class ModelInfoView(QWidget):
    """
    Widget for displaying model information.
    
    This widget shows detailed information about a loaded GGUF model,
    including metadata, memory usage, and provides a model switching interface.
    """
    
    # Signal emitted when a model is selected
    model_selected = Signal(str)  # model_id
    
    def __init__(self, event_bus=None, parent=None):
        """Initialize the model information view."""
        super().__init__(parent)
        self.logger = logging.getLogger("gguf_loader.ui.model_info_view")
        self.event_bus = event_bus
        
        # Create layout
        layout = QVBoxLayout(self)
        
        # Create model switcher
        self.model_switcher = ModelSwitcherWidget()
        self.model_switcher.model_selected.connect(self._on_model_selected)
        layout.addWidget(self.model_switcher)
        
        # Create tab widget
        self.tab_widget = QTabWidget()
        
        # Create metadata tab
        self.metadata_widget = ModelMetadataWidget()
        self.tab_widget.addTab(self.metadata_widget, "Metadata")
        
        # Create memory usage tab
        self.memory_widget = MemoryUsageWidget()
        self.tab_widget.addTab(self.memory_widget, "Memory")
        
        layout.addWidget(self.tab_widget)
        
        # Set up timer for memory updates
        self.memory_timer = QTimer(self)
        self.memory_timer.timeout.connect(self._update_memory)
        self.memory_timer.start(5000)  # Update every 5 seconds
        
        # Initialize state
        self.current_model_id = ""
        self.models = {}  # id -> metadata
    
    def add_model(self, model_id: str, model_name: str, metadata: Dict[str, Any]):
        """
        Add a model to the view.
        
        Args:
            model_id: Unique identifier for the model
            model_name: Display name for the model
            metadata: Dictionary of model metadata
        """
        self.models[model_id] = metadata
        self.model_switcher.add_model(model_id, model_name)
        
        # If this is the first model, select it
        if len(self.models) == 1:
            self.set_current_model(model_id)
    
    def remove_model(self, model_id: str):
        """
        Remove a model from the view.
        
        Args:
            model_id: Unique identifier for the model
        """
        if model_id in self.models:
            del self.models[model_id]
            self.model_switcher.remove_model(model_id)
            
            # If this was the current model, clear the view
            if model_id == self.current_model_id:
                self.current_model_id = ""
                self._update_view()
    
    def set_current_model(self, model_id: str):
        """
        Set the current model.
        
        Args:
            model_id: Unique identifier for the model
        """
        if model_id in self.models or not model_id:
            self.current_model_id = model_id
            self.model_switcher.set_current_model(model_id)
            self._update_view()
    
    def get_current_model(self) -> str:
        """
        Get the current model ID.
        
        Returns:
            Current model ID, or empty string if no model is selected
        """
        return self.current_model_id
    
    def _update_view(self):
        """Update the view based on the current model."""
        if self.current_model_id and self.current_model_id in self.models:
            # Update metadata
            self.metadata_widget.update_metadata(self.models[self.current_model_id])
            
            # Update memory usage
            self._update_memory()
        else:
            # Clear view
            self.metadata_widget.update_metadata({})
            self.memory_widget.update_memory_usage(0, 0, 0)
    
    def _update_memory(self):
        """Update memory usage information."""
        if self.current_model_id and self.current_model_id in self.models:
            # In a real implementation, we would get actual memory usage
            # For now, just use placeholder values based on model size
            metadata = self.models[self.current_model_id]
            model_size_mb = metadata.get("size", 0) / (1024 * 1024)
            
            # Simulate memory usage
            total_memory_mb = 16 * 1024  # 16 GB
            used_memory_mb = model_size_mb + 1024  # Model size + 1 GB for application
            
            self.memory_widget.update_memory_usage(used_memory_mb, total_memory_mb, model_size_mb)
    
    def _on_model_selected(self, model_id: str):
        """
        Handle model selection change.
        
        Args:
            model_id: Selected model ID
        """
        self.current_model_id = model_id
        self._update_view()
        self.model_selected.emit(model_id)
    
    def update_model_info(self, model_info: Dict[str, Any]):
        """
        Update the model information display.
        
        Args:
            model_info: Dictionary containing model information
        """
        model_id = model_info.get("id", "unknown")
        model_name = model_info.get("name", "Unknown Model")
        
        # Add or update the model
        self.add_model(model_id, model_name, model_info)
    
    def clear(self):
        """Clear all model information."""
        self.models.clear()
        self.current_model_id = ""
        self.model_switcher = ModelSwitcherWidget()
        self.metadata_widget.update_metadata({})
        self.memory_widget.update_memory_usage(0, 0, 0)