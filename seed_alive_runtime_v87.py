import json
from datetime import datetime
from pathlib import Path

STATE_FILE = Path("seed_alive_runtime_v87_state.json")

def now():
    return datetime.now().isoformat(timespec="seconds")

def safe(fn):
    try:
        return fn()
    except Exception as e:
        return {"ok": False, "error": str(e)}

def start_alive():
    print("\n=== SEED v87 ALIVE COMPANION MODE ===")
    print("Starting panel, wake listener, and curiosity loop.")
    panel = safe(lambda: __import__("seed_runtime_v83", fromlist=["start_panel"]).start_panel(open_browser=True))
    wake = safe(lambda: __import__("seed_wake_word_v861", fromlist=["start_daemon"]).start_daemon())
    curiosity = safe(lambda: __import__("seed_curiosity_life_v87", fromlist=["start_daemon"]).start_daemon())
    data = {"created_at": now(), "version": "v87.0.0", "ok": panel.get("ok") and wake.get("ok") and curiosity.get("ok"), "panel": panel, "wake": wake, "curiosity": curiosity}
    STATE_FILE.write_text(json.dumps(data, indent=4, ensure_ascii=False))
    print(json.dumps(data, indent=4, ensure_ascii=False))
    return data

def stop_alive():
    wake = safe(lambda: __import__("seed_wake_word_v861", fromlist=["stop_daemon"]).stop_daemon())
    curiosity = safe(lambda: __import__("seed_curiosity_life_v87", fromlist=["stop_daemon"]).stop_daemon())
    data = {"created_at": now(), "version": "v87.0.0", "ok": True, "wake": wake, "curiosity": curiosity}
    STATE_FILE.write_text(json.dumps(data, indent=4, ensure_ascii=False))
    print(json.dumps(data, indent=4, ensure_ascii=False))
    return data

def alive_status():
    wake = safe(lambda: __import__("seed_wake_word_v861", fromlist=["wake_status"]).wake_status())
    curiosity = safe(lambda: __import__("seed_curiosity_life_v87", fromlist=["curiosity_status"]).curiosity_status())
    senses = safe(lambda: __import__("seed_senses_v87", fromlist=["sense_status"]).sense_status())
    data = {"created_at": now(), "version": "v87.0.0", "ok": True, "wake": wake, "curiosity": curiosity, "senses": senses}
    STATE_FILE.write_text(json.dumps(data, indent=4, ensure_ascii=False))
    return data

def show_alive():
    print("\n=== SEED v87 ALIVE STATUS ===")
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
