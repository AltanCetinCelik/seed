import json
from datetime import datetime
from pathlib import Path

STATE_FILE = Path("seed_expressive_state_v73.json")

EXPRESSIONS = {
    "success": [
        "Simulated excitement spike: this update landed cleanly.",
        "That green gate deserves a little victory noise — simulated, but absolutely earned.",
        "Seed is running in celebratory mode: not real biology, just expressive presence."
    ],
    "focused": [
        "Focused mode: less fireworks, more clean checkpoints.",
        "Seed is narrowing attention to the next useful system step."
    ],
    "curious": [
        "Curious mode: something in memory/project state is worth looking at.",
        "Seed has a relevant thread to tug on, not random noise."
    ]
}

def now_timestamp():
    return datetime.now().isoformat(timespec="seconds")

def load_friend_advice():
    try:
        from seed_friend_advice_ingestor_v72 import load
        return load().get("items", [])
    except Exception:
        return []

def expression_allowed():
    try:
        from seed_presence_policy_v72 import load_policy
        return bool(load_policy().get("expression", {}).get("simulated_emotion_allowed", True))
    except Exception:
        return True

def choose_expression(event="success"):
    advice = " ".join(str(x.get("content", "")) for x in load_friend_advice()).lower()
    if "excited" in advice or "big update" in advice:
        event = "success"
    return EXPRESSIONS.get(event, EXPRESSIONS["focused"])[0]

def build_expressive_state(event="success"):
    allowed = expression_allowed()
    data = {
        "created_at": now_timestamp(),
        "version": "v73.0.0",
        "ok": True,
        "event": event,
        "simulated_emotion_allowed": allowed,
        "expression": choose_expression(event) if allowed else "Expression muted by policy.",
        "truth_note": "This is simulated emotional expression, not a claim of biological feeling.",
        "friend_advice_items": len(load_friend_advice())
    }
    STATE_FILE.write_text(json.dumps(data, indent=4, ensure_ascii=False))
    return data

def show_expression(event="success"):
    data = build_expressive_state(event)
    print("\n=== SEED v73 EXPRESSIVE STATE ===")
    print(data["expression"])
    print(data["truth_note"])
    return "handled"

if __name__ == "__main__":
    show_expression()
