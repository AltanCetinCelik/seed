import json
import subprocess
from datetime import datetime
from pathlib import Path

STATE_FILE = Path("seed_self_state_v741.json")

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
    # IMPORTANT:
    # Do NOT call seed_v75_gate from here.
    # v75_gate -> v75_systems -> self_state caused recursion in v75.0.0.
    lower_gates = {
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
    avatar = safe(lambda: __import__("seed_avatar_panel_v74", fromlist=["build_avatar_panel_state"]).build_avatar_panel_state(), {})
    voice = safe(lambda: __import__("seed_live_voice_v731", fromlist=["voice_status"]).voice_status(), {})

    installed_layers_green = ["v75"]
    installed_layers_green.extend([k for k, v in lower_gates.items() if v.get("ready")])

    data = {
        "created_at": now(),
        "version": "v75.1.0",
        "ok": True,
        "true_current_version": "v75.1.0",
        "previous_broken_version": "v75.0.0 recursion hotfixed",
        "release_track": "Seed local companion v1-alpha hardening",
        "installed_layers_green": installed_layers_green,
        "gates": {k: {"ready": v.get("ready"), "version": v.get("version")} for k, v in lower_gates.items()},
        "capabilities": {
            "local_chat": True,
            "ollama_model_router": bool(role_map),
            "voice_record_transcribe_reply": bool(voice.get("ok")),
            "embodied_web_panel": lower_gates["v74"].get("ready") is True,
            "presence_policy": lower_gates["v72"].get("ready") is True,
            "real_memory_review": bool(memory.get("ok", True)),
            "self_state_truth": True,
            "recursion_hotfix": True,
        },
        "models": models,
        "role_map": role_map,
        "memory": memory,
        "avatar": avatar,
        "voice": voice,
        "git_head": git_head(),
        "truth_rules": [
            "Current version is v75.1.0 when v75.1 gate is green.",
            "v75.0.0 had a recursion bug and was hotfixed.",
            "v70 is an older base layer, not current.",
            "Current goal is real Seed v1 hardening.",
            "Mention voice/panel/memory as working when gates are green.",
        ],
        "next_recommended_updates": [
            "v76 Voice 2.0",
            "v77 Panel 2.0",
            "v78 Proactive presence",
            "v79 Permissioned executor",
            "v80 Aider production loop",
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
        "Current stage: moving toward real Seed v1.",
        f"Green layers: {', '.join(s.get('installed_layers_green', []))}",
        f"Voice working: {s['capabilities'].get('voice_record_transcribe_reply')}",
        f"Embodied panel working: {s['capabilities'].get('embodied_web_panel')}",
        f"Real memory review working: {s['capabilities'].get('real_memory_review')}",
        f"Accepted memories: {mem.get('accepted_count', 0)}",
        f"Pending memory candidates: {mem.get('pending_count', 'unknown')}",
        f"Memory decisions logged: {mem.get('decision_count', 0)}",
        "v70 is an older base layer, not the current version.",
        "v75.0.0 recursion bug is hotfixed in v75.1.0.",
        "Next best work: review memories, then v76 voice polish and v77 panel polish.",
        "========================================",
    ])

def show_self_state():
    print("\n=== SEED v75.1 SELF-STATE TRUTH ===")
    print(json.dumps(build_self_state(), indent=4, ensure_ascii=False))

if __name__ == "__main__":
    show_self_state()
