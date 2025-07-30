"""
Force Enable Save Button

This module provides a direct patch to force enable the Save button in the email settings dialog
after successful Gmail OAuth authentication.
"""

def force_enable_save_button(dialog):
    """
    Force enable the Save button in the email settings dialog.
    
    Args:
        dialog: The EmailSettingsDialog instance
    """
    # Directly enable the Save button
    if hasattr(dialog, 'save_button'):
        dialog.save_button.setEnabled(True)
        
        # Update the status label to indicate the Save button is enabled
        if hasattr(dialog, 'oauth_status_label'):
            current_text = dialog.oauth_status_label.text()
            if "Save button enabled" not in current_text:
                dialog.oauth_status_label.setText(f"{current_text} - Save button enabled")
                dialog.oauth_status_label.setStyleSheet(
                    "color: #28a745; font-size: 11px; margin-top: 5px; font-weight: bold;"
                )
        
        print("Save button has been force-enabled!")