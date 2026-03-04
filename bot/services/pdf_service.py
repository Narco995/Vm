import os
import re
from fpdf import FPDF
from datetime import datetime
from config import TEMP_DIR
from bot.services.ai_service import AIService
import pdfplumber


class PDFService:
    def __init__(self):
        self.ai = AIService()

    async def generate_pdf(self, topic: str, user_id: int) -> str:
        # Generate report content (will use optimized provider for long context)
        content = await self.ai.generate_report(topic)

        pdf = FPDF()
        pdf.add_page()
        pdf.set_auto_page_break(auto=True, margin=15)

        # Title
        pdf.set_font("Helvetica", "B", 24)
        pdf.set_text_color(44, 62, 80)
        pdf.multi_cell(0, 12, topic, align="C")
        pdf.ln(4)

        # Date
        pdf.set_font("Helvetica", "", 10)
        pdf.set_text_color(127, 140, 141)
        pdf.cell(0, 8, f"Generated: {datetime.now().strftime('%B %d, %Y')}", align="C")
        pdf.ln(10)

        # Divider
        pdf.set_draw_color(52, 152, 219)
        pdf.set_line_width(0.5)
        pdf.line(15, pdf.get_y(), 195, pdf.get_y())
        pdf.ln(8)

        # Content
        lines = content.split('\n')
        for line in lines:
            line = line.strip()
            if not line:
                pdf.ln(3)
                continue

            if line.startswith('## ') or (line.startswith('**') and line.endswith('**')):
                text = line.lstrip('#').strip().strip('*')
                pdf.set_font("Helvetica", "B", 14)
                pdf.set_text_color(22, 58, 92)
                pdf.ln(4)
                pdf.multi_cell(0, 8, text)
                pdf.ln(2)
            elif line.startswith('# '):
                text = line.lstrip('#').strip()
                pdf.set_font("Helvetica", "B", 16)
                pdf.set_text_color(44, 62, 80)
                pdf.ln(6)
                pdf.multi_cell(0, 10, text)
                pdf.ln(3)
            elif line.startswith('- ') or line.startswith('• ') or line.startswith('* '):
                text = "  • " + line.lstrip('-•* ').strip()
                text = re.sub(r'\*\*(.*?)\*\*', r'\1', text)
                pdf.set_font("Helvetica", "", 11)
                pdf.set_text_color(44, 62, 80)
                pdf.multi_cell(0, 7, text)
            else:
                clean = re.sub(r'\*\*(.*?)\*\*', r'\1', line)
                pdf.set_font("Helvetica", "", 11)
                pdf.set_text_color(44, 62, 80)
                pdf.multi_cell(0, 7, clean)

        # Footer
        pdf.set_y(-20)
        pdf.set_font("Helvetica", "I", 8)
        pdf.set_text_color(149, 165, 166)
        pdf.cell(0, 8, f"Page {pdf.page_no()} — AI Generated Report", align="C")

        filename = f"report_{user_id}_{int(datetime.now().timestamp())}.pdf"
        filepath = os.path.join(TEMP_DIR, filename)
        pdf.output(filepath)
        return filepath

    async def read_pdf(self, filepath: str) -> str:
        try:
            with pdfplumber.open(filepath) as pdf:
                text = ""
                for page in pdf.pages[:10]:
                    text += page.extract_text() or ""
                return text[:8000] if text else "No text extracted."
        except Exception as e:
            return f"Error reading PDF: {str(e)}"
