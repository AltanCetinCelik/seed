import json,subprocess,sys,time
from pathlib import Path
from datetime import datetime
MODULES=["seed_proactive_rhythm_v108.py","seed_action_approval_v107.py","seed_native_wake_v109.py","seed_stt_v110.py","seed_tts_v111.py","seed_repo_bootstrap_v1221.py","seed_v1221_reality_gate.py"]
def now(): return datetime.now().isoformat(timespec="seconds")
def comp(m):
    p=subprocess.run([sys.executable,"-m","py_compile",m],capture_output=True,text=True,timeout=30); return {"module":m,"ok":p.returncode==0,"stderr":p.stderr[-1000:]}
def run_gate():
    checks=[comp(m) for m in MODULES]; modules_ok=all(c["ok"] for c in checks); details={}; tests=[]
    def safe(name,fn):
        try:
            d=fn(); details[name]=d; tests.append(bool(d.get("ok",True)))
        except Exception as e: details[name]={"ok":False,"error":str(e)}; tests.append(False)
    safe("approval_cleanup",lambda: __import__("seed_action_approval_v107",fromlist=["cleanup_stale"]).cleanup_stale())
    safe("approval_status",lambda: __import__("seed_action_approval_v107",fromlist=["status"]).status())
    safe("wake",lambda: __import__("seed_native_wake_v109",fromlist=["test"]).test())
    safe("stt",lambda: __import__("seed_stt_v110",fromlist=["test"]).test())
    safe("tts",lambda: __import__("seed_tts_v111",fromlist=["status"]).status())
    safe("repo_bootstrap",lambda: __import__("seed_repo_bootstrap_v1221",fromlist=["status"]).status())
    import seed_proactive_rhythm_v108 as p
    st=p.start(False); time.sleep(.6); mid=p.status(); sp=p.stop()
    details["proactive_daemon"]={"start":st,"mid":mid,"stop":sp,"ok":st.get("ok") and mid.get("alive") is True and sp.get("ok") is True}
    tests.append(details["proactive_daemon"]["ok"])
    report={"created_at":now(),"version":"v122.1.0","ready":modules_ok and all(tests),"modules_ok":modules_ok,"tests_ok":all(tests),"checks":checks,"details":details}
    Path("seed_v1221_reality_gate_report.json").write_text(json.dumps(report,indent=4,ensure_ascii=False)); return report
def show():
    r=run_gate()
    print("\n=== SEED v122.1 REALITY COMPLETION GATE ===")
    print(f"Ready: {r['ready']}")
    print(f"Modules OK: {r['modules_ok']}")
    print(f"Tests OK: {r['tests_ok']}")
    print(f"Pending approvals: {r['details'].get('approval_status',{}).get('pending_count')}")
    print(f"Wake route: {r['details'].get('wake',{}).get('route')}")
    print(f"STT readiness: {r['details'].get('stt',{}).get('status',{}).get('readiness')}")
    print(f"Proactive alive test: {r['details'].get('proactive_daemon',{}).get('ok')}")
if __name__=="__main__": show()
