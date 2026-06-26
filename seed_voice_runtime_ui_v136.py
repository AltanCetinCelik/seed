import json, os, signal, subprocess, sys
from http.server import BaseHTTPRequestHandler, HTTPServer
from pathlib import Path
from urllib.parse import urlparse, parse_qs
from datetime import datetime

PID=Path("seed_voice_runtime_ui_v136.pid")
LOG=Path("seed_voice_runtime_ui_v136.log")
PORT=8816

def now():
    return datetime.now().isoformat(timespec="seconds")

def runtime_status():
    try:
        import seed_voice_runtime_v136 as rt
        return rt.runtime_status()
    except Exception as e:
        return {"ok":False,"error":str(e)}

HTML = """<!doctype html><html><head><meta charset='utf-8'><title>Seed Voice Runtime v136</title><meta name='viewport' content='width=device-width,initial-scale=1'><style>
body{margin:0;background:#050505;color:#f5f5f5;font-family:-apple-system,BlinkMacSystemFont,Segoe UI,sans-serif}.wrap{max-width:1100px;margin:0 auto;padding:30px}.hero{background:#111318;border:1px solid #2a2d33;border-radius:24px;padding:24px;margin-bottom:18px}.title{font-size:38px;font-weight:850;letter-spacing:-.04em}.muted{color:#a3a7ad}.grid{display:grid;grid-template-columns:repeat(auto-fit,minmax(250px,1fr));gap:14px}.card{background:#111318;border:1px solid #2a2d33;border-radius:20px;padding:18px}button{background:#ff8a23;color:#111;border:0;border-radius:13px;padding:12px 14px;font-weight:750;margin:4px;cursor:pointer}input{background:#090a0c;color:#fff;border:1px solid #2a2d33;border-radius:13px;padding:12px;width:70%}pre{white-space:pre-wrap;word-break:break-word;background:#08090b;border:1px solid #24272e;border-radius:14px;padding:12px;max-height:420px;overflow:auto}.ok{color:#72f59c}.bad{color:#ff6868}</style></head><body><div class='wrap'><div class='hero'><div class='muted'>Local Companion OS</div><div class='title'>Seed Voice Runtime v136</div><p class='muted'>One orchestrator for wake text, voice once, intent normalization, answer, and speech.</p><button onclick='api("start")'>Start</button><button onclick='api("stop")'>Stop</button><button onclick='api("once")'>Voice Once</button><button onclick='api("wake-text","wake up status")'>Test Wake Status</button></div><div class='card'><input id='txt' value='wake up status'><button onclick='api("wake-text",txt.value)'>Run Wake Text</button><button onclick='api("text",txt.value)'>Run Text</button></div><div class='grid'><div class='card'><h3>Status</h3><pre id='status'>loading</pre></div><div class='card'><h3>Recent Events</h3><pre id='events'>loading</pre></div></div></div><script>
async function api(action,text){
  let u='/api/'+action;
  if(text) u+='?text='+encodeURIComponent(text);
  let r=await fetch(u);
  let j=await r.json();
  await refresh();
  alert(JSON.stringify(j,null,2).slice(0,900));
}
async function refresh(){
  let j=await (await fetch('/api/status?'+Date.now())).json();
  status.textContent=JSON.stringify(j,null,2);
  events.textContent=JSON.stringify(j.recent_events||[],null,2);
}
refresh(); setInterval(refresh,2500);
</script></body></html>"""

class H(BaseHTTPRequestHandler):
    def send_json(self,obj):
        b=json.dumps(obj,ensure_ascii=False).encode()
        self.send_response(200)
        self.send_header("Content-Type","application/json")
        self.end_headers()
        self.wfile.write(b)
    def do_GET(self):
        p=urlparse(self.path)
        q=parse_qs(p.query)
        try:
            import seed_voice_runtime_v136 as rt
            if p.path=="/api/status":
                self.send_json(rt.runtime_status())
            elif p.path=="/api/start":
                self.send_json(rt.start())
            elif p.path=="/api/stop":
                self.send_json(rt.stop())
            elif p.path=="/api/once":
                self.send_json(rt.voice_once())
            elif p.path=="/api/text":
                self.send_json(rt.run_text(q.get("text",[""])[0]))
            elif p.path=="/api/wake-text":
                self.send_json(rt.run_wake_text(q.get("text",[""])[0]))
            else:
                b=HTML.encode()
                self.send_response(200)
                self.send_header("Content-Type","text/html")
                self.end_headers()
                self.wfile.write(b)
        except Exception as e:
            self.send_json({"ok":False,"error":str(e)})
    def log_message(self,*a):
        return

def alive(pid):
    try:
        os.kill(int(pid),0)
        return True
    except Exception:
        return False

def serve():
    HTTPServer(("127.0.0.1",PORT),H).serve_forever()

def start():
    if PID.exists():
        try:
            pid=int(PID.read_text().strip())
            if alive(pid):
                subprocess.Popen(["open",f"http://127.0.0.1:{PORT}/"])
                return {"ok":True,"already_running":True,"pid":pid,"url":f"http://127.0.0.1:{PORT}/"}
        except Exception:
            pass
    p=subprocess.Popen([sys.executable,"seed_voice_runtime_ui_v136.py","serve"],stdout=LOG.open("a"),stderr=LOG.open("a"))
    PID.write_text(str(p.pid))
    subprocess.Popen(["open",f"http://127.0.0.1:{PORT}/"])
    return {"ok":True,"pid":p.pid,"url":f"http://127.0.0.1:{PORT}/"}

def stop():
    pid=None; stopped=False
    if PID.exists():
        try:
            pid=int(PID.read_text().strip())
            if alive(pid):
                os.kill(pid,signal.SIGTERM); stopped=True
            PID.unlink(missing_ok=True)
        except Exception:
            pass
    return {"ok":True,"stopped":stopped,"pid":pid}

def status():
    pid=None; al=False
    if PID.exists():
        try:
            pid=int(PID.read_text().strip()); al=alive(pid)
        except Exception: pass
    return {"created_at":now(),"version":"v136.0.0","ok":True,"alive":al,"pid":pid,"url":f"http://127.0.0.1:{PORT}/"}

if __name__=="__main__":
    a=sys.argv[1] if len(sys.argv)>1 else "status"
    if a=="serve":
        serve()
    elif a=="start":
        print(json.dumps(start(),indent=4,ensure_ascii=False))
    elif a=="stop":
        print(json.dumps(stop(),indent=4,ensure_ascii=False))
    else:
        print(json.dumps(status(),indent=4,ensure_ascii=False))
