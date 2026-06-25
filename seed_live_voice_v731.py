import json
import os
import re
import shutil
import subprocess
from datetime import datetime
from pathlib import Path

VOICE_DIR = Path("seed_voice_recordings_v731")
VOICE_DIR.mkdir(exist_ok=True)

JOURNAL_FILE = Path("seed_voice_journal_v731.jsonl")
SETTINGS_FILE = Path("seed_voice_settings_v731.json")


def now_timestamp():
    return datetime.now().isoformat(timespec="seconds")


def tool_path(name):
    return shutil.which(name)


def load_settings():
    if SETTINGS_FILE.exists():
        try:
            return json.loads(SETTINGS_FILE.read_text(errors="ignore"))
        except Exception:
            pass
    return {
        "version": "v73.1.0",
        "ffmpeg_avfoundation_audio_device": ":0",
        "whisper_model": os.environ.get("SEED_WHISPER_MODEL", "tiny.en"),
        "speak_reply": True,
    }


def save_settings(data):
    data["updated_at"] = now_timestamp()
    SETTINGS_FILE.write_text(json.dumps(data, indent=4, ensure_ascii=False))
    return data


def voice_status():
    data = {
        "created_at": now_timestamp(),
        "version": "v73.1.0",
        "ok": True,
        "tools": {
            "ffmpeg": tool_path("ffmpeg"),
            "macos_say": tool_path("say"),
            "faster_whisper": False,
        },
        "settings": load_settings(),
        "commands": [
            "voice once",
            "voice once 8",
            "voice devices",
            "voice test say",
            "voice status",
        ],
        "path": "record -> transcribe -> Seed local chat -> optional macOS say -> journal",
    }

    try:
        import faster_whisper  # noqa: F401
        data["tools"]["faster_whisper"] = True
    except Exception:
        data["tools"]["faster_whisper"] = False

    return data


def show_voice_status():
    print("\n=== SEED v73.1 LIVE VOICE ===")
    print(json.dumps(voice_status(), indent=4, ensure_ascii=False))
    print("To record: type 'voice once' or 'voice once 8'.")
    return "handled"


def list_voice_devices():
    ffmpeg = tool_path("ffmpeg")
    if not ffmpeg:
        print("ffmpeg not found.")
        return "handled"

    print("\n=== macOS audio/video devices from ffmpeg ===")
    proc = subprocess.run(
        [ffmpeg, "-f", "avfoundation", "-list_devices", "true", "-i", ""],
        capture_output=True,
        text=True,
        timeout=20,
    )

    output = (proc.stderr or proc.stdout or "").strip()
    print(output[-5000:] if output else "No device output.")
    print("\nFor Mac audio, Seed tries :0, :1, :2 automatically.")
    return "handled"


def _record_with_device(seconds, device):
    ffmpeg = tool_path("ffmpeg")
    if not ffmpeg:
        raise RuntimeError("ffmpeg not found.")

    stamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    out = VOICE_DIR / f"voice_{stamp}.wav"

    cmd = [
        ffmpeg,
        "-y",
        "-loglevel",
        "error",
        "-f",
        "avfoundation",
        "-i",
        device,
        "-t",
        str(int(seconds)),
        "-ar",
        "16000",
        "-ac",
        "1",
        str(out),
    ]

    proc = subprocess.run(cmd, capture_output=True, text=True, timeout=int(seconds) + 20)

    if proc.returncode != 0 or not out.exists() or out.stat().st_size < 2000:
        raise RuntimeError((proc.stderr or proc.stdout or "recording failed").strip())

    return out


def record_audio(seconds=6):
    settings = load_settings()
    preferred = settings.get("ffmpeg_avfoundation_audio_device", ":0")
    candidates = []
    for dev in [preferred, ":0", ":1", ":2", ":3"]:
        if dev not in candidates:
            candidates.append(dev)

    errors = []
    for device in candidates:
        try:
            path = _record_with_device(seconds, device)
            settings["ffmpeg_avfoundation_audio_device"] = device
            save_settings(settings)
            return path, device
        except Exception as error:
            errors.append(f"{device}: {error}")

    raise RuntimeError("Could not record audio with any tried device:\n" + "\n".join(errors[-5:]))


def transcribe_audio(path):
    try:
        from faster_whisper import WhisperModel
    except Exception as error:
        raise RuntimeError(f"faster_whisper import failed: {error}")

    settings = load_settings()
    model_name = settings.get("whisper_model", "tiny.en")

    model = WhisperModel(model_name, device="cpu", compute_type="int8")
    segments, info = model.transcribe(str(path), beam_size=1, vad_filter=True)

    text = " ".join(seg.text.strip() for seg in segments).strip()

    return {
        "text": text,
        "language": getattr(info, "language", None),
        "duration": getattr(info, "duration", None),
        "model": model_name,
    }


def ask_seed_text(message):
    try:
        from seed_local_chat_v701 import choose_role, model_fallbacks, call_ollama
    except Exception as error:
        raise RuntimeError(f"Could not import Seed local chat router: {error}")

    role = choose_role(message)

    for model in model_fallbacks(role):
        try:
            print(f"Using {model} for {role}.")
            reply = call_ollama(model, role, message)
            reply = (reply or "").strip()

            if reply and reply.lower() not in {"normal", "ok", "okay"}:
                return {
                    "ok": True,
                    "role": role,
                    "model": model,
                    "reply": reply,
                }
        except Exception as error:
            last_error = str(error)

    return {
        "ok": False,
        "role": role,
        "model": None,
        "reply": "",
        "error": locals().get("last_error", "no valid reply"),
    }


def say_text(text):
    say = tool_path("say")
    if not say:
        return False

    clean = str(text or "").strip()
    if not clean:
        return False

    subprocess.run([say, clean[:900]], timeout=90)
    return True


def append_journal(row):
    with JOURNAL_FILE.open("a") as f:
        f.write(json.dumps(row, ensure_ascii=False) + "\n")


def run_voice_once(seconds=6, speak=True):
    print(f"\n=== SEED v73.1 VOICE ONCE ({seconds}s) ===")
    print("Recording now. Speak after the microphone permission prompt if macOS shows one.")

    try:
        audio_path, device = record_audio(seconds)
        print(f"Recorded: {audio_path} using device {device}")

        transcript = transcribe_audio(audio_path)
        text = transcript.get("text", "").strip()

        print(f"Transcript: {text or '[empty]'}")

        if not text:
            row = {
                "created_at": now_timestamp(),
                "ok": False,
                "audio": str(audio_path),
                "device": device,
                "error": "empty transcript",
            }
            append_journal(row)
            print("I recorded, but transcription was empty. Try 'voice once 8' and speak closer to the mic.")
            return "handled"

        answer = ask_seed_text(text)
        reply = answer.get("reply", "")

        print("\nSeed:")
        print(reply or "[no reply]")

        did_say = False
        if speak and reply:
            did_say = say_text(reply)

        row = {
            "created_at": now_timestamp(),
            "ok": answer.get("ok"),
            "audio": str(audio_path),
            "device": device,
            "transcript": text,
            "transcript_meta": transcript,
            "role": answer.get("role"),
            "model": answer.get("model"),
            "reply": reply,
            "spoke": did_say,
        }
        append_journal(row)

        return "handled"

    except Exception as error:
        row = {
            "created_at": now_timestamp(),
            "ok": False,
            "error": str(error),
            "hint": "Run 'voice devices' if recording fails. macOS may need microphone permission for Terminal.",
        }
        append_journal(row)

        print("\nVoice failed:")
        print(error)
        print("\nTry:")
        print("- voice devices")
        print("- give Terminal/iTerm microphone permission in macOS Settings > Privacy & Security > Microphone")
        print("- voice once 8")
        return "handled"


def handle_voice_command_v731(user_message):
    text = str(user_message or "").strip().lower()

    if text in {"voice status", "voice live", "voice"}:
        return show_voice_status()

    if text in {"voice devices", "list voice devices", "mic devices", "microphone devices"}:
        return list_voice_devices()

    if text in {"voice test say", "test say", "say test"}:
        say_text("Seed voice output is working.")
        print("macOS say test sent.")
        return "handled"

    if text.startswith("voice once") or text.startswith("record voice") or text.startswith("test voice"):
        match = re.search(r"\b(\d{1,2})\b", text)
        seconds = int(match.group(1)) if match else 6
        seconds = max(2, min(seconds, 20))
        return run_voice_once(seconds=seconds, speak=True)

    return None


if __name__ == "__main__":
    show_voice_status()
