"""
Chat configuration constants for improved text generation
"""

# Maximum tokens for generation
MAX_TOKENS = 512

# English system prompts
ENGLISH_SYSTEM_PROMPTS = {
    "assistant": {
        "prompt": "You are a helpful AI assistant. Answer questions clearly and concisely in English. Provide accurate and useful information while being friendly and professional."
    },
    "creative": {
        "prompt": "You are a creative AI assistant. Help users with creative writing, brainstorming, and imaginative tasks. Be inspiring and original while maintaining clarity."
    },
    "technical": {
        "prompt": "You are a technical AI assistant. Provide detailed, accurate technical information and explanations. Use precise language and include relevant examples when helpful."
    },
    "concise": {
        "prompt": "You are a concise AI assistant. Provide brief, direct answers while ensuring accuracy. Get straight to the point without unnecessary elaboration."
    }
}

# Default generation parameters
DEFAULT_TEMPERATURE = 0.7
DEFAULT_TOP_P = 0.9
DEFAULT_TOP_K = 40
DEFAULT_REPEAT_PENALTY = 1.1

# Stop tokens for proper conversation flow
STOP_TOKENS = [
    "<|im_end|>", 
    "</s>", 
    "user:", 
    "assistant:", 
    "###",
    "\nHuman:", 
    "\nUser:", 
    "Human:", 
    "User:",
    "\n\nUser:",
    "\n\nHuman:"
]