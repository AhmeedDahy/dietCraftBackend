from typing import List, Dict, Optional
import time
import re
from core.llm_ag import OllamaModel
from core.code_executor import CodeExecutor
from config import settings


class CodeAgent:
    def __init__(self):
        self.llm = OllamaModel()
        self.executor = CodeExecutor(timeout=settings.code_execution_timeout)
        self.system_prompt = """You are an AI assistant that can execute Python code.
        Respond in Markdown format. For code, use ```python code blocks.
        For regular conversation, use normal Markdown formatting."""

    async def process_message(
        self, message: str, conversation_history: List[Dict[str, str]]
    ) -> Dict:
        conversation_history.append({"role": "user", "content": message})

        start_time = time.time()
        response = await self.llm.generate(
            messages=conversation_history, system_prompt=self.system_prompt
        )
        processing_time = time.time() - start_time

        result = {
            "content": response,
            "processing_time": f"{processing_time:.2f} seconds",
            "contains_code": False,
            "execution_result": None,
            "code_blocks": [],
        }

        if self.executor.contains_python_code(response):
            result["contains_code"] = True
            code_blocks = re.findall(r"```(?:python)?\n(.*?)\n```", response, re.DOTALL)
            result["code_blocks"] = [block.strip() for block in code_blocks]

            if code_blocks:
                stdout, stderr = await self.executor.execute_python_code(code_blocks[0])
                if stderr:
                    result["execution_result"] = f"Error: {stderr}"
                elif stdout:
                    result["execution_result"] = stdout

        conversation_history.append({"role": "assistant", "content": response})
        return result