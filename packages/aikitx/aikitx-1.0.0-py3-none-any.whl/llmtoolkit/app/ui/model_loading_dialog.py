"""
Model Loading Progress Dialog

This module provides a progress dialog for model loading operations with
detailed progress reporting, memory usage monitoring, and cancellation support.
"""

import logging
from typing import Optional

from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, 
    QProgressBar, QTextEdit, QFrame
)
from PySide6.QtCore import Qt, Signal, Slot
from PySide6.QtGui import QFont, QTextCursor


class ModelLoadingDialog(QDialog):
    """
    Progress dialog for model loading operations.
    
    Features:
    - Progress bar with percentage
    - Detailed progress messages
    - Memory usage monitoring
    - Cancellation support
    - Clean, informative interface
    """
    
    # Signals
    cancelled = Signal()  # User requested cancellation
    
    def __init__(self, model_name: str, parent=None):
        """
        Initialize the model loading dialog.
        
        Args:
            model_name: Name of the model being loaded
            parent: Parent widget
        """
        super().__init__(parent)
        
        self.logger = logging.getLogger("gguf_loader.ui.model_loading_dialog")
        self.model_name = model_name
        self._is_cancelled = False
        
        # Set dialog properties
        self.setWindowTitle("Loading Model")
        self.setModal(True)
        self.setFixedSize(500, 300)
        self.setWindowFlags(Qt.Dialog | Qt.WindowTitleHint)
        
        # Initialize UI
        self._init_ui()
        
        self.logger.info(f"Model loading dialog initialized for: {model_name}")
    
    def _init_ui(self):
        """Initialize the user interface."""
        layout = QVBoxLayout(self)
        layout.setSpacing(15)
        layout.setContentsMargins(20, 20, 20, 20)
        
        # Title section
        title_label = QLabel(f"Loading Model: {self.model_name}")
        title_font = QFont()
        title_font.setPointSize(12)
        title_font.setBold(True)
        title_label.setFont(title_font)
        title_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(title_label)
        
        # Progress bar section
        progress_frame = QFrame()
        progress_layout = QVBoxLayout(progress_frame)
        progress_layout.setSpacing(10)
        
        # Progress bar
        self.progress_bar = QProgressBar()
        self.progress_bar.setRange(0, 100)
        self.progress_bar.setValue(0)
        self.progress_bar.setTextVisible(True)
        self.progress_bar.setStyleSheet("""
            QProgressBar {
                border: 2px solid #cccccc;
                border-radius: 5px;
                text-align: center;
                font-weight: bold;
            }
            QProgressBar::chunk {
                background-color: #4CAF50;
                border-radius: 3px;
            }
        """)
        progress_layout.addWidget(self.progress_bar)
        
        # Progress message
        self.progress_label = QLabel("Initializing...")
        self.progress_label.setAlignment(Qt.AlignCenter)
        self.progress_label.setStyleSheet("color: #666666; font-size: 11px;")
        progress_layout.addWidget(self.progress_label)
        
        layout.addWidget(progress_frame)
        
        # Memory usage section
        memory_frame = QFrame()
        memory_layout = QHBoxLayout(memory_frame)
        memory_layout.setContentsMargins(0, 0, 0, 0)
        
        memory_icon_label = QLabel("🧠")
        memory_icon_label.setFixedWidth(20)
        memory_layout.addWidget(memory_icon_label)
        
        self.memory_label = QLabel("Memory Usage: -- MB")
        self.memory_label.setStyleSheet("color: #444444; font-size: 10px;")
        memory_layout.addWidget(self.memory_label)
        
        memory_layout.addStretch()
        layout.addWidget(memory_frame)
        
        # Detailed log section (collapsible)
        self.log_text = QTextEdit()
        self.log_text.setMaximumHeight(80)
        self.log_text.setReadOnly(True)
        self.log_text.setStyleSheet("""
            QTextEdit {
                background-color: #f8f8f8;
                border: 1px solid #dddddd;
                border-radius: 3px;
                font-family: 'Courier New', monospace;
                font-size: 9px;
                color: #333333;
            }
        """)
        layout.addWidget(self.log_text)
        
        # Button section
        button_layout = QHBoxLayout()
        button_layout.addStretch()
        
        self.cancel_button = QPushButton("Cancel")
        self.cancel_button.setFixedSize(80, 30)
        self.cancel_button.clicked.connect(self._on_cancel)
        self.cancel_button.setStyleSheet("""
            QPushButton {
                background-color: #f44336;
                color: white;
                border: none;
                border-radius: 4px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #d32f2f;
            }
            QPushButton:pressed {
                background-color: #b71c1c;
            }
            QPushButton:disabled {
                background-color: #cccccc;
                color: #666666;
            }
        """)
        button_layout.addWidget(self.cancel_button)
        
        layout.addLayout(button_layout)
    
    @Slot(int)
    def update_progress(self, percentage: int):
        """
        Update the progress bar.
        
        Args:
            percentage: Progress percentage (0-100)
        """
        self.progress_bar.setValue(percentage)
        
        if percentage >= 100:
            self.progress_label.setText("Loading complete!")
            self.cancel_button.setEnabled(False)
    
    @Slot(str)
    def update_progress_message(self, message: str):
        """
        Update the progress message.
        
        Args:
            message: Progress message to display
        """
        self.progress_label.setText(message)
        
        # Add to log
        self.log_text.append(f"• {message}")
        
        # Auto-scroll to bottom
        cursor = self.log_text.textCursor()
        cursor.movePosition(QTextCursor.MoveOperation.End)
        self.log_text.setTextCursor(cursor)
    
    @Slot(int)
    def update_memory_usage(self, memory_mb: int):
        """
        Update the memory usage display.
        
        Args:
            memory_mb: Memory usage in megabytes
        """
        self.memory_label.setText(f"Memory Usage: {memory_mb:,} MB")
        
        # Change color based on memory usage
        if memory_mb > 8000:  # > 8GB
            color = "#f44336"  # Red
        elif memory_mb > 4000:  # > 4GB
            color = "#ff9800"  # Orange
        else:
            color = "#4CAF50"  # Green
        
        self.memory_label.setStyleSheet(f"color: {color}; font-size: 10px; font-weight: bold;")
    
    @Slot()
    def on_loading_finished(self):
        """Handle successful model loading completion."""
        self.progress_bar.setValue(100)
        self.progress_label.setText("Model loaded successfully!")
        self.cancel_button.setText("Close")
        self.cancel_button.setStyleSheet("""
            QPushButton {
                background-color: #4CAF50;
                color: white;
                border: none;
                border-radius: 4px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #45a049;
            }
        """)
        
        # Auto-close after a short delay
        from PySide6.QtCore import QTimer
        QTimer.singleShot(1500, self.accept)
    
    @Slot()
    def on_loading_error(self, error_message: str):
        """
        Handle model loading error.
        
        Args:
            error_message: Error message to display
        """
        self.progress_label.setText("Loading failed!")
        self.progress_label.setStyleSheet("color: #f44336; font-weight: bold;")
        
        self.log_text.append(f"[ERROR] ERROR: {error_message}")
        
        self.cancel_button.setText("Close")
        self.cancel_button.setStyleSheet("""
            QPushButton {
                background-color: #666666;
                color: white;
                border: none;
                border-radius: 4px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #555555;
            }
        """)
    
    @Slot()
    def on_loading_cancelled(self):
        """Handle model loading cancellation."""
        self.progress_label.setText("Loading cancelled")
        self.progress_label.setStyleSheet("color: #ff9800; font-weight: bold;")
        
        self.log_text.append("[WARN] Loading cancelled by user")
        
        self.cancel_button.setText("Close")
        self.cancel_button.setEnabled(True)
    
    def _on_cancel(self):
        """Handle cancel button click."""
        if self.cancel_button.text() == "Cancel" and not self._is_cancelled:
            self._is_cancelled = True
            self.cancelled.emit()
            self.cancel_button.setEnabled(False)
            self.cancel_button.setText("Cancelling...")
            self.progress_label.setText("Cancelling...")
            self.logger.info("User requested model loading cancellation")
        else:
            # Close dialog
            self.reject()
    
    def closeEvent(self, event):
        """Handle dialog close event."""
        if not self._is_cancelled and self.cancel_button.text() == "Cancel":
            # User is trying to close during loading - treat as cancellation
            self._on_cancel()
            event.ignore()  # Don't close yet
        else:
            event.accept()