import json


try:
    from seed_config import (
        COMPANION_OS_COCKPIT_HOST,
        COMPANION_OS_COCKPIT_PORT,
        COCKPIT_REFRESH_SECONDS
    )
except Exception:
    COMPANION_OS_COCKPIT_HOST = "127.0.0.1"
    COMPANION_OS_COCKPIT_PORT = 8770
    COCKPIT_REFRESH_SECONDS = 5


try:
    from fastapi import FastAPI
    from fastapi.responses import HTMLResponse, JSONResponse
    import uvicorn
    FASTAPI_AVAILABLE = True
except Exception:
    FASTAPI_AVAILABLE = False


from seed_companion_os import (
    load_companion_os_state,
    load_companion_os_events,
    calculate_companion_os_v2_score,
    format_companion_os_status
)


try:
    from seed_world_engine import get_world_context_for_prompt
    WORLD_AVAILABLE = True
except Exception:
    WORLD_AVAILABLE = False


try:
    from seed_avatar_state import get_avatar_state
    AVATAR_AVAILABLE = True
except Exception:
    AVATAR_AVAILABLE = False


try:
    from seed_voice_session import load_voice_state, build_voice_pulse
    VOICE_AVAILABLE = True
except Exception:
    VOICE_AVAILABLE = False


try:
    from seed_trace_engine import load_traces, trace_stats
    TRACE_AVAILABLE = True
except Exception:
    TRACE_AVAILABLE = False


try:
    from seed_tool_manifest_v2 import get_tool_manifest
    TOOL_MANIFEST_AVAILABLE = True
except Exception:
    TOOL_MANIFEST_AVAILABLE = False


try:
    from seed_os_registry import get_os_command_registry, registry_stats
    REGISTRY_AVAILABLE = True
except Exception:
    REGISTRY_AVAILABLE = False


try:
    from seed_document_registry import load_registry
    DOCUMENTS_AVAILABLE = True
except Exception:
    DOCUMENTS_AVAILABLE = False


try:
    from seed_release_manager import load_release_state
    RELEASE_AVAILABLE = True
except Exception:
    RELEASE_AVAILABLE = False


try:
    from seed_workflow_engine import get_workflows
    WORKFLOW_AVAILABLE = True
except Exception:
    WORKFLOW_AVAILABLE = False


try:
    from seed_continuity_engine import build_continuity_context
    CONTINUITY_AVAILABLE = True
except Exception:
    CONTINUITY_AVAILABLE = False


try:
    from seed_llm import ask_llm
    LLM_AVAILABLE = True
except Exception:
    LLM_AVAILABLE = False


def cockpit_payload():
    state = load_companion_os_state()
    v2 = calculate_companion_os_v2_score(save=False)

    payload = {
        "state": state,
        "events": load_companion_os_events(limit=30),
        "v2": v2,
        "status_text": format_companion_os_status()
    }

    if AVATAR_AVAILABLE:
        try:
            payload["avatar"] = get_avatar_state()
        except Exception as error:
            payload["avatar_error"] = str(error)

    if VOICE_AVAILABLE:
        try:
            payload["voice"] = load_voice_state()
        except Exception as error:
            payload["voice_error"] = str(error)

    if TRACE_AVAILABLE:
        try:
            payload["traces"] = load_traces(limit=20)
            payload["trace_stats"] = trace_stats()
        except Exception as error:
            payload["trace_error"] = str(error)

    if TOOL_MANIFEST_AVAILABLE:
        try:
            payload["tools"] = get_tool_manifest()
        except Exception as error:
            payload["tools_error"] = str(error)

    if REGISTRY_AVAILABLE:
        try:
            payload["commands"] = get_os_command_registry()
            payload["registry_stats"] = registry_stats()
        except Exception as error:
            payload["registry_error"] = str(error)

    if DOCUMENTS_AVAILABLE:
        try:
            payload["documents"] = load_registry()
        except Exception as error:
            payload["documents_error"] = str(error)

    if RELEASE_AVAILABLE:
        try:
            payload["release"] = load_release_state()
        except Exception as error:
            payload["release_error"] = str(error)

    if WORKFLOW_AVAILABLE:
        try:
            payload["workflows"] = get_workflows()
        except Exception as error:
            payload["workflow_error"] = str(error)

    return payload


def cockpit_chat_response(message):
    if not LLM_AVAILABLE:
        return "Cockpit chat LLM unavailable."

    context = {}

    if CONTINUITY_AVAILABLE:
        try:
            context["continuity"] = build_continuity_context(message)
        except Exception as error:
            context["continuity_error"] = str(error)

    context["cockpit_state"] = cockpit_payload()

    prompt = f"""
You are Seed inside the Companion OS Cockpit.

User message:
{message}

Context:
{json.dumps(context, indent=2)}

Rules:
- Seed is not alive or conscious.
- Be direct and useful.
- Use Companion OS state.
- If asked about actions, explain approval gates.
- Do not claim capabilities beyond registered state/tools.
"""

    return ask_llm(prompt, task_type="chat", runtime_context=None)


def create_app():
    if not FASTAPI_AVAILABLE:
        return None

    app = FastAPI(title="Seed Companion OS Cockpit")

    @app.get("/")
    def home():
        return HTMLResponse(cockpit_html())

    @app.get("/api/state")
    def api_state():
        return JSONResponse(cockpit_payload())

    @app.get("/api/v2")
    def api_v2():
        return JSONResponse(calculate_companion_os_v2_score(save=False))

    @app.get("/api/events")
    def api_events():
        return JSONResponse(load_companion_os_events(limit=50))

    @app.get("/api/traces")
    def api_traces():
        if not TRACE_AVAILABLE:
            return JSONResponse({"error": "trace engine unavailable"})
        return JSONResponse({
            "stats": trace_stats(),
            "traces": load_traces(limit=50)
        })

    @app.get("/api/tools")
    def api_tools():
        if not TOOL_MANIFEST_AVAILABLE:
            return JSONResponse({"error": "tool manifest unavailable"})
        return JSONResponse(get_tool_manifest())

    @app.get("/api/commands")
    def api_commands():
        if not REGISTRY_AVAILABLE:
            return JSONResponse({"error": "registry unavailable"})
        return JSONResponse({
            "stats": registry_stats(),
            "commands": get_os_command_registry()
        })

    @app.get("/api/documents")
    def api_documents():
        if not DOCUMENTS_AVAILABLE:
            return JSONResponse({"error": "document registry unavailable"})
        return JSONResponse(load_registry())

    @app.get("/api/release")
    def api_release():
        if not RELEASE_AVAILABLE:
            return JSONResponse({"error": "release manager unavailable"})
        return JSONResponse(load_release_state())

    @app.get("/api/workflows")
    def api_workflows():
        if not WORKFLOW_AVAILABLE:
            return JSONResponse({"error": "workflow engine unavailable"})
        return JSONResponse(get_workflows())

    @app.get("/api/pulse")
    def api_pulse():
        if VOICE_AVAILABLE:
            text = build_voice_pulse()
        else:
            text = "Companion OS Alpha is online. Voice session is unavailable."
        return JSONResponse({"pulse": text})

    @app.post("/api/chat")
    async def api_chat(payload: dict):
        message = payload.get("message", "")
        response = cockpit_chat_response(message)
        return JSONResponse({"response": response})

    try:
        from seed_cockpit_actions import attach_cockpit_action_routes, mark_cockpit_api_signals
        attach_cockpit_action_routes(app)
        mark_cockpit_api_signals()
    except Exception as error:
        print(f"Cockpit action routes unavailable: {error}")

    return app


def run_companion_cockpit():
    if not FASTAPI_AVAILABLE:
        print("FastAPI/uvicorn missing. Run: pip install fastapi uvicorn")
        return

    app = create_app()

    print("\n=== SEED COMPANION OS COCKPIT ===")
    print(f"Open: http://{COMPANION_OS_COCKPIT_HOST}:{COMPANION_OS_COCKPIT_PORT}")
    print("CTRL+C to stop.")

    uvicorn.run(
        app,
        host=COMPANION_OS_COCKPIT_HOST,
        port=COMPANION_OS_COCKPIT_PORT
    )


def cockpit_html():
    refresh_ms = int(COCKPIT_REFRESH_SECONDS) * 1000

    return f"""
<!DOCTYPE html>
<html>
<head>
<title>Seed Companion OS Alpha</title>
<meta charset="utf-8">
<style>
:root {{
  --bg:#07090c;
  --panel:#14181d;
  --panel2:#1d232a;
  --text:#f4efe4;
  --muted:#aaa39a;
  --accent:#ff9f1c;
  --gold:#ffd166;
  --green:#06d6a0;
  --red:#ef476f;
}}
* {{ box-sizing:border-box; }}
body {{
  margin:0;
  background:
    radial-gradient(circle at top left, rgba(255,159,28,.20), transparent 30%),
    radial-gradient(circle at bottom right, rgba(6,214,160,.08), transparent 25%),
    var(--bg);
  color:var(--text);
  font-family:-apple-system,BlinkMacSystemFont,"Segoe UI",sans-serif;
}}
header {{
  padding:22px 30px;
  border-bottom:1px solid #2b323a;
  display:flex;
  justify-content:space-between;
  align-items:center;
}}
h1 {{ margin:0; font-size:24px; }}
.sub {{ color:var(--accent); margin-top:5px; }}
.grid {{
  padding:24px 30px;
  display:grid;
  grid-template-columns:1.25fr 1fr 1fr;
  gap:16px;
}}
.panel {{
  background:linear-gradient(180deg,var(--panel),#0e1114);
  border:1px solid #2d333a;
  border-radius:18px;
  padding:16px;
  box-shadow:0 12px 30px rgba(0,0,0,.30);
}}
.wide {{ grid-column:span 2; }}
.full {{ grid-column:span 3; }}
h2 {{
  margin:0 0 12px;
  font-size:16px;
  color:var(--gold);
}}
.metric {{
  display:flex;
  justify-content:space-between;
  gap:12px;
  padding:8px 0;
  border-bottom:1px solid #293038;
  color:var(--muted);
}}
.metric strong {{ color:var(--text); text-align:right; }}
.world {{
  min-height:270px;
  border-radius:18px;
  background:linear-gradient(180deg,#1b2027,#090b0d);
  position:relative;
  overflow:hidden;
  border:1px solid #343c45;
}}
.orb {{
  position:absolute;
  left:calc(50% - 46px);
  top:72px;
  width:92px;
  height:92px;
  border-radius:50%;
  background:radial-gradient(circle,#ffe39a,#ff9f1c 55%,#6f3900);
  box-shadow:0 0 60px rgba(255,159,28,.8);
  animation:breathe 3s ease-in-out infinite;
}}
.ring {{
  position:absolute;
  left:calc(50% - 120px);
  top:40px;
  width:240px;
  height:160px;
  border:1px solid rgba(255,159,28,.35);
  border-radius:50%;
  transform:rotate(-8deg);
}}
@keyframes breathe {{ 0%,100%{{transform:scale(1)}} 50%{{transform:scale(1.08)}} }}
.label {{
  position:absolute;
  bottom:18px;
  left:18px;
  right:18px;
  color:var(--muted);
  line-height:1.5;
}}
pre {{
  white-space:pre-wrap;
  color:var(--muted);
  max-height:260px;
  overflow:auto;
}}
button {{
  background:var(--panel2);
  color:var(--text);
  border:1px solid #3a424b;
  padding:10px 14px;
  border-radius:12px;
  cursor:pointer;
}}
button:hover {{ border-color:var(--accent); }}
input {{
  width:100%;
  padding:12px;
  background:#0d1013;
  color:var(--text);
  border:1px solid #343b44;
  border-radius:12px;
}}
.chatrow {{
  display:grid;
  grid-template-columns:1fr auto;
  gap:10px;
}}
#chatlog {{
  min-height:120px;
  max-height:260px;
  overflow:auto;
  color:var(--muted);
  margin-bottom:10px;
}}
.badge {{
  display:inline-block;
  padding:4px 8px;
  border:1px solid #3a424b;
  border-radius:999px;
  color:var(--muted);
  margin:2px;
}}
@media(max-width:1000px) {{
  .grid{{grid-template-columns:1fr}}
  .wide,.full{{grid-column:span 1}}
}}
</style>
</head>
<body>
<header>
  <div>
    <h1>Seed Companion OS Alpha</h1>
    <div class="sub" id="subtitle">loading...</div>
  </div>
  <button onclick="refresh()">Refresh</button>
</header>

<main class="grid">
  <section class="panel wide">
    <h2>Seed World</h2>
    <div class="world">
      <div class="ring"></div>
      <div class="orb"></div>
      <div class="label" id="world">Loading world...</div>
    </div>
  </section>

  <section class="panel">
    <h2>V2 Release Gate</h2>
    <div id="v2"></div>
  </section>

  <section class="panel">
    <h2>Memory Garden</h2>
    <div id="garden"></div>
  </section>

  <section class="panel">
    <h2>Presence</h2>
    <div id="presence"></div>
  </section>

  <section class="panel">
    <h2>Trust</h2>
    <div id="trust"></div>
  </section>

  <section class="panel">
    <h2>Systems</h2>
    <div id="systems"></div>
  </section>

  <section class="panel full">
    <h2>Cockpit Chat</h2>
    <div id="chatlog">Ask Seed from the cockpit. This uses Companion OS state.</div>
    <div class="chatrow">
      <input id="chatinput" placeholder="Ask Seed..." onkeydown="if(event.key==='Enter') sendChat()">
      <button onclick="sendChat()">Send</button>
    </div>
  </section>

  <section class="panel wide">
    <h2>Recent Events</h2>
    <pre id="events">loading...</pre>
  </section>

  <section class="panel">
    <h2>Trace Stats</h2>
    <div id="traces"></div>
  </section>


  <section class="panel full">
    <h2>Interactive Cockpit Actions</h2>

    <div style="display:grid; grid-template-columns:repeat(auto-fit,minmax(220px,1fr)); gap:10px; margin-bottom:12px;">
      <button onclick="runAction('voice_privacy_check', {{}})">Voice Privacy Check</button>
      <button onclick="runAction('voice_pulse_dry', {{}})">Voice Pulse Dry-Run</button>
      <button onclick="runAction('module_health', {{}})">Module Health</button>
      <button onclick="runAction('test_matrix', {{}})">Test Matrix</button>
      <button onclick="runAction('release_readiness', {{}})">Release Readiness</button>
      <button onclick="runAction('release_check', {{}})">Release Check</button>
      <button onclick="runAction('v2_check', {{}})">V2 Gate</button>
      <button onclick="runAction('avatar_mode', {{mode:'builder'}})">Avatar Builder Mode</button>
    </div>

    <div style="display:grid; grid-template-columns:1fr 220px auto; gap:10px; margin-bottom:10px;">
      <input id="simAction" placeholder="Action to simulate, e.g. Run v2 release gate">
      <input id="simTool" placeholder="Tool ID, optional">
      <button onclick="simulateFromCockpit()">Simulate</button>
    </div>

    <div style="display:grid; grid-template-columns:1fr 220px 1fr auto; gap:10px; margin-bottom:10px;">
      <input id="reqAction" placeholder="Approval request action">
      <input id="reqTool" placeholder="Tool ID, optional">
      <input id="reqReason" placeholder="Reason">
      <button onclick="requestFromCockpit()">Queue Approval</button>
    </div>

    <div style="display:grid; grid-template-columns:160px 1fr 1fr 90px auto; gap:10px; margin-bottom:10px;">
      <input id="worldType" placeholder="type" value="companion">
      <input id="worldTitle" placeholder="World event title">
      <input id="worldNote" placeholder="Note">
      <input id="worldImportance" placeholder="1-5" value="3">
      <button onclick="worldEventFromCockpit()">World Event</button>
    </div>

    <pre id="actionlog">No cockpit action yet.</pre>
  </section>

</main>

<script>
function row(k,v) {{
  return `<div class="metric"><span>${{k}}</span><strong>${{v}}</strong></div>`;
}}

function badges(items) {{
  if(!items || items.length === 0) return '<span class="badge">none</span>';
  return items.slice(0,8).map(x => `<span class="badge">${{x}}</span>`).join('');
}}

async function refresh() {{
  const res = await fetch('/api/state');
  const data = await res.json();
  const s = data.state;
  const world = s.world || {{}};
  const garden = (world.memory_garden || {{}});
  const avatar = data.avatar || (s.presence ? s.presence.avatar : {{}}) || {{}};
  const voice = data.voice || {{}};

  document.getElementById('subtitle').innerText = s.mission || 'Companion OS Alpha';

  document.getElementById('world').innerHTML =
    `<strong>${{world.current_place}}</strong><br>` +
    `Season: ${{world.season}}<br>` +
    `Weather: ${{world.weather}}<br>` +
    `Symbol: ${{world.mood_symbol}}<br><br>` +
    badges(world.unlocked_places || []);

  document.getElementById('v2').innerHTML =
    row('Score', `${{data.v2.score}} / ${{data.v2.target}}`) +
    row('Ready', data.v2.is_ready) +
    row('Blockers', (data.v2.blockers || []).length);

  document.getElementById('garden').innerHTML =
    row('Seeds', garden.seeds || 0) +
    row('Trees', garden.trees || 0) +
    row('Stones', garden.stones || 0) +
    row('Lights', garden.lights || 0) +
    row('Artifacts', (garden.artifacts || []).length);

  document.getElementById('presence').innerHTML =
    row('Mode', s.presence ? s.presence.mode : 'unknown') +
    row('Attention', s.presence ? s.presence.attention : 'unknown') +
    row('Avatar', `${{avatar.state || 'unknown'}} / ${{avatar.expression || 'unknown'}}`) +
    row('Voice', `${{voice.enabled}} / ${{voice.tts_backend || 'unknown'}}`);

  document.getElementById('trust').innerHTML =
    row('Emergency', s.trust ? s.trust.emergency_stop : 'unknown') +
    row('Rules', s.trust ? s.trust.guardian_rules.length : 0) +
    row('Permission traces', s.trust ? s.trust.permission_traces.length : 0);

  document.getElementById('systems').innerHTML =
    row('Tools', data.tools ? data.tools.length : 0) +
    row('Commands', data.commands ? data.commands.length : 0) +
    row('Documents', data.documents ? data.documents.documents.length : 0) +
    row('Workflows', data.workflows ? data.workflows.length : 0) +
    row('Release drafts', data.release ? data.release.drafts.length : 0);

  document.getElementById('events').innerText =
    (data.events || []).map(e => `${{e.created_at}} — ${{e.type}}: ${{e.title}}`).join('\\n');

  document.getElementById('traces').innerHTML =
    row('Total', data.trace_stats ? data.trace_stats.total : 0) +
    row('Recent shown', data.traces ? data.traces.length : 0);
}}

async function sendChat() {{
  const input = document.getElementById('chatinput');
  const msg = input.value.trim();
  if(!msg) return;

  const log = document.getElementById('chatlog');
  log.innerHTML += `<div><strong>User:</strong> ${{msg}}</div>`;
  input.value = '';

  const res = await fetch('/api/chat', {{
    method:'POST',
    headers:{{'Content-Type':'application/json'}},
    body:JSON.stringify({{message:msg}})
  }});

  const data = await res.json();
  log.innerHTML += `<div style="margin-top:8px"><strong>Seed:</strong> ${{data.response}}</div>`;
  log.scrollTop = log.scrollHeight;
}}


async function runAction(action_id, payload) {{
  const log = document.getElementById('actionlog');
  log.innerText = 'Running ' + action_id + '...';

  const res = await fetch('/api/cockpit/action', {{
    method:'POST',
    headers:{{'Content-Type':'application/json'}},
    body:JSON.stringify({{action_id:action_id, payload:payload || {{}}}})
  }});

  const data = await res.json();
  log.innerText = JSON.stringify(data, null, 2);
  refresh();
}}

function simulateFromCockpit() {{
  runAction('agency_simulate', {{
    action_text: document.getElementById('simAction').value,
    tool_id: document.getElementById('simTool').value
  }});
}}

function requestFromCockpit() {{
  runAction('agency_request', {{
    action_text: document.getElementById('reqAction').value,
    tool_id: document.getElementById('reqTool').value,
    reason: document.getElementById('reqReason').value
  }});
}}

function worldEventFromCockpit() {{
  runAction('world_event', {{
    event_type: document.getElementById('worldType').value,
    title: document.getElementById('worldTitle').value,
    note: document.getElementById('worldNote').value,
    importance: document.getElementById('worldImportance').value
  }});
}}

refresh();
setInterval(refresh, {refresh_ms});
</script>
</body>
</html>
"""


if __name__ == "__main__":
    run_companion_cockpit()
