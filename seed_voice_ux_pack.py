import json
from datetime import datetime


try:
    from seed_config import SEED_VOICE_UX_STATE_FILE, SEED_TRANSCRIPT_JOURNAL_FILE
except Exception:
    SEED_VOICE_UX_STATE_FILE = "seed_voice_ux_state.json"
    SEED_TRANSCRIPT_JOURNAL_FILE = "seed_transcript_journal.jsonl"


def now_timestamp():
    return datetime.now().isoformat(timespec="seconds")


def classify_voice_intent(text):
    lowered = (text or "").lower()

    if any(x in lowered for x in ["open cockpit", "dashboard", "browser"]):
        return "cockpit"
    if any(x in lowered for x in ["git status", "repo status"]):
        return "git_status"
    if any(x in lowered for x in ["repo doctor", "diagnose repo"]):
        return "repo_doctor"
    if any(x in lowered for x in ["agent run", "create agent"]):
        return "agent_run"
    if any(x in lowered for x in ["aider", "executor"]):
        return "executor"
    if any(x in lowered for x in ["voice", "transcript", "heard me"]):
        return "voice_debug"
    if any(x in lowered for x in ["mode", "focus", "coding mode"]):
        return "mode"
    return "chat"


def add_transcript_journal(transcript, interpreted_as=None, note=None):
    item = {
        "created_at": now_timestamp(),
        "transcript": transcript,
        "intent": classify_voice_intent(transcript),
        "interpreted_as": interpreted_as,
        "note": note
    }

    with open(SEED_TRANSCRIPT_JOURNAL_FILE, "a") as file:
        file.write(json.dumps(item) + "\n")

    return item


def read_transcript_journal(limit=20):
    items = []
    try:
        with open(SEED_TRANSCRIPT_JOURNAL_FILE, "r") as file:
            for line in file:
                line = line.strip()
                if not line:
                    continue
                try:
                    items.append(json.loads(line))
                except Exception:
                    pass
    except FileNotFoundError:
        pass

    return {
        "ok": True,
        "count": len(items),
        "items": items[-limit:]
    }


def voice_ux_snapshot():
    data = {
        "created_at": now_timestamp(),
        "version": "v2.9.0",
        "ok": True,
        "no_secret_always_listening": True,
        "recommended_voice_modes": [
            "Push-to-talk command",
            "One-shot listen/respond",
            "Active visible listener",
            "Debug transcript review"
        ],
        "routing": {
            "cockpit": "open dashboard/cockpit actions",
            "git_status": "Skill Kernel git.status",
            "repo_doctor": "Repo Doctor",
            "agent_run": "Supervised Agent Lifecycle",
            "executor": "Executor/Aider bridge",
            "voice_debug": "Transcript Journal and Voice UX",
            "mode": "Experience Modes",
            "chat": "Normal Seed response"
        },
        "recent_transcripts": read_transcript_journal(limit=8)["items"],
        "next_voice_patch": [
            "Add direct /voice-one-shot launcher",
            "Show last transcript confidence/debug",
            "Add voice command correction flow",
            "Create voice regression phrases"
        ]
    }

    with open(SEED_VOICE_UX_STATE_FILE, "w") as file:
        json.dump(data, file, indent=4)

    return data


def voice_ux_context(user_prompt=""):
    data = voice_ux_snapshot()
    return (
        "=== SEED v2.9 VOICE UX PACK ===\n"
        "Voice is explicit only; no secret always-listening.\n"
        f"Current inferred voice intent: {classify_voice_intent(user_prompt)}\n"
        "Voice routes: cockpit, git_status, repo_doctor, agent_run, executor, voice_debug, mode, chat.\n"
    )


def show_voice_ux():
    data = voice_ux_snapshot()

    print("\n=== SEED VOICE UX PACK ===")
    print("No secret always-listening: True")
    print("\nRecommended voice modes:")
    for item in data["recommended_voice_modes"]:
        print(f"- {item}")

    print("\nNext voice patch:")
    for item in data["next_voice_patch"]:
        print(f"- {item}")


def show_transcript_add():
    transcript = input("Transcript: ").strip()
    interpreted_as = input("Interpreted as or blank: ").strip() or None
    note = input("Note or blank: ").strip() or None
    print(json.dumps(add_transcript_journal(transcript, interpreted_as, note), indent=4))


def show_transcripts():
    print(json.dumps(read_transcript_journal(), indent=4))


if __name__ == "__main__":
    show_voice_ux()
