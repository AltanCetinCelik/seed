import json, os, signal, subprocess, sys
from datetime import datetime
from http.server import BaseHTTPRequestHandler, HTTPServer
from pathlib import Path
from urllib.parse import urlparse

STATE_FILE=Path("seed_avatar_v89_state.json"); PID_FILE=Path("seed_avatar_v89.pid"); LOG_FILE=Path("seed_avatar_v89.log"); PORT_FILE=Path("seed_avatar_v89_port.txt")
PORT=8798
DEFAULT={"version":"v89.2.0","mode":"idle","emotion":"calm","message":"Seed is present.","hearing":False,"seeing":False,"thinking":False,"speaking":False,"last_note":None}

def now(): return datetime.now().isoformat(timespec="seconds")
def state():
    if STATE_FILE.exists():
        try:
            d=DEFAULT.copy(); d.update(json.loads(STATE_FILE.read_text(errors="ignore"))); d["version"]="v89.2.0"; return d
        except Exception: pass
    return DEFAULT.copy()
def set_avatar_state(**kw):
    d=state()
    # reset sensor flags unless explicitly provided
    if "mode" in kw and kw.get("mode") in {"idle","noting","curious"}:
        kw.setdefault("hearing", False); kw.setdefault("seeing", False); kw.setdefault("thinking", False); kw.setdefault("speaking", False)
    d.update({k:v for k,v in kw.items() if v is not None}); d["version"]="v89.2.0"; d["updated_at"]=now(); STATE_FILE.write_text(json.dumps(d,indent=4,ensure_ascii=False)); return d

HTML="""<!doctype html><html><head><meta charset='utf-8'><title>Seed Avatar</title><style>
body{margin:0;height:100vh;display:grid;place-items:center;background:radial-gradient(circle,#202020,#050505);color:#eee;font-family:-apple-system,BlinkMacSystemFont,sans-serif}
.card{width:420px;padding:28px;border:1px solid #333;border-radius:28px;background:rgba(20,20,20,.78);text-align:center;box-shadow:0 0 60px rgba(255,122,24,.12)}
.seed{width:190px;height:190px;margin:0 auto 22px;border-radius:50%;background:radial-gradient(circle at 35% 30%,#ffe0b4,#ff8a23 35%,#813900 82%);box-shadow:0 0 45px rgba(255,126,30,.42),inset 0 0 30px rgba(255,255,255,.18);animation:breathe 3s ease-in-out infinite;position:relative}
.seed:before,.seed:after{content:"";position:absolute;top:74px;width:18px;height:28px;border-radius:20px;background:rgba(20,20,20,.72)}.seed:before{left:62px}.seed:after{right:62px}
.seed.listening{box-shadow:0 0 70px rgba(70,180,255,.45)}.seed.seeing{box-shadow:0 0 70px rgba(120,255,170,.45)}.seed.thinking{animation-duration:1.1s}.seed.speaking{animation-duration:.75s}.seed.curious{transform:rotate(-2deg)}
@keyframes breathe{0%,100%{transform:scale(1)}50%{transform:scale(1.045)}}
h1{margin:0;font-size:34px}.mode{color:#ff9c3f;margin-top:8px;font-weight:700}.msg{margin-top:18px;min-height:48px;line-height:1.4}.badges{margin-top:18px;display:flex;gap:8px;justify-content:center;flex-wrap:wrap}.badge{border:1px solid #333;border-radius:999px;padding:6px 10px;font-size:12px;color:#aaa}.on{border-color:#ff8a23;color:#fff}.note{margin-top:18px;color:#aaa;font-size:12px}
</style></head><body><div class='card'><div id='seed' class='seed'></div><h1>Seed</h1><div id='mode' class='mode'></div><div id='msg' class='msg'></div><div class='badges'><span id='hearing' class='badge'>hearing</span><span id='seeing' class='badge'>seeing</span><span id='thinking' class='badge'>thinking</span><span id='speaking' class='badge'>speaking</span></div><div id='note' class='note'></div></div><script>
async function tick(){try{let s=await (await fetch('/state?x='+Date.now())).json();document.getElementById('seed').className='seed '+(s.mode||'idle');document.getElementById('mode').textContent=(s.mode||'idle')+' / '+(s.emotion||'calm');document.getElementById('msg').textContent=s.message||'Seed is present.';for(let k of ['hearing','seeing','thinking','speaking'])document.getElementById(k).className='badge '+(s[k]?'on':'');document.getElementById('note').textContent=s.last_note?('last note: '+s.last_note.summary):''}catch(e){}}setInterval(tick,700);tick();
</script></body></html>"""

class H(BaseHTTPRequestHandler):
    def sendx(self,code,body,ctype): self.send_response(code); self.send_header("Content-Type",ctype); self.send_header("Cache-Control","no-store"); self.end_headers(); self.wfile.write(body.encode())
    def do_GET(self):
        p=urlparse(self.path).path
        if p in ["/","/avatar"]: self.sendx(200,HTML,"text/html")
        elif p=="/state": self.sendx(200,json.dumps(state(),ensure_ascii=False),"application/json")
        else: self.sendx(404,"not found","text/plain")
    def log_message(self,*a): return
def serve(port=PORT):
    set_avatar_state(mode="idle",emotion="calm",message="Seed avatar is awake.",hearing=False,seeing=False,thinking=False,speaking=False); PORT_FILE.write_text(str(port)); print(f"Seed avatar: http://127.0.0.1:{port}"); HTTPServer(("127.0.0.1",int(port)),H).serve_forever()
def alive(pid):
    try: os.kill(int(pid),0); return True
    except Exception: return False
def start_server(port=PORT,open_browser=True):
    if PID_FILE.exists():
        try:
            pid=int(PID_FILE.read_text().strip())
            if alive(pid):
                url=f"http://127.0.0.1:{PORT_FILE.read_text().strip() if PORT_FILE.exists() else port}"
                if open_browser: subprocess.Popen(["open",url])
                return {"ok":True,"already_running":True,"pid":pid,"url":url}
        except Exception: pass
    log=LOG_FILE.open("a"); p=subprocess.Popen([sys.executable,"seed_avatar_v89.py","serve",str(port)],stdout=log,stderr=log); PID_FILE.write_text(str(p.pid)); url=f"http://127.0.0.1:{port}"
    if open_browser: subprocess.Popen(["open",url])
    return {"ok":True,"pid":p.pid,"url":url}
def stop_server():
    pid=None; stopped=False
    if PID_FILE.exists():
        try:
            pid=int(PID_FILE.read_text().strip())
            if alive(pid): os.kill(pid,signal.SIGTERM); stopped=True
            PID_FILE.unlink(missing_ok=True)
        except Exception: pass
    return {"ok":True,"pid":pid,"stopped":stopped}
def avatar_status():
    pid=None; a=False
    if PID_FILE.exists():
        try: pid=int(PID_FILE.read_text().strip()); a=alive(pid)
        except Exception: pass
    port=PORT_FILE.read_text().strip() if PORT_FILE.exists() else str(PORT)
    return {"created_at":now(),"version":"v89.2.0","ok":True,"alive":a,"pid":pid,"url":f"http://127.0.0.1:{port}","state":state()}
if __name__=="__main__":
    arg=sys.argv[1] if len(sys.argv)>1 else "status"
    if arg=="serve": serve(int(sys.argv[2]) if len(sys.argv)>2 else PORT)
    elif arg=="start": print(start_server())
    elif arg=="stop": print(stop_server())
    elif arg=="set": print(set_avatar_state(mode=sys.argv[2] if len(sys.argv)>2 else "idle",message=" ".join(sys.argv[3:])))
    else: print(json.dumps(avatar_status(),indent=4,ensure_ascii=False))
