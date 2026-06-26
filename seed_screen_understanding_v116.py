import json,hashlib
from pathlib import Path
from datetime import datetime
STATE=Path("seed_screen_understanding_v116_state.json")
def now(): return datetime.now().isoformat(timespec="seconds")
def observe():
    import seed_operator2_v115 as op; aw=op.active_window(); fp=hashlib.sha1(json.dumps(aw,sort_keys=True).encode()).hexdigest()[:12]; prev={}
    if STATE.exists():
        try: prev=json.loads(STATE.read_text(errors='ignore'))
        except Exception: pass
    r={"created_at":now(),"version":"v116.0.0","ok":True,"fingerprint":fp,"changed":prev.get("fingerprint")!=fp,"active_window":aw,"privacy":"no raw screenshot saved"}; STATE.write_text(json.dumps(r,indent=4)); return r
def status(): return {"created_at":now(),"version":"v116.0.0","ok":True,"current":observe()}
if __name__=="__main__":
    import json; print(json.dumps(status(),indent=4,ensure_ascii=False))
