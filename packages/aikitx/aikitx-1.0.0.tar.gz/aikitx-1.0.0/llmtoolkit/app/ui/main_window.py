"""
Main Window

This module contains the MainWindow class, which is the primary UI component
of llm toolkit. Features a clean, minimal interface with only
essential controls visible on the main surface, supporting universal model formats.
"""

import os
import logging
import time
from pathlib import Path
from typing import Optional, Dict, Any, List, Tuple

from PySide6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
    QPushButton, QFileDialog, QMessageBox, QMenu, QMenuBar,
    QStatusBar, QTabWidget, QTextEdit, QLineEdit, QComboBox,
    QProgressBar, QSplitter, QDialog
)
from PySide6.QtCore import Qt, QSize, QTimer, Signal, Slot
from PySide6.QtGui import QIcon, QAction, QKeySequence

from llmtoolkit.app.core.event_bus import EventBus
from llmtoolkit.app.core.config_manager import ConfigManager
from llmtoolkit.app.ui.file_dialog import GGUFFileDialog
from llmtoolkit.app.ui.preferences_dialog import PreferencesDialog

from llmtoolkit.app.ui.chat_tab import ChatTab
from llmtoolkit.app.ui.summarization_tab import SummarizationTab
from llmtoolkit.app.ui.email_automation_tab import EmailAutomationTab
from llmtoolkit.app.ui.bulk_email_marketing_tab import BulkEmailMarketingTab
from llmtoolkit.app.ui.social_media_marketing_tab import SocialMediaMarketingTab
from llmtoolkit.app.ui.about_dialog import AboutDialog
from llmtoolkit.app.ui.model_loading_dialog import ModelLoadingDialog
from llmtoolkit.app.ui.system_prompts_dialog import SystemPromptsDialog
from llmtoolkit.app.ui.model_parameters_dialog import ModelParametersDialog
from llmtoolkit.app.ui.email_settings_dialog import EmailSettingsDialog
from llmtoolkit.app.ui.theme_manager import ThemeManager, Theme
from llmtoolkit.app.services.email_service import EmailService

# Import performance optimization components
from llmtoolkit.app.core.performance_integration import PerformanceIntegratedBackendManager

# Import universal loading components
from llmtoolkit.app.services.universal_model_loader import UniversalModelLoader, UniversalLoadingResult
from llmtoolkit.app.core.universal_events import UniversalLoadingProgress
from llmtoolkit.app.ui.universal_model_dialog import UniversalModelDialog
from llmtoolkit.app.core.universal_loading_monitor import UniversalLoadingMonitor
from llmtoolkit.app.core.universal_format_detector import ModelFormat

# Import resource monitoring components
from llmtoolkit.app.ui.resource_monitor_header import ResourceMonitorHeader
from llmtoolkit.app.services.system_resource_monitor import SystemResourceMonitor


class MainWindow(QMainWindow):
    """
    Main application window with clean, minimal interface.
    
    Features only essential controls on the main surface:
    - Model selection dropdown at the top
    - Tab widget for Chat and Summarization
    - Comprehensive menu bar for advanced settings
    """
    
    def __init__(self, event_bus: EventBus, config_manager: ConfigManager, email_service=None, backend_manager=None, parent=None):
        """
        Initialize the main window.
        
        Args:
            event_bus: Application event bus
            config_manager: Configuration manager
            email_service: Email service instance (optional, will create if not provided)
            backend_manager: Backend manager instance (optional, will create if not provided)
            parent: Parent widget
        """
        super().__init__(parent)
        
        self.logger = logging.getLogger("gguf_loader.ui.main_window")
        self.event_bus = event_bus
        self.config_manager = config_manager
        
        # Progress dialog for model loading
        self.loading_dialog: Optional[ModelLoadingDialog] = None
        
        # Use provided backend manager or create a new one
        if backend_manager:
            self.backend_manager = backend_manager
        else:
            # Fallback for backward compatibility
            self.backend_manager = PerformanceIntegratedBackendManager()
            self.backend_manager.start_monitoring()
        
        # Initialize universal loading components
        self.universal_loader = UniversalModelLoader()
        self.loading_monitor = UniversalLoadingMonitor()
        
        # Initialize resource monitoring components
        self.system_resource_monitor = SystemResourceMonitor(self.event_bus, self)
        
        # Connect universal loader signals
        self._connect_universal_loader_signals()
        
        # Connect loading monitor to universal loader for comprehensive monitoring
        self._integrate_loading_monitor()
        
        # Connect BackendManager events to UI update methods
        self._connect_backend_manager_events()
        
        # Log BackendManager readiness for chat operations
        self._log_backend_manager_status()
        
        # Initialize theme manager
        self.theme_manager = ThemeManager(config_manager)
        
        # Use provided email service or create a fallback one
        if email_service:
            self.email_service = email_service
        else:
            # Fallback for backward compatibility
            self.email_service = EmailService(event_bus, config_manager)
        
        # Current system prompt and model parameters
        self.current_system_prompt = ""
        self.current_model_parameters = {}
        
        # Set window properties
        self.setWindowTitle("LLM Toolkit")
        self.setMinimumSize(800, 600)
        
        # Set window icon
        from llmtoolkit.resource_manager import get_icon
        app_icon = get_icon("icon.ico")
        if app_icon:
            self.setWindowIcon(app_icon)
        
        # Initialize UI components
        self._init_ui()
        
        # Connect event handlers
        self._connect_events()
        
        # Bridge new backend to old event system for chat/summary/email
        self._setup_backend_bridge()
        
        # Load window state from configuration
        self._load_window_state()
    
    def _init_ui(self):
        """Initialize UI components with clean, minimal design."""
        # Create central widget
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # Create main layout
        main_layout = QVBoxLayout(central_widget)
        main_layout.setContentsMargins(10, 10, 10, 10)
        main_layout.setSpacing(10)
        
        # Create comprehensive menu bar
        self._create_menu_bar()
        
        # Create model selection section (essential control)
        model_section = self._create_model_selection()
        main_layout.addWidget(model_section)
        
        # Create resource monitoring header (positioned below model loading section)
        self.resource_monitor_header = ResourceMonitorHeader(
            self.event_bus, 
            self.theme_manager, 
            self
        )
        main_layout.addWidget(self.resource_monitor_header)
        
        # Create tab widget for Chat and Summarization (essential controls)
        self.main_tabs = QTabWidget()
        # Tab styling will be handled by theme manager
        
        # Create Chat tab
        self.chat_tab = ChatTab(self.event_bus, self)
        self.main_tabs.addTab(self.chat_tab, "Chat")
        
        # Create Summarization tab
        self.summarization_tab = SummarizationTab(self.event_bus, self)
        self.main_tabs.addTab(self.summarization_tab, "Summarization")
        
        # Create Email Automation tab
        self.email_automation_tab = EmailAutomationTab(self.event_bus, self.email_service, self.theme_manager, self)
        self.main_tabs.addTab(self.email_automation_tab, "📧 Email Automation")
        
        # Create Bulk Email Marketing tab
        self.bulk_email_marketing_tab = BulkEmailMarketingTab(self.event_bus, self.theme_manager, self)
        self.main_tabs.addTab(self.bulk_email_marketing_tab, "📊 Bulk Email Marketing")
        
        # Create Social Media Marketing tab
        self.social_media_marketing_tab = SocialMediaMarketingTab(self.event_bus, self.theme_manager, self)
        self.main_tabs.addTab(self.social_media_marketing_tab, "📱 Social Media Marketing")
        
        main_layout.addWidget(self.main_tabs)
        
        # Create status bar
        self.status_bar = QStatusBar()
        # Status bar styling will be handled by theme manager
        self.setStatusBar(self.status_bar)
        self.status_bar.showMessage("Ready")
    
    def _create_model_selection(self):
        """Create the model selection section with dropdown."""
        model_widget = QWidget()
        model_layout = QHBoxLayout(model_widget)
        model_layout.setContentsMargins(0, 0, 0, 0)
        
        # Model selection label
        model_label = QLabel("Model:")
        model_label.setObjectName("model_label")  # For theme styling
        model_layout.addWidget(model_label)
        
        # Model selection dropdown
        self.model_dropdown = QComboBox()
        self.model_dropdown.setMinimumWidth(300)
        self.model_dropdown.setObjectName("model_dropdown")  # For theme styling
        self.model_dropdown.addItem("No model loaded")
        self.model_dropdown.setEnabled(False)
        model_layout.addWidget(self.model_dropdown)
        
        model_layout.addStretch()
        
        # Load model button (compact)
        load_button = QPushButton("Load Model...")
        load_button.setObjectName("load_model_button")  # For theme styling
        load_button.clicked.connect(self._on_load_model)
        model_layout.addWidget(load_button)
        
        return model_widget
    

    

    
    def _create_menu_bar(self):
        """Create comprehensive menu bar structure."""
        # File menu
        file_menu = self.menuBar().addMenu("&File")
        
        # Model loading actions
        load_model_action = QAction("&Load Model...", self)
        load_model_action.setShortcut(QKeySequence.Open)
        load_model_action.triggered.connect(self._on_load_model)
        file_menu.addAction(load_model_action)
        
        # Recent models submenu
        self.recent_models_menu = QMenu("Recent Models", self)
        file_menu.addMenu(self.recent_models_menu)
        self._update_recent_models_menu()
        
        file_menu.addSeparator()
        
        # Document operations
        load_document_action = QAction("Load &Document...", self)
        load_document_action.triggered.connect(self._load_document)
        file_menu.addAction(load_document_action)
        
        save_summary_action = QAction("&Save Summary...", self)
        save_summary_action.triggered.connect(self._save_summary)
        file_menu.addAction(save_summary_action)
        
        file_menu.addSeparator()
        
        # Exit
        exit_action = QAction("E&xit", self)
        exit_action.setShortcut(QKeySequence.Quit)
        exit_action.triggered.connect(self.close)
        file_menu.addAction(exit_action)
        
        # Edit menu
        edit_menu = self.menuBar().addMenu("&Edit")
        
        # Standard edit actions
        copy_action = QAction("&Copy", self)
        copy_action.setShortcut(QKeySequence.Copy)
        copy_action.triggered.connect(self._copy_text)
        edit_menu.addAction(copy_action)
        
        paste_action = QAction("&Paste", self)
        paste_action.setShortcut(QKeySequence.Paste)
        paste_action.triggered.connect(self._paste_text)
        edit_menu.addAction(paste_action)
        
        edit_menu.addSeparator()
        
        # Preferences
        preferences_action = QAction("&Preferences...", self)
        preferences_action.triggered.connect(self._show_preferences)
        edit_menu.addAction(preferences_action)
        
        # Model menu
        model_menu = self.menuBar().addMenu("&Model")
        
        # Model parameters
        parameters_action = QAction("&Parameters...", self)
        parameters_action.triggered.connect(self._show_model_parameters)
        model_menu.addAction(parameters_action)
        
        # System prompts
        system_prompts_action = QAction("&System Prompts...", self)
        system_prompts_action.triggered.connect(self._show_system_prompts)
        model_menu.addAction(system_prompts_action)
        
        model_menu.addSeparator()
        
        # Model info
        model_info_action = QAction("Model &Info...", self)
        model_info_action.triggered.connect(self._show_model_info)
        model_menu.addAction(model_info_action)
        
        model_menu.addSeparator()
        
        # Unified model management
        model_manager_action = QAction("Model &Manager...", self)
        model_manager_action.triggered.connect(self._show_model_manager)
        model_menu.addAction(model_manager_action)
        
        # Loading statistics
        loading_stats_action = QAction("Loading &Statistics...", self)
        loading_stats_action.triggered.connect(self._show_loading_statistics)
        model_menu.addAction(loading_stats_action)
        
        # Export metrics
        export_metrics_action = QAction("&Export Metrics...", self)
        export_metrics_action.triggered.connect(self._export_metrics)
        model_menu.addAction(export_metrics_action)
        
        model_menu.addSeparator()
        
        # Clear cache
        clear_cache_action = QAction("&Clear Cache", self)
        clear_cache_action.triggered.connect(self._clear_model_cache)
        model_menu.addAction(clear_cache_action)
        
        # Email menu
        email_menu = self.menuBar().addMenu("&Email")
        
        # Email settings
        email_settings_action = QAction("&Settings...", self)
        email_settings_action.triggered.connect(self._show_email_settings)
        email_menu.addAction(email_settings_action)
        
        # View menu
        view_menu = self.menuBar().addMenu("&View")
        
        # Dark mode toggle
        self.dark_mode_action = QAction("🌙 Dark Mode", self)
        self.dark_mode_action.setCheckable(True)
        self.dark_mode_action.setChecked(self.theme_manager.is_dark_mode())
        self.dark_mode_action.triggered.connect(self._toggle_dark_mode)
        view_menu.addAction(self.dark_mode_action)
        
        # Help menu
        help_menu = self.menuBar().addMenu("&Help")
        
        # Documentation
        user_guide_action = QAction("&User Guide", self)
        user_guide_action.triggered.connect(self._show_user_guide)
        help_menu.addAction(user_guide_action)
        

        
        help_menu.addSeparator()
        
        # About
        about_action = QAction("&About", self)
        about_action.triggered.connect(self._show_about)
        help_menu.addAction(about_action)
    
    def _connect_events(self):
        """Connect event handlers."""
        self.event_bus.subscribe("model.loaded", self._on_model_loaded)
        self.event_bus.subscribe("model.unloaded", self._on_model_unloaded)
        self.event_bus.subscribe("model.error", self._on_model_error)
        self.event_bus.subscribe("model.loading.progress", self._on_loading_progress)
    
    def _connect_universal_loader_signals(self):
        """Connect universal loader signals."""
        self.universal_loader.loading_started.connect(self._on_universal_loading_started)
        self.universal_loader.progress_updated.connect(self._on_universal_progress_updated)
        self.universal_loader.loading_completed.connect(self._on_universal_loading_completed)
        self.universal_loader.loading_failed.connect(self._on_universal_loading_failed)
        self.universal_loader.format_detected.connect(self._on_universal_format_detected)
        self.universal_loader.backend_selected.connect(self._on_universal_backend_selected)
        self.universal_loader.memory_check_completed.connect(self._on_universal_memory_check)
        self.universal_loader.metadata_extracted.connect(self._on_universal_metadata_extracted)
    
    def _integrate_loading_monitor(self):
        """Integrate loading monitor with universal loader for comprehensive monitoring."""
        # Connect monitor signals for real-time feedback
        self.loading_monitor.metrics_updated.connect(self._on_loading_metrics_updated)
        self.loading_monitor.health_updated.connect(self._on_system_health_updated)
        self.loading_monitor.performance_alert.connect(self._on_performance_alert)
        
        # Set up monitoring session tracking
        self.current_monitoring_session = None
    
    def _connect_backend_manager_events(self):
        """Connect BackendManager events to UI update methods."""
        # Connect backend change events
        self.backend_manager.on_backend_changed = self._on_backend_manager_backend_changed
        
        # Connect fallback events
        self.backend_manager.on_fallback_triggered = self._on_backend_manager_fallback_triggered
        
        # Connect loading progress events
        self.backend_manager.on_loading_progress = self._on_backend_manager_loading_progress
        
        self.logger.info("BackendManager events connected to UI update methods")
    
    def _log_backend_manager_status(self):
        """Add logging to confirm BackendManager is ready for chat operations."""
        try:
            # Check if BackendManager is properly initialized
            if not hasattr(self, 'backend_manager') or self.backend_manager is None:
                self.logger.error("[ERROR] BackendManager not initialized - chat operations will fail")
                return
            
            # Get available backends
            available_backends = self.backend_manager.get_available_backends()
            
            # Log BackendManager status
            self.logger.info("[TOOL] BackendManager Status Check:")
            self.logger.info(f"   [OK] BackendManager initialized: {type(self.backend_manager).__name__}")
            self.logger.info(f"   [LIST] Available backends: {', '.join(available_backends) if available_backends else 'None'}")
            
            # Check hardware detection
            if hasattr(self.backend_manager, 'hardware_detector'):
                hardware_info = self.backend_manager.hardware_detector.get_hardware_info()
                self.logger.info(f"   [HARDWARE]  Hardware detected: {hardware_info.gpu_count} GPUs, {hardware_info.total_ram}MB RAM")
                if hardware_info.gpu_count > 0:
                    self.logger.info(f"   [GPU] GPU acceleration available: {hardware_info.total_vram}MB VRAM")
            
            # Check current model status
            if self.backend_manager.current_backend:
                backend_info = self.backend_manager.get_current_backend_info()
                backend_name = backend_info.get('name', 'unknown') if backend_info else 'unknown'
                self.logger.info(f"   [OK] Model loaded: {backend_name}")
                self.logger.info("   🎯 BackendManager ready for chat operations")
            else:
                self.logger.info("   [WAIT] No model loaded - load a model to enable chat operations")
            
            # Log performance optimization status
            if hasattr(self.backend_manager, 'performance_optimizer'):
                self.logger.info("   [PERF] Performance optimization enabled")
            
        except Exception as e:
            self.logger.error(f"[ERROR] Error checking BackendManager status: {e}")
            self.logger.error("   Chat operations may not work properly")
    
    def _setup_backend_bridge(self):
        """Set up bridge between new performance backend and old event system."""
        # Subscribe to chat/summary/email generation requests
        self.event_bus.subscribe("chat.send", self._on_chat_generation_request)
        self.event_bus.subscribe("summarization.text_async_request", self._on_summary_generation_request)
        self.event_bus.subscribe("summarization.file_async_request", self._on_file_summary_generation_request)
        self.event_bus.subscribe("email.generate", self._on_email_generation_request)
        self.event_bus.subscribe("chat.cancel", self._on_generation_cancel_request)
        self.event_bus.subscribe("summarization.cancel", self._on_summarization_cancel_request)
        self.event_bus.subscribe("summarization.cancel", self._on_generation_cancel_request)
        
        self.logger.info("Backend bridge established for chat/summary/email integration")
        self.event_bus.subscribe("model.loading.progress_message", self._on_loading_progress_message)
        self.event_bus.subscribe("model.loading.memory_usage", self._on_loading_memory_usage)
        self.event_bus.subscribe("model.loading.cancelled", self._on_loading_cancelled)
        self.event_bus.subscribe("summarization.completed", self._on_summarization_complete)
    
    def _load_window_state(self):
        """Load window state from configuration."""
        geometry = self.config_manager.get_value("window.geometry")
        if geometry:
            try:
                self.restoreGeometry(bytes.fromhex(geometry))
            except Exception as e:
                self.logger.warning(f"Failed to restore window geometry: {e}")
    
    def _save_window_state(self):
        """Save window state to configuration."""
        geometry = self.saveGeometry().toHex().data().decode()
        self.config_manager.set_value("window.geometry", geometry)
    
    def _update_recent_models_menu(self):
        """Update the recent models menu."""
        self.recent_models_menu.clear()
        
        recent_models = self.config_manager.get_value("recent_models", [])
        
        if not recent_models:
            no_recent_action = QAction("No Recent Models", self)
            no_recent_action.setEnabled(False)
            self.recent_models_menu.addAction(no_recent_action)
            return
        
        for model_path in recent_models:
            action = QAction(os.path.basename(model_path), self)
            action.setToolTip(model_path)
            action.triggered.connect(lambda checked, path=model_path: self._load_model(path))
            self.recent_models_menu.addAction(action)
        
        self.recent_models_menu.addSeparator()
        
        clear_action = QAction("Clear Recent Models", self)
        clear_action.triggered.connect(self._clear_recent_models)
        self.recent_models_menu.addAction(clear_action)
    
    # Event handlers
    def _on_load_model(self):
        """Handle load model action with universal loading support."""
        # Use universal model dialog for all formats
        dialog = UniversalModelDialog(self.universal_loader, self.config_manager, self)
        dialog.model_selected.connect(self._on_universal_model_selected)
        
        if dialog.exec() == QDialog.Accepted:
            # Model selection is handled by the signal
            pass
    
    def _load_model_optimized(self, file_path):
        """Load a model with performance optimization."""
        self.logger.info(f"Loading model with optimization: {file_path}")
        
        # Update status
        model_name = os.path.basename(file_path)
        self.status_bar.showMessage(f"Optimizing and loading model: {model_name}...")
        
        # Add to recent models
        self._add_to_recent_models(file_path)
        
        # Show progress dialog with optimization info
        self.loading_dialog = ModelLoadingDialog(model_name, self)
        self.loading_dialog.cancelled.connect(self._on_loading_cancel_requested)
        self.loading_dialog.show()
        
        # Update progress dialog with optimization status
        self.loading_dialog.update_progress_message("Analyzing hardware and optimizing configuration...")
        
        try:
            # Load model with performance optimization
            result = self.backend_manager.load_model_optimized(
                model_path=file_path,
                hardware_preference="auto",
                performance_target="balanced"
            )
            
            if result.success:
                # Update progress dialog with success info
                self.loading_dialog.update_progress_message(f"Model loaded successfully with {result.backend_used}!")
                self.loading_dialog.update_progress(100)
                
                # Log optimization details
                self.logger.info(f"[OK] Model loaded with optimization:")
                self.logger.info(f"   Backend: {result.backend_used}")
                self.logger.info(f"   Load time: {result.load_time:.1f}ms")
                self.logger.info(f"   Memory usage: {result.memory_usage}MB")
                
                # Get optimization details from model info
                model_info = result.model_info
                if model_info.get('optimization_applied'):
                    self.logger.info(f"   GPU layers: {model_info.get('gpu_layers_optimized', 'N/A')}")
                    self.logger.info(f"   Batch size: {model_info.get('batch_size_optimized', 'N/A')}")
                    self.logger.info(f"   Context size: {model_info.get('context_size_optimized', 'N/A')}")
                    self.logger.info(f"   Confidence: {model_info.get('recommendation_confidence', 0):.2%}")
                
                # Publish successful model load event
                self.event_bus.publish("model.loaded", result.backend_used, {
                    'name': model_name,
                    'path': file_path,
                    'backend': result.backend_used,
                    'optimization_applied': model_info.get('optimization_applied', False),
                    'load_time_ms': result.load_time,
                    'memory_usage_mb': result.memory_usage
                })
                
                # Log updated BackendManager status for chat operations
                self._log_backend_manager_status()
                
                # Update status with success
                self.status_bar.showMessage(f"[OK] Model loaded: {model_name} ({result.backend_used})")
                
            else:
                # Handle loading failure
                error_msg = result.error_message or 'Unknown error'
                self.logger.error(f"[ERROR] Model loading failed: {error_msg}")
                
                # Update progress dialog with error
                self.loading_dialog.update_progress_message(f"Loading failed: {error_msg}")
                
                # Show error dialog
                QMessageBox.critical(
                    self,
                    "Model Loading Failed",
                    f"Failed to load the model:\n\n{error_msg}\n\nThe performance optimization system tried multiple backends but none succeeded. Please check the troubleshooting guide for solutions."
                )
                
                # Publish error event
                self.event_bus.publish("model.error", error_msg)
                
                # Update status with error
                self.status_bar.showMessage(f"[ERROR] Failed to load model: {model_name}")
        
        except Exception as e:
            # Handle unexpected errors
            error_msg = f"Unexpected error during optimized model loading: {str(e)}"
            self.logger.error(error_msg)
            
            # Update progress dialog with error
            if self.loading_dialog:
                self.loading_dialog.update_progress_message(f"Error: {str(e)}")
            
            # Show error dialog
            QMessageBox.critical(
                self,
                "Model Loading Error",
                f"An unexpected error occurred:\n\n{str(e)}\n\nPlease check the logs for more details."
            )
            
            # Publish error event
            self.event_bus.publish("model.error", error_msg)
            
            # Update status with error
            self.status_bar.showMessage(f"[ERROR] Error loading model: {model_name}")
        
        finally:
            # Close loading dialog
            if self.loading_dialog:
                self.loading_dialog.close()
                self.loading_dialog = None
    
    def _load_model(self, file_path):
        """Legacy model loading method - redirects to optimized version."""
        self.logger.info("Redirecting to optimized model loading...")
        self._load_model_optimized(file_path)
    
    def get_performance_insights(self):
        """Get performance optimization insights for display in UI."""
        try:
            if hasattr(self, 'backend_manager'):
                return self.backend_manager.get_performance_insights()
            else:
                return {'error': 'Performance optimization not available'}
        except Exception as e:
            self.logger.error(f"Error getting performance insights: {e}")
            return {'error': f'Failed to get insights: {str(e)}'}
    
    def get_optimization_recommendations(self):
        """Get optimization recommendations for display in UI."""
        try:
            if hasattr(self, 'backend_manager'):
                # Use the correct method name from the performance integration
                if hasattr(self.backend_manager, 'get_performance_insights'):
                    insights = self.backend_manager.get_performance_insights()
                    # Extract recommendations from insights
                    recommendations = {
                        'current_setup': insights.get('current_model', {}),
                        'actionable_recommendations': [],
                        'hardware_info': insights.get('hardware_utilization', {})
                    }
                    
                    # Add some basic recommendations based on hardware
                    hardware_info = self.backend_manager.hardware_detector.get_hardware_info()
                    if hardware_info.gpu_count > 0 and hardware_info.total_vram > 8192:
                        recommendations['actionable_recommendations'].append(
                            "High-end GPU detected - performance optimization is active"
                        )
                    if hardware_info.total_ram > 32768:
                        recommendations['actionable_recommendations'].append(
                            "High RAM available - consider larger context sizes for better quality"
                        )
                    
                    return recommendations
                else:
                    return {'error': 'Performance insights not available'}
            else:
                return {'error': 'Performance optimization not available'}
        except Exception as e:
            self.logger.error(f"Error getting optimization recommendations: {e}")
            return {'error': f'Failed to get recommendations: {str(e)}'}
    
    def run_performance_benchmark(self):
        """Run performance benchmark and return results."""
        try:
            if hasattr(self, 'backend_manager') and self.backend_manager.current_backend:
                self.status_bar.showMessage("Running performance benchmark...")
                benchmark_results = self.backend_manager.run_comprehensive_benchmark(num_iterations=3)
                self.status_bar.showMessage("Performance benchmark completed")
                return benchmark_results
            else:
                return {'error': 'No model loaded for benchmarking'}
        except Exception as e:
            self.logger.error(f"Error running benchmark: {e}")
            self.status_bar.showMessage("Benchmark failed")
            return {'error': f'Benchmark failed: {str(e)}'}
    
    # Backend Status and Error Handling Methods
    
    def get_backend_manager_status(self) -> Dict[str, Any]:
        """Get comprehensive BackendManager status information."""
        try:
            if not hasattr(self, 'backend_manager') or self.backend_manager is None:
                return {
                    "status": "not_initialized",
                    "error": "BackendManager not initialized",
                    "available_backends": [],
                    "current_backend": None,
                    "model_loaded": False,
                    "hardware_info": None
                }
            
            # Get available backends
            available_backends = self.backend_manager.get_available_backends()
            
            # Get current backend info
            current_backend_info = None
            model_loaded = False
            if self.backend_manager.current_backend:
                current_backend_info = self.backend_manager.get_current_backend_info()
                model_loaded = True
            
            # Get hardware info if available
            hardware_info = None
            if hasattr(self.backend_manager, 'hardware_detector'):
                try:
                    hw_info = self.backend_manager.hardware_detector.get_hardware_info()
                    hardware_info = {
                        "gpu_count": hw_info.gpu_count,
                        "total_vram": hw_info.total_vram,
                        "cpu_cores": hw_info.cpu_cores,
                        "total_ram": hw_info.total_ram,
                        "recommended_backend": hw_info.recommended_backend
                    }
                except Exception as e:
                    self.logger.warning(f"Could not get hardware info: {e}")
            
            return {
                "status": "ready" if model_loaded else "no_model",
                "error": None,
                "available_backends": available_backends,
                "current_backend": current_backend_info,
                "model_loaded": model_loaded,
                "hardware_info": hardware_info,
                "backend_manager_type": type(self.backend_manager).__name__
            }
            
        except Exception as e:
            self.logger.error(f"Error getting BackendManager status: {e}")
            return {
                "status": "error",
                "error": str(e),
                "available_backends": [],
                "current_backend": None,
                "model_loaded": False,
                "hardware_info": None
            }
    
    def get_detailed_error_info(self, error: Exception, context: str = "") -> Dict[str, Any]:
        """Get detailed error information for better debugging."""
        backend_status = self.get_backend_manager_status()
        
        error_info = {
            "error_type": type(error).__name__,
            "error_message": str(error),
            "context": context,
            "timestamp": time.time(),
            "backend_status": backend_status["status"],
            "backend_error": backend_status.get("error"),
            "model_loaded": backend_status["model_loaded"],
            "available_backends": backend_status["available_backends"],
            "current_backend": backend_status.get("current_backend", {}).get("name", "none") if backend_status.get("current_backend") else "none"
        }
        
        # Add specific error categories
        if "model" in str(error).lower() or "backend" in str(error).lower():
            error_info["category"] = "backend_model_error"
            error_info["suggested_action"] = "Try reloading the model or selecting a different backend"
        elif "memory" in str(error).lower() or "cuda" in str(error).lower():
            error_info["category"] = "hardware_error"
            error_info["suggested_action"] = "Check GPU memory availability or try CPU backend"
        elif "generation" in str(error).lower() or "config" in str(error).lower():
            error_info["category"] = "generation_error"
            error_info["suggested_action"] = "Check generation parameters or try different settings"
        else:
            error_info["category"] = "general_error"
            error_info["suggested_action"] = "Check logs for more details"
        
        return error_info
    
    def check_chat_readiness(self) -> Tuple[bool, str]:
        """Check if chat functionality is ready and return status message."""
        status = self.get_backend_manager_status()
        
        if status["status"] == "not_initialized":
            return False, "BackendManager not initialized. Please restart the application."
        
        if status["status"] == "error":
            return False, f"BackendManager error: {status['error']}"
        
        if not status["available_backends"]:
            return False, "No backends available. Please check your installation."
        
        if not status["model_loaded"]:
            backends_list = ", ".join(status["available_backends"])
            return False, f"No model loaded. Please load a model first. Available backends: {backends_list}"
        
        backend_name = status.get("current_backend", {}).get("name", "unknown")
        return True, f"Chat ready with {backend_name} backend"
    
    def log_backend_operation(self, operation: str, success: bool, details: Dict[str, Any] = None):
        """Log backend operations for debugging purposes."""
        status = self.get_backend_manager_status()
        
        log_data = {
            "operation": operation,
            "success": success,
            "backend_status": status["status"],
            "current_backend": status.get("current_backend", {}).get("name", "none") if status.get("current_backend") else "none",
            "timestamp": time.time()
        }
        
        if details:
            log_data.update(details)
        
        if success:
            self.logger.info(f"[OK] Backend operation '{operation}' succeeded: {log_data}")
        else:
            self.logger.error(f"[ERROR] Backend operation '{operation}' failed: {log_data}")
    
    # Backend Bridge Methods for Chat/Summary/Email Integration
    
    def _on_chat_generation_request(self, data: Dict[str, Any]):
        """Handle chat generation request using BackendManager with proper GenerationConfig."""
        try:
            # Validate message content first
            message = data.get("message", "")
            if not message.strip():
                error_info = {
                    "message": "Empty message received. Please enter a message to send.",
                    "category": "validation_error",
                    "timestamp": time.time()
                }
                self.event_bus.publish("chat.error", error_info)
                self.logger.warning("Chat request failed: Empty message")
                return
            
            # Check chat readiness using enhanced status checking
            is_ready, status_message = self.check_chat_readiness()
            if not is_ready:
                error_info = {
                    "message": status_message,
                    "category": "backend_not_ready",
                    "backend_status": self.get_backend_manager_status(),
                    "timestamp": time.time()
                }
                self.event_bus.publish("chat.error", error_info)
                self.logger.error(f"Chat request failed: {status_message}")
                return
            
            self.logger.info(f"Processing chat request with BackendManager: {message[:50]}...")
            
            # Notify that generation is starting
            self.event_bus.publish("chat.generating", True)
            
            # Create proper GenerationConfig for BackendManager
            from llmtoolkit.app.core.model_backends import GenerationConfig
            
            # Extract generation parameters from request data or use defaults
            generation_params = data.get("generation_params", {})
            config = GenerationConfig(
                max_tokens=generation_params.get("max_tokens", 512),
                temperature=generation_params.get("temperature", 0.7),
                top_p=generation_params.get("top_p", 0.9),
                top_k=generation_params.get("top_k", 40),
                repeat_penalty=generation_params.get("repeat_penalty", 1.1),
                seed=generation_params.get("seed", -1),
                stop_sequences=generation_params.get("stop_sequences", []),
                stream=generation_params.get("stream", False)
            )
            
            self.logger.debug(f"Using generation config: max_tokens={config.max_tokens}, temperature={config.temperature}, top_p={config.top_p}")
            
            # Start async text generation to prevent UI freezing
            self._start_async_text_generation(message, config)
            
        except Exception as e:
            # Use enhanced error reporting
            error_info = self.get_detailed_error_info(e, "chat_generation")
            
            # Log the operation failure
            self.log_backend_operation("chat_generation", False, {
                "error": str(e),
                "message_length": len(message) if 'message' in locals() else 0
            })
            
            # Publish detailed error information
            self.event_bus.publish("chat.error", error_info)
    
    def _start_async_text_generation(self, message: str, config):
        """Start text generation in a background thread to prevent UI freezing."""
        from PySide6.QtCore import QThread, QObject, Signal, QTimer
        
        class TextGenerationWorker(QObject):
            """Worker for text generation in background thread."""
            finished = Signal(str)  # Generated text
            error = Signal(str)     # Error message
            
            def __init__(self, backend_manager, message, config, logger):
                super().__init__()
                self.backend_manager = backend_manager
                self.message = message
                self.config = config
                self.logger = logger
            
            def run(self):
                """Run text generation in background thread."""
                try:
                    self.logger.info(f"🔄 Starting text generation in background thread...")
                    
                    # Generate response using BackendManager's optimized generation
                    if hasattr(self.backend_manager, 'generate_text_optimized'):
                        # Use optimized generation if available (PerformanceIntegratedBackendManager)
                        # Disable batch processing for now as it returns placeholder responses
                        response = self.backend_manager.generate_text_optimized(
                            prompt=self.message,
                            config=self.config,
                            use_batch_processing=False
                        )
                    else:
                        # Fallback to standard generation method
                        response = self.backend_manager.generate_text(
                            prompt=self.message,
                            config=self.config
                        )
                    
                    self.logger.info(f"🎯 Text generation completed, response length: {len(response) if response else 0}")
                    
                    if response and response.strip():
                        self.finished.emit(response.strip())
                    else:
                        self.error.emit("Empty response generated by model")
                        
                except Exception as e:
                    self.logger.error(f"[ERROR] Text generation failed: {e}")
                    self.error.emit(str(e))
        
        # Stop any existing generation
        if hasattr(self, 'generation_thread') and self.generation_thread.isRunning():
            self.logger.info("⏹️ Stopping existing generation thread...")
            self.generation_thread.quit()
            self.generation_thread.wait(1000)  # Wait up to 1 second
        
        # Create worker and thread
        self.generation_thread = QThread()
        self.generation_worker = TextGenerationWorker(self.backend_manager, message, config, self.logger)
        
        # Move worker to thread
        self.generation_worker.moveToThread(self.generation_thread)
        
        # Connect signals
        self.generation_thread.started.connect(self.generation_worker.run)
        self.generation_worker.finished.connect(self._on_generation_finished)
        self.generation_worker.error.connect(self._on_generation_error)
        self.generation_worker.finished.connect(self.generation_thread.quit)
        self.generation_worker.error.connect(self.generation_thread.quit)
        self.generation_thread.finished.connect(self.generation_thread.deleteLater)
        
        # Add timeout to prevent infinite hanging (5 minutes)
        self.generation_timeout = QTimer()
        self.generation_timeout.setSingleShot(True)
        self.generation_timeout.timeout.connect(self._on_generation_timeout)
        self.generation_timeout.start(300000)  # 5 minutes timeout
        
        # Start the thread
        self.generation_thread.start()
        
        self.logger.info("[GPU] Started async text generation with 5-minute timeout to prevent UI freezing")
    
    def _on_generation_timeout(self):
        """Handle generation timeout."""
        self.logger.error("⏰ Text generation timed out after 5 minutes")
        
        # Stop the generation thread
        if hasattr(self, 'generation_thread') and self.generation_thread.isRunning():
            self.generation_thread.quit()
            self.generation_thread.wait(1000)
        
        # Publish timeout error
        error_info = {
            "message": "Text generation timed out after 5 minutes. The model may be too large or the prompt too complex.",
            "category": "timeout_error",
            "timestamp": time.time()
        }
        
        self.event_bus.publish("chat.error", error_info)
        self.event_bus.publish("chat.generating", False)
    
    def _on_generation_finished(self, response: str):
        """Handle successful text generation completion."""
        try:
            # Stop timeout timer
            if hasattr(self, 'generation_timeout'):
                self.generation_timeout.stop()
            
            # Reset generating state
            self.event_bus.publish("chat.generating", False)
            
            backend_name = self.backend_manager.current_backend.config.name if self.backend_manager.current_backend else "unknown"
            
            # Log successful operation
            self.log_backend_operation("chat_generation", True, {
                "response_length": len(response),
                "backend_used": backend_name,
            })
            
            # Publish successful response with metadata
            response_data = {
                "message": response,
                "backend_used": backend_name,
                "timestamp": time.time()
            }
            
            self.event_bus.publish("chat.response", response_data)
            self.logger.info(f"[OK] Chat generation completed successfully ({len(response)} chars)")
            
        except Exception as e:
            self.logger.error(f"[ERROR] Error handling generation completion: {e}")
            self._on_generation_error(str(e))
    
    def _on_generation_error(self, error_message: str):
        """Handle text generation error."""
        try:
            # Stop timeout timer
            if hasattr(self, 'generation_timeout'):
                self.generation_timeout.stop()
            
            # Reset generating state
            self.event_bus.publish("chat.generating", False)
            
            # Handle empty response with detailed error info
            backend_info = self.backend_manager.get_current_backend_info()
            backend_name = backend_info.get('name', 'unknown') if backend_info else 'unknown'
            
            error_info = {
                "message": f"Text generation failed: {error_message}",
                "category": "generation_error",
                "backend_used": backend_name,
                "backend_status": self.get_backend_manager_status(),
                "timestamp": time.time()
            }
            
            # Log the operation failure
            self.log_backend_operation("chat_generation", False, {
                "error": error_message,
                "backend_used": backend_name
            })
            
            self.event_bus.publish("chat.error", error_info)
            self.logger.error(f"[ERROR] Chat generation failed: {error_message}")
            
        except Exception as e:
            self.logger.error(f"[ERROR] Error handling generation error: {e}")
            
            # Fallback error handling
            self.event_bus.publish("chat.error", {
                "message": f"Critical error in chat generation: {str(e)}",
                "category": "critical_error",
                "timestamp": time.time()
            })
            self.event_bus.publish("chat.generating", False)
    

    
    def _on_summary_generation_request(self, data: Dict[str, Any]):
        """Handle text summary generation request using the new performance backend."""
        try:
            if not hasattr(self, 'backend_manager') or not self.backend_manager.current_backend:
                self.event_bus.publish("summarization.error", "No model loaded. Please load a model first.")
                return
            
            text_to_summarize = data.get("text", "")
            style = data.get("style", "concise")
            
            if not text_to_summarize.strip():
                self.event_bus.publish("summarization.error", "No text provided for summarization.")
                return
            
            self.logger.info(f"Processing text summary request: {len(text_to_summarize)} characters, style: {style}")
            
            # Notify that generation is starting
            self.event_bus.publish("summarization.generating")
            
            # Create style-specific summary prompt
            if style == "bullet_points":
                summary_prompt = f"Please provide a bullet-point summary of the following text:\n\n{text_to_summarize}\n\nBullet-point summary:"
            elif style == "detailed":
                summary_prompt = f"Please provide a detailed summary of the following text:\n\n{text_to_summarize}\n\nDetailed summary:"
            else:  # concise
                summary_prompt = f"Please provide a concise summary of the following text:\n\n{text_to_summarize}\n\nSummary:"
            
            # Use the performance-optimized backend for generation
            from llmtoolkit.app.core.model_backends import GenerationConfig
            config = GenerationConfig(
                max_tokens=400 if style == "detailed" else 256,
                temperature=0.3,  # Lower temperature for more focused summaries
                top_p=0.9,
                top_k=40
            )
            
            # Generate summary using optimized backend
            response = self.backend_manager.generate_text_optimized(
                prompt=summary_prompt,
                config=config,
                use_batch_processing=True
            )
            
            if response:
                self.logger.info(f"Text summary generated: {len(response)} characters")
                self.event_bus.publish("summarization.completed", response)
            else:
                self.event_bus.publish("summarization.error", "Failed to generate summary. Please try again.")
            
        except Exception as e:
            error_msg = f"Text summary generation error: {str(e)}"
            self.logger.error(error_msg)
            self.event_bus.publish("summarization.error", error_msg)
        finally:
            self.event_bus.publish("summarization.generating", False)
    
    def _on_file_summary_generation_request(self, data: Dict[str, Any]):
        """Handle file summary generation request using threaded processing and chunked summarization."""
        try:
            self.logger.info(f"File summary generation request received: {data}")
            
            # Validate backend availability
            if not hasattr(self, 'backend_manager') or not self.backend_manager:
                error_msg = "Backend manager not available. Please restart the application."
                self.logger.error(error_msg)
                self.event_bus.publish("summarization.error", error_msg)
                return
                
            if not self.backend_manager.current_backend:
                error_msg = "No model loaded. Please load a model first."
                self.logger.error(error_msg)
                self.event_bus.publish("summarization.error", error_msg)
                return
            
            # Extract and validate parameters
            file_path = data.get("file_path", "")
            style = data.get("style", "concise")
            
            if not file_path:
                error_msg = "No file path provided for summarization."
                self.logger.error(error_msg)
                self.event_bus.publish("summarization.error", error_msg)
                return
            
            self.logger.info(f"Processing file: {file_path}, style: {style}")
            
            # Notify that generation is starting
            self.event_bus.publish("summarization.generating")
            
            # Initialize threaded processing components
            if not hasattr(self, '_pdf_reader'):
                from llmtoolkit.app.core.threaded_pdf_reader import ThreadedPDFReader
                self._pdf_reader = ThreadedPDFReader()
            
            if not hasattr(self, '_chunked_summarizer'):
                from llmtoolkit.app.core.chunked_summarization import ChunkedSummarizationManager
                self._chunked_summarizer = ChunkedSummarizationManager()
                
                # Connect chunked summarizer signals
                self._chunked_summarizer.progress_updated.connect(
                    lambda progress, message: self.event_bus.publish("summarization.progress", message)
                )
                self._chunked_summarizer.summarization_completed.connect(
                    lambda summary: self.event_bus.publish("summarization.completed", summary)
                )
                self._chunked_summarizer.summarization_error.connect(
                    lambda error: self.event_bus.publish("summarization.error", error)
                )
            
            # Check if it's a PDF file that needs threaded extraction
            if file_path.lower().endswith('.pdf'):
                self._process_pdf_file(file_path, style)
            else:
                # Handle other file types with regular reading
                self._process_regular_file(file_path, style)
                
        except Exception as e:
            error_msg = f"File summary generation setup error: {str(e)}"
            self.logger.error(error_msg)
            self.event_bus.publish("summarization.error", error_msg)
            self.event_bus.publish("summarization.generating", False)
    
    def _process_pdf_file(self, file_path: str, style: str):
        """Process PDF file using threaded extraction and chunked summarization."""
        self.logger.info(f"Starting threaded PDF processing: {file_path}")
        
        def on_pdf_progress(progress: int, message: str):
            """Handle PDF extraction progress."""
            self.event_bus.publish("summarization.progress", f"PDF: {message}")
        
        def on_pdf_page_processed(page_num: int, total_pages: int, preview: str):
            """Handle PDF page processing."""
            self.event_bus.publish("summarization.progress", 
                                 f"PDF: Processed page {page_num}/{total_pages}")
        
        def on_pdf_success(extracted_text: str):
            """Handle successful PDF extraction."""
            self.logger.info(f"PDF extraction completed: {len(extracted_text)} characters")
            
            # Start chunked summarization
            self.event_bus.publish("summarization.progress", "Starting intelligent summarization...")
            
            success = self._chunked_summarizer.start_summarization(
                extracted_text, style, self.backend_manager
            )
            
            if not success:
                self.event_bus.publish("summarization.error", "Failed to start chunked summarization")
                self.event_bus.publish("summarization.generating", False)
        
        def on_pdf_error(error_message: str):
            """Handle PDF extraction error."""
            self.logger.error(f"PDF extraction failed: {error_message}")
            self.event_bus.publish("summarization.error", f"PDF extraction failed: {error_message}")
            self.event_bus.publish("summarization.generating", False)
        
        # Start threaded PDF extraction
        success = self._pdf_reader.start_extraction(
            file_path,
            progress_callback=on_pdf_progress,
            page_callback=on_pdf_page_processed,
            success_callback=on_pdf_success,
            error_callback=on_pdf_error
        )
        
        if not success:
            self.event_bus.publish("summarization.error", "Failed to start PDF extraction")
            self.event_bus.publish("summarization.generating", False)
    
    def _process_regular_file(self, file_path: str, style: str):
        """Process regular (non-PDF) files with chunked summarization."""
        try:
            self.event_bus.publish("summarization.progress", "Reading file content...")
            
            # Read file content synchronously (these are usually smaller files)
            file_content = self._read_file_content(file_path)
            
            if not file_content or not file_content.strip():
                self.event_bus.publish("summarization.error", "File is empty or could not be read.")
                self.event_bus.publish("summarization.generating", False)
                return
            
            self.logger.info(f"File content read: {len(file_content)} characters")
            
            # Start chunked summarization
            self.event_bus.publish("summarization.progress", "Starting intelligent summarization...")
            
            success = self._chunked_summarizer.start_summarization(
                file_content, style, self.backend_manager
            )
            
            if not success:
                self.event_bus.publish("summarization.error", "Failed to start chunked summarization")
                self.event_bus.publish("summarization.generating", False)
                
        except Exception as e:
            error_msg = f"Failed to read file: {str(e)}"
            self.logger.error(error_msg)
            self.event_bus.publish("summarization.error", error_msg)
            self.event_bus.publish("summarization.generating", False)
    
    def _on_email_generation_request(self, data: Dict[str, Any]):
        """Handle email generation request using the new performance backend."""
        try:
            if not hasattr(self, 'backend_manager') or not self.backend_manager.current_backend:
                self.event_bus.publish("email.error", "No model loaded. Please load a model first.")
                return
            
            email_prompt = data.get("prompt", "")
            email_type = data.get("type", "general")
            
            if not email_prompt.strip():
                self.event_bus.publish("email.error", "No email prompt provided.")
                return
            
            self.logger.info(f"Processing email generation request: {email_type}")
            
            # Notify that generation is starting
            self.event_bus.publish("email.generating", True)
            
            # Create email-specific prompt based on type
            if email_type == "marketing":
                full_prompt = f"Write a professional marketing email about: {email_prompt}\n\nEmail:"
            elif email_type == "response":
                full_prompt = f"Write a professional email response to: {email_prompt}\n\nEmail:"
            else:
                full_prompt = f"Write a professional email about: {email_prompt}\n\nEmail:"
            
            # Use the performance-optimized backend for generation
            from llmtoolkit.app.core.model_backends import GenerationConfig
            config = GenerationConfig(
                max_tokens=400,  # Good length for emails
                temperature=0.5,  # Balanced creativity for professional emails
                top_p=0.9,
                top_k=40
            )
            
            # Generate email using optimized backend
            response = self.backend_manager.generate_text_optimized(
                prompt=full_prompt,
                config=config,
                use_batch_processing=True
            )
            
            if response:
                self.logger.info(f"Email generated: {len(response)} characters")
                self.event_bus.publish("email.response", response)
            else:
                self.event_bus.publish("email.error", "Failed to generate email. Please try again.")
            
        except Exception as e:
            error_msg = f"Email generation error: {str(e)}"
            self.logger.error(error_msg)
            self.event_bus.publish("email.error", error_msg)
        finally:
            self.event_bus.publish("email.generating", False)
    
    def _on_generation_cancel_request(self, data: Any):
        """Handle generation cancellation request."""
        try:
            self.logger.info("Generation cancellation requested")
            # For now, we'll just publish the cancelled events
            # In a full implementation, we would interrupt the generation process
            self.event_bus.publish("chat.cancelled", True)
            self.event_bus.publish("summary.cancelled", True)
            self.event_bus.publish("email.cancelled", True)
            self.event_bus.publish("chat.generating", False)
            self.event_bus.publish("summary.generating", False)
            self.event_bus.publish("email.generating", False)
        except Exception as e:
            self.logger.error(f"Error handling cancellation: {e}")
    
    def _on_summarization_cancel_request(self, data: Any):
        """Handle summarization cancellation request."""
        try:
            self.logger.info("Summarization cancellation requested")
            
            # Stop PDF reader if running
            if hasattr(self, '_pdf_reader') and self._pdf_reader.is_extracting():
                self.logger.info("Stopping PDF extraction...")
                self._pdf_reader.stop_extraction()
            
            # Stop chunked summarizer if running
            if hasattr(self, '_chunked_summarizer'):
                self.logger.info("Stopping chunked summarization...")
                self._chunked_summarizer.stop_summarization()
            
            # Publish cancellation complete
            self.event_bus.publish("summarization.cancelled")
            self.event_bus.publish("summarization.generating", False)
            
            self.logger.info("Summarization cancellation completed")
            
        except Exception as e:
            self.logger.error(f"Error handling summarization cancellation: {e}")
            # Ensure we still clear the generating state
            self.event_bus.publish("summarization.generating", False)
    
    def _read_file_content(self, file_path: str) -> str:
        """
        Read file content with support for different file types.
        
        Args:
            file_path: Path to the file to read
            
        Returns:
            File content as text
            
        Raises:
            Exception: If file cannot be read or format is unsupported
        """
        file_extension = Path(file_path).suffix.lower()
        
        try:
            if file_extension == '.pdf':
                # Handle PDF files
                return self._read_pdf_content(file_path)
            elif file_extension in ['.docx', '.doc']:
                # Handle Word documents
                return self._read_word_content(file_path)
            elif file_extension in ['.txt', '.md', '.py', '.js', '.html', '.css', '.json', '.xml', '.csv']:
                # Handle text-based files
                return self._read_text_content(file_path)
            else:
                # Try to read as text with multiple encodings
                return self._read_text_content_with_fallback(file_path)
                
        except Exception as e:
            raise Exception(f"Unsupported file type '{file_extension}' or read error: {str(e)}")
    
    def _read_pdf_content(self, file_path: str) -> str:
        """Read content from PDF file with enhanced error handling and progress reporting."""
        self.logger.info(f"Starting PDF content extraction from: {file_path}")
        
        try:
            # Check if file exists and is readable
            if not os.path.exists(file_path):
                raise Exception(f"PDF file does not exist: {file_path}")
            
            if not os.access(file_path, os.R_OK):
                raise Exception(f"PDF file is not readable: {file_path}")
            
            file_size = os.path.getsize(file_path)
            self.logger.info(f"PDF file size: {file_size} bytes")
            
            if file_size == 0:
                raise Exception("PDF file is empty")
            
            # Try pdfplumber first (generally better text extraction)
            try:
                self.logger.info("Attempting PDF extraction with pdfplumber...")
                import pdfplumber
                
                text = ""
                with pdfplumber.open(file_path) as pdf:
                    total_pages = len(pdf.pages)
                    self.logger.info(f"PDF has {total_pages} pages")
                    
                    for i, page in enumerate(pdf.pages):
                        self.logger.debug(f"Extracting text from page {i+1}/{total_pages}")
                        page_text = page.extract_text()
                        if page_text:
                            text += page_text + "\n"
                        
                        # Report progress for large PDFs
                        if i % 10 == 0 and i > 0:
                            self.logger.info(f"Processed {i+1}/{total_pages} pages...")
                
                if text.strip():
                    self.logger.info(f"pdfplumber extracted {len(text)} characters successfully")
                    return text.strip()
                else:
                    self.logger.warning("pdfplumber extracted empty text, trying PyPDF2...")
                    
            except ImportError:
                self.logger.info("pdfplumber not available, trying PyPDF2...")
            except Exception as e:
                self.logger.warning(f"pdfplumber extraction failed: {e}, trying PyPDF2...")
            
            # Fallback to PyPDF2
            try:
                self.logger.info("Attempting PDF extraction with PyPDF2...")
                import PyPDF2
                
                text = ""
                with open(file_path, 'rb') as file:
                    pdf_reader = PyPDF2.PdfReader(file)
                    total_pages = len(pdf_reader.pages)
                    self.logger.info(f"PDF has {total_pages} pages")
                    
                    for i, page in enumerate(pdf_reader.pages):
                        self.logger.debug(f"Extracting text from page {i+1}/{total_pages}")
                        page_text = page.extract_text()
                        if page_text:
                            text += page_text + "\n"
                        
                        # Report progress for large PDFs
                        if i % 10 == 0 and i > 0:
                            self.logger.info(f"Processed {i+1}/{total_pages} pages...")
                
                if text.strip():
                    self.logger.info(f"PyPDF2 extracted {len(text)} characters successfully")
                    return text.strip()
                else:
                    raise Exception("PDF appears to contain no extractable text (may be image-based)")
                    
            except ImportError:
                raise Exception("PDF reading requires PyPDF2 or pdfplumber. Install with: pip install PyPDF2 pdfplumber")
            except Exception as e:
                if "no extractable text" in str(e):
                    raise e
                else:
                    raise Exception(f"PyPDF2 extraction failed: {str(e)}")
                    
        except Exception as e:
            error_msg = f"Failed to read PDF '{os.path.basename(file_path)}': {str(e)}"
            self.logger.error(error_msg)
            raise Exception(error_msg)
    
    def _read_word_content(self, file_path: str) -> str:
        """Read content from Word document."""
        try:
            import docx
            doc = docx.Document(file_path)
            text = ""
            for paragraph in doc.paragraphs:
                text += paragraph.text + "\n"
            return text
        except ImportError:
            raise Exception("Word document reading requires python-docx. Install with: pip install python-docx")
        except Exception as e:
            raise Exception(f"Failed to read Word document: {str(e)}")
    
    def _read_text_content(self, file_path: str) -> str:
        """Read content from text file with UTF-8 encoding."""
        with open(file_path, 'r', encoding='utf-8') as f:
            return f.read()
    
    def _read_text_content_with_fallback(self, file_path: str) -> str:
        """Read text content with multiple encoding fallbacks."""
        encodings = ['utf-8', 'utf-16', 'latin-1', 'cp1252', 'iso-8859-1']
        
        for encoding in encodings:
            try:
                with open(file_path, 'r', encoding=encoding) as f:
                    content = f.read()
                    self.logger.info(f"Successfully read file with {encoding} encoding")
                    return content
            except UnicodeDecodeError:
                continue
            except Exception as e:
                raise Exception(f"Failed to read file: {str(e)}")
        
        raise Exception(f"Could not read file with any of the supported encodings: {encodings}")
    
    def _add_to_recent_models(self, file_path):
        """Add a model to the recent models list."""
        recent_models = self.config_manager.get_value("recent_models", [])
        
        if file_path in recent_models:
            recent_models.remove(file_path)
        
        recent_models.insert(0, file_path)
        recent_models = recent_models[:10]  # Keep only 10 recent models
        
        self.config_manager.set_value("recent_models", recent_models)
        self._update_recent_models_menu()
    
    def _clear_recent_models(self):
        """Clear the recent models list."""
        self.config_manager.set_value("recent_models", [])
        self._update_recent_models_menu()
    
    def _on_model_loaded(self, model_id, model_info):
        """Handle model loaded event."""
        model_name = model_info.get('name', 'Unnamed Model')
        
        # Update dropdown
        self.model_dropdown.clear()
        self.model_dropdown.addItem(model_name)
        self.model_dropdown.setEnabled(True)
        
        # Update window title
        self.setWindowTitle(f"LLM Toolkit - {model_name}")
        
        # Update status
        self.status_bar.showMessage(f"Model loaded: {model_name}")
        
        # Close loading dialog if it exists
        if self.loading_dialog:
            self.loading_dialog.on_loading_finished()
            self.loading_dialog = None
        
        self.logger.info(f"Model loaded: {model_id}")
    
    def _on_model_unloaded(self, model_id):
        """Handle model unloaded event."""
        # Update dropdown
        self.model_dropdown.clear()
        self.model_dropdown.addItem("No model loaded")
        self.model_dropdown.setEnabled(False)
        
        # Update window title
        self.setWindowTitle("LLM Toolkit")
        
        # Update status
        self.status_bar.showMessage("Model unloaded")
        
        self.logger.info(f"Model unloaded: {model_id}")
    
    def _on_model_error(self, error_message):
        """Handle model loading error."""
        self.status_bar.showMessage("Model loading failed")
        
        QMessageBox.critical(
            self,
            "Model Loading Error",
            f"Failed to load the model:\n\n{error_message}"
        )
        
        self.logger.error(f"Model loading error: {error_message}")
        
        # Close loading dialog if it exists
        if self.loading_dialog:
            self.loading_dialog.on_loading_error(error_message)
    
    def _on_loading_progress(self, percentage):
        """Handle loading progress update."""
        if self.loading_dialog:
            self.loading_dialog.update_progress(percentage)
    
    def _on_loading_progress_message(self, message):
        """Handle loading progress message update."""
        if self.loading_dialog:
            self.loading_dialog.update_progress_message(message)
    
    def _on_loading_memory_usage(self, memory_mb):
        """Handle loading memory usage update."""
        if self.loading_dialog:
            self.loading_dialog.update_memory_usage(memory_mb)
    
    def _on_loading_cancelled(self):
        """Handle loading cancellation."""
        if self.loading_dialog:
            self.loading_dialog.on_loading_cancelled()
        
        self.status_bar.showMessage("Model loading cancelled")
        self.logger.info("Model loading was cancelled")
    
    def _on_loading_cancel_requested(self):
        """Handle user request to cancel loading."""
        self.event_bus.publish("model.load.cancel", {})
        self.logger.info("User requested to cancel model loading")
    
    def _on_backend_manager_backend_changed(self, old_backend: str, new_backend: str):
        """Handle BackendManager backend change event."""
        self.logger.info(f"🔄 BackendManager backend changed: {old_backend} → {new_backend}")
        
        # Update UI to reflect backend change
        self.status_bar.showMessage(f"Backend changed to: {new_backend}")
        
        # Update model dropdown if needed
        if new_backend and hasattr(self.backend_manager, 'current_model_path'):
            model_path = self.backend_manager.current_model_path
            if model_path:
                model_name = os.path.basename(model_path)
                self.model_dropdown.clear()
                self.model_dropdown.addItem(f"{model_name} ({new_backend})")
                self.model_dropdown.setEnabled(True)
        
        # Log chat readiness status
        if new_backend:
            self.logger.info("[OK] BackendManager ready for chat operations with new backend")
        else:
            self.logger.info("[WARN]  No backend loaded - chat operations disabled")
    
    def _on_backend_manager_fallback_triggered(self, failed_backend: str, fallback_backend: str, reason: str):
        """Handle BackendManager fallback event."""
        self.logger.warning(f"🔄 BackendManager fallback triggered:")
        self.logger.warning(f"   Failed backend: {failed_backend}")
        self.logger.warning(f"   Fallback backend: {fallback_backend}")
        self.logger.warning(f"   Reason: {reason}")
        
        # Update status bar with fallback information
        self.status_bar.showMessage(f"Fallback: {failed_backend} → {fallback_backend}")
        
        # Show user notification about fallback
        if hasattr(self, 'main_tabs') and self.main_tabs:
            # Could show a temporary notification in the UI
            pass
        
        # Log impact on chat operations
        if fallback_backend:
            self.logger.info("[OK] Chat operations continue with fallback backend")
        else:
            self.logger.warning("[WARN]  No fallback available - chat operations may fail")
    
    def _on_backend_manager_loading_progress(self, message: str, percentage: int):
        """Handle BackendManager loading progress event."""
        self.logger.debug(f"BackendManager loading progress: {message} ({percentage}%)")
        
        # Update loading dialog if present
        if self.loading_dialog:
            self.loading_dialog.update_progress_message(f"BackendManager: {message}")
            self.loading_dialog.update_progress(percentage)
        
        # Update status bar
        if percentage < 100:
            self.status_bar.showMessage(f"Loading: {message} ({percentage}%)")
        else:
            self.status_bar.showMessage("Model loaded successfully")
            self.logger.info("[OK] BackendManager model loading completed - chat operations ready")
    
    def _on_summarization_complete(self, summary):
        """Handle summarization completion."""
        # This is handled by the SummarizationTab component
        pass
    
    # Menu action handlers (placeholder implementations)
    def _load_document(self):
        """Load document from file."""
        # Switch to summarization tab and trigger its load document functionality
        self.main_tabs.setCurrentWidget(self.summarization_tab)
        self.summarization_tab._load_document_file()
    
    def _save_summary(self):
        """Save summary to file."""
        # Switch to summarization tab and trigger its save summary functionality
        self.main_tabs.setCurrentWidget(self.summarization_tab)
        self.summarization_tab._save_summary()
    
    def _copy_text(self):
        """Copy selected text."""
        focused_widget = self.focusWidget()
        if hasattr(focused_widget, 'copy'):
            focused_widget.copy()
    
    def _paste_text(self):
        """Paste text."""
        focused_widget = self.focusWidget()
        if hasattr(focused_widget, 'paste'):
            focused_widget.paste()
    
    def _show_preferences(self):
        """Show preferences dialog."""
        try:
            dialog = PreferencesDialog(self.config_manager, self)
            dialog.exec()
        except Exception as e:
            QMessageBox.information(self, "Preferences", "Preferences dialog not yet implemented.")
    
    def _show_model_parameters(self):
        """Show model parameters dialog."""
        try:
            # Load current parameters
            current_params = self.config_manager.get_value("model_parameters", {})
            
            # Create and show dialog
            dialog = ModelParametersDialog(self.config_manager, current_params, self)
            dialog.parameters_changed.connect(self._on_model_parameters_changed)
            
            if dialog.exec() == QDialog.Accepted:
                self.logger.info("Model parameters updated")
        except Exception as e:
            self.logger.error(f"Error showing model parameters dialog: {e}")
            QMessageBox.critical(self, "Error", f"Failed to open model parameters dialog:\n{str(e)}")
    
    def _show_system_prompts(self):
        """Show system prompts dialog."""
        try:
            # Load current system prompt
            current_prompt = self.config_manager.get_value("system_prompt", "")
            
            # Create and show dialog
            dialog = SystemPromptsDialog(self.config_manager, current_prompt, self)
            dialog.system_prompt_changed.connect(self._on_system_prompt_changed)
            
            if dialog.exec() == QDialog.Accepted:
                self.logger.info("System prompt updated")
        except Exception as e:
            self.logger.error(f"Error showing system prompts dialog: {e}")
            QMessageBox.critical(self, "Error", f"Failed to open system prompts dialog:\n{str(e)}")
    
    def _show_model_info(self):
        """Show model information dialog."""
        if self.model_dropdown.currentText() == "No model loaded":
            QMessageBox.warning(
                self,
                "No Model Loaded",
                "Please load a GGUF model first to view information."
            )
            return
        
        # Placeholder for model info dialog
        QMessageBox.information(
            self, 
            "Model Information", 
            f"Model: {self.model_dropdown.currentText()}\n\n"
            "• Architecture: GGUF\n"
            "• Parameters: Loading...\n"
            "• Quantization: Loading...\n"
            "• Memory Usage: Loading...\n\n"
            "Full model information dialog coming soon..."
        )
    

    
    def _show_user_guide(self):
        """Show user guide."""
        QMessageBox.information(self, "User Guide", "User guide not yet implemented.")
    

    
    def _show_email_settings(self):
        """Show email settings dialog."""
        try:
            # Load current email configuration from EmailService
            current_config = self.email_service.get_email_config()
            
            # Create and show dialog
            dialog = EmailSettingsDialog(self, current_config)
            dialog.settings_saved.connect(self._on_email_settings_saved)
            
            # Connect OAuth authentication signal
            dialog.oauth_authentication_requested.connect(self._handle_oauth_authentication)
            
            # IMPORTANT: Monkey patch the update_oauth_status method to always enable the Save button
            original_update_oauth_status = dialog.update_oauth_status
            
            def patched_update_oauth_status(success, message, email=""):
                # Call the original method
                original_update_oauth_status(success, message, email)
                
                # Always enable the Save button if authentication was successful
                if success:
                    self.logger.info("OAuth authentication successful, forcing Save button to be enabled")
                    dialog.save_button.setEnabled(True)
                    
                    # Update the status label
                    current_text = dialog.oauth_status_label.text()
                    if "Save button enabled" not in current_text:
                        dialog.oauth_status_label.setText(f"{current_text} - Save button enabled")
            
            # Apply the monkey patch
            dialog.update_oauth_status = patched_update_oauth_status
            
            if dialog.exec() == QDialog.Accepted:
                self.logger.info("Email settings updated")
        except Exception as e:
            self.logger.error(f"Error showing email settings dialog: {e}")
            QMessageBox.critical(self, "Error", f"Failed to open email settings dialog:\n{str(e)}")
    
    def _show_about(self):
        """Show about dialog."""
        dialog = AboutDialog(self)
        dialog.exec()
    
    def _toggle_dark_mode(self):
        """Toggle dark mode on/off."""
        self.theme_manager.toggle_theme()
        self.dark_mode_action.setChecked(self.theme_manager.is_dark_mode())
        
        # Update action text
        if self.theme_manager.is_dark_mode():
            self.dark_mode_action.setText("☀️ Light Mode")
        else:
            self.dark_mode_action.setText("🌙 Dark Mode")
        
        self.logger.info(f"Theme toggled to: {'dark' if self.theme_manager.is_dark_mode() else 'light'}")
    
    def _on_system_prompt_changed(self, new_prompt: str):
        """Handle system prompt change."""
        self.current_system_prompt = new_prompt
        self.logger.info(f"System prompt updated: {new_prompt[:50]}...")
        
        # Notify chat service about the new system prompt
        self.event_bus.publish("system_prompt.changed", {
            "prompt": new_prompt
        })
    
    def _on_model_parameters_changed(self, new_parameters: dict):
        """Handle model parameters change."""
        self.current_model_parameters = new_parameters
        self.logger.info(f"Model parameters updated: {new_parameters}")
        
        # Notify services about the new parameters
        self.event_bus.publish("model_parameters.changed", {
            "parameters": new_parameters
        })
    
    def _on_email_settings_saved(self, email_config: dict):
        """Handle email settings save and refresh email automation tab."""
        # Save email configuration through EmailService
        success, message = self.email_service.save_email_config(email_config)
        
        if success:
            self.logger.info("Email configuration saved successfully")
            
            # Refresh the email automation tab to reflect new OAuth status
            if hasattr(self, 'email_automation_tab'):
                self.logger.info("Refreshing email automation tab after settings save")
                try:
                    # Force refresh the email automation tab
                    self.email_automation_tab._complete_email_refresh()
                    self.logger.info("Email automation tab refreshed successfully")
                except Exception as e:
                    self.logger.error(f"Error refreshing email automation tab: {e}")
            
            # Show success message to user
            QMessageBox.information(self, "Settings Saved", "Email settings have been saved successfully.\n\nThe email automation tab has been updated.")
        else:
            self.logger.error(f"Failed to save email configuration: {message}")
            # Show error message to user
            QMessageBox.critical(self, "Save Failed", f"Failed to save email settings: {message}\n\nPlease check your configuration and try again.")
    
    def _handle_oauth_authentication(self, credentials_path: str):
        """
        Handle OAuth authentication request from email settings dialog.
        
        Args:
            credentials_path: Path to the credentials.json file
        """
        try:
            self.logger.info(f"Handling OAuth authentication request with credentials: {credentials_path}")
            
            # Get the email settings dialog that requested authentication
            dialog = self.sender().parent()
            
            # Authenticate using the email service
            success, message = self.email_service.authenticate_gmail_oauth(credentials_path)
            
            # Close the loading dialog if it exists
            if hasattr(dialog, 'close_oauth_loading_dialog'):
                dialog.close_oauth_loading_dialog()
            
            # Update the dialog with authentication result
            if success:
                # Get the authenticated email from the email service
                email_config = self.email_service.get_email_config()
                oauth_email = email_config.get('oauth_email', '')
                
                # Update the dialog's OAuth status
                dialog.update_oauth_status(True, "Authentication successful", oauth_email)
                self.logger.info(f"OAuth authentication successful for {oauth_email}")
                
                # DIRECT FIX: Always force enable the Save button after successful authentication
                from llmtoolkit.app.ui.force_enable_save_button import force_enable_save_button
                force_enable_save_button(dialog)
                self.logger.info("Force enabled Save button after successful authentication")
            else:
                dialog.update_oauth_status(False, message)
                self.logger.error(f"OAuth authentication failed: {message}")
                
        except Exception as e:
            self.logger.error(f"Error during OAuth authentication: {e}")
            
            # Update dialog with error if possible
            try:
                dialog = self.sender().parent()
                dialog.update_oauth_status(False, f"Authentication error: {str(e)}")
                
                # Close the loading dialog if it exists
                if hasattr(dialog, 'close_oauth_loading_dialog'):
                    dialog.close_oauth_loading_dialog()
            except:
                pass
    
    def _on_load_model(self):
        """Handle load model button click - show universal model dialog."""
        try:
            self.logger.info("Opening universal model selection dialog")
            
            # Create and show universal model dialog
            dialog = UniversalModelDialog(
                self.universal_loader,
                self.config_manager,
                self
            )
            
            # Connect dialog signals
            dialog.model_selected.connect(self._on_universal_model_selected)
            
            # Show dialog
            if dialog.exec() == QDialog.Accepted:
                self.logger.info("Model selection dialog completed successfully")
            else:
                self.logger.info("Model selection dialog cancelled by user")
                
        except Exception as e:
            self.logger.error(f"Error opening model selection dialog: {e}")
            QMessageBox.critical(
                self,
                "Error",
                f"Failed to open model selection dialog:\n{str(e)}"
            )
    
    def _on_universal_model_selected(self, model_path: str, format_type: ModelFormat):
        """Handle model selection from universal dialog."""
        self.logger.info(f"Model selected: {model_path} (format: {format_type.value})")
        self._load_model_universal(model_path, format_type)
    
    def _save_window_state(self):
        """Save window state to configuration."""
        try:
            # Save window geometry and state
            self.config_manager.set('ui.window_geometry', self.saveGeometry())
            self.config_manager.set('ui.window_state', self.saveState())
            
            # Save current tab
            if hasattr(self, 'tab_widget'):
                self.config_manager.set('ui.current_tab', self.tab_widget.currentIndex())
            
            self.logger.debug("Window state saved")
        except Exception as e:
            self.logger.warning(f"Failed to save window state: {e}")
    
    def _add_to_recent_models(self, model_path: str):
        """Add model to recent models list."""
        try:
            # Get current recent models
            recent_models = self.config_manager.get('ui.recent_models', [])
            
            # Remove if already exists
            recent_models = [m for m in recent_models if m.get('path') != model_path]
            
            # Add to beginning
            recent_models.insert(0, {
                'path': model_path,
                'name': Path(model_path).name,
                'last_used': time.strftime('%Y-%m-%d %H:%M:%S')
            })
            
            # Keep only last 10
            recent_models = recent_models[:10]
            
            # Save back to config
            self.config_manager.set('ui.recent_models', recent_models)
            
            # Update recent models menu
            self._update_recent_models_menu()
            
            self.logger.debug(f"Added to recent models: {model_path}")
        except Exception as e:
            self.logger.warning(f"Failed to add to recent models: {e}")
    
    def _update_recent_models_menu(self):
        """Update the recent models menu."""
        try:
            if not hasattr(self, 'recent_models_menu'):
                return
            
            # Clear existing actions
            self.recent_models_menu.clear()
            
            # Get recent models
            recent_models = self.config_manager.get('ui.recent_models', [])
            
            if not recent_models:
                # Add disabled "No recent models" action
                no_recent_action = QAction("No recent models", self)
                no_recent_action.setEnabled(False)
                self.recent_models_menu.addAction(no_recent_action)
            else:
                # Add recent model actions
                for model_info in recent_models:
                    model_path = model_info.get('path', '')
                    model_name = model_info.get('name', Path(model_path).name)
                    last_used = model_info.get('last_used', '')
                    
                    action_text = f"{model_name}"
                    if last_used:
                        action_text += f" ({last_used})"
                    
                    action = QAction(action_text, self)
                    action.setData(model_path)  # Store path in action data
                    action.triggered.connect(lambda checked, path=model_path: self._load_recent_model(path))
                    self.recent_models_menu.addAction(action)
                
                # Add separator and clear action
                self.recent_models_menu.addSeparator()
                clear_action = QAction("Clear Recent Models", self)
                clear_action.triggered.connect(self._clear_recent_models)
                self.recent_models_menu.addAction(clear_action)
                
        except Exception as e:
            self.logger.warning(f"Failed to update recent models menu: {e}")
    
    def _load_recent_model(self, model_path: str):
        """Load a model from recent models list."""
        try:
            if os.path.exists(model_path):
                # Detect format and load
                result = self.universal_loader.format_detector.detect_format(model_path)
                if result.format_type != ModelFormat.UNKNOWN:
                    self._load_model_universal(model_path, result.format_type)
                else:
                    QMessageBox.warning(
                        self,
                        "Invalid Model",
                        f"Could not determine format of model:\n{model_path}"
                    )
            else:
                QMessageBox.warning(
                    self,
                    "Model Not Found",
                    f"Model file no longer exists:\n{model_path}\n\nRemoving from recent models."
                )
                # Remove from recent models
                recent_models = self.config_manager.get('ui.recent_models', [])
                recent_models = [m for m in recent_models if m.get('path') != model_path]
                self.config_manager.set('ui.recent_models', recent_models)
                self._update_recent_models_menu()
        except Exception as e:
            self.logger.error(f"Failed to load recent model: {e}")
            QMessageBox.critical(
                self,
                "Error",
                f"Failed to load model:\n{str(e)}"
            )
    
    def _clear_recent_models(self):
        """Clear recent models list."""
        try:
            self.config_manager.set('ui.recent_models', [])
            self._update_recent_models_menu()
            self.logger.info("Recent models cleared")
        except Exception as e:
            self.logger.warning(f"Failed to clear recent models: {e}")
    
    def _on_loading_cancel_requested(self):
        """Handle loading cancellation request."""
        try:
            self.logger.info("Loading cancellation requested by user")
            
            # Cancel universal loading if in progress
            if hasattr(self.universal_loader, 'cancel_loading'):
                self.universal_loader.cancel_loading()
            
            # Close loading dialog
            if self.loading_dialog:
                self.loading_dialog.close()
                self.loading_dialog = None
            
            # Update status
            self.status_bar.showMessage("Loading cancelled by user", 3000)
            
        except Exception as e:
            self.logger.error(f"Error handling loading cancellation: {e}")
    
    def closeEvent(self, event):
        """Handle window close event."""
        self.logger.info("Closing application and cleaning up resources...")
        
        # Save window state
        self._save_window_state()
        
        # Cleanup performance-optimized backend manager
        try:
            if hasattr(self, 'backend_manager'):
                self.backend_manager.cleanup()
                self.logger.info("Backend manager cleanup completed")
        except Exception as e:
            self.logger.error(f"Error during backend manager cleanup: {e}")
        
        # Call parent close event
        super().closeEvent(event)
    
    def _load_model_universal(self, model_path: str, format_type: ModelFormat):
        """Load a model using the universal loading pipeline."""
        self.logger.info(f"Loading {format_type.value} model: {model_path}")
        
        # Update status
        model_name = Path(model_path).name if format_type != ModelFormat.HUGGINGFACE else model_path
        self.status_bar.showMessage(f"Loading {format_type.value} model: {model_name}...")
        
        # Add to recent models
        self._add_to_recent_models(model_path)
        
        # Show progress dialog
        self.loading_dialog = ModelLoadingDialog(model_name, self)
        self.loading_dialog.cancelled.connect(self._on_loading_cancel_requested)
        self.loading_dialog.show()
        
        # Start universal loading
        try:
            result = self.universal_loader.load_model(model_path)
            # Result will be handled by signal handlers
        except Exception as e:
            self.logger.error(f"Failed to start universal loading: {e}")
            self._on_universal_loading_failed(str(e), None)
    
    # Universal loader signal handlers
    def _on_universal_loading_started(self, model_path: str):
        """Handle universal loading started."""
        self.logger.info(f"Universal loading started: {model_path}")
        if self.loading_dialog:
            self.loading_dialog.update_progress_message("Initializing universal loading pipeline...")
    
    def _on_universal_progress_updated(self, progress: UniversalLoadingProgress):
        """Handle universal loading progress updates."""
        if self.loading_dialog:
            self.loading_dialog.update_progress(progress.progress)
            self.loading_dialog.update_progress_message(progress.message)
            
            if progress.details:
                self.loading_dialog.update_progress_message(f"{progress.message}\n{progress.details}")
        
        # Update status bar
        self.status_bar.showMessage(f"{progress.message} ({progress.progress}%)")
    
    def _on_universal_loading_completed(self, result: UniversalLoadingResult):
        """Handle universal loading completion."""
        if self.loading_dialog:
            self.loading_dialog.on_loading_finished()
            self.loading_dialog = None
        
        if result.success:
            # Update UI for successful load
            model_name = Path(result.model_path).name if result.format_type != ModelFormat.HUGGINGFACE else result.model_path
            
            # Update model dropdown
            self.model_dropdown.clear()
            self.model_dropdown.addItem(f"{model_name} ({result.format_type.value})")
            self.model_dropdown.setEnabled(True)
            
            # Update status bar
            self.status_bar.showMessage(
                f"✓ {result.format_type.value} model loaded with {result.backend_used} "
                f"({result.load_time:.1f}s, {result.memory_usage}MB)"
            )
            
            # Log comprehensive results
            self.logger.info(f"[OK] Universal loading completed successfully:")
            self.logger.info(f"   Model: {result.model_path}")
            self.logger.info(f"   Format: {result.format_type.value}")
            self.logger.info(f"   Backend: {result.backend_used}")
            self.logger.info(f"   Load time: {result.load_time:.2f}s")
            self.logger.info(f"   Memory usage: {result.memory_usage}MB")
            
            if result.optimization_applied:
                self.logger.info(f"   Optimizations: {', '.join(result.optimization_applied)}")
            
            if result.fallback_attempts:
                self.logger.info(f"   Fallback attempts: {', '.join(result.fallback_attempts)}")
            
            # IMPORTANT: Load the model into BackendManager for chat functionality
            try:
                self.logger.info("🔗 Bridging universal loading to BackendManager for chat functionality...")
                
                # Map universal backend names to BackendManager backend names if needed
                backend_name = result.backend_used
                if backend_name == "llama_cpp_python":
                    backend_name = "llama-cpp-python"
                
                backend_result = self.backend_manager.load_model_optimized(
                    model_path=result.model_path,
                    hardware_preference="auto",
                    force_backend=backend_name
                )
                
                if backend_result and hasattr(backend_result, 'success') and backend_result.success:
                    self.logger.info(f"[OK] Model successfully loaded into BackendManager for chat")
                    
                    # Verify the model is actually loaded
                    if self.backend_manager.current_backend:
                        self.logger.info(f"🎯 Chat functionality is now ready with {backend_name}")
                    else:
                        self.logger.warning(f"[WARN] BackendManager reports no current backend after loading")
                        
                elif backend_result:
                    self.logger.warning(f"[WARN] BackendManager loading failed: {backend_result}")
                else:
                    self.logger.warning(f"[WARN] BackendManager returned no result")
                    
            except Exception as e:
                self.logger.error(f"[ERROR] Error bridging to BackendManager: {e}")
                import traceback
                self.logger.error(f"Traceback: {traceback.format_exc()}")
                
                # Don't fail the entire loading process if BackendManager bridge fails
                self.logger.info("📝 Universal loading succeeded, but chat may not work until model is loaded via BackendManager")
            
            # Publish model loaded event for other components
            self.event_bus.publish("model.loaded", result.backend_used, {
                'name': model_name,
                'path': result.model_path,
                'format': result.format_type.value,
                'backend': result.backend_used,
                'load_time_s': result.load_time,
                'memory_usage_mb': result.memory_usage,
                'metadata': result.metadata,
                'optimization_applied': result.optimization_applied,
                'universal_loading': True
            })
            
            # Show success message with details
            QMessageBox.information(
                self,
                "Model Loaded Successfully",
                f"Model: {model_name}\n"
                f"Format: {result.format_type.value}\n"
                f"Backend: {result.backend_used}\n"
                f"Load time: {result.load_time:.1f}s\n"
                f"Memory usage: {result.memory_usage}MB\n"
                f"Chat: {'Ready' if hasattr(self, 'backend_manager') and self.backend_manager and self.backend_manager.current_backend else 'Not Ready'}"
            )
        
        else:
            self.logger.error(f"Universal loading failed: {result.error_analysis}")
            self._show_loading_error("Universal loading failed", str(result.error_analysis))
    
    def _on_universal_loading_failed(self, error_message: str, error_analysis):
        """Handle universal loading failure."""
        if self.loading_dialog:
            self.loading_dialog.on_loading_error(error_message)
            self.loading_dialog = None
        
        self.status_bar.showMessage("[ERROR] Model loading failed")
        
        self.logger.error(f"Universal loading failed: {error_message}")
        
        # Show detailed error information
        self._show_loading_error("Universal Loading Failed", error_message, error_analysis)
        
        # Publish error event
        self.event_bus.publish("model.error", error_message, {
            'universal_loading': True,
            'error_analysis': error_analysis
        })
    
    def _on_universal_format_detected(self, model_path: str, format_type: ModelFormat):
        """Handle format detection."""
        self.logger.info(f"Format detected: {format_type.value} for {model_path}")
        if self.loading_dialog:
            self.loading_dialog.update_progress_message(f"Detected {format_type.value} format")
    
    def _on_universal_backend_selected(self, backend_name: str, reason: str):
        """Handle backend selection."""
        self.logger.info(f"Backend selected: {backend_name} ({reason})")
        if self.loading_dialog:
            self.loading_dialog.update_progress_message(f"Selected {backend_name} backend")
    
    def _on_universal_memory_check(self, memory_check):
        """Handle memory check completion."""
        if memory_check.is_available:
            self.logger.info(f"Memory check passed: {memory_check.available_memory // (1024*1024)}MB available")
        else:
            self.logger.warning(f"Memory check warning: {memory_check.memory_deficit // (1024*1024)}MB deficit")
            
        if self.loading_dialog:
            if memory_check.is_available:
                self.loading_dialog.update_progress_message("Memory check passed")
            else:
                self.loading_dialog.update_progress_message("Memory optimization required")
    
    def _on_universal_metadata_extracted(self, metadata):
        """Handle metadata extraction."""
        self.logger.info(f"Metadata extracted: {metadata.model_name} ({metadata.architecture})")
        if self.loading_dialog:
            self.loading_dialog.update_progress_message(f"Extracted metadata for {metadata.model_name}")
    
    def _show_loading_error(self, title: str, message: str, error_analysis=None):
        """Show detailed loading error dialog."""
        error_dialog = QMessageBox(self)
        error_dialog.setIcon(QMessageBox.Critical)
        error_dialog.setWindowTitle(title)
        error_dialog.setText(message)
        
        if error_analysis:
            # Add detailed error information if available
            details = []
            if hasattr(error_analysis, 'root_cause'):
                details.append(f"Root cause: {error_analysis.root_cause}")
            if hasattr(error_analysis, 'resolution_suggestions'):
                details.append("Suggestions:")
                for suggestion in error_analysis.resolution_suggestions[:3]:  # Show top 3
                    details.append(f"• {suggestion.title}")
            
            if details:
                error_dialog.setDetailedText("\n".join(details))
        
        error_dialog.exec()
    
    # Monitoring signal handlers
    def _on_loading_metrics_updated(self, metrics):
        """Handle loading metrics updates from monitor."""
        self.logger.debug(f"Loading metrics updated: {metrics.model_path} - {metrics.success}")
        
        # Update status bar with performance info
        if metrics.success:
            self.status_bar.showMessage(
                f"✓ {metrics.format_type.value} loaded in {metrics.total_duration:.1f}s "
                f"({metrics.memory_usage_mb}MB, {metrics.backend_used})"
            )
        
        # Log comprehensive metrics
        self.logger.info(f"📊 Loading Metrics:")
        self.logger.info(f"   Model: {Path(metrics.model_path).name}")
        self.logger.info(f"   Format: {metrics.format_type.value}")
        self.logger.info(f"   Backend: {metrics.backend_used}")
        self.logger.info(f"   Success: {metrics.success}")
        self.logger.info(f"   Total time: {metrics.total_duration:.2f}s")
        self.logger.info(f"   Memory usage: {metrics.memory_usage_mb}MB")
        
        if metrics.optimization_applied:
            self.logger.info(f"   Optimizations: {', '.join(metrics.optimization_applied)}")
        
        if metrics.fallback_attempts:
            self.logger.info(f"   Fallbacks: {', '.join(metrics.fallback_attempts)}")
    
    def _on_system_health_updated(self, health):
        """Handle system health updates from monitor."""
        # Log health status periodically (every 30 seconds)
        current_time = time.time()
        if not hasattr(self, '_last_health_log') or current_time - self._last_health_log > 30:
            self.logger.debug(f"System Health: CPU {health.cpu_usage:.1f}%, "
                            f"Memory {health.memory_usage:.1f}%, "
                            f"Active loadings: {health.active_loadings}")
            self._last_health_log = current_time
        
        # Update UI if health is critical
        if health.cpu_usage > 90 or health.memory_usage > 95:
            self.status_bar.showMessage(
                f"[WARN] High resource usage: CPU {health.cpu_usage:.0f}%, Memory {health.memory_usage:.0f}%",
                5000  # Show for 5 seconds
            )
    
    def _on_performance_alert(self, alert_type: str, message: str):
        """Handle performance alerts from monitor."""
        self.logger.warning(f"Performance Alert ({alert_type}): {message}")
        
        # Show alert in status bar
        alert_icons = {
            'slow_loading': '🐌',
            'high_memory': '🧠',
            'low_success_rate': '[ERROR]',
            'backend_failure': '[WARN]'
        }
        
        icon = alert_icons.get(alert_type, '[WARN]')
        self.status_bar.showMessage(f"{icon} {message}", 10000)  # Show for 10 seconds
        
        # For critical alerts, show dialog
        if alert_type in ['high_memory', 'low_success_rate']:
            QMessageBox.warning(
                self,
                f"Performance Alert: {alert_type.replace('_', ' ').title()}",
                message
            )
    
    def get_universal_loading_statistics(self) -> Dict[str, Any]:
        """Get comprehensive universal loading statistics for display."""
        try:
            # Get statistics from universal loader
            loader_stats = self.universal_loader.get_loading_statistics()
            
            # Get performance summary from monitor
            performance_summary = self.loading_monitor.get_performance_summary()
            
            # Get system health status
            health_status = self.loading_monitor.get_system_health_status()
            
            return {
                'loader_statistics': loader_stats,
                'performance_summary': performance_summary,
                'system_health': health_status,
                'supported_formats': [fmt.value for fmt in self.universal_loader.get_supported_formats()],
                'available_backends': self.universal_loader.get_available_backends()
            }
        except Exception as e:
            self.logger.error(f"Failed to get universal loading statistics: {e}")
            return {'error': str(e)}
    
    def export_loading_metrics(self, file_path: str, format: str = 'json'):
        """Export loading metrics to file."""
        try:
            self.loading_monitor.export_metrics(file_path, format)
            QMessageBox.information(
                self,
                "Export Successful",
                f"Loading metrics exported to {file_path}"
            )
        except Exception as e:
            self.logger.error(f"Failed to export metrics: {e}")
            QMessageBox.critical(
                self,
                "Export Failed",
                f"Failed to export metrics:\n{str(e)}"
            )
    
    # Unified model management methods
    def _show_model_manager(self):
        """Show unified model management dialog."""
        try:
            from .model_manager_dialog import ModelManagerDialog
            
            dialog = ModelManagerDialog(
                self.universal_loader,
                self.loading_monitor,
                self.config_manager,
                self
            )
            dialog.exec()
        except ImportError:
            # Fallback to basic model info if dialog not available
            self._show_model_info()
    
    def _show_loading_statistics(self):
        """Show loading statistics dialog."""
        stats = self.get_universal_loading_statistics()
        
        # Create a simple dialog to display statistics
        dialog = QDialog(self)
        dialog.setWindowTitle("Loading Statistics")
        dialog.setModal(True)
        dialog.resize(600, 400)
        
        layout = QVBoxLayout(dialog)
        
        # Create text area for statistics
        text_area = QTextEdit()
        text_area.setReadOnly(True)
        
        # Format statistics for display
        stats_text = self._format_statistics_text(stats)
        text_area.setPlainText(stats_text)
        
        layout.addWidget(text_area)
        
        # Close button
        close_button = QPushButton("Close")
        close_button.clicked.connect(dialog.accept)
        layout.addWidget(close_button)
        
        dialog.exec()
    
    def _export_metrics(self):
        """Export loading metrics to file."""
        file_dialog = QFileDialog(self)
        file_dialog.setAcceptMode(QFileDialog.AcceptSave)
        file_dialog.setNameFilters([
            "JSON Files (*.json)",
            "CSV Files (*.csv)",
            "All Files (*)"
        ])
        file_dialog.setDefaultSuffix("json")
        
        if file_dialog.exec():
            selected_files = file_dialog.selectedFiles()
            if selected_files:
                file_path = selected_files[0]
                
                # Determine format from extension
                if file_path.lower().endswith('.csv'):
                    format_type = 'csv'
                else:
                    format_type = 'json'
                
                self.export_loading_metrics(file_path, format_type)
    
    def _clear_model_cache(self):
        """Clear model loading cache."""
        reply = QMessageBox.question(
            self,
            "Clear Cache",
            "Are you sure you want to clear the model loading cache?\n\n"
            "This will remove all cached loading results and may slow down "
            "subsequent loads of the same models.",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No
        )
        
        if reply == QMessageBox.Yes:
            try:
                self.universal_loader.clear_cache()
                QMessageBox.information(
                    self,
                    "Cache Cleared",
                    "Model loading cache has been cleared successfully."
                )
                self.logger.info("Model loading cache cleared by user")
            except Exception as e:
                self.logger.error(f"Failed to clear cache: {e}")
                QMessageBox.critical(
                    self,
                    "Clear Cache Failed",
                    f"Failed to clear cache:\n{str(e)}"
                )
    
    def _format_statistics_text(self, stats: Dict[str, Any]) -> str:
        """Format statistics for display in text area."""
        if 'error' in stats:
            return f"Error loading statistics: {stats['error']}"
        
        lines = []
        lines.append("=== Universal Loading Statistics ===\n")
        
        # Loader statistics
        if 'loader_statistics' in stats:
            loader_stats = stats['loader_statistics']
            lines.append("📊 Loader Statistics:")
            lines.append(f"  Cache size: {loader_stats.get('cache_size', 0)}")
            lines.append(f"  Supported formats: {', '.join(loader_stats.get('supported_formats', []))}")
            lines.append(f"  Available backends: {', '.join(loader_stats.get('available_backends', []))}")
            if loader_stats.get('current_loading'):
                lines.append(f"  Currently loading: {loader_stats['current_loading']}")
            lines.append("")
        
        # Performance summary
        if 'performance_summary' in stats:
            perf_summary = stats['performance_summary']
            if 'error' not in perf_summary:
                lines.append("[PERF] Performance Summary:")
                lines.append(f"  Total loads: {perf_summary.get('total_loads', 0)}")
                lines.append(f"  Successful loads: {perf_summary.get('successful_loads', 0)}")
                lines.append(f"  Success rate: {perf_summary.get('success_rate', 0):.1%}")
                
                if 'performance' in perf_summary:
                    perf = perf_summary['performance']
                    lines.append(f"  Average load time: {perf.get('avg_load_time', 0):.2f}s")
                    lines.append(f"  Average memory usage: {perf.get('avg_memory_usage_mb', 0):.0f}MB")
                
                if 'distributions' in perf_summary:
                    dist = perf_summary['distributions']
                    if dist.get('formats'):
                        lines.append(f"  Format distribution: {dist['formats']}")
                    if dist.get('backends'):
                        lines.append(f"  Backend distribution: {dist['backends']}")
                
                lines.append("")
        
        # System health
        if 'system_health' in stats:
            health = stats['system_health']
            if health.get('status') != 'no_data':
                lines.append("🏥 System Health:")
                lines.append(f"  Status: {health.get('status', 'unknown')}")
                lines.append(f"  Health score: {health.get('health_score', 0)}/100")
                
                if 'metrics' in health:
                    metrics = health['metrics']
                    lines.append(f"  CPU usage: {metrics.get('cpu_usage', 0):.1f}%")
                    lines.append(f"  Memory usage: {metrics.get('memory_usage', 0):.1f}%")
                    lines.append(f"  Active loadings: {metrics.get('active_loadings', 0)}")
                    lines.append(f"  Error rate: {metrics.get('error_rate', 0):.1%}")
                
                if health.get('recommendations'):
                    lines.append("  Recommendations:")
                    for rec in health['recommendations']:
                        lines.append(f"    • {rec}")
                
                lines.append("")
        
        return "\n".join(lines)