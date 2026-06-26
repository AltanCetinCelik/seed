import json,subprocess,time,re
from pathlib import Path
from datetime import datetime
EVENTS=Path("seed_project_memory_v114.jsonl")
def now(): return datetime.now().isoformat(timespec="seconds")
def write(r):
    r.setdefault("event_id",f"pm_{int(time.time()*1000)}"); r.setdefault("created_at",now()); r.setdefault("version","v114.0.0")
    with EVENTS.open("a") as f:f.write(json.dumps(r,ensure_ascii=False)+"\n")
    return r
def read():
    if not EVENTS.exists(): return []
    out=[]
    for l in EVENTS.read_text(errors="ignore").splitlines():
        try: out.append(json.loads(l))
        except Exception: pass
    return out
def record(kind,summary,outcome='unknown'): return {"ok":True,"event":write({"kind":kind,"summary":summary,"outcome":outcome})}
def gate(action):
    warns=[e for e in read() if e.get("outcome") in {"failed","avoid"} and any(w in action.lower() for w in e.get("summary","").lower().split() if len(w)>4)]
    return {"ok":True,"allowed":True,"warning_count":len(warns),"warnings":warns[:5]}
def git_status():
    try:
        p=subprocess.run(["git","status","--short"],capture_output=True,text=True,timeout=20); return {"ok":p.returncode==0,"stdout":p.stdout}
    except Exception as e:return {"ok":False,"error":str(e)}
def status(): return {"created_at":now(),"version":"v114.0.0","ok":True,"events":len(read()),"git":git_status(),"latest":read()[-5:]}
def test(): return {"ok":gate("safe dashboard status")["ok"]}
if __name__=="__main__":
    import sys
    a=sys.argv[1] if len(sys.argv)>1 else "status"
    print(json.dumps(record(a," ".join(sys.argv[2:])) if a in {"fix","decision","mistake"} else gate(" ".join(sys.argv[2:])) if a=="gate" else test() if a=="test" else status(),indent=4,ensure_ascii=False))
