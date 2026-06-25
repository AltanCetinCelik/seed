import json
from datetime import datetime
from pathlib import Path

STATE_FILE = Path("seed_v87_systems_state.json")

def now():
    return datetime.now().isoformat(timespec="seconds")

def safe(title, summary, fn):
    try:
        data = fn()
        return {"title": title, "summary": summary, "status": "ok" if data.get("ok", True) else "warning", "data": data}
    except Exception as e:
        return {"title": title, "summary": summary, "status": "error", "error": str(e)}

def build_v87_state():
    cards = [
        safe("Companion Self-State", "Private friend/companion framing, current v87 truth.", lambda: __import__("seed_self_state_v87", fromlist=["build_self_state"]).build_self_state()),
        safe("Wake Polish", "Long phrase priority, false-positive filtering, better reply.", lambda: __import__("seed_wake_word_v861", fromlist=["wake_status"]).wake_status()),
        safe("Senses", "Screen capture sense and camera availability check.", lambda: __import__("seed_senses_v87", fromlist=["sense_status"]).sense_status()),
        safe("Curiosity / Alive Loop", "Seed notices, queues, asks, and speaks within anti-spam limits.", lambda: __import__("seed_curiosity_life_v87", fromlist=["curiosity_status"]).curiosity_status()),
        safe("Alive Runtime", "Starts panel + wake + curiosity together.", lambda: __import__("seed_alive_runtime_v87", fromlist=["alive_status"]).alive_status()),
    ]
    data = {"created_at": now(), "version": "v87.0.0", "ok": all(c["status"] != "error" for c in cards), "cards": cards}
    STATE_FILE.write_text(json.dumps(data, indent=4, ensure_ascii=False))
    return data

def show_v87_status():
    data = build_v87_state()
    print("\n=== SEED v87 ALIVE COMPANION STATUS ===")
    print(f"OK: {data['ok']}")
    for c in data["cards"]:
        print(f"- {c['title']}: {c['status']} — {c['summary']}")

if __name__ == "__main__":
    show_v87_status()
