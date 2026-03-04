"""
Test script for multi-LLM provider system
Tests all providers individually and fallback mechanism
"""

import asyncio
import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from bot.services.llm_providers import LLMProviderManager, create_default_manager, TaskType
from config import GEMINI_API_KEY, GROQ_API_KEY, DEEPSEEK_API_KEY, MISTRAL_API_KEY


async def test_providers():
    """Test all registered providers"""
    
    print("=" * 60)
    print("Multi-LLM Provider System Test")
    print("=" * 60)
    
    # Create provider manager
    api_keys = {
        'GEMINI_API_KEY': GEMINI_API_KEY,
        'GROQ_API_KEY': GROQ_API_KEY,
        'DEEPSEEK_API_KEY': DEEPSEEK_API_KEY,
        'MISTRAL_API_KEY': MISTRAL_API_KEY,
    }
    
    manager = create_default_manager(api_keys)
    
    print(f"\n📊 Provider Status:")
    print("-" * 60)
    status = manager.get_status()
    
    for name, info in status['providers'].items():
        available = "✅" if info['available'] else "❌"
        print(f"{available} {name}")
        print(f"   Model: {info['default_model']}")
        print(f"   Context: {info['capabilities']['max_context_tokens']:,} tokens")
        print(f"   Latency: {info['capabilities']['avg_latency_ms']}ms")
        print()
    
    if len(manager.providers) == 0:
        print("❌ No providers available. Check API keys.")
        return
    
    print("=" * 60)
    print("Testing Individual Providers")
    print("=" * 60)
    
    test_message = "What is 2 + 2? Answer in 5 words or less."
    
    for provider in manager.providers.values():
        if not provider.is_available():
            continue
            
        print(f"\n🧪 Testing {provider.name}...")
        try:
            response = await provider.chat(
                messages=[{"role": "user", "content": test_message}],
                system_prompt="You are a helpful assistant."
            )
            
            if response.success:
                print(f"✅ Success! Response: {response.content}")
                print(f"   Model: {response.model}")
                print(f"   Tokens: {response.tokens_used}")
            else:
                print(f"❌ Failed: {response.error}")
        except Exception as e:
            print(f"❌ Exception: {e}")
    
    print("\n" + "=" * 60)
    print("Testing Task-Based Routing")
    print("=" * 60)
    
    tasks = [
        (TaskType.SPEED_CRITICAL, "Say hello in 2 words", "Quick chat"),
        (TaskType.CODING, "Write a Python function to add two numbers", "Coding"),
        (TaskType.REASONING, "Why is the sky blue? Explain in 3 sentences", "Reasoning"),
        (TaskType.LONG_CONTEXT, "Summarize: " + "Lorem ipsum " * 100, "Long context"),
    ]
    
    for task_type, prompt, description in tasks:
        print(f"\n🎯 Testing {description} ({task_type.value})...")
        
        # Get best provider for this task
        best_provider = manager.get_best_provider_for_task(task_type)
        if best_provider:
            print(f"   Selected provider: {best_provider.name}")
            print(f"   Priority: {best_provider.get_priority_for_task(task_type)}/10")
        
        try:
            response = await manager.execute_with_fallback(
                task_type=task_type,
                messages=[{"role": "user", "content": prompt}],
                system_prompt="You are a helpful assistant."
            )
            
            if response.success:
                print(f"✅ Success! Provider: {response.provider}")
                print(f"   Response: {response.content[:100]}...")
            else:
                print(f"❌ Failed: {response.error}")
        except Exception as e:
            print(f"❌ Exception: {e}")
    
    print("\n" + "=" * 60)
    print("Test Complete")
    print("=" * 60)


if __name__ == "__main__":
    asyncio.run(test_providers())