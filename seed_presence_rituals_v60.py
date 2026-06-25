import json
from datetime import datetime
from pathlib import Path


RITUAL_FILE = Path("seed_presence_rituals_v60.json")


def now_timestamp():
    return datetime.now().isoformat(timespec="seconds")


def build_rituals():
    rituals = {
        "morning": {
            "purpose": "Choose today's most useful Seed move.",
            "message_style": "one clear recommendation, no spam",
            "questions": [
                "What do you want Seed to improve today?",
                "Should we polish UX or deepen intelligence today?",
                "Do you want me to run health checks first?"
            ],
        },
        "night_review": {
            "purpose": "Capture what changed and what Seed should remember.",
            "message_style": "short reflection",
            "questions": [
                "What did we finish today?",
                "What should I remember from this session?",
                "What is tomorrow's first move?"
            ],
        },
        "after_failure": {
            "purpose": "Recover from errors without panic.",
            "message_style": "diagnose, patch, retest",
            "questions": [
                "Do you want me to isolate the failing module?",
                "Should I create a rollback checkpoint first?"
            ],
        },
        "after_success": {
            "purpose": "Lock in working state.",
            "message_style": "confirm, commit, backup",
            "questions": [
                "Should we commit this stable version?",
                "Should I write a memory about what worked?"
            ],
        },
        "curiosity": {
            "purpose": "Ask useful questions only when grounded in context.",
            "message_style": "reason-first",
            "rule": "Seed must say why it is asking.",
        },
    }

    data = {
        "created_at": now_timestamp(),
        "version": "v60.0.0",
        "ok": True,
        "rituals": rituals,
        "presence_principle": "Seed feels present through continuity, memory, initiative, and reasoned nudges — not by claiming consciousness.",
    }

    RITUAL_FILE.write_text(json.dumps(data, indent=4))
    return data


def daily_brief():
    try:
        from seed_nothing_left_behind_v50 import dust_check
        dust = dust_check()
    except Exception:
        dust = {"ok": None}

    try:
        from seed_task_hygiene_v302 import task_stats
        tasks = task_stats()
    except Exception:
        tasks = {}

    try:
        from seed_agent_hq_v30 import build_agent_hq_fast
        hq = build_agent_hq_fast()
    except Exception:
        hq = {}

    return {
        "created_at": now_timestamp(),
        "version": "v60.0.0",
        "ok": True,
        "brief": "Seed is ready. Best next move: improve natural UX and deepen repo fusion.",
        "why": "The architecture exists; the experience needs to feel conversational and professional.",
        "dust_ok": dust.get("ok"),
        "ready_real_tasks": tasks.get("ready_real"),
        "agents": hq.get("agent_count"),
    }


def show_rituals():
    print("\n=== SEED PRESENCE 2.0 RITUALS v60 ===")
    print(json.dumps(build_rituals(), indent=4))


def show_daily_brief():
    print("\n=== SEED DAILY BRIEF v60 ===")
    print(json.dumps(daily_brief(), indent=4))


if __name__ == "__main__":
    show_rituals()
