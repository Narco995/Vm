"""
Mistral AI Provider
Best for: Complex reasoning, multilingual support
Free Tier: 1 RPS, 500k TPM
"""

import asyncio
from typing import List, Dict, Optional
from .base import BaseLLMProvider, LLMResponse, ProviderCapabilities, TaskType

try:
    from mistralai import Mistral
    MISTRAL_AVAILABLE = True
except ImportError:
    MISTRAL_AVAILABLE = False


class MistralProvider(BaseLLMProvider):
    """Mistral AI API Provider"""
    
    name = "mistral"
    description = "Mistral AI - High quality European models"
    
    def __init__(self, api_key: Optional[str] = None, **kwargs):
        super().__init__(api_key, **kwargs)
        self._model_name = kwargs.get('model', 'mistral-large-latest')
        
        if MISTRAL_AVAILABLE and self.api_key:
            self._client = Mistral(api_key=self.api_key)
    
    async def chat(
        self, 
        messages: List[Dict[str, str]], 
        system_prompt: Optional[str] = None,
        **kwargs
    ) -> LLMResponse:
        """Send a chat completion request to Mistral"""
        
        if not self.is_available():
            return LLMResponse(
                content="Mistral provider not configured",
                model=self._model_name,
                provider=self.name,
                success=False,
                error="API key not provided"
            )
        
        if not MISTRAL_AVAILABLE:
            return LLMResponse(
                content="mistralai package not installed",
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
            
            # Create completion (Mistral client is synchronous)
            response = await asyncio.get_event_loop().run_in_executor(
                None,
                lambda: self._client.chat.complete(
                    model=self._model_name,
                    messages=api_messages,
                    max_tokens=kwargs.get('max_tokens', 4096),
                    temperature=kwargs.get('temperature', 0.7)
                )
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
                content=f"Mistral error: {str(e)}",
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
        """Mistral doesn't currently support direct image analysis"""
        return LLMResponse(
            content="Mistral does not support direct image analysis",
            model=self._model_name,
            provider=self.name,
            success=False,
            error="Vision not supported"
        )
    
    def get_capabilities(self) -> ProviderCapabilities:
        """Return Mistral capabilities"""
        return ProviderCapabilities(
            supports_vision=False,
            supports_audio=False,
            supports_streaming=True,
            max_context_tokens=128000,
            supports_function_calling=True,
            avg_latency_ms=500,
            free_tier_limits={
                "requests_per_second": 1,
                "tokens_per_minute": 500000
            }
        )
    
    def get_default_model(self) -> str:
        """Return default Mistral model"""
        return self._model_name
    
    def get_priority_for_task(self, task_type: TaskType) -> int:
        """Mistral is great for complex reasoning"""
        priorities = {
            TaskType.REASONING: 9,
            TaskType.CODING: 8,
            TaskType.CHAT: 8,
            TaskType.ANALYSIS: 8,
            TaskType.RESEARCH: 7,
            TaskType.SPEED_CRITICAL: 5,
            TaskType.LONG_CONTEXT: 6,
            TaskType.VISION: 0  # Not supported
        }
        return priorities.get(task_type, 6)