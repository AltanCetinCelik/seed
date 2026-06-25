import json, platform, socket
from pathlib import Path
from datetime import datetime
DEV=Path("seed_devices_v103.json")
def now(): return datetime.now().isoformat(timespec="seconds")
def load():
    if DEV.exists():
        try: return json.loads(DEV.read_text(errors="ignore"))
        except Exception: pass
    return {"version":"v103.0.0","devices":{}}
def add_current(role="mac_main_body"):
    d=load(); name=socket.gethostname(); d["devices"][name]={"role":role,"platform":platform.platform(),"last_seen":now()}; DEV.write_text(json.dumps(d,indent=4)); return {"ok":True,"device":name}
def status(): add_current(); return {"created_at":now(),"version":"v103.0.0","ok":True,"devices":load()["devices"]}
if __name__=="__main__":
    import json; print(json.dumps(status(),indent=4))
