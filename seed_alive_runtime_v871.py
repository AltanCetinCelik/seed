import json
from datetime import datetime
from pathlib import Path

STATE_FILE = Path("seed_alive_runtime_v871_state.json")

def now():
    return datetime.now().isoformat(timespec="seconds")

def safe(fn):
    try:
        return fn()
    except Exception as e:
        return {"ok": False, "error": str(e)}

def start_alive():
    print("\n=== SEED v87.1 ALIVE MODE ===")
    print("Starting panel + low-latency wake + curiosity.")
    panel = safe(lambda: __import__("seed_runtime_v83", fromlist=["start_panel"]).start_panel(open_browser=True))
    wake = safe(lambda: __import__("seed_wake_word_v871", fromlist=["start_daemon"]).start_daemon())
    curiosity = safe(lambda: __import__("seed_curiosity_life_v871", fromlist=["start_daemon"]).start_daemon())
    data = {"created_at": now(), "version": "v87.1.0", "ok": panel.get("ok") and wake.get("ok") and curiosity.get("ok"), "panel": panel, "wake": wake, "curiosity": curiosity}
    STATE_FILE.write_text(json.dumps(data, indent=4, ensure_ascii=False))
    print(json.dumps(data, indent=4, ensure_ascii=False))
    return data

def stop_alive():
    wake = safe(lambda: __import__("seed_wake_word_v871", fromlist=["stop_daemon"]).stop_daemon())
    curiosity = safe(lambda: __import__("seed_curiosity_life_v871", fromlist=["stop_daemon"]).stop_daemon())
    data = {"created_at": now(), "version": "v87.1.0", "ok": True, "wake": wake, "curiosity": curiosity}
    STATE_FILE.write_text(json.dumps(data, indent=4, ensure_ascii=False))
    print(json.dumps(data, indent=4, ensure_ascii=False))
    return data

def alive_status():
    wake = safe(lambda: __import__("seed_wake_word_v871", fromlist=["wake_status"]).wake_status())
    curiosity = safe(lambda: __import__("seed_curiosity_life_v871", fromlist=["curiosity_status"]).curiosity_status())
    conversation = safe(lambda: __import__("seed_wake_conversation_v871", fromlist=["load_settings"]).load_settings())
    data = {"created_at": now(), "version": "v87.1.0", "ok": True, "wake": wake, "curiosity": curiosity, "conversation_settings": conversation}
    STATE_FILE.write_text(json.dumps(data, indent=4, ensure_ascii=False))
    return data

def show_alive():
    print("\n=== SEED v87.1 ALIVE STATUS ===")
    print(json.dumps(alive_status(), indent=4, ensure_ascii=False))

if __name__ == "__main__":
    import sys
    arg = sys.argv[1] if len(sys.argv) > 1 else "status"
    if arg == "start":
        start_alive()
    elif arg == "stop":
        stop_alive()
    else:
        show_alive()
