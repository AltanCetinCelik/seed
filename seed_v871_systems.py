import json
from datetime import datetime
from pathlib import Path

STATE_FILE = Path("seed_v871_systems_state.json")

def now():
    return datetime.now().isoformat(timespec="seconds")

def safe(title, summary, fn):
    try:
        data = fn()
        return {"title": title, "summary": summary, "status": "ok" if data.get("ok", True) else "warning", "data": data}
    except Exception as e:
        return {"title": title, "summary": summary, "status": "error", "error": str(e)}

def build_v871_state():
    cards = [
        safe("Wake Conversation", "Direct Ollama route after wake; avoids old context/gate chain.", lambda: __import__("seed_wake_conversation_v871", fromlist=["load_settings"]).load_settings()),
        safe("Wake Listener v87.1", "Wake phrase to immediate conversation path.", lambda: __import__("seed_wake_word_v871", fromlist=["wake_status"]).wake_status()),
        safe("Curiosity v87.1", "More Altan-specific useful curiosity.", lambda: __import__("seed_curiosity_life_v871", fromlist=["curiosity_status"]).curiosity_status()),
        safe("Alive Runtime v87.1", "Panel + wake + curiosity together.", lambda: __import__("seed_alive_runtime_v871", fromlist=["alive_status"]).alive_status()),
    ]
    data = {"created_at": now(), "version": "v87.1.1", "ok": all(c["status"] != "error" for c in cards), "cards": cards}
    STATE_FILE.write_text(json.dumps(data, indent=4, ensure_ascii=False))
    return data

def show_v871_status():
    data = build_v871_state()
    print("\n=== SEED v87.1.1 WAKE CONVERSATION POLISH STATUS ===")
    print(f"OK: {data['ok']}")
    for c in data["cards"]:
        print(f"- {c['title']}: {c['status']} — {c['summary']}")

if __name__ == "__main__":
    show_v871_status()
