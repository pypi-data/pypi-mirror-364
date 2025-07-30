"""
Email Settings Dialog Fix

This module provides a fix for the issue where the Save button remains disabled
after successful Gmail OAuth authentication.
"""

import logging
from pathlib import Path

def apply_oauth_fix(email_settings_dialog):
    """
    Apply fix to enable the Save button after successful OAuth authentication.
    
    Args:
        email_settings_dialog: The EmailSettingsDialog instance to fix
    """
    logger = logging.getLogger("gguf_loader.ui.email_settings_dialog_fix")
    logger.info("Applying OAuth authentication fix")
    
    # Store the original update_oauth_status method
    original_update_oauth_status = email_settings_dialog.update_oauth_status
    
    # Create a patched version that ensures the Save button is enabled
    def patched_update_oauth_status(success, message, email=""):
        """
        Patched version of update_oauth_status that ensures the Save button is enabled.
        
        Args:
            success: Whether authentication was successful
            message: Status message to display
            email: Authenticated email address (if successful)
        """
        # Call the original method
        original_update_oauth_status(success, message, email)
        
        # If authentication was successful, explicitly enable the Save button
        if success:
            logger.info("OAuth authentication successful, enabling Save button")
            email_settings_dialog.save_button.setEnabled(True)
    
    # Replace the method with our patched version
    email_settings_dialog.update_oauth_status = patched_update_oauth_status
    
    # Also patch the _on_oauth_authenticate_clicked method to handle authentication results
    original_on_oauth_authenticate = email_settings_dialog._on_oauth_authenticate_clicked
    
    def patched_on_oauth_authenticate():
        """Patched version of _on_oauth_authenticate_clicked that ensures proper validation."""
        # Call the original method
        original_on_oauth_authenticate()
        
        # After authentication completes, ensure form validation is triggered
        email_settings_dialog._validate_form()
    
    # Replace the method with our patched version
    email_settings_dialog._on_oauth_authenticate_clicked = patched_on_oauth_authenticate
    
    logger.info("OAuth authentication fix applied successfully")