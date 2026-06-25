import json
from datetime import datetime
from pathlib import Path

STATE_FILE = Path("seed_body_alive_v88_state.json")

def now():
    return datetime.now().isoformat(timespec="seconds")

def safe(fn):
    try:
        return fn()
    except Exception as e:
        return {"ok": False, "error": str(e)}

def start_body_alive():
    print("\n=== SEED v88 MAC BODY ALIVE MODE ===")
    print("Starting panel + fast wake + curiosity + Mac body status.")
    panel = safe(lambda: __import__("seed_runtime_v83", fromlist=["start_panel"]).start_panel(open_browser=True))
    wake = safe(lambda: __import__("seed_wake_fast_v872", fromlist=["start_daemon"]).start_daemon())
    curiosity = safe(lambda: __import__("seed_curiosity_life_v871", fromlist=["start_daemon"]).start_daemon())
    body = safe(lambda: __import__("seed_mac_body_v88", fromlist=["body_status"]).body_status())
    data = {"created_at": now(), "version": "v88.0.0", "ok": panel.get("ok") and wake.get("ok") and curiosity.get("ok") and body.get("ok"), "panel": panel, "wake": wake, "curiosity": curiosity, "body": body}
    STATE_FILE.write_text(json.dumps(data, indent=4, ensure_ascii=False))
    print(json.dumps(data, indent=4, ensure_ascii=False))
    return data

def stop_body_alive():
    wake = safe(lambda: __import__("seed_wake_fast_v872", fromlist=["stop_daemon"]).stop_daemon())
    curiosity = safe(lambda: __import__("seed_curiosity_life_v871", fromlist=["stop_daemon"]).stop_daemon())
    data = {"created_at": now(), "version": "v88.0.0", "ok": True, "wake": wake, "curiosity": curiosity}
    STATE_FILE.write_text(json.dumps(data, indent=4, ensure_ascii=False))
    print(json.dumps(data, indent=4, ensure_ascii=False))
    return data

def body_alive_status():
    wake = safe(lambda: __import__("seed_wake_fast_v872", fromlist=["wake_status"]).wake_status())
    body = safe(lambda: __import__("seed_mac_body_v88", fromlist=["body_status"]).body_status())
    curiosity = safe(lambda: __import__("seed_curiosity_life_v871", fromlist=["curiosity_status"]).curiosity_status())
    data = {"created_at": now(), "version": "v88.0.0", "ok": True, "wake": wake, "body": body, "curiosity": curiosity}
    STATE_FILE.write_text(json.dumps(data, indent=4, ensure_ascii=False))
    return data

def show_status():
    print("\n=== SEED v88 BODY ALIVE STATUS ===")
    print(json.dumps(body_alive_status(), indent=4, ensure_ascii=False))

if __name__ == "__main__":
    import sys
    arg = sys.argv[1] if len(sys.argv) > 1 else "status"
    if arg == "start":
        start_body_alive()
    elif arg == "stop":
        stop_body_alive()
    else:
        show_status()
