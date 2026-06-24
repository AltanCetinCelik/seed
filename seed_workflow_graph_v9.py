import json
from datetime import datetime


try:
    from seed_config import SEED_WORKFLOW_GRAPH_FILE
except Exception:
    SEED_WORKFLOW_GRAPH_FILE = "seed_workflow_graph_v9.json"


def now_timestamp():
    return datetime.now().isoformat(timespec="seconds")


def build_workflow_graph():
    graph = {
        "created_at": now_timestamp(),
        "version": "v20.0.0",
        "ok": True,
        "engine": "Seed Workflow Graph Brain v9",
        "external_reference": "LangGraph-style durable workflow graph, implemented Seed-native first.",
        "nodes": [
            {"id": "understand_goal", "type": "analysis"},
            {"id": "retrieve_context", "type": "memory"},
            {"id": "policy_check", "type": "safety"},
            {"id": "checkpoint", "type": "rollback"},
            {"id": "plan_tasks", "type": "task_os"},
            {"id": "dry_run", "type": "executor"},
            {"id": "review_diff", "type": "human_review"},
            {"id": "approve", "type": "approval"},
            {"id": "execute", "type": "executor"},
            {"id": "verify", "type": "gate"},
            {"id": "learn", "type": "memory"}
        ],
        "edges": [
            ["understand_goal", "retrieve_context"],
            ["retrieve_context", "policy_check"],
            ["policy_check", "checkpoint"],
            ["checkpoint", "plan_tasks"],
            ["plan_tasks", "dry_run"],
            ["dry_run", "review_diff"],
            ["review_diff", "approve"],
            ["approve", "execute"],
            ["execute", "verify"],
            ["verify", "learn"]
        ],
        "rules": {
            "manual_tick_only": True,
            "approval_before_write": True,
            "rollback_before_executor": True,
            "verify_before_success_claim": True
        }
    }

    with open(SEED_WORKFLOW_GRAPH_FILE, "w") as file:
        json.dump(graph, file, indent=4)

    return graph


def show_workflow_graph_v9():
    graph = build_workflow_graph()
    print("\n=== SEED WORKFLOW GRAPH BRAIN v9 ===")
    print(f"Nodes: {len(graph['nodes'])}")
    print(f"Edges: {len(graph['edges'])}")
    for a, b in graph["edges"]:
        print(f"- {a} -> {b}")


if __name__ == "__main__":
    show_workflow_graph_v9()
