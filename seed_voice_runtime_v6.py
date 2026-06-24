import importlib.util
import json
import shutil
from datetime import datetime
from pathlib import Path


try:
    from seed_config import SEED_VOICE_RUNTIME_FILE
except Exception:
    SEED_VOICE_RUNTIME_FILE = "seed_voice_runtime_v6.json"


PROVIDERS = {
    "faster_whisper": {
        "kind": "stt",
        "import_name": "faster_whisper",
        "role": "local speech-to-text"
    },
    "whisper": {
        "kind": "stt",
        "import_name": "whisper",
        "role": "speech-to-text fallback"
    },
    "livekit": {
        "kind": "realtime_voice",
        "import_name": "livekit",
        "role": "future realtime voice pipeline"
    },
    "pipecat": {
        "kind": "realtime_voice",
        "import_name": "pipecat",
        "role": "future realtime multimodal pipeline"
    },
    "kokoro": {
        "kind": "tts",
        "import_name": "kokoro",
        "role": "future local text-to-speech"
    }
}


def now_timestamp():
    return datetime.now().isoformat(timespec="seconds")


def provider_status():
    out = {}
    for provider, spec in PROVIDERS.items():
        out[provider] = {
            **spec,
            "installed": importlib.util.find_spec(spec["import_name"]) is not None
        }
    return out


def build_voice_runtime():
    runtime = {
        "created_at": now_timestamp(),
        "version": "v20.0.0",
        "ok": True,
        "runtime": "Seed Voice Runtime v6",
        "mode": {
            "push_to_talk": True,
            "one_shot": True,
            "always_listening": False,
            "secret_recording": False
        },
        "providers": provider_status(),
        "commands": {
            "voice_runtime": "/voice-runtime",
            "voice_ux": "/voice-ux",
            "voice_one_shot": "/voice-one-shot",
            "latency": "/latency"
        },
        "pipeline": [
            "push-to-talk or one-shot transcript",
            "terminal/command guard",
            "intent route",
            "manual approval for risky action",
            "event bus logging",
            "optional TTS response"
        ]
    }

    with open(SEED_VOICE_RUNTIME_FILE, "w") as file:
        json.dump(runtime, file, indent=4)

    return runtime


def add_transcript(text, source="manual"):
    path = Path("seed_voice_transcript_journal.jsonl")
    item = {
        "created_at": now_timestamp(),
        "version": "v20.0.0",
        "source": source,
        "text": text
    }
    with open(path, "a") as file:
        file.write(json.dumps(item) + "\n")
    return item


def show_voice_runtime():
    data = build_voice_runtime()
    print("\n=== SEED VOICE RUNTIME v6 ===")
    print(f"Push-to-talk: {data['mode']['push_to_talk']}")
    print(f"Always listening: {data['mode']['always_listening']}")
    print("Providers:")
    for name, spec in data["providers"].items():
        print(f"- {name}: installed={spec['installed']} role={spec['role']}")


if __name__ == "__main__":
    show_voice_runtime()
