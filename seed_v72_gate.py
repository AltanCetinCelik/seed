import json, subprocess
from datetime import datetime
MODULES=["seed_presence_policy_v72.py","seed_friend_advice_ingestor_v72.py","seed_repo_pattern_extractor_v72.py","seed_avatar_state_v72.py","seed_presence_inbox_v72.py","seed_curiosity_engine_v72.py","seed_voice_session_v72.py","seed_v72_systems.py","seed_v72_gate.py","seed_v72_commands.py","seed_natural_intent_router_v72.py"]
def now(): return datetime.now().isoformat(timespec="seconds")
def comp(m):
    p=subprocess.run(["python","-m","py_compile",m],capture_output=True,text=True,timeout=30)
    return {"module":m,"ok":p.returncode==0,"stderr":p.stderr[-1200:]}
def run_v72_gate():
    checks=[comp(m) for m in MODULES]; modules_ok=all(x["ok"] for x in checks); details={}
    try:
        from seed_v72_systems import build_v72_state
        s=build_v72_state(); systems_ok=s.get("ok") is True and len(s.get("cards",[]))>=7; details["v72_state"]={"ok":s.get("ok"),"cards":len(s.get("cards",[]))}
    except Exception as e: systems_ok=False; details["v72_state_error"]=str(e)
    try:
        from seed_v70_gate import run_v70_gate
        v70=run_v70_gate(); v70_ok=v70.get("ready") is True; details["v70"]={"ready":v70.get("ready")}
    except Exception as e: v70_ok=False; details["v70_error"]=str(e)
    r={"created_at":now(),"version":"v72.0.0","ready":modules_ok and systems_ok and v70_ok,"modules_ok":modules_ok,"systems_ok":systems_ok,"v70_ok":v70_ok,"module_checks":checks,"details":details}
    open("seed_v72_gate_report.json","w").write(json.dumps(r,indent=4)); return r
def show_v72_gate():
    r=run_v72_gate(); print("\n=== SEED v72 PRESENCE MAX GATE ==="); print("Ready:",r["ready"]); print("Modules OK:",r["modules_ok"]); print("Systems OK:",r["systems_ok"]); print("v70 OK:",r["v70_ok"]); print("Details:",r["details"])
if __name__ == "__main__": show_v72_gate()
