import html
import json
from datetime import datetime


def safe(value, default=None):
    return value if value is not None else default


def esc(value):
    return html.escape(str(value))


def status_pill(ok):
    if ok is True:
        return '<span class="pill good">OK</span>'
    if ok is False:
        return '<span class="pill warn">CHECK</span>'
    return '<span class="pill neutral">UNKNOWN</span>'


def command_chip(command):
    return f'<button class="cmd" onclick="copyText({json.dumps(command)})">{esc(command)}</button>'


def render_control_plane_ui(bundle):
    mission = bundle.get("mission", {}) or {}
    runtime = bundle.get("status", {}) or {}
    commands = bundle.get("commands", {}) or {}
    voice = bundle.get("voice", {}) or {}
    agents = bundle.get("agents", {}) or {}
    aider = bundle.get("aider", {}) or {}
    apps = bundle.get("apps", {}) or {}
    timeline = bundle.get("timeline", {}) or {}

    health = mission.get("health", {}) or {}
    next_actions = mission.get("next_actions", []) or []
    command_groups = commands.get("groups", {}) or {}
    tools = apps.get("tools", {}) or {}
    recent_runs = agents.get("runs", []) or []
    timeline_items = timeline.get("items", []) or []

    available_tools = [name for name, item in tools.items() if item.get("available")]
    missing_tools = [name for name, item in tools.items() if not item.get("available")]

    release_commands = command_groups.get("release", [])
    mission_commands = command_groups.get("mission", [])
    agent_commands = command_groups.get("agents", [])
    aider_commands = command_groups.get("aider", [])
    voice_commands = command_groups.get("voice", [])
    skill_commands = command_groups.get("skills", [])

    raw_summary = {
        "note": "Compact summary only. Full data is available through /api/home-bundle.",
        "mission_health": (mission.get("health", {}) if isinstance(mission, dict) else {}),
        "operator": bundle.get("operator", {}),
        "tasks": {
            "count": (bundle.get("tasks", {}) or {}).get("count"),
            "items_shown": len((bundle.get("tasks", {}) or {}).get("tasks", []) or [])
        },
        "capability_graph": {
            "node_count": (bundle.get("capability_graph", {}) or {}).get("node_count"),
            "edge_count": (bundle.get("capability_graph", {}) or {}).get("edge_count")
        },
        "integration": {
            "candidate_count": (bundle.get("integration_fusion", {}) or {}).get("candidate_count"),
            "top_10": (bundle.get("integration_fusion", {}) or {}).get("top_10", [])[:5]
        }
    }
    data_json = json.dumps(raw_summary, indent=2)
    now = datetime.now().strftime("%H:%M:%S")

    html_doc = r'''<!doctype html>
<html>
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Seed Control Plane</title>
<style>
:root {
  --bg: #07090d;
  --panel: #10151d;
  --panel2: #151c26;
  --panel3: #1b2431;
  --border: #273242;
  --text: #edf2f7;
  --muted: #9aa7b7;
  --soft: #c6d0dd;
  --orange: #ff9f43;
  --orange2: #ffb86b;
  --green: #3ddc97;
  --red: #ff6b6b;
  --blue: #72a7ff;
  --shadow: 0 18px 50px rgba(0,0,0,.35);
}
* { box-sizing: border-box; }
body {
  margin: 0;
  background:
    radial-gradient(circle at top left, rgba(255,159,67,.14), transparent 32rem),
    radial-gradient(circle at top right, rgba(114,167,255,.10), transparent 28rem),
    var(--bg);
  color: var(--text);
  font-family: -apple-system, BlinkMacSystemFont, "SF Pro Display", Helvetica, Arial, sans-serif;
}
.app {
  min-height: 100vh;
  display: grid;
  grid-template-columns: 270px 1fr;
}
.sidebar {
  position: sticky;
  top: 0;
  height: 100vh;
  padding: 22px;
  background: rgba(10,14,20,.92);
  border-right: 1px solid var(--border);
  backdrop-filter: blur(16px);
}
.brand {
  display: flex;
  gap: 12px;
  align-items: center;
  margin-bottom: 26px;
}
.logo {
  width: 42px;
  height: 42px;
  border-radius: 14px;
  background: linear-gradient(135deg, var(--orange), #7a4cff);
  box-shadow: 0 0 28px rgba(255,159,67,.25);
}
.brand h1 {
  font-size: 19px;
  margin: 0;
}
.brand p {
  margin: 2px 0 0;
  color: var(--muted);
  font-size: 12px;
}
.nav a {
  display: block;
  color: var(--soft);
  text-decoration: none;
  padding: 11px 12px;
  border-radius: 11px;
  margin: 5px 0;
}
.nav a:hover {
  background: var(--panel2);
  color: white;
}
.sidebox {
  margin-top: 22px;
  padding: 14px;
  border: 1px solid var(--border);
  border-radius: 14px;
  background: var(--panel);
  color: var(--muted);
  font-size: 13px;
}
.main {
  padding: 26px;
}
.hero {
  display: grid;
  grid-template-columns: 1.4fr .8fr;
  gap: 18px;
  margin-bottom: 18px;
}
.card {
  background: rgba(16,21,29,.88);
  border: 1px solid var(--border);
  border-radius: 18px;
  padding: 18px;
  box-shadow: var(--shadow);
}
.card h2 {
  margin: 0 0 14px;
  font-size: 17px;
}
.card h3 {
  margin: 16px 0 8px;
  color: var(--soft);
  font-size: 14px;
}
.hero-title {
  font-size: 38px;
  letter-spacing: -1.2px;
  margin: 0 0 8px;
}
.hero-sub {
  color: var(--muted);
  font-size: 15px;
  max-width: 760px;
  line-height: 1.45;
}
.grid {
  display: grid;
  grid-template-columns: repeat(3, minmax(260px, 1fr));
  gap: 18px;
}
.wide { grid-column: span 2; }
.full { grid-column: 1 / -1; }
.metric-row {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
}
.metric {
  flex: 1;
  min-width: 145px;
  padding: 12px;
  background: var(--panel2);
  border: 1px solid var(--border);
  border-radius: 14px;
}
.metric .label {
  color: var(--muted);
  font-size: 12px;
}
.metric .value {
  margin-top: 5px;
  font-size: 18px;
  font-weight: 700;
}
.pill {
  display: inline-flex;
  align-items: center;
  gap: 6px;
  border-radius: 999px;
  padding: 5px 9px;
  font-size: 12px;
  font-weight: 700;
}
.good { background: rgba(61,220,151,.12); color: var(--green); border: 1px solid rgba(61,220,151,.25); }
.warn { background: rgba(255,107,107,.12); color: var(--red); border: 1px solid rgba(255,107,107,.25); }
.neutral { background: rgba(154,167,183,.12); color: var(--muted); border: 1px solid rgba(154,167,183,.25); }
.action-list {
  display: grid;
  gap: 9px;
  margin: 0;
  padding: 0;
  list-style: none;
}
.action-list li {
  padding: 11px 12px;
  background: var(--panel2);
  border: 1px solid var(--border);
  border-radius: 13px;
  color: var(--soft);
}
.cmd-grid {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
}
.cmd {
  cursor: pointer;
  border: 1px solid rgba(255,159,67,.28);
  background: rgba(255,159,67,.09);
  color: var(--orange2);
  border-radius: 999px;
  padding: 8px 10px;
  font-family: ui-monospace, SFMono-Regular, Menlo, monospace;
  font-size: 12px;
}
.cmd:hover {
  background: rgba(255,159,67,.16);
}
.kv {
  display: grid;
  gap: 8px;
}
.kv div {
  display: flex;
  justify-content: space-between;
  gap: 10px;
  padding: 9px 0;
  border-bottom: 1px solid rgba(255,255,255,.06);
}
.kv span:first-child { color: var(--muted); }
.kv span:last-child { color: var(--soft); text-align: right; }
.timeline {
  display: grid;
  gap: 8px;
  max-height: 360px;
  overflow: auto;
}
.event {
  padding: 10px 12px;
  border-left: 3px solid var(--orange);
  background: var(--panel2);
  border-radius: 10px;
}
.event .time {
  color: var(--muted);
  font-size: 12px;
}
.event .body {
  margin-top: 4px;
  color: var(--soft);
  font-size: 13px;
}
pre {
  white-space: pre-wrap;
  word-break: break-word;
  background: #05070a;
  border: 1px solid var(--border);
  border-radius: 14px;
  padding: 14px;
  color: #d5dbe5;
  max-height: 420px;
  overflow: auto;
}
.topline {
  display: flex;
  justify-content: space-between;
  gap: 12px;
  align-items: center;
  margin-bottom: 12px;
}
.refresh {
  border: 1px solid var(--border);
  background: var(--panel2);
  color: var(--soft);
  border-radius: 999px;
  padding: 9px 12px;
  cursor: pointer;
}
.refresh:hover { color: white; border-color: var(--orange); }
.toast {
  position: fixed;
  right: 18px;
  bottom: 18px;
  background: var(--panel3);
  border: 1px solid var(--border);
  border-radius: 12px;
  padding: 12px 14px;
  color: var(--soft);
  display: none;
}
@media (max-width: 1050px) {
  .app { grid-template-columns: 1fr; }
  .sidebar { position: relative; height: auto; }
  .hero { grid-template-columns: 1fr; }
  .grid { grid-template-columns: 1fr; }
  .wide { grid-column: auto; }
}
</style>
</head>
<body>
<div class="app">
  <aside class="sidebar">
    <div class="brand">
      <div class="logo"></div>
      <div>
        <h1>Seed Control</h1>
        <p>v3.0.1 local cockpit</p>
      </div>
    </div>
    <nav class="nav">
      <a href="#mission">Mission</a>
      <a href="#gates">Gates</a>
      <a href="#voice">Voice</a>
      <a href="#agents">Agents</a>
      <a href="#aider">Aider</a>
      <a href="#commands">Commands</a>
      <a href="#timeline">Timeline</a>
      <a href="#api">API</a>
    </nav>
    <div class="sidebox">
      <strong>Local only</strong><br>
      127.0.0.1. No remote bind. No auto-execute. CLI approval flow stays in control.
    </div>
    <div class="sidebox">
      <strong>Last render</strong><br>
      __NOW__
    </div>
  </aside>

  <main class="main">
    <section class="hero">
      <div class="card">
        <div class="topline">
          <span class="pill good">LOCAL</span>
          <button class="refresh" onclick="location.reload()">Refresh</button>
        </div>
        <h1 class="hero-title">Mission Control</h1>
        <p class="hero-sub">
          Your Seed cockpit: status, gates, voice, agents, Aider, app tools, commands, and recent events.
          This page is designed for decisions: what is healthy, what needs action, and which command to run next.
        </p>
      </div>

      <div class="card" id="mission">
        <h2>Mission Health</h2>
        <div class="metric-row">
          __HEALTH_METRICS__
        </div>
      </div>
    </section>

    <section class="grid">
      <div class="card wide">
        <h2>Next Actions</h2>
        <ul class="action-list">
          __NEXT_ACTIONS__
        </ul>
      </div>

      <div class="card">
        <h2>Runtime</h2>
        <div class="kv">
          __RUNTIME_KV__
        </div>
      </div>

      <div class="card" id="gates">
        <h2>Gate Quick Stack</h2>
        <div class="cmd-grid">__RELEASE_COMMANDS__</div>
      </div>

      <div class="card" id="voice">
        <h2>Voice</h2>
        <div class="kv">__VOICE_KV__</div>
        <h3>Commands</h3>
        <div class="cmd-grid">__VOICE_COMMANDS__</div>
      </div>

      <div class="card" id="agents">
        <h2>Agents</h2>
        <div class="kv">__AGENT_KV__</div>
        <h3>Commands</h3>
        <div class="cmd-grid">__AGENT_COMMANDS__</div>
      </div>

      <div class="card" id="aider">
        <h2>Aider</h2>
        <div class="kv">__AIDER_KV__</div>
        <h3>Commands</h3>
        <div class="cmd-grid">__AIDER_COMMANDS__</div>
      </div>

      <div class="card">
        <h2>Local Tools</h2>
        <div class="kv">__TOOLS_KV__</div>
      </div>

      <div class="card wide" id="commands">
        <h2>Command Center</h2>
        <h3>Mission</h3>
        <div class="cmd-grid">__MISSION_COMMANDS__</div>
        <h3>Skills</h3>
        <div class="cmd-grid">__SKILL_COMMANDS__</div>
      </div>

      <div class="card full" id="timeline">
        <h2>Recent Timeline</h2>
        <div class="timeline">__TIMELINE__</div>
      </div>

      <div class="card full" id="api">
        <h2>Raw Bundle</h2>
        <pre>__RAW_JSON__</pre>
      </div>
    </section>
  </main>
</div>

<div class="toast" id="toast">Copied</div>

<script>
function copyText(text) {
  navigator.clipboard.writeText(text).then(() => {
    const toast = document.getElementById("toast");
    toast.style.display = "block";
    toast.innerText = "Copied: " + text;
    setTimeout(() => toast.style.display = "none", 1400);
  });
}
</script>
</body>
</html>
'''

    health_html = ""
    for key, value in health.items():
        health_html += f'''
        <div class="metric">
          <div class="label">{esc(key)}</div>
          <div class="value">{status_pill(value)}</div>
        </div>
        '''

    next_html = "".join(f"<li>{esc(item)}</li>" for item in next_actions) or "<li>No next actions. System looks calm.</li>"

    system = runtime.get("system", {}) or {}
    runtime_kv = "".join([
        f"<div><span>Python</span><span>{esc(system.get('python', 'unknown'))}</span></div>",
        f"<div><span>Machine</span><span>{esc(system.get('machine', 'unknown'))}</span></div>",
        f"<div><span>Platform</span><span>{esc(system.get('platform', 'unknown'))}</span></div>",
    ])

    voice_kv = "".join([
        f"<div><span>No secret listening</span><span>{esc(voice.get('no_secret_always_listening', True))}</span></div>",
        f"<div><span>Recent transcripts</span><span>{len(voice.get('recent_transcripts', []) or [])}</span></div>",
        f"<div><span>Next patch items</span><span>{len(voice.get('next_voice_patch', []) or [])}</span></div>",
    ])

    agent_kv = "".join([
        f"<div><span>Recent runs</span><span>{len(recent_runs)}</span></div>",
        f"<div><span>Approved runs shown</span><span>{sum(1 for r in recent_runs if r.get('approved'))}</span></div>",
    ])

    aider_policy = aider.get("policy", {}) or {}
    aider_kv = "".join([
        f"<div><span>Available</span><span>{esc(aider.get('aider_available'))}</span></div>",
        f"<div><span>Command</span><span>{esc(aider.get('aider_command'))}</span></div>",
        f"<div><span>Execution locked</span><span>{esc(aider_policy.get('execution_locked'))}</span></div>",
    ])

    tools_kv = "".join([
        f"<div><span>Available</span><span>{esc(', '.join(available_tools) or 'none')}</span></div>",
        f"<div><span>Missing</span><span>{esc(', '.join(missing_tools) or 'none')}</span></div>",
    ])

    timeline_html = ""
    for item in timeline_items[-12:]:
        created = item.get("created_at") or item.get("timestamp") or "unknown-time"
        source = item.get("_source_file") or "Seed"
        event = item.get("event") or item.get("type") or item.get("command") or item.get("intent") or "event"
        timeline_html += f'''
        <div class="event">
          <div class="time">{esc(created)} · {esc(source)}</div>
          <div class="body">{esc(event)}</div>
        </div>
        '''
    if not timeline_html:
        timeline_html = '<div class="event"><div class="body">No timeline items yet.</div></div>'

    replacements = {
        "__NOW__": esc(now),
        "__HEALTH_METRICS__": health_html,
        "__NEXT_ACTIONS__": next_html,
        "__RUNTIME_KV__": runtime_kv,
        "__RELEASE_COMMANDS__": "".join(command_chip(cmd) for cmd in release_commands),
        "__VOICE_KV__": voice_kv,
        "__VOICE_COMMANDS__": "".join(command_chip(cmd) for cmd in voice_commands),
        "__AGENT_KV__": agent_kv,
        "__AGENT_COMMANDS__": "".join(command_chip(cmd) for cmd in agent_commands),
        "__AIDER_KV__": aider_kv,
        "__AIDER_COMMANDS__": "".join(command_chip(cmd) for cmd in aider_commands),
        "__TOOLS_KV__": tools_kv,
        "__MISSION_COMMANDS__": "".join(command_chip(cmd) for cmd in mission_commands),
        "__SKILL_COMMANDS__": "".join(command_chip(cmd) for cmd in skill_commands),
        "__TIMELINE__": timeline_html,
        "__RAW_JSON__": esc(data_json),
    }

    for key, value in replacements.items():
        html_doc = html_doc.replace(key, value)

    return html_doc
