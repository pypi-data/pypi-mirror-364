"""
Dark Theme Helper

This module provides utilities to apply consistent dark theme to any Qt widget or dialog.
This simplifies the theming process by providing a single, consistent dark theme
instead of complex light/dark mode switching.
"""

from typing import Optional
from PySide6.QtWidgets import QWidget, QDialog, QApplication
from .theme_manager import ThemeManager


class DarkThemeHelper:
    """Helper class to apply consistent dark theme to Qt widgets."""
    
    def __init__(self):
        """Initialize the dark theme helper."""
        self.theme_manager = ThemeManager()
        self.colors = self.theme_manager.get_colors()
    
    def apply_to_widget(self, widget: QWidget):
        """
        Apply consistent dark theme to any Qt widget.
        
        Args:
            widget: The widget to apply dark theme to
        """
        try:
            widget.setStyleSheet(f"""
                QWidget {{
                    background-color: {self.colors["background"]};
                    color: {self.colors["text"]};
                }}
                
                /* Input Fields */
                QLineEdit, QTextEdit, QPlainTextEdit {{
                    background-color: {self.colors["surface"]};
                    color: {self.colors["text"]};
                    border: 2px solid {self.colors["border"]};
                    border-radius: 6px;
                    padding: 8px 12px;
                    font-size: 13px;
                    selection-background-color: {self.colors["primary"]};
                    selection-color: white;
                }}
                
                QLineEdit:focus, QTextEdit:focus, QPlainTextEdit:focus {{
                    border-color: {self.colors["primary"]};
                    outline: none;
                }}
                
                QLineEdit::placeholder {{
                    color: {self.colors["text_secondary"]};
                    font-style: italic;
                }}
                
                /* Buttons */
                QPushButton {{
                    background-color: {self.colors["surface"]};
                    color: {self.colors["text"]};
                    border: 2px solid {self.colors["border"]};
                    border-radius: 6px;
                    padding: 10px 20px;
                    font-weight: bold;
                    font-size: 13px;
                    min-width: 80px;
                }}
                
                QPushButton:hover {{
                    background-color: {self.colors["border"]};
                }}
                
                QPushButton:pressed {{
                    background-color: {self.colors["primary"]};
                    color: white;
                }}
                
                QPushButton:disabled {{
                    background-color: {self.colors["border"]};
                    color: {self.colors["text_secondary"]};
                }}
                
                /* Primary Buttons */
                QPushButton[buttonType="primary"] {{
                    background-color: {self.colors["primary"]};
                    color: white;
                    border: 2px solid {self.colors["primary"]};
                }}
                
                QPushButton[buttonType="primary"]:hover {{
                    background-color: #106ebe;
                    border-color: #106ebe;
                }}
                
                QPushButton[buttonType="primary"]:pressed {{
                    background-color: #005a9e;
                    border-color: #005a9e;
                }}
                
                /* Cancel/Secondary Buttons */
                QPushButton[buttonType="cancel"], QPushButton[buttonType="secondary"] {{
                    background-color: {self.colors["surface"]};
                    color: {self.colors["text"]};
                    border: 2px solid {self.colors["border"]};
                }}
                
                QPushButton[buttonType="cancel"]:hover, QPushButton[buttonType="secondary"]:hover {{
                    background-color: {self.colors["border"]};
                }}
                
                /* Error/Danger Buttons */
                QPushButton[buttonType="danger"] {{
                    background-color: {self.colors["error"]};
                    color: white;
                    border: 2px solid {self.colors["error"]};
                }}
                
                QPushButton[buttonType="danger"]:hover {{
                    background-color: #c82333;
                    border-color: #c82333;
                }}
                
                /* Group Boxes */
                QGroupBox {{
                    font-weight: bold;
                    border: 2px solid {self.colors["border"]};
                    border-radius: 8px;
                    margin-top: 10px;
                    padding-top: 15px;
                    color: {self.colors["text"]};
                }}
                
                QGroupBox::title {{
                    subcontrol-origin: margin;
                    left: 10px;
                    padding: 0 8px 0 8px;
                    color: {self.colors["text"]};
                    background-color: {self.colors["background"]};
                }}
                
                /* Labels */
                QLabel {{
                    color: {self.colors["text"]};
                }}
                
                /* Combo Boxes */
                QComboBox {{
                    background-color: {self.colors["surface"]};
                    color: {self.colors["text"]};
                    border: 2px solid {self.colors["border"]};
                    border-radius: 6px;
                    padding: 8px 12px;
                    font-size: 13px;
                }}
                
                QComboBox:focus {{
                    border-color: {self.colors["primary"]};
                }}
                
                QComboBox::drop-down {{
                    background-color: {self.colors["surface"]};
                    border: none;
                    border-left: 1px solid {self.colors["border"]};
                    border-radius: 0px 4px 4px 0px;
                    width: 20px;
                }}
                
                QComboBox::drop-down:hover {{
                    background-color: {self.colors["primary"]};
                }}
                
                /* Spin Boxes */
                QSpinBox, QDoubleSpinBox {{
                    background-color: {self.colors["surface"]};
                    color: {self.colors["text"]};
                    border: 2px solid {self.colors["border"]};
                    border-radius: 6px;
                    padding: 8px 12px;
                    font-size: 13px;
                }}
                
                QSpinBox:focus, QDoubleSpinBox:focus {{
                    border-color: {self.colors["primary"]};
                }}
                
                /* Check Boxes and Radio Buttons */
                QCheckBox, QRadioButton {{
                    color: {self.colors["text"]};
                    spacing: 8px;
                }}
                
                QCheckBox::indicator, QRadioButton::indicator {{
                    width: 16px;
                    height: 16px;
                    background-color: {self.colors["surface"]};
                    border: 2px solid {self.colors["border"]};
                    border-radius: 3px;
                }}
                
                QCheckBox::indicator:checked, QRadioButton::indicator:checked {{
                    background-color: {self.colors["primary"]};
                    border-color: {self.colors["primary"]};
                }}
                
                /* Progress Bars */
                QProgressBar {{
                    border: 1px solid {self.colors["border"]};
                    border-radius: 6px;
                    background-color: {self.colors["surface"]};
                    text-align: center;
                    color: {self.colors["text"]};
                }}
                
                QProgressBar::chunk {{
                    background-color: {self.colors["primary"]};
                    border-radius: 5px;
                }}
                
                /* Scroll Areas */
                QScrollArea {{
                    background-color: {self.colors["background"]};
                    border: 1px solid {self.colors["border"]};
                    border-radius: 6px;
                }}
                
                QScrollBar:vertical {{
                    background-color: {self.colors["surface"]};
                    width: 12px;
                    border-radius: 6px;
                }}
                
                QScrollBar::handle:vertical {{
                    background-color: {self.colors["border"]};
                    border-radius: 6px;
                    min-height: 20px;
                }}
                
                QScrollBar::handle:vertical:hover {{
                    background-color: {self.colors["primary"]};
                }}
            """)
            
        except Exception as e:
            print(f"Failed to apply dark theme to widget: {e}")
    
    def apply_to_dialog(self, dialog: QDialog):
        """
        Apply consistent dark theme to any Qt dialog.
        
        Args:
            dialog: The dialog to apply dark theme to
        """
        self.apply_to_widget(dialog)
        
        # Additional dialog-specific styling
        try:
            dialog.setStyleSheet(dialog.styleSheet() + f"""
                QDialog {{
                    background-color: {self.colors["background"]};
                    color: {self.colors["text"]};
                }}
            """)
        except Exception as e:
            print(f"Failed to apply dialog-specific styling: {e}")
    
    def apply_to_application(self, app: Optional[QApplication] = None):
        """
        Apply consistent dark theme to the entire application.
        
        Args:
            app: QApplication instance. If None, uses QApplication.instance()
        """
        if app is None:
            app = QApplication.instance()
        
        if app is None:
            print("No QApplication instance found")
            return
        
        try:
            app.setStyleSheet(f"""
                QApplication {{
                    background-color: {self.colors["background"]};
                    color: {self.colors["text"]};
                }}
            """)
        except Exception as e:
            print(f"Failed to apply application-wide dark theme: {e}")


# Global instance for easy access
dark_theme = DarkThemeHelper()


def apply_dark_theme_to_widget(widget: QWidget):
    """
    Convenience function to apply dark theme to any widget.
    
    Args:
        widget: The widget to apply dark theme to
    """
    dark_theme.apply_to_widget(widget)


def apply_dark_theme_to_dialog(dialog: QDialog):
    """
    Convenience function to apply dark theme to any dialog.
    
    Args:
        dialog: The dialog to apply dark theme to
    """
    dark_theme.apply_to_dialog(dialog)


def apply_dark_theme_to_application(app: Optional[QApplication] = None):
    """
    Convenience function to apply dark theme to the entire application.
    
    Args:
        app: QApplication instance. If None, uses QApplication.instance()
    """
    dark_theme.apply_to_application(app)