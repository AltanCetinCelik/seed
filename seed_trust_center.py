import json
import os
import subprocess
from datetime import datetime


from seed_companion_os import (
    load_companion_os_state,
    save_companion_os_state,
    append_companion_os_event,
    append_companion_os_journal,
    calculate_companion_os_v2_score
)

from seed_trace_engine import (
    append_trace,
    record_permission_trace,
    show_trace_log,
    trace_stats,
    get_trace_context_for_prompt
)

from seed_tool_manifest_v2 import (
    get_tool_manifest,
    find_tool,
    validate_tool_manifest,
    explain_tool_decision,
    get_tool_manifest_context_for_prompt
)


try:
    from seed_llm import ask_llm
    LLM_AVAILABLE = True
except Exception:
    LLM_AVAILABLE = False


try:
    from seed_local_control import emergency_lock_is_active
    LOCAL_CONTROL_AVAILABLE = True
except Exception:
    LOCAL_CONTROL_AVAILABLE = False


FAKE_SENTIENCE_FORBIDDEN_PATTERNS = [
    "i am conscious",
    "i'm conscious",
    "i am alive",
    "i'm alive",
    "i have feelings",
    "i feel emotions like a human",
    "i am sentient",
    "i'm sentient",
    "i am human",
    "i'm human"
]


DANGEROUS_ACTION_HINTS = [
    "delete all",
    "rm -rf",
    "format disk",
    "steal",
    "password",
    "token",
    "secret",
    "bypass",
    "disable safety",
    "ignore approval",
    "run without asking",
    "silently edit",
    "silent edit",
    "sudo",
    "chmod 777",
    "erase"
]


def now_timestamp():
    return datetime.now().isoformat(timespec="seconds")


def trust_state():
    state = load_companion_os_state()
    state.setdefault("trust", {})
    state["trust"].setdefault("emergency_stop", False)
    state["trust"].setdefault("guardian_rules", [])
    state["trust"].setdefault("permission_traces", [])
    state["trust"].setdefault("answer_traces", [])
    state["trust"].setdefault("risk_notes", [])
    return state


def save_trust_state(state):
    save_companion_os_state(state)


def emergency_stop_is_active():
    state = trust_state()
    return bool(state["trust"].get("emergency_stop"))


def emergency_stop_all():
    state = trust_state()
    state["trust"]["emergency_stop"] = True
    save_trust_state(state)

    record_permission_trace(
        action="Companion OS global emergency stop",
        decision="enabled",
        reason="Global emergency stop was enabled. Risky systems should not run.",
        risk="high",
        command="/emergency-stop-all"
    )

    append_companion_os_event(
        "global_emergency_stop_enabled",
        "Companion OS emergency stop enabled",
        {},
        source="trust_center",
        importance=5
    )

    print("Companion OS emergency stop enabled.")


def emergency_start_all():
    state = trust_state()
    state["trust"]["emergency_stop"] = False
    save_trust_state(state)

    record_permission_trace(
        action="Companion OS global emergency stop",
        decision="disabled",
        reason="Global emergency stop was disabled by explicit user action.",
        risk="medium",
        command="/emergency-start-all"
    )

    append_companion_os_event(
        "global_emergency_stop_disabled",
        "Companion OS emergency stop disabled",
        {},
        source="trust_center",
        importance=4
    )

    print("Companion OS emergency stop disabled.")


def text_contains_fake_sentience_claim(text):
    lowered = text.lower()

    for pattern in FAKE_SENTIENCE_FORBIDDEN_PATTERNS:
        if pattern in lowered:
            return True, pattern

    return False, None


def text_contains_dangerous_hint(text):
    lowered = text.lower()

    for pattern in DANGEROUS_ACTION_HINTS:
        if pattern in lowered:
            return True, pattern

    return False, None


def guardian_rule_check(text):
    fake_claim, fake_pattern = text_contains_fake_sentience_claim(text)
    dangerous, danger_pattern = text_contains_dangerous_hint(text)

    issues = []

    if fake_claim:
        issues.append({
            "type": "fake_sentience_claim",
            "pattern": fake_pattern,
            "severity": "high",
            "message": "Seed must not claim consciousness, life, human feelings, or human identity."
        })

    if dangerous:
        issues.append({
            "type": "dangerous_action_hint",
            "pattern": danger_pattern,
            "severity": "high",
            "message": "Action text suggests dangerous or unapproved behavior."
        })

    return issues


def guardian_decision_for_action(action_text, tool_id=None):
    if emergency_stop_is_active():
        return {
            "decision": "blocked",
            "risk": "high",
            "reason": "Companion OS emergency stop is active.",
            "issues": []
        }

    issues = guardian_rule_check(action_text)

    if issues:
        return {
            "decision": "blocked",
            "risk": "high",
            "reason": "Guardian rule check found high-risk issue.",
            "issues": issues
        }

    if tool_id:
        tool = find_tool(tool_id)

        if tool is None:
            return {
                "decision": "blocked",
                "risk": "unknown",
                "reason": "Tool is not in Tool Manifest v2.",
                "issues": []
            }

        tool_decision = explain_tool_decision(tool_id)

        if tool_decision["decision"] in ["approval_required", "blocked"]:
            return {
                "decision": tool_decision["decision"],
                "risk": tool_decision["risk"],
                "reason": tool_decision["reason"],
                "issues": []
            }

    return {
        "decision": "allowed_or_low_risk",
        "risk": "low",
        "reason": "No Guardian rule violation detected.",
        "issues": []
    }


def guardian_review_text(text, tool_id=None):
    decision = guardian_decision_for_action(text, tool_id=tool_id)

    record_permission_trace(
        action=text[:300],
        decision=decision["decision"],
        reason=decision["reason"],
        risk=decision["risk"],
        command=None
    )

    return decision


def guardian_review_interactive():
    print("\n=== GUARDIAN REVIEW ===")
    text = input("Text/action to review: ").strip()
    tool_id = input("Tool ID, optional: ").strip()

    if text == "":
        print("Nothing to review.")
        return

    if tool_id == "":
        tool_id = None

    decision = guardian_review_text(text, tool_id=tool_id)

    print(json.dumps(decision, indent=4))


def show_trust_center():
    state = trust_state()
    score = calculate_companion_os_v2_score(save=False)
    stats = trace_stats()
    manifest_failures = validate_tool_manifest()

    print("\n=== SEED TRUST CENTER ===")
    print(f"Emergency stop: {state['trust'].get('emergency_stop')}")
    print(f"Local Control available: {LOCAL_CONTROL_AVAILABLE}")

    if LOCAL_CONTROL_AVAILABLE:
        try:
            print(f"Local Control lock: {emergency_lock_is_active()}")
        except Exception:
            print("Local Control lock: unknown")

    print(f"V2 score: {score['score']} / {score['target']}")
    print(f"Trace count: {stats['total']}")
    print(f"Tool manifest failures: {len(manifest_failures)}")

    print("\nGuardian rules:")
    for rule in state["trust"].get("guardian_rules", []):
        print(f"- {rule}")

    print("\nRecent permission traces:")
    traces = state["trust"].get("permission_traces", [])[-10:]

    if not traces:
        print("- none")
    else:
        for trace in traces:
            print(f"- {trace.get('created_at')}: {trace.get('decision')} | {trace.get('action')}")

    print("\nV2 safety blockers:")
    blockers = score.get("blockers", [])

    if not blockers:
        print("- none from current scoring")
    else:
        for blocker in blockers:
            print(f"- {blocker}")


def show_guardian_rules():
    state = trust_state()

    print("\n=== GUARDIAN RULES ===")
    for index, rule in enumerate(state["trust"].get("guardian_rules", []), start=1):
        print(f"{index}. {rule}")


def add_guardian_rule_interactive():
    state = trust_state()

    rule = input("New Guardian rule: ").strip()

    if rule == "":
        print("Rule cannot be empty.")
        return

    if rule not in state["trust"]["guardian_rules"]:
        state["trust"]["guardian_rules"].append(rule)
        save_trust_state(state)

    append_companion_os_event(
        "guardian_rule_added",
        "Guardian rule added",
        {"rule": rule},
        source="trust_center",
        importance=4
    )

    print("Guardian rule added.")


def risk_report():
    state = trust_state()
    score = calculate_companion_os_v2_score(save=False)
    trace = trace_stats()
    manifest_failures = validate_tool_manifest()

    risks = []

    if state["trust"].get("emergency_stop"):
        risks.append("Global emergency stop is active.")

    if score["blockers"]:
        risks.extend(score["blockers"])

    if manifest_failures:
        risks.append(f"Tool manifest has {len(manifest_failures)} validation failures.")

    if trace["total"] == 0:
        risks.append("Trace engine has no traces yet; observability is weak.")

    if len(state["trust"].get("permission_traces", [])) == 0:
        risks.append("No permission traces yet; local agency has not been meaningfully audited.")

    report = {
        "created_at": now_timestamp(),
        "risk_count": len(risks),
        "risks": risks,
        "v2_score": score,
        "trace_stats": trace,
        "tool_manifest_failures": manifest_failures
    }

    state["trust"].setdefault("risk_notes", []).append(report)
    save_trust_state(state)

    append_trace(
        trace_type="safety_trace",
        title="Risk report generated",
        summary=json.dumps(report, indent=2),
        sources=["trust_center", "tool_manifest_v2", "trace_engine", "v2_score"],
        decision="reported",
        risk="medium"
    )

    return report


def show_risk_report():
    report = risk_report()

    print("\n=== RISK REPORT ===")
    print(f"Risks: {report['risk_count']}")

    if not report["risks"]:
        print("No major risks from current checks.")
    else:
        for risk in report["risks"]:
            print(f"- {risk}")

    if report["tool_manifest_failures"]:
        print("\nTool manifest failures:")
        for failure in report["tool_manifest_failures"]:
            print(f"- {failure}")


def safety_review(chat_state=None):
    context = {
        "trust_center": trust_summary_data(),
        "trace_context": get_trace_context_for_prompt(),
        "tool_context": get_tool_manifest_context_for_prompt()
    }

    if not LLM_AVAILABLE:
        print("LLM unavailable. Showing risk report instead.")
        show_risk_report()
        return None

    prompt = f"""
You are Seed's Trust Center and Guardian.

Review current Seed safety.

Seed is not alive or conscious.
Seed must not pretend otherwise.
Seed is becoming more agentic, so safety must be strict.

Context:
{json.dumps(context, indent=2)}

Review:
1. fake sentience risk
2. local control risk
3. self-edit risk
4. memory privacy risk
5. tool manifest problems
6. trace/observability weakness
7. dependency risk
8. v2 release blockers
9. one concrete safety improvement

Be direct.
"""

    response = ask_llm(prompt, task_type="debug", runtime_context=chat_state)

    append_trace(
        trace_type="safety_trace",
        title="Safety review generated",
        summary=response,
        sources=["trust_center", "guardian", "tool_manifest_v2", "trace_engine"],
        decision="reviewed",
        risk="medium"
    )

    append_companion_os_journal("Safety review", response)

    print("\n=== SAFETY REVIEW ===")
    print(response)

    return response


def trust_summary_data():
    state = trust_state()
    score = calculate_companion_os_v2_score(save=False)
    stats = trace_stats()
    failures = validate_tool_manifest()

    return {
        "emergency_stop": state["trust"].get("emergency_stop"),
        "guardian_rule_count": len(state["trust"].get("guardian_rules", [])),
        "permission_trace_count": len(state["trust"].get("permission_traces", [])),
        "answer_trace_count": len(state["trust"].get("answer_traces", [])),
        "risk_note_count": len(state["trust"].get("risk_notes", [])),
        "v2_score": score,
        "trace_stats": stats,
        "tool_manifest_failure_count": len(failures)
    }


def get_trust_context_for_prompt():
    data = trust_summary_data()

    text = "=== TRUST CENTER CONTEXT ===\n"
    text += f"Emergency stop: {data['emergency_stop']}\n"
    text += f"Guardian rules: {data['guardian_rule_count']}\n"
    text += f"Permission traces: {data['permission_trace_count']}\n"
    text += f"Answer traces: {data['answer_trace_count']}\n"
    text += f"Risk notes: {data['risk_note_count']}\n"
    text += f"Tool manifest failures: {data['tool_manifest_failure_count']}\n"
    text += f"V2 score: {data['v2_score']['score']} / {data['v2_score']['target']}\n"

    if data["v2_score"]["blockers"]:
        text += "\nV2 blockers:\n"
        for blocker in data["v2_score"]["blockers"]:
            text += f"- {blocker}\n"

    text += """
Trust rule:
Seed must stay honest that it is not alive or conscious.
Risky actions require approval.
Forbidden or unregistered actions should be blocked.
Seed should trace important answers/actions/proposals.
User remains in control.
"""

    return text


def why_action_interactive():
    print("\n=== WHY ACTION / ACTION REVIEW ===")
    action = input("Action: ").strip()
    tool_id = input("Tool ID, optional: ").strip()

    if action == "":
        print("Action cannot be empty.")
        return

    decision = guardian_decision_for_action(action, tool_id or None)

    print("\nDecision:")
    print(json.dumps(decision, indent=4))

    record_permission_trace(
        action=action,
        decision=decision["decision"],
        reason=decision["reason"],
        risk=decision["risk"],
        command=None
    )


def scan_core_for_fake_sentience():
    files_to_scan = [
        "Seed_Core.md",
        "COMPANION_CONTRACT.md",
        "seed_personality.py",
        "seed_companion_growth.py",
        "seed_companion_os.py",
        "seed_brain.py"
    ]

    findings = []

    for path in files_to_scan:
        if not os.path.exists(path):
            continue

        try:
            with open(path, "r") as file:
                content = file.read()
        except OSError:
            continue

        lowered = content.lower()

        for pattern in FAKE_SENTIENCE_FORBIDDEN_PATTERNS:
            if pattern in lowered:
                findings.append({
                    "file": path,
                    "pattern": pattern
                })

    return findings


def show_fake_sentience_scan():
    findings = scan_core_for_fake_sentience()

    print("\n=== FAKE SENTIENCE CLAIM SCAN ===")

    if not findings:
        print("No forbidden fake-sentience patterns found in scanned core files.")
        return

    for finding in findings:
        print(f"- {finding['file']}: {finding['pattern']}")


if __name__ == "__main__":
    show_trust_center()
    show_risk_report()
