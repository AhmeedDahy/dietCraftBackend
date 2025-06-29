from typing import List, Dict
from ollama import Client
from config import settings


class OllamaModel:
    def __init__(self, model: str = settings.ollama_model):
        self.model = model
        self.client = Client()

    async def generate(
        self, messages: List[Dict[str, str]], system_prompt: str
    ) -> str:
        chat_messages = [{"role": "system", "content": system_prompt}]
        chat_messages.extend(messages)
        response = self.client.chat(model=self.model, messages=chat_messages)
        return response["message"]["content"]