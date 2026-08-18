import ast
import json
import os
import subprocess
import sys
from datetime import datetime
from pathlib import Path

REPORT_FILE = Path("seed_recovery_report_v82.json")
LAST_GREEN_FILE = Path("seed_last_green_checkpoint_v82.json")
ROLLBACK_NOTES = Path("seed_recovery_rollback_notes_v82.md")

CORE_RUNTIME_FILES = [
    "seed_cli.py",
    "seed_commands.py",
    "seed_local_chat_v701.py",
    "seed_v85_gate.py",
    "seed_v85_systems.py",
    "seed_self_state_v85.py",
    "seed_recovery_v82.py",
    "seed_runtime_v83.py",
    "seed_privacy_backup_v84.py",
    "seed_release_candidate_v85.py",
    "seed_v81_gate.py",
    "seed_v75_gate.py",
    "seed_v74_gate.py",
    "seed_v731_gate.py",
]

SELF_GATE_FORBIDDEN = {
    "seed_self_state_v741.py": "seed_v75_gate",
    "seed_self_state_v81.py": "seed_v81_gate",
    "seed_self_state_v85.py": "seed_v85_gate",
}

def now():
    return datetime.now().isoformat(timespec="seconds")

def compile_file(path):
    try:
        proc = subprocess.run([sys.executable, "-m", "py_compile", str(path)], capture_output=True, text=True, timeout=20)
        return {"file": str(path), "ok": proc.returncode == 0, "stderr": proc.stderr[-1200:]}
    except Exception as e:
        return {"file": str(path), "ok": False, "stderr": str(e)}

def compile_all():
    files = [Path(f) for f in CORE_RUNTIME_FILES if Path(f).exists()]
    checks = [compile_file(p) for p in files]
    failed = [c for c in checks if not c["ok"]]
    return {"ok": len(failed) == 0, "count": len(checks), "failed": failed, "checks": checks}

def file_has_real_gate_import(filename, forbidden_module):
    p = Path(filename)
    if not p.exists():
        return False

    text = p.read_text(errors="ignore")
    try:
        tree = ast.parse(text)
    except Exception:
        # If parse fails, compile checks will catch it; don't make recursion guard responsible.
        return False

    for node in ast.walk(tree):
        # import seed_v85_gate
        if isinstance(node, ast.Import):
            for alias in node.names:
                if alias.name == forbidden_module:
                    return True

        # from seed_v85_gate import ...
        if isinstance(node, ast.ImportFrom):
            if node.module == forbidden_module:
                return True

        # __import__("seed_v85_gate", ...)
        if isinstance(node, ast.Call):
            if isinstance(node.func, ast.Name) and node.func.id == "__import__" and node.args:
                first = node.args[0]
                if isinstance(first, ast.Constant) and first.value == forbidden_module:
                    return True

            # gate("seed_v85_gate", "run_v85_gate")
            if isinstance(node.func, ast.Name) and node.func.id in {"gate", "_gate_status"} and node.args:
                first = node.args[0]
                if isinstance(first, ast.Constant) and first.value == forbidden_module:
                    return True

    return False

def recursion_guard():
    warnings = []
    for filename, forbidden in SELF_GATE_FORBIDDEN.items():
        if file_has_real_gate_import(filename, forbidden):
            warnings.append({
                "file": filename,
                "forbidden": forbidden,
                "warning": f"{filename} should not import/call its own gate module {forbidden}",
            })
    return {
        "ok": len(warnings) == 0,
        "warnings": warnings,
        "method": "AST-based; ignores comments and harmless strings.",
    }

def dependency_check():
    import shutil
    deps = {name: shutil.which(name) for name in ["ffmpeg", "say", "aider", "git"]}
    try:
        import faster_whisper
        deps["faster_whisper"] = True
    except Exception:
        deps["faster_whisper"] = False
    return {"ok": bool(deps.get("git")), "deps": deps}

def storage_check():
    try:
        usage = os.statvfs(".")
        free_gb = usage.f_bavail * usage.f_frsize / (1024**3)
        total_gb = usage.f_blocks * usage.f_frsize / (1024**3)
        return {"ok": free_gb > 3, "free_gb": round(free_gb, 2), "total_gb": round(total_gb, 2)}
    except Exception as e:
        return {"ok": False, "error": str(e)}

def mark_last_green(label="manual_green_checkpoint"):
    data = {"created_at": now(), "version": "v85.3.0", "label": label, "cwd": str(Path(".").resolve())}
    try:
        proc = subprocess.run(["git", "rev-parse", "--short", "HEAD"], capture_output=True, text=True, timeout=8)
        if proc.returncode == 0:
            data["git_head"] = proc.stdout.strip()
    except Exception:
        pass
    LAST_GREEN_FILE.write_text(json.dumps(data, indent=4))
    return data

def recovery_summary():
    comp = compile_all()
    guard = recursion_guard()
    deps = dependency_check()
    storage = storage_check()

    blockers = []
    warnings = []

    if not comp["ok"]:
        blockers.append(f"{len(comp['failed'])} core runtime compile failures")
    if not guard["ok"]:
        blockers.append("real recursion guard warning")
    if not deps["ok"]:
        blockers.append("missing critical dependency: git")
    if not storage["ok"]:
        warnings.append("storage warning")

    data = {
        "created_at": now(),
        "version": "v85.3.0",
        "ok": len(blockers) == 0,
        "blockers": blockers,
        "warnings": warnings,
        "compile": {"ok": comp["ok"], "count": comp["count"], "failed": comp["failed"][:10]},
        "recursion_guard": guard,
        "dependencies": deps,
        "storage": storage,
        "last_green": json.loads(LAST_GREEN_FILE.read_text()) if LAST_GREEN_FILE.exists() else None,
        "note": "v85.3 uses AST recursion guard, so comments mentioning seed_v75_gate/seed_v85_gate no longer create false blockers.",
    }
    REPORT_FILE.write_text(json.dumps(data, indent=4, ensure_ascii=False))
    return data

def write_rollback_notes():
    s = recovery_summary()
    ROLLBACK_NOTES.write_text("\n".join([
        "# Seed v85.3 Recovery Notes",
        "",
        f"Created: {now()}",
        f"OK: {s.get('ok')}",
        f"Blockers: {s.get('blockers')}",
        f"Warnings: {s.get('warnings')}",
        "",
        "Rollback:",
        "1. Stop Seed servers with Ctrl+C.",
        "2. Restore latest seed_backup_*_green folder.",
        "3. Or use git reset --hard <green_commit>.",
        "4. Re-run seed_v85_gate.py.",
    ]))
    return {"ok": True, "file": str(ROLLBACK_NOTES)}

def show_recovery():
    d = recovery_summary()
    print("\n=== SEED v85.3 RECOVERY ===")
    print(f"OK: {d['ok']}")
    print(f"Blockers: {d['blockers']}")
    print(f"Warnings: {d['warnings']}")
    print(f"Compile: {d['compile']['ok']} ({d['compile']['count']} core runtime files)")
    print(f"Recursion guard: {d['recursion_guard']}")
    print(f"Deps: {d['dependencies']['deps']}")

if __name__ == "__main__":
    show_recovery()
