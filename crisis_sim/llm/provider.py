from abc import ABC, abstractmethod
from typing import AsyncIterator


class BaseProvider(ABC):
    @abstractmethod
    async def generate(self, system_prompt: str, messages: list[dict], temperature: float = 0.8) -> str:
        ...

    @abstractmethod
    async def generate_stream(self, system_prompt: str, messages: list[dict], temperature: float = 0.8) -> AsyncIterator[str]:
        """流式生成，逐块 yield 文本片段"""
        ...

    @abstractmethod
    def count_tokens(self, text: str) -> int:
        ...
