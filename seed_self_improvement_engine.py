import ast
import json
import os
import subprocess
from datetime import datetime


try:
    from seed_config import SELF_IMPROVEMENT_TEST_COMMANDS
except Exception:
    SELF_IMPROVEMENT_TEST_COMMANDS = [
        "python -m py_compile seed_companion_os.py"
    ]


from seed_companion_os import (
    load_companion_os_state,
    save_companion_os_state,
    append_companion_os_event,
    append_companion_os_journal
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
    from seed_microagent_council import run_council
    COUNCIL_AVAILABLE = True
except Exception:
    COUNCIL_AVAILABLE = False


try:
    from seed_code_map import build_code_map, load_code_map
    CODE_MAP_AVAILABLE = True
except Exception:
    CODE_MAP_AVAILABLE = False


try:
    from seed_os_registry import get_os_command_registry
    REGISTRY_AVAILABLE = True
except Exception:
    REGISTRY_AVAILABLE = False


try:
    from seed_tool_manifest_v2 import get_tool_manifest
    TOOL_MANIFEST_AVAILABLE = True
except Exception:
    TOOL_MANIFEST_AVAILABLE = False


IGNORE_DIRS = {
    ".git",
    "__pycache__",
    "seed_logs",
    "seed_edit_backups",
    "third_party_repos",
    ".venv",
    "venv",
    "node_modules",
    "seed_companion_os_backups"
}


def now_timestamp():
    return datetime.now().isoformat(timespec="seconds")


def list_python_files():
    files = []

    for root, folders, file_names in os.walk("."):
        folders[:] = [folder for folder in folders if folder not in IGNORE_DIRS]

        for file_name in file_names:
            if file_name.endswith(".py"):
                path = os.path.join(root, file_name).replace("./", "", 1)
                files.append(path)

    return sorted(files)


def analyze_imports(path):
    try:
        with open(path, "r") as file:
            source = file.read()
        tree = ast.parse(source)
    except Exception as error:
        return {
            "path": path,
            "error": str(error),
            "imports": [],
            "from_imports": [],
            "functions": [],
            "classes": [],
            "line_count": 0
        }

    imports = []
    from_imports = []
    functions = []
    classes = []

    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for alias in node.names:
                imports.append(alias.name)
        elif isinstance(node, ast.ImportFrom):
            module = node.module or ""
            from_imports.append(module)
        elif isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            functions.append(node.name)
        elif isinstance(node, ast.ClassDef):
            classes.append(node.name)

    return {
        "path": path,
        "imports": sorted(set(imports)),
        "from_imports": sorted(set(from_imports)),
        "functions": sorted(set(functions)),
        "classes": sorted(set(classes)),
        "line_count": len(source.splitlines())
    }


def build_dependency_graph():
    files = list_python_files()
    graph = {}

    for path in files:
        graph[path] = analyze_imports(path)

    state = load_companion_os_state()
    state["self_improvement"]["dependency_graph"] = graph
    save_companion_os_state(state)

    append_companion_os_event(
        "dependency_graph_built",
        "Repo dependency graph built",
        {
            "file_count": len(files)
        },
        source="self_improvement_engine",
        importance=4
    )

    if TRACE_AVAILABLE:
        append_trace(
            trace_type="self_edit_trace",
            title="Dependency graph built",
            summary=f"Built dependency graph for {len(files)} Python files.",
            sources=["Aider", "SWE-agent", "mini-SWE-agent"],
            decision="diagnostic",
            risk="low"
        )

    return graph


def show_dependencies():
    graph = build_dependency_graph()

    print("\n=== REPO DEPENDENCY GRAPH ===")

    for path, info in graph.items():
        print(f"\n{path}")

        if "error" in info and info.get("error"):
            print(f"  ERROR: {info.get('error')}")
            continue

        print(f"  Lines: {info.get('line_count')}")
        print(f"  Imports: {', '.join(info.get('imports', [])[:10])}")
        print(f"  From imports: {', '.join(info.get('from_imports', [])[:10])}")
        print(f"  Functions: {len(info.get('functions', []))}")
        print(f"  Classes: {len(info.get('classes', []))}")


def impact_check(target):
    graph = build_dependency_graph()

    target_clean = target.replace(".py", "").replace("./", "")

    impacted = []

    for path, info in graph.items():
        haystack = " ".join(info.get("imports", []) + info.get("from_imports", []))

        if target_clean in haystack or target in haystack:
            impacted.append(path)

    report = {
        "created_at": now_timestamp(),
        "target": target,
        "impacted_files": sorted(set(impacted)),
        "direct_file_exists": os.path.exists(target)
    }

    state = load_companion_os_state()
    state["self_improvement"].setdefault("impact_reports", []).append(report)
    save_companion_os_state(state)

    append_companion_os_event(
        "impact_check_completed",
        f"Impact check: {target}",
        report,
        source="self_improvement_engine",
        importance=4
    )

    return report


def impact_check_interactive():
    target = input("Target file/module: ").strip()

    if target == "":
        print("Target cannot be empty.")
        return

    report = impact_check(target)

    print("\n=== IMPACT CHECK ===")
    print(f"Target: {report['target']}")
    print(f"Direct file exists: {report['direct_file_exists']}")

    if not report["impacted_files"]:
        print("No obvious import dependents found.")
    else:
        print("Potentially impacted files:")
        for path in report["impacted_files"]:
            print(f"- {path}")


def run_safe_tests():
    results = []

    for command in SELF_IMPROVEMENT_TEST_COMMANDS:
        result = subprocess.run(
            command,
            shell=True,
            capture_output=True,
            text=True
        )

        results.append({
            "command": command,
            "returncode": result.returncode,
            "stdout": result.stdout[-2000:],
            "stderr": result.stderr[-2000:],
            "ok": result.returncode == 0
        })

    append_companion_os_event(
        "safe_tests_run",
        "Self-improvement safe tests run",
        {
            "count": len(results),
            "passed": len([result for result in results if result["ok"]])
        },
        source="self_improvement_engine",
        importance=4
    )

    if TRACE_AVAILABLE:
        append_trace(
            trace_type="self_edit_trace",
            title="Safe tests run",
            summary=json.dumps(results, indent=2),
            sources=["SWE-agent", "mini-SWE-agent"],
            decision="tested",
            risk="low"
        )

    return results


def show_safe_tests():
    results = run_safe_tests()

    print("\n=== SAFE TESTS ===")

    for result in results:
        status = "OK" if result["ok"] else "FAIL"
        print(f"\n{status}: {result['command']}")

        if result["stdout"]:
            print("STDOUT:")
            print(result["stdout"])

        if result["stderr"]:
            print("STDERR:")
            print(result["stderr"])


def self_improvement_context(goal=""):
    state = load_companion_os_state()

    context = {
        "goal": goal,
        "mission": state.get("mission"),
        "truth": state.get("truth"),
        "dependency_graph_summary": {
            "file_count": len(state.get("self_improvement", {}).get("dependency_graph", {})),
            "recent_impact_reports": state.get("self_improvement", {}).get("impact_reports", [])[-5:]
        },
        "v2": state.get("v2", {}),
        "repo_dna": state.get("repo_dna", {}),
        "friend_advice_dna": state.get("friend_advice_dna", {})
    }

    if CODE_MAP_AVAILABLE:
        try:
            context["code_map"] = load_code_map()
        except Exception as error:
            context["code_map_error"] = str(error)

    if REGISTRY_AVAILABLE:
        try:
            context["command_registry"] = get_os_command_registry()
        except Exception as error:
            context["command_registry_error"] = str(error)

    if TOOL_MANIFEST_AVAILABLE:
        try:
            context["tool_manifest"] = get_tool_manifest()
        except Exception as error:
            context["tool_manifest_error"] = str(error)

    return context


def upgrade_plan(goal, chat_state=None, create_council=True):
    context = self_improvement_context(goal)

    if create_council and COUNCIL_AVAILABLE:
        try:
            council_response = run_council(
                goal=f"Self-improvement planning: {goal}",
                chat_state=chat_state,
                create_workflow_from_result=False
            )
            context["council_response"] = council_response
        except Exception as error:
            context["council_error"] = str(error)

    if not LLM_AVAILABLE:
        response = json.dumps(context, indent=2)[:6000]
    else:
        prompt = f"""
You are Seed's Repo-Aware Self-Improvement Engine.

Goal:
{goal}

Seed is not alive or conscious.
Seed may inspect, plan, test, and draft.
Seed must not silently edit or apply risky changes.

Use these patterns:
- Aider: repo-aware patch planning
- Cline: approval-gated tool/file actions
- SWE-agent: inspect-plan-test loop
- mini-SWE-agent: minimal understandable loop
- OpenHands: task decomposition
- MCP Servers: capability contracts

Context:
{json.dumps(context, indent=2)}

Output:
1. Meaning
2. Target files
3. New files
4. Dependencies and impact risks
5. Step-by-step implementation plan
6. Approval points
7. Test plan
8. Rollback plan
9. V2 pillar impact
10. What NOT to do
"""

        response = ask_llm(prompt, task_type="code", runtime_context=chat_state)

    state = load_companion_os_state()

    plan = {
        "created_at": now_timestamp(),
        "goal": goal,
        "plan": response
    }

    state["self_improvement"].setdefault("upgrade_plans", []).append(plan)
    save_companion_os_state(state)

    append_companion_os_journal(f"Upgrade plan: {goal}", response)

    if TRACE_AVAILABLE:
        append_trace(
            trace_type="proposal_trace",
            title=f"Upgrade plan: {goal}",
            summary=response,
            sources=["Aider", "Cline", "SWE-agent", "OpenHands"],
            decision="planned",
            risk="medium"
        )

    return response


def upgrade_plan_interactive(chat_state=None):
    goal = input("Upgrade goal: ").strip()

    if goal == "":
        print("Goal cannot be empty.")
        return

    response = upgrade_plan(goal, chat_state=chat_state)

    print("\n=== UPGRADE PLAN ===")
    print(response)


def patch_plan(goal, target_files=None, chat_state=None):
    if target_files is None:
        target_files = []

    context = self_improvement_context(goal)

    for file_path in target_files:
        context.setdefault("impact_checks", []).append(impact_check(file_path))

    if not LLM_AVAILABLE:
        response = json.dumps(context, indent=2)[:6000]
    else:
        prompt = f"""
Create a patch plan for Seed.

Goal:
{goal}

Target files:
{json.dumps(target_files, indent=2)}

Context:
{json.dumps(context, indent=2)}

Rules:
- Do not output full code unless asked later.
- Do not apply edits.
- Include exact files, functions, risks, tests, rollback.
- Preserve existing commands.
- Keep approval gates.

Output:
1. Patch purpose
2. Files to inspect first
3. Files to create/edit
4. Functions/classes likely needed
5. Risks
6. Tests
7. Self-edit prompt outline
"""

        response = ask_llm(prompt, task_type="code", runtime_context=chat_state)

    if TRACE_AVAILABLE:
        append_trace(
            trace_type="self_edit_trace",
            title=f"Patch plan: {goal}",
            summary=response,
            sources=["Aider", "Cline"],
            decision="patch_planned",
            risk="medium",
            related_files=target_files
        )

    return response


def patch_plan_interactive(chat_state=None):
    goal = input("Patch goal: ").strip()
    files_raw = input("Target files, comma-separated: ").strip()

    target_files = [item.strip() for item in files_raw.split(",") if item.strip()]

    if goal == "":
        print("Goal cannot be empty.")
        return

    response = patch_plan(goal, target_files=target_files, chat_state=chat_state)

    print("\n=== PATCH PLAN ===")
    print(response)


def test_plan(goal, chat_state=None):
    context = self_improvement_context(goal)

    if not LLM_AVAILABLE:
        response = "\n".join(SELF_IMPROVEMENT_TEST_COMMANDS)
    else:
        prompt = f"""
Create a Seed test plan.

Goal:
{goal}

Context:
{json.dumps(context, indent=2)}

Output:
- Python compile checks
- import checks
- command checks
- manual chat checks
- safety checks
- rollback checks
"""

        response = ask_llm(prompt, task_type="code", runtime_context=chat_state)

    return response


def test_plan_interactive(chat_state=None):
    goal = input("Test plan goal: ").strip()

    if goal == "":
        print("Goal cannot be empty.")
        return

    response = test_plan(goal, chat_state=chat_state)

    print("\n=== TEST PLAN ===")
    print(response)


def get_self_improvement_context_for_prompt(user_prompt=""):
    state = load_companion_os_state()
    reports = state.get("self_improvement", {}).get("impact_reports", [])[-5:]
    plans = state.get("self_improvement", {}).get("upgrade_plans", [])[-5:]

    text = "=== SELF-IMPROVEMENT ENGINE CONTEXT ===\n"
    text += f"Dependency graph files: {len(state.get('self_improvement', {}).get('dependency_graph', {}))}\n"
    text += f"Recent impact reports: {len(reports)}\n"
    text += f"Recent upgrade plans: {len(plans)}\n"

    if reports:
        text += "\nImpact reports:\n"
        for report in reports:
            text += f"- {report.get('target')}: {len(report.get('impacted_files', []))} impacted files\n"

    if plans:
        text += "\nUpgrade plans:\n"
        for plan in plans:
            text += f"- {plan.get('goal')} ({plan.get('created_at')})\n"

    text += """
Self-improvement rule:
Seed may inspect, plan, draft, and test.
Seed must not silently edit or apply risky changes.
Use existing self-edit approval workflow for actual edits.
"""

    return text


if __name__ == "__main__":
    show_dependencies()
