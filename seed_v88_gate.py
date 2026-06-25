import json
import subprocess
import sys
from datetime import datetime
from pathlib import Path

MODULES = [
    "seed_wake_fast_v872.py",
    "seed_mac_body_v88.py",
    "seed_mac_body_router_v88.py",
    "seed_body_alive_v88.py",
    "seed_v88_systems.py",
    "seed_v88_gate.py",
    "seed_natural_intent_router_v88.py",
]

def now():
    return datetime.now().isoformat(timespec="seconds")

def compile_module(module):
    proc = subprocess.run([sys.executable, "-m", "py_compile", module], capture_output=True, text=True, timeout=30)
    return {"module": module, "ok": proc.returncode == 0, "stderr": proc.stderr[-1600:]}

def run_v88_gate():
    checks = [compile_module(m) for m in MODULES]
    modules_ok = all(c["ok"] for c in checks)
    details = {}

    try:
        from seed_v88_systems import build_v88_state
        state = build_v88_state()
        systems_ok = state.get("ok") is True and len(state.get("cards", [])) >= 3
        details["v88_state"] = {"ok": state.get("ok"), "cards": len(state.get("cards", []))}
    except Exception as e:
        systems_ok = False
        details["v88_state_error"] = str(e)

    try:
        from seed_wake_fast_v872 import match_wake
        wake_ok = match_wake("wake up what are you")[0] and match_wake("see it")[0] is False
        details["wake_tests"] = {"wake_inline": match_wake("wake up what are you"), "false_positive": match_wake("see it")}
    except Exception as e:
        wake_ok = False
        details["wake_error"] = str(e)

    try:
        from seed_mac_body_v88 import body_status
        body = body_status()
        body_ok = body.get("ok") is True and bool(body.get("tools", {}).get("osascript")) and bool(body.get("tools", {}).get("open"))
        details["body"] = body
    except Exception as e:
        body_ok = False
        details["body_error"] = str(e)

    report = {
        "created_at": now(),
        "version": "v88.0.0",
        "ready": modules_ok and systems_ok and wake_ok and body_ok,
        "modules_ok": modules_ok,
        "systems_ok": systems_ok,
        "wake_ok": wake_ok,
        "body_ok": body_ok,
        "module_checks": checks,
        "details": details,
    }
    Path("seed_v88_gate_report.json").write_text(json.dumps(report, indent=4, ensure_ascii=False))
    return report

def show_v88_gate():
    r = run_v88_gate()
    print("\n=== SEED v88 MAC BODY + FAST WAKE GATE ===")
    print(f"Ready: {r['ready']}")
    print(f"Modules OK: {r['modules_ok']}")
    print(f"Systems OK: {r['systems_ok']}")
    print(f"Wake OK: {r['wake_ok']}")
    print(f"Body OK: {r['body_ok']}")
    print(f"Details: {r['details']}")

if __name__ == "__main__":
    show_v88_gate()
