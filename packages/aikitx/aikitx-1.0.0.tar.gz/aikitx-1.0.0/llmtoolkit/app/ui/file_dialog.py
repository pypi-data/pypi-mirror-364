"""
File Selection Dialog

This module contains the GGUFFileDialog class, which is a custom file dialog
for selecting GGUF model files with additional features like recent files
and file validation.
"""

import os
import logging
from pathlib import Path
from typing import List, Optional, Tuple, Dict, Any

from PySide6.QtWidgets import (
    QDialog, QFileDialog, QVBoxLayout, QHBoxLayout, QLabel,
    QPushButton, QListWidget, QListWidgetItem, QSplitter,
    QWidget, QLineEdit, QComboBox, QCheckBox, QGroupBox,
    QRadioButton, QButtonGroup, QSizePolicy, QSpacerItem,
    QToolButton, QMenu, QMessageBox
)
from PySide6.QtCore import (
    Qt, QSize, QDir, QFileInfo, QUrl, QSettings, Signal,
    Slot, QModelIndex, QStandardPaths
)
from PySide6.QtGui import (
    QIcon, QPixmap, QFont, QColor, QDragEnterEvent,
    QDropEvent, QKeySequence
)

class GGUFFileDialog(QDialog):
    """
    Custom file dialog for selecting GGUF model files.
    
    This dialog extends the standard file dialog with additional features:
    - Recent files list
    - File validation
    - Favorites
    - File details preview
    """
    
    def __init__(self, parent=None, caption="Select GGUF Model", directory="", filter=""):
        """
        Initialize the file dialog.
        
        Args:
            parent: Parent widget
            caption: Dialog title
            directory: Initial directory
            filter: File filter
        """
        super().__init__(parent)
        self.logger = logging.getLogger("gguf_loader.ui.file_dialog")
        
        # Set dialog properties
        self.setWindowTitle(caption)
        self.resize(900, 600)
        self.setModal(True)
        
        # Initialize state variables
        self.current_directory = directory or QDir.homePath()
        self.selected_file = ""
        self.recent_files = []
        self.favorite_directories = []
        
        # Create UI components
        self._create_layout()
        self._load_settings()
        self._populate_recent_files()
        self._populate_favorite_directories()
        self._populate_file_list()
        
        self.logger.info("File dialog initialized")
    
    def _create_layout(self):
        """Create the dialog layout."""
        # Main layout
        main_layout = QVBoxLayout(self)
        
        # Create splitter for sidebar and main area
        splitter = QSplitter(Qt.Horizontal)
        main_layout.addWidget(splitter)
        
        # Create sidebar
        sidebar = self._create_sidebar()
        splitter.addWidget(sidebar)
        
        # Create main area
        main_area = self._create_main_area()
        splitter.addWidget(main_area)
        
        # Set initial splitter sizes
        splitter.setSizes([200, 700])
        
        # Create bottom area with buttons
        bottom_area = self._create_bottom_area()
        main_layout.addWidget(bottom_area)
    
    def _create_sidebar(self):
        """Create the sidebar with recent files and favorites."""
        sidebar_widget = QWidget()
        sidebar_layout = QVBoxLayout(sidebar_widget)
        sidebar_layout.setContentsMargins(0, 0, 0, 0)
        
        # Recent files group
        recent_group = QGroupBox("Recent Files")
        recent_layout = QVBoxLayout(recent_group)
        
        self.recent_list = QListWidget()
        self.recent_list.itemDoubleClicked.connect(self._on_recent_item_double_clicked)
        recent_layout.addWidget(self.recent_list)
        
        clear_recent_button = QPushButton("Clear Recent")
        clear_recent_button.clicked.connect(self._on_clear_recent)
        recent_layout.addWidget(clear_recent_button)
        
        sidebar_layout.addWidget(recent_group)
        
        # Favorites group
        favorites_group = QGroupBox("Favorites")
        favorites_layout = QVBoxLayout(favorites_group)
        
        self.favorites_list = QListWidget()
        self.favorites_list.itemDoubleClicked.connect(self._on_favorite_item_double_clicked)
        favorites_layout.addWidget(self.favorites_list)
        
        favorites_buttons_layout = QHBoxLayout()
        
        add_favorite_button = QPushButton("Add")
        add_favorite_button.clicked.connect(self._on_add_favorite)
        favorites_buttons_layout.addWidget(add_favorite_button)
        
        remove_favorite_button = QPushButton("Remove")
        remove_favorite_button.clicked.connect(self._on_remove_favorite)
        favorites_buttons_layout.addWidget(remove_favorite_button)
        
        favorites_layout.addLayout(favorites_buttons_layout)
        
        sidebar_layout.addWidget(favorites_group)
        
        return sidebar_widget
    
    def _create_main_area(self):
        """Create the main area with file browser and details."""
        main_widget = QWidget()
        main_layout = QVBoxLayout(main_widget)
        main_layout.setContentsMargins(0, 0, 0, 0)
        
        # Location bar
        location_layout = QHBoxLayout()
        
        back_button = QToolButton()
        back_button.setText("←")
        back_button.clicked.connect(self._on_back)
        location_layout.addWidget(back_button)
        
        up_button = QToolButton()
        up_button.setText("↑")
        up_button.clicked.connect(self._on_up)
        location_layout.addWidget(up_button)
        
        self.location_edit = QLineEdit()
        self.location_edit.setText(self.current_directory)
        self.location_edit.returnPressed.connect(self._on_location_changed)
        location_layout.addWidget(self.location_edit)
        
        browse_button = QToolButton()
        browse_button.setText("...")
        browse_button.clicked.connect(self._on_browse)
        location_layout.addWidget(browse_button)
        
        main_layout.addLayout(location_layout)
        
        # File list
        self.file_list = QListWidget()
        self.file_list.setSelectionMode(QListWidget.SingleSelection)
        self.file_list.itemDoubleClicked.connect(self._on_file_double_clicked)
        self.file_list.itemSelectionChanged.connect(self._on_file_selection_changed)
        main_layout.addWidget(self.file_list)
        
        # File details
        details_group = QGroupBox("File Details")
        details_layout = QVBoxLayout(details_group)
        
        self.file_name_label = QLabel("Name: ")
        details_layout.addWidget(self.file_name_label)
        
        self.file_size_label = QLabel("Size: ")
        details_layout.addWidget(self.file_size_label)
        
        self.file_date_label = QLabel("Date: ")
        details_layout.addWidget(self.file_date_label)
        
        self.file_type_label = QLabel("Type: ")
        details_layout.addWidget(self.file_type_label)
        
        main_layout.addWidget(details_group)
        
        return main_widget
    
    def _create_bottom_area(self):
        """Create the bottom area with buttons."""
        bottom_widget = QWidget()
        bottom_layout = QHBoxLayout(bottom_widget)
        
        # File name
        file_name_label = QLabel("File name:")
        bottom_layout.addWidget(file_name_label)
        
        self.file_name_edit = QLineEdit()
        self.file_name_edit.textChanged.connect(self._on_file_name_changed)
        bottom_layout.addWidget(self.file_name_edit)
        
        # File type filter
        file_type_label = QLabel("File type:")
        bottom_layout.addWidget(file_type_label)
        
        self.file_type_combo = QComboBox()
        self.file_type_combo.addItem("GGUF Files (*.gguf)")
        self.file_type_combo.addItem("All Files (*)")
        bottom_layout.addWidget(self.file_type_combo)
        
        # Buttons
        button_layout = QHBoxLayout()
        
        spacer = QSpacerItem(40, 20, QSizePolicy.Expanding, QSizePolicy.Minimum)
        button_layout.addItem(spacer)
        
        self.open_button = QPushButton("Open")
        self.open_button.setDefault(True)
        self.open_button.clicked.connect(self.accept)
        self.open_button.setEnabled(False)
        button_layout.addWidget(self.open_button)
        
        cancel_button = QPushButton("Cancel")
        cancel_button.clicked.connect(self.reject)
        button_layout.addWidget(cancel_button)
        
        bottom_layout.addLayout(button_layout)
        
        return bottom_widget
    
    def _load_settings(self):
        """Load dialog settings."""
        settings = QSettings()
        
        # Load recent files
        self.recent_files = settings.value("file_dialog/recent_files", [])
        if not isinstance(self.recent_files, list):
            self.recent_files = []
        
        # Load favorite directories
        self.favorite_directories = settings.value("file_dialog/favorite_directories", [])
        if not isinstance(self.favorite_directories, list):
            self.favorite_directories = []
        
        # Add default favorites if empty
        if not self.favorite_directories:
            documents_dir = QStandardPaths.writableLocation(QStandardPaths.DocumentsLocation)
            downloads_dir = QStandardPaths.writableLocation(QStandardPaths.DownloadLocation)
            
            if documents_dir:
                self.favorite_directories.append(documents_dir)
            if downloads_dir:
                self.favorite_directories.append(downloads_dir)
    
    def _save_settings(self):
        """Save dialog settings."""
        settings = QSettings()
        
        # Save recent files
        settings.setValue("file_dialog/recent_files", self.recent_files)
        
        # Save favorite directories
        settings.setValue("file_dialog/favorite_directories", self.favorite_directories)
    
    def _populate_recent_files(self):
        """Populate the recent files list."""
        self.recent_list.clear()
        
        for file_path in self.recent_files:
            if os.path.exists(file_path):
                item = QListWidgetItem(os.path.basename(file_path))
                item.setData(Qt.UserRole, file_path)
                item.setToolTip(file_path)
                self.recent_list.addItem(item)
    
    def _populate_favorite_directories(self):
        """Populate the favorite directories list."""
        self.favorites_list.clear()
        
        for directory in self.favorite_directories:
            if os.path.exists(directory) and os.path.isdir(directory):
                item = QListWidgetItem(os.path.basename(directory))
                item.setData(Qt.UserRole, directory)
                item.setToolTip(directory)
                self.favorites_list.addItem(item)
    
    def _populate_file_list(self):
        """Populate the file list with files from the current directory."""
        self.file_list.clear()
        
        # Update location edit
        self.location_edit.setText(self.current_directory)
        
        # Get file filter
        file_filter = "*.gguf" if self.file_type_combo.currentIndex() == 0 else "*"
        
        # Get files and directories
        dir_path = Path(self.current_directory)
        
        try:
            # Add parent directory item
            if dir_path.parent != dir_path:
                parent_item = QListWidgetItem("..")
                parent_item.setData(Qt.UserRole, str(dir_path.parent))
                parent_item.setData(Qt.UserRole + 1, "directory")
                self.file_list.addItem(parent_item)
            
            # Add directories
            for item in dir_path.iterdir():
                if item.is_dir():
                    list_item = QListWidgetItem(item.name)
                    list_item.setData(Qt.UserRole, str(item))
                    list_item.setData(Qt.UserRole + 1, "directory")
                    self.file_list.addItem(list_item)
            
            # Add files matching filter
            if file_filter == "*":
                files = list(dir_path.glob("*.*"))
            else:
                files = list(dir_path.glob(file_filter))
            
            for item in files:
                if item.is_file():
                    list_item = QListWidgetItem(item.name)
                    list_item.setData(Qt.UserRole, str(item))
                    list_item.setData(Qt.UserRole + 1, "file")
                    self.file_list.addItem(list_item)
        
        except Exception as e:
            self.logger.error(f"Error populating file list: {e}")
            QMessageBox.warning(
                self,
                "Error",
                f"Error accessing directory: {e}"
            )
    
    def _update_file_details(self, file_path):
        """Update the file details display."""
        if not file_path or not os.path.exists(file_path):
            self.file_name_label.setText("Name: ")
            self.file_size_label.setText("Size: ")
            self.file_date_label.setText("Date: ")
            self.file_type_label.setText("Type: ")
            return
        
        try:
            file_info = QFileInfo(file_path)
            
            # Update labels
            self.file_name_label.setText(f"Name: {file_info.fileName()}")
            
            # Format size
            size_bytes = file_info.size()
            if size_bytes < 1024:
                size_str = f"{size_bytes} bytes"
            elif size_bytes < 1024 * 1024:
                size_str = f"{size_bytes / 1024:.2f} KB"
            elif size_bytes < 1024 * 1024 * 1024:
                size_str = f"{size_bytes / (1024 * 1024):.2f} MB"
            else:
                size_str = f"{size_bytes / (1024 * 1024 * 1024):.2f} GB"
            
            self.file_size_label.setText(f"Size: {size_str}")
            
            # Format date
            date_str = file_info.lastModified().toString("yyyy-MM-dd hh:mm:ss")
            self.file_date_label.setText(f"Date: {date_str}")
            
            # Get file type
            if file_info.suffix().lower() == "gguf":
                self.file_type_label.setText("Type: GGUF Model File")
            else:
                self.file_type_label.setText(f"Type: {file_info.suffix().upper()} File")
            
        except Exception as e:
            self.logger.error(f"Error updating file details: {e}")
    
    def _add_to_recent_files(self, file_path):
        """Add a file to the recent files list."""
        # Remove if already in list
        if file_path in self.recent_files:
            self.recent_files.remove(file_path)
        
        # Add to beginning of list
        self.recent_files.insert(0, file_path)
        
        # Limit to 10 items
        if len(self.recent_files) > 10:
            self.recent_files = self.recent_files[:10]
        
        # Update UI and save settings
        self._populate_recent_files()
        self._save_settings()
    
    def _validate_file(self, file_path):
        """
        Validate a GGUF file.
        
        Args:
            file_path: Path to the file to validate
            
        Returns:
            Tuple of (is_valid, error_message)
        """
        # Check if file exists
        if not os.path.exists(file_path):
            return False, "File does not exist"
        
        # Check if it's a file
        if not os.path.isfile(file_path):
            return False, "Not a file"
        
        # Check file extension
        if not file_path.lower().endswith(".gguf"):
            return False, "Not a GGUF file"
        
        # Check if file is readable
        try:
            with open(file_path, "rb") as f:
                # Read first few bytes to check if it's a valid GGUF file
                # In a real implementation, we would check the file header
                header = f.read(4)
                if header != b"GGUF":
                    return False, "Invalid GGUF file format"
        except Exception as e:
            return False, f"Error reading file: {e}"
        
        return True, ""
    
    def _on_recent_item_double_clicked(self, item):
        """Handle double-click on a recent file item."""
        file_path = item.data(Qt.UserRole)
        if file_path and os.path.exists(file_path):
            self.selected_file = file_path
            self.file_name_edit.setText(os.path.basename(file_path))
            self._update_file_details(file_path)
            self.open_button.setEnabled(True)
            self.accept()
    
    def _on_favorite_item_double_clicked(self, item):
        """Handle double-click on a favorite directory item."""
        directory = item.data(Qt.UserRole)
        if directory and os.path.exists(directory) and os.path.isdir(directory):
            self.current_directory = directory
            self._populate_file_list()
    
    def _on_file_double_clicked(self, item):
        """Handle double-click on a file list item."""
        path = item.data(Qt.UserRole)
        item_type = item.data(Qt.UserRole + 1)
        
        if item_type == "directory":
            # Navigate to directory
            self.current_directory = path
            self._populate_file_list()
        elif item_type == "file":
            # Select file
            self.selected_file = path
            self.file_name_edit.setText(os.path.basename(path))
            self._update_file_details(path)
            self.open_button.setEnabled(True)
            self.accept()
    
    def _on_file_selection_changed(self):
        """Handle file selection change."""
        selected_items = self.file_list.selectedItems()
        if selected_items:
            item = selected_items[0]
            path = item.data(Qt.UserRole)
            item_type = item.data(Qt.UserRole + 1)
            
            if item_type == "file":
                self.selected_file = path
                self.file_name_edit.setText(os.path.basename(path))
                self._update_file_details(path)
                self.open_button.setEnabled(True)
            else:
                self._update_file_details("")
                self.open_button.setEnabled(False)
        else:
            self._update_file_details("")
            self.open_button.setEnabled(False)
    
    def _on_file_name_changed(self, text):
        """Handle file name change."""
        if text:
            # Check if the file exists in the current directory
            file_path = os.path.join(self.current_directory, text)
            if os.path.exists(file_path) and os.path.isfile(file_path):
                self.selected_file = file_path
                self._update_file_details(file_path)
                self.open_button.setEnabled(True)
            else:
                self._update_file_details("")
                self.open_button.setEnabled(False)
        else:
            self._update_file_details("")
            self.open_button.setEnabled(False)
    
    def _on_location_changed(self):
        """Handle location edit change."""
        new_location = self.location_edit.text()
        if os.path.exists(new_location) and os.path.isdir(new_location):
            self.current_directory = new_location
            self._populate_file_list()
        else:
            QMessageBox.warning(
                self,
                "Invalid Directory",
                f"The directory '{new_location}' does not exist."
            )
            self.location_edit.setText(self.current_directory)
    
    def _on_back(self):
        """Handle back button click."""
        # In a real implementation, we would maintain a history
        pass
    
    def _on_up(self):
        """Handle up button click."""
        parent_dir = os.path.dirname(self.current_directory)
        if parent_dir != self.current_directory:
            self.current_directory = parent_dir
            self._populate_file_list()
    
    def _on_browse(self):
        """Handle browse button click."""
        directory = QFileDialog.getExistingDirectory(
            self,
            "Select Directory",
            self.current_directory
        )
        
        if directory:
            self.current_directory = directory
            self._populate_file_list()
    
    def _on_clear_recent(self):
        """Handle clear recent files button click."""
        self.recent_files = []
        self._populate_recent_files()
        self._save_settings()
    
    def _on_add_favorite(self):
        """Handle add favorite button click."""
        if self.current_directory not in self.favorite_directories:
            self.favorite_directories.append(self.current_directory)
            self._populate_favorite_directories()
            self._save_settings()
    
    def _on_remove_favorite(self):
        """Handle remove favorite button click."""
        selected_items = self.favorites_list.selectedItems()
        if selected_items:
            item = selected_items[0]
            directory = item.data(Qt.UserRole)
            
            if directory in self.favorite_directories:
                self.favorite_directories.remove(directory)
                self._populate_favorite_directories()
                self._save_settings()
    
    def accept(self):
        """Handle dialog acceptance."""
        if not self.selected_file:
            QMessageBox.warning(
                self,
                "No File Selected",
                "Please select a file to open."
            )
            return
        
        # Validate the file
        is_valid, error_message = self._validate_file(self.selected_file)
        if not is_valid:
            QMessageBox.warning(
                self,
                "Invalid File",
                f"The selected file is not a valid GGUF file: {error_message}"
            )
            return
        
        # Add to recent files
        self._add_to_recent_files(self.selected_file)
        
        # Accept the dialog
        super().accept()
    
    def get_selected_file(self):
        """
        Get the selected file path.
        
        Returns:
            Selected file path, or empty string if no file was selected
        """
        return self.selected_file
    
    @staticmethod
    def get_gguf_file(parent=None, caption="Select GGUF Model", directory=""):
        """
        Static method to get a GGUF file.
        
        Args:
            parent: Parent widget
            caption: Dialog title
            directory: Initial directory
            
        Returns:
            Tuple of (file_path, ok), where ok is True if a file was selected
        """
        dialog = GGUFFileDialog(parent, caption, directory)
        result = dialog.exec()
        
        if result == QDialog.Accepted:
            return dialog.get_selected_file(), True
        else:
            return "", False