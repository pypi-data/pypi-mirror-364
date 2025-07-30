"""
Automatic dependency detection and management utilities.
"""

import subprocess
import sys
import os
import platform
import logging
import importlib.util
from typing import Dict, List, Optional, Tuple, Any
from dataclasses import dataclass
from enum import Enum
import json
import pkg_resources

logger = logging.getLogger(__name__)


@dataclass
class DependencyInfo:
    """Information about a dependency."""
    name: str
    version: Optional[str]
    installed: bool
    required_version: Optional[str]
    compatible: bool
    location: Optional[str]
    extras: List[str]


@dataclass
class SystemRequirements:
    """System requirements for backends."""
    python_version: Tuple[int, int, int]
    platform: str
    architecture: str
    gpu_support: Dict[str, bool]
    memory_gb: float
    disk_space_gb: float


class DependencyDetector:
    """Detects and manages dependencies for backend installations."""
    
    def __init__(self):
        self.system_info = self._get_system_info()
        self.python_executable = sys.executable
        
    def _get_system_info(self) -> Dict[str, Any]:
        """Get comprehensive system information."""
        return {
            'platform': platform.system(),
            'platform_release': platform.release(),
            'architecture': platform.machine(),
            'python_version': sys.version_info,
            'python_executable': sys.executable,
            'pip_version': self._get_pip_version(),
            'virtual_env': self._detect_virtual_environment()
        }
    
    def _get_pip_version(self) -> Optional[str]:
        """Get pip version."""
        try:
            result = subprocess.run(
                [self.python_executable, '-m', 'pip', '--version'],
                capture_output=True, text=True, timeout=10
            )
            if result.returncode == 0:
                # Extract version from output like "pip 21.3.1 from ..."
                version_line = result.stdout.strip()
                if 'pip' in version_line:
                    return version_line.split()[1]
        except Exception as e:
            logger.warning(f"Could not detect pip version: {e}")
        return None
    
    def _detect_virtual_environment(self) -> Dict[str, Any]:
        """Detect if running in virtual environment."""
        venv_info = {
            'in_venv': False,
            'venv_type': None,
            'venv_path': None
        }
        
        # Check for virtual environment
        if hasattr(sys, 'real_prefix') or (hasattr(sys, 'base_prefix') and sys.base_prefix != sys.prefix):
            venv_info['in_venv'] = True
            venv_info['venv_path'] = sys.prefix
            
            # Determine venv type
            if os.path.exists(os.path.join(sys.prefix, 'pyvenv.cfg')):
                venv_info['venv_type'] = 'venv'
            elif 'conda' in sys.prefix or 'anaconda' in sys.prefix:
                venv_info['venv_type'] = 'conda'
            elif 'virtualenv' in sys.prefix:
                venv_info['venv_type'] = 'virtualenv'
            else:
                venv_info['venv_type'] = 'unknown'
        
        return venv_info
    
    def detect_backend_dependencies(self, backend_name: str) -> Dict[str, DependencyInfo]:
        """Detect dependencies for a specific backend."""
        dependency_specs = self._get_backend_dependency_specs()
        
        if backend_name not in dependency_specs:
            logger.warning(f"No dependency specification found for backend: {backend_name}")
            return {}
        
        spec = dependency_specs[backend_name]
        dependencies = {}
        
        for dep_name, dep_config in spec.items():
            dep_info = self._check_dependency(dep_name, dep_config)
            dependencies[dep_name] = dep_info
        
        return dependencies
    
    def _get_backend_dependency_specs(self) -> Dict[str, Dict[str, Any]]:
        """Get dependency specifications for all backends."""
        return {
            'ctransformers': {
                'ctransformers': {
                    'required_version': '>=0.2.0',
                    'extras': ['cuda', 'rocm', 'metal'],
                    'import_name': 'ctransformers'
                }
            },
            'transformers': {
                'transformers': {
                    'required_version': '>=4.20.0',
                    'extras': [],
                    'import_name': 'transformers'
                },
                'torch': {
                    'required_version': '>=1.12.0',
                    'extras': ['cuda', 'rocm'],
                    'import_name': 'torch'
                },
                'accelerate': {
                    'required_version': '>=0.20.0',
                    'extras': [],
                    'import_name': 'accelerate'
                }
            },
            'llamafile': {
                # No Python dependencies, just executable
            },
            'llama-cpp-python': {
                'llama-cpp-python': {
                    'required_version': '>=0.2.0',
                    'extras': ['cuda', 'rocm', 'vulkan', 'metal'],
                    'import_name': 'llama_cpp'
                }
            }
        }
    
    def _check_dependency(self, dep_name: str, dep_config: Dict[str, Any]) -> DependencyInfo:
        """Check a specific dependency."""
        try:
            # Try to get installed version
            installed_version = None
            installed = False
            location = None
            
            try:
                # Check using pkg_resources
                dist = pkg_resources.get_distribution(dep_name)
                installed_version = dist.version
                installed = True
                location = dist.location
            except pkg_resources.DistributionNotFound:
                # Try importing directly
                import_name = dep_config.get('import_name', dep_name)
                try:
                    spec = importlib.util.find_spec(import_name)
                    if spec is not None:
                        installed = True
                        location = spec.origin
                        # Try to get version from module
                        try:
                            module = importlib.import_module(import_name)
                            if hasattr(module, '__version__'):
                                installed_version = module.__version__
                        except Exception:
                            pass
                except ImportError:
                    pass
            
            # Check version compatibility
            required_version = dep_config.get('required_version')
            compatible = True
            
            if installed and required_version and installed_version:
                try:
                    from packaging import version
                    # Parse requirement (e.g., ">=0.2.0")
                    if required_version.startswith('>='):
                        min_version = required_version[2:]
                        compatible = version.parse(installed_version) >= version.parse(min_version)
                    elif required_version.startswith('=='):
                        exact_version = required_version[2:]
                        compatible = version.parse(installed_version) == version.parse(exact_version)
                    elif required_version.startswith('>'):
                        min_version = required_version[1:]
                        compatible = version.parse(installed_version) > version.parse(min_version)
                except Exception as e:
                    logger.warning(f"Could not parse version requirement {required_version}: {e}")
                    compatible = True  # Assume compatible if we can't parse
            
            return DependencyInfo(
                name=dep_name,
                version=installed_version,
                installed=installed,
                required_version=required_version,
                compatible=compatible,
                location=location,
                extras=dep_config.get('extras', [])
            )
            
        except Exception as e:
            logger.error(f"Error checking dependency {dep_name}: {e}")
            return DependencyInfo(
                name=dep_name,
                version=None,
                installed=False,
                required_version=dep_config.get('required_version'),
                compatible=False,
                location=None,
                extras=dep_config.get('extras', [])
            )
    
    def check_system_requirements(self, backend_name: str) -> SystemRequirements:
        """Check system requirements for a backend."""
        requirements = {
            'ctransformers': {
                'python_version': (3, 7, 0),
                'memory_gb': 4.0,
                'disk_space_gb': 2.0
            },
            'transformers': {
                'python_version': (3, 8, 0),
                'memory_gb': 8.0,
                'disk_space_gb': 5.0
            },
            'llamafile': {
                'python_version': (3, 6, 0),  # Minimal Python requirement
                'memory_gb': 2.0,
                'disk_space_gb': 1.0
            },
            'llama-cpp-python': {
                'python_version': (3, 7, 0),
                'memory_gb': 4.0,
                'disk_space_gb': 3.0
            }
        }
        
        backend_reqs = requirements.get(backend_name, {})
        
        return SystemRequirements(
            python_version=backend_reqs.get('python_version', (3, 6, 0)),
            platform=self.system_info['platform'],
            architecture=self.system_info['architecture'],
            gpu_support=self._detect_gpu_support(),
            memory_gb=self._get_available_memory(),
            disk_space_gb=self._get_available_disk_space()
        )
    
    def _detect_gpu_support(self) -> Dict[str, bool]:
        """Detect available GPU support."""
        gpu_support = {
            'cuda': False,
            'rocm': False,
            'vulkan': False,
            'metal': False,
            'opencl': False
        }
        
        try:
            # Check NVIDIA CUDA
            result = subprocess.run(['nvidia-smi'], capture_output=True, text=True, timeout=10)
            if result.returncode == 0:
                gpu_support['cuda'] = True
        except (subprocess.TimeoutExpired, FileNotFoundError):
            pass
        
        try:
            # Check AMD ROCm
            result = subprocess.run(['rocm-smi'], capture_output=True, text=True, timeout=10)
            if result.returncode == 0:
                gpu_support['rocm'] = True
        except (subprocess.TimeoutExpired, FileNotFoundError):
            pass
        
        # Check for Apple Metal (macOS with Apple Silicon)
        if self.system_info['platform'] == 'Darwin':
            if 'arm' in self.system_info['architecture'].lower():
                gpu_support['metal'] = True
        
        # Check for Vulkan
        try:
            # Try to find Vulkan loader
            if self.system_info['platform'] == 'Windows':
                vulkan_paths = [
                    'C:\\Windows\\System32\\vulkan-1.dll',
                    'C:\\Windows\\SysWOW64\\vulkan-1.dll'
                ]
                gpu_support['vulkan'] = any(os.path.exists(path) for path in vulkan_paths)
            else:
                result = subprocess.run(['vulkaninfo'], capture_output=True, text=True, timeout=10)
                gpu_support['vulkan'] = result.returncode == 0
        except (subprocess.TimeoutExpired, FileNotFoundError):
            pass
        
        return gpu_support
    
    def _get_available_memory(self) -> float:
        """Get available system memory in GB."""
        try:
            import psutil
            memory = psutil.virtual_memory()
            return memory.total / (1024**3)  # Convert to GB
        except ImportError:
            # Fallback method without psutil
            if self.system_info['platform'] == 'Linux':
                try:
                    with open('/proc/meminfo', 'r') as f:
                        for line in f:
                            if line.startswith('MemTotal:'):
                                kb = int(line.split()[1])
                                return kb / (1024**2)  # Convert KB to GB
                except Exception:
                    pass
            return 8.0  # Default assumption
    
    def _get_available_disk_space(self) -> float:
        """Get available disk space in GB."""
        try:
            import shutil
            total, used, free = shutil.disk_usage(os.path.expanduser('~'))
            return free / (1024**3)  # Convert to GB
        except Exception:
            return 50.0  # Default assumption
    
    def get_missing_dependencies(self, backend_name: str) -> List[str]:
        """Get list of missing dependencies for a backend."""
        dependencies = self.detect_backend_dependencies(backend_name)
        missing = []
        
        for dep_name, dep_info in dependencies.items():
            if not dep_info.installed or not dep_info.compatible:
                missing.append(dep_name)
        
        return missing
    
    def get_installation_recommendations(self, backend_name: str) -> Dict[str, Any]:
        """Get installation recommendations for a backend."""
        dependencies = self.detect_backend_dependencies(backend_name)
        system_reqs = self.check_system_requirements(backend_name)
        gpu_support = self._detect_gpu_support()
        
        recommendations = {
            'backend_name': backend_name,
            'system_compatible': True,
            'missing_dependencies': [],
            'gpu_recommendations': [],
            'installation_notes': [],
            'estimated_download_size': '0 MB',
            'estimated_install_time': '1-2 minutes'
        }
        
        # Check Python version compatibility
        current_python = self.system_info['python_version']
        required_python = system_reqs.python_version
        
        if current_python < required_python:
            recommendations['system_compatible'] = False
            recommendations['installation_notes'].append(
                f"Python {required_python[0]}.{required_python[1]}+ required, "
                f"current: {current_python[0]}.{current_python[1]}.{current_python[2]}"
            )
        
        # Check missing dependencies
        for dep_name, dep_info in dependencies.items():
            if not dep_info.installed or not dep_info.compatible:
                recommendations['missing_dependencies'].append(dep_name)
        
        # GPU recommendations
        if gpu_support['cuda']:
            recommendations['gpu_recommendations'].append('CUDA acceleration available')
        if gpu_support['rocm']:
            recommendations['gpu_recommendations'].append('ROCm acceleration available')
        if gpu_support['metal']:
            recommendations['gpu_recommendations'].append('Metal acceleration available')
        if gpu_support['vulkan']:
            recommendations['gpu_recommendations'].append('Vulkan acceleration available')
        
        if not any(gpu_support.values()):
            recommendations['gpu_recommendations'].append('CPU-only mode (no GPU acceleration detected)')
        
        # Backend-specific recommendations
        if backend_name == 'ctransformers':
            recommendations['estimated_download_size'] = '50-100 MB'
            recommendations['installation_notes'].append('Recommended for easy GPU setup')
        elif backend_name == 'transformers':
            recommendations['estimated_download_size'] = '200-500 MB'
            recommendations['estimated_install_time'] = '3-5 minutes'
            recommendations['installation_notes'].append('Best for latest model support')
        elif backend_name == 'llamafile':
            recommendations['estimated_download_size'] = '10-20 MB'
            recommendations['installation_notes'].append('Single executable, no Python dependencies')
        elif backend_name == 'llama-cpp-python':
            recommendations['estimated_download_size'] = '100-200 MB'
            recommendations['estimated_install_time'] = '5-10 minutes'
            recommendations['installation_notes'].append('May require build tools on some systems')
        
        return recommendations
    
    def validate_environment(self) -> Dict[str, Any]:
        """Validate the current environment for backend installations."""
        validation = {
            'valid': True,
            'issues': [],
            'warnings': [],
            'recommendations': []
        }
        
        # Check Python version
        python_version = self.system_info['python_version']
        if python_version < (3, 7, 0):
            validation['valid'] = False
            validation['issues'].append(f"Python 3.7+ required, current: {python_version}")
        
        # Check pip availability
        if not self.system_info['pip_version']:
            validation['valid'] = False
            validation['issues'].append("pip not available")
        
        # Check virtual environment
        venv_info = self.system_info['virtual_env']
        if not venv_info['in_venv']:
            validation['warnings'].append("Not running in virtual environment")
            validation['recommendations'].append("Consider using a virtual environment")
        
        # Check disk space
        disk_space = self._get_available_disk_space()
        if disk_space < 5.0:
            validation['warnings'].append(f"Low disk space: {disk_space:.1f} GB available")
        
        # Check memory
        memory = self._get_available_memory()
        if memory < 4.0:
            validation['warnings'].append(f"Low memory: {memory:.1f} GB available")
        
        return validation