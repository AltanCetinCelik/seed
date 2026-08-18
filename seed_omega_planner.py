import json
from datetime import datetime


try:
    from seed_config import SEED_OMEGA_PLAN_FILE
except Exception:
    SEED_OMEGA_PLAN_FILE = "seed_omega_plan.json"


def now_timestamp():
    return datetime.now().isoformat(timespec="seconds")


def build_omega_plan():
    from seed_repo_dna_engine import build_repo_dna
    from seed_integration_fusion_engine import build_integration_fusion

    dna = build_repo_dna()
    fusion = build_integration_fusion()

    top = fusion["top_10"]

    waves = {
        "wave_1_now": [
            {
                "id": "checkpoint-discipline",
                "name": "Checkpoint discipline",
                "why": "Dirty tree blocks safe executor work.",
                "commands": [
                    "git status",
                    "git add .",
                    "git commit -m 'Checkpoint Seed clean baseline'",
                    "git push"
                ],
                "risk": "low"
            },
            {
                "id": "mcp-seed-skill-server",
                "name": "Seed MCP Skill Server",
                "why": "Expose Seed skills as formal tool protocol without giving arbitrary shell.",
                "source": "MCP",
                "risk": "medium"
            },
            {
                "id": "aider-install-detect",
                "name": "Aider install + real unlock prep",
                "why": "Aider is the first useful external coding executor.",
                "source": "Aider",
                "risk": "medium-high"
            },
            {
                "id": "memory-extraction-upgrade",
                "name": "Memory extraction upgrade",
                "why": "Use Mem0-style idea extraction in Seed-native memory.",
                "source": "Mem0",
                "risk": "medium"
            }
        ],
        "wave_2_next": [
            {
                "id": "voice-realtime-sandbox",
                "name": "Real-time voice sandbox",
                "why": "Prototype Pipecat/LiveKit-style flow outside core first.",
                "risk": "high"
            },
            {
                "id": "browser-agent-sandbox",
                "name": "Browser-use sandbox",
                "why": "Browser actions require account/form safety rules.",
                "risk": "high"
            },
            {
                "id": "guardrail-policy-engine",
                "name": "Guardrail policy engine",
                "why": "Convert current rules into explicit policy checks.",
                "risk": "medium"
            }
        ],
        "wave_3_later": [
            {
                "id": "openhands-sandbox",
                "name": "OpenHands sandbox",
                "why": "Broad coding agent only after Aider path is stable.",
                "risk": "very-high"
            },
            {
                "id": "vector-db-backend",
                "name": "Qdrant/pgvector backend",
                "why": "Upgrade memory retrieval after local index proves stable.",
                "risk": "high"
            }
        ]
    }

    plan = {
        "created_at": now_timestamp(),
        "version": "v3.5.0",
        "ok": True,
        "repo_dna_summary": dna.get("dna_summary"),
        "repo_stats": {
            "python_files": dna.get("python_file_count"),
            "commands": dna.get("command_count")
        },
        "top_integrations": top,
        "waves": waves,
        "rules": [
            "Do not directly paste repo code into Seed core.",
            "Create adapters.",
            "Sandbox high-risk systems.",
            "Approval required for external execution.",
            "Commit before executor work.",
            "Release orchestrator before commit.",
            "User remains in control."
        ],
        "next_big_build": "Seed v3.6.0 — MCP Skill Server + Aider Install/Unlock Prep"
    }

    with open(SEED_OMEGA_PLAN_FILE, "w") as file:
        json.dump(plan, file, indent=4)

    return plan


def omega_plan_context(user_prompt=""):
    plan = build_omega_plan()
    return (
        "=== SEED OMEGA PLAN ===\n"
        f"Next big build: {plan['next_big_build']}\n"
        f"Repo Python files: {plan['repo_stats']['python_files']}\n"
        f"Commands: {plan['repo_stats']['commands']}\n"
    )


def show_omega_plan():
    plan = build_omega_plan()

    print("\n=== SEED OMEGA PLAN ===")
    print(f"Next big build: {plan['next_big_build']}")

    for wave, items in plan["waves"].items():
        print(f"\n[{wave}]")
        for item in items:
            print(f"- {item['name']} risk={item['risk']}")
            print(f"  {item['why']}")


if __name__ == "__main__":
    show_omega_plan()
