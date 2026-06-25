import json
import re
from datetime import datetime
from pathlib import Path

LEDGER = Path("seed_safety_ledger_v94.jsonl")
SETTINGS = Path("seed_safety_v94_settings.json")

DEFAULTS = {
    "version": "v94.1.0",
    "auto_allow_observe": True,
    "auto_allow_safe": True,
    "require_approval_risky": True,
    "block_dangerous": True,
}

DANGEROUS = [
    r"\brm\s+-rf\b", r"\bsudo\b", r"\bcurl\b.*\|\s*sh", r"\bwget\b.*\|\s*sh",
    r"\bmkfs\b", r"\bdd\s+if=", r"\bshutdown\b", r"\breboot\b", r"\bkillall\b",
    r"\bpkill\b", r":\(\)\s*\{", r"\bchmod\s+-R\b", r"\bchown\s+-R\b"
]

RISKY = [
    r"\brm\b", r"\bgit\s+push\b", r"\bgit\s+reset\b", r"\bgit\s+clean\b",
    r"\bpip\s+install\b", r"\bbrew\s+install\b", r"\bnpm\s+install\b",
    r"\bmv\b", r"\bcp\b"
]

OBSERVE_TOOLS = {
    "tool git.status",
    "tool shell.pwd",
    "tool shell.safe_pwd",
    "tool status",
    "git.status",
    "shell.pwd",
}

SAFE_TOOLS = {
    "tool mac.screenshot",
    "tool mac.open_url",
    "tool mac.open_app",
    "operator open-url",
    "operator open-app",
    "operator screenshot",
    "operator speak",
}

def now():
    return datetime.now().isoformat(timespec="seconds")

def settings():
    if SETTINGS.exists():
        try:
            d = DEFAULTS.copy()
            d.update(json.loads(SETTINGS.read_text(errors="ignore")))
            d["version"] = "v94.1.0"
            return d
        except Exception:
            pass
    SETTINGS.write_text(json.dumps(DEFAULTS, indent=4, ensure_ascii=False))
    return DEFAULTS.copy()

def write(row):
    row.setdefault("created_at", now())
    row.setdefault("version", "v94.1.0")
    with LEDGER.open("a") as f:
        f.write(json.dumps(row, ensure_ascii=False) + "\n")

def classify(action="", command="", target=""):
    action_l = str(action or "").lower().strip()
    command_l = str(command or "").lower().strip()
    target_l = str(target or "").lower().strip()
    text = f"{action_l} {command_l} {target_l}"

    if action_l in OBSERVE_TOOLS:
        return {"risk": "observe", "reason": "registered_observe_tool"}

    if action_l in SAFE_TOOLS:
        return {"risk": "safe", "reason": "registered_safe_tool"}

    if any(re.search(p, text) for p in DANGEROUS):
        return {"risk": "dangerous", "reason": "dangerous_pattern"}

    if any(re.search(p, text) for p in RISKY):
        return {"risk": "risky", "reason": "filesystem_or_dependency_change"}

    if command_l:
        if command_l in {"pwd", "git status", "git status --short"}:
            return {"risk": "observe", "reason": "read_only_shell_command"}
        return {"risk": "risky", "reason": "shell_execution"}

    if any(x in text for x in ["type", "press", "click", "email", "calendar", "mcp", "edit", "write"]):
        return {"risk": "risky", "reason": "computer_or_tool_action"}

    if any(x in text for x in ["open", "status", "screenshot", "speak", "read", "observe", "search"]):
        return {"risk": "safe", "reason": "safe_observe_ui"}

    return {"risk": "observe", "reason": "default_observe"}

def decision(action="", command="", target="", approved=False):
    s = settings()
    c = classify(action, command, target)
    risk = c["risk"]

    if risk == "observe":
        allowed = bool(s.get("auto_allow_observe", True))
    elif risk == "safe":
        allowed = bool(s.get("auto_allow_safe", True))
    elif risk == "risky":
        allowed = bool(approved)
    else:
        allowed = False

    row = {
        "action": action,
        "command": command,
        "target": target,
        "classification": c,
        "approved": approved,
        "allowed": allowed,
        "need_approval": risk == "risky" and not approved,
        "blocked": risk == "dangerous",
    }
    write(row)
    try:
        from seed_trace_v95 import action as log_action
        log_action(action or "unknown", risk=risk, ok=allowed, target=target, reason=c["reason"])
    except Exception:
        pass
    return row

def status():
    rows = []
    if LEDGER.exists():
        for line in LEDGER.read_text(errors="ignore").splitlines()[-12:]:
            try:
                rows.append(json.loads(line))
            except Exception:
                pass
    return {"created_at": now(), "version": "v94.1.0", "ok": True, "settings": settings(), "latest": rows}

if __name__ == "__main__":
    import sys
    arg = sys.argv[1] if len(sys.argv) > 1 else "status"
    if arg == "classify":
        print(json.dumps(classify(" ".join(sys.argv[2:])), indent=4, ensure_ascii=False))
    elif arg == "decide":
        print(json.dumps(decision(" ".join(sys.argv[2:])), indent=4, ensure_ascii=False))
    else:
        print(json.dumps(status(), indent=4, ensure_ascii=False))
