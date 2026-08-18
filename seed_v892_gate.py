import json, subprocess, sys
from datetime import datetime
from pathlib import Path

MODULES = ["seed_organism_notes_v89.py", "seed_avatar_v89.py", "seed_organism_v89.py", "seed_v892_gate.py"]

def now():
    return datetime.now().isoformat(timespec="seconds")

def comp(m):
    p=subprocess.run([sys.executable,"-m","py_compile",m],capture_output=True,text=True,timeout=30)
    return {"module":m,"ok":p.returncode==0,"stderr":p.stderr[-1000:]}

def run_v892_gate():
    checks=[comp(m) for m in MODULES]
    modules_ok=all(c["ok"] for c in checks)
    details={}
    try:
        notes=__import__("seed_organism_notes_v89",fromlist=["is_low_value_vision","is_generic_question","settings"])
        low_ok=notes.is_low_value_vision("A Firefox window is open, displaying the Person of Interest show.", {"active_window":{"app":"firefox","title":"Person of Interest"}}) is True
        generic_q_ok=notes.is_generic_question("What is User doing on the Mac?") is True
        privacy=notes.settings()
        privacy_ok=privacy.get("store_raw_audio") is False and privacy.get("store_raw_screenshots") is False and privacy.get("store_raw_transcripts") is False
        details={"low_value_filter_ok":low_ok,"generic_question_filter_ok":generic_q_ok,"privacy":privacy}
    except Exception as e:
        low_ok=False; generic_q_ok=False; privacy_ok=False; details={"error":str(e)}
    r={"created_at":now(),"version":"v89.2.0","ready":modules_ok and low_ok and generic_q_ok and privacy_ok,"modules_ok":modules_ok,"low_value_filter_ok":low_ok,"generic_question_filter_ok":generic_q_ok,"privacy_ok":privacy_ok,"module_checks":checks,"details":details}
    Path("seed_v892_gate_report.json").write_text(json.dumps(r,indent=4,ensure_ascii=False))
    return r

def show_v892_gate():
    r=run_v892_gate()
    print("\n=== SEED v89.2 ORGANISM FILTER GATE ===")
    print(f"Ready: {r['ready']}")
    print(f"Modules OK: {r['modules_ok']}")
    print(f"Low Value Filter OK: {r['low_value_filter_ok']}")
    print(f"Generic Question Filter OK: {r['generic_question_filter_ok']}")
    print(f"Privacy OK: {r['privacy_ok']}")
    print(f"Details: {r['details']}")

if __name__=="__main__": show_v892_gate()
