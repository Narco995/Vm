"""
AI Service - Multi-LLM Provider Architecture
Supports: Gemini, Groq, DeepSeek, Mistral, OpenRouter
Intelligent routing based on task type with automatic fallback
"""

import asyncio
import logging
from typing import List, Dict, Optional

from config import (
    GEMINI_API_KEY, GROQ_API_KEY, DEEPSEEK_API_KEY, MISTRAL_API_KEY,
    COMMUNICATION_STYLES, AI_MODEL
)
from bot.services.llm_providers import LLMProviderManager, create_default_manager
from bot.services.llm_providers.base import TaskType, LLMResponse

logger = logging.getLogger(__name__)


class AIService:
    """AI Service with multi-provider support and intelligent routing"""
    
    def __init__(self):
        # Initialize provider manager with all available API keys
        api_keys = {
            'GEMINI_API_KEY': GEMINI_API_KEY,
            'GROQ_API_KEY': GROQ_API_KEY,
            'DEEPSEEK_API_KEY': DEEPSEEK_API_KEY,
            'MISTRAL_API_KEY': MISTRAL_API_KEY,
        }
        self.provider_manager = create_default_manager(api_keys)
        self.default_provider = AI_MODEL if AI_MODEL != 'auto' else None
        
        logger.info(f"AI Service initialized with {len(self.provider_manager.providers)} providers")
    
    def _get_task_type_for_content(self, content: str, style: str = "conversational") -> TaskType:
        """Determine task type based on content analysis"""
        content_lower = content.lower()
        
        # Coding indicators
        code_keywords = ['code', 'function', 'class', 'method', 'python', 'javascript', 
                        'debug', 'implement', 'algorithm', 'programming']
        if any(kw in content_lower for kw in code_keywords):
            return TaskType.CODING
        
        # Reasoning indicators
        reasoning_keywords = ['analyze', 'reason', 'explain why', 'compare', 'evaluate',
                             'pros and cons', 'logic', 'argument', 'math']
        if any(kw in content_lower for kw in reasoning_keywords):
            return TaskType.REASONING
        
        # Research indicators
        research_keywords = ['research', 'investigate', 'find information', 'explore',
                            'summarize', 'overview', 'what is']
        if any(kw in content_lower for kw in research_keywords):
            return TaskType.RESEARCH
        
        # Analysis indicators
        analysis_keywords = ['analyze', 'data', 'statistics', 'trend', 'pattern',
                            'report', 'metrics']
        if any(kw in content_lower for kw in analysis_keywords):
            return TaskType.ANALYSIS
        
        # Default to chat
        return TaskType.CHAT
    
    async def chat(
        self, 
        messages: List[Dict[str, str]], 
        style: str = "conversational",
        task_type: Optional[TaskType] = None,
        provider: Optional[str] = None
    ) -> str:
        """
        Send a chat request with intelligent routing
        
        Args:
            messages: List of message dicts with 'role' and 'content'
            style: Communication style (concise, structured, conversational)
            task_type: Override auto-detected task type
            provider: Override provider selection
            
        Returns:
            Response content as string
        """
        style_prompt = COMMUNICATION_STYLES.get(style, COMMUNICATION_STYLES["conversational"])
        system_prompt = f"You are an advanced AI assistant. {style_prompt} You help users with any task — research, coding, writing, analysis, and more."
        
        # Determine task type if not specified
        if task_type is None:
            content = messages[-1].get('content', '') if messages else ''
            task_type = self._get_task_type_for_content(content, style)
        
        try:
            # Use specific provider if requested
            if provider:
                provider_instance = self.provider_manager.get_provider(provider)
                if provider_instance:
                    response = await provider_instance.chat(messages, system_prompt)
                else:
                    return f"❌ Provider '{provider}' not found"
            else:
                # Use intelligent routing with fallback
                response = await self.provider_manager.execute_with_fallback(
                    task_type=task_type,
                    messages=messages,
                    system_prompt=system_prompt
                )
            
            if response.success:
                return response.content
            else:
                return f"❌ AI error: {response.error}"
                
        except Exception as e:
            logger.error(f"Chat error: {e}")
            return f"❌ AI error: {str(e)}"
    
    async def analyze_image(self, image_data: bytes, prompt: str = "Describe this image in detail.") -> str:
        """Analyze an image using vision-capable providers"""
        try:
            response = await self.provider_manager.analyze_image_with_fallback(
                image_data=image_data,
                prompt=prompt
            )
            
            if response.success:
                return response.content
            else:
                return f"❌ Vision error: {response.error}"
                
        except Exception as e:
            logger.error(f"Image analysis error: {e}")
            return f"❌ Vision error: {str(e)}"
    
    async def research(self, topic: str, style: str = "structured") -> str:
        """Conduct comprehensive research on a topic"""
        messages = [{
            "role": "user",
            "content": f"""Conduct comprehensive research on: {topic}

Structure your response with:
1. **Executive Summary** (2-3 sentences)
2. **Background & Context**
3. **Key Findings** (5-7 bullet points)
4. **Current Developments**
5. **Implications & Applications**
6. **Expert Perspectives**
7. **Conclusion & Recommendations**

Be thorough, cite relevant examples, and provide actionable insights."""
        }]
        return await self.chat(messages, style=style, task_type=TaskType.RESEARCH)
    
    async def generate_report(self, topic: str) -> str:
        """Generate a professional structured report"""
        messages = [{
            "role": "user",
            "content": f"""Create a professional structured report on: {topic}

Include: Executive Summary, Introduction, Methodology, Findings, Analysis, Recommendations, Conclusion.
Use professional language, data-driven insights, and clear section headers."""
        }]
        return await self.chat(messages, style="structured", task_type=TaskType.ANALYSIS)
    
    async def analyze_data_text(self, data_summary: str, style: str = "structured") -> str:
        """Analyze data and provide insights"""
        messages = [{
            "role": "user",
            "content": f"Analyze this data and provide insights, patterns, and recommendations:\n\n{data_summary}"
        }]
        return await self.chat(messages, style=style, task_type=TaskType.ANALYSIS)
    
    async def code_generation(self, prompt: str, language: str = "python") -> str:
        """Generate code based on prompt"""
        messages = [{
            "role": "user",
            "content": f"Write {language} code for the following task:\n\n{prompt}\n\nProvide clean, well-documented code with explanations."
        }]
        return await self.chat(messages, style="structured", task_type=TaskType.CODING)
    
    async def quick_chat(self, message: str) -> str:
        """Fast response for quick queries (uses speed-optimized providers)"""
        messages = [{"role": "user", "content": message}]
        return await self.chat(messages, task_type=TaskType.SPEED_CRITICAL)
    
    async def deep_reasoning(self, query: str) -> str:
        """Use reasoning-capable providers for complex queries"""
        messages = [{
            "role": "user",
            "content": f"Think carefully and reason through this step by step:\n\n{query}"
        }]
        return await self.chat(messages, style="structured", task_type=TaskType.REASONING)
    
    def get_status(self) -> Dict:
        """Get status of all providers"""
        return self.provider_manager.get_status()
    
    def get_available_providers(self) -> List[str]:
        """Get list of available provider names"""
        return list(self.provider_manager.providers.keys())