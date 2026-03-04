"""
DeepSeek Provider
Best for: Coding, math, complex reasoning
Free Tier: 5M free tokens (new users)
"""

import asyncio
from typing import List, Dict, Optional
from .base import BaseLLMProvider, LLMResponse, ProviderCapabilities, TaskType

try:
    from openai import AsyncOpenAI
    OPENAI_AVAILABLE = True
except ImportError:
    OPENAI_AVAILABLE = False


class DeepSeekProvider(BaseLLMProvider):
    """DeepSeek API Provider - OpenAI-compatible endpoints"""
    
    name = "deepseek"
    description = "DeepSeek - High performance reasoning & coding"
    
    def __init__(self, api_key: Optional[str] = None, **kwargs):
        super().__init__(api_key, **kwargs)
        self._model_name = kwargs.get('model', 'deepseek-chat')
        self._base_url = "https://api.deepseek.com/v1"
        
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
        """Send a chat completion request to DeepSeek"""
        
        if not self.is_available():
            return LLMResponse(
                content="DeepSeek provider not configured",
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
                content=f"DeepSeek error: {str(e)}",
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
        """DeepSeek doesn't currently support vision"""
        return LLMResponse(
            content="DeepSeek does not support image analysis",
            model=self._model_name,
            provider=self.name,
            success=False,
            error="Vision not supported"
        )
    
    def get_capabilities(self) -> ProviderCapabilities:
        """Return DeepSeek capabilities"""
        return ProviderCapabilities(
            supports_vision=False,
            supports_audio=False,
            supports_streaming=True,
            max_context_tokens=64000,
            supports_function_calling=True,
            avg_latency_ms=400,
            free_tier_limits={
                "free_tokens_new_users": "5M",
                "low_cost_scaling": True
            }
        )
    
    def get_default_model(self) -> str:
        """Return default DeepSeek model"""
        return self._model_name
    
    def get_priority_for_task(self, task_type: TaskType) -> int:
        """DeepSeek excels at coding and reasoning"""
        priorities = {
            TaskType.CODING: 10,  # Excellent
            TaskType.REASONING: 9,
            TaskType.ANALYSIS: 8,
            TaskType.CHAT: 7,
            TaskType.RESEARCH: 7,
            TaskType.SPEED_CRITICAL: 6,
            TaskType.LONG_CONTEXT: 5,
            TaskType.VISION: 0  # Not supported
        }
        return priorities.get(task_type, 6)