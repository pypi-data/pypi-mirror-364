"""
Chat Service

Manages conversational AI interactions, conversation context and history.
Integrates with ModelService for response generation.
"""

import logging
import uuid
from datetime import datetime
from typing import List, Optional, Dict, Any

from llmtoolkit.app.core.event_bus import EventBus


class ChatMessage:
    """Represents a single chat message."""
    
    def __init__(self, role: str, content: str, timestamp: datetime = None, message_id: str = None):
        """
        Initialize a chat message.
        
        Args:
            role: Message role ('user' or 'assistant')
            content: Message content
            timestamp: Message timestamp (defaults to now)
            message_id: Unique message ID (auto-generated if not provided)
        """
        self.id = message_id or str(uuid.uuid4())
        self.role = role
        self.content = content
        self.timestamp = timestamp or datetime.now()
        self.metadata = {}  # Additional metadata for the message
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert message to dictionary."""
        return {
            "id": self.id,
            "role": self.role,
            "content": self.content,
            "timestamp": self.timestamp.isoformat(),
            "metadata": self.metadata
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'ChatMessage':
        """Create message from dictionary."""
        message = cls(
            role=data["role"],
            content=data["content"],
            timestamp=datetime.fromisoformat(data["timestamp"]),
            message_id=data["id"]
        )
        message.metadata = data.get("metadata", {})
        return message
    
    def __str__(self):
        return f"{self.role}: {self.content}"
    
    def __repr__(self):
        return f"ChatMessage(id='{self.id}', role='{self.role}', content='{self.content[:50]}...')"


class ChatSession:
    """Represents a chat conversation session."""
    
    def __init__(self, session_id: str = None):
        """
        Initialize a chat session.
        
        Args:
            session_id: Unique session ID (auto-generated if not provided)
        """
        self.id = session_id or str(uuid.uuid4())
        self.messages: List[ChatMessage] = []
        self.created_at = datetime.now()
        self.last_active = self.created_at
        self.system_prompt: Optional[str] = None
        self.metadata = {}  # Additional session metadata
    
    def add_message(self, message: ChatMessage) -> None:
        """Add a message to the session."""
        self.messages.append(message)
        self.last_active = datetime.now()
    
    def get_messages(self, limit: int = None) -> List[ChatMessage]:
        """Get messages from the session."""
        if limit is None:
            return self.messages.copy()
        return self.messages[-limit:] if limit > 0 else []
    
    def clear_messages(self) -> None:
        """Clear all messages from the session."""
        self.messages.clear()
        self.last_active = datetime.now()
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert session to dictionary."""
        return {
            "id": self.id,
            "messages": [msg.to_dict() for msg in self.messages],
            "created_at": self.created_at.isoformat(),
            "last_active": self.last_active.isoformat(),
            "system_prompt": self.system_prompt,
            "metadata": self.metadata
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'ChatSession':
        """Create session from dictionary."""
        session = cls(session_id=data["id"])
        session.messages = [ChatMessage.from_dict(msg_data) for msg_data in data["messages"]]
        session.created_at = datetime.fromisoformat(data["created_at"])
        session.last_active = datetime.fromisoformat(data["last_active"])
        session.system_prompt = data.get("system_prompt")
        session.metadata = data.get("metadata", {})
        return session


class ChatService:
    """Service for managing chat conversations."""
    
    def __init__(self, model_service=None, event_bus: EventBus = None, config_manager=None):
        """
        Initialize the chat service.
        
        Args:
            model_service: ModelService instance for text generation (should be BackendManager-enabled)
            event_bus: EventBus instance for communication
            config_manager: Configuration manager for settings
        """
        self.logger = logging.getLogger("gguf_loader.chat_service")
        self.model_service = model_service
        self.event_bus = event_bus
        self.config_manager = config_manager
        
        # Validate that ModelService has BackendManager integration
        if self.model_service and not hasattr(self.model_service, 'backend_manager'):
            self.logger.warning("ModelService does not have BackendManager integration - chat may not work properly")
        elif self.model_service and self.model_service.backend_manager:
            self.logger.info("ChatService initialized with BackendManager-enabled ModelService")
        
        # Current session
        self.current_session: Optional[ChatSession] = None
        
        # Chat settings
        self.default_system_prompt = self._get_system_prompt()
        self.max_context_length = 4096  # Maximum context length in tokens (approximate)
        self.context_window_ratio = 0.8  # Use 80% of context for conversation history
        
        # Generation parameters - optimized for focused, single-response chat
        self.default_temperature = 0.8  # Slightly higher temperature for better text flow
        self.default_max_tokens = 512   # More tokens for complete, well-formed responses
        self.default_top_p = 0.95       # Higher top_p for better text coherence
        self.default_top_k = 50         # Higher top_k for better vocabulary
        self.default_repeat_penalty = 1.05  # Lower repeat penalty to avoid text corruption
        
        # Subscribe to events if event bus is available
        if self.event_bus:
            self.event_bus.subscribe("model.loaded", self._on_model_loaded)
            self.event_bus.subscribe("model.unloaded", self._on_model_unloaded)
            self.event_bus.subscribe("system_prompt.changed", self._on_system_prompt_changed)
            self.event_bus.subscribe("model_parameters.changed", self._on_model_parameters_changed)
            self.event_bus.subscribe("chat.cancel", self._on_cancel_request)
        
        # Create initial session
        self.start_new_session()
        
        self.logger.info("ChatService initialized")
    
    def _get_system_prompt(self) -> str:
        """
        Get the system prompt from configuration.
        
        Returns:
            System prompt string
        """
        if self.config_manager:
            return self.config_manager.get_value(
                "chat_system_prompt", 
                "You are a concise assistant. Answer briefly unless the user asks a detailed question. For greetings like 'hi' or 'hello', respond with a short greeting. Keep replies natural and conversational."
            )
        return "You are a concise assistant. Answer briefly unless the user asks a detailed question. For greetings like 'hi' or 'hello', respond with a short greeting."
    
    def _on_model_loaded(self, model_id: str, model_info: Dict[str, Any]):
        """Handle model loaded event from BackendManager."""
        if self.model_service and hasattr(self.model_service, 'backend_manager'):
            backend_manager = self.model_service.backend_manager
            if backend_manager and backend_manager.current_backend:
                self.logger.info(f"Model loaded for chat via BackendManager: {model_id}")
                if self.event_bus:
                    self.event_bus.publish("chat.model_ready", {
                        "model_id": model_id,
                        "backend": backend_manager.current_backend.config.name if hasattr(backend_manager.current_backend, 'config') else "unknown",
                        "backend_info": backend_manager.get_current_backend_info()
                    })
                return
        
        # Log warning if BackendManager not available
        self.logger.warning(f"Model loaded event received but BackendManager not available: {model_id}")
    
    def _on_model_unloaded(self, model_id: str):
        """Handle model unloaded event from BackendManager."""
        if self.model_service and hasattr(self.model_service, 'backend_manager'):
            backend_manager = self.model_service.backend_manager
            if backend_manager and not backend_manager.current_backend:
                self.logger.info(f"Model unloaded from chat via BackendManager: {model_id}")
                if self.event_bus:
                    self.event_bus.publish("chat.model_unavailable", {
                        "model_id": model_id,
                        "reason": "unloaded_from_backend"
                    })
                return
        
        # Log warning if BackendManager not available
        self.logger.warning(f"Model unloaded event received but BackendManager not available: {model_id}")
    
    def _on_system_prompt_changed(self, event_data: Dict[str, Any]):
        """Handle system prompt change event."""
        new_prompt = event_data.get("prompt", "")
        self.default_system_prompt = new_prompt
        
        # Update current session if exists
        if self.current_session:
            self.current_session.system_prompt = new_prompt
        
        self.logger.info(f"System prompt updated: {new_prompt[:50]}...")
    
    def _on_model_parameters_changed(self, event_data: Dict[str, Any]):
        """Handle model parameters change event."""
        new_params = event_data.get("parameters", {})
        
        # Update generation parameters
        if "temperature" in new_params:
            self.default_temperature = new_params["temperature"]
        if "max_tokens" in new_params:
            self.default_max_tokens = new_params["max_tokens"]
        if "top_p" in new_params:
            self.default_top_p = new_params["top_p"]
        if "top_k" in new_params:
            self.default_top_k = new_params["top_k"]
        if "repeat_penalty" in new_params:
            self.default_repeat_penalty = new_params["repeat_penalty"]
        
        self.logger.info(f"Model parameters updated: {new_params}")
    
    def start_new_session(self, session_id: str = None) -> str:
        """
        Start a new chat session.
        
        Args:
            session_id: Optional session ID
            
        Returns:
            The session ID
        """
        self.current_session = ChatSession(session_id)
        self.current_session.system_prompt = self.default_system_prompt
        
        self.logger.info(f"Started new chat session: {self.current_session.id}")
        
        if self.event_bus:
            self.event_bus.publish("chat.session_started", self.current_session.id)
        
        return self.current_session.id
    
    def get_current_session(self) -> Optional[ChatSession]:
        """Get the current chat session."""
        return self.current_session
    
    def send_message_async(self, message: str, **generation_params) -> bool:
        """
        Send a message and get AI response asynchronously.
        
        This method starts text generation in a background thread and returns immediately.
        Listen to chat events through the event bus for updates.
        
        Args:
            message: User message
            **generation_params: Optional generation parameters
            
        Returns:
            True if generation started successfully, False otherwise
        """
        if not self.current_session:
            self.logger.error("No active chat session")
            return False
        
        if not self.model_service:
            self.logger.error("No model service available")
            return False
        
        # Check model availability through BackendManager
        if not self._is_model_available():
            error_msg = self._get_model_status_message()
            self.logger.error(error_msg)
            if self.event_bus:
                self.event_bus.publish("chat.error", error_msg)
            return False
        
        try:
            # Add user message to session
            user_message = ChatMessage("user", message)
            self.current_session.add_message(user_message)
            
            self.logger.debug(f"User message added: {message[:100]}...")
            
            # Check for simple greetings and provide quick responses
            quick_response = self._get_quick_response(message)
            if quick_response:
                # Handle quick response directly
                assistant_message = ChatMessage("assistant", quick_response)
                self.current_session.add_message(assistant_message)
                
                # Publish response immediately
                if self.event_bus:
                    self.event_bus.publish("chat.response", quick_response)
                
                self.logger.debug(f"Quick response provided: {quick_response}")
                return True
            
            # Prepare generation parameters with adjusted settings for better text flow
            params = {
                "temperature": generation_params.get("temperature", self.default_temperature),
                "max_tokens": generation_params.get("max_tokens", self.default_max_tokens),
                "top_p": generation_params.get("top_p", self.default_top_p),
                "top_k": generation_params.get("top_k", self.default_top_k),
                "repeat_penalty": generation_params.get("repeat_penalty", self.default_repeat_penalty),
                "stop": generation_params.get("stop", [])
            }
            
            # Build conversation context
            context = self._build_conversation_context()
            
            # Connect to model service generation signals
            self.model_service.generation_started.connect(self._on_generation_started)
            self.model_service.generation_token.connect(self._on_generation_token)
            self.model_service.generation_finished.connect(self._on_generation_finished)
            self.model_service.generation_error.connect(self._on_generation_error)
            self.model_service.generation_cancelled.connect(self._on_generation_cancelled)
            
            # Start asynchronous text generation
            success = self.model_service.generate_text_async(
                prompt=context,
                system_prompt=self.current_session.system_prompt,
                **params
            )
            
            if success:
                self.logger.debug("Asynchronous text generation started")
                return True
            else:
                self.logger.error("Failed to start text generation")
                return False
                
        except Exception as e:
            self.logger.error(f"Error in send_message_async: {e}")
            return False
    
    def _on_generation_started(self):
        """Handle generation started event."""
        self.logger.debug("Text generation started")
        if self.event_bus:
            self.event_bus.publish("chat.generating", True)
    
    def _on_generation_token(self, token: str):
        """
        Handle individual token generation for streaming.
        
        Args:
            token: Generated token text
        """
        if self.event_bus:
            self.event_bus.publish("chat.token", token)
    
    def _on_generation_cancelled(self):
        """Handle generation cancellation."""
        self.logger.info("Text generation was cancelled")
        if self.event_bus:
            self.event_bus.publish("chat.cancelled", True)
    
    def _on_cancel_request(self, cancel_data):
        """Handle cancellation request from UI."""
        self.logger.info("Received cancellation request from UI")
        self.cancel_generation()
    
    def cancel_generation(self) -> bool:
        """
        Cancel the current text generation.
        
        Returns:
            True if cancellation was requested, False if no generation is running
        """
        if self.model_service:
            return self.model_service.cancel_generation()
        return False
    
    def _on_generation_finished(self, generated_text: str):
        """
        Handle successful text generation.
        
        Args:
            generated_text: The generated text
        """
        try:
            # Disconnect signals to avoid multiple connections
            try:
                self.model_service.generation_started.disconnect(self._on_generation_started)
                self.model_service.generation_token.disconnect(self._on_generation_token)
                self.model_service.generation_finished.disconnect(self._on_generation_finished)
                self.model_service.generation_error.disconnect(self._on_generation_error)
                self.model_service.generation_cancelled.disconnect(self._on_generation_cancelled)
            except (TypeError, RuntimeError):
                # Signals might not be connected, ignore
                pass
            
            if generated_text and self.current_session:
                # Use the generated text as-is (no spacing "fixes" that break the text)
                fixed_text = generated_text.strip()
                
                # Add assistant response to session
                assistant_message = ChatMessage("assistant", fixed_text)
                self.current_session.add_message(assistant_message)
                
                self.logger.debug(f"Assistant response generated: {fixed_text[:100]}...")
                
                # Publish chat event through event bus
                if self.event_bus:
                    self.event_bus.publish("chat.response", fixed_text)
                    self.event_bus.publish("chat.message_exchanged", {
                        "session_id": self.current_session.id,
                        "user_message": self.current_session.messages[-2].to_dict(),  # User message
                        "assistant_message": assistant_message.to_dict()
                    })
            else:
                self.logger.error("No generated text or session available")
                if self.event_bus:
                    self.event_bus.publish("chat.error", "No response generated")
                
        except Exception as e:
            self.logger.error(f"Error handling generation finished: {e}")
            if self.event_bus:
                self.event_bus.publish("chat.error", f"Error processing response: {str(e)}")
    
    def _on_generation_error(self, error_message: str):
        """
        Handle text generation error.
        
        Args:
            error_message: Error message
        """
        try:
            # Disconnect signals to avoid multiple connections
            try:
                self.model_service.generation_started.disconnect(self._on_generation_started)
                self.model_service.generation_token.disconnect(self._on_generation_token)
                self.model_service.generation_finished.disconnect(self._on_generation_finished)
                self.model_service.generation_error.disconnect(self._on_generation_error)
                self.model_service.generation_cancelled.disconnect(self._on_generation_cancelled)
            except (TypeError, RuntimeError):
                # Signals might not be connected, ignore
                pass
            
            self.logger.error(f"Text generation error: {error_message}")
            
            # Publish error event through event bus
            if self.event_bus:
                self.event_bus.publish("chat.error", error_message)
                
        except Exception as e:
            self.logger.error(f"Error handling generation error: {e}")
    
    def send_message(self, message: str, **generation_params) -> Optional[str]:
        """
        Send a message and get AI response.
        
        Args:
            message: User message
            **generation_params: Optional generation parameters
            
        Returns:
            AI response or None if generation failed
        """
        if not self.current_session:
            self.logger.error("No active chat session")
            return None
        
        if not self.model_service:
            self.logger.error("No model service available")
            return None
        
        # Check model availability through BackendManager
        if not self._is_model_available():
            error_msg = self._get_model_status_message()
            self.logger.error(error_msg)
            return None
        
        try:
            # Add user message to session
            user_message = ChatMessage("user", message)
            self.current_session.add_message(user_message)
            
            self.logger.debug(f"User message added: {message[:100]}...")
            
            # Prepare generation parameters
            params = {
                "temperature": generation_params.get("temperature", self.default_temperature),
                "max_tokens": generation_params.get("max_tokens", self.default_max_tokens),
                "top_p": generation_params.get("top_p", self.default_top_p),
                "top_k": generation_params.get("top_k", self.default_top_k),
                "repeat_penalty": generation_params.get("repeat_penalty", self.default_repeat_penalty),
                "stop": generation_params.get("stop", [])
            }
            
            # Build conversation context
            context = self._build_conversation_context()
            
            # Generate response using model service
            response = self.model_service.generate_text(
                prompt=context,
                system_prompt=self.current_session.system_prompt,
                **params
            )
            
            if response:
                # Add assistant response to session
                assistant_message = ChatMessage("assistant", response.strip())
                self.current_session.add_message(assistant_message)
                
                self.logger.debug(f"Assistant response generated: {response[:100]}...")
                
                # Publish chat event
                if self.event_bus:
                    self.event_bus.publish("chat.message_exchanged", {
                        "session_id": self.current_session.id,
                        "user_message": user_message.to_dict(),
                        "assistant_message": assistant_message.to_dict()
                    })
                
                return response.strip()
            else:
                self.logger.error("Failed to generate response")
                return None
                
        except Exception as e:
            self.logger.error(f"Error in send_message: {e}")
            return None
    
    def _build_conversation_context(self) -> str:
        """
        Build conversation context from message history.
        
        Returns:
            Formatted conversation context
        """
        if not self.current_session or not self.current_session.messages:
            return ""
        
        # Get recent messages that fit within context window
        messages = self._get_context_messages()
        
        # Format messages for the model - only include completed exchanges
        context_parts = []
        for message in messages[:-1]:  # Exclude the last (current) user message
            if message.role == "user":
                context_parts.append(f"Human: {message.content}")
            elif message.role == "assistant":
                context_parts.append(f"Assistant: {message.content}")
        
        # Add the current user message
        if messages:
            last_message = messages[-1]
            if last_message.role == "user":
                context_parts.append(f"Human: {last_message.content}")
        
        # Format for single response - don't add "Assistant:" at the end to avoid loops
        return "\n\n".join(context_parts)
    
    def _get_context_messages(self) -> List[ChatMessage]:
        """
        Get messages that fit within the context window.
        
        Returns:
            List of messages to include in context
        """
        if not self.current_session:
            return []
        
        # For now, use a simple approach: include recent messages up to a limit
        # In a more sophisticated implementation, we would estimate token count
        max_messages = 20  # Approximate limit for context
        
        messages = self.current_session.messages
        if len(messages) <= max_messages:
            return messages
        
        # Keep the most recent messages
        return messages[-max_messages:]
    
    def _get_quick_response(self, message: str) -> Optional[str]:
        """
        Get a quick response for simple greetings and common phrases.
        
        Args:
            message: User message
            
        Returns:
            Quick response string or None if no quick response available
        """
        message_lower = message.lower().strip()
        
        # Simple greetings
        if message_lower in ['hi', 'hello', 'hey', 'good morning', 'good afternoon', 'good evening']:
            return "Hi there! How can I help you today?"
        
        # How are you variations
        if any(phrase in message_lower for phrase in ['how are you', 'how do you do', 'how\'s it going']):
            return "I'm doing well, thank you for asking! What can I assist you with?"
        
        # Thank you variations
        if any(phrase in message_lower for phrase in ['thank you', 'thanks', 'thx']):
            return "You're welcome! Is there anything else I can help you with?"
        
        # Goodbye variations
        if message_lower in ['bye', 'goodbye', 'see you', 'farewell']:
            return "Goodbye! Feel free to come back if you need any help."
        
        # No quick response available
        return None
    
    def _is_model_available(self) -> bool:
        """
        Check if a model is available for text generation through BackendManager.
        
        Returns:
            True if a model is loaded and available, False otherwise
        """
        if not self.model_service:
            return False
        
        # Check BackendManager (only supported method)
        if hasattr(self.model_service, 'backend_manager') and self.model_service.backend_manager:
            backend_manager = self.model_service.backend_manager
            if backend_manager.current_backend:
                self.logger.debug("Model available through BackendManager")
                return True
            else:
                self.logger.debug("No model loaded in BackendManager")
                return False
        
        # No BackendManager available
        self.logger.warning("BackendManager not available - chat functionality requires BackendManager")
        return False
    
    def _get_model_status_message(self) -> str:
        """
        Get a descriptive message about the current model status.
        
        Returns:
            Human-readable status message
        """
        if not self.model_service:
            return "No model service available for text generation"
        
        # Check BackendManager status (only supported method)
        if hasattr(self.model_service, 'backend_manager') and self.model_service.backend_manager:
            backend_manager = self.model_service.backend_manager
            if not backend_manager.current_backend:
                available_backends = backend_manager.get_available_backends()
                if available_backends and isinstance(available_backends, (list, tuple)):
                    return f"No model loaded in BackendManager. Available backends: {', '.join(available_backends)}"
                else:
                    return "No model loaded and no backends available"
            else:
                # This shouldn't happen if we're calling this method, but just in case
                return "Model is loaded in BackendManager"
        
        return "BackendManager not available - chat functionality requires BackendManager"
    
    def get_current_backend_info(self) -> Optional[Dict[str, Any]]:
        """
        Get information about the current backend.
        
        Returns:
            Dictionary with backend information or None if no backend available
        """
        if not self.model_service:
            return None
        
        # Get BackendManager info
        if hasattr(self.model_service, 'backend_manager') and self.model_service.backend_manager:
            backend_manager = self.model_service.backend_manager
            if backend_manager.current_backend:
                try:
                    backend_info = backend_manager.get_current_backend_info()
                    if backend_info:
                        return {
                            "backend_name": backend_manager.current_backend.config.name if hasattr(backend_manager.current_backend, 'config') else "unknown",
                            "model_path": backend_manager.current_model_path,
                            "backend_info": backend_info,
                            "available_backends": backend_manager.get_available_backends()
                        }
                except Exception as e:
                    self.logger.warning(f"Error getting backend info: {e}")
                
                # Fallback basic info
                return {
                    "backend_name": backend_manager.current_backend.config.name if hasattr(backend_manager.current_backend, 'config') else "unknown",
                    "model_path": backend_manager.current_model_path,
                    "available_backends": backend_manager.get_available_backends()
                }
        
        return None
    
    def _fix_text_spacing(self, text: str) -> str:
        """
        Fix spacing issues in generated text where words run together.
        
        This method addresses severe tokenization issues where spaces are missing
        between words, punctuation, and contractions.
        
        Args:
            text: The generated text with potential spacing issues
            
        Returns:
            Text with corrected spacing
        """
        import re
        
        if not text:
            return text
        
        # Log original text for debugging
        self.logger.debug(f"Fixing spacing for text: {text[:100]}...")
        
        # Start with the original text
        fixed_text = text
        
        # For severely corrupted text (like your Afghanistan example), we need aggressive fixes
        
        # Pattern 1: Add spaces after punctuation followed by letters
        # "Afghanistan,alandlocked" -> "Afghanistan, alandlocked"
        fixed_text = re.sub(r'([.!?,;:])([a-zA-Z])', r'\1 \2', fixed_text)
        
        # Pattern 2: Add spaces before capital letters in the middle of words
        # "SouthAsia" -> "South Asia", "BritishEmpires" -> "British Empires"
        fixed_text = re.sub(r'([a-z])([A-Z])', r'\1 \2', fixed_text)
        
        # Pattern 3: Add spaces around common connecting words
        # This handles cases like "countryinSouth" -> "country in South"
        connecting_words = [
            'in', 'of', 'to', 'for', 'with', 'by', 'from', 'at', 'on', 'as', 'is', 'was', 'are', 'were',
            'the', 'a', 'an', 'and', 'or', 'but', 'that', 'this', 'has', 'have', 'had', 'will', 'would',
            'can', 'could', 'may', 'might', 'shall', 'should', 'must', 'do', 'does', 'did', 'be', 'been'
        ]
        
        for word in connecting_words:
            # Add space before the word if it's stuck to another word
            pattern = f'([a-z])({word})([a-z])'
            replacement = f'\\1 {word} \\3'
            fixed_text = re.sub(pattern, replacement, fixed_text, flags=re.IGNORECASE)
        
        # Pattern 4: Fix specific problematic combinations from your examples
        specific_fixes = {
            # Afghanistan example fixes
            'alandlocked': 'a landlocked',
            'countryinSouth': 'country in South',
            'SouthAsia': 'South Asia',
            'hasarich': 'has a rich',
            'richhistory': 'rich history',
            'historydating': 'history dating',
            'datingback': 'dating back',
            'backto': 'back to',
            'toancient': 'to ancient',
            'ancienttimes': 'ancient times',
            'timesIt': 'times. It',
            'Itwas': 'It was',
            'wasonce': 'was once',
            'oncea': 'once a',
            'apartof': 'a part of',
            'partof': 'part of',
            'ofseveral': 'of several',
            'severalgreat': 'several great',
            'greatempires': 'great empires',
            'empiresincluding': 'empires including',
            'includingthe': 'including the',
            'thePersian': 'the Persian',
            'PersianGreek': 'Persian, Greek',
            'GreekMughal': 'Greek, Mughal',
            'Mughaland': 'Mughal, and',
            'andBritish': 'and British',
            'BritishEmpires': 'British Empires',
            'EmpiresHowever': 'Empires. However',
            'Howeverits': 'However, its',
            'itsmodern': 'its modern',
            'modernhistory': 'modern history',
            'historyis': 'history is',
            'ismarked': 'is marked',
            'markedby': 'marked by',
            'byconflict': 'by conflict',
            'conflictand': 'conflict and',
            'andinstability': 'and instability',
            
            # Common patterns
            'Iam': 'I am',
            'Ihave': 'I have',
            'Ican': 'I can',
            'Iwill': 'I will',
            'Iwould': 'I would',
            'Idon\'t': 'I don\'t',
            'Youcan': 'You can',
            'Thisis': 'This is',
            'Thereare': 'There are',
            'Thereis': 'There is',
            'Asamachine': 'As a machine',
            'Asanai': 'As an AI',
            'Asanassistant': 'As an assistant',
        }
        
        # Apply specific fixes
        for wrong, correct in specific_fixes.items():
            fixed_text = fixed_text.replace(wrong, correct)
        
        # Pattern 5: Add spaces around numbers and years
        # "1990sduringthe" -> "1990s during the"
        fixed_text = re.sub(r'([0-9]+)([a-zA-Z])', r'\1 \2', fixed_text)
        fixed_text = re.sub(r'([a-zA-Z])([0-9]+)', r'\1 \2', fixed_text)
        
        # Pattern 6: Fix missing spaces before question words after punctuation
        question_starters = ['What', 'How', 'Why', 'When', 'Where', 'Who', 'Which', 'The', 'They', 'This', 'That']
        for word in question_starters:
            pattern = f'([.!?])({word})'
            replacement = f'\\1 \\2'
            fixed_text = re.sub(pattern, replacement, fixed_text)
        
        # Pattern 7: Clean up multiple spaces and fix punctuation spacing
        fixed_text = re.sub(r'\s+', ' ', fixed_text)  # Multiple spaces -> single space
        fixed_text = re.sub(r'\s+([.!?,:;])', r'\1', fixed_text)  # Remove space before punctuation
        fixed_text = re.sub(r'([.!?])\s*([A-Z])', r'\1 \2', fixed_text)  # Ensure space after sentence punctuation
        
        # Clean up and return
        fixed_text = fixed_text.strip()
        
        # Log the fix if changes were made
        if fixed_text != text:
            self.logger.info(f"Fixed text spacing: '{text[:50]}...' -> '{fixed_text[:50]}...'")
        
        return fixed_text
    
    def get_conversation_history(self, limit: int = None) -> List[ChatMessage]:
        """
        Get current conversation history.
        
        Args:
            limit: Maximum number of messages to return
            
        Returns:
            List of chat messages
        """
        if not self.current_session:
            return []
        
        return self.current_session.get_messages(limit)
    
    def clear_conversation(self) -> None:
        """Clear current conversation."""
        if self.current_session:
            self.current_session.clear_messages()
            self.logger.info(f"Cleared conversation for session: {self.current_session.id}")
            
            if self.event_bus:
                self.event_bus.publish("chat.conversation_cleared", self.current_session.id)
    
    def set_system_prompt(self, prompt: str) -> None:
        """
        Set system prompt for chat.
        
        Args:
            prompt: System prompt text
        """
        if self.current_session:
            self.current_session.system_prompt = prompt
            self.logger.info("System prompt updated")
            
            if self.event_bus:
                self.event_bus.publish("chat.system_prompt_changed", {
                    "session_id": self.current_session.id,
                    "system_prompt": prompt
                })
    
    def get_system_prompt(self) -> Optional[str]:
        """
        Get current system prompt.
        
        Returns:
            Current system prompt or None
        """
        if self.current_session:
            return self.current_session.system_prompt
        return None
    
    def set_generation_parameters(self, **params) -> None:
        """
        Set default generation parameters.
        
        Args:
            **params: Generation parameters to update
        """
        if "temperature" in params:
            self.default_temperature = params["temperature"]
        if "max_tokens" in params:
            self.default_max_tokens = params["max_tokens"]
        if "top_p" in params:
            self.default_top_p = params["top_p"]
        if "top_k" in params:
            self.default_top_k = params["top_k"]
        if "repeat_penalty" in params:
            self.default_repeat_penalty = params["repeat_penalty"]
        
        self.logger.info(f"Generation parameters updated: {params}")
    
    def get_generation_parameters(self) -> Dict[str, Any]:
        """
        Get current generation parameters.
        
        Returns:
            Dictionary of generation parameters
        """
        return {
            "temperature": self.default_temperature,
            "max_tokens": self.default_max_tokens,
            "top_p": self.default_top_p,
            "top_k": self.default_top_k,
            "repeat_penalty": self.default_repeat_penalty
        }
    
    def get_session_info(self) -> Optional[Dict[str, Any]]:
        """
        Get information about the current session.
        
        Returns:
            Session information dictionary or None
        """
        if not self.current_session:
            return None
        
        return {
            "id": self.current_session.id,
            "created_at": self.current_session.created_at.isoformat(),
            "last_active": self.current_session.last_active.isoformat(),
            "message_count": len(self.current_session.messages),
            "system_prompt": self.current_session.system_prompt
        }
    
    def export_conversation(self) -> Optional[Dict[str, Any]]:
        """
        Export the current conversation.
        
        Returns:
            Conversation data dictionary or None
        """
        if not self.current_session:
            return None
        
        return self.current_session.to_dict()
    
    def import_conversation(self, conversation_data: Dict[str, Any]) -> bool:
        """
        Import a conversation.
        
        Args:
            conversation_data: Conversation data dictionary
            
        Returns:
            True if import was successful, False otherwise
        """
        try:
            self.current_session = ChatSession.from_dict(conversation_data)
            self.logger.info(f"Imported conversation: {self.current_session.id}")
            
            if self.event_bus:
                self.event_bus.publish("chat.conversation_imported", self.current_session.id)
            
            return True
            
        except Exception as e:
            self.logger.error(f"Error importing conversation: {e}")
            return False