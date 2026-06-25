import json, importlib.util
from datetime import datetime
from pathlib import Path
STATE=Path("seed_wake_engine_v93_state.json")
def now(): return datetime.now().isoformat(timespec="seconds")
def available(): return {"openwakeword":importlib.util.find_spec("openwakeword") is not None,"pvporcupine":importlib.util.find_spec("pvporcupine") is not None,"fallback_v91":Path("seed_wake_context_v91.py").exists()}
def chosen():
    a=available()
    if a["openwakeword"]: return "openwakeword"
    if a["pvporcupine"]: return "pvporcupine"
    return "fallback_v91_contextual_wake"
def start():
    if chosen()=="fallback_v91_contextual_wake":
        try:
            from seed_wake_context_v91 import start_daemon
            r=start_daemon()
        except Exception as e: r={"ok":False,"error":str(e)}
    else: r={"ok":False,"error":"native wake engine detected but runner not installed; fallback recommended"}
    data={"created_at":now(),"version":"v93.0.0","engine":chosen(),"result":r}; STATE.write_text(json.dumps(data,indent=4)); return data
def stop():
    try:
        from seed_wake_context_v91 import stop_daemon
        r=stop_daemon()
    except Exception as e: r={"ok":False,"error":str(e)}
    return {"created_at":now(),"version":"v93.0.0","ok":r.get("ok",False),"result":r}
def status(): return {"created_at":now(),"version":"v93.0.0","ok":True,"available":available(),"chosen":chosen()}
if __name__=="__main__":
    import sys
    a=sys.argv[1] if len(sys.argv)>1 else "status"
    print(json.dumps(start() if a=="start" else stop() if a=="stop" else status(),indent=4))
