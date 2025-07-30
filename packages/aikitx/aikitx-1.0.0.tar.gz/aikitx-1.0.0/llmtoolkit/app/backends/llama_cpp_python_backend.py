"""
llama-cpp-python Backend Implementation

This module implements the llama-cpp-python backend for GGUF model loading
and inference with GPU acceleration support for CUDA, ROCm, Metal, and Vulkan.

Features:
- GGUF model format support
- GPU acceleration (CUDA, ROCm, Metal, Vulkan)
- Automatic hardware detection and optimization
- Comprehensive error handling and validation
- Resource management and cleanup
"""

import logging
import time
import os
import platform
import subprocess
import gc
from pathlib import Path
from typing import Dict, Any, Optional, Tuple, List, Union

from llmtoolkit.app.core.model_backends import (
    ModelBackend, BackendConfig, HardwareInfo, LoadingResult, 
    GenerationConfig, HardwareType, BackendError, InstallationError, 
    HardwareError, ModelLoadingError
)


class LlamaCppPythonBackend(ModelBackend):
    """
    llama-cpp-python backend implementation with comprehensive GGUF support.
    
    This backend provides:
    - GGUF model format support
    - GPU acceleration (CUDA, ROCm, Metal, Vulkan)
    - Automatic hardware detection and optimization
    - Comprehensive error handling and validation
    - Resource management and cleanup
    """
    
    # File extensions that indicate GGUF format
    GGUF_EXTENSIONS = {'.gguf', '.ggml', '.bin'}
    
    def __init__(self, config: BackendConfig):
        """Initialize the llama-cpp-python backend."""
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
        Check if llama-cpp-python is available and properly configured.
        
        Returns:
            Tuple of (is_available, error_message)
        """
        try:
            # Try to import llama_cpp
            import llama_cpp
            
            # Get version info safely
            try:
                version = getattr(llama_cpp, '__version__', 'unknown')
                self.logger.info(f"llama-cpp-python version: {version}")
            except:
                self.logger.info("llama-cpp-python version: unknown")
            
            # Check if we can create a basic model instance (validates installation)
            try:
                # This will fail gracefully if llama-cpp-python is not properly installed
                params = llama_cpp.llama_context_params()
                self.logger.debug("llama-cpp-python context params creation successful")
            except AttributeError as e:
                return False, f"llama-cpp-python components not available: {e}"
            
            # Check for GPU support if enabled
            if self.config.gpu_enabled:
                gpu_support_info = self._check_gpu_support()
                if gpu_support_info:
                    self.logger.info(f"GPU support detected: {gpu_support_info}")
            
            return True, None
            
        except ImportError as e:
            error_msg = f"llama-cpp-python not installed: {e}"
            self.logger.warning(error_msg)
            return False, error_msg
        except Exception as e:
            error_msg = f"Error checking llama-cpp-python availability: {e}"
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
            
        # Check Vulkan support
        if self._check_vulkan_support():
            gpu_info.append("Vulkan")
        
        return ", ".join(gpu_info) if gpu_info else None
    
    def _check_cuda_support(self) -> bool:
        """Check if CUDA support is available."""
        try:
            # Check if nvidia-smi is available
            result = subprocess.run(['nvidia-smi'], capture_output=True, timeout=5)
            if result.returncode != 0:
                return False
                
            # Check if llama-cpp-python has CUDA support
            import llama_cpp
            
            # Check for GGML_USE_CUBLAS constant
            if hasattr(llama_cpp, 'GGML_USE_CUBLAS'):
                has_cuda = bool(llama_cpp.GGML_USE_CUBLAS)
                if has_cuda:
                    return True
            
            # Check if 'cuda' is in the library path
            if hasattr(llama_cpp, '__file__'):
                if 'cuda' in str(llama_cpp.__file__).lower():
                    return True
            
            # Try to create a model with n_gpu_layers > 0
            try:
                params = llama_cpp.llama_context_params()
                if hasattr(params, 'n_gpu_layers'):
                    return True
            except:
                pass
                
            return False
            
        except (subprocess.TimeoutExpired, subprocess.CalledProcessError, FileNotFoundError, ImportError):
            return False
    
    def _check_rocm_support(self) -> bool:
        """Check if ROCm support is available."""
        try:
            # Check if rocm-smi is available
            result = subprocess.run(['rocm-smi'], capture_output=True, timeout=5)
            if result.returncode != 0:
                return False
                
            # Check if llama-cpp-python has ROCm support
            import llama_cpp
            
            # Check for GGML_USE_ROCM constant
            if hasattr(llama_cpp, 'GGML_USE_ROCM'):
                has_rocm = bool(llama_cpp.GGML_USE_ROCM)
                if has_rocm:
                    return True
            
            # Check if 'rocm' is in the library path
            if hasattr(llama_cpp, '__file__'):
                if 'rocm' in str(llama_cpp.__file__).lower():
                    return True
                    
            return False
            
        except (subprocess.TimeoutExpired, subprocess.CalledProcessError, FileNotFoundError, ImportError):
            return False
    
    def _check_metal_support(self) -> bool:
        """Check if Metal support is available (macOS only)."""
        if platform.system() != "Darwin":
            return False
        
        try:
            # Check if we're on macOS with Metal support
            result = subprocess.run(['system_profiler', 'SPDisplaysDataType'], 
                                  capture_output=True, text=True, timeout=10)
            if result.returncode != 0 or 'Metal' not in result.stdout:
                return False
                
            # Check if llama-cpp-python has Metal support
            import llama_cpp
            
            # Check for GGML_USE_METAL constant
            if hasattr(llama_cpp, 'GGML_USE_METAL'):
                has_metal = bool(llama_cpp.GGML_USE_METAL)
                if has_metal:
                    return True
            
            # Check if 'metal' is in the library path
            if hasattr(llama_cpp, '__file__'):
                if 'metal' in str(llama_cpp.__file__).lower():
                    return True
                    
            return False
            
        except (subprocess.TimeoutExpired, subprocess.CalledProcessError, FileNotFoundError, ImportError):
            return False
            
    def _check_vulkan_support(self) -> bool:
        """Check if Vulkan support is available."""
        try:
            # Check for vulkaninfo utility
            result = subprocess.run(['vulkaninfo'], capture_output=True, timeout=5)
            if result.returncode != 0:
                return False
                
            # Check if llama-cpp-python has Vulkan support
            import llama_cpp
            
            # Check for GGML_USE_VULKAN constant
            if hasattr(llama_cpp, 'GGML_USE_VULKAN'):
                has_vulkan = bool(llama_cpp.GGML_USE_VULKAN)
                if has_vulkan:
                    return True
            
            # Check if 'vulkan' is in the library path
            if hasattr(llama_cpp, '__file__'):
                if 'vulkan' in str(llama_cpp.__file__).lower():
                    return True
                    
            return False
            
        except (subprocess.TimeoutExpired, subprocess.CalledProcessError, FileNotFoundError, ImportError):
            return False
    
    def load_model(self, model_path: str, **kwargs) -> LoadingResult:
        """
        Load a GGUF model using llama-cpp-python with comprehensive validation and optimization.
        
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
            
            # Import llama_cpp with error handling
            try:
                import llama_cpp
                self.logger.debug("llama-cpp-python imported successfully")
            except ImportError as e:
                return LoadingResult(
                    success=False,
                    backend_used=self.config.name,
                    hardware_used="none",
                    load_time=0.0,
                    error_message=f"llama-cpp-python not available: {e}"
                )
            
            # Prepare optimized loading configuration
            load_config = self._prepare_load_config(model_path, **kwargs)
            
            self.logger.info(f"Loading GGUF model: {Path(model_path).name}")
            self.logger.info(f"GPU layers: {load_config.get('n_gpu_layers', 0)}")
            self.logger.info(f"Context size: {load_config.get('n_ctx', self.config.context_size)}")
            
            # Attempt model loading with retry logic
            self.model = self._load_model_with_retry(
                model_path, load_config, llama_cpp.Llama
            )
            
            # Store model information and metadata
            self.model_path = model_path
            self._context_length = load_config.get('n_ctx', self.config.context_size)
            self._gpu_layers_used = load_config.get('n_gpu_layers', 0)
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
                'extension': path.suffix.lower(),
                'file_name': path.name
            }
            
        except Exception as e:
            return {'valid': False, 'error': f"Error validating model file: {e}"}
    
    def _load_model_with_retry(self, model_path: str, load_config: Dict[str, Any], 
                              model_class) -> Any:
        """
        Load model with retry logic for GPU fallback.
        
        Args:
            model_path: Path to model file
            load_config: Loading configuration
            model_class: llama-cpp-python model class
            
        Returns:
            Loaded model instance
        """
        original_gpu_layers = load_config.get('n_gpu_layers', 0)
        
        try:
            # First attempt with original configuration
            self.logger.debug(f"Attempting to load with GPU layers: {original_gpu_layers}")
            return model_class(
                model_path=model_path,
                **load_config
            )
            
        except Exception as e:
            if original_gpu_layers > 0:
                # GPU loading failed, try with reduced GPU layers
                self.logger.warning(f"GPU loading failed ({e}), trying with reduced GPU layers")
                
                for gpu_layers in [original_gpu_layers // 2, original_gpu_layers // 4, 0]:
                    try:
                        load_config_retry = load_config.copy()
                        load_config_retry['n_gpu_layers'] = gpu_layers
                        
                        self.logger.debug(f"Retry attempt with GPU layers: {gpu_layers}")
                        return model_class(
                            model_path=model_path,
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
        context_size = load_config.get('n_ctx', self.config.context_size)
        context_overhead = (context_size * 4) // (1024 * 1024)  # Rough estimate: 4 bytes per token
        memory_usage += context_overhead
        
        # Add GPU memory overhead if using GPU
        gpu_layers = load_config.get('n_gpu_layers', 0)
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
        gpu_layers = load_config.get('n_gpu_layers', 0)
        
        if gpu_layers == 0:
            return "cpu"
        
        # Determine GPU type based on system
        if self._check_cuda_support():
            return "cuda"
        elif self._check_rocm_support():
            return "rocm"
        elif self._check_metal_support():
            return "metal"
        elif self._check_vulkan_support():
            return "vulkan"
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
    
    def _prepare_load_config(self, model_path: str, **kwargs) -> Dict[str, Any]:
        """
        Prepare optimized configuration for model loading.
        
        Args:
            model_path: Path to the model file
            **kwargs: Additional configuration parameters
            
        Returns:
            Dictionary with loading configuration
        """
        config = {}
        
        # Context length configuration
        context_length = kwargs.get('context_length', self.config.context_size)
        config['n_ctx'] = context_length
        
        # GPU configuration with intelligent layer estimation
        if self.config.gpu_enabled:
            gpu_layers = self._determine_optimal_gpu_layers(model_path, kwargs)
            if gpu_layers > 0:
                config['n_gpu_layers'] = gpu_layers
                self.logger.info(f"Using GPU acceleration with {gpu_layers} layers")
            else:
                self.logger.info("Using CPU-only mode")
        else:
            self.logger.info("GPU disabled in configuration, using CPU-only mode")
        
        # Threading configuration
        threads = kwargs.get('threads', self.config.threads)
        if threads > 0:
            config['n_threads'] = threads
        elif threads == -1:  # Auto-detect
            config['n_threads'] = self._get_optimal_thread_count()
        
        # Batch size optimization
        batch_size = kwargs.get('batch_size', self.config.batch_size)
        if batch_size > 0:
            config['n_batch'] = batch_size
        
        # Memory mapping (always use for better performance)
        config['use_mmap'] = True
        
        # Verbose mode for debugging
        config['verbose'] = False
        
        # Custom arguments (highest priority)
        if self.config.custom_args:
            config.update(self.config.custom_args)
        
        # Override with explicit kwargs
        for key, value in kwargs.items():
            if key not in ['context_length', 'threads', 'batch_size']:
                config[key] = value
        
        self.logger.debug(f"Final loading configuration: {config}")
        return config
    
    def _determine_optimal_gpu_layers(self, model_path: str, kwargs: Dict[str, Any]) -> int:
        """
        Determine optimal number of GPU layers based on hardware and model.
        
        Args:
            model_path: Path to model file
            kwargs: Additional parameters
            
        Returns:
            Optimal number of GPU layers
        """
        # Check if GPU layers explicitly specified
        if 'n_gpu_layers' in kwargs:
            return kwargs['n_gpu_layers']
        
        if self.config.gpu_layers != -1:
            return self.config.gpu_layers
        
        # Auto-detection based on hardware and model
        return self._estimate_gpu_layers(model_path)
    
    def _estimate_gpu_layers(self, model_path: str) -> int:
        """
        Estimate optimal GPU layers based on model size and available VRAM.
        
        Args:
            model_path: Path to model file
            
        Returns:
            Estimated number of GPU layers
        """
        try:
            # Get model size
            model_size_mb = Path(model_path).stat().st_size // (1024 * 1024)
            
            # Check available VRAM
            vram_mb = self._get_available_vram()
            
            # If we couldn't detect VRAM, use model size heuristic
            if vram_mb <= 0:
                # Estimate layers based on model size (rough heuristic)
                if model_size_mb < 1000:  # < 1GB
                    return 32
                elif model_size_mb < 4000:  # < 4GB
                    return 28
                elif model_size_mb < 8000:  # < 8GB
                    return 24
                elif model_size_mb < 16000:  # < 16GB
                    return 20
                else:
                    return 16
            
            # If we have VRAM info, use it for better estimation
            # Each layer is roughly 2-5% of model size
            layer_size_estimate = model_size_mb * 0.04  # 4% per layer
            
            # Use 80% of available VRAM for layers
            usable_vram = vram_mb * 0.8
            
            # Calculate how many layers would fit
            max_layers = int(usable_vram / layer_size_estimate)
            
            # Cap at reasonable values
            max_layers = min(max_layers, 100)  # No more than 100 layers
            max_layers = max(max_layers, 0)    # At least 0 layers
            
            self.logger.debug(f"Estimated {max_layers} GPU layers based on {vram_mb}MB VRAM")
            return max_layers
            
        except Exception as e:
            self.logger.debug(f"Error estimating GPU layers: {e}")
            return 32  # Default fallback
    
    def _get_available_vram(self) -> int:
        """
        Get available VRAM in MB.
        
        Returns:
            Available VRAM in MB, or 0 if unknown
        """
        try:
            # Try NVIDIA GPU first
            if self._check_cuda_support():
                try:
                    import pynvml
                    pynvml.nvmlInit()
                    device_count = pynvml.nvmlDeviceGetCount()
                    
                    if device_count > 0:
                        # Use first GPU for simplicity
                        handle = pynvml.nvmlDeviceGetHandleByIndex(0)
                        info = pynvml.nvmlDeviceGetMemoryInfo(handle)
                        free_vram = info.free // (1024 * 1024)  # Convert to MB
                        return free_vram
                except:
                    pass
            
            # Try AMD GPU
            if self._check_rocm_support():
                try:
                    # This is a simplified approach - in a real implementation
                    # you might parse rocm-smi output
                    result = subprocess.run(['rocm-smi', '--showmeminfo', 'vram'], 
                                         capture_output=True, text=True)
                    
                    if result.returncode == 0:
                        # Very rough parsing - would need improvement in real code
                        for line in result.stdout.split('\n'):
                            if 'free' in line.lower():
                                parts = line.split()
                                for i, part in enumerate(parts):
                                    if part.lower() == 'free':
                                        try:
                                            return int(parts[i+1])
                                        except:
                                            pass
                except:
                    pass
            
            # No VRAM info available
            return 0
            
        except Exception as e:
            self.logger.debug(f"Error getting VRAM info: {e}")
            return 0
    
    def _get_optimal_thread_count(self) -> int:
        """Get optimal thread count for CPU inference."""
        try:
            cpu_count = os.cpu_count() or 4
            # Use 75% of available cores, but at least 1 and at most 16
            optimal_threads = max(1, min(16, int(cpu_count * 0.75)))
            return optimal_threads
        except Exception:
            return 4  # Safe fallback
    
    def generate_text(self, prompt: str, config: GenerationConfig) -> str:
        """
        Generate text from the given prompt.
        
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
            raise ModelLoadingError("No model loaded")
        
        try:
            start_time = time.time()
            
            # Convert GenerationConfig to llama-cpp-python parameters
            params = {
                'max_tokens': config.max_tokens,
                'temperature': config.temperature,
                'top_p': config.top_p,
                'top_k': config.top_k,
                'repeat_penalty': config.repeat_penalty,
                'seed': config.seed if config.seed >= 0 else -1,
                'stop': config.stop_sequences if config.stop_sequences else None,
                'stream': config.stream
            }
            
            # Generate text
            self.logger.debug(f"Generating text with prompt length: {len(prompt)}")
            
            if config.stream:
                # For streaming, we need to collect tokens
                generated_text = ""
                for chunk in self.model(prompt, **params):
                    token = chunk.get('choices', [{}])[0].get('text', '')
                    generated_text += token
                    
                result = generated_text
            else:
                # For non-streaming, we get the full response
                response = self.model(prompt, **params)
                result = response.get('choices', [{}])[0].get('text', '')
            
            # Update generation statistics
            generation_time = time.time() - start_time
            tokens_generated = len(result.split())
            
            self._generation_stats['total_tokens'] += tokens_generated
            self._generation_stats['total_time'] += generation_time
            
            if self._generation_stats['total_time'] > 0:
                self._generation_stats['average_tokens_per_second'] = (
                    self._generation_stats['total_tokens'] / self._generation_stats['total_time']
                )
            
            self.logger.debug(f"Generated {tokens_generated} tokens in {generation_time:.2f}s "
                           f"({tokens_generated/generation_time:.2f} tokens/s)")
            
            return result
            
        except Exception as e:
            error_msg = f"Text generation failed: {e}"
            self.logger.error(error_msg)
            raise BackendError(error_msg)
    
    def unload_model(self) -> bool:
        """
        Unload the current model.
        
        Returns:
            True if successful, False otherwise
        """
        try:
            if self.model is not None:
                # llama-cpp-python doesn't have an explicit unload method
                # Set to None to allow garbage collection
                self.model = None
                
                # Force garbage collection to reclaim memory
                gc.collect()
                
                self.is_loaded = False
                self.logger.info("Model unloaded successfully")
                return True
            
            return True  # No model to unload
            
        except Exception as e:
            self.logger.error(f"Error unloading model: {e}")
            return False
    
    def get_hardware_info(self) -> HardwareInfo:
        """
        Get information about hardware acceleration.
        
        Returns:
            HardwareInfo object with current hardware status
        """
        hardware_info = HardwareInfo()
        
        try:
            # Detect CPU info
            hardware_info.cpu_cores = os.cpu_count() or 4
            
            # Detect system RAM
            import psutil
            hardware_info.total_ram = psutil.virtual_memory().total // (1024 * 1024)  # MB
            
            # Detect NVIDIA GPUs
            if self._check_cuda_support():
                try:
                    import pynvml
                    pynvml.nvmlInit()
                    device_count = pynvml.nvmlDeviceGetCount()
                    
                    hardware_info.gpu_count = device_count
                    hardware_info.supported_hardware.append(HardwareType.CUDA)
                    
                    total_vram = 0
                    for i in range(device_count):
                        handle = pynvml.nvmlDeviceGetHandleByIndex(i)
                        name = pynvml.nvmlDeviceGetName(handle)
                        memory = pynvml.nvmlDeviceGetMemoryInfo(handle)
                        vram_mb = memory.total // (1024 * 1024)
                        total_vram += vram_mb
                        
                        hardware_info.gpu_devices.append({
                            'index': i,
                            'name': name,
                            'vram_mb': vram_mb,
                            'type': 'NVIDIA'
                        })
                    
                    hardware_info.total_vram = total_vram
                    
                except Exception as e:
                    self.logger.debug(f"Error getting NVIDIA GPU info: {e}")
            
            # Detect AMD GPUs
            if self._check_rocm_support():
                hardware_info.supported_hardware.append(HardwareType.ROCM)
                # Add AMD GPU detection code here
            
            # Detect Metal support
            if self._check_metal_support():
                hardware_info.supported_hardware.append(HardwareType.METAL)
                # Add Metal GPU detection code here
                
            # Detect Vulkan support
            if self._check_vulkan_support():
                hardware_info.supported_hardware.append(HardwareType.VULKAN)
                # Add Vulkan GPU detection code here
            
            # Set recommended backend
            if hardware_info.gpu_count > 0:
                hardware_info.recommended_backend = "llama-cpp-python"
            else:
                hardware_info.recommended_backend = "llama-cpp-python"  # CPU fallback
            
        except Exception as e:
            self.logger.error(f"Error getting hardware info: {e}")
        
        return hardware_info