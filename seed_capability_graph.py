import json
from datetime import datetime


try:
    from seed_config import SEED_CAPABILITY_GRAPH_FILE
except Exception:
    SEED_CAPABILITY_GRAPH_FILE = "seed_capability_graph.json"


def now_timestamp():
    return datetime.now().isoformat(timespec="seconds")


def safe_call(fn, default=None):
    try:
        return fn()
    except Exception:
        return default


def build_capability_graph():
    command_center = safe_call(
        lambda: __import__("seed_command_center", fromlist=["build_command_center"]).build_command_center(),
        {"groups": {}}
    )

    mcp_tools = safe_call(
        lambda: __import__("seed_mcp_client", fromlist=["list_seed_mcp_tools"]).list_seed_mcp_tools(),
        {"tools": []}
    )

    integration = safe_call(
        lambda: __import__("seed_integration_fusion_engine", fromlist=["build_integration_fusion"]).build_integration_fusion(),
        {"top_10": []}
    )

    policy = safe_call(
        lambda: __import__("seed_execution_policy", fromlist=["build_policy_manifest"]).build_policy_manifest(),
        {}
    )

    nodes = []
    edges = []

    for group, commands in (command_center.get("groups", {}) or {}).items():
        nodes.append({"id": f"command_group:{group}", "type": "command_group", "label": group})
        for command in commands:
            nodes.append({"id": f"command:{command}", "type": "command", "label": command})
            edges.append({"from": f"command_group:{group}", "to": f"command:{command}", "relation": "contains"})

    for tool in mcp_tools.get("tools", []) or []:
        name = tool.get("name")
        nodes.append({"id": f"mcp:{name}", "type": "mcp_tool", "label": name})
        edges.append({"from": "command_group:agents", "to": f"mcp:{name}", "relation": "can_call"})

    for item in integration.get("top_10", []) or []:
        name = item.get("name")
        nodes.append({
            "id": f"integration:{item.get('id')}",
            "type": "integration_candidate",
            "label": name,
            "score": item.get("score"),
            "status": item.get("status")
        })
        edges.append({"from": "command_group:mission", "to": f"integration:{item.get('id')}", "relation": "plans"})

    graph = {
        "created_at": now_timestamp(),
        "version": "v5.0.0",
        "ok": True,
        "node_count": len(nodes),
        "edge_count": len(edges),
        "nodes": nodes,
        "edges": edges,
        "policy": {
            "manual_tick_only": policy.get("manual_tick_only", True),
            "no_arbitrary_shell": policy.get("no_arbitrary_shell", True)
        },
        "intent_routes": {
            "status": ["command:/mission-control", "command:/runtime-supervisor", "mcp:seed.git_status"],
            "release": ["command:/gate-matrix", "command:/release-check"],
            "integration": ["command:/repo-dna", "command:/integration-fusion", "command:/omega-plan"],
            "voice": ["command:/voice-ux", "command:/aider-patch-flow"],
            "coding": ["command:/aider-unlock-plan", "command:/aider-patch-flow"],
            "rollback": ["command:/checkpoint-create", "command:/checkpoint-status"],
            "services": ["command:/service-status", "command:/service-start"]
        }
    }

    with open(SEED_CAPABILITY_GRAPH_FILE, "w") as file:
        json.dump(graph, file, indent=4)

    return graph


def route_intent(text):
    lowered = (text or "").lower()

    if "release" in lowered or "gate" in lowered or "check" in lowered:
        intent = "release"
    elif "voice" in lowered or "speak" in lowered or "transcript" in lowered:
        intent = "voice"
    elif "aider" in lowered or "code" in lowered or "patch" in lowered:
        intent = "coding"
    elif "rollback" in lowered or "checkpoint" in lowered:
        intent = "rollback"
    elif "service" in lowered or "control plane" in lowered or "server" in lowered:
        intent = "services"
    elif "repo" in lowered or "integration" in lowered or "friend" in lowered:
        intent = "integration"
    else:
        intent = "status"

    graph = build_capability_graph()
    return {
        "ok": True,
        "intent": intent,
        "routes": graph["intent_routes"].get(intent, [])
    }


def show_capability_graph():
    graph = build_capability_graph()

    print("\n=== SEED CAPABILITY GRAPH ===")
    print(f"Nodes: {graph['node_count']}")
    print(f"Edges: {graph['edge_count']}")

    print("\nIntent routes:")
    for intent, routes in graph["intent_routes"].items():
        print(f"- {intent}: {', '.join(routes[:5])}")


def show_capability_route():
    text = input("Text/goal: ").strip()
    print(json.dumps(route_intent(text), indent=4))


if __name__ == "__main__":
    show_capability_graph()
