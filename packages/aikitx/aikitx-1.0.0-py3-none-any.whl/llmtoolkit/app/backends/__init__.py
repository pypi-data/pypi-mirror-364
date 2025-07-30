"""
Backend implementations for the GGUF loader application.

This module contains all the backend implementations for different
model inference engines.

Backends are registered automatically when the BackendManager is initialized
to avoid circular import issues.
"""

# Backend classes are imported when needed by the BackendManager
# to avoid circular import issues during module initialization

__all__ = [
    'CtransformersBackend',
    'TransformersBackend', 
    'LlamafileBackend',
    'LlamaCppPythonBackend'
]