import json, subprocess, sys
from pathlib import Path
from datetime import datetime

MODULES = [
    "seed_autonomy_policy_v13622.py",
    "seed_approval_autopilot_v13622.py",
    "seed_autonomy_panel_v13622.py",
    "seed_v13622_autonomy_gate.py"
]

def now():
    return datetime.now().isoformat(timespec="seconds")

def comp(m):
    p=subprocess.run([sys.executable,"-m","py_compile",m],capture_output=True,text=True,timeout=30)
    return {"module":m,"ok":p.returncode==0,"stderr":p.stderr[-1000:]}

def run_gate():
    checks=[comp(m) for m in MODULES]
    modules_ok=all(c["ok"] for c in checks)
    details={}
    try:
        import seed_autonomy_policy_v13622 as pol
        pt=pol.test()
        st=pol.status()
        details["policy_test"]=pt
        details["policy_status"]=st
        policy_ok=pt.get("ok") is True and st.get("mode") in {"trusted_local","operator_light","balanced","strict"}
    except Exception as e:
        policy_ok=False; details["policy_error"]=str(e)
    try:
        import seed_approval_autopilot_v13622 as auto
        at=auto.test()
        details["autopilot_test"]=at
        autopilot_ok=at.get("ok") is True
    except Exception as e:
        autopilot_ok=False; details["autopilot_error"]=str(e)
    try:
        import seed_autonomy_panel_v13622 as panel
        ps=panel.status()
        details["panel"]=ps
        panel_ok=ps.get("ok") is True
    except Exception as e:
        panel_ok=False; details["panel_error"]=str(e)
    report={
        "created_at":now(),
        "version":"v136.2.2",
        "ready":modules_ok and policy_ok and autopilot_ok and panel_ok,
        "modules_ok":modules_ok,
        "policy_ok":policy_ok,
        "autopilot_ok":autopilot_ok,
        "panel_ok":panel_ok,
        "checks":checks,
        "details":details
    }
    Path("seed_v13622_autonomy_gate_report.json").write_text(json.dumps(report,indent=4,ensure_ascii=False))
    return report

def show():
    r=run_gate()
    print("\n=== SEED v136.2.2 AUTONOMY / LESS APPROVALS GATE ===")
    print(f"Ready: {r['ready']}")
    print(f"Modules OK: {r['modules_ok']}")
    print(f"Policy OK: {r['policy_ok']}")
    print(f"Autopilot OK: {r['autopilot_ok']}")
    print(f"Panel OK: {r['panel_ok']}")
    try:
        print("Mode:", r["details"]["policy_status"]["mode"])
        print("Pending approvals:", r["details"]["autopilot_test"]["status"]["approval_status"].get("pending_count"))
    except Exception:
        pass

if __name__=="__main__":
    show()
