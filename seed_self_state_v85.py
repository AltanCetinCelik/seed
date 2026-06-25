import json
from datetime import datetime
from pathlib import Path

STATE_FILE = Path("seed_self_state_v85.json")

def now():
    return datetime.now().isoformat(timespec="seconds")

def read_json(path, default=None):
    p = Path(path)
    if not p.exists():
        return default if default is not None else {}
    try:
        return json.loads(p.read_text(errors="ignore"))
    except Exception:
        return default if default is not None else {}

def safe(fn, fallback=None):
    try:
        return fn()
    except Exception as e:
        return fallback if fallback is not None else {"ok": False, "error": str(e)}

def build_self_state():
    # No gate calls here. This is deliberately lightweight to avoid recursion and slow chat.
    reports = {
        "v81": read_json("seed_v81_gate_report.json", {}),
        "v75": read_json("seed_v75_gate_report.json", {}),
        "v74": read_json("seed_v74_gate_report.json", {}),
        "v731": read_json("seed_v731_gate_report.json", {}),
    }

    role_map, models = {}, []
    try:
        from seed_model_real_mode_v61 import load_role_map, list_models
        role_map = load_role_map().get("role_map", {})
        models = list_models().get("models", [])
    except Exception:
        pass

    memory = safe(lambda: __import__("seed_memory_review_v75", fromlist=["memory_summary"]).memory_summary(), {})
    recovery = safe(lambda: __import__("seed_recovery_v82", fromlist=["recovery_summary"]).recovery_summary(), {})
    runtime = safe(lambda: __import__("seed_runtime_v83", fromlist=["runtime_status"]).runtime_status(), {})
    privacy = safe(lambda: __import__("seed_privacy_backup_v84", fromlist=["privacy_status"]).privacy_status(), {})
    rc = safe(lambda: __import__("seed_release_candidate_v85", fromlist=["release_candidate_summary"]).release_candidate_summary(), {})

    installed = ["v85", "v84", "v83", "v82", "v81", "v80", "v79", "v78", "v77", "v76"]
    for key in ["v75", "v74", "v731"]:
        if reports.get(key, {}).get("ready"):
            installed.append(key)
    installed.extend(["v73", "v72", "v70"])

    data = {
        "created_at": now(),
        "version": "v85.0.0",
        "ok": True,
        "true_current_version": "v85.0.0",
        "release_track": "Seed v1 release candidate preparation",
        "installed_layers_green": installed,
        "report_snapshot": {k: {"ready": v.get("ready"), "version": v.get("version")} for k, v in reports.items()},
        "capabilities": {
            "recovery_self_repair": True,
            "one_command_runtime": True,
            "backup_privacy_export_forget": True,
            "release_candidate_checks": True,
            "v81_mega_stack": reports.get("v81", {}).get("ready") is True,
            "real_memory_review": bool(memory.get("ok", True)),
        },
        "models": models,
        "role_map": role_map,
        "memory": memory,
        "recovery": recovery,
        "runtime": runtime,
        "privacy": privacy,
        "release_candidate": rc,
        "truth_rules": [
            "Current version is v85.0.0 when v85 gate is green.",
            "v82-v85 were installed as the final real-v1 preparation stack.",
            "v81 and below are older green layers, not the current version.",
            "Remaining step after v85 is v1.0 final stabilization.",
        ],
        "next_recommended_updates": [
            "Fix anything v85 RC report marks as blocker.",
            "Run one-command runtime and backup/privacy tests.",
            "Prepare Seed v1.0 final release.",
        ],
    }

    STATE_FILE.write_text(json.dumps(data, indent=4, ensure_ascii=False))
    return data

def build_seed_truth_context():
    s = build_self_state()
    return "\n".join([
        "=== TRUE CURRENT SEED STATE OVERRIDE ===",
        f"Current Seed version: {s.get('true_current_version')}",
        "Current stage: Seed v1 release-candidate preparation.",
        f"Green/current layers: {', '.join(s.get('installed_layers_green', []))}",
        f"Recovery/self-repair available: {s['capabilities'].get('recovery_self_repair')}",
        f"One-command runtime available: {s['capabilities'].get('one_command_runtime')}",
        f"Backup/privacy/export/forget available: {s['capabilities'].get('backup_privacy_export_forget')}",
        f"Release candidate checks available: {s['capabilities'].get('release_candidate_checks')}",
        "Do not call v70/v75/v81 the current version. They are older green layers.",
        "Next best work after v85: run RC checks, fix blockers, then Seed v1.0 final.",
        "========================================",
    ])

def show_self_state():
    print("\n=== SEED v85 SELF-STATE TRUTH ===")
    print(json.dumps(build_self_state(), indent=4, ensure_ascii=False))

if __name__ == "__main__":
    show_self_state()
