import json, time, traceback
from datetime import datetime
from pathlib import Path
TRACE=Path("seed_trace_v95.jsonl"); ERR=Path("seed_errors_v95.jsonl"); ACT=Path("seed_actions_v95.jsonl")
def now(): return datetime.now().isoformat(timespec="seconds")
def write(path,row):
    row.setdefault("created_at",now()); row.setdefault("version","v95.0.0")
    with path.open("a") as f: f.write(json.dumps(row,ensure_ascii=False)+"\n")
def trace(event, **data): row={"event":event,**data}; write(TRACE,row); return row
def action(name, risk="observe", ok=True, **data): row={"action":name,"risk":risk,"ok":ok,**data}; write(ACT,row); return row
def error(where, exc=None, **data): row={"where":where,"error":str(exc),"traceback":traceback.format_exc(),**data}; write(ERR,row); return row
def read(path,limit=50):
    if not path.exists(): return []
    out=[]
    for line in path.read_text(errors="ignore").splitlines()[-limit:]:
        try: out.append(json.loads(line))
        except Exception: pass
    return out
def status(): return {"created_at":now(),"version":"v95.0.0","ok":True,"trace":len(read(TRACE,99999)),"errors":len(read(ERR,99999)),"actions":len(read(ACT,99999)),"latest_trace":read(TRACE,5),"latest_errors":read(ERR,5)}
if __name__=="__main__":
    import sys
    if len(sys.argv)>1 and sys.argv[1]=="log": print(trace(sys.argv[2] if len(sys.argv)>2 else "manual", message=" ".join(sys.argv[3:])))
    else: print(json.dumps(status(),indent=4,ensure_ascii=False))
