import inspect
import json
import os
import platform
import shutil
import subprocess
from datetime import datetime
from pathlib import Path


try:
    from seed_config import (
        SEED_VOICE_COMMAND_STATE_FILE,
        SEED_VOICE_COMMAND_INPUT_AUDIO_FILE,
        SEED_VOICE_COMMAND_TRANSCRIPT_FILE,
        VOICE_COMMAND_DEFAULT_RECORD_SECONDS,
        VOICE_COMMAND_NO_ALWAYS_LISTENING,
        VOICE_COMMAND_TYPED_FALLBACK
    )
except Exception:
    SEED_VOICE_COMMAND_STATE_FILE = "seed_voice_command_state.json"
    SEED_VOICE_COMMAND_INPUT_AUDIO_FILE = "seed_voice_command_input.wav"
    SEED_VOICE_COMMAND_TRANSCRIPT_FILE = "seed_voice_command_transcript.txt"
    VOICE_COMMAND_DEFAULT_RECORD_SECONDS = 6
    VOICE_COMMAND_NO_ALWAYS_LISTENING = True
    VOICE_COMMAND_TYPED_FALLBACK = True


try:
    from seed_voice_session import speak_text
    VOICE_SESSION_AVAILABLE = True
except Exception:
    VOICE_SESSION_AVAILABLE = False


try:
    from seed_trace_engine import append_trace, record_voice_trace
    TRACE_AVAILABLE = True
except Exception:
    TRACE_AVAILABLE = False


try:
    from seed_companion_os import append_companion_os_event, append_companion_os_journal
    COMPANION_OS_AVAILABLE = True
except Exception:
    COMPANION_OS_AVAILABLE = False


try:
    from seed_companion_os_context import get_full_companion_os_context_for_prompt
    CONTEXT_AVAILABLE = True
except Exception:
    CONTEXT_AVAILABLE = False


try:
    from seed_llm import ask_llm
    LLM_AVAILABLE = True
except Exception:
    LLM_AVAILABLE = False


try:
    from seed_companion_os_commands import handle_companion_os_command
    COMMANDS_AVAILABLE = True
except Exception:
    COMMANDS_AVAILABLE = False


_WHISPER_MODEL_CACHE = None


def get_cached_whisper_model():
    global _WHISPER_MODEL_CACHE

    if _WHISPER_MODEL_CACHE is not None:
        return _WHISPER_MODEL_CACHE

    try:
        from seed_config import SEED_VOICE_WHISPER_MODEL
        model_name = SEED_VOICE_WHISPER_MODEL
    except Exception:
        model_name = "tiny"

    from faster_whisper import WhisperModel
    _WHISPER_MODEL_CACHE = WhisperModel(model_name, device="cpu", compute_type="int8")
    return _WHISPER_MODEL_CACHE


VOICE_COMMAND_RULES = [
    "Voice command mode is push-to-talk / explicit session only.",
    "Seed must not secretly always-listen.",
    "Typed fallback is allowed when STT is not installed.",
    "STT is optional and must be user-invoked.",
    "Voice output does not imply Seed is alive or conscious.",
    "Seed can speak replies back when user invokes voice command mode.",
    "External installs and microphone configuration require Altan's approval."
]


def now_timestamp():
    return datetime.now().isoformat(timespec="seconds")


def load_json(path, default):
    try:
        with open(path, "r") as file:
            return json.load(file)
    except Exception:
        return default() if callable(default) else default


def save_json(path, data):
    with open(path, "w") as file:
        json.dump(data, file, indent=4)


def default_voice_command_state():
    return {
        "created_at": now_timestamp(),
        "updated_at": now_timestamp(),
        "version": "v2.0.0",
        "mode": "push_to_talk",
        "truth": "Voice command is an explicit interface. Seed is not alive or conscious.",
        "no_always_listening": True,
        "typed_fallback": True,
        "audio_device": ":0",
        "default_record_seconds": VOICE_COMMAND_DEFAULT_RECORD_SECONDS,
        "history": [],
        "last_check": None,
        "last_launcher_created": None,
        "rules": VOICE_COMMAND_RULES
    }


def load_voice_command_state():
    return load_json(SEED_VOICE_COMMAND_STATE_FILE, default_voice_command_state)


def save_voice_command_state(state):
    state["updated_at"] = now_timestamp()
    save_json(SEED_VOICE_COMMAND_STATE_FILE, state)


def command_exists(name):
    return shutil.which(name) is not None


def faster_whisper_import_available():
    try:
        import faster_whisper  # noqa: F401
        return True
    except Exception:
        return False


def whisper_cli_available():
    return command_exists("whisper")


def ffmpeg_available():
    return command_exists("ffmpeg")


def macos_say_available():
    return platform.system().lower() == "darwin" and command_exists("say")


def voice_command_check_data():
    state = load_voice_command_state()

    data = {
        "created_at": now_timestamp(),
        "version": "v2.0.0",
        "platform": platform.system(),
        "python": os.sys.executable,
        "no_always_listening": state.get("no_always_listening") is True and VOICE_COMMAND_NO_ALWAYS_LISTENING is True,
        "typed_fallback": state.get("typed_fallback") is True and VOICE_COMMAND_TYPED_FALLBACK is True,
        "voice_session_available": VOICE_SESSION_AVAILABLE,
        "tts_available": VOICE_SESSION_AVAILABLE or macos_say_available(),
        "ffmpeg_available": ffmpeg_available(),
        "faster_whisper_import_available": faster_whisper_import_available(),
        "whisper_cli_available": whisper_cli_available(),
        "stt_available": faster_whisper_import_available() or whisper_cli_available(),
        "recording_available": ffmpeg_available() and platform.system().lower() == "darwin",
        "push_to_talk_ready": True,
        "rules": VOICE_COMMAND_RULES
    }

    data["ready"] = (
        data["push_to_talk_ready"]
        and data["typed_fallback"]
        and data["tts_available"]
        and data["no_always_listening"]
    )

    state["last_check"] = data
    save_voice_command_state(state)
    return data


def show_voice_command_check():
    data = voice_command_check_data()

    print("\n=== SEED VOICE COMMAND CHECK ===")
    print(f"Ready: {data['ready']}")
    print(f"Typed fallback: {data['typed_fallback']}")
    print(f"TTS available: {data['tts_available']}")
    print(f"STT available: {data['stt_available']}")
    print(f"Recording available: {data['recording_available']}")
    print(f"ffmpeg: {data['ffmpeg_available']}")
    print(f"faster-whisper import: {data['faster_whisper_import_available']}")
    print(f"whisper CLI: {data['whisper_cli_available']}")
    print(f"No always-listening: {data['no_always_listening']}")

    print("\nRules:")
    for rule in data["rules"]:
        print(f"- {rule}")

    if not data["stt_available"]:
        print("\nSTT note:")
        print("- STT is optional for v2.0.0. Seed uses typed fallback plus spoken replies.")
        print("- For true speech input later: install/configure ffmpeg + faster-whisper after approval.")


def record_audio_push_to_talk(seconds=None, output_path=None):
    state = load_voice_command_state()
    seconds = int(seconds or state.get("default_record_seconds", VOICE_COMMAND_DEFAULT_RECORD_SECONDS))
    output_path = output_path or SEED_VOICE_COMMAND_INPUT_AUDIO_FILE
    audio_device = state.get("audio_device", ":0")

    if not ffmpeg_available():
        return {
            "ok": False,
            "error": "ffmpeg is not installed.",
            "output_path": output_path
        }

    if platform.system().lower() != "darwin":
        return {
            "ok": False,
            "error": "Automatic recording path is currently configured for macOS avfoundation only.",
            "output_path": output_path
        }

    command = [
        "ffmpeg",
        "-y",
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
        output_path
    ]

    print(f"Recording for {seconds} seconds. Speak now.")
    result = subprocess.run(command, capture_output=True, text=True)

    return {
        "ok": result.returncode == 0 and Path(output_path).exists(),
        "returncode": result.returncode,
        "command": " ".join(command),
        "stdout": result.stdout[-1000:],
        "stderr": result.stderr[-3000:],
        "output_path": output_path
    }


def clean_audio_for_transcription(audio_path):
    """
    Create a cleaner 16k mono WAV for STT.
    Uses ffmpeg filters when available.
    """
    try:
        from seed_config import SEED_VOICE_AUDIO_CLEANUP_ENABLED
        enabled = bool(SEED_VOICE_AUDIO_CLEANUP_ENABLED)
    except Exception:
        enabled = True

    if not enabled:
        return audio_path

    try:
        import shutil
        import subprocess
        from pathlib import Path

        if shutil.which("ffmpeg") is None:
            return audio_path

        source = Path(audio_path)
        if not source.exists():
            return audio_path

        cleaned = source.with_name(source.stem + "_clean.wav")

        command = [
            "ffmpeg",
            "-y",
            "-hide_banner",
            "-loglevel",
            "error",
            "-i",
            str(source),
            "-af",
            "highpass=f=80,lowpass=f=7800,dynaudnorm,loudnorm",
            "-ar",
            "16000",
            "-ac",
            "1",
            str(cleaned)
        ]

        result = subprocess.run(command, capture_output=True, text=True)

        if result.returncode == 0 and cleaned.exists():
            return str(cleaned)

        return audio_path
    except Exception:
        return audio_path


def transcribe_audio(audio_path=None):
    audio_path = audio_path or SEED_VOICE_COMMAND_INPUT_AUDIO_FILE

    if not Path(audio_path).exists():
        return {
            "ok": False,
            "error": f"Audio file not found: {audio_path}",
            "text": ""
        }

    audio_path = clean_audio_for_transcription(audio_path)

    if faster_whisper_import_available():
        try:
            try:
                from seed_config import SEED_VOICE_TRANSCRIBE_BEAM_SIZE
                beam_size = int(SEED_VOICE_TRANSCRIBE_BEAM_SIZE)
            except Exception:
                beam_size = 1

            try:
                from seed_config import (
                    SEED_VOICE_VAD_FILTER,
                    SEED_VOICE_CONDITION_ON_PREVIOUS_TEXT,
                    SEED_VOICE_LANGUAGE_HINT,
                    SEED_VOICE_INITIAL_PROMPT
                )
                vad_filter = bool(SEED_VOICE_VAD_FILTER)
                condition_on_previous_text = bool(SEED_VOICE_CONDITION_ON_PREVIOUS_TEXT)
                language_hint = SEED_VOICE_LANGUAGE_HINT
                initial_prompt = SEED_VOICE_INITIAL_PROMPT
            except Exception:
                vad_filter = True
                condition_on_previous_text = False
                language_hint = None
                initial_prompt = "Altan is talking to Seed."

            model = get_cached_whisper_model()
            segments, info = model.transcribe(
                audio_path,
                beam_size=beam_size,
                vad_filter=vad_filter,
                condition_on_previous_text=condition_on_previous_text,
                temperature=0,
                language=language_hint,
                initial_prompt=initial_prompt
            )
            text = " ".join(segment.text.strip() for segment in segments).strip()

            Path(SEED_VOICE_COMMAND_TRANSCRIPT_FILE).write_text(text)

            return {
                "ok": bool(text),
                "backend": "faster_whisper_cached",
                "text": text,
                "language": getattr(info, "language", None)
            }
        except Exception as error:
            return {
                "ok": False,
                "backend": "faster_whisper_cached",
                "error": str(error),
                "text": ""
            }

    if whisper_cli_available():
        try:
            result = subprocess.run(
                ["whisper", audio_path, "--model", "base", "--fp16", "False", "--output_format", "txt"],
                capture_output=True,
                text=True
            )

            txt_path = str(Path(audio_path).with_suffix(".txt"))
            text = ""
            if Path(txt_path).exists():
                text = Path(txt_path).read_text().strip()

            Path(SEED_VOICE_COMMAND_TRANSCRIPT_FILE).write_text(text)

            return {
                "ok": result.returncode == 0 and bool(text),
                "backend": "whisper_cli",
                "text": text,
                "stdout": result.stdout[-1000:],
                "stderr": result.stderr[-2000:]
            }
        except Exception as error:
            return {
                "ok": False,
                "backend": "whisper_cli",
                "error": str(error),
                "text": ""
            }

    return {
        "ok": False,
        "error": "No STT backend installed. Use typed fallback.",
        "text": ""
    }


def speak_answer(text, reason="voice_command_reply"):
    if not text:
        return {
            "ok": False,
            "message": "No text to speak."
        }

    if VOICE_SESSION_AVAILABLE:
        try:
            return speak_text(text, reason=reason)
        except Exception as error:
            return {
                "ok": False,
                "message": f"Seed voice_session speak_text failed: {error}"
            }

    if macos_say_available():
        result = subprocess.run(["say", text], capture_output=True, text=True)
        return {
            "ok": result.returncode == 0,
            "message": "Spoken through macOS say.",
            "returncode": result.returncode,
            "stderr": result.stderr[-1000:]
        }

    return {
        "ok": False,
        "message": "No TTS backend available."
    }


def call_ask_llm(prompt):
    if not LLM_AVAILABLE:
        return "Voice command bridge cannot reach Seed LLM right now."

    try:
        sig = inspect.signature(ask_llm)
        kwargs = {}
        if "task_type" in sig.parameters:
            kwargs["task_type"] = "voice_command"
        if "runtime_context" in sig.parameters:
            kwargs["runtime_context"] = None
        return ask_llm(prompt, **kwargs)
    except TypeError:
        try:
            return ask_llm(prompt)
        except Exception as error:
            return f"Seed LLM call failed: {error}"
    except Exception as error:
        return f"Seed LLM call failed: {error}"


def ask_seed_text(user_text):
    user_text = (user_text or "").strip()

    if not user_text:
        return "I did not receive a command."

    try:
        from seed_action_kernel import maybe_handle_action_text
        action_answer = maybe_handle_action_text(user_text)
        if action_answer:
            return action_answer
    except Exception as error:
        if any(word in user_text.lower() for word in ["open", "cockpit", "browser", "memory", "agent", "mcp"]):
            return f"I tried to route that through the action kernel, but it failed: {error}"

    try:
        from seed_cockpit_browser_action import maybe_handle_cockpit_voice_action
        cockpit_action_answer = maybe_handle_cockpit_voice_action(user_text)
        if cockpit_action_answer:
            return cockpit_action_answer
    except Exception as error:
        if "cockpit" in user_text.lower() or "dashboard" in user_text.lower():
            return f"I tried to open Cockpit, but the local action failed: {error}"

    if user_text.startswith("/") and COMMANDS_AVAILABLE:
        try:
            result = handle_companion_os_command(user_text, chat_state={})
            if result == "handled":
                return f"Command {user_text} was handled. Check the terminal output."
        except Exception as error:
            return f"Command failed: {error}"

    try:
        from seed_config import SEED_VOICE_SKIP_HEAVY_CONTEXT_IN_VOICE
        skip_heavy_context = bool(SEED_VOICE_SKIP_HEAVY_CONTEXT_IN_VOICE)
    except Exception:
        skip_heavy_context = True

    if skip_heavy_context:
        try:
            from seed_fast_voice_context import get_fast_voice_context_for_prompt
            context = get_fast_voice_context_for_prompt(user_text)
        except Exception:
            context = ""
    elif CONTEXT_AVAILABLE:
        try:
            context = get_full_companion_os_context_for_prompt(user_text)
        except Exception:
            context = ""
    else:
        context = ""

    prompt = f"""
You are Seed v2.0.0, Altan's local-first Companion OS.

Truth boundary:
Seed is not alive, conscious, sentient, or human.
Seed can still be companion-like through memory, continuity, tools, rituals, voice, and approval-gated agency.
Altan remains in control.

Voice command rule:
Answer the spoken/typed command directly.
Do not mention that this is a prompt.
Do not explain your internal context.
Keep the answer useful and speakable.

Context:
{context}

Altan said:
{user_text}

Seed answer:
"""

    answer = call_ask_llm(prompt)

    if not isinstance(answer, str):
        answer = str(answer)

    return answer.strip()


def log_voice_command(source, user_text, answer, spoken_result=None):
    state = load_voice_command_state()

    item = {
        "created_at": now_timestamp(),
        "source": source,
        "user_text": user_text,
        "answer": answer,
        "spoken_result": spoken_result
    }

    state.setdefault("history", []).append(item)
    save_voice_command_state(state)

    if TRACE_AVAILABLE:
        try:
            record_voice_trace(
                title="Voice command handled",
                summary=json.dumps(item, indent=2)[:2500],
                decision="answered_and_spoken" if spoken_result and spoken_result.get("ok") else "answered",
                risk="low"
            )
        except Exception:
            try:
                append_trace(
                    trace_type="voice_trace",
                    title="Voice command handled",
                    summary=json.dumps(item, indent=2)[:2500],
                    sources=["voice_command_bridge"],
                    decision="answered",
                    risk="low"
                )
            except Exception:
                pass

    if COMPANION_OS_AVAILABLE:
        try:
            append_companion_os_event(
                "voice_command_handled",
                "Voice command handled",
                {"source": source, "spoken": bool(spoken_result and spoken_result.get("ok"))},
                source="voice_command_bridge",
                importance=4
            )
        except Exception:
            pass

    return item


def handle_text_voice_command(user_text, speak=True, source="typed_fallback"):
    answer = ask_seed_text(user_text)
    spoken = None

    if speak:
        spoken = speak_answer(answer, reason="voice_command_reply")

    log_voice_command(source, user_text, answer, spoken)

    return {
        "ok": True,
        "user_text": user_text,
        "answer": answer,
        "spoken": spoken
    }


def handle_recorded_voice_command(seconds=None, speak=True):
    recording = record_audio_push_to_talk(seconds=seconds)

    if not recording.get("ok"):
        return {
            "ok": False,
            "stage": "record",
            "recording": recording
        }

    transcript = transcribe_audio(recording.get("output_path"))

    if not transcript.get("ok"):
        return {
            "ok": False,
            "stage": "transcribe",
            "recording": recording,
            "transcript": transcript
        }

    result = handle_text_voice_command(transcript.get("text"), speak=speak, source="recorded_stt")
    result["recording"] = recording
    result["transcript"] = transcript
    return result


def voice_command_record_test():
    check = voice_command_check_data()
    print("\n=== VOICE COMMAND RECORD TEST ===")

    if not check["recording_available"]:
        print("Recording is not available.")
        print("Reason: ffmpeg missing, non-macOS platform, or avfoundation unavailable.")
        print("Typed fallback remains ready.")
        return

    seconds = input(f"Record seconds [{VOICE_COMMAND_DEFAULT_RECORD_SECONDS}]: ").strip()
    seconds = int(seconds) if seconds else VOICE_COMMAND_DEFAULT_RECORD_SECONDS

    result = handle_recorded_voice_command(seconds=seconds, speak=True)
    print(json.dumps(result, indent=4))


def voice_command_loop():
    check = voice_command_check_data()

    print("\n=== SEED v2.0.0 VOICE COMMAND BRIDGE ===")
    print("Mode: explicit push-to-talk / typed fallback")
    print("No always-listening.")
    print(f"Ready: {check['ready']}")
    print(f"STT available: {check['stt_available']}")
    print(f"Recording available: {check['recording_available']}")
    print("\nCommands:")
    print("- Type a message and press Enter")
    print("- Type r to record audio when recording/STT is available")
    print("- Type check to show voice command check")
    print("- Type q to quit")

    while True:
        raw = input("\nAltan / r / check / q: ").strip()

        if raw.lower() in ["q", "quit", "exit"]:
            print("Voice command bridge closed.")
            break

        if raw.lower() == "check":
            show_voice_command_check()
            continue

        if raw.lower() == "r":
            result = handle_recorded_voice_command(speak=True)
            if not result.get("ok"):
                print(json.dumps(result, indent=4))
                print("Typed fallback is still available.")
            else:
                print("\nSeed:")
                print(result.get("answer"))
            continue

        if not raw:
            continue

        result = handle_text_voice_command(raw, speak=True, source="typed_fallback")
        print("\nSeed:")
        print(result.get("answer"))


def show_voice_command_history():
    state = load_voice_command_state()
    print("\n=== VOICE COMMAND HISTORY ===")
    for item in state.get("history", [])[-20:]:
        print(f"\n{item.get('created_at')} — {item.get('source')}")
        print(f"Altan: {item.get('user_text')}")
        print(f"Seed: {item.get('answer')}")


def voice_command_install_plan():
    print("\n=== OPTIONAL STT INSTALL PLAN ===")
    print("This is optional. v2.0.0 works with typed fallback + spoken replies.")
    print("")
    print("For real recorded speech input on Mac:")
    print("1. Install ffmpeg:")
    print("   brew install ffmpeg")
    print("2. Install faster-whisper into Seed's Python environment:")
    print("   python -m pip install faster-whisper")
    print("3. Run:")
    print("   python seed_voice_command_bridge.py")
    print("4. Type r inside the voice command bridge.")
    print("")
    print("Privacy rule: no always-listening; recording starts only when you explicitly choose it.")


def get_voice_command_context_for_prompt():
    check = voice_command_check_data()
    text = "=== VOICE COMMAND BRIDGE CONTEXT ===\n"
    text += f"Ready: {check['ready']}\n"
    text += f"Typed fallback: {check['typed_fallback']}\n"
    text += f"TTS available: {check['tts_available']}\n"
    text += f"STT available: {check['stt_available']}\n"
    text += f"Recording available: {check['recording_available']}\n"
    text += f"No always-listening: {check['no_always_listening']}\n"
    text += "Rule: explicit push-to-talk or typed fallback only. No secret always-listening.\n"
    return text


if __name__ == "__main__":
    voice_command_loop()
