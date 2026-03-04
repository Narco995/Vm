from telegram import Update
from telegram.ext import ContextTypes
from database.db_manager import DBManager
from bot.orchestrator.task_orchestrator import TaskOrchestrator
import logging

logger = logging.getLogger(__name__)
db = DBManager()
orchestrator = TaskOrchestrator()


async def handle_text(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    text = update.message.text

    await db.get_or_create_user(user.id, user.username or "", user.first_name or "")

    # Typing indicator
    await context.bot.send_chat_action(chat_id=update.effective_chat.id, action="typing")

    # Get user preferences
    style = await db.get_user_style(user.id)
    history = await db.get_conversation_history(user.id)
    memory_notes = await db.get_memory_notes(user.id)

    # Save user message
    await db.add_message(user.id, "user", text)

    # Process via orchestrator
    response = await orchestrator.process(text, history, style, memory_notes)

    # Save assistant response
    await db.add_message(user.id, "assistant", response)

    # Send response in chunks if needed
    chunks = [response[i:i+4000] for i in range(0, len(response), 4000)]
    for chunk in chunks:
        await update.message.reply_text(chunk)
