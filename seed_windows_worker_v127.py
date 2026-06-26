import json,time,platform
from pathlib import Path
from datetime import datetime
CFG=Path("seed_windows_worker_v127_config.json"); JOBS=Path("seed_windows_worker_v127_jobs.jsonl")
DEFAULT={"version":"v127.0.0","enabled":False,"host":"","capabilities":["gpu_vision","coding","batch_rag","long_research"],"transport":"future_http_or_shared_folder"}
def now(): return datetime.now().isoformat(timespec="seconds")
def cfg():
    if CFG.exists():
        try:
            d=DEFAULT.copy(); d.update(json.loads(CFG.read_text(errors="ignore"))); d["version"]="v127.0.0"; return d
        except Exception: pass
    CFG.write_text(json.dumps(DEFAULT,indent=4)); return DEFAULT.copy()
def submit(kind,prompt):
    row={"job_id":f"winjob_{int(time.time()*1000)}","kind":kind,"prompt":prompt,"status":"queued","created_at":now(),"version":"v127.0.0"}
    with JOBS.open("a") as f: f.write(json.dumps(row,ensure_ascii=False)+"\n")
    return {"ok":True,"job":row}
def jobs():
    if not JOBS.exists(): return []
    out=[]
    for l in JOBS.read_text(errors="ignore").splitlines()[-30:]:
        try: out.append(json.loads(l))
        except Exception: pass
    return out
def write_stub():
    p=Path("seed_windows_worker_agent_v127.py"); p.write_text('import json,platform; print(json.dumps({"ok":True,"worker":"windows","platform":platform.platform(),"note":"no remote execution by default"},indent=4))\n'); return {"ok":True,"path":str(p)}
def status(): return {"created_at":now(),"version":"v127.0.0","ok":True,"config":cfg(),"jobs":jobs(),"worker_stub":write_stub()}
if __name__=="__main__":
    import sys; print(json.dumps(submit(sys.argv[2]," ".join(sys.argv[3:])) if len(sys.argv)>1 and sys.argv[1]=="submit" else status(),indent=4,ensure_ascii=False))
