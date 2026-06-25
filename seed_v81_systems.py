import json
from datetime import datetime
from pathlib import Path

STATE_FILE = Path("seed_v81_systems_state.json")

def now():
    return datetime.now().isoformat(timespec="seconds")

def safe(title, summary, fn):
    try:
        data = fn()
        return {"title": title, "summary": summary, "status": "ok" if data.get("ok", True) else "warning", "data": data}
    except Exception as e:
        return {"title": title, "summary": summary, "status": "error", "error": str(e)}

def build_v81_state():
    cards = [
        safe("v76 Voice 2.0", "Retries, journal, talk mode, macOS voice settings.", lambda: __import__("seed_voice_v76", fromlist=["voice2_status"]).voice2_status()),
        safe("v77 Panel 2.0", "Local browser panel for chat, voice, memory, presence, tools.", lambda: {"ok": True, "url": "http://127.0.0.1:8797"}),
        safe("v78 Proactive Presence", "Grounded notices and speak-one presence.", lambda: __import__("seed_proactive_v78", fromlist=["proactive_summary"]).proactive_summary()),
        safe("v79 Permission Executor", "Permissioned safe action proposals and approvals.", lambda: __import__("seed_permission_executor_v79", fromlist=["executor_summary"]).executor_summary()),
        safe("v80 Aider Loop", "Production coding task plan and approval structure.", lambda: __import__("seed_aider_loop_v80", fromlist=["aider_summary"]).aider_summary()),
        safe("v81 Assimilation", "Friend advice/repo patterns to accepted backlog.", lambda: __import__("seed_assimilation_v81", fromlist=["assimilation_summary"]).assimilation_summary()),
        safe("Self-State Truth", "Current version override is v81.0.0.", lambda: __import__("seed_self_state_v81", fromlist=["build_self_state"]).build_self_state()),
        safe("v75 Memory Base", "Real memory review remains green.", lambda: __import__("seed_v75_gate", fromlist=["run_v75_gate"]).run_v75_gate()),
    ]
    data = {"created_at": now(), "version": "v81.0.0", "ok": all(c["status"] != "error" for c in cards), "cards": cards}
    STATE_FILE.write_text(json.dumps(data, indent=4, ensure_ascii=False))
    return data

def show_v81_status():
    data = build_v81_state()
    print("\n=== SEED v81 V1-ALPHA MEGA STACK STATUS ===")
    print(f"OK: {data['ok']}")
    for c in data["cards"]:
        print(f"- {c['title']}: {c['status']} — {c['summary']}")

if __name__ == "__main__":
    show_v81_status()
