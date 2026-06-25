import json
from datetime import datetime
from pathlib import Path

STATE_FILE = Path("seed_v75_systems_state.json")

def now():
    return datetime.now().isoformat(timespec="seconds")

def safe(title, summary, fn):
    try:
        data = fn()
        return {"title": title, "summary": summary, "status": "ok" if data.get("ok", True) else "warning", "data": data}
    except Exception as e:
        return {"title": title, "summary": summary, "status": "error", "error": str(e)}

def build_v75_state():
    # IMPORTANT:
    # This can call self_state because self_state no longer calls v75_gate.
    cards = [
        safe("Self-State Truth", "Seed knows current version and green layers without recursion.", lambda: __import__("seed_self_state_v741", fromlist=["build_self_state"]).build_self_state()),
        safe("Real Memory Review", "Review/save/ignore/later accepted memory store.", lambda: __import__("seed_memory_review_v75", fromlist=["memory_summary"]).memory_summary()),
        safe("Embodied Companion", "v74 panel remains green.", lambda: __import__("seed_v74_gate", fromlist=["run_v74_gate"]).run_v74_gate()),
        safe("Voice Pipeline", "v73.1 voice remains green.", lambda: __import__("seed_v731_gate", fromlist=["run_v731_gate"]).run_v731_gate()),
    ]

    data = {
        "created_at": now(),
        "version": "v75.1.0",
        "ok": all(card["status"] != "error" for card in cards),
        "cards": cards,
        "hotfix": "v75.1 recursion fix",
    }

    STATE_FILE.write_text(json.dumps(data, indent=4, ensure_ascii=False))
    return data

def show_v75_status():
    data = build_v75_state()
    print("\n=== SEED v75.1 SELF-TRUTH + REAL MEMORY STATUS ===")
    print(f"OK: {data['ok']}")
    for card in data["cards"]:
        print(f"- {card['title']}: {card['status']} — {card['summary']}")

if __name__ == "__main__":
    show_v75_status()
