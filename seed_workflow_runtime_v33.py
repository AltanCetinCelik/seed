import json
import uuid
from datetime import datetime
from pathlib import Path


WORKFLOW_FILE = Path("seed_workflow_runtime_v33.json")


DEFAULT_NODES = [
    "understand",
    "retrieve_memory",
    "council_review",
    "policy_check",
    "checkpoint",
    "dry_run",
    "human_review",
    "execute",
    "verify",
    "learn"
]


def now_timestamp():
    return datetime.now().isoformat(timespec="seconds")


def _load():
    if WORKFLOW_FILE.exists():
        try:
            return json.loads(WORKFLOW_FILE.read_text(errors="ignore"))
        except Exception:
            pass
    return {"version": "v45.0.0", "workflows": []}


def _save(data):
    WORKFLOW_FILE.write_text(json.dumps(data, indent=4))
    return data


def create_workflow(goal, nodes=None):
    nodes = nodes or DEFAULT_NODES
    workflow = {
        "id": uuid.uuid4().hex[:10],
        "created_at": now_timestamp(),
        "version": "v45.0.0",
        "goal": goal,
        "nodes": [{"id": n, "status": "pending", "events": []} for n in nodes],
        "current_index": 0,
        "status": "running",
        "human_in_loop": True,
        "durable": True
    }
    data = _load()
    data.setdefault("workflows", []).append(workflow)
    _save(data)
    return workflow


def tick_workflow(workflow_id=None):
    data = _load()
    workflows = data.get("workflows", [])

    if workflow_id:
        workflow = next((w for w in workflows if w.get("id") == workflow_id), None)
    else:
        workflow = next((w for w in workflows if w.get("status") == "running"), None)

    if not workflow:
        return {"ok": False, "error": "No running workflow."}

    idx = int(workflow.get("current_index", 0))
    nodes = workflow.get("nodes", [])

    if idx >= len(nodes):
        workflow["status"] = "done"
        _save(data)
        return {"ok": True, "done": True, "workflow": workflow}

    node = nodes[idx]
    node["status"] = "done"
    node.setdefault("events", []).append({"created_at": now_timestamp(), "event": "manual_tick_completed"})
    workflow["current_index"] = idx + 1

    if workflow["current_index"] >= len(nodes):
        workflow["status"] = "done"

    _save(data)

    return {"ok": True, "completed_node": node["id"], "workflow": workflow}


def workflow_status():
    data = _load()
    return {
        "created_at": now_timestamp(),
        "version": "v45.0.0",
        "ok": True,
        "count": len(data.get("workflows", [])),
        "running": len([w for w in data.get("workflows", []) if w.get("status") == "running"]),
        "workflows": data.get("workflows", [])[-10:]
    }


def show_workflow_runtime():
    print("\n=== SEED WORKFLOW RUNTIME MAX v33 ===")
    print(json.dumps(workflow_status(), indent=4))


def show_workflow_new():
    goal = input("Workflow goal: ").strip()
    print(json.dumps(create_workflow(goal), indent=4))


def show_workflow_tick():
    print(json.dumps(tick_workflow(), indent=4))


if __name__ == "__main__":
    show_workflow_runtime()
