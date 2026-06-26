import json, sys, re, time
from pathlib import Path
from datetime import datetime, timedelta

VERSION = "v136.2.2"
SETTINGS = Path("seed_autonomy_policy_v13622_settings.json")
GRANTS = Path("seed_autonomy_policy_v13622_grants.json")
DECISIONS = Path("seed_autonomy_policy_v13622_decisions.jsonl")

DEFAULT_SETTINGS = {
    "version": VERSION,
    "mode": "trusted_local",
    "description": "Less approval friction while keeping hard safety boundaries.",
    "auto_approve_low_risk": True,
    "auto_approve_readonly_tools": True,
    "auto_approve_operator_type": True,
    "auto_approve_operator_key": True,
    "auto_approve_operator_click": False,
    "auto_reject_stale_empty_risky": True,
    "stale_after_minutes": 90,
    "session_grant_minutes": 120,
    "never_auto_approve_keywords": [
        "rm -rf", "sudo ", "passwd", "password", "token", "api key", "secret",
        "delete ", "trash ", "erase", "format", "wipe", "factory reset",
        "send_email", "send email", "gmail send", "payment", "purchase", "buy ",
        "curl ", "wget ", "| sh", "chmod 777", "chown ", "ssh-key", "private key",
        "killall", "pkill", "launchctl unload", "security find", "keychain"
    ],
    "readonly_tool_actions": [
        "tool git.status", "tool shell.pwd", "tool ls", "tool list", "tool status",
        "status", "read", "inspect", "observe", "scan"
    ],
    "trusted_operator_actions": [
        "operator type", "operator key", "operator hotkey", "operator paste"
    ],
    "manual_operator_actions": [
        "operator click", "operator drag", "operator scroll"
    ]
}

def now():
    return datetime.now().isoformat(timespec="seconds")

def load_json(path, fallback):
    if path.exists():
        try:
            obj = json.loads(path.read_text(errors="ignore"))
            if isinstance(obj, dict):
                base = fallback.copy()
                base.update(obj)
                base["version"] = VERSION
                return base
        except Exception:
            pass
    path.write_text(json.dumps(fallback, indent=4, ensure_ascii=False))
    return fallback.copy()

def settings():
    return load_json(SETTINGS, DEFAULT_SETTINGS)

def save_settings(s):
    s["version"] = VERSION
    SETTINGS.write_text(json.dumps(s, indent=4, ensure_ascii=False))
    return s

def grants():
    if GRANTS.exists():
        try:
            obj = json.loads(GRANTS.read_text(errors="ignore"))
            if isinstance(obj, dict):
                return obj
        except Exception:
            pass
    obj = {"version": VERSION, "created_at": now(), "grants": []}
    GRANTS.write_text(json.dumps(obj, indent=4, ensure_ascii=False))
    return obj

def save_grants(g):
    g["version"] = VERSION
    g["updated_at"] = now()
    GRANTS.write_text(json.dumps(g, indent=4, ensure_ascii=False))
    return g

def log_decision(row):
    row.setdefault("created_at", now())
    row.setdefault("version", VERSION)
    with DECISIONS.open("a") as f:
        f.write(json.dumps(row, ensure_ascii=False) + "\n")
    return row

def parse_dt(s):
    try:
        return datetime.fromisoformat(str(s).replace("Z", "+00:00").replace("+00:00",""))
    except Exception:
        return None

def age_minutes(item):
    d = parse_dt(item.get("created_at") if isinstance(item, dict) else None)
    if not d:
        return None
    return (datetime.now() - d).total_seconds() / 60.0

def item_text(item):
    if not isinstance(item, dict):
        return str(item).lower()
    parts = []
    for k in ["action", "command", "target", "tool", "name", "reason"]:
        v = item.get(k)
        if v is not None:
            parts.append(str(v))
    parts.append(json.dumps(item, ensure_ascii=False))
    return " ".join(parts).lower()

def has_deny_keyword(text, s=None):
    s = s or settings()
    hits = []
    for kw in s.get("never_auto_approve_keywords", []):
        if kw.lower() in text:
            hits.append(kw)
    return hits

def grant(pattern, minutes=None):
    s = settings()
    minutes = int(minutes or s.get("session_grant_minutes", 120))
    expires = datetime.now() + timedelta(minutes=minutes)
    g = grants()
    g["grants"].append({
        "pattern": pattern.lower(),
        "created_at": now(),
        "expires_at": expires.isoformat(timespec="seconds"),
        "version": VERSION
    })
    save_grants(g)
    return {"ok": True, "pattern": pattern, "minutes": minutes, "expires_at": expires.isoformat(timespec="seconds")}

def active_grants():
    g = grants()
    out = []
    changed = False
    for gr in g.get("grants", []):
        exp = parse_dt(gr.get("expires_at"))
        if exp and exp > datetime.now():
            out.append(gr)
        else:
            changed = True
    if changed:
        g["grants"] = out
        save_grants(g)
    return out

def grant_matches(text):
    hits = []
    for gr in active_grants():
        p = gr.get("pattern", "").lower()
        if p and p in text:
            hits.append(gr)
    return hits

def set_mode(mode):
    if mode not in {"strict", "balanced", "trusted_local", "operator_light"}:
        return {"ok": False, "error": "mode must be strict, balanced, trusted_local, or operator_light"}
    s = settings()
    s["mode"] = mode
    if mode == "strict":
        s["auto_approve_operator_type"] = False
        s["auto_approve_operator_key"] = False
        s["auto_approve_operator_click"] = False
    elif mode == "balanced":
        s["auto_approve_operator_type"] = False
        s["auto_approve_operator_key"] = False
        s["auto_approve_operator_click"] = False
    elif mode == "operator_light":
        s["auto_approve_operator_type"] = True
        s["auto_approve_operator_key"] = True
        s["auto_approve_operator_click"] = False
    elif mode == "trusted_local":
        s["auto_approve_operator_type"] = True
        s["auto_approve_operator_key"] = True
        s["auto_approve_operator_click"] = False
    save_settings(s)
    return {"ok": True, "mode": mode, "settings": s}

def decision_for(item):
    s = settings()
    text = item_text(item)
    action = str(item.get("action", "") if isinstance(item, dict) else "").lower()
    command = str(item.get("command", "") if isinstance(item, dict) else "")
    target = str(item.get("target", "") if isinstance(item, dict) else "")
    deny_hits = has_deny_keyword(text, s)
    if deny_hits:
        dec = {
            "ok": True, "decision": "manual", "allowed": False,
            "reason": "hard_boundary_keyword", "hits": deny_hits,
            "mode": s.get("mode"), "item": item
        }
        log_decision(dec)
        return dec

    age = age_minutes(item) if isinstance(item, dict) else None
    if s.get("auto_reject_stale_empty_risky") and action in {"operator type", "operator click", "operator key", "operator hotkey"}:
        if not command and not target and age is not None and age >= float(s.get("stale_after_minutes", 90)):
            dec = {
                "ok": True, "decision": "auto_reject", "allowed": False,
                "reason": "stale_empty_operator_request", "age_minutes": round(age, 2),
                "mode": s.get("mode"), "item": item
            }
            log_decision(dec)
            return dec

    grant_hits = grant_matches(text)
    if grant_hits:
        dec = {
            "ok": True, "decision": "auto_approve", "allowed": True,
            "reason": "active_session_grant", "grant_hits": grant_hits,
            "mode": s.get("mode"), "item": item
        }
        log_decision(dec)
        return dec

    if s.get("auto_approve_readonly_tools"):
        for prefix in s.get("readonly_tool_actions", []):
            if action.startswith(prefix) or text.startswith(prefix):
                dec = {
                    "ok": True, "decision": "auto_approve", "allowed": True,
                    "reason": "readonly_tool_auto_approved",
                    "mode": s.get("mode"), "item": item
                }
                log_decision(dec)
                return dec

    mode = s.get("mode")
    if mode in {"trusted_local", "operator_light"}:
        if action == "operator type" and s.get("auto_approve_operator_type"):
            dec = {
                "ok": True, "decision": "auto_approve", "allowed": True,
                "reason": "trusted_operator_type",
                "mode": mode, "item": item
            }
            log_decision(dec)
            return dec
        if action in {"operator key", "operator hotkey", "operator paste"} and s.get("auto_approve_operator_key"):
            dec = {
                "ok": True, "decision": "auto_approve", "allowed": True,
                "reason": "trusted_operator_key_or_paste",
                "mode": mode, "item": item
            }
            log_decision(dec)
            return dec
        if action in {"operator click", "operator drag", "operator scroll"} and s.get("auto_approve_operator_click"):
            dec = {
                "ok": True, "decision": "auto_approve", "allowed": True,
                "reason": "trusted_operator_pointer",
                "mode": mode, "item": item
            }
            log_decision(dec)
            return dec

    if action in {"status", "scan", "inspect", "observe"}:
        dec = {
            "ok": True, "decision": "auto_approve", "allowed": True,
            "reason": "low_risk_observe",
            "mode": mode, "item": item
        }
        log_decision(dec)
        return dec

    dec = {
        "ok": True, "decision": "manual", "allowed": False,
        "reason": "not_in_auto_policy",
        "mode": mode, "item": item
    }
    log_decision(dec)
    return dec

def status():
    s = settings()
    return {
        "created_at": now(),
        "version": VERSION,
        "ok": True,
        "mode": s.get("mode"),
        "settings": s,
        "active_grants": active_grants(),
        "policy_summary": {
            "auto_approves": [
                "read-only status/observe tools",
                "operator type/key/paste in trusted_local or operator_light",
                "active session-granted actions"
            ],
            "never_auto_approves": s.get("never_auto_approve_keywords", []),
            "manual_by_default": [
                "delete/trash/destructive shell",
                "secrets/password/token/keychain actions",
                "email/send/payment/purchase actions",
                "pointer click/drag unless explicitly enabled"
            ]
        }
    }

def test():
    samples = [
        {"action": "tool git.status", "command": "", "target": "", "created_at": now()},
        {"action": "operator type", "command": "hello", "target": "notes", "created_at": now()},
        {"action": "operator type", "command": "", "target": "", "created_at": "2020-01-01T00:00:00"},
        {"action": "tool shell.run", "command": "rm -rf ~/Desktop", "target": "", "created_at": now()},
    ]
    return {"ok": True, "version": VERSION, "decisions": [decision_for(x) for x in samples]}

if __name__ == "__main__":
    cmd = sys.argv[1] if len(sys.argv) > 1 else "status"
    if cmd == "mode":
        print(json.dumps(set_mode(sys.argv[2] if len(sys.argv) > 2 else "trusted_local"), indent=4, ensure_ascii=False))
    elif cmd == "grant":
        pattern = sys.argv[2] if len(sys.argv) > 2 else "operator type"
        minutes = int(sys.argv[3]) if len(sys.argv) > 3 and sys.argv[3].isdigit() else None
        print(json.dumps(grant(pattern, minutes), indent=4, ensure_ascii=False))
    elif cmd == "decide":
        item = json.loads(" ".join(sys.argv[2:])) if len(sys.argv) > 2 else {"action": "operator type", "command": "", "target": ""}
        print(json.dumps(decision_for(item), indent=4, ensure_ascii=False))
    elif cmd == "test":
        print(json.dumps(test(), indent=4, ensure_ascii=False))
    else:
        print(json.dumps(status(), indent=4, ensure_ascii=False))
