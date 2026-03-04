import os
from dotenv import load_dotenv

load_dotenv()

# Telegram Configuration
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
DATABASE_PATH = os.getenv("DATABASE_PATH", "bot_database.db")
MAX_MEMORY_MESSAGES = int(os.getenv("MAX_MEMORY_MESSAGES", 50))
CODE_EXECUTION_TIMEOUT = int(os.getenv("CODE_EXECUTION_TIMEOUT", 30))
MAX_FILE_SIZE_MB = int(os.getenv("MAX_FILE_SIZE_MB", 20))
DEFAULT_COMMUNICATION_STYLE = os.getenv("DEFAULT_COMMUNICATION_STYLE", "conversational")

# Communication Styles
COMMUNICATION_STYLES = {
    "concise": "Be extremely brief. Max 3 sentences. No fluff.",
    "structured": "Use headers, bullet points, numbered lists. Organize clearly.",
    "conversational": "Warm, natural tone. Thorough but approachable.",
}

# Legacy OpenAI Configuration (kept for backward compatibility)
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

# Multi-LLM Provider Configuration
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
GROQ_API_KEY = os.getenv("GROQ_API_KEY")
DEEPSEEK_API_KEY = os.getenv("DEEPSEEK_API_KEY")
MISTRAL_API_KEY = os.getenv("MISTRAL_API_KEY")
OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")

# Default AI Model (legacy, use provider manager instead)
GPT_MODEL = "gpt-4o"
WHISPER_MODEL = "whisper-1"
DALLE_MODEL = "dall-e-3"
MISTRAL_MODEL = "mistral-large-latest"

# Provider-specific model configurations
GEMINI_MODEL = "gemini-2.5-flash"
GROQ_MODEL = "llama-3.3-70b-versatile"
DEEPSEEK_MODEL = "deepseek-chat"
OPENROUTER_MODEL = "meta-llama/llama-3.3-70b-instruct:free"

# AI Model Selection (can be 'auto', 'gemini', 'groq', 'deepseek', 'mistral', 'openrouter')
AI_MODEL = os.getenv("AI_MODEL", "auto")

# Worker Priorities (for auto-routing)
WORKER_PRIORITIES = {
    "speed": ["groq", "deepseek"],  # Fast responses
    "reasoning": ["deepseek", "gemini", "mistral"],  # Complex reasoning
    "coding": ["deepseek", "mistral", "groq"],  # Code generation
    "vision": ["gemini"],  # Image analysis
    "long_context": ["gemini"],  # Large context windows
    "chat": ["groq", "gemini", "deepseek"],  # General chat
    "research": ["gemini", "deepseek"],  # Research tasks
    "analysis": ["gemini", "deepseek", "mistral"],  # Data analysis
}

# File Configuration
TEMP_DIR = "/tmp/telegram_bot"
os.makedirs(TEMP_DIR, exist_ok=True)

# Deployment Settings
MEMORY_LIMIT = int(os.getenv("MEMORY_LIMIT", 4096))
CPU_LIMIT = float(os.getenv("CPU_LIMIT", 2.0))
ENVIRONMENT = os.getenv("ENVIRONMENT", "development")
DEBUG = os.getenv("DEBUG", "true").lower() == "true"
TZ = os.getenv("TZ", "UTC")

# Dashboard Configuration
DASHBOARD_PORT = int(os.getenv("DASHBOARD_PORT", 8080))
GRAFANA_PASSWORD = os.getenv("GRAFANA_PASSWORD", "admin123")

# Logging
LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")