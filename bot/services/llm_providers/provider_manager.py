"""
LLM Provider Manager
Handles provider selection, routing, and fallback logic
"""

import asyncio
import logging
from typing import List, Dict, Optional, Tuple
from collections import defaultdict

from .base import BaseLLMProvider, TaskType, LLMResponse
from .gemini_provider import GeminiProvider
from .groq_provider import GroqProvider
from .deepseek_provider import DeepSeekProvider
from .mistral_provider import MistralProvider
from .openrouter_provider import OpenRouterProvider

logger = logging.getLogger(__name__)


class LLMProviderManager:
    """Manages multiple LLM providers with intelligent routing and fallback"""
    
    def __init__(self):
        self.providers: Dict[str, BaseLLMProvider] = {}
        self.task_priorities: Dict[str, List[Tuple[str, int]]] = defaultdict(list)
        self.error_counts: Dict[str, int] = defaultdict(int)
        self.max_errors_before_fallback = 3
        
    def register_provider(self, provider: BaseLLMProvider, priority: int = 5):
        """Register a provider with optional priority"""
        if not provider.is_available():
            logger.warning(f"Provider {provider.name} is not available, skipping")
            return
        
        self.providers[provider.name] = provider
        
        # Register priorities for all task types
        for task_type in TaskType:
            score = provider.get_priority_for_task(task_type)
            self.task_priorities[task_type.value].append((provider.name, score))
        
        # Sort by priority (descending)
        for task_type in self.task_priorities:
            self.task_priorities[task_type].sort(key=lambda x: x[1], reverse=True)
        
        logger.info(f"Registered provider: {provider.name}")
    
    def get_provider(self, provider_name: str) -> Optional[BaseLLMProvider]:
        """Get a specific provider by name"""
        return self.providers.get(provider_name)
    
    def get_best_provider_for_task(self, task_type: TaskType) -> Optional[BaseLLMProvider]:
        """Get the best provider for a specific task type"""
        provider_list = self.task_priorities.get(task_type.value, [])
        
        for provider_name, _ in provider_list:
            provider = self.providers.get(provider_name)
            if provider and self.error_counts[provider_name] < self.max_errors_before_fallback:
                return provider
        
        # Fallback to first available provider
        if self.providers:
            return next(iter(self.providers.values()))
        
        return None
    
    def get_providers_for_task(self, task_type: TaskType) -> List[BaseLLMProvider]:
        """Get all providers that support a task, ordered by priority"""
        provider_list = self.task_priorities.get(task_type.value, [])
        providers = []
        
        for provider_name, _ in provider_list:
            provider = self.providers.get(provider_name)
            if provider:
                providers.append(provider)
        
        return providers
    
    def get_all_available_providers(self) -> List[BaseLLMProvider]:
        """Get all available providers"""
        return list(self.providers.values())
    
    def record_error(self, provider_name: str):
        """Record an error for a provider"""
        self.error_counts[provider_name] += 1
        logger.warning(f"Error recorded for {provider_name}. Total errors: {self.error_counts[provider_name]}")
    
    def reset_errors(self, provider_name: str):
        """Reset error count for a provider"""
        self.error_counts[provider_name] = 0
        logger.info(f"Error count reset for {provider_name}")
    
    async def execute_with_fallback(
        self,
        task_type: TaskType,
        messages: List[Dict[str, str]],
        system_prompt: Optional[str] = None,
        **kwargs
    ) -> LLMResponse:
        """
        Execute a request with automatic fallback on errors
        Uses waterfall pattern: tries providers in priority order
        """
        providers = self.get_providers_for_task(task_type)
        
        if not providers:
            return LLMResponse(
                content="No LLM providers available",
                model="unknown",
                provider="none",
                success=False,
                error="No providers configured"
            )
        
        last_error = None
        
        for provider in providers:
            if self.error_counts[provider.name] >= self.max_errors_before_fallback:
                logger.info(f"Skipping {provider.name} due to error threshold")
                continue
            
            logger.info(f"Trying provider: {provider.name} for task: {task_type.value}")
            
            try:
                response = await provider.chat(messages, system_prompt, **kwargs)
                
                if response.success:
                    self.reset_errors(provider.name)
                    return response
                else:
                    last_error = response.error
                    self.record_error(provider.name)
                    logger.warning(f"Provider {provider.name} failed: {response.error}")
                    
            except Exception as e:
                last_error = str(e)
                self.record_error(provider.name)
                logger.error(f"Provider {provider.name} raised exception: {e}")
        
        # All providers failed
        return LLMResponse(
            content=f"All providers failed. Last error: {last_error}",
            model="unknown",
            provider="none",
            success=False,
            error=last_error
        )
    
    async def analyze_image_with_fallback(
        self,
        image_data: bytes,
        prompt: str,
        **kwargs
    ) -> LLMResponse:
        """Execute image analysis with providers that support vision"""
        providers = self.get_providers_for_task(TaskType.VISION)
        
        for provider in providers:
            if not provider.supports_task(TaskType.VISION):
                continue
                
            try:
                response = await provider.analyze_image(image_data, prompt, **kwargs)
                if response.success:
                    return response
            except Exception as e:
                logger.error(f"Provider {provider.name} vision failed: {e}")
        
        return LLMResponse(
            content="No provider available for image analysis",
            model="unknown",
            provider="none",
            success=False,
            error="Vision not supported"
        )
    
    def get_status(self) -> Dict:
        """Get status of all providers"""
        return {
            "total_providers": len(self.providers),
            "providers": {
                name: {
                    "available": provider.is_available(),
                    "error_count": self.error_counts[name],
                    "capabilities": provider.get_capabilities().__dict__,
                    "default_model": provider.get_default_model()
                }
                for name, provider in self.providers.items()
            }
        }


def create_default_manager(api_keys: Dict[str, str]) -> LLMProviderManager:
    """Create a provider manager with default providers"""
    manager = LLMProviderManager()
    
    # Register providers if API keys are available
    if api_keys.get('GEMINI_API_KEY'):
        manager.register_provider(
            GeminiProvider(api_key=api_keys['GEMINI_API_KEY'])
        )
    
    if api_keys.get('GROQ_API_KEY'):
        manager.register_provider(
            GroqProvider(api_key=api_keys['GROQ_API_KEY'])
        )
    
    if api_keys.get('DEEPSEEK_API_KEY'):
        manager.register_provider(
            DeepSeekProvider(api_key=api_keys['DEEPSEEK_API_KEY'])
        )
    
    if api_keys.get('MISTRAL_API_KEY'):
        manager.register_provider(
            MistralProvider(api_key=api_keys['MISTRAL_API_KEY'])
        )
    
    if api_keys.get('OPENROUTER_API_KEY'):
        manager.register_provider(
            OpenRouterProvider(api_key=api_keys['OPENROUTER_API_KEY'])
        )
    
    logger.info(f"Created provider manager with {len(manager.providers)} providers")
    return manager