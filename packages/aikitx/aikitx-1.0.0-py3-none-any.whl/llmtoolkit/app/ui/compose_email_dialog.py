"""
Compose Email Dialog

This module contains the ComposeEmailDialog class, which provides an interface
for composing new emails with AI assistance for draft generation.
"""

import logging
from typing import Optional, Dict, Any

from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QFormLayout, QLabel, 
    QLineEdit, QTextEdit, QPushButton, QGroupBox, QFrame,
    QProgressDialog, QMessageBox, QToolTip
)
from PySide6.QtCore import Qt, Signal, QTimer, QPropertyAnimation, QEasingCurve
from PySide6.QtGui import QFont, QKeySequence

from .mixins.theme_mixin import DialogThemeMixin


class ComposeEmailDialog(QDialog, DialogThemeMixin):
    """
    Email composition dialog with AI assistance.
    
    Features:
    - To field for recipient email address
    - Subject field for email subject
    - Message field for email body content
    - Send button for sending the email
    - Generate Draft with AI button for AI-powered content generation
    - Support for prefilling fields (useful for replies)
    """
    
    # Signals
    email_send_requested = Signal(dict)  # Emitted when send is requested
    draft_generation_requested = Signal(dict)  # Emitted when AI draft generation is requested
    
    def __init__(self, parent=None, prefill_data: Optional[Dict[str, str]] = None):
        """
        Initialize the compose email dialog.
        
        Args:
            parent: Parent widget
            prefill_data: Optional data to prefill fields (to, subject, body)
        """
        super().__init__(parent)
        
        self.logger = logging.getLogger("gguf_loader.ui.compose_email_dialog")
        self.prefill_data = prefill_data or {}
        
        # Set dialog properties
        self.setWindowTitle("✉️ Compose Email")
        self.setModal(True)
        self.setFixedSize(600, 500)
        
        # Initialize UI first
        self._init_ui()
        
        # Apply theme to dialog after UI is created
        self._apply_theme_to_dialog(parent)
        
        # Load prefill data if provided
        self._load_prefill_data()
        
        self.logger.info("ComposeEmailDialog initialized")
    
    def _init_ui(self):
        """Initialize the user interface."""
        layout = QVBoxLayout(self)
        layout.setSpacing(15)
        layout.setContentsMargins(20, 20, 20, 20)
        
        # Header
        header_label = QLabel("✉️ Compose New Email")
        header_font = QFont()
        header_font.setPointSize(16)
        header_font.setBold(True)
        header_label.setFont(header_font)
        layout.addWidget(header_label)
        
        # Description
        desc_label = QLabel("Compose a new email message. Use AI assistance to generate professional content.")
        desc_label.setWordWrap(True)
        layout.addWidget(desc_label)
        
        # Email composition form
        form_group = self._create_form_group()
        layout.addWidget(form_group)
        
        # Add spacer
        layout.addStretch()
        
        # Button layout
        self._create_button_layout(layout)
    
    def _create_form_group(self) -> QGroupBox:
        """
        Create the email composition form group.
        
        Returns:
            QGroupBox: Form group widget
        """
        group = QGroupBox("Email Details")
        
        layout = QFormLayout(group)
        layout.setSpacing(15)
        layout.setContentsMargins(15, 20, 15, 15)
        
        # To field
        self.to_edit = QLineEdit()
        self.to_edit.setPlaceholderText("recipient@example.com")
        layout.addRow("To:", self.to_edit)
        
        # Subject field
        self.subject_edit = QLineEdit()
        self.subject_edit.setPlaceholderText("Enter email subject")
        layout.addRow("Subject:", self.subject_edit)
        
        # Message field
        self.message_edit = QTextEdit()
        self.message_edit.setPlaceholderText("Type your message here...")
        self.message_edit.setMinimumHeight(200)
        layout.addRow("Message:", self.message_edit)
        
        return group
    
    def _create_button_layout(self, layout: QVBoxLayout):
        """
        Create the button layout with Send and AI generation buttons.
        
        Args:
            layout: Parent layout to add buttons to
        """
        button_layout = QHBoxLayout()
        button_layout.setSpacing(10)
        
        # Generate Draft with AI button - use centralized AI button styling
        self.generate_draft_button = self._create_ai_button("🧠 Generate Draft with AI")
        self.generate_draft_button.setMinimumWidth(160)
        self.generate_draft_button.clicked.connect(self._on_generate_draft_clicked)
        button_layout.addWidget(self.generate_draft_button)
        
        # Add spacer to push Send button to the right
        button_layout.addStretch()
        
        # Cancel button - use centralized cancel button styling
        cancel_button = self._create_cancel_button("Cancel")
        cancel_button.setMinimumWidth(80)
        cancel_button.clicked.connect(self.reject)
        button_layout.addWidget(cancel_button)
        
        # Send button - use centralized primary button styling
        self.send_button = self._create_primary_button("📤 Send")
        self.send_button.setDefault(True)
        self.send_button.setMinimumWidth(100)
        self.send_button.clicked.connect(self._on_send_clicked)
        button_layout.addWidget(self.send_button)
        
        layout.addLayout(button_layout)
        
        # Connect validation
        self._connect_validation()
    

    
    def _connect_validation(self):
        """Connect form validation to input fields."""
        # Connect text change events for validation
        self.to_edit.textChanged.connect(self._validate_form)
        self.subject_edit.textChanged.connect(self._validate_form)
        self.message_edit.textChanged.connect(self._validate_form)
        
        # Initial validation
        self._validate_form()
    
    def _validate_form(self):
        """Validate form fields and enable/disable send button."""
        # Check required fields
        to_text = self.to_edit.text().strip()
        subject_text = self.subject_edit.text().strip()
        message_text = self.message_edit.toPlainText().strip()
        
        # Basic validation
        is_valid = (
            len(to_text) > 0 and
            "@" in to_text and
            "." in to_text.split("@")[1] if "@" in to_text else False and
            len(subject_text) > 0 and
            len(message_text) > 0
        )
        
        self.send_button.setEnabled(is_valid)
        
        # Update field styling based on validation
        self._update_field_styling()
    
    def _update_field_styling(self):
        """Update field styling based on validation state."""
        # Get theme colors for error styling
        theme_colors = self._get_theme_colors()
        error_color = theme_colors.get('error', '#dc3545')
        
        # Get base input field styles to maintain theme consistency
        base_input_styles = self._get_input_field_styles()
        
        # To field validation - only add error styling if invalid
        to_text = self.to_edit.text().strip()
        if not to_text or "@" not in to_text or "." not in to_text.split("@")[1] if "@" in to_text else True:
            # Apply error styling with theme-aware colors
            self.to_edit.setProperty("validationError", True)
            self.to_edit.style().unpolish(self.to_edit)
            self.to_edit.style().polish(self.to_edit)
        else:
            # Clear error state
            self.to_edit.setProperty("validationError", False)
            self.to_edit.style().unpolish(self.to_edit)
            self.to_edit.style().polish(self.to_edit)
        
        # Subject field validation
        if not self.subject_edit.text().strip():
            # Apply error styling with theme-aware colors
            self.subject_edit.setProperty("validationError", True)
            self.subject_edit.style().unpolish(self.subject_edit)
            self.subject_edit.style().polish(self.subject_edit)
        else:
            # Clear error state
            self.subject_edit.setProperty("validationError", False)
            self.subject_edit.style().unpolish(self.subject_edit)
            self.subject_edit.style().polish(self.subject_edit)
        
        # Message field validation
        if not self.message_edit.toPlainText().strip():
            # Apply error styling with theme-aware colors
            self.message_edit.setProperty("validationError", True)
            self.message_edit.style().unpolish(self.message_edit)
            self.message_edit.style().polish(self.message_edit)
        else:
            # Clear error state
            self.message_edit.setProperty("validationError", False)
            self.message_edit.style().unpolish(self.message_edit)
            self.message_edit.style().polish(self.message_edit)
    
    def _load_prefill_data(self):
        """Load prefill data into form fields."""
        if not self.prefill_data:
            return
        
        # Load prefilled data
        self.to_edit.setText(self.prefill_data.get("to", ""))
        self.subject_edit.setText(self.prefill_data.get("subject", ""))
        self.message_edit.setPlainText(self.prefill_data.get("body", ""))
        
        self.logger.info("Prefill data loaded into dialog")
    
    def _on_generate_draft_clicked(self):
        """Handle generate draft with AI button click with progress indicator."""
        from PySide6.QtWidgets import QProgressDialog, QMessageBox
        from PySide6.QtCore import QTimer
        
        # Validate required fields for AI generation
        to_text = self.to_edit.text().strip()
        subject_text = self.subject_edit.text().strip()
        
        if not to_text and not subject_text:
            QMessageBox.warning(
                self,
                "AI Generation",
                "Please provide at least a recipient or subject to help generate better content."
            )
            return
        
        # Collect current form data for AI generation
        draft_data = {
            "to": to_text,
            "subject": subject_text,
            "current_message": self.message_edit.toPlainText().strip()
        }
        
        # Show progress dialog for AI generation
        self.ai_progress = QProgressDialog("Generating AI draft...", "Cancel", 0, 100, self)
        self.ai_progress.setWindowModality(Qt.WindowModal)
        self.ai_progress.setMinimumDuration(0)
        self.ai_progress.setValue(0)
        self.ai_progress.show()
        
        # Disable the button temporarily to prevent multiple clicks
        self.generate_draft_button.setEnabled(False)
        self.generate_draft_button.setText("🧠 Generating...")
        
        # Create a timer to simulate AI generation progress
        self.ai_timer = QTimer()
        self.ai_progress_value = 0
        
        def update_ai_progress():
            self.ai_progress_value += 15
            self.ai_progress.setValue(self.ai_progress_value)
            
            # Update progress message based on stage
            if self.ai_progress_value <= 30:
                self.ai_progress.setLabelText("Analyzing context...")
            elif self.ai_progress_value <= 60:
                self.ai_progress.setLabelText("Generating content...")
            elif self.ai_progress_value <= 90:
                self.ai_progress.setLabelText("Refining draft...")
            else:
                self.ai_progress.setLabelText("Finalizing...")
            
            if self.ai_progress_value >= 100:
                self.ai_timer.stop()
                self.ai_progress.close()
                self._complete_ai_generation(draft_data)
        
        self.ai_timer.timeout.connect(update_ai_progress)
        self.ai_timer.start(200)  # Update every 200ms for smoother progress
        
        # Handle cancel button
        def on_ai_cancel():
            self.ai_timer.stop()
            self._reset_generate_button()
            self.logger.info("AI draft generation cancelled by user")
        
        self.ai_progress.canceled.connect(on_ai_cancel)
        
        self.logger.info("AI draft generation requested with progress indicator")
    
    def _complete_ai_generation(self, draft_data: dict):
        """Complete the AI generation process."""
        from PySide6.QtWidgets import QMessageBox
        
        try:
            # Emit signal for AI draft generation
            self.draft_generation_requested.emit(draft_data)
            
            # Note: The actual content setting will be handled by the parent
            # through the set_generated_content method
            
        except Exception as e:
            # Show error message
            QMessageBox.critical(
                self,
                "AI Generation Failed",
                f"Failed to generate AI draft:\n\n{str(e)}\n\nPlease try again or compose manually."
            )
            
            self.logger.error(f"Error in AI generation: {e}")
            self._reset_generate_button()
    
    def _reset_generate_button(self):
        """Reset the generate draft button to its original state."""
        self.generate_draft_button.setEnabled(True)
        self.generate_draft_button.setText("🧠 Generate Draft with AI")
    
    def _on_send_clicked(self):
        """Handle send button click."""
        if not self.send_button.isEnabled():
            return
        
        # Collect form data
        email_data = {
            "to": self.to_edit.text().strip(),
            "subject": self.subject_edit.text().strip(),
            "body": self.message_edit.toPlainText().strip()
        }
        
        # Emit signal for email sending
        self.email_send_requested.emit(email_data)
        
        self.logger.info(f"Email send requested to: {email_data['to']}")
        
        # Accept dialog
        self.accept()
    
    def prefill_reply_data(self, to: str, subject: str, body: str):
        """
        Prefill dialog with reply data.
        
        Args:
            to: Recipient email address
            subject: Email subject (typically with "Re:" prefix)
            body: Email body content
        """
        self.to_edit.setText(to)
        self.subject_edit.setText(subject)
        self.message_edit.setPlainText(body)
        
        self.logger.info(f"Reply data prefilled for: {to}")
    
    def set_generated_content(self, content: str):
        """
        Set AI-generated content in the message field.
        
        Args:
            content: Generated email content
        """
        from PySide6.QtWidgets import QMessageBox
        
        if content and content.strip():
            self.message_edit.setPlainText(content)
            self.logger.info("AI-generated content set in message field")
            
            # Show success notification
            QMessageBox.information(
                self,
                "AI Draft Generated",
                "AI draft has been generated successfully!\n\nYou can review and edit the content before sending."
            )
        else:
            # Show warning if content is empty
            QMessageBox.warning(
                self,
                "AI Generation",
                "AI generation completed but no content was generated.\n\nPlease try again with different parameters or compose manually."
            )
            self.logger.warning("AI generation returned empty content")
        
        # Reset the generate draft button
        self._reset_generate_button()
    
    def get_email_data(self) -> Dict[str, str]:
        """
        Get current email data from form fields.
        
        Returns:
            Dict[str, str]: Current email data
        """
        return {
            "to": self.to_edit.text().strip(),
            "subject": self.subject_edit.text().strip(),
            "body": self.message_edit.toPlainText().strip()
        }    

    def keyPressEvent(self, event):
        """Handle keyboard shortcuts for improved UX."""
        from PySide6.QtGui import QKeySequence
        from PySide6.QtCore import Qt
        
        # Ctrl+Enter to send email
        if event.key() == Qt.Key_Return and event.modifiers() == Qt.ControlModifier:
            if self.send_button.isEnabled():
                self._on_send_clicked()
            event.accept()
            return
        
        # Ctrl+G to generate AI draft
        if event.key() == Qt.Key_G and event.modifiers() == Qt.ControlModifier:
            if self.generate_draft_button.isEnabled():
                self._on_generate_draft_clicked()
            event.accept()
            return
        
        # Ctrl+S to save draft (placeholder for future implementation)
        if event.matches(QKeySequence.Save):
            self._save_draft()
            event.accept()
            return
        
        # F1 for help
        if event.key() == Qt.Key_F1:
            self._show_compose_help()
            event.accept()
            return
        
        # Escape to cancel
        if event.key() == Qt.Key_Escape:
            self.reject()
            event.accept()
            return
        
        # Call parent implementation
        super().keyPressEvent(event)
    
    def _save_draft(self):
        """Save current email as draft (placeholder for future implementation)."""
        from PySide6.QtWidgets import QMessageBox
        
        # For now, just show a message that this feature is coming soon
        QMessageBox.information(
            self,
            "Save Draft",
            "Draft saving feature is coming soon!\n\n"
            "For now, your content is preserved while the dialog is open."
        )
    
    def _show_compose_help(self):
        """Show compose email help dialog."""
        from PySide6.QtWidgets import QMessageBox
        
        help_text = """
        ✉️ Compose Email Help
        
        Email Composition Tips:
        • Fill in recipient, subject, and message
        • Use AI assistance for professional content
        • Review generated content before sending
        
        AI Draft Generation:
        • Provide recipient and/or subject for better results
        • AI will generate professional email content
        • You can edit the generated content
        
        Keyboard Shortcuts:
        • Ctrl+Enter: Send email
        • Ctrl+G: Generate AI draft
        • Ctrl+S: Save draft (coming soon)
        • F1: Show this help
        • Escape: Cancel
        
        Email Validation:
        • Recipient must be a valid email address
        • Subject and message are required
        • Fields with red borders need attention
        
        Tips for Better Emails:
        • Use clear, descriptive subjects
        • Keep messages concise and professional
        • Proofread before sending
        • Use AI assistance for formal communications
        """
        
        QMessageBox.information(self, "Compose Email Help", help_text)
    
    def showEvent(self, event):
        """Handle dialog show event to set up tooltips and initial focus."""
        super().showEvent(event)
        
        # Set up enhanced tooltips
        self._setup_enhanced_tooltips()
        
        # Set initial focus to first empty field
        self._set_initial_focus()
        
        # Add visual feedback for required fields
        self._highlight_required_fields()
    
    def _setup_enhanced_tooltips(self):
        """Set up enhanced tooltips for better user guidance."""
        # To field tooltip
        self.to_edit.setToolTip(
            "Enter recipient's email address\n"
            "Example: user@example.com\n"
            "Multiple recipients: separate with commas"
        )
        
        # Subject field tooltip
        self.subject_edit.setToolTip(
            "Enter email subject line\n"
            "Keep it clear and descriptive\n"
            "Example: Meeting Request - Project Update"
        )
        
        # Message field tooltip
        self.message_edit.setToolTip(
            "Enter your email message\n"
            "Use AI assistance for professional content\n"
            "Tip: Provide context for better AI generation"
        )
        
        # Generate draft button tooltip
        self.generate_draft_button.setToolTip(
            "Generate professional email content using AI\n"
            "Keyboard shortcut: Ctrl+G\n"
            "Tip: Fill in recipient and subject for better results"
        )
        
        # Send button tooltip
        self.send_button.setToolTip(
            "Send the email\n"
            "Keyboard shortcut: Ctrl+Enter\n"
            "All fields must be filled and valid"
        )
    
    def _set_initial_focus(self):
        """Set initial focus to the first empty required field."""
        if not self.to_edit.text().strip():
            self.to_edit.setFocus()
        elif not self.subject_edit.text().strip():
            self.subject_edit.setFocus()
        elif not self.message_edit.toPlainText().strip():
            self.message_edit.setFocus()
        else:
            self.send_button.setFocus()
    
    def _highlight_required_fields(self):
        """Add subtle visual indicators for required fields."""
        # Add asterisk to required field labels (if not already present)
        try:
            # This is a visual enhancement - if it fails, it's not critical
            form_layout = self.findChild(QFormLayout)
            if form_layout:
                # Update labels to show required fields
                for i in range(form_layout.rowCount()):
                    label_item = form_layout.itemAt(i, QFormLayout.LabelRole)
                    if label_item and label_item.widget():
                        label = label_item.widget()
                        if isinstance(label, QLabel):
                            text = label.text()
                            if text in ["To:", "Subject:", "Message:"] and not text.endswith("*"):
                                label.setText(text.rstrip(":") + "*:")
        except Exception as e:
            # Visual enhancement failure is not critical
            self.logger.debug(f"Failed to highlight required fields: {e}")
    
    def _animate_send_success(self):
        """Show success animation when email is sent."""
        try:
            # Create a brief success animation using theme colors
            self.success_animation = QPropertyAnimation(self.send_button, b"styleSheet")
            self.success_animation.setDuration(1000)  # 1 second
            
            # Get theme colors for success animation
            theme_colors = self._get_theme_colors()
            success_bg = theme_colors.get('success', '#28a745')
            success_border = theme_colors.get('success_border', '#20c997')
            
            # Define animation keyframes
            original_style = self.send_button.styleSheet()
            
            # Create simple success style for animation
            success_style = f"""
                QPushButton {{
                    background-color: {success_bg};
                    color: white;
                    border: 2px solid {success_border};
                    border-radius: 6px;
                    padding: 10px 20px;
                    font-weight: bold;
                    font-size: 13px;
                    min-width: 100px;
                }}
            """
            
            self.success_animation.setKeyValueAt(0, original_style)
            self.success_animation.setKeyValueAt(0.5, success_style)
            self.success_animation.setKeyValueAt(1, original_style)
            
            self.success_animation.setEasingCurve(QEasingCurve.InOutQuad)
            self.success_animation.start()
            
        except Exception as e:
            # Animation is optional, don't fail if it doesn't work
            self.logger.debug(f"Send success animation failed: {e}")
    
    def _show_send_confirmation(self):
        """Show confirmation dialog before sending email."""
        from PySide6.QtWidgets import QMessageBox
        
        email_data = self.get_email_data()
        
        # Create confirmation message
        confirmation_msg = f"""
        📤 Confirm Email Send
        
        To: {email_data['to']}
        Subject: {email_data['subject']}
        
        Message Preview:
        {email_data['body'][:100]}{'...' if len(email_data['body']) > 100 else ''}
        
        Are you sure you want to send this email?
        """
        
        reply = QMessageBox.question(
            self,
            "Confirm Send",
            confirmation_msg,
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.Yes
        )
        
        return reply == QMessageBox.Yes
    
    def _on_send_clicked_with_confirmation(self):
        """Handle send button click with confirmation dialog."""
        if not self.send_button.isEnabled():
            return
        
        # Show confirmation dialog
        if self._show_send_confirmation():
            # Show success animation
            self._animate_send_success()
            
            # Proceed with sending
            self._on_send_clicked()
    
    def _enhance_ai_generation_feedback(self, draft_data: dict):
        """Provide enhanced feedback during AI generation."""
        # This method can be called to provide more detailed feedback
        # about the AI generation process
        
        context_info = []
        
        if draft_data.get("to"):
            context_info.append(f"Recipient: {draft_data['to']}")
        
        if draft_data.get("subject"):
            context_info.append(f"Subject: {draft_data['subject']}")
        
        if draft_data.get("current_message"):
            context_info.append("Existing content will be enhanced")
        
        if context_info:
            context_text = "\n".join(context_info)
            self.logger.info(f"AI generation context: {context_text}")
    
    def set_generated_content_with_animation(self, content: str):
        """Set AI-generated content with visual feedback animation."""
        if content and content.strip():
            # Set the content
            self.message_edit.setPlainText(content)
            
            # Add visual feedback animation using theme colors
            try:
                self.content_animation = QPropertyAnimation(self.message_edit, b"styleSheet")
                self.content_animation.setDuration(1500)  # 1.5 seconds
                
                # Get theme colors for success animation
                theme_colors = self._get_theme_colors()
                success_bg = theme_colors.get('success_bg', '#e8f5e8')
                success_border = theme_colors.get('success', '#28a745')
                
                original_style = self.message_edit.styleSheet()
                
                # Create simple highlight style for animation
                highlight_style = f"""
                    QTextEdit {{
                        background-color: {success_bg};
                        border: 2px solid {success_border};
                        border-radius: 6px;
                        padding: 8px 12px;
                        font-size: 13px;
                    }}
                """
                
                self.content_animation.setKeyValueAt(0, original_style)
                self.content_animation.setKeyValueAt(0.3, highlight_style)
                self.content_animation.setKeyValueAt(1, original_style)
                
                self.content_animation.setEasingCurve(QEasingCurve.InOutQuad)
                self.content_animation.start()
                
            except Exception as e:
                self.logger.debug(f"Content animation failed: {e}")
            
            # Show success notification
            QMessageBox.information(
                self,
                "[OK] AI Draft Generated",
                "AI draft has been generated successfully!\n\n"
                "✨ The content has been added to your message.\n"
                "📝 You can review and edit it before sending.\n\n"
                "💡 Tip: Use Ctrl+Enter to send when ready."
            )
            
            self.logger.info("AI-generated content set with animation")
            
        else:
            # Show warning if content is empty
            QMessageBox.warning(
                self,
                "[WARN] AI Generation",
                "AI generation completed but no content was generated.\n\n"
                "💡 Try providing more context:\n"
                "• Add a specific subject line\n"
                "• Include recipient information\n"
                "• Add some initial message content\n\n"
                "🔄 Please try again or compose manually."
            )
            self.logger.warning("AI generation returned empty content")
        
        # Reset the generate draft button
        self._reset_generate_button()
    
    def closeEvent(self, event):
        """Handle dialog close event with unsaved changes warning."""
        # Check if there's unsaved content
        has_content = (
            bool(self.to_edit.text().strip()) or
            bool(self.subject_edit.text().strip()) or
            bool(self.message_edit.toPlainText().strip())
        )
        
        if has_content:
            from PySide6.QtWidgets import QMessageBox
            
            reply = QMessageBox.question(
                self,
                "Unsaved Changes",
                "You have unsaved email content.\n\n"
                "Are you sure you want to close without sending?",
                QMessageBox.Yes | QMessageBox.No,
                QMessageBox.No
            )
            
            if reply == QMessageBox.No:
                event.ignore()
                return
        
        # Accept the close event
        event.accept()
        super().closeEvent(event)