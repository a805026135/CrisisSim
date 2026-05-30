from anthropic import AsyncAnthropic
from .provider import BaseProvider
from .. import config


class ClaudeProvider(BaseProvider):
    def __init__(self):
        self.client = AsyncAnthropic(api_key=config.ANTHROPIC_API_KEY)
        self.model = config.CLAUDE_MODEL

    async def generate(self, system_prompt: str, messages: list[dict], temperature: float = 0.8) -> str:
        resp = await self.client.messages.create(
            model=self.model,
            max_tokens=1024,
            system=system_prompt,
            messages=messages,
            temperature=temperature,
        )
        return resp.content[0].text

    def count_tokens(self, text: str) -> int:
        return len(text) // 2
