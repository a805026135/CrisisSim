from __future__ import annotations
from enum import Enum
from typing import Optional
from pydantic import BaseModel, Field


class RoleType(str, Enum):
    VICTIM = "victim"
    KOL = "kol"
    SUPPORTER = "supporter"
    DECISION = "decision"


class SentimentLabel(str, Enum):
    POSITIVE = "positive"
    NEGATIVE = "negative"
    NEUTRAL = "neutral"


class AgentConfig(BaseModel):
    agent_id: str
    name: str
    role_type: RoleType
    persona_description: str
    stance: float = Field(default=0.0, ge=-1.0, le=1.0)
    influence_weight: float = Field(default=0.5, ge=0.1, le=1.0)
    speaking_style: str = "理性客观"


class Message(BaseModel):
    agent_id: str
    agent_name: str
    role_type: RoleType
    content: str
    round_number: int
    sentiment: Optional[SentimentLabel] = None
    is_official: bool = False
    reply_to: Optional[str] = None


class StrategyOption(BaseModel):
    strategy_id: str
    title: str
    description: str
    official_statement: str
    reasoning: str


class RoundState(BaseModel):
    round_number: int
    messages: list[Message] = Field(default_factory=list)
    agent_stances: dict[str, float] = Field(default_factory=dict)
    sentiment_distribution: dict[str, float] = Field(default_factory=dict)
    strategy_chosen: Optional[StrategyOption] = None
    decision_reflection: Optional[str] = None


class ScenarioConfig(BaseModel):
    scenario_id: str
    title: str
    summary: str
    brand_name: str
    initial_event: str
    channels: list[str]
    agent_configs: list[AgentConfig]


class ManualOpinion(BaseModel):
    """用户手动输入的舆情数据"""
    content: str
    source: str = "用户输入"
    sentiment_hint: Optional[str] = None


class SimulationResult(BaseModel):
    scenario: ScenarioConfig
    rounds: list[RoundState] = Field(default_factory=list)
    final_summary: str = ""
    total_tokens_used: int = 0
