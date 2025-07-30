"""
System Prompts Dialog

This module provides a dialog for configuring system prompts and templates
for different AI conversation scenarios.
"""

import logging
from typing import Dict, Any

from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, 
    QTextEdit, QComboBox, QTabWidget, QWidget, QMessageBox,
    QSplitter, QListWidget, QListWidgetItem
)
from PySide6.QtCore import Qt, Signal, Slot
from PySide6.QtGui import QFont


class SystemPromptsDialog(QDialog):
    """
    Dialog for configuring system prompts and templates.
    
    Features:
    - Default system prompt configuration
    - Pre-built prompt templates
    - Custom prompt creation and management
    - Preview functionality
    """
    
    # Signals
    system_prompt_changed = Signal(str)  # Emitted when system prompt changes
    
    # Default system prompts for different scenarios
    DEFAULT_PROMPTS = {
        "Assistant": "You are a helpful, harmless, and honest AI assistant. Provide accurate, informative responses while being respectful and professional. If you're unsure about something, say so rather than guessing.",
        
        "Creative Writer": "You are a creative writing assistant. Help users with storytelling, character development, plot ideas, and creative expression. Be imaginative and inspiring while maintaining coherence and quality.",
        
        "Code Helper": "You are a programming assistant. Help users with coding questions, debugging, code review, and software development best practices. Provide clear explanations and working code examples when appropriate.",
        
        "Research Assistant": "You are a research assistant. Help users find information, analyze data, summarize sources, and provide well-researched answers. Always cite sources when possible and distinguish between facts and opinions.",
        
        "Tutor": "You are a patient and encouraging tutor. Help users learn new concepts by breaking down complex topics into understandable parts. Use examples, analogies, and step-by-step explanations.",
        
        "Professional": "You are a professional business assistant. Provide formal, concise, and actionable advice for workplace scenarios. Focus on efficiency, clarity, and professional communication standards.",
        
        "Casual Friend": "You are a friendly and casual conversational partner. Be warm, approachable, and engaging while maintaining helpfulness. Use a relaxed tone and show genuine interest in the conversation.",
        
        "Technical Expert": "You are a technical expert with deep knowledge in various fields. Provide detailed, accurate technical information with proper terminology. Explain complex concepts thoroughly and precisely."
    }
    
    def __init__(self, config_manager, current_prompt: str = "", parent=None):
        """
        Initialize the system prompts dialog.
        
        Args:
            config_manager: Configuration manager for saving settings
            current_prompt: Current system prompt
            parent: Parent widget
        """
        super().__init__(parent)
        
        self.logger = logging.getLogger("gguf_loader.ui.system_prompts_dialog")
        self.config_manager = config_manager
        self.current_prompt = current_prompt or self.DEFAULT_PROMPTS["Assistant"]
        
        # Set dialog properties
        self.setWindowTitle("System Prompts Configuration")
        self.setModal(True)
        self.setMinimumSize(700, 500)
        
        # Initialize UI
        self._init_ui()
        
        # Load current settings
        self._load_settings()
        
        self.logger.info("System prompts dialog initialized")
    
    def _init_ui(self):
        """Initialize the user interface."""
        layout = QVBoxLayout(self)
        layout.setSpacing(15)
        layout.setContentsMargins(20, 20, 20, 20)
        
        # Title
        title_label = QLabel("System Prompts Configuration")
        title_font = QFont()
        title_font.setPointSize(14)
        title_font.setBold(True)
        title_label.setFont(title_font)
        layout.addWidget(title_label)
        
        # Create splitter for templates and editor
        splitter = QSplitter(Qt.Horizontal)
        layout.addWidget(splitter)
        
        # Left side - Template selection
        template_widget = self._create_template_widget()
        splitter.addWidget(template_widget)
        
        # Right side - Prompt editor
        editor_widget = self._create_editor_widget()
        splitter.addWidget(editor_widget)
        
        # Set splitter proportions
        splitter.setSizes([250, 450])
        
        # Button layout
        button_layout = QHBoxLayout()
        button_layout.addStretch()
        
        # Preview button
        self.preview_button = QPushButton("Preview")
        self.preview_button.clicked.connect(self._preview_prompt)
        button_layout.addWidget(self.preview_button)
        
        # Reset button
        self.reset_button = QPushButton("Reset to Default")
        self.reset_button.clicked.connect(self._reset_to_default)
        button_layout.addWidget(self.reset_button)
        
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
    
    def _create_template_widget(self):
        """Create the template selection widget."""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        
        # Template list label
        label = QLabel("Prompt Templates:")
        label.setStyleSheet("font-weight: bold; color: #495057;")
        layout.addWidget(label)
        
        # Template list
        self.template_list = QListWidget()
        self.template_list.setStyleSheet("""
            QListWidget {
                border: 1px solid #dee2e6;
                border-radius: 4px;
                background-color: white;
                selection-background-color: #0078d4;
            }
            QListWidget::item {
                padding: 8px;
                border-bottom: 1px solid #f0f0f0;
            }
            QListWidget::item:hover {
                background-color: #f8f9fa;
            }
        """)
        
        # Add template items
        for template_name in self.DEFAULT_PROMPTS.keys():
            item = QListWidgetItem(template_name)
            self.template_list.addItem(item)
        
        self.template_list.currentItemChanged.connect(self._on_template_selected)
        layout.addWidget(self.template_list)
        
        return widget
    
    def _create_editor_widget(self):
        """Create the prompt editor widget."""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        
        # Editor label
        label = QLabel("System Prompt:")
        label.setStyleSheet("font-weight: bold; color: #495057;")
        layout.addWidget(label)
        
        # Prompt editor
        self.prompt_editor = QTextEdit()
        self.prompt_editor.setPlaceholderText("Enter your system prompt here...")
        self.prompt_editor.setStyleSheet("""
            QTextEdit {
                border: 2px solid #dee2e6;
                border-radius: 8px;
                padding: 15px;
                font-family: 'Segoe UI', Arial, sans-serif;
                font-size: 14px;
                background-color: white;
                line-height: 1.4;
            }
            QTextEdit:focus {
                border-color: #0078d4;
            }
        """)
        layout.addWidget(self.prompt_editor)
        
        # Character count
        self.char_count_label = QLabel("0 characters")
        self.char_count_label.setStyleSheet("color: #6c757d; font-size: 12px;")
        self.prompt_editor.textChanged.connect(self._update_char_count)
        layout.addWidget(self.char_count_label)
        
        return widget
    
    def _load_settings(self):
        """Load current settings."""
        # Load saved system prompt or use default
        saved_prompt = self.config_manager.get_value("system_prompt", self.DEFAULT_PROMPTS["Assistant"])
        self.prompt_editor.setText(saved_prompt)
        self._update_char_count()
        
        # Select matching template if any
        for i in range(self.template_list.count()):
            item = self.template_list.item(i)
            template_name = item.text()
            if self.DEFAULT_PROMPTS[template_name] == saved_prompt:
                self.template_list.setCurrentItem(item)
                break
    
    def _on_template_selected(self, current, previous):
        """Handle template selection."""
        if current:
            template_name = current.text()
            template_prompt = self.DEFAULT_PROMPTS[template_name]
            self.prompt_editor.setText(template_prompt)
            self.logger.info(f"Selected template: {template_name}")
    
    def _update_char_count(self):
        """Update character count display."""
        text = self.prompt_editor.toPlainText()
        char_count = len(text)
        self.char_count_label.setText(f"{char_count:,} characters")
        
        # Change color based on length
        if char_count > 2000:
            color = "#dc3545"  # Red for very long
        elif char_count > 1000:
            color = "#fd7e14"  # Orange for long
        else:
            color = "#6c757d"  # Gray for normal
        
        self.char_count_label.setStyleSheet(f"color: {color}; font-size: 12px;")
    
    def _preview_prompt(self):
        """Preview the current prompt."""
        prompt = self.prompt_editor.toPlainText().strip()
        if not prompt:
            QMessageBox.warning(self, "No Prompt", "Please enter a system prompt to preview.")
            return
        
        # Show preview dialog
        preview_dialog = QDialog(self)
        preview_dialog.setWindowTitle("System Prompt Preview")
        preview_dialog.setMinimumSize(500, 300)
        
        layout = QVBoxLayout(preview_dialog)
        
        # Preview text
        preview_text = QTextEdit()
        preview_text.setReadOnly(True)
        preview_text.setText(prompt)
        preview_text.setStyleSheet("""
            QTextEdit {
                border: 1px solid #dee2e6;
                border-radius: 4px;
                padding: 15px;
                background-color: #f8f9fa;
                font-family: 'Segoe UI', Arial, sans-serif;
                font-size: 14px;
            }
        """)
        layout.addWidget(preview_text)
        
        # Close button
        close_button = QPushButton("Close")
        close_button.clicked.connect(preview_dialog.accept)
        button_layout = QHBoxLayout()
        button_layout.addStretch()
        button_layout.addWidget(close_button)
        layout.addLayout(button_layout)
        
        preview_dialog.exec()
    
    def _reset_to_default(self):
        """Reset to default assistant prompt."""
        default_prompt = self.DEFAULT_PROMPTS["Assistant"]
        self.prompt_editor.setText(default_prompt)
        
        # Select the Assistant template
        for i in range(self.template_list.count()):
            item = self.template_list.item(i)
            if item.text() == "Assistant":
                self.template_list.setCurrentItem(item)
                break
        
        self.logger.info("Reset to default system prompt")
    
    def _apply_changes(self):
        """Apply the changes and close dialog."""
        prompt = self.prompt_editor.toPlainText().strip()
        
        if not prompt:
            QMessageBox.warning(self, "Empty Prompt", "System prompt cannot be empty.")
            return
        
        # Save to configuration
        self.config_manager.set_value("system_prompt", prompt)
        
        # Emit signal
        self.system_prompt_changed.emit(prompt)
        
        self.logger.info(f"Applied system prompt: {prompt[:50]}...")
        self.accept()
    
    def get_current_prompt(self) -> str:
        """Get the current prompt text."""
        return self.prompt_editor.toPlainText().strip()