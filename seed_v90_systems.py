import json
from datetime import datetime
from pathlib import Path

STATE_FILE = Path("seed_v90_systems_state.json")

def now():
    return datetime.now().isoformat(timespec="seconds")

def safe(title, summary, fn):
    try:
        data = fn()
        return {"title": title, "summary": summary, "status": "ok" if data.get("ok", True) else "warning", "data": data}
    except Exception as e:
        return {"title": title, "summary": summary, "status": "error", "error": str(e)}

def build_v90_state():
    cards = [
        safe("Memory Garden", "Reviews organism notes and promotes only meaningful memories.", lambda: __import__("seed_memory_garden_v90", fromlist=["status"]).status()),
        safe("Garden Context", "Creates compact memory context for future Seed chat.", lambda: {"ok": True, "context": __import__("seed_memory_garden_v90", fromlist=["garden_context"]).garden_context()}),
    ]
    data = {"created_at": now(), "version": "v90.0.0", "ok": all(c["status"] != "error" for c in cards), "cards": cards}
    STATE_FILE.write_text(json.dumps(data, indent=4, ensure_ascii=False))
    return data

def show_v90_status():
    data = build_v90_state()
    print("\n=== SEED v90 MEMORY GARDEN STATUS ===")
    print(f"OK: {data['ok']}")
    for c in data["cards"]:
        print(f"- {c['title']}: {c['status']} — {c['summary']}")

if __name__ == "__main__":
    show_v90_status()
