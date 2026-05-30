from __future__ import annotations
from dataclasses import dataclass
from crisis_sim.agents.base import BaseAgent, MemoryEntry
from crisis_sim.models.schemas import RoleType, Message, SentimentLabel
from crisis_sim import config


ROLE_SYSTEM_PROMPTS = {
    RoleType.VICTIM: """你是一位直接受到事件影响的消费者/受害者。
你的情绪以愤怒、焦虑和维权诉求为主。你关注的核心是：谁来负责？怎么赔偿？
你会引用自己的亲身经历，语气直接且带情绪。
当看到道歉和赔偿方案时，你可能会稍微缓和；若看到推卸责任，你会更加愤怒。""",

    RoleType.KOL: """你是一位行业专家/KOL，拥有大量粉丝和行业影响力。
你以理性分析为主，关注事实和数据。你会引用行业知识和过往案例进行对比。
你的观点对其他参与者有较大影响。当品牌表现诚恳时你会给予肯定，反之会犀利批评。
你始终保持专业和客观，但不代表你没有立场。""",

    RoleType.SUPPORTER: """你是该品牌的忠实用户或员工。
你倾向于为品牌辩护，强调品牌的正面历史和成就。
当面对负面信息时，你会尝试从另一个角度解读，或呼吁大家给品牌时间。
你的语气友善但坚定，有时会和其他反对者产生争论。""",
}


@dataclass
class PersonaAgent(BaseAgent):

    def _stance_to_desc(self) -> str:
        if self.stance < -0.6:
            return "强烈反对/愤怒"
        elif self.stance < -0.2:
            return "偏向负面/不满"
        elif self.stance < 0.2:
            return "中立观望"
        elif self.stance < 0.6:
            return "偏向正面/理解"
        else:
            return "强烈支持/维护"

    def build_system_prompt(self) -> str:
        role_prompt = ROLE_SYSTEM_PROMPTS.get(self.role_type, "")
        return f"""你是 {self.name}，在一场舆论危机中的参与者。

【角色背景】
{self.cfg.persona_description}

【角色行为指南】
{role_prompt}

【发言风格】{self.cfg.speaking_style}
【当前立场】{self._stance_to_desc()}（数值: {self.stance:.2f}）

规则：
1. 始终保持角色一致性，用该角色的口吻和视角发言
2. 发言简洁，2-4 句话，模拟真实社交媒体风格
3. 不要暴露自己是 AI，不要使用括号标注动作或心理描写
4. 你的立场会受到信息影响，请基于当前立场发言
5. 可以引用或回应其他人的发言"""

    def generate_reaction(
        self,
        event_context: str,
        other_messages: list[Message],
        rag_knowledge: str = "",
        rag_opinions: str = "",
    ) -> tuple[list[dict], str]:
        context_parts = [f"【事件背景】\n{event_context}"]

        if rag_knowledge:
            context_parts.append(f"【相关背景资料】\n{rag_knowledge}")

        if rag_opinions:
            context_parts.append(f"【已有的舆情声音】\n{rag_opinions}")

        if self.short_term_memory:
            context_parts.append(f"【你记得的之前的讨论】\n{self.get_recent_context()}")

        if other_messages:
            recent = other_messages[-8:]
            msg_lines = []
            for m in recent:
                msg_lines.append(f"[{m.agent_name}] {m.content}")
            context_parts.append("【最新发言】\n" + "\n".join(msg_lines))

        full_context = "\n\n".join(context_parts)
        messages = [{"role": "user", "content": f"请以你的角色发表对当前事件的看法：\n\n{full_context}"}]

        return messages, self.build_system_prompt()

    def parse_response(self, content: str, round_number: int) -> Message:
        return Message(
            agent_id=self.agent_id,
            agent_name=self.name,
            role_type=self.role_type,
            content=content.strip(),
            round_number=round_number,
        )

    def update_stance_from_messages(self, messages: list[Message]):
        sentiment_score_map = {
            SentimentLabel.POSITIVE: 1.0,
            SentimentLabel.NEUTRAL: 0.5,
            SentimentLabel.NEGATIVE: 0.0,
        }
        for msg in messages:
            if msg.agent_id == self.agent_id:
                continue

            authority = 0.5
            if msg.role_type == RoleType.KOL:
                authority = 0.8
            elif msg.is_official:
                authority = 1.0

            if msg.is_official:
                keywords_positive = ["道歉", "赔偿", "负责", "召回", "改进", "深表歉意", "立即"]
                keywords_negative = ["不存在", "没有证据", "夸大", "恶意", "竞争对手"]
                pos_hits = sum(1 for k in keywords_positive if k in msg.content)
                neg_hits = sum(1 for k in keywords_negative if k in msg.content)
                delta = (pos_hits * 0.15 - neg_hits * 0.2) * authority
                self.update_stance(delta)
            else:
                if msg.agent_id in self.trust_scores:
                    trust = self.trust_scores[msg.agent_id]
                else:
                    trust = 0.5 if msg.role_type == RoleType.KOL else 0.3
                    self.trust_scores[msg.agent_id] = trust

                score = sentiment_score_map.get(msg.sentiment, 0.5)
                delta = (score - 0.5) * 0.1 * trust * authority
                self.update_stance(delta)

        if messages:
            cutoff = max(0, messages[-1].round_number - config.MEMORY_WINDOW)
            self.short_term_memory = [m for m in self.short_term_memory if m.round_number >= cutoff]
