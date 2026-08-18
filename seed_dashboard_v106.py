import json, os, signal, subprocess, sys
from datetime import datetime
from http.server import BaseHTTPRequestHandler, HTTPServer
from pathlib import Path
from urllib.parse import urlparse

PID=Path("seed_dashboard_v106.pid")
LOG=Path("seed_dashboard_v106.log")
PORT=8806

GROUPS={
    "Command":[("Supervisor","seed_supervisor_v92","supervisor_status"),("Doctor","seed_doctor_v105","diagnose"),("Approval Center","seed_action_approval_v107","status"),("Proactive Rhythm","seed_proactive_rhythm_v108","status")],
    "Intelligence":[("Memory Garden 3","seed_memory_garden3_v112","status"),("Memory Gate","seed_memory_gate_v113","status"),("Deep Research","seed_deep_research_v123","status"),("Knowledge Graph","seed_knowledge_graph_v124","status"),("Private RAG 2","seed_rag2_v122","status"),("Project Memory","seed_project_memory_v114","status")],
    "Voice / Body":[("Native Wake","seed_native_wake_v109","status"),("STT","seed_stt_v110","status"),("TTS","seed_tts_v111","status"),("Screen Understanding","seed_screen_understanding_v116","status"),("Operator 2","seed_operator2_v115","status"),("Avatar 2","seed_avatar2_v129","status")],
    "Expansion":[("Device Router","seed_device_router_v125","status"),("Pi Satellite","seed_pi_satellite_v126","status"),("Windows Worker","seed_windows_worker_v127","status"),("Skill Registry","seed_skill_registry2_v118","status"),("Safe MCP Bridge","seed_mcp_bridge_v119","status"),("Repo Audit","seed_repo_audit_v121","status"),("Release Packaging","seed_release_packaging_v130","status")]
}

def now():
    return datetime.now().isoformat(timespec="seconds")

def safe_call(title,module,fn):
    try:
        m=__import__(module,fromlist=[fn])
        data=getattr(m,fn)()
        return {"title":title,"module":module,"ok":bool(data.get("ok",True)),"data":data,"summary":summary(title,data)}
    except Exception as e:
        return {"title":title,"module":module,"ok":False,"data":{"error":str(e)},"summary":str(e)}

def summary(title,d):
    if title=="Supervisor": return f"{d.get('ok_count','?')}/{d.get('total','?')} · {d.get('mode','online')}"
    if title=="Doctor": return "required green" if d.get("required_ok",d.get("ok")) else "required check failed"
    if title=="Approval Center": return f"{d.get('pending_count',0)} pending approval(s)"
    if title=="Proactive Rhythm":
        hb=d.get("heartbeat",{})
        return f"alive={d.get('alive')} · asks={d.get('today_asks')} · heartbeat={hb.get('fresh')}"
    if title=="Memory Garden 3": return f"{d.get('count',0)} typed memories"
    if title=="Deep Research": return f"{len(d.get('sessions',[]))} sessions · {d.get('claims',0)} claims"
    if title=="Knowledge Graph": return f"{d.get('triples',0)} triples"
    if title=="Private RAG 2": return f"{d.get('chunks',0)} indexed chunks"
    if title=="Project Memory": return f"{d.get('events',0)} project events"
    if title=="Native Wake": return f"{d.get('route','unknown')} · configured={d.get('configured')}"
    if title in {"STT","TTS"}:
        r=d.get("readiness",{})
        return f"{r.get('engine','unknown')} · {r.get('level','unknown')}"
    if title=="Screen Understanding":
        cur=d.get("current",{}); aw=cur.get("active_window",{})
        return f"{aw.get('app','unknown')} · changed={cur.get('changed')}"
    if title=="Avatar 2":
        st=d.get("state",{})
        return f"{st.get('mood','idle')} · alive={d.get('alive')}"
    if title=="Device Router": return f"{len(d.get('devices',{}))} device routes"
    if title=="Skill Registry": return f"{d.get('count',0)} skills"
    if title=="Safe MCP Bridge":
        reg=d.get("registry",{})
        return f"enabled={reg.get('enabled',False)} · execute={reg.get('allow_execute',False)}"
    if title=="Repo Audit": return f"{d.get('repo_count',0)} repos · {len(d.get('missing_priority_repos',[]))} missing"
    return "OK" if d.get("ok",True) else "CHECK"

def gather():
    groups=[]; cards=[]
    for group,specs in GROUPS.items():
        group_cards=[safe_call(*x) for x in specs]
        groups.append({"name":group,"cards":group_cards,"ok_count":sum(c["ok"] for c in group_cards),"total":len(group_cards)})
        cards.extend(group_cards)
    ok_count=sum(c["ok"] for c in cards)
    pending=0
    for c in cards:
        if c["title"]=="Approval Center":
            pending=c["data"].get("pending_count",0)
    health=round((ok_count/max(1,len(cards)))*100)
    mood="needs approval" if pending else "green" if health>=95 else "focused"
    return {"created_at":now(),"version":"v130.1-ui","ok":ok_count>=max(1,len(cards)-2),"health":health,"mood":mood,"ok_count":ok_count,"total":len(cards),"groups":groups,"cards":cards}

HTML = r'''
<!doctype html>
<html><head><meta charset="utf-8"><title>Seed Control Room</title><meta name="viewport" content="width=device-width,initial-scale=1">
<style>
:root{--bg:#050505;--panel:#111214;--line:#2a2d33;--text:#f4f4f2;--muted:#a3a7ad;--orange:#ff8a23;--green:#72f59c;--red:#ff6868}
*{box-sizing:border-box} body{margin:0;background:radial-gradient(circle at 12% 8%,rgba(255,138,35,.18),transparent 32%),linear-gradient(180deg,#070707,#050505 60%);color:var(--text);font-family:-apple-system,BlinkMacSystemFont,"SF Pro Display","Segoe UI",sans-serif}
.app{display:grid;grid-template-columns:280px 1fr;min-height:100vh}.sidebar{border-right:1px solid var(--line);background:rgba(9,10,12,.82);backdrop-filter:blur(24px);padding:24px;position:sticky;top:0;height:100vh}
.brand{display:flex;align-items:center;gap:13px;margin-bottom:28px}.logo{width:48px;height:48px;border-radius:18px;background:radial-gradient(circle at 35% 24%,#ffe5c5,#ff8a23 47%,#5a2100);box-shadow:0 0 42px rgba(255,138,35,.42)}
.brand h1{font-size:22px;margin:0}.brand p{margin:3px 0 0;color:var(--muted);font-size:12px}.nav button,.quick button{width:100%;background:transparent;color:var(--muted);border:1px solid transparent;text-align:left;border-radius:13px;padding:11px 12px;margin:3px 0;cursor:pointer;font-size:14px}.nav button:hover,.nav button.active,.quick button:hover{background:#15171b;color:var(--text);border-color:#24272e}.quick{margin-top:24px;border-top:1px solid var(--line);padding-top:18px}.quick h3{font-size:12px;color:var(--muted);font-weight:600;text-transform:uppercase;letter-spacing:.12em}
.main{padding:26px 34px 50px}.top{display:flex;justify-content:space-between;gap:20px;align-items:flex-start;margin-bottom:22px}.kicker{color:#ffb36b;font-size:12px;text-transform:uppercase;letter-spacing:.16em;font-weight:700}.title{font-size:38px;line-height:1.04;letter-spacing:-.04em;margin:8px 0}.subtitle{color:var(--muted);max-width:780px;line-height:1.45}.pill{border:1px solid var(--line);border-radius:999px;padding:8px 12px;background:#111318;color:var(--muted);font-size:13px;white-space:nowrap}
.hero{display:grid;grid-template-columns:1.1fr .9fr;gap:16px;margin-bottom:22px}.panel{background:linear-gradient(180deg,rgba(23,25,29,.94),rgba(14,15,18,.94));border:1px solid var(--line);border-radius:24px;padding:20px;box-shadow:0 18px 70px rgba(0,0,0,.35)}
.healthrow{display:flex;align-items:center;gap:18px}.ring{width:120px;height:120px;border-radius:50%;display:grid;place-items:center;background:conic-gradient(var(--green) calc(var(--p)*1%),#262a31 0);position:relative}.ring:after{content:"";position:absolute;width:88px;height:88px;border-radius:50%;background:#111318;border:1px solid var(--line)}.ring b{position:relative;z-index:1;font-size:26px}
.metrics{display:grid;grid-template-columns:repeat(3,1fr);gap:10px;margin-top:16px}.metric{background:#0c0d10;border:1px solid #23262d;border-radius:16px;padding:12px}.metric div:first-child{font-size:12px;color:var(--muted)}.metric div:last-child{font-size:20px;font-weight:750;margin-top:4px}
.searchbar{display:flex;gap:10px;margin:20px 0}.searchbar input{flex:1;background:#0d0e11;border:1px solid var(--line);border-radius:15px;color:var(--text);padding:13px 14px;font-size:14px}.grid{display:grid;grid-template-columns:repeat(auto-fill,minmax(285px,1fr));gap:14px}.group{margin-top:22px}.groupHead{display:flex;align-items:center;justify-content:space-between;margin-bottom:10px}.groupHead h2{font-size:18px;margin:0}
.card{background:rgba(18,20,24,.86);border:1px solid var(--line);border-radius:20px;padding:16px;transition:.16s transform,.16s border-color}.card:hover{transform:translateY(-2px);border-color:#424751}.cardTop{display:flex;justify-content:space-between;gap:12px;align-items:center}.card h3{font-size:16px;margin:0}.status{font-size:11px;font-weight:800;border-radius:999px;padding:5px 8px}.ok{background:rgba(114,245,156,.16);color:var(--green);border:1px solid rgba(114,245,156,.32)}.bad{background:rgba(255,104,104,.15);color:var(--red);border:1px solid rgba(255,104,104,.3)}.summary{color:var(--muted);font-size:13px;line-height:1.35;margin:12px 0;min-height:36px}
details{border-top:1px solid #252830;padding-top:10px}summary{cursor:pointer;color:#ffb36b;font-size:13px}pre{white-space:pre-wrap;word-break:break-word;background:#08090b;border:1px solid #24272e;border-radius:14px;padding:12px;max-height:300px;overflow:auto;color:#d8d8d8;font-size:12px}.cmd{font-family:ui-monospace,SFMono-Regular,Menlo,monospace;background:#08090b;border:1px solid #24272e;border-radius:14px;padding:12px;color:#d7d7d7}
@media(max-width:980px){.app{grid-template-columns:1fr}.sidebar{position:relative;height:auto}.hero{grid-template-columns:1fr}.top{flex-direction:column}.title{font-size:30px}}
</style></head>
<body><div class="app"><aside class="sidebar"><div class="brand"><div class="logo"></div><div><h1>Seed</h1><p>Control Room · v130.1</p></div></div><div class="nav" id="nav"></div><div class="quick"><h3>Quick Actions</h3><button onclick="copyCmd('python seed_v1301_ui_gate.py')">Copy UI gate</button><button onclick="copyCmd('python seed_dashboard_v106.py start')">Copy dashboard start</button><button onclick="copyCmd('python seed_avatar2_v129.py start')">Copy avatar start</button><button onclick="copyCmd('./seed status')">Copy ./seed status</button></div></aside>
<main class="main"><div class="top"><div><div class="kicker">Local companion OS</div><div class="title">Seed is online.</div><div class="subtitle">Cleaner command center for status, approvals, memory, voice, body, research, and multi-device expansion. No raw screenshots. No blind remote execution.</div></div><div class="pill" id="stamp">loading…</div></div>
<section class="hero"><div class="panel"><div class="healthrow"><div class="ring" id="ring" style="--p:0"><b id="health">—</b></div><div><div class="kicker">System mood</div><h2 id="mood" style="font-size:32px;margin:8px 0 4px">checking…</h2><div class="subtitle" id="summary">Reading local modules…</div></div></div><div class="metrics"><div class="metric"><div>Green cards</div><div id="green">—</div></div><div class="metric"><div>Total cards</div><div id="total">—</div></div><div class="metric"><div>Refresh</div><div>4s</div></div></div></div><div class="panel"><div class="kicker">Command hints</div><div class="cmd">python seed_v1301_ui_gate.py<br>python seed_dashboard_v106.py start<br>python seed_avatar2_v129.py start<br>./seed status</div></div></section>
<div class="searchbar"><input id="filter" placeholder="Filter cards: approval, wake, memory, rag, avatar…" oninput="render()"></div><div id="content"></div></main></div>
<script>
let DATA=null,ACTIVE=null;
function esc(x){return String(x??'').replace(/[&<>"']/g,m=>({"&":"&amp;","<":"&lt;",">":"&gt;","\"":"&quot;","'":"&#039;"}[m]))}
function copyCmd(x){navigator.clipboard?.writeText(x)}
async function refresh(){const d=await(await fetch('/api/status?ts='+Date.now())).json();DATA=d;stamp.textContent=d.created_at;health.textContent=d.health+'%';ring.style.setProperty('--p',d.health);mood.textContent=d.mood;green.textContent=d.ok_count;total.textContent=d.total;summary.textContent=d.ok?'Core systems are healthy. Open cards for exact module state.':'Some systems need attention.';if(!ACTIVE&&d.groups?.length)ACTIVE=d.groups[0].name;renderNav();render()}
function renderNav(){nav.innerHTML=(DATA.groups||[]).map(g=>`<button class="${g.name===ACTIVE?'active':''}" onclick="ACTIVE='${esc(g.name)}';renderNav();render()">${esc(g.name)} · ${g.ok_count}/${g.total}</button>`).join('')}
function render(){if(!DATA)return;const q=(filter.value||'').toLowerCase();let groups=DATA.groups||[];if(ACTIVE)groups=groups.filter(g=>g.name===ACTIVE);content.innerHTML=groups.map(g=>{let cards=(g.cards||[]).filter(c=>(c.title+' '+c.summary+' '+c.module).toLowerCase().includes(q));return `<section class="group"><div class="groupHead"><h2>${esc(g.name)}</h2><span class="pill">${g.ok_count}/${g.total}</span></div><div class="grid">${cards.map(c=>`<article class="card"><div class="cardTop"><h3>${esc(c.title)}</h3><span class="status ${c.ok?'ok':'bad'}">${c.ok?'OK':'CHECK'}</span></div><div class="summary">${esc(c.summary)}</div><details><summary>module details</summary><pre>${esc(JSON.stringify(c.data,null,2))}</pre></details></article>`).join('')}</div></section>`}).join('')}
refresh();setInterval(refresh,4000);
</script></body></html>
'''

class H(BaseHTTPRequestHandler):
    def _send(self,code,body,ctype):
        if isinstance(body,str): body=body.encode("utf-8")
        self.send_response(code); self.send_header("Content-Type",ctype); self.send_header("Cache-Control","no-store"); self.send_header("Content-Length",str(len(body))); self.end_headers(); self.wfile.write(body)
    def do_GET(self):
        path=urlparse(self.path).path
        if path in ["/api/status","/status"]: self._send(200,json.dumps(gather(),ensure_ascii=False),"application/json; charset=utf-8")
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
                subprocess.Popen(["open",f"http://127.0.0.1:{PORT}/?v=1301"])
                return {"ok":True,"already_running":True,"pid":pid,"url":f"http://127.0.0.1:{PORT}/"}
        except Exception: pass
    p=subprocess.Popen([sys.executable,"seed_dashboard_v106.py","serve"],stdout=LOG.open("a"),stderr=LOG.open("a")); PID.write_text(str(p.pid)); subprocess.Popen(["open",f"http://127.0.0.1:{PORT}/?v=1301"]); return {"ok":True,"pid":p.pid,"url":f"http://127.0.0.1:{PORT}/"}
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
    return {"created_at":now(),"version":"v130.1-ui","ok":True,"alive":al,"pid":pid,"url":f"http://127.0.0.1:{PORT}/"}
if __name__=="__main__":
    a=sys.argv[1] if len(sys.argv)>1 else "status"
    if a=="serve": serve()
    elif a=="start": print(json.dumps(start(),indent=4,ensure_ascii=False))
    elif a=="stop": print(json.dumps(stop(),indent=4,ensure_ascii=False))
    else: print(json.dumps(status(),indent=4,ensure_ascii=False))
