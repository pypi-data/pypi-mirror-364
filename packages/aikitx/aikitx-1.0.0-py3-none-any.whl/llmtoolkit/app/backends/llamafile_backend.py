"""
Llamafile Backend Implementation

This module implements the llamafile backend for GGUF model loading
and inference using external llamafile process execution.

Features:
- External llamafile process management
- Automatic GPU detection and optimization
- Process communication and lifecycle management
- Comprehensive error handling for external process failures
- Cross-platform support (Windows, Linux, macOS)
"""

import logging
import time
import os
import platform
import subprocess
import tempfile
import shutil
import json
import threading
import queue
import signal
from pathlib import Path
from typing import Dict, Any, Optional, Tuple, List, Union
import requests
import psutil

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from core.model_backends import (
    ModelBackend, BackendConfig, HardwareInfo, LoadingResult, 
    GenerationConfig, HardwareType, BackendError, InstallationError, 
    HardwareError, ModelLoadingError
)


class LlamafileBackend(ModelBackend):
    """
    Llamafile backend implementation with external process management.
    
    This backend provides:
    - External llamafile process execution
    - Automatic GPU detection and optimization
    - HTTP API communication with llamafile server
    - Process lifecycle management
    - Comprehensive error handling
    """
    
    # Default llamafile server configuration
    DEFAULT_HOST = "127.0.0.1"
    DEFAULT_PORT = 8080
    DEFAULT_TIMEOUT = 30
    
    # Llamafile executable names by platform
    LLAMAFILE_EXECUTABLES = {
        'Windows': ['llamafile.exe', 'llamafile'],
        'Linux': ['llamafile', 'llamafile.bin'],
        'Darwin': ['llamafile', 'llamafile.bin']
    }
    
    # GGUF file extensions
    GGUF_EXTENSIONS = {'.gguf', '.ggml', '.bin'}
    
    def __init__(self, config: BackendConfig):
        """Initialize the llamafile backend."""
        super().__init__(config)
        self.process = None
        self.server_host = self.DEFAULT_HOST
        self.server_port = self._find_available_port()
        self.server_url = f"http://{self.server_host}:{self.server_port}"
        self.llamafile_path = None
        self._model_type = None
        self._hardware_acceleration = None
        self._process_monitor_thread = None
        self._stop_monitoring = threading.Event()
        self._generation_stats = {
            'total_tokens': 0,
            'total_time': 0.0,
            'average_tokens_per_second': 0.0
        }
        
        # Find llamafile executable
        self._find_llamafile_executable()
        
    def _find_available_port(self, start_port: int = 8080) -> int:
        """Find an available port for the llamafile server."""
        import socket
        
        for port in range(start_port, start_port + 100):
            try:
                with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                    s.bind((self.DEFAULT_HOST, port))
                    return port
            except OSError:
                continue
        
        # Fallback to default port if no available port found
        return self.DEFAULT_PORT
    
    def _find_llamafile_executable(self):
        """Find llamafile executable in system PATH or common locations."""
        system = platform.system()
        executables = self.LLAMAFILE_EXECUTABLES.get(system, ['llamafile'])
        
        # Check system PATH first
        for exe_name in executables:
            if shutil.which(exe_name):
                self.llamafile_path = shutil.which(exe_name)
                self.logger.info(f"Found llamafile executable: {self.llamafile_path}")
                return
        
        # Check common installation directories
        common_paths = self._get_common_llamafile_paths()
        for path in common_paths:
            for exe_name in executables:
                exe_path = Path(path) / exe_name
                if exe_path.exists() and exe_path.is_file():
                    self.llamafile_path = str(exe_path)
                    self.logger.info(f"Found llamafile executable: {self.llamafile_path}")
                    return
        
        self.logger.warning("Llamafile executable not found in PATH or common locations")
    
    def _get_common_llamafile_paths(self) -> List[str]:
        """Get common paths where llamafile might be installed."""
        system = platform.system()
        paths = []
        
        if system == "Windows":
            paths.extend([
                os.path.expanduser("~/AppData/Local/llamafile"),
                "C:/Program Files/llamafile",
                "C:/llamafile",
                os.path.join(os.getcwd(), "llamafile")
            ])
        elif system == "Linux":
            paths.extend([
                "/usr/local/bin",
                "/usr/bin",
                os.path.expanduser("~/.local/bin"),
                os.path.expanduser("~/llamafile"),
                os.path.join(os.getcwd(), "llamafile")
            ])
        elif system == "Darwin":  # macOS
            paths.extend([
                "/usr/local/bin",
                "/opt/homebrew/bin",
                os.path.expanduser("~/Applications/llamafile"),
                os.path.expanduser("~/llamafile"),
                os.path.join(os.getcwd(), "llamafile")
            ])
        
        return paths
    
    def is_available(self) -> Tuple[bool, Optional[str]]:
        """
        Check if llamafile is available and properly configured.
        
        Returns:
            Tuple of (is_available, error_message)
        """
        try:
            # Check if llamafile executable exists
            if not self.llamafile_path:
                return False, "Llamafile executable not found. Please install llamafile or add it to PATH."
            
            if not os.path.exists(self.llamafile_path):
                return False, f"Llamafile executable not found at: {self.llamafile_path}"
            
            # Check if executable is actually executable
            if not os.access(self.llamafile_path, os.X_OK):
                return False, f"Llamafile executable is not executable: {self.llamafile_path}"
            
            # Try to get version information
            try:
                result = subprocess.run(
                    [self.llamafile_path, "--version"],
                    capture_output=True,
                    text=True,
                    timeout=10
                )
                if result.returncode == 0:
                    version_info = result.stdout.strip()
                    self.logger.info(f"Llamafile version: {version_info}")
                else:
                    # Some versions might not support --version, try --help
                    result = subprocess.run(
                        [self.llamafile_path, "--help"],
                        capture_output=True,
                        text=True,
                        timeout=10
                    )
                    if result.returncode != 0:
                        return False, f"Llamafile executable appears to be invalid: {self.llamafile_path}"
            
            except subprocess.TimeoutExpired:
                return False, "Llamafile executable is not responding (timeout)"
            except Exception as e:
                return False, f"Error testing llamafile executable: {e}"
            
            # Check for GPU support if enabled
            if self.config.gpu_enabled:
                gpu_support_info = self._check_gpu_support()
                if gpu_support_info:
                    self.logger.info(f"GPU support detected: {gpu_support_info}")
            
            return True, None
            
        except Exception as e:
            error_msg = f"Error checking llamafile availability: {e}"
            self.logger.error(error_msg)
            return False, error_msg
    
    def _check_gpu_support(self) -> Optional[str]:
        """
        Check what GPU acceleration is available for llamafile.
        
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
            result = subprocess.run(['nvidia-smi'], capture_output=True, timeout=5)
            return result.returncode == 0
        except (subprocess.TimeoutExpired, subprocess.CalledProcessError, FileNotFoundError):
            return False
    
    def _check_rocm_support(self) -> bool:
        """Check if ROCm support is available."""
        try:
            result = subprocess.run(['rocm-smi'], capture_output=True, timeout=5)
            return result.returncode == 0
        except (subprocess.TimeoutExpired, subprocess.CalledProcessError, FileNotFoundError):
            return False
    
    def _check_metal_support(self) -> bool:
        """Check if Metal support is available (macOS only)."""
        if platform.system() != "Darwin":
            return False
        
        try:
            result = subprocess.run(['system_profiler', 'SPDisplaysDataType'], 
                                  capture_output=True, text=True, timeout=10)
            return result.returncode == 0 and 'Metal' in result.stdout
        except (subprocess.TimeoutExpired, subprocess.CalledProcessError, FileNotFoundError):
            return False
    
    def _check_vulkan_support(self) -> bool:
        """Check if Vulkan support is available."""
        try:
            # Check for vulkaninfo utility
            result = subprocess.run(['vulkaninfo'], capture_output=True, timeout=5)
            return result.returncode == 0
        except (subprocess.TimeoutExpired, subprocess.CalledProcessError, FileNotFoundError):
            return False
    
    def load_model(self, model_path: str, **kwargs) -> LoadingResult:
        """
        Load a GGUF model using llamafile with comprehensive validation and optimization.
        
        Args:
            model_path: Path to the GGUF model file
            **kwargs: Additional loading parameters
            
        Returns:
            LoadingResult with detailed success/failure information
        """
        start_time = time.time()
        
        try:
            # Validate model file
            validation_result = self._validate_model_file(model_path)
            if not validation_result['valid']:
                return LoadingResult(
                    success=False,
                    backend_used=self.config.name,
                    hardware_used="none",
                    load_time=0.0,
                    error_message=validation_result['error']
                )
            
            # Check if llamafile is available
            is_available, error_msg = self.is_available()
            if not is_available:
                return LoadingResult(
                    success=False,
                    backend_used=self.config.name,
                    hardware_used="none",
                    load_time=0.0,
                    error_message=error_msg
                )
            
            # Stop any existing process
            if self.process and self.process.poll() is None:
                self._stop_llamafile_process()
            
            # Prepare llamafile command arguments
            cmd_args = self._prepare_llamafile_command(model_path, **kwargs)
            
            self.logger.info(f"Starting llamafile server: {Path(model_path).name}")
            self.logger.info(f"Server URL: {self.server_url}")
            self.logger.debug(f"Command: {' '.join(cmd_args)}")
            
            # Start llamafile process
            self.process = self._start_llamafile_process(cmd_args)
            
            # Wait for server to be ready
            if not self._wait_for_server_ready():
                self._stop_llamafile_process()
                return LoadingResult(
                    success=False,
                    backend_used=self.config.name,
                    hardware_used="none",
                    load_time=0.0,
                    error_message="Llamafile server failed to start or become ready"
                )
            
            # Start process monitoring
            self._start_process_monitoring()
            
            # Get model information from server
            model_info = self._get_server_model_info()
            
            # Store model information
            self.model_path = model_path
            self._model_type = self._detect_model_type(model_path)
            self.is_loaded = True
            
            # Calculate performance metrics
            load_time = time.time() - start_time
            self.load_time = load_time
            
            # Estimate memory usage
            self.memory_usage = self._estimate_memory_usage(validation_result, model_info)
            
            # Determine hardware acceleration used
            hardware_used = self._determine_hardware_used(cmd_args)
            self._hardware_acceleration = hardware_used
            
            self.logger.info(f"Model loaded successfully in {load_time:.2f}s")
            self.logger.info(f"Hardware acceleration: {hardware_used}")
            self.logger.info(f"Server ready at: {self.server_url}")
            
            return LoadingResult(
                success=True,
                backend_used=self.config.name,
                hardware_used=hardware_used,
                load_time=load_time,
                memory_usage=self.memory_usage,
                model_info={
                    'model_type': self._model_type,
                    'server_url': self.server_url,
                    'hardware_acceleration': hardware_used,
                    'process_id': self.process.pid,
                    **model_info,
                    **validation_result
                }
            )
            
        except Exception as e:
            load_time = time.time() - start_time
            error_msg = self._format_loading_error(e, model_path)
            self.logger.error(error_msg)
            
            # Clean up on failure
            if self.process:
                self._stop_llamafile_process()
            
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
            format_type = 'Unknown'
            try:
                with open(model_path, 'rb') as f:
                    header = f.read(8)
                    if len(header) >= 4:
                        if header[:4] == b'GGUF':
                            format_type = 'GGUF'
                        elif header[:4] == b'ggml' or header[:4] == b'GGML':
                            format_type = 'GGML'
                        else:
                            self.logger.warning(f"Unknown model format, attempting to load anyway")
            except Exception as e:
                self.logger.warning(f"Could not read model header: {e}")
            
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
    
    def _prepare_llamafile_command(self, model_path: str, **kwargs) -> List[str]:
        """
        Prepare command line arguments for llamafile.
        
        Args:
            model_path: Path to the model file
            **kwargs: Additional configuration parameters
            
        Returns:
            List of command line arguments
        """
        cmd_args = [self.llamafile_path]
        
        # Model file
        cmd_args.extend(["-m", model_path])
        
        # Server configuration
        cmd_args.extend(["--host", self.server_host])
        cmd_args.extend(["--port", str(self.server_port)])
        
        # Context size
        context_size = kwargs.get('context_size', self.config.context_size)
        cmd_args.extend(["-c", str(context_size)])
        
        # GPU configuration
        if self.config.gpu_enabled:
            gpu_layers = self._determine_optimal_gpu_layers(model_path, kwargs)
            if gpu_layers > 0:
                cmd_args.extend(["-ngl", str(gpu_layers)])
                self.logger.info(f"Using GPU acceleration with {gpu_layers} layers")
        
        # Threading configuration
        threads = kwargs.get('threads', self.config.threads)
        if threads > 0:
            cmd_args.extend(["-t", str(threads)])
        elif threads == -1:  # Auto-detect
            threads = self._get_optimal_thread_count()
            cmd_args.extend(["-t", str(threads)])
        
        # Batch size
        batch_size = kwargs.get('batch_size', self.config.batch_size)
        if batch_size > 0:
            cmd_args.extend(["-b", str(batch_size)])
        
        # Memory mapping
        cmd_args.append("--mmap")
        
        # Disable interactive mode (server mode)
        cmd_args.append("--server")
        
        # Additional custom arguments
        if self.config.custom_args:
            for key, value in self.config.custom_args.items():
                if isinstance(value, bool):
                    if value:
                        cmd_args.append(f"--{key}")
                else:
                    cmd_args.extend([f"--{key}", str(value)])
        
        # Override with explicit kwargs
        for key, value in kwargs.items():
            if key not in ['context_size', 'threads', 'batch_size', 'gpu_layers']:
                if isinstance(value, bool):
                    if value:
                        cmd_args.append(f"--{key}")
                else:
                    cmd_args.extend([f"--{key}", str(value)])
        
        return cmd_args
    
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
        if 'gpu_layers' in kwargs:
            return kwargs['gpu_layers']
        
        if self.config.gpu_layers != -1:
            return self.config.gpu_layers
        
        # Auto-detection based on hardware and model size
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
        
        except Exception as e:
            self.logger.debug(f"Error estimating GPU layers: {e}")
            return 32  # Default fallback
    
    def _get_optimal_thread_count(self) -> int:
        """Get optimal thread count for CPU inference."""
        try:
            cpu_count = os.cpu_count() or 4
            # Use 75% of available cores, but at least 1 and at most 16
            optimal_threads = max(1, min(16, int(cpu_count * 0.75)))
            return optimal_threads
        except Exception:
            return 4  # Safe fallback
    
    def _start_llamafile_process(self, cmd_args: List[str]) -> subprocess.Popen:
        """
        Start the llamafile process.
        
        Args:
            cmd_args: Command line arguments
            
        Returns:
            Process object
            
        Raises:
            ModelLoadingError: If process fails to start
        """
        try:
            # Prepare environment
            env = os.environ.copy()
            
            # Set GPU-related environment variables if needed
            if self.config.gpu_enabled:
                if self._check_cuda_support():
                    env['CUDA_VISIBLE_DEVICES'] = '0'  # Use first GPU by default
            
            # Start process
            process = subprocess.Popen(
                cmd_args,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                env=env,
                text=True,
                bufsize=1,
                universal_newlines=True
            )
            
            # Give process a moment to start
            time.sleep(1)
            
            # Check if process started successfully
            if process.poll() is not None:
                stdout, stderr = process.communicate(timeout=5)
                error_msg = f"Llamafile process failed to start. Exit code: {process.returncode}"
                if stderr:
                    error_msg += f"\nError output: {stderr}"
                raise ModelLoadingError(error_msg)
            
            self.logger.info(f"Llamafile process started with PID: {process.pid}")
            return process
            
        except subprocess.TimeoutExpired:
            raise ModelLoadingError("Llamafile process startup timeout")
        except Exception as e:
            raise ModelLoadingError(f"Failed to start llamafile process: {e}")
    
    def _wait_for_server_ready(self, timeout: int = None) -> bool:
        """
        Wait for the llamafile server to be ready.
        
        Args:
            timeout: Maximum time to wait in seconds
            
        Returns:
            True if server is ready, False otherwise
        """
        if timeout is None:
            timeout = self.DEFAULT_TIMEOUT
        
        start_time = time.time()
        
        while time.time() - start_time < timeout:
            try:
                # Check if process is still running
                if self.process.poll() is not None:
                    self.logger.error("Llamafile process terminated unexpectedly")
                    return False
                
                # Try to connect to server
                response = requests.get(
                    f"{self.server_url}/health",
                    timeout=2
                )
                
                if response.status_code == 200:
                    self.logger.info("Llamafile server is ready")
                    return True
                    
            except requests.exceptions.RequestException:
                # Server not ready yet, continue waiting
                pass
            
            time.sleep(0.5)
        
        self.logger.error(f"Llamafile server not ready after {timeout} seconds")
        return False
    
    def _get_server_model_info(self) -> Dict[str, Any]:
        """
        Get model information from the llamafile server.
        
        Returns:
            Dictionary with model information
        """
        try:
            response = requests.get(
                f"{self.server_url}/v1/models",
                timeout=10
            )
            
            if response.status_code == 200:
                data = response.json()
                if 'data' in data and len(data['data']) > 0:
                    model_info = data['data'][0]
                    return {
                        'server_model_id': model_info.get('id', 'unknown'),
                        'server_model_object': model_info.get('object', 'model'),
                        'server_created': model_info.get('created', 0)
                    }
            
        except Exception as e:
            self.logger.debug(f"Could not get server model info: {e}")
        
        return {}
    
    def _start_process_monitoring(self):
        """Start monitoring the llamafile process."""
        if self._process_monitor_thread and self._process_monitor_thread.is_alive():
            return
        
        self._stop_monitoring.clear()
        self._process_monitor_thread = threading.Thread(
            target=self._monitor_process,
            daemon=True
        )
        self._process_monitor_thread.start()
    
    def _monitor_process(self):
        """Monitor the llamafile process and handle unexpected termination."""
        while not self._stop_monitoring.is_set():
            try:
                if self.process and self.process.poll() is not None:
                    # Process has terminated
                    stdout, stderr = self.process.communicate()
                    self.logger.error(f"Llamafile process terminated unexpectedly. Exit code: {self.process.returncode}")
                    if stderr:
                        self.logger.error(f"Process error output: {stderr}")
                    
                    self.is_loaded = False
                    break
                
                time.sleep(1)
                
            except Exception as e:
                self.logger.error(f"Error monitoring llamafile process: {e}")
                break
    
    def _stop_llamafile_process(self):
        """Stop the llamafile process gracefully."""
        if not self.process:
            return
        
        try:
            # Stop monitoring
            self._stop_monitoring.set()
            if self._process_monitor_thread and self._process_monitor_thread.is_alive():
                self._process_monitor_thread.join(timeout=2)
            
            # Try graceful shutdown first
            if self.process.poll() is None:
                try:
                    # Send shutdown request to server
                    requests.post(f"{self.server_url}/shutdown", timeout=5)
                    time.sleep(2)
                except:
                    pass
            
            # If still running, terminate
            if self.process.poll() is None:
                self.logger.info("Terminating llamafile process...")
                self.process.terminate()
                
                # Wait for termination
                try:
                    self.process.wait(timeout=5)
                except subprocess.TimeoutExpired:
                    # Force kill if necessary
                    self.logger.warning("Force killing llamafile process...")
                    self.process.kill()
                    self.process.wait()
            
            self.logger.info("Llamafile process stopped")
            
        except Exception as e:
            self.logger.error(f"Error stopping llamafile process: {e}")
        finally:
            self.process = None
            self.is_loaded = False
    
    def generate_text(self, prompt: str, config: GenerationConfig) -> str:
        """
        Generate text from the given prompt using the llamafile server.
        
        Args:
            prompt: Input text prompt
            config: Generation configuration
            
        Returns:
            Generated text
            
        Raises:
            ModelLoadingError: If no model is loaded
            BackendError: If generation fails
        """
        if not self.is_loaded or not self.process or self.process.poll() is not None:
            raise ModelLoadingError("No model is loaded or llamafile process is not running")
        
        try:
            start_time = time.time()
            
            # Prepare request payload
            payload = {
                "prompt": prompt,
                "max_tokens": config.max_tokens,
                "temperature": config.temperature,
                "top_p": config.top_p,
                "top_k": config.top_k,
                "repeat_penalty": config.repeat_penalty,
                "stream": config.stream
            }
            
            # Add seed if specified
            if config.seed >= 0:
                payload["seed"] = config.seed
            
            # Add stop sequences if specified
            if config.stop_sequences:
                payload["stop"] = config.stop_sequences
            
            self.logger.debug(f"Generating text with payload: {payload}")
            
            if config.stream:
                return self._generate_streaming(payload, start_time)
            else:
                return self._generate_non_streaming(payload, start_time)
            
        except Exception as e:
            error_msg = f"Text generation failed: {e}"
            self.logger.error(error_msg)
            raise BackendError(error_msg)
    
    def _generate_non_streaming(self, payload: Dict[str, Any], start_time: float) -> str:
        """Generate text without streaming."""
        try:
            response = requests.post(
                f"{self.server_url}/v1/completions",
                json=payload,
                timeout=120  # Generous timeout for generation
            )
            
            if response.status_code != 200:
                raise BackendError(f"Server returned status {response.status_code}: {response.text}")
            
            data = response.json()
            
            if 'choices' not in data or len(data['choices']) == 0:
                raise BackendError("No completion choices returned from server")
            
            generated_text = data['choices'][0]['text']
            
            # Update generation statistics
            generation_time = time.time() - start_time
            tokens_generated = len(generated_text.split())  # Rough token count
            
            self._generation_stats['total_tokens'] += tokens_generated
            self._generation_stats['total_time'] += generation_time
            if self._generation_stats['total_time'] > 0:
                self._generation_stats['average_tokens_per_second'] = (
                    self._generation_stats['total_tokens'] / self._generation_stats['total_time']
                )
            
            self.logger.debug(f"Generated {tokens_generated} tokens in {generation_time:.2f}s")
            
            return generated_text
            
        except requests.exceptions.RequestException as e:
            raise BackendError(f"Request to llamafile server failed: {e}")
        except json.JSONDecodeError as e:
            raise BackendError(f"Invalid JSON response from server: {e}")
    
    def _generate_streaming(self, payload: Dict[str, Any], start_time: float) -> str:
        """Generate text with streaming (simplified implementation)."""
        try:
            response = requests.post(
                f"{self.server_url}/v1/completions",
                json=payload,
                stream=True,
                timeout=120
            )
            
            if response.status_code != 200:
                raise BackendError(f"Server returned status {response.status_code}: {response.text}")
            
            generated_text = ""
            
            for line in response.iter_lines():
                if line:
                    line = line.decode('utf-8')
                    if line.startswith('data: '):
                        data_str = line[6:]  # Remove 'data: ' prefix
                        if data_str.strip() == '[DONE]':
                            break
                        
                        try:
                            data = json.loads(data_str)
                            if 'choices' in data and len(data['choices']) > 0:
                                delta = data['choices'][0].get('text', '')
                                generated_text += delta
                        except json.JSONDecodeError:
                            continue
            
            # Update generation statistics
            generation_time = time.time() - start_time
            tokens_generated = len(generated_text.split())
            
            self._generation_stats['total_tokens'] += tokens_generated
            self._generation_stats['total_time'] += generation_time
            if self._generation_stats['total_time'] > 0:
                self._generation_stats['average_tokens_per_second'] = (
                    self._generation_stats['total_tokens'] / self._generation_stats['total_time']
                )
            
            return generated_text
            
        except requests.exceptions.RequestException as e:
            raise BackendError(f"Streaming request to llamafile server failed: {e}")
    
    def unload_model(self) -> bool:
        """
        Unload the current model by stopping the llamafile process.
        
        Returns:
            True if successful, False otherwise
        """
        try:
            if self.process:
                self._stop_llamafile_process()
            
            # Reset state
            self.model_path = None
            self._model_type = None
            self._hardware_acceleration = None
            self.is_loaded = False
            self.load_time = 0.0
            self.memory_usage = 0
            
            self.logger.info("Model unloaded successfully")
            return True
            
        except Exception as e:
            self.logger.error(f"Error unloading model: {e}")
            return False
    
    def get_hardware_info(self) -> HardwareInfo:
        """
        Get information about hardware acceleration.
        
        Returns:
            HardwareInfo object with current hardware status
        """
        try:
            hardware_info = HardwareInfo()
            
            # Get CPU information
            hardware_info.cpu_cores = os.cpu_count() or 0
            
            # Get memory information
            try:
                memory = psutil.virtual_memory()
                hardware_info.total_ram = memory.total // (1024 * 1024)  # Convert to MB
            except:
                hardware_info.total_ram = 0
            
            # Detect GPU information
            gpu_devices = []
            total_vram = 0
            supported_hardware = [HardwareType.CPU]
            
            # Check CUDA GPUs
            if self._check_cuda_support():
                try:
                    result = subprocess.run(
                        ['nvidia-smi', '--query-gpu=name,memory.total', '--format=csv,noheader,nounits'],
                        capture_output=True, text=True, timeout=10
                    )
                    if result.returncode == 0:
                        for line in result.stdout.strip().split('\n'):
                            if line.strip():
                                parts = line.split(', ')
                                if len(parts) >= 2:
                                    gpu_name = parts[0].strip()
                                    gpu_memory = int(parts[1].strip())
                                    gpu_devices.append({
                                        'name': gpu_name,
                                        'memory_mb': gpu_memory,
                                        'type': 'CUDA'
                                    })
                                    total_vram += gpu_memory
                        
                        if gpu_devices:
                            supported_hardware.append(HardwareType.CUDA)
                except:
                    pass
            
            # Check ROCm GPUs
            if self._check_rocm_support():
                supported_hardware.append(HardwareType.ROCM)
            
            # Check Metal support
            if self._check_metal_support():
                supported_hardware.append(HardwareType.METAL)
            
            # Check Vulkan support
            if self._check_vulkan_support():
                supported_hardware.append(HardwareType.VULKAN)
            
            hardware_info.gpu_count = len(gpu_devices)
            hardware_info.gpu_devices = gpu_devices
            hardware_info.total_vram = total_vram
            hardware_info.supported_hardware = supported_hardware
            hardware_info.recommended_backend = "llamafile"
            
            return hardware_info
            
        except Exception as e:
            self.logger.error(f"Error getting hardware info: {e}")
            return HardwareInfo()
    
    def _detect_model_type(self, model_path: str) -> str:
        """
        Detect model type from file name.
        
        Args:
            model_path: Path to the model file
            
        Returns:
            Detected model type string
        """
        model_path_lower = model_path.lower()
        model_name = Path(model_path).name.lower()
        
        # Detection patterns (order matters - more specific first)
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
        ]
        
        for patterns, model_type in detection_patterns:
            for pattern in patterns:
                if pattern in model_name or pattern in model_path_lower:
                    self.logger.info(f"Detected model type '{model_type}' from pattern '{pattern}'")
                    return model_type
        
        # Default fallback
        self.logger.warning(f"Could not detect model type from '{model_name}', defaulting to 'llama'")
        return 'llama'
    
    def _estimate_memory_usage(self, validation_result: Dict[str, Any], model_info: Dict[str, Any]) -> int:
        """
        Estimate memory usage based on model size and configuration.
        
        Args:
            validation_result: Model file validation results
            model_info: Additional model information
            
        Returns:
            Estimated memory usage in MB
        """
        base_size_mb = validation_result.get('file_size_mb', 0)
        
        # Base memory usage (model weights)
        memory_usage = base_size_mb
        
        # Add context buffer overhead
        context_overhead = (self.config.context_size * 4) // (1024 * 1024)  # 4 bytes per token
        memory_usage += context_overhead
        
        # Add server overhead
        memory_usage += 100  # Llamafile server overhead
        
        # Add GPU memory overhead if using GPU
        if self.config.gpu_enabled and self.config.gpu_layers > 0:
            memory_usage = int(memory_usage * 1.2)  # 20% GPU overhead
        else:
            memory_usage = int(memory_usage * 1.1)  # 10% CPU overhead
        
        return memory_usage
    
    def _determine_hardware_used(self, cmd_args: List[str]) -> str:
        """
        Determine what hardware acceleration is being used based on command arguments.
        
        Args:
            cmd_args: Command line arguments used to start llamafile
            
        Returns:
            Hardware type string
        """
        # Check if GPU layers are specified
        gpu_layers = 0
        for i, arg in enumerate(cmd_args):
            if arg == "-ngl" and i + 1 < len(cmd_args):
                try:
                    gpu_layers = int(cmd_args[i + 1])
                    break
                except ValueError:
                    pass
        
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
        if "executable not found" in error_str.lower():
            return (f"Llamafile executable not found. Please install llamafile and ensure it's in your PATH. "
                   f"Error: {error}")
        
        elif "permission denied" in error_str.lower():
            return (f"Permission denied accessing llamafile or model file. "
                   f"Check file permissions. Error: {error}")
        
        elif "port" in error_str.lower() and "in use" in error_str.lower():
            return (f"Server port {self.server_port} is already in use. "
                   f"Try stopping other llamafile instances. Error: {error}")
        
        elif "timeout" in error_str.lower():
            return (f"Llamafile server startup timeout. The model might be too large or system too slow. "
                   f"Error: {error}")
        
        elif "process terminated" in error_str.lower():
            return (f"Llamafile process terminated unexpectedly while loading {Path(model_path).name}. "
                   f"Check model file integrity. Error: {error}")
        
        else:
            return f"Failed to load model {Path(model_path).name} with llamafile: {error}"
    
    def get_generation_stats(self) -> Dict[str, Any]:
        """Get generation statistics."""
        return self._generation_stats.copy()
    
    def get_server_status(self) -> Dict[str, Any]:
        """
        Get current server status.
        
        Returns:
            Dictionary with server status information
        """
        status = {
            'is_running': False,
            'server_url': self.server_url,
            'process_id': None,
            'model_loaded': self.is_loaded
        }
        
        if self.process:
            status['is_running'] = self.process.poll() is None
            status['process_id'] = self.process.pid
        
        return status
    
    def __del__(self):
        """Cleanup when backend is destroyed."""
        try:
            if self.process:
                self._stop_llamafile_process()
        except:
            pass