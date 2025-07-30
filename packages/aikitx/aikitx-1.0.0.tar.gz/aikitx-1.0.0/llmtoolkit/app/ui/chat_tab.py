"""
Chat Tab

This module contains the ChatTab class, which provides a clean chat interface
for AI conversations with message history display and progress indicators.
Enhanced with universal model loading system integration.
"""

import logging
from typing import Optional, List, Dict, Any
from datetime import datetime

from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QTextEdit, QLineEdit, 
    QPushButton, QLabel, QProgressBar, QScrollArea, QFrame,
    QMessageBox, QFileDialog
)
from PySide6.QtCore import Qt, QTimer, Signal, Slot
from PySide6.QtGui import QTextCursor, QFont, QIcon

from llmtoolkit.app.core.event_bus import EventBus
from llmtoolkit.app.ui.chat_bubble import ChatBubble
from llmtoolkit.app.ui.theme_manager import ThemeManager
from llmtoolkit.app.core.universal_events import (
    UniversalEventType, UniversalLoadingProgress, UniversalModelInfo,
    LoadingStage
)


class ChatMessage:
    """Represents a single chat message."""
    
    def __init__(self, role: str, content: str, timestamp: Optional[datetime] = None):
        self.role = role  # 'user' or 'assistant'
        self.content = content
        self.timestamp = timestamp or datetime.now()
        self.id = f"{self.role}_{self.timestamp.timestamp()}"


class ChatTab(QWidget):
    """
    Clean chat interface for AI conversations.
    
    Features:
    - Clean message history display with visual distinction
    - Text input area with send button
    - Progress indicators for response generation
    - Message formatting and styling
    """
    
    # Signals
    message_sent = Signal(str)  # Emitted when user sends a message
    
    def __init__(self, event_bus: EventBus, parent=None):
        """
        Initialize the chat tab.
        
        Args:
            event_bus: Application event bus
            parent: Parent widget
        """
        super().__init__(parent)
        
        self.logger = logging.getLogger("gguf_loader.ui.chat_tab")
        self.event_bus = event_bus
        self.messages: List[ChatMessage] = []
        self.is_generating = False
        
        # Streaming state
        self.current_streaming_message = None
        self.streaming_content = ""
        
        # Universal model loading state
        self.current_model_info: Optional[UniversalModelInfo] = None
        self.loading_progress_widget = None
        
        # Theme manager
        self.theme_manager = ThemeManager()
        
        # Initialize UI
        self._init_ui()
        
        # Apply theme
        self._apply_theme()
        
        # Connect events
        self._connect_events()
        
        # Connect universal model loading events
        self._connect_universal_events()
    
    def _init_ui(self):
        """Initialize the chat interface."""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(15, 15, 15, 15)
        layout.setSpacing(15)
        
        # Chat display area - using scroll area with chat bubbles
        self.chat_scroll = QScrollArea()
        self.chat_scroll.setWidgetResizable(True)
        self.chat_scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.chat_scroll.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        
        # Chat container widget
        self.chat_container = QWidget()
        self.chat_layout = QVBoxLayout(self.chat_container)
        self.chat_layout.setContentsMargins(20, 20, 20, 20)
        self.chat_layout.setSpacing(10)
        self.chat_layout.addStretch()  # Push messages to top
        
        # Placeholder label
        self.placeholder_label = QLabel("Start a conversation with the AI assistant...")
        self.placeholder_label.setAlignment(Qt.AlignCenter)
        self.chat_layout.insertWidget(0, self.placeholder_label)
        
        self.chat_scroll.setWidget(self.chat_container)
        layout.addWidget(self.chat_scroll)
        
        # Progress indicator (initially hidden)
        self.progress_bar = QProgressBar()
        self.progress_bar.setRange(0, 0)  # Indeterminate progress
        self.progress_bar.hide()
        layout.addWidget(self.progress_bar)
        
        # Chat input area
        input_layout = QHBoxLayout()
        input_layout.setSpacing(12)
        
        # Text input
        self.chat_input = QLineEdit()
        self.chat_input.setPlaceholderText("Type your message here...")
        self.chat_input.returnPressed.connect(self._send_message)
        input_layout.addWidget(self.chat_input)
        
        # Send button
        self.send_button = QPushButton("Send")
        self.send_button.clicked.connect(self._send_message)
        input_layout.addWidget(self.send_button)
        
        # Cancel button (initially hidden)
        self.cancel_button = QPushButton("Cancel")
        self.cancel_button.clicked.connect(self._cancel_generation)
        self.cancel_button.hide()
        input_layout.addWidget(self.cancel_button)
        
        layout.addLayout(input_layout)
        
        # Status label (initially hidden)
        self.status_label = QLabel()
        self.status_label.hide()
        layout.addWidget(self.status_label)
    
    def _apply_theme(self):
        """Apply consistent dark theme to chat tab components."""
        try:
            # Get consistent dark theme colors
            colors = self.theme_manager.get_colors()
            
            # Apply dark theme to the entire widget
            self.setStyleSheet(f"""
                QWidget {{
                    background-color: {colors["background"]};
                    color: {colors["text"]};
                }}
            """)
            
            # Apply specific styling for chat components
            self.chat_scroll.setStyleSheet(f"""
                QScrollArea {{
                    background-color: {colors["background"]};
                    border: 1px solid {colors["border"]};
                    border-radius: 12px;
                }}
                QScrollArea QWidget {{
                    background-color: {colors["background"]};
                }}
            """)
            
            self.placeholder_label.setStyleSheet(f"""
                QLabel {{
                    color: {colors["text_secondary"]};
                    font-size: 14px;
                    font-style: italic;
                    padding: 40px;
                }}
            """)
            
            self.progress_bar.setStyleSheet(f"""
                QProgressBar {{
                    border: 1px solid {colors["border"]};
                    border-radius: 6px;
                    background-color: {colors["surface"]};
                    height: 8px;
                }}
                QProgressBar::chunk {{
                    background-color: {colors["primary"]};
                    border-radius: 5px;
                }}
            """)
            
            self.chat_input.setStyleSheet(f"""
                QLineEdit {{
                    padding: 15px 20px;
                    border: 2px solid {colors["border"]};
                    border-radius: 25px;
                    font-size: 14px;
                    background-color: {colors["surface"]};
                    color: {colors["text"]};
                    min-height: 20px;
                }}
                QLineEdit:focus {{
                    border-color: {colors["primary"]};
                    outline: none;
                }}
                QLineEdit::placeholder {{
                    color: {colors["text_secondary"]};
                    font-style: italic;
                }}
            """)
            
            self.send_button.setStyleSheet(f"""
                QPushButton {{
                    background-color: {colors["primary"]};
                    color: white;
                    border: none;
                    border-radius: 25px;
                    padding: 15px 30px;
                    font-weight: bold;
                    font-size: 14px;
                    min-width: 80px;
                }}
                QPushButton:hover {{
                    background-color: #106ebe;
                }}
                QPushButton:pressed {{
                    background-color: #005a9e;
                }}
                QPushButton:disabled {{
                    background-color: {colors["text_secondary"]};
                    cursor: not-allowed;
                }}
            """)
            
            self.cancel_button.setStyleSheet(f"""
                QPushButton {{
                    background-color: {colors["error"]};
                    color: white;
                    border: none;
                    border-radius: 25px;
                    padding: 15px 30px;
                    font-weight: bold;
                    font-size: 14px;
                    min-width: 80px;
                }}
                QPushButton:hover {{
                    background-color: #c82333;
                }}
                QPushButton:pressed {{
                    background-color: #bd2130;
                }}
            """)
            
            self.status_label.setStyleSheet(f"""
                QLabel {{
                    color: {colors["text_secondary"]};
                    font-size: 12px;
                    font-style: italic;
                    padding: 5px 10px;
                }}
            """)
            
        except Exception as e:
            self.logger.error(f"Failed to apply theme to chat tab: {e}")
    
    def _connect_events(self):
        """Connect event handlers."""
        self.event_bus.subscribe("chat.response", self._on_chat_response)
        self.event_bus.subscribe("chat.token", self._on_chat_token)
        self.event_bus.subscribe("chat.error", self._on_chat_error)
        self.event_bus.subscribe("chat.generating", self._on_chat_generating)
        self.event_bus.subscribe("chat.cancelled", self._on_chat_cancelled)
        self.event_bus.subscribe("model.loaded", self._on_model_loaded)
        self.event_bus.subscribe("model.unloaded", self._on_model_unloaded)
    
    def _connect_universal_events(self):
        """Connect to universal loading system events."""
        self.event_bus.subscribe(UniversalEventType.UNIVERSAL_LOADING_STARTED, self._on_universal_loading_started)
        self.event_bus.subscribe(UniversalEventType.UNIVERSAL_PROGRESS_UPDATED, self._on_universal_progress_updated)
        self.event_bus.subscribe(UniversalEventType.UNIVERSAL_MODEL_LOADED, self._on_universal_model_loaded)
        self.event_bus.subscribe(UniversalEventType.UNIVERSAL_LOADING_FAILED, self._on_universal_loading_failed)
        self.event_bus.subscribe(UniversalEventType.UNIVERSAL_MODEL_UNLOADED, self._on_universal_model_unloaded)
        self.event_bus.subscribe(UniversalEventType.UNIVERSAL_BACKEND_SELECTED, self._on_universal_backend_selected)
    
    def _send_message(self):
        """Send a chat message."""
        message_text = self.chat_input.text().strip()
        if not message_text or self.is_generating:
            return
        
        # Create user message
        user_message = ChatMessage("user", message_text)
        self.messages.append(user_message)
        
        # Display user message
        self._display_message(user_message)
        
        # Clear input
        self.chat_input.clear()
        
        # Set generating state
        self._set_generating_state(True)
        
        # Emit signal and publish event
        self.message_sent.emit(message_text)
        self.event_bus.publish("chat.send", {
            "message": message_text,
            "conversation_id": "main_chat"
        })
        
        self.logger.info(f"Sent chat message: {message_text[:50]}...")
    
    def _display_message(self, message: ChatMessage):
        """Display a message using ChatBubble widget."""
        # Hide placeholder if this is the first message
        if self.placeholder_label.isVisible():
            self.placeholder_label.hide()
        
        # Create chat bubble
        is_user = (message.role == "user")
        bubble = ChatBubble(message.content, is_user)
        
        # Create container for bubble alignment
        bubble_container = QWidget()
        bubble_layout = QHBoxLayout(bubble_container)
        bubble_layout.setContentsMargins(0, 0, 0, 0)
        
        if is_user:
            # User messages aligned to the right
            bubble_layout.addStretch()
            bubble_layout.addWidget(bubble)
        else:
            # Assistant messages aligned to the left
            bubble_layout.addWidget(bubble)
            bubble_layout.addStretch()
        
        # Add to chat layout (before the stretch)
        self.chat_layout.insertWidget(self.chat_layout.count() - 1, bubble_container)
        
        # Scroll to bottom
        self._scroll_to_bottom()
    
    def _show_typing_indicator(self):
        """Show typing indicator for AI response."""
        # Hide placeholder if this is the first message
        if self.placeholder_label.isVisible():
            self.placeholder_label.hide()
        
        # Create typing indicator bubble
        typing_bubble = ChatBubble("🤖 Assistant is typing...", False)
        typing_bubble.setObjectName("typing_indicator")  # For easy removal
        
        # Create container for bubble alignment
        bubble_container = QWidget()
        bubble_container.setObjectName("typing_container")
        bubble_layout = QHBoxLayout(bubble_container)
        bubble_layout.setContentsMargins(0, 0, 0, 0)
        
        # Assistant messages aligned to the left
        bubble_layout.addWidget(typing_bubble)
        bubble_layout.addStretch()
        
        # Add to chat layout (before the stretch)
        self.chat_layout.insertWidget(self.chat_layout.count() - 1, bubble_container)
        self._scroll_to_bottom()
    
    def _remove_typing_indicator(self):
        """Remove the typing indicator."""
        # Find and remove the typing indicator container
        for i in range(self.chat_layout.count()):
            widget = self.chat_layout.itemAt(i).widget()
            if widget and widget.objectName() == "typing_container":
                self.chat_layout.removeWidget(widget)
                widget.deleteLater()
                break
    
    def _cancel_generation(self):
        """Cancel the current text generation."""
        if self.is_generating:
            self.logger.info("User requested generation cancellation")
            # Publish cancellation event
            self.event_bus.publish("chat.cancel", True)
    
    def _set_generating_state(self, generating: bool):
        """Set the generating state and update UI accordingly."""
        self.is_generating = generating
        
        # Update input and button states
        self.chat_input.setEnabled(not generating)
        self.send_button.setEnabled(not generating)
        
        if generating:
            self.send_button.setText("Generating...")
            self.send_button.hide()
            self.cancel_button.show()
            self.progress_bar.show()
            self.status_label.setText("AI is generating response... (Click Cancel to stop)")
            self.status_label.show()
            self._show_typing_indicator()
        else:
            self.send_button.setText("Send")
            self.send_button.show()
            self.cancel_button.hide()
            self.progress_bar.hide()
            self.status_label.hide()
    
    def _scroll_to_bottom(self):
        """Scroll chat display to bottom."""
        scrollbar = self.chat_scroll.verticalScrollBar()
        scrollbar.setValue(scrollbar.maximum())
    
    def _escape_html(self, text: str) -> str:
        """Escape HTML characters in text while preserving natural spacing."""
        return (text.replace("&", "&amp;")
                   .replace("<", "&lt;")
                   .replace(">", "&gt;")
                   .replace('"', "&quot;")
                   .replace("'", "&#x27;")
                   .replace("\n", "<br>"))
        # Note: We don't convert spaces to &nbsp; to maintain natural text flow
    
    # Universal model loading event handlers
    def _on_universal_loading_started(self, *args, **kwargs):
        """Handle universal model loading started event."""
        # Extract data from args or kwargs
        data = args[0] if args else kwargs
        model_path = data.get('model_path', 'Unknown model')
        self.logger.info(f"Universal model loading started: {model_path}")
        
        # Show loading started message
        loading_message = f"Starting to load model: {model_path.split('/')[-1]}"
        self._show_system_message(loading_message, "info")
        
        # Disable chat input during loading
        self.chat_input.setEnabled(False)
        self.send_button.setEnabled(False)
    
    def _on_universal_progress_updated(self, *args, **kwargs):
        """Handle universal loading progress updates."""
        # Extract data from args or kwargs
        progress_data = args[0] if args else kwargs
        self.logger.info(f"Progress update received: {progress_data}")
        
        stage = progress_data.get('stage', 'unknown')
        progress = progress_data.get('progress', 0)
        message = progress_data.get('message', 'Loading...')
        details = progress_data.get('details')
        backend_info = progress_data.get('backend_info')
        
        # Create progress message
        progress_message = f"Loading Progress: {message} ({progress}%)"
        if backend_info:
            progress_message += f" - {backend_info}"
        
        # Show progress in status label
        self.status_label.setText(progress_message)
        self.status_label.show()
        
        # Update progress bar - ensure it's visible and set correct range
        self.progress_bar.setRange(0, 100)
        self.progress_bar.setValue(progress)
        self.progress_bar.show()
        
        self.logger.debug(f"Loading progress: {stage} - {progress}% - {message}")
    
    def _on_universal_model_loaded(self, *args, **kwargs):
        """Handle enhanced model loaded event with format information."""
        # Extract data from args or kwargs
        model_data = args[0] if args else kwargs
        self.logger.info("Universal model loaded successfully")
        
        # Create UniversalModelInfo from the data
        self.current_model_info = self._create_model_info_from_data(model_data)
        
        # Hide progress indicators
        self.progress_bar.hide()
        self.status_label.hide()
        
        # Show enhanced welcome message with model capabilities
        self._show_enhanced_welcome_message()
        
        # Enable chat functionality
        self.chat_input.setEnabled(True)
        self.send_button.setEnabled(True)
        self.chat_input.setFocus()
    
    def _on_universal_loading_failed(self, *args, **kwargs):
        """Handle universal loading failure with enhanced error information."""
        # Extract data from args or kwargs
        error_data = args[0] if args else kwargs
        error_message = error_data.get('error_message', 'Unknown error')
        error_analysis = error_data.get('error_analysis', {})
        
        self.logger.error(f"Universal model loading failed: {error_message}")
        
        # Hide progress indicators
        self.progress_bar.hide()
        self.status_label.hide()
        
        # Show enhanced error message
        self._show_enhanced_error_message(error_message, error_analysis)
        
        # Keep chat input disabled
        self.chat_input.setEnabled(False)
        self.send_button.setEnabled(False)
    
    def _on_universal_model_unloaded(self, *args, **kwargs):
        """Handle universal model unloaded event."""
        # Extract data from args or kwargs
        unload_data = args[0] if args else kwargs
        model_path = unload_data.get('model_path', 'Unknown model')
        self.logger.info(f"Universal model unloaded: {model_path}")
        
        # Clear current model info
        self.current_model_info = None
        
        # Show unload message
        unload_message = f"Model unloaded: {model_path.split('/')[-1]}"
        self._show_system_message(unload_message, "warning")
        
        # Disable chat input and reset generating state
        self._set_generating_state(False)
        self.chat_input.setEnabled(False)
        self.send_button.setEnabled(False)
    
    def _on_universal_backend_selected(self, *args, **kwargs):
        """Handle backend selection event."""
        # Extract data from args or kwargs
        backend_data = args[0] if args else kwargs
        backend_name = backend_data.get('backend_name', 'Unknown')
        reason = backend_data.get('reason', 'No reason provided')
        confidence = backend_data.get('confidence', 1.0)
        
        self.logger.info(f"Backend selected: {backend_name} (confidence: {confidence:.2f})")
        
        # Show backend selection info
        backend_message = f"Selected backend: {backend_name}"
        if confidence < 0.8:
            backend_message += f" (fallback option)"
        
        self._show_system_message(backend_message, "info")
    
    def _create_model_info_from_data(self, model_data: dict) -> UniversalModelInfo:
        """Create UniversalModelInfo object from event data."""
        # Extract basic information
        model_path = model_data.get('model_path', '')
        format_type = model_data.get('format_type', 'unknown')
        backend_used = model_data.get('backend_used', 'unknown')
        hardware_used = model_data.get('hardware_used', 'unknown')
        capabilities = model_data.get('capabilities', [])
        performance_metrics = model_data.get('performance_metrics', {})
        memory_usage = model_data.get('memory_usage', 0)
        optimization_applied = model_data.get('optimization_applied', [])
        fallback_attempts = model_data.get('fallback_attempts', [])
        warnings = model_data.get('warnings', [])
        load_time = model_data.get('load_time', 0.0)
        
        # Create a simplified UniversalModelInfo-like object
        class ModelInfo:
            def __init__(self):
                self.model_path = model_path
                self.format_type = format_type
                self.backend_used = backend_used
                self.hardware_used = hardware_used
                self.capabilities = capabilities
                self.performance_metrics = performance_metrics
                self.memory_usage = memory_usage
                self.optimization_applied = optimization_applied
                self.fallback_attempts = fallback_attempts
                self.warnings = warnings
                self.load_time = load_time
                self.display_name = model_data.get('display_name', model_path.split('/')[-1])
                self.capability_description = model_data.get('capability_description', 'Standard text generation')
                self.performance_summary = model_data.get('performance_summary', f'Load time: {load_time:.1f}s')
                self.backend_info = model_data.get('backend_info', f'{backend_used} ({hardware_used})')
        
        return ModelInfo()
    
    def _show_enhanced_welcome_message(self):
        """Show enhanced welcome message with model capabilities."""
        if not self.current_model_info:
            return
        
        # Create comprehensive welcome message
        welcome_lines = [
            f"🤖 Model loaded successfully: {self.current_model_info.display_name}",
            f"📊 Backend: {self.current_model_info.backend_info}",
            f"[PERF] Performance: {self.current_model_info.performance_summary}",
            f"🎯 Capabilities: {self.current_model_info.capability_description}"
        ]
        
        # Add optimization info if available
        if self.current_model_info.optimization_applied:
            optimizations = ", ".join(self.current_model_info.optimization_applied)
            welcome_lines.append(f"[TOOL] Optimizations: {optimizations}")
        
        # Add warnings if any
        if self.current_model_info.warnings:
            warning_text = "; ".join(self.current_model_info.warnings)
            welcome_lines.append(f"[WARN] Warnings: {warning_text}")
        
        welcome_lines.append("\n💬 You can now start chatting with the AI assistant!")
        
        welcome_message = "\n".join(welcome_lines)
        self._show_system_message(welcome_message, "success")
    
    def _show_enhanced_error_message(self, error_message: str, error_analysis: dict):
        """Show enhanced error message with suggested solutions."""
        error_lines = [f"[ERROR] Model loading failed: {error_message}"]
        
        # Add error analysis if available
        if error_analysis:
            user_friendly_message = error_analysis.get('user_friendly_message')
            if user_friendly_message:
                error_lines.append(f"📝 Details: {user_friendly_message}")
            
            resolution_suggestions = error_analysis.get('resolution_suggestions', [])
            if resolution_suggestions:
                error_lines.append("💡 Suggestions:")
                for suggestion in resolution_suggestions[:3]:  # Show max 3 suggestions
                    error_lines.append(f"  • {suggestion}")
        
        error_lines.append("\n🔄 Please try loading a different model or check the model file.")
        
        error_message_full = "\n".join(error_lines)
        self._show_system_message(error_message_full, "error")
    
    def _show_system_message(self, message: str, message_type: str = "info"):
        """Show a system message with appropriate styling."""
        # Hide placeholder if this is the first message
        if self.placeholder_label.isVisible():
            self.placeholder_label.hide()
        
        # Create system message bubble
        system_bubble = ChatBubble(message, False)
        
        # Apply styling based on message type
        if message_type == "success":
            system_bubble.setStyleSheet("""
                QFrame {
                    background-color: #d4edda;
                    border: 1px solid #c3e6cb;
                    border-radius: 15px;
                    margin: 5px;
                }
                QLabel { 
                    color: #155724; 
                    font-size: 14px; 
                    padding: 12px 16px;
                    line-height: 1.6;
                }
            """)
        elif message_type == "error":
            system_bubble.setStyleSheet("""
                QFrame {
                    background-color: #f8d7da;
                    border: 1px solid #f5c6cb;
                    border-radius: 15px;
                    margin: 5px;
                }
                QLabel { 
                    color: #721c24; 
                    font-size: 14px; 
                    padding: 12px 16px;
                    line-height: 1.6;
                }
            """)
        elif message_type == "warning":
            system_bubble.setStyleSheet("""
                QFrame {
                    background-color: #fff3cd;
                    border: 1px solid #ffeaa7;
                    border-radius: 15px;
                    margin: 5px;
                }
                QLabel { 
                    color: #856404; 
                    font-size: 14px; 
                    padding: 12px 16px;
                    line-height: 1.6;
                }
            """)
        else:  # info
            system_bubble.setStyleSheet("""
                QFrame {
                    background-color: #d1ecf1;
                    border: 1px solid #bee5eb;
                    border-radius: 15px;
                    margin: 5px;
                }
                QLabel { 
                    color: #0c5460; 
                    font-size: 14px; 
                    padding: 12px 16px;
                    line-height: 1.6;
                }
            """)
        
        # Create container for system bubble (centered)
        bubble_container = QWidget()
        bubble_layout = QHBoxLayout(bubble_container)
        bubble_layout.setContentsMargins(0, 0, 0, 0)
        bubble_layout.addStretch()
        bubble_layout.addWidget(system_bubble)
        bubble_layout.addStretch()
        
        # Add to chat layout
        self.chat_layout.insertWidget(self.chat_layout.count() - 1, bubble_container)
        self._scroll_to_bottom()

    # Event handlers
    @Slot(object)
    def _on_chat_response(self, response_data):
        """Handle chat response from AI."""
        # Handle both old string format and new dictionary format
        if isinstance(response_data, dict):
            response = response_data.get("message", "")
            backend_used = response_data.get("backend_used", "unknown")
            self.logger.info(f"Received chat response from {backend_used}: {response[:50] if response else 'empty'}...")
        else:
            # Legacy string format
            response = str(response_data)
            self.logger.info(f"Received chat response: {response[:50] if response else 'empty'}...")
        
        # If we were streaming, finalize the streaming message
        if self.current_streaming_message:
            # Update the final content
            self.current_streaming_message.content = response
            self.streaming_content = response
            
            # Reset streaming state
            self.current_streaming_message = None
            self.streaming_content = ""
        else:
            # Non-streaming response - display normally
            # Remove typing indicator
            self._remove_typing_indicator()
            
            # Create assistant message
            assistant_message = ChatMessage("assistant", response)
            self.messages.append(assistant_message)
            
            # Display assistant message
            self._display_message(assistant_message)
        
        # Reset generating state
        self._set_generating_state(False)
    
    @Slot(str)
    def _on_chat_error(self, error_message: str):
        """Handle chat error."""
        self.logger.error(f"Chat error: {error_message}")
        
        # Remove typing indicator
        self._remove_typing_indicator()
        
        # Show error message using ChatBubble
        error_bubble = ChatBubble(f"Error: {error_message}", False)
        error_bubble.setStyleSheet("""
            QFrame {
                background-color: #f8d7da;
                border: 1px solid #f5c6cb;
                border-radius: 15px;
                margin: 5px;
            }
            QLabel { 
                color: #721c24; 
                font-size: 14px; 
                padding: 12px 16px;
                line-height: 1.6;
            }
        """)
        
        # Create container for error bubble (centered)
        bubble_container = QWidget()
        bubble_layout = QHBoxLayout(bubble_container)
        bubble_layout.setContentsMargins(0, 0, 0, 0)
        bubble_layout.addStretch()
        bubble_layout.addWidget(error_bubble)
        bubble_layout.addStretch()
        
        # Add to chat layout
        self.chat_layout.insertWidget(self.chat_layout.count() - 1, bubble_container)
        self._scroll_to_bottom()
        
        # Reset generating state
        self._set_generating_state(False)
    
    @Slot(str)
    def _on_chat_token(self, token: str):
        """Handle streaming token from AI response."""
        # DISABLED: Streaming is disabled, this method does nothing
        pass
    
    def _escape_html_preserve_spaces(self, text: str) -> str:
        """Escape HTML characters while preserving spaces for streaming display."""
        # Use a different approach for streaming - preserve spaces as regular spaces
        # but escape other HTML characters
        return (text.replace("&", "&amp;")
                   .replace("<", "&lt;")
                   .replace(">", "&gt;")
                   .replace('"', "&quot;")
                   .replace("'", "&#x27;")
                   .replace("\n", "<br>"))
        # Note: We keep regular spaces, not &nbsp;, for natural text flow
    
    @Slot()
    def _on_chat_generating(self, generating=True):
        """Handle chat generation start."""
        self._set_generating_state(generating)
    
    @Slot()
    def _on_chat_cancelled(self):
        """Handle chat generation cancellation."""
        self.logger.info("Chat generation was cancelled")
        
        # Remove typing indicator
        self._remove_typing_indicator()
        
        # Clean up streaming state
        if self.current_streaming_message:
            # Finalize the partial message
            if self.streaming_content:
                self.current_streaming_message.content = self.streaming_content + " [cancelled]"
            else:
                # Remove the empty message if no content was generated
                if self.current_streaming_message in self.messages:
                    self.messages.remove(self.current_streaming_message)
        
        # Reset streaming state
        self.current_streaming_message = None
        self.streaming_content = ""
        
        # Show cancellation message using ChatBubble
        cancel_bubble = ChatBubble("Generation cancelled by user", False)
        cancel_bubble.setStyleSheet("""
            QFrame {
                background-color: #fff3cd;
                border: 1px solid #ffeaa7;
                border-radius: 15px;
                margin: 5px;
            }
            QLabel { 
                color: #856404; 
                font-size: 12px; 
                padding: 8px 12px;
                font-style: italic;
            }
        """)
        
        # Create container for cancel bubble (centered)
        bubble_container = QWidget()
        bubble_layout = QHBoxLayout(bubble_container)
        bubble_layout.setContentsMargins(0, 0, 0, 0)
        bubble_layout.addStretch()
        bubble_layout.addWidget(cancel_bubble)
        bubble_layout.addStretch()
        
        # Add to chat layout
        self.chat_layout.insertWidget(self.chat_layout.count() - 1, bubble_container)
        self._scroll_to_bottom()
        
        # Reset generating state
        self._set_generating_state(False)
    
    @Slot(str, dict)
    def _on_model_loaded(self, model_id: str, model_info: dict):
        """Handle model loaded event."""
        self.logger.info(f"Model loaded: {model_id}")
        
        # Show welcome message using ChatBubble
        welcome_message = f"Model loaded: {model_info.get('name', 'Unknown Model')}\nYou can now start chatting with the AI assistant!"
        welcome_bubble = ChatBubble(welcome_message, False)
        welcome_bubble.setStyleSheet("""
            QFrame {
                background-color: #d4edda;
                border: 1px solid #c3e6cb;
                border-radius: 15px;
                margin: 5px;
            }
            QLabel { 
                color: #155724; 
                font-size: 14px; 
                padding: 12px 16px;
                line-height: 1.6;
                font-weight: bold;
            }
        """)
        
        # Create container for welcome bubble (centered)
        bubble_container = QWidget()
        bubble_layout = QHBoxLayout(bubble_container)
        bubble_layout.setContentsMargins(0, 0, 0, 0)
        bubble_layout.addStretch()
        bubble_layout.addWidget(welcome_bubble)
        bubble_layout.addStretch()
        
        # Add to chat layout
        self.chat_layout.insertWidget(self.chat_layout.count() - 1, bubble_container)
        self._scroll_to_bottom()
        
        # Enable input
        self.chat_input.setEnabled(True)
        self.send_button.setEnabled(True)
        self.chat_input.setFocus()
    
    @Slot(str)
    def _on_model_unloaded(self, model_id: str):
        """Handle model unloaded event."""
        self.logger.info(f"Model unloaded: {model_id}")
        
        # Show unload message using ChatBubble
        unload_message = "Model unloaded. Please load a model to continue chatting."
        unload_bubble = ChatBubble(unload_message, False)
        unload_bubble.setStyleSheet("""
            QFrame {
                background-color: #fff3cd;
                border: 1px solid #ffeaa7;
                border-radius: 15px;
                margin: 5px;
            }
            QLabel { 
                color: #856404; 
                font-size: 14px; 
                padding: 12px 16px;
                line-height: 1.6;
                font-weight: bold;
            }
        """)
        
        # Create container for unload bubble (centered)
        bubble_container = QWidget()
        bubble_layout = QHBoxLayout(bubble_container)
        bubble_layout.setContentsMargins(0, 0, 0, 0)
        bubble_layout.addStretch()
        bubble_layout.addWidget(unload_bubble)
        bubble_layout.addStretch()
        
        # Add to chat layout
        self.chat_layout.insertWidget(self.chat_layout.count() - 1, bubble_container)
        self._scroll_to_bottom()
        
        # Disable input
        self.chat_input.setEnabled(False)
        self.send_button.setEnabled(False)
        self._set_generating_state(False)
    
    def clear_conversation(self):
        """Clear the conversation history."""
        self.messages.clear()
        
        # Clear all chat bubbles from the layout
        for i in reversed(range(self.chat_layout.count())):
            widget = self.chat_layout.itemAt(i).widget()
            if widget and widget != self.placeholder_label:
                self.chat_layout.removeWidget(widget)
                widget.deleteLater()
        
        # Show placeholder again
        self.placeholder_label.show()
        
        self._set_generating_state(False)
        self.logger.info("Conversation cleared")
    
    def get_conversation_history(self) -> List[ChatMessage]:
        """Get the current conversation history."""
        return self.messages.copy()
    
    def add_system_message(self, message: str):
        """Add a system message to the chat."""
        # Create system message using ChatBubble
        system_bubble = ChatBubble(message, False)
        system_bubble.setStyleSheet("""
            QFrame {
                background-color: #f8f9fa;
                border: 1px solid #dee2e6;
                border-radius: 15px;
                margin: 5px;
            }
            QLabel { 
                color: #6c757d; 
                font-size: 12px; 
                padding: 8px 12px;
                font-style: italic;
            }
        """)
        
        # Create container for system bubble (centered)
        bubble_container = QWidget()
        bubble_layout = QHBoxLayout(bubble_container)
        bubble_layout.setContentsMargins(0, 0, 0, 0)
        bubble_layout.addStretch()
        bubble_layout.addWidget(system_bubble)
        bubble_layout.addStretch()
        
        # Add to chat layout
        self.chat_layout.insertWidget(self.chat_layout.count() - 1, bubble_container)
        self._scroll_to_bottom()
    
    def get_current_model_info(self) -> Optional[object]:
        """Get current universal model information."""
        return self.current_model_info
    
    def is_model_loaded(self) -> bool:
        """Check if a model is currently loaded via universal loading system."""
        return self.current_model_info is not None
    
    def get_model_capabilities(self) -> List[str]:
        """Get current model capabilities."""
        if self.current_model_info:
            return self.current_model_info.capabilities
        return []
    
    def has_capability(self, capability: str) -> bool:
        """Check if current model has a specific capability."""
        if self.current_model_info:
            return capability.lower() in [cap.lower() for cap in self.current_model_info.capabilities]
        return False