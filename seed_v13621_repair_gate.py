import json, subprocess, sys
from pathlib import Path
from datetime import datetime

MODULES = [
    "seed_hygiene_repair_v13621.py",
    "seed_hygiene_repair_panel_v13621.py",
    "seed_v13621_repair_gate.py"
]

def now():
    return datetime.now().isoformat(timespec="seconds")

def comp(m):
    p = subprocess.run([sys.executable, "-m", "py_compile", m], capture_output=True, text=True, timeout=30)
    return {"module": m, "ok": p.returncode == 0, "stderr": p.stderr[-1000:]}

def run_gate():
    checks = [comp(m) for m in MODULES]
    modules_ok = all(c["ok"] for c in checks)
    details = {}
    try:
        import seed_hygiene_repair_v13621 as r
        test = r.test()
        status = r.status()
        dry = r.safe_apply(False)
        details["test"] = test
        details["status_summary"] = status.get("scan_summary")
        details["dry_run_after"] = dry.get("after")
        repair_ok = test.get("ok") is True and dry.get("ok") is True
    except Exception as e:
        repair_ok = False
        details["repair_error"] = str(e)
    try:
        import seed_hygiene_repair_panel_v13621 as p
        ps = p.status()
        details["panel"] = ps
        panel_ok = ps.get("ok") is True
    except Exception as e:
        panel_ok = False
        details["panel_error"] = str(e)
    report = {
        "created_at": now(),
        "version": "v136.2.1",
        "ready": modules_ok and repair_ok and panel_ok,
        "modules_ok": modules_ok,
        "repair_ok": repair_ok,
        "panel_ok": panel_ok,
        "checks": checks,
        "details": details
    }
    Path("seed_v13621_repair_gate_report.json").write_text(json.dumps(report, indent=4, ensure_ascii=False))
    return report

def show():
    r = run_gate()
    print("\n=== SEED v136.2.1 ACTUAL HYGIENE REPAIR GATE ===")
    print(f"Ready: {r['ready']}")
    print(f"Modules OK: {r['modules_ok']}")
    print(f"Repair OK: {r['repair_ok']}")
    print(f"Panel OK: {r['panel_ok']}")
    s = r.get("details", {}).get("status_summary") or {}
    if s:
        print(f"Current score: {s.get('score')}/100")
        print(f"Approvals pending: {s.get('approval_pending')}")
        print(f"Test tasks: {s.get('test_tasks')}")
        print(f"Duplicate memory entries: {s.get('duplicate_memory_entries')}")

if __name__ == "__main__":
    show()
