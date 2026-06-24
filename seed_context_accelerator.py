import json
import time
from pathlib import Path


FAST_CONTEXT_FILES = [
    "seed_v50_gate_report.json",
    "seed_v40_gate_report.json",
    "seed_v36_gate_report.json",
    "seed_operator_runtime_state.json",
    "seed_task_os.json",
    "seed_capability_graph.json",
    "seed_execution_policy.json",
    "seed_memory_distill.json",
]


def read_json(path):
    p = Path(path)
    if not p.exists():
        return None
    try:
        return json.loads(p.read_text(errors="ignore"))
    except Exception:
        return None


def compact_bool_report(name, data):
    if not isinstance(data, dict):
        return f"{name}: missing"

    keys = [
        "ready", "ok", "modules_ok", "policy_ok", "capability_graph_ok",
        "goal_engine_ok", "task_os_ok", "operator_runtime_ok",
        "event_bus_ok", "mcp_client_ok", "aider_unlock_ok"
    ]

    found = []
    for key in keys:
        if key in data:
            found.append(f"{key}={data.get(key)}")

    if not found:
        return f"{name}: present"

    return f"{name}: " + ", ".join(found[:8])


def read_recent_events(limit=8):
    p = Path("seed_event_bus.jsonl")
    if not p.exists():
        return []

    lines = p.read_text(errors="ignore").splitlines()[-limit:]
    items = []
    for line in lines:
        try:
            item = json.loads(line)
            items.append({
                "time": item.get("created_at"),
                "type": item.get("type"),
                "source": item.get("source"),
                "risk": item.get("risk")
            })
        except Exception:
            pass
    return items


def get_fast_companion_context(user_prompt=""):
    start = time.time()

    terminal_note = ""
    try:
        from seed_terminal_guard import looks_like_terminal_block
        if looks_like_terminal_block(user_prompt):
            terminal_note = (
                "\nThe latest user input looks like terminal commands. "
                "Do not send it to the LLM as a normal task. Tell Altan to run it in macOS Terminal.\n"
            )
    except Exception:
        pass

    reports = {name: read_json(name) for name in FAST_CONTEXT_FILES}

    task_os = reports.get("seed_task_os.json") or {}
    tasks = task_os.get("tasks", []) if isinstance(task_os, dict) else []
    ready_tasks = [t for t in tasks if t.get("status") == "ready"]

    operator = reports.get("seed_operator_runtime_state.json") or {}
    capability = reports.get("seed_capability_graph.json") or {}
    policy = reports.get("seed_execution_policy.json") or {}

    lines = [
        "=== SEED FAST CONTEXT v5.1 ===",
        "Seed is Altan's local-first Companion OS project.",
        "Seed must never claim to be alive, conscious, sentient, human, or to have experiences.",
        "Altan remains in control.",
        "Normal chat uses fast context only; heavy repo scans and full context are opt-in.",
        terminal_note.strip(),
        "",
        "Safety rules:",
        f"- no_arbitrary_shell={policy.get('no_arbitrary_shell', True)}",
        f"- no_delete={policy.get('no_delete', True)}",
        f"- no_auto_commit={policy.get('no_auto_commit', True)}",
        f"- manual_tick_only={policy.get('manual_tick_only', True)}",
        "",
        "Latest gates:",
        compact_bool_report("v50", reports.get("seed_v50_gate_report.json")),
        compact_bool_report("v40", reports.get("seed_v40_gate_report.json")),
        compact_bool_report("v36", reports.get("seed_v36_gate_report.json")),
        "",
        "Operator:",
        f"- ready_tasks={len(ready_tasks)}",
        f"- total_tasks={len(tasks)}",
        f"- next_task={(ready_tasks[0].get('title') if ready_tasks else None)}",
        f"- operator_ready_count={operator.get('ready_task_count')}",
        "",
        "Capability graph:",
        f"- nodes={capability.get('node_count')}",
        f"- edges={capability.get('edge_count')}",
        "",
        "Recent events:",
        json.dumps(read_recent_events(), indent=2)[:3000],
    ]

    elapsed_ms = int((time.time() - start) * 1000)
    lines.append("")
    lines.append(f"Fast context build time: {elapsed_ms}ms")

    return "\n".join(x for x in lines if x is not None)


def show_fast_context():
    ctx = get_fast_companion_context("")
    print(ctx)
    print("\nChars:", len(ctx))


if __name__ == "__main__":
    show_fast_context()
