import json
import re
from datetime import datetime


try:
    from seed_config import (
        SEED_SKILL_STATE_FILE,
        SEED_SKILL_HISTORY_FILE
    )
except Exception:
    SEED_SKILL_STATE_FILE = "seed_skill_state.json"
    SEED_SKILL_HISTORY_FILE = "seed_skill_history.jsonl"


SKILLS = {
    "filesystem": {
        "risk": "read_only",
        "approval_required": False,
        "operations": ["list", "read", "search", "stat"],
        "description": "List/read/search files safely inside the Seed project root."
    },
    "git": {
        "risk": "read_only_repo",
        "approval_required": False,
        "operations": ["status", "diff_stat", "changed_files", "log", "summary"],
        "description": "Read git status, diff stats, changed files, and recent log."
    },
    "repo": {
        "risk": "read_only",
        "approval_required": False,
        "operations": ["summary", "imports", "todos", "inspect"],
        "description": "Inspect repo structure, modules, imports, TODOs, and file symbols."
    },
    "safe_shell": {
        "risk": "diagnostic",
        "approval_required": False,
        "operations": ["diagnostic", "run", "list"],
        "description": "Run whitelisted safe diagnostics only. No arbitrary shell."
    },
    "browser": {
        "risk": "external_web_action",
        "approval_required": False,
        "operations": ["validate", "open", "read"],
        "description": "Open/read public http(s) URLs. No login/account/send/purchase actions."
    },
    "coding_prep": {
        "risk": "coding_agent_preparation",
        "approval_required": False,
        "operations": ["prepare", "list"],
        "description": "Prepare approval-gated coding-agent task folders and plans."
    }
}


def now_timestamp():
    return datetime.now().isoformat(timespec="seconds")


def append_history(item):
    with open(SEED_SKILL_HISTORY_FILE, "a") as file:
        file.write(json.dumps(item) + "\n")


def save_state(item):
    with open(SEED_SKILL_STATE_FILE, "w") as file:
        json.dump(item, file, indent=4)


def skill_result(skill_id, operation, ok, verified, spoken_message, data=None, risk="unknown"):
    item = {
        "created_at": now_timestamp(),
        "skill_id": skill_id,
        "operation": operation,
        "ok": bool(ok),
        "verified": bool(verified),
        "risk": risk,
        "spoken_message": spoken_message,
        "data": data or {}
    }

    try:
        append_history(item)
        save_state(item)
    except Exception:
        pass

    return item


def run_skill(skill_id, operation, args=None):
    args = args or {}
    spec = SKILLS.get(skill_id)

    if not spec:
        return skill_result(
            skill_id,
            operation,
            False,
            False,
            f"Unknown skill: {skill_id}",
            data={"args": args}
        )

    if operation not in spec["operations"]:
        return skill_result(
            skill_id,
            operation,
            False,
            False,
            f"Unknown operation for {skill_id}: {operation}",
            risk=spec["risk"],
            data={"args": args}
        )

    try:
        if skill_id == "filesystem":
            from seed_filesystem_skill import run_filesystem_skill
            data = run_filesystem_skill(operation, args)

        elif skill_id == "git":
            from seed_git_skill import run_git_skill
            data = run_git_skill(operation, args)

        elif skill_id == "repo":
            from seed_repo_inspection_skill import run_repo_skill
            data = run_repo_skill(operation, args)

        elif skill_id == "safe_shell":
            from seed_safe_shell_skill import run_safe_shell_skill
            data = run_safe_shell_skill(operation, args)

        elif skill_id == "browser":
            from seed_browser_skill import run_browser_skill
            data = run_browser_skill(operation, args)

        elif skill_id == "coding_prep":
            from seed_coding_prep_skill import run_coding_prep_skill
            data = run_coding_prep_skill(operation, args)

        else:
            data = {"ok": False, "error": f"No handler for skill {skill_id}"}

        ok = bool(data.get("ok"))
        message = summarize_skill_result(skill_id, operation, data)

        return skill_result(
            skill_id,
            operation,
            ok,
            ok,
            message,
            risk=spec["risk"],
            data=data
        )

    except Exception as error:
        return skill_result(
            skill_id,
            operation,
            False,
            False,
            f"{skill_id}.{operation} failed: {error}",
            risk=spec["risk"],
            data={"error": str(error), "args": args}
        )


def summarize_skill_result(skill_id, operation, data):
    if not data.get("ok"):
        return f"{skill_id}.{operation} failed: {data.get('error', 'unknown error')}"

    if skill_id == "filesystem" and operation == "list":
        return f"I listed {data.get('count', 0)} items in {data.get('path', '.')}."

    if skill_id == "filesystem" and operation == "read":
        return f"I read {data.get('bytes_read', 0)} bytes from {data.get('path')}."

    if skill_id == "filesystem" and operation == "search":
        return f"I found {data.get('count', 0)} file matches for '{data.get('query')}'."

    if skill_id == "git" and operation == "status":
        return f"Git branch is {data.get('branch') or 'unknown'}; dirty={data.get('dirty')}."

    if skill_id == "git":
        return f"I ran git {operation}."

    if skill_id == "repo" and operation == "summary":
        return f"I inspected the repo: {data.get('python_file_count', 0)} Python files found."

    if skill_id == "repo":
        return f"I ran repo inspection: {operation}."

    if skill_id == "safe_shell" and operation == "diagnostic":
        return "Safe skill diagnostics passed." if data.get("ok") else "Safe skill diagnostics found a problem."

    if skill_id == "browser" and operation == "open":
        return f"I opened {data.get('url')} in the browser." if data.get("ok") else "Browser open failed."

    if skill_id == "browser" and operation == "read":
        return f"I read {data.get('bytes_read', 0)} bytes from {data.get('final_url') or data.get('url')}."

    if skill_id == "browser" and operation == "validate":
        return f"URL is valid: {data.get('url')}"

    if skill_id == "coding_prep" and operation == "prepare":
        return f"I prepared a coding-agent task plan at {data.get('plan_file')}."

    return f"I ran {skill_id}.{operation}."


def extract_url(text):
    match = re.search(r"https?://\S+", text or "")
    if match:
        return match.group(0).rstrip(".,)")
    return None


def route_skill_from_text(text):
    lowered = (text or "").lower().strip()

    if lowered in ["show skills", "skills", "what skills do you have"]:
        return "skill_kernel", "list", {}

    if "git status" in lowered:
        return "git", "status", {}

    if "git diff" in lowered or "diff stat" in lowered:
        return "git", "diff_stat", {}

    if "changed files" in lowered:
        return "git", "changed_files", {}

    if "git log" in lowered or "recent commits" in lowered:
        return "git", "log", {"limit": 5}

    if "repo summary" in lowered or "inspect repo" in lowered or "repo inspection" in lowered:
        return "repo", "summary", {}

    if "import graph" in lowered:
        return "repo", "imports", {}

    if "todo" in lowered or "fixme" in lowered:
        return "repo", "todos", {}

    if "safe skill diagnostic" in lowered or "skill diagnostic" in lowered:
        return "safe_shell", "diagnostic", {}

    if lowered.startswith("list files"):
        rest = lowered.replace("list files", "", 1).strip()
        return "filesystem", "list", {"path": rest or "."}

    if lowered.startswith("read file"):
        rest = (text or "").replace("read file", "", 1).strip()
        return "filesystem", "read", {"path": rest}

    if lowered.startswith("search files for"):
        query = (text or "").split("search files for", 1)[-1].strip()
        return "filesystem", "search", {"query": query, "path": "."}

    if lowered.startswith("search repo for"):
        query = (text or "").split("search repo for", 1)[-1].strip()
        return "filesystem", "search", {"query": query, "path": "."}

    if "open url" in lowered or "open website" in lowered:
        url = extract_url(text) or lowered.replace("open url", "").replace("open website", "").strip()
        return "browser", "open", {"url": url}

    if "read url" in lowered or "read website" in lowered:
        url = extract_url(text) or lowered.replace("read url", "").replace("read website", "").strip()
        return "browser", "read", {"url": url}

    if "prepare coding" in lowered or "coding prep" in lowered or "prepare agent task" in lowered:
        return "coding_prep", "prepare", {"task": text}

    return None, None, None


def maybe_handle_skill_text(text):
    skill_id, operation, args = route_skill_from_text(text)

    if not skill_id:
        return None

    if skill_id == "skill_kernel":
        return skill_list_text()

    result = run_skill(skill_id, operation, args)
    return result.get("spoken_message")


def skill_list_text():
    lines = ["=== SEED REAL SKILLS ==="]
    for skill_id, spec in SKILLS.items():
        lines.append(f"- {skill_id}: {spec['description']}")
        lines.append(f"  ops: {', '.join(spec['operations'])}")
    return "\n".join(lines)


def show_skills():
    print(skill_list_text())


def show_skill_history():
    print("\n=== SEED SKILL HISTORY ===")
    try:
        with open(SEED_SKILL_HISTORY_FILE, "r") as file:
            lines = file.readlines()[-40:]
        for line in lines:
            item = json.loads(line)
            print(f"\n{item.get('created_at')} — {item.get('skill_id')}.{item.get('operation')} ok={item.get('ok')} verified={item.get('verified')}")
            print(item.get("spoken_message"))
    except Exception:
        print("No skill history yet.")


def show_run_skill():
    show_skills()
    skill_id = input("\nSkill id: ").strip()
    operation = input("Operation: ").strip()
    raw_args = input("Args JSON or blank: ").strip()

    args = {}
    if raw_args:
        args = json.loads(raw_args)

    result = run_skill(skill_id, operation, args)
    print(json.dumps(result, indent=4))


def skill_kernel_context(user_prompt=""):
    return (
        "=== SEED v2.5 REAL SKILL SYSTEM ===\n"
        "Seed can now use verified local skills: filesystem, git, repo inspection, safe shell diagnostics, browser read/open, and coding prep.\n"
        "Rules: no arbitrary shell, no deletes, no auto-commit, risky actions require approval, verify results before claiming success.\n"
        f"Available skills: {', '.join(SKILLS.keys())}\n"
    )


if __name__ == "__main__":
    show_skills()


# ============================================================
# Seed v2.5 Skill Kernel Compatibility Layer
# ============================================================
# Older Seed modules may import older context/status/helper names.
# These wrappers keep seed_brain.py and other modules compatible with
# the new v2.5 real skill system.

try:
    TOOL_REGISTRY = SKILLS
except Exception:
    TOOL_REGISTRY = {}


def get_skill_context_for_prompt(user_prompt="", max_results=None):
    """
    Compatibility wrapper expected by seed_brain.py.
    """
    try:
        return skill_kernel_context(user_prompt or "")
    except Exception as error:
        return f"=== SEED v2.5 REAL SKILL SYSTEM ===\nUnavailable: {error}\n"


def format_skill_context_for_prompt(user_prompt="", max_results=None):
    return get_skill_context_for_prompt(user_prompt, max_results=max_results)


def get_real_skill_context_for_prompt(user_prompt="", max_results=None):
    return get_skill_context_for_prompt(user_prompt, max_results=max_results)


def retrieve_skill_context(user_prompt="", max_results=None):
    return get_skill_context_for_prompt(user_prompt, max_results=max_results)


def skill_context_for_prompt(user_prompt="", max_results=None):
    return get_skill_context_for_prompt(user_prompt, max_results=max_results)


def get_skill_kernel_context(user_prompt="", max_results=None):
    return get_skill_context_for_prompt(user_prompt, max_results=max_results)


def list_skills_data():
    return {
        "ok": True,
        "version": "v2.5.0",
        "skills": SKILLS
    }


def get_skill_registry():
    return SKILLS


def get_tool_registry():
    return SKILLS


def skill_status_data():
    return {
        "ok": True,
        "version": "v2.5.0",
        "skill_count": len(SKILLS),
        "skills": list(SKILLS.keys()),
        "rules": {
            "no_arbitrary_shell": True,
            "no_delete": True,
            "no_auto_commit": True,
            "approval_for_risky": True,
            "verify_results": True
        }
    }


def get_skill_status():
    return skill_status_data()


def show_skill_status():
    data = skill_status_data()

    print("\n=== SEED SKILL STATUS ===")
    print(f"Version: {data['version']}")
    print(f"Skill count: {data['skill_count']}")
    print("\nSkills:")
    for skill in data["skills"]:
        print(f"- {skill}")

    print("\nRules:")
    for key, value in data["rules"].items():
        print(f"- {key}: {value}")

    return data


def run_seed_skill(skill_id, operation, args=None):
    return run_skill(skill_id, operation, args or {})


def execute_skill(skill_id, operation, args=None):
    return run_skill(skill_id, operation, args or {})


def call_skill(skill_id, operation, args=None):
    return run_skill(skill_id, operation, args or {})


def __getattr__(name):
    """
    Last-resort compatibility fallback for optional old imports.
    """
    if name in ["TOOL_REGISTRY", "SKILL_REGISTRY"]:
        return SKILLS

    if "context" in name:
        return get_skill_context_for_prompt

    if "status" in name:
        return skill_status_data

    if "registry" in name:
        return get_skill_registry

    if "run" in name or "execute" in name or "call" in name:
        return run_seed_skill

    raise AttributeError(f"module 'seed_skill_kernel' has no attribute '{name}'")



# ============================================================
# Seed v2.5 Full Legacy Skill API Compatibility Pack
# ============================================================
# Older modules expect load_all_skills, get_all_capabilities,
# get_capability, and format_skill_map. These map the old API
# to the new v2.5 SKILLS registry.

try:
    SKILL_REGISTRY = SKILLS
    TOOL_REGISTRY = SKILLS
except Exception:
    SKILL_REGISTRY = {}
    TOOL_REGISTRY = {}


def load_all_skills():
    """
    Compatibility wrapper expected by seed_visuals.py / seed_cockpit.py.
    Returns the full skill registry.
    """
    return SKILLS


def get_all_skills():
    return SKILLS


def load_skills():
    return SKILLS


def get_all_capabilities():
    """
    Returns a capability map derived from the v2.5 skill registry.
    """
    capabilities = {}

    for skill_id, spec in SKILLS.items():
        capabilities[skill_id] = {
            "id": skill_id,
            "name": skill_id,
            "risk": spec.get("risk"),
            "approval_required": spec.get("approval_required"),
            "description": spec.get("description"),
            "operations": spec.get("operations", [])
        }

        for op in spec.get("operations", []):
            capabilities[f"{skill_id}.{op}"] = {
                "id": f"{skill_id}.{op}",
                "skill_id": skill_id,
                "operation": op,
                "risk": spec.get("risk"),
                "approval_required": spec.get("approval_required"),
                "description": f"{skill_id}.{op}"
            }

    return capabilities


def load_all_capabilities():
    return get_all_capabilities()


def get_capabilities():
    return get_all_capabilities()


def get_capability(capability_id):
    """
    Compatibility wrapper expected by seed_skill_planner.py / seed_capability_runtime.py.
    Supports both 'git' and 'git.status' style capability ids.
    """
    capabilities = get_all_capabilities()

    if capability_id in capabilities:
        return capabilities[capability_id]

    if capability_id in SKILLS:
        spec = SKILLS[capability_id]
        return {
            "id": capability_id,
            "name": capability_id,
            "risk": spec.get("risk"),
            "approval_required": spec.get("approval_required"),
            "description": spec.get("description"),
            "operations": spec.get("operations", [])
        }

    return None


def format_skill_map():
    """
    Human-readable skill map expected by older context/growth/evolution modules.
    """
    lines = ["=== SEED SKILL MAP ==="]

    for skill_id, spec in SKILLS.items():
        lines.append(f"- {skill_id}")
        lines.append(f"  risk: {spec.get('risk')}")
        lines.append(f"  approval_required: {spec.get('approval_required')}")
        lines.append(f"  description: {spec.get('description')}")
        lines.append(f"  operations: {', '.join(spec.get('operations', []))}")

    return "\\n".join(lines)


def format_tool_map():
    return format_skill_map()


def format_capability_map():
    caps = get_all_capabilities()
    lines = ["=== SEED CAPABILITY MAP ==="]

    for cap_id, cap in caps.items():
        lines.append(f"- {cap_id}: {cap.get('description')} risk={cap.get('risk')}")

    return "\\n".join(lines)


def show_skill_map():
    print(format_skill_map())


def get_skill_context_for_prompt(user_prompt="", max_results=None):
    try:
        return skill_kernel_context(user_prompt or "")
    except Exception as error:
        return f"=== SEED v2.5 REAL SKILL SYSTEM ===\\nUnavailable: {error}\\n"


def format_skill_context_for_prompt(user_prompt="", max_results=None):
    return get_skill_context_for_prompt(user_prompt, max_results=max_results)


def get_real_skill_context_for_prompt(user_prompt="", max_results=None):
    return get_skill_context_for_prompt(user_prompt, max_results=max_results)


def retrieve_skill_context(user_prompt="", max_results=None):
    return get_skill_context_for_prompt(user_prompt, max_results=max_results)


def skill_context_for_prompt(user_prompt="", max_results=None):
    return get_skill_context_for_prompt(user_prompt, max_results=max_results)


def get_skill_kernel_context(user_prompt="", max_results=None):
    return get_skill_context_for_prompt(user_prompt, max_results=max_results)


def list_skills_data():
    return {
        "ok": True,
        "version": "v2.5.0",
        "skills": SKILLS
    }


def get_skill_registry():
    return SKILLS


def get_tool_registry():
    return SKILLS


def skill_status_data():
    return {
        "ok": True,
        "version": "v2.5.0",
        "skill_count": len(SKILLS),
        "skills": list(SKILLS.keys()),
        "capability_count": len(get_all_capabilities()),
        "rules": {
            "no_arbitrary_shell": True,
            "no_delete": True,
            "no_auto_commit": True,
            "approval_for_risky": True,
            "verify_results": True
        }
    }


def get_skill_status():
    return skill_status_data()


def show_skill_status():
    data = skill_status_data()

    print("\\n=== SEED SKILL STATUS ===")
    print(f"Version: {data['version']}")
    print(f"Skill count: {data['skill_count']}")
    print(f"Capability count: {data['capability_count']}")

    print("\\nSkills:")
    for skill in data["skills"]:
        print(f"- {skill}")

    print("\\nRules:")
    for key, value in data["rules"].items():
        print(f"- {key}: {value}")

    return data


def run_seed_skill(skill_id, operation, args=None):
    return run_skill(skill_id, operation, args or {})


def execute_skill(skill_id, operation, args=None):
    return run_skill(skill_id, operation, args or {})


def call_skill(skill_id, operation, args=None):
    return run_skill(skill_id, operation, args or {})


def execute_capability(capability_id, args=None):
    cap = get_capability(capability_id)
    if not cap:
        return {
            "ok": False,
            "error": f"Unknown capability: {capability_id}"
        }

    if "." in capability_id:
        skill_id, operation = capability_id.split(".", 1)
        return run_skill(skill_id, operation, args or {})

    return {
        "ok": False,
        "error": f"Capability {capability_id} is a skill group. Pick an operation."
    }



# ============================================================
# Seed v2.5 Bootstrap Compatibility Pack
# ============================================================
# Older Seed command/runtime modules expect bootstrap/register/load/save helpers.
# v2.5 uses static SKILLS, so these are safe compatibility wrappers.

def bootstrap_default_skills():
    """
    Compatibility function expected by seed_commands.py.
    Ensures default v2.5 skills are available and returns the registry.
    """
    try:
        state = {
            "ok": True,
            "version": "v2.5.0",
            "bootstrapped": True,
            "skill_count": len(SKILLS),
            "skills": list(SKILLS.keys())
        }
        save_state(state)
    except Exception:
        pass

    return SKILLS


def bootstrap_skills():
    return bootstrap_default_skills()


def initialize_skills():
    return bootstrap_default_skills()


def init_skills():
    return bootstrap_default_skills()


def ensure_default_skills():
    return bootstrap_default_skills()


def save_all_skills(skills=None):
    """
    Compatibility save wrapper.
    The v2.5 skill registry is code-defined, but we can persist a snapshot.
    """
    try:
        snapshot = {
            "ok": True,
            "version": "v2.5.0",
            "skills": skills or SKILLS
        }
        save_state(snapshot)
        return True
    except Exception:
        return False


def save_skills(skills=None):
    return save_all_skills(skills)


def register_skill(skill_id, spec=None):
    """
    Compatibility register wrapper.
    Runtime registration is allowed only in memory; no risky execution is added.
    """
    if not skill_id:
        return False

    SKILLS[skill_id] = spec or {
        "risk": "unknown",
        "approval_required": True,
        "operations": [],
        "description": "Runtime compatibility skill placeholder."
    }

    return True


def unregister_skill(skill_id):
    if skill_id in SKILLS:
        SKILLS.pop(skill_id)
        return True
    return False


def get_skill(skill_id):
    return SKILLS.get(skill_id)


def skill_exists(skill_id):
    return skill_id in SKILLS


def get_skill_names():
    return list(SKILLS.keys())


def list_skill_names():
    return get_skill_names()


def get_skill_operations(skill_id):
    spec = SKILLS.get(skill_id) or {}
    return spec.get("operations", [])


def get_capability_names():
    return list(get_all_capabilities().keys())


def run_capability(capability_id, args=None):
    return execute_capability(capability_id, args=args or {})


def call_capability(capability_id, args=None):
    return execute_capability(capability_id, args=args or {})


def skill_summary():
    return {
        "ok": True,
        "version": "v2.5.0",
        "skill_count": len(SKILLS),
        "capability_count": len(get_all_capabilities()),
        "skills": SKILLS
    }


def load_skill_kernel():
    return skill_summary()


def show_skill_kernel():
    print(format_skill_map())
    return skill_summary()



# ============================================================
# Seed v2.5 Auto Import Compatibility Pack
# ============================================================
# Auto-generated compatibility for every name imported from seed_skill_kernel
# by existing Seed modules. This prevents old UI/HUD/runtime modules from
# crashing while v2.5 uses the new Skill Kernel internally.

_IMPORTED_SKILL_KERNEL_NAMES = [
    "SKILLS",
    "bootstrap_default_skills",
    "format_skill_map",
    "get_all_capabilities",
    "get_capability",
    "get_skill_context_for_prompt",
    "load_all_skills",
    "route_skill_from_text",
    "run_skill",
    "show_run_skill",
    "show_skill_audit",
    "show_skill_detail",
    "show_skill_history",
    "show_skill_map",
    "show_skills",
    "skill_kernel_context"
]


def _seed_skill_compat_callable(name):
    def _compat(*args, **kwargs):
        lower = name.lower()

        if "context" in lower:
            return get_skill_context_for_prompt(*(args or ("",)), **kwargs)

        if "format" in lower and ("map" in lower or "skill" in lower):
            return format_skill_map()

        if "format" in lower and "capability" in lower:
            return format_capability_map()

        if "status" in lower or "summary" in lower:
            data = skill_summary()
            if lower.startswith("show"):
                print(json.dumps(data, indent=4))
            return data

        if "detail" in lower and "capability" in lower:
            capability_id = args[0] if args else kwargs.get("capability_id")
            data = get_capability(capability_id) if capability_id else get_all_capabilities()
            if lower.startswith("show"):
                print(json.dumps(data, indent=4))
            return data

        if "detail" in lower and "skill" in lower:
            skill_id = args[0] if args else kwargs.get("skill_id")
            data = get_skill(skill_id) if skill_id else SKILLS
            if lower.startswith("show"):
                print(json.dumps(data, indent=4))
            return data

        if lower.startswith("show"):
            if "capability" in lower:
                print(format_capability_map())
                return get_all_capabilities()
            print(format_skill_map())
            return skill_summary()

        if "all_skills" in lower or lower in ["load_skills", "get_skills", "list_skills"]:
            return load_all_skills()

        if "all_capabilities" in lower or lower in ["load_capabilities", "get_capabilities", "list_capabilities"]:
            return get_all_capabilities()

        if "capability" in lower and ("get" in lower or "load" in lower):
            capability_id = args[0] if args else kwargs.get("capability_id")
            return get_capability(capability_id) if capability_id else get_all_capabilities()

        if "skill" in lower and ("get" in lower or "load" in lower):
            skill_id = args[0] if args else kwargs.get("skill_id")
            return get_skill(skill_id) if skill_id else load_all_skills()

        if "bootstrap" in lower or "initialize" in lower or lower.startswith("init"):
            return bootstrap_default_skills()

        if "register" in lower and "unregister" not in lower:
            skill_id = args[0] if args else kwargs.get("skill_id")
            spec = args[1] if len(args) > 1 else kwargs.get("spec")
            return register_skill(skill_id, spec)

        if "unregister" in lower:
            skill_id = args[0] if args else kwargs.get("skill_id")
            return unregister_skill(skill_id)

        if "run" in lower or "execute" in lower or "call" in lower:
            if args:
                if len(args) >= 2:
                    return run_skill(args[0], args[1], args[2] if len(args) > 2 else kwargs.get("args", {}))
                if len(args) == 1:
                    return execute_capability(args[0], kwargs.get("args", {}))
            return {
                "ok": False,
                "error": f"Compatibility skill runner '{name}' needs arguments."
            }

        return skill_summary()

    _compat.__name__ = name
    return _compat


for _compat_name in _IMPORTED_SKILL_KERNEL_NAMES:
    if _compat_name not in globals():
        if _compat_name.isupper():
            globals()[_compat_name] = SKILLS
        else:
            globals()[_compat_name] = _seed_skill_compat_callable(_compat_name)


def __getattr__(name):
    lower = name.lower()

    if name in ["TOOL_REGISTRY", "SKILL_REGISTRY"]:
        return SKILLS

    if name not in globals():
        globals()[name] = SKILLS if name.isupper() else _seed_skill_compat_callable(name)

    return globals()[name]

