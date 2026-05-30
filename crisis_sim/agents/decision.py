from __future__ import annotations
import json
from dataclasses import dataclass
from typing import AsyncIterator
from crisis_sim.agents.base import BaseAgent, MemoryEntry
from crisis_sim.models.schemas import (
    AgentConfig, RoleType, StrategyOption, Message, SentimentLabel,
)
from crisis_sim.llm.provider import BaseProvider


@dataclass
class DecisionAgent(BaseAgent):
    scenario_context: str = ""
    reflections: list[str] = None

    def __post_init__(self):
        super().__post_init__()
        if self.reflections is None:
            self.reflections = []

    def _build_sentiment_summary(self, messages: list[Message]) -> str:
        if not messages:
            return "尚无舆论反应。"
        pos = sum(1 for m in messages if m.sentiment == SentimentLabel.POSITIVE)
        neg = sum(1 for m in messages if m.sentiment == SentimentLabel.NEGATIVE)
        neu = sum(1 for m in messages if m.sentiment == SentimentLabel.NEUTRAL)
        total = len(messages)
        lines = [
            f"共 {total} 条发言：正面 {pos}({pos/total*100:.0f}%), "
            f"负面 {neg}({neg/total*100:.0f}%), 中性 {neu}({neu/total*100:.0f}%)"
        ]
        for m in messages:
            lines.append(f"- [{m.agent_name}/{m.role_type.value}] {m.content[:80]}...")
        return "\n".join(lines)

    def _build_strategy_prompt(self, current_messages: list[Message], round_number: int) -> str:
        sentiment_summary = self._build_sentiment_summary(current_messages)
        return f"""你是一位资深危机公关顾问。当前危机场景：
{self.scenario_context}

【第 {round_number} 轮舆情态势】
{sentiment_summary}

【之前的策略与反思】
{chr(10).join(self.reflections[-2:]) if self.reflections else '这是第一轮，暂无历史。'}

请给出 2 个可行的应对策略。以 JSON 数组格式返回，每个策略包含：
- strategy_id: "A" 或 "B"
- title: 策略标题（5-10字）
- description: 策略描述（1-2句）
- official_statement: 按此策略发布的官方声明全文（50-100字，模拟真实公关稿风格）
- reasoning: 选择此策略的理由（1-2句）

只返回 JSON 数组，不要有其他文字。"""

    def _parse_strategies(self, raw: str) -> list[StrategyOption]:
        try:
            raw_clean = raw.strip()
            if raw_clean.startswith("```"):
                raw_clean = raw_clean.split("\n", 1)[1].rsplit("```", 1)[0].strip()
            data = json.loads(raw_clean)
            return [StrategyOption(**s) for s in data[:2]]
        except (json.JSONDecodeError, Exception):
            return [
                StrategyOption(
                    strategy_id="A", title="诚恳道歉并承诺赔偿",
                    description="发布道歉声明，宣布赔偿方案和整改措施。",
                    official_statement="我们对此次事件深表歉意。已成立专项小组调查，将对受影响消费者进行赔偿，并全面排查产品质量。",
                    reasoning="诚恳态度有助于挽回公众信任，展现企业责任感。",
                ),
                StrategyOption(
                    strategy_id="B", title="技术性澄清与证据展示",
                    description="发布技术检测报告，从专业角度解释情况。",
                    official_statement="我们高度重视此事。经第三方权威机构检测，产品符合国家标准。我们将公布完整检测报告，欢迎社会各界监督。",
                    reasoning="用事实和数据说话，避免情绪化回应，但可能被认为缺乏同理心。",
                ),
            ]

    async def generate_strategies(
        self, current_messages: list[Message], round_number: int
    ) -> list[StrategyOption]:
        prompt = self._build_strategy_prompt(current_messages, round_number)
        messages = [{"role": "user", "content": prompt}]
        raw = await self.llm.generate("你是危机公关策略专家。", messages, temperature=0.7)
        return self._parse_strategies(raw)

    async def generate_strategies_stream(
        self, current_messages: list[Message], round_number: int
    ) -> AsyncIterator[str]:
        """流式生成策略，逐块 yield 文本，最后 yield 完整 JSON"""
        prompt = self._build_strategy_prompt(current_messages, round_number)
        messages = [{"role": "user", "content": prompt}]
        full_text = ""
        async for chunk in self.llm.generate_stream("你是危机公关策略专家。", messages, temperature=0.7):
            full_text += chunk
            yield chunk
        # 最终解析结果
        strategies = self._parse_strategies(full_text)
        yield "\n__STRATEGIES_JSON__\n" + json.dumps(
            [{"strategy_id": s.strategy_id, "title": s.title, "description": s.description,
              "official_statement": s.official_statement, "reasoning": s.reasoning}
             for s in strategies], ensure_ascii=False
        )

    async def generate_statement(self, strategy: StrategyOption) -> str:
        return strategy.official_statement

    async def reflect(self, strategy: StrategyOption, messages: list[Message]) -> str:
        sentiment_summary = self._build_sentiment_summary(messages)
        prompt = f"""作为公关顾问，请评估本轮策略效果。

【采用的策略】{strategy.title}: {strategy.description}
【发布的声明】{strategy.official_statement}

【舆论反应统计】
{sentiment_summary}

请简要评估：策略效果如何？哪些方面有效？哪些方面可能适得其反？下一步建议。
控制在 3-5 句话。"""

        reflection = await self.llm.generate(
            "你是危机公关复盘专家。", [{"role": "user", "content": prompt}], temperature=0.5
        )
        self.reflections.append(reflection)
        return reflection
