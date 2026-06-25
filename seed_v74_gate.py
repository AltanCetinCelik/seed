import json, subprocess
from datetime import datetime
MODULES=["seed_embodied_state_v74.py","seed_avatar_panel_v74.py","seed_memory_actions_v74.py","seed_action_tasks_v74.py","seed_embodied_companion_server_v74.py","seed_v74_systems.py","seed_v74_gate.py","seed_v74_commands.py","seed_natural_intent_router_v74.py"]
def now_timestamp(): return datetime.now().isoformat(timespec="seconds")
def compile_module(m):
    p=subprocess.run(["python","-m","py_compile",m],capture_output=True,text=True,timeout=30)
    return {"module":m,"ok":p.returncode==0,"stderr":p.stderr[-1600:]}
def run_v74_gate():
    checks=[compile_module(m) for m in MODULES]; modules_ok=all(c["ok"] for c in checks); details={}
    try:
        from seed_v74_systems import build_v74_state
        state=build_v74_state(); systems_ok=state.get("ok") is True and len(state.get("cards",[]))>=6; details["v74_state"]={"ok":state.get("ok"),"cards":len(state.get("cards",[]))}
    except Exception as e: systems_ok=False; details["v74_state_error"]=str(e)
    try:
        from seed_v731_gate import run_v731_gate
        v731=run_v731_gate(); v731_ok=v731.get("ready") is True; details["v731"]={"ready":v731.get("ready")}
    except Exception as e: v731_ok=False; details["v731_error"]=str(e)
    report={"created_at":now_timestamp(),"version":"v74.0.0","ready":modules_ok and systems_ok and v731_ok,"modules_ok":modules_ok,"systems_ok":systems_ok,"v731_ok":v731_ok,"module_checks":checks,"details":details}
    open("seed_v74_gate_report.json","w").write(json.dumps(report,indent=4)); return report
def show_v74_gate():
    r=run_v74_gate(); print("\n=== SEED v74 EMBODIED COMPANION GATE ==="); print("Ready:",r["ready"]); print("Modules OK:",r["modules_ok"]); print("Systems OK:",r["systems_ok"]); print("v73.1 OK:",r["v731_ok"]); print("Details:",r["details"])
if __name__=="__main__": show_v74_gate()
