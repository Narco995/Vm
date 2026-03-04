"""
Web Dashboard for Telegram AI Bot
Accessible from any browser — desktop, iOS Safari, Android Chrome
"""
import asyncio
import json
import os
import aiosqlite
from aiohttp import web
from datetime import datetime, timedelta
from config import DATABASE_PATH

HTML_DASHBOARD = '''<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0">
<meta name="apple-mobile-web-app-capable" content="yes">
<meta name="apple-mobile-web-app-status-bar-style" content="black-translucent">
<meta name="theme-color" content="#0f172a">
<title>🤖 AI Bot Dashboard</title>
<link rel="apple-touch-icon" href="/static/icon.png">
<style>
  :root {
    --bg: #0f172a; --card: #1e293b; --accent: #3b82f6;
    --green: #22c55e; --yellow: #f59e0b; --red: #ef4444;
    --text: #f1f5f9; --muted: #94a3b8; --border: #334155;
  }
  * { margin:0; padding:0; box-sizing:border-box; }
  body { background:var(--bg); color:var(--text); font-family:-apple-system,BlinkMacSystemFont,'Segoe UI',sans-serif; min-height:100vh; }
  
  /* Header */
  .header { background:var(--card); border-bottom:1px solid var(--border); padding:16px 20px; display:flex; align-items:center; justify-content:space-between; position:sticky; top:0; z-index:100; backdrop-filter:blur(10px); }
  .header h1 { font-size:1.1rem; font-weight:700; display:flex; align-items:center; gap:8px; }
  .status-badge { display:flex; align-items:center; gap:6px; font-size:0.8rem; background:#22c55e22; color:var(--green); padding:4px 12px; border-radius:20px; border:1px solid #22c55e44; }
  .status-dot { width:8px; height:8px; border-radius:50%; background:var(--green); animation:pulse 2s infinite; }
  @keyframes pulse { 0%,100%{opacity:1} 50%{opacity:0.4} }

  /* Grid */
  .container { max-width:1200px; margin:0 auto; padding:20px; }
  .grid-4 { display:grid; grid-template-columns:repeat(auto-fit,minmax(220px,1fr)); gap:16px; margin-bottom:24px; }
  .grid-2 { display:grid; grid-template-columns:repeat(auto-fit,minmax(340px,1fr)); gap:16px; }

  /* Cards */
  .card { background:var(--card); border:1px solid var(--border); border-radius:12px; padding:20px; }
  .card-title { font-size:0.75rem; font-weight:600; color:var(--muted); text-transform:uppercase; letter-spacing:0.05em; margin-bottom:12px; }
  
  /* Stat cards */
  .stat-card { display:flex; flex-direction:column; gap:8px; }
  .stat-value { font-size:2rem; font-weight:800; line-height:1; }
  .stat-label { font-size:0.85rem; color:var(--muted); }
  .stat-icon { font-size:1.5rem; margin-bottom:4px; }
  .blue { color:var(--accent); } .green { color:var(--green); }
  .yellow { color:var(--yellow); } .red { color:var(--red); }

  /* Table */
  .table { width:100%; border-collapse:collapse; }
  .table th { text-align:left; font-size:0.72rem; text-transform:uppercase; letter-spacing:0.05em; color:var(--muted); padding:8px 12px; border-bottom:1px solid var(--border); }
  .table td { padding:10px 12px; border-bottom:1px solid var(--border)22; font-size:0.85rem; }
  .table tr:last-child td { border:none; }
  .table tr:hover td { background:#ffffff08; }

  /* Badges */
  .badge { display:inline-block; padding:3px 8px; border-radius:6px; font-size:0.72rem; font-weight:600; }
  .badge-blue { background:#3b82f622; color:var(--accent); }
  .badge-green { background:#22c55e22; color:var(--green); }
  .badge-yellow { background:#f59e0b22; color:var(--yellow); }
  .badge-purple { background:#a855f722; color:#a855f7; }
  .badge-pink { background:#ec489922; color:#ec4899; }

  /* Chart bars */
  .bar-chart { display:flex; flex-direction:column; gap:10px; }
  .bar-row { display:flex; align-items:center; gap:10px; }
  .bar-label { font-size:0.8rem; color:var(--muted); width:80px; flex-shrink:0; }
  .bar-track { flex:1; background:var(--border); border-radius:4px; height:8px; overflow:hidden; }
  .bar-fill { height:100%; border-radius:4px; transition:width 1s ease; }
  .bar-count { font-size:0.8rem; font-weight:600; width:30px; text-align:right; flex-shrink:0; }

  /* Activity feed */
  .activity-item { display:flex; align-items:flex-start; gap:12px; padding:10px 0; border-bottom:1px solid var(--border)44; }
  .activity-item:last-child { border:none; }
  .activity-icon { width:32px; height:32px; border-radius:8px; display:flex; align-items:center; justify-content:center; font-size:0.9rem; flex-shrink:0; }
  .activity-content { flex:1; min-width:0; }
  .activity-text { font-size:0.85rem; white-space:nowrap; overflow:hidden; text-overflow:ellipsis; }
  .activity-time { font-size:0.72rem; color:var(--muted); margin-top:2px; }

  /* Services grid */
  .services { display:grid; grid-template-columns:repeat(auto-fit,minmax(150px,1fr)); gap:12px; }
  .service-card { background:var(--bg); border:1px solid var(--border); border-radius:10px; padding:14px; display:flex; flex-direction:column; align-items:center; gap:8px; text-align:center; }
  .service-icon { font-size:1.6rem; }
  .service-name { font-size:0.8rem; font-weight:600; }
  .service-status { font-size:0.7rem; }

  /* Refresh */
  .refresh-bar { text-align:center; padding:12px; font-size:0.75rem; color:var(--muted); }
  
  /* Mobile tweaks */
  @media(max-width:600px) {
    .container { padding:12px; }
    .stat-value { font-size:1.6rem; }
    .grid-2 { grid-template-columns:1fr; }
  }
</style>
</head>
<body>
<div class="header">
  <h1>🤖 AI Bot Dashboard</h1>
  <div class="status-badge"><div class="status-dot"></div>Live</div>
</div>

<div class="container">

  <!-- Stat Cards -->
  <div class="grid-4" id="stats">
    <div class="card stat-card">
      <div class="stat-icon">👥</div>
      <div class="stat-value blue" id="total-users">—</div>
      <div class="stat-label">Total Users</div>
    </div>
    <div class="card stat-card">
      <div class="stat-icon">✅</div>
      <div class="stat-value green" id="total-tasks">—</div>
      <div class="stat-label">Tasks Completed</div>
    </div>
    <div class="card stat-card">
      <div class="stat-icon">⚙️</div>
      <div class="stat-value yellow" id="automations">—</div>
      <div class="stat-label">Automations</div>
    </div>
    <div class="card stat-card">
      <div class="stat-icon">🧠</div>
      <div class="stat-value" id="memory-notes">—</div>
      <div class="stat-label">Memory Notes</div>
    </div>
  </div>

  <div class="grid-2">

    <!-- Task breakdown -->
    <div class="card">
      <div class="card-title">📊 Task Breakdown</div>
      <div class="bar-chart" id="task-chart">
        <div style="color:var(--muted);font-size:0.85rem">Loading...</div>
      </div>
    </div>

    <!-- Recent Activity -->
    <div class="card">
      <div class="card-title">⚡ Recent Activity</div>
      <div id="activity-feed">
        <div style="color:var(--muted);font-size:0.85rem">Loading...</div>
      </div>
    </div>

    <!-- Active Services -->
    <div class="card">
      <div class="card-title">🐳 Docker Services</div>
      <div class="services">
        <div class="service-card">
          <div class="service-icon">🤖</div>
          <div class="service-name">Telegram Bot</div>
          <div class="service-status green">● Running</div>
        </div>
        <div class="service-card">
          <div class="service-icon">🌐</div>
          <div class="service-name">Dashboard</div>
          <div class="service-status green">● Running</div>
        </div>
        <div class="service-card">
          <div class="service-icon">🔒</div>
          <div class="service-name">Nginx</div>
          <div class="service-status green">● Running</div>
        </div>
        <div class="service-card">
          <div class="service-icon">🔄</div>
          <div class="service-name">Watchtower</div>
          <div class="service-status green">● Running</div>
        </div>
        <div class="service-card">
          <div class="service-icon">📊</div>
          <div class="service-name">Portainer</div>
          <div class="service-status green">● Running</div>
        </div>
        <div class="service-card">
          <div class="service-icon">📈</div>
          <div class="service-name">Grafana</div>
          <div class="service-status green">● Running</div>
        </div>
      </div>
    </div>

    <!-- AI Models -->
    <div class="card">
      <div class="card-title">🧠 AI Models Active</div>
      <div class="services">
        <div class="service-card">
          <div class="service-icon">⚡</div>
          <div class="service-name">GPT-4o</div>
          <div class="service-status green">● Active</div>
        </div>
        <div class="service-card">
          <div class="service-icon">🎨</div>
          <div class="service-name">DALL-E 3</div>
          <div class="service-status green">● Active</div>
        </div>
        <div class="service-card">
          <div class="service-icon">🎙</div>
          <div class="service-name">Whisper</div>
          <div class="service-status green">● Active</div>
        </div>
        <div class="service-card">
          <div class="service-icon">🌟</div>
          <div class="service-name">Mistral</div>
          <div class="service-status green">● Active</div>
        </div>
        <div class="service-card">
          <div class="service-icon">👁</div>
          <div class="service-name">GPT Vision</div>
          <div class="service-status green">● Active</div>
        </div>
      </div>
    </div>

  </div>
  <div class="refresh-bar" id="refresh-time">Auto-refreshes every 15s</div>
</div>

<script>
const TASK_COLORS = {
  pdf:'#3b82f6', docx:'#a855f7', code:'#22c55e', research:'#f59e0b',
  image:'#ec4899', vision:'#06b6d4', data_analysis:'#f97316', report:'#6366f1', file_analysis:'#84cc16'
};
const TASK_ICONS = {
  pdf:'📄', docx:'📝', code:'💻', research:'🔬', image:'🖼',
  vision:'👁', data_analysis:'📊', report:'📋', file_analysis:'📂', chat:'💬'
};

async function loadStats() {
  try {
    const r = await fetch('/api/stats');
    const d = await r.json();

    document.getElementById('total-users').textContent = d.total_users ?? 0;
    document.getElementById('total-tasks').textContent = d.total_tasks ?? 0;
    document.getElementById('automations').textContent = d.automations ?? 0;
    document.getElementById('memory-notes').textContent = d.memory_notes ?? 0;

    // Bar chart
    const chart = document.getElementById('task-chart');
    const tasks = d.task_breakdown || {};
    const max = Math.max(...Object.values(tasks), 1);
    chart.innerHTML = Object.entries(tasks).map(([type, count]) => `
      <div class="bar-row">
        <div class="bar-label">${TASK_ICONS[type]||'📌'} ${type}</div>
        <div class="bar-track"><div class="bar-fill" style="width:${(count/max*100).toFixed(1)}%;background:${TASK_COLORS[type]||'#64748b'}"></div></div>
        <div class="bar-count">${count}</div>
      </div>`).join('') || '<div style="color:var(--muted)">No tasks yet</div>';

    // Activity feed
    const feed = document.getElementById('activity-feed');
    const acts = d.recent_tasks || [];
    feed.innerHTML = acts.map(t => `
      <div class="activity-item">
        <div class="activity-icon" style="background:${TASK_COLORS[t.type]||'#334155'}22">${TASK_ICONS[t.type]||'📌'}</div>
        <div class="activity-content">
          <div class="activity-text">${t.description}</div>
          <div class="activity-time">${t.type} · ${t.created_at?.slice(0,16) || ''}</div>
        </div>
      </div>`).join('') || '<div style="color:var(--muted);font-size:0.85rem">No activity yet</div>';

    document.getElementById('refresh-time').textContent = 'Last updated: ' + new Date().toLocaleTimeString();
  } catch(e) {
    console.error('Failed to load stats:', e);
  }
}

loadStats();
setInterval(loadStats, 15000);
</script>
</body>
</html>'''


async def handle_dashboard(request):
    return web.Response(text=HTML_DASHBOARD, content_type='text/html')


async def handle_stats(request):
    try:
        async with aiosqlite.connect(DATABASE_PATH) as db:
            # Total users
            async with db.execute("SELECT COUNT(*) FROM users") as c:
                total_users = (await c.fetchone())[0]

            # Total tasks
            async with db.execute("SELECT COUNT(*) FROM task_history WHERE status='completed'") as c:
                total_tasks = (await c.fetchone())[0]

            # Automations
            async with db.execute("SELECT COUNT(*) FROM automations WHERE active=1") as c:
                automations = (await c.fetchone())[0]

            # Memory notes
            async with db.execute("SELECT COUNT(*) FROM memory_notes") as c:
                memory_notes = (await c.fetchone())[0]

            # Task breakdown
            async with db.execute(
                "SELECT task_type, COUNT(*) FROM task_history GROUP BY task_type ORDER BY COUNT(*) DESC"
            ) as c:
                rows = await c.fetchall()
                task_breakdown = {r[0]: r[1] for r in rows}

            # Recent tasks
            async with db.execute(
                "SELECT task_type, description, status, created_at FROM task_history ORDER BY created_at DESC LIMIT 8"
            ) as c:
                rows = await c.fetchall()
                recent_tasks = [
                    {"type": r[0], "description": r[1][:60], "status": r[2], "created_at": r[3]}
                    for r in rows
                ]

        return web.json_response({
            "total_users": total_users,
            "total_tasks": total_tasks,
            "automations": automations,
            "memory_notes": memory_notes,
            "task_breakdown": task_breakdown,
            "recent_tasks": recent_tasks,
            "uptime": "Online",
            "timestamp": datetime.now().isoformat()
        })
    except Exception as e:
        return web.json_response({"error": str(e), "total_users": 0, "total_tasks": 0,
                                   "automations": 0, "memory_notes": 0,
                                   "task_breakdown": {}, "recent_tasks": []})


async def handle_health(request):
    return web.json_response({"status": "ok", "timestamp": datetime.now().isoformat()})


def create_app():
    app = web.Application()
    app.router.add_get('/', handle_dashboard)
    app.router.add_get('/api/stats', handle_stats)
    app.router.add_get('/health', handle_health)
    return app


if __name__ == '__main__':
    port = int(os.getenv('DASHBOARD_PORT', 8080))
    print(f"🌐 Dashboard starting on http://0.0.0.0:{port}")
    web.run_app(create_app(), host='0.0.0.0', port=port)
