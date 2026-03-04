# Multi-LLM Provider Architecture

## Overview
The Telegram bot now uses a sophisticated multi-LLM provider system with intelligent routing and automatic fallback capabilities. This architecture ensures optimal performance, cost efficiency, and reliability.

## Supported Providers

### 1. **Google Gemini 2.5 Flash** ✅
- **Best for:** Long context tasks (1M tokens), vision analysis, complex research
- **Free Tier:** 1,500 requests/day, 1M TPM
- **Priority Tasks:** Long context, vision, research, analysis
- **Status:** Active and tested

### 2. **Groq (Llama 3.3 70B)** ✅
- **Best for:** Ultra-fast responses, real-time chat
- **Free Tier:** ~30 RPM, 30k-100k TPM
- **Priority Tasks:** Speed-critical, chat, quick responses
- **Status:** Active and tested (100ms latency)

### 3. **Mistral Large** ✅
- **Best for:** Complex reasoning, multilingual support, coding
- **Free Tier:** 1 RPS, 500k TPM
- **Priority Tasks:** Reasoning, coding, analysis
- **Status:** Active and tested

### 4. **DeepSeek** ⚠️
- **Best for:** Coding, math, complex reasoning
- **Free Tier:** 5M free tokens (new users)
- **Priority Tasks:** Coding, reasoning
- **Status:** Configured but needs API credits (402 error)

### 5. **OpenRouter** 🔄
- **Best for:** Flexibility, access to multiple models
- **Free Tier:** ~20 RPM, 200 requests/day
- **Priority Tasks:** General purpose, fallback
- **Status:** Available but no API key configured

## Intelligent Routing System

### Task-Based Routing
The bot automatically selects the best provider based on task type:

| Task Type | Best Provider | Why |
|-----------|--------------|-----|
| **Speed Critical** | Groq | 100ms latency |
| **Coding** | DeepSeek → Groq → Mistral | Optimized for code generation |
| **Reasoning** | DeepSeek → Mistral | Strong logical reasoning |
| **Long Context** | Gemini | 1M token context window |
| **Vision** | Gemini | Multimodal capabilities |
| **Research** | Gemini → DeepSeek | Deep analysis capabilities |
| **Analysis** | Gemini → DeepSeek → Mistral | Data processing strength |
| **Chat** | Groq → Gemini → DeepSeek | Balanced performance |

### Auto-Fallback Mechanism
- Automatically switches providers on errors or rate limits
- Tracks error counts per provider
- Skips providers after 3 consecutive errors
- Waterfall pattern: tries providers in priority order

## Architecture Components

### 1. Base Provider Interface (`base.py`)
- `BaseLLMProvider` - Abstract class for all providers
- `TaskType` enum - Task classification
- `LLMResponse` - Standardized response format
- `ProviderCapabilities` - Provider feature description

### 2. Provider Implementations
- `GeminiProvider` - Google Gemini integration
- `GroqProvider` - Groq API (OpenAI-compatible)
- `DeepSeekProvider` - DeepSeek API (OpenAI-compatible)
- `MistralProvider` - Mistral AI integration
- `OpenRouterProvider` - OpenRouter aggregation

### 3. Provider Manager (`provider_manager.py`)
- Registers and manages all providers
- Handles provider selection based on tasks
- Implements fallback logic
- Tracks provider health and errors

### 4. AI Service (`ai_service.py`)
- Refactored to use multi-provider system
- Automatic task detection
- Provider-agnostic API
- Maintains backward compatibility

## Configuration

### Environment Variables
```bash
# Telegram
TELEGRAM_BOT_TOKEN=your_token

# AI Providers
GEMINI_API_KEY=your_gemini_key
GROQ_API_KEY=your_groq_key
DEEPSEEK_API_KEY=your_deepseek_key
MISTRAL_API_KEY=your_mistral_key
OPENROUTER_API_KEY=your_openrouter_key

# Auto-routing
AI_MODEL=auto  # 'auto' for intelligent routing, or specify provider
```

### Provider Priorities
Customizable via `config.py`:
```python
WORKER_PRIORITIES = {
    "speed": ["groq", "deepseek"],
    "reasoning": ["deepseek", "gemini", "mistral"],
    "coding": ["deepseek", "mistral", "groq"],
    # ... more priorities
}
```

## Usage Examples

### Automatic Routing (Recommended)
```python
from bot.services.ai_service import AIService

ai = AIService()

# Automatically uses best provider based on content
response = await ai.chat([
    {"role": "user", "content": "What is 2+2?"}
], style="conversational")
```

### Specific Provider
```python
# Force use of specific provider
response = await ai.chat(
    messages=[...],
    provider="groq"  # Use Groq
)
```

### Task Type Override
```python
from bot.services.llm_providers.base import TaskType

# Override auto-detection
response = await ai.chat(
    messages=[...],
    task_type=TaskType.CODING  # Force coding provider
)
```

## Testing

### Run Provider Tests
```bash
cd Vm
python3 test_providers.py
```

### Test Results Summary
- ✅ Gemini 2.5 Flash: Working
- ✅ Groq (Llama 3.3 70B): Working (59 tokens, 100ms)
- ❌ DeepSeek: Insufficient balance
- ✅ Mistral Large: Working (34 tokens)
- ✅ Auto-fallback: Working

## Performance Characteristics

| Provider | Latency | Context | Vision | Best For |
|----------|---------|---------|--------|----------|
| Gemini | 800ms | 1M tokens | ✅ | Long tasks |
| Groq | 100ms | 128k tokens | ❌ | Speed |
| Mistral | 500ms | 128k tokens | ❌ | Reasoning |
| DeepSeek | 400ms | 64k tokens | ❌ | Coding |
| OpenRouter | 600ms | Varies | ⚠️ | Flexibility |

## Deployment

### Prerequisites
```bash
pip install -r requirements.txt
```

### Start Bot
```bash
cd Vm
python3 main.py
```

### GitHub Repository
All changes have been pushed to `Narco995/Vm` (commit: e9b1300)

## Future Enhancements

1. **Add More Providers**
   - Anthropic Claude
   - OpenAI GPT-4 (optional)
   - Local models via Ollama

2. **Advanced Features**
   - Cost tracking and budgeting
   - Performance analytics dashboard
   - A/B testing of providers
   - Custom routing rules

3. **Optimization**
   - Response caching
   - Request batching
   - Streaming support
   - Token usage optimization

## Troubleshooting

### Provider Not Working
- Check API key in `.env`
- Verify API credits/balance
- Check provider status page
- Review error logs

### Bot Not Responding
- Kill previous bot instances: `pkill -f "python3 main.py"`
- Check Telegram API connection
- Verify bot token is valid
- Review logs for errors

### High Latency
- Check provider status
- Try switching provider priority
- Use `/status` command to see provider health
- Check network connectivity

## Support

For issues or questions:
1. Check logs in `/workspace/outputs/`
2. Run `python3 test_providers.py` for diagnostics
3. Review provider documentation
4. Check GitHub issues

## License

This is part of the Vm Telegram Bot project.