import os
from dotenv import load_dotenv

load_dotenv()

TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
MISTRAL_API_KEY = os.getenv("MISTRAL_API_KEY")
DATABASE_PATH = os.getenv("DATABASE_PATH", "bot_database.db")
MAX_MEMORY_MESSAGES = int(os.getenv("MAX_MEMORY_MESSAGES", 50))
CODE_EXECUTION_TIMEOUT = int(os.getenv("CODE_EXECUTION_TIMEOUT", 30))
MAX_FILE_SIZE_MB = int(os.getenv("MAX_FILE_SIZE_MB", 20))
DEFAULT_COMMUNICATION_STYLE = os.getenv("DEFAULT_COMMUNICATION_STYLE", "conversational")

COMMUNICATION_STYLES = {
    "concise": "Be extremely brief. Max 3 sentences. No fluff.",
    "structured": "Use headers, bullet points, numbered lists. Organize clearly.",
    "conversational": "Warm, natural tone. Thorough but approachable.",
}

GPT_MODEL = "gpt-4o"
WHISPER_MODEL = "whisper-1"
DALLE_MODEL = "dall-e-3"
MISTRAL_MODEL = "mistral-large-latest"

TEMP_DIR = "/tmp/telegram_bot"
os.makedirs(TEMP_DIR, exist_ok=True)
