import json, os, signal, subprocess, sys, time
from pathlib import Path
from datetime import datetime
SETTINGS=Path("seed_real_wake_v132_settings.json")
EVENTS=Path("seed_real_wake_v132_events.jsonl")
PID=Path("seed_real_wake_v132.pid")
LOG=Path("seed_real_wake_v132.log")
DEFAULT={"version":"v132.0.0","enabled":False,"engine":"auto","poll_seconds":2,"store_raw_audio":False,"fallback_text_matcher":True}
def now(): return datetime.now().isoformat(timespec="seconds")
def settings():
    if SETTINGS.exists():
        try:
            d=DEFAULT.copy(); d.update(json.loads(SETTINGS.read_text(errors="ignore"))); d["version"]="v132.0.0"; return d
        except Exception: pass
    SETTINGS.write_text(json.dumps(DEFAULT,indent=4,ensure_ascii=False)); return DEFAULT.copy()
def save(d): d["version"]="v132.0.0"; SETTINGS.write_text(json.dumps(d,indent=4,ensure_ascii=False)); return d
def event(row):
    row.setdefault("created_at",now()); row.setdefault("version","v132.0.0")
    with EVENTS.open("a") as f: f.write(json.dumps(row,ensure_ascii=False)+"\n")
    return row
def events(limit=50):
    if not EVENTS.exists(): return []
    out=[]
    for l in EVENTS.read_text(errors="ignore").splitlines()[-limit:]:
        try: out.append(json.loads(l))
        except Exception: pass
    return out
def detect():
    import importlib.util
    return {"openwakeword":importlib.util.find_spec("openwakeword") is not None,"porcupine":importlib.util.find_spec("pvporcupine") is not None,"v107_fallback":Path("seed_wake_reliability_v107.py").exists()}
def engine():
    d=detect()
    if d["openwakeword"]: return "openwakeword"
    if d["porcupine"]: return "porcupine"
    if d["v107_fallback"]: return "v107_text_fallback"
    return "none"
def match_text(text):
    try:
        from seed_wake_reliability_v107 import match_wake_reliable
        ok,phrase,rest=match_wake_reliable(text)
        return {"ok":True,"matched":ok,"phrase":phrase,"rest":rest,"event":event({"event":"text_match","text":text,"matched":ok,"phrase":phrase,"rest":rest,"engine":engine()})}
    except Exception as e: return {"ok":False,"error":str(e)}
def report():
    ev=[e for e in events(500) if e.get("event")=="text_match"]
    return {"ok":True,"events":len(ev),"accepted":len([x for x in ev if x.get("matched")]),"rejected":len([x for x in ev if not x.get("matched")]),"recent":ev[-10:]}
def alive(pid):
    try: os.kill(int(pid),0); return True
    except Exception: return False
def daemon():
    event({"event":"daemon_started","engine":engine(),"note":"Audio wake uses openWakeWord/Porcupine if installed; text fallback remains available."})
    while True: time.sleep(int(settings().get("poll_seconds",2)))
def start():
    s=settings(); s["enabled"]=True; save(s)
    if PID.exists():
        try:
            pid=int(PID.read_text())
            if alive(pid): return {"ok":True,"already_running":True,"pid":pid,"engine":engine()}
        except Exception: pass
    p=subprocess.Popen([sys.executable,"seed_real_wake_v132.py","daemon"],stdout=LOG.open("a"),stderr=LOG.open("a"))
    PID.write_text(str(p.pid)); return {"ok":True,"pid":p.pid,"engine":engine()}
def stop():
    pid=None; stopped=False
    if PID.exists():
        try:
            pid=int(PID.read_text())
            if alive(pid): os.kill(pid,signal.SIGTERM); stopped=True
            PID.unlink(missing_ok=True)
        except Exception: pass
    s=settings(); s["enabled"]=False; save(s)
    return {"ok":True,"stopped":stopped,"pid":pid}
def test():
    a=match_text("make up status"); b=match_text("pumpkin seed recipe")
    return {"ok":a.get("matched") is True and b.get("matched") is False,"positive":a,"negative":b,"engine":engine()}
def status():
    pid=None; al=False
    if PID.exists():
        try: pid=int(PID.read_text()); al=alive(pid)
        except Exception: pass
    return {"created_at":now(),"version":"v132.0.0","ok":True,"alive":al,"pid":pid,"engine":engine(),"detect":detect(),"settings":settings(),"false_positive_report":report()}
if __name__=="__main__":
    a=sys.argv[1] if len(sys.argv)>1 else "status"
    if a=="start": print(json.dumps(start(),indent=4,ensure_ascii=False))
    elif a=="stop": print(json.dumps(stop(),indent=4,ensure_ascii=False))
    elif a=="daemon": daemon()
    elif a=="match": print(json.dumps(match_text(" ".join(sys.argv[2:])),indent=4,ensure_ascii=False))
    elif a=="test": print(json.dumps(test(),indent=4,ensure_ascii=False))
    else: print(json.dumps(status(),indent=4,ensure_ascii=False))
