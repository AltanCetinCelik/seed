import json
import subprocess
import threading
from datetime import datetime
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

HOST = "127.0.0.1"
PORT = 8797

HTML = """<!doctype html><html><head><meta charset="utf-8"/><title>Seed v77 Panel 2.0</title>
<style>
body{margin:0;background:#0f1115;color:#f4f4f5;font-family:-apple-system,BlinkMacSystemFont,Segoe UI,sans-serif}
header{padding:16px 22px;border-bottom:1px solid #2a2f3a;display:flex;justify-content:space-between}
main{display:grid;grid-template-columns:360px 1fr 420px;gap:14px;padding:14px}
.card{background:#171a21;border:1px solid #2a2f3a;border-radius:18px;padding:16px}
.orb{width:150px;height:150px;border-radius:50%;background:#f97316;box-shadow:0 0 50px #f97316;margin:auto;display:flex;align-items:center;justify-content:center;font-size:56px}
textarea,input{width:100%;background:#0b0d12;color:#f4f4f5;border:1px solid #333847;border-radius:12px;padding:10px}
button{background:#272b35;color:#f4f4f5;border:1px solid #3b4252;border-radius:12px;padding:9px 11px;margin:4px;cursor:pointer}
button:hover{border-color:#f97316}.log{height:420px;overflow:auto;background:#0b0d12;border-radius:12px;padding:10px;white-space:pre-wrap}.item{border:1px solid #303542;border-radius:12px;padding:10px;margin:8px 0}.small{color:#a1a1aa;font-size:12px}
</style></head><body><header><b>Seed v77 Panel 2.0 / v81 stack</b><span id="version">loading</span></header><main>
<section class="card"><div class="orb" id="orb">●</div><h2 id="mood">Seed</h2><p id="reason" class="small"></p><button onclick="refresh()">Refresh</button><button onclick="speakPresence()">Speak presence</button></section>
<section class="card"><h2>Chat + Voice</h2><div class="log" id="log"></div><textarea id="msg" placeholder="Talk to Seed..."></textarea><button onclick="chat()">Send</button><button onclick="voice(8)">Voice 8s</button><button onclick="voice(12)">Voice 12s</button></section>
<section class="card"><h2>Systems</h2><button onclick="load('memory')">Memory</button><button onclick="load('assimilation')">Assimilation</button><button onclick="load('executor')">Executor</button><button onclick="load('aider')">Aider</button><button onclick="load('presence')">Presence</button><div id="side"></div></section>
</main><script>
async function j(p,o){let r=await fetch(p,o);return await r.json()}
function log(t){let e=document.getElementById('log');e.textContent+='\\n'+t+'\\n';e.scrollTop=e.scrollHeight}
async function refresh(){let s=await j('/api/state');document.getElementById('version').textContent=s.self?.true_current_version||'v81';document.getElementById('mood').textContent=(s.avatar?.mood||'steady')+' / '+(s.avatar?.mode||'idle');document.getElementById('reason').textContent=s.avatar?.reason||''}
async function chat(){let m=document.getElementById('msg').value;document.getElementById('msg').value='';log('You: '+m);let r=await j('/api/chat',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({message:m})});log('Seed: '+(r.reply||r.error||''));refresh()}
async function voice(sec){log('Recording '+sec+'s...');let r=await j('/api/voice',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({seconds:sec})});log('Transcript: '+(r.transcript||''));log('Seed: '+(r.reply||r.error||''));refresh()}
async function load(kind){let r=await j('/api/'+kind);document.getElementById('side').innerHTML='<pre class="small">'+JSON.stringify(r,null,2).slice(0,8000)+'</pre>'}
async function speakPresence(){let r=await j('/api/presence/speak',{method:'POST'});log('Presence: '+(r.spoken||r.error||''))}
refresh();setInterval(refresh,5000)
</script></body></html>"""

def now():
    return datetime.now().isoformat(timespec="seconds")

def state():
    self_state = {}
    avatar = {}
    try:
        from seed_self_state_v81 import build_self_state
        self_state = build_self_state()
    except Exception as e:
        self_state = {"ok": False, "error": str(e)}
    try:
        from seed_avatar_panel_v74 import build_avatar_panel_state
        avatar = build_avatar_panel_state()
    except Exception as e:
        avatar = {"ok": False, "error": str(e)}
    return {"created_at": now(), "version": "v77.0.0", "ok": True, "self": self_state, "avatar": avatar}

def chat(message):
    try:
        from seed_local_chat_v701 import choose_role, model_fallbacks, call_ollama
        role = choose_role(message)
        for model in model_fallbacks(role):
            reply = call_ollama(model, role, message)
            reply = (reply or "").strip()
            if reply and reply.lower() not in {"normal", "ok", "okay"}:
                return {"ok": True, "reply": reply, "model": model, "role": role}
        return {"ok": False, "error": "no valid reply"}
    except Exception as e:
        return {"ok": False, "error": str(e)}

class Handler(BaseHTTPRequestHandler):
    def send_json(self, data, code=200):
        self.send_response(code)
        self.send_header("Content-Type", "application/json")
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Headers", "Content-Type")
        self.end_headers()
        self.wfile.write(json.dumps(data, ensure_ascii=False).encode())

    def body(self):
        n = int(self.headers.get("Content-Length", "0") or "0")
        if not n:
            return {}
        try:
            return json.loads(self.rfile.read(n).decode())
        except Exception:
            return {}

    def do_OPTIONS(self):
        self.send_json({"ok": True})

    def do_GET(self):
        if self.path in {"/", "/panel"}:
            self.send_response(200); self.send_header("Content-Type", "text/html; charset=utf-8"); self.end_headers(); self.wfile.write(HTML.encode()); return
        if self.path == "/api/state": return self.send_json(state())
        if self.path == "/api/memory":
            from seed_memory_review_v75 import memory_summary
            return self.send_json(memory_summary())
        if self.path == "/api/assimilation":
            from seed_assimilation_v81 import build_backlog
            return self.send_json(build_backlog())
        if self.path == "/api/executor":
            from seed_permission_executor_v79 import executor_summary
            return self.send_json(executor_summary())
        if self.path == "/api/aider":
            from seed_aider_loop_v80 import aider_summary
            return self.send_json(aider_summary())
        if self.path == "/api/presence":
            from seed_proactive_v78 import enqueue_notices
            return self.send_json(enqueue_notices())
        return self.send_json({"ok": False, "error": "not found"}, 404)

    def do_POST(self):
        b = self.body()
        if self.path == "/api/chat": return self.send_json(chat(b.get("message", "")))
        if self.path == "/api/voice":
            from seed_voice_v76 import run_voice2_once
            return self.send_json(run_voice2_once(seconds=b.get("seconds", 8), speak=True))
        if self.path == "/api/presence/speak":
            from seed_proactive_v78 import speak_one
            return self.send_json(speak_one(force=True))
        return self.send_json({"ok": False, "error": "not found"}, 404)

    def log_message(self, fmt, *args):
        print("[v77]", fmt % args)

def run_panel(open_browser=True):
    url = f"http://{HOST}:{PORT}"
    print("\n=== SEED v77 PANEL 2.0 ===")
    print(f"Open: {url}")
    print("Press Ctrl+C to stop.")
    if open_browser:
        threading.Timer(0.8, lambda: subprocess.Popen(["open", url])).start()
    ThreadingHTTPServer((HOST, PORT), Handler).serve_forever()

if __name__ == "__main__":
    run_panel(True)
