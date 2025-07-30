"""
Model Provider Interface

This module defines the IModelProvider interface, which addons can implement
to provide custom model loading functionality.
"""

from abc import ABC, abstractmethod
from typing import Dict, Any, Optional

from llmtoolkit.app.models.gguf_model import GGUFModel

class IModelProvider(ABC):
    """
    Interface for addons that provide model loading functionality.
    
    Addons can implement this interface to provide custom model loading capabilities.
    """
    
    @abstractmethod
    def load_model(self, file_path: str) -> GGUFModel:
        """
        Load a model from the specified path.
        
        Args:
            file_path: Path to the model file
            
        Returns:
            Loaded GGUFModel object
            
        Raises:
            Exception: If the model cannot be loaded
        """
        pass
    
    @abstractmethod
    def get_model_info(self, model_id: str) -> Dict[str, Any]:
        """
        Get detailed information about a model.
        
        Args:
            model_id: ID of the model
            
        Returns:
            Dictionary containing model information
            
        Raises:
            Exception: If the model information cannot be retrieved
        """
        pass
    
    @abstractmethod
    def unload_model(self, model_id: str) -> bool:
        """
        Unload a model from memory.
        
        Args:
            model_id: ID of the model to unload
            
        Returns:
            True if the model was unloaded successfully, False otherwise
        """
        pass