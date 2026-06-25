import json
from datetime import datetime
from pathlib import Path

STATE_FILE = Path("seed_v88_systems_state.json")

def now():
    return datetime.now().isoformat(timespec="seconds")

def safe(title, summary, fn):
    try:
        data = fn()
        return {"title": title, "summary": summary, "status": "ok" if data.get("ok", True) else "warning", "data": data}
    except Exception as e:
        return {"title": title, "summary": summary, "status": "error", "error": str(e)}

def build_v88_state():
    cards = [
        safe("Fast Wake v87.2", "Warm Ollama, direct small prompt, inline follow-up.", lambda: __import__("seed_wake_fast_v872", fromlist=["wake_status"]).wake_status()),
        safe("Mac Body v88", "Open apps, URLs, screenshot, type, press keys, optional shell.", lambda: __import__("seed_mac_body_v88", fromlist=["body_status"]).body_status()),
        safe("Body Alive Runtime", "Panel + fast wake + curiosity + body status.", lambda: __import__("seed_body_alive_v88", fromlist=["body_alive_status"]).body_alive_status()),
    ]
    data = {"created_at": now(), "version": "v88.0.0", "ok": all(c["status"] != "error" for c in cards), "cards": cards}
    STATE_FILE.write_text(json.dumps(data, indent=4, ensure_ascii=False))
    return data

def show_v88_status():
    data = build_v88_state()
    print("\n=== SEED v88 MAC BODY + FAST WAKE STATUS ===")
    print(f"OK: {data['ok']}")
    for c in data["cards"]:
        print(f"- {c['title']}: {c['status']} — {c['summary']}")

if __name__ == "__main__":
    show_v88_status()
