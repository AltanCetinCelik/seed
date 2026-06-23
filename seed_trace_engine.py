import json
import os
from datetime import datetime


try:
    from seed_config import SEED_TRACE_LOG_FILE, COMPANION_OS_TRACE_LIMIT
except Exception:
    SEED_TRACE_LOG_FILE = "seed_trace_log.jsonl"
    COMPANION_OS_TRACE_LIMIT = 30


try:
    from seed_companion_os import (
        append_companion_os_event,
        append_companion_os_journal,
        load_companion_os_state,
        save_companion_os_state
    )
    COMPANION_OS_AVAILABLE = True
except Exception:
    COMPANION_OS_AVAILABLE = False


TRACE_TYPES = [
    "answer_trace",
    "memory_trace",
    "tool_trace",
    "permission_trace",
    "proposal_trace",
    "ritual_trace",
    "voice_trace",
    "world_trace",
    "self_edit_trace",
    "safety_trace",
    "release_trace",
    "migration_trace",
    "bridge_trace",
    "registry_trace"
]


def now_timestamp():
    return datetime.now().isoformat(timespec="seconds")


def normalize_trace_type(trace_type):
    if trace_type in TRACE_TYPES:
        return trace_type

    return "general_trace"


def append_trace(
    trace_type,
    title,
    summary,
    sources=None,
    decision=None,
    risk="unknown",
    related_command=None,
    related_files=None,
    metadata=None
):
    if sources is None:
        sources = []

    if related_files is None:
        related_files = []

    if metadata is None:
        metadata = {}

    trace = {
        "created_at": now_timestamp(),
        "trace_type": normalize_trace_type(trace_type),
        "title": title,
        "summary": summary,
        "sources": sources,
        "decision": decision,
        "risk": risk,
        "related_command": related_command,
        "related_files": related_files,
        "metadata": metadata
    }

    with open(SEED_TRACE_LOG_FILE, "a") as file:
        file.write(json.dumps(trace) + "\n")

    if COMPANION_OS_AVAILABLE:
        try:
            append_companion_os_event(
                event_type="trace_recorded",
                title=f"Trace recorded: {title}",
                details={
                    "trace_type": trace["trace_type"],
                    "risk": risk,
                    "decision": decision,
                    "related_command": related_command
                },
                source="trace_engine",
                importance=3
            )
        except Exception:
            pass

        try:
            state = load_companion_os_state()
            state.setdefault("trust", {})
            state["trust"].setdefault("answer_traces", [])

            if trace["trace_type"] in ["answer_trace", "proposal_trace", "safety_trace"]:
                state["trust"]["answer_traces"].append(trace)

            if trace["trace_type"] == "permission_trace":
                state["trust"].setdefault("permission_traces", [])
                state["trust"]["permission_traces"].append({
                    "created_at": trace["created_at"],
                    "action": title,
                    "decision": decision or "recorded",
                    "reason": summary,
                    "risk": risk
                })

            save_companion_os_state(state)
        except Exception:
            pass

    return trace


def load_traces(limit=None, trace_type=None):
    if not os.path.exists(SEED_TRACE_LOG_FILE):
        return []

    traces = []

    with open(SEED_TRACE_LOG_FILE, "r") as file:
        for line in file:
            try:
                trace = json.loads(line)
            except json.JSONDecodeError:
                continue

            if trace_type is not None and trace.get("trace_type") != trace_type:
                continue

            traces.append(trace)

    if limit is not None:
        return traces[-limit:]

    return traces


def get_last_trace():
    traces = load_traces(limit=1)

    if not traces:
        return None

    return traces[-1]


def format_trace(trace):
    if trace is None:
        return "No trace."

    text = "=== SEED TRACE ===\n"
    text += f"Title: {trace.get('title')}\n"
    text += f"Type: {trace.get('trace_type')}\n"
    text += f"Created: {trace.get('created_at')}\n"
    text += f"Risk: {trace.get('risk')}\n"
    text += f"Decision: {trace.get('decision')}\n"

    if trace.get("related_command"):
        text += f"Command: {trace.get('related_command')}\n"

    if trace.get("related_files"):
        text += f"Files: {', '.join(trace.get('related_files', []))}\n"

    text += "\nSummary:\n"
    text += f"{trace.get('summary')}\n"

    if trace.get("sources"):
        text += "\nSources:\n"
        for source in trace.get("sources", []):
            text += f"- {source}\n"

    if trace.get("metadata"):
        text += "\nMetadata:\n"
        text += json.dumps(trace.get("metadata"), indent=4) + "\n"

    return text


def show_trace_log(limit=COMPANION_OS_TRACE_LIMIT):
    print("\n=== SEED TRACE LOG ===")

    traces = load_traces(limit=limit)

    if not traces:
        print("No traces yet.")
        return

    for trace in traces:
        print(f"\n{trace.get('created_at')} — {trace.get('trace_type')}")
        print(f"Title: {trace.get('title')}")
        print(f"Risk: {trace.get('risk')}")
        print(f"Decision: {trace.get('decision')}")
        if trace.get("related_command"):
            print(f"Command: {trace.get('related_command')}")


def show_last_trace():
    print("\n" + format_trace(get_last_trace()))


def record_answer_trace(prompt, answer, context_sources=None, confidence="medium"):
    if context_sources is None:
        context_sources = []

    summary = (
        "Seed answered a user prompt.\n\n"
        f"Prompt:\n{prompt}\n\n"
        f"Answer excerpt:\n{answer[:1200]}"
    )

    return append_trace(
        trace_type="answer_trace",
        title="Answer generated",
        summary=summary,
        sources=context_sources,
        decision="answered",
        risk="low",
        metadata={
            "confidence": confidence
        }
    )


def record_tool_trace(command, tool_name, decision, reason, risk="unknown", side_effects=None):
    if side_effects is None:
        side_effects = []

    return append_trace(
        trace_type="tool_trace",
        title=f"Tool use: {tool_name}",
        summary=reason,
        sources=["tool_manifest_v2", "command_registry"],
        decision=decision,
        risk=risk,
        related_command=command,
        metadata={
            "tool_name": tool_name,
            "side_effects": side_effects
        }
    )


def record_permission_trace(action, decision, reason, risk="unknown", command=None):
    return append_trace(
        trace_type="permission_trace",
        title=f"Permission decision: {action}",
        summary=reason,
        sources=["trust_center", "tool_manifest_v2"],
        decision=decision,
        risk=risk,
        related_command=command
    )


def record_proposal_trace(title, proposal_summary, source_repos=None, risk="medium"):
    if source_repos is None:
        source_repos = []

    return append_trace(
        trace_type="proposal_trace",
        title=title,
        summary=proposal_summary,
        sources=source_repos,
        decision="proposed",
        risk=risk
    )


def record_self_edit_trace(title, files, decision, summary, risk="high"):
    return append_trace(
        trace_type="self_edit_trace",
        title=title,
        summary=summary,
        sources=["self_editor", "Cline", "Aider"],
        decision=decision,
        risk=risk,
        related_files=files
    )


def record_world_trace(title, summary, world_event_type="world_update"):
    return append_trace(
        trace_type="world_trace",
        title=title,
        summary=summary,
        sources=["Seed World", "Memory Garden"],
        decision="world_state_updated",
        risk="low",
        metadata={
            "world_event_type": world_event_type
        }
    )


def record_voice_trace(title, summary, decision="spoken", risk="low"):
    return append_trace(
        trace_type="voice_trace",
        title=title,
        summary=summary,
        sources=["voice_session"],
        decision=decision,
        risk=risk
    )


def why_did_you_report(query=None):
    traces = load_traces(limit=20)

    if not traces:
        return "No traces exist yet, so Seed cannot explain from trace history."

    if query:
        lowered = query.lower()
        scored = []

        for trace in traces:
            haystack = json.dumps(trace).lower()
            score = 0

            for word in lowered.split():
                if len(word) >= 3 and word in haystack:
                    score += 1

            if score > 0:
                scored.append((score, trace))

        scored.sort(key=lambda pair: pair[0], reverse=True)

        if scored:
            chosen = scored[0][1]
            return format_trace(chosen)

    return format_trace(traces[-1])


def why_did_you_interactive():
    query = input("What should Seed explain? ").strip()

    if query == "":
        query = None

    print("\n" + why_did_you_report(query))


def trace_stats():
    traces = load_traces()

    by_type = {}
    by_risk = {}
    by_decision = {}

    for trace in traces:
        by_type[trace.get("trace_type", "unknown")] = by_type.get(trace.get("trace_type", "unknown"), 0) + 1
        by_risk[trace.get("risk", "unknown")] = by_risk.get(trace.get("risk", "unknown"), 0) + 1
        by_decision[trace.get("decision", "unknown")] = by_decision.get(trace.get("decision", "unknown"), 0) + 1

    return {
        "total": len(traces),
        "by_type": by_type,
        "by_risk": by_risk,
        "by_decision": by_decision
    }


def show_trace_stats():
    stats = trace_stats()

    print("\n=== TRACE STATS ===")
    print(f"Total traces: {stats['total']}")

    print("\nBy type:")
    for key, value in sorted(stats["by_type"].items()):
        print(f"- {key}: {value}")

    print("\nBy risk:")
    for key, value in sorted(stats["by_risk"].items()):
        print(f"- {key}: {value}")

    print("\nBy decision:")
    for key, value in sorted(stats["by_decision"].items()):
        print(f"- {key}: {value}")


def get_trace_context_for_prompt():
    stats = trace_stats()
    recent = load_traces(limit=8)

    text = "=== TRACE ENGINE CONTEXT ===\n"
    text += f"Total traces: {stats['total']}\n"

    text += "\nRecent traces:\n"
    if not recent:
        text += "No traces yet.\n"
    else:
        for trace in recent:
            text += (
                f"- {trace.get('trace_type')}: {trace.get('title')} "
                f"[risk={trace.get('risk')}, decision={trace.get('decision')}]\n"
            )

    text += """
Trace rule:
Seed should be able to explain important answers, proposals, tool uses, permissions, self-edits, world updates, and voice actions through trace records.
If no trace exists, Seed should say so honestly.
"""

    return text


if __name__ == "__main__":
    show_trace_stats()
    show_last_trace()
