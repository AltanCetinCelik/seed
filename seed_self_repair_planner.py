import json
import subprocess
from datetime import datetime
from pathlib import Path


try:
    from seed_config import SEED_SELF_REPAIR_PLAN_FILE
except Exception:
    SEED_SELF_REPAIR_PLAN_FILE = "seed_self_repair_plan.json"


CORE_IMPORT_MODULES = [
    "seed_skill_kernel",
    "seed_brain",
    "seed_commands",
    "seed_cli",
    "seed_action_kernel",
    "seed_mission_control",
    "seed_release_orchestrator",
    "seed_voice_ux_pack"
]


def now_timestamp():
    return datetime.now().isoformat(timespec="seconds")


def import_probe(module):
    code = f"import {module}; print('OK')"
    result = subprocess.run(["python", "-c", code], capture_output=True, text=True, timeout=15)
    return {
        "module": module,
        "ok": result.returncode == 0,
        "stdout": result.stdout[-1000:],
        "stderr": result.stderr[-2500:]
    }


def build_self_repair_plan():
    probes = [import_probe(module) for module in CORE_IMPORT_MODULES]
    failures = [item for item in probes if not item["ok"]]

    plan = {
        "created_at": now_timestamp(),
        "version": "v2.9.0",
        "ok": len(failures) == 0,
        "plan_only": True,
        "probes": probes,
        "failures": failures,
        "repair_steps": []
    }

    for failure in failures:
        stderr = failure.get("stderr", "")
        module = failure["module"]

        if "ImportError" in stderr and "cannot import name" in stderr:
            plan["repair_steps"].append({
                "module": module,
                "type": "missing_compat_import",
                "suggestion": "Add compatibility wrapper to source module or update old import."
            })
        elif "EOFError" in stderr:
            plan["repair_steps"].append({
                "module": module,
                "type": "import_runs_input_loop",
                "suggestion": "Wrap CLI main() in if __name__ == '__main__'."
            })
        elif "SyntaxError" in stderr:
            plan["repair_steps"].append({
                "module": module,
                "type": "syntax_error",
                "suggestion": "Open traceback line and patch exact syntax."
            })
        else:
            plan["repair_steps"].append({
                "module": module,
                "type": "unknown",
                "suggestion": "Inspect traceback and patch minimal compatibility."
            })

    if not plan["repair_steps"]:
        plan["repair_steps"].append({
            "type": "none",
            "suggestion": "No import repair needed."
        })

    with open(SEED_SELF_REPAIR_PLAN_FILE, "w") as file:
        json.dump(plan, file, indent=4)

    return plan


def self_repair_context(user_prompt=""):
    return (
        "=== SEED SELF-REPAIR PLANNER ===\n"
        "Read-only import probe and repair plan generator. It does not edit files automatically.\n"
        "Use /self-repair-plan when a module import or command breaks.\n"
    )


def show_self_repair_plan():
    plan = build_self_repair_plan()

    print("\n=== SEED SELF-REPAIR PLAN ===")
    print(f"OK: {plan['ok']}")
    print(f"Failures: {len(plan['failures'])}")

    print("\nRepair steps:")
    for step in plan["repair_steps"]:
        print(f"- {step.get('type')}: {step.get('suggestion')}")


if __name__ == "__main__":
    show_self_repair_plan()
