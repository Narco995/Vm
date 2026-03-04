import re
from bot.services.ai_service import AIService
from bot.services.llm_providers.base import TaskType


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
            "reasoning": any(kw in text_lower for kw in ["explain why", "reason", "logic", "argument", "prove", "analyze the logic"]),
            "quick": any(kw in text_lower for kw in ["quickly", "fast", "brief", "short"]),
        }
        detected = [k for k, v in intents.items() if v]
        return {"intents": detected, "primary": detected[0] if detected else "chat"}

    def get_task_type_for_intent(self, intent: str) -> TaskType:
        """Map intent to TaskType for optimal provider routing"""
        intent_to_task = {
            "write_code": TaskType.CODING,
            "research": TaskType.RESEARCH,
            "analyze_data": TaskType.ANALYSIS,
            "summarize": TaskType.SPEED_CRITICAL,
            "translate": TaskType.CHAT,
            "reasoning": TaskType.REASONING,
            "quick": TaskType.SPEED_CRITICAL,
            "generate_image": TaskType.VISION,
            "generate_pdf": TaskType.LONG_CONTEXT,
            "generate_doc": TaskType.LONG_CONTEXT,
        }
        return intent_to_task.get(intent, TaskType.CHAT)

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

        # Get task type for intelligent routing
        task_type = self.get_task_type_for_intent(primary)
        
        # Use the AI service with task type for optimal routing
        return await self.ai.chat(messages, style=style, task_type=task_type)
