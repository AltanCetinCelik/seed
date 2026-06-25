import json
import subprocess
import sys
from pathlib import Path
from datetime import datetime

MODULES = [
    "seed_vision_v98.py",
    "seed_wake_reliability_v107.py",
    "seed_action_approval_v107.py",
    "seed_supervisor_stress_v107.py",
    "seed_eval_v107.py",
    "seed_dashboard_v106.py",
    "seed_v107_hardening_gate.py",
]

def now():
    return datetime.now().isoformat(timespec="seconds")

def comp(module):
    proc = subprocess.run([sys.executable, "-m", "py_compile", module], capture_output=True, text=True, timeout=30)
    return {"module": module, "ok": proc.returncode == 0, "stderr": proc.stderr[-1200:]}

def run_gate():
    checks = [comp(m) for m in MODULES]
    modules_ok = all(c["ok"] for c in checks)
    details = {}

    try:
        import seed_vision_v98 as vision
        vs = vision.status()
        rt = vs.get("ambient_vision", {}).get("runtime_status", {})
        saved = rt.get("saved", {}) if isinstance(rt, dict) else {}
        vision_ok = not (saved.get("ok") and "seed_vision_v98.py once" in json.dumps(saved).lower())
        details["vision"] = {"ok": vision_ok, "runtime_cleaned": rt.get("stale_display_cleaned", False) if isinstance(rt, dict) else False}
    except Exception as e:
        vision_ok = False
        details["vision_error"] = str(e)

    try:
        import seed_wake_reliability_v107 as wake
        wake_ok = wake.run_tests().get("ok") is True
        details["wake"] = wake.run_tests().get("results", {})
    except Exception as e:
        wake_ok = False
        details["wake_error"] = str(e)

    try:
        import seed_eval_v107 as ev
        er = ev.run()
        eval_ok = er.get("ready") is True
        details["eval"] = er.get("tests", {})
    except Exception as e:
        eval_ok = False
        details["eval_error"] = str(e)

    try:
        import seed_supervisor_stress_v107 as stress
        dr = stress.dry()
        stress_ok = dr.get("ok") is True
        details["stress_dry"] = dr
    except Exception as e:
        stress_ok = False
        details["stress_error"] = str(e)

    try:
        import seed_action_approval_v107 as approval
        ar = approval.status()
        approval_ok = ar.get("ok") is True and "pending_count" in ar
        details["approval"] = {"pending_count": ar.get("pending_count"), "ok": ar.get("ok")}
    except Exception as e:
        approval_ok = False
        details["approval_error"] = str(e)

    try:
        import seed_dashboard_v106 as dash
        html_ok = "Approval Center" in dash.HTML and "v106.3" in dash.HTML
        api = dash.view_model()
        dash_ok = html_ok and api.get("total", 0) >= 14
        details["dashboard"] = {"html_ok": html_ok, "total": api.get("total"), "ok_count": api.get("ok_count")}
    except Exception as e:
        dash_ok = False
        details["dashboard_error"] = str(e)

    report = {
        "created_at": now(),
        "version": "v107.0.0",
        "ready": modules_ok and vision_ok and wake_ok and eval_ok and stress_ok and approval_ok and dash_ok,
        "modules_ok": modules_ok,
        "vision_ok": vision_ok,
        "wake_ok": wake_ok,
        "eval_ok": eval_ok,
        "stress_dry_ok": stress_ok,
        "approval_ok": approval_ok,
        "dashboard_ok": dash_ok,
        "checks": checks,
        "details": details,
    }
    Path("seed_v107_hardening_gate_report.json").write_text(json.dumps(report, indent=4, ensure_ascii=False))
    return report

def show():
    r = run_gate()
    print("\n=== SEED v107 REAL HARDENING GATE ===")
    print(f"Ready: {r['ready']}")
    print(f"Modules OK: {r['modules_ok']}")
    print(f"Vision OK: {r['vision_ok']}")
    print(f"Wake OK: {r['wake_ok']}")
    print(f"Eval OK: {r['eval_ok']}")
    print(f"Stress Dry OK: {r['stress_dry_ok']}")
    print(f"Approval OK: {r['approval_ok']}")
    print(f"Dashboard OK: {r['dashboard_ok']}")
    print(f"Details: {r['details']}")

if __name__ == "__main__":
    show()
