#!/usr/bin/env python3
from pathlib import Path
import re, subprocess, sys

NEW_DAILY_SUMMARY = '\ndef daily_summary():\n    """Summarize only promoted memories or meaningful unreviewed candidates.\n    Do not summarize archived low-value startup notes."""\n    archived_ids = {str(r.get("source_note_id", "")) for r in read_jsonl(ARCHIVE_FILE, 5000)}\n    mems = memories(50)\n    if mems:\n        bullets = []\n        for r in mems[-12:]:\n            s = str(r.get("summary", "")).strip()\n            if s:\n                bullets.append("- " + s)\n        return {"ok": True, "summary": "Seed day summary:\\n" + "\\n".join(bullets[-12:])}\n\n    meaningful = []\n    for note in load_notes()[-80:]:\n        nid = note_id(note)\n        if nid in archived_ids:\n            continue\n        decision = classify_note(note)\n        if decision.get("action") in {"candidate", "promote"}:\n            s = str(note.get("summary", "")).strip()\n            if s:\n                meaningful.append("- " + s)\n\n    if meaningful:\n        return {"ok": True, "summary": "Seed day summary candidates:\\n" + "\\n".join(meaningful[-12:])}\n\n    return {"ok": True, "summary": "Seed day summary: no meaningful promoted memories yet."}\n'
GATE = '\nimport json, subprocess, sys\nfrom datetime import datetime\nfrom pathlib import Path\n\ndef now():\n    return datetime.now().isoformat(timespec="seconds")\n\ndef run_v901_gate():\n    checks = []\n    for m in ["seed_memory_garden_v90.py", "seed_v901_gate.py"]:\n        p = subprocess.run([sys.executable, "-m", "py_compile", m], capture_output=True, text=True, timeout=30)\n        checks.append({"module": m, "ok": p.returncode == 0, "stderr": p.stderr[-1000:]})\n\n    modules_ok = all(c["ok"] for c in checks)\n    try:\n        import seed_memory_garden_v90 as g\n        summary = g.daily_summary()["summary"]\n        no_archive_leak = "organism mode started" not in summary.lower()\n        status = g.status()\n        ok = modules_ok and no_archive_leak and status.get("ok") is True\n        details = {"summary": summary, "status": status, "no_archive_leak": no_archive_leak}\n    except Exception as e:\n        ok = False\n        no_archive_leak = False\n        details = {"error": str(e)}\n\n    report = {"created_at": now(), "version": "v90.1.0", "ready": ok, "modules_ok": modules_ok, "no_archive_leak": no_archive_leak, "module_checks": checks, "details": details}\n    Path("seed_v901_gate_report.json").write_text(json.dumps(report, indent=4, ensure_ascii=False))\n    return report\n\ndef show_v901_gate():\n    r = run_v901_gate()\n    print("\\n=== SEED v90.1 MEMORY SUMMARY GATE ===")\n    print(f"Ready: {r[\'ready\']}")\n    print(f"Modules OK: {r[\'modules_ok\']}")\n    print(f"No Archive Leak: {r[\'no_archive_leak\']}")\n    print(f"Details: {r[\'details\']}")\n\nif __name__ == "__main__":\n    show_v901_gate()\n'

p = Path("seed_memory_garden_v90.py")
text = p.read_text(errors="ignore")

pattern = r'def daily_summary\(\):\n(?:    .*\n)+?def status\(\):'
m = re.search(pattern, text)
if not m:
    print("Could not locate daily_summary block safely.")
    sys.exit(1)

text = text[:m.start()] + NEW_DAILY_SUMMARY + "\ndef status():" + text[m.end():]
p.write_text(text)
print("Patched seed_memory_garden_v90.py daily_summary")

Path("seed_v901_gate.py").write_text(GATE.strip() + "\n")
print("Wrote seed_v901_gate.py")

cfg = Path("seed_config.py")
ct = cfg.read_text(errors="ignore") if cfg.exists() else 'SEED_VERSION = "v90.1.0"\n'
ct = re.sub(r'^SEED_VERSION\s*=\s*".*?"', 'SEED_VERSION = "v90.1.0"', ct, flags=re.M)
if "SEED_V901_MEMORY_SUMMARY_FIX" not in ct:
    ct += "\nSEED_V901_MEMORY_SUMMARY_FIX = True\n"
cfg.write_text(ct)
print("Updated seed_config.py")

core = Path("Seed_Core.md")
co = core.read_text(errors="ignore") if core.exists() else ""
if "Seed v90.1 — Memory Summary Fix" not in co:
    co += """
## Seed v90.1 — Memory Summary Fix

Fixes Memory Garden day summary:
- Archived low-value notes no longer appear in `summary`.
- If no promoted memories exist, summary reports that clearly.
- Candidate notes can appear only if they are meaningful and unarchived.
"""
core.write_text(co)
print("Updated Seed_Core.md")

for m in ["seed_memory_garden_v90.py", "seed_v901_gate.py"]:
    proc = subprocess.run([sys.executable, "-m", "py_compile", m], capture_output=True, text=True, timeout=30)
    print("$ python -m py_compile", m)
    if proc.returncode == 0:
        print("OK")
    else:
        print(proc.stderr)
        sys.exit(proc.returncode)

print("\nSeed v90.1 Memory Summary Fix installed.")
