import json
import subprocess
import sys
from pathlib import Path
from datetime import datetime

def now():
    return datetime.now().isoformat(timespec="seconds")

def run_gate():
    checks = []
    for module in ["seed_dashboard_v106.py", "seed_v1061_dashboard_gate.py"]:
        proc = subprocess.run([sys.executable, "-m", "py_compile", module], capture_output=True, text=True, timeout=30)
        checks.append({"module": module, "ok": proc.returncode == 0, "stderr": proc.stderr[-1000:]})

    modules_ok = all(c["ok"] for c in checks)

    try:
        import seed_dashboard_v106 as dash
        html_ok = "Seed Dashboard" in dash.HTML and "System health" in dash.HTML and "grid" in dash.HTML
        api = dash.view_model()
        api_ok = api.get("total", 0) >= 10 and "cards" in api
        status_ok = dash.status().get("ok") is True
        details = {"api_total": api.get("total"), "api_ok_count": api.get("ok_count"), "status": dash.status()}
    except Exception as e:
        html_ok = False
        api_ok = False
        status_ok = False
        details = {"error": str(e)}

    report = {
        "created_at": now(),
        "version": "v106.1.0",
        "ready": modules_ok and html_ok and api_ok and status_ok,
        "modules_ok": modules_ok,
        "html_ok": html_ok,
        "api_ok": api_ok,
        "status_ok": status_ok,
        "checks": checks,
        "details": details,
    }
    Path("seed_v1061_dashboard_gate_report.json").write_text(json.dumps(report, indent=4, ensure_ascii=False))
    return report

def show():
    r = run_gate()
    print("\n=== SEED v106.1 DASHBOARD UI GATE ===")
    print(f"Ready: {r['ready']}")
    print(f"Modules OK: {r['modules_ok']}")
    print(f"HTML OK: {r['html_ok']}")
    print(f"API OK: {r['api_ok']}")
    print(f"Status OK: {r['status_ok']}")
    print(f"Details: {r['details']}")

if __name__ == "__main__":
    show()
