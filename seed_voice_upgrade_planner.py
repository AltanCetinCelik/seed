import json
from datetime import datetime
from pathlib import Path


try:
    from seed_config import SEED_VOICE_UPGRADE_PLAN_FILE
except Exception:
    SEED_VOICE_UPGRADE_PLAN_FILE = "seed_voice_upgrade_plan.json"


VOICE_FILES = [
    "seed_active_voice_daemon.py",
    "seed_voice_command_bridge.py",
    "seed_fast_voice_context.py",
    "seed_voice_quality_router.py",
    "seed_voice_session.py",
    "seed_voice_hardening.py"
]


def now_timestamp():
    return datetime.now().isoformat(timespec="seconds")


def inspect_voice_files():
    files = []

    for file_name in VOICE_FILES:
        path = Path(file_name)
        if not path.exists():
            files.append({
                "file": file_name,
                "exists": False
            })
            continue

        text = path.read_text(errors="ignore")
        files.append({
            "file": file_name,
            "exists": True,
            "chars": len(text),
            "has_whisper": "whisper" in text.lower(),
            "has_tts": "tts" in text.lower() or "speak" in text.lower(),
            "has_ffmpeg": "ffmpeg" in text.lower(),
            "has_action_kernel": "action_kernel" in text.lower(),
            "has_skill_kernel": "skill_kernel" in text.lower(),
            "has_agent_context": "agent" in text.lower(),
            "has_clarification": "clarify" in text.lower() or "repeat" in text.lower()
        })

    return files


def build_voice_upgrade_plan():
    files = inspect_voice_files()

    plan = {
        "created_at": now_timestamp(),
        "version": "v2.7.0",
        "ok": True,
        "read_only": True,
        "voice_files": files,
        "current_strengths": [
            "Explicit active voice launcher exists.",
            "Whisper/faster-whisper style transcription is already integrated.",
            "TTS/spoken response path exists.",
            "Action Kernel and Skill Kernel context now exist.",
            "No secret always-listening policy is preserved."
        ],
        "next_upgrades": [
            {
                "id": "voice-001",
                "name": "One-shot voice command mode",
                "why": "For reliability, add a fast record-once-answer-once command beside continuous active voice.",
                "risk": "low"
            },
            {
                "id": "voice-002",
                "name": "Transcript confidence journal",
                "why": "Track bad transcripts and repeated misunderstandings so fixes are data-driven.",
                "risk": "low"
            },
            {
                "id": "voice-003",
                "name": "Voice intent router",
                "why": "Route voice to home/mode/action/skill/agent before LLM response.",
                "risk": "medium"
            },
            {
                "id": "voice-004",
                "name": "Barge-in later",
                "why": "Make Seed interruptible, more Jarvis-like. Requires careful audio loop changes.",
                "risk": "high"
            },
            {
                "id": "voice-005",
                "name": "Pipecat/LiveKit research branch",
                "why": "Future real-time voice pipeline. Do not merge until isolated prototype works.",
                "risk": "high"
            }
        ],
        "recommended_next_patch": "Seed v2.7.1 Voice UX Pack: one-shot launcher, transcript journal, voice intent router."
    }

    with open(SEED_VOICE_UPGRADE_PLAN_FILE, "w") as file:
        json.dump(plan, file, indent=4)

    return plan


def voice_upgrade_context(user_prompt=""):
    plan = build_voice_upgrade_plan()

    lines = ["=== SEED VOICE UPGRADE PLAN CONTEXT ==="]
    lines.append(f"Recommended next patch: {plan.get('recommended_next_patch')}")
    for item in plan.get("next_upgrades", [])[:5]:
        lines.append(f"- {item['id']} {item['name']} risk={item['risk']}: {item['why']}")
    return "\n".join(lines)


def show_voice_upgrade_plan():
    plan = build_voice_upgrade_plan()

    print("\n=== SEED VOICE UPGRADE PLAN ===")
    print(f"Recommended next patch: {plan.get('recommended_next_patch')}")
    print("\nVoice files:")
    for item in plan["voice_files"]:
        print(f"- {item['file']}: exists={item.get('exists')} chars={item.get('chars')}")
    print("\nNext upgrades:")
    for item in plan["next_upgrades"]:
        print(f"- {item['id']} — {item['name']} risk={item['risk']}")
        print(f"  {item['why']}")


if __name__ == "__main__":
    show_voice_upgrade_plan()
