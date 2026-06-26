import json,platform
from pathlib import Path
from datetime import datetime
CFG=Path("seed_pi_satellite_v126_config.json"); HB=Path("seed_pi_satellite_v126_heartbeats.jsonl")
DEFAULT={"version":"v126.0.0","enabled":False,"mac_host":"127.0.0.1","wake_engine":"openWakeWord_or_v107_fallback","store_raw_audio":False}
def now(): return datetime.now().isoformat(timespec="seconds")
def cfg():
    if CFG.exists():
        try:
            d=DEFAULT.copy(); d.update(json.loads(CFG.read_text(errors="ignore"))); d["version"]="v126.0.0"; return d
        except Exception: pass
    CFG.write_text(json.dumps(DEFAULT,indent=4)); return DEFAULT.copy()
def heartbeat(status="alive"):
    row={"created_at":now(),"version":"v126.0.0","device":"pi_satellite","status":status}
    with HB.open("a") as f: f.write(json.dumps(row)+"\n")
    return {"ok":True,"heartbeat":row}
def write_agent():
    p=Path("seed_pi_satellite_agent_v126.py"); p.write_text('import json,platform; print(json.dumps({"ok":True,"device":"pi_satellite","platform":platform.platform(),"note":"stub; add openWakeWord later"},indent=4))\n'); p.chmod(0o755); return {"ok":True,"path":str(p)}
def status(): return {"created_at":now(),"version":"v126.0.0","ok":True,"config":cfg(),"agent":write_agent()}
if __name__=="__main__":
    import sys; print(json.dumps(heartbeat() if len(sys.argv)>1 and sys.argv[1]=="heartbeat" else write_agent() if len(sys.argv)>1 and sys.argv[1]=="write-agent" else status(),indent=4))
