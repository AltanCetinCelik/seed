import json
from datetime import datetime
from pathlib import Path


try:
    from seed_config import SEED_MEMORY_V2_FILE
except Exception:
    SEED_MEMORY_V2_FILE = "seed_memory_v2.json"


LAYERS = {
    "identity": "Stable facts about User and Seed boundaries.",
    "projects": "Project history, code decisions, milestones.",
    "preferences": "User's style, UX, language, response preferences.",
    "people": "People/context only when useful and appropriate.",
    "skills": "Coding, engineering, hardware, research capabilities.",
    "events": "Recent Seed runtime events and checkpoints.",
    "do_not_claim": "Boundary: Seed is not alive/sentient/conscious/human."
}


def now_timestamp():
    return datetime.now().isoformat(timespec="seconds")


def safe_call(fn, default):
    try:
        return fn()
    except Exception:
        return default


def build_memory_v2():
    events = safe_call(
        lambda: __import__("seed_event_bus", fromlist=["read_events"]).read_events(limit=25),
        []
    )

    tasks = safe_call(
        lambda: __import__("seed_task_os", fromlist=["list_tasks"]).list_tasks(limit=80),
        {"tasks": []}
    )

    distill = safe_call(
        lambda: __import__("seed_memory_distiller", fromlist=["build_memory_distill"]).build_memory_distill(),
        {}
    )

    memory = {
        "created_at": now_timestamp(),
        "version": "v20.0.0",
        "ok": True,
        "engine": "Seed Memory Engine 2.0",
        "layers": LAYERS,
        "policy": {
            "local_first": True,
            "no_sensitive_guessing": True,
            "do_not_store_random_private_facts": True,
            "user_controls_memory": True,
            "seed_boundary": "Seed must not claim life/consciousness/sentience/human experience."
        },
        "memory_sources": {
            "event_bus_sample": events,
            "task_os_sample": tasks.get("tasks", [])[:20],
            "runtime_distill_summary": distill.get("summary", {}) if isinstance(distill, dict) else {}
        },
        "external_repo_adapters": {
            "mem0": {
                "status": "adapter_pattern",
                "purpose": "Extract durable user/project memories from chat and events."
            },
            "qdrant": {
                "status": "optional_backend",
                "purpose": "Local vector retrieval backend later; not required for v20."
            },
            "llamaindex": {
                "status": "document_rag_reference",
                "purpose": "Document registry and retrieval patterns."
            }
        }
    }

    with open(SEED_MEMORY_V2_FILE, "w") as file:
        json.dump(memory, file, indent=4)

    return memory


def show_memory_v2():
    data = build_memory_v2()
    print("\n=== SEED MEMORY ENGINE 2.0 ===")
    print(f"OK: {data['ok']}")
    print("Layers:")
    for key, value in data["layers"].items():
        print(f"- {key}: {value}")


if __name__ == "__main__":
    show_memory_v2()
