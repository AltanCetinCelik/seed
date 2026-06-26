import json, os, signal, subprocess, sys, time
from pathlib import Path
from datetime import datetime

VERSION = "v136.2.2"
PID = Path("seed_approval_autopilot_v13622.pid")
LOG = Path("seed_approval_autopilot_v13622.log")
EVENTS = Path("seed_approval_autopilot_v13622_events.jsonl")
SETTINGS = Path("seed_approval_autopilot_v13622_settings.json")

DEFAULT = {
    "version": VERSION,
    "enabled": True,
    "interval_seconds": 2,
    "apply": True,
    "max_actions_per_tick": 5,
    "note": "Autopilot auto-resolves only requests allowed by seed_autonomy_policy_v13622."
}

def now():
    return datetime.now().isoformat(timespec="seconds")

def settings():
    if SETTINGS.exists():
        try:
            obj = json.loads(SETTINGS.read_text(errors="ignore"))
            if isinstance(obj, dict):
                base = DEFAULT.copy(); base.update(obj); base["version"] = VERSION; return base
        except Exception:
            pass
    SETTINGS.write_text(json.dumps(DEFAULT, indent=4, ensure_ascii=False))
    return DEFAULT.copy()

def save_settings(s):
    s["version"] = VERSION
    SETTINGS.write_text(json.dumps(s, indent=4, ensure_ascii=False))
    return s

def event(row):
    row.setdefault("created_at", now())
    row.setdefault("version", VERSION)
    with EVENTS.open("a") as f:
        f.write(json.dumps(row, ensure_ascii=False) + "\n")
    return row

def alive(pid):
    try:
        os.kill(int(pid), 0)
        return True
    except Exception:
        return False

def approval_module():
    import seed_action_approval_v107 as app
    return app

def approval_status():
    try:
        app = approval_module()
        st = app.status()
        pending = []
        for key in ["pending", "requests", "items", "approvals"]:
            if isinstance(st.get(key), list):
                pending = st[key]; break
        return {"ok": True, "status": st, "pending": pending, "pending_count": int(st.get("pending_count", len(pending)) or 0)}
    except Exception as e:
        return {"ok": False, "error": str(e), "pending": [], "pending_count": 0}

def approval_id(item):
    if not isinstance(item, dict):
        return None
    for k in ["request_id", "id", "approval_id", "uid"]:
        if item.get(k):
            return str(item.get(k))
    return None

def call_approval(action, request_id=None, reason="seed approval autopilot"):
    try:
        app = approval_module()
    except Exception as e:
        return {"ok": False, "error": str(e)}
    names = ["reject", "deny", "decline", "resolve"] if action == "reject" else ["approve", "allow", "grant"]
    tried = []
    for name in names:
        fn = getattr(app, name, None)
        if not callable(fn):
            continue
        patterns = []
        if request_id:
            patterns.extend([
                ((request_id,), {}),
                ((request_id, reason), {}),
                ((), {"request_id": request_id, "reason": reason}),
                ((), {"approval_id": request_id, "reason": reason}),
                ((), {"id": request_id, "reason": reason}),
            ])
        else:
            patterns.append(((), {}))
        for args, kwargs in patterns:
            try:
                res = fn(*args, **kwargs)
                return {"ok": True, "function": name, "request_id": request_id, "result": res}
            except Exception as e:
                tried.append({"function": name, "args": list(args), "kwargs": kwargs, "error": str(e)})
    return {"ok": False, "error": "no compatible approval function worked", "action": action, "request_id": request_id, "tried": tried}

def resolve_once(apply=True):
    import seed_autonomy_policy_v13622 as policy
    st = approval_status()
    actions = []
    if not st.get("ok"):
        return {"ok": False, "error": st.get("error"), "actions": []}
    for item in st.get("pending", [])[: int(settings().get("max_actions_per_tick", 5))]:
        dec = policy.decision_for(item)
        rid = approval_id(item)
        row = {"request_id": rid, "item": item, "decision": dec, "applied": False}
        if dec.get("decision") == "auto_approve":
            if apply:
                row["result"] = call_approval("approve", rid, "Auto-approved by v136.2.2 autonomy policy: " + dec.get("reason",""))
                row["applied"] = bool(row["result"].get("ok"))
            actions.append(row)
        elif dec.get("decision") == "auto_reject":
            if apply:
                row["result"] = call_approval("reject", rid, "Auto-rejected by v136.2.2 autonomy policy: " + dec.get("reason",""))
                row["applied"] = bool(row["result"].get("ok"))
            actions.append(row)
        else:
            actions.append(row)
    out = {"created_at": now(), "version": VERSION, "ok": True, "apply": apply, "pending_count": st.get("pending_count"), "actions": actions}
    event({"event": "resolve_once", "apply": apply, "action_count": len(actions), "actions": actions})
    return out

def daemon():
    s = settings()
    event({"event": "daemon_started", "pid": os.getpid(), "settings": s})
    while True:
        s = settings()
        if s.get("enabled", True):
            try:
                resolve_once(apply=bool(s.get("apply", True)))
            except Exception as e:
                event({"event": "daemon_error", "error": str(e)})
        time.sleep(float(s.get("interval_seconds", 2)))

def start():
    if PID.exists():
        try:
            pid = int(PID.read_text().strip())
            if alive(pid):
                return {"ok": True, "already_running": True, "pid": pid}
        except Exception:
            pass
    p = subprocess.Popen([sys.executable, "seed_approval_autopilot_v13622.py", "daemon"], stdout=LOG.open("a"), stderr=LOG.open("a"))
    PID.write_text(str(p.pid))
    return {"ok": True, "pid": p.pid}

def stop():
    pid = None; stopped = False
    if PID.exists():
        try:
            pid = int(PID.read_text().strip())
            if alive(pid):
                os.kill(pid, signal.SIGTERM); stopped = True
            PID.unlink(missing_ok=True)
        except Exception:
            pass
    event({"event": "daemon_stopped", "pid": pid, "stopped": stopped})
    return {"ok": True, "stopped": stopped, "pid": pid}

def status():
    pid = None; al = False
    if PID.exists():
        try:
            pid = int(PID.read_text().strip()); al = alive(pid)
        except Exception:
            pass
    recent = []
    if EVENTS.exists():
        for line in EVENTS.read_text(errors="ignore").splitlines()[-10:]:
            try: recent.append(json.loads(line))
            except Exception: pass
    return {
        "created_at": now(),
        "version": VERSION,
        "ok": True,
        "alive": al,
        "pid": pid,
        "settings": settings(),
        "approval_status": approval_status(),
        "recent_events": recent
    }

def set_enabled(v):
    s = settings()
    s["enabled"] = bool(v)
    save_settings(s)
    return {"ok": True, "enabled": s["enabled"]}

def test():
    import seed_autonomy_policy_v13622 as policy
    return {"ok": True, "policy_test": policy.test(), "dry_run": resolve_once(apply=False), "status": status()}

if __name__ == "__main__":
    cmd = sys.argv[1] if len(sys.argv) > 1 else "status"
    if cmd == "daemon":
        daemon()
    elif cmd == "start":
        print(json.dumps(start(), indent=4, ensure_ascii=False))
    elif cmd == "stop":
        print(json.dumps(stop(), indent=4, ensure_ascii=False))
    elif cmd in {"once", "apply"}:
        print(json.dumps(resolve_once(apply=True), indent=4, ensure_ascii=False))
    elif cmd in {"dry-run", "preview"}:
        print(json.dumps(resolve_once(apply=False), indent=4, ensure_ascii=False))
    elif cmd == "enable":
        print(json.dumps(set_enabled(True), indent=4, ensure_ascii=False))
    elif cmd == "disable":
        print(json.dumps(set_enabled(False), indent=4, ensure_ascii=False))
    elif cmd == "test":
        print(json.dumps(test(), indent=4, ensure_ascii=False))
    else:
        print(json.dumps(status(), indent=4, ensure_ascii=False))
