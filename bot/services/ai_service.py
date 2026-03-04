import asyncio
from openai import AsyncOpenAI
from mistralai import Mistral
from config import OPENAI_API_KEY, MISTRAL_API_KEY, GPT_MODEL, MISTRAL_MODEL, COMMUNICATION_STYLES
import base64


class AIService:
    def __init__(self):
        self.openai = AsyncOpenAI(api_key=OPENAI_API_KEY)
        self.mistral = Mistral(api_key=MISTRAL_API_KEY)

    async def chat(self, messages: list, style: str = "conversational", use_mistral: bool = False) -> str:
        style_prompt = COMMUNICATION_STYLES.get(style, COMMUNICATION_STYLES["conversational"])
        system = f"You are an advanced AI assistant. {style_prompt} You help users with any task — research, coding, writing, analysis, and more."

        try:
            if use_mistral:
                response = await asyncio.get_event_loop().run_in_executor(
                    None,
                    lambda: self.mistral.chat.complete(
                        model=MISTRAL_MODEL,
                        messages=[{"role": "system", "content": system}] + messages
                    )
                )
                return response.choices[0].message.content
            else:
                response = await self.openai.chat.completions.create(
                    model=GPT_MODEL,
                    messages=[{"role": "system", "content": system}] + messages,
                    max_tokens=4096
                )
                return response.choices[0].message.content
        except Exception as e:
            return f"❌ AI error: {str(e)}"

    async def analyze_image(self, image_data: bytes, prompt: str = "Describe this image in detail.") -> str:
        try:
            b64 = base64.b64encode(image_data).decode("utf-8")
            response = await self.openai.chat.completions.create(
                model=GPT_MODEL,
                messages=[{
                    "role": "user",
                    "content": [
                        {"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{b64}"}},
                        {"type": "text", "text": prompt}
                    ]
                }],
                max_tokens=1024
            )
            return response.choices[0].message.content
        except Exception as e:
            return f"❌ Vision error: {str(e)}"

    async def transcribe_audio(self, audio_path: str) -> str:
        try:
            with open(audio_path, "rb") as f:
                response = await self.openai.audio.transcriptions.create(
                    model="whisper-1",
                    file=f
                )
            return response.text
        except Exception as e:
            return f"❌ Transcription error: {str(e)}"

    async def generate_image(self, prompt: str) -> str:
        try:
            response = await self.openai.images.generate(
                model="dall-e-3",
                prompt=prompt,
                n=1,
                size="1024x1024",
                quality="standard"
            )
            return response.data[0].url
        except Exception as e:
            return f"❌ Image generation error: {str(e)}"

    async def research(self, topic: str, style: str = "structured") -> str:
        messages = [{
            "role": "user",
            "content": f"""Conduct comprehensive research on: {topic}

Structure your response with:
1. **Executive Summary** (2-3 sentences)
2. **Background & Context**
3. **Key Findings** (5-7 bullet points)
4. **Current Developments**
5. **Implications & Applications**
6. **Expert Perspectives**
7. **Conclusion & Recommendations**

Be thorough, cite relevant examples, and provide actionable insights."""
        }]
        return await self.chat(messages, style=style)

    async def generate_report(self, topic: str) -> str:
        messages = [{
            "role": "user",
            "content": f"""Create a professional structured report on: {topic}

Include: Executive Summary, Introduction, Methodology, Findings, Analysis, Recommendations, Conclusion.
Use professional language, data-driven insights, and clear section headers."""
        }]
        return await self.chat(messages, style="structured")

    async def analyze_data_text(self, data_summary: str, style: str = "structured") -> str:
        messages = [{
            "role": "user",
            "content": f"Analyze this data and provide insights, patterns, and recommendations:\n\n{data_summary}"
        }]
        return await self.chat(messages, style=style)
