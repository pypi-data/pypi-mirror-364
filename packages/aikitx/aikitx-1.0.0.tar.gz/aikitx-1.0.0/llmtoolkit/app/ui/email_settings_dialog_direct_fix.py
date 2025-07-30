"""
Email Settings Dialog Direct Fix

This module provides a direct fix for the issue where the Save button remains disabled
after successful Gmail OAuth authentication in the email settings dialog.
"""

import logging
from pathlib import Path

def apply_direct_fix(dialog):
    """
    Apply a direct fix to the email settings dialog to ensure the Save button is enabled
    after successful OAuth authentication.
    
    Args:
        dialog: The EmailSettingsDialog instance to fix
    """
    logger = logging.getLogger("gguf_loader.ui.email_settings_dialog_fix")
    logger.info("Applying direct OAuth Save button fix")
    
    # Force enable the Save button if OAuth is selected and authenticated
    if hasattr(dialog, 'gmail_oauth_radio') and dialog.gmail_oauth_radio.isChecked():
        if hasattr(dialog, 'oauth_status_label'):
            status_text = dialog.oauth_status_label.text()
            if "[OK]" in status_text or "authenticated" in status_text.lower():
                logger.info("OAuth authentication detected, forcing Save button to be enabled")
                dialog.save_button.setEnabled(True)
                
                # Update the status label to indicate the Save button is enabled
                dialog.oauth_status_label.setText(f"{status_text} - Save button enabled")
                dialog.oauth_status_label.setStyleSheet(
                    "color: #28a745; font-size: 11px; margin-top: 5px; font-weight: bold;"
                )
    
    # Override the _validate_form method to always enable the Save button for OAuth
    original_validate_form = dialog._validate_form
    
    def fixed_validate_form(self):
        """Fixed validation method that ensures the Save button is enabled for OAuth."""
        # Call the original method
        original_validate_form()
        
        # Force enable the Save button if OAuth is selected and authenticated
        if dialog.gmail_oauth_radio.isChecked():
            status_text = dialog.oauth_status_label.text()
            if "[OK]" in status_text or "authenticated" in status_text.lower():
                logger.info("OAuth authentication detected in validation, forcing Save button to be enabled")
                dialog.save_button.setEnabled(True)
    
    # Replace the method with our fixed version - use a lambda to bind it properly
    dialog._validate_form = lambda: fixed_validate_form(dialog)
    
    # Also patch the update_oauth_status method
    if hasattr(dialog, 'update_oauth_status'):
        original_update_oauth_status = dialog.update_oauth_status
        
        def fixed_update_oauth_status(self, success, message, email=""):
            """Fixed update_oauth_status method that ensures the Save button is enabled."""
            # Call the original method
            original_update_oauth_status(success, message, email)
            
            # Force enable the Save button if authentication was successful
            if success:
                logger.info("OAuth authentication successful, forcing Save button to be enabled")
                dialog.save_button.setEnabled(True)
        
        # Replace the method with our fixed version - use a lambda to bind it properly
        dialog.update_oauth_status = lambda success, message, email="": fixed_update_oauth_status(dialog, success, message, email)
    
    logger.info("Direct OAuth Save button fix applied successfully")