import json, subprocess, sys
from datetime import datetime
from pathlib import Path

MODULES = ["seed_memory_garden_v90.py", "seed_natural_intent_router_v90.py", "seed_v90_systems.py", "seed_v90_gate.py"]

def now():
    return datetime.now().isoformat(timespec="seconds")

def comp(m):
    p = subprocess.run([sys.executable, "-m", "py_compile", m], capture_output=True, text=True, timeout=30)
    return {"module": m, "ok": p.returncode == 0, "stderr": p.stderr[-1000:]}

def run_v90_gate():
    checks = [comp(m) for m in MODULES]
    modules_ok = all(c["ok"] for c in checks)
    details = {}
    try:
        garden = __import__("seed_memory_garden_v90", fromlist=["classify_note", "garden_context", "status"])
        low_note = {"id":"note_test_low", "source":"vision", "summary":"A Firefox window is open displaying Person of Interest episode.", "importance":68, "tags":["firefox"]}
        high_note = {"id":"note_test_high", "source":"vision", "summary":"Seed Mac body keyboard permissions are now working after Accessibility permission fix.", "importance":86, "tags":["seed","mac body","permission"]}
        low_ok = garden.classify_note(low_note)["action"] == "archive"
        high_ok = garden.classify_note(high_note)["action"] in {"candidate", "promote"}
        status = garden.status()
        garden_ok = status.get("ok") is True
        details = {"low_note_test": garden.classify_note(low_note), "high_note_test": garden.classify_note(high_note), "status": status}
    except Exception as e:
        low_ok = False
        high_ok = False
        garden_ok = False
        details = {"error": str(e)}
    r = {"created_at": now(), "version": "v90.0.0", "ready": modules_ok and low_ok and high_ok and garden_ok, "modules_ok": modules_ok, "low_note_filter_ok": low_ok, "high_note_candidate_ok": high_ok, "garden_ok": garden_ok, "module_checks": checks, "details": details}
    Path("seed_v90_gate_report.json").write_text(json.dumps(r, indent=4, ensure_ascii=False))
    return r

def show_v90_gate():
    r = run_v90_gate()
    print("\n=== SEED v90 MEMORY GARDEN GATE ===")
    print(f"Ready: {r['ready']}")
    print(f"Modules OK: {r['modules_ok']}")
    print(f"Low Note Filter OK: {r['low_note_filter_ok']}")
    print(f"High Note Candidate OK: {r['high_note_candidate_ok']}")
    print(f"Garden OK: {r['garden_ok']}")
    print(f"Details: {r['details']}")

if __name__ == "__main__":
    show_v90_gate()
