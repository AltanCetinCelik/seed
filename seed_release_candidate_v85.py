import json
import subprocess
import sys
from datetime import datetime
from pathlib import Path

REPORT_FILE = Path("seed_v85_release_candidate_report.json")
README_FILE = Path("README_SEED_V1_RC.md")

ESSENTIAL_FILES = [
    "seed_cli.py",
    "seed_local_chat_v701.py",
    "seed_v81_gate.py",
    "seed_v85_gate.py",
    "seed_runtime_v83.py",
    "seed_privacy_backup_v84.py",
    "seed_recovery_v82.py",
]

def now():
    return datetime.now().isoformat(timespec="seconds")

def run(cmd, timeout=120):
    try:
        proc = subprocess.run(cmd, capture_output=True, text=True, timeout=timeout)
        return {"command": " ".join(cmd), "ok": proc.returncode == 0, "returncode": proc.returncode, "stdout_tail": proc.stdout[-4000:], "stderr_tail": proc.stderr[-4000:]}
    except subprocess.TimeoutExpired:
        return {"command": " ".join(cmd), "ok": False, "returncode": None, "stderr_tail": f"timeout after {timeout}s"}
    except Exception as e:
        return {"command": " ".join(cmd), "ok": False, "returncode": None, "stderr_tail": str(e)}

def essential_file_check():
    items = []
    for f in ESSENTIAL_FILES:
        p = Path(f)
        items.append({"file": f, "exists": p.exists(), "size": p.stat().st_size if p.exists() else 0})
    return {"ok": all(i["exists"] for i in items), "items": items}

def compile_core():
    files = [p for p in Path(".").glob("seed_*.py")]
    checks = []
    for p in files:
        proc = run([sys.executable, "-m", "py_compile", str(p)], timeout=30)
        checks.append({"file": str(p), "ok": proc["ok"], "stderr": proc.get("stderr_tail", "")})
    return {"ok": all(c["ok"] for c in checks), "count": len(checks), "failed": [c for c in checks if not c["ok"]][:20]}

def gate_simulation():
    gates = []
    for g in ["seed_v81_gate.py", "seed_v75_gate.py", "seed_v74_gate.py", "seed_v731_gate.py"]:
        if Path(g).exists():
            gates.append(run([sys.executable, g], timeout=160))
    return {"ok": all(g["ok"] for g in gates), "gates": gates}

def release_candidate_summary():
    return {"created_at": now(), "version": "v85.0.0", "ok": True, "readme": str(README_FILE), "report": str(REPORT_FILE)}

def build_release_candidate_report(full=False):
    essentials = essential_file_check()
    compile_report = compile_core()
    gates = gate_simulation() if full else {"ok": True, "skipped": "full gate simulation skipped in summary mode"}
    blockers = []
    if not essentials["ok"]:
        blockers.append("missing essential files")
    if not compile_report["ok"]:
        blockers.append("compile failures")
    if not gates["ok"]:
        blockers.append("lower gate failures")
    data = {
        "created_at": now(),
        "version": "v85.0.0",
        "ok": len(blockers) == 0,
        "blockers": blockers,
        "essential_files": essentials,
        "compile": {"ok": compile_report["ok"], "count": compile_report["count"], "failed": compile_report["failed"]},
        "gates": gates,
        "remaining_to_v1": [
            "Fix any v85 blockers.",
            "Run one-command runtime end-to-end.",
            "Create backup and memory export.",
            "Test voice/panel/memory/executor/aider once.",
            "Write final README and known issues.",
        ],
    }
    REPORT_FILE.write_text(json.dumps(data, indent=4, ensure_ascii=False))
    return data

def write_readme():
    text = f"""# Seed v1 Release Candidate

Generated: {now()}

## Current layer

Seed v85.0.0 — Release Candidate preparation stack.

## Run

```bash
./seed
```

Fallback:

```bash
python seed_runtime_v83.py start
```

## Main checks

```bash
python seed_v85_gate.py
python seed_v81_gate.py
python seed_v75_gate.py
```

## Main features

- Local companion chat
- Local Ollama model router
- Voice recording/transcription/reply
- Avatar/panel interface
- Memory review and accepted memory store
- Proactive presence inbox
- Permissioned executor
- Aider coding task loop
- Backup/export/forget tools
- Recovery and compile checks

## Backup

```bash
python seed_privacy_backup_v84.py
```

Natural command inside Seed:

```text
backup seed
export memory
forget memory <keyword>
```

## Known remaining path

- v85 blockers cleanup
- v1.0 final stabilization
"""
    README_FILE.write_text(text)
    return {"ok": True, "file": str(README_FILE)}

def show_release_candidate(full=False):
    print("\n=== SEED v85 RELEASE CANDIDATE ===")
    report = build_release_candidate_report(full=full)
    readme = write_readme()
    print(f"OK: {report['ok']}")
    print(f"Blockers: {report['blockers']}")
    print(f"Compile: {report['compile']['ok']} ({report['compile']['count']} files)")
    print(f"README: {readme['file']}")

if __name__ == "__main__":
    show_release_candidate(full="--full" in sys.argv)
