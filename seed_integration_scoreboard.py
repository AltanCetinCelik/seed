import json
from datetime import datetime


try:
    from seed_config import SEED_REPO_SCOREBOARD_FILE
except Exception:
    SEED_REPO_SCOREBOARD_FILE = "seed_integration_scoreboard.json"


PATTERN_POINTS = {
    "agent orchestration": 20,
    "memory / RAG": 18,
    "voice / realtime": 18,
    "browser automation": 16,
    "coding executor": 22,
    "MCP/tool protocol": 20,
    "dashboard/workspace UI": 12
}

ADAPTER_POINTS = {
    "aider": 30,
    "langgraph": 28,
    "mcp": 25,
    "mem0": 24,
    "qdrant": 20,
    "browser-use": 22,
    "openhands": 22,
    "swe-agent": 20,
    "cline": 16,
    "open-interpreter": 14,
    "letta": 18,
    "livekit": 18,
    "pipecat": 18,
    "open-webui": 12,
    "anythingllm": 12,
    "khoj": 12
}

RISK_PENALTY = {
    "low": 0,
    "medium": 8,
    "high": 18
}


def now_timestamp():
    return datetime.now().isoformat(timespec="seconds")


def score_item(item):
    patterns = item.get("patterns", {}).get("patterns", [])
    adapters = item.get("known_adapter_matches", [])
    risk = item.get("risks", {}).get("risk_level", "low")

    score = 0
    reasons = []

    for pattern in patterns:
        score += PATTERN_POINTS.get(pattern, 0)
        reasons.append(f"pattern:{pattern}")

    for adapter in adapters:
        score += ADAPTER_POINTS.get(adapter, 0)
        reasons.append(f"adapter:{adapter}")

    score -= RISK_PENALTY.get(risk, 0)

    if adapters:
        integration_mode = "known_adapter"
    elif risk == "high":
        integration_mode = "sandbox_only"
    else:
        integration_mode = "pattern_reference"

    return {
        "name": item.get("name"),
        "repo": item.get("repo"),
        "score": max(score, 0),
        "risk": risk,
        "integration_mode": integration_mode,
        "adapters": adapters,
        "patterns": patterns,
        "reasons": reasons
    }


def build_integration_scoreboard():
    from seed_repo_assimilation_engine import build_repo_assimilation_report

    report = build_repo_assimilation_report()
    scored = [score_item(item) for item in report.get("items", [])]
    scored = sorted(scored, key=lambda x: x["score"], reverse=True)

    scoreboard = {
        "created_at": now_timestamp(),
        "version": "v30.0.0",
        "ok": True,
        "repo_count": len(scored),
        "top_20": scored[:20],
        "all": scored
    }

    with open(SEED_REPO_SCOREBOARD_FILE, "w") as file:
        json.dump(scoreboard, file, indent=4)

    return scoreboard


def show_scoreboard():
    data = build_integration_scoreboard()
    print("\n=== SEED INTEGRATION SCOREBOARD v30 ===")
    for item in data["top_20"]:
        print(f"- {item['name']}: score={item['score']} risk={item['risk']} mode={item['integration_mode']} adapters={item['adapters']}")


if __name__ == "__main__":
    show_scoreboard()
