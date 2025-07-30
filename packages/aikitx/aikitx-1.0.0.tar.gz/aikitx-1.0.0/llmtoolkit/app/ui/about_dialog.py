"""
About Dialog

This module provides an about dialog showing application information,
version details, and credits.
"""

import logging
from pathlib import Path

from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, 
    QTextEdit, QFrame
)
from PySide6.QtCore import Qt
from PySide6.QtGui import QFont, QPixmap

from llmtoolkit.app.ui.theme_manager import ThemeManager


class AboutDialog(QDialog):
    """
    About dialog showing application information.
    
    Features:
    - Application name and version
    - Description and features
    - Credits and acknowledgments
    - System information
    """
    
    def __init__(self, parent=None):
        """
        Initialize the about dialog.
        
        Args:
            parent: Parent widget
        """
        super().__init__(parent)
        
        self.logger = logging.getLogger("gguf_loader.ui.about_dialog")
        
        # Initialize theme manager
        self.theme_manager = ThemeManager()
        
        # Set dialog properties
        self.setWindowTitle("About LLM Toolkit")
        self.setModal(True)
        self.setFixedSize(500, 400)
        
        # Initialize UI
        self._init_ui()
        
        # Apply global theme
        self._apply_theme()
        
        self.logger.info("About dialog initialized")
    
    def _init_ui(self):
        """Initialize the user interface."""
        layout = QVBoxLayout(self)
        layout.setSpacing(20)
        layout.setContentsMargins(30, 30, 30, 30)
        
        # Header section
        header_layout = QHBoxLayout()
        
        # App icon (if available)
        try:
            from llmtoolkit.resource_manager import get_pixmap
            pixmap = get_pixmap("icon.ico")
            if pixmap and not pixmap.isNull():
                icon_label = QLabel()
                scaled_pixmap = pixmap.scaled(64, 64, Qt.KeepAspectRatio, Qt.SmoothTransformation)
                icon_label.setPixmap(scaled_pixmap)
                header_layout.addWidget(icon_label)
        except Exception:
            pass  # Skip icon if there's an issue
        
        # App info
        info_layout = QVBoxLayout()
        
        # App name
        app_name = QLabel("LLM Toolkit")
        app_font = QFont()
        app_font.setPointSize(18)
        app_font.setBold(True)
        app_name.setFont(app_font)
        info_layout.addWidget(app_name)
        
        # Version
        version_label = QLabel("Version 1.0.0")
        info_layout.addWidget(version_label)
        
        # Description
        desc_label = QLabel("A comprehensive desktop toolkit for working with Large Language Models")
        desc_label.setWordWrap(True)
        info_layout.addWidget(desc_label)
        
        header_layout.addLayout(info_layout)
        header_layout.addStretch()
        layout.addLayout(header_layout)
        
        # Separator
        separator = QFrame()
        separator.setFrameShape(QFrame.HLine)
        separator.setFrameShadow(QFrame.Sunken)
        layout.addWidget(separator)
        
        # Features section
        features_label = QLabel("Features:")
        layout.addWidget(features_label)
        
        features_text = QTextEdit()
        features_text.setReadOnly(True)
        features_text.setMaximumHeight(150)
        
        features_content = """• Load and manage GGUF model files
• Interactive chat interface with AI models
• Document summarization capabilities
• Background model loading with progress tracking
• Memory usage monitoring and optimization
• Configurable system prompts and model parameters
• Dark mode support and theme customization
• Extensible plugin system
• GPU acceleration support (CUDA, OpenCL, Metal)
• Comprehensive error handling and recovery"""
        
        features_text.setText(features_content)
        layout.addWidget(features_text)
        
        # Developer section
        developer_label = QLabel("Developer:")
        layout.addWidget(developer_label)
        
        developer_text = QLabel("Hussain Nazar\nEmail: Artaservices2021@gmail.com")
        developer_text.setWordWrap(True)
        layout.addWidget(developer_text)
        
        # Credits section
        credits_label = QLabel("Built with:")
        layout.addWidget(credits_label)
        
        credits_text = QLabel("• PySide6 for the user interface\n• llama-cpp-python for model inference\n• Python 3.10+ runtime environment")
        layout.addWidget(credits_text)
        
        # Support section
        support_label = QLabel("Support:")
        layout.addWidget(support_label)
        
        support_text = QLabel("For documentation and support,\nvisit our GitHub repository at:\nhttps://github.com/llm-toolkit/gguf-loader")
        support_text.setWordWrap(True)
        layout.addWidget(support_text)
        
        # Button layout
        button_layout = QHBoxLayout()
        button_layout.addStretch()
        
        # Close button
        close_button = QPushButton("Close")
        close_button.setDefault(True)
        close_button.clicked.connect(self.accept)
        button_layout.addWidget(close_button)
        
        layout.addLayout(button_layout)
    
    def _apply_theme(self):
        """Apply global theme to about dialog using ThemeManager."""
        try:
            # Use the global theme manager to apply consistent theming
            self.theme_manager.apply_theme_to_widget(self)
            
        except Exception as e:
            self.logger.error(f"Failed to apply theme to about dialog: {e}")