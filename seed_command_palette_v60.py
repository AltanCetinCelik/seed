import json
from datetime import datetime
from pathlib import Path


PALETTE_FILE = Path("seed_command_palette_v60.json")


ACTIONS = [
    {
        "natural": ["check yourself", "are you healthy", "run health check", "is everything working"],
        "internal": "health_check",
        "description": "Runs v60/v50/v45 gates and latency probe.",
    },
    {
        "natural": ["open dashboard", "open control plane", "show dashboard"],
        "internal": "open_control_plane",
        "description": "Opens local Control Plane.",
    },
    {
        "natural": ["what changed", "show full update", "what did we build"],
        "internal": "full_update",
        "description": "Shows full update ledger.",
    },
    {
        "natural": ["show models", "model manager", "what models do we have"],
        "internal": "model_manager",
        "description": "Shows model manager and pull plan.",
    },
    {
        "natural": ["benchmark models", "test models", "model arena"],
        "internal": "model_benchmark",
        "description": "Benchmarks local Ollama models.",
    },
    {
        "natural": ["compare hermes moltbot openclaw", "fusion lab", "use hermes and moltbot"],
        "internal": "fusion_lab",
        "description": "Runs Hermes/Moltbot/OpenClaw fusion analysis.",
    },
    {
        "natural": ["extract memories", "learn from logs", "update your memory"],
        "internal": "memory_auto_extract",
        "description": "Extracts memory candidates from logs/docs.",
    },
    {
        "natural": ["promote memories", "save important memories"],
        "internal": "memory_auto_promote",
        "description": "Promotes top memory candidates.",
    },
    {
        "natural": ["daily brief", "what should we do today", "what now"],
        "internal": "daily_brief",
        "description": "Shows presence daily brief.",
    },
    {
        "natural": ["make a patch plan", "create aider plan", "improve yourself"],
        "internal": "aider_self_improve",
        "description": "Starts real self-improvement loop planning.",
    },
    {
        "natural": ["show command palette", "what can i say", "help me talk to seed"],
        "internal": "command_palette",
        "description": "Shows natural language action palette.",
    },
]


def now_timestamp():
    return datetime.now().isoformat(timespec="seconds")


def build_palette():
    data = {
        "created_at": now_timestamp(),
        "version": "v60.0.0",
        "ok": True,
        "actions": ACTIONS,
        "principle": "The user talks naturally. Seed routes internally.",
    }
    PALETTE_FILE.write_text(json.dumps(data, indent=4))
    return data


def show_palette():
    data = build_palette()
    print("\n=== SEED NATURAL COMMAND PALETTE v60 ===")
    print("You can talk normally. Examples:\n")
    for action in data["actions"]:
        print(f"- {action['natural'][0]}  →  {action['description']}")


if __name__ == "__main__":
    show_palette()
