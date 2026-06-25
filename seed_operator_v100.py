import json
from datetime import datetime
def now(): return datetime.now().isoformat(timespec="seconds")
def run(action,arg="",approved=False):
    try:
        from seed_safety_ledger_v94 import decision
        dec=decision("operator "+action,target=arg,approved=approved)
        if not dec.get("allowed"): return {"ok":False,"blocked":True,"decision":dec}
        import seed_mac_body_v88 as b
        r=b.open_app(arg) if action=="open-app" else b.open_url(arg) if action=="open-url" else b.screenshot() if action=="screenshot" else b.speak(arg) if action=="speak" else b.type_text(arg) if action=="type" else b.press(arg) if action=="press" else {"ok":False,"error":"unknown"}
        return {"created_at":now(),"version":"v100.0.0","ok":r.get("ok",False),"decision":dec,"result":r}
    except Exception as e: return {"created_at":now(),"version":"v100.0.0","ok":False,"error":str(e)}
def status(): return {"created_at":now(),"version":"v100.0.0","ok":True,"actions":["open-app","open-url","screenshot","speak","type --yes","press --yes"],"safety":"v94 ledger"}
if __name__=="__main__":
    import sys
    a=sys.argv[1] if len(sys.argv)>1 else "status"; approved="--yes" in sys.argv; args=[x for x in sys.argv[2:] if x!="--yes"]
    print(json.dumps(status() if a=="status" else run(a," ".join(args),approved),indent=4,ensure_ascii=False))
