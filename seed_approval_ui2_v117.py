import json
from pathlib import Path
from datetime import datetime,timedelta
POLICY=Path("seed_approval_policy_v117.jsonl")
def now(): return datetime.now().isoformat(timespec="seconds")
def write(r):
    r.setdefault("created_at",now()); r.setdefault("version","v117.0.0")
    with POLICY.open("a") as f:f.write(json.dumps(r,ensure_ascii=False)+"\n")
    return r
def read():
    if not POLICY.exists(): return []
    out=[]
    for l in POLICY.read_text(errors='ignore').splitlines():
        try: out.append(json.loads(l))
        except Exception: pass
    return out
def approve_once(a): return {"ok":True,"policy":write({"kind":"approve_once","action":a})}
def approve_minutes(a,m=10): return {"ok":True,"policy":write({"kind":"approve_until","action":a,"until":(datetime.now()+timedelta(minutes=int(m))).isoformat(timespec='seconds')})}
def status():
    try:
        import seed_action_approval_v107 as aa; center=aa.status()
    except Exception as e:center={"ok":False,"error":str(e)}
    return {"created_at":now(),"version":"v117.0.0","ok":True,"policy_count":len(read()),"approval_center":center}
if __name__=="__main__":
    import sys; a=sys.argv[1] if len(sys.argv)>1 else "status"; print(json.dumps(approve_once(" ".join(sys.argv[2:])) if a=="once" else approve_minutes(sys.argv[2],sys.argv[3] if len(sys.argv)>3 else 10) if a=="minutes" else status(),indent=4,ensure_ascii=False))
