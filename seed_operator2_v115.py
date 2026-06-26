import json, subprocess
from datetime import datetime
def now(): return datetime.now().isoformat(timespec="seconds")
def active_window():
    try:
        p=subprocess.run(["osascript","-e",'tell application "System Events" to get name of first application process whose frontmost is true'],capture_output=True,text=True,timeout=5); return {"ok":p.returncode==0,"app":p.stdout.strip()}
    except Exception as e:return {"ok":False,"error":str(e)}
def plan(a,t=''): return {"ok":True,"action":a,"target":t,"risk":"observe" if a in {"status","active-window"} else "risky","steps":["classify","approve if needed","execute","log"]}
def run(a,t='',approved=False):
    import seed_safety_ledger_v94 as s; dec=s.decision("operator2 "+a,target=t,approved=approved)
    if not dec.get("allowed"): return {"ok":False,"blocked":True,"plan":plan(a,t),"decision":dec}
    if a=="active-window": res=active_window()
    else:
        import seed_operator_v100 as op; res=op.run({"open-url":"open-url","open-app":"open-app","speak":"speak","type":"type","press":"press","screenshot":"screenshot"}.get(a,a),t,approved)
    return {"created_at":now(),"version":"v115.0.0","ok":res.get("ok",False),"decision":dec,"result":res}
def status(): return {"created_at":now(),"version":"v115.0.0","ok":True,"actions":["active-window","open-url","open-app","speak","type --yes","press --yes"]}
if __name__=="__main__":
    import sys; a=sys.argv[1] if len(sys.argv)>1 else "status"; print(json.dumps(status() if a=="status" else run(a," ".join(x for x in sys.argv[2:] if x!='--yes'),"--yes" in sys.argv),indent=4,ensure_ascii=False))
