import asyncio
from typing import AsyncIterator
from openai import AsyncOpenAI, RateLimitError, APIConnectionError
from .provider import BaseProvider
from .. import config


class OpenAIProvider(BaseProvider):
    def __init__(self):
        self.client = AsyncOpenAI(
            api_key=config.OPENAI_API_KEY,
            base_url=config.OPENAI_BASE_URL,
            max_retries=0,
        )
        self.model = config.OPENAI_MODEL
        self._semaphore = asyncio.Semaphore(3)

    async def generate(self, system_prompt: str, messages: list[dict], temperature: float = 0.8) -> str:
        full_messages = [{"role": "system", "content": system_prompt}] + messages
        async with self._semaphore:
            for attempt in range(5):
                try:
                    resp = await self.client.chat.completions.create(
                        model=self.model,
                        messages=full_messages,
                        temperature=temperature,
                        max_tokens=1024,
                    )
                    return resp.choices[0].message.content or ""
                except RateLimitError:
                    if attempt == 4:
                        raise
                    await asyncio.sleep(2 ** attempt + 1)
                except APIConnectionError:
                    if attempt == 4:
                        raise
                    await asyncio.sleep(2)
        return ""

    async def generate_stream(self, system_prompt: str, messages: list[dict], temperature: float = 0.8) -> AsyncIterator[str]:
        full_messages = [{"role": "system", "content": system_prompt}] + messages
        async with self._semaphore:
            for attempt in range(5):
                try:
                    stream = await self.client.chat.completions.create(
                        model=self.model,
                        messages=full_messages,
                        temperature=temperature,
                        max_tokens=1024,
                        stream=True,
                    )
                    async for chunk in stream:
                        delta = chunk.choices[0].delta if chunk.choices else None
                        if delta and delta.content:
                            yield delta.content
                    return
                except RateLimitError:
                    if attempt == 4:
                        raise
                    await asyncio.sleep(2 ** attempt + 1)
                except APIConnectionError:
                    if attempt == 4:
                        raise
                    await asyncio.sleep(2)

    def count_tokens(self, text: str) -> int:
        return len(text) // 2
