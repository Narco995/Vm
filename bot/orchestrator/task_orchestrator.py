import re
from bot.services.ai_service import AIService


class TaskOrchestrator:
    def __init__(self):
        self.ai = AIService()

    def detect_intent(self, text: str) -> dict:
        text_lower = text.lower()
        intents = {
            "generate_image": any(kw in text_lower for kw in ["generate image", "create image", "draw", "make a picture", "dall-e"]),
            "write_code": any(kw in text_lower for kw in ["write code", "create script", "code for", "python script", "program that"]),
            "research": any(kw in text_lower for kw in ["research", "investigate", "find out about", "what is", "explain in depth"]),
            "generate_pdf": any(kw in text_lower for kw in ["create pdf", "generate pdf", "make pdf"]),
            "generate_doc": any(kw in text_lower for kw in ["create doc", "word doc", "make document", "write a report"]),
            "analyze_data": any(kw in text_lower for kw in ["analyze", "analyse", "csv", "excel", "data"]),
            "summarize": any(kw in text_lower for kw in ["summarize", "summarise", "tldr", "key points"]),
            "translate": any(kw in text_lower for kw in ["translate", "in spanish", "in french", "in arabic", "in chinese"]),
        }
        detected = [k for k, v in intents.items() if v]
        return {"intents": detected, "primary": detected[0] if detected else "chat"}

    async def process(self, text: str, history: list, style: str, memory_notes: list) -> str:
        intent = self.detect_intent(text)
        primary = intent["primary"]

        # Build context from memory
        memory_context = ""
        if memory_notes:
            memory_context = "\n\nUser memory notes:\n" + "\n".join([f"- {n[1]}" for n in memory_notes[:5]])

        messages = history[-20:] + [{"role": "user", "content": text + memory_context}]

        # Enrich prompt based on intent
        if primary == "summarize":
            messages[-1]["content"] = f"Provide a clear, concise summary of: {text}"
        elif primary == "translate":
            messages[-1]["content"] = text

        return await self.ai.chat(messages, style=style)
