"""
OpenRouter Provider
Best for: Flexibility - aggregates many free models
Free Tier: ~20 RPM, 200 requests/day
"""

import asyncio
from typing import List, Dict, Optional
from .base import BaseLLMProvider, LLMResponse, ProviderCapabilities, TaskType

try:
    from openai import AsyncOpenAI
    OPENAI_AVAILABLE = True
except ImportError:
    OPENAI_AVAILABLE = False


class OpenRouterProvider(BaseLLMProvider):
    """OpenRouter API Provider - Aggregates multiple models"""
    
    name = "openrouter"
    description = "OpenRouter - Access to multiple free and paid models"
    
    def __init__(self, api_key: Optional[str] = None, **kwargs):
        super().__init__(api_key, **kwargs)
        # Default to a free model through OpenRouter
        self._model_name = kwargs.get('model', 'meta-llama/llama-3.3-70b-instruct:free')
        self._base_url = "https://openrouter.ai/api/v1"
        
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
        """Send a chat completion request via OpenRouter"""
        
        if not self.is_available():
            return LLMResponse(
                content="OpenRouter provider not configured",
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
                content=f"OpenRouter error: {str(e)}",
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
        """OpenRouter supports vision through specific models"""
        return LLMResponse(
            content="OpenRouter vision support depends on selected model",
            model=self._model_name,
            provider=self.name,
            success=False,
            error="Vision requires model-specific configuration"
        )
    
    def get_capabilities(self) -> ProviderCapabilities:
        """Return OpenRouter capabilities (varies by model)"""
        return ProviderCapabilities(
            supports_vision=True,  # Depends on model
            supports_audio=False,
            supports_streaming=True,
            max_context_tokens=128000,  # Depends on model
            supports_function_calling=True,
            avg_latency_ms=600,
            free_tier_limits={
                "requests_per_minute": 20,
                "requests_per_day": 200
            }
        )
    
    def get_default_model(self) -> str:
        """Return default OpenRouter model"""
        return self._model_name
    
    def get_priority_for_task(self, task_type: TaskType) -> int:
        """OpenRouter is flexible but depends on model"""
        priorities = {
            TaskType.CHAT: 7,
            TaskType.CODING: 7,
            TaskType.REASONING: 7,
            TaskType.ANALYSIS: 7,
            TaskType.RESEARCH: 7,
            TaskType.SPEED_CRITICAL: 5,
            TaskType.LONG_CONTEXT: 6,
            TaskType.VISION: 5  # Depends on model
        }
        return priorities.get(task_type, 6)