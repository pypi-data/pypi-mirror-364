"""
Email Settings Dialog Simple Fix

This module provides a simple direct fix for the issue where the Save button remains disabled
after successful Gmail OAuth authentication in the email settings dialog.
"""

import logging

def apply_simple_fix(dialog):
    """
    Apply a simple direct fix to the email settings dialog to ensure the Save button is enabled
    after successful OAuth authentication.
    
    Args:
        dialog: The EmailSettingsDialog instance to fix
    """
    logger = logging.getLogger("gguf_loader.ui.email_settings_dialog_fix")
    logger.info("Applying simple OAuth Save button fix")
    
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
    
    # Add a special method to force enable the Save button
    dialog.force_enable_save_button = lambda: dialog.save_button.setEnabled(True)
    
    logger.info("Simple OAuth Save button fix applied successfully")