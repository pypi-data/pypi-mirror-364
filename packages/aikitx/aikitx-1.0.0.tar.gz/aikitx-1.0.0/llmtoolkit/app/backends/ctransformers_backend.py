"""
ctransformers Backend Implementation

This module implements the ctransformers backend for GGUF model loading
and inference with GPU acceleration support for CUDA, ROCm, and Metal.

Features:
- GGUF model format support
- GPU acceleration (CUDA, ROCm, Metal)
- Automatic hardware detection and optimization
- Comprehensive error handling and validation
- Resource management and cleanup
"""

import logging
import time
import os
import platform
import subprocess
from pathlib import Path
from typing import Dict, Any, Optional, Tuple, List, Union

from llmtoolkit.app.core.model_backends import (
    ModelBackend, BackendConfig, HardwareInfo, LoadingResult, 
    GenerationConfig, HardwareType, BackendError, InstallationError, 
    HardwareError, ModelLoadingError
)


class CtransformersBackend(ModelBackend):
    """
    ctransformers backend implementation with comprehensive GGUF support.
    
    This backend provides:
    - GGUF model format support
    - GPU acceleration (CUDA, ROCm, Metal)
    - Automatic model type detection
    - Optimized memory management
    - Comprehensive error handling
    """
    
    # Supported model types and their ctransformers identifiers
    SUPPORTED_MODEL_TYPES = {
        'llama': 'llama',
        'llama2': 'llama',
        'codellama': 'codellama',
        'mistral': 'mistral',
        'mixtral': 'mistral',
        'falcon': 'falcon',
        'mpt': 'mpt',
        'gpt2': 'gpt2',
        'gptj': 'gptj',
        'gptneox': 'gptneox',
        'starcoder': 'starcoder',
        'santacoder': 'starcoder',
        'replit': 'replit',
        'dolly': 'dolly-v2',
        'stablelm': 'stablelm',
        'chatglm': 'chatglm'
    }
    
    # File extensions that indicate GGUF format
    GGUF_EXTENSIONS = {'.gguf', '.ggml', '.bin'}
    
    def __init__(self, config: BackendConfig):
        """Initialize the ctransformers backend."""
        super().__init__(config)
        self.model = None
        self._model_type = None
        self._context_length = None
        self._gpu_layers_used = 0
        self._hardware_acceleration = None
        self._model_metadata = {}
        self._generation_stats = {
            'total_tokens': 0,
            'total_time': 0.0,
            'average_tokens_per_second': 0.0
        }
        
    def is_available(self) -> Tuple[bool, Optional[str]]:
        """
        Check if ctransformers is available and properly configured.
        
        Returns:
            Tuple of (is_available, error_message)
        """
        try:
            # Try to import ctransformers
            import ctransformers
            
            # Get version info safely
            try:
                version = getattr(ctransformers, '__version__', 'unknown')
                self.logger.info(f"ctransformers version: {version}")
            except:
                self.logger.info("ctransformers version: unknown")
            
            # Check if we can create a basic model instance (validates installation)
            try:
                # This will fail gracefully if ctransformers is not properly installed
                from ctransformers import AutoModelForCausalLM
                self.logger.debug("ctransformers AutoModelForCausalLM import successful")
            except ImportError as e:
                return False, f"ctransformers components not available: {e}"
            
            # Check for GPU support if enabled
            if self.config.gpu_enabled:
                gpu_support_info = self._check_gpu_support()
                if gpu_support_info:
                    self.logger.info(f"GPU support detected: {gpu_support_info}")
            
            return True, None
            
        except ImportError as e:
            error_msg = f"ctransformers not installed: {e}"
            self.logger.warning(error_msg)
            return False, error_msg
        except Exception as e:
            error_msg = f"Error checking ctransformers availability: {e}"
            self.logger.error(error_msg)
            return False, error_msg
    
    def _check_gpu_support(self) -> Optional[str]:
        """
        Check what GPU acceleration is available.
        
        Returns:
            String describing available GPU support or None
        """
        gpu_info = []
        
        # Check CUDA support
        if self._check_cuda_support():
            gpu_info.append("CUDA")
        
        # Check ROCm support (AMD)
        if self._check_rocm_support():
            gpu_info.append("ROCm")
        
        # Check Metal support (macOS)
        if self._check_metal_support():
            gpu_info.append("Metal")
        
        return ", ".join(gpu_info) if gpu_info else None
    
    def _check_cuda_support(self) -> bool:
        """Check if CUDA support is available."""
        try:
            # Check if nvidia-smi is available
            result = subprocess.run(['nvidia-smi'], capture_output=True, timeout=5)
            if result.returncode == 0:
                self.logger.debug("CUDA support detected via nvidia-smi")
                return True
        except (subprocess.TimeoutExpired, subprocess.CalledProcessError, FileNotFoundError):
            pass
        
        # Check for CUDA libraries
        try:
            import ctransformers
            # ctransformers with CUDA support should have been installed with [cuda] extra
            # This is a heuristic check
            return True  # Assume CUDA support if ctransformers is installed
        except:
            pass
        
        return False
    
    def _check_rocm_support(self) -> bool:
        """Check if ROCm support is available."""
        try:
            # Check if rocm-smi is available
            result = subprocess.run(['rocm-smi'], capture_output=True, timeout=5)
            if result.returncode == 0:
                self.logger.debug("ROCm support detected via rocm-smi")
                return True
        except (subprocess.TimeoutExpired, subprocess.CalledProcessError, FileNotFoundError):
            pass
        
        return False
    
    def _check_metal_support(self) -> bool:
        """Check if Metal support is available (macOS only)."""
        if platform.system() != "Darwin":
            return False
        
        try:
            # Check if we're on macOS with Metal support
            result = subprocess.run(['system_profiler', 'SPDisplaysDataType'], 
                                  capture_output=True, text=True, timeout=10)
            if result.returncode == 0 and 'Metal' in result.stdout:
                self.logger.debug("Metal support detected on macOS")
                return True
        except (subprocess.TimeoutExpired, subprocess.CalledProcessError, FileNotFoundError):
            pass
        
        return False
    
    def load_model(self, model_path: str, **kwargs) -> LoadingResult:
        """
        Load a GGUF model using ctransformers with comprehensive validation and optimization.
        
        Args:
            model_path: Path to the GGUF model file
            **kwargs: Additional loading parameters
            
        Returns:
            LoadingResult with detailed success/failure information
        """
        start_time = time.time()
        
        try:
            # Comprehensive model path validation
            validation_result = self._validate_model_file(model_path)
            if not validation_result['valid']:
                return LoadingResult(
                    success=False,
                    backend_used=self.config.name,
                    hardware_used="none",
                    load_time=0.0,
                    error_message=validation_result['error']
                )
            
            # Import ctransformers with error handling
            try:
                from ctransformers import AutoModelForCausalLM
                self.logger.debug("ctransformers imported successfully")
            except ImportError as e:
                return LoadingResult(
                    success=False,
                    backend_used=self.config.name,
                    hardware_used="none",
                    load_time=0.0,
                    error_message=f"ctransformers not available: {e}"
                )
            
            # Detect and validate model type
            model_type = kwargs.pop('model_type', None)  # Remove from kwargs to avoid conflicts
            if not model_type:
                model_type = self._detect_model_type(model_path)
                self.logger.info(f"Auto-detected model type: {model_type}")
            else:
                self.logger.info(f"Using specified model type: {model_type}")
            
            # Validate model type
            if not self._validate_model_type(model_type):
                return LoadingResult(
                    success=False,
                    backend_used=self.config.name,
                    hardware_used="none",
                    load_time=0.0,
                    error_message=f"Unsupported model type: {model_type}"
                )
            
            # Prepare optimized loading configuration
            load_config = self._prepare_load_config(model_path, model_type, **kwargs)
            
            self.logger.info(f"Loading GGUF model: {Path(model_path).name}")
            self.logger.info(f"Model type: {model_type}")
            self.logger.info(f"GPU layers: {load_config.get('gpu_layers', 0)}")
            self.logger.info(f"Context size: {load_config.get('context_length', self.config.context_size)}")
            
            # Attempt model loading with retry logic
            self.model = self._load_model_with_retry(
                model_path, model_type, load_config, AutoModelForCausalLM
            )
            
            # Store model information and metadata
            self.model_path = model_path
            self._model_type = model_type
            self._context_length = load_config.get('context_length', self.config.context_size)
            self._gpu_layers_used = load_config.get('gpu_layers', 0)
            self.is_loaded = True
            
            # Calculate performance metrics
            load_time = time.time() - start_time
            self.load_time = load_time
            
            # Get detailed model information
            model_info = self._get_model_metadata(model_path, validation_result)
            self._model_metadata = model_info
            
            # Estimate memory usage more accurately
            self.memory_usage = self._estimate_memory_usage(model_info, load_config)
            
            # Determine hardware acceleration used
            hardware_used = self._determine_hardware_used(load_config)
            self._hardware_acceleration = hardware_used
            
            self.logger.info(f"Model loaded successfully in {load_time:.2f}s")
            self.logger.info(f"Hardware acceleration: {hardware_used}")
            self.logger.info(f"Memory usage: {self.memory_usage}MB")
            
            return LoadingResult(
                success=True,
                backend_used=self.config.name,
                hardware_used=hardware_used,
                load_time=load_time,
                memory_usage=self.memory_usage,
                model_info={
                    'model_type': model_type,
                    'context_length': self._context_length,
                    'gpu_layers': self._gpu_layers_used,
                    'hardware_acceleration': hardware_used,
                    **model_info
                }
            )
            
        except Exception as e:
            load_time = time.time() - start_time
            error_msg = self._format_loading_error(e, model_path)
            self.logger.error(error_msg)
            
            return LoadingResult(
                success=False,
                backend_used=self.config.name,
                hardware_used="none",
                load_time=load_time,
                error_message=error_msg
            )
    
    def _validate_model_file(self, model_path: str) -> Dict[str, Any]:
        """
        Comprehensive validation of the model file.
        
        Args:
            model_path: Path to the model file
            
        Returns:
            Dictionary with validation results
        """
        try:
            path = Path(model_path)
            
            # Basic path validation
            if not path.exists():
                return {'valid': False, 'error': f"Model file does not exist: {model_path}"}
            
            if not path.is_file():
                return {'valid': False, 'error': f"Path is not a file: {model_path}"}
            
            # File size validation
            file_size = path.stat().st_size
            if file_size == 0:
                return {'valid': False, 'error': f"Model file is empty: {model_path}"}
            
            file_size_mb = file_size // (1024 * 1024)
            if file_size_mb < 1:
                return {'valid': False, 'error': f"Model file too small (< 1MB): {model_path}"}
            
            # File extension validation
            if path.suffix.lower() not in self.GGUF_EXTENSIONS:
                self.logger.warning(f"Unusual file extension for GGUF model: {path.suffix}")
            
            # File format validation (basic header check)
            try:
                with open(model_path, 'rb') as f:
                    header = f.read(8)
                    if len(header) >= 4:
                        # Check for GGUF magic number
                        if header[:4] == b'GGUF':
                            format_type = 'GGUF'
                        elif header[:4] == b'ggml' or header[:4] == b'GGML':
                            format_type = 'GGML'
                        else:
                            format_type = 'Unknown'
                            self.logger.warning(f"Unknown model format, attempting to load anyway")
                    else:
                        format_type = 'Unknown'
            except Exception as e:
                self.logger.warning(f"Could not read model header: {e}")
                format_type = 'Unknown'
            
            return {
                'valid': True,
                'file_size': file_size,
                'file_size_mb': file_size_mb,
                'format_type': format_type,
                'extension': path.suffix.lower()
            }
            
        except Exception as e:
            return {'valid': False, 'error': f"Error validating model file: {e}"}
    
    def _validate_model_type(self, model_type: str) -> bool:
        """
        Validate that the model type is supported by ctransformers.
        
        Args:
            model_type: Model type string
            
        Returns:
            True if supported, False otherwise
        """
        return model_type.lower() in self.SUPPORTED_MODEL_TYPES
    
    def _load_model_with_retry(self, model_path: str, model_type: str, 
                              load_config: Dict[str, Any], 
                              model_class) -> Any:
        """
        Load model with retry logic for GPU fallback.
        
        Args:
            model_path: Path to model file
            model_type: Model type
            load_config: Loading configuration
            model_class: ctransformers model class
            
        Returns:
            Loaded model instance
        """
        original_gpu_layers = load_config.get('gpu_layers', 0)
        
        try:
            # First attempt with original configuration
            self.logger.debug(f"Attempting to load with GPU layers: {original_gpu_layers}")
            return model_class.from_pretrained(
                model_path,
                model_type=model_type,
                **load_config
            )
            
        except Exception as e:
            if original_gpu_layers > 0:
                # GPU loading failed, try with reduced GPU layers
                self.logger.warning(f"GPU loading failed ({e}), trying with reduced GPU layers")
                
                for gpu_layers in [original_gpu_layers // 2, original_gpu_layers // 4, 0]:
                    try:
                        load_config_retry = load_config.copy()
                        load_config_retry['gpu_layers'] = gpu_layers
                        
                        self.logger.debug(f"Retry attempt with GPU layers: {gpu_layers}")
                        return model_class.from_pretrained(
                            model_path,
                            model_type=model_type,
                            **load_config_retry
                        )
                        
                    except Exception as retry_e:
                        self.logger.debug(f"Retry with {gpu_layers} GPU layers failed: {retry_e}")
                        continue
            
            # All attempts failed, re-raise the original exception
            raise e
    
    def _get_model_metadata(self, model_path: str, validation_result: Dict[str, Any]) -> Dict[str, Any]:
        """
        Extract metadata from the model file.
        
        Args:
            model_path: Path to model file
            validation_result: Result from file validation
            
        Returns:
            Dictionary with model metadata
        """
        metadata = {
            'file_name': Path(model_path).name,
            'file_size_mb': validation_result.get('file_size_mb', 0),
            'format_type': validation_result.get('format_type', 'Unknown'),
            'extension': validation_result.get('extension', ''),
        }
        
        # Try to extract additional metadata from GGUF file
        try:
            # This is a simplified metadata extraction
            # In a full implementation, you might use a GGUF parser
            with open(model_path, 'rb') as f:
                header = f.read(1024)  # Read first 1KB for metadata
                
                # Look for common metadata patterns
                if b'llama' in header.lower():
                    metadata['architecture'] = 'llama'
                elif b'mistral' in header.lower():
                    metadata['architecture'] = 'mistral'
                elif b'falcon' in header.lower():
                    metadata['architecture'] = 'falcon'
                
        except Exception as e:
            self.logger.debug(f"Could not extract additional metadata: {e}")
        
        return metadata
    
    def _estimate_memory_usage(self, model_info: Dict[str, Any], load_config: Dict[str, Any]) -> int:
        """
        Estimate memory usage based on model size and configuration.
        
        Args:
            model_info: Model metadata
            load_config: Loading configuration
            
        Returns:
            Estimated memory usage in MB
        """
        base_size_mb = model_info.get('file_size_mb', 0)
        
        # Base memory usage (model weights)
        memory_usage = base_size_mb
        
        # Add context buffer overhead
        context_size = load_config.get('context_length', self.config.context_size)
        context_overhead = (context_size * 4) // (1024 * 1024)  # Rough estimate: 4 bytes per token
        memory_usage += context_overhead
        
        # Add GPU memory overhead if using GPU
        gpu_layers = load_config.get('gpu_layers', 0)
        if gpu_layers > 0:
            # GPU memory typically needs more overhead
            memory_usage = int(memory_usage * 1.2)
        else:
            # CPU memory overhead
            memory_usage = int(memory_usage * 1.1)
        
        return memory_usage
    
    def _determine_hardware_used(self, load_config: Dict[str, Any]) -> str:
        """
        Determine what hardware acceleration is being used.
        
        Args:
            load_config: Loading configuration
            
        Returns:
            Hardware type string
        """
        gpu_layers = load_config.get('gpu_layers', 0)
        
        if gpu_layers == 0:
            return "cpu"
        
        # Determine GPU type based on system
        if self._check_cuda_support():
            return "cuda"
        elif self._check_rocm_support():
            return "rocm"
        elif self._check_metal_support():
            return "metal"
        else:
            return "gpu"  # Generic GPU
    
    def _format_loading_error(self, error: Exception, model_path: str) -> str:
        """
        Format loading error with helpful information.
        
        Args:
            error: The exception that occurred
            model_path: Path to the model that failed to load
            
        Returns:
            Formatted error message
        """
        error_str = str(error)
        
        # Common error patterns and suggestions
        if "out of memory" in error_str.lower() or "cuda out of memory" in error_str.lower():
            return (f"GPU out of memory loading {Path(model_path).name}. "
                   f"Try reducing GPU layers or using CPU mode. Error: {error}")
        
        elif "no such file" in error_str.lower():
            return f"Model file not found: {model_path}. Error: {error}"
        
        elif "permission denied" in error_str.lower():
            return f"Permission denied accessing model file: {model_path}. Error: {error}"
        
        elif "unsupported" in error_str.lower():
            return (f"Unsupported model format or type for {Path(model_path).name}. "
                   f"Ensure this is a valid GGUF model. Error: {error}")
        
        elif "cuda" in error_str.lower() and "not available" in error_str.lower():
            return (f"CUDA not available for GPU acceleration. "
                   f"Model will fall back to CPU mode. Error: {error}")
        
        else:
            return f"Failed to load model {Path(model_path).name}: {error}"
    
    def _detect_model_type(self, model_path: str) -> str:
        """
        Detect model type from file name with comprehensive pattern matching.
        
        Args:
            model_path: Path to the model file
            
        Returns:
            Detected model type string
        """
        model_path_lower = model_path.lower()
        model_name = Path(model_path).name.lower()
        
        # Comprehensive model type detection patterns
        # Order matters - more specific patterns first
        detection_patterns = [
            # Code models (must come before general llama)
            (['codellama', 'code-llama'], 'codellama'),
            
            # Mistral variants
            (['mixtral'], 'mistral'),
            (['mistral'], 'mistral'),
            
            # Llama variants (after more specific variants)
            (['llama-2', 'llama2'], 'llama'),
            (['llama', 'alpaca', 'vicuna'], 'llama'),
            
            # Other popular models
            (['falcon'], 'falcon'),
            (['mpt'], 'mpt'),
            (['gpt-2', 'gpt2'], 'gpt2'),
            (['gpt-j', 'gptj'], 'gptj'),
            (['gpt-neox', 'gptneox'], 'gptneox'),
            (['starcoder', 'star-coder'], 'starcoder'),
            (['santacoder', 'santa-coder'], 'starcoder'),
            (['replit'], 'replit'),
            (['dolly'], 'dolly-v2'),
            (['stablelm', 'stable-lm'], 'stablelm'),
            (['chatglm', 'chat-glm'], 'chatglm'),
        ]
        
        # Check each pattern
        for patterns, model_type in detection_patterns:
            for pattern in patterns:
                if pattern in model_name or pattern in model_path_lower:
                    self.logger.info(f"Detected model type '{model_type}' from pattern '{pattern}'")
                    return model_type
        
        # Try to detect from common naming conventions
        if any(x in model_name for x in ['7b', '13b', '30b', '65b', '70b']):
            # Likely a Llama-style model
            self.logger.info("Detected Llama-style model from parameter count pattern")
            return 'llama'
        
        # Check for instruction-tuned variants
        if any(x in model_name for x in ['instruct', 'chat', 'it']):
            if 'mistral' in model_name:
                return 'mistral'
            else:
                return 'llama'  # Most instruction models are Llama-based
        
        # Default fallback with warning
        self.logger.warning(f"Could not detect model type from '{model_name}', defaulting to 'llama'")
        self.logger.info("If this is incorrect, specify model_type explicitly when loading")
        return 'llama'
    
    def _prepare_load_config(self, model_path: str, model_type: str, **kwargs) -> Dict[str, Any]:
        """
        Prepare optimized configuration for model loading.
        
        Args:
            model_path: Path to the model file
            model_type: Detected model type
            **kwargs: Additional configuration parameters
            
        Returns:
            Dictionary with loading configuration
        """
        config = {}
        
        # Context length configuration
        context_length = kwargs.get('context_length', self.config.context_size)
        config['context_length'] = self._optimize_context_length(context_length, model_type)
        
        # GPU configuration with intelligent layer estimation
        if self.config.gpu_enabled:
            gpu_layers = self._determine_optimal_gpu_layers(model_path, model_type, kwargs)
            if gpu_layers > 0:
                config['gpu_layers'] = gpu_layers
                self.logger.info(f"Using GPU acceleration with {gpu_layers} layers")
            else:
                self.logger.info("Using CPU-only mode")
        else:
            self.logger.info("GPU disabled in configuration, using CPU-only mode")
        
        # Threading configuration
        threads = kwargs.get('threads', self.config.threads)
        if threads > 0:
            config['threads'] = threads
        elif threads == -1:  # Auto-detect
            config['threads'] = self._get_optimal_thread_count()
        
        # Batch size optimization
        batch_size = kwargs.get('batch_size', getattr(self.config, 'batch_size', 512))
        if batch_size > 0:
            config['batch_size'] = self._optimize_batch_size(batch_size, config.get('gpu_layers', 0))
        
        # Model-specific optimizations
        model_specific_config = self._get_model_specific_config(model_type)
        config.update(model_specific_config)
        
        # Custom arguments (highest priority)
        if self.config.custom_args:
            config.update(self.config.custom_args)
        
        # Override with explicit kwargs
        for key, value in kwargs.items():
            if key not in ['model_type']:  # Don't override model_type
                config[key] = value
        
        self.logger.debug(f"Final loading configuration: {config}")
        return config
    
    def _optimize_context_length(self, context_length: int, model_type: str) -> int:
        """
        Optimize context length based on model type and available memory.
        
        Args:
            context_length: Requested context length
            model_type: Model type
            
        Returns:
            Optimized context length
        """
        # Model-specific context length limits
        model_limits = {
            'llama': 4096,
            'mistral': 8192,
            'codellama': 16384,
            'falcon': 2048,
            'mpt': 8192,
            'gpt2': 1024,
            'gptj': 2048,
            'gptneox': 2048,
            'starcoder': 8192
        }
        
        max_context = model_limits.get(model_type, 4096)
        
        # Don't exceed model's maximum context length
        if context_length > max_context:
            self.logger.warning(f"Requested context length {context_length} exceeds model limit {max_context}")
            context_length = max_context
        
        # Ensure minimum context length
        context_length = max(context_length, 512)
        
        return context_length
    
    def _determine_optimal_gpu_layers(self, model_path: str, model_type: str, kwargs: Dict[str, Any]) -> int:
        """
        Determine optimal number of GPU layers based on hardware and model.
        
        Args:
            model_path: Path to model file
            model_type: Model type
            kwargs: Additional parameters
            
        Returns:
            Optimal number of GPU layers
        """
        # Check if GPU layers explicitly specified
        if 'gpu_layers' in kwargs:
            return kwargs['gpu_layers']
        
        if self.config.gpu_layers != -1:
            return self.config.gpu_layers
        
        # Auto-detection based on hardware and model
        return self._estimate_gpu_layers(model_path, model_type)
    
    def _estimate_gpu_layers(self, model_path: str, model_type: str) -> int:
        """
        Estimate optimal number of GPU layers based on model size and available VRAM.
        
        Args:
            model_path: Path to model file
            model_type: Model type
            
        Returns:
            Estimated number of GPU layers
        """
        try:
            # Get model file size
            model_size_mb = Path(model_path).stat().st_size // (1024 * 1024)
            
            # Get available GPU memory
            try:
                from llmtoolkit.app.core.monitoring import GPUMonitor
                gpu_monitor = GPUMonitor()
                gpu_metrics = gpu_monitor.get_gpu_metrics()
                
                if not gpu_metrics:
                    self.logger.info("No GPU detected, using CPU-only mode")
                    return 0
                
                # Use the GPU with most available memory
                best_gpu = max(gpu_metrics, key=lambda x: x.get('memory_total_mb', 0))
                total_vram_mb = best_gpu.get('memory_total_mb', 0)
                used_vram_mb = best_gpu.get('memory_used_mb', 0)
                available_vram_mb = total_vram_mb - used_vram_mb
                
                self.logger.info(f"GPU: {best_gpu.get('name', 'Unknown')}")
                self.logger.info(f"Total VRAM: {total_vram_mb}MB, Available: {available_vram_mb}MB")
                self.logger.info(f"Model size: {model_size_mb}MB")
                
                # Conservative estimation: leave 1GB for system and context
                safety_margin_mb = 1024
                usable_vram_mb = max(0, available_vram_mb - safety_margin_mb)
                
                if usable_vram_mb < 500:  # Less than 500MB available
                    self.logger.warning("Insufficient GPU memory available, using CPU-only mode")
                    return 0
                
                # Estimate layers based on model size and available VRAM
                # This is a rough heuristic - different models have different layer sizes
                if model_size_mb <= 1000:  # Small models (< 1GB)
                    if usable_vram_mb >= model_size_mb * 1.5:
                        return -1  # Use all layers
                    else:
                        return max(1, int((usable_vram_mb / model_size_mb) * 32))
                        
                elif model_size_mb <= 4000:  # Medium models (1-4GB)
                    if usable_vram_mb >= model_size_mb * 1.3:
                        return -1  # Use all layers
                    else:
                        return max(1, int((usable_vram_mb / model_size_mb) * 40))
                        
                elif model_size_mb <= 8000:  # Large models (4-8GB)
                    if usable_vram_mb >= model_size_mb * 1.2:
                        return -1  # Use all layers
                    else:
                        return max(1, int((usable_vram_mb / model_size_mb) * 35))
                        
                else:  # Very large models (> 8GB)
                    if usable_vram_mb >= model_size_mb:
                        return max(1, int((usable_vram_mb / model_size_mb) * 30))
                    else:
                        self.logger.warning("Model too large for available GPU memory, using CPU-only mode")
                        return 0
                        
            except Exception as e:
                self.logger.warning(f"Error checking GPU memory: {e}")
                # Fallback: try a conservative number of layers
                if self._check_cuda_support():
                    self.logger.info("CUDA detected, trying conservative GPU layer count")
                    return 20  # Conservative default for CUDA
                else:
                    return 0
                    
        except Exception as e:
            self.logger.error(f"Error estimating GPU layers: {e}")
            return 0
    
    def _get_optimal_thread_count(self) -> int:
        """
        Get optimal thread count for CPU inference.
        
        Returns:
            Optimal number of threads
        """
        try:
            import os
            # Use number of physical CPU cores
            cpu_count = os.cpu_count() or 4
            # Use 75% of available cores to leave room for system
            optimal_threads = max(1, int(cpu_count * 0.75))
            self.logger.debug(f"Using {optimal_threads} threads (from {cpu_count} CPU cores)")
            return optimal_threads
        except Exception as e:
            self.logger.warning(f"Could not determine optimal thread count: {e}")
            return 4  # Safe default
    
    def _optimize_batch_size(self, batch_size: int, gpu_layers: int) -> int:
        """
        Optimize batch size based on hardware acceleration.
        
        Args:
            batch_size: Requested batch size
            gpu_layers: Number of GPU layers
            
        Returns:
            Optimized batch size
        """
        if gpu_layers > 0:
            # GPU can handle larger batches
            return min(batch_size, 1024)
        else:
            # CPU prefers smaller batches
            return min(batch_size, 256)
    
    def _get_model_specific_config(self, model_type: str) -> Dict[str, Any]:
        """
        Get model-specific configuration optimizations.
        
        Args:
            model_type: Model type
            
        Returns:
            Model-specific configuration
        """
        config = {}
        
        # Model-specific optimizations
        if model_type == 'codellama':
            # Code models benefit from larger context
            config['context_length'] = max(config.get('context_length', 4096), 8192)
        elif model_type == 'mistral':
            # Mistral models support larger context efficiently
            config['context_length'] = max(config.get('context_length', 4096), 8192)
        elif model_type == 'falcon':
            # Falcon models are memory-intensive
            config['batch_size'] = min(config.get('batch_size', 512), 256)
        
        return config
    
    def _estimate_gpu_layers(self, model_path: str, model_type: str) -> int:
        """
        Estimate optimal number of GPU layers based on model size, type, and available VRAM.
        
        Args:
            model_path: Path to model file
            model_type: Model type
            
        Returns:
            Optimal number of GPU layers
        """
        try:
            file_size_mb = Path(model_path).stat().st_size // (1024 * 1024)
            
            # Get hardware info to check VRAM
            hw_info = self.get_hardware_info()
            
            if hw_info.total_vram == 0:
                self.logger.info("No GPU VRAM detected, using CPU-only mode")
                return 0
            
            # Model-specific layer count estimates (approximate)
            model_layer_estimates = {
                'llama': {'7b': 32, '13b': 40, '30b': 60, '65b': 80, '70b': 80},
                'mistral': {'7b': 32, '8x7b': 32},  # Mixtral uses same layer count
                'codellama': {'7b': 32, '13b': 40, '34b': 48},
                'falcon': {'7b': 32, '40b': 60},
                'mpt': {'7b': 32, '30b': 60},
                'gpt2': {'small': 12, 'medium': 24, 'large': 36, 'xl': 48},
                'gptj': {'6b': 28},
                'gptneox': {'20b': 44},
                'starcoder': {'15b': 40}
            }
            
            # Estimate model size category from file size
            size_category = self._estimate_model_size_category(file_size_mb)
            estimated_layers = model_layer_estimates.get(model_type, {}).get(size_category, 32)
            
            # Calculate VRAM requirements
            # Rough estimation: each layer needs about file_size / total_layers MB
            vram_per_layer = file_size_mb / estimated_layers if estimated_layers > 0 else file_size_mb
            
            # Add overhead for context and intermediate computations
            context_overhead = (self.config.context_size * 4) // (1024 * 1024)  # 4 bytes per token
            total_overhead = context_overhead + int(file_size_mb * 0.2)  # 20% overhead
            
            available_vram = hw_info.total_vram - total_overhead
            
            if available_vram <= 0:
                self.logger.warning(f"Insufficient VRAM after overhead ({total_overhead}MB), using CPU")
                return 0
            
            # Calculate how many layers can fit in VRAM
            max_gpu_layers = int(available_vram / vram_per_layer)
            
            # Don't exceed the estimated total layers
            optimal_layers = min(max_gpu_layers, estimated_layers)
            
            # Ensure we use at least some GPU if we have enough VRAM for a few layers
            if optimal_layers < 4 and available_vram > vram_per_layer * 4:
                optimal_layers = 4
            
            # Cap at reasonable maximum
            optimal_layers = min(optimal_layers, 100)
            
            self.logger.info(f"GPU layer estimation: {optimal_layers}/{estimated_layers} layers")
            self.logger.info(f"VRAM usage: ~{optimal_layers * vram_per_layer + total_overhead:.0f}MB / {hw_info.total_vram}MB")
            
            return max(0, optimal_layers)
            
        except Exception as e:
            self.logger.warning(f"Error estimating GPU layers: {e}")
            return 0
    
    def _estimate_model_size_category(self, file_size_mb: int) -> str:
        """
        Estimate model size category from file size.
        
        Args:
            file_size_mb: File size in MB
            
        Returns:
            Size category string
        """
        # Rough size categories based on typical GGUF file sizes
        if file_size_mb < 1000:  # < 1GB
            return '7b'
        elif file_size_mb < 3000:  # < 3GB
            return '7b'
        elif file_size_mb < 8000:  # < 8GB
            return '13b'
        elif file_size_mb < 20000:  # < 20GB
            return '30b'
        elif file_size_mb < 45000:  # < 45GB
            return '65b'
        else:
            return '70b'
    
    def generate_text(self, prompt: str, config: GenerationConfig) -> str:
        """
        Generate text using the loaded model with comprehensive error handling.
        
        Args:
            prompt: Input text prompt
            config: Generation configuration
            
        Returns:
            Generated text
            
        Raises:
            ModelLoadingError: If no model is loaded
            BackendError: If generation fails
        """
        if not self.is_loaded or self.model is None:
            raise ModelLoadingError("No model is loaded")
        
        if not prompt or not prompt.strip():
            raise BackendError("Empty prompt provided")
        
        start_time = time.time()
        
        try:
            # Validate and prepare generation parameters
            generation_params = self._prepare_generation_params(config)
            
            # Validate prompt length
            if len(prompt) > self._context_length * 4:  # Rough token estimate
                self.logger.warning(f"Prompt may exceed context length ({self._context_length} tokens)")
            
            self.logger.debug(f"Generating text with params: {generation_params}")
            self.logger.debug(f"Prompt length: {len(prompt)} characters")
            
            # Generate text with error handling
            response = self._generate_with_error_handling(prompt, generation_params, config.stream)
            
            # Update generation statistics
            generation_time = time.time() - start_time
            self._update_generation_stats(response, generation_time)
            
            self.logger.debug(f"Generated {len(response)} characters in {generation_time:.2f}s")
            
            return response
            
        except ModelLoadingError:
            raise  # Re-raise model loading errors
        except Exception as e:
            error_msg = self._format_generation_error(e, prompt, config)
            self.logger.error(error_msg)
            raise BackendError(error_msg)
    
    def _prepare_generation_params(self, config: GenerationConfig) -> Dict[str, Any]:
        """
        Prepare and validate generation parameters.
        
        Args:
            config: Generation configuration
            
        Returns:
            Dictionary with validated generation parameters
        """
        params = {
            'max_new_tokens': max(1, min(config.max_tokens, 4096)),  # Reasonable limits
            'temperature': max(0.0, min(config.temperature, 2.0)),
            'top_p': max(0.0, min(config.top_p, 1.0)),
            'top_k': max(1, min(config.top_k, 200)),
            'repetition_penalty': max(0.5, min(config.repeat_penalty, 2.0)),
        }
        
        # Add seed if specified and valid
        if config.seed >= 0:
            params['seed'] = config.seed
        
        # Add stop sequences if specified
        if config.stop_sequences:
            # Filter out only truly empty stop sequences (not whitespace-only)
            stop_sequences = [s for s in config.stop_sequences if s]
            if stop_sequences:
                params['stop'] = stop_sequences
        
        return params
    
    def _generate_with_error_handling(self, prompt: str, params: Dict[str, Any], stream: bool) -> str:
        """
        Generate text with comprehensive error handling and retry logic.
        
        Args:
            prompt: Input prompt
            params: Generation parameters
            stream: Whether to use streaming
            
        Returns:
            Generated text
        """
        try:
            if stream:
                return self._generate_streaming(prompt, params)
            else:
                return self._generate_non_streaming(prompt, params)
                
        except Exception as e:
            # Try to recover from common errors
            if "out of memory" in str(e).lower():
                # Reduce parameters and retry
                self.logger.warning("Out of memory during generation, reducing parameters")
                reduced_params = params.copy()
                reduced_params['max_new_tokens'] = min(reduced_params['max_new_tokens'], 256)
                
                try:
                    if stream:
                        return self._generate_streaming(prompt, reduced_params)
                    else:
                        return self._generate_non_streaming(prompt, reduced_params)
                except Exception as retry_e:
                    self.logger.error(f"Retry with reduced parameters failed: {retry_e}")
                    raise e  # Raise original error
            
            raise e
    
    def _generate_streaming(self, prompt: str, params: Dict[str, Any]) -> str:
        """
        Generate text using streaming mode.
        
        Args:
            prompt: Input prompt
            params: Generation parameters
            
        Returns:
            Generated text
        """
        response_parts = []
        token_count = 0
        
        try:
            for token in self.model(prompt, stream=True, **params):
                if token:  # Skip empty tokens
                    response_parts.append(token)
                    token_count += 1
                    
                    # Safety check to prevent infinite generation
                    if token_count > params.get('max_new_tokens', 512) * 2:
                        self.logger.warning("Generation exceeded expected token count, stopping")
                        break
            
            return ''.join(response_parts)
            
        except Exception as e:
            if response_parts:
                # Return partial response if we got something
                self.logger.warning(f"Streaming generation interrupted: {e}")
                return ''.join(response_parts)
            raise e
    
    def _generate_non_streaming(self, prompt: str, params: Dict[str, Any]) -> str:
        """
        Generate text using non-streaming mode.
        
        Args:
            prompt: Input prompt
            params: Generation parameters
            
        Returns:
            Generated text
        """
        response = self.model(prompt, **params)
        
        if not isinstance(response, str):
            raise BackendError(f"Unexpected response type: {type(response)}")
        
        return response
    
    def _update_generation_stats(self, response: str, generation_time: float):
        """
        Update generation statistics.
        
        Args:
            response: Generated text
            generation_time: Time taken for generation
        """
        # Rough token count estimation (4 characters per token average)
        estimated_tokens = len(response) // 4
        
        self._generation_stats['total_tokens'] += estimated_tokens
        self._generation_stats['total_time'] += generation_time
        
        if generation_time > 0:
            tokens_per_second = estimated_tokens / generation_time
            
            # Update rolling average
            if self._generation_stats['average_tokens_per_second'] == 0:
                self._generation_stats['average_tokens_per_second'] = tokens_per_second
            else:
                # Simple exponential moving average
                alpha = 0.1
                self._generation_stats['average_tokens_per_second'] = (
                    alpha * tokens_per_second + 
                    (1 - alpha) * self._generation_stats['average_tokens_per_second']
                )
    
    def _format_generation_error(self, error: Exception, prompt: str, config: GenerationConfig) -> str:
        """
        Format generation error with helpful information.
        
        Args:
            error: The exception that occurred
            prompt: The input prompt
            config: Generation configuration
            
        Returns:
            Formatted error message
        """
        error_str = str(error)
        
        if "out of memory" in error_str.lower():
            return (f"Out of memory during text generation. "
                   f"Try reducing max_tokens ({config.max_tokens}) or context size.")
        
        elif "context" in error_str.lower() and "length" in error_str.lower():
            return (f"Prompt exceeds model context length. "
                   f"Current context: {self._context_length} tokens, "
                   f"prompt length: ~{len(prompt)//4} tokens.")
        
        elif "timeout" in error_str.lower():
            return f"Text generation timed out. Try reducing max_tokens or complexity."
        
        elif "invalid" in error_str.lower() and "parameter" in error_str.lower():
            return f"Invalid generation parameters: {error}"
        
        else:
            return f"Text generation failed: {error}"
    
    def unload_model(self) -> bool:
        """
        Unload the current model and clean up resources.
        
        Returns:
            True if successful, False otherwise
        """
        try:
            if self.model is not None:
                self.logger.info("Unloading ctransformers model...")
                
                # ctransformers doesn't have explicit unload method
                # Clear the model reference
                self.model = None
                
                # Force garbage collection to free memory
                import gc
                gc.collect()
                
                # On CUDA systems, try to clear GPU memory
                if self._hardware_acceleration in ['cuda', 'gpu']:
                    try:
                        # Try to clear CUDA cache if available
                        import torch
                        if torch.cuda.is_available():
                            torch.cuda.empty_cache()
                            self.logger.debug("CUDA cache cleared")
                    except ImportError:
                        pass  # torch not available
                    except Exception as e:
                        self.logger.debug(f"Could not clear CUDA cache: {e}")
            
            # Reset all state variables
            self._reset_state()
            
            self.logger.info("Model unloaded successfully")
            return True
            
        except Exception as e:
            self.logger.error(f"Error unloading model: {e}")
            # Still reset state even if cleanup failed
            self._reset_state()
            return False
    
    def _reset_state(self):
        """Reset all internal state variables."""
        self.model_path = None
        self._model_type = None
        self._context_length = None
        self._gpu_layers_used = 0
        self._hardware_acceleration = None
        self._model_metadata = {}
        self.is_loaded = False
        self.memory_usage = 0
        self.load_time = 0.0
        
        # Reset generation statistics
        self._generation_stats = {
            'total_tokens': 0,
            'total_time': 0.0,
            'average_tokens_per_second': 0.0
        }
    
    def get_hardware_info(self) -> HardwareInfo:
        """
        Get comprehensive hardware information for ctransformers backend.
        
        Returns:
            HardwareInfo object with current hardware status
        """
        if self.hardware_info is not None:
            return self.hardware_info
        
        # Use the hardware detector from the parent class
        import sys
        import os
        sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
        from core.hardware_detector import HardwareDetector
        detector = HardwareDetector()
        
        hw_info = detector.get_hardware_info()
        
        # Add ctransformers-specific hardware support information
        supported_hardware = [HardwareType.CPU]  # CPU is always supported
        
        # Check for GPU acceleration support
        if hw_info.gpu_count > 0:
            # Check CUDA support (NVIDIA)
            nvidia_gpus = [gpu for gpu in hw_info.gpu_devices if gpu.get('vendor') == 'nvidia']
            if nvidia_gpus and self._check_cuda_support():
                supported_hardware.append(HardwareType.CUDA)
                self.logger.debug(f"CUDA support available for {len(nvidia_gpus)} NVIDIA GPU(s)")
            
            # Check ROCm support (AMD)
            amd_gpus = [gpu for gpu in hw_info.gpu_devices if gpu.get('vendor') == 'amd']
            if amd_gpus and self._check_rocm_support():
                supported_hardware.append(HardwareType.ROCM)
                self.logger.debug(f"ROCm support available for {len(amd_gpus)} AMD GPU(s)")
            
            # Check Metal support (Apple)
            if self._check_metal_support():
                supported_hardware.append(HardwareType.METAL)
                self.logger.debug("Metal support available on macOS")
        
        # Update supported hardware in the hardware info
        hw_info.supported_hardware = supported_hardware
        
        # Add ctransformers-specific recommendations
        if not hw_info.recommended_backend:
            hw_info.recommended_backend = "ctransformers"
        
        # Cache the result
        self.hardware_info = hw_info
        
        self.logger.info(f"Hardware support: {[hw.value for hw in supported_hardware]}")
        
        return hw_info
    
    def get_model_info(self) -> Dict[str, Any]:
        """
        Get comprehensive information about the currently loaded model.
        
        Returns:
            Dictionary with model information
        """
        base_info = super().get_model_info()
        
        # Always include backend information
        base_info['backend'] = self.config.name
        base_info['backend_version'] = self._get_backend_version()
        
        if self.is_loaded:
            # Add ctransformers-specific information
            ctransformers_info = {
                'model_type': self._model_type,
                'context_length': self._context_length,
                'gpu_layers_used': self._gpu_layers_used,
                'hardware_acceleration': self._hardware_acceleration,
                'model_metadata': self._model_metadata,
                'generation_stats': self._generation_stats.copy(),
            }
            
            base_info.update(ctransformers_info)
        
        return base_info
    
    def _get_backend_version(self) -> str:
        """Get ctransformers version information."""
        try:
            import ctransformers
            return getattr(ctransformers, '__version__', 'unknown')
        except ImportError:
            return "unknown"
    
    def get_generation_stats(self) -> Dict[str, Any]:
        """
        Get generation performance statistics.
        
        Returns:
            Dictionary with generation statistics
        """
        return self._generation_stats.copy()
    
    def reset_generation_stats(self):
        """Reset generation performance statistics."""
        self._generation_stats = {
            'total_tokens': 0,
            'total_time': 0.0,
            'average_tokens_per_second': 0.0
        }
        self.logger.info("Generation statistics reset")
    
    def validate_configuration(self) -> Tuple[bool, List[str]]:
        """
        Validate the current backend configuration.
        
        Returns:
            Tuple of (is_valid, list_of_issues)
        """
        issues = []
        
        # Check if backend is available
        is_available, error = self.is_available()
        if not is_available:
            issues.append(f"Backend not available: {error}")
        
        # Validate configuration parameters
        if self.config.context_size < 512:
            issues.append("Context size too small (minimum 512)")
        elif self.config.context_size > 32768:
            issues.append("Context size very large (may cause memory issues)")
        
        if self.config.gpu_enabled:
            hw_info = self.get_hardware_info()
            if hw_info.gpu_count == 0:
                issues.append("GPU enabled but no GPUs detected")
            elif not any(hw in hw_info.supported_hardware for hw in [HardwareType.CUDA, HardwareType.ROCM, HardwareType.METAL]):
                issues.append("GPU enabled but no supported GPU acceleration found")
        
        if hasattr(self.config, 'batch_size') and self.config.batch_size > 2048:
            issues.append("Batch size very large (may cause memory issues)")
        
        return len(issues) == 0, issues