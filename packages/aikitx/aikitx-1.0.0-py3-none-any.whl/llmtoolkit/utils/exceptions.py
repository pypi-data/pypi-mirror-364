"""
Custom Exceptions for GGUF Loader App

This module defines custom exceptions used throughout the application.
"""

class GGUFLoaderError(Exception):
    """Base exception class for all GGUF Loader application errors."""
    def __init__(self, message="An error occurred in the GGUF Loader application", 
                 error_code=None, details=None):
        self.message = message
        self.error_code = error_code
        self.details = details
        super().__init__(self.message)


# UI Layer Exceptions
class UIError(GGUFLoaderError):
    """Base exception for UI-related errors."""
    def __init__(self, message="A UI error occurred", error_code=None, details=None):
        super().__init__(message, error_code, details)


class DialogError(UIError):
    """Exception raised when there's an error with dialogs."""
    def __init__(self, message="Error displaying dialog", error_code=None, details=None):
        super().__init__(message, error_code, details)


class RenderError(UIError):
    """Exception raised when there's an error rendering UI components."""
    def __init__(self, message="Error rendering UI component", error_code=None, details=None):
        super().__init__(message, error_code, details)


# Core Layer Exceptions
class CoreError(GGUFLoaderError):
    """Base exception for core application errors."""
    def __init__(self, message="A core application error occurred", error_code=None, details=None):
        super().__init__(message, error_code, details)


class ConfigError(CoreError):
    """Exception raised when there's a configuration error."""
    def __init__(self, message="Configuration error", error_code=None, details=None):
        super().__init__(message, error_code, details)


class EventError(CoreError):
    """Exception raised when there's an error with the event system."""
    def __init__(self, message="Event system error", error_code=None, details=None):
        super().__init__(message, error_code, details)


# Model Layer Exceptions
class ModelError(GGUFLoaderError):
    """Base exception for model-related errors."""
    def __init__(self, message="A model error occurred", error_code=None, details=None):
        super().__init__(message, error_code, details)


class ModelLoadError(ModelError):
    """Exception raised when there's an error loading a model."""
    def __init__(self, message="Error loading model", error_code=None, details=None):
        super().__init__(message, error_code, details)


class ModelFormatError(ModelError):
    """Exception raised when there's an error with the model format."""
    def __init__(self, message="Invalid model format", error_code=None, details=None):
        super().__init__(message, error_code, details)


class ModelMemoryError(ModelError):
    """Exception raised when there's not enough memory for a model."""
    def __init__(self, message="Not enough memory for model", error_code=None, details=None):
        super().__init__(message, error_code, details)


# Addon Layer Exceptions
class AddonError(GGUFLoaderError):
    """Base exception for addon-related errors."""
    def __init__(self, message="An addon error occurred", error_code=None, details=None):
        super().__init__(message, error_code, details)


class AddonLoadError(AddonError):
    """Exception raised when there's an error loading an addon."""
    def __init__(self, message="Error loading addon", error_code=None, details=None):
        super().__init__(message, error_code, details)


class AddonCompatibilityError(AddonError):
    """Exception raised when an addon is incompatible."""
    def __init__(self, message="Addon compatibility error", error_code=None, details=None):
        super().__init__(message, error_code, details)


class AddonDependencyError(AddonError):
    """Exception raised when there's an addon dependency error."""
    def __init__(self, message="Addon dependency error", error_code=None, details=None):
        super().__init__(message, error_code, details)


# File System Exceptions
class FileSystemError(GGUFLoaderError):
    """Base exception for file system errors."""
    def __init__(self, message="A file system error occurred", error_code=None, details=None):
        super().__init__(message, error_code, details)


class FileAccessError(FileSystemError):
    """Exception raised when there's an error accessing a file."""
    def __init__(self, message="Error accessing file", error_code=None, details=None):
        super().__init__(message, error_code, details)


class FileFormatError(FileSystemError):
    """Exception raised when there's an error with the file format."""
    def __init__(self, message="Invalid file format", error_code=None, details=None):
        super().__init__(message, error_code, details)