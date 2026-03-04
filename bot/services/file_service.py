import os
import aiohttp
import aiofiles
from docx import Document
from config import TEMP_DIR, MAX_FILE_SIZE_MB
import pdfplumber


class FileService:
    async def download_file(self, file_url: str, filename: str) -> str:
        filepath = os.path.join(TEMP_DIR, filename)
        async with aiohttp.ClientSession() as session:
            async with session.get(file_url) as resp:
                if resp.status == 200:
                    async with aiofiles.open(filepath, 'wb') as f:
                        await f.write(await resp.read())
        return filepath

    async def extract_text(self, filepath: str) -> str:
        ext = os.path.splitext(filepath)[1].lower()
        try:
            if ext == '.pdf':
                return await self._extract_pdf(filepath)
            elif ext in ['.docx', '.doc']:
                return self._extract_docx(filepath)
            elif ext in ['.txt', '.md', '.py', '.js', '.html', '.css']:
                with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
                    return f.read()[:8000]
            elif ext in ['.csv']:
                with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
                    return f.read()[:4000]
            else:
                return None
        except Exception as e:
            return f"Error extracting text: {str(e)}"

    async def _extract_pdf(self, filepath: str) -> str:
        with pdfplumber.open(filepath) as pdf:
            text = ""
            for page in pdf.pages[:15]:
                text += page.extract_text() or ""
        return text[:8000]

    def _extract_docx(self, filepath: str) -> str:
        doc = Document(filepath)
        return "\n".join([p.text for p in doc.paragraphs])[:8000]

    def is_data_file(self, filename: str) -> bool:
        return os.path.splitext(filename)[1].lower() in ['.csv', '.xlsx', '.xls', '.json']

    def is_image_file(self, filename: str) -> bool:
        return os.path.splitext(filename)[1].lower() in ['.jpg', '.jpeg', '.png', '.gif', '.webp']
