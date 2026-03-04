import os
from telegram import Update
from telegram.ext import ContextTypes
from database.db_manager import DBManager
from bot.services.ai_service import AIService
from config import TEMP_DIR
import logging

logger = logging.getLogger(__name__)
db = DBManager()
ai = AIService()


async def handle_photo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    await db.get_or_create_user(user.id, user.username or "", user.first_name or "")

    caption = update.message.caption or "Describe and analyze this image in detail."
    msg = await update.message.reply_text("🖼 Analyzing image with GPT-4 Vision...")

    try:
        photo = update.message.photo[-1]
        file = await context.bot.get_file(photo.file_id)
        img_path = os.path.join(TEMP_DIR, f"img_{user.id}_{photo.file_id}.jpg")
        await file.download_to_drive(img_path)

        with open(img_path, 'rb') as f:
            image_data = f.read()
        os.unlink(img_path)

        analysis = await ai.analyze_image(image_data, caption)
        await db.add_task(user.id, "vision", caption[:100], "completed")
        await msg.delete()

        chunks = [analysis[i:i+4000] for i in range(0, len(analysis), 4000)]
        for chunk in chunks:
            await update.message.reply_text(chunk)

    except Exception as e:
        logger.error(f"Photo handler error: {e}")
        await msg.edit_text(f"❌ Image analysis error: {str(e)}")
