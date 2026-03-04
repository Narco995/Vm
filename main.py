import asyncio
import logging
from telegram.ext import (
    Application,
    CommandHandler,
    MessageHandler,
    CallbackQueryHandler,
    filters,
)
from config import TELEGRAM_BOT_TOKEN
from database.db_manager import DBManager
from bot.handlers.command_handler import (
    cmd_start, cmd_help, cmd_style, cmd_pdf, cmd_doc,
    cmd_report, cmd_code, cmd_research, cmd_image,
    cmd_memory, cmd_remember, cmd_clearmemory,
    cmd_history, cmd_automations, cmd_automate, cmd_status
)
from bot.handlers.message_handler import handle_text
from bot.handlers.voice_handler import handle_voice
from bot.handlers.image_handler import handle_photo
from bot.handlers.file_handler import handle_document
from bot.handlers.callback_handler import handle_callback
from bot.services.automation_service import AutomationService

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO,
)
logger = logging.getLogger(__name__)


async def post_init(application: Application):
    """Initialize DB and automation service after app starts."""
    db = DBManager()
    await db.init_db()

    automation_service = AutomationService(application.bot)
    await automation_service.start()
    application.automation_service = automation_service
    logger.info("✅ Database initialized")
    logger.info("✅ Automation service started")


def main():
    if not TELEGRAM_BOT_TOKEN:
        raise ValueError("TELEGRAM_BOT_TOKEN not set in .env")

    app = (
        Application.builder()
        .token(TELEGRAM_BOT_TOKEN)
        .post_init(post_init)
        .build()
    )

    # Commands
    app.add_handler(CommandHandler("start", cmd_start))
    app.add_handler(CommandHandler("help", cmd_help))
    app.add_handler(CommandHandler("style", cmd_style))
    app.add_handler(CommandHandler("pdf", cmd_pdf))
    app.add_handler(CommandHandler("doc", cmd_doc))
    app.add_handler(CommandHandler("report", cmd_report))
    app.add_handler(CommandHandler("code", cmd_code))
    app.add_handler(CommandHandler("research", cmd_research))
    app.add_handler(CommandHandler("image", cmd_image))
    app.add_handler(CommandHandler("memory", cmd_memory))
    app.add_handler(CommandHandler("remember", cmd_remember))
    app.add_handler(CommandHandler("clearmemory", cmd_clearmemory))
    app.add_handler(CommandHandler("history", cmd_history))
    app.add_handler(CommandHandler("automations", cmd_automations))
    app.add_handler(CommandHandler("automate", cmd_automate))
    app.add_handler(CommandHandler("status", cmd_status))

    # Media & Files
    app.add_handler(MessageHandler(filters.VOICE | filters.AUDIO, handle_voice))
    app.add_handler(MessageHandler(filters.PHOTO, handle_photo))
    app.add_handler(MessageHandler(filters.Document.ALL, handle_document))

    # Text messages
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_text))

    # Inline keyboard
    app.add_handler(CallbackQueryHandler(handle_callback))

    logger.info("🤖 Bot starting...")
    app.run_polling(allowed_updates=["message", "callback_query"])


if __name__ == "__main__":
    main()
