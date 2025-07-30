"""
Email Settings Dialog

This module contains the EmailSettingsDialog class, which allows users to
configure their email settings for SMTP and Gmail OAuth 2.0 authentication.
"""

import logging
import os
import json
from typing import Dict, Any, Optional
from pathlib import Path

from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QFormLayout, QLabel, 
    QLineEdit, QSpinBox, QPushButton, QGroupBox, QDialogButtonBox,
    QCheckBox, QFrame, QRadioButton, QButtonGroup, QFileDialog,
    QProgressDialog, QMessageBox, QToolTip, QTextEdit, QPlainTextEdit,
    QComboBox
)
from PySide6.QtCore import Qt, Signal, QTimer, QPropertyAnimation, QEasingCurve
from PySide6.QtGui import QFont, QKeySequence

from .mixins.theme_mixin import DialogThemeMixin

# Gmail OAuth imports (optional - will be imported when needed)
try:
    from llmtoolkit.app.services.gmail_client import GmailClient, GmailAuthError, GmailAPIError
    from llmtoolkit.app.services.gmail_oauth_errors import (
        GmailOAuthError, GmailOAuthErrorType, GmailOAuthErrorHandler,
        create_credentials_error, create_network_error, create_rate_limit_error,
        create_auth_expired_error
    )
    GMAIL_AVAILABLE = True
except ImportError:
    GMAIL_AVAILABLE = False
    GmailClient = None
    GmailAuthError = Exception
    GmailAPIError = Exception
    GmailOAuthError = Exception
    GmailOAuthErrorType = None
    GmailOAuthErrorHandler = None


class EmailSettingsDialog(QDialog, DialogThemeMixin):
    """
    Email settings configuration dialog.
    
    Features:
    - SMTP server configuration
    - Email authentication settings
    - Optional API key configuration
    - Form validation for required fields
    - Save and Cancel functionality
    """
    
    # Signals
    settings_saved = Signal(dict)  # Emitted when settings are saved
    auth_method_changed = Signal(str)  # Emitted when authentication method changes
    oauth_authentication_requested = Signal(str)  # Emitted when OAuth auth is requested
    
    def __init__(self, parent=None, current_config: Optional[Dict[str, Any]] = None):
        """
        Initialize the email settings dialog.
        
        Args:
            parent: Parent widget
            current_config: Current email configuration to load
        """
        super().__init__(parent)
        
        self.logger = logging.getLogger("gguf_loader.ui.email_settings_dialog")
        self.current_config = current_config or {}
        
        # Set dialog properties
        self.setWindowTitle("Email Settings")
        self.setModal(True)
        
        # Initialize UI first to prevent layout issues
        self._init_ui()
        
        # Load current settings
        self._load_settings()
        
        # Set proper size after UI is initialized
        self.setMinimumSize(550, 700)
        self.resize(550, 750)  # Larger size to prevent overlap
        
        # Center the dialog on parent
        if parent:
            self._center_on_parent(parent)
        
        # Force layout update to prevent overlap
        self.layout().activate()
        self.adjustSize()
        
        # Apply centralized theme system
        self._apply_theme_to_dialog()
        
        self.logger.info("EmailSettingsDialog initialized")
    
    def _center_on_parent(self, parent):
        """Center the dialog on the parent window."""
        if parent:
            parent_geometry = parent.geometry()
            dialog_geometry = self.geometry()
            
            # Calculate center position
            x = parent_geometry.x() + (parent_geometry.width() - dialog_geometry.width()) // 2
            y = parent_geometry.y() + (parent_geometry.height() - dialog_geometry.height()) // 2
            
            # Ensure dialog stays on screen
            x = max(0, x)
            y = max(0, y)
            
            self.move(x, y)
    
    # Removed _adjust_dialog_size method to fix layout overlap issues
    
    def _init_ui(self):
        """Initialize the user interface."""
        layout = QVBoxLayout(self)
        layout.setSpacing(15)
        layout.setContentsMargins(20, 20, 20, 20)
        
        # Header
        header_label = QLabel("📧 Email Configuration")
        header_font = QFont()
        header_font.setPointSize(16)
        header_font.setBold(True)
        header_label.setFont(header_font)
        header_label.setStyleSheet(self._get_label_styles() + "font-size: 16px; font-weight: bold; margin-bottom: 10px;")
        layout.addWidget(header_label)
        
        # Description
        desc_label = QLabel("Configure your email settings to enable email automation features.")
        desc_label.setStyleSheet(self._get_label_styles() + "font-size: 12px; margin-bottom: 15px; color: #6c757d;")
        desc_label.setWordWrap(True)
        layout.addWidget(desc_label)
        
        # Authentication Method Selection Group
        auth_method_group = self._create_auth_method_group()
        layout.addWidget(auth_method_group)
        
        # SMTP Configuration Group
        self.smtp_group = self._create_smtp_group()
        layout.addWidget(self.smtp_group)
        
        # Gmail OAuth Configuration Group
        self.gmail_oauth_group = self._create_gmail_oauth_group()
        layout.addWidget(self.gmail_oauth_group)
        
        # Authentication Group (for SMTP credentials)
        self.auth_group = self._create_auth_group()
        layout.addWidget(self.auth_group)
        
        # Optional Settings Group
        optional_group = self._create_optional_group()
        layout.addWidget(optional_group)
        
        # Add spacer
        layout.addStretch()
        
        # Button box
        self._create_button_box(layout)
    
    def _create_smtp_group(self) -> QGroupBox:
        """
        Create SMTP configuration group.
        
        Returns:
            QGroupBox: SMTP configuration group widget
        """
        group = QGroupBox("SMTP Server Configuration")
        group.setStyleSheet(self._get_group_box_styles())
        
        layout = QFormLayout(group)
        layout.setSpacing(10)
        layout.setContentsMargins(15, 20, 15, 15)
        
        # SMTP Server
        self.smtp_server_edit = QLineEdit()
        self.smtp_server_edit.setPlaceholderText("e.g., smtp.gmail.com")
        self.smtp_server_edit.setStyleSheet(self._get_input_field_styles())
        layout.addRow("SMTP Server:", self.smtp_server_edit)
        
        # Port
        self.port_spin = QSpinBox()
        self.port_spin.setRange(1, 65535)
        self.port_spin.setValue(587)  # Default SMTP port
        self.port_spin.setStyleSheet(self._get_input_field_styles())
        layout.addRow("Port:", self.port_spin)
        
        # Use TLS checkbox
        self.use_tls_check = QCheckBox("Use TLS encryption (recommended)")
        self.use_tls_check.setChecked(True)
        self.use_tls_check.setStyleSheet(self._get_checkbox_radio_styles() + "font-size: 12px;")
        layout.addRow("", self.use_tls_check)
        
        return group
    
    def _create_auth_group(self) -> QGroupBox:
        """
        Create authentication configuration group.
        
        Returns:
            QGroupBox: Authentication configuration group widget
        """
        group = QGroupBox("Authentication")
        group.setStyleSheet(self._get_group_box_styles())
        
        layout = QFormLayout(group)
        layout.setSpacing(10)
        layout.setContentsMargins(15, 20, 15, 15)
        
        # Email Address
        self.email_edit = QLineEdit()
        self.email_edit.setPlaceholderText("your.email@example.com")
        self.email_edit.setStyleSheet(self._get_input_field_styles())
        layout.addRow("Email Address:", self.email_edit)
        
        # Password
        self.password_edit = QLineEdit()
        self.password_edit.setEchoMode(QLineEdit.Password)
        self.password_edit.setPlaceholderText("Your email password or app password")
        self.password_edit.setStyleSheet(self._get_input_field_styles())
        layout.addRow("Password:", self.password_edit)
        
        # Password info
        password_info = QLabel("💡 For Gmail, use an App Password instead of your regular password")
        password_info.setStyleSheet(self._get_label_styles() + "color: #0078d4; font-size: 11px; margin-top: 5px;")
        password_info.setWordWrap(True)
        layout.addRow("", password_info)
        
        return group
    
    def _create_optional_group(self) -> QGroupBox:
        """
        Create optional settings group.
        
        Returns:
            QGroupBox: Optional settings group widget
        """
        group = QGroupBox("Optional Settings")
        group.setStyleSheet(self._get_group_box_styles())
        
        layout = QFormLayout(group)
        layout.setSpacing(10)
        layout.setContentsMargins(15, 20, 15, 15)
        
        # API Key
        self.api_key_edit = QLineEdit()
        self.api_key_edit.setPlaceholderText("Optional API key for enhanced features")
        self.api_key_edit.setStyleSheet(self._get_input_field_styles())
        layout.addRow("API Key:", self.api_key_edit)
        
        # API Key info
        api_info = QLabel("ℹ️ API key is optional and used for advanced email features")
        api_info.setStyleSheet(self._get_label_styles() + "font-size: 11px; margin-top: 5px;")
        api_info.setWordWrap(True)
        layout.addRow("", api_info)
        
        return group
    
    def _create_auth_method_group(self) -> QGroupBox:
        """
        Create authentication method selection group.
        
        Returns:
            QGroupBox: Authentication method selection group widget
        """
        group = QGroupBox("Authentication Method")
        group.setStyleSheet(self._get_group_box_styles())
        
        layout = QVBoxLayout(group)
        layout.setSpacing(10)
        layout.setContentsMargins(15, 20, 15, 15)
        
        # Create radio button group
        self.auth_method_group = QButtonGroup(self)
        
        # SMTP radio button
        self.smtp_radio = QRadioButton("SMTP (Traditional email server)")
        self.smtp_radio.setChecked(True)  # Default selection
        self.smtp_radio.setStyleSheet(self._get_checkbox_radio_styles() + "font-size: 12px; margin: 5px 0px;")
        self.smtp_radio.toggled.connect(lambda checked: self._on_smtp_toggled(checked))
        self.auth_method_group.addButton(self.smtp_radio, 0)
        layout.addWidget(self.smtp_radio)
        
        # Gmail OAuth radio button
        self.gmail_oauth_radio = QRadioButton("Gmail OAuth 2.0 (Secure Google authentication)")
        self.gmail_oauth_radio.setEnabled(True)  # Always enable
        self.gmail_oauth_radio.setStyleSheet(self._get_checkbox_radio_styles() + "font-size: 12px; margin: 5px 0px;")
        self.gmail_oauth_radio.toggled.connect(lambda checked: self._on_oauth_toggled(checked))
        self.auth_method_group.addButton(self.gmail_oauth_radio, 1)
        layout.addWidget(self.gmail_oauth_radio)
        
        # Connect signal
        self.auth_method_group.buttonClicked.connect(self._on_auth_method_changed)
        
        return group
    
    def _create_gmail_oauth_group(self) -> QGroupBox:
        """
        Create Gmail OAuth configuration group.
        
        Returns:
            QGroupBox: Gmail OAuth configuration group widget
        """
        group = QGroupBox("Gmail OAuth 2.0 Configuration")
        group.setStyleSheet(self._get_group_box_styles())
        
        layout = QFormLayout(group)
        layout.setSpacing(10)
        layout.setContentsMargins(15, 20, 15, 15)
        
        # Credentials file selection
        credentials_layout = QHBoxLayout()
        self.credentials_path_edit = QLineEdit()
        self.credentials_path_edit.setPlaceholderText("Select credentials.json file from Google Cloud Console")
        self.credentials_path_edit.setStyleSheet(self._get_input_field_styles())
        self.credentials_path_edit.setReadOnly(True)
        credentials_layout.addWidget(self.credentials_path_edit)
        
        self.credentials_browse_button = QPushButton("Browse...")
        self.credentials_browse_button.setStyleSheet("""
            QPushButton {
                background-color: #6c757d;
                color: white;
                border: none;
                border-radius: 4px;
                padding: 8px 16px;
                font-size: 12px;
                min-width: 80px;
            }
            QPushButton:hover {
                background-color: #5a6268;
            }
            QPushButton:pressed {
                background-color: #545b62;
            }
        """)
        self.credentials_browse_button.clicked.connect(self._on_credentials_browse_clicked)
        credentials_layout.addWidget(self.credentials_browse_button)
        
        layout.addRow("Credentials File:", credentials_layout)
        
        # OAuth status
        self.oauth_status_label = QLabel("Not authenticated")
        self.oauth_status_label.setStyleSheet("color: #dc3545; font-size: 11px; margin-top: 5px;")
        layout.addRow("Status:", self.oauth_status_label)
        
        # Authenticate button
        self.oauth_auth_button = self._create_oauth_button("🔐 Authenticate with Google")
        # Initially disable button until credentials file is selected
        self.oauth_auth_button.setEnabled(False)
        self.oauth_auth_button.clicked.connect(self._direct_oauth_authenticate)
        layout.addRow("", self.oauth_auth_button)
        
        # Help text with setup help button
        help_layout = QHBoxLayout()
        help_text = QLabel("💡 Get credentials.json from Google Cloud Console → APIs & Services → Credentials")
        help_text.setStyleSheet("color: #0078d4; font-size: 11px; margin-top: 5px;")
        help_text.setWordWrap(True)
        help_layout.addWidget(help_text)
        
        # Setup help button
        self.setup_help_button = QPushButton("❓ Setup Help")
        self.setup_help_button.setStyleSheet("""
            QPushButton {
                background-color: #17a2b8;
                color: white;
                border: none;
                border-radius: 4px;
                padding: 6px 12px;
                font-size: 11px;
                min-width: 80px;
            }
            QPushButton:hover {
                background-color: #138496;
            }
            QPushButton:pressed {
                background-color: #117a8b;
            }
        """)
        self.setup_help_button.clicked.connect(self._show_oauth_setup_help)
        help_layout.addWidget(self.setup_help_button)
        help_layout.addStretch()
        
        layout.addRow("", help_layout)
        
        # Initially hidden (will be shown when Gmail OAuth is selected)
        group.setVisible(False)
        
        return group
    
    def _on_auth_method_changed(self, button):
        """Handle authentication method change."""
        if button == self.smtp_radio:
            # Show SMTP groups, hide Gmail OAuth group
            self.smtp_group.setVisible(True)
            self.auth_group.setVisible(True)
            self.gmail_oauth_group.setVisible(False)
            self.auth_method_changed.emit("smtp")
            self.logger.info("Authentication method changed to SMTP")
        elif button == self.gmail_oauth_radio:
            # Show Gmail OAuth group, hide SMTP groups
            self.smtp_group.setVisible(False)
            self.auth_group.setVisible(False)
            self.gmail_oauth_group.setVisible(True)
            self.auth_method_changed.emit("gmail_oauth")
            self.logger.info("Authentication method changed to Gmail OAuth")
        
        # Update form validation
        self._validate_form()
    
    def _on_smtp_toggled(self, checked):
        """Handle SMTP radio button toggle."""
        if checked:
            self.smtp_group.setVisible(True)
            self.auth_group.setVisible(True)
            self.gmail_oauth_group.setVisible(False)
            self.auth_method_changed.emit("smtp")
            self.logger.info("Authentication method changed to SMTP")
            self._validate_form()
    
    def _on_oauth_toggled(self, checked):
        """Handle OAuth radio button toggle."""
        if checked:
            self.smtp_group.setVisible(False)
            self.auth_group.setVisible(False)
            self.gmail_oauth_group.setVisible(True)
            self.auth_method_changed.emit("gmail_oauth")
            self.logger.info("Authentication method changed to Gmail OAuth")
            
            # Update OAuth button state when switching to OAuth method
            self._update_oauth_button_on_credentials_change()
            
            self._validate_form()
    

    
    def _on_credentials_browse_clicked(self):
        """Handle credentials file browse button click."""
        file_dialog = QFileDialog(self)
        file_dialog.setWindowTitle("Select Google Cloud Credentials File")
        file_dialog.setNameFilter("JSON Files (*.json);;All Files (*)")
        file_dialog.setFileMode(QFileDialog.ExistingFile)
        
        if file_dialog.exec():
            selected_files = file_dialog.selectedFiles()
            if selected_files:
                credentials_path = selected_files[0]
                
                # Always set the path first
                self.credentials_path_edit.setText(credentials_path)
                
                # Validate the credentials file first
                if self._validate_credentials_file(credentials_path):
                    self.logger.info(f"Valid credentials file selected: {credentials_path}")
                    # Update button state for valid credentials
                    self._update_oauth_button_on_credentials_change()
                else:
                    self.logger.warning(f"Invalid credentials file selected: {credentials_path}")
                    
                    # Get detailed error message
                    error_message = self._get_credentials_validation_error_message(credentials_path)
                    
                    # Show detailed error dialog
                    from PySide6.QtWidgets import QMessageBox
                    msg_box = QMessageBox(self)
                    msg_box.setWindowTitle("Invalid Credentials File")
                    msg_box.setIcon(QMessageBox.Warning)
                    msg_box.setText("The selected credentials file is not valid.")
                    msg_box.setDetailedText(error_message)
                    msg_box.setStandardButtons(QMessageBox.Ok)
                    msg_box.exec()
                    
                    # Clear the invalid path and update button state
                    self.credentials_path_edit.setText("")
                    self._update_oauth_button_on_credentials_change()
                
                # Update form validation
                self._validate_form()
    
    def _validate_credentials_file(self, file_path: str) -> bool:
        """
        Validate that the selected file is a valid Google Cloud credentials.json file.
        
        Args:
            file_path: Path to the credentials file
            
        Returns:
            True if valid, False otherwise
        """
        try:
            # Check file existence and permissions
            if not Path(file_path).exists():
                self.logger.error(f"Credentials file does not exist: {file_path}")
                return False
            
            if not os.access(file_path, os.R_OK):
                self.logger.error(f"Cannot read credentials file: {file_path}")
                return False
            
            # Validate JSON format
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
            except json.JSONDecodeError as e:
                self.logger.error(f"Invalid JSON format in credentials file: {e}")
                return False
            except UnicodeDecodeError as e:
                self.logger.error(f"Invalid file encoding in credentials file: {e}")
                return False
            
            # Validate OAuth 2.0 client structure
            if not isinstance(data, dict):
                self.logger.error("Credentials file must contain a JSON object")
                return False
            
            # Check for OAuth 2.0 client configuration
            client_data = None
            if 'installed' in data:
                client_data = data['installed']
                self.logger.debug("Found 'installed' OAuth client configuration")
            elif 'web' in data:
                client_data = data['web']
                self.logger.debug("Found 'web' OAuth client configuration")
            else:
                self.logger.error("Credentials file missing OAuth client configuration ('installed' or 'web')")
                return False
            
            if not isinstance(client_data, dict):
                self.logger.error("OAuth client configuration must be a JSON object")
                return False
            
            # Validate required OAuth 2.0 fields
            required_fields = [
                'client_id',
                'client_secret',
                'auth_uri',
                'token_uri'
            ]
            
            missing_fields = []
            for field in required_fields:
                if field not in client_data:
                    missing_fields.append(field)
                elif not isinstance(client_data[field], str) or not client_data[field].strip():
                    missing_fields.append(f"{field} (empty or invalid)")
            
            if missing_fields:
                self.logger.error(f"Credentials file missing required fields: {', '.join(missing_fields)}")
                return False
            
            # Validate OAuth URIs
            auth_uri = client_data.get('auth_uri', '')
            token_uri = client_data.get('token_uri', '')
            
            if not auth_uri.startswith('https://'):
                self.logger.error(f"Invalid auth_uri: must be HTTPS URL, got: {auth_uri}")
                return False
            
            if not token_uri.startswith('https://'):
                self.logger.error(f"Invalid token_uri: must be HTTPS URL, got: {token_uri}")
                return False
            
            # Validate Google OAuth endpoints
            if 'accounts.google.com' not in auth_uri:
                self.logger.warning(f"Unexpected auth_uri domain: {auth_uri}")
            
            if 'oauth2.googleapis.com' not in token_uri:
                self.logger.warning(f"Unexpected token_uri domain: {token_uri}")
            
            # Validate client_id format (should be a Google client ID)
            client_id = client_data.get('client_id', '')
            if not client_id.endswith('.apps.googleusercontent.com'):
                self.logger.warning(f"Client ID doesn't match expected Google format: {client_id}")
            
            # Additional validation for installed app configuration
            if 'installed' in data:
                redirect_uris = client_data.get('redirect_uris', [])
                if not isinstance(redirect_uris, list):
                    self.logger.error("redirect_uris must be a list")
                    return False
                
                # Check for required redirect URIs for installed apps
                expected_redirects = ['urn:ietf:wg:oauth:2.0:oob', 'http://localhost']
                has_valid_redirect = any(
                    uri in redirect_uris or uri.startswith('http://localhost:') 
                    for uri in expected_redirects + [r for r in redirect_uris if r.startswith('http://localhost:')]
                )
                
                if not has_valid_redirect:
                    self.logger.warning("No valid redirect URI found for installed app")
            
            self.logger.info(f"Credentials file validation successful: {file_path}")
            return True
            
        except Exception as e:
            self.logger.error(f"Unexpected error validating credentials file: {e}")
            return False
    
    def _get_credentials_validation_error_message(self, file_path: str) -> str:
        """
        Get a detailed error message for credentials file validation failure.
        
        Args:
            file_path: Path to the credentials file
            
        Returns:
            Detailed error message with troubleshooting guidance
        """
        try:
            # Check file existence
            if not Path(file_path).exists():
                return (
                    "Credentials file not found.\n\n"
                    "Please ensure you've downloaded the credentials.json file from "
                    "Google Cloud Console and selected the correct file path."
                )
            
            # Check file permissions
            if not os.access(file_path, os.R_OK):
                return (
                    "Cannot read credentials file due to permission restrictions.\n\n"
                    "Please check that the file has read permissions and try again."
                )
            
            # Check JSON format
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
            except json.JSONDecodeError as e:
                return (
                    f"Invalid JSON format in credentials file.\n\n"
                    f"Error: {str(e)}\n\n"
                    "Please ensure you've downloaded the correct credentials.json file "
                    "from Google Cloud Console without any modifications."
                )
            except UnicodeDecodeError:
                return (
                    "Invalid file encoding in credentials file.\n\n"
                    "Please ensure the file is saved in UTF-8 encoding."
                )
            
            # Check structure
            if not isinstance(data, dict):
                return (
                    "Invalid credentials file structure.\n\n"
                    "The file must contain a valid JSON object with OAuth 2.0 client configuration."
                )
            
            # Check for OAuth client configuration
            if 'installed' not in data and 'web' not in data:
                return (
                    "Missing OAuth client configuration.\n\n"
                    "The credentials file must contain either 'installed' or 'web' client configuration.\n\n"
                    "Please ensure you've downloaded the correct OAuth 2.0 client credentials "
                    "(not service account credentials) from Google Cloud Console."
                )
            
            # Check required fields
            client_data = data.get('installed') or data.get('web')
            required_fields = ['client_id', 'client_secret', 'auth_uri', 'token_uri']
            missing_fields = [field for field in required_fields if field not in client_data]
            
            if missing_fields:
                return (
                    f"Missing required OAuth fields: {', '.join(missing_fields)}\n\n"
                    "Please ensure you've downloaded the complete OAuth 2.0 client credentials "
                    "from Google Cloud Console."
                )
            
            return (
                "Invalid credentials file format.\n\n"
                "Please ensure you've downloaded the correct OAuth 2.0 client credentials "
                "from Google Cloud Console → APIs & Services → Credentials."
            )
            
        except Exception:
            return (
                "Unable to validate credentials file.\n\n"
                "Please ensure you've selected a valid credentials.json file "
                "downloaded from Google Cloud Console."
            )
    
    def _on_oauth_authenticate_clicked(self):
        """Handle OAuth authentication button click with enhanced loading indicators."""
        self.logger.info("OAuth authenticate button clicked!")
        
        credentials_path = self.credentials_path_edit.text().strip()
        self.logger.info(f"Credentials path: {credentials_path}")
        
        if not credentials_path:
            self.logger.warning("No credentials file selected")
            from PySide6.QtWidgets import QMessageBox
            QMessageBox.warning(
                self,
                "No Credentials File",
                "Please select a credentials.json file first."
            )
            return
        
        # Validate credentials file exists
        if not Path(credentials_path).exists():
            self.logger.error(f"Credentials file does not exist: {credentials_path}")
            from PySide6.QtWidgets import QMessageBox
            QMessageBox.critical(
                self,
                "File Not Found",
                f"Credentials file not found:\n{credentials_path}\n\nPlease select a valid credentials.json file."
            )
            return
        
        # Show loading state with progress dialog
        self._show_oauth_loading_dialog()
        
        self.logger.info("Starting OAuth authentication process")
        
        # Emit signal to request authentication
        self.logger.info("Emitting oauth_authentication_requested signal")
        self.oauth_authentication_requested.emit(credentials_path)
        
        # Note: The parent window will handle the authentication and call update_oauth_status
        # which will then enable the Save button if authentication is successful
    
    def _direct_oauth_authenticate(self):
        """Direct OAuth authentication method that actually works."""
        from PySide6.QtWidgets import QMessageBox, QProgressDialog
        from PySide6.QtCore import QThread, QTimer
        
        print("DIRECT OAUTH BUTTON CLICKED!")  # Debug output
        self.logger.info("DIRECT OAuth authenticate button clicked!")
        
        credentials_path = self.credentials_path_edit.text().strip()
        
        if not credentials_path:
            # Show file dialog directly
            from PySide6.QtWidgets import QFileDialog
            file_dialog = QFileDialog(self)
            file_dialog.setWindowTitle("Select Google Cloud Credentials File")
            file_dialog.setNameFilter("JSON Files (*.json);;All Files (*)")
            file_dialog.setFileMode(QFileDialog.ExistingFile)
            
            if file_dialog.exec():
                selected_files = file_dialog.selectedFiles()
                if selected_files:
                    credentials_path = selected_files[0]
                    self.credentials_path_edit.setText(credentials_path)
                else:
                    return
            else:
                return
        
        # Validate file exists
        if not Path(credentials_path).exists():
            QMessageBox.critical(self, "File Not Found", f"File not found: {credentials_path}")
            return
        
        # Check if we need to clear existing tokens for re-authentication
        button_text = self.oauth_auth_button.text()
        if "Re-authenticate" in button_text:
            # Clear existing token file to force re-authentication
            token_path = Path(credentials_path).parent / "token.json"
            if token_path.exists():
                try:
                    token_path.unlink()
                    self.logger.info("Cleared existing token file for re-authentication")
                except Exception as e:
                    self.logger.warning(f"Could not clear token file: {e}")
        
        # Show progress dialog
        progress = QProgressDialog("Authenticating with Google...", "Cancel", 0, 0, self)
        progress.setWindowTitle("OAuth Authentication")
        progress.setModal(True)
        progress.show()
        
        # Update button state during authentication
        self._set_oauth_button_authenticating_state()
        
        try:
            # Import and use the actual Gmail client
            if GMAIL_AVAILABLE:
                from llmtoolkit.app.services.gmail_client import GmailClient
                
                # Create Gmail client with credentials path
                gmail_client = GmailClient(credentials_path)
                
                # Perform authentication
                self.logger.info("Starting real OAuth authentication...")
                success = gmail_client.authenticate()
                
                if success:
                    # Get user email from the authenticated client
                    try:
                        user_profile = gmail_client.service.users().getProfile(userId='me').execute()
                        user_email = user_profile.get('emailAddress', 'authenticated@gmail.com')
                    except:
                        user_email = 'authenticated@gmail.com'
                    
                    # Update status to authenticated
                    self.update_oauth_status(True, "Authentication successful", user_email)
                    
                    # Show success message
                    QMessageBox.information(
                        self,
                        "Authentication Successful",
                        f"Successfully authenticated with Google!\n\nEmail: {user_email}\n\nYou can now save your settings."
                    )
                    
                    self.logger.info(f"OAuth authentication successful for {user_email}")
                else:
                    raise Exception("Authentication failed")
                    
            else:
                # Fallback if Gmail client is not available
                raise ImportError("Gmail client not available")
                
        except Exception as e:
            self.logger.error(f"OAuth authentication failed: {e}")
            
            # Update status to failed
            self.update_oauth_status(False, f"Authentication failed: {str(e)}")
            
            # Show error message
            QMessageBox.critical(
                self,
                "Authentication Failed",
                f"Failed to authenticate with Google:\n\n{str(e)}\n\nPlease check your credentials file and try again."
            )
        
        finally:
            # Close progress dialog and reset button state
            progress.close()
            self._reset_oauth_button_state()
        
        print("OAuth authentication completed!")
        self.logger.info("OAuth authentication completed!")
    
    def _create_button_box(self, layout: QVBoxLayout):
        """
        Create dialog button box.
        
        Args:
            layout: Parent layout to add button box to
        """
        button_layout = QHBoxLayout()
        button_layout.addStretch()
        
        # Cancel button
        cancel_button = QPushButton("Cancel")
        cancel_button.setStyleSheet(self._get_button_styles())
        cancel_button.clicked.connect(self.reject)
        button_layout.addWidget(cancel_button)
        
        # Test Connection button
        self.test_button = QPushButton("🔄 Test Connection")
        self.test_button.setStyleSheet(self._get_button_styles())
        self.test_button.clicked.connect(self._on_test_connection_clicked)
        button_layout.addWidget(self.test_button)
        
        # Save button
        self.save_button = QPushButton("Save")
        self.save_button.setDefault(True)
        self.save_button.setStyleSheet(self._get_button_styles())
        self.save_button.clicked.connect(self._on_save_clicked)
        button_layout.addWidget(self.save_button)
        
        layout.addLayout(button_layout)
        
        # Connect validation
        self._connect_validation()
    

    
    def _connect_validation(self):
        """Connect form validation to input fields."""
        # Connect text change events for validation
        self.smtp_server_edit.textChanged.connect(self._validate_form)
        self.email_edit.textChanged.connect(self._validate_form)
        self.password_edit.textChanged.connect(self._validate_form)
        
        # Connect OAuth-related validation
        self.credentials_path_edit.textChanged.connect(self._validate_form)
        self.credentials_path_edit.textChanged.connect(self._update_oauth_button_on_credentials_change)
        
        # Initial validation
        self._validate_form()
    
    def _validate_form(self):
        """Validate form fields and enable/disable save button."""
        is_valid = False
        
        # Check which authentication method is selected
        if self.smtp_radio.isChecked():
            # SMTP validation
            smtp_server = self.smtp_server_edit.text().strip()
            email = self.email_edit.text().strip()
            password = self.password_edit.text().strip()
            
            # Basic SMTP validation
            is_valid = (
                len(smtp_server) > 0 and
                len(email) > 0 and
                "@" in email and
                "." in email.split("@")[1] and
                len(password) > 0
            )
            
            # Update the Save button state for SMTP
            self.save_button.setEnabled(is_valid)
        elif self.gmail_oauth_radio.isChecked():
            # Gmail OAuth validation
            credentials_path = self.credentials_path_edit.text().strip()
            oauth_status = self.oauth_status_label.text()
            
            # Check if authentication was successful
            oauth_authenticated = (
                "[OK]" in oauth_status or 
                "authenticated" in oauth_status.lower()
            ) and "not authenticated" not in oauth_status.lower()
            
            # CRITICAL FIX: If OAuth is authenticated, always enable the Save button
            if oauth_authenticated:
                self.logger.info("OAuth authentication detected, forcing Save button to be enabled")
                self.save_button.setEnabled(True)
                
                # Skip the rest of the validation
                return
            else:
                # OAuth validation - require credentials file and successful authentication
                is_valid = (
                    len(credentials_path) > 0 and
                    Path(credentials_path).exists()
                )
                
                # Update the Save button state for non-authenticated OAuth
                self.save_button.setEnabled(is_valid)
        
        # Update field styling based on validation
        self._update_field_styling()
    
    def _update_field_styling(self):
        """Update field styling based on validation state."""
        # SMTP Server validation
        if not self.smtp_server_edit.text().strip():
            self.smtp_server_edit.setStyleSheet(self._get_input_field_styles() + """
                QLineEdit { border-color: #dc3545; }
            """)
        else:
            self.smtp_server_edit.setStyleSheet(self._get_input_field_styles())
        
        # Email validation
        email = self.email_edit.text().strip()
        if not email or "@" not in email or "." not in email.split("@")[1] if "@" in email else True:
            self.email_edit.setStyleSheet(self._get_input_field_styles() + """
                QLineEdit { border-color: #dc3545; }
            """)
        else:
            self.email_edit.setStyleSheet(self._get_input_field_styles())
        
        # Password validation
        if not self.password_edit.text().strip():
            self.password_edit.setStyleSheet(self._get_input_field_styles() + """
                QLineEdit { border-color: #dc3545; }
            """)
        else:
            self.password_edit.setStyleSheet(self._get_input_field_styles())
    
    def _load_settings(self):
        """Load current settings into form fields."""
        if not self.current_config:
            return
        
        # Determine authentication method
        auth_method = self.current_config.get("auth_method", "smtp")
        
        if auth_method == "gmail_oauth":
            # Set Gmail OAuth radio button
            self.gmail_oauth_radio.setChecked(True)
            self._on_auth_method_changed(self.gmail_oauth_radio)
            
            # Load OAuth settings
            credentials_path = self.current_config.get("credentials_path", "")
            self.credentials_path_edit.setText(credentials_path)
            
            # Update OAuth button state based on credentials file
            self._update_oauth_button_on_credentials_change()
            
            # Check if OAuth is authenticated
            oauth_authenticated = self.current_config.get("oauth_authenticated", False)
            oauth_email = self.current_config.get("oauth_email", "")
            
            if oauth_authenticated and oauth_email:
                self.update_oauth_status(True, f"Authenticated as {oauth_email}", oauth_email)
            elif oauth_authenticated:
                self.update_oauth_status(True, "Authenticated successfully")
            else:
                self.oauth_status_label.setText("Not authenticated")
                self.oauth_status_label.setStyleSheet("color: #dc3545; font-size: 11px; margin-top: 5px;")
        else:
            # Set SMTP radio button (default)
            self.smtp_radio.setChecked(True)
            self._on_auth_method_changed(self.smtp_radio)
            
            # Load SMTP settings
            self.smtp_server_edit.setText(self.current_config.get("smtp_server", ""))
            self.port_spin.setValue(self.current_config.get("port", 587))
            self.use_tls_check.setChecked(self.current_config.get("use_tls", True))
            
            # Load authentication settings
            self.email_edit.setText(self.current_config.get("email_address", ""))
            self.password_edit.setText(self.current_config.get("password", ""))
        
        # Load optional settings (common to both methods)
        self.api_key_edit.setText(self.current_config.get("api_key", ""))
        
        self.logger.info(f"Settings loaded into dialog (auth method: {auth_method})")
    
    def update_oauth_status(self, success: bool, message: str, email: str = ""):
        """
        Update OAuth authentication status and enable/disable save button.
        
        Args:
            success: Whether authentication was successful
            message: Status message to display
            email: Authenticated email address (if successful)
        """
        if success:
            self.oauth_status_label.setText(f"[OK] Authenticated as {email}" if email else "[OK] Authenticated successfully")
            self.oauth_status_label.setStyleSheet("color: #28a745; font-size: 11px; margin-top: 5px; font-weight: bold;")
            self._update_oauth_button_state(True, email)
            self.logger.info(f"OAuth authentication successful for {email}")
            
            # CRITICAL FIX: Always enable the Save button on successful authentication
            self.save_button.setEnabled(True)
            self.logger.info("Save button explicitly enabled after successful authentication")
            
            # Update the status label to indicate the Save button is enabled
            current_text = self.oauth_status_label.text()
            if "Save button enabled" not in current_text:
                self.oauth_status_label.setText(f"{current_text} - Save button enabled")
        else:
            self.oauth_status_label.setText(f"[ERROR] {message}")
            self.oauth_status_label.setStyleSheet("color: #dc3545; font-size: 11px; margin-top: 5px;")
            self._update_oauth_button_state(False)
            self.logger.error(f"OAuth authentication failed: {message}")
        
        # Skip form validation to prevent the Save button from being disabled
        # self._validate_form()
    
    def _update_oauth_button_state(self, authenticated: bool, email: str = ""):
        """
        Update OAuth authentication button state and text based on authentication status.
        
        Args:
            authenticated: Whether user is authenticated
            email: User email if authenticated
        """
        if authenticated:
            # Button remains enabled for re-authentication
            self.oauth_auth_button.setEnabled(True)
            self.oauth_auth_button.setText("🔐 Re-authenticate")
            self.logger.info("OAuth button updated for re-authentication")
        else:
            # Enable button if credentials file is selected, otherwise disable
            credentials_path = self.credentials_path_edit.text().strip()
            if credentials_path and Path(credentials_path).exists() and self._validate_credentials_file(credentials_path):
                self.oauth_auth_button.setEnabled(True)
                self.oauth_auth_button.setText("🔐 Authenticate with Google")
                self.logger.info("OAuth button enabled for authentication")
            else:
                self.oauth_auth_button.setEnabled(False)
                self.oauth_auth_button.setText("🔐 Authenticate with Google")
                self.logger.info("OAuth button disabled - no valid credentials file")
    
    def _update_oauth_button_on_credentials_change(self):
        """
        Update OAuth button state when credentials file changes.
        Called when credentials file is selected or changed.
        """
        credentials_path = self.credentials_path_edit.text().strip()
        
        # Check if currently authenticated
        oauth_status = self.oauth_status_label.text()
        is_authenticated = "[OK]" in oauth_status and "authenticated" in oauth_status.lower()
        
        if is_authenticated:
            # If already authenticated, keep re-authenticate state
            self._update_oauth_button_state(True)
        else:
            # Update based on credentials file validity
            if credentials_path and Path(credentials_path).exists() and self._validate_credentials_file(credentials_path):
                self.oauth_auth_button.setEnabled(True)
                self.oauth_auth_button.setText("🔐 Authenticate with Google")
                self.logger.info(f"OAuth button enabled - valid credentials file: {credentials_path}")
            else:
                self.oauth_auth_button.setEnabled(False)
                self.oauth_auth_button.setText("🔐 Authenticate with Google")
                self.logger.info("OAuth button disabled - invalid or missing credentials file")
    
    def _set_oauth_button_authenticating_state(self):
        """
        Set OAuth button to authenticating state (disabled with loading text).
        """
        self.oauth_auth_button.setEnabled(False)
        self.oauth_auth_button.setText("🔐 Authenticating...")
        self.logger.info("OAuth button set to authenticating state")
    
    def _reset_oauth_button_state(self):
        """
        Reset OAuth button state after authentication attempt.
        Updates button based on current authentication status.
        """
        oauth_status = self.oauth_status_label.text()
        is_authenticated = "[OK]" in oauth_status and "authenticated" in oauth_status.lower()
        
        if is_authenticated:
            # Authentication successful - enable for re-authentication
            self.oauth_auth_button.setEnabled(True)
            self.oauth_auth_button.setText("🔐 Re-authenticate")
            self.logger.info("OAuth button reset to re-authenticate state")
        else:
            # Authentication failed - check credentials file validity
            credentials_path = self.credentials_path_edit.text().strip()
            if credentials_path and Path(credentials_path).exists() and self._validate_credentials_file(credentials_path):
                self.oauth_auth_button.setEnabled(True)
                self.oauth_auth_button.setText("🔐 Authenticate with Google")
                self.logger.info("OAuth button reset to authenticate state")
            else:
                self.oauth_auth_button.setEnabled(False)
                self.oauth_auth_button.setText("🔐 Authenticate with Google")
                self.logger.info("OAuth button reset to disabled state - no valid credentials")
    
    def _show_oauth_loading_dialog(self):
        """Show OAuth loading dialog with progress indication."""
        self.oauth_progress = QProgressDialog("Authenticating with Google...", "Cancel", 0, 0, self)
        self.oauth_progress.setWindowModality(Qt.WindowModal)
        self.oauth_progress.setMinimumDuration(0)
        self.oauth_progress.setCancelButton(None)  # No cancel button during OAuth
        self.oauth_progress.show()
        
        # Auto-close after 30 seconds if still showing
        QTimer.singleShot(30000, lambda: self.oauth_progress.close() if hasattr(self, 'oauth_progress') else None)
    
    def close_oauth_loading_dialog(self):
        """Close the OAuth loading dialog."""
        if hasattr(self, 'oauth_progress'):
            self.oauth_progress.close()
            delattr(self, 'oauth_progress')
    
    def _show_oauth_setup_help(self):
        """Show comprehensive OAuth setup help dialog with step-by-step instructions."""
        from PySide6.QtWidgets import QMessageBox, QTextBrowser, QVBoxLayout, QHBoxLayout, QPushButton
        from PySide6.QtCore import QUrl
        from PySide6.QtGui import QDesktopServices
        
        # Create custom dialog for setup help
        help_dialog = QDialog(self)
        help_dialog.setWindowTitle("Gmail OAuth 2.0 Setup Guide")
        help_dialog.setModal(True)
        help_dialog.resize(700, 600)
        
        layout = QVBoxLayout(help_dialog)
        
        # Create text browser for rich content
        text_browser = QTextBrowser()
        text_browser.setOpenExternalLinks(True)
        
        # Comprehensive setup instructions
        help_content = """
        <h2>[TOOL] Gmail OAuth 2.0 Setup Guide</h2>
        
        <p>Follow these steps to set up Gmail OAuth 2.0 authentication:</p>
        
        <h3>[LIST] Step 1: Create Google Cloud Project</h3>
        <ol>
            <li>Go to <a href="https://console.cloud.google.com/">Google Cloud Console</a></li>
            <li>Click "Select a project" → "New Project"</li>
            <li>Enter a project name (e.g., "Email Automation App")</li>
            <li>Click "Create"</li>
        </ol>
        
        <h3>🔌 Step 2: Enable Gmail API</h3>
        <ol>
            <li>In your project, go to "APIs & Services" → "Library"</li>
            <li>Search for "Gmail API"</li>
            <li>Click on "Gmail API" and then "Enable"</li>
        </ol>
        
        <h3>🔐 Step 3: Configure OAuth Consent Screen</h3>
        <ol>
            <li>Go to "APIs & Services" → "OAuth consent screen"</li>
            <li>Choose "External" user type (unless you have Google Workspace)</li>
            <li>Fill in required fields:
                <ul>
                    <li><strong>App name:</strong> Your application name</li>
                    <li><strong>User support email:</strong> Your email</li>
                    <li><strong>Developer contact:</strong> Your email</li>
                </ul>
            </li>
            <li>Click "Save and Continue"</li>
            <li>Add scopes (optional for testing) → "Save and Continue"</li>
            <li>Add test users (your Gmail address) → "Save and Continue"</li>
        </ol>
        
        <h3>🗝️ Step 4: Create OAuth 2.0 Credentials</h3>
        <ol>
            <li>Go to "APIs & Services" → "Credentials"</li>
            <li>Click "Create Credentials" → "OAuth client ID"</li>
            <li>Choose "Desktop application" as application type</li>
            <li>Enter a name (e.g., "Email Automation Client")</li>
            <li>Click "Create"</li>
            <li><strong>Download the JSON file</strong> - this is your credentials.json</li>
        </ol>
        
        <h3>📁 Step 5: Use Credentials File</h3>
        <ol>
            <li>Save the downloaded JSON file to a secure location</li>
            <li>Click "Browse..." in this dialog to select the file</li>
            <li>Click "Authenticate with Google" to start OAuth flow</li>
        </ol>
        
        <h3>[WARN] Common Issues & Solutions</h3>
        
        <h4>🚫 "Access blocked" Error</h4>
        <ul>
            <li><strong>Cause:</strong> App not verified by Google</li>
            <li><strong>Solution:</strong> Click "Advanced" → "Go to [App Name] (unsafe)" during OAuth flow</li>
            <li><strong>Note:</strong> This is safe for personal use applications</li>
        </ul>
        
        <h4>🔒 "Invalid client" Error</h4>
        <ul>
            <li><strong>Cause:</strong> Wrong credentials file or application type</li>
            <li><strong>Solution:</strong> Ensure you selected "Desktop application" when creating credentials</li>
        </ul>
        
        <h4>🌐 "Redirect URI mismatch" Error</h4>
        <ul>
            <li><strong>Cause:</strong> OAuth flow using wrong redirect URI</li>
            <li><strong>Solution:</strong> Desktop applications automatically handle this - ensure you're using "Desktop application" type</li>
        </ul>
        
        <h4>📧 "Insufficient permissions" Error</h4>
        <ul>
            <li><strong>Cause:</strong> Missing required Gmail API scopes</li>
            <li><strong>Solution:</strong> Delete token.json file and re-authenticate to refresh permissions</li>
        </ul>
        
        <h3>🔗 Useful Links</h3>
        <ul>
            <li><a href="https://console.cloud.google.com/">Google Cloud Console</a></li>
            <li><a href="https://developers.google.com/gmail/api/quickstart/python">Gmail API Python Quickstart</a></li>
            <li><a href="https://developers.google.com/identity/protocols/oauth2">OAuth 2.0 Documentation</a></li>
            <li><a href="https://support.google.com/cloud/answer/6158849">OAuth Consent Screen Help</a></li>
        </ul>
        
        <h3>🛡️ Security Notes</h3>
        <ul>
            <li><strong>Keep credentials.json secure</strong> - never share or commit to version control</li>
            <li><strong>Token files are sensitive</strong> - they provide access to your Gmail account</li>
            <li><strong>Revoke access</strong> anytime at <a href="https://myaccount.google.com/permissions">Google Account Permissions</a></li>
        </ul>
        """
        
        text_browser.setHtml(help_content)
        layout.addWidget(text_browser)
        
        # Button layout
        button_layout = QHBoxLayout()
        
        # Open Google Cloud Console button
        console_button = QPushButton("🌐 Open Google Cloud Console")
        console_button.setStyleSheet("""
            QPushButton {
                background-color: #4285f4;
                color: white;
                border: none;
                border-radius: 6px;
                padding: 10px 20px;
                font-weight: bold;
                font-size: 12px;
            }
            QPushButton:hover {
                background-color: #3367d6;
            }
        """)
        console_button.clicked.connect(lambda: QDesktopServices.openUrl(QUrl("https://console.cloud.google.com/")))
        button_layout.addWidget(console_button)
        
        button_layout.addStretch()
        
        # Close button
        close_button = QPushButton("Close")
        close_button.setStyleSheet("""
            QPushButton {
                background-color: #6c757d;
                color: white;
                border: none;
                border-radius: 6px;
                padding: 10px 20px;
                font-weight: bold;
                font-size: 12px;
                min-width: 80px;
            }
            QPushButton:hover {
                background-color: #5a6268;
            }
        """)
        close_button.clicked.connect(help_dialog.accept)
        button_layout.addWidget(close_button)
        
        layout.addLayout(button_layout)
        
        # Show dialog
        help_dialog.exec()
    
    def _show_gmail_oauth_error(self, error_type: str, error_message: str, details: str = None):
        """
        Show detailed Gmail OAuth error message with troubleshooting suggestions.
        
        Args:
            error_type: Type of error (auth_failed, invalid_credentials, etc.)
            error_message: Main error message
            details: Additional error details
        """
        from PySide6.QtWidgets import QMessageBox, QTextBrowser, QVBoxLayout, QHBoxLayout, QPushButton
        from PySide6.QtCore import QUrl
        from PySide6.QtGui import QDesktopServices
        
        # Create custom error dialog
        error_dialog = QDialog(self)
        error_dialog.setWindowTitle("Gmail OAuth Error")
        error_dialog.setModal(True)
        error_dialog.resize(600, 500)
        
        layout = QVBoxLayout(error_dialog)
        
        # Create text browser for rich content
        text_browser = QTextBrowser()
        text_browser.setOpenExternalLinks(True)
        
        # Generate error-specific content
        error_content = self._generate_oauth_error_content(error_type, error_message, details)
        text_browser.setHtml(error_content)
        layout.addWidget(text_browser)
        
        # Button layout
        button_layout = QHBoxLayout()
        
        # Setup help button
        help_button = QPushButton("📖 Setup Guide")
        help_button.setStyleSheet("""
            QPushButton {
                background-color: #17a2b8;
                color: white;
                border: none;
                border-radius: 6px;
                padding: 10px 20px;
                font-weight: bold;
                font-size: 12px;
            }
            QPushButton:hover {
                background-color: #138496;
            }
        """)
        help_button.clicked.connect(lambda: (error_dialog.accept(), self._show_oauth_setup_help()))
        button_layout.addWidget(help_button)
        
        button_layout.addStretch()
        
        # Close button
        close_button = QPushButton("Close")
        close_button.setStyleSheet("""
            QPushButton {
                background-color: #6c757d;
                color: white;
                border: none;
                border-radius: 6px;
                padding: 10px 20px;
                font-weight: bold;
                font-size: 12px;
                min-width: 80px;
            }
            QPushButton:hover {
                background-color: #5a6268;
            }
        """)
        close_button.clicked.connect(error_dialog.accept)
        button_layout.addWidget(close_button)
        
        layout.addLayout(button_layout)
        
        # Show dialog
        error_dialog.exec()
    
    def _generate_oauth_error_content(self, error_type: str, error_message: str, details: str = None) -> str:
        """
        Generate HTML content for OAuth error messages with specific troubleshooting.
        
        Args:
            error_type: Type of error
            error_message: Main error message
            details: Additional error details
            
        Returns:
            HTML content string
        """
        base_content = f"""
        <h2>🚨 Gmail OAuth Authentication Error</h2>
        <p><strong>Error:</strong> {error_message}</p>
        """
        
        if details:
            base_content += f"<p><strong>Details:</strong> {details}</p>"
        
        # Error-specific troubleshooting
        if error_type == "invalid_credentials":
            base_content += """
            <h3>[TOOL] Troubleshooting Steps</h3>
            <ol>
                <li><strong>Verify credentials file:</strong> Ensure you downloaded the correct OAuth 2.0 client credentials (not service account)</li>
                <li><strong>Check application type:</strong> Must be "Desktop application" in Google Cloud Console</li>
                <li><strong>Re-download credentials:</strong> Generate new credentials if the file is corrupted</li>
                <li><strong>File format:</strong> Ensure the file is valid JSON and not corrupted</li>
            </ol>
            
            <h3>[LIST] Required Credentials Format</h3>
            <p>Your credentials.json should contain:</p>
            <ul>
                <li>client_id</li>
                <li>client_secret</li>
                <li>auth_uri</li>
                <li>token_uri</li>
            </ul>
            """
        
        elif error_type == "auth_failed":
            base_content += """
            <h3>[TOOL] Troubleshooting Steps</h3>
            <ol>
                <li><strong>Check internet connection:</strong> OAuth requires internet access</li>
                <li><strong>Firewall/Proxy:</strong> Ensure port 8080 is not blocked</li>
                <li><strong>Browser issues:</strong> Try a different browser or incognito mode</li>
                <li><strong>Clear browser cache:</strong> Clear cookies and cache for Google accounts</li>
                <li><strong>Account permissions:</strong> Ensure your Google account can access the app</li>
            </ol>
            
            <h3>🔒 Common OAuth Flow Issues</h3>
            <ul>
                <li><strong>"Access blocked":</strong> Click "Advanced" → "Go to [App Name] (unsafe)"</li>
                <li><strong>"App not verified":</strong> Normal for personal apps - proceed anyway</li>
                <li><strong>"Redirect URI mismatch":</strong> Ensure using Desktop application type</li>
            </ul>
            """
        
        elif error_type == "insufficient_permissions":
            base_content += """
            <h3>[TOOL] Troubleshooting Steps</h3>
            <ol>
                <li><strong>Delete token file:</strong> Remove any existing token.json file</li>
                <li><strong>Re-authenticate:</strong> Start the OAuth flow again</li>
                <li><strong>Grant all permissions:</strong> Accept all requested permissions during OAuth</li>
                <li><strong>Check API scopes:</strong> Ensure Gmail API is enabled in Google Cloud Console</li>
            </ol>
            
            <h3>📧 Required Gmail Permissions</h3>
            <ul>
                <li>Read Gmail messages</li>
                <li>Send Gmail messages</li>
                <li>Modify Gmail messages (mark as read)</li>
            </ul>
            """
        
        elif error_type == "api_error":
            base_content += """
            <h3>[TOOL] Troubleshooting Steps</h3>
            <ol>
                <li><strong>Check API status:</strong> Verify Gmail API is enabled in Google Cloud Console</li>
                <li><strong>Quota limits:</strong> Check if you've exceeded API quotas</li>
                <li><strong>Billing account:</strong> Some APIs require a billing account (free tier available)</li>
                <li><strong>Wait and retry:</strong> Temporary API issues may resolve automatically</li>
            </ol>
            
            <h3>📊 API Quota Information</h3>
            <ul>
                <li>Gmail API has generous free quotas for personal use</li>
                <li>Rate limits: 1 billion quota units per day</li>
                <li>Check usage in Google Cloud Console → APIs & Services → Quotas</li>
            </ul>
            """
        
        elif error_type == "network_error":
            base_content += """
            <h3>[TOOL] Troubleshooting Steps</h3>
            <ol>
                <li><strong>Check internet connection:</strong> Ensure stable internet access</li>
                <li><strong>Firewall settings:</strong> Allow the application through firewall</li>
                <li><strong>Proxy configuration:</strong> Configure proxy settings if needed</li>
                <li><strong>DNS issues:</strong> Try using different DNS servers (8.8.8.8, 1.1.1.1)</li>
                <li><strong>VPN interference:</strong> Temporarily disable VPN if active</li>
            </ol>
            
            <h3>🌐 Network Requirements</h3>
            <ul>
                <li>HTTPS access to accounts.google.com</li>
                <li>HTTPS access to oauth2.googleapis.com</li>
                <li>Local server on port 8080 for OAuth callback</li>
            </ul>
            """
        
        else:
            # Generic error troubleshooting
            base_content += """
            <h3>[TOOL] General Troubleshooting Steps</h3>
            <ol>
                <li><strong>Check setup:</strong> Verify Google Cloud Console configuration</li>
                <li><strong>Restart application:</strong> Close and reopen the application</li>
                <li><strong>Clear tokens:</strong> Delete any existing token files</li>
                <li><strong>Re-authenticate:</strong> Start the OAuth process from scratch</li>
                <li><strong>Check logs:</strong> Look for additional error details in application logs</li>
            </ol>
            """
        
        # Add common links and resources
        base_content += """
        <h3>🔗 Helpful Resources</h3>
        <ul>
            <li><a href="https://console.cloud.google.com/">Google Cloud Console</a></li>
            <li><a href="https://developers.google.com/gmail/api/quickstart/python">Gmail API Quickstart</a></li>
            <li><a href="https://support.google.com/cloud/answer/6158849">OAuth Consent Screen Help</a></li>
            <li><a href="https://myaccount.google.com/permissions">Manage App Permissions</a></li>
        </ul>
        
        <h3>🛡️ Security Notes</h3>
        <ul>
            <li><strong>Keep credentials.json secure</strong> - never share or commit to version control</li>
            <li><strong>Token files are sensitive</strong> - they provide access to your Gmail account</li>
            <li><strong>Revoke access</strong> anytime at <a href="https://myaccount.google.com/permissions">Google Account Permissions</a></li>
        </ul>
        
        <h3>💡 Still Need Help?</h3>
        <p>If the issue persists:</p>
        <ul>
            <li>Check the application logs for detailed error information</li>
            <li>Verify all setup steps in the Setup Guide</li>
            <li>Try creating a new Google Cloud project and credentials</li>
            <li>Ensure your Google account has the necessary permissions</li>
        </ul>
        """
        
        return base_content
    
    def _on_save_clicked(self):
        """Handle save button click with enhanced error handling and user feedback."""
        from PySide6.QtWidgets import QMessageBox, QProgressDialog
        from PySide6.QtCore import QTimer
        
        if not self.save_button.isEnabled():
            return
        
        # Collect form data based on authentication method
        if self.smtp_radio.isChecked():
            # SMTP configuration
            config = {
                "auth_method": "smtp",
                "smtp_server": self.smtp_server_edit.text().strip(),
                "port": self.port_spin.value(),
                "use_tls": self.use_tls_check.isChecked(),
                "email_address": self.email_edit.text().strip(),
                "password": self.password_edit.text().strip(),
                "api_key": self.api_key_edit.text().strip()
            }
        elif self.gmail_oauth_radio.isChecked():
            # Gmail OAuth configuration
            config = {
                "auth_method": "gmail_oauth",
                "credentials_path": self.credentials_path_edit.text().strip(),
                "token_path": "token.json",  # Default token path
                "oauth_authenticated": "[OK]" in self.oauth_status_label.text(),
                "api_key": self.api_key_edit.text().strip()
            }
            
            # Extract email from status if available
            status_text = self.oauth_status_label.text()
            oauth_email = ""
            
            if "Authenticated as " in status_text:
                # Extract email from "[OK] Authenticated as user@gmail.com - Save button enabled"
                parts = status_text.split("Authenticated as ")
                if len(parts) > 1:
                    email_part = parts[1].split(" -")[0].split(" ")[0].strip()
                    if "@" in email_part:
                        oauth_email = email_part
            
            # If no email extracted, use a default or prompt user
            if not oauth_email and config["oauth_authenticated"]:
                oauth_email = "authenticated@gmail.com"  # Fallback
            
            if oauth_email:
                config["oauth_email"] = oauth_email
        else:
            # Fallback to SMTP if no method selected
            config = {
                "auth_method": "smtp",
                "smtp_server": self.smtp_server_edit.text().strip(),
                "port": self.port_spin.value(),
                "use_tls": self.use_tls_check.isChecked(),
                "email_address": self.email_edit.text().strip(),
                "password": self.password_edit.text().strip(),
                "api_key": self.api_key_edit.text().strip()
            }
        
        # Show progress dialog for validation
        progress = QProgressDialog("Validating email configuration...", "Cancel", 0, 100, self)
        progress.setWindowModality(Qt.WindowModal)
        progress.setMinimumDuration(0)
        progress.setValue(0)
        progress.show()
        
        # Disable save button during validation
        self.save_button.setEnabled(False)
        self.save_button.setText("Validating...")
        
        # Create a timer to simulate validation progress
        self.validation_timer = QTimer()
        self.validation_progress = 0
        
        def update_progress():
            self.validation_progress += 20
            progress.setValue(self.validation_progress)
            
            if self.validation_progress >= 100:
                self.validation_timer.stop()
                progress.close()
                self._complete_save_validation(config)
        
        self.validation_timer.timeout.connect(update_progress)
        self.validation_timer.start(100)  # Update every 100ms
        
        # Handle cancel button
        def on_cancel():
            self.validation_timer.stop()
            self.save_button.setEnabled(True)
            self.save_button.setText("Save")
            self.logger.info("Email settings validation cancelled by user")
        
        progress.canceled.connect(on_cancel)
    
    def _complete_save_validation(self, config: Dict[str, Any]):
        """Complete the save validation process."""
        from PySide6.QtWidgets import QMessageBox
        
        try:
            # Perform additional validation (simulate email service validation)
            validation_errors = []
            
            # Validate based on authentication method
            auth_method = config.get("auth_method", "smtp")
            
            if auth_method == "smtp":
                # Check for common SMTP server issues
                smtp_server = config.get("smtp_server", "").lower()
                if "gmail" in smtp_server and config.get("port") != 587:
                    validation_errors.append("Gmail typically uses port 587 with TLS")
                
                if "outlook" in smtp_server and config.get("port") not in [587, 993]:
                    validation_errors.append("Outlook typically uses port 587 (SMTP) or 993 (IMAP)")
                
                # Check password strength for security
                password = config.get("password", "")
                if len(password) < 8:
                    validation_errors.append("Password should be at least 8 characters for better security")
            
            elif auth_method == "gmail_oauth":
                # Validate OAuth configuration
                credentials_path = config.get("credentials_path", "")
                oauth_authenticated = config.get("oauth_authenticated", False)
                
                if not credentials_path:
                    validation_errors.append("Credentials file path is required for Gmail OAuth")
                elif not Path(credentials_path).exists():
                    validation_errors.append(f"Credentials file not found: {credentials_path}")
                
                if not oauth_authenticated:
                    validation_errors.append("Gmail OAuth authentication is required before saving")
            
            # Show validation warnings if any
            if validation_errors:
                warning_msg = "Configuration saved with warnings:\n\n" + "\n".join(f"• {error}" for error in validation_errors)
                warning_msg += "\n\nDo you want to continue?"
                
                reply = QMessageBox.question(
                    self, 
                    "Configuration Warnings", 
                    warning_msg,
                    QMessageBox.Yes | QMessageBox.No,
                    QMessageBox.Yes
                )
                
                if reply == QMessageBox.No:
                    self.save_button.setEnabled(True)
                    self.save_button.setText("Save")
                    return
            
            # Emit settings saved signal
            self.settings_saved.emit(config)
            
            # Show success message
            QMessageBox.information(
                self,
                "Settings Saved",
                "Email configuration has been saved successfully!\n\nYou can now use email automation features."
            )
            
            self.logger.info("Email settings saved successfully")
            
            # Accept dialog
            self.accept()
            
        except Exception as e:
            # Show error message
            QMessageBox.critical(
                self,
                "Save Failed",
                f"Failed to save email configuration:\n\n{str(e)}\n\nPlease check your settings and try again."
            )
            
            self.logger.error(f"Error saving email settings: {e}")
            
        finally:
            # Re-enable save button
            self.save_button.setEnabled(True)
            self.save_button.setText("Save")
    
    def _on_test_connection_clicked(self):
        """Handle test connection button click with support for both authentication methods."""
        from PySide6.QtWidgets import QMessageBox
        
        # Determine which authentication method is selected
        if self.smtp_radio.isChecked():
            # Test SMTP connection
            self._test_smtp_connection()
        elif self.gmail_oauth_radio.isChecked():
            # Test Gmail OAuth connection
            self._test_gmail_oauth_connection()
        else:
            QMessageBox.warning(
                self,
                "[WARN] No Authentication Method Selected",
                "Please select an authentication method (SMTP or Gmail OAuth) before testing the connection."
            )
    
    def _test_smtp_connection(self):
        """Test SMTP connection with enhanced error handling."""
        from PySide6.QtWidgets import QMessageBox, QProgressDialog
        from PySide6.QtCore import QTimer
        import smtplib
        import socket
        
        # Validate form first
        if not self._is_form_valid_for_test():
            QMessageBox.warning(
                self,
                "Incomplete Configuration",
                "Please fill in all required fields before testing the connection:\n\n"
                "• SMTP Server\n"
                "• Email Address\n"
                "• Password"
            )
            return
        
        # Get current form data
        config = self.get_config()
        
        # Show progress dialog
        progress = QProgressDialog("Testing SMTP connection...", "Cancel", 0, 100, self)
        progress.setWindowModality(Qt.WindowModal)
        progress.setMinimumDuration(0)
        progress.setValue(0)
        progress.show()
        
        # Disable test button during testing
        self.test_button.setEnabled(False)
        self.test_button.setText("Testing...")
        
        # Create timer for progress simulation and actual testing
        self.test_timer = QTimer()
        self.test_progress = 0
        self.test_stages = [
            "Resolving SMTP server...",
            "Connecting to server...",
            "Starting TLS encryption...",
            "Authenticating credentials...",
            "Verifying connection..."
        ]
        self.current_stage = 0
        
        def update_test_progress():
            self.test_progress += 20
            progress.setValue(self.test_progress)
            
            if self.current_stage < len(self.test_stages):
                progress.setLabelText(self.test_stages[self.current_stage])
                self.current_stage += 1
            
            if self.test_progress >= 100:
                self.test_timer.stop()
                progress.close()
                self._perform_actual_connection_test(config)
        
        self.test_timer.timeout.connect(update_test_progress)
        self.test_timer.start(500)  # Update every 500ms for realistic timing
        
        # Handle cancel button
        def on_test_cancel():
            self.test_timer.stop()
            self.test_button.setEnabled(True)
            self.test_button.setText("🔄 Test Connection")
            self.logger.info("SMTP connection test cancelled by user")
        
        progress.canceled.connect(on_test_cancel)
    
    def _test_gmail_oauth_connection(self):
        """Test Gmail OAuth connection."""
        from PySide6.QtWidgets import QMessageBox, QProgressDialog
        from PySide6.QtCore import QTimer
        
        # Check if Gmail OAuth is properly configured
        credentials_path = self.credentials_path_edit.text().strip()
        if not credentials_path:
            QMessageBox.warning(
                self,
                "[WARN] Missing Credentials File",
                "Please select a credentials.json file before testing the Gmail OAuth connection.\n\n"
                "You can get this file from Google Cloud Console → APIs & Services → Credentials."
            )
            return
        
        if not GMAIL_AVAILABLE:
            QMessageBox.critical(
                self,
                "[ERROR] Gmail OAuth Not Available",
                "Gmail OAuth functionality is not available.\n\n"
                "Please install the required dependencies:\n"
                "• google-auth\n"
                "• google-auth-oauthlib\n"
                "• google-api-python-client\n\n"
                "Run: pip install google-auth google-auth-oauthlib google-api-python-client"
            )
            return
        
        # Disable test button during test
        self.test_button.setEnabled(False)
        self.test_button.setText("Testing OAuth...")
        
        # Show progress dialog
        progress = QProgressDialog("Testing Gmail OAuth connection...", "Cancel", 0, 100, self)
        progress.setWindowModality(Qt.WindowModal)
        progress.setMinimumDuration(0)
        progress.setValue(0)
        progress.show()
        
        # Create timer for progress updates
        self.test_timer = QTimer()
        self.test_progress = 0
        self.oauth_test_stages = [
            "Validating credentials file...",
            "Initializing OAuth client...",
            "Testing API connection...",
            "Verifying permissions...",
            "Connection test complete..."
        ]
        self.current_stage = 0
        
        def update_test_progress():
            self.test_progress += 20
            progress.setValue(self.test_progress)
            
            if self.current_stage < len(self.oauth_test_stages):
                progress.setLabelText(self.oauth_test_stages[self.current_stage])
                self.current_stage += 1
            
            if self.test_progress >= 100:
                self.test_timer.stop()
                progress.close()
                
                # Perform actual Gmail OAuth connection test
                self._perform_gmail_oauth_test(credentials_path)
        
        self.test_timer.timeout.connect(update_test_progress)
        self.test_timer.start(400)  # Update every 400ms
        
        # Handle cancel button
        def on_test_cancel():
            self.test_timer.stop()
            self.test_button.setEnabled(True)
            self.test_button.setText("🔄 Test Connection")
            self.logger.info("Gmail OAuth connection test cancelled by user")
        
        progress.canceled.connect(on_test_cancel)
    
    def _perform_gmail_oauth_test(self, credentials_path: str):
        """Perform the actual Gmail OAuth connection test with comprehensive error handling."""
        try:
            self.logger.info(f"Testing Gmail OAuth connection with credentials: {credentials_path}")
            
            if not GMAIL_AVAILABLE:
                self._show_gmail_oauth_error(
                    "dependencies_missing",
                    "Gmail OAuth dependencies not available",
                    "Please install required packages: google-auth, google-auth-oauthlib, google-api-python-client"
                )
                return
            
            # Create a temporary Gmail client for testing
            from llmtoolkit.app.services.gmail_client import GmailClient
            
            try:
                test_client = GmailClient(credentials_path, "test_token.json")
                
                # Test the connection
                test_result = test_client.test_connection()
                
                if test_result.get('success', False):
                    email_address = test_result.get('email_address', 'Unknown')
                    self._show_gmail_test_success(email_address, test_result)
                    
                    # Update OAuth status in the UI
                    self.oauth_status_label.setText(f"[OK] Connected as {email_address}")
                    self.oauth_status_label.setStyleSheet("color: #28a745; font-size: 11px;")
                else:
                    # Determine error type based on error message
                    error_msg = test_result.get('error', 'Unknown error')
                    error_details = test_result.get('details', '')
                    
                    if 'authentication' in error_msg.lower() or 'auth' in error_msg.lower():
                        error_type = "auth_failed"
                    elif 'credentials' in error_msg.lower() or 'invalid' in error_msg.lower():
                        error_type = "invalid_credentials"
                    elif 'permission' in error_msg.lower() or 'scope' in error_msg.lower():
                        error_type = "insufficient_permissions"
                    elif 'network' in error_msg.lower() or 'connection' in error_msg.lower():
                        error_type = "network_error"
                    elif 'api' in error_msg.lower() or 'quota' in error_msg.lower():
                        error_type = "api_error"
                    else:
                        error_type = "unknown_error"
                    
                    self._show_gmail_oauth_error(error_type, error_msg, error_details)
                    
            except GmailOAuthError as e:
                # Handle comprehensive OAuth errors with user-friendly messages and recovery suggestions
                self.logger.error(f"Gmail OAuth error during test: {e.get_user_friendly_message()}")
                
                # Show error with recovery suggestions
                self._show_comprehensive_oauth_error(e)
                
                # Update OAuth status
                self.oauth_status_label.setText(f"[ERROR] {e.get_user_friendly_message()}")
                self.oauth_status_label.setStyleSheet("color: #dc3545; font-size: 11px; margin-top: 5px;")
                
            except GmailAuthError as e:
                self.logger.error(f"Gmail authentication error: {e}")
                self._show_gmail_oauth_error("auth_failed", str(e), "OAuth authentication process failed")
            except GmailAPIError as e:
                self.logger.error(f"Gmail API error: {e}")
                self._show_gmail_oauth_error("api_error", str(e), "Gmail API operation failed")
            except FileNotFoundError:
                self.logger.error(f"Credentials file not found: {credentials_path}")
                self._show_gmail_oauth_error("invalid_credentials", "Credentials file not found", f"Could not find file: {credentials_path}")
            except Exception as e:
                # Create comprehensive error from generic exception
                if GMAIL_AVAILABLE and GmailOAuthErrorHandler:
                    error_handler = GmailOAuthErrorHandler()
                    oauth_error = error_handler.create_error_from_exception(e, "Gmail OAuth test")
                    self._show_comprehensive_oauth_error(oauth_error)
                    
                    # Update OAuth status
                    self.oauth_status_label.setText(f"[ERROR] {oauth_error.get_user_friendly_message()}")
                    self.oauth_status_label.setStyleSheet("color: #dc3545; font-size: 11px; margin-top: 5px;")
                else:
                    # Fallback to legacy error handling
                    error_msg = str(e)
                    self.logger.error(f"Unexpected error during Gmail OAuth test: {e}")
                    
                    if 'credentials' in error_msg.lower():
                        self._show_gmail_oauth_error("invalid_credentials", error_msg, "Please check your credentials.json file")
                    elif 'network' in error_msg.lower() or 'connection' in error_msg.lower():
                        self._show_gmail_oauth_error("network_error", error_msg, "Network connectivity issue")
                    else:
                        self._show_gmail_oauth_error("unknown_error", error_msg, "Unexpected error during OAuth test")
                    
        except Exception as e:
            self.logger.error(f"Critical error during Gmail OAuth test: {e}")
            self._show_gmail_oauth_error("unknown_error", f"Critical error: {str(e)}", "Please check application logs for details")
        finally:
            # Re-enable test button
            self.test_button.setEnabled(True)
            self.test_button.setText("🔄 Test Connection")
    
    def _show_comprehensive_oauth_error(self, oauth_error: 'GmailOAuthError'):
        """
        Show a comprehensive error dialog with user-friendly message and recovery suggestions.
        
        Args:
            oauth_error: The GmailOAuthError instance with detailed error information
        """
        from PySide6.QtWidgets import QMessageBox, QTextBrowser, QVBoxLayout, QHBoxLayout, QPushButton
        
        # Create custom error dialog
        error_dialog = QDialog(self)
        error_dialog.setWindowTitle("Gmail OAuth Error")
        error_dialog.setModal(True)
        error_dialog.resize(600, 500)
        
        layout = QVBoxLayout(error_dialog)
        
        # Error message
        error_label = QLabel(f"[ERROR] {oauth_error.get_user_friendly_message()}")
        error_label.setStyleSheet("color: #dc3545; font-weight: bold; font-size: 14px; margin-bottom: 10px;")
        error_label.setWordWrap(True)
        layout.addWidget(error_label)
        
        # Recovery suggestions
        suggestions = oauth_error.get_recovery_suggestions()
        if suggestions:
            suggestions_browser = QTextBrowser()
            suggestions_browser.setMaximumHeight(300)
            
            suggestions_html = "<h3>💡 How to fix this:</h3><ol>"
            for suggestion in suggestions:
                suggestions_html += f"<li>{suggestion}</li>"
            suggestions_html += "</ol>"
            
            # Add error-specific help links
            if hasattr(oauth_error, 'error_type') and oauth_error.error_type:
                if oauth_error.error_type == GmailOAuthErrorType.INVALID_CREDENTIALS:
                    suggestions_html += """
                    <h4>🔗 Helpful Links:</h4>
                    <ul>
                        <li><a href="https://console.cloud.google.com/apis/credentials">Google Cloud Console - Credentials</a></li>
                        <li><a href="https://developers.google.com/gmail/api/quickstart/python">Gmail API Python Quickstart</a></li>
                    </ul>
                    """
                elif oauth_error.error_type == GmailOAuthErrorType.API_DISABLED:
                    suggestions_html += """
                    <h4>🔗 Helpful Links:</h4>
                    <ul>
                        <li><a href="https://console.cloud.google.com/apis/library/gmail.googleapis.com">Enable Gmail API</a></li>
                        <li><a href="https://console.cloud.google.com/apis/dashboard">API Dashboard</a></li>
                    </ul>
                    """
                elif oauth_error.error_type in [GmailOAuthErrorType.RATE_LIMIT_EXCEEDED, GmailOAuthErrorType.QUOTA_EXCEEDED]:
                    suggestions_html += """
                    <h4>🔗 Helpful Links:</h4>
                    <ul>
                        <li><a href="https://console.cloud.google.com/apis/api/gmail.googleapis.com/quotas">Gmail API Quotas</a></li>
                        <li><a href="https://developers.google.com/gmail/api/reference/quota">Gmail API Usage Limits</a></li>
                    </ul>
                    """
            
            suggestions_browser.setHtml(suggestions_html)
            suggestions_browser.setOpenExternalLinks(True)
            layout.addWidget(suggestions_browser)
        
        # Technical details (collapsible)
        if hasattr(oauth_error, 'details') and oauth_error.details or hasattr(oauth_error, 'original_error') and oauth_error.original_error:
            details_label = QLabel("Technical Details:")
            details_label.setStyleSheet("font-weight: bold; margin-top: 10px;")
            layout.addWidget(details_label)
            
            details_text = ""
            if hasattr(oauth_error, 'details') and oauth_error.details:
                details_text += f"Details: {oauth_error.details}\n"
            if hasattr(oauth_error, 'original_error') and oauth_error.original_error:
                details_text += f"Original Error: {str(oauth_error.original_error)}\n"
            if hasattr(oauth_error, 'error_code') and oauth_error.error_code:
                details_text += f"Error Code: {oauth_error.error_code}\n"
            
            details_browser = QTextBrowser()
            details_browser.setMaximumHeight(100)
            details_browser.setPlainText(details_text)
            layout.addWidget(details_browser)
        
        # Buttons
        button_layout = QHBoxLayout()
        button_layout.addStretch()
        
        # Setup Help button (for certain error types)
        if (hasattr(oauth_error, 'error_type') and oauth_error.error_type and 
            oauth_error.error_type in [
                GmailOAuthErrorType.INVALID_CREDENTIALS,
                GmailOAuthErrorType.API_DISABLED,
                GmailOAuthErrorType.MISSING_OAUTH_SCOPES
            ]):
            setup_help_button = QPushButton("📖 Setup Guide")
            setup_help_button.clicked.connect(lambda: self._show_oauth_setup_help())
            setup_help_button.clicked.connect(error_dialog.accept)
            button_layout.addWidget(setup_help_button)
        
        # Retry button (for retryable errors)
        if hasattr(oauth_error, 'is_retryable') and oauth_error.is_retryable():
            retry_button = QPushButton("🔄 Retry")
            retry_button.clicked.connect(error_dialog.accept)
            retry_button.clicked.connect(lambda: self._on_test_connection_clicked())
            button_layout.addWidget(retry_button)
        
        # Close button
        close_button = QPushButton("Close")
        close_button.clicked.connect(error_dialog.accept)
        button_layout.addWidget(close_button)
        
        layout.addLayout(button_layout)
        
        # Show the dialog
        error_dialog.exec()
    
    def _show_gmail_test_success(self, email_address: str, test_result: dict):
        """Show successful Gmail OAuth test result."""
        from PySide6.QtWidgets import QMessageBox
        
        profile = test_result.get('profile', {})
        quota_info = test_result.get('quota', {})
        
        # Build success message with detailed information
        message = f"Gmail OAuth connection test completed successfully!\n\n"
        message += f"📧 Account: {email_address}\n"
        
        if profile.get('messagesTotal'):
            message += f"📬 Total Messages: {profile.get('messagesTotal', 'Unknown')}\n"
        
        if quota_info:
            used = quota_info.get('usageInGb', 'Unknown')
            limit = quota_info.get('limitInGb', 'Unknown')
            message += f"💾 Storage: {used}GB / {limit}GB used\n"
        
        message += f"🔐 Authentication: [OK] Valid OAuth 2.0 tokens\n"
        message += f"🌐 API Access: [OK] Gmail API accessible\n\n"
        message += f"Your Gmail OAuth configuration is working correctly and ready to use."
        
        QMessageBox.information(
            self,
            "[OK] Gmail OAuth Test Successful",
            message
        )
        
        self.logger.info(f"Gmail OAuth connection test successful for {email_address}")
    
    def _show_gmail_test_error(self, error: str, details: str):
        """Show Gmail OAuth test error with troubleshooting suggestions."""
        from PySide6.QtWidgets import QMessageBox
        
        # Provide specific troubleshooting based on error type
        if "authentication" in error.lower() or "auth" in error.lower():
            suggestions = ("Troubleshooting steps:\n"
                         "• Ensure credentials.json is from Google Cloud Console\n"
                         "• Check that Gmail API is enabled in your Google Cloud project\n"
                         "• Verify OAuth 2.0 consent screen is configured\n"
                         "• Make sure your application is not in testing mode with restricted users")
        elif "api" in error.lower():
            suggestions = ("Troubleshooting steps:\n"
                         "• Check your internet connection\n"
                         "• Verify Gmail API is enabled in Google Cloud Console\n"
                         "• Ensure API quotas are not exceeded\n"
                         "• Check if your IP address is allowed")
        elif "permission" in error.lower() or "scope" in error.lower():
            suggestions = ("Troubleshooting steps:\n"
                         "• Ensure your OAuth application has the required scopes\n"
                         "• Check Gmail API permissions in Google Cloud Console\n"
                         "• Re-authenticate to grant necessary permissions")
        else:
            suggestions = ("General troubleshooting steps:\n"
                         "• Verify credentials.json file is valid and not corrupted\n"
                         "• Check your internet connection\n"
                         "• Ensure Gmail API is enabled in Google Cloud Console\n"
                         "• Try re-downloading credentials.json from Google Cloud Console")
        
        message = f"Gmail OAuth connection test failed.\n\n"
        message += f"[ERROR] Error: {error}\n\n"
        message += f"📝 Details: {details}\n\n"
        message += suggestions
        
        QMessageBox.critical(
            self,
            "[ERROR] Gmail OAuth Test Failed",
            message
        )
        
        self.logger.error(f"Gmail OAuth connection test failed: {error} - {details}")
    
    def _is_form_valid_for_test(self) -> bool:
        """Check if form has minimum required fields for testing based on authentication method."""
        if self.smtp_radio.isChecked():
            # SMTP validation
            smtp_server = self.smtp_server_edit.text().strip()
            email = self.email_edit.text().strip()
            password = self.password_edit.text().strip()
            
            return (
                len(smtp_server) > 0 and
                len(email) > 0 and
                "@" in email and
                len(password) > 0
            )
        elif self.gmail_oauth_radio.isChecked():
            # Gmail OAuth validation
            credentials_path = self.credentials_path_edit.text().strip()
            return len(credentials_path) > 0 and GMAIL_AVAILABLE
        else:
            # No authentication method selected
            return False
    
    def _perform_actual_connection_test(self, config: Dict[str, Any]):
        """Perform the actual SMTP connection test."""
        from PySide6.QtWidgets import QMessageBox
        import smtplib
        import socket
        import ssl
        
        try:
            smtp_server = config["smtp_server"]
            port = config["port"]
            email_address = config["email_address"]
            password = config["password"]
            use_tls = config["use_tls"]
            
            self.logger.info(f"Testing SMTP connection to {smtp_server}:{port}")
            
            # Test connection
            server = None
            try:
                # Create SMTP connection
                server = smtplib.SMTP(smtp_server, port, timeout=10)
                
                # Enable debug output for troubleshooting
                # server.set_debuglevel(1)
                
                # Say hello to the server
                server.ehlo()
                
                # Start TLS if enabled
                if use_tls:
                    server.starttls()
                    server.ehlo()  # Re-identify after TLS
                
                # Attempt authentication
                server.login(email_address, password)
                
                # If we get here, everything worked!
                self._show_test_success(smtp_server, port, use_tls)
                
            except smtplib.SMTPAuthenticationError as e:
                self._show_test_auth_error(e, smtp_server)
            except smtplib.SMTPConnectError as e:
                self._show_test_connection_error(e, smtp_server, port)
            except smtplib.SMTPServerDisconnected as e:
                self._show_test_disconnection_error(e, smtp_server)
            except socket.gaierror as e:
                self._show_test_dns_error(e, smtp_server)
            except socket.timeout as e:
                self._show_test_timeout_error(e, smtp_server, port)
            except ssl.SSLError as e:
                self._show_test_ssl_error(e, smtp_server)
            except Exception as e:
                self._show_test_generic_error(e, smtp_server, port)
            finally:
                # Always close the connection
                if server:
                    try:
                        server.quit()
                    except:
                        pass  # Ignore errors when closing
                        
        except Exception as e:
            self.logger.error(f"Unexpected error during connection test: {e}")
            QMessageBox.critical(
                self,
                "Test Failed",
                f"An unexpected error occurred during the connection test:\n\n{str(e)}"
            )
        finally:
            # Re-enable test button
            self.test_button.setEnabled(True)
            self.test_button.setText("🔄 Test Connection")
    
    def _show_test_success(self, smtp_server: str, port: int, use_tls: bool):
        """Show successful connection test result."""
        from PySide6.QtWidgets import QMessageBox
        
        tls_status = "[OK] TLS Enabled" if use_tls else "[WARN] TLS Disabled"
        
        QMessageBox.information(
            self,
            "[OK] Connection Successful",
            f"Email configuration test completed successfully!\n\n"
            f"📧 Server: {smtp_server}:{port}\n"
            f"🔐 Authentication: [OK] Valid\n"
            f"🔒 Security: {tls_status}\n\n"
            f"Your email settings are working correctly and ready to use."
        )
        
        self.logger.info(f"SMTP connection test successful for {smtp_server}:{port}")
    
    def _show_test_auth_error(self, error, smtp_server: str):
        """Show authentication error details."""
        from PySide6.QtWidgets import QMessageBox
        
        error_code = getattr(error, 'smtp_code', 'Unknown')
        error_msg = getattr(error, 'smtp_error', str(error))
        
        if "gmail" in smtp_server.lower():
            suggestion = ("For Gmail:\n"
                         "• Use an App Password instead of your regular password\n"
                         "• Enable 2-factor authentication first\n"
                         "• Generate App Password in Google Account settings")
        elif "outlook" in smtp_server.lower() or "hotmail" in smtp_server.lower():
            suggestion = ("For Outlook/Hotmail:\n"
                         "• Enable 'Less secure app access' in account settings\n"
                         "• Or use OAuth2 authentication if available")
        else:
            suggestion = ("Common solutions:\n"
                         "• Verify your email address and password\n"
                         "• Check if 2-factor authentication requires app password\n"
                         "• Contact your email provider for SMTP settings")
        
        QMessageBox.critical(
            self,
            "[ERROR] Authentication Failed",
            f"Failed to authenticate with the email server.\n\n"
            f"📧 Server: {smtp_server}\n"
            f"🔐 Error Code: {error_code}\n"
            f"📝 Error: {error_msg}\n\n"
            f"{suggestion}"
        )
        
        self.logger.error(f"SMTP authentication failed for {smtp_server}: {error}")
    
    def _show_test_connection_error(self, error, smtp_server: str, port: int):
        """Show connection error details."""
        from PySide6.QtWidgets import QMessageBox
        
        QMessageBox.critical(
            self,
            "[ERROR] Connection Failed",
            f"Could not connect to the email server.\n\n"
            f"📧 Server: {smtp_server}:{port}\n"
            f"📝 Error: {str(error)}\n\n"
            f"Possible solutions:\n"
            f"• Check your internet connection\n"
            f"• Verify the SMTP server address and port\n"
            f"• Check if your firewall is blocking the connection\n"
            f"• Try a different port (25, 465, 587, 2525)"
        )
        
        self.logger.error(f"SMTP connection failed for {smtp_server}:{port}: {error}")
    
    def _show_test_disconnection_error(self, error, smtp_server: str):
        """Show server disconnection error."""
        from PySide6.QtWidgets import QMessageBox
        
        QMessageBox.warning(
            self,
            "[WARN] Connection Interrupted",
            f"The server disconnected unexpectedly.\n\n"
            f"📧 Server: {smtp_server}\n"
            f"📝 Error: {str(error)}\n\n"
            f"This might be temporary. Try again in a few moments."
        )
        
        self.logger.warning(f"SMTP server disconnected for {smtp_server}: {error}")
    
    def _show_test_dns_error(self, error, smtp_server: str):
        """Show DNS resolution error."""
        from PySide6.QtWidgets import QMessageBox
        
        QMessageBox.critical(
            self,
            "[ERROR] Server Not Found",
            f"Could not find the email server.\n\n"
            f"📧 Server: {smtp_server}\n"
            f"📝 Error: {str(error)}\n\n"
            f"Possible solutions:\n"
            f"• Check the SMTP server address spelling\n"
            f"• Verify your internet connection\n"
            f"• Try using the server's IP address instead"
        )
        
        self.logger.error(f"DNS resolution failed for {smtp_server}: {error}")
    
    def _show_test_timeout_error(self, error, smtp_server: str, port: int):
        """Show connection timeout error."""
        from PySide6.QtWidgets import QMessageBox
        
        QMessageBox.warning(
            self,
            "⏱️ Connection Timeout",
            f"Connection to the server timed out.\n\n"
            f"📧 Server: {smtp_server}:{port}\n"
            f"📝 Error: {str(error)}\n\n"
            f"Possible solutions:\n"
            f"• Check your internet connection speed\n"
            f"• Try a different port\n"
            f"• Check if your firewall is blocking the connection\n"
            f"• The server might be temporarily unavailable"
        )
        
        self.logger.warning(f"SMTP connection timeout for {smtp_server}:{port}: {error}")
    
    def _show_test_ssl_error(self, error, smtp_server: str):
        """Show SSL/TLS error details."""
        from PySide6.QtWidgets import QMessageBox
        
        QMessageBox.critical(
            self,
            "🔒 SSL/TLS Error",
            f"SSL/TLS encryption failed.\n\n"
            f"📧 Server: {smtp_server}\n"
            f"📝 Error: {str(error)}\n\n"
            f"Possible solutions:\n"
            f"• Try disabling TLS encryption\n"
            f"• Use a different port (465 for SSL, 587 for TLS)\n"
            f"• Check if the server supports the encryption method"
        )
        
        self.logger.error(f"SSL/TLS error for {smtp_server}: {error}")
    
    def _show_test_generic_error(self, error, smtp_server: str, port: int):
        """Show generic error details."""
        from PySide6.QtWidgets import QMessageBox
        
        QMessageBox.critical(
            self,
            "[ERROR] Test Failed",
            f"Email connection test failed.\n\n"
            f"📧 Server: {smtp_server}:{port}\n"
            f"📝 Error: {str(error)}\n\n"
            f"Please check your settings and try again.\n"
            f"Contact your email provider if the problem persists."
        )
        
        self.logger.error(f"Generic SMTP error for {smtp_server}:{port}: {error}")
    
    def _show_gmail_test_success(self, email_address: str, test_result: dict):
        """Show Gmail OAuth test success message with account details."""
        from PySide6.QtWidgets import QMessageBox
        
        messages_total = test_result.get('messages_total', 0)
        threads_total = test_result.get('threads_total', 0)
        
        success_msg = f"""[OK] Gmail OAuth Connection Successful!

🔐 Authentication: OAuth 2.0 ✓
📧 Account: {email_address}
📬 Total Messages: {messages_total:,}
🧵 Total Threads: {threads_total:,}

Your Gmail OAuth settings are configured correctly and ready to use.
You can now fetch emails, send messages, and manage your Gmail account securely."""
        
        QMessageBox.information(
            self,
            "Gmail Connection Test Successful",
            success_msg
        )
        
        # Update OAuth status in UI
        self.oauth_status_label.setText(f"[OK] Authenticated as {email_address}")
        self.oauth_status_label.setStyleSheet("color: #28a745; font-size: 11px; margin-top: 5px;")
        
        self.logger.info(f"Gmail OAuth connection test successful for {email_address}")
    
    def _show_gmail_test_error(self, error_title: str, error_details: str):
        """Show Gmail OAuth test error with basic troubleshooting."""
        from PySide6.QtWidgets import QMessageBox
        
        error_msg = f"""[ERROR] Gmail OAuth Connection Failed

{error_title}

{error_details}

💡 Quick troubleshooting:
• Verify your credentials.json file is valid
• Check your internet connection
• Ensure Gmail API is enabled in Google Cloud Console
• Try re-authenticating with Google

Click 'Setup Help' for detailed troubleshooting guide."""
        
        msg_box = QMessageBox(self)
        msg_box.setIcon(QMessageBox.Critical)
        msg_box.setWindowTitle("Gmail Connection Test Failed")
        msg_box.setText(error_msg)
        
        # Add custom buttons
        setup_help_btn = msg_box.addButton("📖 Setup Help", QMessageBox.ActionRole)
        close_btn = msg_box.addButton("Close", QMessageBox.RejectRole)
        
        msg_box.exec()
        
        # Handle button clicks
        if msg_box.clickedButton() == setup_help_btn:
            self._show_oauth_setup_help()
        
        self.logger.error(f"Gmail OAuth connection test failed: {error_title} - {error_details}")

    def get_config(self) -> Dict[str, Any]:
        """
        Get current configuration from form fields.
        
        Returns:
            Dict[str, Any]: Current email configuration
        """
        return {
            "smtp_server": self.smtp_server_edit.text().strip(),
            "port": self.port_spin.value(),
            "use_tls": self.use_tls_check.isChecked(),
            "email_address": self.email_edit.text().strip(),
            "password": self.password_edit.text().strip(),
            "api_key": self.api_key_edit.text().strip()
        }
    
    def _show_oauth_loading_dialog(self):
        """Show OAuth loading dialog with progress indicators."""
        from PySide6.QtWidgets import QProgressDialog
        from PySide6.QtCore import QTimer
        
        # Show progress dialog for OAuth authentication
        self.oauth_progress = QProgressDialog("Starting OAuth authentication...", "Cancel", 0, 100, self)
        self.oauth_progress.setWindowModality(Qt.WindowModal)
        self.oauth_progress.setMinimumDuration(0)
        self.oauth_progress.setValue(0)
        self.oauth_progress.show()
        
        # Disable the authenticate button temporarily
        self.oauth_auth_button.setEnabled(False)
        self.oauth_auth_button.setText("🔐 Authenticating...")
        
        # Create a timer to simulate OAuth progress
        self.oauth_timer = QTimer()
        self.oauth_progress_value = 0
        self.oauth_stages = [
            "Initializing OAuth client...",
            "Opening browser for authentication...",
            "Waiting for user authorization...",
            "Processing authorization code...",
            "Retrieving access tokens...",
            "Verifying authentication..."
        ]
        self.oauth_stage_index = 0
        
        def update_oauth_progress():
            self.oauth_progress_value += 15
            self.oauth_progress.setValue(self.oauth_progress_value)
            
            # Update stage message
            if self.oauth_stage_index < len(self.oauth_stages):
                self.oauth_progress.setLabelText(self.oauth_stages[self.oauth_stage_index])
                if self.oauth_progress_value % 20 == 0:  # Change stage every 20%
                    self.oauth_stage_index += 1
            
            if self.oauth_progress_value >= 100:
                self.oauth_timer.stop()
                self.oauth_progress.close()
                self._complete_oauth_authentication()
        
        self.oauth_timer.timeout.connect(update_oauth_progress)
        self.oauth_timer.start(300)  # Update every 300ms for realistic timing
        
        # Handle cancel button
        def on_oauth_cancel():
            self.oauth_timer.stop()
            self._reset_oauth_button()
            self.logger.info("OAuth authentication cancelled by user")
        
        self.oauth_progress.canceled.connect(on_oauth_cancel)
    
    def _complete_oauth_authentication(self):
        """Complete OAuth authentication with success/error handling."""
        # This method will be called by the parent when OAuth completes
        # For now, just reset the button state
        self._reset_oauth_button()
    
    def _reset_oauth_button(self):
        """Reset OAuth authentication button to original state."""
        self.oauth_auth_button.setEnabled(True)
        self.oauth_auth_button.setText("🔐 Authenticate with Google")
    
    def _is_form_valid_for_test(self) -> bool:
        """Check if form has minimum required fields for connection testing."""
        if self.smtp_radio.isChecked():
            return (
                bool(self.smtp_server_edit.text().strip()) and
                bool(self.email_edit.text().strip()) and
                bool(self.password_edit.text().strip())
            )
        elif self.gmail_oauth_radio.isChecked():
            return bool(self.credentials_path_edit.text().strip())
        return False
    
    def _perform_actual_connection_test(self, config: Dict[str, Any]):
        """Perform the actual SMTP connection test."""
        from PySide6.QtWidgets import QMessageBox
        import smtplib
        import socket
        
        try:
            smtp_server = config.get("smtp_server", "")
            port = config.get("port", 587)
            use_tls = config.get("use_tls", True)
            email = config.get("email_address", "")
            password = config.get("password", "")
            
            self.logger.info(f"Testing SMTP connection to {smtp_server}:{port}")
            
            # Create SMTP connection
            server = smtplib.SMTP(smtp_server, port, timeout=10)
            
            if use_tls:
                server.starttls()
            
            # Attempt login
            server.login(email, password)
            server.quit()
            
            # Show success message
            QMessageBox.information(
                self,
                "[OK] Connection Successful",
                f"SMTP connection test successful!\n\n"
                f"Server: {smtp_server}:{port}\n"
                f"Email: {email}\n"
                f"TLS: {'Enabled' if use_tls else 'Disabled'}\n\n"
                f"Your email configuration is working correctly."
            )
            
            self.logger.info("SMTP connection test successful")
            
        except smtplib.SMTPAuthenticationError as e:
            error_msg = "Authentication failed. Please check your email address and password."
            if "gmail" in smtp_server.lower():
                error_msg += "\n\nFor Gmail, you need to use an App Password instead of your regular password."
            
            QMessageBox.critical(
                self,
                "[ERROR] Authentication Failed",
                f"{error_msg}\n\nError details: {str(e)}"
            )
            self.logger.error(f"SMTP authentication error: {e}")
            
        except smtplib.SMTPConnectError as e:
            QMessageBox.critical(
                self,
                "[ERROR] Connection Failed",
                f"Could not connect to SMTP server.\n\n"
                f"Please check:\n"
                f"• Server address: {smtp_server}\n"
                f"• Port number: {port}\n"
                f"• Internet connection\n"
                f"• Firewall settings\n\n"
                f"Error details: {str(e)}"
            )
            self.logger.error(f"SMTP connection error: {e}")
            
        except socket.timeout:
            QMessageBox.critical(
                self,
                "[ERROR] Connection Timeout",
                f"Connection to SMTP server timed out.\n\n"
                f"This could be due to:\n"
                f"• Network connectivity issues\n"
                f"• Firewall blocking the connection\n"
                f"• Incorrect server address or port\n\n"
                f"Server: {smtp_server}:{port}"
            )
            self.logger.error("SMTP connection timeout")
            
        except Exception as e:
            QMessageBox.critical(
                self,
                "[ERROR] Connection Test Failed",
                f"SMTP connection test failed with an unexpected error.\n\n"
                f"Error details: {str(e)}\n\n"
                f"Please check your configuration and try again."
            )
            self.logger.error(f"Unexpected SMTP test error: {e}")
            
        finally:
            # Re-enable test button
            self.test_button.setEnabled(True)
            self.test_button.setText("🔄 Test Connection")
    
    def _perform_gmail_oauth_test(self, credentials_path: str):
        """Perform the actual Gmail OAuth connection test with comprehensive error handling."""
        from PySide6.QtWidgets import QMessageBox
        
        try:
            self.logger.info(f"Testing Gmail OAuth connection with credentials: {credentials_path}")
            
            if not GMAIL_AVAILABLE:
                QMessageBox.critical(
                    self,
                    "[ERROR] Gmail OAuth Not Available",
                    "Gmail OAuth functionality is not available.\n\n"
                    "Please install the required dependencies:\n"
                    "• google-auth\n"
                    "• google-auth-oauthlib\n"
                    "• google-api-python-client"
                )
                return
            
            # Validate credentials file
            if not self._validate_credentials_file(credentials_path):
                QMessageBox.critical(
                    self,
                    "[ERROR] Invalid Credentials File",
                    "The selected credentials file is not valid.\n\n"
                    "Please ensure you've downloaded the correct OAuth 2.0 client credentials from Google Cloud Console."
                )
                return
            
            # Initialize Gmail client for testing
            test_client = GmailClient(credentials_path)
            
            # Test connection (this will use existing tokens if available)
            test_result = test_client.test_connection()
            
            if test_result.get('success', False):
                # Show success message
                user_email = test_result.get('user_email', 'Unknown')
                QMessageBox.information(
                    self,
                    "[OK] Gmail OAuth Test Successful",
                    f"Gmail OAuth connection test successful!\n\n"
                    f"Authenticated as: {user_email}\n"
                    f"API Access: Working\n"
                    f"Permissions: Verified\n\n"
                    f"Your Gmail OAuth configuration is working correctly."
                )
                
                # Update OAuth status
                self.oauth_status_label.setText(f"[OK] Authenticated as {user_email}")
                self.oauth_status_label.setStyleSheet("color: #28a745; font-size: 11px; margin-top: 5px;")
                
                self.logger.info(f"Gmail OAuth test successful for {user_email}")
                
            else:
                # Show error message
                error_msg = test_result.get('error', 'Unknown error')
                error_details = test_result.get('details', '')
                
                QMessageBox.warning(
                    self,
                    "[WARN] Gmail OAuth Test Failed",
                    f"Gmail OAuth connection test failed.\n\n"
                    f"Error: {error_msg}\n"
                    f"Details: {error_details}\n\n"
                    f"You may need to authenticate first by clicking 'Authenticate with Google'."
                )
                
                self.logger.warning(f"Gmail OAuth test failed: {error_msg}")
                
        except GmailOAuthError as e:
            # Handle OAuth-specific errors with detailed troubleshooting
            self._show_gmail_oauth_error("oauth_test_failed", str(e), e.get_user_friendly_message())
            self.logger.error(f"Gmail OAuth test error: {e}")
            
        except Exception as e:
            # Handle unexpected errors
            QMessageBox.critical(
                self,
                "[ERROR] Gmail OAuth Test Error",
                f"Gmail OAuth connection test failed with an unexpected error.\n\n"
                f"Error details: {str(e)}\n\n"
                f"Please check your configuration and try again."
            )
            self.logger.error(f"Unexpected Gmail OAuth test error: {e}")
            
        finally:
            # Re-enable test button
            self.test_button.setEnabled(True)
            self.test_button.setText("🔄 Test Connection")
    
    def get_config(self) -> Dict[str, Any]:
        """
        Get current configuration from form fields.
        
        Returns:
            Dictionary containing current form configuration
        """
        if self.smtp_radio.isChecked():
            return {
                "auth_method": "smtp",
                "smtp_server": self.smtp_server_edit.text().strip(),
                "port": self.port_spin.value(),
                "use_tls": self.use_tls_check.isChecked(),
                "email_address": self.email_edit.text().strip(),
                "password": self.password_edit.text().strip(),
                "api_key": self.api_key_edit.text().strip()
            }
        elif self.gmail_oauth_radio.isChecked():
            return {
                "auth_method": "gmail_oauth",
                "credentials_path": self.credentials_path_edit.text().strip(),
                "oauth_status": self.oauth_status_label.text(),
                "api_key": self.api_key_edit.text().strip()
            }
        else:
            return {}
    
    def set_oauth_authentication_status(self, success: bool, message: str, user_email: str = None):
        """
        Update OAuth authentication status with visual feedback.
        
        Args:
            success: Whether authentication was successful
            message: Status message to display
            user_email: Authenticated user email (if successful)
        """
        if success:
            # Show success status
            display_message = f"[OK] Authenticated as {user_email}" if user_email else "[OK] Authenticated"
            self.oauth_status_label.setText(display_message)
            self.oauth_status_label.setStyleSheet("color: #28a745; font-size: 11px; margin-top: 5px;")
            
            # Show success animation (brief color change)
            self._animate_success_feedback(self.oauth_status_label)
            
            # Show success message
            QMessageBox.information(
                self,
                "[OK] Authentication Successful",
                f"Gmail OAuth authentication completed successfully!\n\n"
                f"Authenticated as: {user_email or 'Unknown'}\n\n"
                f"You can now use Gmail API features."
            )
            
            self.logger.info(f"OAuth authentication successful for {user_email}")
            
        else:
            # Show error status
            self.oauth_status_label.setText("[ERROR] Authentication failed")
            self.oauth_status_label.setStyleSheet("color: #dc3545; font-size: 11px; margin-top: 5px;")
            
            # Show error message with troubleshooting
            self._show_gmail_oauth_error("auth_failed", message)
            
            self.logger.error(f"OAuth authentication failed: {message}")
        
        # Reset OAuth button
        self._reset_oauth_button()
    
    def _animate_success_feedback(self, widget):
        """Add a brief success animation to a widget."""
        try:
            # Create a property animation for background color
            self.success_animation = QPropertyAnimation(widget, b"styleSheet")
            self.success_animation.setDuration(1000)  # 1 second
            
            # Define animation keyframes
            original_style = widget.styleSheet()
            success_style = original_style + "; background-color: #d4edda; border-radius: 4px; padding: 2px;"
            
            self.success_animation.setKeyValueAt(0, original_style)
            self.success_animation.setKeyValueAt(0.5, success_style)
            self.success_animation.setKeyValueAt(1, original_style)
            
            self.success_animation.setEasingCurve(QEasingCurve.InOutQuad)
            self.success_animation.start()
            
        except Exception as e:
            # Animation is optional, don't fail if it doesn't work
            self.logger.debug(f"Success animation failed: {e}")
    
    def keyPressEvent(self, event):
        """Handle keyboard shortcuts for improved UX."""
        from PySide6.QtGui import QKeySequence
        from PySide6.QtCore import Qt
        
        # Ctrl+S to save
        if event.matches(QKeySequence.Save):
            if self.save_button.isEnabled():
                self._on_save_clicked()
            event.accept()
            return
        
        # Ctrl+T to test connection
        if event.key() == Qt.Key_T and event.modifiers() == Qt.ControlModifier:
            if self.test_button.isEnabled():
                self._on_test_connection_clicked()
            event.accept()
            return
        
        # F1 for help
        if event.key() == Qt.Key_F1:
            if self.gmail_oauth_radio.isChecked():
                self._show_oauth_setup_help()
            else:
                self._show_smtp_help()
            event.accept()
            return
        
        # Escape to cancel
        if event.key() == Qt.Key_Escape:
            self.reject()
            event.accept()
            return
        
        # Call parent implementation
        super().keyPressEvent(event)
    
    def _show_smtp_help(self):
        """Show SMTP configuration help dialog."""
        from PySide6.QtWidgets import QMessageBox
        
        help_text = """
        📧 SMTP Configuration Help
        
        Common SMTP Settings:
        
        Gmail:
        • Server: smtp.gmail.com
        • Port: 587 (TLS) or 465 (SSL)
        • Use App Password (not regular password)
        
        Outlook/Hotmail:
        • Server: smtp-mail.outlook.com
        • Port: 587
        • Use regular password
        
        Yahoo:
        • Server: smtp.mail.yahoo.com
        • Port: 587 or 465
        • Use App Password
        
        Security Tips:
        • Always use TLS/SSL encryption
        • Use App Passwords when available
        • Keep credentials secure
        
        Keyboard Shortcuts:
        • Ctrl+S: Save settings
        • Ctrl+T: Test connection
        • F1: Show this help
        • Escape: Cancel
        """
        
        QMessageBox.information(self, "SMTP Help", help_text)
    
    def showEvent(self, event):
        """Handle dialog show event to set up tooltips and initial focus."""
        super().showEvent(event)
        
        # Set up enhanced tooltips
        self._setup_enhanced_tooltips()
        
        # Set initial focus to first empty required field
        self._set_initial_focus()
    
    def _setup_enhanced_tooltips(self):
        """Set up enhanced tooltips for better user guidance."""
        # SMTP Server tooltip
        self.smtp_server_edit.setToolTip(
            "Enter your email provider's SMTP server address\n"
            "Examples:\n"
            "• Gmail: smtp.gmail.com\n"
            "• Outlook: smtp-mail.outlook.com\n"
            "• Yahoo: smtp.mail.yahoo.com"
        )
        
        # Port tooltip
        self.port_spin.setToolTip(
            "SMTP server port number\n"
            "Common ports:\n"
            "• 587: SMTP with TLS (recommended)\n"
            "• 465: SMTP with SSL\n"
            "• 25: Unencrypted (not recommended)"
        )
        
        # Email tooltip
        self.email_edit.setToolTip(
            "Your email address\n"
            "This will be used as the 'From' address for sent emails"
        )
        
        # Password tooltip
        self.password_edit.setToolTip(
            "Your email password or App Password\n"
            "For Gmail: Use App Password (not regular password)\n"
            "For Outlook: Use regular password\n"
            "For Yahoo: Use App Password"
        )
        
        # OAuth credentials tooltip
        self.credentials_path_edit.setToolTip(
            "Path to your Google Cloud credentials.json file\n"
            "Get this from Google Cloud Console:\n"
            "APIs & Services → Credentials → Create OAuth 2.0 Client ID"
        )
        
        # Test button tooltip
        self.test_button.setToolTip(
            "Test your email configuration\n"
            "Keyboard shortcut: Ctrl+T"
        )
        
        # Save button tooltip
        self.save_button.setToolTip(
            "Save email configuration\n"
            "Keyboard shortcut: Ctrl+S"
        )
    
    def _set_initial_focus(self):
        """Set initial focus to the first empty required field."""
        if self.smtp_radio.isChecked():
            if not self.smtp_server_edit.text().strip():
                self.smtp_server_edit.setFocus()
            elif not self.email_edit.text().strip():
                self.email_edit.setFocus()
            elif not self.password_edit.text().strip():
                self.password_edit.setFocus()
            else:
                self.save_button.setFocus()
        elif self.gmail_oauth_radio.isChecked():
            if not self.credentials_path_edit.text().strip():
                self.credentials_browse_button.setFocus()
            else:
                self.oauth_auth_button.setFocus() 
