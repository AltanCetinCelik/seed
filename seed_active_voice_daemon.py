import json
import os
import platform
import shutil
import subprocess
from datetime import datetime
from pathlib import Path


try:
    from seed_config import (
        SEED_ACTIVE_VOICE_STATE_FILE,
        SEED_ACTIVE_VOICE_INPUT_FILE,
        SEED_ACTIVE_VOICE_COMMAND_FILE,
        ACTIVE_VOICE_WAKE_WORDS,
        ACTIVE_VOICE_LISTEN_SECONDS,
        ACTIVE_VOICE_COMMAND_SECONDS,
        ACTIVE_VOICE_NO_SECRET_ALWAYS_LISTENING,
        ACTIVE_VOICE_REQUIRE_EXPLICIT_LAUNCH
    )
except Exception:
    SEED_ACTIVE_VOICE_STATE_FILE = "seed_active_voice_state.json"
    SEED_ACTIVE_VOICE_INPUT_FILE = "seed_active_voice_input.wav"
    SEED_ACTIVE_VOICE_COMMAND_FILE = "seed_active_voice_command.wav"
    ACTIVE_VOICE_WAKE_WORDS = ["seed", "hey seed", "yo seed"]
    ACTIVE_VOICE_LISTEN_SECONDS = 3
    ACTIVE_VOICE_COMMAND_SECONDS = 8
    ACTIVE_VOICE_NO_SECRET_ALWAYS_LISTENING = True
    ACTIVE_VOICE_REQUIRE_EXPLICIT_LAUNCH = True


try:
    from seed_voice_command_bridge import (
        ask_seed_text,
        speak_answer,
        voice_command_check_data,
        transcribe_audio
    )
    VOICE_COMMAND_BRIDGE_AVAILABLE = True
except Exception:
    VOICE_COMMAND_BRIDGE_AVAILABLE = False


try:
    from seed_companion_os import append_companion_os_event, append_companion_os_journal
    COMPANION_OS_AVAILABLE = True
except Exception:
    COMPANION_OS_AVAILABLE = False


try:
    from seed_trace_engine import append_trace, record_voice_trace
    TRACE_AVAILABLE = True
except Exception:
    TRACE_AVAILABLE = False


_WHISPER_MODEL = None


def now_timestamp():
    return datetime.now().isoformat(timespec="seconds")


def command_exists(name):
    return shutil.which(name) is not None


def load_json(path, default):
    try:
        with open(path, "r") as file:
            return json.load(file)
    except Exception:
        return default() if callable(default) else default


def save_json(path, data):
    with open(path, "w") as file:
        json.dump(data, file, indent=4)


def default_state():
    return {
        "created_at": now_timestamp(),
        "updated_at": now_timestamp(),
        "version": "v2.1.0",
        "mode": "explicit_active_voice",
        "truth": "Active voice is a user-launched local listener. Seed is not alive or conscious.",
        "no_secret_always_listening": True,
        "require_explicit_launch": True,
        "audio_device": ":0",
        "wake_words": ACTIVE_VOICE_WAKE_WORDS,
        "listen_seconds": ACTIVE_VOICE_LISTEN_SECONDS,
        "command_seconds": ACTIVE_VOICE_COMMAND_SECONDS,
        "history": [],
        "last_check": None,
        "rules": [
            "Active voice starts only when Altan launches it.",
            "No secret always-listening.",
            "Wake-word loop is local and explicit.",
            "STT must be local or explicitly approved.",
            "Seed must not execute tools from voice without approval.",
            "Seed is not alive, conscious, sentient, or human."
        ]
    }


def load_state():
    return load_json(SEED_ACTIVE_VOICE_STATE_FILE, default_state)


def save_state(state):
    state["updated_at"] = now_timestamp()
    save_json(SEED_ACTIVE_VOICE_STATE_FILE, state)


def ffmpeg_available():
    return command_exists("ffmpeg")


def faster_whisper_available():
    try:
        import faster_whisper  # noqa
        return True
    except Exception:
        return False


def active_voice_check_data():
    base = {}
    if VOICE_COMMAND_BRIDGE_AVAILABLE:
        try:
            base = voice_command_check_data()
        except Exception:
            base = {}

    state = load_state()

    data = {
        "created_at": now_timestamp(),
        "version": "v2.1.0",
        "platform": platform.system(),
        "ffmpeg_available": ffmpeg_available(),
        "faster_whisper_available": faster_whisper_available(),
        "voice_command_bridge_available": VOICE_COMMAND_BRIDGE_AVAILABLE,
        "tts_available": bool(base.get("tts_available")),
        "stt_available": faster_whisper_available(),
        "recording_available": ffmpeg_available() and platform.system().lower() == "darwin",
        "active_voice_ready": (
            ffmpeg_available()
            and faster_whisper_available()
            and VOICE_COMMAND_BRIDGE_AVAILABLE
            and bool(base.get("tts_available"))
        ),
        "no_secret_always_listening": (
            state.get("no_secret_always_listening") is True
            and ACTIVE_VOICE_NO_SECRET_ALWAYS_LISTENING is True
        ),
        "require_explicit_launch": (
            state.get("require_explicit_launch") is True
            and ACTIVE_VOICE_REQUIRE_EXPLICIT_LAUNCH is True
        ),
        "wake_words": state.get("wake_words", ACTIVE_VOICE_WAKE_WORDS),
        "audio_device": state.get("audio_device", ":0"),
        "rules": state.get("rules", [])
    }

    state["last_check"] = data
    save_state(state)
    return data


def show_active_voice_check():
    data = active_voice_check_data()

    print("\n=== SEED v2.1 ACTIVE VOICE CHECK ===")
    print(f"Active voice ready: {data['active_voice_ready']}")
    print(f"ffmpeg: {data['ffmpeg_available']}")
    print(f"faster-whisper: {data['faster_whisper_available']}")
    print(f"TTS available: {data['tts_available']}")
    print(f"Recording available: {data['recording_available']}")
    print(f"No secret always-listening: {data['no_secret_always_listening']}")
    print(f"Explicit launch required: {data['require_explicit_launch']}")
    print(f"Audio device: {data['audio_device']}")
    print(f"Wake words: {', '.join(data['wake_words'])}")

    if not data["active_voice_ready"]:
        print("\nMissing pieces:")
        if not data["ffmpeg_available"]:
            print("- ffmpeg missing: brew install ffmpeg")
        if not data["faster_whisper_available"]:
            print("- faster-whisper missing: python -m pip install faster-whisper")
        if not data["tts_available"]:
            print("- TTS unavailable: Seed voice output needs macOS say or seed_voice_session.")

    print("\nRules:")
    for rule in data["rules"]:
        print(f"- {rule}")


def list_macos_audio_devices():
    print("\n=== MAC AUDIO DEVICE LIST ===")
    if not ffmpeg_available():
        print("ffmpeg is missing. Install with: brew install ffmpeg")
        return

    if platform.system().lower() != "darwin":
        print("This helper is for macOS avfoundation.")
        return

    result = subprocess.run(
        ["ffmpeg", "-f", "avfoundation", "-list_devices", "true", "-i", ""],
        capture_output=True,
        text=True
    )

    print(result.stderr)


def set_audio_device_interactive():
    state = load_state()
    print("\nCurrent audio device:", state.get("audio_device", ":0"))
    print("For macOS default mic, ':0' often works.")
    print("To list devices, run /active-voice-devices.")
    device = input("New audio device value: ").strip()
    if not device:
        print("No change.")
        return

    state["audio_device"] = device
    save_state(state)
    print("Audio device updated:", device)


def record_audio(seconds, path):
    state = load_state()
    audio_device = state.get("audio_device", ":0")

    if not ffmpeg_available():
        return {
            "ok": False,
            "error": "ffmpeg is missing",
            "path": path
        }

    if platform.system().lower() != "darwin":
        return {
            "ok": False,
            "error": "active voice recording is currently macOS avfoundation only",
            "path": path
        }

    command = [
        "ffmpeg",
        "-y",
        "-hide_banner",
        "-loglevel",
        "error",
        "-f",
        "avfoundation",
        "-i",
        audio_device,
        "-t",
        str(seconds),
        "-ar",
        "16000",
        "-ac",
        "1",
        path
    ]

    result = subprocess.run(command, capture_output=True, text=True)

    return {
        "ok": result.returncode == 0 and Path(path).exists(),
        "command": " ".join(command),
        "returncode": result.returncode,
        "stdout": result.stdout[-1000:],
        "stderr": result.stderr[-2000:],
        "path": path
    }


def transcribe_local(audio_path):
    if VOICE_COMMAND_BRIDGE_AVAILABLE:
        return transcribe_audio(audio_path)

    return {
        "ok": False,
        "text": "",
        "error": "voice command bridge unavailable"
    }


def wake_detected(text):
    lowered = (text or "").lower()
    for word in ACTIVE_VOICE_WAKE_WORDS:
        if word.lower() in lowered:
            return True
    return False


def strip_wake_words(text):
    cleaned = text or ""
    for word in ACTIVE_VOICE_WAKE_WORDS:
        cleaned = cleaned.replace(word, "")
        cleaned = cleaned.replace(word.title(), "")
        cleaned = cleaned.replace(word.upper(), "")
    return cleaned.strip(" ,.!?:;-").strip()


def answer_and_speak(command_text, source="active_voice"):
    if not VOICE_COMMAND_BRIDGE_AVAILABLE:
        return {
            "ok": False,
            "error": "voice command bridge unavailable",
            "command_text": command_text
        }

    answer = ask_seed_text(command_text)
    spoken = speak_answer(answer, reason="active_voice_reply")

    item = {
        "created_at": now_timestamp(),
        "source": source,
        "command_text": command_text,
        "answer": answer,
        "spoken": spoken
    }

    state = load_state()
    state.setdefault("history", []).append(item)
    save_state(state)

    if TRACE_AVAILABLE:
        try:
            record_voice_trace(
                title="Active voice command answered",
                summary=json.dumps(item, indent=2)[:2500],
                decision="answered_and_spoken" if spoken and spoken.get("ok") else "answered",
                risk="low"
            )
        except Exception:
            try:
                append_trace(
                    trace_type="voice_trace",
                    title="Active voice command answered",
                    summary=json.dumps(item, indent=2)[:2500],
                    sources=["active_voice_daemon"],
                    decision="answered",
                    risk="low"
                )
            except Exception:
                pass

    if COMPANION_OS_AVAILABLE:
        try:
            append_companion_os_event(
                "active_voice_command_answered",
                "Active voice command answered",
                {"spoken": bool(spoken and spoken.get("ok"))},
                source="active_voice_daemon",
                importance=4
            )
        except Exception:
            pass

    return {
        "ok": True,
        "command_text": command_text,
        "answer": answer,
        "spoken": spoken
    }


def active_voice_once():
    check = active_voice_check_data()

    if not check["active_voice_ready"]:
        show_active_voice_check()
        return {
            "ok": False,
            "error": "active voice is not ready"
        }

    print("\nSay: Seed + your command.")
    print(f"Listening for {ACTIVE_VOICE_COMMAND_SECONDS} seconds...")

    recording = record_audio(ACTIVE_VOICE_COMMAND_SECONDS, SEED_ACTIVE_VOICE_COMMAND_FILE)

    if not recording.get("ok"):
        print(json.dumps(recording, indent=4))
        return {
            "ok": False,
            "stage": "record",
            "recording": recording
        }

    transcript = transcribe_local(SEED_ACTIVE_VOICE_COMMAND_FILE)
    print("\nTranscript:")
    print(transcript.get("text"))

    if not transcript.get("ok"):
        print(json.dumps(transcript, indent=4))
        return {
            "ok": False,
            "stage": "transcribe",
            "transcript": transcript
        }

    command_text = strip_wake_words(transcript.get("text", ""))

    if not command_text:
        command_text = transcript.get("text", "")

    result = answer_and_speak(command_text, source="active_voice_once")
    print("\nSeed:")
    print(result.get("answer"))
    return result


def active_voice_loop():
    check = active_voice_check_data()

    print("\n=== SEED v2.1 ACTIVE VOICE LISTENER ===")
    print("This is explicit local listening only while this window is open.")
    print("No secret always-listening.")
    print("Say one of:", ", ".join(ACTIVE_VOICE_WAKE_WORDS))
    print("Say 'Seed stop' or press CTRL+C to stop.")
    print(f"Active voice ready: {check['active_voice_ready']}")

    if not check["active_voice_ready"]:
        show_active_voice_check()
        print("\nInstall missing dependencies, then restart this launcher.")
        return

    try:
        while True:
            print("\nListening for wake word...")
            recording = record_audio(ACTIVE_VOICE_LISTEN_SECONDS, SEED_ACTIVE_VOICE_INPUT_FILE)

            if not recording.get("ok"):
                print("Recording failed:")
                print(json.dumps(recording, indent=4))
                break

            transcript = transcribe_local(SEED_ACTIVE_VOICE_INPUT_FILE)
            text = transcript.get("text", "").strip()
            if text:
                print("Heard:", text)

            if not transcript.get("ok") or not text:
                continue

            if wake_detected(text):
                maybe_command = strip_wake_words(text)

                if "stop" in maybe_command.lower() or "quit" in maybe_command.lower():
                    speak_answer("Active voice listener stopped.", reason="active_voice_stop")
                    print("Stopped.")
                    break

                if maybe_command and len(maybe_command.split()) >= 2:
                    result = answer_and_speak(maybe_command, source="active_voice_wake_inline")
                    print("\nSeed:")
                    print(result.get("answer"))
                    continue

                speak_answer("Yes?", reason="active_voice_wake_ack")
                print("Wake word detected. Listening for command...")
                active_voice_once()

    except KeyboardInterrupt:
        print("\nActive voice listener stopped by Altan.")


def active_voice_install_plan():
    print("\n=== ACTIVE VOICE INSTALL PLAN ===")
    print("Run:")
    print("brew install ffmpeg")
    print("python -m pip install faster-whisper")
    print("")
    print("Then test:")
    print("python seed_active_voice_daemon.py")
    print("")
    print("If microphone device fails:")
    print("1. Run /active-voice-devices")
    print("2. Pick the microphone index")
    print("3. Run /active-voice-device")
    print("4. Set audio device like ':0' or ':1'")
    print("")
    print("Privacy:")
    print("- Active voice only listens while you explicitly run the listener.")
    print("- No background hidden listener is installed.")


def show_active_voice_history():
    state = load_state()
    print("\n=== ACTIVE VOICE HISTORY ===")
    for item in state.get("history", [])[-20:]:
        print(f"\n{item.get('created_at')} — {item.get('source')}")
        print("Altan:", item.get("command_text"))
        print("Seed:", item.get("answer"))


def get_active_voice_context_for_prompt():
    data = active_voice_check_data()
    text = "=== ACTIVE VOICE CONTEXT ===\n"
    text += f"Active voice ready: {data['active_voice_ready']}\n"
    text += f"ffmpeg: {data['ffmpeg_available']}\n"
    text += f"faster-whisper: {data['faster_whisper_available']}\n"
    text += f"TTS: {data['tts_available']}\n"
    text += f"Recording: {data['recording_available']}\n"
    text += f"No secret always-listening: {data['no_secret_always_listening']}\n"
    text += "Rule: active voice is local and explicit; no hidden background listener.\n"
    return text


if __name__ == "__main__":
    active_voice_loop()
