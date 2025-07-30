"""
Enhanced Summarization Tab with Universal Model Loading Integration

This module contains the EnhancedSummarizationTab class, which provides a clean interface
for document processing with summarization controls and output display, integrated with
the universal model loading system for enhanced capabilities.
"""

import logging
import os
import time
from typing import Optional, Dict, Any, List
from dataclasses import dataclass
from pathlib import Path

from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QTextEdit, QPushButton, 
    QLabel, QComboBox, QProgressBar, QFileDialog, QMessageBox,
    QSplitter, QFrame, QGroupBox, QCheckBox, QSpinBox, QScrollArea
)
from PySide6.QtCore import Qt, QTimer, Signal, Slot
from PySide6.QtGui import QFont, QTextCursor

from llmtoolkit.app.core.event_bus import EventBus
from llmtoolkit.app.ui.theme_manager import ThemeManager
from llmtoolkit.app.core.universal_format_detector import ModelFormat
from llmtoolkit.app.core.enhanced_backend_manager import EnhancedLoadingResult


@dataclass
class UniversalModelInfo:
    """Enhanced model information from universal loading system."""
    model_path: str
    format_type: ModelFormat
    backend_used: str
    hardware_used: str
    metadata: Dict[str, Any]
    capabilities: List[str]
    performance_metrics: Dict[str, Any]
    memory_usage: int
    optimization_applied: List[str]
    load_time: float
    
    def get_display_name(self) -> str:
        """Get user-friendly model name."""
        if self.metadata and 'model_name' in self.metadata:
            return self.metadata['model_name']
        return Path(self.model_path).stem
        
    def get_capability_description(self) -> str:
        """Get human-readable capability description."""
        return ", ".join(self.capabilities) if self.capabilities else "General text processing"
        
    def get_performance_summary(self) -> str:
        """Get performance summary for display."""
        return f"Load time: {self.load_time:.1f}s, Memory: {self.memory_usage}MB"

@dataclass
class UniversalLoadingProgress:
    """Universal loading progress information."""
    stage: str
    progress: int  # 0-100
    message: str
    details: Optional[str]
    elapsed_time: float
    estimated_remaining: Optional[float]
    backend_info: Optional[str]
    memory_usage: Optional[int]

class EnhancedSummarizationTab(QWidget):
    """
    Enhanced interface for document processing and summarization with universal model loading integration.
    
    Features:
    - Document input area (text or file)
    - Summarization controls and style options with format-specific adaptations
    - Summary output display with copy/save functionality
    - Integration with universal model loading system
    - Model-specific interface adaptation based on capabilities
    - Format-specific summarization options display
    - Performance expectations and memory-aware processing
    - Model metadata display relevant to summarization tasks
    """
    
    # Signals
    summarization_requested = Signal(str, dict)  # text, options
    
    def __init__(self, event_bus: EventBus, parent=None):
        """
        Initialize the enhanced summarization tab.
        
        Args:
            event_bus: Application event bus
            parent: Parent widget
        """
        super().__init__(parent)
        
        self.logger = logging.getLogger("gguf_loader.ui.enhanced_summarization_tab")
        self.event_bus = event_bus
        self.is_processing = False
        self.current_document_path = None
        
        # Universal model loading integration
        self.current_model_info: Optional[UniversalModelInfo] = None
        self.loading_progress_widget = None
        self.model_info_widget = None
        self.format_specific_options = None
        self.performance_indicator = None
        
        # Theme manager
        self.theme_manager = ThemeManager()
        
        # Initialize UI
        self._init_ui()
        
        # Apply theme
        self._apply_theme()
        
        # Connect events (including universal events)
        self._connect_events()
        self._connect_universal_events()
    
    def _apply_theme(self):
        """Apply global theme to summarization tab using ThemeManager."""
        try:
            # Use the global theme manager to apply consistent theming
            self.theme_manager.apply_theme_to_widget(self)
            
        except Exception as e:
            self.logger.error(f"Failed to apply theme to summarization tab: {e}")
    
    def _init_ui(self):
        """Initialize the enhanced summarization interface."""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(15, 15, 15, 15)
        layout.setSpacing(15)
        
        # Model information section (initially hidden)
        self.model_info_widget = self._create_model_info_section()
        self.model_info_widget.hide()
        layout.addWidget(self.model_info_widget)
        
        # Loading progress section (initially hidden)
        self.loading_progress_widget = self._create_loading_progress_section()
        self.loading_progress_widget.hide()
        layout.addWidget(self.loading_progress_widget)
        
        # Create splitter for input and output
        splitter = QSplitter(Qt.Vertical)
        layout.addWidget(splitter)
        
        # Document input section
        input_section = self._create_input_section()
        splitter.addWidget(input_section)
        
        # Controls section with format-specific options
        controls_section = self._create_enhanced_controls_section()
        layout.addWidget(controls_section)
        
        # Progress section (initially hidden)
        self.progress_section = self._create_progress_section()
        self.progress_section.hide()
        layout.addWidget(self.progress_section)
        
        # Summary output section
        output_section = self._create_output_section()
        splitter.addWidget(output_section)
        
        # Set splitter proportions
        splitter.setSizes([300, 300])
    
    def _create_input_section(self):
        """Create the document input section."""
        input_group = QGroupBox("Document Input")
        
        layout = QVBoxLayout(input_group)
        layout.setSpacing(10)
        
        # File loading section
        file_layout = QHBoxLayout()
        
        load_file_button = QPushButton("Load Document File...")
        load_file_button.setProperty("buttonType", "info")
        load_file_button.clicked.connect(self._load_document_file)
        file_layout.addWidget(load_file_button)
        
        self.file_label = QLabel("No file loaded")
        file_layout.addWidget(self.file_label)
        
        file_layout.addStretch()
        layout.addLayout(file_layout)
        
        # Document text input
        input_label = QLabel("Document Text:")
        layout.addWidget(input_label)
        
        self.document_input = QTextEdit()
        self.document_input.setPlaceholderText("Paste your document text here or load from file...")
        self.document_input.setMinimumHeight(200)
        layout.addWidget(self.document_input)
        
        return input_group
    

    
    def _create_output_section(self):
        """Create the summary output section."""
        output_group = QGroupBox("Summary Output")
        output_group.setStyleSheet("""
            QGroupBox {
                font-weight: bold;
                border: 2px solid #dee2e6;
                border-radius: 8px;
                margin-top: 10px;
                padding-top: 10px;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 5px 0 5px;
                color: #495057;
            }
        """)
        
        layout = QVBoxLayout(output_group)
        layout.setSpacing(10)
        
        # Output controls
        output_controls = QHBoxLayout()
        
        copy_button = QPushButton("Copy Summary")
        copy_button.setStyleSheet("""
            QPushButton {
                background-color: #6c757d;
                color: white;
                border: none;
                border-radius: 6px;
                padding: 8px 16px;
                font-weight: bold;
                font-size: 14px;
            }
            QPushButton:hover {
                background-color: #5a6268;
            }
            QPushButton:pressed {
                background-color: #545b62;
            }
        """)
        copy_button.clicked.connect(self._copy_summary)
        output_controls.addWidget(copy_button)
        
        save_button = QPushButton("Save Summary...")
        save_button.setStyleSheet("""
            QPushButton {
                background-color: #0078d4;
                color: white;
                border: none;
                border-radius: 6px;
                padding: 8px 16px;
                font-weight: bold;
                font-size: 14px;
            }
            QPushButton:hover {
                background-color: #106ebe;
            }
            QPushButton:pressed {
                background-color: #005a9e;
            }
        """)
        save_button.clicked.connect(self._save_summary)
        output_controls.addWidget(save_button)
        
        output_controls.addStretch()
        
        # Word count label
        self.word_count_label = QLabel("0 words")
        self.word_count_label.setStyleSheet("color: #6c757d; font-size: 12px;")
        output_controls.addWidget(self.word_count_label)
        
        layout.addLayout(output_controls)
        
        # Summary output display
        self.summary_output = QTextEdit()
        self.summary_output.setReadOnly(True)
        self.summary_output.setPlaceholderText("Summary will appear here...")
        # Remove hardcoded styling - will use global theme
        self.summary_output.textChanged.connect(self._update_word_count)
        layout.addWidget(self.summary_output)
        
        return output_group
    
    def _create_model_info_section(self):
        """Create the model information display section."""
        info_group = QGroupBox("Model Information")
        layout = QVBoxLayout(info_group)
        layout.setSpacing(8)
        
        # Model name and format
        self.model_name_label = QLabel("No model loaded")
        self.model_name_label.setStyleSheet("font-weight: bold; font-size: 14px; color: #2c3e50;")
        layout.addWidget(self.model_name_label)
        
        # Model capabilities
        self.model_capabilities_label = QLabel("")
        self.model_capabilities_label.setStyleSheet("color: #7f8c8d; font-size: 12px;")
        layout.addWidget(self.model_capabilities_label)
        
        # Performance metrics
        self.performance_metrics_label = QLabel("")
        self.performance_metrics_label.setStyleSheet("color: #27ae60; font-size: 11px;")
        layout.addWidget(self.performance_metrics_label)
        
        return info_group
    
    def _create_loading_progress_section(self):
        """Create the loading progress display section."""
        progress_group = QGroupBox("Model Loading Progress")
        layout = QVBoxLayout(progress_group)
        layout.setSpacing(8)
        
        # Progress message
        self.loading_message_label = QLabel("Preparing to load model...")
        layout.addWidget(self.loading_message_label)
        
        # Progress bar
        self.loading_progress_bar = QProgressBar()
        self.loading_progress_bar.setRange(0, 100)
        layout.addWidget(self.loading_progress_bar)
        
        # Stage information
        self.loading_stage_label = QLabel("")
        self.loading_stage_label.setStyleSheet("color: #7f8c8d; font-size: 11px;")
        layout.addWidget(self.loading_stage_label)
        
        return progress_group
    
    def _create_enhanced_controls_section(self):
        """Create the enhanced summarization controls section with format-specific options."""
        controls_group = QGroupBox("Summarization Options")
        
        layout = QVBoxLayout(controls_group)
        layout.setSpacing(15)
        
        # Basic controls row
        basic_controls = QHBoxLayout()
        basic_controls.setSpacing(15)
        
        # Summary style selection
        style_label = QLabel("Style:")
        style_label.setStyleSheet("font-weight: bold; color: #495057;")
        basic_controls.addWidget(style_label)
        
        self.style_combo = QComboBox()
        self.style_combo.addItems([
            "Concise",
            "Detailed", 
            "Bullet Points",
            "Executive Summary",
            "Key Insights"
        ])
        basic_controls.addWidget(self.style_combo)
        
        # Summary length
        length_label = QLabel("Max Length:")
        length_label.setStyleSheet("font-weight: bold; color: #495057;")
        basic_controls.addWidget(length_label)
        
        self.length_spinbox = QSpinBox()
        self.length_spinbox.setRange(50, 1000)
        self.length_spinbox.setValue(200)
        self.length_spinbox.setSuffix(" words")
        basic_controls.addWidget(self.length_spinbox)
        
        basic_controls.addStretch()
        layout.addLayout(basic_controls)
        
        # Format-specific options (initially hidden)
        self.format_specific_options = self._create_format_specific_options()
        self.format_specific_options.hide()
        layout.addWidget(self.format_specific_options)
        
        # Performance indicator (initially hidden)
        self.performance_indicator = self._create_performance_indicator()
        self.performance_indicator.hide()
        layout.addWidget(self.performance_indicator)
        
        # Action buttons
        button_layout = QHBoxLayout()
        
        self.summarize_button = QPushButton("Summarize Document")
        self.summarize_button.setStyleSheet("""
            QPushButton {
                background-color: #28a745;
                color: white;
                border: none;
                border-radius: 6px;
                padding: 12px 24px;
                font-weight: bold;
                font-size: 14px;
            }
            QPushButton:hover {
                background-color: #218838;
            }
            QPushButton:pressed {
                background-color: #1e7e34;
            }
            QPushButton:disabled {
                background-color: #6c757d;
                cursor: not-allowed;
            }
        """)
        self.summarize_button.clicked.connect(self._summarize_document)
        button_layout.addWidget(self.summarize_button)
        
        # Cancel button (initially hidden)
        self.cancel_button = QPushButton("Cancel")
        self.cancel_button.setStyleSheet("""
            QPushButton {
                background-color: #dc3545;
                color: white;
                border: none;
                border-radius: 6px;
                padding: 12px 24px;
                font-weight: bold;
                font-size: 14px;
            }
            QPushButton:hover {
                background-color: #c82333;
            }
            QPushButton:pressed {
                background-color: #bd2130;
            }
        """)
        self.cancel_button.clicked.connect(self._cancel_summarization)
        self.cancel_button.hide()
        button_layout.addWidget(self.cancel_button)
        
        layout.addLayout(button_layout)
        
        return controls_group
    
    def _create_format_specific_options(self):
        """Create format-specific summarization options."""
        options_group = QGroupBox("Format-Specific Options")
        layout = QVBoxLayout(options_group)
        layout.setSpacing(8)
        
        # Memory-aware processing option
        self.memory_aware_checkbox = QCheckBox("Enable memory-aware processing")
        self.memory_aware_checkbox.setToolTip("Adjust processing approach based on available memory")
        layout.addWidget(self.memory_aware_checkbox)
        
        # Optimization options
        self.optimization_label = QLabel("Optimizations: None applied")
        self.optimization_label.setStyleSheet("color: #7f8c8d; font-size: 11px;")
        layout.addWidget(self.optimization_label)
        
        return options_group
    
    def _create_performance_indicator(self):
        """Create performance expectations indicator."""
        perf_group = QGroupBox("Performance Expectations")
        layout = QVBoxLayout(perf_group)
        layout.setSpacing(8)
        
        # Backend information
        self.backend_info_label = QLabel("Backend: Not loaded")
        layout.addWidget(self.backend_info_label)
        
        # Memory usage warning
        self.memory_warning_label = QLabel("")
        self.memory_warning_label.setStyleSheet("color: #e74c3c; font-size: 11px;")
        layout.addWidget(self.memory_warning_label)
        
        # Performance expectations
        self.performance_expectation_label = QLabel("")
        self.performance_expectation_label.setStyleSheet("color: #3498db; font-size: 11px;")
        layout.addWidget(self.performance_expectation_label)
        
        return perf_group
    
    def _create_progress_section(self):
        """Create the progress display section."""
        progress_group = QGroupBox("Processing Progress")
        layout = QVBoxLayout(progress_group)
        layout.setSpacing(8)
        
        # Overall progress bar
        self.progress_bar = QProgressBar()
        self.progress_bar.setRange(0, 100)
        self.progress_bar.setValue(0)
        layout.addWidget(self.progress_bar)
        
        # Progress message
        self.progress_message_label = QLabel("Initializing...")
        self.progress_message_label.setStyleSheet("color: #2c3e50; font-weight: bold;")
        layout.addWidget(self.progress_message_label)
        
        # Detailed progress information
        self.progress_details_label = QLabel("")
        self.progress_details_label.setStyleSheet("color: #7f8c8d; font-size: 11px;")
        self.progress_details_label.setWordWrap(True)
        layout.addWidget(self.progress_details_label)
        
        # Processing statistics
        self.processing_stats_label = QLabel("")
        self.processing_stats_label.setStyleSheet("color: #27ae60; font-size: 10px;")
        layout.addWidget(self.processing_stats_label)
        
        return progress_group
    
    def _connect_events(self):
        """Connect event handlers."""
        self.event_bus.subscribe("summarization.completed", self._on_summarization_complete)
        self.event_bus.subscribe("summarization.generating", self._on_summarization_generating)
        self.event_bus.subscribe("summarization.error", self._on_summarization_error)
        self.event_bus.subscribe("summarization.progress", self._on_summarization_progress)
        self.event_bus.subscribe("summarization.partial", self._on_summarization_partial)
        self.event_bus.subscribe("summarization.cancelled", self._on_summarization_cancelled)
        self.event_bus.subscribe("model.loaded", self._on_model_loaded)
        self.event_bus.subscribe("model.unloaded", self._on_model_unloaded)
        
        # Enhanced progress events for chunked processing
        self.event_bus.subscribe("summarization.chunk_progress", self._on_chunk_progress)
        self.event_bus.subscribe("summarization.chunk_completed", self._on_chunk_completed)
    
    def _connect_universal_events(self):
        """Connect to universal loading system events."""
        self.event_bus.subscribe("universal.model.loading_started", self._on_universal_loading_started)
        self.event_bus.subscribe("universal.model.progress_updated", self._on_universal_progress_updated)
        self.event_bus.subscribe("universal.model.format_detected", self._on_universal_format_detected)
        self.event_bus.subscribe("universal.model.backend_selected", self._on_universal_backend_selected)
        self.event_bus.subscribe("universal.model.loaded", self._on_universal_model_loaded)
        self.event_bus.subscribe("universal.model.loading_failed", self._on_universal_loading_failed)
        self.event_bus.subscribe("universal.model.unloaded", self._on_universal_model_unloaded)
        self.event_bus.subscribe("performance.metrics_updated", self._on_performance_metrics_updated)
        self.event_bus.subscribe("performance.warning", self._on_performance_warning)
    
    def _load_document_file(self):
        """Load document from file."""
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            "Load Document",
            "",
            "Text Files (*.txt);;Markdown Files (*.md);;PDF Files (*.pdf);;All Files (*)"
        )
        
        if file_path:
            try:
                # Use the event bus to request file loading from the summarization service
                self.event_bus.publish("summarization.load_file", {
                    "file_path": file_path,
                    "encoding": "utf-8"
                })
                
                # For now, we'll handle the file loading directly here
                # This will be improved when we integrate with the service properly
                from pathlib import Path
                file_ext = Path(file_path).suffix.lower()
                
                if file_ext == '.pdf':
                    # For PDF files, we'll show a message that they need to be processed
                    self.document_input.setText(f"PDF file loaded: {os.path.basename(file_path)}\n\nClick 'Summarize Document' to process this PDF file.")
                    content = ""  # We'll let the service handle PDF extraction during summarization
                else:
                    # Handle regular text files
                    with open(file_path, 'r', encoding='utf-8') as f:
                        content = f.read()
                    self.document_input.setText(content)
                
                self.current_document_path = file_path
                self.file_label.setText(f"Loaded: {os.path.basename(file_path)}")
                self.file_label.setStyleSheet("color: #28a745; font-style: normal;")
                
                self.logger.info(f"Loaded document: {file_path}")
                
            except Exception as e:
                QMessageBox.critical(
                    self,
                    "Error Loading Document",
                    f"Failed to load document:\n{str(e)}"
                )
                self.logger.error(f"Failed to load document {file_path}: {e}")
    
    def _summarize_document(self):
        """Summarize the document text with enhanced error handling and timeout protection."""
        text = self.document_input.toPlainText().strip()
        
        # Check if we have a PDF file loaded
        if self.current_document_path and self.current_document_path.lower().endswith('.pdf'):
            # For PDF files, use file-based summarization
            if not self.current_document_path:
                QMessageBox.warning(
                    self,
                    "No PDF File",
                    "Please load a PDF file to summarize."
                )
                return
            
            # Validate PDF file exists
            if not os.path.exists(self.current_document_path):
                QMessageBox.critical(
                    self,
                    "File Not Found",
                    f"PDF file not found: {os.path.basename(self.current_document_path)}"
                )
                return
            
            self.logger.info(f"Starting PDF summarization for: {self.current_document_path}")
            
            # Get summarization options
            options = {
                "style": self.style_combo.currentText().lower().replace(" ", "_"),
                "max_length": self.length_spinbox.value()
            }
            
            # Set processing state
            self._set_processing_state(True)
            
            # Set up timeout protection (5 minutes for PDF processing)
            self._setup_summarization_timeout(300)  # 5 minutes
            
            # Publish async file summarization event
            self.event_bus.publish("summarization.file_async_request", {
                "file_path": self.current_document_path,
                "style": options["style"],
                "encoding": "utf-8"
            })
            
            self.logger.info(f"Requested async PDF summarization for: {self.current_document_path}")
            
        else:
            # Handle regular text summarization
            if not text:
                QMessageBox.warning(
                    self,
                    "No Document Text",
                    "Please enter some document text or load a file to summarize."
                )
                return
            
            self.logger.info(f"Starting text summarization for {len(text)} characters")
            
            # Get summarization options
            options = {
                "style": self.style_combo.currentText().lower().replace(" ", "_"),
                "max_length": self.length_spinbox.value()
            }
            
            # Set processing state
            self._set_processing_state(True)
            
            # Set up timeout protection (2 minutes for text processing)
            self._setup_summarization_timeout(120)  # 2 minutes
            
            # Emit signal and publish async text summarization event
            self.summarization_requested.emit(text, options)
            self.event_bus.publish("summarization.text_async_request", {
                "text": text,
                "style": options["style"]
            })
            
            self.logger.info(f"Requested async text summarization with style: {options['style']}, max_length: {options['max_length']}")
    
    def _setup_summarization_timeout(self, timeout_seconds: int):
        """Set up timeout protection for summarization."""
        if hasattr(self, '_timeout_timer'):
            self._timeout_timer.stop()
        
        self._timeout_timer = QTimer()
        self._timeout_timer.setSingleShot(True)
        self._timeout_timer.timeout.connect(self._on_summarization_timeout)
        self._timeout_timer.start(timeout_seconds * 1000)  # Convert to milliseconds
        
        self.logger.info(f"Summarization timeout set to {timeout_seconds} seconds")
    
    def _on_summarization_timeout(self):
        """Handle summarization timeout."""
        self.logger.error("Summarization timed out - forcing cancellation")
        
        # Force reset processing state
        self._set_processing_state(False)
        
        # Show timeout error
        self.summary_output.setText("Summarization timed out. This may be due to:\n\n"
                                   "• Very large document size\n"
                                   "• Model processing issues\n"
                                   "• System resource constraints\n\n"
                                   "Try with a smaller document or restart the application.")
        
        # Publish cancellation event
        self.event_bus.publish("summarization.cancel", True)
        
        # Show error dialog
        QMessageBox.warning(
            self,
            "Summarization Timeout",
            "The summarization process timed out. Please try with a smaller document or restart the application."
        )
    
    def _clear_timeout(self):
        """Clear the summarization timeout."""
        if hasattr(self, '_timeout_timer'):
            self._timeout_timer.stop()
    
    def _cancel_summarization(self):
        """Cancel the current summarization process."""
        self.logger.info("User requested summarization cancellation")
        
        # Publish cancellation event
        self.event_bus.publish("summarization.cancel", True)
        
        # Update UI immediately
        self.summary_output.setText("Cancelling summarization...\n\nStopping background processes...")
        
        if hasattr(self, 'progress_message_label'):
            self.progress_message_label.setText("Cancelling...")
        
        if hasattr(self, 'progress_details_label'):
            self.progress_details_label.setText("Stopping all processing threads...")
    
    def _set_processing_state(self, processing: bool):
        """Set the processing state and update UI accordingly."""
        self.is_processing = processing
        
        # Update button states
        self.summarize_button.setEnabled(not processing)
        
        if processing:
            self.summarize_button.setText("Processing...")
            self.cancel_button.show()
            
            # Show and initialize progress section
            if hasattr(self, 'progress_section'):
                self.progress_section.show()
                self.progress_bar.setRange(0, 100)
                self.progress_bar.setValue(0)
                self.progress_message_label.setText("Initializing...")
                self.progress_details_label.setText("")
                self.processing_stats_label.setText("")
            
            self.summary_output.setText("Starting summarization process...\n\n" +
                                      "📄 Large documents will be processed in intelligent chunks\n" +
                                      "[PERF] Progress will be shown in real-time\n" +
                                      "🔄 You can cancel at any time\n\n" +
                                      "Please wait while we process your document...")
        else:
            self.summarize_button.setText("Summarize Document")
            self.cancel_button.hide()
            
            # Hide progress section
            if hasattr(self, 'progress_section'):
                self.progress_section.hide()
            
            self._clear_timeout()
    
    def _copy_summary(self):
        """Copy summary to clipboard."""
        summary = self.summary_output.toPlainText()
        if summary:
            clipboard = self.summary_output.clipboard()
            clipboard.setText(summary)
            
            # Show temporary status message
            original_text = self.word_count_label.text()
            self.word_count_label.setText("Copied to clipboard!")
            self.word_count_label.setStyleSheet("color: #28a745; font-size: 12px;")
            
            # Reset after 2 seconds
            QTimer.singleShot(2000, lambda: (
                self.word_count_label.setText(original_text),
                self.word_count_label.setStyleSheet("color: #6c757d; font-size: 12px;")
            ))
        else:
            QMessageBox.information(self, "No Summary", "No summary to copy.")
    
    def _save_summary(self):
        """Save summary to file."""
        summary = self.summary_output.toPlainText()
        if not summary:
            QMessageBox.information(self, "No Summary", "No summary to save.")
            return
        
        # Suggest filename based on original document
        suggested_name = "summary.txt"
        if self.current_document_path:
            base_name = os.path.splitext(os.path.basename(self.current_document_path))[0]
            suggested_name = f"{base_name}_summary.txt"
        
        file_path, _ = QFileDialog.getSaveFileName(
            self,
            "Save Summary",
            suggested_name,
            "Text Files (*.txt);;Markdown Files (*.md);;All Files (*)"
        )
        
        if file_path:
            try:
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write(summary)
                
                QMessageBox.information(
                    self,
                    "Summary Saved",
                    f"Summary saved to:\n{file_path}"
                )
                self.logger.info(f"Saved summary to: {file_path}")
                
            except Exception as e:
                QMessageBox.critical(
                    self,
                    "Error Saving Summary",
                    f"Failed to save summary:\n{str(e)}"
                )
                self.logger.error(f"Failed to save summary to {file_path}: {e}")
    
    def _update_word_count(self):
        """Update the word count label."""
        text = self.summary_output.toPlainText()
        word_count = len(text.split()) if text.strip() else 0
        self.word_count_label.setText(f"{word_count} words")
    
    # Event handlers
    @Slot(str)
    def _on_summarization_complete(self, summary: str):
        """Handle summarization completion."""
        self.logger.info(f"Received summary: {len(summary)} characters")
        
        # Clear timeout
        self._clear_timeout()
        
        # Display summary
        self.summary_output.setText(summary)
        
        # Reset processing state
        self._set_processing_state(False)
    
    @Slot(str)
    def _on_summarization_error(self, error_message: str):
        """Handle summarization error."""
        self.logger.error(f"Summarization error: {error_message}")
        
        # Clear timeout
        self._clear_timeout()
        
        # Show error in output
        self.summary_output.setText(f"Error: {error_message}")
        
        # Reset processing state
        self._set_processing_state(False)
        
        # Show error dialog
        QMessageBox.critical(
            self,
            "Summarization Error",
            f"Failed to generate summary:\n\n{error_message}"
        )
    
    @Slot()
    def _on_summarization_generating(self):
        """Handle summarization generation start."""
        self.logger.info("Summarization generation started")
        
        # Set processing state if not already set
        if not self.is_processing:
            self._set_processing_state(True)
    
    @Slot(str)
    def _on_summarization_progress(self, progress_message: str):
        """Handle summarization progress update."""
        if hasattr(self, 'progress_message_label'):
            self.progress_message_label.setText(progress_message)
        
        # Also update the summary output for backward compatibility
        current_text = self.summary_output.toPlainText()
        if not current_text or "Starting summarization" in current_text:
            self.summary_output.setText(f"Processing: {progress_message}")
        
        # Show progress section if not visible
        if hasattr(self, 'progress_section') and not self.progress_section.isVisible():
            self.progress_section.show()
    
    @Slot(str)
    def _on_summarization_partial(self, partial_summary: str):
        """Handle partial summary update for streaming display."""
        self.logger.debug(f"Received partial summary: {len(partial_summary)} characters")
        
        # Display partial summary with progress indicator
        display_text = f"{partial_summary}\n\n[Processing continues...]"
        self.summary_output.setText(display_text)
    
    @Slot()
    def _on_summarization_cancelled(self):
        """Handle summarization cancellation."""
        self.logger.info("Summarization was cancelled")
        
        # Clear timeout
        self._clear_timeout()
        
        # Show cancellation message
        self.summary_output.setText("Summarization was cancelled.")
        
        # Reset processing state
        self._set_processing_state(False)
    
    @Slot(str, dict)
    def _on_model_loaded(self, model_id: str, model_info: dict):
        """Handle model loaded event."""
        self.logger.info(f"Model loaded: {model_id}")
        
        # Enable summarization
        self.summarize_button.setEnabled(True)
    
    @Slot(str)
    def _on_model_unloaded(self, model_id: str):
        """Handle model unloaded event."""
        self.logger.info(f"Model unloaded: {model_id}")
        
        # Disable summarization
        self.summarize_button.setEnabled(False)
        self._set_processing_state(False)
    
    # Universal loading system event handlers
    @Slot(dict)
    def _on_universal_loading_started(self, data: Dict[str, Any]):
        """Handle universal loading started event."""
        self.logger.info("Universal model loading started")
        
        # Show loading progress widget
        self.loading_progress_widget.show()
        self.model_info_widget.hide()
        
        # Update loading message
        model_path = data.get('model_path', 'Unknown')
        self.loading_message_label.setText(f"Loading model: {Path(model_path).name}")
        self.loading_progress_bar.setValue(0)
        self.loading_stage_label.setText("Initializing...")
        
        # Disable summarization during loading
        self.summarize_button.setEnabled(False)
    
    @Slot(dict)
    def _on_universal_progress_updated(self, data: Dict[str, Any]):
        """Handle universal loading progress update."""
        progress_info = data.get('progress_info', {})
        
        if isinstance(progress_info, dict):
            progress = progress_info.get('progress', 0)
            message = progress_info.get('message', 'Loading...')
            stage = progress_info.get('stage', '')
            backend_info = progress_info.get('backend_info', '')
            
            # Update progress display
            self.loading_progress_bar.setValue(progress)
            self.loading_message_label.setText(message)
            
            stage_text = f"Stage: {stage}"
            if backend_info:
                stage_text += f" | Backend: {backend_info}"
            self.loading_stage_label.setText(stage_text)
    
    @Slot(dict)
    def _on_universal_format_detected(self, data: Dict[str, Any]):
        """Handle universal format detection event."""
        model_path = data.get('model_path', '')
        format_type = data.get('format_type', 'unknown')
        metadata = data.get('metadata', {})
        
        self.logger.info(f"Model format detected: {format_type} for {Path(model_path).name}")
        
        # Update loading stage
        self.loading_stage_label.setText(f"Format detected: {format_type}")
    
    @Slot(dict)
    def _on_universal_backend_selected(self, data: Dict[str, Any]):
        """Handle universal backend selection event."""
        backend_name = data.get('backend_name', 'unknown')
        reason = data.get('reason', '')
        confidence = data.get('confidence', 0.0)
        
        self.logger.info(f"Backend selected: {backend_name} (confidence: {confidence:.2f})")
        
        # Update loading stage
        stage_text = f"Backend selected: {backend_name}"
        if reason:
            stage_text += f" | Reason: {reason}"
        self.loading_stage_label.setText(stage_text)
    
    @Slot(dict)
    def _on_universal_model_loaded(self, data: Dict[str, Any]):
        """Handle enhanced model loaded event."""
        loading_result = data.get('loading_result')
        if not loading_result:
            self.logger.warning("No loading result in universal model loaded event")
            return
        
        try:
            # Extract enhanced model information
            self.current_model_info = UniversalModelInfo(
                model_path=loading_result.get('model_path', ''),
                format_type=ModelFormat(loading_result.get('format_type', 'unknown')),
                backend_used=loading_result.get('backend_used', 'unknown'),
                hardware_used=loading_result.get('hardware_used', 'unknown'),
                metadata=loading_result.get('metadata', {}),
                capabilities=self._extract_capabilities(loading_result),
                performance_metrics=loading_result.get('performance_metrics', {}),
                memory_usage=loading_result.get('memory_usage', 0),
                optimization_applied=loading_result.get('optimization_applied', []),
                load_time=loading_result.get('load_time', 0.0)
            )
            
            self.logger.info(f"Universal model loaded: {self.current_model_info.get_display_name()}")
            
            # Hide loading progress and show model info
            self.loading_progress_widget.hide()
            self.model_info_widget.show()
            
            # Update model information display
            self._update_model_info_display()
            
            # Adapt interface based on model capabilities
            self._adapt_interface_for_model()
            
            # Show format-specific options
            self._show_format_specific_options()
            
            # Update performance indicators
            self._update_performance_indicators()
            
            # Enable summarization
            self.summarize_button.setEnabled(True)
            
        except Exception as e:
            self.logger.error(f"Error handling universal model loaded event: {e}")
            self._on_universal_loading_failed({'error_message': str(e), 'error_analysis': {}})
    
    @Slot(dict)
    def _on_universal_loading_failed(self, data: Dict[str, Any]):
        """Handle universal loading failure event."""
        error_message = data.get('error_message', 'Unknown error')
        error_analysis = data.get('error_analysis', {})
        
        self.logger.error(f"Universal model loading failed: {error_message}")
        
        # Hide loading progress
        self.loading_progress_widget.hide()
        self.model_info_widget.hide()
        
        # Reset current model info
        self.current_model_info = None
        
        # Hide format-specific options
        if self.format_specific_options:
            self.format_specific_options.hide()
        if self.performance_indicator:
            self.performance_indicator.hide()
        
        # Disable summarization
        self.summarize_button.setEnabled(False)
        
        # Show error message
        QMessageBox.critical(
            self,
            "Model Loading Failed",
            f"Failed to load model:\n\n{error_message}"
        )
    
    @Slot(dict)
    def _on_universal_model_unloaded(self, data: Dict[str, Any]):
        """Handle universal model unloaded event."""
        model_path = data.get('model_path', '')
        cleanup_info = data.get('cleanup_info', {})
        
        self.logger.info(f"Universal model unloaded: {Path(model_path).name}")
        
        # Reset state
        self.current_model_info = None
        self.model_info_widget.hide()
        self.loading_progress_widget.hide()
        
        # Hide format-specific options
        if self.format_specific_options:
            self.format_specific_options.hide()
        if self.performance_indicator:
            self.performance_indicator.hide()
        
        # Disable summarization
        self.summarize_button.setEnabled(False)
        self._set_processing_state(False)
    
    @Slot(dict)
    def _on_performance_metrics_updated(self, data: Dict[str, Any]):
        """Handle performance metrics update."""
        performance_data = data.get('performance_data', {})
        
        if self.current_model_info and self.performance_indicator.isVisible():
            # Update performance expectations
            self._update_performance_indicators(performance_data)
    
    @Slot(dict)
    def _on_performance_warning(self, data: Dict[str, Any]):
        """Handle performance warning."""
        warning_type = data.get('warning_type', '')
        details = data.get('details', '')
        
        if self.performance_indicator and self.performance_indicator.isVisible():
            # Show memory warning
            if 'memory' in warning_type.lower():
                self.memory_warning_label.setText(f"[WARN] {details}")
                self.memory_warning_label.show()
    
    # Helper methods for universal integration
    def _extract_capabilities(self, loading_result: Dict[str, Any]) -> List[str]:
        """Extract model capabilities from loading result."""
        capabilities = []
        
        # Extract from metadata
        metadata = loading_result.get('metadata', {})
        if 'task_capabilities' in metadata:
            capabilities.extend(metadata['task_capabilities'])
        
        # Add format-specific capabilities
        format_type = loading_result.get('format_type', 'unknown')
        if format_type == 'gguf':
            capabilities.append('Efficient inference')
        elif format_type == 'safetensors':
            capabilities.append('Safe tensor loading')
        elif format_type == 'huggingface':
            capabilities.append('HuggingFace ecosystem')
        
        # Add backend-specific capabilities
        backend_used = loading_result.get('backend_used', '')
        if 'gpu' in backend_used.lower():
            capabilities.append('GPU acceleration')
        
        return capabilities or ['General text processing']
    
    def _update_model_info_display(self):
        """Update the model information display."""
        if not self.current_model_info:
            return
        
        # Update model name and format
        display_name = self.current_model_info.get_display_name()
        format_name = self.current_model_info.format_type.value.upper()
        self.model_name_label.setText(f"{display_name} ({format_name})")
        
        # Update capabilities
        capabilities_text = self.current_model_info.get_capability_description()
        self.model_capabilities_label.setText(f"Capabilities: {capabilities_text}")
        
        # Update performance metrics
        performance_text = self.current_model_info.get_performance_summary()
        backend_text = f"Backend: {self.current_model_info.backend_used}"
        self.performance_metrics_label.setText(f"{performance_text} | {backend_text}")
    
    def _adapt_interface_for_model(self):
        """Adapt interface based on loaded model capabilities."""
        if not self.current_model_info:
            return
        
        # Show optimal parameters for summarization
        if 'summarization' in self.current_model_info.capabilities:
            # Adjust default settings for summarization-optimized models
            self.style_combo.setCurrentText("Concise")
            self.length_spinbox.setValue(150)  # Shorter for specialized models
        
        # Adjust memory-aware processing
        if self.current_model_info.memory_usage > 8000:  # 8GB
            self.memory_aware_checkbox.setChecked(True)
            self.memory_aware_checkbox.setToolTip(
                f"Model uses {self.current_model_info.memory_usage}MB memory. "
                "Memory-aware processing is recommended."
            )
    
    def _show_format_specific_options(self):
        """Show format-specific summarization options."""
        if not self.current_model_info:
            return
        
        # Show format-specific options
        self.format_specific_options.show()
        
        # Update optimization information
        if self.current_model_info.optimization_applied:
            optimizations = ", ".join(self.current_model_info.optimization_applied)
            self.optimization_label.setText(f"Optimizations: {optimizations}")
        else:
            self.optimization_label.setText("Optimizations: None applied")
    
    def _update_performance_indicators(self, performance_data: Dict[str, Any] = None):
        """Update performance expectations display."""
        if not self.current_model_info:
            return
        
        # Show performance indicator
        self.performance_indicator.show()
        
        # Update backend information
        backend_text = f"Backend: {self.current_model_info.backend_used}"
        if self.current_model_info.hardware_used != 'unknown':
            backend_text += f" ({self.current_model_info.hardware_used})"
        self.backend_info_label.setText(backend_text)
        
        # Update performance expectations based on format and backend
        format_type = self.current_model_info.format_type
        backend = self.current_model_info.backend_used
        
        if format_type == ModelFormat.GGUF and 'gpu' in backend.lower():
            expectation = "[PERF] Fast inference with GPU acceleration"
        elif format_type == ModelFormat.GGUF:
            expectation = "[TOOL] Optimized CPU inference"
        elif format_type == ModelFormat.SAFETENSORS:
            expectation = "🛡️ Safe and reliable inference"
        elif format_type == ModelFormat.HUGGINGFACE:
            expectation = "🤗 Full HuggingFace ecosystem support"
        else:
            expectation = "📊 Standard inference performance"
        
        self.performance_expectation_label.setText(expectation)
        
        # Clear memory warning if performance is good
        if self.current_model_info.memory_usage < 4000:  # Less than 4GB
            self.memory_warning_label.hide()
    
    # Enhanced progress event handlers
    @Slot(int, str)
    def _on_chunk_progress(self, progress_percent: int, status_message: str):
        """Handle chunk processing progress."""
        if hasattr(self, 'progress_bar'):
            self.progress_bar.setValue(progress_percent)
        
        if hasattr(self, 'progress_details_label'):
            self.progress_details_label.setText(status_message)
        
        self.logger.debug(f"Chunk progress: {progress_percent}% - {status_message}")
    
    @Slot(int, str)
    def _on_chunk_completed(self, chunk_index: int, chunk_summary: str):
        """Handle chunk completion."""
        if hasattr(self, 'processing_stats_label'):
            stats_text = f"Completed chunk {chunk_index + 1} ({len(chunk_summary)} characters)"
            self.processing_stats_label.setText(stats_text)
        
        # Show partial progress in summary output
        current_text = self.summary_output.toPlainText()
        if "Starting summarization" in current_text or "Processing:" in current_text:
            preview = chunk_summary[:200] + "..." if len(chunk_summary) > 200 else chunk_summary
            self.summary_output.setText(f"Processing chunks... Latest completed:\n\n{preview}\n\n[Processing continues...]")
        
        self.logger.info(f"Chunk {chunk_index + 1} completed: {len(chunk_summary)} characters")
    
    def clear_document(self):
        """Clear the document input."""
        self.document_input.clear()
        self.current_document_path = None
        self.file_label.setText("No file loaded")
        self.file_label.setStyleSheet("color: #6c757d; font-style: italic;")
    
    def clear_summary(self):
        """Clear the summary output."""
        self.summary_output.clear()
    
    def get_document_text(self) -> str:
        """Get the current document text."""
        return self.document_input.toPlainText()
    
    def set_document_text(self, text: str):
        """Set the document text."""
        self.document_input.setText(text)
    
    def get_summary_text(self) -> str:
        """Get the current summary text."""
        return self.summary_output.toPlainText()
# Backward compatibility alias
SummarizationTab = EnhancedSummarizationTab