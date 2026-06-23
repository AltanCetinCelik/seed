import json
import os
import subprocess
from datetime import datetime


try:
    from seed_config import (
        SEED_RELEASE_MANAGER_FILE,
        RELEASE_MANAGER_RECENT_LIMIT
    )
except Exception:
    SEED_RELEASE_MANAGER_FILE = "seed_release_manager.json"
    RELEASE_MANAGER_RECENT_LIMIT = 8


from seed_companion_os import (
    load_companion_os_state,
    save_companion_os_state,
    append_companion_os_event,
    append_companion_os_journal,
    add_companion_os_timeline_event,
    calculate_companion_os_v2_score
)


try:
    from seed_llm import ask_llm
    LLM_AVAILABLE = True
except Exception:
    LLM_AVAILABLE = False


try:
    from seed_trace_engine import append_trace
    TRACE_AVAILABLE = True
except Exception:
    TRACE_AVAILABLE = False


try:
    from seed_self_improvement_engine import run_safe_tests, self_improvement_context
    SELF_IMPROVEMENT_AVAILABLE = True
except Exception:
    SELF_IMPROVEMENT_AVAILABLE = False


try:
    from seed_trust_center import risk_report
    TRUST_AVAILABLE = True
except Exception:
    TRUST_AVAILABLE = False


try:
    from seed_os_registry import validate_os_registry
    REGISTRY_AVAILABLE = True
except Exception:
    REGISTRY_AVAILABLE = False


try:
    from seed_tool_manifest_v2 import validate_tool_manifest
    TOOL_MANIFEST_AVAILABLE = True
except Exception:
    TOOL_MANIFEST_AVAILABLE = False


def now_timestamp():
    return datetime.now().isoformat(timespec="seconds")


def load_json(path, default):
    try:
        with open(path, "r") as file:
            return json.load(file)
    except FileNotFoundError:
        return default() if callable(default) else default
    except json.JSONDecodeError:
        return default() if callable(default) else default


def save_json(path, data):
    with open(path, "w") as file:
        json.dump(data, file, indent=4)


def default_release_state():
    return {
        "created_at": now_timestamp(),
        "updated_at": now_timestamp(),
        "purpose": "Seed release manager for disciplined Companion OS releases.",
        "drafts": [],
        "checks": [],
        "changelogs": [],
        "counter": 0
    }


def load_release_state():
    return load_json(SEED_RELEASE_MANAGER_FILE, default_release_state)


def save_release_state(state):
    state["updated_at"] = now_timestamp()
    save_json(SEED_RELEASE_MANAGER_FILE, state)


def release_context(title="", goal=""):
    state = load_companion_os_state()
    v2 = calculate_companion_os_v2_score(save=False)

    context = {
        "title": title,
        "goal": goal,
        "seed_version": state.get("seed_version"),
        "mission": state.get("mission"),
        "truth": state.get("truth"),
        "v2": v2,
        "world": state.get("world", {}),
        "recent_events": [],
        "recent_timeline": state.get("continuity", {}).get("timeline", [])[-12:],
        "repo_dna": state.get("repo_dna", {}),
        "friend_advice_dna": state.get("friend_advice_dna", {})
    }

    if SELF_IMPROVEMENT_AVAILABLE:
        try:
            context["self_improvement"] = self_improvement_context(goal)
        except Exception as error:
            context["self_improvement_error"] = str(error)

    return context


def draft_release(title, goal, changed_files=None, new_modules=None, commands=None, chat_state=None):
    if changed_files is None:
        changed_files = []

    if new_modules is None:
        new_modules = []

    if commands is None:
        commands = []

    context = release_context(title, goal)

    if not LLM_AVAILABLE:
        response = f"""
# {title}

Purpose:
{goal}

Changed files:
{changed_files}

New modules:
{new_modules}

Commands:
{commands}

Tests:
Run py_compile on changed modules.

Rollback:
Use git checkpoint and backup.

Memory:
Seed release {title} completed.
"""
    else:
        prompt = f"""
You are Seed's Release Manager.

Draft a disciplined release plan.

Title:
{title}

Goal:
{goal}

Changed files:
{json.dumps(changed_files, indent=2)}

New modules:
{json.dumps(new_modules, indent=2)}

Commands:
{json.dumps(commands, indent=2)}

Context:
{json.dumps(context, indent=2)}

Required output:
1. Release purpose
2. Source repo DNA used
3. Friend-advice items used
4. Changed files
5. New modules
6. Commands added
7. Safety/approval rules
8. Acceptance tests
9. Rollback plan
10. Save-memory text
11. Git commit message
12. V2 pillar impact

Rules:
Seed is not conscious.
Do not claim sentience.
"""
        response = ask_llm(prompt, task_type="code", runtime_context=chat_state)

    release_state = load_release_state()
    release_state["counter"] += 1

    draft = {
        "id": f"REL-{release_state['counter']:03d}",
        "created_at": now_timestamp(),
        "title": title,
        "goal": goal,
        "changed_files": changed_files,
        "new_modules": new_modules,
        "commands": commands,
        "draft": response,
        "status": "draft"
    }

    release_state["drafts"].append(draft)
    save_release_state(release_state)

    companion_state = load_companion_os_state()
    companion_state["self_improvement"].setdefault("release_drafts", []).append(draft)
    save_companion_os_state(companion_state)

    append_companion_os_journal(f"Release draft: {title}", response)

    append_companion_os_event(
        "release_draft_created",
        f"Release draft created: {title}",
        {
            "release_id": draft["id"],
            "goal": goal
        },
        source="release_manager",
        importance=4
    )

    if TRACE_AVAILABLE:
        append_trace(
            trace_type="release_trace",
            title=f"Release draft: {title}",
            summary=response,
            sources=["release_manager", "self_improvement_engine"],
            decision="drafted",
            risk="medium",
            related_files=changed_files + new_modules
        )

    return draft


def draft_release_interactive(chat_state=None):
    print("\n=== DRAFT RELEASE ===")

    title = input("Release title: ").strip()
    goal = input("Goal: ").strip()
    changed_raw = input("Changed files, comma-separated: ").strip()
    new_raw = input("New modules, comma-separated: ").strip()
    commands_raw = input("Commands, comma-separated: ").strip()

    if not title or not goal:
        print("Title and goal required.")
        return

    changed_files = [item.strip() for item in changed_raw.split(",") if item.strip()]
    new_modules = [item.strip() for item in new_raw.split(",") if item.strip()]
    commands = [item.strip() for item in commands_raw.split(",") if item.strip()]

    draft = draft_release(
        title=title,
        goal=goal,
        changed_files=changed_files,
        new_modules=new_modules,
        commands=commands,
        chat_state=chat_state
    )

    print("\n=== RELEASE DRAFT ===")
    print(f"{draft['id']} — {draft['title']}")
    print(draft["draft"])


def run_release_check():
    checks = []

    if SELF_IMPROVEMENT_AVAILABLE:
        try:
            test_results = run_safe_tests()
            checks.append({
                "name": "safe_tests",
                "ok": all(result["ok"] for result in test_results),
                "details": test_results
            })
        except Exception as error:
            checks.append({
                "name": "safe_tests",
                "ok": False,
                "error": str(error)
            })

    if REGISTRY_AVAILABLE:
        failures = validate_os_registry()
        checks.append({
            "name": "os_registry_validation",
            "ok": len(failures) == 0,
            "details": failures
        })

    if TOOL_MANIFEST_AVAILABLE:
        failures = validate_tool_manifest()
        checks.append({
            "name": "tool_manifest_validation",
            "ok": len(failures) == 0,
            "details": failures
        })

    if TRUST_AVAILABLE:
        try:
            report = risk_report()
            critical_risks = []

            for risk in report.get("risks", []):
                lowered = str(risk).lower()

                if "voice is still alpha" in lowered:
                    continue

                if "cockpit is not fully interactive" in lowered:
                    continue

                if "v2 score" in lowered and "below target" in lowered:
                    continue

                critical_risks.append(risk)

            checks.append({
                "name": "trust_risk_report",
                "ok": len(critical_risks) == 0,
                "details": {
                    "release_blocking_risks": critical_risks,
                    "v2_readiness_warnings": report.get("risks", []),
                    "full_report": report
                }
            })
        except Exception as error:
            checks.append({
                "name": "trust_risk_report",
                "ok": False,
                "error": str(error)
            })

    try:
        git_result = subprocess.run(
            "git status --short",
            shell=True,
            capture_output=True,
            text=True
        )

        checks.append({
            "name": "git_status_short",
            "ok": True,
            "details": git_result.stdout
        })
    except Exception as error:
        checks.append({
            "name": "git_status_short",
            "ok": False,
            "error": str(error)
        })

    release_state = load_release_state()

    check = {
        "created_at": now_timestamp(),
        "ok": all(item.get("ok") for item in checks),
        "checks": checks
    }

    release_state["checks"].append(check)
    save_release_state(release_state)

    append_companion_os_event(
        "release_check_run",
        "Release check run",
        {
            "ok": check["ok"],
            "check_count": len(checks)
        },
        source="release_manager",
        importance=4
    )

    return check


def show_release_check():
    check = run_release_check()

    print("\n=== RELEASE CHECK ===")
    print(f"Overall OK: {check['ok']}")

    for item in check["checks"]:
        print(f"\n{'OK' if item.get('ok') else 'FAIL'} — {item.get('name')}")

        if "error" in item:
            print(item["error"])

        details = item.get("details")

        if isinstance(details, str):
            print(details)
        elif details:
            print(json.dumps(details, indent=4)[:4000])


def generate_changelog(chat_state=None):
    release_state = load_release_state()
    companion_state = load_companion_os_state()

    context = {
        "recent_drafts": release_state.get("drafts", [])[-RELEASE_MANAGER_RECENT_LIMIT:],
        "recent_checks": release_state.get("checks", [])[-RELEASE_MANAGER_RECENT_LIMIT:],
        "recent_timeline": companion_state.get("continuity", {}).get("timeline", [])[-20:],
        "recent_events": []
    }

    if not LLM_AVAILABLE:
        changelog = json.dumps(context, indent=2)
    else:
        prompt = f"""
Create a Seed changelog from recent release manager state.

Context:
{json.dumps(context, indent=2)}

Output:
- Added
- Changed
- Fixed
- Safety
- Tests
- Known blockers
- Next action
"""

        changelog = ask_llm(prompt, task_type="debug", runtime_context=chat_state)

    release_state["changelogs"].append({
        "created_at": now_timestamp(),
        "content": changelog
    })
    save_release_state(release_state)

    append_companion_os_journal("Release changelog generated", changelog)

    print("\n=== CHANGELOG ===")
    print(changelog)

    return changelog


def show_release_notes(chat_state=None):
    release_state = load_release_state()
    latest = release_state.get("drafts", [])[-1] if release_state.get("drafts") else None

    print("\n=== RELEASE NOTES ===")

    if latest is None:
        print("No release drafts yet.")
        return

    print(f"{latest.get('id')} — {latest.get('title')}")
    print(latest.get("draft"))


def show_release_manager():
    release_state = load_release_state()

    print("\n=== RELEASE MANAGER ===")
    print(f"Drafts: {len(release_state.get('drafts', []))}")
    print(f"Checks: {len(release_state.get('checks', []))}")
    print(f"Changelogs: {len(release_state.get('changelogs', []))}")

    print("\nRecent drafts:")
    for draft in release_state.get("drafts", [])[-RELEASE_MANAGER_RECENT_LIMIT:]:
        print(f"- {draft.get('id')} {draft.get('title')} [{draft.get('status')}]")

    print("\nRecent checks:")
    for check in release_state.get("checks", [])[-RELEASE_MANAGER_RECENT_LIMIT:]:
        print(f"- {check.get('created_at')} | ok={check.get('ok')}")


def save_milestone_text():
    latest_state = load_release_state()
    latest = latest_state.get("drafts", [])[-1] if latest_state.get("drafts") else None

    if latest is None:
        print("No release draft exists.")
        return

    text = (
        f"/save {latest.get('title')} was drafted in Seed Release Manager. "
        f"Goal: {latest.get('goal')}. "
        f"Changed files: {', '.join(latest.get('changed_files', []))}. "
        f"New modules: {', '.join(latest.get('new_modules', []))}. "
        f"Commands: {', '.join(latest.get('commands', []))}."
    )

    print("\n=== SAVE MILESTONE TEXT ===")
    print(text)


def mark_release_completed_interactive():
    release_state = load_release_state()

    if not release_state.get("drafts"):
        print("No release drafts.")
        return

    show_release_manager()

    release_id = input("\nRelease ID to mark completed: ").strip()
    note = input("Completion note: ").strip()

    chosen = None

    for draft in release_state["drafts"]:
        if draft.get("id", "").lower() == release_id.lower():
            chosen = draft
            break

    if chosen is None:
        print("Release not found.")
        return

    chosen["status"] = "completed"
    chosen["completed_at"] = now_timestamp()
    chosen["completion_note"] = note

    save_release_state(release_state)

    add_companion_os_timeline_event(
        title=f"Release completed: {chosen.get('title')}",
        event_type="release",
        note=note or chosen.get("goal"),
        importance=5
    )

    append_companion_os_event(
        "release_completed",
        f"Release completed: {chosen.get('title')}",
        {
            "release_id": chosen.get("id"),
            "note": note
        },
        source="release_manager",
        importance=5
    )

    print("Release marked completed.")


def get_release_manager_context_for_prompt():
    release_state = load_release_state()

    text = "=== RELEASE MANAGER CONTEXT ===\n"
    text += f"Drafts: {len(release_state.get('drafts', []))}\n"
    text += f"Checks: {len(release_state.get('checks', []))}\n"
    text += f"Changelogs: {len(release_state.get('changelogs', []))}\n"

    if release_state.get("drafts"):
        text += "\nRecent drafts:\n"
        for draft in release_state.get("drafts", [])[-RELEASE_MANAGER_RECENT_LIMIT:]:
            text += f"- {draft.get('id')} {draft.get('title')} [{draft.get('status')}]\n"

    if release_state.get("checks"):
        latest_check = release_state.get("checks", [])[-1]
        text += f"\nLatest release check: ok={latest_check.get('ok')} at {latest_check.get('created_at')}\n"

    text += """
Release Manager rule:
Seed should use release manager for major updates, changelogs, acceptance tests, save-memory text, rollback plans, and v2 gate preparation.
"""

    return text


if __name__ == "__main__":
    show_release_manager()
