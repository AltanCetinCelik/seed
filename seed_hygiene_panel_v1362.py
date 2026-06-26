import json, os, signal, subprocess, sys
from http.server import BaseHTTPRequestHandler, HTTPServer
from pathlib import Path
from urllib.parse import urlparse
from datetime import datetime
PID=Path("seed_hygiene_panel_v1362.pid"); LOG=Path("seed_hygiene_panel_v1362.log"); PORT=8818
HTML="""<!doctype html><html><head><meta charset='utf-8'><title>Seed Hygiene Center v136.2</title><style>body{margin:0;background:radial-gradient(circle at 15% 0%,rgba(255,138,35,.18),transparent 34%),#050505;color:#f4f4f2;font-family:-apple-system,BlinkMacSystemFont,Segoe UI,sans-serif}.wrap{max-width:1180px;margin:0 auto;padding:28px}.hero,.card{background:#111318;border:1px solid #2a2d33;border-radius:24px;padding:22px;margin:14px 0}.title{font-size:42px;font-weight:850;letter-spacing:-.05em}.muted{color:#a3a7ad}.grid{display:grid;grid-template-columns:repeat(auto-fit,minmax(270px,1fr));gap:14px}.score{font-size:56px;font-weight:900;color:#72f59c}button{background:#ff8a23;color:#111;border:0;border-radius:13px;padding:12px 15px;font-weight:850;margin:5px;cursor:pointer}.secondary{background:#1a1d22;color:#f4f4f2;border:1px solid #2a2d33}pre{white-space:pre-wrap;word-break:break-word;background:#08090b;border:1px solid #24272e;border-radius:14px;padding:12px;max-height:520px;overflow:auto}</style></head><body><div class='wrap'><div class='hero'><div class='muted'>Local Companion OS</div><div class='title'>Seed Hygiene Center v136.2</div><p class='muted'>Clean runtime state before always-on wake.</p><button onclick='api("scan")'>Scan</button><button onclick='api("snapshot")'>Snapshot</button><button onclick='api("apply-safe")'>Apply Safe</button></div><div class='grid'><div class='card'><div class='muted'>Hygiene Score</div><div id='score' class='score'>—</div><div id='grade' class='muted'>loading</div></div><div class='card'><div class='muted'>Runtime</div><pre id='runtime'>loading</pre></div><div class='card'><div class='muted'>Known Dirt</div><pre id='dirt'>loading</pre></div></div><div class='card'><h3>Full Scan</h3><pre id='raw'>loading</pre></div></div><script>async function api(x){let j=await(await fetch('/api/'+x)).json();await refresh();alert(JSON.stringify(j,null,2).slice(0,1000))}async function refresh(){let j=await(await fetch('/api/scan?'+Date.now())).json();score.textContent=(j.hygiene&&j.hygiene.score)||'—';grade.textContent=(j.hygiene&&j.hygiene.grade)+' · '+((j.hygiene&&j.hygiene.reasons)||[]).join(', ');runtime.textContent=JSON.stringify(j.runtime,null,2);dirt.textContent=JSON.stringify(j.suggestions||[],null,2);raw.textContent=JSON.stringify(j,null,2)}refresh();setInterval(refresh,4000)</script></body></html>"""
def now(): return datetime.now().isoformat(timespec="seconds")
def alive(pid):
    try: os.kill(int(pid),0); return True
    except Exception: return False
class H(BaseHTTPRequestHandler):
    def send_json(self,o):
        b=json.dumps(o,ensure_ascii=False).encode(); self.send_response(200); self.send_header("Content-Type","application/json"); self.end_headers(); self.wfile.write(b)
    def do_GET(self):
        p=urlparse(self.path).path
        try:
            import seed_hygiene_center_v1362 as h
            if p=="/api/scan": self.send_json(h.scan())
            elif p=="/api/snapshot": self.send_json(h.snapshot())
            elif p=="/api/apply-safe": self.send_json(h.apply_safe())
            else:
                b=HTML.encode(); self.send_response(200); self.send_header("Content-Type","text/html"); self.end_headers(); self.wfile.write(b)
        except Exception as e: self.send_json({"ok":False,"error":str(e)})
    def log_message(self,*a): return
def serve(): HTTPServer(("127.0.0.1",8818),H).serve_forever()
def start():
    if PID.exists():
        try:
            pid=int(PID.read_text().strip())
            if alive(pid): subprocess.Popen(["open","http://127.0.0.1:8818/"]); return {"ok":True,"already_running":True,"pid":pid,"url":"http://127.0.0.1:8818/"}
        except Exception: pass
    p=subprocess.Popen([sys.executable,"seed_hygiene_panel_v1362.py","serve"],stdout=LOG.open("a"),stderr=LOG.open("a")); PID.write_text(str(p.pid)); subprocess.Popen(["open","http://127.0.0.1:8818/"]); return {"ok":True,"pid":p.pid,"url":"http://127.0.0.1:8818/"}
def stop():
    pid=None; stopped=False
    if PID.exists():
        try:
            pid=int(PID.read_text().strip())
            if alive(pid): os.kill(pid,signal.SIGTERM); stopped=True
            PID.unlink(missing_ok=True)
        except Exception: pass
    return {"ok":True,"stopped":stopped,"pid":pid}
def status():
    pid=None; al=False
    if PID.exists():
        try: pid=int(PID.read_text().strip()); al=alive(pid)
        except Exception: pass
    return {"created_at":now(),"version":"v136.2.0","ok":True,"alive":al,"pid":pid,"url":"http://127.0.0.1:8818/"}
if __name__=="__main__":
    a=sys.argv[1] if len(sys.argv)>1 else "status"
    if a=="serve": serve()
    elif a=="start": print(json.dumps(start(),indent=4,ensure_ascii=False))
    elif a=="stop": print(json.dumps(stop(),indent=4,ensure_ascii=False))
    else: print(json.dumps(status(),indent=4,ensure_ascii=False))
