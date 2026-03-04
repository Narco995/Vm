import os
from telegram import Update
from telegram.ext import ContextTypes
from database.db_manager import DBManager
from bot.services.ai_service import AIService
from bot.services.file_service import FileService
from bot.services.data_service import DataService
from config import TEMP_DIR, MAX_FILE_SIZE_MB
import logging

logger = logging.getLogger(__name__)
db = DBManager()
ai = AIService()
file_svc = FileService()
data_svc = DataService()


async def handle_document(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    await db.get_or_create_user(user.id, user.username or "", user.first_name or "")

    doc = update.message.document
    filename = doc.file_name or "document"
    file_size_mb = (doc.file_size or 0) / (1024 * 1024)

    if file_size_mb > MAX_FILE_SIZE_MB:
        await update.message.reply_text(f"❌ File too large. Max size: {MAX_FILE_SIZE_MB}MB")
        return

    msg = await update.message.reply_text(f"📂 Processing: *{filename}*...", parse_mode="Markdown")

    try:
        file = await context.bot.get_file(doc.file_id)
        filepath = os.path.join(TEMP_DIR, filename)
        await file.download_to_drive(filepath)

        style = await db.get_user_style(user.id)
        caption = update.message.caption or ""

        # Data files get analysis
        if file_svc.is_data_file(filename):
            result = await data_svc.analyze_file(filepath, style)
            await db.add_task(user.id, "data_analysis", filename, "completed")
        else:
            # Extract text and process
            text = await file_svc.extract_text(filepath)
            if text:
                prompt = caption if caption else f"Analyze and summarize this document: {filename}"
                messages = [{"role": "user", "content": f"{prompt}\n\nDocument content:\n{text[:6000]}"}]
                result = await ai.chat(messages, style=style)
                await db.add_task(user.id, "file_analysis", filename, "completed")
            else:
                result = "❌ Could not extract text from this file type."

        os.unlink(filepath)
        await msg.delete()
        chunks = [result[i:i+4000] for i in range(0, len(result), 4000)]
        for chunk in chunks:
            await update.message.reply_text(chunk)

    except Exception as e:
        logger.error(f"Document handler error: {e}")
        await msg.edit_text(f"❌ File processing error: {str(e)}")
