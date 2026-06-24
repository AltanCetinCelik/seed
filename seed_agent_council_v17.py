import json
from datetime import datetime


try:
    from seed_config import SEED_AGENT_COUNCIL_V17_FILE
except Exception:
    SEED_AGENT_COUNCIL_V17_FILE = "seed_agent_council_v17.json"


COUNCIL = [
    {"id": "engineer", "name": "Engineer", "focus": "code quality, tests, architecture"},
    {"id": "safety", "name": "Safety Officer", "focus": "policy, approvals, rollback"},
    {"id": "memory", "name": "Memory Curator", "focus": "durable useful memory only"},
    {"id": "voice", "name": "Voice Operator", "focus": "fast voice UX, transcript quality"},
    {"id": "product", "name": "Product Designer", "focus": "dashboard, flow, operator usability"},
    {"id": "researcher", "name": "Researcher", "focus": "repo integration, references"},
]


def now_timestamp():
    return datetime.now().isoformat(timespec="seconds")


def council_review(goal):
    recommendations = []
    lowered = goal.lower()

    for agent in COUNCIL:
        rec = {
            "agent": agent["id"],
            "focus": agent["focus"],
            "risk": "low",
            "recommendation": "Proceed with manual-tick planning."
        }

        if agent["id"] == "safety":
            rec["recommendation"] = "Create checkpoint and require approval before Aider/browser/OpenHands real actions."
        elif agent["id"] == "engineer":
            rec["recommendation"] = "Use gates and small target-file changes."
        elif agent["id"] == "voice" and "voice" in lowered:
            rec["recommendation"] = "Use push-to-talk and transcript journal; no secret listening."
        elif agent["id"] == "researcher":
            rec["recommendation"] = "Adapter-first. Do not dump external repo code into Seed."

        recommendations.append(rec)

    report = {
        "created_at": now_timestamp(),
        "version": "v20.0.0",
        "ok": True,
        "engine": "Seed Multi-Agent Council v17",
        "goal": goal,
        "council": COUNCIL,
        "recommendations": recommendations,
        "decision": "proceed_with_manual_tick_and_policy"
    }

    with open(SEED_AGENT_COUNCIL_V17_FILE, "w") as file:
        json.dump(report, file, indent=4)

    return report


def show_agent_council():
    goal = input("Goal for council review: ").strip() or "Improve Seed safely"
    print(json.dumps(council_review(goal), indent=4))


if __name__ == "__main__":
    show_agent_council()
