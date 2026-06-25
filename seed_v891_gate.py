import json, subprocess, sys
from datetime import datetime
from pathlib import Path

MODULES = ["seed_organism_notes_v89.py", "seed_ambient_vision_v89.py", "seed_v891_gate.py"]

def now():
    return datetime.now().isoformat(timespec="seconds")

def comp(m):
    p = subprocess.run([sys.executable, "-m", "py_compile", m], capture_output=True, text=True, timeout=30)
    return {"module": m, "ok": p.returncode == 0, "stderr": p.stderr[-1000:]}

def run_v891_gate():
    checks = [comp(m) for m in MODULES]
    modules_ok = all(c["ok"] for c in checks)
    details = {}
    try:
        from seed_organism_notes_v89 import is_bad_summary, settings
        reject_ok = is_bad_summary("Inspect this temporary screenshot, then return ONLY JSON with importance 0-100") is True
        privacy = settings()
        privacy_ok = privacy.get("store_raw_audio") is False and privacy.get("store_raw_screenshots") is False and privacy.get("store_raw_transcripts") is False
        details["reject_prompt_leak_test"] = reject_ok
        details["privacy"] = privacy
    except Exception as e:
        reject_ok = False
        privacy_ok = False
        details["error"] = str(e)
    r = {"created_at": now(), "version": "v89.1.0", "ready": modules_ok and reject_ok and privacy_ok, "modules_ok": modules_ok, "prompt_leak_reject_ok": reject_ok, "privacy_ok": privacy_ok, "module_checks": checks, "details": details}
    Path("seed_v891_gate_report.json").write_text(json.dumps(r, indent=4, ensure_ascii=False))
    return r

def show_v891_gate():
    r = run_v891_gate()
    print("\n=== SEED v89.1 ORGANISM NOTE QUALITY GATE ===")
    print(f"Ready: {r['ready']}")
    print(f"Modules OK: {r['modules_ok']}")
    print(f"Prompt Leak Reject OK: {r['prompt_leak_reject_ok']}")
    print(f"Privacy OK: {r['privacy_ok']}")
    print(f"Details: {r['details']}")

if __name__ == "__main__":
    show_v891_gate()
