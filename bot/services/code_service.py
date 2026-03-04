import asyncio
import subprocess
import os
import sys
import tempfile
import traceback
from config import CODE_EXECUTION_TIMEOUT, TEMP_DIR
from bot.services.ai_service import AIService
from bot.services.llm_providers.base import TaskType


class CodeService:
    def __init__(self):
        self.ai = AIService()
        self.timeout = CODE_EXECUTION_TIMEOUT

    async def generate_and_run(self, description: str, style: str = "conversational") -> dict:
        messages = [{
            "role": "user",
            "content": f"""Write Python code to: {description}

Requirements:
- Complete, runnable Python script
- Include all necessary imports
- Add print() statements to show output
- Handle errors gracefully
- No external APIs unless specified
- Return ONLY the Python code, no markdown fences"""
        }]

        # Use coding-optimized provider
        code = await self.ai.chat(messages, style="concise", task_type=TaskType.CODING)
        code = code.strip()
        if code.startswith("```python"):
            code = code[9:]
        if code.startswith("```"):
            code = code[3:]
        if code.endswith("```"):
            code = code[:-3]
        code = code.strip()

        result = await self.execute_code(code)
        return {"code": code, "result": result}

    async def execute_code(self, code: str) -> str:
        try:
            with tempfile.NamedTemporaryFile(mode='w', suffix='.py', dir=TEMP_DIR, delete=False) as f:
                f.write(code)
                tmp_path = f.name

            loop = asyncio.get_event_loop()
            result = await loop.run_in_executor(
                None,
                lambda: subprocess.run(
                    [sys.executable, tmp_path],
                    capture_output=True,
                    text=True,
                    timeout=self.timeout,
                    cwd=TEMP_DIR
                )
            )

            os.unlink(tmp_path)

            output = ""
            if result.stdout:
                output += result.stdout
            if result.stderr:
                output += f"\n⚠️ Stderr:\n{result.stderr}"
            if not output.strip():
                output = "✅ Code executed successfully (no output)"

            return output[:3000]

        except subprocess.TimeoutExpired:
            return f"⏱️ Code execution timed out after {self.timeout}s"
        except Exception as e:
            return f"❌ Execution error: {str(e)}\n{traceback.format_exc()[:500]}"

    async def explain_code(self, code: str, style: str = "conversational") -> str:
        messages = [{
            "role": "user",
            "content": f"Explain this code clearly:\n\n```python\n{code}\n```"
        }]
        # Use reasoning-optimized provider for code explanation
        return await self.ai.chat(messages, style=style, task_type=TaskType.REASONING)
