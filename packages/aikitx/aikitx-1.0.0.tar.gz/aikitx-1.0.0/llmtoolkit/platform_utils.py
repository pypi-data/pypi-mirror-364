"""
Platform-specific utilities for cross-platform compatibility.

This module provides utilities for handling platform-specific functionality
and ensuring the application works correctly across Windows, macOS, and Linux.
"""

import os
import sys
import platform
import subprocess
import logging
from pathlib import Path
from typing import Dict, Optional, List, Tuple

logger = logging.getLogger(__name__)


class PlatformManager:
    """Manages platform-specific functionality and compatibility."""
    
    def __init__(self):
        self.system = platform.system().lower()
        self.is_windows = self.system == 'windows'
        self.is_macos = self.system == 'darwin'
        self.is_linux = self.system == 'linux'
        self.is_posix = os.name == 'posix'
        
    def get_platform_info(self) -> Dict[str, str]:
        """Get comprehensive platform information."""
        return {
            'system': platform.system(),
            'release': platform.release(),
            'version': platform.version(),
            'machine': platform.machine(),
            'processor': platform.processor(),
            'architecture': platform.architecture()[0],
            'python_version': platform.python_version(),
            'python_implementation': platform.python_implementation(),
            'is_64bit': platform.architecture()[0] == '64bit',
        }
    
    def get_executable_extension(self) -> str:
        """Get the appropriate executable extension for the platform."""
        return '.exe' if self.is_windows else ''
    
    def get_script_extension(self) -> str:
        """Get the appropriate script extension for the platform."""
        if self.is_windows:
            return '.bat'
        else:
            return '.sh'
    
    def get_config_directory(self, app_name: str = 'llmtoolkit') -> Path:
        """Get the appropriate configuration directory for the platform."""
        if self.is_windows:
            # Windows: Use APPDATA
            base_dir = os.environ.get('APPDATA', os.path.expanduser('~'))
            return Path(base_dir) / app_name
        elif self.is_macos:
            # macOS: Use ~/Library/Application Support
            return Path.home() / 'Library' / 'Application Support' / app_name
        else:
            # Linux/Unix: Use XDG_CONFIG_HOME or ~/.config
            config_home = os.environ.get('XDG_CONFIG_HOME', os.path.expanduser('~/.config'))
            return Path(config_home) / app_name
    
    def get_data_directory(self, app_name: str = 'llmtoolkit') -> Path:
        """Get the appropriate data directory for the platform."""
        if self.is_windows:
            # Windows: Use LOCALAPPDATA
            base_dir = os.environ.get('LOCALAPPDATA', os.environ.get('APPDATA', os.path.expanduser('~')))
            return Path(base_dir) / app_name
        elif self.is_macos:
            # macOS: Use ~/Library/Application Support
            return Path.home() / 'Library' / 'Application Support' / app_name
        else:
            # Linux/Unix: Use XDG_DATA_HOME or ~/.local/share
            data_home = os.environ.get('XDG_DATA_HOME', os.path.expanduser('~/.local/share'))
            return Path(data_home) / app_name
    
    def get_cache_directory(self, app_name: str = 'llmtoolkit') -> Path:
        """Get the appropriate cache directory for the platform."""
        if self.is_windows:
            # Windows: Use TEMP or LOCALAPPDATA
            base_dir = os.environ.get('LOCALAPPDATA', os.environ.get('TEMP', os.path.expanduser('~')))
            return Path(base_dir) / app_name / 'cache'
        elif self.is_macos:
            # macOS: Use ~/Library/Caches
            return Path.home() / 'Library' / 'Caches' / app_name
        else:
            # Linux/Unix: Use XDG_CACHE_HOME or ~/.cache
            cache_home = os.environ.get('XDG_CACHE_HOME', os.path.expanduser('~/.cache'))
            return Path(cache_home) / app_name
    
    def ensure_directory_exists(self, directory: Path) -> bool:
        """Ensure a directory exists, creating it if necessary."""
        try:
            directory.mkdir(parents=True, exist_ok=True)
            return True
        except Exception as e:
            logger.error(f"Failed to create directory {directory}: {e}")
            return False
    
    def check_gui_availability(self) -> Tuple[bool, Optional[str]]:
        """Check if GUI is available on the current platform."""
        try:
            if self.is_windows:
                # On Windows, GUI should always be available
                return True, None
            elif self.is_macos:
                # On macOS, check if we're in a GUI session
                if os.environ.get('DISPLAY') or os.environ.get('TERM_PROGRAM'):
                    return True, None
                else:
                    return False, "No GUI session detected (SSH or headless mode)"
            else:
                # On Linux, check for X11 or Wayland
                if os.environ.get('DISPLAY') or os.environ.get('WAYLAND_DISPLAY'):
                    return True, None
                else:
                    return False, "No X11 or Wayland display available"
        except Exception as e:
            return False, f"Error checking GUI availability: {e}"
    
    def get_python_executable(self) -> str:
        """Get the path to the Python executable."""
        return sys.executable
    
    def get_pip_executable(self) -> str:
        """Get the path to the pip executable."""
        python_exe = self.get_python_executable()
        if self.is_windows:
            # On Windows, try to find pip.exe in the same directory as python.exe
            python_dir = Path(python_exe).parent
            pip_exe = python_dir / 'Scripts' / 'pip.exe'
            if pip_exe.exists():
                return str(pip_exe)
        
        # Fallback: use python -m pip
        return f'"{python_exe}" -m pip'
    
    def run_command(self, command: List[str], **kwargs) -> subprocess.CompletedProcess:
        """Run a command with platform-appropriate settings."""
        if self.is_windows:
            # On Windows, ensure proper shell handling
            kwargs.setdefault('shell', True)
            kwargs.setdefault('creationflags', subprocess.CREATE_NO_WINDOW)
        
        return subprocess.run(command, **kwargs)
    
    def get_environment_variables(self) -> Dict[str, str]:
        """Get platform-specific environment variables."""
        env_vars = {}
        
        if self.is_windows:
            # Windows-specific environment variables
            env_vars.update({
                'PYTHONIOENCODING': 'utf-8',
                'PYTHONLEGACYWINDOWSSTDIO': '1',
            })
        elif self.is_macos:
            # macOS-specific environment variables
            env_vars.update({
                'PYTHONIOENCODING': 'utf-8',
            })
        else:
            # Linux-specific environment variables
            env_vars.update({
                'PYTHONIOENCODING': 'utf-8',
            })
        
        return env_vars
    
    def setup_environment(self) -> None:
        """Set up platform-specific environment variables."""
        env_vars = self.get_environment_variables()
        for key, value in env_vars.items():
            if key not in os.environ:
                os.environ[key] = value
                logger.debug(f"Set environment variable {key}={value}")
    
    def get_font_directories(self) -> List[Path]:
        """Get platform-specific font directories."""
        font_dirs = []
        
        if self.is_windows:
            # Windows font directories
            font_dirs.extend([
                Path(os.environ.get('WINDIR', 'C:\\Windows')) / 'Fonts',
                Path.home() / 'AppData' / 'Local' / 'Microsoft' / 'Windows' / 'Fonts',
            ])
        elif self.is_macos:
            # macOS font directories
            font_dirs.extend([
                Path('/System/Library/Fonts'),
                Path('/Library/Fonts'),
                Path.home() / 'Library' / 'Fonts',
            ])
        else:
            # Linux font directories
            font_dirs.extend([
                Path('/usr/share/fonts'),
                Path('/usr/local/share/fonts'),
                Path.home() / '.fonts',
                Path.home() / '.local' / 'share' / 'fonts',
            ])
        
        # Filter to existing directories
        return [d for d in font_dirs if d.exists()]
    
    def get_temp_directory(self) -> Path:
        """Get the appropriate temporary directory for the platform."""
        import tempfile
        return Path(tempfile.gettempdir())
    
    def is_admin(self) -> bool:
        """Check if the current process has administrator/root privileges."""
        try:
            if self.is_windows:
                import ctypes
                return ctypes.windll.shell32.IsUserAnAdmin() != 0
            else:
                return os.geteuid() == 0
        except Exception:
            return False
    
    def get_system_info(self) -> Dict[str, str]:
        """Get comprehensive system information for debugging."""
        info = self.get_platform_info()
        
        # Add additional system information
        try:
            info['hostname'] = platform.node()
            info['user'] = os.environ.get('USER', os.environ.get('USERNAME', 'unknown'))
            info['home_directory'] = str(Path.home())
            info['current_directory'] = str(Path.cwd())
            info['python_executable'] = self.get_python_executable()
            info['is_admin'] = str(self.is_admin())
            
            # GUI availability
            gui_available, gui_error = self.check_gui_availability()
            info['gui_available'] = str(gui_available)
            if gui_error:
                info['gui_error'] = gui_error
            
            # Environment variables
            important_env_vars = [
                'PATH', 'PYTHONPATH', 'DISPLAY', 'WAYLAND_DISPLAY',
                'APPDATA', 'LOCALAPPDATA', 'XDG_CONFIG_HOME', 'XDG_DATA_HOME'
            ]
            for var in important_env_vars:
                value = os.environ.get(var)
                if value:
                    info[f'env_{var}'] = value
                    
        except Exception as e:
            info['system_info_error'] = str(e)
        
        return info


# Global platform manager instance
platform_manager = PlatformManager()


def get_platform_manager() -> PlatformManager:
    """Get the global platform manager instance."""
    return platform_manager


def setup_platform_environment():
    """Set up platform-specific environment for the application."""
    platform_manager.setup_environment()
    
    # Ensure required directories exist
    config_dir = platform_manager.get_config_directory()
    data_dir = platform_manager.get_data_directory()
    cache_dir = platform_manager.get_cache_directory()
    
    for directory in [config_dir, data_dir, cache_dir]:
        platform_manager.ensure_directory_exists(directory)
    
    logger.info(f"Platform setup complete for {platform_manager.system}")
    logger.debug(f"Config directory: {config_dir}")
    logger.debug(f"Data directory: {data_dir}")
    logger.debug(f"Cache directory: {cache_dir}")


if __name__ == '__main__':
    # Test the platform utilities
    pm = get_platform_manager()
    info = pm.get_system_info()
    
    print("Platform Information:")
    for key, value in info.items():
        print(f"  {key}: {value}")