import os
from telegram import Update
from telegram.ext import ContextTypes
from database.db_manager import DBManager
from bot.services.ai_service import AIService
from bot.orchestrator.task_orchestrator import TaskOrchestrator
from config import TEMP_DIR
import logging

logger = logging.getLogger(__name__)
db = DBManager()
ai = AIService()
orchestrator = TaskOrchestrator()


async def handle_voice(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    await db.get_or_create_user(user.id, user.username or "", user.first_name or "")

    msg = await update.message.reply_text("🎙 Transcribing your voice message...")

    try:
        voice = update.message.voice or update.message.audio
        file = await context.bot.get_file(voice.file_id)
        audio_path = os.path.join(TEMP_DIR, f"voice_{user.id}_{voice.file_id}.ogg")
        await file.download_to_drive(audio_path)

        transcript = await ai.transcribe_audio(audio_path)
        os.unlink(audio_path)

        await msg.edit_text(f"🎙 *Transcribed:* _{transcript}_\n\n⌛ Processing...", parse_mode="Markdown")

        style = await db.get_user_style(user.id)
        history = await db.get_conversation_history(user.id)
        memory_notes = await db.get_memory_notes(user.id)

        await db.add_message(user.id, "user", f"[Voice]: {transcript}")
        response = await orchestrator.process(transcript, history, style, memory_notes)
        await db.add_message(user.id, "assistant", response)

        await msg.delete()
        chunks = [response[i:i+4000] for i in range(0, len(response), 4000)]
        for chunk in chunks:
            await update.message.reply_text(chunk)

    except Exception as e:
        logger.error(f"Voice handler error: {e}")
        await msg.edit_text(f"❌ Voice processing error: {str(e)}")
