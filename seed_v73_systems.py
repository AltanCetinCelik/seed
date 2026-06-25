import json
from datetime import datetime
from pathlib import Path

STATE_FILE = Path("seed_v73_systems_state.json")

def now_timestamp():
    return datetime.now().isoformat(timespec="seconds")

def safe(title, summary, fn):
    try:
        data = fn()
        return {"title": title, "summary": summary, "status": "ok" if data.get("ok", True) else "warning", "data": data}
    except Exception as error:
        return {"title": title, "summary": summary, "status": "error", "error": str(error)}

def build_v73_state():
    cards = [
        safe("Expressive State", "Seed can show simulated excitement after wins while being honest.", lambda: __import__("seed_expressive_state_v73", fromlist=["build_expressive_state"]).build_expressive_state()),
        safe("Memory Review Actions", "Top memory candidates plus save/ignore/later decision overlay.", lambda: __import__("seed_memory_review_actions_v73", fromlist=["load_candidates"]).load_candidates()),
        safe("Live Voice", "Record/transcribe/chat/say foundation.", lambda: {"ok": True, "tools": __import__("seed_voice_live_v73", fromlist=["voice_tools"]).voice_tools()}),
        safe("Avatar Panel", "Standalone web avatar panel from Seed state.", lambda: __import__("seed_avatar_panel_v73", fromlist=["build_avatar_panel"]).build_avatar_panel()),
        safe("Action Tasks", "Converts advice/repo/curiosity into actionable tasks.", lambda: __import__("seed_task_converter_v73", fromlist=["build_tasks"]).build_tasks()),
        safe("Curiosity Speaker", "Can speak one relevant grounded curiosity.", lambda: __import__("seed_curiosity_speaker_v73", fromlist=["build_spoken_curiosity"]).build_spoken_curiosity(False)),
    ]
    data = {"created_at": now_timestamp(), "version": "v73.0.0", "ok": all(c["status"] != "error" for c in cards), "cards": cards}
    STATE_FILE.write_text(json.dumps(data, indent=4, ensure_ascii=False))
    return data

def show_v73_status():
    data = build_v73_state()
    print("\n=== SEED v73 ACTION PRESENCE STATUS ===")
    print(f"OK: {data['ok']}")
    for card in data["cards"]:
        print(f"- {card['title']}: {card['status']} — {card['summary']}")
    return "handled"

if __name__ == "__main__":
    show_v73_status()
