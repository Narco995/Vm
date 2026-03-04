from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes
from database.db_manager import DBManager
from bot.services.ai_service import AIService
from bot.services.pdf_service import PDFService
from bot.services.document_service import DocumentService
from bot.services.code_service import CodeService
from bot.services.research_service import ResearchService
from bot.utils.formatters import format_task_history, format_automations, truncate
from config import COMMUNICATION_STYLES
import logging

logger = logging.getLogger(__name__)
db = DBManager()
ai = AIService()
pdf_svc = PDFService()
doc_svc = DocumentService()
code_svc = CodeService()
research_svc = ResearchService()


async def cmd_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    await db.get_or_create_user(user.id, user.username or "", user.first_name or "")

    keyboard = [
        [InlineKeyboardButton("📄 Generate PDF", callback_data="help_pdf"),
         InlineKeyboardButton("📝 Generate DOC", callback_data="help_doc")],
        [InlineKeyboardButton("💻 Run Code", callback_data="help_code"),
         InlineKeyboardButton("🔬 Research", callback_data="help_research")],
        [InlineKeyboardButton("🖼 Generate Image", callback_data="help_image"),
         InlineKeyboardButton("🎨 Change Style", callback_data="help_style")],
        [InlineKeyboardButton("📊 Analyze Data", callback_data="help_data"),
         InlineKeyboardButton("⚙️ Automations", callback_data="help_auto")],
    ]

    await update.message.reply_text(
        f"🤖 *Welcome, {user.first_name}!*\n\n"
        "I'm your advanced AI assistant powered by *GPT-4o*, *Whisper*, *DALL-E 3*, and *Mistral AI*.\n\n"
        "I can help you with:\n"
        "📄 Documents & PDFs • 💻 Code Execution\n"
        "🔬 Deep Research • 🖼 Image Generation\n"
        "🎙 Voice Messages • 📊 Data Analysis\n"
        "🧠 Long-term Memory • ⚙️ Automation\n\n"
        "Just send me a message or use /help for all commands!",
        parse_mode="Markdown",
        reply_markup=InlineKeyboardMarkup(keyboard)
    )


async def cmd_help(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "📖 *All Commands:*\n\n"
        "🛠 *Generation:*\n"
        "`/pdf [topic]` — Generate PDF report\n"
        "`/doc [topic]` — Generate Word document\n"
        "`/report [topic]` — Structured report (text)\n"
        "`/image [prompt]` — Generate AI image\n\n"
        "💻 *Code:*\n"
        "`/code [description]` — Write & execute Python\n\n"
        "🔬 *Research:*\n"
        "`/research [topic]` — In-depth research\n\n"
        "🧠 *Memory:*\n"
        "`/memory` — View saved notes\n"
        "`/remember [note]` — Save a note\n"
        "`/clearmemory` — Clear history & notes\n\n"
        "⚙️ *Automation:*\n"
        "`/automate name|task|schedule` — Create automation\n"
        "`/automations` — List automations\n\n"
        "📊 *Info:*\n"
        "`/history` — Task history\n"
        "`/status` — Bot status\n"
        "`/style` — Change communication style\n\n"
        "📎 *Also supports:*\n"
        "• Voice messages (auto-transcribed)\n"
        "• Photos (GPT-4 Vision analysis)\n"
        "• PDF, DOCX, CSV, Excel files",
        parse_mode="Markdown"
    )


async def cmd_style(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [
        [InlineKeyboardButton("💬 Conversational", callback_data="style_conversational")],
        [InlineKeyboardButton("📋 Structured", callback_data="style_structured")],
        [InlineKeyboardButton("⚡ Concise", callback_data="style_concise")],
    ]
    await update.message.reply_text(
        "🎨 *Choose your communication style:*\n\n"
        "💬 *Conversational* — Warm, natural, thorough\n"
        "📋 *Structured* — Headers, bullets, organized\n"
        "⚡ *Concise* — Ultra-brief, max 3 sentences",
        parse_mode="Markdown",
        reply_markup=InlineKeyboardMarkup(keyboard)
    )


async def cmd_pdf(update: Update, context: ContextTypes.DEFAULT_TYPE):
    topic = " ".join(context.args) if context.args else None
    if not topic:
        await update.message.reply_text("Usage: `/pdf The Future of AI in Healthcare`", parse_mode="Markdown")
        return

    msg = await update.message.reply_text(f"📄 Generating PDF: *{topic}*...", parse_mode="Markdown")
    try:
        filepath = await pdf_svc.generate_pdf(topic, update.effective_user.id)
        await db.add_task(update.effective_user.id, "pdf", topic, "completed")
        await msg.delete()
        await update.message.reply_document(
            document=open(filepath, 'rb'),
            filename=f"{topic[:30].replace(' ', '_')}.pdf",
            caption=f"📄 PDF Report: *{topic}*", parse_mode="Markdown"
        )
    except Exception as e:
        await msg.edit_text(f"❌ Error: {str(e)}")


async def cmd_doc(update: Update, context: ContextTypes.DEFAULT_TYPE):
    topic = " ".join(context.args) if context.args else None
    if not topic:
        await update.message.reply_text("Usage: `/doc Quarterly Business Review`", parse_mode="Markdown")
        return

    msg = await update.message.reply_text(f"📝 Generating Word document: *{topic}*...", parse_mode="Markdown")
    try:
        filepath = await doc_svc.generate_document(topic, update.effective_user.id)
        await db.add_task(update.effective_user.id, "docx", topic, "completed")
        await msg.delete()
        await update.message.reply_document(
            document=open(filepath, 'rb'),
            filename=f"{topic[:30].replace(' ', '_')}.docx",
            caption=f"📝 Word Document: *{topic}*", parse_mode="Markdown"
        )
    except Exception as e:
        await msg.edit_text(f"❌ Error: {str(e)}")


async def cmd_report(update: Update, context: ContextTypes.DEFAULT_TYPE):
    topic = " ".join(context.args) if context.args else None
    if not topic:
        await update.message.reply_text("Usage: `/report Climate Change Solutions`", parse_mode="Markdown")
        return

    msg = await update.message.reply_text(f"📋 Generating report: *{topic}*...", parse_mode="Markdown")
    result = await ai.generate_report(topic)
    await db.add_task(update.effective_user.id, "report", topic, "completed")
    await msg.delete()
    chunks = [result[i:i+4000] for i in range(0, len(result), 4000)]
    for chunk in chunks:
        await update.message.reply_text(chunk)


async def cmd_code(update: Update, context: ContextTypes.DEFAULT_TYPE):
    description = " ".join(context.args) if context.args else None
    if not description:
        await update.message.reply_text("Usage: `/code Create a bar chart of sales data`", parse_mode="Markdown")
        return

    msg = await update.message.reply_text(f"💻 Writing & executing code: *{description[:50]}*...", parse_mode="Markdown")
    result = await code_svc.generate_and_run(description)
    await db.add_task(update.effective_user.id, "code", description, "completed")
    await msg.delete()

    code_preview = result['code'][:800] + "..." if len(result['code']) > 800 else result['code']
    output_preview = result['result'][:1200] + "..." if len(result['result']) > 1200 else result['result']

    await update.message.reply_text(
        f"💻 *Code:*\n```python\n{code_preview}\n```",
        parse_mode="Markdown"
    )
    await update.message.reply_text(
        f"📤 *Output:*\n```\n{output_preview}\n```",
        parse_mode="Markdown"
    )


async def cmd_research(update: Update, context: ContextTypes.DEFAULT_TYPE):
    topic = " ".join(context.args) if context.args else None
    if not topic:
        await update.message.reply_text("Usage: `/research Quantum Computing`", parse_mode="Markdown")
        return

    msg = await update.message.reply_text(f"🔬 Researching: *{topic}*...", parse_mode="Markdown")
    result = await research_svc.research(topic)
    await db.add_task(update.effective_user.id, "research", topic, "completed")
    await msg.delete()
    chunks = [result[i:i+4000] for i in range(0, len(result), 4000)]
    for chunk in chunks:
        await update.message.reply_text(chunk)


async def cmd_image(update: Update, context: ContextTypes.DEFAULT_TYPE):
    prompt = " ".join(context.args) if context.args else None
    if not prompt:
        await update.message.reply_text("Usage: `/image A futuristic city at sunset`", parse_mode="Markdown")
        return

    msg = await update.message.reply_text(f"🎨 Generating image: *{prompt[:50]}*...", parse_mode="Markdown")
    url = await ai.generate_image(prompt)
    await db.add_task(update.effective_user.id, "image", prompt, "completed")
    await msg.delete()
    if url.startswith("http"):
        await update.message.reply_photo(photo=url, caption=f"🖼 {prompt}")
    else:
        await update.message.reply_text(url)


async def cmd_memory(update: Update, context: ContextTypes.DEFAULT_TYPE):
    notes = await db.get_memory_notes(update.effective_user.id)
    if not notes:
        await update.message.reply_text("🧠 No memory notes saved.\n\nUse `/remember [note]` to save one.", parse_mode="Markdown")
        return
    text = "🧠 *Your Memory Notes:*\n\n"
    for i, (note_id, note, created) in enumerate(notes, 1):
        text += f"{i}. {note}\n   _{created[:10]}_\n\n"
    await update.message.reply_text(text, parse_mode="Markdown")


async def cmd_remember(update: Update, context: ContextTypes.DEFAULT_TYPE):
    note = " ".join(context.args) if context.args else None
    if not note:
        await update.message.reply_text("Usage: `/remember I prefer Python over JavaScript`", parse_mode="Markdown")
        return
    await db.add_memory_note(update.effective_user.id, note)
    await update.message.reply_text(f"✅ Saved to memory: _{note}_", parse_mode="Markdown")


async def cmd_clearmemory(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await db.clear_history(update.effective_user.id)
    await db.clear_memory_notes(update.effective_user.id)
    await update.message.reply_text("🗑️ Memory cleared! Starting fresh.")


async def cmd_history(update: Update, context: ContextTypes.DEFAULT_TYPE):
    tasks = await db.get_task_history(update.effective_user.id)
    await update.message.reply_text(format_task_history(tasks), parse_mode="Markdown")


async def cmd_automations(update: Update, context: ContextTypes.DEFAULT_TYPE):
    autos = await db.get_automations(update.effective_user.id)
    await update.message.reply_text(format_automations(autos), parse_mode="Markdown")


async def cmd_automate(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = " ".join(context.args) if context.args else ""
    parts = [p.strip() for p in text.split("|")]
    if len(parts) < 3:
        await update.message.reply_text(
            "Usage: `/automate name|task|schedule`\n\n"
            "Example: `/automate Daily News|Summarize today's AI news|every day at 9am`",
            parse_mode="Markdown"
        )
        return

    name, task, schedule = parts[0], parts[1], parts[2]
    if hasattr(context.application, 'automation_service'):
        success = await context.application.automation_service.add_automation(
            update.effective_user.id, name, task, schedule
        )
        if success:
            await update.message.reply_text(f"⚙️ Automation *{name}* created!\n📅 Schedule: {schedule}", parse_mode="Markdown")
        else:
            await update.message.reply_text("❌ Failed to create automation.")
    else:
        await db.add_automation(update.effective_user.id, name, task, schedule)
        await update.message.reply_text(f"⚙️ Automation *{name}* saved!\n📅 Schedule: {schedule}", parse_mode="Markdown")


async def cmd_status(update: Update, context: ContextTypes.DEFAULT_TYPE):
    tasks = await db.get_task_history(update.effective_user.id, limit=100)
    autos = await db.get_automations(update.effective_user.id)
    notes = await db.get_memory_notes(update.effective_user.id)
    style = await db.get_user_style(update.effective_user.id)

    await update.message.reply_text(
        f"📊 *Bot Status*\n\n"
        f"👤 User: {update.effective_user.first_name}\n"
        f"🎨 Style: {style}\n"
        f"📋 Tasks completed: {len(tasks)}\n"
        f"⚙️ Automations: {len(autos)}\n"
        f"🧠 Memory notes: {len(notes)}\n\n"
        f"🤖 Models: GPT-4o • DALL-E 3 • Whisper • Mistral Large\n"
        f"✅ All systems operational",
        parse_mode="Markdown"
    )
