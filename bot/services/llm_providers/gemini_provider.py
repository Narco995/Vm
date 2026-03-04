"""
Gemini (Google AI Studio) Provider
Best for: Long context (1M tokens), complex reasoning, multimodal tasks
Free Tier: 1,500 requests/day, 1M TPM
"""

import asyncio
from typing import List, Dict, Optional
from .base import BaseLLMProvider, LLMResponse, ProviderCapabilities, TaskType

try:
    import google.generativeai as genai
    GENAI_AVAILABLE = True
except ImportError:
    GENAI_AVAILABLE = False


class GeminiProvider(BaseLLMProvider):
    """Google Gemini API Provider"""
    
    name = "gemini"
    description = "Google Gemini - High context, multimodal AI"
    
    def __init__(self, api_key: Optional[str] = None, **kwargs):
        super().__init__(api_key, **kwargs)
        # Use a stable model name that works
        self._model_name = kwargs.get('model', 'gemini-2.5-flash')
        
        if GENAI_AVAILABLE and self.api_key:
            genai.configure(api_key=self.api_key)
            self._client = genai.GenerativeModel(self._model_name)
    
    async def chat(
        self, 
        messages: List[Dict[str, str]], 
        system_prompt: Optional[str] = None,
        **kwargs
    ) -> LLMResponse:
        """Send a chat completion request to Gemini"""
        
        if not self.is_available():
            return LLMResponse(
                content="Gemini provider not configured",
                model=self._model_name,
                provider=self.name,
                success=False,
                error="API key not provided"
            )
        
        if not GENAI_AVAILABLE:
            return LLMResponse(
                content="google-generativeai package not installed",
                model=self._model_name,
                provider=self.name,
                success=False,
                error="Missing dependency"
            )
        
        try:
            # Build chat history
            chat_history = []
            for msg in messages[:-1]:  # All but last message
                role = 'user' if msg['role'] == 'user' else 'model'
                chat_history.append({
                    'role': role,
                    'parts': [msg['content']]
                })
            
            # Create chat session with system prompt
            chat = self._client.start_chat(history=chat_history)
            
            # Send the last message
            if system_prompt:
                # Prepend system instruction
                final_prompt = f"{system_prompt}\n\n{messages[-1]['content']}"
            else:
                final_prompt = messages[-1]['content']
            
            # Generate response
            response = await asyncio.get_event_loop().run_in_executor(
                None,
                lambda: chat.send_message(final_prompt, **kwargs)
            )
            
            return LLMResponse(
                content=response.text,
                model=self._model_name,
                provider=self.name,
                success=True
            )
            
        except Exception as e:
            return LLMResponse(
                content=f"Gemini error: {str(e)}",
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
        """Analyze an image using Gemini Vision"""
        
        if not self.is_available() or not GENAI_AVAILABLE:
            return LLMResponse(
                content="Gemini Vision not available",
                model=self._model_name,
                provider=self.name,
                success=False,
                error="Provider not configured"
            )
        
        try:
            import google.generativeai.types as types
            
            # Create image part
            image_part = types.Part.from_bytes(
                mime_type="image/jpeg",
                data=image_data
            )
            
            # Generate response
            response = await asyncio.get_event_loop().run_in_executor(
                None,
                lambda: self._client.generate_content([image_part, prompt])
            )
            
            return LLMResponse(
                content=response.text,
                model=self._model_name,
                provider=self.name,
                success=True
            )
            
        except Exception as e:
            return LLMResponse(
                content=f"Gemini Vision error: {str(e)}",
                model=self._model_name,
                provider=self.name,
                success=False,
                error=str(e)
            )
    
    def get_capabilities(self) -> ProviderCapabilities:
        """Return Gemini capabilities"""
        return ProviderCapabilities(
            supports_vision=True,
            supports_audio=True,
            supports_streaming=True,
            max_context_tokens=1000000,  # 1M token context
            supports_function_calling=True,
            avg_latency_ms=800,
            free_tier_limits={
                "requests_per_day": 1500,
                "tokens_per_minute": 1000000
            }
        )
    
    def get_default_model(self) -> str:
        """Return default Gemini model"""
        return self._model_name
    
    def get_priority_for_task(self, task_type: TaskType) -> int:
        """Gemini is best for long context and vision tasks"""
        priorities = {
            TaskType.LONG_CONTEXT: 10,  # Excellent
            TaskType.VISION: 9,
            TaskType.REASONING: 8,
            TaskType.RESEARCH: 9,
            TaskType.ANALYSIS: 8,
            TaskType.CHAT: 6,
            TaskType.SPEED_CRITICAL: 4,  # Not the fastest
            TaskType.CODING: 7
        }
        return priorities.get(task_type, 6)