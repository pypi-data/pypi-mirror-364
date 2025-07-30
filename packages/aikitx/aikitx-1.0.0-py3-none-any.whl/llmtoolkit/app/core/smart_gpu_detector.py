"""
Smart GPU Detector - LM Studio Style

This module provides seamless GPU detection and acceleration exactly like LM Studio:
- Auto-detect and use GPU if available
- Use only system-installed drivers (no bundled dependencies)
- CUDA for NVIDIA, Metal for macOS, fallback to CPU
- Works out of the box or falls back gracefully
"""

import os
import sys
import logging
import platform
import subprocess
from typing import Dict, List, Optional, Tuple, Any
from dataclasses import dataclass
from enum import Enum


class GPUBackend(Enum):
    """GPU backends supported by llama.cpp."""
    CUDA = "cuda"
    METAL = "metal"
    CPU = "cpu"


@dataclass
class GPUInfo:
    """Information about detected GPU."""
    name: str
    memory_mb: int
    backend: GPUBackend
    device_id: int = 0
    is_available: bool = True
    driver_version: str = ""


@dataclass
class GPUCapabilities:
    """System GPU capabilities."""
    has_gpu: bool = False
    backend: GPUBackend = GPUBackend.CPU
    devices: List[GPUInfo] = None
    recommended_layers: int = 0
    total_vram_mb: int = 0
    
    def __post_init__(self):
        if self.devices is None:
            self.devices = []


class SmartGPUDetector:
    """
    Smart GPU detection exactly like LM Studio.
    
    Features:
    - Auto-detects GPU and uses system drivers only
    - CUDA for NVIDIA, Metal for macOS
    - Seamless fallback to CPU
    - No manual installation required
    - Works out of the box
    """
    
    def __init__(self, logger=None):
        """Initialize the smart GPU detector."""
        self.logger = logger or logging.getLogger("gguf_loader.smart_gpu")
        self.capabilities = GPUCapabilities()
        self._detection_complete = False
    
    def detect_gpu_capabilities(self) -> GPUCapabilities:
        """
        Detect GPU capabilities using system-installed drivers only.
        
        Returns:
            GPUCapabilities with detected information
        """
        if self._detection_complete:
            return self.capabilities
        
        self.logger.info("🔍 Detecting GPU capabilities (LM Studio style)...")
        
        # Reset capabilities
        self.capabilities = GPUCapabilities()
        
        # Detect based on platform and available hardware
        if platform.system() == "Darwin":  # macOS
            self._detect_metal()
        else:  # Windows/Linux
            self._detect_cuda()
        
        # Log detection results
        self._log_detection_results()
        
        self._detection_complete = True
        return self.capabilities
    
    def _detect_cuda(self):
        """Detect NVIDIA CUDA support using system drivers."""
        try:
            # Check for NVIDIA GPU using nvidia-ml-py (if available)
            cuda_info = self._check_nvidia_ml()
            if cuda_info:
                self.capabilities.has_gpu = True
                self.capabilities.backend = GPUBackend.CUDA
                self.capabilities.devices = cuda_info
                self.capabilities.total_vram_mb = sum(gpu.memory_mb for gpu in cuda_info)
                self.capabilities.recommended_layers = self._calculate_cuda_layers(self.capabilities.total_vram_mb)
                self.logger.info(f"[OK] CUDA GPU detected: {len(cuda_info)} device(s)")
                return
            
            # Fallback: Check nvidia-smi
            cuda_info = self._check_nvidia_smi()
            if cuda_info:
                self.capabilities.has_gpu = True
                self.capabilities.backend = GPUBackend.CUDA
                self.capabilities.devices = cuda_info
                self.capabilities.total_vram_mb = sum(gpu.memory_mb for gpu in cuda_info)
                self.capabilities.recommended_layers = self._calculate_cuda_layers(self.capabilities.total_vram_mb)
                self.logger.info(f"[OK] CUDA GPU detected via nvidia-smi: {len(cuda_info)} device(s)")
                return
            
        except Exception as e:
            self.logger.debug(f"CUDA detection failed: {e}")
        
        # No CUDA GPU found
        self.logger.info("ℹ️ No CUDA GPU detected, using CPU")
        self.capabilities.backend = GPUBackend.CPU
    
    def _detect_metal(self):
        """Detect Metal support on macOS."""
        try:
            # Check macOS version for Metal support
            version = platform.mac_ver()[0]
            if version:
                major, minor = map(int, version.split('.')[:2])
                if major > 10 or (major == 10 and minor >= 11):
                    # Get GPU info using system_profiler
                    metal_info = self._check_metal_gpu()
                    if metal_info:
                        self.capabilities.has_gpu = True
                        self.capabilities.backend = GPUBackend.METAL
                        self.capabilities.devices = metal_info
                        self.capabilities.total_vram_mb = sum(gpu.memory_mb for gpu in metal_info)
                        self.capabilities.recommended_layers = self._calculate_metal_layers(self.capabilities.total_vram_mb)
                        self.logger.info(f"[OK] Metal GPU detected: {len(metal_info)} device(s)")
                        return
            
        except Exception as e:
            self.logger.debug(f"Metal detection failed: {e}")
        
        # No Metal GPU or unsupported macOS version
        self.logger.info("ℹ️ No Metal GPU detected, using CPU")
        self.capabilities.backend = GPUBackend.CPU
    
    def _check_nvidia_ml(self) -> Optional[List[GPUInfo]]:
        """Check NVIDIA GPUs using nvidia-ml-py."""
        try:
            import pynvml
            pynvml.nvmlInit()
            
            device_count = pynvml.nvmlDeviceGetCount()
            if device_count == 0:
                return None
            
            gpus = []
            for i in range(device_count):
                handle = pynvml.nvmlDeviceGetHandleByIndex(i)
                name = pynvml.nvmlDeviceGetName(handle).decode('utf-8')
                
                # Get memory info
                mem_info = pynvml.nvmlDeviceGetMemoryInfo(handle)
                memory_mb = mem_info.total // (1024 * 1024)
                
                # Get driver version
                try:
                    driver_version = pynvml.nvmlSystemGetDriverVersion().decode('utf-8')
                except:
                    driver_version = "Unknown"
                
                gpu = GPUInfo(
                    name=name,
                    memory_mb=memory_mb,
                    backend=GPUBackend.CUDA,
                    device_id=i,
                    driver_version=driver_version
                )
                gpus.append(gpu)
            
            return gpus if gpus else None
            
        except ImportError:
            # pynvml not available, try nvidia-smi
            return None
        except Exception:
            return None
    
    def _check_nvidia_smi(self) -> Optional[List[GPUInfo]]:
        """Check NVIDIA GPUs using nvidia-smi."""
        try:
            cmd = ["nvidia-smi", "--query-gpu=index,name,memory.total,driver_version", 
                   "--format=csv,noheader,nounits"]
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=5)
            
            if result.returncode != 0 or not result.stdout.strip():
                return None
            
            gpus = []
            for line in result.stdout.strip().split('\n'):
                parts = [p.strip() for p in line.split(',')]
                if len(parts) >= 4:
                    try:
                        device_id = int(parts[0])
                        name = parts[1]
                        memory_mb = int(parts[2])
                        driver_version = parts[3]
                        
                        gpu = GPUInfo(
                            name=name,
                            memory_mb=memory_mb,
                            backend=GPUBackend.CUDA,
                            device_id=device_id,
                            driver_version=driver_version
                        )
                        gpus.append(gpu)
                    except (ValueError, IndexError):
                        continue
            
            return gpus if gpus else None
            
        except (subprocess.TimeoutExpired, FileNotFoundError, subprocess.SubprocessError):
            return None
    
    def _check_metal_gpu(self) -> Optional[List[GPUInfo]]:
        """Check Metal GPUs on macOS."""
        try:
            cmd = ["system_profiler", "SPDisplaysDataType", "-json"]
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=10)
            
            if result.returncode != 0:
                return None
            
            import json
            data = json.loads(result.stdout)
            
            gpus = []
            device_id = 0
            
            for display in data.get('SPDisplaysDataType', []):
                if 'sppci_model' in display:
                    name = display['sppci_model']
                    
                    # Extract VRAM
                    memory_mb = 1024  # Default fallback
                    if 'sppci_vram' in display:
                        vram_str = display['sppci_vram']
                        if 'MB' in vram_str:
                            try:
                                memory_mb = int(vram_str.replace(' MB', ''))
                            except ValueError:
                                pass
                        elif 'GB' in vram_str:
                            try:
                                memory_mb = int(float(vram_str.replace(' GB', '')) * 1024)
                            except ValueError:
                                pass
                    
                    # Only include dedicated GPUs (skip integrated if possible)
                    if memory_mb >= 512:  # At least 512MB VRAM
                        gpu = GPUInfo(
                            name=name,
                            memory_mb=memory_mb,
                            backend=GPUBackend.METAL,
                            device_id=device_id
                        )
                        gpus.append(gpu)
                        device_id += 1
            
            return gpus if gpus else None
            
        except (subprocess.TimeoutExpired, FileNotFoundError, json.JSONDecodeError):
            return None
    
    def _calculate_cuda_layers(self, vram_mb: int) -> int:
        """Calculate recommended GPU layers for CUDA based on VRAM."""
        if vram_mb >= 24000:  # 24GB+
            return 50
        elif vram_mb >= 16000:  # 16GB+
            return 45
        elif vram_mb >= 12000:  # 12GB+
            return 40
        elif vram_mb >= 8000:   # 8GB+
            return 35
        elif vram_mb >= 6000:   # 6GB+
            return 30
        elif vram_mb >= 4000:   # 4GB+
            return 25
        elif vram_mb >= 2000:   # 2GB+
            return 15
        else:
            return 10
    
    def _calculate_metal_layers(self, vram_mb: int) -> int:
        """Calculate recommended GPU layers for Metal based on VRAM."""
        # Metal is generally more efficient, so we can be more aggressive
        if vram_mb >= 16000:  # 16GB+
            return 50
        elif vram_mb >= 8000:   # 8GB+
            return 45
        elif vram_mb >= 4000:   # 4GB+
            return 35
        elif vram_mb >= 2000:   # 2GB+
            return 25
        else:
            return 15
    
    def _log_detection_results(self):
        """Log the detection results."""
        if self.capabilities.has_gpu:
            backend_name = self.capabilities.backend.value.upper()
            total_vram = self.capabilities.total_vram_mb / 1024  # Convert to GB
            
            self.logger.info(f"🎮 GPU Acceleration: {backend_name}")
            self.logger.info(f"📊 Total VRAM: {total_vram:.1f} GB")
            self.logger.info(f"[TOOL] Recommended GPU Layers: {self.capabilities.recommended_layers}")
            
            for i, gpu in enumerate(self.capabilities.devices):
                vram_gb = gpu.memory_mb / 1024
                self.logger.info(f"   GPU {i}: {gpu.name} ({vram_gb:.1f} GB)")
                if gpu.driver_version:
                    self.logger.info(f"   Driver: {gpu.driver_version}")
        else:
            self.logger.info("[HARDWARE] Using CPU acceleration (no compatible GPU found)")
    
    def get_llama_cpp_args(self, user_gpu_layers: Optional[int] = None) -> Dict[str, Any]:
        """
        Get llama.cpp arguments for the detected GPU configuration.
        
        Args:
            user_gpu_layers: User-specified number of GPU layers (overrides auto-detection)
            
        Returns:
            Dictionary of llama.cpp initialization arguments
        """
        if not self.capabilities.has_gpu:
            return {
                "n_gpu_layers": 0,
                "verbose": False
            }
        
        # Determine GPU layers
        gpu_layers = user_gpu_layers if user_gpu_layers is not None else self.capabilities.recommended_layers
        
        args = {
            "n_gpu_layers": gpu_layers,
            "verbose": False
        }
        
        # Add backend-specific arguments
        if self.capabilities.backend == GPUBackend.CUDA:
            # CUDA-specific settings
            if len(self.capabilities.devices) > 1:
                # Multi-GPU support (use primary GPU)
                args["main_gpu"] = 0
            
        elif self.capabilities.backend == GPUBackend.METAL:
            # Metal-specific settings
            args["f16_kv"] = True  # Use half precision for key/value cache
        
        return args
    
    def get_status_info(self) -> Dict[str, Any]:
        """
        Get current GPU status information for logging/UI.
        
        Returns:
            Dictionary with status information
        """
        if not self._detection_complete:
            self.detect_gpu_capabilities()
        
        return {
            "has_gpu": self.capabilities.has_gpu,
            "backend": self.capabilities.backend.value,
            "device_count": len(self.capabilities.devices),
            "total_vram_gb": round(self.capabilities.total_vram_mb / 1024, 1),
            "recommended_layers": self.capabilities.recommended_layers,
            "devices": [
                {
                    "name": gpu.name,
                    "memory_gb": round(gpu.memory_mb / 1024, 1),
                    "driver_version": gpu.driver_version
                }
                for gpu in self.capabilities.devices
            ]
        }
    
    def is_gpu_available(self) -> bool:
        """Check if GPU acceleration is available."""
        if not self._detection_complete:
            self.detect_gpu_capabilities()
        return self.capabilities.has_gpu
    
    def get_backend(self) -> GPUBackend:
        """Get the detected GPU backend."""
        if not self._detection_complete:
            self.detect_gpu_capabilities()
        return self.capabilities.backend
    
    def get_recommended_layers(self) -> int:
        """Get recommended number of GPU layers."""
        if not self._detection_complete:
            self.detect_gpu_capabilities()
        return self.capabilities.recommended_layers