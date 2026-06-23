import json
from datetime import datetime


try:
    from seed_config import WORKFLOW_RECENT_LIMIT, WORKFLOW_MAX_STEPS
except Exception:
    WORKFLOW_RECENT_LIMIT = 12
    WORKFLOW_MAX_STEPS = 20


from seed_companion_os import (
    load_companion_os_state,
    save_companion_os_state,
    append_companion_os_event,
    append_companion_os_journal,
    add_companion_os_timeline_event
)


try:
    from seed_trace_engine import append_trace
    TRACE_AVAILABLE = True
except Exception:
    TRACE_AVAILABLE = False


WORKFLOW_STATUSES = [
    "active",
    "paused",
    "completed",
    "cancelled",
    "blocked"
]


STEP_STATUSES = [
    "todo",
    "doing",
    "done",
    "blocked",
    "skipped"
]


def now_timestamp():
    return datetime.now().isoformat(timespec="seconds")


def get_workflows():
    state = load_companion_os_state()
    return state.setdefault("workflows", [])


def save_workflows(workflows):
    state = load_companion_os_state()
    state["workflows"] = workflows
    save_companion_os_state(state)


def next_workflow_id(workflows):
    return f"WF2-{len(workflows) + 1:03d}"


def create_workflow(title, goal, source_repos=None, v2_pillars=None, risk="medium"):
    if source_repos is None:
        source_repos = []

    if v2_pillars is None:
        v2_pillars = []

    workflows = get_workflows()

    workflow = {
        "id": next_workflow_id(workflows),
        "created_at": now_timestamp(),
        "updated_at": now_timestamp(),
        "title": title,
        "goal": goal,
        "status": "active",
        "risk": risk,
        "source_repos": source_repos,
        "v2_pillars": v2_pillars,
        "steps": [],
        "notes": [],
        "approval_points": [],
        "result": None
    }

    workflows.append(workflow)
    save_workflows(workflows)

    append_companion_os_event(
        "workflow_created",
        f"Workflow created: {title}",
        workflow,
        source="workflow_engine",
        importance=4
    )

    add_companion_os_timeline_event(
        title=f"Workflow started: {title}",
        event_type="workflow",
        note=goal,
        importance=4
    )

    if TRACE_AVAILABLE:
        append_trace(
            trace_type="proposal_trace",
            title=f"Workflow created: {title}",
            summary=f"Goal: {goal}",
            sources=source_repos,
            decision="created",
            risk=risk
        )

    return workflow


def create_workflow_interactive():
    print("\n=== CREATE DURABLE WORKFLOW ===")

    title = input("Title: ").strip()
    goal = input("Goal: ").strip()
    repos_raw = input("Source repos, comma-separated: ").strip()
    pillars_raw = input("V2 pillars, comma-separated: ").strip()
    risk = input("Risk low/medium/high: ").strip() or "medium"

    if not title or not goal:
        print("Title and goal are required.")
        return

    source_repos = [repo.strip() for repo in repos_raw.split(",") if repo.strip()]
    v2_pillars = [pillar.strip() for pillar in pillars_raw.split(",") if pillar.strip()]

    workflow = create_workflow(
        title=title,
        goal=goal,
        source_repos=source_repos,
        v2_pillars=v2_pillars,
        risk=risk
    )

    print(f"Workflow created: {workflow['id']}")


def find_workflow(workflow_id):
    for workflow in get_workflows():
        if workflow.get("id", "").lower() == workflow_id.lower():
            return workflow

    return None


def update_workflow(updated_workflow):
    workflows = get_workflows()

    for index, workflow in enumerate(workflows):
        if workflow.get("id") == updated_workflow.get("id"):
            updated_workflow["updated_at"] = now_timestamp()
            workflows[index] = updated_workflow
            save_workflows(workflows)
            return True

    return False


def add_workflow_step(workflow_id, title, details="", risk="low", approval_required=False, owner="Builder"):
    workflow = find_workflow(workflow_id)

    if workflow is None:
        return {
            "ok": False,
            "message": "Workflow not found."
        }

    if len(workflow.get("steps", [])) >= WORKFLOW_MAX_STEPS:
        return {
            "ok": False,
            "message": f"Workflow already has max steps: {WORKFLOW_MAX_STEPS}"
        }

    step = {
        "step": len(workflow.get("steps", [])) + 1,
        "created_at": now_timestamp(),
        "updated_at": now_timestamp(),
        "title": title,
        "details": details,
        "status": "todo",
        "risk": risk,
        "approval_required": bool(approval_required),
        "owner": owner
    }

    workflow.setdefault("steps", []).append(step)
    update_workflow(workflow)

    append_companion_os_event(
        "workflow_step_added",
        f"Workflow step added: {title}",
        {
            "workflow_id": workflow_id,
            "step": step
        },
        source="workflow_engine",
        importance=3
    )

    return {
        "ok": True,
        "step": step
    }


def add_workflow_step_interactive():
    show_workflows()

    workflow_id = input("\nWorkflow ID: ").strip()
    title = input("Step title: ").strip()
    details = input("Details: ").strip()
    risk = input("Risk low/medium/high: ").strip() or "low"
    approval = input("Approval required? y/n: ").strip().lower() == "y"
    owner = input("Owner agent: ").strip() or "Builder"

    if not workflow_id or not title:
        print("Workflow ID and title required.")
        return

    result = add_workflow_step(
        workflow_id=workflow_id,
        title=title,
        details=details,
        risk=risk,
        approval_required=approval,
        owner=owner
    )

    if result["ok"]:
        print("Step added.")
    else:
        print(result["message"])


def set_workflow_status(workflow_id, status):
    if status not in WORKFLOW_STATUSES:
        return {
            "ok": False,
            "message": f"Invalid status. Use: {', '.join(WORKFLOW_STATUSES)}"
        }

    workflow = find_workflow(workflow_id)

    if workflow is None:
        return {
            "ok": False,
            "message": "Workflow not found."
        }

    workflow["status"] = status
    update_workflow(workflow)

    append_companion_os_event(
        "workflow_status_changed",
        f"Workflow {workflow_id} set to {status}",
        {
            "workflow_id": workflow_id,
            "status": status
        },
        source="workflow_engine",
        importance=3
    )

    return {
        "ok": True,
        "workflow": workflow
    }


def pause_workflow_interactive():
    show_workflows()
    workflow_id = input("\nWorkflow ID to pause: ").strip()
    result = set_workflow_status(workflow_id, "paused")
    print(result["message"] if not result["ok"] else "Workflow paused.")


def resume_workflow_interactive():
    show_workflows()
    workflow_id = input("\nWorkflow ID to resume: ").strip()
    result = set_workflow_status(workflow_id, "active")
    print(result["message"] if not result["ok"] else "Workflow resumed.")


def cancel_workflow_interactive():
    show_workflows()
    workflow_id = input("\nWorkflow ID to cancel: ").strip()
    reason = input("Reason: ").strip()

    workflow = find_workflow(workflow_id)

    if workflow is None:
        print("Workflow not found.")
        return

    workflow["status"] = "cancelled"
    workflow.setdefault("notes", []).append({
        "created_at": now_timestamp(),
        "note": f"Cancelled: {reason}"
    })

    update_workflow(workflow)

    append_companion_os_event(
        "workflow_cancelled",
        f"Workflow cancelled: {workflow.get('title')}",
        {
            "workflow_id": workflow_id,
            "reason": reason
        },
        source="workflow_engine",
        importance=3
    )

    print("Workflow cancelled.")


def complete_workflow_interactive():
    show_workflows()
    workflow_id = input("\nWorkflow ID to complete: ").strip()
    result_text = input("Result: ").strip()

    workflow = find_workflow(workflow_id)

    if workflow is None:
        print("Workflow not found.")
        return

    workflow["status"] = "completed"
    workflow["result"] = result_text
    workflow["completed_at"] = now_timestamp()

    update_workflow(workflow)

    add_companion_os_timeline_event(
        title=f"Workflow completed: {workflow.get('title')}",
        event_type="workflow_completed",
        note=result_text,
        importance=4
    )

    append_companion_os_journal(
        f"Workflow completed: {workflow.get('title')}",
        result_text
    )

    print("Workflow completed.")


def set_step_status(workflow_id, step_number, status):
    if status not in STEP_STATUSES:
        return {
            "ok": False,
            "message": f"Invalid step status. Use: {', '.join(STEP_STATUSES)}"
        }

    workflow = find_workflow(workflow_id)

    if workflow is None:
        return {
            "ok": False,
            "message": "Workflow not found."
        }

    for step in workflow.get("steps", []):
        if int(step.get("step")) == int(step_number):
            step["status"] = status
            step["updated_at"] = now_timestamp()
            update_workflow(workflow)
            return {
                "ok": True,
                "step": step
            }

    return {
        "ok": False,
        "message": "Step not found."
    }


def set_step_status_interactive():
    show_workflows()

    workflow_id = input("\nWorkflow ID: ").strip()
    step_number = input("Step number: ").strip()
    status = input(f"Status {STEP_STATUSES}: ").strip()

    result = set_step_status(workflow_id, step_number, status)

    if result["ok"]:
        print("Step updated.")
    else:
        print(result["message"])


def add_workflow_note_interactive():
    show_workflows()

    workflow_id = input("\nWorkflow ID: ").strip()
    note = input("Note: ").strip()

    workflow = find_workflow(workflow_id)

    if workflow is None:
        print("Workflow not found.")
        return

    workflow.setdefault("notes", []).append({
        "created_at": now_timestamp(),
        "note": note
    })

    update_workflow(workflow)
    print("Workflow note added.")


def workflow_summary(workflow):
    done_steps = len([step for step in workflow.get("steps", []) if step.get("status") == "done"])
    total_steps = len(workflow.get("steps", []))

    return {
        "id": workflow.get("id"),
        "title": workflow.get("title"),
        "goal": workflow.get("goal"),
        "status": workflow.get("status"),
        "risk": workflow.get("risk"),
        "steps_done": done_steps,
        "steps_total": total_steps,
        "v2_pillars": workflow.get("v2_pillars", []),
        "source_repos": workflow.get("source_repos", [])
    }


def show_workflows(limit=WORKFLOW_RECENT_LIMIT):
    workflows = get_workflows()[-limit:]

    print("\n=== DURABLE WORKFLOWS ===")

    if not workflows:
        print("No workflows yet.")
        return

    for workflow in workflows:
        summary = workflow_summary(workflow)

        print(f"\n{summary['id']} — {summary['title']}")
        print(f"Status: {summary['status']}")
        print(f"Risk: {summary['risk']}")
        print(f"Goal: {summary['goal']}")
        print(f"Progress: {summary['steps_done']} / {summary['steps_total']}")
        print(f"Pillars: {', '.join(summary['v2_pillars'])}")
        print(f"Sources: {', '.join(summary['source_repos'])}")

        for step in workflow.get("steps", []):
            approval = " approval" if step.get("approval_required") else ""
            print(
                f"  {step.get('step')}. [{step.get('status')}] "
                f"{step.get('title')} ({step.get('owner')}, {step.get('risk')}{approval})"
            )


def get_workflow_context_for_prompt():
    workflows = get_workflows()[-WORKFLOW_RECENT_LIMIT:]

    text = "=== WORKFLOW ENGINE CONTEXT ===\n"
    text += f"Recent workflows: {len(workflows)}\n"

    if not workflows:
        text += "No workflows yet.\n"
    else:
        for workflow in workflows:
            summary = workflow_summary(workflow)
            text += (
                f"- {summary['id']} {summary['title']} "
                f"[{summary['status']}] "
                f"{summary['steps_done']}/{summary['steps_total']} steps\n"
            )
            text += f"  Goal: {summary['goal']}\n"

    text += """
Workflow rule:
Workflows are durable plans, not autonomous execution.
Risky workflow steps require explicit approval through existing gates.
"""

    return text


if __name__ == "__main__":
    show_workflows()
