import json
from datetime import datetime
from pathlib import Path


UI_MODEL_FILE = Path("seed_agent_hq_ui_model_v38.json")


def now_timestamp():
    return datetime.now().isoformat(timespec="seconds")


def build_ui_model():
    model = {
        "created_at": now_timestamp(),
        "version": "v45.0.0",
        "ok": True,
        "layout": {
            "top_bar": ["Seed version", "latency", "gate status", "service status"],
            "left_nav": ["Agent HQ", "Tasks", "Memory", "Workflows", "Aider", "Browser", "Voice", "Repos", "World"],
            "main_cards": [
                "Agent status cards",
                "Workflow graph",
                "Patch review panel",
                "Memory review inbox",
                "Browser session summary",
                "Voice transcript timeline",
                "Repo integration roadmap",
                "Presence queue"
            ],
            "right_panel": ["Pending approvals", "warnings", "next suggested action"]
        },
        "professional_rules": [
            "show less raw JSON",
            "show clear next actions",
            "separate heavy rebuild from fast status",
            "make every risky action visible",
            "always show last gate result"
        ]
    }
    UI_MODEL_FILE.write_text(json.dumps(model, indent=4))
    return model


def show_ui_model():
    print("\n=== SEED AGENT HQ UI MODEL v38 ===")
    print(json.dumps(build_ui_model(), indent=4))


if __name__ == "__main__":
    show_ui_model()
