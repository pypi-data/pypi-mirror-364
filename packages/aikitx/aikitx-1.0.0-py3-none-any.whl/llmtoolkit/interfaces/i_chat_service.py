"""
Chat Service Interface

Defines the interface for chat conversation management.
"""

from abc import ABC, abstractmethod
from typing import List, TYPE_CHECKING

if TYPE_CHECKING:
    from ..app.services.chat_service import ChatMessage


class IChatService(ABC):
    """Interface for chat service operations"""
    
    @abstractmethod
    def send_message(self, message: str) -> str:
        """Send message and get AI response"""
        pass
    
    @abstractmethod
    def get_conversation_history(self) -> List['ChatMessage']:
        """Get current conversation history"""
        pass
    
    @abstractmethod
    def clear_conversation(self) -> None:
        """Clear current conversation"""
        pass
    
    @abstractmethod
    def set_system_prompt(self, prompt: str) -> None:
        """Set system prompt for chat"""
        pass