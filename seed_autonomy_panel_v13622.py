import json, os, signal, subprocess, sys
from http.server import BaseHTTPRequestHandler, HTTPServer
from pathlib import Path
from urllib.parse import urlparse, parse_qs
from datetime import datetime

PID = Path("seed_autonomy_panel_v13622.pid")
LOG = Path("seed_autonomy_panel_v13622.log")
PORT = 8820

HTML = """<!doctype html><html><head><meta charset='utf-8'><title>Seed Autonomy v136.2.2</title><meta name='viewport' content='width=device-width,initial-scale=1'><style>
body{margin:0;background:radial-gradient(circle at 10% 0%,rgba(255,138,35,.22),transparent 35%),#050505;color:#f4f4f2;font-family:-apple-system,BlinkMacSystemFont,Segoe UI,sans-serif}.wrap{max-width:1180px;margin:0 auto;padding:28px}.hero,.card{background:#111318;border:1px solid #2a2d33;border-radius:24px;padding:22px;margin:14px 0}.title{font-size:42px;font-weight:850;letter-spacing:-.05em}.muted{color:#a3a7ad}.grid{display:grid;grid-template-columns:repeat(auto-fit,minmax(300px,1fr));gap:14px}button{background:#ff8a23;color:#111;border:0;border-radius:13px;padding:12px 15px;font-weight:850;margin:5px;cursor:pointer}.secondary{background:#1a1d22;color:#f4f4f2;border:1px solid #2a2d33}input{background:#08090b;color:#f4f4f2;border:1px solid #2a2d33;border-radius:12px;padding:12px;width:65%}pre{white-space:pre-wrap;word-break:break-word;background:#08090b;border:1px solid #24272e;border-radius:14px;padding:12px;max-height:560px;overflow:auto}.big{font-size:36px;font-weight:900;color:#72f59c}</style></head><body><div class='wrap'><div class='hero'><div class='muted'>Local Companion OS</div><div class='title'>Seed Autonomy v136.2.2</div><p class='muted'>Less approvals. Not zero safety.</p><button onclick='api("mode/trusted_local")'>Trusted Local</button><button onclick='api("mode/operator_light")'>Operator Light</button><button class='secondary' onclick='api("mode/balanced")'>Balanced</button><button class='secondary' onclick='api("autopilot/start")'>Start Autopilot</button><button class='secondary' onclick='api("autopilot/once")'>Resolve Once</button></div><div class='card'><input id='grant' value='operator type'><button onclick='api("grant?pattern="+encodeURIComponent(grant.value))'>Grant 120 min</button></div><div class='grid'><div class='card'><div class='muted'>Mode</div><div id='mode' class='big'>—</div></div><div class='card'><div class='muted'>Pending</div><pre id='pending'>loading</pre></div></div><div class='card'><h3>Status</h3><pre id='raw'>loading</pre></div></div><script>
async function api(path){let j=await(await fetch('/api/'+path)).json();raw.textContent=JSON.stringify(j,null,2);await refresh();alert(JSON.stringify(j,null,2).slice(0,1000))}
async function refresh(){let j=await(await fetch('/api/status?'+Date.now())).json();raw.textContent=JSON.stringify(j,null,2);mode.textContent=(j.policy&&j.policy.mode)||'—';pending.textContent=JSON.stringify((j.autopilot&&j.autopilot.approval_status)||{},null,2)}
refresh();setInterval(refresh,4000)
</script></body></html>"""

def now():
    return datetime.now().isoformat(timespec="seconds")

def alive(pid):
    try:
        os.kill(int(pid), 0); return True
    except Exception: return False

class H(BaseHTTPRequestHandler):
    def send_json(self, obj):
        b=json.dumps(obj,ensure_ascii=False).encode()
        self.send_response(200); self.send_header("Content-Type","application/json"); self.end_headers(); self.wfile.write(b)
    def do_GET(self):
        p=urlparse(self.path); q=parse_qs(p.query)
        try:
            import seed_autonomy_policy_v13622 as pol
            import seed_approval_autopilot_v13622 as auto
            if p.path == "/api/status":
                self.send_json({"ok": True, "policy": pol.status(), "autopilot": auto.status()})
            elif p.path.startswith("/api/mode/"):
                self.send_json(pol.set_mode(p.path.rsplit("/",1)[-1]))
            elif p.path == "/api/grant":
                self.send_json(pol.grant((q.get("pattern") or ["operator type"])[0]))
            elif p.path == "/api/autopilot/start":
                self.send_json(auto.start())
            elif p.path == "/api/autopilot/stop":
                self.send_json(auto.stop())
            elif p.path == "/api/autopilot/once":
                self.send_json(auto.resolve_once(True))
            elif p.path == "/api/autopilot/dry-run":
                self.send_json(auto.resolve_once(False))
            else:
                b=HTML.encode(); self.send_response(200); self.send_header("Content-Type","text/html"); self.end_headers(); self.wfile.write(b)
        except Exception as e:
            self.send_json({"ok": False, "error": str(e)})
    def log_message(self,*a): return

def serve():
    HTTPServer(("127.0.0.1", PORT), H).serve_forever()

def start():
    if PID.exists():
        try:
            pid=int(PID.read_text().strip())
            if alive(pid):
                subprocess.Popen(["open", f"http://127.0.0.1:{PORT}/"])
                return {"ok": True, "already_running": True, "pid": pid, "url": f"http://127.0.0.1:{PORT}/"}
        except Exception: pass
    p=subprocess.Popen([sys.executable,"seed_autonomy_panel_v13622.py","serve"],stdout=LOG.open("a"),stderr=LOG.open("a"))
    PID.write_text(str(p.pid)); subprocess.Popen(["open", f"http://127.0.0.1:{PORT}/"])
    return {"ok": True, "pid": p.pid, "url": f"http://127.0.0.1:{PORT}/"}

def stop():
    pid=None; stopped=False
    if PID.exists():
        try:
            pid=int(PID.read_text().strip())
            if alive(pid): os.kill(pid, signal.SIGTERM); stopped=True
            PID.unlink(missing_ok=True)
        except Exception: pass
    return {"ok": True, "stopped": stopped, "pid": pid}

def status():
    pid=None; al=False
    if PID.exists():
        try: pid=int(PID.read_text().strip()); al=alive(pid)
        except Exception: pass
    return {"created_at": now(), "version": "v136.2.2", "ok": True, "alive": al, "pid": pid, "url": f"http://127.0.0.1:{PORT}/"}

if __name__ == "__main__":
    a=sys.argv[1] if len(sys.argv)>1 else "status"
    if a=="serve": serve()
    elif a=="start": print(json.dumps(start(),indent=4,ensure_ascii=False))
    elif a=="stop": print(json.dumps(stop(),indent=4,ensure_ascii=False))
    else: print(json.dumps(status(),indent=4,ensure_ascii=False))
