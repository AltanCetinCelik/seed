import json
from datetime import datetime


try:
    from seed_config import SEED_MEMORY_DISTILL_FILE
except Exception:
    SEED_MEMORY_DISTILL_FILE = "seed_memory_distill.json"


def now_timestamp():
    return datetime.now().isoformat(timespec="seconds")


def safe_call(fn):
    try:
        return {"ok": True, "data": fn()}
    except Exception as error:
        return {"ok": False, "error": str(error)}


def build_memory_distill():
    repo_dna = safe_call(lambda: __import__("seed_repo_dna_engine", fromlist=["build_repo_dna"]).build_repo_dna())
    fusion = safe_call(lambda: __import__("seed_integration_fusion_engine", fromlist=["build_integration_fusion"]).build_integration_fusion())
    omega = safe_call(lambda: __import__("seed_omega_planner", fromlist=["build_omega_plan"]).build_omega_plan())
    events = safe_call(lambda: __import__("seed_event_bus", fromlist=["read_events"]).read_events(limit=25))
    services = safe_call(lambda: __import__("seed_service_manager", fromlist=["service_status"]).service_status())

    summary = {
        "created_at": now_timestamp(),
        "version": "v4.0.0",
        "ok": True,
        "memory_type": "runtime_distill",
        "summary": {
            "seed_now": "Seed has Control Plane, Omega integration planning, MCP skill server, Aider unlock path, event bus, workflows, service manager, rollback checkpoints.",
            "current_major_capabilities": [
                "local control plane",
                "gate matrix",
                "MCP skill server/client",
                "Aider supervised dry-run/real-run path",
                "integration backlog",
                "workflow automation",
                "rollback checkpoints",
                "event bus"
            ],
            "next_best_upgrade": "v4.1 — real Aider patch review UI + promote sandbox workflow + live Control Plane actions"
        },
        "repo": repo_dna,
        "fusion": fusion,
        "omega": omega,
        "events": events,
        "services": services
    }

    with open(SEED_MEMORY_DISTILL_FILE, "w") as file:
        json.dump(summary, file, indent=4)

    return summary


def show_memory_distill():
    print("\n=== SEED MEMORY DISTILL ===")
    data = build_memory_distill()
    print(json.dumps(data["summary"], indent=4))


if __name__ == "__main__":
    show_memory_distill()
