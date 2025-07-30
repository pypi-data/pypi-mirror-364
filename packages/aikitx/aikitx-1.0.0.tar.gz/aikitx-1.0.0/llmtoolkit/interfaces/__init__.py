"""
Public interfaces for the GGUF Loader App.

This package contains the core service interfaces for the application.
"""

# Import and export interfaces
from .i_model_provider import IModelProvider
from .i_model_processor import IModelProcessor, ProcessingResult
from .i_model_service import IModelService
from .i_chat_service import IChatService
from .i_summarization_service import ISummarizationService

__all__ = [
    'IModelProvider',
    'IModelProcessor',
    'ProcessingResult',
    'IModelService',
    'IChatService',
    'ISummarizationService'
]