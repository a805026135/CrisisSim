from __future__ import annotations
import asyncio
from dataclasses import dataclass, field
from pathlib import Path
from crisis_sim.models.schemas import (
    ScenarioConfig, AgentConfig, RoleType, Message, SentimentLabel,
    StrategyOption, RoundState, SimulationResult,
)
from crisis_sim.agents.persona import PersonaAgent
from crisis_sim.agents.decision import DecisionAgent
from crisis_sim.agents.base import MemoryEntry
from crisis_sim.analysis.sentiment import classify_message, compute_round_stats, extract_keywords
from crisis_sim.llm.provider import BaseProvider
from crisis_sim.rag.vector_store import VectorStore
from crisis_sim.rag.document_processor import DocumentProcessor
from crisis_sim.scenarios.knowledge_data import get_knowledge, get_opinion_seeds
from crisis_sim import config


@dataclass
class SimulationEngine:
    scenario: ScenarioConfig
    llm: BaseProvider

    persona_agents: list[PersonaAgent] = field(default_factory=list)
    decision_agent: DecisionAgent = None
    rounds: list[RoundState] = field(default_factory=list)
    all_messages: list[Message] = field(default_factory=list)
    current_round: int = 0
    total_tokens: int = 0
    vector_store: VectorStore = field(default_factory=VectorStore)

    def initialize(self):
        self.persona_agents = []
        for ac in self.scenario.agent_configs:
            agent = PersonaAgent(cfg=ac, llm=self.llm)
            self.persona_agents.append(agent)

        decision_cfg = AgentConfig(
            agent_id="decision", name="公关决策顾问",
            role_type=RoleType.DECISION,
            persona_description="资深危机公关顾问",
            stance=0.0, influence_weight=1.0, speaking_style="专业理性",
        )
        self.decision_agent = DecisionAgent(
            cfg=decision_cfg, llm=self.llm,
            scenario_context=f"品牌: {self.scenario.brand_name}\n事件: {self.scenario.summary}",
        )
        # 自动加载预置知识库和舆情种子
        self._load_preset_knowledge()

    def _load_preset_knowledge(self):
        sid = self.scenario.scenario_id
        kb_docs = get_knowledge(sid)
        if kb_docs:
            chunks = DocumentProcessor.process_text("\n\n".join(kb_docs), source="预置知识库")
            self.vector_store.add_to_knowledge_base(chunks)
        seeds = get_opinion_seeds(sid)
        if seeds:
            self.vector_store.add_opinions(seeds, [{"source": "预置舆情"} for _ in seeds])

    # ---- RAG 操作 ----
    def add_document(self, file_path: str, filename: str | None = None) -> int:
        chunks = DocumentProcessor.process(file_path, filename)
        return self.vector_store.add_to_knowledge_base(chunks)

    def add_manual_opinion(self, text: str, source: str = "用户输入") -> int:
        chunks = DocumentProcessor.process_text(text, source=source)
        return self.vector_store.add_to_knowledge_base(chunks)

    def add_raw_opinion(self, text: str) -> int:
        return self.vector_store.add_opinions([text])

    def _get_rag_context(self, query: str) -> tuple[str, str]:
        kb_results = self.vector_store.query_knowledge_base(query, n_results=3)
        op_results = self.vector_store.query_opinions(query, n_results=3)
        kb_text = "\n".join(kb_results) if kb_results else ""
        op_text = "\n".join(op_results) if op_results else ""
        return kb_text, op_text

    # ---- 模拟流程 ----
    async def generate_initial_event(self) -> Message:
        msg = Message(
            agent_id="system", agent_name="事件起源",
            role_type=RoleType.VICTIM, content=self.scenario.initial_event,
            round_number=0, sentiment=SentimentLabel.NEGATIVE, is_official=False,
        )
        self.all_messages.append(msg)
        for agent in self.persona_agents:
            agent.add_memory(MemoryEntry(
                round_number=0, content=self.scenario.initial_event,
                source_agent="事件起源", sentiment=SentimentLabel.NEGATIVE,
            ))
        return msg

    async def get_strategies(self) -> list[StrategyOption]:
        return await self.decision_agent.generate_strategies(
            self.all_messages, self.current_round + 1
        )

    async def execute_round(self, strategy: StrategyOption, progress_cb=None) -> RoundState:
        def _progress(msg: str):
            if progress_cb:
                progress_cb(msg)

        self.current_round += 1
        round_state = RoundState(
            round_number=self.current_round,
            strategy_chosen=strategy,
        )

        _progress("正在生成官方声明...")
        official_statement = await self.decision_agent.generate_statement(strategy)
        official_msg = Message(
            agent_id="decision", agent_name=f"{self.scenario.brand_name}官方",
            role_type=RoleType.DECISION, content=official_statement,
            round_number=self.current_round, is_official=True,
        )
        round_state.messages.append(official_msg)
        self.all_messages.append(official_msg)

        for agent in self.persona_agents:
            agent.add_memory(MemoryEntry(
                round_number=self.current_round, content=official_statement,
                source_agent=f"{self.scenario.brand_name}官方",
            ))

        # ── 并行生成所有 Agent 反应 ──
        _progress(f"正在并行模拟 {len(self.persona_agents)} 个角色反应...")

        async def _agent_react(agent: PersonaAgent) -> Message:
            rag_kb, rag_ops = self._get_rag_context(
                f"{self.scenario.title} {self.scenario.summary}"
            )
            msgs_prompt, sys_prompt = agent.generate_reaction(
                self.scenario.initial_event,
                round_state.messages,
                rag_knowledge=rag_kb,
                rag_opinions=rag_ops,
            )
            content = await self.llm.generate(sys_prompt, msgs_prompt, temperature=0.85)
            msg = agent.parse_response(content, self.current_round)
            msg.sentiment = await classify_message(self.llm, msg)
            return msg

        results = await asyncio.gather(
            *[_agent_react(a) for a in self.persona_agents],
            return_exceptions=True,
        )

        agent_messages: list[Message] = []
        for agent, result in zip(self.persona_agents, results):
            if isinstance(result, Exception):
                continue
            agent_messages.append(result)
            round_state.messages.append(result)
            self.all_messages.append(result)

        # ── 并行生成 KOL 互动 ──
        _progress("正在生成互动讨论...")

        async def _kol_followup(agent: PersonaAgent) -> Message | None:
            other_recent = [m for m in agent_messages if m.agent_id != agent.agent_id][:4]
            if not other_recent:
                return None
            context = "\n".join(f"[{m.agent_name}] {m.content}" for m in other_recent)
            follow_prompt = [
                {"role": "user", "content": f"基于以下最新讨论，请补充你的观点或回应（1-2句）：\n{context}"}
            ]
            content = await self.llm.generate(agent.build_system_prompt(), follow_prompt, temperature=0.8)
            if len(content.strip()) <= 5:
                return None
            follow_msg = Message(
                agent_id=agent.agent_id, agent_name=agent.name,
                role_type=agent.role_type, content=content.strip(),
                round_number=self.current_round,
                reply_to=other_recent[-1].agent_id,
            )
            follow_msg.sentiment = await classify_message(self.llm, follow_msg)
            return follow_msg

        kol_agents = [a for a in self.persona_agents if a.role_type == RoleType.KOL]
        if kol_agents:
            kol_results = await asyncio.gather(
                *[_kol_followup(a) for a in kol_agents],
                return_exceptions=True,
            )
            for result in kol_results:
                if isinstance(result, Exception) or result is None:
                    continue
                round_state.messages.append(result)
                self.all_messages.append(result)

        for agent in self.persona_agents:
            agent.update_stance_from_messages(round_state.messages)
            for msg in round_state.messages:
                if msg.agent_id != agent.agent_id:
                    agent.add_memory(MemoryEntry(
                        round_number=self.current_round, content=msg.content,
                        source_agent=msg.agent_name, sentiment=msg.sentiment,
                    ))

        round_state.agent_stances = {a.agent_id: round(a.stance, 3) for a in self.persona_agents}
        round_state.sentiment_distribution = compute_round_stats(round_state.messages)

        round_state.decision_reflection = await self.decision_agent.reflect(
            strategy, round_state.messages
        )

        self.rounds.append(round_state)
        return round_state

    def get_sentiment_trend(self) -> list[dict[str, float]]:
        return [r.sentiment_distribution for r in self.rounds]

    def get_stance_evolution(self) -> dict[str, list[float]]:
        result = {}
        for agent in self.persona_agents:
            result[agent.name] = agent.stance_history
        return result

    def build_result(self) -> SimulationResult:
        summary_parts = []
        for i, r in enumerate(self.rounds, 1):
            sd = r.sentiment_distribution
            summary_parts.append(
                f"第{i}轮 [{r.strategy_chosen.title if r.strategy_chosen else '?'}]: "
                f"正{sd.get('positive',0)*100:.0f}% 负{sd.get('negative',0)*100:.0f}% 中{sd.get('neutral',0)*100:.0f}%"
            )
        return SimulationResult(
            scenario=self.scenario, rounds=self.rounds,
            final_summary="\n".join(summary_parts),
            total_tokens_used=self.total_tokens,
        )
