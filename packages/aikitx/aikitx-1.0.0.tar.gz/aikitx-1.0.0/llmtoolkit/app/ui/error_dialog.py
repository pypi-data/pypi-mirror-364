"""
Error Dialog

This module provides a dialog for displaying detailed error information to users.
"""

import os
import datetime
from typing import Optional, Dict, Any, List

from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, 
    QTextEdit, QTabWidget, QWidget, QFileDialog, QMessageBox,
    QTableWidget, QTableWidgetItem, QHeaderView
)
from PySide6.QtCore import Qt, QSize
from PySide6.QtGui import QFont, QIcon

class ErrorDetailsDialog(QDialog):
    """
    Dialog for displaying detailed error information.
    
    This dialog shows:
    - User-friendly error message
    - Technical details (exception type, traceback)
    - Context information
    - Options to copy error details or save to file
    """
    
    def __init__(self, error: Exception, category: str, context: str, 
                 parent=None, error_manager=None):
        """
        Initialize the error details dialog.
        
        Args:
            error: The exception
            category: Error category
            context: Error context
            parent: Parent widget
            error_manager: Reference to the error manager (optional)
        """
        super().__init__(parent)
        
        self.error = error
        self.category = category
        self.context = context
        self.error_manager = error_manager
        
        self.setWindowTitle("Error Details")
        self.setMinimumSize(600, 400)
        
        self._init_ui()
    
    def _init_ui(self):
        """Initialize the UI components."""
        layout = QVBoxLayout()
        
        # Error message
        message_label = QLabel(f"<b>{str(self.error)}</b>")
        message_label.setWordWrap(True)
        layout.addWidget(message_label)
        
        # Context information
        if self.context:
            context_label = QLabel(f"Context: {self.context}")
            context_label.setWordWrap(True)
            layout.addWidget(context_label)
        
        # Tab widget for details
        tab_widget = QTabWidget()
        
        # Details tab
        details_widget = QWidget()
        details_layout = QVBoxLayout(details_widget)
        
        details_text = QTextEdit()
        details_text.setReadOnly(True)
        
        # Collect error details
        details = f"Error Type: {type(self.error).__name__}\n"
        details += f"Category: {self.category}\n"
        details += f"Timestamp: {datetime.datetime.now().isoformat()}\n\n"
        
        if hasattr(self.error, "__traceback__"):
            import traceback
            details += "Traceback:\n"
            details += "".join(traceback.format_exception(
                type(self.error), self.error, self.error.__traceback__
            ))
        
        details_text.setText(details)
        details_layout.addWidget(details_text)
        
        tab_widget.addTab(details_widget, "Technical Details")
        
        # Recent errors tab (if error manager is available)
        if self.error_manager:
            history_widget = QWidget()
            history_layout = QVBoxLayout(history_widget)
            
            history_table = QTableWidget()
            history_table.setColumnCount(4)
            history_table.setHorizontalHeaderLabels(["Time", "Type", "Category", "Message"])
            history_table.horizontalHeader().setSectionResizeMode(3, QHeaderView.Stretch)
            
            # Get recent errors
            recent_errors = self.error_manager.get_recent_errors(limit=20)
            history_table.setRowCount(len(recent_errors))
            
            for i, error in enumerate(recent_errors):
                # Format timestamp
                timestamp = error.get("timestamp", "")
                if timestamp:
                    try:
                        dt = datetime.datetime.fromisoformat(timestamp)
                        timestamp = dt.strftime("%H:%M:%S")
                    except (ValueError, TypeError):
                        pass
                
                history_table.setItem(i, 0, QTableWidgetItem(timestamp))
                history_table.setItem(i, 1, QTableWidgetItem(error.get("type", "")))
                history_table.setItem(i, 2, QTableWidgetItem(error.get("category", "")))
                history_table.setItem(i, 3, QTableWidgetItem(error.get("message", "")))
            
            history_layout.addWidget(history_table)
            tab_widget.addTab(history_widget, "Recent Errors")
        
        layout.addWidget(tab_widget)
        
        # Buttons
        button_layout = QHBoxLayout()
        
        copy_button = QPushButton("Copy Details")
        copy_button.clicked.connect(lambda: self._copy_to_clipboard(details))
        
        save_button = QPushButton("Save Details")
        save_button.clicked.connect(lambda: self._save_to_file(details))
        
        close_button = QPushButton("Close")
        close_button.clicked.connect(self.accept)
        
        button_layout.addWidget(copy_button)
        button_layout.addWidget(save_button)
        button_layout.addStretch()
        button_layout.addWidget(close_button)
        
        layout.addLayout(button_layout)
        
        self.setLayout(layout)
    
    def _copy_to_clipboard(self, text):
        """Copy text to clipboard."""
        from PySide6.QtGui import QGuiApplication
        clipboard = QGuiApplication.clipboard()
        clipboard.setText(text)
        
        QMessageBox.information(
            self,
            "Copied",
            "Error details copied to clipboard."
        )
    
    def _save_to_file(self, text):
        """Save text to a file."""
        file_path, _ = QFileDialog.getSaveFileName(
            self,
            "Save Error Details",
            os.path.expanduser("~/error_details.txt"),
            "Text Files (*.txt)"
        )
        
        if file_path:
            try:
                with open(file_path, 'w') as f:
                    f.write(text)
                
                QMessageBox.information(
                    self,
                    "Saved",
                    f"Error details saved to {file_path}"
                )
            except Exception as e:
                QMessageBox.warning(
                    self,
                    "Save Failed",
                    f"Failed to save error details: {str(e)}"
                )


class ErrorLogViewerDialog(QDialog):
    """
    Dialog for viewing and managing error logs.
    
    This dialog shows:
    - Table of error logs
    - Filtering options
    - Export functionality
    """
    
    def __init__(self, error_manager, parent=None):
        """
        Initialize the error log viewer dialog.
        
        Args:
            error_manager: Reference to the error manager
            parent: Parent widget
        """
        super().__init__(parent)
        
        self.error_manager = error_manager
        
        self.setWindowTitle("Error Log Viewer")
        self.setMinimumSize(800, 500)
        
        self._init_ui()
    
    def _init_ui(self):
        """Initialize the UI components."""
        layout = QVBoxLayout()
        
        # Table for error logs
        self.table = QTableWidget()
        self.table.setColumnCount(5)
        self.table.setHorizontalHeaderLabels(["Time", "Type", "Category", "Severity", "Message"])
        self.table.horizontalHeader().setSectionResizeMode(4, QHeaderView.Stretch)
        
        # Load error logs
        self._load_error_logs()
        
        layout.addWidget(self.table)
        
        # Buttons
        button_layout = QHBoxLayout()
        
        refresh_button = QPushButton("Refresh")
        refresh_button.clicked.connect(self._load_error_logs)
        
        export_button = QPushButton("Export Logs")
        export_button.clicked.connect(self._export_logs)
        
        clear_button = QPushButton("Clear Logs")
        clear_button.clicked.connect(self._clear_logs)
        
        close_button = QPushButton("Close")
        close_button.clicked.connect(self.accept)
        
        button_layout.addWidget(refresh_button)
        button_layout.addWidget(export_button)
        button_layout.addWidget(clear_button)
        button_layout.addStretch()
        button_layout.addWidget(close_button)
        
        layout.addLayout(button_layout)
        
        self.setLayout(layout)
    
    def _load_error_logs(self):
        """Load error logs into the table."""
        # Get all error logs
        error_logs = self.error_manager.get_recent_errors(limit=1000)
        
        # Update table
        self.table.setRowCount(len(error_logs))
        
        for i, error in enumerate(error_logs):
            # Format timestamp
            timestamp = error.get("timestamp", "")
            if timestamp:
                try:
                    dt = datetime.datetime.fromisoformat(timestamp)
                    timestamp = dt.strftime("%Y-%m-%d %H:%M:%S")
                except (ValueError, TypeError):
                    pass
            
            self.table.setItem(i, 0, QTableWidgetItem(timestamp))
            self.table.setItem(i, 1, QTableWidgetItem(error.get("type", "")))
            self.table.setItem(i, 2, QTableWidgetItem(error.get("category", "")))
            self.table.setItem(i, 3, QTableWidgetItem(error.get("severity", "")))
            self.table.setItem(i, 4, QTableWidgetItem(error.get("message", "")))
    
    def _export_logs(self):
        """Export error logs to a file."""
        file_path, _ = QFileDialog.getSaveFileName(
            self,
            "Export Error Logs",
            os.path.expanduser("~/error_logs.json"),
            "JSON Files (*.json)"
        )
        
        if file_path:
            success = self.error_manager.export_error_report(file_path)
            
            if success:
                QMessageBox.information(
                    self,
                    "Export Successful",
                    f"Error logs exported to {file_path}"
                )
            else:
                QMessageBox.warning(
                    self,
                    "Export Failed",
                    "Failed to export error logs"
                )
    
    def _clear_logs(self):
        """Clear error logs."""
        reply = QMessageBox.question(
            self,
            "Clear Logs",
            "Are you sure you want to clear all error logs?",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No
        )
        
        if reply == QMessageBox.Yes:
            self.error_manager.clear_error_history()
            self._load_error_logs()  # Refresh the table