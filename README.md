# CrisisSim - 舆论危机推演沙盘

基于多智能体（Multi-Agent）的舆论危机模拟与决策支持系统。利用大语言模型驱动多个 AI 角色，模拟品牌危机事件中不同利益相关方的反应，帮助危机公关团队制定更有效的应对策略。

<!-- 在此处放入系统整体截图 -->

## 核心功能

- **多智能体仿真** — 受害者、KOL、品牌支持者等角色由 LLM 独立驱动，拥有记忆、立场演化与信任体系
- **RAG 知识增强** — ChromaDB 向量检索 + 网络搜索，为智能体注入真实背景信息与舆情数据
- **策略推演与对比** — AI 公关顾问生成候选方案及官方声明，用户可自定义策略并观察舆情走向
- **实时数据分析** — 情绪分布、立场漂移、关键词提取，图表实时更新
- **5 大预设场景** — 涵盖食品安全、数据泄露、汽车召回、代言人塌房、大数据杀熟

<!-- 在此处放入功能概览截图 -->

## 技术路线

```
┌──────────────────────────────────────────────────────────────┐
│                        Flask Web UI                          │
│            暗色主题 SPA · Chart.js 实时图表                    │
└──────────────────┬───────────────────────────────────────────┘
                   │ REST API + SSE (流式输出)
┌──────────────────▼───────────────────────────────────────────┐
│                  SimulationEngine                             │
│         asyncio.gather 并行驱动所有 Agent 反应                  │
│         立场演化 · 记忆管理 · 信任权重计算                        │
├─────────────────┬────────────────────┬───────────────────────┤
│  DecisionAgent  │   PersonaAgent×N   │  SentimentAnalyzer    │
│  策略生成+反思    │  角色反应+立场更新    │  LLM分类+关键词回退     │
└────────┬────────┴────────┬───────────┴───────────────────────┘
         │                 │
┌────────▼─────────┐  ┌───▼──────────────────────────────────┐
│   LLM Provider   │  │          RAG Layer                   │
│  OpenAI / Claude  │  │  ChromaDB 向量库 · 文档处理 · 网络搜索  │
│  / Ollama 可插拔   │  │  knowledge_base + opinions 双集合     │
└──────────────────┘  └──────────────────────────────────────┘
```

### 关键实现细节

| 模块 | 实现方式 |
|------|---------|
| **LLM 调用** | 工厂模式 (`factory.py`)，支持 OpenAI 兼容接口 / Anthropic Claude / Ollama 本地部署，互换只需改 `.env` |
| **并发控制** | `asyncio.Semaphore(3)` 限制并发 API 调用，指数退避重试（最多 5 次） |
| **Agent 记忆** | 滑动窗口短期记忆（默认 5 条），Pydantic 模型结构化存储 |
| **立场演化** | 基于消息发送者权威度 × 信任系数加权，立场值在 [-1.0, +1.0] 区间连续更新 |
| **向量检索** | ChromaDB 内存模式，500 字分块 + 80 字重叠，支持 PDF/DOCX/TXT/MD/CSV |
| **网络搜索** | 抓取搜狗/百度搜索结果页，无需 API Key |
| **情绪分析** | 主路径 LLM 分类，回退路径中文关键词匹配（jieba 分词） |
| **流式输出** | Server-Sent Events (SSE)，策略生成过程实时显示 |

## 系统架构

### 项目结构

```
CrisisSim/
├── app.py                          # Flask 入口 + 完整前端 (Jinja2 模板)
├── requirements.txt
├── .env.example                    # 环境变量模板
├── run_streamlit.py                # Streamlit 启动脚本 (备用)
│
└── crisis_sim/                     # 核心 Python 包
    ├── config.py                   # 统一配置加载
    ├── models/
    │   └── schemas.py              # Pydantic 数据模型
    ├── agents/
    │   ├── base.py                 # Agent 基类 (记忆/立场/信任)
    │   ├── persona.py              # 角色 Agent
    │   └── decision.py             # 决策 Agent (PR 顾问)
    ├── llm/
    │   ├── provider.py             # LLM 抽象基类
    │   ├── factory.py              # Provider 工厂
    │   ├── openai_provider.py      # OpenAI 兼容实现
    │   ├── claude_provider.py      # Anthropic Claude 实现
    │   └── ollama_provider.py      # Ollama 本地实现
    ├── engine/
    │   └── simulation.py           # 仿真引擎主循环
    ├── analysis/
    │   └── sentiment.py            # 情绪分析与关键词提取
    ├── rag/
    │   ├── document_processor.py   # 文档分块与解析
    │   ├── vector_store.py         # ChromaDB 向量存储
    │   └── web_searcher.py         # 网络搜索
    └── scenarios/
        ├── presets.py              # 5 大预设危机场景
        └── knowledge_data.py       # 知识库与舆情种子数据
```

### Agent 角色体系

| 角色类型 | 说明 | 行为特征 |
|---------|------|---------|
| `Victim` | 受害者 / 消费者 / 维权人士 | 情绪化表达，关注自身利益，立场偏负面 |
| `KOL` | 意见领袖 / 行业专家 / 媒体人 | 理性分析，影响力大，KOL 间有追加讨论轮 |
| `Supporter` | 品牌忠实用户 / 行业观察者 | 倾向维护品牌，但会因证据改变立场 |
| `Decision` | 公关顾问 (系统级) | 生成策略方案、官方声明，每轮结束后反思评估 |

### 仿真流程

```
用户选择场景 → 加载知识库+舆情种子 → [可选] 网络搜索/手动输入
        ↓
PR 顾问生成 2 套候选策略 (含官方声明草稿)
        ↓
用户选择策略 或 自定义声明
        ↓
┌───── 仿真轮次循环 (默认 3 轮) ─────────────────────┐
│  1. 发布官方声明                                     │
│  2. 所有 PersonaAgent 并行生成反应                    │
│  3. KOL 间追加讨论                                    │
│  4. 计算情绪分布 + 立场演化                             │
│  5. PR 顾问反思策略效果                                │
└─────────────────────────────────────────────────────┘
        ↓
生成仿真总结报告
```

## 预设场景

| 场景 | 品牌 | 危机类型 | Agent 数量 |
|------|------|---------|-----------|
| 喜茶奶茶食品安全事件 | 喜茶 (HEYTEA) | 食品安全 — 饮品中发现异物 | 7 |
| 星辰科技用户数据泄露事件 | 星辰科技 (虚构) | 数据安全 — 5000万用户数据泄露 | 6 |
| 极驰汽车高速失速召回事件 | 极驰汽车 (虚构) | 产品质量 — 电动汽车高速失速 | 6 |
| 代言人塌房危机 | 锐动体育 (虚构) | 舆论危机 — 代言人违法被拘 | 6 |
| 飞享出行大数据杀熟事件 | 飞享出行 (虚构) | 算法伦理 — 算法定价歧视 | 7 |

<!-- 在此处放入各场景截图 -->

## 快速开始

### 环境要求

- Python 3.10+
- 任意 LLM API Key（OpenAI 兼容接口 / Anthropic Claude / 本地 Ollama）

### 安装与运行

```bash
# 1. 克隆仓库
git clone https://github.com/YOUR_USERNAME/CrisisSim.git
cd CrisisSim

# 2. 安装依赖
pip install -r requirements.txt

# 3. 配置环境变量
cp .env.example .env
# 编辑 .env，填入你的 API Key 和模型配置

# 4. 启动服务
python app.py
```

访问 `http://localhost:5000` 即可使用。

### LLM 配置示例

**OpenAI 兼容接口（默认）：**
```env
LLM_PROVIDER=openai
OPENAI_API_KEY=sk-xxx
OPENAI_BASE_URL=https://api.openai.com/v1
OPENAI_MODEL=gpt-4o-mini
```

**Anthropic Claude：**
```env
LLM_PROVIDER=claude
ANTHROPIC_API_KEY=sk-ant-xxx
CLAUDE_MODEL=claude-haiku-4-5-20251001
```

**Ollama 本地部署：**
```env
LLM_PROVIDER=ollama
OLLAMA_BASE_URL=http://localhost:11434
OLLAMA_MODEL=llama3
```

## 使用指南

### Step 1: 选择危机场景

从 5 个预设场景中选择一个，系统自动加载对应的 Agent 角色、知识库和舆情种子数据。

<!-- 在此处放入场景选择截图 -->

### Step 2: 配置与情报收集

- 查看/编辑 Agent 角色设定（姓名、立场、影响力、发言风格）
- 使用网络搜索获取实时背景信息
- 手动导入或编辑舆情数据

<!-- 在此处放入配置界面截图 -->

### Step 3: 策略推演

- AI 公关顾问生成两套候选策略及官方声明
- 选择策略或自定义声明，启动仿真
- 实时观察各 Agent 的反应和情绪变化

<!-- 在此处放入策略选择截图 -->

### Step 4: 分析与复盘

- 查看情绪分布和立场漂移图表
- 阅读 PR 顾问的策略反思
- 进入下一轮推演或查看最终总结

<!-- 在此处放入分析仪表盘截图 -->

## 技术栈

| 类别 | 技术 |
|------|-----|
| 后端框架 | Flask 3.0+ |
| 前端 | Vanilla JS + Chart.js 4.4 (CDN) |
| LLM 接口 | OpenAI SDK / Anthropic SDK / httpx (Ollama) |
| 向量数据库 | ChromaDB (内存模式) |
| 数据验证 | Pydantic 2.0+ |
| 中文分词 | jieba |
| 异步并发 | asyncio + Semaphore |
| HTTP 客户端 | httpx |

## 许可证

MIT License
