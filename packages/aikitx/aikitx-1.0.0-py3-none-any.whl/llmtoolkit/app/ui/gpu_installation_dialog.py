"""
GPU Installation Dialog

This module provides a comprehensive dialog for installing GPU acceleration dependencies.
"""

import logging
import sys
import subprocess
import threading
from typing import Dict, List, Optional, Tuple
from enum import Enum

from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QTextEdit, QProgressBar, QGroupBox, QCheckBox, QComboBox,
    QTabWidget, QWidget, QScrollArea, QMessageBox, QDialogButtonBox,
    QListWidget, QListWidgetItem, QSplitter
)
from PySide6.QtCore import Qt, QThread, Signal, QTimer, QSize
from PySide6.QtGui import QFont, QIcon, QPixmap

from llmtoolkit.app.core.gpu_detector import GPUDetector, GPUBackend


class InstallationStatus(Enum):
    """Installation status enumeration."""
    PENDING = "pending"
    INSTALLING = "installing"
    SUCCESS = "success"
    FAILED = "failed"
    CANCELLED = "cancelled"


class InstallationWorker(QThread):
    """Worker thread for installing GPU dependencies."""
    
    # Signals
    progress_updated = Signal(str)  # Progress message
    installation_completed = Signal(str, bool)  # Backend name, success
    log_message = Signal(str)  # Log message
    
    def __init__(self, gpu_detector: GPUDetector, backend: GPUBackend):
        """
        Initialize the installation worker.
        
        Args:
            gpu_detector: GPU detector instance
            backend: Backend to install
        """
        super().__init__()
        self.gpu_detector = gpu_detector
        self.backend = backend
        self.cancelled = False
        self.logger = logging.getLogger("gguf_loader.gpu_installation")
    
    def run(self):
        """Run the installation process."""
        try:
            self.progress_updated.emit(f"Starting {self.backend.value.upper()} installation...")
            self.log_message.emit(f"Installing {self.backend.value.upper()} dependencies")
            
            # Install dependencies
            success = self.gpu_detector.install_gpu_dependencies(self.backend)
            
            if not self.cancelled:
                if success:
                    self.progress_updated.emit(f"{self.backend.value.upper()} installation completed successfully")
                    self.log_message.emit(f"[OK] {self.backend.value.upper()} installation successful")
                else:
                    self.progress_updated.emit(f"{self.backend.value.upper()} installation failed")
                    self.log_message.emit(f"[ERROR] {self.backend.value.upper()} installation failed")
                
                self.installation_completed.emit(self.backend.value, success)
            
        except Exception as e:
            if not self.cancelled:
                error_msg = f"Error installing {self.backend.value.upper()}: {str(e)}"
                self.progress_updated.emit(error_msg)
                self.log_message.emit(f"[ERROR] {error_msg}")
                self.installation_completed.emit(self.backend.value, False)
    
    def cancel(self):
        """Cancel the installation."""
        self.cancelled = True
        self.progress_updated.emit("Installation cancelled")
        self.log_message.emit("[WARN] Installation cancelled by user")


class GPUInstallationDialog(QDialog):
    """
    Comprehensive dialog for installing GPU acceleration dependencies.
    
    This dialog provides:
    - Detection of available GPU backends
    - Installation options for each backend
    - Progress tracking and logging
    - System requirements checking
    - Post-installation verification
    """
    
    def __init__(self, gpu_detector: GPUDetector, parent=None):
        """
        Initialize the GPU installation dialog.
        
        Args:
            gpu_detector: GPU detector instance
            parent: Parent widget
        """
        super().__init__(parent)
        self.logger = logging.getLogger("gguf_loader.ui.gpu_installation")
        self.gpu_detector = gpu_detector
        self.gpu_capabilities = None
        
        # Installation state
        self.installation_workers = {}
        self.installation_status = {}
        
        # Set dialog properties
        self.setWindowTitle("GPU Acceleration Setup")
        self.setMinimumSize(800, 600)
        self.setModal(True)
        
        # Initialize UI
        self._init_ui()
        
        # Detect GPU capabilities
        self._detect_capabilities()
    
    def _init_ui(self):
        """Initialize the user interface."""
        layout = QVBoxLayout(self)
        
        # Title and description
        title_label = QLabel("GPU Acceleration Setup")
        title_label.setStyleSheet("font-size: 18px; font-weight: bold; margin-bottom: 10px;")
        layout.addWidget(title_label)
        
        desc_label = QLabel(
            "This wizard will help you install GPU acceleration support for faster model inference. "
            "Select the appropriate backend for your GPU and follow the installation steps."
        )
        desc_label.setWordWrap(True)
        desc_label.setStyleSheet("color: #666; margin-bottom: 20px;")
        layout.addWidget(desc_label)
        
        # Create tab widget
        self.tab_widget = QTabWidget()
        layout.addWidget(self.tab_widget)
        
        # Create tabs
        self._create_detection_tab()
        self._create_installation_tab()
        self._create_verification_tab()
        
        # Button box
        button_box = QDialogButtonBox(QDialogButtonBox.Close)
        button_box.rejected.connect(self.reject)
        layout.addWidget(button_box)
    
    def _create_detection_tab(self):
        """Create the GPU detection tab."""
        tab = QWidget()
        layout = QVBoxLayout(tab)
        
        # Detection status
        status_group = QGroupBox("GPU Detection Status")
        status_layout = QVBoxLayout(status_group)
        
        self.detection_status_label = QLabel("Detecting GPUs...")
        self.detection_status_label.setStyleSheet("font-weight: bold;")
        status_layout.addWidget(self.detection_status_label)
        
        # Refresh button
        refresh_layout = QHBoxLayout()
        refresh_button = QPushButton("Refresh Detection")
        refresh_button.clicked.connect(self._detect_capabilities)
        refresh_layout.addWidget(refresh_button)
        refresh_layout.addStretch()
        status_layout.addLayout(refresh_layout)
        
        layout.addWidget(status_group)
        
        # GPU devices list
        devices_group = QGroupBox("Detected GPU Devices")
        devices_layout = QVBoxLayout(devices_group)
        
        self.devices_list = QListWidget()
        self.devices_list.setMinimumHeight(150)
        devices_layout.addWidget(self.devices_list)
        
        layout.addWidget(devices_group)
        
        # Backend support status
        backends_group = QGroupBox("Backend Support Status")
        backends_layout = QVBoxLayout(backends_group)
        
        self.backends_list = QListWidget()
        self.backends_list.setMinimumHeight(150)
        backends_layout.addWidget(self.backends_list)
        
        layout.addWidget(backends_group)
        
        layout.addStretch()
        self.tab_widget.addTab(tab, "Detection")
    
    def _create_installation_tab(self):
        """Create the installation tab."""
        tab = QWidget()
        layout = QVBoxLayout(tab)
        
        # Installation options
        options_group = QGroupBox("Installation Options")
        options_layout = QVBoxLayout(options_group)
        
        # Backend selection
        backend_layout = QHBoxLayout()
        backend_layout.addWidget(QLabel("Select Backend:"))
        
        self.backend_combo = QComboBox()
        self.backend_combo.currentTextChanged.connect(self._on_backend_selection_changed)
        backend_layout.addWidget(self.backend_combo)
        
        backend_layout.addStretch()
        options_layout.addLayout(backend_layout)
        
        # Backend description
        self.backend_description = QLabel()
        self.backend_description.setWordWrap(True)
        self.backend_description.setStyleSheet("color: #666; margin: 10px 0;")
        options_layout.addWidget(self.backend_description)
        
        # Installation requirements
        self.requirements_label = QLabel()
        self.requirements_label.setWordWrap(True)
        self.requirements_label.setStyleSheet("background: #f0f0f0; padding: 10px; border-radius: 5px;")
        options_layout.addWidget(self.requirements_label)
        
        layout.addWidget(options_group)
        
        # Installation controls
        controls_group = QGroupBox("Installation")
        controls_layout = QVBoxLayout(controls_group)
        
        # Install button
        button_layout = QHBoxLayout()
        self.install_button = QPushButton("Install Selected Backend")
        self.install_button.setStyleSheet("""
            QPushButton {
                background-color: #28a745;
                color: white;
                border: none;
                border-radius: 6px;
                padding: 10px 20px;
                font-weight: bold;
                font-size: 14px;
            }
            QPushButton:hover {
                background-color: #218838;
            }
            QPushButton:disabled {
                background-color: #6c757d;
            }
        """)
        self.install_button.clicked.connect(self._install_selected_backend)
        button_layout.addWidget(self.install_button)
        
        self.cancel_button = QPushButton("Cancel Installation")
        self.cancel_button.setEnabled(False)
        self.cancel_button.clicked.connect(self._cancel_installation)
        button_layout.addWidget(self.cancel_button)
        
        button_layout.addStretch()
        controls_layout.addLayout(button_layout)
        
        # Progress bar
        self.progress_bar = QProgressBar()
        self.progress_bar.setRange(0, 0)  # Indeterminate
        self.progress_bar.setVisible(False)
        controls_layout.addWidget(self.progress_bar)
        
        # Progress label
        self.progress_label = QLabel()
        self.progress_label.setStyleSheet("color: #666;")
        controls_layout.addWidget(self.progress_label)
        
        layout.addWidget(controls_group)
        
        # Installation log
        log_group = QGroupBox("Installation Log")
        log_layout = QVBoxLayout(log_group)
        
        self.log_text = QTextEdit()
        self.log_text.setReadOnly(True)
        self.log_text.setMaximumHeight(200)
        self.log_text.setStyleSheet("font-family: monospace; background: #f8f9fa;")
        log_layout.addWidget(self.log_text)
        
        layout.addWidget(log_group)
        
        self.tab_widget.addTab(tab, "Installation")
    
    def _create_verification_tab(self):
        """Create the verification tab."""
        tab = QWidget()
        layout = QVBoxLayout(tab)
        
        # Verification status
        status_group = QGroupBox("Installation Verification")
        status_layout = QVBoxLayout(status_group)
        
        self.verification_status = QLabel("Click 'Verify Installation' to check if GPU acceleration is working.")
        self.verification_status.setWordWrap(True)
        status_layout.addWidget(self.verification_status)
        
        # Verify button
        verify_layout = QHBoxLayout()
        verify_button = QPushButton("Verify Installation")
        verify_button.clicked.connect(self._verify_installation)
        verify_layout.addWidget(verify_button)
        verify_layout.addStretch()
        status_layout.addLayout(verify_layout)
        
        layout.addWidget(status_group)
        
        # Verification results
        results_group = QGroupBox("Verification Results")
        results_layout = QVBoxLayout(results_group)
        
        self.verification_results = QTextEdit()
        self.verification_results.setReadOnly(True)
        self.verification_results.setStyleSheet("font-family: monospace; background: #f8f9fa;")
        results_layout.addWidget(self.verification_results)
        
        layout.addWidget(results_group)
        
        # Next steps
        next_steps_group = QGroupBox("Next Steps")
        next_steps_layout = QVBoxLayout(next_steps_group)
        
        next_steps_text = QLabel(
            "After successful installation:\n"
            "1. Restart the application\n"
            "2. Go to Preferences → Models\n"
            "3. Select 'GPU Preferred' or 'Auto' processing unit\n"
            "4. Load a model to test GPU acceleration"
        )
        next_steps_text.setStyleSheet("color: #666;")
        next_steps_layout.addWidget(next_steps_text)
        
        layout.addWidget(next_steps_group)
        
        layout.addStretch()
        self.tab_widget.addTab(tab, "Verification")
    
    def _detect_capabilities(self):
        """Detect GPU capabilities and update UI."""
        try:
            self.detection_status_label.setText("Detecting GPUs...")
            
            # Perform detection
            self.gpu_capabilities = self.gpu_detector.detect_gpu_capabilities()
            
            # Update detection status
            if self.gpu_capabilities.has_gpu:
                gpu_count = len(self.gpu_capabilities.devices)
                self.detection_status_label.setText(f"[OK] Found {gpu_count} GPU device(s)")
                self.detection_status_label.setStyleSheet("font-weight: bold; color: green;")
            else:
                self.detection_status_label.setText("[WARN] No GPU devices detected")
                self.detection_status_label.setStyleSheet("font-weight: bold; color: orange;")
            
            # Update devices list
            self.devices_list.clear()
            if self.gpu_capabilities.devices:
                for device in self.gpu_capabilities.devices:
                    item_text = f"{device.name} ({device.backend.value.upper()}) - {device.memory_total} MB"
                    item = QListWidgetItem(item_text)
                    if device.is_available:
                        item.setIcon(self._get_status_icon("success"))
                    else:
                        item.setIcon(self._get_status_icon("warning"))
                    self.devices_list.addItem(item)
            else:
                item = QListWidgetItem("No GPU devices detected")
                item.setIcon(self._get_status_icon("info"))
                self.devices_list.addItem(item)
            
            # Update backends list
            self.backends_list.clear()
            for backend_name, available in self.gpu_capabilities.dependencies_status.items():
                status_text = "[OK] Available" if available else "[ERROR] Not Available"
                item_text = f"{backend_name.upper()}: {status_text}"
                item = QListWidgetItem(item_text)
                
                if available:
                    item.setIcon(self._get_status_icon("success"))
                else:
                    item.setIcon(self._get_status_icon("error"))
                
                self.backends_list.addItem(item)
            
            # Update installation options
            self._update_installation_options()
            
        except Exception as e:
            self.detection_status_label.setText(f"[ERROR] Detection failed: {str(e)}")
            self.detection_status_label.setStyleSheet("font-weight: bold; color: red;")
            self.logger.error(f"GPU detection failed: {e}")
    
    def _update_installation_options(self):
        """Update installation options based on detection results."""
        self.backend_combo.clear()
        
        if not self.gpu_capabilities:
            return
        
        # Add backends that are not available for installation
        installable_backends = []
        for backend_name, available in self.gpu_capabilities.dependencies_status.items():
            if not available:
                try:
                    backend_enum = GPUBackend(backend_name)
                    installable_backends.append(backend_enum)
                except ValueError:
                    continue
        
        if installable_backends:
            for backend in installable_backends:
                self.backend_combo.addItem(backend.value.upper(), backend)
            
            # Select the first backend by default
            self._on_backend_selection_changed()
            self.install_button.setEnabled(True)
        else:
            self.backend_combo.addItem("No backends available for installation")
            self.install_button.setEnabled(False)
            self.backend_description.setText("All supported GPU backends are already installed.")
            self.requirements_label.setText("")
    
    def _on_backend_selection_changed(self):
        """Handle backend selection change."""
        backend_data = self.backend_combo.currentData()
        if not isinstance(backend_data, GPUBackend):
            return
        
        backend = backend_data
        
        # Update description
        descriptions = {
            GPUBackend.CUDA: "NVIDIA CUDA provides the best performance for NVIDIA GPUs. Recommended for RTX/GTX series graphics cards.",
            GPUBackend.OPENCL: "OpenCL provides cross-platform GPU acceleration. Works with NVIDIA, AMD, and Intel GPUs.",
            GPUBackend.VULKAN: "Vulkan is a modern graphics API with GPU compute capabilities. Requires manual setup.",
            GPUBackend.DIRECTML: "DirectML is Microsoft's machine learning API for Windows. Currently not implemented.",
            GPUBackend.METAL: "Metal is Apple's graphics API for macOS. Automatically available on supported systems."
        }
        
        self.backend_description.setText(descriptions.get(backend, "No description available."))
        
        # Update requirements
        requirements = self.gpu_detector.get_installation_instructions(backend)
        self.requirements_label.setText(f"Requirements:\n{requirements}")
    
    def _install_selected_backend(self):
        """Install the selected backend."""
        backend_data = self.backend_combo.currentData()
        if not isinstance(backend_data, GPUBackend):
            return
        
        backend = backend_data
        
        # Confirm installation
        reply = QMessageBox.question(
            self,
            "Confirm Installation",
            f"Install {backend.value.upper()} support for GPU acceleration?\n\n"
            f"This may take several minutes and requires an internet connection.",
            QMessageBox.Yes | QMessageBox.No
        )
        
        if reply != QMessageBox.Yes:
            return
        
        # Start installation
        self._start_installation(backend)
    
    def _start_installation(self, backend: GPUBackend):
        """Start the installation process."""
        # Update UI state
        self.install_button.setEnabled(False)
        self.cancel_button.setEnabled(True)
        self.progress_bar.setVisible(True)
        self.progress_label.setText(f"Installing {backend.value.upper()}...")
        
        # Clear log
        self.log_text.clear()
        self.log_text.append(f"Starting {backend.value.upper()} installation...")
        
        # Create and start worker
        worker = InstallationWorker(self.gpu_detector, backend)
        worker.progress_updated.connect(self.progress_label.setText)
        worker.log_message.connect(self.log_text.append)
        worker.installation_completed.connect(self._on_installation_completed)
        
        self.installation_workers[backend.value] = worker
        self.installation_status[backend.value] = InstallationStatus.INSTALLING
        
        worker.start()
    
    def _cancel_installation(self):
        """Cancel the current installation."""
        for worker in self.installation_workers.values():
            if worker.isRunning():
                worker.cancel()
                worker.wait(3000)  # Wait up to 3 seconds
                if worker.isRunning():
                    worker.terminate()
        
        # Update UI state
        self.install_button.setEnabled(True)
        self.cancel_button.setEnabled(False)
        self.progress_bar.setVisible(False)
        self.progress_label.setText("Installation cancelled")
    
    def _on_installation_completed(self, backend_name: str, success: bool):
        """Handle installation completion."""
        # Update UI state
        self.install_button.setEnabled(True)
        self.cancel_button.setEnabled(False)
        self.progress_bar.setVisible(False)
        
        if success:
            self.progress_label.setText(f"{backend_name.upper()} installation completed successfully!")
            self.installation_status[backend_name] = InstallationStatus.SUCCESS
            
            # Show success message
            QMessageBox.information(
                self,
                "Installation Complete",
                f"{backend_name.upper()} support has been installed successfully!\n\n"
                f"Please restart the application to use GPU acceleration."
            )
            
            # Switch to verification tab
            self.tab_widget.setCurrentIndex(2)
            
        else:
            self.progress_label.setText(f"{backend_name.upper()} installation failed")
            self.installation_status[backend_name] = InstallationStatus.FAILED
            
            # Show error message
            QMessageBox.warning(
                self,
                "Installation Failed",
                f"Failed to install {backend_name.upper()} support.\n\n"
                f"Please check the installation log for details."
            )
        
        # Re-detect capabilities
        QTimer.singleShot(1000, self._detect_capabilities)
    
    def _verify_installation(self):
        """Verify the installation."""
        self.verification_results.clear()
        self.verification_results.append("Verifying GPU acceleration installation...\n")
        
        try:
            # Re-detect capabilities
            capabilities = self.gpu_detector.detect_gpu_capabilities()
            
            self.verification_results.append("=== GPU Detection Results ===")
            self.verification_results.append(f"GPUs Found: {len(capabilities.devices)}")
            self.verification_results.append(f"GPU Support Available: {'Yes' if capabilities.has_gpu else 'No'}")
            self.verification_results.append(f"Recommended Backend: {capabilities.recommended_backend.value.upper()}")
            
            if capabilities.devices:
                self.verification_results.append("\n=== Detected Devices ===")
                for i, device in enumerate(capabilities.devices, 1):
                    self.verification_results.append(f"{i}. {device.name}")
                    self.verification_results.append(f"   Backend: {device.backend.value.upper()}")
                    self.verification_results.append(f"   Memory: {device.memory_total:,} MB")
            
            self.verification_results.append("\n=== Backend Status ===")
            for backend, available in capabilities.dependencies_status.items():
                status = "[OK] Available" if available else "[ERROR] Not Available"
                self.verification_results.append(f"{backend.upper()}: {status}")
            
            if capabilities.has_gpu:
                self.verification_results.append("\n[OK] GPU acceleration is ready!")
                self.verification_status.setText("[OK] GPU acceleration is working correctly.")
                self.verification_status.setStyleSheet("color: green; font-weight: bold;")
            else:
                self.verification_results.append("\n[WARN] No GPU acceleration available.")
                self.verification_status.setText("[WARN] GPU acceleration is not available. Check installation and drivers.")
                self.verification_status.setStyleSheet("color: orange; font-weight: bold;")
            
        except Exception as e:
            self.verification_results.append(f"\n[ERROR] Verification failed: {str(e)}")
            self.verification_status.setText("[ERROR] Verification failed. Check installation.")
            self.verification_status.setStyleSheet("color: red; font-weight: bold;")
    
    def _get_status_icon(self, status: str):
        """Get status icon (placeholder for now)."""
        # In a real implementation, you would return actual QIcon objects
        # For now, we'll just return None
        return None
    
    def closeEvent(self, event):
        """Handle dialog close event."""
        # Cancel any running installations
        for worker in self.installation_workers.values():
            if worker.isRunning():
                worker.cancel()
                worker.wait(1000)
                if worker.isRunning():
                    worker.terminate()
        
        super().closeEvent(event)