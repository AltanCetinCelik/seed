import json, subprocess, sys
from datetime import datetime
def now(): return datetime.now().isoformat(timespec="seconds")
def run(cmd,timeout=60):
    try:
        p=subprocess.run(cmd,capture_output=True,text=True,timeout=timeout); txt=(p.stdout or "").strip()
        try: data=json.loads(txt)
        except Exception: data={"raw":txt}
        return {"ok":p.returncode==0,"cmd":cmd,"data":data,"stderr":(p.stderr or "")[-1200:]}
    except Exception as e: return {"ok":False,"cmd":cmd,"error":str(e)}
def start_clean(include_ui=False):
    steps=[{"step":"pre_hygiene_scan","result":run([sys.executable,"seed_hygiene_center_v1362.py","scan"])},{"step":"start_seed","result":run([sys.executable,"seed_start.py","start"]+(["--ui"] if include_ui else []))},{"step":"post_hygiene_scan","result":run([sys.executable,"seed_hygiene_center_v1362.py","scan"])}]
    return {"created_at":now(),"version":"v136.2.0","ok":all(s["result"].get("ok") for s in steps),"steps":steps}
def stop_clean():
    steps=[{"step":"snapshot","result":run([sys.executable,"seed_hygiene_center_v1362.py","snapshot"])},{"step":"stop_seed","result":run([sys.executable,"seed_start.py","stop"])}]
    return {"created_at":now(),"version":"v136.2.0","ok":all(s["result"].get("ok") for s in steps),"steps":steps}
def status():
    a=run([sys.executable,"seed_start.py","status"]); b=run([sys.executable,"seed_hygiene_center_v1362.py","scan"])
    return {"created_at":now(),"version":"v136.2.0","ok":a.get("ok") and b.get("ok"),"seed_start":a,"hygiene":b}
if __name__=="__main__":
    cmd=sys.argv[1] if len(sys.argv)>1 else "status"
    if cmd=="start": print(json.dumps(start_clean("--ui" in sys.argv),indent=4,ensure_ascii=False))
    elif cmd=="stop": print(json.dumps(stop_clean(),indent=4,ensure_ascii=False))
    else: print(json.dumps(status(),indent=4,ensure_ascii=False))
