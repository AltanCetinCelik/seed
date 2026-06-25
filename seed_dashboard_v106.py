import json
import os
import signal
import subprocess
import sys
from datetime import datetime
from http.server import BaseHTTPRequestHandler, HTTPServer
from pathlib import Path
from urllib.parse import urlparse, parse_qs

PID = Path("seed_dashboard_v106.pid")
LOG = Path("seed_dashboard_v106.log")
PORT = 8806

def now():
    return datetime.now().isoformat(timespec="seconds")

def module_call(title, module, fn):
    try:
        m = __import__(module, fromlist=[fn])
        data = getattr(m, fn)()
        ok = bool(data.get("ok", True))
        return {"title": title, "ok": ok, "data": data}
    except Exception as e:
        return {"title": title, "ok": False, "error": str(e), "data": {"ok": False, "error": str(e)}}

def gather():
    cards = [
        module_call("Supervisor OS", "seed_supervisor_v92", "supervisor_status"),
        module_call("Wake Engine", "seed_wake_engine_v93", "status"),
        module_call("Wake Reliability", "seed_wake_reliability_v107", "status"),
        module_call("Safety Ledger", "seed_safety_ledger_v94", "status"),
        module_call("Action Approval", "seed_action_approval_v107", "status"),
        module_call("Trace / Errors", "seed_trace_v95", "status"),
        module_call("Memory Garden 2", "seed_memory_garden2_v96", "status"),
        module_call("Tool Bridge", "seed_tool_bridge_v97", "status"),
        module_call("Vision", "seed_vision_v98", "status"),
        module_call("Tasks", "seed_tasks_v99", "status"),
        module_call("Operator", "seed_operator_v100", "status"),
        module_call("Coder", "seed_coder_v101", "status"),
        module_call("Voice", "seed_voice_v102", "status"),
        module_call("Devices", "seed_device_body_v103", "status"),
        module_call("Private RAG", "seed_private_rag_v104", "status"),
        module_call("Doctor", "seed_doctor_v105", "diagnose"),
    ]
    ok_count = sum(1 for c in cards if c["ok"])
    return {"created_at": now(), "version": "v106.3.0", "ok": ok_count >= 12, "ok_count": ok_count, "total": len(cards), "cards": cards}

def summarize_card(card):
    data = card.get("data") or {}
    title = card.get("title", "")
    if title == "Supervisor OS":
        return f"{data.get('ok_count', '?')}/{data.get('total', '?')} subsystem cards · {data.get('mode', 'unknown')}"
    if title == "Wake Engine":
        return f"Chosen: {data.get('chosen', 'unknown')}"
    if title == "Wake Reliability":
        return "Wake mishear library active"
    if title == "Safety Ledger":
        settings = data.get("settings", {})
        return f"Risky approval required: {settings.get('require_approval_risky', True)}"
    if title == "Action Approval":
        return f"Pending approvals: {data.get('pending_count', 0)}"
    if title == "Trace / Errors":
        return f"Trace {data.get('trace', 0)} · Errors {data.get('errors', 0)} · Actions {data.get('actions', 0)}"
    if title == "Memory Garden 2":
        return f"Base memories: {data.get('base_memories', 0)}"
    if title == "Tool Bridge":
        return f"{len(data.get('tools', {}))} registered tools"
    if title == "Vision":
        return "Vision note-only with stale self-test cleanup"
    if title == "Tasks":
        return f"Open tasks: {len(data.get('open', data.get('tasks', [])))}"
    if title == "Operator":
        return "Mac actions gated by safety ledger"
    if title == "Coder":
        return f"Aider: {'found' if data.get('aider') else 'not found'}"
    if title == "Voice":
        s = data.get("settings", {})
        return f"Mode {s.get('mode', 'normal')} · rate {s.get('rate', '?')}"
    if title == "Devices":
        return f"{len(data.get('devices', {}))} device(s)"
    if title == "Private RAG":
        return f"Indexed files: {data.get('indexed', 0)}"
    if title == "Doctor":
        bad = [k for k, v in (data.get("checks", {}) or {}).items() if not v.get("ok") and v.get("required", True)]
        return "Required checks green" if not bad else "Needs attention: " + ", ".join(bad)
    return "Ready" if card.get("ok") else "Needs attention"

def view_model():
    data = gather()
    for card in data["cards"]:
        card["summary"] = summarize_card(card)
    return data

HTML = '''<!doctype html>
<html>
<head>
<meta charset="utf-8">
<title>Seed Dashboard v106.3</title>
<meta name="viewport" content="width=device-width, initial-scale=1">
<style>
:root{--bg:#080808;--panel:#141414;--text:#f4f4f4;--muted:#a9a9a9;--orange:#ff8a23;--green:#65e88a;--red:#ff5d5d;--line:#2d2d2d}
*{box-sizing:border-box}
body{margin:0;background:radial-gradient(circle at top left,#201103,#080808 42%);color:var(--text);font-family:-apple-system,BlinkMacSystemFont,"SF Pro Display","Segoe UI",sans-serif}
header{padding:28px 34px;border-bottom:1px solid var(--line);display:flex;align-items:center;justify-content:space-between;gap:18px;background:rgba(10,10,10,.72);backdrop-filter:blur(18px);position:sticky;top:0;z-index:10}
.brand{display:flex;align-items:center;gap:15px}
.orb{width:42px;height:42px;border-radius:50%;background:radial-gradient(circle at 35% 25%,#ffe0b6,#ff8a23 45%,#612400);box-shadow:0 0 36px rgba(255,138,35,.35);animation:pulse 3s ease-in-out infinite}
@keyframes pulse{0%,100%{transform:scale(1)}50%{transform:scale(1.07)}}
h1{font-size:27px;margin:0}.sub{color:var(--muted);font-size:13px;margin-top:3px}
.badge{border:1px solid var(--line);border-radius:999px;padding:8px 12px;background:#111;color:var(--muted);font-size:13px}
main{padding:28px 34px 48px}
.hero{display:grid;grid-template-columns:1.2fr .8fr;gap:18px;margin-bottom:18px}
.box{background:linear-gradient(180deg,var(--panel),#101010);border:1px solid var(--line);border-radius:22px;padding:20px;box-shadow:0 20px 70px rgba(0,0,0,.35)}
.big{font-size:42px;font-weight:800;margin:8px 0}.muted{color:var(--muted)}
.grid{display:grid;grid-template-columns:repeat(auto-fill,minmax(280px,1fr));gap:16px}
.card{background:var(--panel);border:1px solid var(--line);border-radius:18px;padding:17px;transition:.16s transform,.16s border-color}
.card:hover{transform:translateY(-2px);border-color:#4a4a4a}
.cardTop{display:flex;justify-content:space-between;align-items:start;gap:12px}
.title{font-weight:750;font-size:17px}.status{font-size:12px;border-radius:999px;padding:5px 9px}
.ok{color:#101;background:var(--green)}.bad{color:#180000;background:var(--red)}
.summary{color:var(--muted);font-size:13px;line-height:1.35;margin:10px 0 14px;min-height:36px}
details{border-top:1px solid var(--line);padding-top:10px}
summary{cursor:pointer;color:var(--orange);font-size:13px}
pre{white-space:pre-wrap;word-break:break-word;color:#d8d8d8;background:#0b0b0b;border:1px solid #262626;border-radius:12px;padding:12px;max-height:260px;overflow:auto;font-size:12px}
button{background:#1d1d1d;border:1px solid #333;color:#eee;border-radius:11px;padding:9px 12px;cursor:pointer}
button:hover{border-color:var(--orange)}
.approval{border:1px solid #3a2a16;background:#130d07;border-radius:14px;padding:10px;margin-top:10px}
@media(max-width:850px){.hero{grid-template-columns:1fr}header{align-items:flex-start;flex-direction:column}}
</style>
</head>
<body>
<header>
  <div class="brand"><div class="orb"></div><div><h1>Seed Dashboard</h1><div class="sub">v106.3 · Hardening / Approval / Eval / Wake Reliability</div></div></div>
  <div style="display:flex;gap:10px;align-items:center;flex-wrap:wrap"><button onclick="refresh()">Refresh</button><span id="stamp" class="badge">loading…</span></div>
</header>
<main>
  <section class="hero">
    <div class="box"><div class="muted">System health</div><div id="score" class="big">—</div><div id="summary" class="muted">Reading Seed state…</div></div>
    <div class="box"><div class="muted">Quick commands</div><pre>python seed_mega_v92_106.py start
python seed_mega_v92_106.py stop
python seed_eval_v107.py
python seed_v107_hardening_gate.py</pre></div>
  </section>
  <section id="approvals" class="box" style="margin-bottom:18px"></section>
  <section id="grid" class="grid"></section>
</main>
<script>
function esc(x){return String(x ?? '').replace(/[&<>"']/g,m=>({"&":"&amp;","<":"&lt;",">":"&gt;","\\"":"&quot;","'":"&#039;"}[m]))}
async function approve(id){await fetch('/api/approve?id='+encodeURIComponent(id)); refresh()}
async function refresh(){
  const res = await fetch('/api/status?ts=' + Date.now());
  const data = await res.json();
  document.getElementById('stamp').textContent = data.created_at;
  document.getElementById('score').textContent = data.ok_count + '/' + data.total + ' green';
  document.getElementById('summary').textContent = data.ok ? 'Seed hardening layer is healthy.' : 'Some modules need attention. Open details below.';
  const approvalCard = data.cards.find(c => c.title === 'Action Approval');
  const pending = ((approvalCard||{}).data||{}).pending || [];
  document.getElementById('approvals').innerHTML = '<h2 style="margin-top:0">Approval Center</h2>' + (pending.length ? pending.map(p=>`
    <div class="approval">
      <b>${esc(p.action)}</b><br><span class="muted">${esc((p.classification||{}).reason || '')}</span>
      <pre>${esc(JSON.stringify(p,null,2))}</pre>
      <button onclick="approve('${esc(p.request_id)}')">Mark approved</button>
    </div>`).join('') : '<div class="muted">No pending risky approvals.</div>');
  document.getElementById('grid').innerHTML = data.cards.map(c => `
    <article class="card"><div class="cardTop"><div class="title">${esc(c.title)}</div><div class="status ${c.ok ? 'ok' : 'bad'}">${c.ok ? 'OK' : 'CHECK'}</div></div>
    <div class="summary">${esc(c.summary || '')}</div><details><summary>details</summary><pre>${esc(JSON.stringify(c.data || c.error || {}, null, 2))}</pre></details></article>`).join('');
}
refresh(); setInterval(refresh, 4000);
</script>
</body>
</html>'''

class Handler(BaseHTTPRequestHandler):
    def send_bytes(self, code, body, ctype):
        if isinstance(body, str):
            body = body.encode("utf-8")
        self.send_response(code)
        self.send_header("Content-Type", ctype)
        self.send_header("Cache-Control", "no-store, no-cache, must-revalidate, max-age=0")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)
    def do_GET(self):
        u = urlparse(self.path)
        if u.path in ["/api/status", "/status"]:
            self.send_bytes(200, json.dumps(view_model(), ensure_ascii=False), "application/json; charset=utf-8")
        elif u.path == "/api/approve":
            rid = (parse_qs(u.query).get("id") or [""])[0]
            try:
                from seed_action_approval_v107 import approve
                result = approve(rid, "approved_from_dashboard")
            except Exception as e:
                result = {"ok": False, "error": str(e)}
            self.send_bytes(200, json.dumps(result, ensure_ascii=False), "application/json; charset=utf-8")
        elif u.path in ["/", "/dashboard", "/index.html"]:
            self.send_bytes(200, HTML, "text/html; charset=utf-8")
        elif u.path == "/health":
            self.send_bytes(200, json.dumps({"ok": True, "version": "v106.3.0"}), "application/json; charset=utf-8")
        else:
            self.send_bytes(404, "not found", "text/plain; charset=utf-8")
    def log_message(self, *args):
        return

def serve():
    print(f"Seed dashboard v106.3: http://127.0.0.1:{PORT}/")
    HTTPServer(("127.0.0.1", PORT), Handler).serve_forever()

def alive(pid):
    try:
        os.kill(int(pid), 0)
        return True
    except Exception:
        return False

def start():
    if PID.exists():
        try:
            pid = int(PID.read_text().strip())
            if alive(pid):
                subprocess.Popen(["open", f"http://127.0.0.1:{PORT}/?v=1063"])
                return {"ok": True, "already_running": True, "pid": pid, "url": f"http://127.0.0.1:{PORT}/"}
        except Exception:
            pass
    log = LOG.open("a")
    proc = subprocess.Popen([sys.executable, "seed_dashboard_v106.py", "serve"], stdout=log, stderr=log)
    PID.write_text(str(proc.pid))
    subprocess.Popen(["open", f"http://127.0.0.1:{PORT}/?v=1063"])
    return {"ok": True, "pid": proc.pid, "url": f"http://127.0.0.1:{PORT}/"}

def stop():
    pid = None
    stopped = False
    if PID.exists():
        try:
            pid = int(PID.read_text().strip())
            if alive(pid):
                os.kill(pid, signal.SIGTERM)
                stopped = True
            PID.unlink(missing_ok=True)
        except Exception:
            pass
    return {"ok": True, "stopped": stopped, "pid": pid}

def status():
    return {"created_at": now(), "version": "v106.3.0", "ok": True, "alive": PID.exists(), "url": f"http://127.0.0.1:{PORT}/"}

if __name__ == "__main__":
    arg = sys.argv[1] if len(sys.argv) > 1 else "status"
    if arg == "serve":
        serve()
    elif arg == "start":
        print(json.dumps(start(), indent=4, ensure_ascii=False))
    elif arg == "stop":
        print(json.dumps(stop(), indent=4, ensure_ascii=False))
    elif arg == "raw":
        print(json.dumps(view_model(), indent=4, ensure_ascii=False))
    else:
        print(json.dumps(status(), indent=4, ensure_ascii=False))
