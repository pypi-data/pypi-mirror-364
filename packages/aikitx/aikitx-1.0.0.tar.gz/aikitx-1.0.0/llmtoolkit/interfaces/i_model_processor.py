"""
Model Processor Interface

This module defines the IModelProcessor interface, which addons can implement
to provide custom model processing functionality.
"""

from abc import ABC, abstractmethod
from typing import Dict, Any, Optional, List, Tuple, Union

from llmtoolkit.app.models.gguf_model import GGUFModel

class ProcessingResult:
    """Class representing the result of a model processing operation."""
    
    def __init__(self, 
                 success: bool, 
                 result: Any = None, 
                 error_message: Optional[str] = None,
                 metrics: Optional[Dict[str, Any]] = None):
        """
        Initialize a processing result.
        
        Args:
            success: Whether the processing was successful
            result: The result of the processing operation
            error_message: Error message if the processing failed
            metrics: Optional metrics about the processing operation
        """
        self.success = success
        self.result = result
        self.error_message = error_message
        self.metrics = metrics or {}

class IModelProcessor(ABC):
    """
    Interface for addons that provide model processing functionality.
    
    Addons can implement this interface to provide custom processing capabilities
    for GGUF models, such as inference, fine-tuning, or analysis.
    """
    
    @abstractmethod
    def get_capabilities(self) -> List[str]:
        """
        Get the processing capabilities provided by this addon.
        
        Returns:
            List of capability identifiers
        """
        pass
    
    @abstractmethod
    def get_supported_models(self) -> List[str]:
        """
        Get the model types supported by this processor.
        
        Returns:
            List of supported model type identifiers or patterns
        """
        pass
    
    @abstractmethod
    def can_process(self, model: GGUFModel) -> bool:
        """
        Check if this processor can process a specific model.
        
        Args:
            model: The model to check
            
        Returns:
            True if the model can be processed, False otherwise
        """
        pass
    
    @abstractmethod
    def process(self, 
                model: GGUFModel, 
                input_data: Any, 
                options: Optional[Dict[str, Any]] = None) -> ProcessingResult:
        """
        Process a model with the given input data and options.
        
        Args:
            model: The model to process
            input_data: Input data for the processing operation
            options: Optional processing options
            
        Returns:
            ProcessingResult object containing the result of the processing operation
        """
        pass
    
    @abstractmethod
    def get_input_schema(self) -> Dict[str, Any]:
        """
        Get the schema for the input data expected by this processor.
        
        Returns:
            JSON Schema object describing the expected input data
        """
        pass
    
    @abstractmethod
    def get_options_schema(self) -> Dict[str, Any]:
        """
        Get the schema for the options accepted by this processor.
        
        Returns:
            JSON Schema object describing the accepted options
        """
        pass