"""网络搜索模块：通过搜索引擎获取事件相关的真实信息"""
from __future__ import annotations
import re
import urllib.parse
import time
import httpx

_HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
        "(KHTML, like Gecko) Chrome/125.0.0.0 Safari/537.36"
    ),
    "Accept-Language": "zh-CN,zh;q=0.9,en;q=0.8",
}


def _strip_html(text: str) -> str:
    return re.sub(r"<[^>]+>", "", text).strip()


async def search_sogou(query: str, max_results: int = 8) -> list[dict]:
    """通过搜狗搜索获取结果"""
    url = f"https://www.sogou.com/web?query={urllib.parse.quote(query)}"
    results: list[dict] = []
    try:
        async with httpx.AsyncClient(timeout=15, follow_redirects=True) as client:
            resp = await client.get(url, headers=_HEADERS)
            if resp.status_code != 200:
                return []
            html = resp.text

        if "antispider" in str(resp.url) or len(html) < 5000:
            return []

        titles_links = re.findall(
            r'<h3[^>]*>.*?<a[^>]*href="([^"]*)"[^>]*>(.*?)</a>.*?</h3>', html, re.S
        )
        blocks = re.split(r"<h3[^>]*>", html)[1:]

        for i, (link, title_html) in enumerate(titles_links[:max_results]):
            title = _strip_html(title_html)
            snippet = ""
            if i < len(blocks):
                after_h3 = re.sub(r"^.*?</h3>", "", blocks[i], flags=re.S)
                after_h3 = re.sub(r"<img[^>]*>", "", after_h3)
                p_match = re.search(r"<p[^>]*>(.*?)</p>", after_h3, re.S)
                if p_match:
                    snippet = _strip_html(p_match.group(1))
                else:
                    snippet = _strip_html(after_h3[:500])
            if title and len(snippet) > 10:
                results.append({"title": title, "snippet": snippet, "url": link})
    except Exception:
        pass
    return results


async def search_bing(query: str, max_results: int = 8) -> list[dict]:
    """通过 Bing 搜索获取结果"""
    encoded = urllib.parse.quote_plus(query)
    url = f"https://www.bing.com/search?q={encoded}&mkt=zh-CN"
    results: list[dict] = []
    try:
        async with httpx.AsyncClient(timeout=15, follow_redirects=True) as client:
            resp = await client.get(url, headers=_HEADERS)
            if resp.status_code != 200:
                return []
            html = resp.text

        parts = html.split("b_algo")[1:]
        for part in parts[:max_results]:
            # 提取标题：<a> 标签内容
            a_match = re.search(r'href="(https?://[^"]+)"[^>]*>(.*?)</a>', part, re.S)
            # 提取摘要：<p> 标签
            p_match = re.search(r"<p[^>]*>(.*?)</p>", part, re.S)
            if not a_match:
                continue
            title = _strip_html(a_match.group(2))
            link = a_match.group(1)
            snippet = _strip_html(p_match.group(1)) if p_match else ""
            # 过滤掉明显不是搜索结果的条目（如字典结果）
            if title and snippet and len(snippet) > 10 and len(title) > 3:
                results.append({"title": title, "snippet": snippet, "url": link})
    except Exception:
        pass
    return results


async def search_multi(query: str, max_results: int = 8) -> list[dict]:
    """多引擎搜索，按优先级尝试"""
    for searcher in [search_sogou, search_bing]:
        results = await searcher(query, max_results)
        if results:
            return results
    return []


def search_event_news(event_keywords: str, max_results: int = 6) -> list[str]:
    """搜索事件相关新闻，返回文本片段列表"""
    import asyncio
    queries = [
        f"{event_keywords} 事件",
        f"{event_keywords} 评论",
    ]
    all_snippets: list[str] = []
    for q in queries:
        results = asyncio.run(search_multi(q, max_results=max_results // 2 + 2))
        for r in results:
            snippet = r["snippet"].strip()
            if len(snippet) > 15:
                all_snippets.append(f"[{r['title']}] {snippet}")
    seen = set()
    unique: list[str] = []
    for s in all_snippets:
        key = s[:30]
        if key not in seen:
            seen.add(key)
            unique.append(s)
    return unique[:max_results]


def search_brand_background(brand_name: str) -> list[str]:
    """搜索品牌/公司背景信息"""
    import asyncio
    queries = [
        f"{brand_name} 公司介绍",
        f"{brand_name} 争议 新闻",
    ]
    all_snippets: list[str] = []
    for q in queries:
        results = asyncio.run(search_multi(q, max_results=4))
        for r in results:
            snippet = r["snippet"].strip()
            if len(snippet) > 15:
                all_snippets.append(f"[{r['title']}] {snippet}")
    return all_snippets[:6]
