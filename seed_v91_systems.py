import json
from datetime import datetime
from pathlib import Path

STATE_FILE = Path("seed_v91_systems_state.json")

def now():
    return datetime.now().isoformat(timespec="seconds")

def safe(title, summary, fn):
    try:
        data = fn()
        return {"title": title, "summary": summary, "status": "ok" if data.get("ok", True) else "warning", "data": data}
    except Exception as e:
        return {"title": title, "summary": summary, "status": "error", "error": str(e)}

def build_v91_state():
    cards = [
        safe("Companion Context", "Builds Seed identity + Memory Garden context for replies.", lambda: __import__("seed_companion_context_v91", fromlist=["status"]).status()),
        safe("Contextual Chat", "Direct Ollama chat that thinks with v91 context.", lambda: __import__("seed_contextual_chat_v91", fromlist=["status"]).status()),
        safe("Contextual Wake", "Wake listener that uses v91 contextual chat and wake mishear handling.", lambda: __import__("seed_wake_context_v91", fromlist=["wake_status"]).wake_status()),
    ]
    data = {"created_at": now(), "version": "v91.0.0", "ok": all(c["status"] != "error" for c in cards), "cards": cards}
    STATE_FILE.write_text(json.dumps(data, indent=4, ensure_ascii=False))
    return data

def show_v91_status():
    data = build_v91_state()
    print("\n=== SEED v91 COMPANION CONTEXT STATUS ===")
    print(f"OK: {data['ok']}")
    for c in data["cards"]:
        print(f"- {c['title']}: {c['status']} — {c['summary']}")

if __name__ == "__main__":
    show_v91_status()
