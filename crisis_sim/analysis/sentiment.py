from __future__ import annotations
from crisis_sim.models.schemas import Message, SentimentLabel, RoundState
from crisis_sim.llm.provider import BaseProvider

NEGATIVE_KEYWORDS = ["愤怒", "失望", "恶心", "垃圾", "骗子", "无良", "黑心", "维权", "赔偿",
                     "道歉", "抵制", "举报", "可恶", "太过分", "无法接受", "严重", "危害"]
POSITIVE_KEYWORDS = ["支持", "理解", "加油", "相信", "负责", "改进", "不错", "赞",
                     "诚恳", "点赞", "看好", "专业", "靠谱", "良心"]
NEUTRAL_KEYWORDS = ["观望", "等待", "看看", "关注", "持续", "了解"]


def keyword_sentiment(text: str) -> SentimentLabel:
    neg = sum(1 for k in NEGATIVE_KEYWORDS if k in text)
    pos = sum(1 for k in POSITIVE_KEYWORDS if k in text)
    if neg > pos:
        return SentimentLabel.NEGATIVE
    elif pos > neg:
        return SentimentLabel.POSITIVE
    return SentimentLabel.NEUTRAL


async def llm_classify_sentiment(llm: BaseProvider, text: str) -> SentimentLabel:
    prompt = f"""判断以下文本的情绪倾向，只返回一个词：positive、negative 或 neutral

文本：{text[:200]}"""
    result = await llm.generate("你是情绪分析工具。", [{"role": "user", "content": prompt}], temperature=0.1)
    result = result.strip().lower()
    if "positive" in result:
        return SentimentLabel.POSITIVE
    elif "negative" in result:
        return SentimentLabel.NEGATIVE
    return SentimentLabel.NEUTRAL


async def classify_message(llm: BaseProvider, message: Message) -> SentimentLabel:
    try:
        return await llm_classify_sentiment(llm, message.content)
    except Exception:
        return keyword_sentiment(message.content)


def compute_round_stats(messages: list[Message]) -> dict[str, float]:
    if not messages:
        return {"positive": 0.0, "negative": 0.0, "neutral": 1.0}

    total = len(messages)
    pos = sum(1 for m in messages if m.sentiment == SentimentLabel.POSITIVE)
    neg = sum(1 for m in messages if m.sentiment == SentimentLabel.NEGATIVE)
    neu = total - pos - neg
    return {
        "positive": round(pos / total, 3),
        "negative": round(neg / total, 3),
        "neutral": round(neu / total, 3),
    }


def compute_overall_score(sentiment_dist: dict[str, float]) -> float:
    pos = sentiment_dist.get("positive", 0)
    neg = sentiment_dist.get("negative", 0)
    return round(pos - neg, 3)


def extract_keywords(messages: list[Message], top_n: int = 10) -> list[tuple[str, int]]:
    import jieba
    word_count: dict[str, int] = {}
    stopwords = {"的", "了", "是", "在", "我", "有", "和", "就", "不", "人", "都", "一", "一个",
                 "上", "也", "很", "到", "说", "要", "去", "你", "会", "着", "没有", "看", "好",
                 "这", "那", "还", "吗", "把", "被", "让", "给", "它", "他", "她", "们", "能",
                 "对", "但", "这个", "那个", "什么", "怎么", "吧", "啊", "呢", "哈"}
    for msg in messages:
        words = jieba.lcut(msg.content)
        for w in words:
            w = w.strip()
            if len(w) >= 2 and w not in stopwords:
                word_count[w] = word_count.get(w, 0) + 1
    sorted_words = sorted(word_count.items(), key=lambda x: x[1], reverse=True)
    return sorted_words[:top_n]
