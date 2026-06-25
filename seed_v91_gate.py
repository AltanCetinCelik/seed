import json, subprocess, sys
from datetime import datetime
from pathlib import Path

MODULES = ["seed_companion_context_v91.py", "seed_contextual_chat_v91.py", "seed_wake_context_v91.py", "seed_natural_intent_router_v91.py", "seed_v91_systems.py", "seed_v91_gate.py"]

def now():
    return datetime.now().isoformat(timespec="seconds")

def comp(m):
    p = subprocess.run([sys.executable, "-m", "py_compile", m], capture_output=True, text=True, timeout=30)
    return {"module": m, "ok": p.returncode == 0, "stderr": p.stderr[-1000:]}

def run_v91_gate():
    checks = [comp(m) for m in MODULES]
    modules_ok = all(c["ok"] for c in checks)
    details = {}

    try:
        ctx = __import__("seed_companion_context_v91", fromlist=["build_context_text", "status", "ensure_baseline_memory"])
        boot = ctx.ensure_baseline_memory()
        text = ctx.build_context_text()
        context_ok = ("SEED COMPANION CONTEXT v91" in text and "private local companion" in text and "v90.1.1" in text)
        details["context_preview"] = text[:500]
        details["bootstrap"] = boot
    except Exception as e:
        context_ok = False
        details["context_error"] = str(e)

    try:
        wake = __import__("seed_wake_context_v91", fromlist=["match_wake"])
        wake_ok = (
            wake.match_wake("make up what are you")[0] is True and
            wake.match_wake("weight up what are you")[0] is True and
            wake.match_wake("hello there")[0] is False
        )
        details["wake_tests"] = {
            "make_up": wake.match_wake("make up what are you"),
            "weight_up": wake.match_wake("weight up what are you"),
            "false": wake.match_wake("hello there")
        }
    except Exception as e:
        wake_ok = False
        details["wake_error"] = str(e)

    try:
        systems = __import__("seed_v91_systems", fromlist=["build_v91_state"]).build_v91_state()
        systems_ok = systems.get("ok") is True and len(systems.get("cards", [])) >= 3
        details["systems"] = {"ok": systems.get("ok"), "cards": len(systems.get("cards", []))}
    except Exception as e:
        systems_ok = False
        details["systems_error"] = str(e)

    r = {
        "created_at": now(),
        "version": "v91.0.0",
        "ready": modules_ok and context_ok and wake_ok and systems_ok,
        "modules_ok": modules_ok,
        "context_ok": context_ok,
        "wake_ok": wake_ok,
        "systems_ok": systems_ok,
        "module_checks": checks,
        "details": details
    }
    Path("seed_v91_gate_report.json").write_text(json.dumps(r, indent=4, ensure_ascii=False))
    return r

def show_v91_gate():
    r = run_v91_gate()
    print("\n=== SEED v91 COMPANION CONTEXT GATE ===")
    print(f"Ready: {r['ready']}")
    print(f"Modules OK: {r['modules_ok']}")
    print(f"Context OK: {r['context_ok']}")
    print(f"Wake OK: {r['wake_ok']}")
    print(f"Systems OK: {r['systems_ok']}")
    print(f"Details: {r['details']}")

if __name__ == "__main__":
    show_v91_gate()
