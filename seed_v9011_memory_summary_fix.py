#!/usr/bin/env python3
from pathlib import Path
import re
import subprocess
import sys

OVERRIDE = '\n# v90.1.1 memory summary override: do not summarize archived low-value notes.\ndef daily_summary():\n    """Summarize only promoted memories or meaningful unreviewed candidates.\n    Archived low-value notes must not appear in the daily summary."""\n    archived_ids = {str(r.get("source_note_id", "")) for r in read_jsonl(ARCHIVE_FILE, 5000)}\n\n    mems = memories(50)\n    if mems:\n        bullets = []\n        for r in mems[-12:]:\n            s = str(r.get("summary", "")).strip()\n            if s:\n                bullets.append("- " + s)\n        if bullets:\n            return {"ok": True, "summary": "Seed day summary:\\n" + "\\n".join(bullets[-12:])}\n\n    meaningful = []\n    for note in load_notes()[-80:]:\n        nid = note_id(note)\n        if nid in archived_ids:\n            continue\n        decision = classify_note(note)\n        if decision.get("action") in {"candidate", "promote"}:\n            s = str(note.get("summary", "")).strip()\n            if s:\n                meaningful.append("- " + s)\n\n    if meaningful:\n        return {"ok": True, "summary": "Seed day summary candidates:\\n" + "\\n".join(meaningful[-12:])}\n\n    return {"ok": True, "summary": "Seed day summary: no meaningful promoted memories yet."}\n'
GATE = '\nimport json\nimport subprocess\nimport sys\nfrom datetime import datetime\nfrom pathlib import Path\n\ndef now():\n    return datetime.now().isoformat(timespec="seconds")\n\ndef run_v9011_gate():\n    checks = []\n    for module in ["seed_memory_garden_v90.py", "seed_v9011_gate.py"]:\n        proc = subprocess.run([sys.executable, "-m", "py_compile", module], capture_output=True, text=True, timeout=30)\n        checks.append({"module": module, "ok": proc.returncode == 0, "stderr": proc.stderr[-1000:]})\n\n    modules_ok = all(c["ok"] for c in checks)\n\n    try:\n        import seed_memory_garden_v90 as garden\n        summary = garden.daily_summary()["summary"]\n        no_archive_leak = "organism mode started" not in summary.lower()\n        no_old_noise = "stores notes only" not in summary.lower()\n        status = garden.status()\n        ready = modules_ok and no_archive_leak and no_old_noise and status.get("ok") is True\n        details = {"summary": summary, "status": status, "no_archive_leak": no_archive_leak, "no_old_noise": no_old_noise}\n    except Exception as e:\n        ready = False\n        no_archive_leak = False\n        no_old_noise = False\n        details = {"error": str(e)}\n\n    report = {\n        "created_at": now(),\n        "version": "v90.1.1",\n        "ready": ready,\n        "modules_ok": modules_ok,\n        "no_archive_leak": no_archive_leak,\n        "no_old_noise": no_old_noise,\n        "module_checks": checks,\n        "details": details,\n    }\n    Path("seed_v9011_gate_report.json").write_text(json.dumps(report, indent=4, ensure_ascii=False))\n    return report\n\ndef show_v9011_gate():\n    r = run_v9011_gate()\n    print("\\n=== SEED v90.1.1 MEMORY SUMMARY GATE ===")\n    print(f"Ready: {r[\'ready\']}")\n    print(f"Modules OK: {r[\'modules_ok\']}")\n    print(f"No Archive Leak: {r[\'no_archive_leak\']}")\n    print(f"No Old Noise: {r[\'no_old_noise\']}")\n    print(f"Details: {r[\'details\']}")\n\nif __name__ == "__main__":\n    show_v9011_gate()\n'
MARKER = "# v90.1.1 memory summary override"

p = Path("seed_memory_garden_v90.py")
text = p.read_text(errors="ignore")

if MARKER not in text:
    main_marker = 'if __name__ == "__main__":'
    idx = text.find(main_marker)
    if idx >= 0:
        text = text[:idx].rstrip() + "\n\n" + OVERRIDE.strip() + "\n\n" + text[idx:]
    else:
        text = text.rstrip() + "\n\n" + OVERRIDE.strip() + "\n"
    p.write_text(text)
    print("Inserted v90.1.1 daily_summary override before main block")
else:
    print("v90.1.1 daily_summary override already present")

Path("seed_v9011_gate.py").write_text(GATE.strip() + "\n")
print("Wrote seed_v9011_gate.py")

cfg = Path("seed_config.py")
ct = cfg.read_text(errors="ignore") if cfg.exists() else 'SEED_VERSION = "v90.1.1"\n'
ct = re.sub(r'^SEED_VERSION\s*=\s*".*?"', 'SEED_VERSION = "v90.1.1"', ct, flags=re.M)
if "SEED_V9011_MEMORY_SUMMARY_FIX" not in ct:
    ct += "\nSEED_V9011_MEMORY_SUMMARY_FIX = True\n"
cfg.write_text(ct)
print("Updated seed_config.py")

core = Path("Seed_Core.md")
co = core.read_text(errors="ignore") if core.exists() else ""
if "Seed v90.1.1 — Memory Summary Fix" not in co:
    co += """
## Seed v90.1.1 — Memory Summary Fix

Fixes Memory Garden summary by inserting a safe override before the CLI main block:
- Archived low-value startup notes no longer appear in `summary`.
- If there are no promoted memories, summary says so clearly.
- Avoids brittle source replacement.
"""
core.write_text(co)
print("Updated Seed_Core.md")

for module in ["seed_memory_garden_v90.py", "seed_v9011_gate.py"]:
    proc = subprocess.run([sys.executable, "-m", "py_compile", module], capture_output=True, text=True, timeout=30)
    print("$ python -m py_compile", module)
    if proc.returncode == 0:
        print("OK")
    else:
        print(proc.stderr)
        sys.exit(proc.returncode)

print("\nSeed v90.1.1 Memory Summary Fix installed.")
