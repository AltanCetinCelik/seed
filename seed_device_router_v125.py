import json,socket,platform
from pathlib import Path
from datetime import datetime
CFG=Path("seed_device_router_v125_devices.json")
DEFAULT={"version":"v125.0.0","devices":{"mac_main":{"role":"main_body","host":"127.0.0.1","platform":platform.platform(),"capabilities":["chat","dashboard","operator","memory","voice"]},"windows_worker":{"role":"gpu_worker","host":"","capabilities":["vision","coding","batch_rag"]},"pi_satellite":{"role":"room_satellite","host":"","capabilities":["wake","listen","sensor"]}}}
def now(): return datetime.now().isoformat(timespec="seconds")
def cfg():
    if CFG.exists():
        try:
            d=DEFAULT.copy(); d.update(json.loads(CFG.read_text(errors="ignore"))); d["version"]="v125.0.0"; return d
        except Exception: pass
    CFG.write_text(json.dumps(DEFAULT,indent=4,ensure_ascii=False)); return DEFAULT.copy()
def register(n,role,host,caps):
    d=cfg(); d["devices"][n]={"role":role,"host":host,"capabilities":[x.strip() for x in caps.split(",") if x.strip()]}; CFG.write_text(json.dumps(d,indent=4,ensure_ascii=False)); return {"ok":True,"device":d["devices"][n]}
def route(task):
    t=task.lower()
    dev="pi_satellite" if any(x in t for x in ["wake","listen","room","sensor"]) else "windows_worker" if any(x in t for x in ["gpu","vision","batch","heavy","windows"]) else "mac_main"
    return {"ok":True,"created_at":now(),"version":"v125.0.0","task":task,"device":dev,"device_info":cfg()["devices"].get(dev,{})}
def status(): return {"created_at":now(),"version":"v125.0.0","ok":True,"devices":cfg()["devices"]}
if __name__=="__main__":
    import sys
    a=sys.argv[1] if len(sys.argv)>1 else "status"
    if a=="register": print(json.dumps(register(sys.argv[2],sys.argv[3],sys.argv[4],sys.argv[5] if len(sys.argv)>5 else ""),indent=4,ensure_ascii=False))
    elif a=="route": print(json.dumps(route(" ".join(sys.argv[2:])),indent=4,ensure_ascii=False))
    else: print(json.dumps(status(),indent=4,ensure_ascii=False))
