import httpx
from .provider import BaseProvider
from .. import config


class OllamaProvider(BaseProvider):
    def __init__(self):
        self.base_url = config.OLLAMA_BASE_URL
        self.model = config.OLLAMA_MODEL

    async def generate(self, system_prompt: str, messages: list[dict], temperature: float = 0.8) -> str:
        full_messages = [{"role": "system", "content": system_prompt}] + messages
        async with httpx.AsyncClient(timeout=120) as client:
            resp = await client.post(
                f"{self.base_url}/api/chat",
                json={"model": self.model, "messages": full_messages, "stream": False,
                       "options": {"temperature": temperature}},
            )
            resp.raise_for_status()
            return resp.json()["message"]["content"]

    def count_tokens(self, text: str) -> int:
        return len(text) // 2
