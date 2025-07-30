"""
Hardware Detection and Management Utilities

This module provides utilities for detecting available hardware (GPUs, CPUs)
and determining optimal settings for different model backends.
"""

import logging
import platform
import subprocess
import psutil
import json
from typing import Dict, List, Optional, Tuple, Any
from dataclasses import dataclass
from pathlib import Path

from .model_backends import HardwareInfo, HardwareType, BackendType


@dataclass
class GPUDevice:
    """Information about a GPU device."""
    id: int
    name: str
    vendor: str  # nvidia, amd, intel
    memory_mb: int
    driver_version: str
    compute_capability: Optional[str] = None
    supports_cuda: bool = False
    supports_rocm: bool = False
    supports_opencl: bool = False
    supports_vulkan: bool = False
    supports_metal: bool = False


class HardwareDetector:
    """Detects available hardware and recommends optimal settings."""
    
    def __init__(self):
        """Initialize the hardware detector."""
        self.logger = logging.getLogger("hardware.detector")
        self._gpu_cache = None
        self._cpu_cache = None
        self._system_cache = None
    
    def detect_gpus(self) -> List[GPUDevice]:
        """
        Detect available GPUs and their capabilities.
        
        Returns:
            List of GPUDevice objects
        """
        if self._gpu_cache is not None:
            return self._gpu_cache
        
        gpus = []
        
        # Try NVIDIA GPUs first
        nvidia_gpus = self._detect_nvidia_gpus()
        gpus.extend(nvidia_gpus)
        
        # Try AMD GPUs
        amd_gpus = self._detect_amd_gpus()
        gpus.extend(amd_gpus)
        
        # Try Intel GPUs
        intel_gpus = self._detect_intel_gpus()
        gpus.extend(intel_gpus)
        
        self._gpu_cache = gpus
        self.logger.info(f"Detected {len(gpus)} GPU(s)")
        
        return gpus
    
    def _detect_nvidia_gpus(self) -> List[GPUDevice]:
        """Detect NVIDIA GPUs using nvidia-smi."""
        gpus = []
        
        try:
            # Try to run nvidia-smi
            result = subprocess.run([
                'nvidia-smi', '--query-gpu=index,name,memory.total,driver_version',
                '--format=csv,noheader,nounits'
            ], capture_output=True, text=True, timeout=10)
            
            if result.returncode == 0:
                lines = result.stdout.strip().split('\n')
                for line in lines:
                    if line.strip():
                        parts = [p.strip() for p in line.split(',')]
                        if len(parts) >= 4:
                            gpu = GPUDevice(
                                id=int(parts[0]),
                                name=parts[1],
                                vendor="nvidia",
                                memory_mb=int(parts[2]),
                                driver_version=parts[3],
                                supports_cuda=True,
                                supports_opencl=True,
                                supports_vulkan=True
                            )
                            
                            # Try to get compute capability
                            gpu.compute_capability = self._get_cuda_compute_capability(gpu.id)
                            
                            gpus.append(gpu)
                            self.logger.info(f"Found NVIDIA GPU: {gpu.name} ({gpu.memory_mb}MB)")
            
        except (subprocess.TimeoutExpired, subprocess.CalledProcessError, FileNotFoundError) as e:
            self.logger.debug(f"nvidia-smi not available or failed: {e}")
        except Exception as e:
            self.logger.warning(f"Error detecting NVIDIA GPUs: {e}")
        
        return gpus
    
    def _detect_amd_gpus(self) -> List[GPUDevice]:
        """Detect AMD GPUs using rocm-smi or system information."""
        gpus = []
        
        try:
            # Try rocm-smi first
            result = subprocess.run([
                'rocm-smi', '--showid', '--showproductname', '--showmeminfo', 'vram'
            ], capture_output=True, text=True, timeout=10)
            
            if result.returncode == 0:
                # Parse rocm-smi output
                lines = result.stdout.strip().split('\n')
                current_gpu = None
                
                for line in lines:
                    line = line.strip()
                    if 'GPU[' in line and ']:' in line:
                        # Extract GPU ID
                        gpu_id = int(line.split('[')[1].split(']')[0])
                        current_gpu = {'id': gpu_id}
                    elif 'Card series:' in line and current_gpu:
                        current_gpu['name'] = line.split(':', 1)[1].strip()
                    elif 'Total Memory (B):' in line and current_gpu:
                        memory_bytes = int(line.split(':', 1)[1].strip())
                        current_gpu['memory_mb'] = memory_bytes // (1024 * 1024)
                        
                        # Create GPU object
                        gpu = GPUDevice(
                            id=current_gpu['id'],
                            name=current_gpu.get('name', 'AMD GPU'),
                            vendor="amd",
                            memory_mb=current_gpu['memory_mb'],
                            driver_version="unknown",
                            supports_rocm=True,
                            supports_opencl=True,
                            supports_vulkan=True
                        )
                        gpus.append(gpu)
                        self.logger.info(f"Found AMD GPU: {gpu.name} ({gpu.memory_mb}MB)")
                        current_gpu = None
            
        except (subprocess.TimeoutExpired, subprocess.CalledProcessError, FileNotFoundError):
            self.logger.debug("rocm-smi not available, trying alternative detection")
            
            # Fallback: try to detect AMD GPUs through system info
            try:
                if platform.system() == "Windows":
                    # Use wmic on Windows
                    result = subprocess.run([
                        'wmic', 'path', 'win32_VideoController', 'get', 'name,AdapterRAM'
                    ], capture_output=True, text=True, timeout=10)
                    
                    if result.returncode == 0:
                        lines = result.stdout.strip().split('\n')
                        gpu_id = 0
                        for line in lines[1:]:  # Skip header
                            if 'AMD' in line or 'Radeon' in line:
                                parts = line.strip().split()
                                if len(parts) >= 2:
                                    memory_bytes = int(parts[0]) if parts[0].isdigit() else 0
                                    name = ' '.join(parts[1:])
                                    
                                    gpu = GPUDevice(
                                        id=gpu_id,
                                        name=name,
                                        vendor="amd",
                                        memory_mb=memory_bytes // (1024 * 1024) if memory_bytes > 0 else 0,
                                        driver_version="unknown",
                                        supports_rocm=True,
                                        supports_opencl=True,
                                        supports_vulkan=True
                                    )
                                    gpus.append(gpu)
                                    gpu_id += 1
                                    self.logger.info(f"Found AMD GPU: {gpu.name}")
                
            except Exception as e:
                self.logger.debug(f"Alternative AMD GPU detection failed: {e}")
        
        except Exception as e:
            self.logger.warning(f"Error detecting AMD GPUs: {e}")
        
        return gpus
    
    def _detect_intel_gpus(self) -> List[GPUDevice]:
        """Detect Intel GPUs."""
        gpus = []
        
        try:
            if platform.system() == "Windows":
                # Use wmic on Windows
                result = subprocess.run([
                    'wmic', 'path', 'win32_VideoController', 'get', 'name,AdapterRAM'
                ], capture_output=True, text=True, timeout=10)
                
                if result.returncode == 0:
                    lines = result.stdout.strip().split('\n')
                    gpu_id = 0
                    for line in lines[1:]:  # Skip header
                        if 'Intel' in line and ('Graphics' in line or 'Iris' in line or 'UHD' in line):
                            parts = line.strip().split()
                            if len(parts) >= 2:
                                memory_bytes = int(parts[0]) if parts[0].isdigit() else 0
                                name = ' '.join(parts[1:])
                                
                                gpu = GPUDevice(
                                    id=gpu_id,
                                    name=name,
                                    vendor="intel",
                                    memory_mb=memory_bytes // (1024 * 1024) if memory_bytes > 0 else 0,
                                    driver_version="unknown",
                                    supports_opencl=True,
                                    supports_vulkan=True
                                )
                                gpus.append(gpu)
                                gpu_id += 1
                                self.logger.info(f"Found Intel GPU: {gpu.name}")
            
            elif platform.system() == "Linux":
                # Try to detect Intel GPUs on Linux
                try:
                    result = subprocess.run([
                        'lspci', '-nn'
                    ], capture_output=True, text=True, timeout=10)
                    
                    if result.returncode == 0:
                        lines = result.stdout.strip().split('\n')
                        gpu_id = 0
                        for line in lines:
                            if 'VGA' in line and 'Intel' in line:
                                # Extract GPU name
                                name_start = line.find('Intel')
                                if name_start != -1:
                                    name = line[name_start:].split('[')[0].strip()
                                    
                                    gpu = GPUDevice(
                                        id=gpu_id,
                                        name=name,
                                        vendor="intel",
                                        memory_mb=0,  # Hard to detect on Linux
                                        driver_version="unknown",
                                        supports_opencl=True,
                                        supports_vulkan=True
                                    )
                                    gpus.append(gpu)
                                    gpu_id += 1
                                    self.logger.info(f"Found Intel GPU: {gpu.name}")
                
                except Exception as e:
                    self.logger.debug(f"lspci detection failed: {e}")
        
        except Exception as e:
            self.logger.warning(f"Error detecting Intel GPUs: {e}")
        
        return gpus
    
    def _get_cuda_compute_capability(self, gpu_id: int) -> Optional[str]:
        """Get CUDA compute capability for a GPU."""
        try:
            # Try to use nvidia-ml-py if available
            import pynvml
            pynvml.nvmlInit()
            handle = pynvml.nvmlDeviceGetHandleByIndex(gpu_id)
            major, minor = pynvml.nvmlDeviceGetCudaComputeCapability(handle)
            return f"{major}.{minor}"
        except ImportError:
            self.logger.debug("pynvml not available for compute capability detection")
        except Exception as e:
            self.logger.debug(f"Error getting compute capability: {e}")
        
        return None
    
    def detect_cpu_info(self) -> Dict[str, Any]:
        """
        Detect CPU information.
        
        Returns:
            Dictionary with CPU information
        """
        if self._cpu_cache is not None:
            return self._cpu_cache
        
        try:
            cpu_info = {
                'cores': psutil.cpu_count(logical=False),
                'threads': psutil.cpu_count(logical=True),
                'frequency': psutil.cpu_freq().current if psutil.cpu_freq() else 0,
                'architecture': platform.machine(),
                'processor': platform.processor()
            }
            
            self._cpu_cache = cpu_info
            self.logger.info(f"CPU: {cpu_info['cores']} cores, {cpu_info['threads']} threads")
            
            return cpu_info
            
        except Exception as e:
            self.logger.warning(f"Error detecting CPU info: {e}")
            return {
                'cores': 1,
                'threads': 1,
                'frequency': 0,
                'architecture': 'unknown',
                'processor': 'unknown'
            }
    
    def detect_system_memory(self) -> Dict[str, int]:
        """
        Detect system memory information.
        
        Returns:
            Dictionary with memory information in MB
        """
        if self._system_cache is not None:
            return self._system_cache
        
        try:
            memory = psutil.virtual_memory()
            memory_info = {
                'total': memory.total // (1024 * 1024),
                'available': memory.available // (1024 * 1024),
                'used': memory.used // (1024 * 1024),
                'percent': memory.percent
            }
            
            self._system_cache = memory_info
            self.logger.info(f"System RAM: {memory_info['total']}MB total, {memory_info['available']}MB available")
            
            return memory_info
            
        except Exception as e:
            self.logger.warning(f"Error detecting system memory: {e}")
            return {
                'total': 8192,  # Default to 8GB
                'available': 4096,
                'used': 4096,
                'percent': 50.0
            }
    
    def get_hardware_info(self) -> HardwareInfo:
        """
        Get comprehensive hardware information.
        
        Returns:
            HardwareInfo object with all detected hardware
        """
        gpus = self.detect_gpus()
        cpu_info = self.detect_cpu_info()
        memory_info = self.detect_system_memory()
        
        # Convert GPUs to dict format
        gpu_devices = []
        total_vram = 0
        supported_hardware = [HardwareType.CPU]  # CPU is always supported
        
        for gpu in gpus:
            gpu_dict = {
                'id': gpu.id,
                'name': gpu.name,
                'vendor': gpu.vendor,
                'memory_mb': gpu.memory_mb,
                'driver_version': gpu.driver_version,
                'compute_capability': gpu.compute_capability,
                'supports_cuda': gpu.supports_cuda,
                'supports_rocm': gpu.supports_rocm,
                'supports_opencl': gpu.supports_opencl,
                'supports_vulkan': gpu.supports_vulkan,
                'supports_metal': gpu.supports_metal
            }
            gpu_devices.append(gpu_dict)
            total_vram += gpu.memory_mb
            
            # Add supported hardware types
            if gpu.supports_cuda and HardwareType.CUDA not in supported_hardware:
                supported_hardware.append(HardwareType.CUDA)
            if gpu.supports_rocm and HardwareType.ROCM not in supported_hardware:
                supported_hardware.append(HardwareType.ROCM)
            if gpu.supports_opencl and HardwareType.OPENCL not in supported_hardware:
                supported_hardware.append(HardwareType.OPENCL)
            if gpu.supports_vulkan and HardwareType.VULKAN not in supported_hardware:
                supported_hardware.append(HardwareType.VULKAN)
            if gpu.supports_metal and HardwareType.METAL not in supported_hardware:
                supported_hardware.append(HardwareType.METAL)
        
        # Determine recommended backend
        recommended_backend = self._recommend_backend(gpus, memory_info)
        
        return HardwareInfo(
            gpu_count=len(gpus),
            gpu_devices=gpu_devices,
            total_vram=total_vram,
            cpu_cores=cpu_info['cores'],
            total_ram=memory_info['total'],
            recommended_backend=recommended_backend,
            supported_hardware=supported_hardware
        )
    
    def _recommend_backend(self, gpus: List[GPUDevice], memory_info: Dict[str, int]) -> str:
        """Recommend the best backend based on available hardware."""
        # If we have NVIDIA GPUs with good VRAM, recommend ctransformers
        nvidia_gpus = [gpu for gpu in gpus if gpu.vendor == "nvidia" and gpu.memory_mb >= 4096]
        if nvidia_gpus:
            return BackendType.CTRANSFORMERS.value
        
        # If we have AMD GPUs with ROCm support, recommend ctransformers
        amd_gpus = [gpu for gpu in gpus if gpu.vendor == "amd" and gpu.supports_rocm]
        if amd_gpus:
            return BackendType.CTRANSFORMERS.value
        
        # If we have any GPU, try transformers
        if gpus:
            return BackendType.TRANSFORMERS.value
        
        # If we have lots of RAM, use llamafile
        if memory_info['total'] >= 16384:  # 16GB+
            return BackendType.LLAMAFILE.value
        
        # Default to ctransformers (CPU mode)
        return BackendType.CTRANSFORMERS.value
    
    def get_optimal_settings(self, backend: str, model_size_mb: int) -> Dict[str, Any]:
        """
        Get optimal settings for the given backend and model size.
        
        Args:
            backend: Backend name
            model_size_mb: Model size in MB
            
        Returns:
            Dictionary with optimal settings
        """
        gpus = self.detect_gpus()
        memory_info = self.detect_system_memory()
        
        settings = {
            'gpu_enabled': len(gpus) > 0,
            'gpu_layers': -1,  # Auto-detect
            'context_size': 4096,
            'batch_size': 512,
            'threads': -1  # Auto-detect
        }
        
        # Adjust based on available VRAM
        if gpus:
            max_vram = max(gpu.memory_mb for gpu in gpus)
            
            # Estimate GPU layers based on VRAM and model size
            if max_vram >= model_size_mb * 1.5:  # Enough VRAM for full GPU
                settings['gpu_layers'] = -1  # All layers
            elif max_vram >= model_size_mb:  # Partial GPU
                settings['gpu_layers'] = int((max_vram / model_size_mb) * 32)  # Estimate
            else:  # Not enough VRAM
                settings['gpu_enabled'] = False
        
        # Adjust context size based on available memory
        available_memory = memory_info['available']
        if available_memory < 4096:  # Less than 4GB available
            settings['context_size'] = 2048
        elif available_memory >= 8192:  # 8GB+ available
            settings['context_size'] = 8192
        
        return settings
    
    def benchmark_backend(self, backend_name: str, model_path: str) -> Dict[str, float]:
        """
        Benchmark a backend's performance.
        
        Args:
            backend_name: Name of backend to benchmark
            model_path: Path to model for benchmarking
            
        Returns:
            Dictionary with benchmark results
        """
        # This is a placeholder for future implementation
        # In a real implementation, we would:
        # 1. Load the model with the backend
        # 2. Run inference tests
        # 3. Measure loading time, inference speed, memory usage
        # 4. Return comprehensive metrics
        
        return {
            'load_time': 0.0,
            'inference_speed': 0.0,
            'memory_usage': 0,
            'tokens_per_second': 0.0
        }
    
    def clear_cache(self):
        """Clear cached hardware information."""
        self._gpu_cache = None
        self._cpu_cache = None
        self._system_cache = None
        self.logger.info("Hardware detection cache cleared")