"""
Email Automation Tab

This module contains the EmailAutomationTab class, which provides a clean interface
for email automation with AI-powered composition and reply generation.
"""

import logging
import time
from typing import Optional, Dict, Any

from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, 
    QSplitter, QListWidget, QTextBrowser, QFrame, QListWidgetItem, QDialog
)
from PySide6.QtCore import Qt, Signal, Slot, QSize, QPropertyAnimation, QTimer
from PySide6.QtGui import QFont, QPalette, QTextOption

from llmtoolkit.app.core.event_bus import EventBus
from llmtoolkit.app.ui.compose_email_dialog import ComposeEmailDialog
from llmtoolkit.app.ui.email_settings_dialog import EmailSettingsDialog
from llmtoolkit.app.ui.theme_manager import ThemeManager


class EmailPreviewWidget(QWidget):
    """Custom widget for displaying email preview in list items with enhanced responsive design."""
    
    def __init__(self, email_data: dict, theme_manager: ThemeManager = None, parent=None):
        super().__init__(parent)
        self.email_data = email_data
        self.theme_manager = theme_manager
        self._init_ui()
    
    def _init_ui(self):
        """Initialize the email preview widget UI with enhanced responsive design."""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(10, 8, 10, 8)
        layout.setSpacing(4)
        
        # Top row: unread indicator and timestamp with improved spacing
        top_row = QHBoxLayout()
        top_row.setContentsMargins(0, 0, 0, 0)
        top_row.setSpacing(8)
        
        # Unread indicator with fixed size
        self.unread_indicator = QLabel("●" if self.email_data.get('unread', False) else "[NONE]")
        self.unread_indicator.setFixedSize(16, 16)
        self.unread_indicator.setAlignment(Qt.AlignCenter)
        # Let theme manager handle unread indicator styling
        top_row.addWidget(self.unread_indicator)
        
        # Spacer to push timestamp to the right
        top_row.addStretch()
        
        # Timestamp with proper truncation
        timestamp_text = self.email_data.get('timestamp', '')
        if len(timestamp_text) > 15:  # Better truncation for timestamps
            timestamp_text = timestamp_text[:12] + "..."
        self.timestamp_label = QLabel(timestamp_text)
        self.timestamp_label.setAlignment(Qt.AlignRight)
        # Let theme manager handle timestamp styling
        self.timestamp_label.setMinimumWidth(60)  # Ensure consistent width
        top_row.addWidget(self.timestamp_label)
        
        layout.addLayout(top_row)
        
        # Subject line with enhanced responsive text handling
        subject_text = self.email_data.get('subject', 'No Subject')
        self.subject_label = QLabel()
        
        # Implement proper text truncation for long subjects
        if len(subject_text) > 50:
            truncated_subject = subject_text[:47] + "..."
        else:
            truncated_subject = subject_text
            
        self.subject_label.setText(truncated_subject)
        self.subject_label.setToolTip(subject_text)  # Show full text on hover
        
        subject_font = QFont()
        subject_font.setBold(self.email_data.get('unread', False))
        subject_font.setPointSize(12)
        self.subject_label.setFont(subject_font)
        
        # Let theme manager handle subject styling
        self.subject_label.setWordWrap(False)  # Disable word wrap for better truncation
        self.subject_label.setTextInteractionFlags(Qt.TextSelectableByMouse)
        layout.addWidget(self.subject_label)
        
        # Sender with enhanced responsive handling and proper truncation
        sender_text = self.email_data.get('sender', 'Unknown')
        sender_name = sender_text.split('<')[0].strip() if '<' in sender_text else sender_text
        
        # Better truncation for sender names
        if len(sender_name) > 35:
            truncated_sender = sender_name[:32] + "..."
        else:
            truncated_sender = sender_name
            
        self.sender_label = QLabel(truncated_sender)
        self.sender_label.setToolTip(sender_name)  # Show full name on hover
        
        # Let theme manager handle sender styling
        self.sender_label.setWordWrap(False)  # Disable word wrap for better truncation
        layout.addWidget(self.sender_label)
        
        # Remove preview text as per task requirements - show only title and sender
        # The preview text widget is completely removed
        
        # Gmail-specific metadata (labels, thread info) - kept but made more compact
        if self.email_data.get('source') == 'gmail':
            self._add_gmail_metadata(layout)
        
        # Set fixed height for consistent list appearance and prevent overlapping
        fixed_height = 75 if self.email_data.get('source') == 'gmail' else 65
        self.setFixedHeight(fixed_height)
        
        # Apply initial theme
        self.apply_theme()
    
    def resizeEvent(self, event):
        """Handle resize events to maintain responsive layout."""
        super().resizeEvent(event)
        
        # Update text truncation based on available width
        self._update_text_truncation()
    
    def _update_text_truncation(self):
        """Update text truncation based on current widget width."""
        try:
            available_width = self.width() - 40  # Account for margins and padding
            
            # Calculate character limits based on available width
            char_width = 8  # Approximate character width in pixels
            max_subject_chars = max(20, (available_width - 100) // char_width)  # Reserve space for timestamp
            max_sender_chars = max(15, (available_width - 50) // char_width)
            
            # Update subject truncation
            original_subject = self.email_data.get('subject', 'No Subject')
            if len(original_subject) > max_subject_chars:
                truncated_subject = original_subject[:max_subject_chars-3] + "..."
                self.subject_label.setText(truncated_subject)
            else:
                self.subject_label.setText(original_subject)
            
            # Update sender truncation
            original_sender = self.email_data.get('sender', 'Unknown')
            sender_name = original_sender.split('<')[0].strip() if '<' in original_sender else original_sender
            if len(sender_name) > max_sender_chars:
                truncated_sender = sender_name[:max_sender_chars-3] + "..."
                self.sender_label.setText(truncated_sender)
            else:
                self.sender_label.setText(sender_name)
                
        except Exception as e:
            # Silently handle any truncation errors
            pass
    
    def apply_theme(self):
        """Apply theme-based styling to the preview widget."""
        if not self.theme_manager:
            # Fallback to default light theme colors
            primary_color = "#007bff"
            text_color = "#212529"
            text_secondary = "#6c757d"
        else:
            primary_color = self.theme_manager.get_color("primary")
            text_color = self.theme_manager.get_color("text")
            text_secondary = self.theme_manager.get_color("text_secondary")
        
        # Let theme manager handle all component styling consistently
    
    def _add_gmail_metadata(self, layout):
        """Add compact Gmail-specific metadata display (labels, thread info)."""
        try:
            # Create compact metadata row
            metadata_row = QHBoxLayout()
            metadata_row.setContentsMargins(0, 2, 0, 0)
            metadata_row.setSpacing(6)
            
            # Gmail labels - more compact display
            labels = self.email_data.get('labels', [])
            if labels:
                # Filter out system labels and show only user labels
                user_labels = [label for label in labels if not label.startswith('CATEGORY_') and label not in ['INBOX', 'UNREAD', 'IMPORTANT']]
                
                if user_labels:
                    # Show only first label to save space
                    labels_text = f"🏷️ {user_labels[0]}"
                    if len(user_labels) > 1:
                        labels_text += f" +{len(user_labels) - 1}"
                    
                    labels_label = QLabel(labels_text)
                    # Let theme manager handle labels styling
                    labels_label.setMaximumWidth(80)  # Prevent labels from taking too much space
                    metadata_row.addWidget(labels_label)
            
            # Thread info - more compact
            thread_id = self.email_data.get('thread_id', '')
            if thread_id:
                thread_label = QLabel("🧵")
                # Let theme manager handle thread label styling
                thread_label.setToolTip("Part of email thread")
                thread_label.setFixedWidth(16)
                metadata_row.addWidget(thread_label)
            
            # Gmail source indicator - more compact
            gmail_indicator = QLabel("📧")
            # Let theme manager handle Gmail indicator styling
            gmail_indicator.setToolTip("Gmail source")
            gmail_indicator.setFixedWidth(16)
            metadata_row.addWidget(gmail_indicator)
            
            # Add spacer to push items to the left
            metadata_row.addStretch()
            
            layout.addLayout(metadata_row)
            
        except Exception as e:
            # Silently handle metadata errors to avoid breaking the preview
            pass


class EmailAutomationTab(QWidget):
    """
    Clean interface for email automation with AI assistance.
    
    Features:
    - Split panel layout with email preview list (25%) and details (75%)
    - Email preview list for browsing emails
    - Email details display with subject, sender, and body
    - AI-powered reply generation
    - Compose email functionality
    """
    
    # Signals
    email_selected = Signal(dict)  # Emitted when an email is selected
    reply_requested = Signal(dict)  # Emitted when reply generation is requested
    compose_requested = Signal()  # Emitted when compose is requested
    
    def __init__(self, event_bus: EventBus, email_service, theme_manager: ThemeManager = None, parent=None):
        """
        Initialize the email automation tab.
        
        Args:
            event_bus: Application event bus
            email_service: EmailService instance for email operations
            theme_manager: Theme manager for consistent styling
            parent: Parent widget
        """
        super().__init__(parent)
        
        self.logger = logging.getLogger("gguf_loader.ui.email_automation_tab")
        self.event_bus = event_bus
        self.email_service = email_service
        self.theme_manager = theme_manager
        self.selected_email = None
        
        # Initialize UI
        self._init_ui()
        
        # Connect event handlers
        self._connect_events()
        
        # Subscribe to email service events for user feedback
        self._subscribe_to_email_events()
        
        # Subscribe to theme changes
        if self.theme_manager:
            self.theme_manager.theme_changed.connect(self._on_theme_changed)
        
        # Apply initial theme
        self._apply_theme()
        
        self.logger.info("EmailAutomationTab initialized")
    

    
    def resizeEvent(self, event):
        """Handle resize events to maintain responsive layout and prevent overlapping."""
        super().resizeEvent(event)
        
        # Update splitter proportions based on new size
        if hasattr(self, 'splitter') and self.splitter:
            total_width = event.size().width()
            if total_width > 800:
                # For larger windows, maintain 25%/75% ratio
                left_width = int(total_width * 0.25)
                right_width = total_width - left_width
                self.splitter.setSizes([left_width, right_width])
            else:
                # For smaller windows, use fixed minimum sizes
                self.splitter.setSizes([250, max(400, total_width - 250)])
        
        # Update email preview widgets to handle text truncation
        self._update_email_preview_truncation()
    
    def _update_email_preview_truncation(self):
        """Update text truncation in all email preview widgets based on current size."""
        if not hasattr(self, 'email_list') or not self.email_list:
            return
            
        try:
            # Update truncation for all email preview widgets
            for i in range(self.email_list.count()):
                item = self.email_list.item(i)
                if item:
                    preview_widget = self.email_list.itemWidget(item)
                    if isinstance(preview_widget, EmailPreviewWidget):
                        preview_widget._update_text_truncation()
        except Exception as e:
            # Silently handle any errors during truncation update
            pass
    
    def _init_ui(self):
        """Initialize UI components with clean, split-panel design."""
        # Create main layout
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(10, 10, 10, 10)
        main_layout.setSpacing(10)
        
        # Create splitter for responsive 25%/75% layout
        self.splitter = QSplitter(Qt.Horizontal)
        self.splitter.setChildrenCollapsible(False)  # Prevent panels from collapsing
        
        # Create left panel (25% - email preview list)
        left_panel = self._create_left_panel()
        self.splitter.addWidget(left_panel)
        
        # Create right panel (75% - email details)
        right_panel = self._create_right_panel()
        self.splitter.addWidget(right_panel)
        
        # Set splitter proportions (25% / 75%) with minimum sizes
        self.splitter.setSizes([300, 900])  # Initial sizes
        self.splitter.setStretchFactor(0, 0)  # Left panel doesn't stretch
        self.splitter.setStretchFactor(1, 1)  # Right panel stretches
        
        # Set minimum sizes to prevent overlapping
        left_panel.setMinimumWidth(250)
        right_panel.setMinimumWidth(400)
        
        # Maximize space for email content
        main_layout.addWidget(self.splitter, 1)
    
    def _create_left_panel(self) -> QWidget:
        """
        Create the left panel with email preview list.
        
        Returns:
            QWidget: Left panel widget
        """
        panel = QFrame()
        panel.setFrameStyle(QFrame.StyledPanel)
        panel.setObjectName("left_panel")  # For theme styling
        
        layout = QVBoxLayout(panel)
        layout.setContentsMargins(5, 5, 5, 5)  # Reduced margins to maximize space
        layout.setSpacing(5)  # Reduced spacing
        
        # Create compact title row with refresh button
        title_row = QHBoxLayout()
        title_row.setContentsMargins(0, 0, 0, 0)
        
        # Add title
        title_label = QLabel("📧 Email Preview")
        title_font = QFont()
        title_font.setBold(True)
        title_font.setPointSize(11)  # Slightly smaller font
        title_label.setFont(title_font)
        title_label.setObjectName("email_preview_title")  # For theme styling
        title_row.addWidget(title_label)
        
        # Add spacer
        title_row.addStretch()
        
        # Add refresh button with text label that will definitely be visible
        self.refresh_button = QPushButton("↻")
        self.refresh_button.setObjectName("refresh_button")
        self.refresh_button.setToolTip("Refresh Gmail emails")
        self.refresh_button.setFixedSize(32, 32)
        self.refresh_button.setStyleSheet("QPushButton { background-color: #555; color: white; border: 1px solid #777; border-radius: 4px; font-size: 18px; font-weight: bold; } QPushButton:hover { background-color: #666; }")
        self.refresh_button.clicked.connect(self._refresh_gmail_emails)
        title_row.addWidget(self.refresh_button)
        
        # Add settings button with text label that will definitely be visible
        self.settings_button = QPushButton("⚙")
        self.settings_button.setObjectName("settings_button")
        self.settings_button.setToolTip("Email Settings")
        self.settings_button.setFixedSize(32, 32)
        self.settings_button.setStyleSheet("QPushButton { background-color: #555; color: white; border: 1px solid #777; border-radius: 4px; font-size: 18px; font-weight: bold; } QPushButton:hover { background-color: #666; }")
        self.settings_button.clicked.connect(self.open_email_settings)
        title_row.addWidget(self.settings_button)
        
        layout.addLayout(title_row)
        
        # Create email list widget with enhanced responsive design
        self.email_list = QListWidget()
        self.email_list.setObjectName("email_list")  # For theme styling
        
        # Configure list for better responsive behavior
        self.email_list.setVerticalScrollMode(QListWidget.ScrollPerPixel)
        self.email_list.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.email_list.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        self.email_list.setResizeMode(QListWidget.Adjust)
        self.email_list.setSpacing(2)  # Add consistent spacing between items
        self.email_list.setUniformItemSizes(True)  # Ensure uniform item sizes
        
        # Set minimum width to prevent excessive compression
        self.email_list.setMinimumWidth(200)
        
        # Add placeholder email items for testing
        self._add_placeholder_emails()
        
        layout.addWidget(self.email_list, 1)  # Give it stretch factor to maximize space
        
        return panel
    
    def _create_right_panel(self) -> QWidget:
        """
        Create the right panel with responsive email details display.
        
        Returns:
            QWidget: Right panel widget
        """
        panel = QFrame()
        panel.setFrameStyle(QFrame.StyledPanel)
        panel.setObjectName("right_panel")  # For theme styling
        
        layout = QVBoxLayout(panel)
        layout.setContentsMargins(15, 15, 15, 15)
        layout.setSpacing(15)
        
        # Email subject (bold, responsive) - let theme manager handle styling
        self.subject_label = QLabel("Select an email to view details")
        subject_font = QFont()
        subject_font.setBold(True)
        subject_font.setPointSize(14)
        self.subject_label.setFont(subject_font)
        self.subject_label.setObjectName("email_subject")  # For theme styling
        self.subject_label.setWordWrap(True)
        self.subject_label.setTextInteractionFlags(Qt.TextSelectableByMouse)
        layout.addWidget(self.subject_label)
        
        # Email sender (responsive) - let theme manager handle styling
        self.sender_label = QLabel("")
        self.sender_label.setObjectName("email_sender")  # For theme styling
        self.sender_label.setWordWrap(True)
        self.sender_label.setTextInteractionFlags(Qt.TextSelectableByMouse)
        layout.addWidget(self.sender_label)
        
        # Email body with responsive design - let theme manager handle all styling
        self.body_browser = QTextBrowser()
        self.body_browser.setObjectName("email_body")  # For theme styling
        self.body_browser.setPlaceholderText("Email content will appear here...")
        
        # Configure responsive text display
        self.body_browser.setLineWrapMode(QTextBrowser.WidgetWidth)
        self.body_browser.setWordWrapMode(QTextOption.WrapAtWordBoundaryOrAnywhere)
        self.body_browser.setOpenExternalLinks(True)
        
        layout.addWidget(self.body_browser)
        
        # Action buttons layout
        button_layout = QHBoxLayout()
        button_layout.setSpacing(10)
        
        # Generate reply button
        self.reply_button = QPushButton("🧠 Generate AI Reply")
        self.reply_button.setObjectName("reply_button")  # For theme styling
        self.reply_button.setEnabled(False)  # Disabled until email is selected
        self.reply_button.setMinimumHeight(35)
        button_layout.addWidget(self.reply_button)
        
        # Add compose button (moved from top bar) - let theme manager handle styling
        self.compose_button = QPushButton("✉️ Compose New Email")
        self.compose_button.setObjectName("compose_button")
        self.compose_button.setMinimumHeight(45)
        self.compose_button.setMinimumWidth(180)
        self.compose_button.setProperty("buttonType", "primary")  # For theme styling
        button_layout.addWidget(self.compose_button)
        
        # Add stretch to push buttons to the left
        button_layout.addStretch()
        
        layout.addLayout(button_layout)
        
        return panel
    
    # Top action bar removed as requested
    
    def _add_placeholder_emails(self):
        """Add email items - use real Gmail emails when OAuth is configured, otherwise use placeholders."""
        try:
            # Get OAuth status information
            oauth_status = self._get_oauth_status_info()
            
            if oauth_status['authenticated']:
                self.logger.info(f"Gmail OAuth authenticated ({oauth_status['user_email']}), fetching real emails")
                try:
                    self._load_gmail_emails()
                except Exception as e:
                    self.logger.warning(f"Failed to load Gmail emails, using placeholder: {e}")
                    self._load_placeholder_emails(oauth_status)
            else:
                self.logger.info(f"Gmail OAuth not authenticated: {oauth_status['status_message']}")
                self._load_placeholder_emails(oauth_status)
        except Exception as e:
            self.logger.error(f"Error loading emails: {e}")
            # Fallback to placeholder emails on error
            self._load_placeholder_emails({'error': str(e)})
    
    def _is_gmail_oauth_configured(self) -> bool:
        """
        Check if Gmail OAuth is configured and authenticated.
        
        Returns:
            True if Gmail OAuth is available and authenticated
        """
        try:
            if not self.email_service:
                self.logger.debug("No email service available")
                return False
            
            # Get current email configuration
            email_config = self.email_service.get_email_config()
            auth_method = email_config.get('auth_method', 'smtp')
            
            self.logger.debug(f"Current auth method: {auth_method}")
            
            # Check if Gmail OAuth is selected
            if auth_method != 'gmail_oauth':
                self.logger.debug("Gmail OAuth not selected as auth method")
                return False
            
            # Check if OAuth is authenticated
            oauth_authenticated = email_config.get('oauth_authenticated', False)
            self.logger.debug(f"OAuth authenticated status: {oauth_authenticated}")
            
            if not oauth_authenticated:
                self.logger.debug("Gmail OAuth not authenticated")
                return False
            
            # Check if Gmail client is available and functional
            if not hasattr(self.email_service, 'gmail_client') or self.email_service.gmail_client is None:
                self.logger.debug("Gmail client not initialized")
                return False
            
            # Verify Gmail client has valid credentials
            gmail_client = self.email_service.gmail_client
            if not hasattr(gmail_client, 'credentials') or gmail_client.credentials is None:
                self.logger.debug("Gmail client has no credentials")
                return False
            
            if not gmail_client.credentials.valid:
                self.logger.debug("Gmail client credentials are not valid")
                # Try to refresh credentials if possible
                if gmail_client.credentials.expired and gmail_client.credentials.refresh_token:
                    try:
                        from google.auth.transport.requests import Request
                        gmail_client.credentials.refresh(Request())
                        self.logger.info("Gmail credentials refreshed successfully")
                        return gmail_client.credentials.valid
                    except Exception as e:
                        self.logger.warning(f"Failed to refresh Gmail credentials: {e}")
                        return False
                return False
            
            self.logger.info("Gmail OAuth is properly configured and authenticated")
            return True
            
        except Exception as e:
            self.logger.error(f"Error checking Gmail OAuth configuration: {e}")
            return False
    
    def _get_oauth_status_info(self) -> Dict[str, Any]:
        """
        Get detailed OAuth status information for UI display.
        
        Returns:
            Dictionary with OAuth status details
        """
        try:
            if not self.email_service:
                return {
                    'configured': False,
                    'authenticated': False,
                    'user_email': None,
                    'status_message': 'Email service not available',
                    'error': 'No email service configured'
                }
            
            email_config = self.email_service.get_email_config()
            auth_method = email_config.get('auth_method', 'smtp')
            
            if auth_method != 'gmail_oauth':
                return {
                    'configured': False,
                    'authenticated': False,
                    'user_email': None,
                    'status_message': 'Gmail OAuth not selected',
                    'error': None
                }
            
            oauth_authenticated = email_config.get('oauth_authenticated', False)
            user_email = email_config.get('oauth_email', email_config.get('user_email'))
            
            if oauth_authenticated:
                # OAuth is marked as authenticated in config
                return {
                    'configured': True,
                    'authenticated': True,
                    'user_email': user_email,
                    'status_message': f'Connected as {user_email}' if user_email else 'Connected to Gmail',
                    'error': None
                }
            else:
                return {
                    'configured': True,
                    'authenticated': False,
                    'user_email': None,
                    'status_message': 'Gmail OAuth configured but not authenticated',
                    'error': 'Authentication required'
                }
                
        except Exception as e:
            self.logger.error(f"Error getting OAuth status info: {e}")
            return {
                'configured': False,
                'authenticated': False,
                'user_email': None,
                'status_message': 'Error checking OAuth status',
                'error': str(e)
            }
    
    def _load_gmail_emails(self):
        """Load real emails from Gmail API."""
        try:
            # Fetch emails from Gmail using EmailService
            gmail_emails = self.email_service._fetch_gmail_emails(max_results=10)
            
            if not gmail_emails:
                self.logger.info("No Gmail emails found, using placeholder emails")
                self._load_placeholder_emails()
                return
            
            self.logger.info(f"Loaded {len(gmail_emails)} Gmail emails")
            
            for email_data in gmail_emails:
                # Convert Gmail email format to internal format
                formatted_email = self._format_gmail_email(email_data)
                
                # Create list item
                item = QListWidgetItem()
                
                # Store the full email data in the item for later use
                item.setData(Qt.UserRole, formatted_email)
                
                # Set item size to accommodate the custom widget with proper spacing
                gmail_source = formatted_email.get('source') == 'gmail'
                item_height = 77 if gmail_source else 67  # Slightly taller for Gmail metadata
                item.setSizeHint(QSize(0, item_height))  # Fixed height for consistent appearance
                
                # Add item to list
                self.email_list.addItem(item)
                
                # Create and set custom widget for this item
                preview_widget = EmailPreviewWidget(formatted_email, self.theme_manager)
                self.email_list.setItemWidget(item, preview_widget)
                
        except Exception as e:
            self.logger.error(f"Error loading Gmail emails: {e}")
            # Fallback to placeholder emails
            self._load_placeholder_emails()
    
    def _format_gmail_email(self, gmail_email: dict) -> dict:
        """
        Format Gmail API email data to internal email format.
        
        Args:
            gmail_email: Email data from Gmail API
            
        Returns:
            Formatted email data dictionary
        """
        try:
            # Format timestamp from Gmail internal date
            timestamp = self._format_gmail_timestamp(gmail_email.get('timestamp', '0'))
            
            # Create preview text from snippet or body
            preview = gmail_email.get('snippet', '')
            if not preview and gmail_email.get('body'):
                # Create preview from body if snippet is not available
                body = gmail_email.get('body', '')
                preview = body[:100] + "..." if len(body) > 100 else body
            
            # Format the email data
            formatted_email = {
                'id': gmail_email.get('id', ''),
                'thread_id': gmail_email.get('thread_id', ''),
                'subject': gmail_email.get('subject', 'No Subject'),
                'sender': gmail_email.get('sender', 'Unknown Sender'),
                'to': gmail_email.get('to', ''),
                'preview': preview,
                'timestamp': timestamp,
                'unread': gmail_email.get('unread', False),
                'body': gmail_email.get('body', ''),
                'date': gmail_email.get('date', ''),
                'labels': gmail_email.get('labels', []),  # Gmail-specific
                'source': 'gmail'  # Mark as Gmail source
            }
            
            return formatted_email
            
        except Exception as e:
            self.logger.error(f"Error formatting Gmail email: {e}")
            # Return a basic formatted email on error
            return {
                'id': gmail_email.get('id', ''),
                'subject': gmail_email.get('subject', 'Error loading email'),
                'sender': gmail_email.get('sender', 'Unknown'),
                'preview': 'Error loading email content',
                'timestamp': 'Unknown',
                'unread': False,
                'body': 'Error loading email content',
                'source': 'gmail'
            }
    
    def _format_gmail_timestamp(self, internal_date: str) -> str:
        """
        Format Gmail internal date to readable timestamp.
        
        Args:
            internal_date: Gmail internal date string (milliseconds since epoch)
            
        Returns:
            Formatted timestamp string
        """
        try:
            from datetime import datetime, timedelta
            
            # Convert from milliseconds to seconds
            timestamp_seconds = int(internal_date) / 1000
            email_date = datetime.fromtimestamp(timestamp_seconds)
            now = datetime.now()
            
            # Calculate time difference
            time_diff = now - email_date
            
            if time_diff.days == 0:
                # Today - show time
                return email_date.strftime("%I:%M %p")
            elif time_diff.days == 1:
                # Yesterday
                return "Yesterday"
            elif time_diff.days < 7:
                # This week - show day
                return email_date.strftime("%A")
            else:
                # Older - show date
                return email_date.strftime("%m/%d/%Y")
                
        except (ValueError, TypeError) as e:
            self.logger.warning(f"Error formatting timestamp {internal_date}: {e}")
            return "Unknown"
    
    def _fetch_gmail_email_content(self, email_id: str) -> str:
        """
        Fetch the full content of a Gmail email by ID.
        
        Args:
            email_id: Gmail email ID
            
        Returns:
            Full email content or error message
        """
        try:
            if not email_id or not self.email_service:
                return "Email content not available"
            
            # Check if email service has Gmail client
            if not hasattr(self.email_service, 'gmail_client') or not self.email_service.gmail_client:
                return "Gmail not connected. Please check your OAuth authentication."
            
            # Try to fetch the email content using the Gmail client
            gmail_client = self.email_service.gmail_client
            if not hasattr(gmail_client, 'service') or not gmail_client.service:
                return "Gmail service not available. Please re-authenticate."
            
            # Fetch the email message
            message = gmail_client.service.users().messages().get(
                userId='me',
                id=email_id,
                format='full'
            ).execute()
            
            # Extract the email body
            body = self._extract_gmail_message_body(message)
            
            if body.strip():
                return body
            else:
                return "Email content could not be loaded"
                
        except Exception as e:
            self.logger.error(f"Error fetching Gmail email content for {email_id}: {e}")
            return f"Error loading email content: {str(e)}"
    
    def _extract_gmail_message_body(self, message: dict) -> str:
        """
        Extract the body text from a Gmail API message.
        
        Args:
            message: Gmail API message object
            
        Returns:
            Email body text
        """
        try:
            import base64
            
            payload = message.get('payload', {})
            body = ""
            
            # Check if message has parts (multipart)
            if 'parts' in payload:
                for part in payload['parts']:
                    if part.get('mimeType') == 'text/plain':
                        data = part.get('body', {}).get('data', '')
                        if data:
                            body = base64.urlsafe_b64decode(data).decode('utf-8')
                            break
                    elif part.get('mimeType') == 'text/html' and not body:
                        # Fallback to HTML if no plain text
                        data = part.get('body', {}).get('data', '')
                        if data:
                            html_body = base64.urlsafe_b64decode(data).decode('utf-8')
                            # Simple HTML to text conversion
                            import re
                            body = re.sub('<[^<]+?>', '', html_body)
            else:
                # Single part message
                if payload.get('mimeType') in ['text/plain', 'text/html']:
                    data = payload.get('body', {}).get('data', '')
                    if data:
                        decoded_body = base64.urlsafe_b64decode(data).decode('utf-8')
                        if payload.get('mimeType') == 'text/html':
                            # Simple HTML to text conversion
                            import re
                            body = re.sub('<[^<]+?>', '', decoded_body)
                        else:
                            body = decoded_body
            
            return body.strip()
            
        except Exception as e:
            self.logger.error(f"Error extracting Gmail message body: {e}")
            return "Error extracting email content"
    
    def _load_placeholder_emails(self, oauth_status: Dict[str, Any] = None):
        """
        Load welcome message or OAuth status information when Gmail is not connected.
        
        Args:
            oauth_status: OAuth status information from _get_oauth_status_info()
        """
        if oauth_status is None:
            oauth_status = self._get_oauth_status_info()
        
        # Clear existing items
        self.email_list.clear()
        
        # Determine the appropriate message based on OAuth status
        if oauth_status.get('configured') and not oauth_status.get('authenticated'):
            # Gmail OAuth is configured but not authenticated
            welcome_data = {
                'subject': 'Gmail Authentication Required',
                'sender': 'Email Assistant',
                'preview': f"Gmail OAuth is configured but authentication is required. {oauth_status.get('status_message', '')}",
                'timestamp': 'Now',
                'unread': True,
                'source': 'oauth_status',
                'body': f'''
                <div style="padding: 20px; font-family: Arial, sans-serif;">
                    <h2 style="color: #ff6b35;">🔐 Gmail Authentication Required</h2>
                    <p><strong>Status:</strong> {oauth_status.get('status_message', 'Authentication needed')}</p>
                    
                    <h3>Next Steps:</h3>
                    <ol>
                        <li>Click the <strong>Settings (⚙)</strong> button above</li>
                        <li>Go to the Gmail OAuth 2.0 section</li>
                        <li>Click <strong>"Authenticate with Google"</strong></li>
                        <li>Complete the authentication process in your browser</li>
                        <li>Return here and click <strong>Refresh (↻)</strong> to load your emails</li>
                    </ol>
                    
                    <p style="margin-top: 20px; padding: 15px; background-color: #f8f9fa; border-left: 4px solid #0078d4;">
                        <strong>💡 Tip:</strong> Once authenticated, you'll be able to view your Gmail messages 
                        and use AI-powered features to compose and reply to emails.
                    </p>
                </div>
                '''
            }
        elif oauth_status.get('error'):
            # There was an error checking OAuth status
            welcome_data = {
                'subject': 'Gmail Connection Error',
                'sender': 'Email Assistant',
                'preview': f"Error connecting to Gmail: {oauth_status.get('error', 'Unknown error')}",
                'timestamp': 'Now',
                'unread': True,
                'source': 'error',
                'body': f'''
                <div style="padding: 20px; font-family: Arial, sans-serif;">
                    <h2 style="color: #dc3545;">[ERROR] Gmail Connection Error</h2>
                    <p><strong>Error:</strong> {oauth_status.get('error', 'Unknown error occurred')}</p>
                    
                    <h3>Troubleshooting Steps:</h3>
                    <ol>
                        <li>Click the <strong>Settings (⚙)</strong> button above</li>
                        <li>Check your Gmail OAuth 2.0 configuration</li>
                        <li>Ensure your credentials.json file is valid</li>
                        <li>Try re-authenticating with Google</li>
                        <li>Click <strong>Refresh (↻)</strong> to retry</li>
                    </ol>
                    
                    <p style="margin-top: 20px; padding: 15px; background-color: #fff3cd; border-left: 4px solid #ffc107;">
                        <strong>[WARN] Note:</strong> If the problem persists, check your internet connection 
                        and ensure your Google Cloud Console project is properly configured.
                    </p>
                </div>
                '''
            }
        else:
            # Gmail OAuth is not configured at all
            welcome_data = {
                'subject': 'Welcome to Email Automation',
                'sender': 'Email Assistant',
                'preview': 'Connect your Gmail account in Settings to start managing your emails with AI assistance.',
                'timestamp': 'Now',
                'unread': False,
                'source': 'welcome',
                'body': '''
                <div style="padding: 20px; font-family: Arial, sans-serif;">
                    <h2 style="color: #0078d4;">📧 Welcome to Email Automation!</h2>
                    <p>Get started by connecting your Gmail account to unlock powerful email management features:</p>
                    <ul>
                        <li><strong>📧 View and organize</strong> your Gmail messages</li>
                        <li><strong>🤖 AI-powered replies</strong> generated automatically</li>
                        <li><strong>✉️ Smart compose</strong> with context-aware suggestions</li>
                        <li><strong>🔍 Advanced search</strong> and filtering capabilities</li>
                    </ul>
                    
                    <h3>Getting Started:</h3>
                    <ol>
                        <li>Click the <strong>Settings (⚙)</strong> button above</li>
                        <li>Select <strong>"Gmail OAuth 2.0"</strong> as your authentication method</li>
                        <li>Upload your <strong>credentials.json</strong> file from Google Cloud Console</li>
                        <li>Complete the authentication process</li>
                        <li>Return here and click <strong>Refresh (↻)</strong> to load your emails</li>
                    </ol>
                    
                    <p style="margin-top: 20px; padding: 15px; background-color: #e8f5e8; border-left: 4px solid #28a745;">
                        <strong>🔒 Privacy:</strong> Your email data is processed securely and never stored permanently.
                    </p>
                </div>
                '''
            }
        
        # Create and add the list item
        item = QListWidgetItem()
        item.setData(Qt.UserRole, welcome_data)
        
        # Set appropriate height based on content type
        item_height = 77 if welcome_data.get('source') in ['oauth_status', 'error'] else 67
        item.setSizeHint(QSize(0, item_height))
        
        self.email_list.addItem(item)
        preview_widget = EmailPreviewWidget(welcome_data, self.theme_manager)
        self.email_list.setItemWidget(item, preview_widget)
        
        self.logger.info(f"Loaded placeholder email: {welcome_data['subject']}")
    
    def _refresh_gmail_emails(self):
        """Refresh Gmail emails manually with OAuth status checking and loading indicator."""
        from PySide6.QtWidgets import QProgressDialog, QMessageBox
        from PySide6.QtCore import QTimer
        
        try:
            self.logger.info("Manually refreshing Gmail emails")
            
            # First check OAuth status
            oauth_status = self._get_oauth_status_info()
            
            if not oauth_status['configured']:
                # Gmail OAuth not configured
                QMessageBox.information(
                    self,
                    "Gmail Not Configured",
                    "Gmail OAuth is not configured.\n\n"
                    "Please click the Settings button (⚙) to set up Gmail OAuth authentication."
                )
                return
            
            if not oauth_status['authenticated']:
                # Gmail OAuth configured but not authenticated
                QMessageBox.warning(
                    self,
                    "Gmail Authentication Required",
                    f"Gmail authentication is required.\n\n"
                    f"Status: {oauth_status['status_message']}\n\n"
                    "Please click the Settings button (⚙) to authenticate with Gmail."
                )
                return
            
            # Show progress dialog
            self.refresh_progress = QProgressDialog("Refreshing emails...", "Cancel", 0, 100, self)
            self.refresh_progress.setWindowModality(Qt.WindowModal)
            self.refresh_progress.setMinimumDuration(0)
            self.refresh_progress.setValue(0)
            self.refresh_progress.show()
            
            # Disable refresh button during operation
            self.refresh_button.setEnabled(False)
            self.refresh_button.setText("[WAIT]")
            
            # Create timer for progress updates
            self.refresh_timer = QTimer()
            self.refresh_progress_value = 0
            self.refresh_stages = [
                f"Connecting to Gmail ({oauth_status['user_email']})...",
                "Fetching email list from Gmail API...",
                "Processing email data...",
                "Updating email preview list...",
                "Refresh complete!"
            ]
            self.refresh_stage_index = 0
            
            def update_refresh_progress():
                self.refresh_progress_value += 20
                self.refresh_progress.setValue(self.refresh_progress_value)
                
                # Update stage message
                if self.refresh_stage_index < len(self.refresh_stages):
                    self.refresh_progress.setLabelText(self.refresh_stages[self.refresh_stage_index])
                    self.refresh_stage_index += 1
                
                if self.refresh_progress_value >= 100:
                    self.refresh_timer.stop()
                    self.refresh_progress.close()
                    self._complete_email_refresh()
            
            self.refresh_timer.timeout.connect(update_refresh_progress)
            self.refresh_timer.start(400)  # Update every 400ms for smoother progress
            
            # Handle cancel button
            def on_refresh_cancel():
                self.refresh_timer.stop()
                self.refresh_button.setEnabled(True)
                self.refresh_button.setText("↻")
                self.logger.info("Email refresh cancelled by user")
            
            self.refresh_progress.canceled.connect(on_refresh_cancel)
                
        except Exception as e:
            self.logger.error(f"Error starting Gmail email refresh: {e}")
            self._complete_email_refresh()
    
    def _complete_email_refresh(self):
        """Complete the email refresh process with enhanced OAuth synchronization."""
        try:
            # Clear existing emails
            self.email_list.clear()
            
            # Get fresh OAuth status
            oauth_status = self._get_oauth_status_info()
            
            if oauth_status['authenticated']:
                self.logger.info(f"Gmail OAuth authenticated ({oauth_status['user_email']}), fetching fresh emails")
                
                # Force refresh of email cache in email service
                if self.email_service and hasattr(self.email_service, '_email_cache'):
                    self.email_service._email_cache.clear()
                    self.email_service._last_fetch_time = None
                
                # Load fresh Gmail emails
                self._load_gmail_emails()
                
                # Update UI status
                self.logger.info("Gmail email refresh completed successfully")
                
            else:
                self.logger.info(f"Gmail OAuth not authenticated: {oauth_status['status_message']}")
                self._load_placeholder_emails(oauth_status)
                
        except Exception as e:
            self.logger.error(f"Error refreshing Gmail emails: {e}")
            
            # Show error status
            error_oauth_status = {
                'configured': False,
                'authenticated': False,
                'user_email': None,
                'status_message': 'Error during refresh',
                'error': str(e)
            }
            
            # Clear list and show error placeholder
            self.email_list.clear()
            self._load_placeholder_emails(error_oauth_status)
            
        finally:
            # Re-enable refresh button
            self.refresh_button.setEnabled(True)
            self.refresh_button.setText("↻")
            
            # Publish refresh completed event
            if self.event_bus:
                self.event_bus.publish("email.refresh_completed", {
                    'success': True,
                    'timestamp': time.time()
                })
    
    def _connect_events(self):
        """Connect UI event handlers."""
        # Connect email list selection
        self.email_list.itemClicked.connect(self._on_email_selected)
        
        # Connect reply button
        self.reply_button.clicked.connect(self._on_generate_reply_clicked)
        
        # Connect compose button
        self.compose_button.clicked.connect(self._on_compose_clicked)
    
    def _subscribe_to_email_events(self):
        """Subscribe to email service events for enhanced user feedback."""
        if self.event_bus:
            # Subscribe to email sent events
            self.event_bus.subscribe("email.sent", self._on_email_sent_event)
            
            # Subscribe to email send error events
            self.event_bus.subscribe("email.send_error", self._on_email_send_error_event)
            
            # Subscribe to email configuration events
            self.event_bus.subscribe("email.config_updated", self._on_email_config_updated)
            
            self.logger.info("Subscribed to email service events")
    
    @Slot(dict)
    def _on_email_sent_event(self, event_data: dict):
        """
        Handle email sent event from EmailService.
        
        Args:
            event_data: Dictionary containing email send details
        """
        self.logger.info(f"Email sent event received: {event_data.get('to', 'unknown')}")
        # Additional UI updates could be added here if needed
        # For example, updating a sent items list or showing notifications
    
    @Slot(dict)
    def _on_email_send_error_event(self, event_data: dict):
        """
        Handle email send error event from EmailService.
        
        Args:
            event_data: Dictionary containing error details
        """
        error_msg = event_data.get('error', 'Unknown error')
        to = event_data.get('to', 'unknown')
        self.logger.error(f"Email send error event received for {to}: {error_msg}")
        # Additional error handling could be added here if needed
    
    @Slot(dict)
    def _on_email_config_updated(self, config_data: dict):
        """
        Handle email configuration updated event.
        
        Args:
            config_data: Updated email configuration
        """
        self.logger.info("Email configuration updated event received")
        # Could update UI elements based on configuration changes if needed
    
    @Slot()
    def _on_email_selected(self, item):
        """
        Handle email selection from the preview list with Gmail integration.
        
        Args:
            item: Selected QListWidgetItem
        """
        if not item:
            return
            
        # Get the stored email data from the item
        email_data = item.data(Qt.UserRole)
        if not email_data:
            return
        
        # Determine the email body content
        if email_data.get('source') == 'gmail':
            # For Gmail emails, use the actual email body from Gmail API
            full_body = email_data.get('body', '')
            
            # If no body content, use the snippet/preview
            if not full_body.strip():
                full_body = email_data.get('preview', 'No content available')
            
            # If still no content, try to fetch the full email content
            if not full_body.strip() or full_body == 'No content available':
                full_body = self._fetch_gmail_email_content(email_data.get('id', ''))
                
        else:
            # For placeholder/demo emails, generate content based on subject
            full_body = f"{email_data['preview']}\n\n"
            
            # Add demo content based on the subject
            if "Meeting Reminder" in email_data['subject']:
                full_body += "Please confirm your attendance by replying to this email.\n\nAgenda:\n1. Q1 Goals Review\n2. Budget Planning\n3. Team Assignments\n\nLocation: Conference Room A\nTime: 2:00 PM - 3:30 PM\n\nBest regards,\nJohn"
            elif "Project Update" in email_data['subject']:
                full_body += "Current Status:\n[OK] Wireframes completed\n[OK] Design mockups approved\n🔄 Frontend development in progress\n[WAIT] Backend API development pending\n\nNext Steps:\n- Complete responsive design\n- Begin user testing\n- Prepare staging environment\n\nExpected completion: End of month\n\nRegards,\nSarah"
            elif "Welcome" in email_data['subject']:
                full_body += "Getting Started:\n1. Complete your profile setup\n2. Explore our features\n3. Join our community forum\n4. Contact support if needed\n\nUseful Links:\n- User Guide: https://help.service.com\n- Community: https://community.service.com\n- Support: support@service.com\n\nWelcome aboard!\nThe Support Team"
            else:
                full_body += "This is a demo email. Connect your Gmail account to view real email content."
        
        # Create complete email data for the details panel
        complete_email_data = {
            'id': email_data.get('id', ''),
            'thread_id': email_data.get('thread_id', ''),
            'subject': email_data['subject'],
            'sender': email_data['sender'],
            'to': email_data.get('to', ''),
            'body': full_body,
            'timestamp': email_data['timestamp'],
            'preview': email_data['preview'],
            'unread': email_data['unread'],
            'labels': email_data.get('labels', []),
            'source': email_data.get('source', 'demo')
        }
        
        self.selected_email = complete_email_data
        
        # Update the details panel
        self.subject_label.setText(complete_email_data['subject'])
        
        # Create sender info with Gmail-specific metadata
        sender_info = f"From: {complete_email_data['sender']} • {complete_email_data['timestamp']}"
        
        # Add Gmail-specific metadata to sender info
        if complete_email_data.get('source') == 'gmail':
            gmail_metadata = []
            
            # Add thread info
            if complete_email_data.get('thread_id'):
                gmail_metadata.append("🧵 Thread")
            
            # Add labels info
            labels = complete_email_data.get('labels', [])
            if labels:
                user_labels = [label for label in labels if not label.startswith('CATEGORY_') and label not in ['INBOX', 'UNREAD', 'IMPORTANT']]
                if user_labels:
                    labels_text = "🏷️ " + ", ".join(user_labels[:3])
                    if len(user_labels) > 3:
                        labels_text += f" +{len(user_labels) - 3}"
                    gmail_metadata.append(labels_text)
            
            # Add Gmail source indicator
            gmail_metadata.append("📧 Gmail")
            
            if gmail_metadata:
                sender_info += " • " + " • ".join(gmail_metadata)
        
        self.sender_label.setText(sender_info)
        
        # Set email body with enhanced Gmail content display
        body_content = complete_email_data.get('body', '')
        
        if complete_email_data.get('source') == 'gmail':
            # For Gmail emails, enhance the display with metadata
            if body_content.strip():
                # Add Gmail-specific header information
                gmail_header = f"📧 Gmail Email (ID: {complete_email_data.get('id', 'Unknown')})\n"
                if complete_email_data.get('to'):
                    gmail_header += f"To: {complete_email_data['to']}\n"
                gmail_header += f"Date: {complete_email_data.get('timestamp', 'Unknown')}\n"
                
                # Add labels if available
                labels = complete_email_data.get('labels', [])
                if labels:
                    user_labels = [label for label in labels if not label.startswith('CATEGORY_') and label not in ['INBOX', 'UNREAD', 'IMPORTANT']]
                    if user_labels:
                        gmail_header += f"Labels: {', '.join(user_labels)}\n"
                
                gmail_header += "\n" + "="*50 + "\n\n"
                
                # Combine header with body content
                full_content = gmail_header + body_content
                self.body_browser.setPlainText(full_content)
            else:
                # If no body content, show a message
                self.body_browser.setPlainText("This Gmail email has no text content or the content could not be loaded.\n\nThis might be an HTML-only email or there may be an issue with content extraction.")
        else:
            # For demo/placeholder emails, display as-is
            self.body_browser.setPlainText(body_content)
        
        # Enable reply button
        self.reply_button.setEnabled(True)
        
        # Emit signal
        self.email_selected.emit(complete_email_data)
        
        self.logger.info(f"Email selected: {complete_email_data['subject']}")
    
    @Slot()
    def _on_generate_reply_clicked(self):
        """Handle generate reply button click."""
        if not self.selected_email:
            return
            
        self.logger.info("Reply generation requested")
        
        # Generate AI reply using the selected email
        generated_reply = self.generate_reply_to_email(self.selected_email)
        
        # Extract sender email from the "From: Name <email>" format
        sender_info = self.selected_email.get('sender', '')
        sender_email = sender_info
        if '<' in sender_info and '>' in sender_info:
            # Extract email from "Name <email@domain.com>" format
            sender_email = sender_info.split('<')[1].split('>')[0].strip()
        elif ' ' in sender_info and '@' in sender_info:
            # Handle "Name email@domain.com" format
            parts = sender_info.split()
            for part in parts:
                if '@' in part:
                    sender_email = part.strip()
                    break
        
        # Prepare reply subject with "Re:" prefix
        original_subject = self.selected_email.get('subject', '')
        reply_subject = original_subject
        if not original_subject.lower().startswith('re:'):
            reply_subject = f"Re: {original_subject}"
        
        # Prepare prefill data for the compose dialog
        prefill_data = {
            'to': sender_email,
            'subject': reply_subject,
            'body': generated_reply
        }
        
        # Create and show compose email dialog with prefilled data
        compose_dialog = ComposeEmailDialog(parent=self, prefill_data=prefill_data)
        
        # Connect dialog signals for handling email operations
        compose_dialog.email_send_requested.connect(self._handle_email_send)
        compose_dialog.draft_generation_requested.connect(lambda data, dialog=compose_dialog: self._handle_draft_generation(data, dialog))
        
        # Show dialog
        result = compose_dialog.exec()
        
        if result == ComposeEmailDialog.Accepted:
            self.logger.info("Reply compose dialog accepted")
        else:
            self.logger.info("Reply compose dialog cancelled")
        
        # Emit signal for other components that might be listening
        self.reply_requested.emit(self.selected_email)
    
    @Slot()
    def _on_compose_clicked(self):
        """Handle compose button click."""
        self.logger.info("Compose email requested")
        
        # Create and show compose email dialog
        compose_dialog = ComposeEmailDialog(parent=self)
        
        # Connect dialog signals for handling email operations
        compose_dialog.email_send_requested.connect(self._handle_email_send)
        compose_dialog.draft_generation_requested.connect(lambda data, dialog=compose_dialog: self._handle_draft_generation(data, dialog))
        
        # Show dialog
        result = compose_dialog.exec()
        
        if result == ComposeEmailDialog.Accepted:
            self.logger.info("Compose dialog accepted")
        else:
            self.logger.info("Compose dialog cancelled")
        
        # Emit signal for other components that might be listening
        self.compose_requested.emit()
    
    @Slot(dict)
    def _handle_email_send(self, email_data: dict):
        """
        Handle email send request from compose dialog with enhanced user feedback.
        
        Args:
            email_data: Dictionary containing to, subject, and body
        """
        from PySide6.QtWidgets import QMessageBox, QProgressDialog
        from PySide6.QtCore import QTimer
        
        self.logger.info(f"Handling email send request to: {email_data.get('to', 'unknown')}")
        
        # Extract email data
        to = email_data.get('to', '').strip()
        subject = email_data.get('subject', '').strip()
        body = email_data.get('body', '').strip()
        
        # Validate email data before sending
        validation_errors = []
        
        if not to:
            validation_errors.append("Recipient email address is required")
        elif "@" not in to or "." not in to.split("@")[1] if "@" in to else True:
            validation_errors.append("Invalid recipient email format")
        
        if not subject:
            validation_errors.append("Email subject is required")
        
        if not body:
            validation_errors.append("Email body is required")
        
        if validation_errors:
            error_msg = "Cannot send email:\n\n" + "\n".join(f"• {error}" for error in validation_errors)
            QMessageBox.warning(self, "Send Failed", error_msg)
            return
        
        # Show progress dialog for email sending
        progress = QProgressDialog("Sending email...", "Cancel", 0, 100, self)
        progress.setWindowModality(Qt.WindowModal)
        progress.setMinimumDuration(0)
        progress.setValue(0)
        progress.show()
        
        # Create a timer to simulate sending progress
        self.send_timer = QTimer()
        self.send_progress = 0
        
        def update_send_progress():
            self.send_progress += 25
            progress.setValue(self.send_progress)
            
            # Update progress message based on stage
            if self.send_progress <= 25:
                progress.setLabelText("Validating configuration...")
            elif self.send_progress <= 50:
                progress.setLabelText("Connecting to SMTP server...")
            elif self.send_progress <= 75:
                progress.setLabelText("Sending email...")
            else:
                progress.setLabelText("Finalizing...")
            
            if self.send_progress >= 100:
                self.send_timer.stop()
                progress.close()
                self._complete_email_send(to, subject, body)
        
        self.send_timer.timeout.connect(update_send_progress)
        self.send_timer.start(300)  # Update every 300ms
        
        # Handle cancel button
        def on_send_cancel():
            self.send_timer.stop()
            self.logger.info("Email sending cancelled by user")
        
        progress.canceled.connect(on_send_cancel)
    
    def _complete_email_send(self, to: str, subject: str, body: str):
        """Complete the email sending process."""
        from PySide6.QtWidgets import QMessageBox
        
        try:
            # Use the SMTP method from EmailService
            success = self.send_email_smtp(to, subject, body)
            
            if success:
                self.logger.info("Email sent successfully")
                # Show detailed success message
                QMessageBox.information(
                    self, 
                    "[OK] Email Sent Successfully", 
                    f"Your email has been sent successfully!\n\n"
                    f"📧 To: {to}\n"
                    f"📝 Subject: {subject}\n"
                    f"📊 Body length: {len(body)} characters\n\n"
                    f"The recipient should receive your message shortly."
                )
            else:
                self.logger.error("Failed to send email")
                # Show detailed error message with troubleshooting tips
                QMessageBox.critical(
                    self, 
                    "[ERROR] Send Failed", 
                    f"Failed to send email to {to}.\n\n"
                    f"📝 Subject: {subject}\n\n"
                    f"Possible solutions:\n"
                    f"• Check your email configuration in Email → Settings\n"
                    f"• Verify your internet connection\n"
                    f"• Ensure your email provider allows SMTP access\n"
                    f"• For Gmail, use an App Password instead of your regular password\n\n"
                    f"Please try again after checking these settings."
                )
                
        except Exception as e:
            self.logger.error(f"Unexpected error during email send: {e}")
            QMessageBox.critical(
                self,
                "[ERROR] Unexpected Error",
                f"An unexpected error occurred while sending email:\n\n"
                f"{str(e)}\n\n"
                f"Please check your configuration and try again."
            )
    
    def _handle_draft_generation(self, draft_data: dict, dialog=None):
        """
        Handle AI draft generation request from compose dialog with progress feedback.
        
        Args:
            draft_data: Dictionary containing to, subject, and current_message
            dialog: ComposeEmailDialog instance that requested the generation
        """
        from PySide6.QtWidgets import QMessageBox, QProgressDialog
        from PySide6.QtCore import QTimer
        
        self.logger.info("Handling AI draft generation request")
        
        # Extract data from the request
        to = draft_data.get('to', '')
        subject = draft_data.get('subject', '')
        current_message = draft_data.get('current_message', '')
        
        # Validate input for better AI generation
        if not to and not subject:
            QMessageBox.warning(
                self,
                "AI Generation",
                "Please provide at least a recipient or subject to generate better content."
            )
            if dialog and hasattr(dialog, '_reset_generate_button'):
                dialog._reset_generate_button()
            return
        
        # Show progress dialog for AI generation
        progress = QProgressDialog("Generating AI draft...", "Cancel", 0, 100, self)
        progress.setWindowModality(Qt.WindowModal)
        progress.setMinimumDuration(0)
        progress.setValue(0)
        progress.show()
        
        # Create a timer to simulate AI generation progress
        self.ai_generation_timer = QTimer()
        self.ai_generation_progress = 0
        
        def update_ai_generation_progress():
            self.ai_generation_progress += 20
            progress.setValue(self.ai_generation_progress)
            
            # Update progress message based on stage
            if self.ai_generation_progress <= 20:
                progress.setLabelText("Analyzing context...")
            elif self.ai_generation_progress <= 40:
                progress.setLabelText("Processing recipient and subject...")
            elif self.ai_generation_progress <= 60:
                progress.setLabelText("Generating content...")
            elif self.ai_generation_progress <= 80:
                progress.setLabelText("Refining draft...")
            else:
                progress.setLabelText("Finalizing content...")
            
            if self.ai_generation_progress >= 100:
                self.ai_generation_timer.stop()
                progress.close()
                self._complete_draft_generation(to, subject, current_message, dialog)
        
        self.ai_generation_timer.timeout.connect(update_ai_generation_progress)
        self.ai_generation_timer.start(250)  # Update every 250ms
        
        # Handle cancel button
        def on_ai_generation_cancel():
            self.ai_generation_timer.stop()
            if dialog and hasattr(dialog, '_reset_generate_button'):
                dialog._reset_generate_button()
            self.logger.info("AI draft generation cancelled by user")
        
        progress.canceled.connect(on_ai_generation_cancel)
    
    def _complete_draft_generation(self, to: str, subject: str, current_message: str, dialog=None):
        """Complete the AI draft generation process."""
        from PySide6.QtWidgets import QMessageBox
        
        try:
            # Generate AI draft using the enhanced method
            generated_content = self.generate_email_draft(to, subject, current_message)
            
            if generated_content and generated_content.strip():
                self.logger.info("AI draft generated successfully")
                
                # Update the dialog with the generated content
                if dialog and hasattr(dialog, 'set_generated_content'):
                    dialog.set_generated_content(generated_content)
                else:
                    self.logger.warning("Could not find compose dialog to update with generated content")
                    # Show success message as fallback
                    QMessageBox.information(
                        self,
                        "AI Draft Generated",
                        f"AI draft generated successfully!\n\nContent length: {len(generated_content)} characters"
                    )
            else:
                self.logger.warning("AI draft generation returned empty content")
                
                # Show warning message
                QMessageBox.warning(
                    self,
                    "AI Generation",
                    "AI generation completed but no content was generated.\n\nPlease try again with different parameters or compose manually."
                )
                
                # Reset the button
                if dialog and hasattr(dialog, '_reset_generate_button'):
                    dialog._reset_generate_button()
                    
        except Exception as e:
            self.logger.error(f"Error in AI draft generation: {e}")
            
            # Show error message
            QMessageBox.critical(
                self,
                "AI Generation Failed",
                f"Failed to generate AI draft:\n\n{str(e)}\n\nPlease try again or compose manually."
            )
            
            # Reset the button
            if dialog and hasattr(dialog, '_reset_generate_button'):
                dialog._reset_generate_button()
    

    
    @Slot(str)
    def _on_theme_changed(self, theme_name: str):
        """
        Handle theme change event.
        
        Args:
            theme_name: Name of the new theme
        """
        self.logger.info(f"Theme changed to: {theme_name}")
        self._apply_theme()
    
    def _apply_theme(self):
        """Apply theme-based styling to all components."""
        if not self.theme_manager:
            return
        
        # Get theme colors
        is_dark = self.theme_manager.is_dark_mode()
        
        # Apply theme to main components
        self._apply_splitter_theme(is_dark)
        self._apply_left_panel_theme(is_dark)
        self._apply_right_panel_theme(is_dark)
        
        # Apply theme to email preview widgets
        self._apply_email_preview_theme(is_dark)
    
    def _apply_splitter_theme(self, is_dark: bool):
        """Apply theme to splitter using theme manager."""
        if not hasattr(self, 'splitter') or not self.theme_manager:
            return
        
        # Apply theme to splitter using theme manager
        self.theme_manager.apply_theme_to_widget(self.splitter)
    
    def _apply_left_panel_theme(self, is_dark: bool):
        """Apply theme to left panel components using theme manager."""
        if not hasattr(self, 'email_list') or not self.theme_manager:
            return
        
        # Apply theme to the entire left panel using theme manager
        left_panel = self.email_list.parent()
        if left_panel:
            self.theme_manager.apply_theme_to_widget(left_panel)
        
        # Apply theme to email list with custom spacing to prevent overlapping
        self.theme_manager.apply_theme_to_widget(self.email_list)
        
        # Email list spacing is handled by the list configuration and theme manager
        
        # Don't apply theme manager to buttons - they have direct styling to ensure visibility
    
    def _apply_right_panel_theme(self, is_dark: bool):
        """Apply theme to right panel components using theme manager."""
        if not hasattr(self, 'subject_label') or not self.theme_manager:
            return
        
        # Apply theme to the entire right panel using theme manager
        right_panel = self.subject_label.parent()
        if right_panel:
            self.theme_manager.apply_theme_to_widget(right_panel)
        
        # Apply theme to individual components - let theme manager handle styling
        if hasattr(self, 'body_browser'):
            self.theme_manager.apply_theme_to_widget(self.body_browser)
        
        if hasattr(self, 'reply_button'):
            # Set button type for theme manager styling
            self.reply_button.setProperty("buttonType", "primary")
            self.theme_manager.apply_theme_to_widget(self.reply_button)
        
        if hasattr(self, 'compose_button'):
            self.compose_button.setProperty("buttonType", "primary")
            self.theme_manager.apply_theme_to_widget(self.compose_button)
    
    # Compose button styling is now done directly when creating the button
    
    def _apply_email_preview_theme(self, is_dark: bool):
        """Apply theme to email preview widgets."""
        if not hasattr(self, 'email_list'):
            return
        
        # Get theme colors
        text_color = self.theme_manager.get_color("text")
        text_secondary = self.theme_manager.get_color("text_secondary")
        primary_color = self.theme_manager.get_color("primary")
        
        # Update all email preview widgets
        for i in range(self.email_list.count()):
            item = self.email_list.item(i)
            if item:
                preview_widget = self.email_list.itemWidget(item)
                if isinstance(preview_widget, EmailPreviewWidget):
                    self._update_email_preview_widget_theme(preview_widget, text_color, text_secondary, primary_color)
    
    def _update_email_preview_widget_theme(self, widget: 'EmailPreviewWidget', text_color: str, text_secondary: str, primary_color: str):
        """Update theme for a single email preview widget."""
        # Update unread indicator
        for child in widget.findChildren(QLabel):
            if child.text() in ["●", "[NONE]"]:
                is_unread = child.text() == "●"
                child.setStyleSheet(f"color: {primary_color if is_unread else text_secondary}; font-size: 10px;")
            elif "AM" in child.text() or "PM" in child.text() or "ago" in child.text() or "Yesterday" in child.text():
                # Timestamp label
                child.setStyleSheet(f"color: {text_secondary}; font-size: 10px;")
            elif len(child.text()) > 20 and not ("AM" in child.text() or "PM" in child.text()):
                # Subject or preview text
                if child.font().bold():
                    # Subject label
                    child.setStyleSheet(f"color: {text_color}; margin: 1px 0px;")
                else:
                    # Preview or sender label
                    child.setStyleSheet(f"color: {text_secondary}; font-size: 10px; margin: 1px 0px;")
            elif "@" in child.text():
                # Sender label
                child.setStyleSheet(f"color: {text_secondary}; font-size: 10px; margin: 1px 0px;")
    
    # Placeholder methods for future implementation
    def generate_reply_to_email(self, email_data: dict) -> str:
        """
        Generate AI-powered reply to email using existing model service.
        
        This method creates a placeholder implementation that uses the existing
        model service through the event bus, following the same pattern as
        the chat and summarization tabs.
        
        Args:
            email_data: Dictionary containing email data (subject, sender, body, etc.)
            
        Returns:
            str: Generated reply content
        """
        try:
            if not email_data:
                self.logger.warning("No email data provided for reply generation")
                return ""
            
            # Extract email information
            sender = email_data.get('sender', 'Unknown')
            subject = email_data.get('subject', 'No Subject')
            body = email_data.get('body', '')
            
            self.logger.info(f"Generating AI reply to email from {sender}")
            
            # PLACEHOLDER IMPLEMENTATION
            # In a full implementation, this would:
            # 1. Use the event bus to communicate with the model service
            # 2. Send a prompt to generate an appropriate reply
            # 3. Wait for the model response
            # 4. Format and return the generated reply
            
            # For now, use the EmailService placeholder method
            generated_reply = self.email_service.generate_reply(email_data)
            
            # If EmailService returns empty, provide a basic template
            if not generated_reply:
                # Create a basic reply template
                sender_name = sender.split('<')[0].strip() if '<' in sender else sender.split('@')[0]
                generated_reply = f"Dear {sender_name},\n\nThank you for your email regarding '{subject}'. I have received your message and will review it carefully.\n\nI will get back to you soon with a detailed response.\n\nBest regards"
            
            self.logger.info("AI reply generated successfully")
            return generated_reply
            
        except Exception as e:
            self.logger.error(f"Error generating email reply: {e}")
            # Return a fallback reply in case of error
            return "Thank you for your email. I will review your message and get back to you soon.\n\nBest regards"
    
    def generate_email_draft(self, to: str, subject: str, context: str = "") -> str:
        """
        Generate AI-powered email draft using existing model service integration patterns.
        
        This method creates a placeholder implementation that uses the existing
        model service through the event bus, following the same pattern as
        the chat and summarization tabs.
        
        Args:
            to: Recipient email address
            subject: Email subject
            context: Additional context for generation
            
        Returns:
            str: Generated email draft
        """
        try:
            self.logger.info(f"Generating AI email draft for {to} with subject: {subject}")
            
            # PLACEHOLDER IMPLEMENTATION
            # In a full implementation, this would:
            # 1. Use the event bus to communicate with the model service
            # 2. Send a prompt to generate an appropriate email draft
            # 3. Wait for the model response
            # 4. Format and return the generated draft
            
            # For now, use the EmailService placeholder method
            generated_draft = self.email_service.generate_draft(to, subject, context)
            
            # If EmailService returns empty, provide a more sophisticated template
            if not generated_draft:
                # Extract recipient name from email
                recipient_name = to.split('@')[0].replace('.', ' ').replace('_', ' ').title()
                
                # Create context-aware draft based on subject
                if any(keyword in subject.lower() for keyword in ['meeting', 'schedule', 'appointment']):
                    generated_draft = f"Dear {recipient_name},\n\nI hope this email finds you well. I would like to schedule a meeting with you regarding {subject.lower()}.\n\nPlease let me know your availability for the coming week, and I will send you a calendar invitation.\n\nLooking forward to hearing from you.\n\nBest regards"
                elif any(keyword in subject.lower() for keyword in ['follow up', 'followup', 'follow-up']):
                    generated_draft = f"Dear {recipient_name},\n\nI wanted to follow up on our previous conversation regarding {subject.lower()}.\n\nPlease let me know if you need any additional information from my side, or if there are any next steps I should be aware of.\n\nThank you for your time.\n\nBest regards"
                elif any(keyword in subject.lower() for keyword in ['thank', 'thanks']):
                    generated_draft = f"Dear {recipient_name},\n\nI wanted to take a moment to thank you for {subject.lower()}.\n\nYour assistance has been invaluable, and I truly appreciate the time and effort you put into helping me.\n\nPlease don't hesitate to reach out if there's anything I can do to return the favor.\n\nWith gratitude"
                elif any(keyword in subject.lower() for keyword in ['proposal', 'project', 'collaboration']):
                    generated_draft = f"Dear {recipient_name},\n\nI hope you are doing well. I am reaching out to discuss a potential opportunity regarding {subject.lower()}.\n\nI believe this could be mutually beneficial, and I would love to explore how we might work together on this.\n\nWould you be available for a brief call this week to discuss the details?\n\nBest regards"
                else:
                    # Generic professional template
                    generated_draft = f"Dear {recipient_name},\n\nI hope this email finds you well. I am writing to you regarding {subject.lower()}.\n\nI would appreciate the opportunity to discuss this matter with you further. Please let me know if you have any questions or if there is additional information I can provide.\n\nThank you for your time and consideration.\n\nBest regards"
            
            self.logger.info("AI email draft generated successfully")
            return generated_draft
            
        except Exception as e:
            self.logger.error(f"Error generating email draft: {e}")
            # Return a fallback draft in case of error
            return f"Dear {to.split('@')[0]},\n\nI hope this email finds you well.\n\n[Please add your message content here]\n\nBest regards"
    
    def send_email_smtp(self, to: str, subject: str, body: str) -> bool:
        """
        Send email via SMTP using EmailService.
        
        Args:
            to: Recipient email address
            subject: Email subject
            body: Email body content
            
        Returns:
            bool: True if sent successfully, False otherwise
        """
        # Use EmailService to send email
        return self.email_service.send_email_smtp(to, subject, body)
    
    def open_email_settings(self):
        """Open email settings dialog."""
        try:
            # Load current email configuration from EmailService
            current_config = self.email_service.get_email_config()
            
            # Create and show dialog
            dialog = EmailSettingsDialog(self, current_config)
            dialog.settings_saved.connect(self._on_email_settings_saved)
            
            # CRITICAL FIX: Connect OAuth authentication signal
            dialog.oauth_authentication_requested.connect(self._on_oauth_authentication_requested)
            
            if dialog.exec() == EmailSettingsDialog.Accepted:
                self.logger.info("Email settings updated from EmailAutomationTab")
        except Exception as e:
            self.logger.error(f"Error showing email settings dialog: {e}")
            from PySide6.QtWidgets import QMessageBox
            QMessageBox.critical(self, "Error", f"Failed to open email settings dialog:\n{str(e)}")
    
    @Slot(dict)
    def _on_email_settings_saved(self, email_config: dict):
        """
        Handle email settings save from the settings dialog.
        
        Args:
            email_config: Dictionary containing email configuration
        """
        # Save email configuration through EmailService
        success = self.email_service.save_email_config(email_config)
        
        if success:
            self.logger.info("Email configuration saved successfully from EmailAutomationTab")
            from PySide6.QtWidgets import QMessageBox
            QMessageBox.information(self, "Settings Saved", "Email settings have been saved successfully.")
        else:
            self.logger.error("Failed to save email configuration from EmailAutomationTab")
            from PySide6.QtWidgets import QMessageBox
            QMessageBox.critical(self, "Save Failed", "Failed to save email settings. Please check your configuration and try again.")
    
    @Slot(str)
    def _on_oauth_authentication_requested(self, credentials_path: str):
        """
        Handle OAuth authentication request from the settings dialog.
        
        Args:
            credentials_path: Path to the credentials.json file
        """
        try:
            self.logger.info(f"OAuth authentication requested with credentials: {credentials_path}")
            
            # Use EmailService to authenticate with Gmail OAuth
            success, message = self.email_service.authenticate_gmail_oauth(credentials_path)
            
            # Find the currently open email settings dialog
            dialog = None
            for widget in self.findChildren(EmailSettingsDialog):
                if widget.isVisible():
                    dialog = widget
                    break
            
            if dialog:
                # Close the loading dialog
                dialog.close_oauth_loading_dialog()
                
                if success:
                    # Extract email from success message if available
                    oauth_email = ""
                    if "for " in message:
                        oauth_email = message.split("for ")[-1]
                    
                    # Update OAuth status in the dialog
                    dialog.update_oauth_status(True, message, oauth_email)
                    self.logger.info(f"OAuth authentication successful: {message}")
                else:
                    # Update OAuth status with error
                    dialog.update_oauth_status(False, message)
                    self.logger.error(f"OAuth authentication failed: {message}")
            else:
                self.logger.warning("Could not find email settings dialog to update OAuth status")
                
        except Exception as e:
            self.logger.error(f"Error handling OAuth authentication request: {e}")
            
            # Try to update dialog with error if possible
            for widget in self.findChildren(EmailSettingsDialog):
                if widget.isVisible():
                    widget.close_oauth_loading_dialog()
                    widget.update_oauth_status(False, f"Authentication error: {str(e)}")
                    break 
   
    def _on_email_selected(self, item):
        """
        Handle email selection from the preview list with enhanced visual feedback.
        
        Args:
            item: Selected QListWidgetItem
        """
        if not item:
            return
            
        # Get the stored email data from the item
        email_data = item.data(Qt.UserRole)
        if not email_data:
            return
        
        # Store selected email
        self.selected_email = email_data
        
        # Update email details display with animation
        self._update_email_details_with_animation(email_data)
        
        # Enable reply button
        self.reply_button.setEnabled(True)
        
        # Emit signal for other components
        self.email_selected.emit(email_data)
        
        self.logger.info(f"Email selected: {email_data.get('subject', 'No Subject')}")
    
    def _update_email_details_with_animation(self, email_data: dict):
        """Update email details display with responsive content formatting."""
        try:
            # Update subject with responsive handling
            subject = email_data.get('subject', 'No Subject')
            self.subject_label.setText(subject)
            
            # Update sender with responsive formatting
            sender = email_data.get('sender', 'Unknown Sender')
            timestamp = email_data.get('timestamp', '')
            
            # Format sender info responsively
            sender_info = f"From: {sender}"
            if timestamp:
                sender_info += f" • {timestamp}"
            self.sender_label.setText(sender_info)
            
            # Create responsive email body content
            full_body = self._create_responsive_email_body(email_data)
            self.body_browser.setHtml(full_body)
            
        except Exception as e:
            self.logger.error(f"Error updating email details: {e}")
            # Fallback to basic display
            self.subject_label.setText("Error loading email")
            self.sender_label.setText("Unknown sender")
            self.body_browser.setPlainText("Error loading email content")
    
    def _create_responsive_email_body(self, email_data: dict) -> str:
        """Create responsive HTML content for email body."""
        try:
            body_content = email_data.get('body', email_data.get('preview', 'No content available'))
            
            # Create responsive HTML with proper styling
            html_content = f"""
            <html>
            <head>
                <style>
                    body {{
                        font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
                        font-size: 14px;
                        line-height: 1.6;
                        color: #333;
                        margin: 0;
                        padding: 0;
                        word-wrap: break-word;
                        overflow-wrap: break-word;
                    }}
                    
                    .email-content {{
                        max-width: 100%;
                        padding: 10px;
                    }}
                    
                    p {{
                        margin: 0 0 12px 0;
                        word-wrap: break-word;
                    }}
                    
                    img {{
                        max-width: 100%;
                        height: auto;
                    }}
                    
                    table {{
                        max-width: 100%;
                        table-layout: fixed;
                        word-wrap: break-word;
                    }}
                    
                    pre {{
                        white-space: pre-wrap;
                        word-wrap: break-word;
                        overflow-x: auto;
                        background-color: #f5f5f5;
                        padding: 10px;
                        border-radius: 4px;
                        font-size: 12px;
                    }}
                    
                    blockquote {{
                        border-left: 3px solid #0078d4;
                        margin: 10px 0;
                        padding-left: 15px;
                        color: #666;
                        font-style: italic;
                    }}
                    
                    a {{
                        color: #0078d4;
                        text-decoration: none;
                        word-wrap: break-word;
                    }}
                    
                    a:hover {{
                        text-decoration: underline;
                    }}
                    
                    @media (max-width: 600px) {{
                        body {{
                            font-size: 13px;
                        }}
                        
                        .email-content {{
                            padding: 8px;
                        }}
                    }}
                </style>
            </head>
            <body>
                <div class="email-content">
                    {body_content}
                </div>
            </body>
            </html>
            """
            
            return html_content
            
        except Exception as e:
            self.logger.error(f"Error creating responsive email body: {e}")
            return f"<p>Error loading email content: {str(e)}</p>"
            
        except Exception as e:
            # Fallback to direct update if animation fails
            self.logger.debug(f"Email details animation failed: {e}")
            self._update_email_details_direct(email_data)
    
    def _update_email_details_direct(self, email_data: dict):
        """Update email details display directly without animation."""
        # Update subject
        self.subject_label.setText(email_data.get('subject', 'No Subject'))
        
        # Update sender
        sender = email_data.get('sender', 'Unknown Sender')
        self.sender_label.setText(f"From: {sender}")
        
        # Create full email body content
        full_body = self._create_full_email_body(email_data)
        self.body_browser.setHtml(full_body)
    
    def _create_full_email_body(self, email_data: dict) -> str:
        """Create full HTML email body content with enhanced formatting."""
        preview = email_data.get('preview', '')
        timestamp = email_data.get('timestamp', 'Unknown')
        source = email_data.get('source', 'unknown')
        
        # Create realistic email content based on the preview and subject
        full_body = f"<div style='font-family: Arial, sans-serif; line-height: 1.6; color: #333;'>"
        
        # Add email metadata
        full_body += f"""
        <div style='background-color: #f8f9fa; padding: 10px; border-radius: 5px; margin-bottom: 15px; font-size: 12px; color: #6c757d;'>
            <strong>📅 Received:</strong> {timestamp}<br>
            <strong>📧 Source:</strong> {source.title()}<br>
        """
        
        # Add Gmail-specific metadata
        if source == 'gmail':
            labels = email_data.get('labels', [])
            if labels:
                user_labels = [label for label in labels if not label.startswith('CATEGORY_') and label not in ['INBOX', 'UNREAD', 'IMPORTANT']]
                if user_labels:
                    full_body += f"<strong>🏷️ Labels:</strong> {', '.join(user_labels[:3])}<br>"
            
            thread_id = email_data.get('thread_id', '')
            if thread_id:
                full_body += f"<strong>🧵 Thread ID:</strong> {thread_id[:8]}...<br>"
        
        full_body += "</div>"
        
        # Add main email content
        full_body += f"<div style='margin-bottom: 20px;'>{preview}</div>"
        
        # Add realistic extended content based on subject
        subject = email_data.get('subject', '').lower()
        
        if "meeting" in subject:
            full_body += """
            <div style='background-color: #e8f4fd; padding: 15px; border-left: 4px solid #007bff; margin: 15px 0;'>
                <h4 style='margin-top: 0; color: #007bff;'>📅 Meeting Details</h4>
                <p><strong>Date:</strong> Tomorrow, 2:00 PM - 3:30 PM</p>
                <p><strong>Location:</strong> Conference Room A</p>
                <p><strong>Agenda:</strong></p>
                <ul>
                    <li>Q1 Goals Review</li>
                    <li>Budget Planning</li>
                    <li>Team Assignments</li>
                </ul>
                <p>Please confirm your attendance by replying to this email.</p>
            </div>
            <p>Looking forward to seeing everyone there!</p>
            <p>Best regards,<br>John Doe</p>
            """
        
        elif "project" in subject:
            full_body += """
            <div style='background-color: #f0f8f0; padding: 15px; border-left: 4px solid #28a745; margin: 15px 0;'>
                <h4 style='margin-top: 0; color: #28a745;'>📊 Project Status</h4>
                <p><strong>Current Progress:</strong></p>
                <ul style='list-style-type: none; padding-left: 0;'>
                    <li>[OK] Wireframes completed</li>
                    <li>[OK] Design mockups approved</li>
                    <li>🔄 Frontend development in progress (75%)</li>
                    <li>[WAIT] Backend API development pending</li>
                </ul>
                <p><strong>Next Steps:</strong></p>
                <ul>
                    <li>Complete responsive design</li>
                    <li>Begin user testing phase</li>
                    <li>Prepare staging environment</li>
                </ul>
                <p><strong>Expected Completion:</strong> End of month</p>
            </div>
            <p>If you have any questions or concerns, please don't hesitate to reach out.</p>
            <p>Best regards,<br>Sarah Smith<br>Project Manager</p>
            """
        
        elif "invoice" in subject:
            full_body += """
            <div style='background-color: #fff3cd; padding: 15px; border-left: 4px solid #ffc107; margin: 15px 0;'>
                <h4 style='margin-top: 0; color: #856404;'>💰 Invoice Details</h4>
                <table style='width: 100%; border-collapse: collapse;'>
                    <tr><td><strong>Invoice Number:</strong></td><td>#12345</td></tr>
                    <tr><td><strong>Amount:</strong></td><td>$2,500.00</td></tr>
                    <tr><td><strong>Due Date:</strong></td><td>January 30, 2024</td></tr>
                    <tr><td><strong>Payment Methods:</strong></td><td>Bank transfer, Credit card</td></tr>
                </table>
            </div>
            <p>Please process payment by the due date to avoid any late fees.</p>
            <p>For questions regarding this invoice, please contact our accounting department at accounting@company.com</p>
            <p>Thank you for your business!</p>
            """
        
        elif "welcome" in subject:
            full_body += """
            <div style='background-color: #e8f5e8; padding: 15px; border-left: 4px solid #28a745; margin: 15px 0;'>
                <h4 style='margin-top: 0; color: #28a745;'>[SUCCESS] Welcome to Our Service!</h4>
                <p>We're excited to have you on board. Here's how to get started:</p>
                <ol>
                    <li><strong>Complete your profile</strong> - Add your information and preferences</li>
                    <li><strong>Explore features</strong> - Take a tour of our platform</li>
                    <li><strong>Connect with support</strong> - We're here to help 24/7</li>
                </ol>
            </div>
            <div style='text-align: center; margin: 20px 0;'>
                <a href='#' style='background-color: #007bff; color: white; padding: 12px 24px; text-decoration: none; border-radius: 5px; display: inline-block;'>Get Started Now</a>
            </div>
            <p>If you have any questions, don't hesitate to reach out to our support team.</p>
            <p>Welcome aboard!<br>The Support Team</p>
            """
        
        elif "security" in subject:
            full_body += """
            <div style='background-color: #f8d7da; padding: 15px; border-left: 4px solid #dc3545; margin: 15px 0;'>
                <h4 style='margin-top: 0; color: #721c24;'>🔒 Security Alert</h4>
                <p><strong>New login detected:</strong></p>
                <ul>
                    <li><strong>Device:</strong> Chrome on Windows</li>
                    <li><strong>Location:</strong> New York, NY</li>
                    <li><strong>Time:</strong> Today at 3:45 PM</li>
                    <li><strong>IP Address:</strong> 192.168.1.100</li>
                </ul>
                <p>If this was you, no action is needed. If you don't recognize this activity, please:</p>
                <ol>
                    <li>Change your password immediately</li>
                    <li>Review your account activity</li>
                    <li>Contact our security team</li>
                </ol>
            </div>
            <p>Your account security is our top priority.</p>
            <p>Best regards,<br>Security Team</p>
            """
        
        else:
            # Generic content for other emails
            full_body += """
            <div style='background-color: #f8f9fa; padding: 15px; border-radius: 5px; margin: 15px 0;'>
                <p>This is additional email content that would typically be included in a full email message.</p>
                <p>Email automation features allow you to:</p>
                <ul>
                    <li>Generate professional replies using AI</li>
                    <li>Compose new emails with AI assistance</li>
                    <li>Manage your email workflow efficiently</li>
                </ul>
            </div>
            <p>Thank you for using our email automation system!</p>
            """
        
        full_body += "</div>"
        return full_body
    
    def _on_generate_reply_clicked(self):
        """Handle generate reply button click with enhanced UX."""
        if not self.selected_email:
            from PySide6.QtWidgets import QMessageBox
            QMessageBox.warning(
                self,
                "No Email Selected",
                "Please select an email from the list to generate a reply."
            )
            return
        
        # Show loading indicator
        self._show_reply_generation_progress()
        
        # Emit signal for reply generation
        self.reply_requested.emit(self.selected_email)
        
        self.logger.info(f"Reply generation requested for: {self.selected_email.get('subject', 'No Subject')}")
    
    def _show_reply_generation_progress(self):
        """Show progress dialog for reply generation."""
        from PySide6.QtWidgets import QProgressDialog
        from PySide6.QtCore import QTimer
        
        # Show progress dialog
        self.reply_progress = QProgressDialog("Generating AI reply...", "Cancel", 0, 100, self)
        self.reply_progress.setWindowModality(Qt.WindowModal)
        self.reply_progress.setMinimumDuration(0)
        self.reply_progress.setValue(0)
        self.reply_progress.show()
        
        # Disable reply button during generation
        self.reply_button.setEnabled(False)
        self.reply_button.setText("🧠 Generating...")
        
        # Create timer for progress updates
        self.reply_timer = QTimer()
        self.reply_progress_value = 0
        self.reply_stages = [
            "Analyzing email content...",
            "Understanding context...",
            "Generating professional response...",
            "Refining reply content...",
            "Finalizing reply..."
        ]
        self.reply_stage_index = 0
        
        def update_reply_progress():
            self.reply_progress_value += 20
            self.reply_progress.setValue(self.reply_progress_value)
            
            # Update stage message
            if self.reply_stage_index < len(self.reply_stages):
                self.reply_progress.setLabelText(self.reply_stages[self.reply_stage_index])
                self.reply_stage_index += 1
            
            if self.reply_progress_value >= 100:
                self.reply_timer.stop()
                self.reply_progress.close()
                self._complete_reply_generation()
        
        self.reply_timer.timeout.connect(update_reply_progress)
        self.reply_timer.start(400)  # Update every 400ms
        
        # Handle cancel button
        def on_reply_cancel():
            self.reply_timer.stop()
            self._reset_reply_button()
            self.logger.info("Reply generation cancelled by user")
        
        self.reply_progress.canceled.connect(on_reply_cancel)
    
    def _complete_reply_generation(self):
        """Complete reply generation and show compose dialog."""
        try:
            # Create reply data
            reply_data = self._create_reply_data(self.selected_email)
            
            # Show compose dialog with reply data
            compose_dialog = ComposeEmailDialog(self, reply_data)
            compose_dialog.email_send_requested.connect(self._on_email_send_requested)
            compose_dialog.draft_generation_requested.connect(self._on_draft_generation_requested)
            
            # Show dialog
            if compose_dialog.exec() == QDialog.Accepted:
                self.logger.info("Reply composed and sent")
            
        except Exception as e:
            from PySide6.QtWidgets import QMessageBox
            QMessageBox.critical(
                self,
                "Reply Generation Error",
                f"Failed to generate reply:\n\n{str(e)}\n\nPlease try again."
            )
            self.logger.error(f"Error in reply generation: {e}")
        
        finally:
            self._reset_reply_button()
    
    def _create_reply_data(self, email_data: dict) -> dict:
        """Create reply data from selected email."""
        original_subject = email_data.get('subject', 'No Subject')
        reply_subject = f"Re: {original_subject}" if not original_subject.startswith('Re:') else original_subject
        
        sender = email_data.get('sender', 'Unknown Sender')
        # Extract email address from sender
        if '<' in sender and '>' in sender:
            reply_to = sender.split('<')[1].split('>')[0]
        else:
            reply_to = sender
        
        # Create reply body with original message
        original_body = email_data.get('preview', '')
        reply_body = f"\n\n--- Original Message ---\nFrom: {sender}\nSubject: {original_subject}\n\n{original_body}"
        
        return {
            "to": reply_to,
            "subject": reply_subject,
            "body": reply_body
        }
    
    def _reset_reply_button(self):
        """Reset reply button to original state."""
        self.reply_button.setEnabled(True)
        self.reply_button.setText("🧠 Generate Reply")
    
    def _on_compose_clicked(self):
        """Handle compose button click with OAuth status checking and enhanced UX."""
        try:
            # Check OAuth status before opening compose dialog
            oauth_status = self._get_oauth_status_info()
            
            if not oauth_status['configured']:
                # Gmail OAuth not configured
                from PySide6.QtWidgets import QMessageBox
                reply = QMessageBox.question(
                    self,
                    "Gmail Not Configured",
                    "Gmail OAuth is not configured for sending emails.\n\n"
                    "Would you like to open the email settings to configure Gmail OAuth?",
                    QMessageBox.Yes | QMessageBox.No,
                    QMessageBox.Yes
                )
                
                if reply == QMessageBox.Yes:
                    self.open_email_settings()
                return
            
            if not oauth_status['authenticated']:
                # Gmail OAuth configured but not authenticated
                from PySide6.QtWidgets import QMessageBox
                reply = QMessageBox.question(
                    self,
                    "Gmail Authentication Required",
                    f"Gmail authentication is required to send emails.\n\n"
                    f"Status: {oauth_status['status_message']}\n\n"
                    "Would you like to open the email settings to authenticate?",
                    QMessageBox.Yes | QMessageBox.No,
                    QMessageBox.Yes
                )
                
                if reply == QMessageBox.Yes:
                    self.open_email_settings()
                return
            
            # OAuth is configured and authenticated, proceed with compose
            self.logger.info(f"Opening compose dialog (authenticated as {oauth_status['user_email']})")
            
            # Show compose dialog with OAuth user info
            compose_dialog = ComposeEmailDialog(self)
            
            # Set the sender email from OAuth info
            if oauth_status['user_email']:
                compose_dialog.set_sender_email(oauth_status['user_email'])
            
            # Connect signals
            compose_dialog.email_send_requested.connect(self._on_email_send_requested)
            compose_dialog.draft_generation_requested.connect(self._on_draft_generation_requested)
            
            # Show dialog
            if compose_dialog.exec() == QDialog.Accepted:
                self.logger.info("New email composed and sent")
                
                # Refresh emails to show sent email if it appears in Gmail
                QTimer.singleShot(2000, self._refresh_gmail_emails)  # Refresh after 2 seconds
            
            # Emit signal
            self.compose_requested.emit()
            
        except Exception as e:
            from PySide6.QtWidgets import QMessageBox
            QMessageBox.critical(
                self,
                "Compose Error",
                f"Failed to open compose dialog:\n\n{str(e)}\n\nPlease try again."
            )
            self.logger.error(f"Error opening compose dialog: {e}")
    
    def _on_email_send_requested(self, email_data: dict):
        """Handle email send request from compose dialog."""
        try:
            # Forward to email service
            if self.email_service:
                success = self.email_service.send_email(
                    email_data.get('to', ''),
                    email_data.get('subject', ''),
                    email_data.get('body', '')
                )
                
                if success:
                    from PySide6.QtWidgets import QMessageBox
                    QMessageBox.information(
                        self,
                        "[OK] Email Sent",
                        f"Email sent successfully to {email_data.get('to', 'recipient')}!"
                    )
                    self.logger.info(f"Email sent successfully to {email_data.get('to', 'recipient')}")
                else:
                    from PySide6.QtWidgets import QMessageBox
                    QMessageBox.critical(
                        self,
                        "[ERROR] Send Failed",
                        f"Failed to send email to {email_data.get('to', 'recipient')}.\n\nPlease check your email configuration."
                    )
                    self.logger.error(f"Failed to send email to {email_data.get('to', 'recipient')}")
            
        except Exception as e:
            from PySide6.QtWidgets import QMessageBox
            QMessageBox.critical(
                self,
                "Send Error",
                f"Error sending email:\n\n{str(e)}\n\nPlease try again."
            )
            self.logger.error(f"Error sending email: {e}")
    
    def _on_draft_generation_requested(self, draft_data: dict):
        """Handle AI draft generation request from compose dialog."""
        try:
            # This would integrate with the AI service for content generation
            # For now, generate a placeholder response
            generated_content = self._generate_placeholder_content(draft_data)
            
            # Find the compose dialog and set the generated content
            for widget in self.findChildren(ComposeEmailDialog):
                if widget.isVisible():
                    widget.set_generated_content_with_animation(generated_content)
                    break
            
        except Exception as e:
            self.logger.error(f"Error generating AI draft: {e}")
    
    def _generate_placeholder_content(self, draft_data: dict) -> str:
        """Generate placeholder AI content for demonstration."""
        to = draft_data.get('to', '')
        subject = draft_data.get('subject', '')
        current_message = draft_data.get('current_message', '')
        
        # Generate contextual content based on subject
        if 'meeting' in subject.lower():
            return f"""Dear {to.split('@')[0] if '@' in to else 'Colleague'},

Thank you for your email regarding the meeting. I would be happy to attend and contribute to the discussion.

I have reviewed the agenda items and have prepared some initial thoughts on:
• Q1 Goals Review - I believe we should focus on achievable milestones
• Budget Planning - I have some cost-saving suggestions to share
• Team Assignments - I'm available for additional responsibilities

Please let me know if you need any materials prepared in advance.

Looking forward to our productive session.

Best regards"""
        
        elif 'project' in subject.lower():
            return f"""Hi {to.split('@')[0] if '@' in to else 'Team'},

Thank you for the comprehensive project update. The progress looks excellent!

I'm particularly impressed with the completion of the wireframes and design mockups. The 75% progress on frontend development is also encouraging.

For the upcoming phases, I'd like to suggest:
• Conducting user testing in parallel with backend development
• Setting up automated testing for the staging environment
• Planning a soft launch strategy

Please keep me updated on any blockers or additional resources needed.

Best regards"""
        
        else:
            return f"""Dear {to.split('@')[0] if '@' in to else 'Recipient'},

Thank you for your email. I appreciate you reaching out.

{current_message if current_message else 'I wanted to follow up on our previous discussion and provide you with the information you requested.'}

I'm available to discuss this further at your convenience. Please let me know if you have any questions or need additional clarification.

Looking forward to hearing from you.

Best regards"""
    
    def _apply_theme(self):
        """Apply theme styling to the email automation tab."""
        if not self.theme_manager:
            return
        
        try:
            # Apply theme to main components
            theme = self.theme_manager.get_current_theme()
            
            # Style the splitter
            self.splitter.setStyleSheet(f"""
                QSplitter::handle {{
                    background-color: {theme.get('border', '#dee2e6')};
                    width: 2px;
                }}
            """)
            
            # Style the compose button (now in top action bar)
            if hasattr(self, 'compose_button'):
                self.compose_button.setStyleSheet("""
                    QPushButton {
                        background-color: #0078d4;
                        color: white;
                        border: none;
                        padding: 12px 20px;
                        border-radius: 8px;
                        font-weight: bold;
                        font-size: 14px;
                        min-width: 180px;
                        min-height: 45px;
                    }
                    QPushButton:hover {
                        background-color: #106ebe;
                    }
                    QPushButton:pressed {
                        background-color: #005a9e;
                    }
                """)
            
        except Exception as e:
            self.logger.debug(f"Theme application failed: {e}")
    
    def _on_theme_changed(self):
        """Handle theme change event."""
        self._apply_theme()
        
        # Update all email preview widgets
        for i in range(self.email_list.count()):
            item = self.email_list.item(i)
            widget = self.email_list.itemWidget(item)
            if isinstance(widget, EmailPreviewWidget):
                widget.apply_theme()
    

    
    def keyPressEvent(self, event):
        """Handle keyboard shortcuts for email automation."""
        from PySide6.QtCore import Qt
        
        # F5 to refresh emails
        if event.key() == Qt.Key_F5:
            self._refresh_gmail_emails()
            event.accept()
            return
        
        # Ctrl+N to compose new email
        if event.key() == Qt.Key_N and event.modifiers() == Qt.ControlModifier:
            self._on_compose_clicked()
            event.accept()
            return
        
        # Ctrl+R to reply to selected email
        if event.key() == Qt.Key_R and event.modifiers() == Qt.ControlModifier:
            if self.reply_button.isEnabled():
                self._on_generate_reply_clicked()
            event.accept()
            return
        
        # Delete key to delete selected email (placeholder)
        if event.key() == Qt.Key_Delete:
            current_item = self.email_list.currentItem()
            if current_item:
                from PySide6.QtWidgets import QMessageBox
                QMessageBox.information(
                    self,
                    "Delete Email",
                    "Email deletion feature coming soon!\n\nThis would integrate with your email provider's API."
                )
            event.accept()
            return
        
        # Call parent implementation
        super().keyPressEvent(event)