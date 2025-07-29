"""
TNSAAI Python Client

A powerful, OpenAI-compatible Python SDK for TNSA NGen3 Pro and Lite Models.
"""

from .client import TNSA
from .async_client import AsyncTNSA
from .exceptions import (
    TNSAError,
    AuthenticationError,
    RateLimitError,
    ModelNotFoundError,
    InvalidRequestError,
    APIConnectionError,
    APITimeoutError,
)
from .models.chat import (
    ChatMessage,
    ChatCompletion,
    ChatCompletionChoice,
    ChatCompletionChunk,
    ChatCompletionDelta,
)
from .models.common import (
    Usage,
    Model,
    ModelPricing,
    Conversation,
)

__version__ = "1.0.0"
__author__ = "TNSA AI"
__email__ = "info@tnsaai.com"

__all__ = [
    "TNSA",
    "AsyncTNSA",
    "TNSAError",
    "AuthenticationError", 
    "RateLimitError",
    "ModelNotFoundError",
    "InvalidRequestError",
    "APIConnectionError",
    "APITimeoutError",
    "ChatMessage",
    "ChatCompletion",
    "ChatCompletionChoice",
    "ChatCompletionChunk",
    "ChatCompletionDelta",
    "Usage",
    "Model",
    "ModelPricing",
    "Conversation",
]