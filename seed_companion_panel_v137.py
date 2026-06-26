import json, os, signal, subprocess, sys
from http.server import BaseHTTPRequestHandler, HTTPServer
from pathlib import Path
from urllib.parse import urlparse, parse_qs
from datetime import datetime

PID = Path("seed_companion_panel_v137.pid")
LOG = Path("seed_companion_panel_v137.log")
PORT = 8821

HTML = """<!doctype html><html><head><meta charset='utf-8'><title>Seed Companion v137</title><meta name='viewport' content='width=device-width,initial-scale=1'><style>
body{margin:0;background:radial-gradient(circle at 10% 0%,rgba(255,138,35,.22),transparent 35%),#050505;color:#f4f4f2;font-family:-apple-system,BlinkMacSystemFont,Segoe UI,sans-serif}.wrap{max-width:1200px;margin:0 auto;padding:28px}.hero,.card{background:#111318;border:1px solid #2a2d33;border-radius:24px;padding:22px;margin:14px 0}.title{font-size:44px;font-weight:900;letter-spacing:-.055em}.muted{color:#a3a7ad}.grid{display:grid;grid-template-columns:repeat(auto-fit,minmax(300px,1fr));gap:14px}.big{font-size:42px;font-weight:900;color:#72f59c}.bad{color:#ff6868}button{background:#ff8a23;color:#111;border:0;border-radius:13px;padding:12px 15px;font-weight:850;margin:5px;cursor:pointer}.secondary{background:#1a1d22;color:#f4f4f2;border:1px solid #2a2d33}input{background:#08090b;color:#f4f4f2;border:1px solid #2a2d33;border-radius:12px;padding:12px;width:65%}pre{white-space:pre-wrap;word-break:break-word;background:#08090b;border:1px solid #24272e;border-radius:14px;padding:12px;max-height:540px;overflow:auto}</style></head><body><div class='wrap'><div class='hero'><div class='muted'>Local Companion OS</div><div class='title'>Seed Companion v137</div><p class='muted'>Presence runtime: dashboard + avatar + proactive + voice + autonomy + wake loop.</p><button onclick='api("start")'>Start Companion</button><button onclick='api("start-audio")'>Start + Audio Wake</button><button class='secondary' onclick='api("stop")'>Stop Companion</button><button class='secondary' onclick='api("audio-off")'>Audio Off</button></div><div class='card'><input id='msg' value='wake up status'><button onclick='api("enqueue?text="+encodeURIComponent(msg.value))'>Send Wake Text</button><button class='secondary' onclick='api("tick")'>Tick</button></div><div class='grid'><div class='card'><div class='muted'>Companion</div><div id='alive' class='big'>—</div><div id='pid' class='muted'></div></div><div class='card'><div class='muted'>Hygiene</div><pre id='hygiene'>loading</pre></div><div class='card'><div class='muted'>Services</div><pre id='services'>loading</pre></div></div><div class='card'><h3>Recent Events</h3><pre id='events'>loading</pre></div><div class='card'><h3>Raw Status</h3><pre id='raw'>loading</pre></div></div><script>
async function api(path){let j=await(await fetch('/api/'+path)).json();raw.textContent=JSON.stringify(j,null,2);await refresh();alert(JSON.stringify(j,null,2).slice(0,1000))}
async function refresh(){let j=await(await fetch('/api/status?'+Date.now())).json();raw.textContent=JSON.stringify(j,null,2);alive.textContent=j.alive?'ALIVE':'STOPPED';alive.className=j.alive?'big':'big bad';pid.textContent='pid '+(j.pid||'—');services.textContent=JSON.stringify(j.services_summary||{},null,2);hygiene.textContent=JSON.stringify(j.hygiene_summary||{},null,2);events.textContent=JSON.stringify(j.recent_events||[],null,2)}
refresh();setInterval(refresh,3000)
</script></body></html>"""

def now():
    return datetime.now().isoformat(timespec="seconds")

def alive(pid):
    try:
        os.kill(int(pid),0); return True
    except Exception: return False

class H(BaseHTTPRequestHandler):
    def send_json(self,obj):
        b=json.dumps(obj,ensure_ascii=False).encode()
        self.send_response(200); self.send_header("Content-Type","application/json"); self.end_headers(); self.wfile.write(b)
    def do_GET(self):
        p=urlparse(self.path); q=parse_qs(p.query)
        try:
            import seed_companion_v137 as c
            if p.path == "/api/status":
                st=c.status()
                st["services_summary"]=summarize_services(st.get("services",{}))
                st["hygiene_summary"]=extract_hygiene(st.get("services",{}))
                self.send_json(st)
            elif p.path == "/api/start":
                self.send_json(c.start())
            elif p.path == "/api/start-audio":
                self.send_json(c.start(audio=True))
            elif p.path == "/api/stop":
                self.send_json(c.stop())
            elif p.path == "/api/audio-off":
                self.send_json(c.configure("audio_wake_enabled","false"))
            elif p.path == "/api/tick":
                self.send_json(c.loop_tick())
            elif p.path == "/api/enqueue":
                self.send_json(c.enqueue((q.get("text") or ["wake up status"])[0], source="panel"))
            else:
                b=HTML.encode(); self.send_response(200); self.send_header("Content-Type","text/html"); self.end_headers(); self.wfile.write(b)
        except Exception as e:
            self.send_json({"ok":False,"error":str(e)})
    def log_message(self,*a): return

def summarize_services(services):
    out={}
    for k,v in services.items():
        data=v.get("data") if isinstance(v,dict) else None
        if isinstance(data,dict):
            out[k]={"ok":v.get("ok"),"alive":data.get("alive"),"pid":data.get("pid"),"url":data.get("url")}
        else:
            out[k]={"ok":v.get("ok") if isinstance(v,dict) else False}
    return out

def extract_hygiene(services):
    h=services.get("effective_hygiene",{}) if isinstance(services,dict) else {}
    data=h.get("data") if isinstance(h,dict) else None
    if isinstance(data,dict):
        hv=data.get("hygiene_v13623") or data.get("hygiene") or {}
        return {"score":hv.get("score"),"grade":hv.get("grade"),"reasons":hv.get("reasons"),"approval_effective":(data.get("approval_v13623") or {}).get("effective_pending_count")}
    return {}

def serve():
    HTTPServer(("127.0.0.1", PORT), H).serve_forever()

def start():
    if PID.exists():
        try:
            pid=int(PID.read_text().strip())
            if alive(pid):
                subprocess.Popen(["open",f"http://127.0.0.1:{PORT}/"])
                return {"ok":True,"already_running":True,"pid":pid,"url":f"http://127.0.0.1:{PORT}/"}
        except Exception: pass
    p=subprocess.Popen([sys.executable,"seed_companion_panel_v137.py","serve"],stdout=LOG.open("a"),stderr=LOG.open("a"))
    PID.write_text(str(p.pid))
    subprocess.Popen(["open",f"http://127.0.0.1:{PORT}/"])
    return {"ok":True,"pid":p.pid,"url":f"http://127.0.0.1:{PORT}/"}

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
    return {"created_at":now(),"version":"v137.0.0","ok":True,"alive":al,"pid":pid,"url":f"http://127.0.0.1:{PORT}/"}

if __name__=="__main__":
    a=sys.argv[1] if len(sys.argv)>1 else "status"
    if a=="serve": serve()
    elif a=="start": print(json.dumps(start(),indent=4,ensure_ascii=False))
    elif a=="stop": print(json.dumps(stop(),indent=4,ensure_ascii=False))
    else: print(json.dumps(status(),indent=4,ensure_ascii=False))
