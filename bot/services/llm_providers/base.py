"""
Base LLM Provider Interface
Defines the standard interface for all LLM providers
"""

from abc import ABC, abstractmethod
from typing import Optional, List, Dict, Any
from dataclasses import dataclass
from enum import Enum


class TaskType(Enum):
    """Types of tasks for routing decisions"""
    CHAT = "chat"
    REASONING = "reasoning"
    CODING = "coding"
    LONG_CONTEXT = "long_context"
    VISION = "vision"
    SPEED_CRITICAL = "speed_critical"
    RESEARCH = "research"
    ANALYSIS = "analysis"


@dataclass
class LLMResponse:
    """Standardized response from any LLM provider"""
    content: str
    model: str
    provider: str
    tokens_used: Optional[int] = None
    finish_reason: Optional[str] = None
    success: bool = True
    error: Optional[str] = None


@dataclass
class ProviderCapabilities:
    """Describes what a provider can do"""
    supports_vision: bool = False
    supports_audio: bool = False
    supports_streaming: bool = True
    max_context_tokens: int = 4096
    supports_function_calling: bool = False
    avg_latency_ms: int = 500
    free_tier_limits: Dict[str, Any] = None
    
    def __post_init__(self):
        if self.free_tier_limits is None:
            self.free_tier_limits = {}


class BaseLLMProvider(ABC):
    """Abstract base class for all LLM providers"""
    
    name: str = "base"
    description: str = "Base LLM Provider"
    
    def __init__(self, api_key: Optional[str] = None, **kwargs):
        self.api_key = api_key
        self.config = kwargs
        self._client = None
    
    @abstractmethod
    async def chat(
        self, 
        messages: List[Dict[str, str]], 
        system_prompt: Optional[str] = None,
        **kwargs
    ) -> LLMResponse:
        """Send a chat completion request"""
        pass
    
    @abstractmethod
    async def analyze_image(
        self, 
        image_data: bytes, 
        prompt: str,
        **kwargs
    ) -> LLMResponse:
        """Analyze an image (if supported)"""
        pass
    
    @abstractmethod
    def get_capabilities(self) -> ProviderCapabilities:
        """Return provider capabilities"""
        pass
    
    @abstractmethod
    def get_default_model(self) -> str:
        """Return the default model for this provider"""
        pass
    
    def is_available(self) -> bool:
        """Check if the provider is properly configured"""
        return self.api_key is not None and len(self.api_key) > 0
    
    def supports_task(self, task_type: TaskType) -> bool:
        """Check if provider supports a specific task type"""
        capabilities = self.get_capabilities()
        
        if task_type == TaskType.VISION:
            return capabilities.supports_vision
        if task_type == TaskType.LONG_CONTEXT:
            return capabilities.max_context_tokens >= 32000
        if task_type == TaskType.SPEED_CRITICAL:
            return capabilities.avg_latency_ms < 300
        
        return True
    
    def get_priority_for_task(self, task_type: TaskType) -> int:
        """
        Return priority score (1-10) for a task type.
        Higher = better suited for the task.
        """
        return 5  # Default neutral priority