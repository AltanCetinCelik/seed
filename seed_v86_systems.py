import json
from datetime import datetime
from pathlib import Path

STATE_FILE = Path("seed_v86_systems_state.json")

def now():
    return datetime.now().isoformat(timespec="seconds")

def safe(title, summary, fn):
    try:
        data = fn()
        return {"title": title, "summary": summary, "status": "ok" if data.get("ok", True) else "warning", "data": data}
    except Exception as e:
        return {"title": title, "summary": summary, "status": "error", "error": str(e)}

def build_v86_state():
    cards = [
        safe("Wake Word Listener", "Say Seed / wake up to open Seed and start voice.", lambda: __import__("seed_wake_word_v86", fromlist=["wake_status"]).wake_status()),
        safe("Voice 2.0 Base", "v76 voice still available.", lambda: __import__("seed_voice_v76", fromlist=["voice2_status"]).voice2_status()),
        safe("Runtime Base", "v83 one-command runtime still available.", lambda: __import__("seed_runtime_v83", fromlist=["runtime_status"]).runtime_status()),
        safe("v85 Base", "v85.3 real-v1 prep gate remains available.", lambda: __import__("seed_v85_gate", fromlist=["run_v85_gate"]).run_v85_gate()),
    ]
    data = {"created_at": now(), "version": "v86.0.0", "ok": all(c["status"] != "error" for c in cards), "cards": cards}
    STATE_FILE.write_text(json.dumps(data, indent=4, ensure_ascii=False))
    return data

def show_v86_status():
    data = build_v86_state()
    print("\n=== SEED v86 WAKE WORD STATUS ===")
    print(f"OK: {data['ok']}")
    for c in data["cards"]:
        print(f"- {c['title']}: {c['status']} — {c['summary']}")

if __name__ == "__main__":
    show_v86_status()
