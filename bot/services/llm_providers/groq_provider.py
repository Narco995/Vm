"""
Groq Provider
Best for: Ultra-fast responses, real-time chat
Free Tier: ~30 RPM, 30k-100k TPM
"""

import asyncio
from typing import List, Dict, Optional
from .base import BaseLLMProvider, LLMResponse, ProviderCapabilities, TaskType

try:
    from openai import AsyncOpenAI
    OPENAI_AVAILABLE = True
except ImportError:
    OPENAI_AVAILABLE = False


class GroqProvider(BaseLLMProvider):
    """Groq API Provider - OpenAI-compatible endpoints"""
    
    name = "groq"
    description = "Groq - Ultra-fast LLM inference"
    
    def __init__(self, api_key: Optional[str] = None, **kwargs):
        super().__init__(api_key, **kwargs)
        self._model_name = kwargs.get('model', 'llama-3.3-70b-versatile')
        self._base_url = "https://api.groq.com/openai/v1"
        
        if OPENAI_AVAILABLE and self.api_key:
            self._client = AsyncOpenAI(
                api_key=self.api_key,
                base_url=self._base_url
            )
    
    async def chat(
        self, 
        messages: List[Dict[str, str]], 
        system_prompt: Optional[str] = None,
        **kwargs
    ) -> LLMResponse:
        """Send a chat completion request to Groq"""
        
        if not self.is_available():
            return LLMResponse(
                content="Groq provider not configured",
                model=self._model_name,
                provider=self.name,
                success=False,
                error="API key not provided"
            )
        
        if not OPENAI_AVAILABLE:
            return LLMResponse(
                content="openai package not installed",
                model=self._model_name,
                provider=self.name,
                success=False,
                error="Missing dependency"
            )
        
        try:
            # Build messages list
            api_messages = []
            if system_prompt:
                api_messages.append({"role": "system", "content": system_prompt})
            api_messages.extend(messages)
            
            # Create completion
            response = await self._client.chat.completions.create(
                model=self._model_name,
                messages=api_messages,
                max_tokens=kwargs.get('max_tokens', 4096),
                temperature=kwargs.get('temperature', 0.7)
            )
            
            return LLMResponse(
                content=response.choices[0].message.content,
                model=self._model_name,
                provider=self.name,
                tokens_used=response.usage.total_tokens if hasattr(response, 'usage') else None,
                finish_reason=response.choices[0].finish_reason,
                success=True
            )
            
        except Exception as e:
            return LLMResponse(
                content=f"Groq error: {str(e)}",
                model=self._model_name,
                provider=self.name,
                success=False,
                error=str(e)
            )
    
    async def analyze_image(
        self, 
        image_data: bytes, 
        prompt: str,
        **kwargs
    ) -> LLMResponse:
        """Groq doesn't support vision yet"""
        return LLMResponse(
            content="Groq does not support image analysis",
            model=self._model_name,
            provider=self.name,
            success=False,
            error="Vision not supported"
        )
    
    def get_capabilities(self) -> ProviderCapabilities:
        """Return Groq capabilities"""
        return ProviderCapabilities(
            supports_vision=False,
            supports_audio=False,
            supports_streaming=True,
            max_context_tokens=131072,  # Up to 128k depending on model
            supports_function_calling=True,
            avg_latency_ms=100,  # Very fast!
            free_tier_limits={
                "requests_per_minute": 30,
                "tokens_per_minute": 100000
            }
        )
    
    def get_default_model(self) -> str:
        """Return default Groq model"""
        return self._model_name
    
    def get_priority_for_task(self, task_type: TaskType) -> int:
        """Groq is best for speed-critical tasks"""
        priorities = {
            TaskType.SPEED_CRITICAL: 10,  # Excellent
            TaskType.CHAT: 9,
            TaskType.CODING: 8,
            TaskType.REASONING: 7,
            TaskType.LONG_CONTEXT: 6,
            TaskType.VISION: 0,  # Not supported
            TaskType.RESEARCH: 6,
            TaskType.ANALYSIS: 7
        }
        return priorities.get(task_type, 6)