"""CrisisSim 舆论危机推演沙盘 — Flask Web UI"""
import asyncio
import json
from flask import Flask, render_template_string, request, jsonify, session, Response
import uuid
from crisis_sim.scenarios.presets import get_preset, list_presets
from crisis_sim.engine.simulation import SimulationEngine
from crisis_sim.llm.factory import create_provider
from crisis_sim.models.schemas import RoleType, SentimentLabel, AgentConfig, ScenarioConfig, StrategyOption
from crisis_sim import config

app = Flask(__name__)
app.secret_key = "crisissim_secret_key"

# 全局引擎存储（按 session）
engines: dict[str, SimulationEngine] = {}
# 暂存搜索结果（引擎创建前）
pending_kb: dict[str, list[str]] = {}
pending_op: dict[str, list[str]] = {}
# 执行进度
exec_progress: dict[str, str] = {}

HTML_TEMPLATE = """<!DOCTYPE html>
<html lang="zh-CN">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>CrisisSim 舆论危机推演沙盘</title>
<script src="https://cdn.jsdelivr.net/npm/chart.js@4.4.7/dist/chart.umd.min.js"></script>
<style>
*{box-sizing:border-box;margin:0;padding:0}
body{font-family:'Microsoft YaHei',sans-serif;background:#0f172a;color:#e2e8f0;min-height:100vh}
.container{max-width:1200px;margin:0 auto;padding:20px}
h1{text-align:center;color:#f8fafc;margin:20px 0;font-size:1.8em}
h2{color:#94a3b8;font-size:1.1em;margin:8px 0}
.card{background:#1e293b;border-radius:12px;padding:16px;margin:8px 0;border:1px solid #334155}
.btn{padding:10px 20px;border:none;border-radius:8px;cursor:pointer;font-size:14px;font-weight:bold;transition:all .2s}
.btn-primary{background:#3b82f6;color:white}.btn-primary:hover{background:#2563eb}
.btn-secondary{background:#475569;color:white}.btn-secondary:hover{background:#334155}
.btn-success{background:#22c55e;color:white}.btn-success:hover{background:#16a34a}
.btn-danger{background:#ef4444;color:white}.btn-danger:hover{background:#dc2626}
.btn-sm{padding:6px 12px;font-size:12px}
select,input[type=text],textarea{background:#0f172a;color:#e2e8f0;border:1px solid #475569;border-radius:8px;padding:8px 12px;width:100%;font-size:14px}
label{color:#94a3b8;font-size:13px;display:block;margin:4px 0}
.grid2{display:grid;grid-template-columns:1fr 1fr;gap:12px}
.grid3{display:grid;grid-template-columns:1fr 1fr 1fr;gap:8px}
.msg{padding:12px;margin:6px 0;border-radius:8px;border-left:4px solid #475569;background:#1e293b}
.msg-official{border-left-color:#f59e0b;background:#1c2a1e}
.msg-victim{border-left-color:#ef4444}
.msg-kol{border-left-color:#3b82f6}
.msg-supporter{border-left-color:#22c55e}
.msg-header{font-weight:bold;font-size:13px;margin-bottom:4px}
.msg-content{font-size:14px;line-height:1.6}
.sentiment-pos{color:#22c55e}.sentiment-neg{color:#ef4444}.sentiment-neu{color:#94a3b8}
.metric{text-align:center;padding:12px;background:#0f172a;border-radius:8px}
.metric-val{font-size:28px;font-weight:bold}.metric-label{font-size:12px;color:#94a3b8}
#status{text-align:center;padding:12px;color:#94a3b8;font-size:14px}
.agent-card{background:#0f172a;border-radius:8px;padding:12px;margin:6px 0;border:1px solid #334155}
.agent-card summary{cursor:pointer;font-weight:bold}
textarea{min-height:80px;resize:vertical}
.strategy-card{background:#0f172a;border-radius:8px;padding:12px;margin:8px 0;border:1px solid #3b82f6;cursor:pointer;transition:all .2s}
.strategy-card:hover{border-color:#60a5fa;background:#172554}
.strategy-card.selected{border-color:#22c55e;background:#14532d}
.reflection{background:#1c2a1e;border-left:4px solid #f59e0b;padding:12px;border-radius:8px;margin:8px 0}
.kb-info{font-size:12px;color:#64748b;margin:4px 0}
.search-row{display:flex;gap:8px;align-items:flex-end}
.search-row input{flex:1}
.search-row .btn{white-space:nowrap}
hr{border:none;border-top:1px solid #334155;margin:12px 0}
</style>
</head>
<body>
<div class="container">
<h1>CrisisSim 舆论危机推演沙盘</h1>
<p style="text-align:center;color:#64748b;margin-bottom:20px">基于多智能体的舆论危机模拟与决策支持系统</p>

<div id="app">
  <div id="setup-phase">
    <div class="grid2">
      <!-- 左栏：场景配置 -->
      <div>
        <div class="card">
          <h2>选择场景</h2>
          <select id="scenario-select" onchange="onScenarioChange()">
            {% for key, title in presets.items() %}
            <option value="{{key}}">{{title}}</option>
            {% endfor %}
          </select>
          <div id="scenario-desc" style="margin-top:12px;font-size:13px;color:#94a3b8"></div>
        </div>

        <div class="card">
          <h2>参与角色</h2>
          <div id="agents-list"></div>
          <button class="btn btn-secondary btn-sm" style="margin-top:8px" onclick="addAgent()">+ 添加角色</button>
        </div>
      </div>

      <!-- 右栏：知识库与搜索 -->
      <div>
        <div class="card">
          <h2>危机事件背景</h2>
          <div id="event-display" style="font-size:13px;line-height:1.8;white-space:pre-wrap;max-height:300px;overflow-y:auto"></div>
        </div>

        <div class="card">
          <h2>从网络获取数据</h2>
          <div class="search-row">
            <input type="text" id="search-keywords" placeholder="品牌名 + 事件关键词">
            <button class="btn btn-secondary btn-sm" onclick="searchWeb('kb')">搜索背景</button>
            <button class="btn btn-secondary btn-sm" onclick="searchWeb('op')">搜索舆情</button>
          </div>
          <div id="search-status" class="kb-info"></div>
        </div>

        <div class="card">
          <h2>手动输入舆情</h2>
          <textarea id="manual-opinions" placeholder="每条一行&#10;例：这个品牌太让人失望了&#10;我觉得应该给品牌一点时间"></textarea>
          <button class="btn btn-secondary btn-sm" style="margin-top:8px" onclick="importOpinions()">导入舆情</button>
        </div>

        <div class="card">
          <h2>知识库状态</h2>
          <div id="kb-status" class="kb-info">开始推演后自动加载知识库和舆情种子</div>
        </div>

        <button class="btn btn-primary" style="width:100%;margin-top:12px;padding:14px;font-size:16px" onclick="startSimulation()">开始推演</button>
      </div>
    </div>
  </div>

  <div id="sim-phase" style="display:none">
    <div class="grid2">
      <div>
        <!-- 策略选择 / 推演结果 -->
        <div id="strategy-area"></div>
        <div id="messages-area"></div>
        <div id="reflection-area"></div>
        <div id="action-area" style="text-align:center;margin:16px 0"></div>
      </div>
      <div>
        <div class="card">
          <h2>舆情仪表盘</h2>
          <div class="grid3" id="sentiment-metrics"></div>
          <hr>
          <h2>情绪趋势</h2>
          <div style="position:relative;height:220px"><canvas id="sentiment-chart"></canvas></div>
          <hr>
          <h2>各角色立场演化</h2>
          <div style="position:relative;height:260px"><canvas id="stance-chart-canvas"></canvas></div>
        </div>
        <div class="card">
          <h2>知识库</h2>
          <div id="kb-status-sim" class="kb-info"></div>
        </div>
      </div>
    </div>
  </div>
</div>

<div id="status"></div>
</div>

<script>
let sessionId = null;
let agents = [];
let currentRound = 0;
let maxRounds = {{ max_rounds }};
let allMessages = [];  // 跨轮次累积所有消息

function setStatus(msg, loading=true) {
  document.getElementById('status').innerHTML = loading ? '⏳ ' + msg : msg;
}

async function api(path, body={}) {
  const resp = await fetch('/api/' + path, {
    method: 'POST',
    headers: {'Content-Type': 'application/json'},
    body: JSON.stringify({session_id: sessionId, ...body})
  });
  return await resp.json();
}

async function onScenarioChange() {
  const key = document.getElementById('scenario-select').value;
  const data = await api('scenario', {preset_key: key});
  if (data.error) { alert(data.error); return; }
  document.getElementById('scenario-desc').innerHTML = '<b>' + data.title + '</b><br>' + data.summary;
  document.getElementById('event-display').textContent = data.initial_event;
  document.getElementById('search-keywords').value = data.brand_name + ' ' + data.title;
  agents = data.agents;
  renderAgents();
}

function esc(s) { return String(s).replace(/&/g,'&amp;').replace(/</g,'&lt;').replace(/>/g,'&gt;').replace(/"/g,'&quot;'); }

function renderAgents() {
  const container = document.getElementById('agents-list');
  const roleLabels = {victim:'受害者/维权者', kol:'KOL/专家', supporter:'品牌支持者'};
  const roleColors = {victim:'#ef4444', kol:'#3b82f6', supporter:'#22c55e'};
  if (!agents.length) { container.innerHTML = '<div class="kb-info">暂无角色</div>'; return; }
  container.innerHTML = agents.map((a, i) => {
    const stanceLabel = a.stance < -0.3 ? '反对' : a.stance < 0.3 ? '中立' : '支持';
    return `<div class="agent-card">
      <details>
        <summary><span style="color:${roleColors[a.role_type]||'#999'}">[${roleLabels[a.role_type]||a.role_type}]</span> ${esc(a.name)} <span style="color:#64748b;font-size:12px">(${stanceLabel})</span></summary>
        <div style="margin-top:8px">
          <label>昵称</label>
          <input type="text" value="${esc(a.name)}" onchange="agents[${i}].name=this.value">
          <div class="grid2">
            <div>
              <label>角色类型</label>
              <select onchange="agents[${i}].role_type=this.value">
                <option value="victim" ${a.role_type==='victim'?'selected':''}>受害者</option>
                <option value="kol" ${a.role_type==='kol'?'selected':''}>KOL/专家</option>
                <option value="supporter" ${a.role_type==='supporter'?'selected':''}>品牌支持者</option>
              </select>
            </div>
            <div>
              <label>立场 (${a.stance.toFixed(1)}) -1反对 ↔ +1支持</label>
              <input type="range" min="-1" max="1" step="0.1" value="${a.stance}" onchange="agents[${i}].stance=parseFloat(this.value);renderAgents()">
            </div>
          </div>
          <div class="grid2">
            <div>
              <label>影响力 (${a.influence_weight.toFixed(1)})</label>
              <input type="range" min="0.1" max="1" step="0.1" value="${a.influence_weight}" onchange="agents[${i}].influence_weight=parseFloat(this.value)">
            </div>
            <div>
              <label>发言风格</label>
              <input type="text" value="${esc(a.speaking_style)}" onchange="agents[${i}].speaking_style=this.value">
            </div>
          </div>
          <label>角色背景</label>
          <textarea onchange="agents[${i}].persona_description=this.value">${esc(a.persona_description)}</textarea>
          <button class="btn btn-danger btn-sm" onclick="agents.splice(${i},1);renderAgents()">删除</button>
        </div>
      </details>
    </div>`;
  }).join('');
}

function addAgent() {
  agents.push({
    agent_id: 'custom_' + (agents.length+1), name: '新角色', role_type: 'supporter',
    persona_description: '请描述角色背景...', stance: 0.0,
    influence_weight: 0.5, speaking_style: '理性客观'
  });
  renderAgents();
}

async function startSimulation() {
  setStatus('正在初始化模拟引擎...');
  const data = await api('init', {agents: agents});
  if (data.error) { alert(data.error); return; }
  sessionId = data.session_id;
  document.getElementById('setup-phase').style.display = 'none';
  document.getElementById('sim-phase').style.display = 'block';
  currentRound = 0;
  sentimentHistory = [];
  stanceHistory = {};

  // 显示知识库状态
  const el2 = document.getElementById('kb-status-sim');
  if (el2) el2.textContent = `知识库: ${data.kb_count} 条 | 舆情库: ${data.op_count} 条`;
  setStatus('初始化完成', false);
  // 延迟一帧初始化图表，确保 canvas 已渲染
  setTimeout(initCharts, 100);
  await loadStrategies();
}

async function loadStrategies() {
  const area = document.getElementById('strategy-area');
  area.innerHTML = `<div class="card"><h2>第 ${currentRound+1} 轮 — 公关顾问正在思考...</h2><div id="stream-output" style="font-size:13px;color:#94a3b8;line-height:1.8;white-space:pre-wrap;min-height:60px"></div></div>`;
  setStatus('公关顾问正在制定策略...');

  const streamDiv = document.getElementById('stream-output');
  let fullText = '';
  let strategies = null;

  try {
    const resp = await fetch('/api/strategies_stream', {
      method: 'POST',
      headers: {'Content-Type': 'application/json'},
      body: JSON.stringify({session_id: sessionId})
    });
    const reader = resp.body.getReader();
    const decoder = new TextDecoder();
    let buffer = '';

    while (true) {
      const {done, value} = await reader.read();
      if (done) break;
      buffer += decoder.decode(value, {stream: true});

      const lines = buffer.split('\n');
      buffer = lines.pop();

      for (const line of lines) {
        if (!line.startsWith('data: ')) continue;
        const payload = line.slice(6);
        if (payload === '[DONE]') continue;
        try {
          const d = JSON.parse(payload);
          if (d.text) {
            // 检查是否是最终 JSON
            if (d.text.includes('__STRATEGIES_JSON__')) {
              const jsonPart = d.text.split('__STRATEGIES_JSON__\n')[1];
              if (jsonPart) {
                try { strategies = JSON.parse(jsonPart); } catch(e) {}
              }
            } else {
              fullText += d.text;
              streamDiv.textContent = fullText;
              streamDiv.scrollTop = streamDiv.scrollHeight;
            }
          }
        } catch(e) {}
      }
    }
  } catch(e) {
    // SSE 失败，回退到普通接口
    const data = await api('strategies');
    if (data.error) { alert(data.error); return; }
    strategies = data.strategies;
  }

  if (strategies) {
    renderStrategies(strategies);
  } else {
    // 解析失败，回退
    const data = await api('strategies');
    if (data.error) { alert(data.error); return; }
    renderStrategies(data.strategies);
  }
  setStatus('请选择策略', false);
}

function renderStrategies(strategies) {
  const area = document.getElementById('strategy-area');
  area.innerHTML = `<div class="card"><h2>第 ${currentRound+1} 轮 — 选择应对策略</h2>` +
    strategies.map(s => `
      <div class="strategy-card" id="strat_${s.strategy_id}" onclick="selectStrategy('${s.strategy_id}')">
        <div style="font-weight:bold;color:#f8fafc">策略${s.strategy_id}: ${esc(s.title)}</div>
        <div style="font-size:13px;color:#94a3b8;margin:4px 0">${esc(s.description)}</div>
        <div style="font-size:13px;color:#60a5fa;margin:4px 0"><b>理由:</b> ${esc(s.reasoning)}</div>
        <div style="font-size:13px;background:#0f172a;padding:8px;border-radius:6px;margin-top:8px;color:#fbbf24"><b>拟发布声明:</b><br>${esc(s.official_statement)}</div>
      </div>
    `).join('') +
    `<hr>
     <div style="margin-top:8px">
       <div style="font-weight:bold;color:#f8fafc;margin-bottom:8px">或 自定义策略：</div>
       <label>策略标题</label>
       <input type="text" id="custom-strategy-title" placeholder="例：邀请第三方权威检测">
       <label style="margin-top:8px">拟发布声明内容</label>
       <textarea id="custom-statement" placeholder="在此输入你希望品牌发布的官方声明...&#10;&#10;例：我们对此次事件深表歉意。已第一时间成立专项调查组，并邀请国家级食品检测机构介入。涉事门店已停业整顿，所有受影响消费者将获得全额退款及三倍赔偿。"></textarea>
       <button class="btn btn-success" style="margin-top:8px;width:100%" onclick="executeCustomStrategy()">执行自定义策略</button>
     </div>
    </div>`;
  window._strategies = strategies;
}

let selectedStrategyId = null;
function selectStrategy(id) {
  selectedStrategyId = id;
  document.querySelectorAll('.strategy-card').forEach(c => c.classList.remove('selected'));
  document.getElementById('strat_' + id).classList.add('selected');
  document.getElementById('action-area').innerHTML =
    `<button class="btn btn-success" style="padding:14px 40px;font-size:16px" onclick="executeRound()">执行策略 ${id}</button>`;
}

async function executeRound() {
  if (!selectedStrategyId) return;
  const strategy = window._strategies.find(s => s.strategy_id === selectedStrategyId);
  await _doExecute(strategy);
}

async function executeCustomStrategy() {
  const title = document.getElementById('custom-strategy-title').value.trim();
  const statement = document.getElementById('custom-statement').value.trim();
  if (!statement) { alert('请输入声明内容'); return; }
  const strategy = {
    strategy_id: 'X',
    title: title || '自定义策略',
    description: '用户自定义的应对策略',
    official_statement: statement,
    reasoning: '用户手动输入',
  };
  await _doExecute(strategy);
}

async function _doExecute(strategy) {
  document.getElementById('strategy-area').innerHTML = '';
  document.getElementById('action-area').innerHTML = '';
  setStatus(`正在执行「${strategy.title}」...`);

  let polling = true;
  const pollProgress = async () => {
    while (polling) {
      try {
        const p = await api('progress');
        if (p.progress) setStatus('⏳ ' + p.progress);
      } catch(e) {}
      await new Promise(r => setTimeout(r, 1500));
    }
  };
  pollProgress();

  const data = await api('execute', {strategy: strategy});
  polling = false;
  if (data.error) { alert(data.error); return; }
  currentRound++;

  // 累积消息到全局历史
  if (data.messages) {
    allMessages.push(...data.messages);
  }

  renderRoundResult(data);
  updateDashboard(data);
  setStatus('', false);

  if (currentRound >= maxRounds) {
    document.getElementById('action-area').innerHTML = `<div class="card"><h2>推演完成</h2><p>共 ${currentRound} 轮推演已结束。请查看上方复盘。</p><button class="btn btn-primary" onclick="location.reload()">重新开始</button></div>`;
    // 加载总结
    const summary = await api('summary');
    if (summary.summary) {
      document.getElementById('action-area').innerHTML += `<div class="card"><h2>复盘总结</h2><pre style="white-space:pre-wrap;font-size:13px;color:#94a3b8">${summary.summary}</pre></div>`;
    }
  } else {
    document.getElementById('action-area').innerHTML = `<button class="btn btn-primary" style="padding:14px 40px;font-size:16px" onclick="loadStrategies()">进入下一轮</button>`;
  }
}

function renderRoundResult(data) {
  const area = document.getElementById('messages-area');
  const roleClass = {official:'msg-official', victim:'msg-victim', kol:'msg-kol', supporter:'msg-supporter'};
  const roleLabel = {official:'官方声明', victim:'受害者/维权者', kol:'KOL/专家', supporter:'品牌支持者'};
  const sentClass = {positive:'sentiment-pos', negative:'sentiment-neg', neutral:'sentiment-neu'};
  const sentLabel = {positive:'正面', negative:'负面', neutral:'中性'};

  let html = `<div class="card">
    <h2 style="border-bottom:1px solid #334155;padding-bottom:8px">第 ${currentRound} 轮 — 推演结果</h2>`;
  for (const msg of data.messages) {
    const cls = roleClass[msg.role_type] || '';
    const label = roleLabel[msg.role_type] || msg.role_type;
    const sent = msg.sentiment ? `<span class="${sentClass[msg.sentiment]||''}">[${sentLabel[msg.sentiment]||msg.sentiment}]</span>` : '';
    const officialTag = msg.is_official ? '<span style="color:#f59e0b;font-size:11px"> [官方]</span>' : '';
    html += `<div class="msg ${cls}">
      <div class="msg-header"><span style="color:#94a3b8">[${label}]</span> ${esc(msg.agent_name)}${officialTag} ${sent}</div>
      <div class="msg-content">${esc(msg.content)}</div>
    </div>`;
  }
  html += '</div>';
  // 最新轮次插入到最前面
  area.innerHTML = html + area.innerHTML;

  if (data.reflection) {
    const ref = document.getElementById('reflection-area');
    ref.innerHTML = `<div class="reflection"><b>第 ${currentRound} 轮公关顾问评估:</b> ${data.reflection}</div>` + ref.innerHTML;
  }
}

// ── 图表状态 ──
let sentimentHistory = [];  // [{positive, negative, neutral}, ...]
let stanceHistory = {};     // {agentName: [stance_r0, stance_r1, ...]}
let sentimentChart = null;
let stanceChart = null;

const CHART_COLORS = ['#ef4444','#f97316','#eab308','#3b82f6','#22c55e','#a855f7','#14b8a6','#ec4899'];

function initCharts() {
  const sentCtx = document.getElementById('sentiment-chart');
  const stanceCtx = document.getElementById('stance-chart-canvas');
  if (!sentCtx || !stanceCtx) return;

  sentimentChart = new Chart(sentCtx, {
    type: 'line',
    data: {
      labels: [],
      datasets: [
        {label:'正面', data:[], borderColor:'#22c55e', backgroundColor:'rgba(34,197,94,0.1)', fill:true, tension:0.3},
        {label:'负面', data:[], borderColor:'#ef4444', backgroundColor:'rgba(239,68,68,0.1)', fill:true, tension:0.3},
        {label:'中性', data:[], borderColor:'#94a3b8', backgroundColor:'rgba(148,163,184,0.1)', fill:true, tension:0.3},
      ]
    },
    options: {
      responsive: true, maintainAspectRatio: false,
      plugins: {legend:{labels:{color:'#e2e8f0',font:{size:11}}}},
      scales: {
        x: {ticks:{color:'#94a3b8'}, grid:{color:'#334155'}},
        y: {min:0, max:100, ticks:{color:'#94a3b8', callback:v=>v+'%'}, grid:{color:'#334155'}}
      }
    }
  });

  stanceChart = new Chart(stanceCtx, {
    type: 'line',
    data: {labels:[], datasets:[]},
    options: {
      responsive: true, maintainAspectRatio: false,
      plugins: {legend:{labels:{color:'#e2e8f0',font:{size:10}}, position:'bottom'}},
      scales: {
        x: {ticks:{color:'#94a3b8'}, grid:{color:'#334155'}},
        y: {min:-1, max:1, ticks:{color:'#94a3b8'}, grid:{color:'#334155'},
            title:{display:true, text:'反对 ← → 支持', color:'#94a3b8'}}
      }
    }
  });
}

function updateDashboard(data) {
  // 更新指标数字
  if (data.sentiment) {
    const sd = data.sentiment;
    document.getElementById('sentiment-metrics').innerHTML = `
      <div class="metric"><div class="metric-val sentiment-pos">${(sd.positive*100).toFixed(0)}%</div><div class="metric-label">正面</div></div>
      <div class="metric"><div class="metric-val sentiment-neg">${(sd.negative*100).toFixed(0)}%</div><div class="metric-label">负面</div></div>
      <div class="metric"><div class="metric-val sentiment-neu">${(sd.neutral*100).toFixed(0)}%</div><div class="metric-label">中性</div></div>`;

    // 记录历史 & 更新折线图
    sentimentHistory.push(sd);
    if (sentimentChart) {
      sentimentChart.data.labels = sentimentHistory.map((_,i) => '第'+(i+1)+'轮');
      sentimentChart.data.datasets[0].data = sentimentHistory.map(s => (s.positive*100).toFixed(1));
      sentimentChart.data.datasets[1].data = sentimentHistory.map(s => (s.negative*100).toFixed(1));
      sentimentChart.data.datasets[2].data = sentimentHistory.map(s => (s.neutral*100).toFixed(1));
      sentimentChart.update();
    }
  }

  // 更新立场图
  if (data.stances) {
    for (const [name, stances] of Object.entries(data.stances)) {
      if (!stanceHistory[name]) stanceHistory[name] = [];
      // stances 是完整历史数组，直接替换
      stanceHistory[name] = stances;
    }
    if (stanceChart) {
      const maxLen = Math.max(...Object.values(stanceHistory).map(v=>v.length));
      stanceChart.data.labels = Array.from({length:maxLen}, (_,i) => 'R'+i);
      stanceChart.data.datasets = Object.entries(stanceHistory).map(([name, vals], i) => ({
        label: name,
        data: vals,
        borderColor: CHART_COLORS[i % CHART_COLORS.length],
        backgroundColor: 'transparent',
        tension: 0.3,
        pointRadius: 4,
        borderWidth: 2,
      }));
      stanceChart.update();
    }
  }
}

async function searchWeb(type) {
  const kw = document.getElementById('search-keywords').value;
  if (!kw.trim()) return;
  document.getElementById('search-status').textContent = '搜索中...';
  const data = await api('search', {query: kw, search_type: type});
  document.getElementById('search-status').textContent = data.message || '搜索完成';
  updateKBStatus();
}

async function importOpinions() {
  const text = document.getElementById('manual-opinions').value;
  if (!text.trim()) return;
  const data = await api('import_opinions', {text: text});
  alert(data.message);
  updateKBStatus();
}

async function updateKBStatus() {
  const data = await api('kb_status');
  const el = document.getElementById('kb-status');
  const el2 = document.getElementById('kb-status-sim');
  const txt = `知识库: ${data.kb_count} 条 | 舆情库: ${data.op_count} 条`;
  if (el) el.textContent = txt;
  if (el2) el2.textContent = txt;
}

// 初始化
window.onload = () => {
  sessionId = crypto.randomUUID();
  onScenarioChange();
};
</script>
</body>
</html>"""


@app.route("/")
def index():
    presets = list_presets()
    return render_template_string(HTML_TEMPLATE, presets=presets, max_rounds=config.MAX_ROUNDS)


@app.route("/api/scenario", methods=["POST"])
def api_scenario():
    data = request.json
    preset_key = data.get("preset_key", "tea_safety")
    try:
        scenario = get_preset(preset_key)
    except KeyError:
        return jsonify({"error": f"未知场景: {preset_key}"})
    return jsonify({
        "title": scenario.title,
        "summary": scenario.summary,
        "brand_name": scenario.brand_name,
        "initial_event": scenario.initial_event,
        "agents": [
            {
                "agent_id": ac.agent_id, "name": ac.name, "role_type": ac.role_type.value,
                "persona_description": ac.persona_description, "stance": ac.stance,
                "influence_weight": ac.influence_weight, "speaking_style": ac.speaking_style,
            }
            for ac in scenario.agent_configs
        ],
    })


@app.route("/api/init", methods=["POST"])
def api_init():
    data = request.json
    sid = data.get("session_id", str(uuid.uuid4()))
    agents_data = data.get("agents", [])

    preset_key = data.get("preset_key", "tea_safety")
    scenario = get_preset(preset_key)

    # 用用户自定义的角色覆盖
    agent_configs = []
    for a in agents_data:
        agent_configs.append(AgentConfig(
            agent_id=a["agent_id"], name=a["name"],
            role_type=RoleType(a["role_type"]),
            persona_description=a.get("persona_description", ""),
            stance=a.get("stance", 0.0),
            influence_weight=a.get("influence_weight", 0.5),
            speaking_style=a.get("speaking_style", "理性客观"),
        ))
    if agent_configs:
        scenario.agent_configs = agent_configs

    try:
        llm = create_provider()
        engine = SimulationEngine(scenario=scenario, llm=llm)
        engine.initialize()

        # 导入暂存的搜索结果
        if sid in pending_kb:
            from crisis_sim.rag.document_processor import DocumentChunk
            chunks = [DocumentChunk(content=s, metadata={"source": "网络搜索", "chunk_id": i})
                      for i, s in enumerate(pending_kb.pop(sid))]
            engine.vector_store.add_to_knowledge_base(chunks)
        if sid in pending_op:
            engine.vector_store.add_opinions(pending_op.pop(sid))

        asyncio.run(engine.generate_initial_event())
        engines[sid] = engine
        return jsonify({"session_id": sid, "kb_count": engine.vector_store.kb_count, "op_count": engine.vector_store.opinion_count})
    except Exception as e:
        return jsonify({"error": str(e)})


@app.route("/api/strategies", methods=["POST"])
def api_strategies():
    data = request.json
    sid = data.get("session_id")
    engine = engines.get(sid)
    if not engine:
        return jsonify({"error": "会话不存在，请重新开始"})
    try:
        strategies = asyncio.run(engine.get_strategies())
        return jsonify({
            "strategies": [
                {"strategy_id": s.strategy_id, "title": s.title, "description": s.description,
                 "official_statement": s.official_statement, "reasoning": s.reasoning}
                for s in strategies
            ]
        })
    except Exception as e:
        return jsonify({"error": str(e)})


@app.route("/api/strategies_stream", methods=["POST"])
def api_strategies_stream():
    data = request.json
    sid = data.get("session_id")
    engine = engines.get(sid)
    if not engine:
        return jsonify({"error": "会话不存在"})

    def generate():
        async def _stream():
            async for chunk in engine.decision_agent.generate_strategies_stream(
                engine.all_messages, engine.current_round + 1
            ):
                yield chunk
        loop = asyncio.new_event_loop()
        try:
            agen = _stream().__aiter__()
            while True:
                try:
                    chunk = loop.run_until_complete(agen.__anext__())
                    yield f"data: {json.dumps({'text': chunk}, ensure_ascii=False)}\n\n"
                except StopAsyncIteration:
                    break
        finally:
            loop.close()
        yield "data: [DONE]\n\n"

    return Response(generate(), mimetype='text/event-stream',
                    headers={'Cache-Control': 'no-cache', 'X-Accel-Buffering': 'no'})


@app.route("/api/execute", methods=["POST"])
def api_execute():
    data = request.json
    sid = data.get("session_id")
    engine = engines.get(sid)
    if not engine:
        return jsonify({"error": "会话不存在"})
    strategy_data = data.get("strategy", {})
    strategy = StrategyOption(
        strategy_id=strategy_data.get("strategy_id", "A"),
        title=strategy_data.get("title", ""),
        description=strategy_data.get("description", ""),
        official_statement=strategy_data.get("official_statement", ""),
        reasoning=strategy_data.get("reasoning", ""),
    )

    def on_progress(msg: str):
        exec_progress[sid] = msg

    exec_progress[sid] = "开始执行..."
    try:
        round_state = asyncio.run(engine.execute_round(strategy, progress_cb=on_progress))
        messages = []
        for msg in round_state.messages:
            messages.append({
                "agent_name": msg.agent_name, "role_type": msg.role_type.value,
                "content": msg.content, "sentiment": msg.sentiment.value if msg.sentiment else None,
                "is_official": msg.is_official,
            })
        return jsonify({
            "messages": messages,
            "sentiment": round_state.sentiment_distribution,
            "stances": {n: [round(v, 3) for v in s] for n, s in engine.get_stance_evolution().items()},
            "reflection": round_state.decision_reflection,
        })
    except Exception as e:
        return jsonify({"error": str(e)})


@app.route("/api/search", methods=["POST"])
def api_search():
    data = request.json
    import sys; print(f"[DEBUG] search request: {data}", flush=True); sys.stdout.flush()
    sid = data.get("session_id")
    engine = engines.get(sid)
    query = data.get("query", "")
    search_type = data.get("search_type", "kb")
    print(f"[DEBUG] query={query}, type={search_type}, engine={engine is not None}")
    if not query.strip():
        return jsonify({"message": "请输入关键词"})

    try:
        if search_type == "kb":
            from crisis_sim.rag.web_searcher import search_brand_background
            snippets = search_brand_background(query)
            print(f"[DEBUG] search_brand_background({query}) -> {len(snippets)} results")
            if not snippets:
                return jsonify({"message": "未搜索到结果，请尝试其他关键词"})
            if engine:
                from crisis_sim.rag.document_processor import DocumentChunk
                chunks = [DocumentChunk(content=s, metadata={"source": "网络搜索", "chunk_id": i}) for i, s in enumerate(snippets)]
                n = engine.vector_store.add_to_knowledge_base(chunks)
                return jsonify({"message": f"已导入 {n} 条背景资料到知识库"})
            else:
                pending_kb.setdefault(sid, []).extend(snippets)
                return jsonify({"message": f"已暂存 {len(snippets)} 条背景资料（开始推演时自动导入）"})
        else:
            from crisis_sim.rag.web_searcher import search_event_news
            snippets = search_event_news(query)
            print(f"[DEBUG] search_event_news({query}) -> {len(snippets)} results")
            if not snippets:
                return jsonify({"message": "未搜索到结果，请尝试其他关键词"})
            if engine:
                engine.vector_store.add_opinions(snippets)
                return jsonify({"message": f"已导入 {len(snippets)} 条舆情数据"})
            else:
                pending_op.setdefault(sid, []).extend(snippets)
                return jsonify({"message": f"已暂存 {len(snippets)} 条舆情（开始推演时自动导入）"})
    except Exception as e:
        print(f"[DEBUG] search error: {e}")
        return jsonify({"message": f"搜索出错: {e}"})


@app.route("/api/import_opinions", methods=["POST"])
def api_import_opinions():
    data = request.json
    sid = data.get("session_id")
    engine = engines.get(sid)
    text = data.get("text", "")
    lines = [l.strip() for l in text.strip().split("\n") if l.strip()]
    if lines and engine:
        engine.vector_store.add_opinions(lines)
        return jsonify({"message": f"已导入 {len(lines)} 条舆情"})
    return jsonify({"message": "无内容可导入"})


@app.route("/api/progress", methods=["POST"])
def api_progress():
    data = request.json
    sid = data.get("session_id")
    return jsonify({"progress": exec_progress.get(sid, "")})


@app.route("/api/kb_status", methods=["POST"])
def api_kb_status():
    data = request.json
    sid = data.get("session_id")
    engine = engines.get(sid)
    if engine:
        return jsonify({"kb_count": engine.vector_store.kb_count, "op_count": engine.vector_store.opinion_count})
    return jsonify({"kb_count": 0, "op_count": 0})


@app.route("/api/summary", methods=["POST"])
def api_summary():
    data = request.json
    sid = data.get("session_id")
    engine = engines.get(sid)
    if not engine:
        return jsonify({"summary": ""})
    result = engine.build_result()
    return jsonify({"summary": result.final_summary})


if __name__ == "__main__":
    print("CrisisSim 启动中...")
    print(f"LLM: {config.LLM_PROVIDER} / {config.OPENAI_MODEL if config.LLM_PROVIDER=='openai' else 'N/A'}")
    print(f"最大轮次: {config.MAX_ROUNDS}")
    print("浏览器访问: http://localhost:5000")
    app.run(debug=False, port=5000, host="0.0.0.0")
