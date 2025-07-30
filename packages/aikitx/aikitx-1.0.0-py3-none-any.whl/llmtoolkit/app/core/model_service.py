"""
Model Service

This module provides a service for loading and managing GGUF models using llama.cpp.
"""

import os
import logging
import threading
from typing import Dict, Optional, Any, List
from datetime import datetime

from PySide6.QtCore import QObject, Signal, QThread

from llmtoolkit.app.models.gguf_model import GGUFModel
from llmtoolkit.app.core.event_bus import EventBus
from llmtoolkit.app.core.model_backends import GenerationConfig

class TextGenerationThread(QThread):
    """Thread for generating text in the background with improved spacing and streaming support."""
    
    # Signals
    progress = Signal(str)  # Progress message
    token_generated = Signal(str)  # Individual token generated (for streaming)
    finished = Signal(str)  # Complete generated text on success
    error = Signal(str)  # Error message on failure
    cancelled = Signal()  # Generation was cancelled
    
    def __init__(self, model, prompt: str, system_prompt: str = None, 
                 temperature: float = 0.7, max_tokens: int = 512, 
                 top_p: float = 0.9, top_k: int = 40, 
                 repeat_penalty: float = 1.1, stop: List[str] = None, 
                 stream: bool = True):
        """
        Initialize the text generation thread with improved tokenization.
        
        Args:
            model: The loaded GGUFModel instance
            prompt: Input prompt for text generation
            system_prompt: Optional system prompt to prepend
            temperature: Sampling temperature (0.0 to 2.0)
            max_tokens: Maximum number of tokens to generate
            top_p: Top-p sampling parameter
            top_k: Top-k sampling parameter
            repeat_penalty: Repetition penalty
            stop: List of stop sequences
            stream: Whether to stream tokens in real-time
        """
        super().__init__()
        self.model = model
        self.prompt = prompt
        self.system_prompt = system_prompt
        self.temperature = temperature
        self.max_tokens = max_tokens
        self.top_p = top_p
        self.top_k = top_k
        self.repeat_penalty = repeat_penalty
        self.stream = stream
        self._cancelled = False
        self.logger = logging.getLogger("gguf_loader.model_service.generation")
        
        # Improved stop tokens for better conversation flow
        default_stop_tokens = [
            "<|im_end|>", "</s>", "user:", "assistant:", "###",
            "\nHuman:", "\nUser:", "Human:", "User:",
            "\n\nUser:", "\n\nHuman:"
        ]
        self.stop = stop or default_stop_tokens
    
    def cancel(self):
        """Cancel the text generation."""
        self._cancelled = True
    
    def _format_prompt(self) -> str:
        """Format the prompt with improved structure for better spacing."""
        if self.system_prompt:
            # Use improved prompt formatting
            formatted = f"{self.system_prompt}\n\n"
            formatted += "Answer clearly and concisely.\n\n"
            formatted += f"User: {self.prompt}\nAssistant: "
            return formatted
        else:
            # Simple format without system prompt
            return f"User: {self.prompt}\nAssistant: "
    
    def run(self):
        """Run the text generation process with improved spacing handling."""
        try:
            if self._cancelled:
                self.cancelled.emit()
                return
                
            self.progress.emit("Preparing prompt...")
            
            # Format the prompt with improved structure
            full_prompt = self._format_prompt()
            
            # Get the llama model instance
            llama_model = getattr(self.model, '_llama_model', None)
            if not llama_model:
                self.error.emit("Model not properly loaded with llama.cpp")
                return
            
            if self._cancelled:
                self.cancelled.emit()
                return
            
            self.progress.emit("Generating response...")
            self.logger.debug(f"Generating text with formatted prompt: {full_prompt[:100]}...")
            
            if self.stream:
                # Stream generation with simple token handling - trust llama.cpp's tokenization
                generated_text = ""
                
                # Use llama.cpp streaming API with simple token handling
                try:
                    stream = llama_model(
                        full_prompt,
                        max_tokens=self.max_tokens,
                        temperature=self.temperature,
                        top_p=self.top_p,
                        top_k=self.top_k,
                        repeat_penalty=self.repeat_penalty,
                        stop=self.stop,
                        echo=False,
                        stream=True  # Enable streaming
                    )
                    
                    for token_data in stream:
                        if self._cancelled:
                            self.cancelled.emit()
                            return
                        
                        # Get both token text and token ID for proper reconstruction
                        choice = token_data.get('choices', [{}])[0]
                        token_text = choice.get('text', '')
                        token_id = choice.get('token', None)
                        
                        # Only process non-empty tokens
                        if token_text or token_id is not None:
                            # Use llama_token_to_str() to get the exact token representation with embedded spaces
                            if token_id is not None:
                                try:
                                    # Use llama.cpp's token_to_str to preserve embedded spaces
                                    if hasattr(llama_model, 'token_to_str'):
                                        proper_token_text = llama_model.token_to_str(token_id)
                                    elif hasattr(llama_model, 'detokenize'):
                                        # Alternative method for some llama.cpp versions
                                        proper_token_text = llama_model.detokenize([token_id]).decode('utf-8', errors='ignore')
                                    else:
                                        # Fallback to original text if no tokenizer method available
                                        proper_token_text = token_text
                                    
                                    # Use the properly decoded token text
                                    if proper_token_text:
                                        token_text = proper_token_text
                                        
                                except Exception as e:
                                    # If token reconstruction fails, use original text
                                    self.logger.debug(f"Token reconstruction failed for token {token_id}: {e}")
                                    # token_text remains as the original fallback
                            
                            # Handle tokenizer space-prefix behavior
                            # Some tokenizers add unwanted leading spaces after special tokens
                            if token_text and len(generated_text) == 0 and token_text.startswith(' '):
                                # Remove leading space at the very beginning of generation
                                token_text = token_text.lstrip(' ')
                            
                            if token_text:  # Only process if we have actual content
                                # Accumulate the properly decoded text
                                generated_text += token_text
                                
                                # Check for stop patterns in accumulated text
                                if any(stop.lower() in generated_text.lower() for stop in self.stop):
                                    break
                                
                                # Emit the properly decoded token with preserved spacing
                                self.token_generated.emit(token_text)
                
                except Exception as stream_error:
                    self.logger.error(f"Streaming error: {stream_error}")
                    # Fall back to non-streaming if streaming fails
                    self.logger.info("Falling back to non-streaming generation")
                    response = llama_model(
                        full_prompt,
                        max_tokens=self.max_tokens,
                        temperature=self.temperature,
                        top_p=self.top_p,
                        top_k=self.top_k,
                        repeat_penalty=self.repeat_penalty,
                        stop=self.stop,
                        echo=False,
                        stream=False
                    )
                    generated_text = response['choices'][0]['text']
                    # Emit the complete text as a single token for fallback
                    self.token_generated.emit(generated_text)
                
                # Update model access time
                self.model.access()
                
                self.logger.debug(f"Generated {len(generated_text)} characters (streamed)")
                self.finished.emit(generated_text)
                
            else:
                # Non-streaming generation (fallback)
                response = llama_model(
                    full_prompt,
                    max_tokens=self.max_tokens,
                    temperature=self.temperature,
                    top_p=self.top_p,
                    top_k=self.top_k,
                    repeat_penalty=self.repeat_penalty,
                    stop=self.stop,
                    echo=False
                )
                
                if self._cancelled:
                    self.cancelled.emit()
                    return
                
                # Extract the generated text
                generated_text = response['choices'][0]['text']
                
                # Update model access time
                self.model.access()
                
                self.logger.debug(f"Generated {len(generated_text)} characters")
                self.finished.emit(generated_text)
            
        except Exception as e:
            if not self._cancelled:
                self.logger.error(f"Error generating text: {e}")
                self.error.emit(str(e))


class ModelLoadingThread(QThread):
    """Thread for loading models in the background with detailed progress reporting."""
    
    # Signals
    progress = Signal(int)  # Progress percentage (0-100)
    progress_message = Signal(str)  # Detailed progress message
    memory_usage = Signal(int)  # Current memory usage in MB
    finished = Signal(object)  # GGUFModel object on success
    error = Signal(str)  # Error message on failure
    cancelled = Signal()  # Loading was cancelled
    
    def __init__(self, file_path: str, load_type: str = None, hardware_config: Dict[str, Any] = None):
        """
        Initialize the model loading thread.
        
        Args:
            file_path: Path to the GGUF model file
            load_type: Loading type (optional)
            hardware_config: Hardware configuration settings
        """
        super().__init__()
        self.file_path = file_path
        self.load_type = load_type
        self.hardware_config = hardware_config or {}
        self._cancelled = False
        self.logger = logging.getLogger("gguf_loader.model_service.thread")
    
    def cancel(self):
        """Cancel the model loading process."""
        self._cancelled = True
        self.logger.info("Model loading cancellation requested")
    
    def run(self):
        """Run the model loading process with detailed progress reporting."""
        try:
            if self._cancelled:
                self.cancelled.emit()
                return
                
            self.logger.info(f"Starting to load model: {self.file_path}")
            self.logger.info(f"Hardware configuration: {self.hardware_config}")
            
            # Step 1: Initialize model object
            self.progress.emit(5)
            self.progress_message.emit("Initializing model...")
            
            if self._cancelled:
                self.cancelled.emit()
                return
                
            model = GGUFModel(self.file_path)
            
            # Report initial memory usage
            import psutil
            process = psutil.Process()
            initial_memory = process.memory_info().rss // (1024 * 1024)  # MB
            self.memory_usage.emit(initial_memory)
            
            # Step 2: Apply hardware configuration
            self.progress.emit(10)
            self.progress_message.emit("Configuring hardware settings...")
            
            if self._cancelled:
                self.cancelled.emit()
                return
                
            if self.hardware_config:
                model.hardware_settings = self._convert_hardware_config(self.hardware_config)
                self.logger.info(f"Applied hardware settings to model: {model.hardware_settings}")
            
            # Step 3: Validate the model file
            self.progress.emit(20)
            self.progress_message.emit("Validating model file...")
            
            if self._cancelled:
                self.cancelled.emit()
                return
                
            is_valid, error = model.validate()
            if not is_valid:
                self.error.emit(f"Model validation failed: {error}")
                return
            
            # Step 4: Extract metadata
            self.progress.emit(30)
            self.progress_message.emit("Extracting model metadata...")
            
            if self._cancelled:
                self.cancelled.emit()
                return
                
            if not model.extract_metadata():
                self.logger.warning("Failed to extract metadata, continuing with basic info")
            
            # Report memory usage after metadata extraction
            current_memory = process.memory_info().rss // (1024 * 1024)  # MB
            self.memory_usage.emit(current_memory)
            
            # Step 5: Prepare environment for model loading
            self.progress.emit(50)
            self.progress_message.emit("Preparing model loading environment...")
            
            if self._cancelled:
                self.cancelled.emit()
                return
            
            # Apply environment variables if provided
            original_env = {}
            env_vars = self.hardware_config.get('env_vars', {})
            if env_vars:
                for key, value in env_vars.items():
                    if key in os.environ:
                        original_env[key] = os.environ[key]
                    os.environ[key] = value
                    self.logger.debug(f"Set environment variable: {key}={value}")
            
            # Step 6: Load the model using llama.cpp
            self.progress.emit(60)
            backend = self.hardware_config.get('backend', 'cpu')
            gpu_layers = self.hardware_config.get('n_gpu_layers', 0)
            
            if backend != 'cpu' and gpu_layers > 0:
                self.progress_message.emit(f"Loading model with {backend.upper()} acceleration ({gpu_layers} GPU layers)...")
            else:
                self.progress_message.emit("Loading model with CPU...")
            
            if self._cancelled:
                self.cancelled.emit()
                return
            
            try:
                # Monitor memory during loading
                def memory_monitor():
                    """Monitor memory usage during model loading."""
                    import time
                    while not self._cancelled and not getattr(self, '_loading_complete', False):
                        try:
                            current_mem = process.memory_info().rss // (1024 * 1024)  # MB
                            self.memory_usage.emit(current_mem)
                            time.sleep(0.5)  # Update every 500ms
                        except:
                            break
                
                # Start memory monitoring in a separate thread
                import threading
                monitor_thread = threading.Thread(target=memory_monitor, daemon=True)
                monitor_thread.start()
                
                # Load the model
                if not model.load(self.load_type):
                    self._loading_complete = True
                    self.error.emit("Failed to load model with llama.cpp")
                    return
                
                self._loading_complete = True
                
            finally:
                # Restore original environment variables
                for key in env_vars.keys():
                    if key in original_env:
                        os.environ[key] = original_env[key]
                    elif key in os.environ:
                        del os.environ[key]
            
            if self._cancelled:
                self.cancelled.emit()
                return
            
            # Step 7: Finalize and report completion
            self.progress.emit(90)
            self.progress_message.emit("Finalizing model initialization...")
            
            # Final memory usage report
            final_memory = process.memory_info().rss // (1024 * 1024)  # MB
            self.memory_usage.emit(final_memory)
            
            # Calculate memory increase
            memory_increase = final_memory - initial_memory
            self.logger.info(f"Model loading increased memory usage by {memory_increase} MB")
            
            # Complete
            self.progress.emit(100)
            self.progress_message.emit(f"Model loaded successfully: {model.name}")
            self.logger.info(f"Model loaded successfully: {model.name}")
            self.finished.emit(model)
            
        except Exception as e:
            if not self._cancelled:
                self.logger.exception(f"Error loading model: {e}")
                self.error.emit(str(e))
            else:
                self.cancelled.emit()
    
    def _convert_hardware_config(self, config):
        """
        Convert hardware configuration to model hardware settings.
        
        Args:
            config: Hardware configuration from GPU acceleration system
            
        Returns:
            Hardware settings dictionary for the model
        """
        # The config already comes in the correct format from GPUAcceleration
        # Just pass it through with some logging
        backend = config.get("backend", "cpu")
        gpu_layers = config.get("n_gpu_layers", 0)
        threads = config.get("n_threads", 4)
        
        if backend != "cpu" and gpu_layers > 0:
            self.logger.info(f"Configured for {backend.upper()}: {gpu_layers} GPU layers, {threads} CPU threads")
        else:
            self.logger.info(f"Configured for CPU: {threads} threads")
        
        return config

class ModelService(QObject):
    """Service for managing GGUF models."""
    
    # Signals
    model_loaded = Signal(str, dict)  # model_id, model_info
    model_unloaded = Signal(str)  # model_id
    loading_progress = Signal(int)  # progress percentage
    loading_progress_message = Signal(str)  # detailed progress message
    loading_memory_usage = Signal(int)  # memory usage in MB
    loading_error = Signal(str)  # error message
    loading_cancelled = Signal()  # loading was cancelled
    
    # Text generation signals
    generation_started = Signal()  # Generation started
    generation_progress = Signal(str)  # Progress message
    generation_token = Signal(str)  # Individual token generated (streaming)
    generation_finished = Signal(str)  # Generated text
    generation_error = Signal(str)  # Error message
    generation_cancelled = Signal()  # Generation was cancelled
    
    def __init__(self, event_bus: EventBus, backend_manager=None, config_manager=None):
        """
        Initialize the model service.
        
        Args:
            event_bus: Application event bus
            backend_manager: BackendManager instance for model operations
            config_manager: Configuration manager for settings
        """
        super().__init__()
        self.logger = logging.getLogger("gguf_loader.model_service")
        self.event_bus = event_bus
        self.backend_manager = backend_manager
        self.config_manager = config_manager
        
        # Current loaded models
        self.loaded_models: Dict[str, GGUFModel] = {}
        self.current_model_id: Optional[str] = None
        
        # Loading thread
        self.loading_thread: Optional[ModelLoadingThread] = None
        
        # Text generation thread
        self.generation_thread: Optional[TextGenerationThread] = None
        
        # Subscribe to events
        self.event_bus.subscribe("model.load.request", self._handle_load_request)
        self.event_bus.subscribe("model.unload.request", self._handle_unload_request)
        self.event_bus.subscribe("model.load.cancel", self._handle_cancel_request)
        
        # Connect signals to event bus
        self.loading_progress.connect(lambda p: self.event_bus.publish("model.loading.progress", p))
        self.loading_progress_message.connect(lambda m: self.event_bus.publish("model.loading.progress_message", m))
        self.loading_memory_usage.connect(lambda m: self.event_bus.publish("model.loading.memory_usage", m))
        self.loading_cancelled.connect(lambda: self.event_bus.publish("model.loading.cancelled", {}))
        
        self.logger.info("ModelService initialized")
    
    def _handle_load_request(self, request_data: Dict[str, Any]):
        """
        Handle model load request.
        
        Args:
            request_data: Dictionary containing file_path and optional parameters
        """
        file_path = request_data.get("file_path")
        if not file_path:
            self.loading_error.emit("No file path provided")
            return
        
        load_type = request_data.get("load_type", "mmap")  # Default to memory-mapped
        
        self.logger.info(f"Received model load request: {file_path}")
        
        # Get hardware configuration from settings
        hardware_config = self._get_hardware_config()
        
        # Stop any existing loading
        if self.loading_thread and self.loading_thread.isRunning():
            self.loading_thread.terminate()
            self.loading_thread.wait()
        
        # Start loading in background thread
        self.loading_thread = ModelLoadingThread(file_path, load_type, hardware_config)
        self.loading_thread.progress.connect(self.loading_progress.emit)
        self.loading_thread.progress_message.connect(self.loading_progress_message.emit)
        self.loading_thread.memory_usage.connect(self.loading_memory_usage.emit)
        self.loading_thread.finished.connect(self._on_model_loaded)
        self.loading_thread.error.connect(self._on_loading_error)
        self.loading_thread.cancelled.connect(self.loading_cancelled.emit)
        self.loading_thread.start()
    
    def _get_hardware_config(self) -> Dict[str, Any]:
        """
        Get hardware configuration with LM Studio-style GPU acceleration.
        
        Returns:
            Dictionary containing llama.cpp configuration
        """
        # Initialize GPU acceleration if needed
        if not hasattr(self, '_gpu_accel'):
            from llmtoolkit.app.core.gpu_acceleration import GPUAcceleration
            self._gpu_accel = GPUAcceleration(config_manager=self.config_manager)
        
        # Get user preferences
        processing_unit = "auto"
        gpu_layers = None
        
        if self.config_manager:
            processing_unit = self.config_manager.get_value("processing_unit", "auto")
            gpu_layers = self.config_manager.get_value("gpu_layers", None)
        
        # Get model configuration from GPU acceleration system
        config = self._gpu_accel.get_model_config(processing_unit, gpu_layers)
        
        # Get environment variables and add them to config
        env_vars = self._gpu_accel.get_environment_variables(processing_unit)
        config['env_vars'] = env_vars
        
        # Log acceleration info
        self._gpu_accel.log_acceleration_info(processing_unit, gpu_layers)
        
        return config
    
    def _determine_processing_unit(self, user_preference: str) -> str:
        """
        Determine the actual processing unit to use based on user preference and GPU availability.
        
        Args:
            user_preference: User's preference ("auto", "cpu", "gpu")
            
        Returns:
            Actual processing unit to use ("cpu" or "gpu")
        """
        if user_preference == "cpu":
            return "cpu"
        elif user_preference == "gpu":
            # Check if GPU is available
            if self._gpu_capabilities and self._gpu_capabilities.has_gpu:
                return "gpu"
            else:
                self.logger.warning("GPU requested but not available, falling back to CPU")
                return "cpu"
        else:  # auto
            # Use GPU if available, otherwise CPU
            if self._gpu_capabilities and self._gpu_capabilities.has_gpu:
                self.logger.info("Auto-detected GPU, using GPU acceleration")
                return "gpu"
            else:
                self.logger.info("No GPU detected, using CPU")
                return "cpu"
    
    def _handle_unload_request(self, model_id: str):
        """
        Handle model unload request.
        
        Args:
            model_id: ID of the model to unload
        """
        if model_id in self.loaded_models:
            model = self.loaded_models[model_id]
            model.unload()
            del self.loaded_models[model_id]
            
            if self.current_model_id == model_id:
                self.current_model_id = None
            
            self.model_unloaded.emit(model_id)
            self.event_bus.publish("model.unloaded", model_id)
            self.logger.info(f"Model unloaded: {model_id}")
    
    def _handle_cancel_request(self, request_data: Dict[str, Any]):
        """
        Handle model loading cancellation request.
        
        Args:
            request_data: Request data (unused)
        """
        if self.cancel_loading():
            self.logger.info("Model loading cancellation processed")
        else:
            self.logger.warning("No model loading to cancel")
    
    def _on_model_loaded(self, model: GGUFModel):
        """
        Handle successful model loading.
        
        Args:
            model: Loaded GGUFModel instance
        """
        try:
            # Generate model ID
            model_id = f"model_{len(self.loaded_models) + 1}"
            
            # Store the model
            self.loaded_models[model_id] = model
            self.current_model_id = model_id
            
            # Prepare model info for UI
            model_info = {
                "id": model_id,
                "name": model.name,
                "file_path": model.file_path,
                "size": model.size,
                "size_str": model.get_size_str(),
                "parameters": model.parameters,
                "metadata": model.metadata,
                "memory_usage": model.memory_usage,
                "load_time": model.load_time.isoformat() if model.load_time else None,
                "loaded": model.loaded
            }
            
            # Emit signals
            self.model_loaded.emit(model_id, model_info)
            self.event_bus.publish("model.loaded", model_id, model_info)
            
            self.logger.info(f"Model loaded and registered: {model_id} - {model.name}")
            
        except Exception as e:
            self.logger.exception(f"Error handling loaded model: {e}")
            self._on_loading_error(str(e))
    
    def _on_loading_error(self, error_message: str):
        """
        Handle model loading error.
        
        Args:
            error_message: Error message
        """
        self.logger.error(f"Model loading error: {error_message}")
        self.loading_error.emit(error_message)
        self.event_bus.publish("model.error", error_message)
    
    def get_current_model(self) -> Optional[Any]:
        """
        Get the currently loaded model.
        
        Returns:
            Current model from BackendManager or None if no model is loaded
        """
        if self.backend_manager and self.backend_manager.current_backend:
            return self.backend_manager.current_backend
        
        # Fallback to legacy model service for backward compatibility
        if self.current_model_id and self.current_model_id in self.loaded_models:
            return self.loaded_models[self.current_model_id]
        return None
    
    def get_loaded_models(self) -> Dict[str, GGUFModel]:
        """
        Get all loaded models.
        
        Returns:
            Dictionary of model_id -> GGUFModel
        """
        return self.loaded_models.copy()
    
    def unload_all_models(self):
        """Unload all models."""
        for model_id in list(self.loaded_models.keys()):
            self._handle_unload_request(model_id)
    
    def generate_text_async(self, prompt: str, system_prompt: str = None, 
                            temperature: float = 0.7, max_tokens: int = 256, 
                            top_p: float = 0.9, top_k: int = 40, 
                            repeat_penalty: float = 1.1, stop: List[str] = None, 
                            stream: bool = False) -> bool:
        """
        Generate text using the current model asynchronously.
        
        This method starts text generation in a background thread and returns immediately.
        Listen to generation_started, generation_progress, generation_finished, and 
        generation_error signals for updates.
        
        Args:
            prompt: Input prompt for text generation
            system_prompt: Optional system prompt to prepend
            temperature: Sampling temperature (0.0 to 2.0)
            max_tokens: Maximum number of tokens to generate
            top_p: Top-p sampling parameter
            top_k: Top-k sampling parameter
            repeat_penalty: Repetition penalty
            stop: List of stop sequences
            
        Returns:
            True if generation started successfully, False otherwise
        """
        # Check if BackendManager has a loaded model
        if not self.backend_manager or not self.backend_manager.current_backend:
            self.logger.error("No model loaded for text generation")
            self.generation_error.emit("No model loaded for text generation")
            return False
        
        current_model = self.get_current_model()
        
        try:
            # Use BackendManager for text generation
            from llmtoolkit.app.core.model_backends import GenerationConfig
            
            # Create generation config
            config = GenerationConfig(
                max_tokens=max_tokens,
                temperature=temperature,
                top_p=top_p,
                top_k=top_k,
                repeat_penalty=repeat_penalty,
                stop_sequences=stop or []
            )
            
            # Build full prompt with system prompt
            full_prompt = prompt
            if system_prompt:
                full_prompt = f"{system_prompt}\n\n{prompt}"
            
            # Emit generation started signal
            self.generation_started.emit()
            
            # Generate text using BackendManager
            if hasattr(self.backend_manager, 'generate_text_optimized'):
                response = self.backend_manager.generate_text_optimized(full_prompt, config)
            else:
                response = self.backend_manager.generate_text(full_prompt, config)
            
            if response and response.strip():
                # Emit generation finished signal
                self.generation_finished.emit(response.strip())
                self.logger.info("Text generation completed successfully")
                return True
            else:
                error_msg = "BackendManager generated empty response"
                self.logger.error(error_msg)
                self.generation_error.emit(error_msg)
                return False
                
        except Exception as e:
            error_msg = f"Error during text generation: {str(e)}"
            self.logger.error(error_msg)
            self.generation_error.emit(error_msg)
            return False
    
    def cancel_generation(self) -> bool:
        """
        Cancel the current text generation.
        
        Returns:
            True if cancellation was requested, False if no generation is running
        """
        # For BackendManager, we don't have a direct cancellation mechanism
        # This is a limitation of the current backend system
        self.logger.info("Text generation cancellation requested (not implemented for BackendManager)")
        return True
    
    def cancel_loading(self) -> bool:
        """
        Cancel the current model loading.
        
        Returns:
            True if cancellation was requested, False if no loading is running
        """
        if self.loading_thread and self.loading_thread.isRunning():
            self.loading_thread.cancel()
            self.logger.info("Model loading cancellation requested")
            return True
        return False
    
    def is_loading(self) -> bool:
        """
        Check if model loading is currently running.
        
        Returns:
            True if loading is running, False otherwise
        """
        return (self.loading_thread is not None and 
                self.loading_thread.isRunning())
    
    def is_generating(self) -> bool:
        """
        Check if text generation is currently running.
        
        Returns:
            True if generation is running, False otherwise
        """
        return (self.generation_thread is not None and 
                self.generation_thread.isRunning())
    
    def _on_generation_finished(self, generated_text: str):
        """
        Handle successful text generation.
        
        Args:
            generated_text: The generated text
        """
        try:
            # Publish generation event
            self.event_bus.publish("model.text_generated", {
                "model_id": self.current_model_id,
                "generated_text": generated_text,
                "timestamp": datetime.now().isoformat()
            })
            
            # Emit the finished signal
            self.generation_finished.emit(generated_text)
            
            self.logger.info(f"Text generation completed: {len(generated_text)} characters")
            
        except Exception as e:
            self.logger.error(f"Error handling generated text: {e}")
            self.generation_error.emit(str(e))
    
    def generate_text(self, prompt: str, system_prompt: str = None, 
                     temperature: float = 0.7, max_tokens: int = 256, 
                     top_p: float = 0.9, top_k: int = 40, 
                     repeat_penalty: float = 1.1, stop: List[str] = None) -> Optional[str]:
        """
        Generate text using the current model synchronously (DEPRECATED).
        
        WARNING: This method blocks the UI thread and should be avoided.
        Use generate_text_async() instead for better user experience.
        
        Args:
            prompt: Input prompt for text generation
            system_prompt: Optional system prompt to prepend
            temperature: Sampling temperature (0.0 to 2.0)
            max_tokens: Maximum number of tokens to generate
            top_p: Top-p sampling parameter
            top_k: Top-k sampling parameter
            repeat_penalty: Repetition penalty
            stop: List of stop sequences
            
        Returns:
            Generated text or None if no model is loaded
        """
        # Check if BackendManager is available and has a loaded model
        if self.backend_manager and self.backend_manager.current_backend:
            try:
                # Prepare the full prompt
                full_prompt = prompt
                if system_prompt:
                    full_prompt = f"{system_prompt}\n\n{prompt}"

                # Create GenerationConfig for BackendManager
                config = GenerationConfig(
                    max_tokens=max_tokens,
                    temperature=temperature,
                    top_p=top_p,
                    top_k=top_k,
                    repeat_penalty=repeat_penalty,
                    stop_sequences=stop or [],
                    stream=False
                )

                self.logger.debug(f"Generating text with BackendManager: {full_prompt[:100]}...")

                # Generate text using BackendManager
                generated_text = self.backend_manager.generate_text(full_prompt, config)

                # Publish generation event
                self.event_bus.publish("model.text_generated", {
                    "backend_name": self.backend_manager.current_backend.config.name if hasattr(self.backend_manager.current_backend, 'config') else "unknown",
                    "prompt": prompt,
                    "generated_text": generated_text,
                    "parameters": {
                        "temperature": temperature,
                        "max_tokens": max_tokens,
                        "top_p": top_p,
                        "top_k": top_k,
                        "repeat_penalty": repeat_penalty
                    }
                })

                self.logger.debug(f"Generated {len(generated_text)} characters using BackendManager")
                return generated_text

            except Exception as e:
                self.logger.error(f"Error generating text with BackendManager: {e}")
                self.event_bus.publish("model.generation_error", str(e))
                return None

        # Fallback to legacy model service for backward compatibility
        current_model = self.get_current_model()
        if not current_model or not getattr(current_model, 'loaded', False):
            self.logger.error("No model loaded for text generation")
            return None
        
        try:
            # Prepare the full prompt
            full_prompt = prompt
            if system_prompt:
                full_prompt = f"{system_prompt}\n\n{prompt}"
            
            # Get the llama model instance
            llama_model = getattr(current_model, '_llama_model', None)
            if not llama_model:
                self.logger.error("Model not properly loaded with llama.cpp")
                return None
            
            # Generate text
            self.logger.debug(f"Generating text with legacy model service: {full_prompt[:100]}...")
            
            response = llama_model(
                full_prompt,
                max_tokens=max_tokens,
                temperature=temperature,
                top_p=top_p,
                top_k=top_k,
                repeat_penalty=repeat_penalty,
                stop=stop or [],
                echo=False  # Don't echo the prompt in the response
            )
            
            # Extract the generated text
            generated_text = response['choices'][0]['text']
            
            # Update model access time
            if hasattr(current_model, 'access'):
                current_model.access()
            
            # Publish generation event
            self.event_bus.publish("model.text_generated", {
                "model_id": self.current_model_id,
                "prompt": prompt,
                "generated_text": generated_text,
                "parameters": {
                    "temperature": temperature,
                    "max_tokens": max_tokens,
                    "top_p": top_p,
                    "top_k": top_k,
                    "repeat_penalty": repeat_penalty
                }
            })
            
            self.logger.debug(f"Generated {len(generated_text)} characters using legacy model service")
            return generated_text
            
        except Exception as e:
            self.logger.error(f"Error generating text with legacy model service: {e}")
            self.event_bus.publish("model.generation_error", str(e))
            return None
    
    def get_model_info(self, model_id: str = None) -> Optional[Dict[str, Any]]:
        """
        Get information about a model.
        
        Args:
            model_id: ID of the model, or None for current model
            
        Returns:
            Model information dictionary or None if model not found
        """
        if model_id is None:
            model_id = self.current_model_id
        
        if not model_id or model_id not in self.loaded_models:
            return None
        
        model = self.loaded_models[model_id]
        
        return {
            "id": model_id,
            "name": model.name,
            "file_path": model.file_path,
            "size": model.size,
            "size_str": model.get_size_str(),
            "parameters": model.parameters,
            "metadata": model.metadata,
            "memory_usage": model.memory_usage,
            "load_time": model.load_time.isoformat() if model.load_time else None,
            "last_accessed": model.last_accessed.isoformat() if model.last_accessed else None,
            "loaded": model.loaded,
            "load_type": model.load_type,
            "hardware_backend": getattr(model, 'hardware_backend', None),
            "hardware_device": getattr(model, 'hardware_device', None)
        }
    
    def set_current_model(self, model_id: str) -> bool:
        """
        Set the current active model.
        
        Args:
            model_id: ID of the model to set as current
            
        Returns:
            True if the model was set successfully, False otherwise
        """
        if model_id not in self.loaded_models:
            self.logger.error(f"Model not found: {model_id}")
            return False
        
        old_model_id = self.current_model_id
        self.current_model_id = model_id
        
        # Publish model change event
        self.event_bus.publish("model.current_changed", {
            "old_model_id": old_model_id,
            "new_model_id": model_id
        })
        
        self.logger.info(f"Current model changed to: {model_id}")
        return True
    
    def is_model_loaded(self, model_id: str = None) -> bool:
        """
        Check if a model is loaded.
        
        Args:
            model_id: ID of the model to check, or None for current model
            
        Returns:
            True if the model is loaded, False otherwise
        """
        if model_id is None:
            model_id = self.current_model_id
        
        return (model_id is not None and 
                model_id in self.loaded_models and 
                self.loaded_models[model_id].loaded)
    
    def get_memory_usage(self) -> Dict[str, int]:
        """
        Get memory usage information for all loaded models.
        
        Returns:
            Dictionary with memory usage information
        """
        total_usage = 0
        model_usage = {}
        
        for model_id, model in self.loaded_models.items():
            usage = model.memory_usage
            model_usage[model_id] = usage
            total_usage += usage
        
        return {
            "total": total_usage,
            "models": model_usage,
            "count": len(self.loaded_models)
        }