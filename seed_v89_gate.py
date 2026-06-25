import json, subprocess, sys
from datetime import datetime
from pathlib import Path
MODULES=["seed_avatar_v89.py","seed_organism_notes_v89.py","seed_ambient_hearing_v89.py","seed_ambient_vision_v89.py","seed_organism_v89.py","seed_v89_systems.py","seed_v89_gate.py","seed_natural_intent_router_v89.py"]
def now(): return datetime.now().isoformat(timespec="seconds")
def comp(m):
    p=subprocess.run([sys.executable,"-m","py_compile",m],capture_output=True,text=True,timeout=30); return {"module":m,"ok":p.returncode==0,"stderr":p.stderr[-1000:]}
def run_v89_gate():
    checks=[comp(m) for m in MODULES]; modules_ok=all(c["ok"] for c in checks); details={}
    try:
        st=__import__("seed_v89_systems",fromlist=["build_v89_state"]).build_v89_state(); systems_ok=st.get("ok") is True and len(st.get("cards",[]))>=5; details["v89_state"]={"ok":st.get("ok"),"cards":len(st.get("cards",[]))}
    except Exception as e: systems_ok=False; details["state_error"]=str(e)
    try:
        ns=__import__("seed_organism_notes_v89",fromlist=["settings"]).settings(); privacy_ok=(ns.get("store_raw_audio") is False and ns.get("store_raw_screenshots") is False and ns.get("store_raw_transcripts") is False and ns.get("note_only_mode") is True); details["privacy"]=ns
    except Exception as e: privacy_ok=False; details["privacy_error"]=str(e)
    r={"created_at":now(),"version":"v89.0.0","ready":modules_ok and systems_ok and privacy_ok,"modules_ok":modules_ok,"systems_ok":systems_ok,"privacy_ok":privacy_ok,"module_checks":checks,"details":details}
    Path("seed_v89_gate_report.json").write_text(json.dumps(r,indent=4,ensure_ascii=False)); return r
def show_v89_gate():
    r=run_v89_gate(); print("\n=== SEED v89 ORGANISM GATE ==="); print(f"Ready: {r['ready']}"); print(f"Modules OK: {r['modules_ok']}"); print(f"Systems OK: {r['systems_ok']}"); print(f"Privacy OK: {r['privacy_ok']}"); print(f"Details: {r['details']}")
if __name__=="__main__": show_v89_gate()
