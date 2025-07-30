"""
Dialog Theme Mixin

This module provides a centralized theming system for dialogs and UI components.
The DialogThemeMixin class can be inherited by any dialog to provide consistent
theme support across the application.
"""

import logging
from typing import Dict, Optional, Any
from PySide6.QtWidgets import QDialog, QWidget
from PySide6.QtCore import QObject

from ..theme_manager import ThemeManager


class DialogThemeMixin:
    """
    Mixin class that provides centralized dark theme functionality for dialogs.
    
    This mixin should be inherited by dialog classes to provide consistent
    dark theme support. It integrates with the ThemeManager to automatically
    apply dark theme styling for consistency.
    
    Features:
    - Consistent dark theme styling for all UI elements
    - Automatic dark theme application
    - Easy integration with existing dialogs
    
    Usage:
        class MyDialog(QDialog, DialogThemeMixin):
            def __init__(self, parent=None):
                super().__init__(parent)
                self._apply_theme_to_dialog()
    """
    
    def __init__(self, *args, **kwargs):
        """Initialize the theme mixin."""
        super().__init__(*args, **kwargs)
        self._theme_manager = None
        self._logger = logging.getLogger(f"gguf_loader.ui.mixins.theme_mixin.{self.__class__.__name__}")
    
    def _get_theme_manager(self) -> ThemeManager:
        """
        Get or create a theme manager instance.
        
        Returns:
            ThemeManager instance
        """
        if self._theme_manager is None:
            self._theme_manager = ThemeManager()
        return self._theme_manager
    
    def _apply_theme_to_dialog(self, parent_widget: Optional[QWidget] = None):
        """
        Apply consistent dark theme to the current dialog.
        
        Args:
            parent_widget: Parent widget (ignored - always use dark theme for consistency)
        """
        try:
            # Get theme manager and apply consistent dark theme
            theme_manager = self._get_theme_manager()
            
            # Get dialog styles and apply them (always dark mode)
            styles = theme_manager.get_dialog_theme_styles()
            
            # Combine all styles
            combined_style = ""
            for style_category, style_css in styles.items():
                combined_style += style_css + "\n"
            
            # Apply the combined stylesheet
            if hasattr(self, 'setStyleSheet'):
                self.setStyleSheet(combined_style)
            
            # Also apply theme to all child input widgets to ensure they inherit properly
            self._apply_theme_to_child_widgets()
            
            self._logger.debug(f"Applied consistent dark theme to dialog: {self.__class__.__name__}")
            
        except Exception as e:
            self._logger.error(f"Failed to apply theme to dialog {self.__class__.__name__}: {e}")
    
    def _apply_theme_to_child_widgets(self):
        """
        Apply consistent dark theme styling directly to child input widgets.
        
        This ensures that input fields properly inherit the theme colors,
        which Qt doesn't always do automatically.
        """
        try:
            from PySide6.QtWidgets import QLineEdit, QTextEdit, QPlainTextEdit, QSpinBox, QComboBox
            
            # Always use dark theme colors for consistency
            bg_color = "#1e1e1e"
            text_color = "#ffffff"
            border_color = "#404040"
            focus_color = "#0078d4"
            placeholder_color = "#9ca3af"
            surface_color = "#2d2d30"
            
            # Find all input widgets in the dialog
            if hasattr(self, 'findChildren'):
                # Style QLineEdit widgets
                for line_edit in self.findChildren(QLineEdit):
                    if not line_edit.styleSheet() or "border-color:" not in line_edit.styleSheet():
                        line_edit.setStyleSheet(f"""
                            QLineEdit {{
                                background-color: {bg_color};
                                color: {text_color};
                                border: 2px solid {border_color};
                                border-radius: 6px;
                                padding: 8px 12px;
                                font-size: 13px;
                                selection-background-color: {focus_color};
                                selection-color: white;
                            }}
                            QLineEdit:focus {{
                                border-color: {focus_color};
                                outline: none;
                            }}
                            QLineEdit::placeholder {{
                                color: {placeholder_color};
                                font-style: italic;
                            }}
                        """)
                
                # Style QTextEdit widgets
                for text_edit in self.findChildren(QTextEdit):
                    if not text_edit.styleSheet() or "border-color:" not in text_edit.styleSheet():
                        text_edit.setStyleSheet(f"""
                            QTextEdit {{
                                background-color: {bg_color};
                                color: {text_color};
                                border: 2px solid {border_color};
                                border-radius: 6px;
                                padding: 8px 12px;
                                font-size: 13px;
                                selection-background-color: {focus_color};
                                selection-color: white;
                                line-height: 1.4;
                            }}
                            QTextEdit:focus {{
                                border-color: {focus_color};
                                outline: none;
                            }}
                        """)
                
                # Style QPlainTextEdit widgets
                for plain_text_edit in self.findChildren(QPlainTextEdit):
                    if not plain_text_edit.styleSheet() or "border-color:" not in plain_text_edit.styleSheet():
                        plain_text_edit.setStyleSheet(f"""
                            QPlainTextEdit {{
                                background-color: {bg_color};
                                color: {text_color};
                                border: 2px solid {border_color};
                                border-radius: 6px;
                                padding: 8px 12px;
                                font-size: 13px;
                                selection-background-color: {focus_color};
                                selection-color: white;
                                line-height: 1.4;
                            }}
                            QPlainTextEdit:focus {{
                                border-color: {focus_color};
                                outline: none;
                            }}
                        """)
                
                # Style QSpinBox widgets
                for spin_box in self.findChildren(QSpinBox):
                    if not spin_box.styleSheet() or "border-color:" not in spin_box.styleSheet():
                        spin_box.setStyleSheet(f"""
                            QSpinBox {{
                                background-color: {bg_color};
                                color: {text_color};
                                border: 2px solid {border_color};
                                border-radius: 6px;
                                padding: 8px 12px;
                                font-size: 13px;
                            }}
                            QSpinBox:focus {{
                                border-color: {focus_color};
                                outline: none;
                            }}
                        """)
                
                # Style QComboBox widgets
                for combo_box in self.findChildren(QComboBox):
                    if not combo_box.styleSheet() or "border-color:" not in combo_box.styleSheet():
                        combo_box.setStyleSheet(f"""
                            QComboBox {{
                                background-color: {bg_color};
                                color: {text_color};
                                border: 2px solid {border_color};
                                border-radius: 6px;
                                padding: 8px 12px;
                                font-size: 13px;
                            }}
                            QComboBox:focus {{
                                border-color: {focus_color};
                                outline: none;
                            }}
                            QComboBox::drop-down {{
                                background-color: {surface_color};
                                border: none;
                                border-left: 1px solid {border_color};
                                border-radius: 0px 4px 4px 0px;
                                width: 20px;
                            }}
                            QComboBox::drop-down:hover {{
                                background-color: {focus_color};
                            }}
                        """)
            
            self._logger.debug("Applied consistent dark theme to child input widgets")
            
        except Exception as e:
            self._logger.error(f"Failed to apply theme to child widgets: {e}")
    
    def _get_input_field_styles(self) -> str:
        """
        Get CSS styles for input fields - Always dark theme for consistency.
        
        Returns:
            CSS string for input field styling
        """
        try:
            theme_manager = self._get_theme_manager()
            styles = theme_manager.get_dialog_theme_styles()
            return styles.get('input_fields', '')
        except Exception as e:
            self._logger.error(f"Failed to get input field styles: {e}")
            return ""
    
    def _get_button_styles(self) -> str:
        """
        Get CSS styles for buttons - Always dark theme for consistency.
        
        Returns:
            CSS string for button styling
        """
        try:
            theme_manager = self._get_theme_manager()
            styles = theme_manager.get_dialog_theme_styles()
            return styles.get('buttons', '')
        except Exception as e:
            self._logger.error(f"Failed to get button styles: {e}")
            return ""
    
    def _get_group_box_styles(self) -> str:
        """
        Get CSS styles for group boxes - Always dark theme for consistency.
        
        Returns:
            CSS string for group box styling
        """
        try:
            theme_manager = self._get_theme_manager()
            styles = theme_manager.get_dialog_theme_styles()
            return styles.get('group_boxes', '')
        except Exception as e:
            self._logger.error(f"Failed to get group box styles: {e}")
            return ""
    
    def _get_label_styles(self) -> str:
        """
        Get CSS styles for labels - Always dark theme for consistency.
        
        Returns:
            CSS string for label styling
        """
        try:
            theme_manager = self._get_theme_manager()
            styles = theme_manager.get_dialog_theme_styles()
            return styles.get('labels', '')
        except Exception as e:
            self._logger.error(f"Failed to get label styles: {e}")
            return ""
    
    def _get_checkbox_radio_styles(self) -> str:
        """
        Get CSS styles for checkboxes and radio buttons - Always dark theme.
        
        Returns:
            CSS string for checkbox and radio button styling
        """
        try:
            theme_manager = self._get_theme_manager()
            styles = theme_manager.get_dialog_theme_styles()
            return styles.get('checkboxes_radio', '')
        except Exception as e:
            self._logger.error(f"Failed to get checkbox/radio styles: {e}")
            return ""
    
    def _get_dialog_styles(self) -> str:
        """
        Get CSS styles for the dialog container - Always dark theme.
        
        Returns:
            CSS string for dialog styling
        """
        try:
            theme_manager = self._get_theme_manager()
            styles = theme_manager.get_dialog_theme_styles()
            return styles.get('dialog', '')
        except Exception as e:
            self._logger.error(f"Failed to get dialog styles: {e}")
            return ""
    
    def _get_all_dialog_styles(self) -> str:
        """
        Get combined CSS styles for all dialog elements - Always dark theme.
        
        Returns:
            Combined CSS string for all dialog elements
        """
        try:
            theme_manager = self._get_theme_manager()
            styles = theme_manager.get_dialog_theme_styles()
            
            # Combine all styles
            combined_styles = ""
            for style_category, style_css in styles.items():
                combined_styles += style_css + "\n"
            
            return combined_styles
        except Exception as e:
            self._logger.error(f"Failed to get combined dialog styles: {e}")
            return ""
    
    def _detect_theme_mode(self, parent_widget: Optional[QWidget] = None) -> bool:
        """
        Always returns True since only dark mode is available for consistency.
        
        Args:
            parent_widget: Parent widget (ignored)
            
        Returns:
            True (always dark mode)
        """
        return True
    
    def _get_theme_colors(self) -> Dict[str, str]:
        """
        Get consistent dark theme color dictionary.
        
        Returns:
            Dictionary of dark theme colors
        """
        try:
            theme_manager = self._get_theme_manager()
            return theme_manager.get_colors()  # Always returns dark theme colors
        except Exception as e:
            self._logger.error(f"Failed to get theme colors: {e}")
            # Return default dark theme colors as fallback
            return {
                "background": "#1e1e1e",
                "surface": "#2d2d30",
                "primary": "#0078d4",
                "text": "#ffffff",
                "text_secondary": "#d1d5db",
                "border": "#404040",
                "success": "#10b981",
                "error": "#ef4444"
            }
    
    def _apply_custom_styles(self, custom_css: str):
        """
        Apply custom CSS styles in addition to the standard dark theme.
        
        Args:
            custom_css: Custom CSS to apply
        """
        try:
            # Get base theme styles
            base_styles = self._get_all_dialog_styles()
            
            # Combine with custom styles
            combined_styles = base_styles + "\n" + custom_css
            
            # Apply to dialog
            if hasattr(self, 'setStyleSheet'):
                self.setStyleSheet(combined_styles)
            
            self._logger.debug(f"Applied custom styles to dialog: {self.__class__.__name__}")
            
        except Exception as e:
            self._logger.error(f"Failed to apply custom styles: {e}")
    
    def _refresh_theme(self):
        """
        Refresh the theme for the dialog.
        
        This method can be called when the theme changes to update the dialog's appearance.
        """
        try:
            self._apply_theme_to_dialog()
            self._logger.debug(f"Refreshed theme for dialog: {self.__class__.__name__}")
        except Exception as e:
            self._logger.error(f"Failed to refresh theme: {e}")
    
    def _setup_theme_change_handler(self):
        """
        Set up automatic theme change handling.
        
        This connects to the theme manager's theme_changed signal to automatically
        update the dialog when the theme changes.
        """
        try:
            theme_manager = self._get_theme_manager()
            if hasattr(theme_manager, 'theme_changed'):
                theme_manager.theme_changed.connect(self._on_theme_changed)
                self._logger.debug(f"Set up theme change handler for dialog: {self.__class__.__name__}")
        except Exception as e:
            self._logger.error(f"Failed to setup theme change handler: {e}")
    
    def _on_theme_changed(self, theme_name: str):
        """
        Handle theme change events.
        
        Args:
            theme_name: Name of the new theme
        """
        try:
            self._refresh_theme()
            self._logger.debug(f"Handled theme change to {theme_name} for dialog: {self.__class__.__name__}")
        except Exception as e:
            self._logger.error(f"Failed to handle theme change: {e}")
    
    # Button Helper Methods
    
    def _set_button_type(self, button, button_type: str):
        """
        Set the button type for themed styling.
        
        Args:
            button: QPushButton instance
            button_type: Type of button ('primary', 'cancel', 'danger', 'info', 'warning', 'outline', 'flat', 'oauth', 'ai')
        """
        try:
            button.setProperty("buttonType", button_type)
            # Force style refresh
            button.style().unpolish(button)
            button.style().polish(button)
            self._logger.debug(f"Set button type '{button_type}' for button: {button.text()}")
        except Exception as e:
            self._logger.error(f"Failed to set button type: {e}")
    
    def _set_button_size(self, button, size: str):
        """
        Set the button size for themed styling.
        
        Args:
            button: QPushButton instance
            size: Size of button ('small', 'normal', 'large')
        """
        try:
            button.setProperty("buttonSize", size)
            # Force style refresh
            button.style().unpolish(button)
            button.style().polish(button)
            self._logger.debug(f"Set button size '{size}' for button: {button.text()}")
        except Exception as e:
            self._logger.error(f"Failed to set button size: {e}")
    
    def _set_button_icon_flag(self, button, has_icon: bool = True):
        """
        Set the icon flag for button styling (affects text alignment).
        
        Args:
            button: QPushButton instance
            has_icon: Whether the button has an icon
        """
        try:
            button.setProperty("hasIcon", "true" if has_icon else "false")
            # Force style refresh
            button.style().unpolish(button)
            button.style().polish(button)
            self._logger.debug(f"Set icon flag '{has_icon}' for button: {button.text()}")
        except Exception as e:
            self._logger.error(f"Failed to set button icon flag: {e}")
    
    def _create_primary_button(self, text: str, size: str = "normal") -> 'QPushButton':
        """
        Create a primary button with proper theming.
        
        Args:
            text: Button text
            size: Button size ('small', 'normal', 'large')
            
        Returns:
            Configured QPushButton
        """
        try:
            from PySide6.QtWidgets import QPushButton
            button = QPushButton(text)
            self._set_button_type(button, "primary")
            if size != "normal":
                self._set_button_size(button, size)
            return button
        except Exception as e:
            self._logger.error(f"Failed to create primary button: {e}")
            from PySide6.QtWidgets import QPushButton
            return QPushButton(text)
    
    def _create_secondary_button(self, text: str, size: str = "normal") -> 'QPushButton':
        """
        Create a secondary button with proper theming.
        
        Args:
            text: Button text
            size: Button size ('small', 'normal', 'large')
            
        Returns:
            Configured QPushButton
        """
        try:
            from PySide6.QtWidgets import QPushButton
            button = QPushButton(text)
            self._set_button_type(button, "secondary")
            if size != "normal":
                self._set_button_size(button, size)
            return button
        except Exception as e:
            self._logger.error(f"Failed to create secondary button: {e}")
            from PySide6.QtWidgets import QPushButton
            return QPushButton(text)
    
    def _create_cancel_button(self, text: str = "Cancel", size: str = "normal") -> 'QPushButton':
        """
        Create a cancel button with proper theming.
        
        Args:
            text: Button text
            size: Button size ('small', 'normal', 'large')
            
        Returns:
            Configured QPushButton
        """
        try:
            from PySide6.QtWidgets import QPushButton
            button = QPushButton(text)
            self._set_button_type(button, "cancel")
            if size != "normal":
                self._set_button_size(button, size)
            return button
        except Exception as e:
            self._logger.error(f"Failed to create cancel button: {e}")
            from PySide6.QtWidgets import QPushButton
            return QPushButton(text)
    
    def _create_info_button(self, text: str, size: str = "normal") -> 'QPushButton':
        """
        Create an info/help button with proper theming.
        
        Args:
            text: Button text
            size: Button size ('small', 'normal', 'large')
            
        Returns:
            Configured QPushButton
        """
        try:
            from PySide6.QtWidgets import QPushButton
            button = QPushButton(text)
            self._set_button_type(button, "info")
            if size != "normal":
                self._set_button_size(button, size)
            return button
        except Exception as e:
            self._logger.error(f"Failed to create info button: {e}")
            from PySide6.QtWidgets import QPushButton
            return QPushButton(text)
    
    def _create_oauth_button(self, text: str = "🔐 Authenticate with Google", size: str = "normal") -> 'QPushButton':
        """
        Create an OAuth button with proper theming.
        
        Args:
            text: Button text
            size: Button size ('small', 'normal', 'large')
            
        Returns:
            Configured QPushButton
        """
        try:
            from PySide6.QtWidgets import QPushButton
            button = QPushButton(text)
            self._set_button_type(button, "oauth")
            self._set_button_icon_flag(button, True)
            if size != "normal":
                self._set_button_size(button, size)
            return button
        except Exception as e:
            self._logger.error(f"Failed to create OAuth button: {e}")
            from PySide6.QtWidgets import QPushButton
            return QPushButton(text)
    
    def _create_ai_button(self, text: str = "🧠 Generate with AI", size: str = "normal") -> 'QPushButton':
        """
        Create an AI/Generate button with proper theming.
        
        Args:
            text: Button text
            size: Button size ('small', 'normal', 'large')
            
        Returns:
            Configured QPushButton
        """
        try:
            from PySide6.QtWidgets import QPushButton
            button = QPushButton(text)
            self._set_button_type(button, "ai")
            self._set_button_icon_flag(button, True)
            if size != "normal":
                self._set_button_size(button, size)
            return button
        except Exception as e:
            self._logger.error(f"Failed to create AI button: {e}")
            from PySide6.QtWidgets import QPushButton
            return QPushButton(text)