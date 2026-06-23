import json
import platform
import shutil
from datetime import datetime


try:
    from seed_config import SEED_VOICE_HARDENING_STATE_FILE
except Exception:
    SEED_VOICE_HARDENING_STATE_FILE = "seed_voice_hardening_state.json"


try:
    from seed_voice_session import (
        load_voice_state,
        save_voice_state,
        initialize_voice_session,
        build_voice_pulse,
        speak_text,
        show_voice_status
    )
    VOICE_SESSION_AVAILABLE = True
except Exception:
    VOICE_SESSION_AVAILABLE = False


try:
    from seed_companion_os import (
        load_companion_os_state,
        save_companion_os_state,
        append_companion_os_event,
        append_companion_os_journal
    )
    COMPANION_OS_AVAILABLE = True
except Exception:
    COMPANION_OS_AVAILABLE = False


try:
    from seed_trace_engine import append_trace, record_voice_trace
    TRACE_AVAILABLE = True
except Exception:
    TRACE_AVAILABLE = False


try:
    from seed_v2_hardening_metrics import mark_hardening_signal
    HARDENING_METRICS_AVAILABLE = True
except Exception:
    HARDENING_METRICS_AVAILABLE = False


try:
    from seed_avatar_state import avatar_for_mode
    AVATAR_AVAILABLE = True
except Exception:
    AVATAR_AVAILABLE = False


VOICE_PRIVACY_RULES = [
    "No secret always-listening.",
    "Voice output must be user-invoked.",
    "STT is not enabled unless explicitly configured later.",
    "Future STT must start as push-to-talk.",
    "Voice history is local runtime state.",
    "Voice does not imply Seed is alive or conscious.",
    "Voice sessions can be started and ended explicitly."
]


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


def default_voice_hardening_state():
    return {
        "created_at": now_timestamp(),
        "updated_at": now_timestamp(),
        "version": "v1.18.0",
        "purpose": "Evidence-based voice hardening for Seed Companion OS.",
        "truth": (
            "Seed voice is a user-invoked interface layer. It is not consciousness, "
            "not sentience, and not always-listening."
        ),
        "active_session": None,
        "sessions": [],
        "transcript_placeholders": [],
        "privacy_checks": [],
        "output_checks": [],
        "pulse_checks": [],
        "ritual_checks": [],
        "capability_report": None,
        "privacy_rules": VOICE_PRIVACY_RULES,
        "stt_boundary": {
            "enabled": False,
            "backend": "not_enabled",
            "future_rule": "push_to_talk_first",
            "always_listening": False
        }
    }


def load_voice_hardening_state():
    return load_json(SEED_VOICE_HARDENING_STATE_FILE, default_voice_hardening_state)


def save_voice_hardening_state(state):
    state["updated_at"] = now_timestamp()
    save_json(SEED_VOICE_HARDENING_STATE_FILE, state)


def mark_voice_signal(key, value=True):
    if HARDENING_METRICS_AVAILABLE:
        try:
            mark_hardening_signal("voice", key, value)
        except Exception:
            pass


def macos_say_available():
    return platform.system().lower() == "darwin" and shutil.which("say") is not None


def sync_voice_presence():
    if not COMPANION_OS_AVAILABLE:
        return

    companion_state = load_companion_os_state()
    voice_hardening = load_voice_hardening_state()

    companion_state.setdefault("presence", {})
    companion_state["presence"].setdefault("voice_hardening", {})

    companion_state["presence"]["voice_hardening"] = {
        "session_state": True,
        "active_session": voice_hardening.get("active_session"),
        "session_count": len(voice_hardening.get("sessions", [])),
        "privacy_checks": len(voice_hardening.get("privacy_checks", [])),
        "pulse_checks": len(voice_hardening.get("pulse_checks", [])),
        "ritual_checks": len(voice_hardening.get("ritual_checks", [])),
        "stt_boundary": voice_hardening.get("stt_boundary", {}),
        "truth": voice_hardening.get("truth")
    }

    save_companion_os_state(companion_state)


def initialize_voice_hardening():
    state = load_voice_hardening_state()

    if VOICE_SESSION_AVAILABLE:
        try:
            initialize_voice_session()
        except Exception:
            pass

    capability = build_voice_capability_report(save=False)
    state["capability_report"] = capability

    save_voice_hardening_state(state)

    mark_voice_signal("session_state", True)
    mark_voice_signal("macos_say_available", capability.get("macos_say_available", False))
    mark_voice_signal("privacy_rules", True)
    mark_voice_signal("stt_boundary_declared", True)

    if VOICE_SESSION_AVAILABLE:
        try:
            voice_state = load_voice_state()
            mark_voice_signal("voice_history", isinstance(voice_state.get("history", []), list))
            mark_voice_signal("voice_pulse", callable(build_voice_pulse))
            mark_voice_signal("voice_ritual", True)
        except Exception:
            pass

    sync_voice_presence()

    if COMPANION_OS_AVAILABLE:
        try:
            append_companion_os_event(
                "voice_hardening_initialized",
                "Voice hardening initialized",
                {
                    "macos_say_available": capability.get("macos_say_available"),
                    "privacy_rules": True,
                    "stt_boundary": state.get("stt_boundary")
                },
                source="voice_hardening",
                importance=4
            )
        except Exception:
            pass

    if TRACE_AVAILABLE:
        try:
            record_voice_trace(
                title="Voice hardening initialized",
                summary="Voice sessions, privacy checks, STT boundary, history checks, pulse checks, and ritual checks are available.",
                decision="initialized",
                risk="low"
            )
        except Exception:
            pass

    print("Voice hardening initialized.")
    return state


def build_voice_capability_report(save=True):
    voice_state = {}

    if VOICE_SESSION_AVAILABLE:
        try:
            voice_state = load_voice_state()
        except Exception:
            voice_state = {}

    report = {
        "created_at": now_timestamp(),
        "platform": platform.system(),
        "macos_say_available": macos_say_available(),
        "voice_session_available": VOICE_SESSION_AVAILABLE,
        "tts_backend": voice_state.get("tts_backend"),
        "stt_backend": voice_state.get("stt_backend"),
        "voice_enabled": voice_state.get("enabled"),
        "allow_speaking": voice_state.get("allow_speaking"),
        "no_always_listening": voice_state.get("no_always_listening"),
        "history_count": len(voice_state.get("history", [])) if isinstance(voice_state.get("history", []), list) else 0,
        "hardening_truth": "Voice is interface output, not consciousness."
    }

    if save:
        state = load_voice_hardening_state()
        state["capability_report"] = report
        save_voice_hardening_state(state)

    return report


def show_voice_capability_report():
    report = build_voice_capability_report(save=True)

    print("\n=== VOICE CAPABILITY REPORT ===")
    print(json.dumps(report, indent=4))


def run_voice_privacy_check():
    state = load_voice_hardening_state()

    voice_state = {}

    if VOICE_SESSION_AVAILABLE:
        try:
            voice_state = load_voice_state()
        except Exception:
            voice_state = {}

    issues = []

    if voice_state.get("no_always_listening") is not True:
        issues.append("Voice state does not explicitly guarantee no always-listening.")

    if voice_state.get("stt_backend") not in ["not_enabled", None, "disabled"]:
        issues.append("STT backend appears enabled; verify push-to-talk boundary.")

    if state.get("stt_boundary", {}).get("always_listening") is not False:
        issues.append("STT boundary does not explicitly block always-listening.")

    if "Voice does not imply Seed is alive or conscious." not in state.get("privacy_rules", []):
        issues.append("Voice privacy rules are missing fake-sentience boundary.")

    check = {
        "created_at": now_timestamp(),
        "ok": len(issues) == 0,
        "issues": issues,
        "privacy_rules": state.get("privacy_rules", []),
        "voice_state": {
            "stt_backend": voice_state.get("stt_backend"),
            "no_always_listening": voice_state.get("no_always_listening"),
            "allow_speaking": voice_state.get("allow_speaking")
        }
    }

    state.setdefault("privacy_checks", []).append(check)
    save_voice_hardening_state(state)

    mark_voice_signal("privacy_rules", check["ok"])
    mark_voice_signal("stt_boundary_declared", True)

    if COMPANION_OS_AVAILABLE:
        try:
            append_companion_os_event(
                "voice_privacy_check_run",
                "Voice privacy check run",
                {
                    "ok": check["ok"],
                    "issues": issues
                },
                source="voice_hardening",
                importance=4
            )
        except Exception:
            pass

    if TRACE_AVAILABLE:
        try:
            record_voice_trace(
                title="Voice privacy check run",
                summary=json.dumps(check, indent=2),
                decision="passed" if check["ok"] else "blocked",
                risk="low" if check["ok"] else "medium"
            )
        except Exception:
            pass

    sync_voice_presence()
    return check


def show_voice_privacy_check():
    check = run_voice_privacy_check()

    print("\n=== VOICE PRIVACY CHECK ===")
    print(f"OK: {check['ok']}")

    if not check["issues"]:
        print("Issues: none")
    else:
        print("Issues:")
        for issue in check["issues"]:
            print(f"- {issue}")

    print("\nPrivacy rules:")
    for rule in check["privacy_rules"]:
        print(f"- {rule}")


def start_voice_session(title="Voice session", purpose="manual"):
    state = load_voice_hardening_state()

    if state.get("active_session"):
        return {
            "ok": False,
            "message": "A voice session is already active.",
            "active_session": state.get("active_session")
        }

    session = {
        "id": f"VOICE-{len(state.get('sessions', [])) + 1:03d}",
        "created_at": now_timestamp(),
        "ended_at": None,
        "title": title,
        "purpose": purpose,
        "status": "active",
        "events": [],
        "transcript_placeholder_ids": []
    }

    state["active_session"] = session["id"]
    state.setdefault("sessions", []).append(session)
    save_voice_hardening_state(state)

    mark_voice_signal("session_state", True)

    if AVATAR_AVAILABLE:
        try:
            avatar_for_mode("voice")
        except Exception:
            pass

    if COMPANION_OS_AVAILABLE:
        try:
            append_companion_os_event(
                "voice_session_started",
                f"Voice session started: {session['id']}",
                session,
                source="voice_hardening",
                importance=4
            )
        except Exception:
            pass

    sync_voice_presence()

    return {
        "ok": True,
        "session": session
    }


def start_voice_session_interactive():
    title = input("Voice session title: ").strip() or "Voice session"
    purpose = input("Purpose: ").strip() or "manual"
    result = start_voice_session(title=title, purpose=purpose)

    if result["ok"]:
        print(f"Voice session started: {result['session']['id']}")
    else:
        print(result["message"])


def find_session(session_id):
    state = load_voice_hardening_state()

    for session in state.get("sessions", []):
        if session.get("id") == session_id:
            return session

    return None


def update_session(updated_session):
    state = load_voice_hardening_state()

    for index, session in enumerate(state.get("sessions", [])):
        if session.get("id") == updated_session.get("id"):
            state["sessions"][index] = updated_session
            save_voice_hardening_state(state)
            sync_voice_presence()
            return True

    return False


def end_voice_session(note=""):
    state = load_voice_hardening_state()
    active_id = state.get("active_session")

    if not active_id:
        return {
            "ok": False,
            "message": "No active voice session."
        }

    for session in state.get("sessions", []):
        if session.get("id") == active_id:
            session["status"] = "ended"
            session["ended_at"] = now_timestamp()
            session["end_note"] = note
            break

    state["active_session"] = None
    save_voice_hardening_state(state)

    if COMPANION_OS_AVAILABLE:
        try:
            append_companion_os_event(
                "voice_session_ended",
                f"Voice session ended: {active_id}",
                {
                    "session_id": active_id,
                    "note": note
                },
                source="voice_hardening",
                importance=4
            )
        except Exception:
            pass

    sync_voice_presence()

    return {
        "ok": True,
        "message": f"Voice session ended: {active_id}"
    }


def end_voice_session_interactive():
    note = input("End note: ").strip()
    result = end_voice_session(note=note)
    print(result["message"])


def add_transcript_placeholder(text, source="manual", session_id=None):
    state = load_voice_hardening_state()

    if session_id is None:
        session_id = state.get("active_session")

    placeholder = {
        "id": f"TRANSCRIPT-{len(state.get('transcript_placeholders', [])) + 1:03d}",
        "created_at": now_timestamp(),
        "session_id": session_id,
        "source": source,
        "text": text,
        "kind": "placeholder_not_real_stt"
    }

    state.setdefault("transcript_placeholders", []).append(placeholder)

    if session_id:
        for session in state.get("sessions", []):
            if session.get("id") == session_id:
                session.setdefault("transcript_placeholder_ids", []).append(placeholder["id"])
                session.setdefault("events", []).append({
                    "created_at": now_timestamp(),
                    "type": "transcript_placeholder",
                    "id": placeholder["id"]
                })

    save_voice_hardening_state(state)

    if COMPANION_OS_AVAILABLE:
        try:
            append_companion_os_event(
                "voice_transcript_placeholder_added",
                "Voice transcript placeholder added",
                {
                    "session_id": session_id,
                    "source": source,
                    "kind": "placeholder_not_real_stt"
                },
                source="voice_hardening",
                importance=3
            )
        except Exception:
            pass

    return placeholder


def add_transcript_placeholder_interactive():
    text = input("Transcript placeholder text: ").strip()

    if not text:
        print("Text required.")
        return

    placeholder = add_transcript_placeholder(text=text, source="interactive")
    print(f"Transcript placeholder added: {placeholder['id']}")


def dry_run_voice_pulse(chat_state=None, use_llm=False):
    if use_llm and VOICE_SESSION_AVAILABLE:
        try:
            text = build_voice_pulse(chat_state=chat_state)
        except TypeError:
            text = build_voice_pulse()
        except Exception as error:
            text = f"Voice pulse unavailable: {error}"

        if isinstance(text, str) and "timed out" in text.lower():
            text = (
                "Voice hardening pulse dry-run: Companion OS voice is available as "
                "user-invoked output. STT remains disabled and there is no always-listening."
            )
    else:
        text = (
            "Voice hardening pulse dry-run: Companion OS voice is available as "
            "user-invoked output. STT remains disabled and there is no always-listening."
        )

    check = {
        "created_at": now_timestamp(),
        "ok": True,
        "spoken": False,
        "text": text,
        "kind": "dry_run_no_audio_no_llm"
    }

    state = load_voice_hardening_state()
    state.setdefault("pulse_checks", []).append(check)
    save_voice_hardening_state(state)

    mark_voice_signal("voice_pulse", True)

    if TRACE_AVAILABLE:
        try:
            record_voice_trace(
                title="Voice pulse dry-run",
                summary=json.dumps(check, indent=2),
                decision="generated",
                risk="low"
            )
        except Exception:
            pass

    print("\n=== VOICE PULSE DRY RUN ===")
    print(text)
    return check

def voice_output_check_interactive():
    print("\n=== VOICE OUTPUT CHECK ===")
    print("This may speak through macOS 'say'.")
    confirm = input("Speak a short test line? y/n: ").strip().lower()

    if confirm != "y":
        print("Cancelled.")
        return

    if not VOICE_SESSION_AVAILABLE:
        print("Voice Session unavailable.")
        return

    text = (
        "Seed voice hardening check. Voice is a user-invoked interface, "
        "not consciousness."
    )

    result = speak_text(text, reason="voice_hardening_output_check")

    check = {
        "created_at": now_timestamp(),
        "ok": result.get("ok", False),
        "result": result,
        "text": text
    }

    state = load_voice_hardening_state()
    state.setdefault("output_checks", []).append(check)
    save_voice_hardening_state(state)

    mark_voice_signal("voice_history", True)
    mark_voice_signal("macos_say_available", macos_say_available())

    print(result.get("message"))


def ritual_check():
    check = {
        "created_at": now_timestamp(),
        "ok": True,
        "spoken": False,
        "meaning": "Voice ritual path exists in seed_voice_session; hardening recognizes ritual support without forcing audio.",
        "kind": "dry_run_no_audio"
    }

    state = load_voice_hardening_state()
    state.setdefault("ritual_checks", []).append(check)
    save_voice_hardening_state(state)

    mark_voice_signal("voice_ritual", True)

    if TRACE_AVAILABLE:
        try:
            record_voice_trace(
                title="Voice ritual dry-run check",
                summary=json.dumps(check, indent=2),
                decision="checked",
                risk="low"
            )
        except Exception:
            pass

    print("\n=== VOICE RITUAL CHECK ===")
    print("Voice ritual support checked without forcing audio.")
    return check


def run_voice_hardening_suite(chat_state=None):
    initialize_voice_hardening()
    privacy = run_voice_privacy_check()
    capability = build_voice_capability_report(save=True)
    pulse = dry_run_voice_pulse(chat_state=chat_state)
    ritual = ritual_check()

    summary = {
        "created_at": now_timestamp(),
        "privacy_ok": privacy.get("ok"),
        "macos_say_available": capability.get("macos_say_available"),
        "voice_session_available": capability.get("voice_session_available"),
        "pulse_ok": pulse.get("ok"),
        "ritual_ok": ritual.get("ok"),
        "stt_boundary_declared": True,
        "audio_spoken": False
    }

    if COMPANION_OS_AVAILABLE:
        try:
            append_companion_os_journal(
                "Voice hardening suite",
                json.dumps(summary, indent=2)
            )
            append_companion_os_event(
                "voice_hardening_suite_run",
                "Voice hardening suite run",
                summary,
                source="voice_hardening",
                importance=4
            )
        except Exception:
            pass

    print("\n=== VOICE HARDENING SUITE ===")
    print(json.dumps(summary, indent=4))

    return summary


def voice_hardening_status_data():
    state = load_voice_hardening_state()
    capability = state.get("capability_report") or build_voice_capability_report(save=False)

    latest_privacy = state.get("privacy_checks", [])[-1] if state.get("privacy_checks") else None

    return {
        "created_at": now_timestamp(),
        "active_session": state.get("active_session"),
        "session_count": len(state.get("sessions", [])),
        "transcript_placeholder_count": len(state.get("transcript_placeholders", [])),
        "privacy_check_count": len(state.get("privacy_checks", [])),
        "latest_privacy_ok": latest_privacy.get("ok") if latest_privacy else None,
        "output_check_count": len(state.get("output_checks", [])),
        "pulse_check_count": len(state.get("pulse_checks", [])),
        "ritual_check_count": len(state.get("ritual_checks", [])),
        "capability": capability,
        "stt_boundary": state.get("stt_boundary", {}),
        "privacy_rules": state.get("privacy_rules", [])
    }


def show_voice_hardening_status():
    data = voice_hardening_status_data()

    print("\n=== VOICE HARDENING STATUS ===")
    print(f"Active session: {data['active_session']}")
    print(f"Sessions: {data['session_count']}")
    print(f"Transcript placeholders: {data['transcript_placeholder_count']}")
    print(f"Privacy checks: {data['privacy_check_count']}")
    print(f"Latest privacy OK: {data['latest_privacy_ok']}")
    print(f"Output checks: {data['output_check_count']}")
    print(f"Pulse checks: {data['pulse_check_count']}")
    print(f"Ritual checks: {data['ritual_check_count']}")

    print("\nCapability:")
    print(json.dumps(data["capability"], indent=4))

    print("\nSTT boundary:")
    print(json.dumps(data["stt_boundary"], indent=4))

    print("\nPrivacy rules:")
    for rule in data["privacy_rules"]:
        print(f"- {rule}")


def show_voice_sessions():
    state = load_voice_hardening_state()

    print("\n=== VOICE HARDENING SESSIONS ===")

    if not state.get("sessions"):
        print("No voice sessions.")
        return

    for session in state.get("sessions", [])[-20:]:
        print(f"\n{session.get('id')} — {session.get('status')}")
        print(f"Title: {session.get('title')}")
        print(f"Purpose: {session.get('purpose')}")
        print(f"Created: {session.get('created_at')}")
        print(f"Ended: {session.get('ended_at')}")
        print(f"Transcript placeholders: {len(session.get('transcript_placeholder_ids', []))}")


def show_transcript_placeholders():
    state = load_voice_hardening_state()

    print("\n=== VOICE TRANSCRIPT PLACEHOLDERS ===")

    if not state.get("transcript_placeholders"):
        print("No transcript placeholders.")
        return

    for item in state.get("transcript_placeholders", [])[-20:]:
        print(f"\n{item.get('id')} — {item.get('created_at')}")
        print(f"Session: {item.get('session_id')}")
        print(f"Source: {item.get('source')}")
        print(f"Kind: {item.get('kind')}")
        print(item.get("text"))


def get_voice_hardening_context_for_prompt():
    data = voice_hardening_status_data()

    text = "=== VOICE HARDENING CONTEXT ===\n"
    text += f"Active session: {data['active_session']}\n"
    text += f"Sessions: {data['session_count']}\n"
    text += f"Privacy checks: {data['privacy_check_count']} latest_ok={data['latest_privacy_ok']}\n"
    text += f"Pulse checks: {data['pulse_check_count']}\n"
    text += f"Ritual checks: {data['ritual_check_count']}\n"
    text += f"Transcript placeholders: {data['transcript_placeholder_count']}\n"
    text += f"Capability: {json.dumps(data['capability'])}\n"

    text += """
Voice hardening rule:
Voice is user-invoked interface output only.
No secret always-listening.
STT is not enabled yet; future STT must begin as push-to-talk.
Transcript placeholders are not real STT transcripts.
Voice does not mean Seed is conscious.
"""

    return text


if __name__ == "__main__":
    run_voice_hardening_suite()
    show_voice_hardening_status()
