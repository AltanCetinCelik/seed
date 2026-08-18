import json, subprocess, sys
from pathlib import Path
from datetime import datetime
MODULES=["seed_supervisor_v92.py","seed_wake_engine_v93.py","seed_safety_ledger_v94.py","seed_trace_v95.py","seed_memory_garden2_v96.py","seed_tool_bridge_v97.py","seed_vision_v98.py","seed_tasks_v99.py","seed_operator_v100.py","seed_coder_v101.py","seed_voice_v102.py","seed_device_body_v103.py","seed_rag_v104.py","seed_doctor_v105.py","seed_dashboard_v106.py","seed_eval_v107.py","seed_mega_v92_106.py"]
def now(): return datetime.now().isoformat(timespec="seconds")
def comp(m):
    p=subprocess.run([sys.executable,"-m","py_compile",m],capture_output=True,text=True,timeout=30); return {"module":m,"ok":p.returncode==0,"stderr":p.stderr[-1000:]}
def run_gate():
    checks=[comp(m) for m in MODULES]; modules_ok=all(c["ok"] for c in checks)
    import seed_safety_ledger_v94 as s
    dangerous=s.classify("shell","rm -rf /")["risk"]=="dangerous"
    safe=s.decision("open url",target="https://example.com").get("allowed") is True
    import seed_supervisor_v92 as sup
    cards=len(sup.supervisor_status().get("cards",[])); supervisor=cards>=10
    r={"created_at":now(),"version":"v92-v106.0.0","ready":modules_ok and dangerous and safe and supervisor,"modules_ok":modules_ok,"dangerous_block_test_ok":dangerous,"safe_action_test_ok":safe,"supervisor_ok":supervisor,"cards":cards,"module_checks":checks}
    Path("seed_v92_106_gate_report.json").write_text(json.dumps(r,indent=4,ensure_ascii=False)); return r
def show():
    r=run_gate(); print("\n=== SEED v92-v106 MEGA GATE ==="); print(f"Ready: {r['ready']}"); print(f"Modules OK: {r['modules_ok']}"); print(f"Dangerous Block Test OK: {r['dangerous_block_test_ok']}"); print(f"Safe Action Test OK: {r['safe_action_test_ok']}"); print(f"Supervisor OK: {r['supervisor_ok']}"); print(f"Cards: {r['cards']}")
if __name__=="__main__": show()
