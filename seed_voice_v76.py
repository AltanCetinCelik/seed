import json
import subprocess
from datetime import datetime
from pathlib import Path

SETTINGS_FILE = Path("seed_voice_v76_settings.json")
JOURNAL_FILE = Path("seed_voice_v76_journal.jsonl")

def now():
    return datetime.now().isoformat(timespec="seconds")

def defaults():
    return {
        "version": "v76.0.0",
        "seconds_default": 8,
        "retries_on_empty": 1,
        "language_mode": "auto",
        "macos_voice": None,
        "speak_replies": True,
        "journal_enabled": True,
        "avatar_sync": True,
    }

def load_settings():
    if SETTINGS_FILE.exists():
        try:
            data = json.loads(SETTINGS_FILE.read_text(errors="ignore"))
            base = defaults()
            base.update(data)
            return base
        except Exception:
            pass
    data = defaults()
    SETTINGS_FILE.write_text(json.dumps(data, indent=4, ensure_ascii=False))
    return data

def save_settings(**updates):
    data = load_settings()
    data.update(updates)
    data["updated_at"] = now()
    SETTINGS_FILE.write_text(json.dumps(data, indent=4, ensure_ascii=False))
    return data

def say_with_settings(text):
    settings = load_settings()
    if not settings.get("speak_replies", True):
        return False
    try:
        say = __import__("shutil").which("say")
        if not say:
            return False
        cmd = [say]
        if settings.get("macos_voice"):
            cmd += ["-v", settings["macos_voice"]]
        cmd.append(str(text or "")[:900])
        subprocess.run(cmd, timeout=90)
        return True
    except Exception:
        return False

def list_macos_voices(limit=80):
    try:
        proc = subprocess.run(["say", "-v", "?"], capture_output=True, text=True, timeout=20)
        voices = []
        for line in (proc.stdout or "").splitlines():
            if line.strip():
                voices.append(line.rstrip())
        return {"ok": True, "count": len(voices), "voices": voices[:limit]}
    except Exception as e:
        return {"ok": False, "error": str(e), "voices": []}

def append_journal(row):
    if not load_settings().get("journal_enabled", True):
        return
    with JOURNAL_FILE.open("a") as f:
        f.write(json.dumps(row, ensure_ascii=False) + "\n")

def voice_journal(limit=20):
    if not JOURNAL_FILE.exists():
        return []
    rows = []
    for line in JOURNAL_FILE.read_text(errors="ignore").splitlines()[-limit:]:
        try:
            rows.append(json.loads(line))
        except Exception:
            pass
    return rows

def set_avatar_mode(mode, reason):
    if not load_settings().get("avatar_sync", True):
        return
    try:
        from seed_embodied_state_v74 import save_state
        save_state(mode=mode, mode_reason=reason)
    except Exception:
        pass

def voice2_status():
    try:
        from seed_live_voice_v731 import voice_status
        base = voice_status()
    except Exception as e:
        base = {"ok": False, "error": str(e)}
    return {
        "created_at": now(),
        "version": "v76.0.0",
        "ok": bool(base.get("ok")),
        "base": base,
        "settings": load_settings(),
        "journal_entries": len(voice_journal(10000)),
        "commands": ["voice2 status", "voice settings", "voice once 8", "talk mode", "voice journal", "list voices", "set voice <name>"],
    }

def run_voice2_once(seconds=None, retries=None, speak=True):
    settings = load_settings()
    seconds = int(seconds or settings.get("seconds_default", 8))
    retries = int(settings.get("retries_on_empty", 1) if retries is None else retries)
    attempts = []

    try:
        from seed_live_voice_v731 import record_audio, transcribe_audio, ask_seed_text
    except Exception as e:
        print(f"Voice2 import failed: {e}")
        return {"ok": False, "error": str(e)}

    for attempt in range(retries + 1):
        set_avatar_mode("listening", f"Voice2 recording attempt {attempt+1}.")
        print(f"\n=== SEED v76 VOICE2 ONCE ({seconds}s) attempt {attempt+1}/{retries+1} ===")
        try:
            audio_path, device = record_audio(seconds)
            transcript = transcribe_audio(audio_path)
            text = (transcript.get("text") or "").strip()
            print(f"Transcript: {text or '[empty]'}")
            attempts.append({"audio": str(audio_path), "device": device, "text": text})

            if not text:
                continue

            set_avatar_mode("thinking", "Seed is thinking about a voice transcript.")
            answer = ask_seed_text(text)
            reply = answer.get("reply", "")
            print("\nSeed:")
            print(reply or "[no reply]")

            set_avatar_mode("speaking", "Seed is speaking a reply.")
            spoke = False
            if speak and reply:
                spoke = say_with_settings(reply)

            set_avatar_mode("idle", "Voice2 exchange complete.")

            row = {
                "created_at": now(),
                "version": "v76.0.0",
                "ok": True,
                "transcript": text,
                "reply": reply,
                "role": answer.get("role"),
                "model": answer.get("model"),
                "spoke": spoke,
                "attempts": attempts,
            }
            append_journal(row)
            return row
        except Exception as e:
            attempts.append({"error": str(e)})
            set_avatar_mode("warning", f"Voice2 error: {e}")

    row = {"created_at": now(), "version": "v76.0.0", "ok": False, "error": "empty transcript after retries", "attempts": attempts}
    append_journal(row)
    print("Voice2 recorded, but transcript stayed empty after retry.")
    return row

def talk_mode(max_turns=5, seconds=None):
    settings = load_settings()
    seconds = int(seconds or settings.get("seconds_default", 8))
    print("\n=== SEED v76 TALK MODE ===")
    print("Say 'stop seed' or press Ctrl+C to end.")
    turns = 0
    while turns < max_turns:
        turns += 1
        result = run_voice2_once(seconds=seconds, retries=settings.get("retries_on_empty", 1), speak=True)
        transcript = (result.get("transcript") or "").lower()
        if any(stop in transcript for stop in ["stop seed", "exit seed", "that's enough", "goodbye seed"]):
            print("Talk mode stopped.")
            break
    return {"ok": True, "turns": turns}

def show_voice_settings():
    print("\n=== SEED v76 VOICE 2.0 SETTINGS ===")
    print(json.dumps(voice2_status(), indent=4, ensure_ascii=False))

def show_voice_journal(limit=10):
    print("\n=== SEED v76 VOICE JOURNAL ===")
    rows = voice_journal(limit)
    if not rows:
        print("No v76 voice journal entries yet.")
        return
    for r in rows:
        print(f"- {r.get('created_at')} ok={r.get('ok')} model={r.get('model')} role={r.get('role')}")
        print(f"  You: {str(r.get('transcript',''))[:180]}")
        print(f"  Seed: {str(r.get('reply',''))[:180]}")

if __name__ == "__main__":
    show_voice_settings()
