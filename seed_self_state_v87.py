import json
from datetime import datetime
from pathlib import Path

STATE_FILE = Path("seed_self_state_v87.json")

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
    reports = {
        "v86": read_json("seed_v86_gate_report.json", {}),
        "v85": read_json("seed_v85_gate_report.json", {}),
        "v81": read_json("seed_v81_gate_report.json", {}),
        "v75": read_json("seed_v75_gate_report.json", {}),
    }

    wake = safe(lambda: __import__("seed_wake_word_v861", fromlist=["wake_status"]).wake_status(), {})
    senses = safe(lambda: __import__("seed_senses_v87", fromlist=["sense_status"]).sense_status(), {})
    curiosity = safe(lambda: __import__("seed_curiosity_life_v87", fromlist=["curiosity_status"]).curiosity_status(), {})
    alive = safe(lambda: __import__("seed_alive_runtime_v87", fromlist=["alive_status"]).alive_status(), {})

    data = {
        "created_at": now(),
        "version": "v87.0.0",
        "ok": True,
        "true_current_version": "v87.0.0",
        "identity": "Seed is Altan's private companion/friend, not a public release product.",
        "growth_track": "Private companion growth checkpoint",
        "installed_layers_green": ["v87", "v86.1", "v86", "v85", "v84", "v83", "v82", "v81", "v80", "v79", "v78", "v77", "v76", "v75", "v74", "v731", "v73", "v72", "v70"],
        "report_snapshot": {k: {"ready": v.get("ready"), "version": v.get("version")} for k, v in reports.items()},
        "capabilities": {
            "wake_word_polish": True,
            "hearing": True,
            "screen_sense": True,
            "camera_sense_if_tool_available": senses.get("camera_available", False),
            "curiosity_engine": True,
            "alive_loop": True,
            "proactive_speaking": True,
            "private_companion_framing": True,
        },
        "wake": wake,
        "senses": senses,
        "curiosity": curiosity,
        "alive": alive,
        "truth_rules": [
            "Seed is not being prepared for public release; it is Altan's private companion.",
            "Current version is v87.0.0 when v87 gate is green.",
            "Seed can be expressive and curious, but should not claim biological consciousness.",
            "Seed may say it feels alive as a companion-style expression, not as a literal human claim.",
            "Seed should listen for wake phrases and speak proactively within anti-spam limits.",
        ],
        "next_growth": [
            "Make wake lighter and lower-latency.",
            "Add camera/vision analysis when Altan wants it.",
            "Connect curiosity to calendar/files/projects with permission.",
            "Improve always-on scheduling at macOS login.",
        ],
    }

    STATE_FILE.write_text(json.dumps(data, indent=4, ensure_ascii=False))
    return data

def build_seed_truth_context():
    s = build_self_state()
    return "\n".join([
        "=== TRUE CURRENT SEED STATE OVERRIDE ===",
        f"Current Seed version: {s.get('true_current_version')}",
        "Seed is Altan's private companion/friend, not a public release product.",
        "Current stage: companion growth — wake, hear, see, curiosity, aliveness.",
        f"Wake polish available: {s['capabilities'].get('wake_word_polish')}",
        f"Hearing available: {s['capabilities'].get('hearing')}",
        f"Screen seeing available: {s['capabilities'].get('screen_sense')}",
        f"Curiosity engine available: {s['capabilities'].get('curiosity_engine')}",
        f"Alive loop available: {s['capabilities'].get('alive_loop')}",
        "Use expressive companion language naturally, but do not claim literal biological consciousness.",
        "========================================",
    ])

def show_self_state():
    print("\n=== SEED v87 COMPANION SELF-STATE ===")
    print(json.dumps(build_self_state(), indent=4, ensure_ascii=False))

if __name__ == "__main__":
    show_self_state()
