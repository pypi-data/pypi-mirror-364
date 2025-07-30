"""
Theme Manager

This module provides theme management functionality including dark mode support
and dynamic theme switching for the application.
"""

import logging
from typing import Dict, Any, Optional
from enum import Enum

from PySide6.QtWidgets import QApplication, QWidget, QDialog
from PySide6.QtCore import QObject, Signal
from PySide6.QtGui import QPalette, QColor


class Theme(Enum):
    """Available themes - Dark mode only for consistency."""
    DARK = "dark"


class ThemeManager(QObject):
    """
    Manages application themes and provides dark mode functionality.
    
    Features:
    - Light and dark theme support
    - Dynamic theme switching
    - Theme persistence
    - Custom color schemes
    """
    
    # Signals
    theme_changed = Signal(str)  # Emitted when theme changes
    
    # Light theme colors
    LIGHT_THEME = {
        "background": "#ffffff",
        "surface": "#f8f9fa",
        "primary": "#0078d4",
        "secondary": "#6c757d",
        "text": "#212529",
        "text_secondary": "#6c757d",
        "border": "#dee2e6",
        "success": "#28a745",
        "warning": "#ffc107",
        "error": "#dc3545",
        "info": "#17a2b8"
    }
    
    # Dark theme colors
    DARK_THEME = {
        "background": "#1e1e1e",
        "surface": "#2d2d30",
        "primary": "#0078d4",
        "secondary": "#9ca3af",
        "text": "#ffffff",
        "text_secondary": "#d1d5db",
        "border": "#404040",
        "success": "#10b981",
        "warning": "#f59e0b",
        "error": "#ef4444",
        "info": "#06b6d4"
    }
    
    def __init__(self, config_manager=None):
        """
        Initialize the theme manager - Dark mode only for consistency.
        
        Args:
            config_manager: Configuration manager (theme is always dark)
        """
        super().__init__()
        
        self.logger = logging.getLogger("gguf_loader.ui.theme_manager")
        self.config_manager = config_manager
        # Always use dark theme for consistency
        self.current_theme = Theme.DARK
        
        # Apply dark theme immediately
        self._apply_theme()
        
        self.logger.info("Theme manager initialized with dark mode only")
    
    def get_current_theme(self) -> Theme:
        """Get the current theme."""
        return self.current_theme
    
    def is_dark_mode(self) -> bool:
        """Check if dark mode is active."""
        return True  # Always dark mode for consistency
    
    def get_colors(self) -> Dict[str, str]:
        """Get the current theme colors (always dark for consistency)."""
        return self.DARK_THEME.copy()
    
    def get_dialog_theme_styles(self, is_dark_mode: bool = True) -> Dict[str, str]:
        """
        Get dialog theme styles (always dark for consistency).
        
        Args:
            is_dark_mode: Ignored - always returns dark theme styles
            
        Returns:
            Dictionary of CSS styles for dialog elements
        """
        colors = self.DARK_THEME
        
        return {
            "dialog": f"""
                QDialog {{
                    background-color: {colors["background"]};
                    color: {colors["text"]};
                }}
            """,
            
            "input_fields": f"""
                QLineEdit, QTextEdit, QPlainTextEdit {{
                    background-color: {colors["surface"]};
                    color: {colors["text"]};
                    border: 2px solid {colors["border"]};
                    border-radius: 6px;
                    padding: 8px 12px;
                    font-size: 13px;
                    selection-background-color: {colors["primary"]};
                    selection-color: white;
                }}
                
                QLineEdit:focus, QTextEdit:focus, QPlainTextEdit:focus {{
                    border-color: {colors["primary"]};
                    outline: none;
                }}
                
                QLineEdit::placeholder {{
                    color: {colors["text_secondary"]};
                    font-style: italic;
                }}
            """,
            
            "buttons": f"""
                QPushButton {{
                    background-color: {colors["surface"]};
                    color: {colors["text"]};
                    border: 2px solid {colors["border"]};
                    border-radius: 6px;
                    padding: 10px 20px;
                    font-weight: bold;
                    font-size: 13px;
                    min-width: 80px;
                }}
                
                QPushButton:hover {{
                    background-color: {colors["border"]};
                }}
                
                QPushButton:pressed {{
                    background-color: {colors["primary"]};
                    color: white;
                }}
                
                QPushButton:disabled {{
                    background-color: {colors["border"]};
                    color: {colors["text_secondary"]};
                }}
                
                QPushButton[buttonType="primary"] {{
                    background-color: {colors["primary"]};
                    color: white;
                    border-color: {colors["primary"]};
                }}
                
                QPushButton[buttonType="primary"]:hover {{
                    background-color: #106ebe;
                    border-color: #106ebe;
                }}
                
                QPushButton[buttonType="cancel"] {{
                    background-color: {colors["surface"]};
                    color: {colors["text"]};
                    border-color: {colors["border"]};
                }}
                
                QPushButton[buttonType="ai"] {{
                    background-color: {colors["info"]};
                    color: white;
                    border-color: {colors["info"]};
                }}
                
                QPushButton[buttonType="ai"]:hover {{
                    background-color: #0891b2;
                    border-color: #0891b2;
                }}
            """,
            
            "group_boxes": f"""
                QGroupBox {{
                    font-weight: bold;
                    border: 2px solid {colors["border"]};
                    border-radius: 8px;
                    margin-top: 10px;
                    padding-top: 15px;
                    color: {colors["text"]};
                }}
                
                QGroupBox::title {{
                    subcontrol-origin: margin;
                    left: 10px;
                    padding: 0 8px 0 8px;
                    color: {colors["text"]};
                    background-color: {colors["background"]};
                }}
            """,
            
            "labels": f"""
                QLabel {{
                    color: {colors["text"]};
                }}
            """,
            
            "checkboxes_radio": f"""
                QCheckBox, QRadioButton {{
                    color: {colors["text"]};
                    spacing: 8px;
                }}
                
                QCheckBox::indicator, QRadioButton::indicator {{
                    width: 16px;
                    height: 16px;
                    background-color: {colors["surface"]};
                    border: 2px solid {colors["border"]};
                    border-radius: 3px;
                }}
                
                QCheckBox::indicator:checked, QRadioButton::indicator:checked {{
                    background-color: {colors["primary"]};
                    border-color: {colors["primary"]};
                }}
            """
        }
    
    def toggle_theme(self):
        """Toggle theme - No-op since only dark mode is available."""
        self.logger.info("Theme toggle requested - staying in dark mode for consistency")
    
    def set_theme(self, theme: Theme):
        """
        Set the application theme - Always dark for consistency.
        
        Args:
            theme: Theme to apply (ignored - always dark)
        """
        # Always use dark theme
        self.current_theme = Theme.DARK
        
        # Apply dark theme
        self._apply_theme()
        
        # Save dark theme preference
        if self.config_manager:
            self.config_manager.set_value("theme", "dark")
        
        # Emit signal
        self.theme_changed.emit("dark")
        
        self.logger.info("Theme set to dark mode (only available theme)")
    
    def _apply_theme(self):
        """Apply the dark theme to the application."""
        app = QApplication.instance()
        if not app:
            return
        
        # Always use dark theme colors
        colors = self.DARK_THEME
        
        # Create and apply palette
        palette = self._create_palette(colors)
        app.setPalette(palette)
        
        # Apply stylesheet
        stylesheet = self._create_stylesheet(colors)
        app.setStyleSheet(stylesheet)
    
    def _create_palette(self, colors: Dict[str, str]) -> QPalette:
        """
        Create a QPalette from color scheme.
        
        Args:
            colors: Color scheme dictionary
            
        Returns:
            QPalette object
        """
        palette = QPalette()
        
        # Window colors
        palette.setColor(QPalette.Window, QColor(colors["background"]))
        palette.setColor(QPalette.WindowText, QColor(colors["text"]))
        
        # Base colors (for input fields) - Always dark
        palette.setColor(QPalette.Base, QColor("#1e1e1e"))  # Pure black for text boxes in dark mode
        palette.setColor(QPalette.AlternateBase, QColor(colors["background"]))
        
        # Text colors
        palette.setColor(QPalette.Text, QColor(colors["text"]))
        palette.setColor(QPalette.BrightText, QColor(colors["text"]))
        
        # Button colors
        palette.setColor(QPalette.Button, QColor(colors["surface"]))
        palette.setColor(QPalette.ButtonText, QColor(colors["text"]))
        
        # Highlight colors
        palette.setColor(QPalette.Highlight, QColor(colors["primary"]))
        palette.setColor(QPalette.HighlightedText, QColor("#ffffff"))
        
        # Disabled colors
        disabled_text = QColor(colors["text_secondary"])
        palette.setColor(QPalette.Disabled, QPalette.Text, disabled_text)
        palette.setColor(QPalette.Disabled, QPalette.ButtonText, disabled_text)
        
        return palette
    
    def _create_stylesheet(self, colors: Dict[str, str]) -> str:
        """
        Create application stylesheet from color scheme.
        
        Args:
            colors: Color scheme dictionary
            
        Returns:
            CSS stylesheet string
        """
        return f"""
        /* Main Window */
        QMainWindow {{
            background-color: {colors["background"]};
            color: {colors["text"]};
        }}
        
        /* Widgets */
        QWidget {{
            background-color: {colors["background"]};
            color: {colors["text"]};
        }}
        
        /* Buttons */
        QPushButton {{
            background-color: {colors["surface"]};
            border: 1px solid {colors["border"]};
            border-radius: 6px;
            padding: 8px 16px;
            color: {colors["text"]};
        }}
        
        QPushButton:hover {{
            background-color: {colors["primary"]};
            color: #ffffff;
        }}
        
        QPushButton:pressed {{
            background-color: {self._darken_color(colors["primary"])};
        }}
        
        QPushButton:disabled {{
            background-color: {colors["border"]};
            color: {colors["text_secondary"]};
        }}
        
        /* Input Fields */
        QLineEdit, QTextEdit, QPlainTextEdit, QTextBrowser {{
            background-color: {colors["background"]};
            border: 2px solid {colors["border"]};
            border-radius: 6px;
            padding: 8px 12px;
            color: {colors["text"]};
            font-size: 13px;
            selection-background-color: {colors["primary"]};
            selection-color: white;
        }}
        
        QLineEdit:focus, QTextEdit:focus, QPlainTextEdit:focus {{
            border-color: {colors["primary"]};
            outline: none;
        }}
        
        QLineEdit:hover, QTextEdit:hover, QPlainTextEdit:hover {{
            border-color: {self._lighten_color(colors["border"])};
        }}
        
        QLineEdit:disabled, QTextEdit:disabled, QPlainTextEdit:disabled {{
            background-color: {colors["surface"]};
            color: {colors["text_secondary"]};
            border-color: {colors["border"]};
        }}
        
        QLineEdit::placeholder {{
            color: {colors["text_secondary"]};
            font-style: italic;
        }}
        
        /* Spin Boxes */
        QSpinBox, QDoubleSpinBox {{
            background-color: {colors["background"]};
            border: 2px solid {colors["border"]};
            border-radius: 6px;
            padding: 8px 12px;
            color: {colors["text"]};
            font-size: 13px;
        }}
        
        QSpinBox:focus, QDoubleSpinBox:focus {{
            border-color: {colors["primary"]};
            outline: none;
        }}
        
        QSpinBox:hover, QDoubleSpinBox:hover {{
            border-color: {self._lighten_color(colors["border"])};
        }}
        
        QSpinBox::up-button, QSpinBox::down-button,
        QDoubleSpinBox::up-button, QDoubleSpinBox::down-button {{
            background-color: {colors["surface"]};
            border: 1px solid {colors["border"]};
            border-radius: 3px;
            width: 16px;
            margin: 1px;
        }}
        
        QSpinBox::up-button:hover, QSpinBox::down-button:hover,
        QDoubleSpinBox::up-button:hover, QDoubleSpinBox::down-button:hover {{
            background-color: {colors["primary"]};
        }}
        
        /* Combo Boxes */
        QComboBox {{
            background-color: {colors["background"]};
            border: 2px solid {colors["border"]};
            border-radius: 6px;
            padding: 8px 12px;
            color: {colors["text"]};
            font-size: 13px;
        }}
        
        QComboBox:focus {{
            border-color: {colors["primary"]};
            outline: none;
        }}
        
        QComboBox:hover {{
            border-color: {self._lighten_color(colors["border"])};
        }}
        
        QComboBox:disabled {{
            background-color: {colors["surface"]};
            color: {colors["text_secondary"]};
            border-color: {colors["border"]};
        }}
        
        QComboBox::drop-down {{
            background-color: {colors["surface"]};
            border: none;
            border-left: 1px solid {colors["border"]};
            border-radius: 0px 4px 4px 0px;
            width: 20px;
        }}
        
        QComboBox::drop-down:hover {{
            background-color: {colors["primary"]};
        }}
        
        QComboBox::down-arrow {{
            color: {colors["text"]};
            width: 12px;
            height: 12px;
        }}
        
        QComboBox QAbstractItemView {{
            background-color: {colors["background"]};
            border: 2px solid {colors["border"]};
            border-radius: 6px;
            selection-background-color: {colors["primary"]};
            selection-color: white;
            color: {colors["text"]};
            padding: 4px;
            font-size: 13px;
        }}
        
        QComboBox QAbstractItemView::item {{
            padding: 8px 12px;
            border-radius: 4px;
            margin: 1px;
        }}
        
        QComboBox QAbstractItemView::item:hover {{
            background-color: {self._lighten_color(colors["primary"])};
        }}
        
        QComboBox QAbstractItemView::item:selected {{
            background-color: {colors["primary"]};
            color: white;
        }}
        
        /* Tab Widget */
        QTabWidget::pane {{
            border: 1px solid {colors["border"]};
            border-radius: 8px;
            background-color: {colors["surface"]};
        }}
        
        QTabBar::tab {{
            background-color: {colors["background"]};
            border: 1px solid {colors["border"]};
            padding: 8px 16px;
            margin-right: 2px;
            border-top-left-radius: 8px;
            border-top-right-radius: 8px;
            color: {colors["text"]};
        }}
        
        QTabBar::tab:selected {{
            background-color: {colors["surface"]};
            border-bottom-color: {colors["surface"]};
        }}
        
        QTabBar::tab:hover {{
            background-color: {colors["border"]};
        }}
        
        /* Menu Bar */
        QMenuBar {{
            background-color: {colors["background"]};
            color: {colors["text"]};
            border-bottom: 1px solid {colors["border"]};
        }}
        
        QMenuBar::item {{
            background-color: transparent;
            padding: 4px 8px;
        }}
        
        QMenuBar::item:selected {{
            background-color: {colors["primary"]};
            color: #ffffff;
        }}
        
        QMenu {{
            background-color: {colors["surface"]};
            border: 1px solid {colors["border"]};
            color: {colors["text"]};
        }}
        
        QMenu::item {{
            padding: 8px 16px;
        }}
        
        QMenu::item:selected {{
            background-color: {colors["primary"]};
            color: #ffffff;
        }}
        
        /* Status Bar */
        QStatusBar {{
            background-color: {colors["surface"]};
            border-top: 1px solid {colors["border"]};
            color: {colors["text_secondary"]};
        }}
        
        /* Progress Bar */
        QProgressBar {{
            border: 1px solid {colors["border"]};
            border-radius: 6px;
            background-color: {colors["surface"]};
            text-align: center;
            color: {colors["text"]};
        }}
        
        QProgressBar::chunk {{
            background-color: {colors["primary"]};
            border-radius: 5px;
        }}
        
        /* Scroll Bars */
        QScrollBar:vertical {{
            background-color: {colors["surface"]};
            width: 12px;
            border-radius: 6px;
        }}
        
        QScrollBar::handle:vertical {{
            background-color: {colors["border"]};
            border-radius: 6px;
            min-height: 20px;
        }}
        
        QScrollBar::handle:vertical:hover {{
            background-color: {colors["text_secondary"]};
        }}
        
        QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {{
            height: 0px;
        }}
        
        /* Group Boxes */
        QGroupBox {{
            font-weight: bold;
            border: 2px solid {colors["border"]};
            border-radius: 8px;
            margin-top: 10px;
            padding-top: 10px;
            color: {colors["text"]};
        }}
        
        QGroupBox::title {{
            subcontrol-origin: margin;
            left: 10px;
            padding: 0 5px 0 5px;
            color: {colors["text"]};
        }}
        
        /* Sliders */
        QSlider::groove:horizontal {{
            border: 1px solid {colors["border"]};
            height: 6px;
            background: {colors["surface"]};
            border-radius: 3px;
        }}
        
        QSlider::handle:horizontal {{
            background: {colors["primary"]};
            border: 1px solid {colors["border"]};
            width: 18px;
            margin: -6px 0;
            border-radius: 9px;
        }}
        
        QSlider::handle:horizontal:hover {{
            background: {self._lighten_color(colors["primary"])};
        }}
        """
    
    def _darken_color(self, color: str, factor: float = 0.8) -> str:
        """Darken a color by a factor."""
        qcolor = QColor(color)
        h, s, l, a = qcolor.getHslF()
        qcolor.setHslF(h, s, l * factor, a)
        return qcolor.name()
    
    def _lighten_color(self, color: str, factor: float = 1.2) -> str:
        """Lighten a color by a factor."""
        qcolor = QColor(color)
        h, s, l, a = qcolor.getHslF()
        qcolor.setHslF(h, s, min(1.0, l * factor), a)
        return qcolor.name()
    
    def get_color(self, color_name: str) -> str:
        """
        Get a color from the dark theme (only available theme).
        
        Args:
            color_name: Name of the color
            
        Returns:
            Color hex string
        """
        colors = self.DARK_THEME
        return colors.get(color_name, "#000000")
    
    def apply_to_widget(self, widget, custom_style: str = ""):
        """
        Apply dark theme to a specific widget.
        
        Args:
            widget: Widget to apply theme to
            custom_style: Additional custom styles
        """
        colors = self.DARK_THEME
        base_style = self._create_stylesheet(colors)
        
        if custom_style:
            widget.setStyleSheet(base_style + "\n" + custom_style)
        else:
            widget.setStyleSheet(base_style)
    
    def apply_theme_to_widget(self, widget):
        """
        Apply current theme to a widget and its children with proper dark mode text box styling.
        
        Args:
            widget: Widget to apply theme to
        """
        if not widget:
            return
        
        colors = self.DARK_THEME
        
        # Enhanced styling for dark mode with black text boxes and white text
        enhanced_style = f"""
            /* Dialog and main containers */
            QDialog {{
                background-color: {colors['surface']};
                color: {colors['text']};
            }}
            
            QWidget {{
                background-color: {colors['surface']};
                color: {colors['text']};
            }}
            
            /* Text input fields - black background in dark mode, white text */
            QLineEdit {{
                background-color: {colors['background']};
                color: {colors['text']};
                border: 1px solid {colors['border']};
                border-radius: 4px;
                padding: 6px;
                selection-background-color: {colors['primary']};
                selection-color: white;
            }}
            
            QLineEdit:focus {{
                border-color: {colors['primary']};
                background-color: {colors['background']};
            }}
            
            QTextEdit {{
                background-color: {colors['background']};
                color: {colors['text']};
                border: 1px solid {colors['border']};
                border-radius: 4px;
                padding: 6px;
                selection-background-color: {colors['primary']};
                selection-color: white;
            }}
            
            QTextBrowser {{
                background-color: {colors['background']};
                color: {colors['text']};
                border: 1px solid {colors['border']};
                border-radius: 4px;
                padding: 6px;
            }}
            
            QSpinBox {{
                background-color: {colors['background']};
                color: {colors['text']};
                border: 1px solid {colors['border']};
                border-radius: 4px;
                padding: 6px;
            }}
            
            QComboBox {{
                background-color: {colors['background']};
                color: {colors['text']};
                border: 1px solid {colors['border']};
                border-radius: 4px;
                padding: 6px;
            }}
            
            QComboBox::drop-down {{
                background-color: {colors['surface']};
                border: none;
            }}
            
            QComboBox QAbstractItemView {{
                background-color: {colors['background']};
                color: {colors['text']};
                border: 1px solid {colors['border']};
                selection-background-color: {colors['primary']};
                selection-color: white;
            }}
            
            /* Group boxes */
            QGroupBox {{
                color: {colors['text']};
                border: 2px solid {colors['border']};
                border-radius: 8px;
                margin-top: 10px;
                padding-top: 10px;
                font-weight: bold;
            }}
            
            QGroupBox::title {{
                color: {colors['text']};
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 5px 0 5px;
            }}
            
            /* Labels */
            QLabel {{
                color: {colors['text']};
                background-color: transparent;
            }}
            
            /* Buttons */
            QPushButton {{
                background-color: {colors['surface']};
                color: {colors['text']};
                border: 1px solid {colors['border']};
                border-radius: 6px;
                padding: 8px 16px;
            }}
            
            QPushButton:hover {{
                background-color: {colors['primary']};
                color: white;
            }}
            
            QPushButton:pressed {{
                background-color: {self._darken_color(colors['primary'])};
            }}
            
            QPushButton:disabled {{
                background-color: {colors['border']};
                color: {colors['text_secondary']};
            }}
            
            /* Radio buttons and checkboxes */
            QRadioButton {{
                color: {colors['text']};
                background-color: transparent;
            }}
            
            QCheckBox {{
                color: {colors['text']};
                background-color: transparent;
            }}
        """
        
        widget.setStyleSheet(enhanced_style)
    
    def detect_parent_theme(self, parent_widget: Optional[QWidget] = None) -> bool:
        """
        Always returns True since only dark theme is available for consistency.
        
        Args:
            parent_widget: Parent widget (ignored - always dark theme)
            
        Returns:
            True (always dark theme)
        """
        self.logger.debug("Parent theme detection: always returning dark mode for consistency")
        return True
    
    def get_dialog_theme_styles(self, is_dark_mode: Optional[bool] = None) -> Dict[str, str]:
        """
        Return CSS styles for dialog elements - Always dark theme for consistency.
        
        Args:
            is_dark_mode: Ignored - always returns dark theme styles
            
        Returns:
            Dictionary containing CSS styles for different dialog elements
        """
        # Always use dark theme for consistency
        colors = self.DARK_THEME.copy()
        is_dark_mode = True
        
        return {
            'dialog': f"""
                QDialog {{
                    background-color: {colors['surface']};
                    color: {colors['text']};
                }}
            """,
            
            'input_fields': f"""
                /* QLineEdit - Text input fields */
                QLineEdit {{
                    background-color: {colors['background']};
                    color: {colors['text']};
                    border: 2px solid {colors['border']};
                    border-radius: 6px;
                    padding: 8px 12px;
                    font-size: 13px;
                    selection-background-color: {colors['primary']};
                    selection-color: {'white' if is_dark_mode else 'black'};
                    min-height: 16px;
                }}
                
                QLineEdit:focus {{
                    border-color: {colors['primary']};
                    background-color: {colors['background']};
                    outline: none;
                }}
                
                QLineEdit:hover {{
                    border-color: {self._lighten_color(colors['border'])};
                }}
                
                QLineEdit:disabled {{
                    background-color: {colors['surface']};
                    color: {colors['text_secondary']};
                    border-color: {colors['border']};
                }}
                
                QLineEdit::placeholder {{
                    color: {colors['text_secondary']};
                    font-style: italic;
                }}
                
                /* QTextEdit - Multi-line text input */
                QTextEdit {{
                    background-color: {colors['background']};
                    color: {colors['text']};
                    border: 2px solid {colors['border']};
                    border-radius: 6px;
                    padding: 8px 12px;
                    font-size: 13px;
                    selection-background-color: {colors['primary']};
                    selection-color: {'white' if is_dark_mode else 'black'};
                    line-height: 1.4;
                }}
                
                QTextEdit:focus {{
                    border-color: {colors['primary']};
                    background-color: {colors['background']};
                    outline: none;
                }}
                
                QTextEdit:hover {{
                    border-color: {self._lighten_color(colors['border'])};
                }}
                
                QTextEdit:disabled {{
                    background-color: {colors['surface']};
                    color: {colors['text_secondary']};
                    border-color: {colors['border']};
                }}
                
                /* QPlainTextEdit - Plain text editor */
                QPlainTextEdit {{
                    background-color: {colors['background']};
                    color: {colors['text']};
                    border: 2px solid {colors['border']};
                    border-radius: 6px;
                    padding: 8px 12px;
                    font-size: 13px;
                    selection-background-color: {colors['primary']};
                    selection-color: {'white' if is_dark_mode else 'black'};
                    line-height: 1.4;
                }}
                
                QPlainTextEdit:focus {{
                    border-color: {colors['primary']};
                    background-color: {colors['background']};
                    outline: none;
                }}
                
                QPlainTextEdit:hover {{
                    border-color: {self._lighten_color(colors['border'])};
                }}
                
                QPlainTextEdit:disabled {{
                    background-color: {colors['surface']};
                    color: {colors['text_secondary']};
                    border-color: {colors['border']};
                }}
                
                /* QSpinBox - Numeric input */
                QSpinBox {{
                    background-color: {colors['background']};
                    color: {colors['text']};
                    border: 2px solid {colors['border']};
                    border-radius: 6px;
                    padding: 8px 12px;
                    font-size: 13px;
                    min-height: 16px;
                }}
                
                QSpinBox:focus {{
                    border-color: {colors['primary']};
                    background-color: {colors['background']};
                    outline: none;
                }}
                
                QSpinBox:hover {{
                    border-color: {self._lighten_color(colors['border']) if is_dark_mode else self._darken_color(colors['border'])};
                }}
                
                QSpinBox:disabled {{
                    background-color: {colors['surface']};
                    color: {colors['text_secondary']};
                    border-color: {colors['border']};
                }}
                
                QSpinBox::up-button {{
                    background-color: {colors['surface']};
                    border: 1px solid {colors['border']};
                    border-radius: 3px;
                    width: 16px;
                    margin: 1px;
                }}
                
                QSpinBox::up-button:hover {{
                    background-color: {colors['primary']};
                }}
                
                QSpinBox::up-button:pressed {{
                    background-color: {self._darken_color(colors['primary'])};
                }}
                
                QSpinBox::down-button {{
                    background-color: {colors['surface']};
                    border: 1px solid {colors['border']};
                    border-radius: 3px;
                    width: 16px;
                    margin: 1px;
                }}
                
                QSpinBox::down-button:hover {{
                    background-color: {colors['primary']};
                }}
                
                QSpinBox::down-button:pressed {{
                    background-color: {self._darken_color(colors['primary'])};
                }}
                
                QSpinBox::up-arrow {{
                    color: {colors['text']};
                    width: 8px;
                    height: 8px;
                }}
                
                QSpinBox::down-arrow {{
                    color: {colors['text']};
                    width: 8px;
                    height: 8px;
                }}
                
                /* QDoubleSpinBox - Decimal numeric input */
                QDoubleSpinBox {{
                    background-color: {colors['background']};
                    color: {colors['text']};
                    border: 2px solid {colors['border']};
                    border-radius: 6px;
                    padding: 8px 12px;
                    font-size: 13px;
                    min-height: 16px;
                }}
                
                QDoubleSpinBox:focus {{
                    border-color: {colors['primary']};
                    background-color: {colors['background']};
                    outline: none;
                }}
                
                QDoubleSpinBox:hover {{
                    border-color: {self._lighten_color(colors['border']) if is_dark_mode else self._darken_color(colors['border'])};
                }}
                
                QDoubleSpinBox:disabled {{
                    background-color: {colors['surface']};
                    color: {colors['text_secondary']};
                    border-color: {colors['border']};
                }}
                
                /* QComboBox - Dropdown selection */
                QComboBox {{
                    background-color: {colors['background']};
                    color: {colors['text']};
                    border: 2px solid {colors['border']};
                    border-radius: 6px;
                    padding: 8px 12px;
                    font-size: 13px;
                    min-height: 16px;
                }}
                
                QComboBox:focus {{
                    border-color: {colors['primary']};
                    background-color: {colors['background']};
                    outline: none;
                }}
                
                QComboBox:hover {{
                    border-color: {self._lighten_color(colors['border']) if is_dark_mode else self._darken_color(colors['border'])};
                }}
                
                QComboBox:disabled {{
                    background-color: {colors['surface']};
                    color: {colors['text_secondary']};
                    border-color: {colors['border']};
                }}
                
                QComboBox::drop-down {{
                    background-color: {colors['surface']};
                    border: none;
                    border-left: 1px solid {colors['border']};
                    border-radius: 0px 4px 4px 0px;
                    width: 20px;
                }}
                
                QComboBox::drop-down:hover {{
                    background-color: {colors['primary']};
                }}
                
                QComboBox::down-arrow {{
                    color: {colors['text']};
                    width: 12px;
                    height: 12px;
                }}
                
                QComboBox QAbstractItemView {{
                    background-color: {colors['background']};
                    color: {colors['text']};
                    border: 2px solid {colors['border']};
                    border-radius: 6px;
                    selection-background-color: {colors['primary']};
                    selection-color: {'white' if is_dark_mode else 'black'};
                    padding: 4px;
                    font-size: 13px;
                }}
                
                QComboBox QAbstractItemView::item {{
                    padding: 8px 12px;
                    border-radius: 4px;
                    margin: 1px;
                }}
                
                QComboBox QAbstractItemView::item:hover {{
                    background-color: {self._lighten_color(colors['primary']) if is_dark_mode else colors['surface']};
                }}
                
                QComboBox QAbstractItemView::item:selected {{
                    background-color: {colors['primary']};
                    color: white;
                }}
            """,
            
            'buttons': f"""
                /* Default/Secondary Button Styles */
                QPushButton {{
                    background-color: {colors['surface']};
                    color: {colors['text']};
                    border: 2px solid {colors['border']};
                    border-radius: 6px;
                    padding: 8px 16px;
                    font-size: 13px;
                    font-weight: 500;
                    min-height: 16px;
                    min-width: 80px;
                }}
                
                QPushButton:hover {{
                    background-color: {self._lighten_color(colors['surface']) if is_dark_mode else self._darken_color(colors['surface'])};
                    border-color: {self._lighten_color(colors['border']) if is_dark_mode else self._darken_color(colors['border'])};
                }}
                
                QPushButton:pressed {{
                    background-color: {self._darken_color(colors['surface'])};
                    border-color: {colors['primary']};
                }}
                
                QPushButton:disabled {{
                    background-color: {colors['border']};
                    color: {colors['text_secondary']};
                    border-color: {colors['border']};
                }}
                
                QPushButton:focus {{
                    border-color: {colors['primary']};
                    outline: none;
                }}
                
                /* Primary Button Styles */
                QPushButton[buttonType="primary"] {{
                    background-color: {colors['success']};
                    color: white;
                    border: 2px solid {colors['success']};
                    font-weight: 600;
                }}
                
                QPushButton[buttonType="primary"]:hover {{
                    background-color: {self._darken_color(colors['success'])};
                    border-color: {self._darken_color(colors['success'])};
                }}
                
                QPushButton[buttonType="primary"]:pressed {{
                    background-color: {self._darken_color(colors['success'], 0.7)};
                }}
                
                QPushButton[buttonType="primary"]:disabled {{
                    background-color: {colors['border']};
                    color: {colors['text_secondary']};
                    border-color: {colors['border']};
                }}
                
                /* Secondary Button Styles */
                QPushButton[buttonType="secondary"] {{
                    background-color: {colors['surface']};
                    color: {colors['text']};
                    border: 2px solid {colors['border']};
                    font-weight: 500;
                }}
                
                QPushButton[buttonType="secondary"]:hover {{
                    background-color: {self._lighten_color(colors['surface']) if is_dark_mode else self._darken_color(colors['surface'])};
                    border-color: {colors['primary']};
                    color: {colors['primary']};
                }}
                
                QPushButton[buttonType="secondary"]:pressed {{
                    background-color: {self._darken_color(colors['surface'])};
                    border-color: {colors['primary']};
                    color: {colors['primary']};
                }}
                
                QPushButton[buttonType="secondary"]:disabled {{
                    background-color: {colors['border']};
                    color: {colors['text_secondary']};
                    border-color: {colors['border']};
                }}
                
                /* Cancel/Danger Button Styles */
                QPushButton[buttonType="cancel"], QPushButton[buttonType="danger"] {{
                    background-color: {colors['error']};
                    color: white;
                    border: 2px solid {colors['error']};
                }}
                
                QPushButton[buttonType="cancel"]:hover, QPushButton[buttonType="danger"]:hover {{
                    background-color: {self._darken_color(colors['error'])};
                    border-color: {self._darken_color(colors['error'])};
                }}
                
                QPushButton[buttonType="cancel"]:pressed, QPushButton[buttonType="danger"]:pressed {{
                    background-color: {self._darken_color(colors['error'], 0.7)};
                }}
                
                /* Info/Help Button Styles */
                QPushButton[buttonType="info"] {{
                    background-color: {colors['info']};
                    color: white;
                    border: 2px solid {colors['info']};
                }}
                
                QPushButton[buttonType="info"]:hover {{
                    background-color: {self._darken_color(colors['info'])};
                    border-color: {self._darken_color(colors['info'])};
                }}
                
                QPushButton[buttonType="info"]:pressed {{
                    background-color: {self._darken_color(colors['info'], 0.7)};
                }}
                
                /* Warning Button Styles */
                QPushButton[buttonType="warning"] {{
                    background-color: {colors['warning']};
                    color: {'black' if is_dark_mode else 'white'};
                    border: 2px solid {colors['warning']};
                }}
                
                QPushButton[buttonType="warning"]:hover {{
                    background-color: {self._darken_color(colors['warning'])};
                    border-color: {self._darken_color(colors['warning'])};
                    color: white;
                }}
                
                QPushButton[buttonType="warning"]:pressed {{
                    background-color: {self._darken_color(colors['warning'], 0.7)};
                    color: white;
                }}
                
                /* Outline Button Styles */
                QPushButton[buttonType="outline"] {{
                    background-color: transparent;
                    color: {colors['primary']};
                    border: 2px solid {colors['primary']};
                }}
                
                QPushButton[buttonType="outline"]:hover {{
                    background-color: {colors['primary']};
                    color: white;
                }}
                
                QPushButton[buttonType="outline"]:pressed {{
                    background-color: {self._darken_color(colors['primary'])};
                    color: white;
                }}
                
                /* Flat/Text Button Styles */
                QPushButton[buttonType="flat"] {{
                    background-color: transparent;
                    color: {colors['primary']};
                    border: 2px solid transparent;
                }}
                
                QPushButton[buttonType="flat"]:hover {{
                    background-color: {self._lighten_color(colors['primary'], 1.8) if is_dark_mode else self._lighten_color(colors['primary'], 1.9)};
                    color: {colors['primary']};
                }}
                
                QPushButton[buttonType="flat"]:pressed {{
                    background-color: {self._lighten_color(colors['primary'], 1.6) if is_dark_mode else self._lighten_color(colors['primary'], 1.7)};
                }}
                
                /* Special OAuth/Google Button Styles */
                QPushButton[buttonType="oauth"] {{
                    background-color: #4285f4;
                    color: white;
                    border: 2px solid #4285f4;
                }}
                
                QPushButton[buttonType="oauth"]:hover {{
                    background-color: #3367d6;
                    border-color: #3367d6;
                }}
                
                QPushButton[buttonType="oauth"]:pressed {{
                    background-color: #2d5aa0;
                }}
                
                /* AI/Generate Button Styles */
                QPushButton[buttonType="ai"] {{
                    background-color: #6f42c1;
                    color: white;
                    border: 2px solid #6f42c1;
                }}
                
                QPushButton[buttonType="ai"]:hover {{
                    background-color: #5a2d91;
                    border-color: #5a2d91;
                }}
                
                QPushButton[buttonType="ai"]:pressed {{
                    background-color: #4c1d82;
                }}
                
                /* Small Button Variant */
                QPushButton[buttonSize="small"] {{
                    padding: 4px 8px;
                    font-size: 11px;
                    min-height: 12px;
                    min-width: 60px;
                }}
                
                /* Large Button Variant */
                QPushButton[buttonSize="large"] {{
                    padding: 12px 24px;
                    font-size: 15px;
                    min-height: 20px;
                    min-width: 120px;
                    font-weight: 600;
                }}
                
                /* Icon Button Styles */
                QPushButton[hasIcon="true"] {{
                    text-align: left;
                    padding-left: 12px;
                }}
            """,
            
            'group_boxes': f"""
                /* QGroupBox - Container grouping with title */
                QGroupBox {{
                    color: {colors['text']};
                    border: 2px solid {colors['border']};
                    border-radius: 8px;
                    margin-top: 12px;
                    padding-top: 12px;
                    padding-left: 8px;
                    padding-right: 8px;
                    padding-bottom: 8px;
                    font-weight: bold;
                    font-size: 13px;
                    background-color: {colors['surface']};
                }}
                
                QGroupBox:hover {{
                    border-color: {self._lighten_color(colors['border']) if is_dark_mode else self._darken_color(colors['border'])};
                }}
                
                QGroupBox:focus {{
                    border-color: {colors['primary']};
                    outline: none;
                }}
                
                QGroupBox:disabled {{
                    color: {colors['text_secondary']};
                    border-color: {colors['border']};
                    background-color: {self._darken_color(colors['surface']) if is_dark_mode else self._lighten_color(colors['surface'])};
                }}
                
                QGroupBox::title {{
                    color: {colors['text']};
                    subcontrol-origin: margin;
                    subcontrol-position: top left;
                    left: 10px;
                    top: -8px;
                    padding: 2px 8px 2px 8px;
                    background-color: {colors['surface']};
                    border: 1px solid {colors['border']};
                    border-radius: 4px;
                    font-weight: bold;
                    font-size: 12px;
                }}
                
                QGroupBox::title:hover {{
                    color: {colors['primary']};
                    border-color: {colors['primary']};
                }}
                
                QGroupBox::title:disabled {{
                    color: {colors['text_secondary']};
                    border-color: {colors['border']};
                    background-color: {self._darken_color(colors['surface']) if is_dark_mode else self._lighten_color(colors['surface'])};
                }}
                
                /* Nested QGroupBox styling */
                QGroupBox QGroupBox {{
                    margin-top: 8px;
                    padding-top: 8px;
                    border: 1px solid {colors['border']};
                    border-radius: 6px;
                    background-color: {colors['background']};
                    font-size: 12px;
                }}
                
                QGroupBox QGroupBox::title {{
                    font-size: 11px;
                    top: -6px;
                    padding: 1px 6px 1px 6px;
                    background-color: {colors['background']};
                    border: 1px solid {self._lighten_color(colors['border']) if is_dark_mode else self._darken_color(colors['border'])};
                }}
                
                /* Third level nesting */
                QGroupBox QGroupBox QGroupBox {{
                    border: 1px dashed {colors['border']};
                    border-radius: 4px;
                    background-color: transparent;
                    font-size: 11px;
                    margin-top: 6px;
                    padding-top: 6px;
                }}
                
                QGroupBox QGroupBox QGroupBox::title {{
                    font-size: 10px;
                    top: -4px;
                    padding: 1px 4px 1px 4px;
                    background-color: {colors['surface']};
                    border: 1px dashed {colors['border']};
                }}
                
                /* Container elements within group boxes */
                QGroupBox QWidget {{
                    background-color: transparent;
                }}
                
                QGroupBox QFrame {{
                    background-color: transparent;
                    border: none;
                }}
                
                QGroupBox QScrollArea {{
                    background-color: {colors['background']};
                    border: 1px solid {colors['border']};
                    border-radius: 4px;
                }}
                
                QGroupBox QScrollArea QWidget {{
                    background-color: {colors['background']};
                }}
                
                /* Special styling for group boxes with specific properties */
                QGroupBox[flat="true"] {{
                    border: none;
                    background-color: transparent;
                    font-weight: normal;
                }}
                
                QGroupBox[flat="true"]::title {{
                    border: none;
                    background-color: transparent;
                    font-weight: bold;
                    color: {colors['primary']};
                }}
                
                QGroupBox[checkable="true"] {{
                    padding-top: 16px;
                }}
                
                QGroupBox[checkable="true"]::title {{
                    padding-left: 20px;
                }}
                
                QGroupBox::indicator {{
                    width: 16px;
                    height: 16px;
                    left: 2px;
                    top: -10px;
                }}
                
                QGroupBox::indicator:unchecked {{
                    border: 2px solid {colors['border']};
                    border-radius: 3px;
                    background-color: {colors['background']};
                }}
                
                QGroupBox::indicator:checked {{
                    border: 2px solid {colors['primary']};
                    border-radius: 3px;
                    background-color: {colors['primary']};
                }}
                
                QGroupBox::indicator:hover {{
                    border-color: {colors['primary']};
                }}
                
                QGroupBox::indicator:disabled {{
                    border-color: {colors['text_secondary']};
                    background-color: {colors['surface']};
                }}
            """,
            
            'labels': f"""
                QLabel {{
                    color: {colors['text']};
                    background-color: transparent;
                }}
            """,
            
            'checkboxes_radio': f"""
                QRadioButton {{
                    color: {colors['text']};
                    background-color: transparent;
                }}
                
                QCheckBox {{
                    color: {colors['text']};
                    background-color: transparent;
                }}
                
                QRadioButton::indicator {{
                    width: 16px;
                    height: 16px;
                }}
                
                QCheckBox::indicator {{
                    width: 16px;
                    height: 16px;
                }}
                
                QRadioButton::indicator:unchecked {{
                    border: 2px solid {colors['border']};
                    border-radius: 8px;
                    background-color: {colors['background']};
                }}
                
                QRadioButton::indicator:checked {{
                    border: 2px solid {colors['primary']};
                    border-radius: 8px;
                    background-color: {colors['primary']};
                }}
                
                QCheckBox::indicator:unchecked {{
                    border: 2px solid {colors['border']};
                    border-radius: 3px;
                    background-color: {colors['background']};
                }}
                
                QCheckBox::indicator:checked {{
                    border: 2px solid {colors['primary']};
                    border-radius: 3px;
                    background-color: {colors['primary']};
                }}
            """
        }
    
    def apply_dialog_theme(self, dialog: QDialog, parent_widget: Optional[QWidget] = None):
        """
        Apply appropriate theme to dialog based on parent widget or current theme.
        
        Args:
            dialog: Dialog to apply theme to
            parent_widget: Parent widget to detect theme from, if None uses current theme
        """
        if not dialog:
            self.logger.warning("Cannot apply theme to None dialog")
            return
        
        try:
            # Detect theme mode
            is_dark_mode = self.detect_parent_theme(parent_widget)
            
            # Get dialog styles
            styles = self.get_dialog_theme_styles(is_dark_mode)
            
            # Combine all styles
            combined_style = ""
            for style_category, style_css in styles.items():
                combined_style += style_css + "\n"
            
            # Apply the combined stylesheet
            dialog.setStyleSheet(combined_style)
            
            self.logger.debug(f"Applied {'dark' if is_dark_mode else 'light'} theme to dialog: {dialog.__class__.__name__}")
            
        except Exception as e:
            self.logger.error(f"Failed to apply dialog theme: {e}")
            # Fallback to current theme
            self.apply_theme_to_widget(dialog)
    
    def get_theme_colors(self, is_dark_mode: Optional[bool] = None) -> Dict[str, str]:
        """
        Get theme colors dictionary.
        
        Args:
            is_dark_mode: If None, uses current theme; otherwise uses specified mode
            
        Returns:
            Dictionary of theme colors
        """
        if is_dark_mode is None:
            is_dark_mode = self.is_dark_mode()
        
        return self.DARK_THEME.copy() if is_dark_mode else self.LIGHT_THEME.copy()