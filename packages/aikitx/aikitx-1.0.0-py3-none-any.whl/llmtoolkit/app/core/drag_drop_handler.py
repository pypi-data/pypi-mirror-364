"""
Drag Drop Handler

This module implements the DragDropHandler class, which is responsible for:
- Intercepting drag-drop events for addon files
- Validating dropped addon files
- Initiating the addon installation workflow
"""

import logging
import os
from pathlib import Path
from typing import List, Optional, Tuple, Any, Dict

from PySide6.QtCore import QObject, QUrl, Signal, Slot
from PySide6.QtGui import QDragEnterEvent, QDropEvent

from llmtoolkit.app.core.addon_manager import AddonManager
from llmtoolkit.app.core.event_bus import EventBus

class DragDropHandler(QObject):
    """
    Handles drag and drop events for addon files.
    
    This class is responsible for:
    - Intercepting drag-drop events for addon files
    - Validating dropped addon files
    - Initiating the addon installation workflow
    """
    
    # Signals
    addon_installation_started = Signal(str)  # file_path
    addon_installation_progress = Signal(str, int)  # file_path, progress
    addon_installation_completed = Signal(str, str)  # file_path, addon_id
    addon_installation_failed = Signal(str, str)  # file_path, error_message
    
    def __init__(self, addon_manager: AddonManager, event_bus: Optional[EventBus] = None):
        """
        Initialize the drag drop handler.
        
        Args:
            addon_manager: AddonManager instance for installing addons
            event_bus: Optional EventBus for publishing events
        """
        super().__init__()
        self.logger = logging.getLogger("gguf_loader.drag_drop_handler")
        self.addon_manager = addon_manager
        self.event_bus = event_bus
        
        # Supported file extensions for addons
        self.addon_extensions = ['.zip', '.addon']
        
        self.logger.info("DragDropHandler initialized")
    
    def can_handle_drag_event(self, event: QDragEnterEvent) -> bool:
        """
        Check if the drag event contains valid addon files.
        
        Args:
            event: The drag enter event to check
            
        Returns:
            True if the event contains valid addon files, False otherwise
        """
        if not event.mimeData().hasUrls():
            return False
        
        # Check if any URL is a valid addon file
        for url in event.mimeData().urls():
            if self._is_valid_addon_url(url):
                return True
        
        return False
    
    def handle_drop_event(self, event: QDropEvent) -> bool:
        """
        Handle a drop event containing addon files.
        
        Args:
            event: The drop event to handle
            
        Returns:
            True if the event was handled successfully, False otherwise
        """
        if not event.mimeData().hasUrls():
            return False
        
        # Process dropped addon files
        for url in event.mimeData().urls():
            if self._is_valid_addon_url(url):
                file_path = url.toLocalFile()
                self._install_addon(file_path)
                return True
        
        return False
    
    def _is_valid_addon_url(self, url: QUrl) -> bool:
        """
        Check if a URL points to a valid addon file.
        
        Args:
            url: The URL to check
            
        Returns:
            True if the URL points to a valid addon file, False otherwise
        """
        if not url.isLocalFile():
            return False
        
        file_path = url.toLocalFile()
        file_ext = os.path.splitext(file_path)[1].lower()
        
        return file_ext in self.addon_extensions
    
    def _install_addon(self, file_path: str) -> None:
        """
        Install an addon from a file.
        
        Args:
            file_path: Path to the addon file
        """
        self.logger.info(f"Installing addon from: {file_path}")
        
        # Emit installation started signal
        self.addon_installation_started.emit(file_path)
        
        # Validate the addon file
        path = Path(file_path)
        if not path.exists():
            error_message = f"Addon file not found: {file_path}"
            self.logger.error(error_message)
            self.addon_installation_failed.emit(file_path, error_message)
            return
        
        # Emit progress signal (25%)
        self.addon_installation_progress.emit(file_path, 25)
        
        # Validate addon package
        is_valid, error_message, metadata = self.addon_manager.loader.validate_addon_package(path)
        if not is_valid:
            self.logger.error(f"Invalid addon package: {error_message}")
            self.addon_installation_failed.emit(file_path, error_message)
            return
        
        # Emit progress signal (50%)
        self.addon_installation_progress.emit(file_path, 50)
        
        # Install the addon
        success, error_message, addon_id = self.addon_manager.install_addon(path)
        
        # Emit progress signal (75%)
        self.addon_installation_progress.emit(file_path, 75)
        
        if not success:
            self.logger.error(f"Failed to install addon: {error_message}")
            self.addon_installation_failed.emit(file_path, error_message)
            return
        
        # Emit progress signal (100%)
        self.addon_installation_progress.emit(file_path, 100)
        
        # Emit installation completed signal
        self.addon_installation_completed.emit(file_path, addon_id)
        
        # Publish event
        if self.event_bus:
            self.event_bus.publish("addon.installed_via_drag_drop", addon_id, metadata.name)
        
        self.logger.info(f"Addon installed successfully: {metadata.name} (ID: {addon_id})")