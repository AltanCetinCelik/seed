import json
import os
import platform
import subprocess
from datetime import datetime


try:
    from seed_config import (
        SEED_VOICE_SESSION_FILE,
        VOICE_TTS_BACKEND,
        VOICE_STT_BACKEND,
        VOICE_ALLOW_SPEAKING,
        VOICE_NO_ALWAYS_LISTENING
    )
except Exception:
    SEED_VOICE_SESSION_FILE = "seed_voice_session.json"
    VOICE_TTS_BACKEND = "macos_say"
    VOICE_STT_BACKEND = "not_enabled"
    VOICE_ALLOW_SPEAKING = True
    VOICE_NO_ALWAYS_LISTENING = True


from seed_companion_os import (
    load_companion_os_state,
    save_companion_os_state,
    append_companion_os_event,
    append_companion_os_journal
)


try:
    from seed_llm import ask_llm
    LLM_AVAILABLE = True
except Exception:
    LLM_AVAILABLE = False


try:
    from seed_trace_engine import record_voice_trace
    TRACE_AVAILABLE = True
except Exception:
    TRACE_AVAILABLE = False


try:
    from seed_avatar_state import avatar_for_mode
    AVATAR_AVAILABLE = True
except Exception:
    AVATAR_AVAILABLE = False


try:
    from seed_continuity_engine import build_continuity_context
    CONTINUITY_AVAILABLE = True
except Exception:
    CONTINUITY_AVAILABLE = False


def now_timestamp():
    return datetime.now().isoformat(timespec="seconds")


def load_json(path, default):
    try:
        with open(path, "r") as file:
            return json.load(file)
    except FileNotFoundError:
        return default() if callable(default) else default
    except json.JSONDecodeError:
        return default() if callable(default) else default


def save_json(path, data):
    with open(path, "w") as file:
        json.dump(data, file, indent=4)


def default_voice_state():
    return {
        "created_at": now_timestamp(),
        "updated_at": now_timestamp(),
        "enabled": True,
        "tts_backend": VOICE_TTS_BACKEND,
        "stt_backend": VOICE_STT_BACKEND,
        "allow_speaking": VOICE_ALLOW_SPEAKING,
        "no_always_listening": VOICE_NO_ALWAYS_LISTENING,
        "mode": "push_to_talk_future",
        "last_spoken_at": None,
        "last_spoken_text": None,
        "history": [],
        "future_backends": {
            "stt": ["Whisper", "faster-whisper", "LiveKit/Pipecat direction"],
            "tts": ["Kokoro", "Chatterbox", "system say for alpha"],
            "realtime": ["LiveKit Agents", "Pipecat"]
        },
        "privacy_rules": [
            "No secret always-listening.",
            "Voice output only when user invokes voice command.",
            "Future STT must be push-to-talk first.",
            "Voice does not imply consciousness."
        ]
    }


def load_voice_state():
    return load_json(SEED_VOICE_SESSION_FILE, default_voice_state)


def save_voice_state(state):
    state["updated_at"] = now_timestamp()
    save_json(SEED_VOICE_SESSION_FILE, state)


def update_companion_voice_presence(voice_state):
    state = load_companion_os_state()
    voice = state.setdefault("presence", {}).setdefault("voice", {})

    voice["status"] = "alpha_enabled" if voice_state.get("enabled") else "disabled"
    voice["input"] = voice_state.get("stt_backend")
    voice["output"] = voice_state.get("tts_backend")
    voice["privacy"] = "no_secret_always_listening" if voice_state.get("no_always_listening") else "check_privacy"

    save_companion_os_state(state)


def initialize_voice_session():
    state = load_voice_state()
    save_voice_state(state)
    update_companion_voice_presence(state)

    append_companion_os_event(
        "voice_session_initialized",
        "Voice Session Alpha initialized",
        {
            "tts_backend": state.get("tts_backend"),
            "stt_backend": state.get("stt_backend"),
            "no_always_listening": state.get("no_always_listening")
        },
        source="voice_session",
        importance=4
    )

    print("Voice Session Alpha initialized.")
    return state


def can_speak():
    state = load_voice_state()

    if not state.get("enabled"):
        return False, "Voice is disabled."

    if not state.get("allow_speaking"):
        return False, "Voice speaking is not allowed in voice state."

    if state.get("tts_backend") == "macos_say" and platform.system().lower() != "darwin":
        return False, "macOS say backend requires macOS."

    return True, "Voice can speak."


def speak_text(text, reason="manual_voice"):
    state = load_voice_state()

    allowed, message = can_speak()

    if not allowed:
        print(message)
        return {
            "ok": False,
            "message": message
        }

    if text is None or text.strip() == "":
        return {
            "ok": False,
            "message": "Text cannot be empty."
        }

    if state.get("tts_backend") == "macos_say":
        subprocess.run(["say", text[:3500]])

    state["last_spoken_at"] = now_timestamp()
    state["last_spoken_text"] = text
    state.setdefault("history", []).append({
        "created_at": now_timestamp(),
        "text": text,
        "reason": reason
    })

    save_voice_state(state)
    update_companion_voice_presence(state)

    append_companion_os_event(
        "voice_spoken",
        "Seed voice spoke",
        {
            "reason": reason,
            "text_excerpt": text[:500]
        },
        source="voice_session",
        importance=3
    )

    if TRACE_AVAILABLE:
        try:
            record_voice_trace(
                title="Seed voice spoke",
                summary=f"Reason: {reason}\nText: {text[:1200]}",
                decision="spoken",
                risk="low"
            )
        except Exception:
            pass

    if AVATAR_AVAILABLE:
        try:
            avatar_for_mode("voice")
        except Exception:
            pass

    return {
        "ok": True,
        "message": "Spoken.",
        "text": text
    }


def speak_text_interactive():
    text = input("Text to speak: ").strip()

    if not text:
        print("Text required.")
        return

    result = speak_text(text, reason="manual")
    print(result["message"])


def voice_test():
    text = (
        "Seed Voice Alpha online. I am not conscious, but I am present as a "
        "local companion system with voice output when User invokes it."
    )

    result = speak_text(text, reason="voice_test")

    if result["ok"]:
        print("Voice test spoken.")
    else:
        print(result["message"])


def build_voice_pulse(chat_state=None):
    if CONTINUITY_AVAILABLE:
        try:
            context = build_continuity_context()
        except Exception as error:
            context = {"continuity_error": str(error)}
    else:
        context = {}

    if LLM_AVAILABLE:
        prompt = f"""
Create a short voice pulse for User.

Seed is not alive or conscious.
Seed is a local companion system.

Voice pulse must be short enough to speak aloud.
No cringe. No fake sentience.

Context:
{json.dumps(context, indent=2)}

Output:
- what changed
- what matters now
- one next action
Keep under 120 words.
"""

        text = ask_llm(prompt, task_type="chat", runtime_context=chat_state)
    else:
        text = (
            "Companion OS Alpha is online. The next move is to finish integration, "
            "then run the v2 release gate."
        )

    return text


def voice_pulse(chat_state=None):
    text = build_voice_pulse(chat_state=chat_state)
    result = speak_text(text, reason="voice_pulse")

    print("\n=== VOICE PULSE ===")
    print(text)

    return result


def voice_ritual(chat_state=None):
    state = load_companion_os_state()
    rituals = state.get("growth", {}).get("rituals", [])

    print("\n=== VOICE RITUAL ===")

    for ritual in rituals:
        print(f"- {ritual.get('id')} {ritual.get('title')}")

    ritual_id = input("Ritual ID or title: ").strip().lower()

    chosen = None

    for ritual in rituals:
        if ritual.get("id", "").lower() == ritual_id or ritual.get("title", "").lower() == ritual_id:
            chosen = ritual
            break

    if chosen is None:
        print("Ritual not found.")
        return None

    ritual_prompt = chosen.get("prompt", "")

    if LLM_AVAILABLE:
        prompt = f"""
Create a short spoken ritual for User.

Ritual:
{json.dumps(chosen, indent=2)}

Rules:
- Seed is not conscious.
- Direct, grounding, useful.
- Under 130 words.
"""
        text = ask_llm(prompt, task_type="chat", runtime_context=chat_state)
    else:
        text = ritual_prompt

    speak_text(text, reason=f"voice_ritual_{chosen.get('id')}")
    print(text)

    append_companion_os_journal(
        f"Voice ritual: {chosen.get('title')}",
        text
    )

    return text


def voice_off():
    state = load_voice_state()
    state["enabled"] = False
    save_voice_state(state)
    update_companion_voice_presence(state)

    append_companion_os_event(
        "voice_disabled",
        "Voice Session disabled",
        {},
        source="voice_session",
        importance=3
    )

    print("Voice disabled.")


def voice_on():
    state = load_voice_state()
    state["enabled"] = True
    save_voice_state(state)
    update_companion_voice_presence(state)

    append_companion_os_event(
        "voice_enabled",
        "Voice Session enabled",
        {},
        source="voice_session",
        importance=3
    )

    print("Voice enabled.")


def show_voice_status():
    state = load_voice_state()

    print("\n=== VOICE SESSION ALPHA ===")
    print(f"Enabled: {state.get('enabled')}")
    print(f"TTS backend: {state.get('tts_backend')}")
    print(f"STT backend: {state.get('stt_backend')}")
    print(f"Allow speaking: {state.get('allow_speaking')}")
    print(f"No always-listening: {state.get('no_always_listening')}")
    print(f"Mode: {state.get('mode')}")
    print(f"Last spoken: {state.get('last_spoken_at')}")
    print(f"History count: {len(state.get('history', []))}")

    print("\nPrivacy rules:")
    for rule in state.get("privacy_rules", []):
        print(f"- {rule}")

    print("\nFuture backends:")
    for key, value in state.get("future_backends", {}).items():
        print(f"- {key}: {', '.join(value)}")


def show_voice_history():
    state = load_voice_state()

    print("\n=== VOICE HISTORY ===")

    history = state.get("history", [])

    if not history:
        print("No voice history.")
        return

    for item in history[-20:]:
        print(f"\n{item.get('created_at')} — {item.get('reason')}")
        print(item.get("text"))


def get_voice_context_for_prompt():
    state = load_voice_state()

    text = "=== VOICE SESSION CONTEXT ===\n"
    text += f"Enabled: {state.get('enabled')}\n"
    text += f"TTS backend: {state.get('tts_backend')}\n"
    text += f"STT backend: {state.get('stt_backend')}\n"
    text += f"No always-listening: {state.get('no_always_listening')}\n"
    text += f"Last spoken: {state.get('last_spoken_at')}\n"
    text += """
Voice rule:
Voice Alpha is user-invoked output only.
No secret always-listening.
Voice does not imply Seed is conscious.
Future STT should be push-to-talk first.
"""
    return text


if __name__ == "__main__":
    initialize_voice_session()
    show_voice_status()
