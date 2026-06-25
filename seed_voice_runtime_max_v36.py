import json
import shutil
import subprocess
from datetime import datetime
from pathlib import Path


VOICE_MAX_FILE = Path("seed_voice_runtime_max_v36.json")
TRANSCRIPT_FILE = Path("seed_voice_transcript_journal.jsonl")


def now_timestamp():
    return datetime.now().isoformat(timespec="seconds")


def provider_status():
    providers = {}
    for name in ["faster_whisper", "whisper", "livekit", "pipecat", "kokoro"]:
        try:
            __import__(name)
            installed = True
        except Exception:
            installed = False
        providers[name] = installed

    providers["macos_say"] = shutil.which("say") is not None
    return providers


def add_transcript(text, source="manual_voice"):
    item = {
        "created_at": now_timestamp(),
        "version": "v45.0.0",
        "source": source,
        "text": text
    }
    with open(TRANSCRIPT_FILE, "a") as file:
        file.write(json.dumps(item) + "\n")
    return item


def speak_text(text):
    if shutil.which("say"):
        subprocess.Popen(["say", str(text)[:500]])
        return {"ok": True, "provider": "macos_say", "text": str(text)[:500]}
    return {"ok": False, "error": "No local TTS provider found.", "text": text}


def voice_runtime_status():
    data = {
        "created_at": now_timestamp(),
        "version": "v45.0.0",
        "ok": True,
        "push_to_talk": True,
        "always_listening": False,
        "providers": provider_status(),
        "transcript_file": str(TRANSCRIPT_FILE),
        "pipeline": [
            "manual transcript or STT",
            "intent route",
            "Seed response",
            "optional TTS",
            "journal"
        ]
    }
    VOICE_MAX_FILE.write_text(json.dumps(data, indent=4))
    return data


def show_voice_max():
    print("\n=== SEED VOICE RUNTIME MAX v36 ===")
    print(json.dumps(voice_runtime_status(), indent=4))


def show_voice_say():
    text = input("Text to speak: ").strip()
    print(json.dumps(speak_text(text), indent=4))


def show_voice_journal():
    text = input("Transcript text: ").strip()
    print(json.dumps(add_transcript(text), indent=4))


if __name__ == "__main__":
    show_voice_max()
