import json, subprocess
from datetime import datetime
MODULES=["seed_fusion_lab_clean_v602.py","seed_model_real_mode_v61.py","seed_companion_shell_v62.py","seed_control_plane_product_v63.py","seed_memory_review_inbox_v64.py","seed_real_aider_loop_v65.py","seed_presence_operator_v66.py","seed_voice_push_to_talk_v67.py","seed_browser_use_adapter_v68.py","seed_multichannel_companion_v69.py","seed_one_of_a_kind_polish_v70.py","seed_control_plane_ui_v70.py","seed_v70_systems.py","seed_v70_gate.py","seed_v70_commands.py","seed_natural_intent_router_v70.py"]
def compile_module(m):
    p=subprocess.run(["python","-m","py_compile",m],capture_output=True,text=True); return {"module":m,"ok":p.returncode==0,"stderr":p.stderr[-2000:]}
def run_v70_gate():
    checks=[compile_module(m) for m in MODULES]; modules_ok=all(c["ok"] for c in checks); details={}
    try:
        from seed_v70_systems import build_v70_state; state=build_v70_state(); systems_ok=state.get("ok") is True and len(state.get("cards",[]))>=11; details["v70_state"]={"ok":state.get("ok"),"cards":len(state.get("cards",[])),"models":state.get("model_status"),"fusion":state.get("fusion_status")}
    except Exception as e: systems_ok=False; details["v70_state_error"]=str(e)
    try:
        from seed_control_plane_server import api_payload; v70=api_payload("/api/v70"); control_plane_ok=bool(v70); details["control_plane"]={"v70_api":bool(v70)}
    except Exception as e: control_plane_ok=False; details["control_plane_error"]=str(e)
    try:
        from seed_v60_gate import run_v60_gate; v60=run_v60_gate(); v60_ok=v60.get("ready") is True; details["v60"]={"ready":v60.get("ready")}
    except Exception as e: v60_ok=False; details["v60_error"]=str(e)
    report={"created_at":datetime.now().isoformat(timespec="seconds"),"version":"v70.0.0","ready":modules_ok and systems_ok and control_plane_ok and v60_ok,"modules_ok":modules_ok,"systems_ok":systems_ok,"control_plane_ok":control_plane_ok,"v60_ok":v60_ok,"module_checks":checks,"details":details}; open("seed_v70_gate_report.json","w").write(json.dumps(report,indent=4)); return report
def show_v70_gate():
    r=run_v70_gate(); print("\n=== SEED v70 MEGA FUSION GATE ==="); print(f"Ready: {r['ready']}"); print(f"Modules OK: {r['modules_ok']}"); print(f"Systems OK: {r['systems_ok']}"); print(f"Control Plane OK: {r['control_plane_ok']}"); print(f"v60 OK: {r['v60_ok']}"); print("\nDetails:"); [print(f"- {k}: {v}") for k,v in r["details"].items()]
if __name__=="__main__": show_v70_gate()
