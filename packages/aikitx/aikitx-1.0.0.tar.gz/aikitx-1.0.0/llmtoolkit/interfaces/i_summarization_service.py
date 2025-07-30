"""
Summarization Service Interface

Defines the interface for document summarization services.
"""

from abc import ABC, abstractmethod
from typing import List


class ISummarizationService(ABC):
    """Interface for summarization service operations"""
    
    @abstractmethod
    def summarize_text(self, text: str, style: str = "concise") -> str:
        """Summarize provided text"""
        pass
    
    @abstractmethod
    def summarize_file(self, file_path: str, style: str = "concise") -> str:
        """Summarize text from file"""
        pass
    
    @abstractmethod
    def get_supported_formats(self) -> List[str]:
        """Get list of supported file formats"""
        pass