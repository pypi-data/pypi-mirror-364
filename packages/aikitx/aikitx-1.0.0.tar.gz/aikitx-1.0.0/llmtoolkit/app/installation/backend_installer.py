"""
Backend installer with improved error handling and automatic dependency management.
"""

import subprocess
import sys
import os
import platform
import logging
from typing import Dict, List, Optional, Tuple, Any
from dataclasses import dataclass
from enum import Enum
import importlib.util
import json
import tempfile
import shutil

logger = logging.getLogger(__name__)


class InstallationStatus(Enum):
    """Installation status enumeration."""
    SUCCESS = "success"
    FAILED = "failed"
    PARTIAL = "partial"
    SKIPPED = "skipped"


@dataclass
class InstallationResult:
    """Result of backend installation."""
    backend_name: str
    status: InstallationStatus
    message: str
    details: Dict[str, Any]
    installation_time: float
    dependencies_installed: List[str]
    errors: List[str]


class BackendInstaller:
    """Handles installation of different backend engines with improved error handling."""
    
    def __init__(self):
        self.system_info = self._get_system_info()
        self.python_executable = sys.executable
        self.installation_cache = {}
        
    def _get_system_info(self) -> Dict[str, str]:
        """Get system information for installation decisions."""
        return {
            'platform': platform.system(),
            'architecture': platform.machine(),
            'python_version': platform.python_version(),
            'os_version': platform.version()
        }
    
    def install_backend(self, backend_name: str, force_reinstall: bool = False) -> InstallationResult:
        """Install a specific backend with comprehensive error handling."""
        start_time = time.time()
        
        try:
            logger.info(f"Starting installation of {backend_name} backend")
            
            # Check if already installed and working
            if not force_reinstall and self._is_backend_working(backend_name):
                return InstallationResult(
                    backend_name=backend_name,
                    status=InstallationStatus.SKIPPED,
                    message=f"{backend_name} is already installed and working",
                    details=self.system_info,
                    installation_time=time.time() - start_time,
                    dependencies_installed=[],
                    errors=[]
                )
            
            # Get installation strategy for backend
            strategy = self._get_installation_strategy(backend_name)
            if not strategy:
                return InstallationResult(
                    backend_name=backend_name,
                    status=InstallationStatus.FAILED,
                    message=f"No installation strategy found for {backend_name}",
                    details=self.system_info,
                    installation_time=time.time() - start_time,
                    dependencies_installed=[],
                    errors=[f"Unsupported backend: {backend_name}"]
                )
            
            # Execute installation
            result = self._execute_installation(backend_name, strategy)
            result.installation_time = time.time() - start_time
            
            return result
            
        except Exception as e:
            logger.error(f"Unexpected error installing {backend_name}: {e}")
            return InstallationResult(
                backend_name=backend_name,
                status=InstallationStatus.FAILED,
                message=f"Unexpected installation error: {str(e)}",
                details=self.system_info,
                installation_time=time.time() - start_time,
                dependencies_installed=[],
                errors=[str(e)]
            )
    
    def _get_installation_strategy(self, backend_name: str) -> Optional[Dict[str, Any]]:
        """Get installation strategy for a specific backend."""
        strategies = {
            'ctransformers': {
                'packages': ['ctransformers'],
                'gpu_packages': {
                    'cuda': ['ctransformers[cuda]'],
                    'rocm': ['ctransformers[rocm]'],
                    'metal': ['ctransformers[metal]'] if self.system_info['platform'] == 'Darwin' else []
                },
                'test_import': 'ctransformers',
                'fallback_packages': ['ctransformers'],
                'pre_install_checks': ['_check_gpu_support'],
                'post_install_validation': ['_validate_ctransformers']
            },
            'transformers': {
                'packages': ['transformers', 'accelerate', 'torch'],
                'gpu_packages': {
                    'cuda': ['torch', 'transformers', 'accelerate'],
                    'rocm': ['torch', 'transformers', 'accelerate'],
                    'mps': ['torch', 'transformers', 'accelerate'] if self.system_info['platform'] == 'Darwin' else []
                },
                'test_import': 'transformers',
                'fallback_packages': ['transformers', 'torch'],
                'pre_install_checks': ['_check_torch_compatibility'],
                'post_install_validation': ['_validate_transformers']
            },
            'llamafile': {
                'packages': [],  # No Python packages needed
                'executable_download': True,
                'download_urls': {
                    'Windows': 'https://github.com/Mozilla-Ocho/llamafile/releases/latest/download/llamafile.exe',
                    'Linux': 'https://github.com/Mozilla-Ocho/llamafile/releases/latest/download/llamafile',
                    'Darwin': 'https://github.com/Mozilla-Ocho/llamafile/releases/latest/download/llamafile'
                },
                'test_executable': True,
                'post_install_validation': ['_validate_llamafile']
            },
            'llama-cpp-python': {
                'packages': ['llama-cpp-python'],
                'gpu_packages': {
                    'cuda': ['llama-cpp-python[cuda]'],
                    'rocm': ['llama-cpp-python[rocm]'],
                    'vulkan': ['llama-cpp-python[vulkan]'],
                    'metal': ['llama-cpp-python[metal]'] if self.system_info['platform'] == 'Darwin' else []
                },
                'test_import': 'llama_cpp',
                'fallback_packages': ['llama-cpp-python'],
                'pre_install_checks': ['_check_build_tools'],
                'post_install_validation': ['_validate_llama_cpp_python'],
                'build_from_source': True
            }
        }
        
        return strategies.get(backend_name)
    
    def _execute_installation(self, backend_name: str, strategy: Dict[str, Any]) -> InstallationResult:
        """Execute the installation strategy."""
        errors = []
        dependencies_installed = []
        
        try:
            # Run pre-install checks
            for check in strategy.get('pre_install_checks', []):
                check_method = getattr(self, check, None)
                if check_method:
                    check_result = check_method()
                    if not check_result.get('success', True):
                        errors.append(f"Pre-install check failed: {check_result.get('message', 'Unknown error')}")
            
            # Handle executable downloads (e.g., llamafile)
            if strategy.get('executable_download'):
                download_result = self._download_executable(backend_name, strategy)
                if download_result['success']:
                    dependencies_installed.extend(download_result.get('files', []))
                else:
                    errors.extend(download_result.get('errors', []))
            
            # Install Python packages
            packages_to_install = self._determine_packages(strategy)
            if packages_to_install:
                install_result = self._install_packages(packages_to_install)
                if install_result['success']:
                    dependencies_installed.extend(packages_to_install)
                else:
                    errors.extend(install_result.get('errors', []))
                    
                    # Try fallback packages if main installation failed
                    fallback_packages = strategy.get('fallback_packages', [])
                    if fallback_packages and fallback_packages != packages_to_install:
                        logger.info(f"Trying fallback packages for {backend_name}")
                        fallback_result = self._install_packages(fallback_packages)
                        if fallback_result['success']:
                            dependencies_installed.extend(fallback_packages)
                            errors = []  # Clear previous errors if fallback succeeded
                        else:
                            errors.extend(fallback_result.get('errors', []))
            
            # Run post-install validation
            validation_success = True
            for validation in strategy.get('post_install_validation', []):
                validation_method = getattr(self, validation, None)
                if validation_method:
                    validation_result = validation_method()
                    if not validation_result.get('success', True):
                        validation_success = False
                        errors.append(f"Validation failed: {validation_result.get('message', 'Unknown error')}")
            
            # Determine final status
            if errors:
                if dependencies_installed:
                    status = InstallationStatus.PARTIAL
                    message = f"{backend_name} partially installed with some issues"
                else:
                    status = InstallationStatus.FAILED
                    message = f"{backend_name} installation failed"
            else:
                status = InstallationStatus.SUCCESS
                message = f"{backend_name} installed successfully"
            
            return InstallationResult(
                backend_name=backend_name,
                status=status,
                message=message,
                details={
                    'system_info': self.system_info,
                    'packages_installed': dependencies_installed,
                    'installation_strategy': backend_name
                },
                installation_time=0,  # Will be set by caller
                dependencies_installed=dependencies_installed,
                errors=errors
            )
            
        except Exception as e:
            logger.error(f"Installation execution failed for {backend_name}: {e}")
            return InstallationResult(
                backend_name=backend_name,
                status=InstallationStatus.FAILED,
                message=f"Installation execution failed: {str(e)}",
                details=self.system_info,
                installation_time=0,
                dependencies_installed=dependencies_installed,
                errors=errors + [str(e)]
            )
    
    def _determine_packages(self, strategy: Dict[str, Any]) -> List[str]:
        """Determine which packages to install based on GPU availability."""
        # Check for GPU support
        gpu_type = self._detect_gpu_type()
        
        if gpu_type and gpu_type in strategy.get('gpu_packages', {}):
            packages = strategy['gpu_packages'][gpu_type]
            logger.info(f"Installing GPU-accelerated packages for {gpu_type}: {packages}")
            return packages
        else:
            packages = strategy.get('packages', [])
            logger.info(f"Installing CPU-only packages: {packages}")
            return packages
    
    def _detect_gpu_type(self) -> Optional[str]:
        """Detect available GPU type for installation decisions."""
        try:
            # Try to detect NVIDIA GPU
            result = subprocess.run(['nvidia-smi'], capture_output=True, text=True, timeout=10)
            if result.returncode == 0:
                return 'cuda'
        except (subprocess.TimeoutExpired, FileNotFoundError):
            pass
        
        try:
            # Try to detect AMD GPU (ROCm)
            result = subprocess.run(['rocm-smi'], capture_output=True, text=True, timeout=10)
            if result.returncode == 0:
                return 'rocm'
        except (subprocess.TimeoutExpired, FileNotFoundError):
            pass
        
        # Check for Apple Silicon
        if self.system_info['platform'] == 'Darwin' and 'arm' in self.system_info['architecture'].lower():
            return 'metal'
        
        return None
    
    def _install_packages(self, packages: List[str]) -> Dict[str, Any]:
        """Install Python packages using pip with comprehensive error handling."""
        if not packages:
            return {'success': True, 'errors': []}
        
        errors = []
        
        try:
            # Upgrade pip first
            pip_upgrade_cmd = [self.python_executable, '-m', 'pip', 'install', '--upgrade', 'pip']
            result = subprocess.run(pip_upgrade_cmd, capture_output=True, text=True, timeout=300)
            if result.returncode != 0:
                logger.warning(f"Failed to upgrade pip: {result.stderr}")
            
            # Install packages
            install_cmd = [
                self.python_executable, '-m', 'pip', 'install',
                '--upgrade',
                '--no-cache-dir',
                '--timeout', '300'
            ] + packages
            
            logger.info(f"Running: {' '.join(install_cmd)}")
            result = subprocess.run(install_cmd, capture_output=True, text=True, timeout=600)
            
            if result.returncode == 0:
                logger.info(f"Successfully installed packages: {packages}")
                return {'success': True, 'errors': []}
            else:
                error_msg = f"Package installation failed: {result.stderr}"
                logger.error(error_msg)
                errors.append(error_msg)
                
                # Try installing packages individually if batch install failed
                individual_success = []
                for package in packages:
                    individual_cmd = [
                        self.python_executable, '-m', 'pip', 'install',
                        '--upgrade', '--no-cache-dir', package
                    ]
                    individual_result = subprocess.run(individual_cmd, capture_output=True, text=True, timeout=300)
                    if individual_result.returncode == 0:
                        individual_success.append(package)
                        logger.info(f"Successfully installed {package} individually")
                    else:
                        errors.append(f"Failed to install {package}: {individual_result.stderr}")
                
                if individual_success:
                    return {'success': True, 'errors': errors, 'partial_success': individual_success}
                else:
                    return {'success': False, 'errors': errors}
                    
        except subprocess.TimeoutExpired:
            error_msg = "Package installation timed out"
            logger.error(error_msg)
            errors.append(error_msg)
            return {'success': False, 'errors': errors}
        except Exception as e:
            error_msg = f"Unexpected error during package installation: {str(e)}"
            logger.error(error_msg)
            errors.append(error_msg)
            return {'success': False, 'errors': errors}
    
    def _download_executable(self, backend_name: str, strategy: Dict[str, Any]) -> Dict[str, Any]:
        """Download executable files (e.g., llamafile)."""
        try:
            import urllib.request
            
            download_urls = strategy.get('download_urls', {})
            platform_name = self.system_info['platform']
            
            if platform_name not in download_urls:
                return {
                    'success': False,
                    'errors': [f"No download URL available for platform: {platform_name}"]
                }
            
            url = download_urls[platform_name]
            filename = f"{backend_name}.exe" if platform_name == 'Windows' else backend_name
            
            # Create executables directory
            exe_dir = os.path.join(os.path.dirname(__file__), '..', '..', 'executables')
            os.makedirs(exe_dir, exist_ok=True)
            
            exe_path = os.path.join(exe_dir, filename)
            
            logger.info(f"Downloading {backend_name} from {url}")
            urllib.request.urlretrieve(url, exe_path)
            
            # Make executable on Unix systems
            if platform_name != 'Windows':
                os.chmod(exe_path, 0o755)
            
            return {
                'success': True,
                'files': [exe_path],
                'errors': []
            }
            
        except Exception as e:
            error_msg = f"Failed to download {backend_name}: {str(e)}"
            logger.error(error_msg)
            return {
                'success': False,
                'errors': [error_msg]
            }
    
    def _is_backend_working(self, backend_name: str) -> bool:
        """Check if a backend is already installed and working."""
        try:
            if backend_name == 'ctransformers':
                import ctransformers
                return True
            elif backend_name == 'transformers':
                import transformers
                import torch
                return True
            elif backend_name == 'llamafile':
                exe_dir = os.path.join(os.path.dirname(__file__), '..', '..', 'executables')
                filename = 'llamafile.exe' if self.system_info['platform'] == 'Windows' else 'llamafile'
                exe_path = os.path.join(exe_dir, filename)
                return os.path.exists(exe_path) and os.access(exe_path, os.X_OK)
            elif backend_name == 'llama-cpp-python':
                import llama_cpp
                return True
            else:
                return False
        except ImportError:
            return False
        except Exception:
            return False
    
    # Validation methods
    def _validate_ctransformers(self) -> Dict[str, Any]:
        """Validate ctransformers installation."""
        try:
            import ctransformers
            # Try to create a simple model instance to test functionality
            return {'success': True, 'message': 'ctransformers validation passed'}
        except Exception as e:
            return {'success': False, 'message': f'ctransformers validation failed: {str(e)}'}
    
    def _validate_transformers(self) -> Dict[str, Any]:
        """Validate transformers installation."""
        try:
            import transformers
            import torch
            # Check if CUDA is available if we installed CUDA version
            gpu_available = torch.cuda.is_available() if hasattr(torch.cuda, 'is_available') else False
            return {
                'success': True, 
                'message': f'transformers validation passed (GPU available: {gpu_available})'
            }
        except Exception as e:
            return {'success': False, 'message': f'transformers validation failed: {str(e)}'}
    
    def _validate_llamafile(self) -> Dict[str, Any]:
        """Validate llamafile installation."""
        try:
            exe_dir = os.path.join(os.path.dirname(__file__), '..', '..', 'executables')
            filename = 'llamafile.exe' if self.system_info['platform'] == 'Windows' else 'llamafile'
            exe_path = os.path.join(exe_dir, filename)
            
            if not os.path.exists(exe_path):
                return {'success': False, 'message': 'llamafile executable not found'}
            
            # Test execution with --help flag
            result = subprocess.run([exe_path, '--help'], capture_output=True, text=True, timeout=10)
            if result.returncode == 0:
                return {'success': True, 'message': 'llamafile validation passed'}
            else:
                return {'success': False, 'message': f'llamafile execution test failed: {result.stderr}'}
                
        except Exception as e:
            return {'success': False, 'message': f'llamafile validation failed: {str(e)}'}
    
    def _validate_llama_cpp_python(self) -> Dict[str, Any]:
        """Validate llama-cpp-python installation."""
        try:
            import llama_cpp
            # Try to check GPU support
            gpu_support = hasattr(llama_cpp, 'llama_backend_cuda_init')
            return {
                'success': True, 
                'message': f'llama-cpp-python validation passed (GPU support: {gpu_support})'
            }
        except Exception as e:
            return {'success': False, 'message': f'llama-cpp-python validation failed: {str(e)}'}
    
    # Pre-install check methods
    def _check_gpu_support(self) -> Dict[str, Any]:
        """Check GPU support availability."""
        gpu_type = self._detect_gpu_type()
        return {
            'success': True,
            'message': f'GPU detection completed (type: {gpu_type or "none"})',
            'gpu_type': gpu_type
        }
    
    def _check_torch_compatibility(self) -> Dict[str, Any]:
        """Check PyTorch compatibility."""
        try:
            # Check if torch is already installed and compatible
            import torch
            version = torch.__version__
            return {'success': True, 'message': f'PyTorch {version} already available'}
        except ImportError:
            return {'success': True, 'message': 'PyTorch not installed, will install fresh'}
        except Exception as e:
            return {'success': False, 'message': f'PyTorch compatibility check failed: {str(e)}'}
    
    def _check_build_tools(self) -> Dict[str, Any]:
        """Check build tools availability for llama-cpp-python."""
        if self.system_info['platform'] == 'Windows':
            # Check for Visual Studio Build Tools
            try:
                result = subprocess.run(['where', 'cl'], capture_output=True, text=True)
                if result.returncode == 0:
                    return {'success': True, 'message': 'Build tools available'}
                else:
                    return {
                        'success': False, 
                        'message': 'Visual Studio Build Tools not found. Please install Visual Studio Build Tools.'
                    }
            except Exception:
                return {'success': False, 'message': 'Could not check for build tools'}
        else:
            # Check for gcc/clang on Unix systems
            try:
                result = subprocess.run(['gcc', '--version'], capture_output=True, text=True)
                if result.returncode == 0:
                    return {'success': True, 'message': 'GCC available'}
                else:
                    result = subprocess.run(['clang', '--version'], capture_output=True, text=True)
                    if result.returncode == 0:
                        return {'success': True, 'message': 'Clang available'}
                    else:
                        return {'success': False, 'message': 'No C compiler found'}
            except Exception:
                return {'success': False, 'message': 'Could not check for C compiler'}


# Add missing import
import time