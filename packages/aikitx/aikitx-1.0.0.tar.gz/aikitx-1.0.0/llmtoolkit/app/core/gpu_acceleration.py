"""
GPU Acceleration Module

This module provides streamlined GPU acceleration support similar to LM Studio:
- Auto-detects and uses GPU if available (NVIDIA CUDA on Windows/Linux, Metal on macOS)
- Uses only system-installed GPU drivers and runtime
- Falls back to CPU automatically if GPU is not available
- Provides minimal but effective user controls
"""

import os
import sys
import logging
import platform
import subprocess
from enum import Enum
from typing import Dict, List, Optional, Tuple, Any, Union
from dataclasses import dataclass


class GPUBackend(Enum):
    """Supported GPU backends."""
    CUDA = "cuda"
    METAL = "metal"
    CPU = "cpu"


@dataclass
class GPUInfo:
    """Information about detected GPU."""
    name: str
    backend: GPUBackend
    memory_total: int  # MB
    available: bool = True
    driver_version: str = ""
    compute_capability: str = ""  # For CUDA


class GPUAcceleration:
    """
    Streamlined GPU acceleration support.
    
    This class provides GPU detection and configuration similar to LM Studio:
    - Simple, automatic detection of CUDA and Metal
    - Uses system-installed drivers only
    - Automatic fallback to CPU
    - Minimal user configuration
    """
    
    def __init__(self, config_manager=None):
        """
        Initialize GPU acceleration support.
        
        Args:
            config_manager: Optional configuration manager
        """
        self.logger = logging.getLogger("gguf_loader.gpu")
        self.config_manager = config_manager
        
        # Detection results
        self.gpu_info = None
        self.backend = GPUBackend.CPU
        self.has_gpu = False
        self.cuda_available = False
        self.metal_available = False
        
        # Environment variables
        self.env_vars = {}
        
        # Detect GPU on initialization
        self.detect_gpu()
    
    def detect_gpu(self) -> bool:
        """
        Detect available GPU and appropriate backend.
        
        Returns:
            True if GPU is available, False otherwise
        """
        self.logger.info("Detecting GPU capabilities")
        
        # Reset state
        self.gpu_info = None
        self.backend = GPUBackend.CPU
        self.has_gpu = False
        self.cuda_available = False
        self.metal_available = False
        
        # Check for CUDA on Windows/Linux
        if platform.system() in ["Windows", "Linux"]:
            self.cuda_available = self._detect_cuda()
            
            if self.cuda_available:
                self.has_gpu = True
                self.backend = GPUBackend.CUDA
                self.logger.info(f"CUDA GPU detected: {self.gpu_info.name}")
        
        # Check for Metal on macOS
        elif platform.system() == "Darwin":  # macOS
            self.metal_available = self._detect_metal()
            
            if self.metal_available:
                self.has_gpu = True
                self.backend = GPUBackend.METAL
                self.logger.info(f"Metal GPU detected: {self.gpu_info.name}")
        
        # Log result
        if not self.has_gpu:
            self.logger.info("No compatible GPU detected, using CPU")
            self.backend = GPUBackend.CPU
        
        return self.has_gpu
    
    def _detect_cuda(self) -> bool:
        """
        Detect NVIDIA GPU with CUDA support.
        
        Returns:
            True if CUDA GPU is available, False otherwise
        """
        try:
            # Check for nvidia-smi
            result = subprocess.run(["nvidia-smi", "--query-gpu=name,memory.total,driver_version", 
                                   "--format=csv,noheader,nounits"], 
                                  capture_output=True, text=True, timeout=5)
            
            if result.returncode != 0:
                self.logger.debug("nvidia-smi command failed")
                return False
            
            # Parse output
            lines = result.stdout.strip().split('\n')
            if not lines:
                return False
                
            # Get first GPU info
            parts = [p.strip() for p in lines[0].split(',')]
            if len(parts) >= 3:
                name = parts[0]
                memory_total = int(parts[1])
                driver_version = parts[2]
                
                # Check for CUDA compute capability
                compute_capability = self._get_cuda_compute_capability()
                
                # Create GPU info
                self.gpu_info = GPUInfo(
                    name=name,
                    backend=GPUBackend.CUDA,
                    memory_total=memory_total,
                    driver_version=driver_version,
                    compute_capability=compute_capability
                )
                
                # Check if llama-cpp-python has CUDA support
                has_cuda_support = self._check_llama_cpp_cuda_support()
                
                return has_cuda_support
                
        except (subprocess.SubprocessError, FileNotFoundError, IndexError) as e:
            self.logger.debug(f"CUDA detection error: {e}")
            return False
    
    def _detect_metal(self) -> bool:
        """
        Detect Apple GPU with Metal support.
        
        Returns:
            True if Metal GPU is available, False otherwise
        """
        try:
            if platform.system() != "Darwin":
                return False
                
            # Check macOS version for Metal support
            mac_ver = platform.mac_ver()[0]
            if mac_ver:
                major, minor = map(int, mac_ver.split('.')[:2])
                # Metal requires macOS 10.11+
                if major < 10 or (major == 10 and minor < 11):
                    self.logger.debug(f"macOS version {mac_ver} does not support Metal")
                    return False
            
            # Use system_profiler to get GPU info
            try:
                result = subprocess.run(["system_profiler", "SPDisplaysDataType", "-json"], 
                                      capture_output=True, text=True, timeout=5)
                
                if result.returncode == 0 and result.stdout:
                    import json
                    data = json.loads(result.stdout)
                    
                    # Handle both array and object formats
                    displays_data = data
                    if isinstance(data, list) and len(data) > 0:
                        displays_data = data[0]
                    
                    for display in displays_data.get('SPDisplaysDataType', []):
                        if 'sppci_model' in display:
                            name = display['sppci_model']
                            
                            # Extract VRAM if available
                            memory_total = 1024  # Default 1GB if unknown
                            if 'sppci_vram' in display:
                                vram_str = display['sppci_vram']
                                if 'MB' in vram_str:
                                    memory_total = int(vram_str.replace(' MB', ''))
                                elif 'GB' in vram_str:
                                    memory_total = int(float(vram_str.replace(' GB', '')) * 1024)
                            
                            # Create GPU info
                            self.gpu_info = GPUInfo(
                                name=name,
                                backend=GPUBackend.METAL,
                                memory_total=memory_total
                            )
                            
                            # Check if llama-cpp-python has Metal support
                            has_metal_support = self._check_llama_cpp_metal_support()
                            
                            return has_metal_support
            except Exception as e:
                self.logger.debug(f"Error parsing system_profiler output: {e}")
                pass
                
            # Fallback: If we can't get detailed info but we're on macOS,
            # assume Metal is available but we don't know details
            self.gpu_info = GPUInfo(
                name="Apple GPU",
                backend=GPUBackend.METAL,
                memory_total=1024  # Default assumption
            )
            
            # Check if llama-cpp-python has Metal support
            return self._check_llama_cpp_metal_support()
                
        except Exception as e:
            self.logger.debug(f"Metal detection error: {e}")
            return False
    
    def _get_cuda_compute_capability(self) -> str:
        """
        Get CUDA compute capability of the GPU.
        
        Returns:
            CUDA compute capability as string (e.g., "7.5")
        """
        try:
            # Try to get compute capability using nvidia-smi
            result = subprocess.run(["nvidia-smi", "--query-gpu=compute_cap", "--format=csv,noheader,nounits"], 
                                  capture_output=True, text=True, timeout=5)
            
            if result.returncode == 0 and result.stdout.strip():
                return result.stdout.strip()
                
        except (subprocess.SubprocessError, FileNotFoundError):
            pass
            
        return "Unknown"
    
    def _check_llama_cpp_cuda_support(self) -> bool:
        """
        Check if llama-cpp-python has CUDA support.
        
        Returns:
            True if CUDA support is available, False otherwise
        """
        try:
            import llama_cpp
            
            # Check if llama-cpp-python was compiled with CUDA support
            # This is a heuristic check - different ways to detect CUDA support
            has_cuda = False
            
            # Check for GGML_USE_CUBLAS constant
            if hasattr(llama_cpp, 'GGML_USE_CUBLAS'):
                has_cuda = bool(llama_cpp.GGML_USE_CUBLAS)
            
            # Check if 'cuda' is in the library path
            if not has_cuda and hasattr(llama_cpp, '__file__'):
                has_cuda = 'cuda' in str(llama_cpp.__file__).lower()
            
            # Try to create a model with n_gpu_layers > 0
            if not has_cuda:
                try:
                    # Just check if the parameter exists and doesn't raise an error
                    # We don't actually load a model here
                    params = llama_cpp.llama_context_params()
                    if hasattr(params, 'n_gpu_layers'):
                        has_cuda = True
                except:
                    pass
            
            return has_cuda
            
        except ImportError:
            self.logger.debug("llama_cpp module not found")
            return False
        except Exception as e:
            self.logger.debug(f"Error checking CUDA support: {e}")
            return False
    
    def _check_llama_cpp_metal_support(self) -> bool:
        """
        Check if llama-cpp-python has Metal support.
        
        Returns:
            True if Metal support is available, False otherwise
        """
        try:
            import llama_cpp
            
            # Check if llama-cpp-python was compiled with Metal support
            has_metal = False
            
            # Check for GGML_USE_METAL constant
            if hasattr(llama_cpp, 'GGML_USE_METAL'):
                has_metal = bool(llama_cpp.GGML_USE_METAL)
            
            # Check if 'metal' is in the library path
            if not has_metal and hasattr(llama_cpp, '__file__'):
                has_metal = 'metal' in str(llama_cpp.__file__).lower()
            
            # Try to create a model with n_gpu_layers > 0
            if not has_metal:
                try:
                    # Just check if the parameter exists and doesn't raise an error
                    params = llama_cpp.llama_context_params()
                    if hasattr(params, 'n_gpu_layers'):
                        has_metal = True
                except:
                    pass
            
            return has_metal
            
        except ImportError:
            self.logger.debug("llama_cpp module not found")
            return False
        except Exception as e:
            self.logger.debug(f"Error checking Metal support: {e}")
            return False
    
    def get_backend_from_preference(self, preference: str = "auto") -> GPUBackend:
        """
        Get the appropriate backend based on user preference and availability.
        
        Args:
            preference: User preference ("auto", "cpu", or "gpu")
            
        Returns:
            Appropriate GPUBackend
        """
        if preference == "cpu":
            return GPUBackend.CPU
        elif preference == "gpu":
            # If GPU is requested but not available, log a warning
            if not self.has_gpu:
                self.logger.warning("GPU requested but not available, falling back to CPU")
                return GPUBackend.CPU
            return self.backend
        else:  # auto
            return self.backend if self.has_gpu else GPUBackend.CPU
    
    def get_model_config(self, preference: str = "auto", gpu_layers: int = None) -> Dict[str, Any]:
        """
        Get model configuration for the selected backend.
        
        Args:
            preference: User preference ("auto", "cpu", or "gpu")
            gpu_layers: Number of layers to run on GPU (None for auto)
            
        Returns:
            Dictionary with model configuration
        """
        backend = self.get_backend_from_preference(preference)
        
        # Base configuration
        config = {
            "backend": backend.value,
            "n_threads": min(os.cpu_count() or 4, 8),  # Default to reasonable thread count
            "n_gpu_layers": 0,  # Default to CPU
            "use_mlock": True,  # Better memory management
        }
        
        # Add GPU-specific configuration
        if backend != GPUBackend.CPU:
            # Calculate optimal GPU layers if not specified
            if gpu_layers is None:
                if self.gpu_info and self.gpu_info.memory_total:
                    memory_gb = self.gpu_info.memory_total / 1024
                    
                    # Scale layers based on available memory
                    if memory_gb >= 24:  # High-end GPU
                        gpu_layers = 100  # Use all layers
                    elif memory_gb >= 16:
                        gpu_layers = 60
                    elif memory_gb >= 8:
                        gpu_layers = 40
                    elif memory_gb >= 4:
                        gpu_layers = 20
                    else:
                        gpu_layers = 10
                else:
                    # Conservative default if we don't know the memory
                    gpu_layers = 20
            
            config["n_gpu_layers"] = gpu_layers
            config["n_threads"] = 4  # Fewer CPU threads when using GPU
            
            # Backend-specific settings
            if backend == GPUBackend.CUDA:
                # CUDA-specific settings
                pass  # No special settings needed currently
            elif backend == GPUBackend.METAL:
                # Metal-specific settings
                pass  # No special settings needed currently
        
        return config
    
    def get_environment_variables(self, preference: str = "auto") -> Dict[str, str]:
        """
        Get environment variables for the selected backend.
        
        Args:
            preference: User preference ("auto", "cpu", or "gpu")
            
        Returns:
            Dictionary with environment variables
        """
        backend = self.get_backend_from_preference(preference)
        env_vars = {}
        
        # Force CPU if requested
        if backend == GPUBackend.CPU:
            env_vars["GGML_FORCE_CPU"] = "1"
        
        # Add backend-specific environment variables
        if backend == GPUBackend.CUDA:
            # No special environment variables needed for CUDA currently
            pass
        elif backend == GPUBackend.METAL:
            # No special environment variables needed for Metal currently
            pass
        
        self.env_vars = env_vars
        return env_vars
    
    def get_status_message(self) -> str:
        """
        Get a user-friendly status message about GPU acceleration.
        
        Returns:
            Status message string
        """
        if not self.has_gpu:
            return "CPU only (no compatible GPU detected)"
        
        if self.backend == GPUBackend.CUDA:
            return f"NVIDIA GPU: {self.gpu_info.name} ({self.gpu_info.memory_total} MB)"
        elif self.backend == GPUBackend.METAL:
            return f"Apple GPU: {self.gpu_info.name} ({self.gpu_info.memory_total} MB)"
        else:
            return "CPU only (GPU disabled)"
    
    def log_acceleration_info(self, preference: str = "auto", gpu_layers: int = None):
        """
        Log information about the current acceleration setup.
        
        Args:
            preference: User preference ("auto", "cpu", or "gpu")
            gpu_layers: Number of layers to run on GPU
        """
        backend = self.get_backend_from_preference(preference)
        
        self.logger.info(f"Acceleration mode: {backend.value.upper()}")
        
        if backend != GPUBackend.CPU:
            if self.gpu_info:
                self.logger.info(f"GPU: {self.gpu_info.name}")
                self.logger.info(f"GPU Memory: {self.gpu_info.memory_total} MB")
                
                if self.gpu_info.backend == GPUBackend.CUDA and self.gpu_info.driver_version:
                    self.logger.info(f"CUDA Driver: {self.gpu_info.driver_version}")
                    if self.gpu_info.compute_capability != "Unknown":
                        self.logger.info(f"Compute Capability: {self.gpu_info.compute_capability}")
            
            actual_layers = gpu_layers
            if actual_layers is None:
                config = self.get_model_config(preference, gpu_layers)
                actual_layers = config.get("n_gpu_layers", 0)
                
            self.logger.info(f"GPU Layers: {actual_layers}")
        else:
            self.logger.info("Using CPU only")
            if preference == "gpu" and not self.has_gpu:
                self.logger.warning("GPU was requested but no compatible GPU was detected")