"""
Splash Screen

This module contains the SplashScreen class, which displays a splash screen
during application startup.
"""

import time
import os
from PySide6.QtWidgets import QSplashScreen, QProgressBar, QVBoxLayout, QWidget
from PySide6.QtGui import QPixmap, QPainter, QColor, QFont
from PySide6.QtCore import Qt, QTimer

class SplashScreen(QSplashScreen):
    """
    Splash screen shown during application startup.
    
    This class displays a splash screen with a progress bar and status messages
    while the application is initializing.
    """
    
    def __init__(self):
        """Initialize the splash screen."""
        # Create a pixmap for the splash screen
        pixmap = QPixmap(400, 300)
        pixmap.fill(Qt.white)
        
        # Initialize the splash screen with the pixmap
        super().__init__(pixmap)
        
        # Create a painter to draw on the pixmap
        painter = QPainter(pixmap)
        
        # Try to load and draw the logo
        text_start_y = 50  # Default text position
        try:
            from llmtoolkit.resource_manager import get_pixmap
            logo_pixmap = get_pixmap("logo.png", "icons")
            if logo_pixmap and not logo_pixmap.isNull():
                # Scale logo to fit nicely (max 120x120)
                logo_pixmap = logo_pixmap.scaled(120, 120, Qt.KeepAspectRatio, Qt.SmoothTransformation)
                # Center the logo horizontally, position it in upper area
                logo_x = (400 - logo_pixmap.width()) // 2
                logo_y = 30
                painter.drawPixmap(logo_x, logo_y, logo_pixmap)
                # Adjust text positions to accommodate logo
                text_start_y = logo_y + logo_pixmap.height() + 20
        except Exception as e:
            # If logo loading fails, continue without it
            pass
        
        # Draw the application name
        font = QFont("Arial", 24, QFont.Bold)
        painter.setFont(font)
        painter.setPen(QColor(0, 0, 0))
        painter.drawText(0, text_start_y, 400, 40, Qt.AlignCenter, "LLM Toolkit")
        
        # Draw the version
        font = QFont("Arial", 12)
        painter.setFont(font)
        painter.drawText(0, text_start_y + 40, 400, 30, Qt.AlignCenter, "v0.1.0")
        
        # Finish painting
        painter.end()
        
        # Set the pixmap
        self.setPixmap(pixmap)
        
        # Create a progress bar
        self.progress_bar = QProgressBar(self)
        self.progress_bar.setGeometry(50, 240, 300, 20)
        self.progress_bar.setRange(0, 100)
        self.progress_bar.setValue(0)
        self.progress_bar.setAlignment(Qt.AlignCenter)
        self.progress_bar.setTextVisible(True)
        
        # Initialize progress
        self.progress = 0
        
        # Show the splash screen
        self.show()
    
    def showMessage(self, message, alignment=Qt.AlignBottom | Qt.AlignHCenter, color=Qt.black):
        """
        Show a message on the splash screen.
        
        Args:
            message: Message to display
            alignment: Text alignment
            color: Text color
        """
        super().showMessage(message, alignment, color)
        
        # Process events to update the UI
        self.update()
    
    def update_progress(self, value, message=None):
        """
        Update the progress bar and optionally show a message.
        
        Args:
            value: Progress value (0-100)
            message: Optional message to display
        """
        self.progress_bar.setValue(value)
        
        if message:
            self.showMessage(message)
        
        # Process events to update the UI
        self.update()
    
    @staticmethod
    def simulate_startup(splash, app_controller):
        """
        Simulate application startup with progress updates.
        
        Args:
            splash: SplashScreen instance
            app_controller: ApplicationController instance
        """
        # Simulate initialization steps
        splash.update_progress(10, "Initializing application...")
        time.sleep(0.2)
        
        splash.update_progress(30, "Loading configuration...")
        app_controller.config_manager.load()
        time.sleep(0.2)
        
        splash.update_progress(50, "Setting up components...")
        time.sleep(0.2)
        
        splash.update_progress(70, "Initializing UI...")
        app_controller.initialize_components()
        time.sleep(0.2)
        
        splash.update_progress(90, "Ready to launch...")
        time.sleep(0.2)
        
        splash.update_progress(100, "Starting application...")
        time.sleep(0.2)
        
        # Show the main window and close the splash screen
        if app_controller.main_window is not None:
            app_controller.main_window.show()
            splash.finish(app_controller.main_window)
        else:
            print("Error: Main window was not created successfully!")
            splash.close()