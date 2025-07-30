"""
Enhanced Transformers Backend Implementation

This module implements the transformers backend with multi-format support including GGUF, 
safetensors, PyTorch bin files, and native HuggingFace models with comprehensive GPU acceleration.

Features:
- Multi-format support: GGUF, safetensors, PyTorch bin, HuggingFace models
- Native safetensors loading with secure tensor handling
- PyTorch bin file loading with automatic config detection
- Automatic tokenizer and config loading for all formats
- GPU acceleration using accelerate library (CUDA, ROCm, MPS)
- Unified model interface across different formats
- Efficient memory management and model caching
- Comprehensive error handling and validation
"""

import logging
import time
import os
import platform
import subprocess
import tempfile
import shutil
from pathlib import Path
from typing import Dict, Any, Optional, Tuple, List, Union, Callable
import json
import gc
import hashlib

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

try:
    import torch
    import transformers
    import accelerate
    import psutil
    DEPENDENCIES_AVAILABLE = True
    
    # Try to import safetensors for secure tensor loading
    try:
        import safetensors
        import safetensors.torch
        SAFETENSORS_AVAILABLE = True
    except ImportError:
        SAFETENSORS_AVAILABLE = False
        
except ImportError:
    DEPENDENCIES_AVAILABLE = False
    SAFETENSORS_AVAILABLE = False

from llmtoolkit.app.core.model_backends import (
    ModelBackend, BackendConfig, HardwareInfo, LoadingResult, 
    GenerationConfig, HardwareType, BackendError, InstallationError, 
    HardwareError, ModelLoadingError
)


class TransformersBackend(ModelBackend):
    """
    Enhanced Transformers backend implementation with multi-format support.
    
    This backend provides:
    - Multi-format support: GGUF, safetensors, PyTorch bin, HuggingFace models
    - Native safetensors loading with secure tensor handling
    - PyTorch bin file loading with automatic config detection
    - Automatic tokenizer and config loading for all formats
    - GPU acceleration using accelerate library
    - Unified model interface across different formats
    - Efficient memory management and caching
    - Support for various quantization formats
    """
    
    # Supported model architectures and their transformers identifiers
    SUPPORTED_ARCHITECTURES = {
        'llama': 'LlamaForCausalLM',
        'llama2': 'LlamaForCausalLM',
        'codellama': 'CodeLlamaForCausalLM',
        'mistral': 'MistralForCausalLM',
        'mixtral': 'MixtralForCausalLM',
        'falcon': 'FalconForCausalLM',
        'mpt': 'MPTForCausalLM',
        'gpt2': 'GPT2LMHeadModel',
        'gptj': 'GPTJForCausalLM',
        'gptneox': 'GPTNeoXForCausalLM',
        'bloom': 'BloomForCausalLM',
        'opt': 'OPTForCausalLM'
    }
    
    # Supported file extensions by format
    GGUF_EXTENSIONS = {'.gguf', '.ggml'}
    SAFETENSORS_EXTENSIONS = {'.safetensors'}
    PYTORCH_EXTENSIONS = {'.bin', '.pt', '.pth'}
    
    # All supported extensions
    SUPPORTED_EXTENSIONS = GGUF_EXTENSIONS | SAFETENSORS_EXTENSIONS | PYTORCH_EXTENSIONS
    
    # Model format types
    FORMAT_GGUF = 'gguf'
    FORMAT_SAFETENSORS = 'safetensors'
    FORMAT_PYTORCH = 'pytorch'
    FORMAT_HUGGINGFACE = 'huggingface'
    
    # Quantization format mappings
    QUANTIZATION_FORMATS = {
        'q4_0': {'bits': 4, 'group_size': 32},
        'q4_1': {'bits': 4, 'group_size': 32},
        'q5_0': {'bits': 5, 'group_size': 32},
        'q5_1': {'bits': 5, 'group_size': 32},
        'q8_0': {'bits': 8, 'group_size': 32},
        'f16': {'bits': 16, 'group_size': -1},
        'f32': {'bits': 32, 'group_size': -1}
    }
    
    def __init__(self, config: BackendConfig):
        """Initialize the transformers backend."""
        super().__init__(config)
        self.model = None
        self.tokenizer = None
        self._model_type = None
        self._format_type = None
        self._device = None
        self._device_map = None
        self._quantization_config = None
        self._model_cache_dir = None
        self._converted_model_path = None
        self._generation_stats = {
            'total_tokens': 0,
            'total_time': 0.0,
            'average_tokens_per_second': 0.0
        }
        
        # Initialize cache directory
        self._setup_cache_directory()
        
    def _setup_cache_directory(self):
        """Setup cache directory for converted models."""
        cache_base = os.path.expanduser("~/.cache/gguf-loader/transformers")
        os.makedirs(cache_base, exist_ok=True)
        self._model_cache_dir = cache_base
        self.logger.info(f"Model cache directory: {self._model_cache_dir}")    
    
    def is_available(self) -> Tuple[bool, Optional[str]]:
        """
        Check if transformers and accelerate are available and properly configured.
        
        Returns:
            Tuple of (is_available, error_message)
        """
        if not DEPENDENCIES_AVAILABLE:
            return False, "Required libraries not installed: transformers, accelerate, torch, or psutil"
        
        try:
            # Check versions
            transformers_version = getattr(transformers, '__version__', 'unknown')
            accelerate_version = getattr(accelerate, '__version__', 'unknown')
            torch_version = getattr(torch, '__version__', 'unknown')
            
            self.logger.info(f"transformers version: {transformers_version}")
            self.logger.info(f"accelerate version: {accelerate_version}")
            self.logger.info(f"torch version: {torch_version}")
            
            # Check safetensors availability
            if SAFETENSORS_AVAILABLE:
                import safetensors
                safetensors_version = getattr(safetensors, '__version__', 'unknown')
                self.logger.info(f"safetensors version: {safetensors_version}")
            else:
                self.logger.warning("safetensors not available - safetensors format support will be limited")
            
            # Check for essential components
            from transformers import AutoModelForCausalLM, AutoTokenizer
            from accelerate import Accelerator
            
            # Check GPU support if enabled
            if self.config.gpu_enabled:
                gpu_support_info = self._check_gpu_support()
                if gpu_support_info:
                    self.logger.info(f"GPU support detected: {gpu_support_info}")
            
            return True, None
            
        except ImportError as e:
            error_msg = f"Required libraries not installed: {e}"
            self.logger.warning(error_msg)
            return False, error_msg
        except Exception as e:
            error_msg = f"Error checking transformers availability: {e}"
            self.logger.error(error_msg)
            return False, error_msg
    
    def _check_gpu_support(self) -> Optional[str]:
        """
        Check what GPU acceleration is available.
        
        Returns:
            String describing available GPU support or None
        """
        gpu_info = []
        
        try:
            import torch
            
            # Check CUDA support
            if torch.cuda.is_available():
                gpu_count = torch.cuda.device_count()
                gpu_info.append(f"CUDA ({gpu_count} devices)")
                
                # Log GPU details
                for i in range(gpu_count):
                    gpu_name = torch.cuda.get_device_name(i)
                    gpu_memory = torch.cuda.get_device_properties(i).total_memory // (1024**3)
                    self.logger.debug(f"GPU {i}: {gpu_name} ({gpu_memory}GB)")
            
            # Check ROCm support (AMD)
            if hasattr(torch, 'hip') and torch.hip.is_available():
                gpu_info.append("ROCm")
            
            # Check MPS support (Apple Silicon)
            if hasattr(torch.backends, 'mps') and torch.backends.mps.is_available():
                gpu_info.append("MPS (Apple Silicon)")
            
        except Exception as e:
            self.logger.debug(f"Error checking GPU support: {e}")
        
        return ", ".join(gpu_info) if gpu_info else None    

    def load_model(self, model_path: str, **kwargs) -> LoadingResult:
        """
        Load a model using transformers with multi-format support.
        
        Supports: GGUF, safetensors, PyTorch bin, and HuggingFace models
        
        Args:
            model_path: Path to the model file or directory
            **kwargs: Additional loading parameters
            
        Returns:
            LoadingResult with detailed success/failure information
        """
        start_time = time.time()
        
        try:
            # Validate model file and detect format
            validation_result = self._validate_model_file(model_path)
            if not validation_result['valid']:
                return LoadingResult(
                    success=False,
                    backend_used=self.config.name,
                    hardware_used="none",
                    load_time=0.0,
                    error_message=validation_result['error']
                )
            
            format_type = validation_result['format_type']
            self.logger.info(f"Detected format: {format_type}")
            
            # Import required libraries
            try:
                import torch
                from transformers import AutoModelForCausalLM, AutoTokenizer
                from accelerate import Accelerator
                self.logger.debug("Required libraries imported successfully")
            except ImportError as e:
                return LoadingResult(
                    success=False,
                    backend_used=self.config.name,
                    hardware_used="none",
                    load_time=0.0,
                    error_message=f"Required libraries not available: {e}"
                )
            
            # Detect model type and architecture
            model_type = kwargs.get('model_type') or self._detect_model_type(model_path)
            architecture = self._get_model_architecture(model_type)
            
            self.logger.info(f"Loading model: {Path(model_path).name}")
            self.logger.info(f"Format: {format_type}, Type: {model_type}, Architecture: {architecture}")
            
            # Setup device and quantization
            device_config = self._setup_device_configuration(**kwargs)
            quantization_config = self._setup_quantization_configuration(model_path, **kwargs)
            
            # Load model based on format
            if format_type in [self.FORMAT_SAFETENSORS, self.FORMAT_PYTORCH, self.FORMAT_HUGGINGFACE]:
                # Direct loading for supported formats
                model_path_to_load = model_path
                self.tokenizer = self._load_tokenizer_for_format(model_path, format_type, model_type)
            else:
                # GGUF or other formats that need conversion
                model_path_to_load = self._get_or_convert_model(model_path, model_type, validation_result)
                self.tokenizer = self._load_tokenizer(model_path_to_load, model_type)
            
            # Load model with optimized configuration
            load_config = self._prepare_model_load_config(
                model_path_to_load, model_type, device_config, quantization_config, **kwargs
            )
            
            self.logger.info(f"Loading model with device: {device_config['device']}")
            if quantization_config:
                self.logger.info(f"Using quantization: {quantization_config}")
            
            # Load the model using format-specific method
            self.model = self._load_model_by_format(
                model_path_to_load, format_type, architecture, load_config, AutoModelForCausalLM
            )
            
            # Setup accelerate if using GPU
            if device_config['device'] != 'cpu':
                self._setup_accelerate(device_config)
            
            # Store model information
            self.model_path = model_path
            self._converted_model_path = model_path_to_load if model_path_to_load != model_path else None
            self._model_type = model_type
            self._format_type = format_type
            self._device = device_config['device']
            self._device_map = device_config.get('device_map')
            self._quantization_config = quantization_config
            self.is_loaded = True
            
            # Calculate performance metrics
            load_time = time.time() - start_time
            self.load_time = load_time
            
            # Get model information and estimate memory usage
            model_info = self._get_model_metadata(model_path, validation_result, architecture)
            self.memory_usage = self._estimate_memory_usage(model_info, device_config, quantization_config)
            
            hardware_used = self._determine_hardware_used(device_config)
            
            self.logger.info(f"Model loaded successfully in {load_time:.2f}s")
            self.logger.info(f"Format: {format_type}, Hardware: {hardware_used}, Memory: {self.memory_usage}MB")
            
            return LoadingResult(
                success=True,
                backend_used=self.config.name,
                hardware_used=hardware_used,
                load_time=load_time,
                memory_usage=self.memory_usage,
                model_info={
                    'format_type': format_type,
                    'model_type': model_type,
                    'architecture': architecture,
                    'device': self._device,
                    'device_map': str(self._device_map) if self._device_map else None,
                    'quantization': str(quantization_config) if quantization_config else None,
                    'converted_model_path': self._converted_model_path,
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
        """Validate the model file or directory and detect format."""
        try:
            path = Path(model_path)
            
            if not path.exists():
                return {'valid': False, 'error': f"Model file does not exist: {model_path}"}
            
            if path.is_dir():
                return self._validate_model_directory(path)
            else:
                return self._validate_model_file_single(path)
                
        except Exception as e:
            return {'valid': False, 'error': f"Error validating model file: {e}"}
    
    def _validate_model_directory(self, path: Path) -> Dict[str, Any]:
        """Validate a model directory (HuggingFace format)."""
        # Check if it's a HuggingFace model directory
        is_hf_model = self._is_huggingface_model(path)
        
        if not is_hf_model:
            return {'valid': False, 'error': f"Directory is not a valid HuggingFace model: {path}"}
        
        # Calculate total size
        file_size = sum(
            f.stat().st_size 
            for f in path.rglob('*') 
            if f.is_file()
        )
        
        # Detect specific format within HuggingFace directory
        format_type = self._detect_hf_directory_format(path)
        
        return {
            'valid': True,
            'file_size': file_size,
            'file_size_mb': file_size / (1024 * 1024),
            'format_type': format_type,
            'extension': '',
            'is_hf_model': True,
            'is_directory': True
        }
    
    def _validate_model_file_single(self, path: Path) -> Dict[str, Any]:
        """Validate a single model file."""
        if not path.is_file():
            return {'valid': False, 'error': f"Path is not a file: {path}"}
        
        file_size = path.stat().st_size
        if file_size == 0:
            return {'valid': False, 'error': f"Model file is empty: {path}"}
        
        extension = path.suffix.lower()
        format_type = self._detect_file_format(path)
        
        # Additional validation based on format
        validation_result = self._validate_format_specific(path, format_type)
        if not validation_result['valid']:
            return validation_result
        
        return {
            'valid': True,
            'file_size': file_size,
            'file_size_mb': file_size / (1024 * 1024),
            'format_type': format_type,
            'extension': extension,
            'is_hf_model': False,
            'is_directory': False
        }
    
    def _detect_file_format(self, path: Path) -> str:
        """Detect format type from file extension and content."""
        extension = path.suffix.lower()
        
        if extension in self.GGUF_EXTENSIONS:
            return self.FORMAT_GGUF
        elif extension in self.SAFETENSORS_EXTENSIONS:
            return self.FORMAT_SAFETENSORS
        elif extension in self.PYTORCH_EXTENSIONS:
            return self._detect_pytorch_format(path)
        else:
            return 'unknown'
    
    def _detect_pytorch_format(self, path: Path) -> str:
        """Detect if a .bin/.pt/.pth file is PyTorch or GGUF format."""
        try:
            # Try to read the first few bytes to detect format
            with open(path, 'rb') as f:
                header = f.read(16)
                
            # GGUF files start with 'GGUF' magic bytes
            if header.startswith(b'GGUF'):
                return self.FORMAT_GGUF
            
            # Try to load as PyTorch tensor
            try:
                import torch
                torch.load(path, map_location='cpu', weights_only=True)
                return self.FORMAT_PYTORCH
            except:
                # If it's not a valid PyTorch file, might be GGUF with .bin extension
                return self.FORMAT_GGUF
                
        except Exception:
            return self.FORMAT_PYTORCH  # Default assumption
    
    def _detect_hf_directory_format(self, path: Path) -> str:
        """Detect the primary format within a HuggingFace directory."""
        # Check for safetensors files first (preferred)
        if any(f.suffix == '.safetensors' for f in path.glob('*.safetensors')):
            return self.FORMAT_SAFETENSORS
        
        # Check for PyTorch bin files
        if any(f.suffix == '.bin' for f in path.glob('*.bin')):
            return self.FORMAT_PYTORCH
        
        # Check for other PyTorch formats
        if any(f.suffix in ['.pt', '.pth'] for f in path.glob('*')):
            return self.FORMAT_PYTORCH
        
        return self.FORMAT_HUGGINGFACE
    
    def _validate_format_specific(self, path: Path, format_type: str) -> Dict[str, Any]:
        """Perform format-specific validation."""
        try:
            if format_type == self.FORMAT_SAFETENSORS:
                return self._validate_safetensors_file(path)
            elif format_type == self.FORMAT_PYTORCH:
                return self._validate_pytorch_file(path)
            elif format_type == self.FORMAT_GGUF:
                return self._validate_gguf_file(path)
            else:
                return {'valid': True}
                
        except Exception as e:
            return {'valid': False, 'error': f"Format validation failed: {e}"}
    
    def _validate_safetensors_file(self, path: Path) -> Dict[str, Any]:
        """Validate a safetensors file."""
        if not SAFETENSORS_AVAILABLE:
            return {'valid': False, 'error': "safetensors library not available"}
        
        try:
            import safetensors
            # Try to read the header to validate the file
            with open(path, 'rb') as f:
                # Read header length (first 8 bytes)
                header_size = int.from_bytes(f.read(8), 'little')
                if header_size > 100 * 1024 * 1024:  # Sanity check: header shouldn't be > 100MB
                    return {'valid': False, 'error': "Invalid safetensors header size"}
                
                # Try to read and parse header
                header_bytes = f.read(header_size)
                header = json.loads(header_bytes.decode('utf-8'))
                
                if not isinstance(header, dict):
                    return {'valid': False, 'error': "Invalid safetensors header format"}
            
            # Count actual tensors (exclude __metadata__ if present)
            tensor_count = len([k for k in header.keys() if k != "__metadata__"])
            return {'valid': True, 'tensor_count': tensor_count}
            
        except Exception as e:
            return {'valid': False, 'error': f"Invalid safetensors file: {e}"}
    
    def _validate_pytorch_file(self, path: Path) -> Dict[str, Any]:
        """Validate a PyTorch file."""
        try:
            import torch
            # Try to load the file to validate it
            state_dict = torch.load(path, map_location='cpu', weights_only=True)
            
            if not isinstance(state_dict, dict):
                return {'valid': False, 'error': "PyTorch file does not contain a state dict"}
            
            return {'valid': True, 'tensor_count': len(state_dict)}
            
        except Exception as e:
            return {'valid': False, 'error': f"Invalid PyTorch file: {e}"}
    
    def _validate_gguf_file(self, path: Path) -> Dict[str, Any]:
        """Validate a GGUF file."""
        try:
            with open(path, 'rb') as f:
                # Check GGUF magic bytes
                magic = f.read(4)
                if magic != b'GGUF':
                    return {'valid': False, 'error': "Not a valid GGUF file (missing magic bytes)"}
                
                # Read version
                version = int.from_bytes(f.read(4), 'little')
                if version < 1 or version > 10:  # Reasonable version range
                    return {'valid': False, 'error': f"Unsupported GGUF version: {version}"}
            
            return {'valid': True, 'gguf_version': version}
            
        except Exception as e:
            return {'valid': False, 'error': f"Invalid GGUF file: {e}"}
    
    def _is_huggingface_model(self, path: Path) -> bool:
        """Check if path points to a HuggingFace model directory."""
        if path.is_dir():
            # Check for common HF model files
            hf_files = ['config.json', 'pytorch_model.bin', 'model.safetensors', 'tokenizer.json', 'tokenizer_config.json']
            return any((path / f).exists() for f in hf_files)
        return False
    
    def _load_model_by_format(self, model_path: str, format_type: str, architecture: str, 
                             load_config: Dict[str, Any], model_class) -> Any:
        """Load model using format-specific method."""
        if format_type == self.FORMAT_SAFETENSORS:
            return self._load_safetensors_model(model_path, architecture, load_config, model_class)
        elif format_type == self.FORMAT_PYTORCH:
            return self._load_pytorch_model(model_path, architecture, load_config, model_class)
        elif format_type in [self.FORMAT_HUGGINGFACE]:
            return self._load_huggingface_model(model_path, load_config, model_class)
        else:
            # Fallback to conversion-based loading for GGUF and others
            return self._load_model_with_retry(model_path, architecture, load_config, model_class)
    
    def _load_safetensors_model(self, model_path: str, architecture: str, 
                              load_config: Dict[str, Any], model_class) -> Any:
        """Load a safetensors model file."""
        if not SAFETENSORS_AVAILABLE:
            raise ImportError("safetensors library not available. Install with: pip install safetensors")
        
        try:
            path = Path(model_path)
            
            if path.is_dir():
                # Directory with safetensors files - use standard HF loading
                return model_class.from_pretrained(model_path, **load_config)
            else:
                # Single safetensors file - need to create temporary HF structure
                return self._load_single_safetensors_file(model_path, architecture, load_config, model_class)
                
        except Exception as e:
            self.logger.error(f"Failed to load safetensors model: {e}")
            raise
    
    def _load_single_safetensors_file(self, model_path: str, architecture: str, 
                                    load_config: Dict[str, Any], model_class) -> Any:
        """Load a single safetensors file by creating temporary HF structure."""
        import tempfile
        import shutil
        
        # Create temporary directory
        temp_dir = tempfile.mkdtemp(prefix="safetensors_model_")
        
        try:
            # Copy safetensors file to temp directory
            temp_model_path = os.path.join(temp_dir, "model.safetensors")
            shutil.copy2(model_path, temp_model_path)
            
            # Create minimal config.json
            config = self._create_model_config(architecture, model_path)
            config_path = os.path.join(temp_dir, "config.json")
            with open(config_path, 'w') as f:
                json.dump(config, f, indent=2)
            
            # Load model from temporary directory
            model = model_class.from_pretrained(temp_dir, **load_config)
            
            return model
            
        finally:
            # Clean up temporary directory
            try:
                shutil.rmtree(temp_dir)
            except Exception as e:
                self.logger.warning(f"Failed to clean up temporary directory: {e}")
    
    def _load_pytorch_model(self, model_path: str, architecture: str, 
                           load_config: Dict[str, Any], model_class) -> Any:
        """Load a PyTorch model file."""
        try:
            path = Path(model_path)
            
            if path.is_dir():
                # Directory with PyTorch files - use standard HF loading
                return model_class.from_pretrained(model_path, **load_config)
            else:
                # Single PyTorch file - need to create temporary HF structure
                return self._load_single_pytorch_file(model_path, architecture, load_config, model_class)
                
        except Exception as e:
            self.logger.error(f"Failed to load PyTorch model: {e}")
            raise
    
    def _load_single_pytorch_file(self, model_path: str, architecture: str, 
                                 load_config: Dict[str, Any], model_class) -> Any:
        """Load a single PyTorch file by creating temporary HF structure."""
        import tempfile
        import shutil
        
        # Create temporary directory
        temp_dir = tempfile.mkdtemp(prefix="pytorch_model_")
        
        try:
            # Copy PyTorch file to temp directory
            temp_model_path = os.path.join(temp_dir, "pytorch_model.bin")
            shutil.copy2(model_path, temp_model_path)
            
            # Create minimal config.json
            config = self._create_model_config(architecture, model_path)
            config_path = os.path.join(temp_dir, "config.json")
            with open(config_path, 'w') as f:
                json.dump(config, f, indent=2)
            
            # Load model from temporary directory
            model = model_class.from_pretrained(temp_dir, **load_config)
            
            return model
            
        finally:
            # Clean up temporary directory
            try:
                shutil.rmtree(temp_dir)
            except Exception as e:
                self.logger.warning(f"Failed to clean up temporary directory: {e}")
    
    def _load_huggingface_model(self, model_path: str, load_config: Dict[str, Any], model_class) -> Any:
        """Load a HuggingFace model directory."""
        return model_class.from_pretrained(model_path, **load_config)
    
    def _create_model_config(self, architecture: str, model_path: str) -> Dict[str, Any]:
        """Create a minimal model configuration for single files."""
        # Extract model info from file if possible
        model_info = self._extract_model_info_from_file(model_path)
        
        config = {
            "architectures": [architecture],
            "model_type": self._get_model_type_from_architecture(architecture),
            "torch_dtype": "float16",
            "transformers_version": "4.0.0",
            "vocab_size": model_info.get('vocab_size', 32000),
            "hidden_size": model_info.get('hidden_size', 4096),
            "intermediate_size": model_info.get('intermediate_size', 11008),
            "num_hidden_layers": model_info.get('num_hidden_layers', 32),
            "num_attention_heads": model_info.get('num_attention_heads', 32),
            "max_position_embeddings": model_info.get('max_position_embeddings', 4096),
            "rms_norm_eps": 1e-6,
            "use_cache": True,
            "pad_token_id": 0,
            "bos_token_id": 1,
            "eos_token_id": 2,
        }
        
        return config
    
    def _extract_model_info_from_file(self, model_path: str) -> Dict[str, Any]:
        """Extract model information from file content."""
        try:
            path = Path(model_path)
            
            if path.suffix == '.safetensors' and SAFETENSORS_AVAILABLE:
                return self._extract_safetensors_info(model_path)
            elif path.suffix in ['.bin', '.pt', '.pth']:
                return self._extract_pytorch_info(model_path)
            
        except Exception as e:
            self.logger.debug(f"Failed to extract model info from file: {e}")
        
        return {}
    
    def _extract_safetensors_info(self, model_path: str) -> Dict[str, Any]:
        """Extract model information from safetensors file."""
        try:
            import safetensors
            
            with open(model_path, 'rb') as f:
                # Read header
                header_size = int.from_bytes(f.read(8), 'little')
                header_bytes = f.read(header_size)
                header = json.loads(header_bytes.decode('utf-8'))
            
            # Extract dimensions from tensor shapes
            info = {}
            
            # Look for common tensor patterns
            for tensor_name, tensor_info in header.items():
                if tensor_name == "__metadata__":
                    continue
                    
                shape = tensor_info.get('shape', [])
                
                if 'embed_tokens.weight' in tensor_name and len(shape) >= 2:
                    info['vocab_size'] = shape[0]
                    info['hidden_size'] = shape[1]
                elif 'lm_head.weight' in tensor_name and len(shape) >= 2:
                    info['vocab_size'] = shape[0]
                elif any(layer_pattern in tensor_name for layer_pattern in ['layers.', 'h.', 'transformer.h.']):
                    # Extract layer number to determine total layers
                    import re
                    layer_match = re.search(r'layers?\.(\d+)', tensor_name)
                    if layer_match:
                        layer_num = int(layer_match.group(1))
                        info['num_hidden_layers'] = max(info.get('num_hidden_layers', 0), layer_num + 1)
            
            return info
            
        except Exception as e:
            self.logger.debug(f"Failed to extract safetensors info: {e}")
            return {}
    
    def _extract_pytorch_info(self, model_path: str) -> Dict[str, Any]:
        """Extract model information from PyTorch file."""
        try:
            import torch
            
            # Load state dict
            state_dict = torch.load(model_path, map_location='cpu', weights_only=True)
            
            info = {}
            
            # Extract dimensions from tensor shapes
            for tensor_name, tensor in state_dict.items():
                shape = tensor.shape
                
                if 'embed_tokens.weight' in tensor_name and len(shape) >= 2:
                    info['vocab_size'] = shape[0]
                    info['hidden_size'] = shape[1]
                elif 'lm_head.weight' in tensor_name and len(shape) >= 2:
                    info['vocab_size'] = shape[0]
                elif any(layer_pattern in tensor_name for layer_pattern in ['layers.', 'h.', 'transformer.h.']):
                    # Extract layer number
                    import re
                    layer_match = re.search(r'layers?\.(\d+)', tensor_name)
                    if layer_match:
                        layer_num = int(layer_match.group(1))
                        info['num_hidden_layers'] = max(info.get('num_hidden_layers', 0), layer_num + 1)
            
            return info
            
        except Exception as e:
            self.logger.debug(f"Failed to extract PyTorch info: {e}")
            return {}
    
    def _get_model_type_from_architecture(self, architecture: str) -> str:
        """Get model type from architecture class name."""
        arch_to_type = {
            'LlamaForCausalLM': 'llama',
            'CodeLlamaForCausalLM': 'codellama',
            'MistralForCausalLM': 'mistral',
            'MixtralForCausalLM': 'mixtral',
            'FalconForCausalLM': 'falcon',
            'MPTForCausalLM': 'mpt',
            'GPT2LMHeadModel': 'gpt2',
            'GPTJForCausalLM': 'gptj',
            'GPTNeoXForCausalLM': 'gptneox',
            'BloomForCausalLM': 'bloom',
            'OPTForCausalLM': 'opt'
        }
        return arch_to_type.get(architecture, 'llama')
    
    def _load_tokenizer_for_format(self, model_path: str, format_type: str, model_type: str):
        """Load tokenizer based on model format."""
        try:
            from transformers import AutoTokenizer
            
            if format_type in [self.FORMAT_HUGGINGFACE, self.FORMAT_SAFETENSORS, self.FORMAT_PYTORCH]:
                path = Path(model_path)
                
                if path.is_dir():
                    # Try to load tokenizer from directory
                    try:
                        tokenizer = AutoTokenizer.from_pretrained(model_path)
                        if tokenizer.pad_token is None:
                            tokenizer.pad_token = tokenizer.eos_token
                        return tokenizer
                    except Exception as e:
                        self.logger.warning(f"Failed to load tokenizer from directory: {e}")
                
                # Fallback to compatible tokenizer
                return self._load_compatible_tokenizer(model_type)
            else:
                # For other formats, use compatible tokenizer
                return self._load_compatible_tokenizer(model_type)
                
        except Exception as e:
            self.logger.warning(f"Failed to load tokenizer: {e}")
            # Final fallback
            from transformers import AutoTokenizer
            return AutoTokenizer.from_pretrained("gpt2")
    
    def _load_compatible_tokenizer(self, model_type: str):
        """Load a compatible tokenizer for the model type."""
        from transformers import AutoTokenizer
        
        tokenizer_name = self._get_compatible_tokenizer(model_type)
        tokenizer = AutoTokenizer.from_pretrained(tokenizer_name)
        
        if tokenizer.pad_token is None:
            tokenizer.pad_token = tokenizer.eos_token
            
        return tokenizer
    
    def _detect_model_type(self, model_path: str) -> str:
        """Detect model type from file name or directory."""
        model_path_lower = model_path.lower()
        model_name = Path(model_path).name.lower()
        
        # Detection patterns (order matters)
        detection_patterns = [
            (['codellama', 'code-llama'], 'codellama'),
            (['mixtral'], 'mixtral'),
            (['mistral'], 'mistral'),
            (['llama-2', 'llama2'], 'llama2'),
            (['llama'], 'llama'),
            (['falcon'], 'falcon'),
            (['mpt'], 'mpt'),
            (['gpt-2', 'gpt2'], 'gpt2'),
            (['gpt-j', 'gptj'], 'gptj'),
            (['gpt-neox', 'gptneox'], 'gptneox'),
            (['bloom'], 'bloom'),
            (['opt'], 'opt'),
        ]
        
        for patterns, model_type in detection_patterns:
            for pattern in patterns:
                if pattern in model_name or pattern in model_path_lower:
                    self.logger.info(f"Detected model type '{model_type}' from pattern '{pattern}'")
                    return model_type
        
        # Default fallback
        self.logger.warning(f"Could not detect model type from '{model_name}', defaulting to 'llama'")
        return 'llama'
    
    def _get_model_architecture(self, model_type: str) -> str:
        """Get the transformers architecture class name for the model type."""
        return self.SUPPORTED_ARCHITECTURES.get(model_type, 'LlamaForCausalLM')    
  
    def _get_or_convert_model(self, model_path: str, model_type: str, validation_result: Dict[str, Any]) -> str:
        """
        Get converted model path or convert GGUF to HuggingFace format if needed.
        
        Args:
            model_path: Original model path
            model_type: Detected model type
            validation_result: Validation results
            
        Returns:
            Path to HuggingFace compatible model
        """
        # If it's already a HuggingFace model, use it directly
        if validation_result.get('is_hf_model'):
            self.logger.info("Model is already in HuggingFace format")
            return model_path
        
        # Check cache for converted model
        cache_key = self._generate_cache_key(model_path, model_type)
        cached_model_path = os.path.join(self._model_cache_dir, cache_key)
        
        if os.path.exists(cached_model_path) and self._validate_cached_model(cached_model_path):
            self.logger.info(f"Using cached converted model: {cached_model_path}")
            return cached_model_path
        
        # Convert GGUF to HuggingFace format
        self.logger.info("Converting GGUF model to HuggingFace format...")
        converted_path = self._convert_gguf_to_hf(model_path, model_type, cached_model_path)
        
        return converted_path
    
    def _generate_cache_key(self, model_path: str, model_type: str) -> str:
        """Generate a cache key for the model."""
        # Create hash from model path, size, and modification time
        path = Path(model_path)
        stat = path.stat()
        
        key_data = f"{path.name}_{stat.st_size}_{stat.st_mtime}_{model_type}"
        cache_key = hashlib.md5(key_data.encode()).hexdigest()
        
        return f"{model_type}_{cache_key}"
    
    def _validate_cached_model(self, cached_path: str) -> bool:
        """Validate that cached model is complete and valid."""
        try:
            path = Path(cached_path)
            if not path.exists() or not path.is_dir():
                return False
            
            # Check for essential HuggingFace files
            required_files = ['config.json']
            model_files = ['pytorch_model.bin', 'model.safetensors']
            
            # At least config.json must exist
            if not (path / 'config.json').exists():
                return False
            
            # At least one model file must exist
            if not any((path / f).exists() for f in model_files):
                return False
            
            return True
            
        except Exception as e:
            self.logger.debug(f"Error validating cached model: {e}")
            return False
    
    def _convert_gguf_to_hf(self, model_path: str, model_type: str, output_path: str) -> str:
        """
        Convert GGUF model to HuggingFace format.
        
        This is a simplified conversion process. In a full implementation,
        you would use tools like llama.cpp's convert scripts or similar.
        """
        try:
            # For now, we'll attempt to load the GGUF model directly with transformers
            # In practice, you might need conversion tools or libraries
            
            # Create output directory
            os.makedirs(output_path, exist_ok=True)
            
            # Try to use ctransformers to load and then save in HF format
            # This is a fallback approach
            converted_path = self._attempt_direct_conversion(model_path, model_type, output_path)
            
            if converted_path:
                return converted_path
            
            # If direct conversion fails, try alternative approaches
            return self._attempt_alternative_conversion(model_path, model_type, output_path)
            
        except Exception as e:
            self.logger.error(f"Model conversion failed: {e}")
            # Fallback: try to use the original model path
            # Some transformers versions can handle GGUF directly
            return model_path
    
    def _attempt_direct_conversion(self, model_path: str, model_type: str, output_path: str) -> Optional[str]:
        """Attempt direct conversion using available tools."""
        try:
            # This is a placeholder for actual conversion logic
            # In practice, you would use conversion tools or libraries
            
            # For demonstration, create a minimal config
            config = {
                "architectures": [self._get_model_architecture(model_type)],
                "model_type": model_type,
                "torch_dtype": "float16",
                "transformers_version": "4.0.0"
            }
            
            config_path = os.path.join(output_path, 'config.json')
            with open(config_path, 'w') as f:
                json.dump(config, f, indent=2)
            
            # Create a placeholder tokenizer config
            tokenizer_config = {
                "tokenizer_class": "LlamaTokenizer" if "llama" in model_type else "AutoTokenizer",
                "model_max_length": 4096
            }
            
            tokenizer_config_path = os.path.join(output_path, 'tokenizer_config.json')
            with open(tokenizer_config_path, 'w') as f:
                json.dump(tokenizer_config, f, indent=2)
            
            self.logger.info(f"Created basic HF structure at {output_path}")
            return output_path
            
        except Exception as e:
            self.logger.debug(f"Direct conversion failed: {e}")
            return None
    
    def _attempt_alternative_conversion(self, model_path: str, model_type: str, output_path: str) -> str:
        """Attempt alternative conversion approaches."""
        # For now, return the original path and let transformers handle it
        # Some newer versions of transformers can load GGUF files directly
        self.logger.warning("Using original GGUF file directly - conversion not implemented")
        return model_path    

    def _setup_device_configuration(self, **kwargs) -> Dict[str, Any]:
        """Setup device configuration for model loading."""
        import torch
        
        device_config = {}
        
        # Determine target device
        if not self.config.gpu_enabled:
            device_config['device'] = 'cpu'
        else:
            if torch.cuda.is_available():
                device_config['device'] = 'cuda'
                device_config['device_count'] = torch.cuda.device_count()
            elif hasattr(torch.backends, 'mps') and torch.backends.mps.is_available():
                device_config['device'] = 'mps'
            elif hasattr(torch, 'hip') and torch.hip.is_available():
                device_config['device'] = 'cuda'  # ROCm uses cuda interface
            else:
                device_config['device'] = 'cpu'
        
        # Setup device map for multi-GPU
        if device_config['device'] == 'cuda' and device_config.get('device_count', 1) > 1:
            device_config['device_map'] = 'auto'
        
        # Override with explicit device if specified
        if 'device' in kwargs:
            device_config['device'] = kwargs['device']
        
        if 'device_map' in kwargs:
            device_config['device_map'] = kwargs['device_map']
        
        return device_config
    
    def _setup_quantization_configuration(self, model_path: str, **kwargs) -> Optional[Dict[str, Any]]:
        """Setup quantization configuration."""
        # Check if quantization is requested
        quantization_type = kwargs.get('quantization')
        if not quantization_type:
            # Try to detect from filename
            quantization_type = self._detect_quantization_from_filename(model_path)
        
        if not quantization_type:
            return None
        
        # Setup quantization config based on type
        if quantization_type in self.QUANTIZATION_FORMATS:
            quant_info = self.QUANTIZATION_FORMATS[quantization_type]
            
            try:
                import torch
                from transformers import BitsAndBytesConfig
                
                if quant_info['bits'] == 4:
                    return BitsAndBytesConfig(
                        load_in_4bit=True,
                        bnb_4bit_compute_dtype=torch.float16,
                        bnb_4bit_use_double_quant=True,
                        bnb_4bit_quant_type="nf4"
                    )
                elif quant_info['bits'] == 8:
                    return BitsAndBytesConfig(
                        load_in_8bit=True
                    )
            except ImportError:
                self.logger.warning("BitsAndBytesConfig not available, skipping quantization")
        
        return None
    
    def _detect_quantization_from_filename(self, model_path: str) -> Optional[str]:
        """Detect quantization format from filename."""
        filename = Path(model_path).name.lower()
        
        for quant_format in self.QUANTIZATION_FORMATS.keys():
            if quant_format in filename:
                return quant_format
        
        return None
    
    def _load_tokenizer(self, model_path: str, model_type: str):
        """Load tokenizer for the model."""
        try:
            from transformers import AutoTokenizer
            
            # Try to load tokenizer from converted model path
            if os.path.isdir(model_path):
                tokenizer = AutoTokenizer.from_pretrained(model_path)
            else:
                # Fallback to a compatible tokenizer
                tokenizer_name = self._get_compatible_tokenizer(model_type)
                tokenizer = AutoTokenizer.from_pretrained(tokenizer_name)
            
            # Ensure pad token is set
            if tokenizer.pad_token is None:
                tokenizer.pad_token = tokenizer.eos_token
            
            return tokenizer
            
        except Exception as e:
            self.logger.warning(f"Failed to load tokenizer: {e}")
            # Return a basic tokenizer as fallback
            from transformers import AutoTokenizer
            return AutoTokenizer.from_pretrained("gpt2")
    
    def _get_compatible_tokenizer(self, model_type: str) -> str:
        """Get a compatible tokenizer name for the model type."""
        tokenizer_map = {
            'llama': 'huggyllama/llama-7b',
            'llama2': 'meta-llama/Llama-2-7b-hf',
            'codellama': 'codellama/CodeLlama-7b-hf',
            'mistral': 'mistralai/Mistral-7B-v0.1',
            'mixtral': 'mistralai/Mixtral-8x7B-v0.1',
            'falcon': 'tiiuae/falcon-7b',
            'mpt': 'mosaicml/mpt-7b',
            'gpt2': 'gpt2',
            'gptj': 'EleutherAI/gpt-j-6B',
            'gptneox': 'EleutherAI/gpt-neox-20b',
            'bloom': 'bigscience/bloom-560m',
            'opt': 'facebook/opt-125m'
        }
        
        return tokenizer_map.get(model_type, 'gpt2') 
   
    def _prepare_model_load_config(self, model_path: str, model_type: str, 
                                  device_config: Dict[str, Any], 
                                  quantization_config: Optional[Dict[str, Any]], 
                                  **kwargs) -> Dict[str, Any]:
        """Prepare configuration for model loading."""
        import torch
        
        config = {}
        
        # Device configuration
        if device_config.get('device_map'):
            config['device_map'] = device_config['device_map']
        else:
            config['device_map'] = device_config['device']
        
        # Quantization configuration
        if quantization_config:
            config['quantization_config'] = quantization_config
        
        # Torch dtype
        if device_config['device'] != 'cpu':
            config['torch_dtype'] = torch.float16
        else:
            config['torch_dtype'] = torch.float32
        
        # Low CPU memory usage
        config['low_cpu_mem_usage'] = True
        
        # Trust remote code (for some models)
        config['trust_remote_code'] = kwargs.get('trust_remote_code', True)
        
        # Custom arguments
        if self.config.custom_args:
            config.update(self.config.custom_args)
        
        # Override with explicit kwargs
        for key, value in kwargs.items():
            if key not in ['model_type', 'device', 'quantization']:
                config[key] = value
        
        return config
    
    def _load_model_with_retry(self, model_path: str, architecture: str, 
                              load_config: Dict[str, Any], model_class) -> Any:
        """Load model with retry logic for fallback scenarios."""
        original_config = load_config.copy()
        
        try:
            # First attempt with original configuration
            self.logger.debug(f"Loading model with config: {load_config}")
            model = model_class.from_pretrained(model_path, **load_config)
            return model
            
        except Exception as e:
            self.logger.warning(f"First load attempt failed: {e}")
            
            # Retry with reduced configuration
            fallback_configs = [
                # Remove quantization if present
                {k: v for k, v in original_config.items() if k != 'quantization_config'},
                
                # Use CPU device
                {**{k: v for k, v in original_config.items() if k != 'quantization_config'}, 
                 'device_map': 'cpu', 'torch_dtype': 'float32'},
                
                # Minimal configuration
                {'device_map': 'cpu', 'torch_dtype': 'float32', 'low_cpu_mem_usage': True}
            ]
            
            for i, fallback_config in enumerate(fallback_configs):
                try:
                    self.logger.info(f"Retry {i+1}: Loading with fallback config")
                    model = model_class.from_pretrained(model_path, **fallback_config)
                    self.logger.info(f"Model loaded successfully with fallback config {i+1}")
                    return model
                except Exception as retry_error:
                    self.logger.warning(f"Fallback {i+1} failed: {retry_error}")
                    continue
            
            # If all retries failed, raise the original error
            raise e
    
    def _setup_accelerate(self, device_config: Dict[str, Any]):
        """Setup accelerate for GPU acceleration."""
        try:
            from accelerate import Accelerator
            
            # Create accelerator with appropriate configuration
            accelerator_kwargs = {}
            
            if device_config['device'] == 'cuda':
                accelerator_kwargs['device_placement'] = True
                accelerator_kwargs['split_batches'] = True
            
            accelerator = Accelerator(**accelerator_kwargs)
            
            # Prepare model with accelerator if needed
            if hasattr(self.model, 'to') and device_config['device'] != 'cpu':
                self.model = accelerator.prepare(self.model)
            
            self.logger.info(f"Accelerate setup completed for device: {device_config['device']}")
            
        except Exception as e:
            self.logger.warning(f"Failed to setup accelerate: {e}")
    
    def _get_model_metadata(self, model_path: str, validation_result: Dict[str, Any], 
                           architecture: str) -> Dict[str, Any]:
        """Extract model metadata."""
        metadata = {
            'architecture': architecture,
            'file_size_mb': validation_result.get('file_size_mb', 0),
            'format_type': validation_result.get('format_type', 'Unknown')
        }
        
        # Add model-specific metadata if available
        if hasattr(self.model, 'config'):
            config = self.model.config
            metadata.update({
                'vocab_size': getattr(config, 'vocab_size', None),
                'hidden_size': getattr(config, 'hidden_size', None),
                'num_layers': getattr(config, 'num_hidden_layers', None),
                'num_attention_heads': getattr(config, 'num_attention_heads', None),
                'max_position_embeddings': getattr(config, 'max_position_embeddings', None)
            })
        
        return metadata
    
    def _estimate_memory_usage(self, model_info: Dict[str, Any], 
                              device_config: Dict[str, Any], 
                              quantization_config: Optional[Dict[str, Any]]) -> int:
        """Estimate memory usage in MB."""
        base_size_mb = model_info.get('file_size_mb', 0)
        
        # Apply quantization factor
        if quantization_config:
            if hasattr(quantization_config, 'load_in_4bit') and quantization_config.load_in_4bit:
                base_size_mb *= 0.25  # 4-bit quantization
            elif hasattr(quantization_config, 'load_in_8bit') and quantization_config.load_in_8bit:
                base_size_mb *= 0.5   # 8-bit quantization
        
        # Apply transformers overhead (typically 30% more than file size)
        base_size_mb *= 1.3
        
        # Apply device-specific overhead
        if device_config['device'] != 'cpu':
            base_size_mb *= 1.2  # GPU overhead
        
        return int(base_size_mb)
    
    def _determine_hardware_used(self, device_config: Dict[str, Any]) -> str:
        """Determine hardware description from device config."""
        device = device_config['device']
        
        if device == 'cuda':
            try:
                import torch
                if torch.cuda.is_available():
                    device_count = torch.cuda.device_count()
                    if device_count > 1:
                        return f"cuda ({device_count} GPUs)"
                    else:
                        gpu_name = torch.cuda.get_device_name(0)
                        return f"cuda ({gpu_name})"
            except:
                pass
            return 'cuda'
        
        return device
    
    def _format_loading_error(self, error: Exception, model_path: str) -> str:
        """Format loading error message for user display."""
        error_str = str(error).lower()
        model_name = Path(model_path).name
        
        if 'cuda out of memory' in error_str or 'out of memory' in error_str:
            return f"GPU out of memory while loading {model_name}. Try reducing GPU layers or using CPU mode."
        
        elif 'no module named' in error_str or 'import' in error_str:
            return f"Missing required dependencies for transformers backend. Please install: pip install transformers accelerate torch"
        
        elif 'model not found' in error_str or 'tokenizer' in error_str:
            return f"Model or tokenizer not found for {model_name}. The model may need conversion or may not be supported."
        
        elif 'conversion' in error_str:
            return f"Model conversion failed for {model_name}. The GGUF model may not be compatible with transformers backend."
        
        elif 'device' in error_str:
            return f"Device configuration error while loading {model_name}. Check GPU availability and drivers."
        
        else:
            return f"Failed to load model {model_name}: {error}"

    def generate_text(self, prompt: str, config: GenerationConfig) -> str:
        """
        Generate text from the given prompt using the loaded model.
        
        Args:
            prompt: Input text prompt
            config: Generation configuration
            
        Returns:
            Generated text
            
        Raises:
            ModelLoadingError: If no model is loaded
            BackendError: If generation fails
        """
        if not self.is_loaded or self.model is None or self.tokenizer is None:
            raise ModelLoadingError("No model is loaded. Please load a model first.")
        
        try:
            start_time = time.time()
            
            # Prepare generation configuration
            generation_config = self._prepare_generation_config(config)
            
            # Tokenize input
            inputs = self.tokenizer(prompt, return_tensors="pt")
            
            # Move to appropriate device
            if self._device != 'cpu':
                inputs = {k: v.to(self._device) for k, v in inputs.items()}
            
            # Generate text
            with torch.no_grad():
                outputs = self.model.generate(
                    inputs['input_ids'],
                    attention_mask=inputs.get('attention_mask'),
                    **generation_config
                )
            
            # Decode output
            generated_text = self.tokenizer.decode(
                outputs[0][inputs['input_ids'].shape[1]:], 
                skip_special_tokens=True
            )
            
            # Update generation statistics
            generation_time = time.time() - start_time
            token_count = len(outputs[0]) - inputs['input_ids'].shape[1]
            
            self._update_generation_stats(token_count, generation_time)
            
            return generated_text
            
        except Exception as e:
            error_msg = f"Text generation failed: {e}"
            self.logger.error(error_msg)
            raise BackendError(error_msg)
    
    def _prepare_generation_config(self, config: GenerationConfig) -> Dict[str, Any]:
        """Prepare generation configuration for transformers."""
        import torch
        
        # Set random seed if specified
        if config.seed >= 0:
            torch.manual_seed(config.seed)
            if torch.cuda.is_available():
                torch.cuda.manual_seed(config.seed)
        
        # Build generation config
        generation_config = {
            'max_new_tokens': config.max_tokens,
            'temperature': config.temperature,
            'top_p': config.top_p,
            'top_k': config.top_k,
            'repetition_penalty': config.repeat_penalty,
            'do_sample': config.temperature > 0.0,
            'pad_token_id': self.tokenizer.eos_token_id,
            'eos_token_id': self.tokenizer.eos_token_id,
        }
        
        # Add stop sequences if specified
        if config.stop_sequences:
            # Convert stop sequences to token IDs
            stop_token_ids = []
            for stop_seq in config.stop_sequences:
                tokens = self.tokenizer.encode(stop_seq, add_special_tokens=False)
                stop_token_ids.extend(tokens)
            
            if stop_token_ids:
                generation_config['eos_token_id'] = stop_token_ids
        
        return generation_config
    
    def _update_generation_stats(self, token_count: int, generation_time: float):
        """Update generation statistics."""
        self._generation_stats['total_tokens'] += token_count
        self._generation_stats['total_time'] += generation_time
        
        if self._generation_stats['total_time'] > 0:
            self._generation_stats['average_tokens_per_second'] = (
                self._generation_stats['total_tokens'] / self._generation_stats['total_time']
            )

    def unload_model(self) -> bool:
        """
        Unload the current model and free memory.
        
        Returns:
            True if successful, False otherwise
        """
        try:
            if self.model is not None:
                # Move model to CPU and delete
                if hasattr(self.model, 'cpu'):
                    self.model.cpu()
                del self.model
                self.model = None
            
            if self.tokenizer is not None:
                del self.tokenizer
                self.tokenizer = None
            
            # Clear device references
            self._device = None
            self._device_map = None
            self._quantization_config = None
            self._converted_model_path = None
            self._model_type = None
            
            # Reset state
            self.is_loaded = False
            self.model_path = None
            self.load_time = 0.0
            self.memory_usage = 0
            
            # Force garbage collection
            gc.collect()
            
            # Clear GPU cache if available
            try:
                import torch
                if torch.cuda.is_available():
                    torch.cuda.empty_cache()
            except:
                pass
            
            self.logger.info("Model unloaded successfully")
            return True
            
        except Exception as e:
            self.logger.error(f"Error unloading model: {e}")
            return False

    def get_hardware_info(self) -> HardwareInfo:
        """
        Get information about hardware acceleration capabilities.
        
        Returns:
            HardwareInfo object with current hardware status
        """
        try:
            import torch
            import psutil
            
            hardware_info = HardwareInfo()
            
            # Get CPU information
            hardware_info.cpu_cores = psutil.cpu_count(logical=False) or 0
            hardware_info.total_ram = int(psutil.virtual_memory().total / (1024 * 1024))  # MB
            
            # Get GPU information
            gpu_devices = []
            total_vram = 0
            supported_hardware = [HardwareType.CPU]
            
            # Check CUDA support
            if torch.cuda.is_available():
                hardware_info.gpu_count = torch.cuda.device_count()
                supported_hardware.append(HardwareType.CUDA)
                
                for i in range(hardware_info.gpu_count):
                    try:
                        props = torch.cuda.get_device_properties(i)
                        device_vram = props.total_memory // (1024 * 1024)  # MB
                        total_vram += device_vram
                        
                        gpu_devices.append({
                            'id': i,
                            'name': props.name,
                            'vram_mb': device_vram,
                            'compute_capability': f"{props.major}.{props.minor}",
                            'type': 'CUDA'
                        })
                    except Exception as e:
                        self.logger.debug(f"Error getting GPU {i} properties: {e}")
            
            # Check ROCm support (AMD)
            if hasattr(torch, 'hip') and torch.hip.is_available():
                supported_hardware.append(HardwareType.ROCM)
            
            # Check MPS support (Apple Silicon)
            if hasattr(torch.backends, 'mps') and torch.backends.mps.is_available():
                supported_hardware.append(HardwareType.MPS)
                # Add Apple Silicon GPU info
                gpu_devices.append({
                    'id': 0,
                    'name': 'Apple Silicon GPU',
                    'vram_mb': 0,  # Unified memory
                    'compute_capability': 'N/A',
                    'type': 'MPS'
                })
            
            hardware_info.gpu_devices = gpu_devices
            hardware_info.total_vram = total_vram
            hardware_info.supported_hardware = supported_hardware
            hardware_info.recommended_backend = 'transformers'
            
            return hardware_info
            
        except Exception as e:
            self.logger.error(f"Error getting hardware info: {e}")
            return HardwareInfo()
    
    def get_generation_stats(self) -> Dict[str, Any]:
        """Get generation performance statistics."""
        return self._generation_stats.copy()
    
    def clear_cache(self):
        """Clear the model conversion cache."""
        try:
            if os.path.exists(self._model_cache_dir):
                for item in os.listdir(self._model_cache_dir):
                    item_path = os.path.join(self._model_cache_dir, item)
                    if os.path.isdir(item_path):
                        shutil.rmtree(item_path)
                    else:
                        os.unlink(item_path)
                
                self.logger.info("Model cache cleared successfully")
        except Exception as e:
            self.logger.error(f"Error clearing cache: {e}")
    
    def get_cache_info(self) -> Dict[str, Any]:
        """Get information about the model cache."""
        try:
            cache_info = {
                'cache_dir': self._model_cache_dir,
                'cached_models': [],
                'total_size_mb': 0
            }
            
            if os.path.exists(self._model_cache_dir):
                for item in os.listdir(self._model_cache_dir):
                    item_path = os.path.join(self._model_cache_dir, item)
                    if os.path.isdir(item_path):
                        # Calculate directory size
                        size = sum(
                            f.stat().st_size 
                            for f in Path(item_path).rglob('*') 
                            if f.is_file()
                        )
                        size_mb = size / (1024 * 1024)
                        
                        cache_info['cached_models'].append({
                            'name': item,
                            'path': item_path,
                            'size_mb': round(size_mb, 2)
                        })
                        cache_info['total_size_mb'] += size_mb
            
            cache_info['total_size_mb'] = round(cache_info['total_size_mb'], 2)
            return cache_info
            
        except Exception as e:
            self.logger.error(f"Error getting cache info: {e}")
            return {
                'cache_dir': self._model_cache_dir,
                'cached_models': [],
                'total_size_mb': 0
            }
            
        except Exception as e:
            self.logger.warning(f"Initial model loading failed: {e}")
            
            # Retry with reduced precision
            if 'torch_dtype' in load_config:
                try:
                    import torch
                    load_config['torch_dtype'] = torch.float32
                    self.logger.debug("Retrying with float32 precision")
                    
                    if os.path.isdir(model_path):
                        return model_class.from_pretrained(model_path, **load_config)
                    else:
                        return self._load_gguf_with_transformers(model_path, architecture, load_config, model_class)
                        
                except Exception as e2:
                    self.logger.warning(f"Retry with float32 failed: {e2}")
            
            # Final fallback: CPU only
            try:
                load_config = original_config.copy()
                load_config['device_map'] = 'cpu'
                if 'quantization_config' in load_config:
                    del load_config['quantization_config']
                
                self.logger.debug("Final fallback: CPU only")
                
                if os.path.isdir(model_path):
                    return model_class.from_pretrained(model_path, **load_config)
                else:
                    return self._load_gguf_with_transformers(model_path, architecture, load_config, model_class)
                    
            except Exception as e3:
                self.logger.error(f"All loading attempts failed. Last error: {e3}")
                raise e  # Raise the original error
    
    def _load_gguf_with_transformers(self, model_path: str, architecture: str, 
                                    load_config: Dict[str, Any], model_class) -> Any:
        """
        Attempt to load GGUF file directly with transformers.
        
        This is a fallback method for when conversion is not available.
        """
        try:
            # Some newer versions of transformers can handle GGUF files directly
            # This is experimental and may not work for all models
            self.logger.warning("Attempting direct GGUF loading - this is experimental")
            
            # Try to load as if it were a regular model file
            # This will likely fail, but we try anyway
            return model_class.from_pretrained(model_path, **load_config)
            
        except Exception as e:
            # If direct loading fails, we need to inform the user about conversion
            raise ModelLoadingError(
                f"GGUF model conversion not implemented. "
                f"Please convert '{model_path}' to HuggingFace format manually or use a different backend. "
                f"Original error: {e}"
            ) 
   
    def _setup_accelerate(self, device_config: Dict[str, Any]):
        """Setup accelerate for distributed/GPU training."""
        try:
            from accelerate import Accelerator
            
            # Create accelerator with appropriate configuration
            accelerator = Accelerator(
                device_placement=True,
                split_batches=True
            )
            
            # Prepare model for accelerate
            if self.model and device_config['device'] != 'cpu':
                self.model = accelerator.prepare(self.model)
                self.logger.info("Model prepared with accelerate")
            
        except Exception as e:
            self.logger.warning(f"Failed to setup accelerate: {e}")
    
    def _get_model_metadata(self, model_path: str, validation_result: Dict[str, Any], 
                           architecture: str) -> Dict[str, Any]:
        """Extract model metadata."""
        metadata = {
            'architecture': architecture,
            'file_size_mb': validation_result.get('file_size_mb', 0),
            'format_type': validation_result.get('format_type', 'Unknown'),
            'model_path': model_path
        }
        
        # Add model-specific information if available
        if self.model and hasattr(self.model, 'config'):
            config = self.model.config
            metadata.update({
                'vocab_size': getattr(config, 'vocab_size', None),
                'hidden_size': getattr(config, 'hidden_size', None),
                'num_layers': getattr(config, 'num_hidden_layers', None),
                'num_attention_heads': getattr(config, 'num_attention_heads', None),
                'max_position_embeddings': getattr(config, 'max_position_embeddings', None)
            })
        
        return metadata
    
    def _estimate_memory_usage(self, model_info: Dict[str, Any], 
                              device_config: Dict[str, Any], 
                              quantization_config: Optional[Dict[str, Any]]) -> int:
        """Estimate memory usage in MB."""
        base_size_mb = model_info.get('file_size_mb', 0)
        
        if base_size_mb == 0:
            return 0
        
        # Apply quantization factor
        if quantization_config:
            if hasattr(quantization_config, 'load_in_4bit') and quantization_config.load_in_4bit:
                base_size_mb *= 0.25  # 4-bit quantization
            elif hasattr(quantization_config, 'load_in_8bit') and quantization_config.load_in_8bit:
                base_size_mb *= 0.5   # 8-bit quantization
        
        # Apply transformers overhead (typically 30% more than file size)
        base_size_mb *= 1.3
        
        # Apply device-specific overhead
        if device_config['device'] != 'cpu':
            base_size_mb *= 1.2  # GPU overhead
        
        return int(base_size_mb)
    
    def _determine_hardware_used(self, device_config: Dict[str, Any]) -> str:
        """Determine what hardware is being used."""
        device = device_config.get('device', 'cpu')
        
        if device == 'cuda':
            return 'cuda'
        elif device == 'mps':
            return 'mps'
        elif device == 'cpu':
            return 'cpu'
        else:
            return device
    
    def _format_loading_error(self, error: Exception, model_path: str) -> str:
        """Format loading error message for user display."""
        error_str = str(error).lower()
        
        if 'cuda out of memory' in error_str or 'out of memory' in error_str:
            return f"GPU out of memory while loading model. Try reducing model size or using CPU mode."
        elif 'no module named' in error_str:
            return f"Missing required dependencies. Please install transformers and accelerate libraries."
        elif 'model not found' in error_str or 'tokenizer' in error_str:
            return f"Model or tokenizer not found. Please check the model path: {model_path}"
        elif 'conversion' in error_str:
            return f"Model conversion failed. The GGUF model may need manual conversion to HuggingFace format."
        else:
            return f"Failed to load model '{Path(model_path).name}': {error}"

    def generate_text(self, prompt: str, config: GenerationConfig) -> str:
        """
        Generate text from the given prompt using the loaded model.
        
        Args:
            prompt: Input text prompt
            config: Generation configuration
            
        Returns:
            Generated text
            
        Raises:
            ModelLoadingError: If no model is loaded
            BackendError: If generation fails
        """
        if not self.is_loaded or self.model is None or self.tokenizer is None:
            raise ModelLoadingError("No model is loaded. Please load a model first.")
        
        try:
            import torch
            start_time = time.time()
            
            # Prepare generation configuration
            generation_config = self._prepare_generation_config(config)
            
            # Tokenize input
            inputs = self.tokenizer(prompt, return_tensors="pt")
            
            # Move inputs to the same device as model
            if hasattr(self.model, 'device'):
                inputs = {k: v.to(self.model.device) for k, v in inputs.items()}
            elif self._device and self._device != 'cpu':
                import torch
                device = torch.device(self._device)
                inputs = {k: v.to(device) for k, v in inputs.items()}
            
            # Generate text
            with torch.no_grad():
                if config.stream:
                    # Streaming generation
                    generated_text = self._generate_streaming(inputs, generation_config, prompt)
                else:
                    # Standard generation
                    outputs = self.model.generate(**inputs, **generation_config)
                    
                    # Decode generated text
                    generated_tokens = outputs[0][inputs['input_ids'].shape[1]:]
                    generated_text = self.tokenizer.decode(generated_tokens, skip_special_tokens=True)
            
            # Update generation statistics
            generation_time = time.time() - start_time
            token_count = len(generated_text.split())  # Rough token count
            
            self._generation_stats['total_tokens'] += token_count
            self._generation_stats['total_time'] += generation_time
            if self._generation_stats['total_time'] > 0:
                self._generation_stats['average_tokens_per_second'] = (
                    self._generation_stats['total_tokens'] / self._generation_stats['total_time']
                )
            
            self.logger.debug(f"Generated {token_count} tokens in {generation_time:.2f}s")
            
            return generated_text
            
        except Exception as e:
            error_msg = f"Text generation failed: {e}"
            self.logger.error(error_msg)
            raise BackendError(error_msg)
    
    def _prepare_generation_config(self, config: GenerationConfig) -> Dict[str, Any]:
        """Prepare generation configuration for transformers."""
        import torch
        
        generation_config = {
            'max_new_tokens': config.max_tokens,
            'temperature': config.temperature,
            'top_p': config.top_p,
            'top_k': config.top_k,
            'repetition_penalty': config.repeat_penalty,
            'do_sample': config.temperature > 0.0,
            'pad_token_id': self.tokenizer.eos_token_id,
            'eos_token_id': self.tokenizer.eos_token_id,
        }
        
        # Add stop sequences if provided
        if config.stop_sequences:
            # Convert stop sequences to token IDs
            stop_token_ids = []
            for stop_seq in config.stop_sequences:
                tokens = self.tokenizer.encode(stop_seq, add_special_tokens=False)
                if tokens:
                    stop_token_ids.extend(tokens)
            
            if stop_token_ids:
                generation_config['eos_token_id'] = stop_token_ids
        
        # Set seed if specified
        if config.seed >= 0:
            torch.manual_seed(config.seed)
            if torch.cuda.is_available():
                torch.cuda.manual_seed(config.seed)
        
        return generation_config
    
    def _generate_streaming(self, inputs: Dict[str, Any], generation_config: Dict[str, Any], 
                           original_prompt: str) -> str:
        """Generate text with streaming (simplified implementation)."""
        # For now, implement as non-streaming since streaming requires more complex setup
        # In a full implementation, you would use TextIteratorStreamer or similar
        self.logger.warning("Streaming generation not fully implemented, falling back to standard generation")
        
        outputs = self.model.generate(**inputs, **generation_config)
        generated_tokens = outputs[0][inputs['input_ids'].shape[1]:]
        return self.tokenizer.decode(generated_tokens, skip_special_tokens=True)
    
    def unload_model(self) -> bool:
        """
        Unload the current model and free memory.
        
        Returns:
            True if successful, False otherwise
        """
        try:
            if self.model is not None:
                # Move model to CPU and delete
                if hasattr(self.model, 'cpu'):
                    self.model.cpu()
                del self.model
                self.model = None
            
            if self.tokenizer is not None:
                del self.tokenizer
                self.tokenizer = None
            
            # Clear other model-related attributes
            self.model_path = None
            self._converted_model_path = None
            self._model_type = None
            self._format_type = None
            self._device = None
            self._device_map = None
            self._quantization_config = None
            self.is_loaded = False
            self.load_time = 0.0
            self.memory_usage = 0
            
            # Force garbage collection
            gc.collect()
            
            # Clear GPU cache if available
            try:
                import torch
                if torch.cuda.is_available():
                    torch.cuda.empty_cache()
            except Exception as e:
                self.logger.debug(f"Failed to clear GPU cache: {e}")
            
            self.logger.info("Model unloaded successfully")
            return True
            
        except Exception as e:
            self.logger.error(f"Error unloading model: {e}")
            return False
    
    def get_hardware_info(self) -> HardwareInfo:
        """
        Get information about hardware acceleration capabilities.
        
        Returns:
            HardwareInfo object with current hardware status
        """
        try:
            import torch
            import psutil
            
            # Get system memory info
            memory = psutil.virtual_memory()
            total_ram_mb = memory.total // (1024 * 1024)
            
            # Initialize hardware info
            hardware_info = HardwareInfo(
                cpu_cores=psutil.cpu_count(),
                total_ram=total_ram_mb,
                recommended_backend='transformers'
            )
            
            # Check GPU availability
            gpu_devices = []
            total_vram_mb = 0
            
            if torch.cuda.is_available():
                hardware_info.gpu_count = torch.cuda.device_count()
                hardware_info.supported_hardware.append(HardwareType.CUDA)
                
                for i in range(hardware_info.gpu_count):
                    props = torch.cuda.get_device_properties(i)
                    vram_mb = props.total_memory // (1024 * 1024)
                    total_vram_mb += vram_mb
                    
                    gpu_info = {
                        'id': i,
                        'name': props.name,
                        'vram_mb': vram_mb,
                        'compute_capability': f"{props.major}.{props.minor}",
                        'type': 'CUDA'
                    }
                    gpu_devices.append(gpu_info)
            
            # Check MPS (Apple Silicon) support
            if hasattr(torch.backends, 'mps') and torch.backends.mps.is_available():
                hardware_info.supported_hardware.append(HardwareType.MPS)
                if not gpu_devices:  # Only add if no CUDA devices
                    gpu_info = {
                        'id': 0,
                        'name': 'Apple Silicon GPU',
                        'vram_mb': 0,  # MPS shares system memory
                        'compute_capability': 'N/A',
                        'type': 'MPS'
                    }
                    gpu_devices.append(gpu_info)
                    hardware_info.gpu_count = 1
            
            # Check ROCm support (AMD)
            if hasattr(torch, 'hip') and torch.hip.is_available():
                hardware_info.supported_hardware.append(HardwareType.ROCM)
                if not gpu_devices:  # Only add if no other GPU devices
                    gpu_info = {
                        'id': 0,
                        'name': 'AMD ROCm GPU',
                        'vram_mb': 0,  # Would need ROCm-specific calls to get actual VRAM
                        'compute_capability': 'N/A',
                        'type': 'ROCm'
                    }
                    gpu_devices.append(gpu_info)
                    hardware_info.gpu_count = 1
            
            hardware_info.gpu_devices = gpu_devices
            hardware_info.total_vram = total_vram_mb
            
            # Always support CPU
            hardware_info.supported_hardware.append(HardwareType.CPU)
            
            return hardware_info
            
        except Exception as e:
            self.logger.error(f"Error getting hardware info: {e}")
            # Return minimal hardware info on error
            return HardwareInfo(
                cpu_cores=1,
                total_ram=1024,
                recommended_backend='transformers',
                supported_hardware=[HardwareType.CPU]
            )
    
    def get_generation_stats(self) -> Dict[str, Any]:
        """Get generation statistics."""
        return self._generation_stats.copy()
    
    def clear_cache(self):
        """Clear the model conversion cache."""
        try:
            if os.path.exists(self._model_cache_dir):
                for item in os.listdir(self._model_cache_dir):
                    item_path = os.path.join(self._model_cache_dir, item)
                    if os.path.isdir(item_path):
                        shutil.rmtree(item_path)
                    else:
                        os.unlink(item_path)
                self.logger.info("Model cache cleared")
        except Exception as e:
            self.logger.error(f"Error clearing cache: {e}")
    
    def get_cache_info(self) -> Dict[str, Any]:
        """Get information about the model cache."""
        try:
            cache_info = {
                'cache_dir': self._model_cache_dir,
                'cached_models': [],
                'total_size_mb': 0
            }
            
            if os.path.exists(self._model_cache_dir):
                for item in os.listdir(self._model_cache_dir):
                    item_path = os.path.join(self._model_cache_dir, item)
                    if os.path.isdir(item_path):
                        # Calculate directory size
                        size_bytes = sum(
                            os.path.getsize(os.path.join(dirpath, filename))
                            for dirpath, dirnames, filenames in os.walk(item_path)
                            for filename in filenames
                        )
                        size_mb = size_bytes // (1024 * 1024)
                        
                        cache_info['cached_models'].append({
                            'name': item,
                            'size_mb': size_mb,
                            'path': item_path
                        })
                        cache_info['total_size_mb'] += size_mb
            
            return cache_info
            
        except Exception as e:
            self.logger.error(f"Error getting cache info: {e}")
            return {
                'cache_dir': self._model_cache_dir,
                'cached_models': [],
                'total_size_mb': 0
            } 
   
    # Hugging Face Integration Methods
    
    def load_huggingface_model(self, model_id: str, 
                              progress_callback: Optional[Callable] = None,
                              force_download: bool = False,
                              **kwargs) -> LoadingResult:
        """
        Load a model directly from Hugging Face Hub.
        
        Args:
            model_id: Hugging Face model ID (e.g., "microsoft/DialoGPT-medium")
            progress_callback: Optional callback for download progress
            force_download: Force re-download even if cached
            **kwargs: Additional loading parameters
            
        Returns:
            LoadingResult with detailed loading information
        """
        start_time = time.time()
        
        try:
            # Import HF integration service
            from llmtoolkit.app.services.huggingface_integration import HuggingFaceIntegration
            
            # Initialize HF integration
            hf_integration = HuggingFaceIntegration()
            
            self.logger.info(f"Loading Hugging Face model: {model_id}")
            
            # Resolve model first
            resolution = hf_integration.resolve_model_id(model_id)
            if not resolution.exists:
                return LoadingResult(
                    success=False,
                    backend_used=self.config.name,
                    hardware_used="none",
                    load_time=time.time() - start_time,
                    error_message=resolution.error_message or "Model not found on Hugging Face Hub"
                )
            
            # Check authentication if required
            if resolution.requires_auth and not hf_integration.is_authenticated():
                return LoadingResult(
                    success=False,
                    backend_used=self.config.name,
                    hardware_used="none",
                    load_time=time.time() - start_time,
                    error_message="Authentication required for private model. Please authenticate first."
                )
            
            # Download model
            download_result = hf_integration.download_model(
                model_id=model_id,
                progress_callback=progress_callback,
                force_download=force_download
            )
            
            if not download_result.success:
                return LoadingResult(
                    success=False,
                    backend_used=self.config.name,
                    hardware_used="none",
                    load_time=time.time() - start_time,
                    error_message=download_result.error_message or "Failed to download model"
                )
            
            # Load the downloaded model using standard transformers loading
            load_result = self.load_model(download_result.local_path, **kwargs)
            
            # Update result with HF-specific information
            if load_result.success and hasattr(load_result, 'model_info'):
                if isinstance(load_result.model_info, dict):
                    load_result.model_info.update({
                        'huggingface_model_id': model_id,
                        'huggingface_cached': download_result.cached,
                        'download_time': download_result.download_time,
                        'download_size_mb': download_result.total_size_mb
                    })
            
            return load_result
            
        except Exception as e:
            error_msg = f"Failed to load Hugging Face model {model_id}: {str(e)}"
            self.logger.error(error_msg)
            
            return LoadingResult(
                success=False,
                backend_used=self.config.name,
                hardware_used="none",
                load_time=time.time() - start_time,
                error_message=error_msg
            )
    
    def authenticate_huggingface(self, token: str) -> Dict[str, Any]:
        """
        Authenticate with Hugging Face using an API token.
        
        Args:
            token: Hugging Face API token
            
        Returns:
            Dictionary with authentication result
        """
        try:
            from llmtoolkit.app.services.huggingface_integration import HuggingFaceIntegration
            
            hf_integration = HuggingFaceIntegration()
            auth_result = hf_integration.authenticate(token)
            
            return {
                'success': auth_result.success,
                'username': auth_result.username,
                'token_valid': auth_result.token_valid,
                'error_message': auth_result.error_message
            }
            
        except Exception as e:
            self.logger.error(f"HF authentication failed: {e}")
            return {
                'success': False,
                'username': None,
                'token_valid': False,
                'error_message': f"Authentication failed: {str(e)}"
            }
    
    def search_huggingface_models(self, query: str, limit: int = 10) -> List[Dict[str, Any]]:
        """
        Search for models on Hugging Face Hub.
        
        Args:
            query: Search query
            limit: Maximum number of results
            
        Returns:
            List of model information dictionaries
        """
        try:
            from llmtoolkit.app.services.huggingface_integration import HuggingFaceIntegration
            
            hf_integration = HuggingFaceIntegration()
            
            # Use HF API to search models
            models = hf_integration.api.list_models(
                search=query,
                limit=limit,
                sort="downloads",
                direction=-1
            )
            
            results = []
            for model in models:
                try:
                    results.append({
                        'model_id': model.modelId,
                        'downloads': getattr(model, 'downloads', 0),
                        'likes': getattr(model, 'likes', 0),
                        'tags': getattr(model, 'tags', []),
                        'pipeline_tag': getattr(model, 'pipeline_tag', None),
                        'private': getattr(model, 'private', False),
                        'last_modified': str(getattr(model, 'last_modified', '')),
                        'library_name': getattr(model, 'library_name', None)
                    })
                except Exception as e:
                    self.logger.warning(f"Error processing model info: {e}")
                    continue
            
            return results
            
        except Exception as e:
            self.logger.error(f"HF model search failed: {e}")
            return []
    
    def get_huggingface_model_info(self, model_id: str) -> Dict[str, Any]:
        """
        Get detailed information about a Hugging Face model.
        
        Args:
            model_id: Hugging Face model ID
            
        Returns:
            Dictionary with model information
        """
        try:
            from llmtoolkit.app.services.huggingface_integration import HuggingFaceIntegration
            
            hf_integration = HuggingFaceIntegration()
            resolution = hf_integration.resolve_model_id(model_id)
            
            if not resolution.exists:
                return {
                    'success': False,
                    'error_message': resolution.error_message or "Model not found"
                }
            
            # Get file list
            files = hf_integration.list_model_files(model_id)
            
            return {
                'success': True,
                'model_id': resolution.model_id,
                'exists': resolution.exists,
                'is_private': resolution.is_private,
                'requires_auth': resolution.requires_auth,
                'model_type': resolution.model_type,
                'architecture': resolution.architecture,
                'tags': resolution.tags or [],
                'downloads': resolution.downloads,
                'last_modified': resolution.last_modified,
                'size_bytes': resolution.size_bytes,
                'size_mb': resolution.size_bytes / (1024 * 1024) if resolution.size_bytes else None,
                'files': [
                    {
                        'filename': f.filename,
                        'size_bytes': f.size_bytes,
                        'size_mb': f.size_bytes / (1024 * 1024),
                        'lfs': f.lfs
                    }
                    for f in files
                ]
            }
            
        except Exception as e:
            self.logger.error(f"Failed to get HF model info for {model_id}: {e}")
            return {
                'success': False,
                'error_message': f"Failed to get model info: {str(e)}"
            }
    
    def check_huggingface_updates(self, model_id: str) -> Dict[str, Any]:
        """
        Check if a cached Hugging Face model has updates available.
        
        Args:
            model_id: Hugging Face model ID
            
        Returns:
            Dictionary with update information
        """
        try:
            from llmtoolkit.app.services.huggingface_integration import HuggingFaceIntegration
            
            hf_integration = HuggingFaceIntegration()
            
            # Find local model path
            cached_path = hf_integration._get_cached_model_path(model_id)
            if not cached_path:
                return {
                    'success': False,
                    'error_message': 'Model not found in cache'
                }
            
            # Check for updates
            update_status = hf_integration.check_model_updates(model_id, str(cached_path))
            
            return {
                'success': True,
                'model_id': update_status.model_id,
                'local_version': update_status.local_version,
                'remote_version': update_status.remote_version,
                'update_available': update_status.update_available,
                'local_path': update_status.local_path,
                'last_check': update_status.last_check.isoformat(),
                'size_difference_mb': update_status.size_difference_mb
            }
            
        except Exception as e:
            self.logger.error(f"Failed to check HF updates for {model_id}: {e}")
            return {
                'success': False,
                'error_message': f"Failed to check updates: {str(e)}"
            }
    
    def get_huggingface_cache_info(self) -> Dict[str, Any]:
        """
        Get information about the Hugging Face cache.
        
        Returns:
            Dictionary with cache information
        """
        try:
            from llmtoolkit.app.services.huggingface_integration import HuggingFaceIntegration
            
            hf_integration = HuggingFaceIntegration()
            return hf_integration.get_cache_info()
            
        except Exception as e:
            self.logger.error(f"Failed to get HF cache info: {e}")
            return {
                'error': f"Failed to get cache info: {str(e)}"
            }
    
    def cleanup_huggingface_cache(self, max_age_days: int = 30, max_size_gb: float = 10.0) -> Dict[str, Any]:
        """
        Clean up old Hugging Face cached models.
        
        Args:
            max_age_days: Maximum age of cached models in days
            max_size_gb: Maximum total cache size in GB
            
        Returns:
            Dictionary with cleanup statistics
        """
        try:
            from llmtoolkit.app.services.huggingface_integration import HuggingFaceIntegration
            
            hf_integration = HuggingFaceIntegration()
            return hf_integration.cleanup_cache(max_age_days, max_size_gb)
            
        except Exception as e:
            self.logger.error(f"Failed to cleanup HF cache: {e}")
            return {
                'error': f"Failed to cleanup cache: {str(e)}"
            }