import json, os, subprocess, threading, urllib.parse
from datetime import datetime
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path

HOST="127.0.0.1"; PORT=int(os.environ.get("SEED_V74_PORT","8794"))
JOURNAL=Path("seed_embodied_session_journal_v74.jsonl")

HTML = r"""<!doctype html><html><head><meta charset="utf-8"/><title>Seed v74</title>
<style>
:root{--bg:#0f1115;--card:#171a21;--line:#2a2f3a;--text:#f4f4f5;--muted:#a1a1aa;--accent:#f97316}
*{box-sizing:border-box}body{margin:0;background:radial-gradient(circle at top,#202633,#0f1115 55%);color:var(--text);font-family:-apple-system,BlinkMacSystemFont,Segoe UI,sans-serif}
header{padding:18px 24px;border-bottom:1px solid var(--line);display:flex;justify-content:space-between}h1{margin:0;font-size:20px}
main{display:grid;grid-template-columns:360px 1fr 380px;gap:16px;padding:16px}.card{background:rgba(23,26,33,.92);border:1px solid var(--line);border-radius:18px;padding:16px;box-shadow:0 10px 30px rgba(0,0,0,.25)}
.avatar{display:flex;flex-direction:column;align-items:center;gap:12px}.orb{width:170px;height:170px;border-radius:50%;background:var(--accent);box-shadow:0 0 50px var(--accent);display:flex;align-items:center;justify-content:center;font-size:58px;transition:.3s}
.status{font-size:14px;color:var(--muted);line-height:1.45}button{background:#272b35;color:var(--text);border:1px solid #3b4252;border-radius:12px;padding:10px 12px;cursor:pointer}button:hover{border-color:var(--accent)}button.primary{background:var(--accent);border-color:var(--accent);color:#111;font-weight:700}
textarea,input{width:100%;background:#0c0e13;color:var(--text);border:1px solid #343946;border-radius:12px;padding:12px}textarea{min-height:80px;resize:vertical}.row{display:flex;gap:8px;flex-wrap:wrap}.chatlog{height:390px;overflow:auto;background:#0c0e13;border:1px solid #282d38;border-radius:12px;padding:12px;white-space:pre-wrap}.small{font-size:12px;color:var(--muted)}.item{padding:10px;border:1px solid #282d38;border-radius:12px;margin:8px 0;background:#10131a}.grid2{display:grid;grid-template-columns:1fr 1fr;gap:10px}
</style></head><body><header><h1>Seed v74 — Embodied Companion Interface</h1><div class="small" id="stamp">loading...</div></header>
<main><section class="card avatar"><div class="orb" id="orb">●</div><h2 id="mood">Seed</h2><div class="status" id="reason">Loading...</div><div class="row"><button onclick="refresh()">Refresh</button><button onclick="openApi()">API</button></div><div class="status" id="model"></div></section>
<section class="card"><h2>Talk to Seed</h2><div class="chatlog" id="chatlog"></div><textarea id="msg" placeholder="Type to Seed..."></textarea><div class="row" style="margin-top:8px"><button class="primary" onclick="sendChat()">Send</button><button onclick="voiceOnce(6)">Voice 6s</button><button onclick="voiceOnce(8)">Voice 8s</button><button onclick="speakCuriosity()">Speak curiosity</button></div><p class="small">Voice uses your Mac mic through local Python server.</p></section>
<section class="card"><h2>Presence</h2><div class="grid2"><button onclick="loadMemory()">Memory review</button><button onclick="loadTasks()">Action tasks</button><button onclick="loadInbox()">Presence inbox</button><button onclick="loadCuriosity()">Curiosity</button></div><div id="side" style="margin-top:12px;max-height:560px;overflow:auto;"></div></section></main>
<script>
const API="";function esc(s){return String(s??"").replace(/[&<>]/g,c=>({"&":"&amp;","<":"&lt;",">":"&gt;"}[c]))}function addLog(r,t){let e=document.getElementById("chatlog");e.innerHTML+="\n"+r+": "+esc(t)+"\n";e.scrollTop=e.scrollHeight}function colorFor(c){return {green:"#22c55e",blue:"#38bdf8",orange:"#f97316",red:"#ef4444",purple:"#a855f7"}[c]||c||"#f97316"}async function j(p,o){let r=await fetch(API+p,o);return await r.json()}
async function refresh(){let s=await j("/api/state");document.getElementById("stamp").textContent=s.created_at||"";let a=s.avatar||{};let col=colorFor(a.color);document.documentElement.style.setProperty("--accent",col);document.getElementById("orb").textContent=a.mode==="listening"?"◉":a.mode==="thinking"?"◌":a.mode==="speaking"?"◍":"●";document.getElementById("mood").textContent=`${a.mood||"steady"} / ${a.mode||"idle"}`;document.getElementById("reason").textContent=a.reason||"";document.getElementById("model").textContent=`model: ${a.last_model||"-"} | role: ${a.last_role||"-"}`}
async function sendChat(){let m=document.getElementById("msg").value.trim();if(!m)return;addLog("You",m);document.getElementById("msg").value="";let r=await j("/api/chat",{method:"POST",headers:{"Content-Type":"application/json"},body:JSON.stringify({message:m})});addLog("Seed",r.reply||r.error||"[no reply]");refresh()}
async function voiceOnce(sec){addLog("System",`Recording ${sec}s...`);let r=await j("/api/voice/once",{method:"POST",headers:{"Content-Type":"application/json"},body:JSON.stringify({seconds:sec})});if(r.transcript)addLog("Voice transcript",r.transcript);addLog("Seed",r.reply||r.error||"[no reply]");refresh()}
async function speakCuriosity(){let r=await j("/api/curiosity/speak",{method:"POST"});addLog("Curiosity",r.spoken||r.error||JSON.stringify(r));refresh()}function openApi(){window.open("/api/state","_blank")}
async function loadMemory(){let r=await j("/api/memory");document.getElementById("side").innerHTML=(r.candidates||[]).map(x=>`<div class=item><b>${esc(x.id)}</b><br>${esc(x.text)}<div class=row><button onclick="memAction('${x.id}','save')">save</button><button onclick="memAction('${x.id}','ignore')">ignore</button><button onclick="memAction('${x.id}','later')">later</button></div></div>`).join("")||"<p>No candidates.</p>"}async function memAction(id,action){await j("/api/memory/action",{method:"POST",headers:{"Content-Type":"application/json"},body:JSON.stringify({candidate_id:id,action})});loadMemory()}
async function loadTasks(){let r=await j("/api/tasks");document.getElementById("side").innerHTML=(r.tasks||[]).slice(0,30).map(t=>`<div class=item><b>${esc(t.id)} — ${esc(t.title)}</b><br><span class=small>${esc(t.category)} / ${esc(t.priority)}</span><br>${esc(t.reason||"")}</div>`).join("")}
async function loadInbox(){let r=await j("/api/inbox");document.getElementById("side").innerHTML=(r.items||[]).slice(-20).map(x=>`<div class=item><b>${esc(x.title)}</b><br><span class=small>${esc(x.category)} / ${esc(x.urgency)}</span><br>${esc(x.body)}</div>`).join("")}
async function loadCuriosity(){let r=await j("/api/curiosity");document.getElementById("side").innerHTML=(r.items||[]).map(x=>`<div class=item><b>${esc(x.title)}</b><br><span class=small>${esc(x.category)} score=${x.relevance_score}</span><br>${esc(x.body)}<br><span class=small>why: ${esc(x.why)}</span></div>`).join("")}
refresh();setInterval(refresh,5000)
</script></body></html>"""

def now_timestamp(): return datetime.now().isoformat(timespec="seconds")
def append_journal(row):
    with JOURNAL.open("a") as f: f.write(json.dumps(row, ensure_ascii=False)+"\n")
def safe_json(fn):
    try: return fn()
    except Exception as e: return {"ok":False,"error":str(e),"created_at":now_timestamp()}
def build_state():
    try:
        from seed_avatar_panel_v74 import build_avatar_panel_state
        avatar=build_avatar_panel_state()
    except Exception as e: avatar={"ok":False,"error":str(e)}
    return {"created_at":now_timestamp(),"version":"v74.0.0","ok":True,"avatar":avatar}
def seed_chat(message):
    from seed_embodied_state_v74 import save_state
    save_state(mode="thinking", mode_reason="Seed is thinking through a typed message.", last_user=message)
    try:
        from seed_local_chat_v701 import choose_role, model_fallbacks, call_ollama
        role=choose_role(message); last_error=None
        for model in model_fallbacks(role):
            try:
                reply=(call_ollama(model, role, message) or "").strip()
                if reply and reply.lower() not in {"normal","ok","okay"}:
                    save_state(mode="idle",mode_reason="Seed replied.",last_user=message,last_reply=reply,last_model=model,last_role=role)
                    append_journal({"created_at":now_timestamp(),"kind":"chat","user":message,"reply":reply,"model":model,"role":role})
                    return {"ok":True,"reply":reply,"model":model,"role":role}
            except Exception as e: last_error=str(e)
        save_state(mode="warning",mode_reason="No local model gave a valid reply.")
        return {"ok":False,"error":last_error or "No valid reply."}
    finally:
        try:
            from seed_embodied_state_v74 import load_state, save_state
            if load_state().get("mode")=="thinking": save_state(mode="idle",mode_reason="Thinking complete.")
        except Exception: pass
def voice_once(seconds=6):
    from seed_embodied_state_v74 import save_state
    save_state(mode="listening",mode_reason=f"Recording {seconds}s from microphone.")
    try:
        from seed_live_voice_v731 import record_audio, transcribe_audio, ask_seed_text, say_text
        audio_path,device=record_audio(seconds); transcript=transcribe_audio(audio_path); text=transcript.get("text","").strip()
        if not text:
            save_state(mode="warning",mode_reason="Voice transcription was empty.",last_transcript="")
            return {"ok":False,"error":"empty transcript","audio":str(audio_path),"device":device}
        save_state(mode="thinking",mode_reason="Seed is thinking about the voice transcript.",last_transcript=text,last_user=text)
        answer=ask_seed_text(text); reply=answer.get("reply","")
        save_state(mode="speaking",mode_reason="Seed is speaking a voice reply.",last_transcript=text,last_user=text,last_reply=reply,last_model=answer.get("model"),last_role=answer.get("role"))
        spoke=say_text(reply) if reply else False
        save_state(mode="idle",mode_reason="Voice exchange complete.")
        row={"created_at":now_timestamp(),"kind":"voice","audio":str(audio_path),"device":device,"transcript":text,"reply":reply,"model":answer.get("model"),"role":answer.get("role"),"spoke":spoke}
        append_journal(row); return {"ok":True,**row}
    except Exception as e:
        save_state(mode="warning",mode_reason=str(e)); return {"ok":False,"error":str(e)}
def speak_curiosity():
    try:
        from seed_curiosity_engine_v72 import best_curiosity
        from seed_live_voice_v731 import say_text
        c=best_curiosity(); text=f"{c.get('title')}. {c.get('body')}"; say_text(text); return {"ok":True,"spoken":text,"curiosity":c}
    except Exception as e: return {"ok":False,"error":str(e)}

class Handler(BaseHTTPRequestHandler):
    def _send(self,status=200,ctype="application/json"):
        self.send_response(status); self.send_header("Content-Type",ctype); self.send_header("Access-Control-Allow-Origin","*"); self.send_header("Access-Control-Allow-Headers","Content-Type"); self.end_headers()
    def _json(self,data,status=200): self._send(status); self.wfile.write(json.dumps(data,ensure_ascii=False).encode("utf-8"))
    def _body(self):
        n=int(self.headers.get("Content-Length","0") or "0")
        if n<=0: return {}
        try: return json.loads(self.rfile.read(n).decode("utf-8",errors="ignore"))
        except Exception: return {}
    def do_OPTIONS(self): self._send()
    def do_GET(self):
        path=urllib.parse.urlparse(self.path).path
        if path in {"/","/panel","/avatar"}: self._send(200,"text/html; charset=utf-8"); self.wfile.write(HTML.encode("utf-8")); return
        if path=="/api/state": return self._json(build_state())
        if path=="/api/memory": return self._json(safe_json(lambda: __import__("seed_memory_actions_v74",fromlist=["get_memory_candidates"]).get_memory_candidates(10)))
        if path=="/api/tasks": return self._json(safe_json(lambda: __import__("seed_action_tasks_v74",fromlist=["build_action_tasks"]).build_action_tasks()))
        if path=="/api/inbox": return self._json(safe_json(lambda: __import__("seed_presence_inbox_v72",fromlist=["build_notices"]).build_notices()))
        if path=="/api/curiosity": return self._json(safe_json(lambda: __import__("seed_curiosity_engine_v72",fromlist=["generate_curiosities"]).generate_curiosities()))
        return self._json({"ok":False,"error":"not found"},404)
    def do_POST(self):
        path=urllib.parse.urlparse(self.path).path; body=self._body()
        if path=="/api/chat": return self._json(safe_json(lambda: seed_chat(body.get("message",""))))
        if path=="/api/voice/once": return self._json(safe_json(lambda: voice_once(max(2,min(int(body.get("seconds",6) or 6),20)))))
        if path=="/api/memory/action":
            def fn():
                from seed_memory_actions_v74 import review_action
                return review_action(body.get("candidate_id",""),body.get("action","later"),body.get("note",""))
            return self._json(safe_json(fn))
        if path=="/api/curiosity/speak": return self._json(safe_json(speak_curiosity))
        return self._json({"ok":False,"error":"not found"},404)
    def log_message(self, fmt, *args): print("[v74]", fmt % args)

def open_browser(url):
    try: subprocess.Popen(["open",url])
    except Exception: pass
def run_server(open_ui=True):
    url=f"http://{HOST}:{PORT}"
    print("\n=== SEED v74 EMBODIED COMPANION INTERFACE ==="); print(f"Open: {url}"); print("Press Ctrl+C to stop.")
    if open_ui: threading.Timer(0.8,lambda:open_browser(url)).start()
    ThreadingHTTPServer((HOST,PORT),Handler).serve_forever()
if __name__=="__main__": run_server(True)
