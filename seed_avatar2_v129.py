import json, os, signal, subprocess, sys
from datetime import datetime
from pathlib import Path
from http.server import BaseHTTPRequestHandler, HTTPServer
from urllib.parse import urlparse
PID=Path("seed_avatar2_v129.pid"); LOG=Path("seed_avatar2_v129.log"); PORT=8799
def now(): return datetime.now().isoformat(timespec="seconds")
def state():
    alerts=[]; mood="idle"; health=100; pending=0; proactive_alive=False
    try:
        import seed_action_approval_v107 as a
        pending=a.status().get("pending_count",0)
        if pending: alerts.append(f"{pending} approval"); mood="needs approval"; health-=8
    except Exception: health-=8
    try:
        import seed_proactive_rhythm_v108 as p
        ps=p.status(); proactive_alive=bool(ps.get("alive"))
        if proactive_alive and mood=="idle": mood="present"
        if ps.get("decision_now",{}).get("should_ask"): alerts.append("curious"); mood="curious" if mood=="idle" else mood
    except Exception: pass
    try:
        import seed_v123_130_systems as s
        if not s.status().get("ok"): alerts.append("system check"); health-=10
    except Exception: pass
    return {"created_at":now(),"version":"v129.1-ui","ok":True,"mood":mood,"health":max(0,health),"pending":pending,"proactive_alive":proactive_alive,"alerts":alerts}
HTML = r'''
<!doctype html><html><head><meta charset="utf-8"><title>Seed Avatar</title><meta name="viewport" content="width=device-width,initial-scale=1">
<style>
:root{--text:#f5f2ee;--muted:#a6a7aa;--orange:#ff8a23}
*{box-sizing:border-box}body{margin:0;min-height:100vh;background:radial-gradient(circle at 50% 34%,rgba(255,138,35,.26),transparent 28%),#050505;color:var(--text);font-family:-apple-system,BlinkMacSystemFont,"SF Pro Display","Segoe UI",sans-serif;overflow:hidden}
.wrap{min-height:100vh;display:grid;place-items:center;padding:28px}.card{width:min(560px,92vw);border:1px solid rgba(255,255,255,.13);border-radius:34px;background:rgba(13,14,17,.68);backdrop-filter:blur(26px);box-shadow:0 35px 120px rgba(0,0,0,.55);padding:30px;text-align:center}
.orbit{position:relative;width:250px;height:250px;margin:10px auto 22px;display:grid;place-items:center}.ring{position:absolute;border:1px solid rgba(255,138,35,.36);border-radius:50%;inset:0;animation:spin 18s linear infinite}.ring:nth-child(2){inset:22px;border-color:rgba(115,245,157,.24);animation-duration:12s;animation-direction:reverse}.ring:nth-child(3){inset:44px;border-color:rgba(255,255,255,.12);animation-duration:24s}
.orb{width:142px;height:142px;border-radius:50%;background:radial-gradient(circle at 35% 25%,#fff2df 0,#ffb36b 25%,#ff8a23 52%,#4b1800 100%);box-shadow:0 0 80px rgba(255,138,35,.48),inset -18px -22px 45px rgba(0,0,0,.32);animation:breathe 3.2s ease-in-out infinite;position:relative;z-index:2}
@keyframes breathe{50%{transform:scale(1.07);box-shadow:0 0 110px rgba(255,138,35,.62),inset -18px -22px 45px rgba(0,0,0,.32)}}@keyframes spin{to{transform:rotate(360deg)}}h1{font-size:44px;line-height:1;margin:0 0 8px;letter-spacing:-.05em}#mood{font-size:18px;color:var(--orange);font-weight:800;text-transform:uppercase;letter-spacing:.14em}
.meta{display:grid;grid-template-columns:repeat(3,1fr);gap:10px;margin-top:22px}.box{border:1px solid rgba(255,255,255,.10);background:#0b0c0f;border-radius:18px;padding:14px}.box div:first-child{font-size:12px;color:var(--muted)}.box div:last-child{font-size:22px;font-weight:800;margin-top:4px}.alerts{display:flex;justify-content:center;gap:8px;flex-wrap:wrap;margin-top:18px}.pill{border:1px solid rgba(255,138,35,.32);background:rgba(255,138,35,.12);color:#ffc591;border-radius:999px;padding:7px 10px;font-size:13px}.actions{display:flex;gap:10px;justify-content:center;flex-wrap:wrap;margin-top:22px}button{background:#15171b;color:#eee;border:1px solid #2d3139;border-radius:13px;padding:10px 13px;cursor:pointer}.footer{color:var(--muted);font-size:12px;margin-top:18px}
</style></head><body><div class="wrap"><div class="card"><div class="orbit"><div class="ring"></div><div class="ring"></div><div class="ring"></div><div class="orb"></div></div><h1>Seed</h1><div id="mood">loading</div><div class="alerts" id="alerts"></div><div class="meta"><div class="box"><div>Health</div><div id="health">—</div></div><div class="box"><div>Approvals</div><div id="pending">—</div></div><div class="box"><div>Proactive</div><div id="proactive">—</div></div></div><div class="actions"><button onclick="openUrl(8806)">Dashboard</button><button onclick="refresh()">Refresh</button><button onclick="copy('python seed_avatar2_v129.py stop')">Copy Stop</button></div><div class="footer" id="stamp">—</div></div></div>
<script>
function copy(x){navigator.clipboard?.writeText(x)}function openUrl(port){location.href='http://127.0.0.1:'+port+'/'}async function refresh(){const d=await(await fetch('/state?ts='+Date.now())).json();mood.textContent=d.mood;health.textContent=d.health+'%';pending.textContent=d.pending;proactive.textContent=d.proactive_alive?'ON':'OFF';stamp.textContent=d.created_at;alerts.innerHTML=(d.alerts.length?d.alerts:['quiet']).map(a=>`<span class="pill">${a}</span>`).join('');document.querySelector('.orb').style.filter=d.mood.includes('approval')?'hue-rotate(-25deg) saturate(1.25)':'none'}refresh();setInterval(refresh,2000)
</script></body></html>
'''
class H(BaseHTTPRequestHandler):
    def _send(self,code,body,ctype):
        if isinstance(body,str): body=body.encode("utf-8")
        self.send_response(code); self.send_header("Content-Type",ctype); self.send_header("Cache-Control","no-store"); self.send_header("Content-Length",str(len(body))); self.end_headers(); self.wfile.write(body)
    def do_GET(self):
        path=urlparse(self.path).path
        if path.startswith("/state"): self._send(200,json.dumps(state(),ensure_ascii=False),"application/json; charset=utf-8")
        else: self._send(200,HTML,"text/html; charset=utf-8")
    def log_message(self,*args): return
def alive(pid):
    try: os.kill(int(pid),0); return True
    except Exception: return False
def serve(): HTTPServer(("127.0.0.1",PORT),H).serve_forever()
def start():
    if PID.exists():
        try:
            pid=int(PID.read_text())
            if alive(pid):
                subprocess.Popen(["open",f"http://127.0.0.1:{PORT}/?v=1291"])
                return {"ok":True,"already_running":True,"pid":pid,"url":f"http://127.0.0.1:{PORT}/"}
        except Exception: pass
    p=subprocess.Popen([sys.executable,"seed_avatar2_v129.py","serve"],stdout=LOG.open("a"),stderr=LOG.open("a")); PID.write_text(str(p.pid)); subprocess.Popen(["open",f"http://127.0.0.1:{PORT}/?v=1291"]); return {"ok":True,"pid":p.pid,"url":f"http://127.0.0.1:{PORT}/"}
def stop():
    pid=None; stopped=False
    if PID.exists():
        try:
            pid=int(PID.read_text())
            if alive(pid): os.kill(pid,signal.SIGTERM); stopped=True
            PID.unlink(missing_ok=True)
        except Exception: pass
    return {"ok":True,"stopped":stopped,"pid":pid}
def status():
    pid=None; al=False
    if PID.exists():
        try: pid=int(PID.read_text()); al=alive(pid)
        except Exception: pass
    return {"created_at":now(),"version":"v129.1-ui","ok":True,"alive":al,"pid":pid,"url":f"http://127.0.0.1:{PORT}/","state":state()}
if __name__=="__main__":
    a=sys.argv[1] if len(sys.argv)>1 else "status"
    if a=="serve": serve()
    elif a=="start": print(json.dumps(start(),indent=4,ensure_ascii=False))
    elif a=="stop": print(json.dumps(stop(),indent=4,ensure_ascii=False))
    else: print(json.dumps(status(),indent=4,ensure_ascii=False))
