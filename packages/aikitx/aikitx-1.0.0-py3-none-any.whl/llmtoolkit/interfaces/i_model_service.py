"""
Model Service Interface

Defines the interface for core model loading and inference services.
"""

from abc import ABC, abstractmethod
from typing import Dict, Optional, TYPE_CHECKING

if TYPE_CHECKING:
    from ..app.models.gguf_model import GGUFModel


class IModelService(ABC):
    """Interface for model service operations"""
    
    @abstractmethod
    def load_model(self, file_path: str) -> 'GGUFModel':
        """Load a GGUF model from file"""
        pass
    
    @abstractmethod
    def get_current_model(self) -> Optional['GGUFModel']:
        """Get currently loaded model"""
        pass
    
    @abstractmethod
    def generate(self, prompt: str, system_prompt: str = None, 
                temperature: float = None, max_tokens: int = None) -> str:
        """Generate text with optional parameter overrides"""
        pass
    
    @abstractmethod
    def get_model_info(self, model_id: str) -> Dict:
        """Get detailed model information"""
        pass
    
    @abstractmethod
    def unload_model(self) -> bool:
        """Unload current model"""
        pass