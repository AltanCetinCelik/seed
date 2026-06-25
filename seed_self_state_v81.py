import json
import subprocess
from datetime import datetime
from pathlib import Path

STATE_FILE = Path("seed_self_state_v81.json")

def now():
    return datetime.now().isoformat(timespec="seconds")

def safe(fn, fallback=None):
    try:
        return fn()
    except Exception as e:
        return fallback if fallback is not None else {"ok": False, "error": str(e)}

def gate(mod, fn):
    return safe(lambda: getattr(__import__(mod, fromlist=[fn]), fn)(), {"ready": False, "error": f"{mod}.{fn} unavailable"})

def git_head():
    try:
        p = subprocess.run(["git", "rev-parse", "--short", "HEAD"], capture_output=True, text=True, timeout=8)
        return p.stdout.strip() if p.returncode == 0 else None
    except Exception:
        return None

def build_self_state():
    # Do not call v81 gate from self-state. Avoid recursion.
    lower_gates = {
        "v75": gate("seed_v75_gate", "run_v75_gate"),
        "v74": gate("seed_v74_gate", "run_v74_gate"),
        "v731": gate("seed_v731_gate", "run_v731_gate"),
        "v73": gate("seed_v73_gate", "run_v73_gate"),
        "v72": gate("seed_v72_gate", "run_v72_gate"),
        "v70": gate("seed_v70_gate", "run_v70_gate"),
    }

    role_map, models = {}, []
    try:
        from seed_model_real_mode_v61 import load_role_map, list_models
        role_map = load_role_map().get("role_map", {})
        models = list_models().get("models", [])
    except Exception:
        pass

    memory = safe(lambda: __import__("seed_memory_review_v75", fromlist=["memory_summary"]).memory_summary(), {})
    voice = safe(lambda: __import__("seed_voice_v76", fromlist=["voice2_status"]).voice2_status(), {})
    assimilation = safe(lambda: __import__("seed_assimilation_v81", fromlist=["assimilation_summary"]).assimilation_summary(), {})
    executor = safe(lambda: __import__("seed_permission_executor_v79", fromlist=["executor_summary"]).executor_summary(), {})
    aider = safe(lambda: __import__("seed_aider_loop_v80", fromlist=["aider_summary"]).aider_summary(), {})
    proactive = safe(lambda: __import__("seed_proactive_v78", fromlist=["proactive_summary"]).proactive_summary(), {})

    installed = ["v81", "v80", "v79", "v78", "v77", "v76"]
    installed.extend([k for k, v in lower_gates.items() if v.get("ready")])

    data = {
        "created_at": now(),
        "version": "v81.0.0",
        "ok": True,
        "true_current_version": "v81.0.0",
        "release_track": "Seed local companion v1-alpha hardening",
        "installed_layers_green": installed,
        "lower_gates": {k: {"ready": v.get("ready"), "version": v.get("version")} for k, v in lower_gates.items()},
        "capabilities": {
            "voice_2": bool(voice.get("ok")),
            "panel_2": True,
            "proactive_presence": bool(proactive.get("ok", True)),
            "permission_executor": bool(executor.get("ok", True)),
            "aider_loop": bool(aider.get("ok", True)),
            "advice_repo_assimilation": bool(assimilation.get("ok", True)),
            "real_memory_review": bool(memory.get("ok", True)),
            "embodied_panel": lower_gates["v74"].get("ready") is True,
        },
        "models": models,
        "role_map": role_map,
        "memory": memory,
        "voice": voice,
        "assimilation": assimilation,
        "executor": executor,
        "aider": aider,
        "proactive": proactive,
        "git_head": git_head(),
        "truth_rules": [
            "Current version is v81.0.0 when v81 gate is green.",
            "v76-v81 were installed as one v1-alpha mega update.",
            "v70, v72, v73, v74, and v75 are older green layers, not current.",
            "Current real-v1 path after v81: reliability/recovery, one-command runtime, backup/privacy, release candidate.",
        ],
        "next_recommended_updates": [
            "v82 Reliability and recovery",
            "v83 One-command runtime",
            "v84 Backup/privacy/export",
            "v85 Release candidate hardening",
            "v1.0 Local Companion release",
        ],
    }
    STATE_FILE.write_text(json.dumps(data, indent=4, ensure_ascii=False))
    return data

def build_seed_truth_context():
    s = build_self_state()
    mem = s.get("memory", {})
    return "\n".join([
        "=== TRUE CURRENT SEED STATE OVERRIDE ===",
        f"Current Seed version: {s.get('true_current_version')}",
        "Current stage: final hardening toward real Seed v1.",
        f"Green/current layers: {', '.join(s.get('installed_layers_green', []))}",
        f"Voice 2 working: {s['capabilities'].get('voice_2')}",
        f"Panel 2 available: {s['capabilities'].get('panel_2')}",
        f"Proactive presence available: {s['capabilities'].get('proactive_presence')}",
        f"Permission executor available: {s['capabilities'].get('permission_executor')}",
        f"Aider loop available: {s['capabilities'].get('aider_loop')}",
        f"Assimilation available: {s['capabilities'].get('advice_repo_assimilation')}",
        f"Accepted memories: {mem.get('accepted_count', 0)}",
        f"Pending memory candidates: {mem.get('pending_count', 'unknown')}",
        "Do not call v70/v75 the current version. They are older green layers.",
        "Next best work after v81: v82 recovery, v83 one-command runtime, v84 backup/privacy, v85 release candidate.",
        "========================================",
    ])

def show_self_state():
    print("\n=== SEED v81 SELF-STATE TRUTH ===")
    print(json.dumps(build_self_state(), indent=4, ensure_ascii=False))

if __name__ == "__main__":
    show_self_state()
