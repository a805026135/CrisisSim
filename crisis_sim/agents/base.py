from __future__ import annotations
from dataclasses import dataclass, field
from crisis_sim.models.schemas import AgentConfig, RoleType, Message, SentimentLabel
from crisis_sim.llm.provider import BaseProvider
from crisis_sim import config


@dataclass
class MemoryEntry:
    round_number: int
    content: str
    source_agent: str
    sentiment: SentimentLabel | None = None


@dataclass
class BaseAgent:
    cfg: AgentConfig
    llm: BaseProvider

    stance: float = 0.0
    short_term_memory: list[MemoryEntry] = field(default_factory=list)
    stance_history: list[float] = field(default_factory=list)
    trust_scores: dict[str, float] = field(default_factory=dict)

    def __post_init__(self):
        self.stance = self.cfg.stance
        self.stance_history.append(self.stance)

    @property
    def agent_id(self) -> str:
        return self.cfg.agent_id

    @property
    def name(self) -> str:
        return self.cfg.name

    @property
    def role_type(self) -> RoleType:
        return self.cfg.role_type

    def add_memory(self, entry: MemoryEntry):
        self.short_term_memory.append(entry)
        if len(self.short_term_memory) > config.MEMORY_WINDOW * 10:
            self.short_term_memory = self.short_term_memory[-config.MEMORY_WINDOW * 5:]

    def get_recent_context(self, n: int | None = None) -> str:
        n = n or config.MEMORY_WINDOW
        recent = self.short_term_memory[-n:]
        if not recent:
            return "暂无相关记忆。"
        lines = []
        for m in recent:
            prefix = f"[{m.source_agent}]"
            lines.append(f"{prefix} {m.content}")
        return "\n".join(lines)

    def update_stance(self, delta: float):
        self.stance = max(-1.0, min(1.0, self.stance + delta))
        self.stance_history.append(self.stance)

    def _build_base_system_prompt(self) -> str:
        stance_desc = "强烈反对" if self.stance < -0.5 else \
                      "轻微反对" if self.stance < -0.1 else \
                      "中立" if self.stance < 0.1 else \
                      "轻微支持" if self.stance < 0.5 else "强烈支持"

        return f"""你是 {self.name}，在一场舆论危机中的参与者。

角色设定：{self.cfg.persona_description}
发言风格：{self.cfg.speaking_style}
当前立场：{stance_desc}（数值: {self.stance:.2f}，范围 -1 到 1）

你必须始终保持角色一致性，用该角色的口吻和视角发言。
发言简洁，控制在 2-4 句话，模拟真实社交媒体风格。
不要暴露自己是 AI，不要使用括号标注动作。
"""
