import json
from pathlib import Path
from datetime import datetime
REG=Path("seed_mcp_registry_v119.json"); CALLS=Path("seed_mcp_calls_v119.jsonl")
DEFAULT={"version":"v119.0.0","enabled":False,"allow_execute":False,"local_only":True,"servers":{}}
def now(): return datetime.now().isoformat(timespec="seconds")
def registry():
    if REG.exists():
        try:
            d=DEFAULT.copy(); d.update(json.loads(REG.read_text(errors='ignore'))); d["version"]="v119.0.0"; return d
        except Exception: pass
    REG.write_text(json.dumps(DEFAULT,indent=4)); return DEFAULT.copy()
def register(n,cmd): d=registry(); d["servers"][n]={"command":cmd,"enabled":False,"risk":"risky"}; REG.write_text(json.dumps(d,indent=4)); return {"ok":True,"server":d["servers"][n]}
def scan(): return {"ok":True,"found":[str(p) for p in [Path('mcp.json'),Path('.mcp.json'),Path('mcp_servers.json')] if p.exists()],"registry":registry()}
def status(): return {"created_at":now(),"version":"v119.0.0","ok":True,"registry":registry(),"scan":scan()["found"]}
if __name__=="__main__":
    import sys; print(json.dumps(register(sys.argv[2]," ".join(sys.argv[3:])) if len(sys.argv)>1 and sys.argv[1]=="register" else scan() if len(sys.argv)>1 and sys.argv[1]=="scan" else status(),indent=4,ensure_ascii=False))
