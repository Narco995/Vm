from telegram import Update
from telegram.ext import ContextTypes
from database.db_manager import DBManager

db = DBManager()


async def handle_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    data = query.data

    if data.startswith("style_"):
        style = data.replace("style_", "")
        await db.set_user_style(update.effective_user.id, style)
        style_names = {
            "conversational": "💬 Conversational",
            "structured": "📋 Structured",
            "concise": "⚡ Concise"
        }
        await query.edit_message_text(
            f"✅ Style set to *{style_names.get(style, style)}*!\n\n"
            f"All future responses will use this style.",
            parse_mode="Markdown"
        )

    elif data == "help_pdf":
        await query.edit_message_text("📄 *PDF Generation*\n\nUse: `/pdf [topic]`\nExample: `/pdf The Future of AI`", parse_mode="Markdown")
    elif data == "help_doc":
        await query.edit_message_text("📝 *Word Documents*\n\nUse: `/doc [topic]`\nExample: `/doc Q3 Business Review`", parse_mode="Markdown")
    elif data == "help_code":
        await query.edit_message_text("💻 *Code Execution*\n\nUse: `/code [description]`\nExample: `/code Create a fibonacci calculator`", parse_mode="Markdown")
    elif data == "help_research":
        await query.edit_message_text("🔬 *Research*\n\nUse: `/research [topic]`\nExample: `/research Quantum Computing`", parse_mode="Markdown")
    elif data == "help_image":
        await query.edit_message_text("🖼 *Image Generation*\n\nUse: `/image [prompt]`\nExample: `/image A neon cyberpunk city`", parse_mode="Markdown")
    elif data == "help_style":
        await query.edit_message_text("🎨 *Communication Style*\n\nUse: `/style` to choose your preferred response format.", parse_mode="Markdown")
    elif data == "help_data":
        await query.edit_message_text("📊 *Data Analysis*\n\nJust send a CSV, Excel, or JSON file!\nI'll analyze and provide insights automatically.", parse_mode="Markdown")
    elif data == "help_auto":
        await query.edit_message_text(
            "⚙️ *Automations*\n\nUse: `/automate name|task|schedule`\n\n"
            "Example:\n`/automate Daily Briefing|Summarize AI news|every day at 9am`",
            parse_mode="Markdown"
        )
