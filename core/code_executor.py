import re
import subprocess
import tempfile
import os
from typing import Tuple, Optional


class CodeExecutor:
    def __init__(self, timeout: int):
        self.timeout = timeout

    def contains_python_code(self, response: str) -> bool:
        return bool(re.search(r"```(?:python)?\n.*?\n```", response, re.DOTALL))

    def extract_python_code(self, response: str) -> Optional[str]:
        code_match = re.search(r"```(?:python)?\n(.*?)\n```", response, re.DOTALL)
        return code_match.group(1).strip() if code_match else None

    async def execute_python_code(self, code: str) -> Tuple[Optional[str], Optional[str]]:
        tmp_file_path = None
        try:
            with tempfile.NamedTemporaryFile(
                mode="w", suffix=".py", delete=False
            ) as tmp_file:
                tmp_file.write(code)
                tmp_file_path = tmp_file.name

            result = subprocess.run(
                ["python", tmp_file_path],
                capture_output=True,
                text=True,
                timeout=self.timeout,
            )
            return result.stdout.strip(), result.stderr.strip()
        except subprocess.TimeoutExpired:
            return None, "Execution timed out."
        except Exception as e:
            return None, str(e)
        finally:
            if tmp_file_path and os.path.exists(tmp_file_path):
                os.remove(tmp_file_path)