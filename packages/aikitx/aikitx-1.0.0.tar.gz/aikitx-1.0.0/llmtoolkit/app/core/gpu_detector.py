"""
GPU Detector

This module provides comprehensive GPU detection and management capabilities.
It detects available GPUs, checks for required dependencies, and provides
recommendations for optimal GPU usage.
"""

import os
import sys
import logging
import platform
import subprocess
import json
import importlib
from typing import Dict, List, Optional, Tuple, Any, Union
from dataclasses import dataclass
from enum import Enum

class GPUBackend(Enum):
    """Supported GPU backends."""
    CUDA = "cuda"
    OPENCL = "opencl"
    VULKAN = "vulkan"
    DIRECTML = "directml"
    METAL = "metal"
    CPU = "cpu"

@dataclass
class GPUDevice:
    """Represents a detected GPU device."""
    id: int
    name: str
    memory_total: int  # MB
    memory_free: int   # MB
    backend: GPUBackend
    driver_version: str = ""
    compute_capability: str = ""
    is_available: bool = True
    performance_score: int = 0  # Relative performance score

@dataclass
class GPUCapabilities:
    """Represents overall GPU capabilities."""
    has_gpu: bool = False
    available_backends: List[GPUBackend] = None
    devices: List[GPUDevice] = None
    recommended_backend: GPUBackend = GPUBackend.CPU
    recommended_device: Optional[GPUDevice] = None
    dependencies_status: Dict[str, bool] = None
    
    def __post_init__(self):
        if self.available_backends is None:
            self.available_backends = []
        if self.devices is None:
            self.devices = []
        if self.dependencies_status is None:
            self.dependencies_status = {}

class GPUDetector:
    """
    Comprehensive GPU detection and management.
    
    This class detects available GPUs, checks dependencies, and provides
    recommendations for optimal GPU usage with llama.cpp.
    """
    
    def __init__(self, event_bus=None, config_manager=None):
        """
        Initialize the GPU detector.
        
        Args:
            event_bus: Optional event bus for publishing events
            config_manager: Optional configuration manager
        """
        self.logger = logging.getLogger("gguf_loader.gpu_detector")
        self.event_bus = event_bus
        self.config_manager = config_manager
        
        # Detection results
        self.capabilities = GPUCapabilities()
        
        # Performance scoring weights
        self.performance_weights = {
            GPUBackend.CUDA: 100,
            GPUBackend.METAL: 90,
            GPUBackend.VULKAN: 80,
            GPUBackend.OPENCL: 70,
            GPUBackend.DIRECTML: 60,
            GPUBackend.CPU: 10
        }
        
        self.logger.info("GPU detector initialized")
    
    def detect_gpu_capabilities(self) -> GPUCapabilities:
        """
        Detect all GPU capabilities and dependencies.
        
        Returns:
            GPUCapabilities object with detection results
        """
        self.logger.info("Starting comprehensive GPU detection")
        
        # Reset capabilities
        self.capabilities = GPUCapabilities()
        
        # Check dependencies first
        self._check_dependencies()
        
        # Detect CUDA
        if self.capabilities.dependencies_status.get("cuda", False):
            self._detect_cuda_devices()
        
        # Detect OpenCL
        if self.capabilities.dependencies_status.get("opencl", False):
            self._detect_opencl_devices()
        
        # Detect Vulkan
        if self.capabilities.dependencies_status.get("vulkan", False):
            self._detect_vulkan_devices()
        
        # Detect DirectML (Windows only)
        if platform.system() == "Windows" and self.capabilities.dependencies_status.get("directml", False):
            self._detect_directml_devices()
        
        # Detect Metal (macOS only)
        if platform.system() == "Darwin" and self.capabilities.dependencies_status.get("metal", False):
            self._detect_metal_devices()
        
        # Determine recommendations
        self._determine_recommendations()
        
        # Update overall GPU availability
        self.capabilities.has_gpu = len(self.capabilities.devices) > 0
        
        # Publish results
        if self.event_bus:
            self.event_bus.publish("gpu.capabilities_detected", self.capabilities)
        
        self.logger.info(f"GPU detection complete. Found {len(self.capabilities.devices)} GPU(s)")
        self.logger.info(f"Available backends: {[b.value for b in self.capabilities.available_backends]}")
        self.logger.info(f"Recommended backend: {self.capabilities.recommended_backend.value}")
        
        return self.capabilities
    
    def _check_dependencies(self):
        """Check for GPU backend dependencies."""
        self.logger.info("Checking GPU dependencies")
        
        dependencies = {
            "cuda": self._check_cuda_dependencies,
            "opencl": self._check_opencl_dependencies,
            "vulkan": self._check_vulkan_dependencies,
            "directml": self._check_directml_dependencies,
            "metal": self._check_metal_dependencies
        }
        
        for backend, check_func in dependencies.items():
            try:
                self.capabilities.dependencies_status[backend] = check_func()
                if self.capabilities.dependencies_status[backend]:
                    self.logger.info(f"{backend.upper()} dependencies available")
                else:
                    self.logger.debug(f"{backend.upper()} dependencies not available")
            except Exception as e:
                self.logger.debug(f"Error checking {backend} dependencies: {e}")
                self.capabilities.dependencies_status[backend] = False
    
    def _check_cuda_dependencies(self) -> bool:
        """Check CUDA dependencies."""
        try:
            # Check for nvidia-smi
            result = subprocess.run(["nvidia-smi", "--version"], 
                                  capture_output=True, text=True, timeout=5)
            if result.returncode != 0:
                return False
            
            # Check for CUDA runtime
            try:
                import llama_cpp
                # Check if llama-cpp-python was compiled with CUDA support
                # This is a heuristic check
                return hasattr(llama_cpp, 'GGML_USE_CUBLAS') or 'cuda' in str(llama_cpp.__file__).lower()
            except ImportError:
                return False
            
        except (subprocess.TimeoutExpired, FileNotFoundError):
            return False
    
    def _check_opencl_dependencies(self) -> bool:
        """Check OpenCL dependencies."""
        try:
            import pyopencl as cl
            # Try to get platforms to verify OpenCL is working
            platforms = cl.get_platforms()
            return len(platforms) > 0
        except ImportError:
            return False
        except Exception:
            return False
    
    def _check_vulkan_dependencies(self) -> bool:
        """Check Vulkan dependencies."""
        try:
            # Check for vulkaninfo
            result = subprocess.run(["vulkaninfo", "--summary"], 
                                  capture_output=True, text=True, timeout=10)
            return result.returncode == 0
        except (subprocess.TimeoutExpired, FileNotFoundError):
            return False
    
    def _check_directml_dependencies(self) -> bool:
        """Check DirectML dependencies (Windows only)."""
        if platform.system() != "Windows":
            return False
        
        try:
            # Check if DirectML is available
            # This is a placeholder - actual DirectML detection would require
            # specific DirectML Python bindings
            return False  # DirectML support not implemented yet
        except ImportError:
            return False
    
    def _check_metal_dependencies(self) -> bool:
        """Check Metal dependencies (macOS only)."""
        if platform.system() != "Darwin":
            return False
        
        try:
            # Check macOS version for Metal support
            import platform
            version = platform.mac_ver()[0]
            if version:
                major, minor = map(int, version.split('.')[:2])
                # Metal requires macOS 10.11+
                return major > 10 or (major == 10 and minor >= 11)
            return False
        except Exception:
            return False
    
    def _detect_cuda_devices(self):
        """Detect CUDA devices."""
        try:
            self.logger.info("Detecting CUDA devices")
            
            # Use nvidia-ml-py if available, otherwise fall back to nvidia-smi
            try:
                import pynvml
                pynvml.nvmlInit()
                device_count = pynvml.nvmlDeviceGetCount()
                
                for i in range(device_count):
                    handle = pynvml.nvmlDeviceGetHandleByIndex(i)
                    name = pynvml.nvmlDeviceGetName(handle).decode('utf-8')
                    
                    # Get memory info
                    mem_info = pynvml.nvmlDeviceGetMemoryInfo(handle)
                    memory_total = mem_info.total // (1024 * 1024)  # Convert to MB
                    memory_free = mem_info.free // (1024 * 1024)
                    
                    # Get driver version
                    driver_version = pynvml.nvmlSystemGetDriverVersion().decode('utf-8')
                    
                    # Get compute capability
                    try:
                        major = pynvml.nvmlDeviceGetCudaComputeCapability(handle)[0]
                        minor = pynvml.nvmlDeviceGetCudaComputeCapability(handle)[1]
                        compute_capability = f"{major}.{minor}"
                    except:
                        compute_capability = "Unknown"
                    
                    device = GPUDevice(
                        id=i,
                        name=name,
                        memory_total=memory_total,
                        memory_free=memory_free,
                        backend=GPUBackend.CUDA,
                        driver_version=driver_version,
                        compute_capability=compute_capability,
                        performance_score=self._calculate_cuda_performance_score(memory_total, compute_capability)
                    )
                    
                    self.capabilities.devices.append(device)
                    self.logger.info(f"Found CUDA device: {name} ({memory_total} MB)")
                
                if device_count > 0:
                    self.capabilities.available_backends.append(GPUBackend.CUDA)
                
            except ImportError:
                # Fall back to nvidia-smi
                self._detect_cuda_devices_nvidia_smi()
                
        except Exception as e:
            self.logger.error(f"Error detecting CUDA devices: {e}")
    
    def _detect_cuda_devices_nvidia_smi(self):
        """Detect CUDA devices using nvidia-smi."""
        try:
            cmd = ["nvidia-smi", "--query-gpu=index,name,memory.total,memory.free,driver_version", 
                   "--format=csv,noheader,nounits"]
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=10)
            
            if result.returncode == 0 and result.stdout:
                for line in result.stdout.strip().split('\n'):
                    parts = [p.strip() for p in line.split(',')]
                    if len(parts) >= 5:
                        device_id = int(parts[0])
                        name = parts[1]
                        memory_total = int(parts[2])
                        memory_free = int(parts[3])
                        driver_version = parts[4]
                        
                        device = GPUDevice(
                            id=device_id,
                            name=name,
                            memory_total=memory_total,
                            memory_free=memory_free,
                            backend=GPUBackend.CUDA,
                            driver_version=driver_version,
                            performance_score=self._calculate_cuda_performance_score(memory_total, "Unknown")
                        )
                        
                        self.capabilities.devices.append(device)
                        self.logger.info(f"Found CUDA device: {name} ({memory_total} MB)")
                
                if self.capabilities.devices:
                    self.capabilities.available_backends.append(GPUBackend.CUDA)
                    
        except Exception as e:
            self.logger.debug(f"nvidia-smi detection failed: {e}")
    
    def _detect_opencl_devices(self):
        """Detect OpenCL devices."""
        try:
            import pyopencl as cl
            
            self.logger.info("Detecting OpenCL devices")
            
            device_id = 0
            for platform in cl.get_platforms():
                for device in platform.get_devices():
                    if device.type == cl.device_type.GPU:
                        name = device.name.strip()
                        memory_total = device.global_mem_size // (1024 * 1024)  # Convert to MB
                        
                        gpu_device = GPUDevice(
                            id=device_id,
                            name=name,
                            memory_total=memory_total,
                            memory_free=memory_total,  # OpenCL doesn't provide free memory easily
                            backend=GPUBackend.OPENCL,
                            driver_version=device.driver_version,
                            performance_score=self._calculate_opencl_performance_score(memory_total)
                        )
                        
                        self.capabilities.devices.append(gpu_device)
                        self.logger.info(f"Found OpenCL device: {name} ({memory_total} MB)")
                        device_id += 1
            
            if any(d.backend == GPUBackend.OPENCL for d in self.capabilities.devices):
                self.capabilities.available_backends.append(GPUBackend.OPENCL)
                
        except Exception as e:
            self.logger.debug(f"OpenCL detection failed: {e}")
    
    def _detect_vulkan_devices(self):
        """Detect Vulkan devices."""
        try:
            self.logger.info("Detecting Vulkan devices")
            
            cmd = ["vulkaninfo", "--summary"]
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=10)
            
            if result.returncode == 0 and result.stdout:
                # Parse vulkaninfo output
                lines = result.stdout.split('\n')
                device_id = 0
                
                for i, line in enumerate(lines):
                    if 'GPU' in line and 'deviceName' in line:
                        # Extract device name
                        name_match = line.split('=')
                        if len(name_match) > 1:
                            name = name_match[1].strip()
                            
                            # Try to find memory info in nearby lines
                            memory_total = 0
                            for j in range(max(0, i-10), min(len(lines), i+10)):
                                if 'heap' in lines[j].lower() and 'size' in lines[j].lower():
                                    try:
                                        # Extract memory size (this is approximate)
                                        import re
                                        numbers = re.findall(r'\d+', lines[j])
                                        if numbers:
                                            memory_total = int(numbers[0]) // (1024 * 1024)  # Convert to MB
                                            break
                                    except:
                                        pass
                            
                            if memory_total == 0:
                                memory_total = 1024  # Default fallback
                            
                            device = GPUDevice(
                                id=device_id,
                                name=name,
                                memory_total=memory_total,
                                memory_free=memory_total,
                                backend=GPUBackend.VULKAN,
                                performance_score=self._calculate_vulkan_performance_score(memory_total)
                            )
                            
                            self.capabilities.devices.append(device)
                            self.logger.info(f"Found Vulkan device: {name} ({memory_total} MB)")
                            device_id += 1
                
                if any(d.backend == GPUBackend.VULKAN for d in self.capabilities.devices):
                    self.capabilities.available_backends.append(GPUBackend.VULKAN)
                    
        except Exception as e:
            self.logger.debug(f"Vulkan detection failed: {e}")
    
    def _detect_directml_devices(self):
        """Detect DirectML devices (Windows only)."""
        # Placeholder for DirectML detection
        # DirectML support would require specific implementation
        self.logger.debug("DirectML detection not implemented yet")
    
    def _detect_metal_devices(self):
        """Detect Metal devices (macOS only)."""
        try:
            self.logger.info("Detecting Metal devices")
            
            # Use system_profiler to get GPU info
            cmd = ["system_profiler", "SPDisplaysDataType", "-json"]
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=10)
            
            if result.returncode == 0 and result.stdout:
                data = json.loads(result.stdout)
                device_id = 0
                
                for display in data.get('SPDisplaysDataType', []):
                    if 'sppci_model' in display:
                        name = display['sppci_model']
                        
                        # Extract VRAM if available
                        memory_total = 1024  # Default
                        if 'sppci_vram' in display:
                            vram_str = display['sppci_vram']
                            if 'MB' in vram_str:
                                memory_total = int(vram_str.replace(' MB', ''))
                            elif 'GB' in vram_str:
                                memory_total = int(float(vram_str.replace(' GB', '')) * 1024)
                        
                        device = GPUDevice(
                            id=device_id,
                            name=name,
                            memory_total=memory_total,
                            memory_free=memory_total,
                            backend=GPUBackend.METAL,
                            performance_score=self._calculate_metal_performance_score(memory_total)
                        )
                        
                        self.capabilities.devices.append(device)
                        self.logger.info(f"Found Metal device: {name} ({memory_total} MB)")
                        device_id += 1
                
                if any(d.backend == GPUBackend.METAL for d in self.capabilities.devices):
                    self.capabilities.available_backends.append(GPUBackend.METAL)
                    
        except Exception as e:
            self.logger.debug(f"Metal detection failed: {e}")
    
    def _calculate_cuda_performance_score(self, memory_mb: int, compute_capability: str) -> int:
        """Calculate performance score for CUDA device."""
        base_score = self.performance_weights[GPUBackend.CUDA]
        
        # Memory bonus (more memory = better)
        memory_bonus = min(memory_mb // 1024, 20)  # Up to 20 points for memory
        
        # Compute capability bonus
        cc_bonus = 0
        if compute_capability != "Unknown":
            try:
                cc_float = float(compute_capability)
                if cc_float >= 8.0:
                    cc_bonus = 20
                elif cc_float >= 7.0:
                    cc_bonus = 15
                elif cc_float >= 6.0:
                    cc_bonus = 10
                elif cc_float >= 5.0:
                    cc_bonus = 5
            except:
                pass
        
        return base_score + memory_bonus + cc_bonus
    
    def _calculate_opencl_performance_score(self, memory_mb: int) -> int:
        """Calculate performance score for OpenCL device."""
        base_score = self.performance_weights[GPUBackend.OPENCL]
        memory_bonus = min(memory_mb // 1024, 15)  # Up to 15 points for memory
        return base_score + memory_bonus
    
    def _calculate_vulkan_performance_score(self, memory_mb: int) -> int:
        """Calculate performance score for Vulkan device."""
        base_score = self.performance_weights[GPUBackend.VULKAN]
        memory_bonus = min(memory_mb // 1024, 15)  # Up to 15 points for memory
        return base_score + memory_bonus
    
    def _calculate_metal_performance_score(self, memory_mb: int) -> int:
        """Calculate performance score for Metal device."""
        base_score = self.performance_weights[GPUBackend.METAL]
        memory_bonus = min(memory_mb // 1024, 15)  # Up to 15 points for memory
        return base_score + memory_bonus
    
    def _determine_recommendations(self):
        """Determine recommended backend and device."""
        if not self.capabilities.devices:
            self.capabilities.recommended_backend = GPUBackend.CPU
            return
        
        # Sort devices by performance score
        sorted_devices = sorted(self.capabilities.devices, 
                              key=lambda d: d.performance_score, 
                              reverse=True)
        
        # Get the best device
        best_device = sorted_devices[0]
        self.capabilities.recommended_backend = best_device.backend
        self.capabilities.recommended_device = best_device
        
        self.logger.info(f"Recommended: {best_device.backend.value} - {best_device.name}")
    
    def get_user_preference(self) -> GPUBackend:
        """
        Get user's preferred processing unit from configuration.
        
        Returns:
            User's preferred backend
        """
        if not self.config_manager:
            return self.capabilities.recommended_backend
        
        processing_unit = self.config_manager.get_value("processing_unit", "auto")
        
        if processing_unit == "cpu":
            return GPUBackend.CPU
        elif processing_unit == "gpu":
            # Return the recommended GPU backend if available
            if self.capabilities.has_gpu:
                return self.capabilities.recommended_backend
            else:
                return GPUBackend.CPU
        else:  # auto
            return self.capabilities.recommended_backend
    
    def get_optimal_settings(self, backend: GPUBackend = None, device_id: int = None) -> Dict[str, Any]:
        """
        Get optimal settings for the specified backend and device.
        
        Args:
            backend: GPU backend to use (None for user preference)
            device_id: Specific device ID (None for best device)
            
        Returns:
            Dictionary of optimal settings
        """
        if backend is None:
            backend = self.get_user_preference()
        
        settings = {
            "backend": backend.value,
            "device_id": device_id or 0,
            "gpu_layers": 0,
            "threads": 4,
            "batch_size": 1,
            "context_size": 2048
        }
        
        if backend == GPUBackend.CPU:
            settings.update({
                "threads": min(os.cpu_count() or 4, 8),
                "gpu_layers": 0
            })
        else:
            # Find the appropriate device
            target_device = None
            if device_id is not None:
                target_device = next((d for d in self.capabilities.devices 
                                    if d.backend == backend and d.id == device_id), None)
            else:
                # Use the best device for this backend
                backend_devices = [d for d in self.capabilities.devices if d.backend == backend]
                if backend_devices:
                    target_device = max(backend_devices, key=lambda d: d.performance_score)
            
            if target_device:
                settings.update({
                    "device_id": target_device.id,
                    "gpu_layers": self._calculate_optimal_gpu_layers(target_device),
                    "threads": 4  # Fewer CPU threads when using GPU
                })
        
        return settings
    
    def _calculate_optimal_gpu_layers(self, device: GPUDevice) -> int:
        """Calculate optimal number of GPU layers for a device."""
        memory_gb = device.memory_total / 1024
        
        if memory_gb >= 24:
            return 50  # High-end GPU
        elif memory_gb >= 12:
            return 40  # Mid-range GPU
        elif memory_gb >= 8:
            return 30  # Entry-level dedicated GPU
        elif memory_gb >= 4:
            return 20  # Low-end GPU or integrated
        else:
            return 10  # Very limited GPU
    
    def install_gpu_dependencies(self, backend: GPUBackend) -> bool:
        """
        Install dependencies for the specified GPU backend.
        
        Args:
            backend: GPU backend to install dependencies for
            
        Returns:
            True if installation was successful
        """
        self.logger.info(f"Installing dependencies for {backend.value}")
        
        try:
            if backend == GPUBackend.CUDA:
                return self._install_cuda_dependencies()
            elif backend == GPUBackend.OPENCL:
                return self._install_opencl_dependencies()
            elif backend == GPUBackend.VULKAN:
                return self._install_vulkan_dependencies()
            elif backend == GPUBackend.DIRECTML:
                return self._install_directml_dependencies()
            elif backend == GPUBackend.METAL:
                return self._install_metal_dependencies()
            else:
                self.logger.warning(f"Dependency installation not implemented for {backend.value}")
                return False
        except Exception as e:
            self.logger.error(f"Failed to install {backend.value} dependencies: {e}")
            return False
    
    def _install_cuda_dependencies(self) -> bool:
        """Install CUDA dependencies."""
        try:
            # Install CUDA-enabled llama-cpp-python
            cmd = [sys.executable, "-m", "pip", "install", "--upgrade", 
                   "llama-cpp-python[cuda]", "--force-reinstall", "--no-cache-dir"]
            
            self.logger.info("Installing CUDA-enabled llama-cpp-python...")
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=300)
            
            if result.returncode == 0:
                self.logger.info("CUDA dependencies installed successfully")
                return True
            else:
                self.logger.error(f"CUDA installation failed: {result.stderr}")
                return False
                
        except Exception as e:
            self.logger.error(f"Error installing CUDA dependencies: {e}")
            return False
    
    def _install_opencl_dependencies(self) -> bool:
        """Install OpenCL dependencies."""
        try:
            # Install PyOpenCL
            cmd = [sys.executable, "-m", "pip", "install", "pyopencl"]
            
            self.logger.info("Installing PyOpenCL...")
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=120)
            
            if result.returncode == 0:
                self.logger.info("OpenCL dependencies installed successfully")
                return True
            else:
                self.logger.error(f"OpenCL installation failed: {result.stderr}")
                return False
                
        except Exception as e:
            self.logger.error(f"Error installing OpenCL dependencies: {e}")
            return False
    
    def _install_vulkan_dependencies(self) -> bool:
        """Install Vulkan dependencies."""
        # Vulkan support would require specific llama.cpp compilation
        self.logger.warning("Vulkan dependency installation not implemented")
        return False
    
    def _install_directml_dependencies(self) -> bool:
        """Install DirectML dependencies."""
        if platform.system() != "Windows":
            self.logger.error("DirectML is only available on Windows")
            return False
        
        try:
            # DirectML support would require specific implementation
            self.logger.warning("DirectML dependency installation not implemented")
            return False
        except Exception as e:
            self.logger.error(f"Error installing DirectML dependencies: {e}")
            return False
    
    def _install_metal_dependencies(self) -> bool:
        """Install Metal dependencies."""
        if platform.system() != "Darwin":
            self.logger.error("Metal is only available on macOS")
            return False
        
        try:
            # Metal support is built into macOS, no additional installation needed
            self.logger.info("Metal support is built into macOS")
            return True
        except Exception as e:
            self.logger.error(f"Error checking Metal dependencies: {e}")
            return False
    
    def get_installation_instructions(self, backend: GPUBackend) -> str:
        """
        Get installation instructions for the specified backend.
        
        Args:
            backend: GPU backend
            
        Returns:
            Human-readable installation instructions
        """
        if backend == GPUBackend.CUDA:
            return """To enable CUDA support:
1. Install NVIDIA GPU drivers
2. Install CUDA Toolkit (11.8 or later recommended)
3. The application will automatically install CUDA-enabled llama-cpp-python"""
        
        elif backend == GPUBackend.OPENCL:
            return """To enable OpenCL support:
1. Install GPU drivers with OpenCL support
2. The application will automatically install PyOpenCL"""
        
        elif backend == GPUBackend.VULKAN:
            return """To enable Vulkan support:
1. Install GPU drivers with Vulkan support
2. Install Vulkan SDK
3. Vulkan support requires custom llama.cpp compilation"""
        
        elif backend == GPUBackend.DIRECTML:
            return """To enable DirectML support:
1. Windows 10 version 1903 or later
2. DirectML support requires custom implementation"""
        
        elif backend == GPUBackend.METAL:
            return """Metal support is automatically available on macOS 10.11+
No additional installation required."""
        
        else:
            return "No additional dependencies required for CPU processing."