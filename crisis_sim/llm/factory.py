from .provider import BaseProvider
from .. import config


def create_provider() -> BaseProvider:
    name = config.LLM_PROVIDER.lower()
    if name == "openai":
        from .openai_provider import OpenAIProvider
        return OpenAIProvider()
    elif name == "claude":
        from .claude_provider import ClaudeProvider
        return ClaudeProvider()
    elif name == "ollama":
        from .ollama_provider import OllamaProvider
        return OllamaProvider()
    else:
        raise ValueError(f"Unknown LLM provider: {name}")
