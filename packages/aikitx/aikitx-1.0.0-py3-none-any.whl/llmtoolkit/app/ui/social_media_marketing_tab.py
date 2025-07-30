"""
Social Media Marketing Tab

This module contains the SocialMediaMarketingTab class, which provides a placeholder
interface for social media marketing functionality (coming soon) with sub-tabs for
different social media platforms.
"""

import logging
from typing import Optional, Dict, Any

from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, 
    QFrame, QTextBrowser, QTabWidget
)
from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QFont, QPixmap, QIcon

from llmtoolkit.app.core.event_bus import EventBus
from llmtoolkit.app.ui.theme_manager import ThemeManager


class SocialMediaPlatformTab(QWidget):
    """Base class for social media platform tabs."""
    
    def __init__(self, platform_name: str, platform_icon: str, theme_manager: ThemeManager = None, parent=None):
        """
        Initialize the social media platform tab.
        
        Args:
            platform_name: Name of the social media platform
            platform_icon: Icon/emoji for the platform
            theme_manager: Theme manager for consistent styling
            parent: Parent widget
        """
        super().__init__(parent)
        
        self.platform_name = platform_name
        self.platform_icon = platform_icon
        self.theme_manager = theme_manager
        
        # Initialize UI
        self._init_ui()
        
        # Apply initial theme
        if self.theme_manager:
            self._apply_theme()
    
    def _init_ui(self):
        """Initialize UI components with coming soon message."""
        # Create main layout
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(20, 20, 20, 20)
        main_layout.setSpacing(15)
        
        # Create centered content
        content_frame = QFrame()
        content_frame.setObjectName(f"{self.platform_name.lower()}_frame")
        content_layout = QVBoxLayout(content_frame)
        content_layout.setContentsMargins(30, 30, 30, 30)
        content_layout.setSpacing(20)
        content_layout.setAlignment(Qt.AlignCenter)
        
        # Add icon
        icon_label = QLabel()
        icon_label.setAlignment(Qt.AlignCenter)
        icon_label.setText(self.platform_icon)
        icon_font = QFont()
        icon_font.setPointSize(48)
        icon_label.setFont(icon_font)
        content_layout.addWidget(icon_label)
        
        # Add title
        title_label = QLabel(f"{self.platform_name} Marketing")
        title_label.setAlignment(Qt.AlignCenter)
        title_font = QFont()
        title_font.setPointSize(24)
        title_font.setBold(True)
        title_label.setFont(title_font)
        content_layout.addWidget(title_label)
        
        # Add coming soon label
        coming_soon_label = QLabel("Coming Soon!")
        coming_soon_label.setAlignment(Qt.AlignCenter)
        coming_soon_font = QFont()
        coming_soon_font.setPointSize(18)
        coming_soon_font.setBold(True)
        coming_soon_label.setFont(coming_soon_font)
        coming_soon_label.setObjectName("coming_soon_label")
        content_layout.addWidget(coming_soon_label)
        
        # Add description
        description_browser = QTextBrowser()
        description_browser.setReadOnly(True)
        description_browser.setOpenExternalLinks(True)
        description_browser.setFrameStyle(QFrame.NoFrame)
        # Ensure proper styling in dark mode
        if self.theme_manager and self.theme_manager.is_dark_mode():
            description_browser.setStyleSheet("""
                QTextBrowser { 
                    background-color: #1e1e1e; 
                    color: #ffffff; 
                    border: none; 
                }
            """)
        description_browser.setHtml(f"""
        <div style="text-align: center; font-size: 14px; line-height: 1.6;">
            <p>Our {self.platform_name} marketing feature is currently under development.</p>
            <p>Soon you'll be able to:</p>
            <ul style="text-align: left; display: inline-block;">
                <li>Create and schedule {self.platform_name} posts with AI assistance</li>
                <li>Analyze engagement metrics and audience insights</li>
                <li>Manage {self.platform_name} campaigns and content calendars</li>
                <li>Respond to comments and messages</li>
                <li>Track performance and ROI</li>
            </ul>
            <p>We're working hard to bring you these features soon!</p>
        </div>
        """)
        content_layout.addWidget(description_browser)
        
        # Add notify me button
        notify_button = QPushButton("Notify Me When Available")
        notify_button.setMinimumHeight(40)
        notify_button.setMinimumWidth(200)
        notify_button.clicked.connect(self._on_notify_clicked)
        content_layout.addWidget(notify_button, 0, Qt.AlignCenter)
        
        # Add to main layout
        main_layout.addWidget(content_frame, 1)
    
    def _on_notify_clicked(self):
        """Handle notify button click."""
        from PySide6.QtWidgets import QMessageBox
        
        QMessageBox.information(
            self,
            "Feature Notification",
            f"Thank you for your interest!\n\n"
            f"We'll notify you when the {self.platform_name} Marketing feature becomes available."
        )
    
    def _apply_theme(self):
        """Apply theme-based styling to all components."""
        if not self.theme_manager:
            return
        
        # Get theme colors
        is_dark = self.theme_manager.is_dark_mode()
        bg_color = self.theme_manager.get_color("background")
        text_color = self.theme_manager.get_color("text")
        accent_color = self.theme_manager.get_color("primary")
        border_color = self.theme_manager.get_color("border")
        
        # Apply theme to frame
        frame_style = f"""
            QFrame#{self.platform_name.lower()}_frame {{
                background-color: {bg_color};
                border: 1px solid {border_color};
                border-radius: 10px;
            }}
        """
        
        # Apply theme to coming soon label
        coming_soon_style = f"""
            QLabel#coming_soon_label {{
                color: {accent_color};
            }}
        """
        
        # Apply styles
        for widget in self.findChildren(QFrame, f"{self.platform_name.lower()}_frame"):
            widget.setStyleSheet(frame_style)
        
        for widget in self.findChildren(QLabel, "coming_soon_label"):
            widget.setStyleSheet(coming_soon_style)


class SocialMediaMarketingTab(QWidget):
    """
    Placeholder interface for social media marketing functionality (coming soon).
    """
    
    def __init__(self, event_bus: EventBus, theme_manager: ThemeManager = None, parent=None):
        """
        Initialize the social media marketing tab.
        
        Args:
            event_bus: Application event bus
            theme_manager: Theme manager for consistent styling
            parent: Parent widget
        """
        super().__init__(parent)
        
        self.logger = logging.getLogger("gguf_loader.ui.social_media_marketing_tab")
        self.event_bus = event_bus
        self.theme_manager = theme_manager
        
        # Initialize UI
        self._init_ui()
        
        # Subscribe to theme changes
        if self.theme_manager:
            self.theme_manager.theme_changed.connect(self._on_theme_changed)
        
        # Apply initial theme
        self._apply_theme()
        
        self.logger.info("SocialMediaMarketingTab initialized")
    
    def _init_ui(self):
        """Initialize UI components with sub-tabs for different platforms."""
        # Create main layout
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(10, 10, 10, 10)
        main_layout.setSpacing(10)
        
        # Create tab widget for social media platforms
        self.platform_tabs = QTabWidget()
        self.platform_tabs.setObjectName("platform_tabs")
        
        # Create Instagram tab
        instagram_tab = SocialMediaPlatformTab("Instagram", "📸", self.theme_manager)
        self.platform_tabs.addTab(instagram_tab, "Instagram")
        
        # Create Facebook tab
        facebook_tab = SocialMediaPlatformTab("Facebook", "👍", self.theme_manager)
        self.platform_tabs.addTab(facebook_tab, "Facebook")
        
        # Create WhatsApp tab
        whatsapp_tab = SocialMediaPlatformTab("WhatsApp", "💬", self.theme_manager)
        self.platform_tabs.addTab(whatsapp_tab, "WhatsApp")
        
        # Create Telegram tab
        telegram_tab = SocialMediaPlatformTab("Telegram", "✈️", self.theme_manager)
        self.platform_tabs.addTab(telegram_tab, "Telegram")
        
        # Add tab widget to main layout
        main_layout.addWidget(self.platform_tabs)
    
    def _on_theme_changed(self):
        """Handle theme change event."""
        self._apply_theme()
        
        # Update platform tabs
        for i in range(self.platform_tabs.count()):
            tab = self.platform_tabs.widget(i)
            if hasattr(tab, '_apply_theme'):
                tab._apply_theme()
    
    def _apply_theme(self):
        """Apply theme-based styling to all components."""
        if not self.theme_manager:
            return
        
        # Get theme colors
        is_dark = self.theme_manager.is_dark_mode()
        bg_color = self.theme_manager.get_color("background")
        text_color = self.theme_manager.get_color("text")
        accent_color = self.theme_manager.get_color("primary")
        border_color = self.theme_manager.get_color("border")
        
        # Apply theme to tab widget
        tab_style = f"""
            QTabWidget::pane {{
                border: 1px solid {border_color};
                border-radius: 5px;
                background-color: {bg_color};
            }}
            
            QTabBar::tab {{
                background-color: {bg_color};
                color: {text_color};
                padding: 8px 16px;
                margin-right: 2px;
                border: 1px solid {border_color};
                border-bottom: none;
                border-top-left-radius: 4px;
                border-top-right-radius: 4px;
            }}
            
            QTabBar::tab:selected {{
                background-color: {accent_color};
                color: white;
            }}
            
            QTabBar::tab:hover:!selected {{
                background-color: {self.theme_manager.get_color("hover")};
            }}
        """
        
        # Apply styles
        self.platform_tabs.setStyleSheet(tab_style)