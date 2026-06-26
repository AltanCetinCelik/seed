import json, os, signal, subprocess, sys, time
from pathlib import Path
from datetime import datetime

VERSION = "v136.2.3"
PID = Path("seed_approval_autopilot_v13623.pid")
LOG = Path("seed_approval_autopilot_v13623.log")
EVENTS = Path("seed_approval_autopilot_v13623_events.jsonl")
SETTINGS = Path("seed_approval_autopilot_v13623_settings.json")

DEFAULT = {"version": VERSION, "enabled": True, "interval_seconds": 5, "apply": True}

def now():
    return datetime.now().isoformat(timespec="seconds")

def settings():
    if SETTINGS.exists():
        try:
            obj=json.loads(SETTINGS.read_text(errors="ignore"))
            if isinstance(obj,dict):
                base=DEFAULT.copy(); base.update(obj); base["version"]=VERSION; return base
        except Exception: pass
    SETTINGS.write_text(json.dumps(DEFAULT, indent=4, ensure_ascii=False))
    return DEFAULT.copy()

def event(row):
    row.setdefault("created_at", now())
    row.setdefault("version", VERSION)
    with EVENTS.open("a") as f:
        f.write(json.dumps(row, ensure_ascii=False)+"\n")
    return row

def alive(pid):
    try:
        os.kill(int(pid),0); return True
    except Exception: return False

def resolve_once(apply=True):
    import seed_approval_resolver_v13623 as resolver
    import seed_autonomy_policy_v13622 as policy
    st = resolver.effective_status()
    actions = []
    for item in st.get("effective_pending", []):
        dec = policy.decision_for(item)
        request_id = resolver.rid(item)
        row = {"request_id": request_id, "item": item, "decision": dec, "applied": False}
        if dec.get("decision") == "auto_reject":
            if apply:
                row["result"] = resolver.apply_reject_and_suppress(request_id)
                row["applied"] = bool(row["result"].get("ok"))
            actions.append(row)
        elif dec.get("decision") == "auto_approve":
            if apply:
                row["result"] = resolver.apply_approve(request_id)
                row["applied"] = bool(row["result"].get("ok"))
            actions.append(row)
        else:
            actions.append(row)
    # Also catch the stale-empty request even if policy was not loaded/matched.
    stale = resolver.repair_stale(apply=apply)
    for a in stale.get("actions", []):
        if not any(x.get("request_id") == a.get("request_id") for x in actions):
            actions.append({"request_id": a.get("request_id"), "decision": {"decision": "auto_reject", "reason": "stale_empty_operator_request"}, "result": a, "applied": apply})
    after = resolver.effective_status()
    out = {"created_at": now(), "version": VERSION, "ok": True, "apply": apply, "before": st, "actions": actions, "after": after}
    event({"event":"resolve_once","apply":apply,"action_count":len(actions),"raw_pending_before":st.get("raw_pending_count"),"effective_pending_after":after.get("effective_pending_count"),"actions":actions})
    return out

def daemon():
    event({"event":"daemon_started","pid":os.getpid()})
    while True:
        s=settings()
        if s.get("enabled", True):
            try:
                resolve_once(apply=bool(s.get("apply", True)))
            except Exception as e:
                event({"event":"daemon_error","error":str(e)})
        time.sleep(float(s.get("interval_seconds", 5)))

def start():
    if PID.exists():
        try:
            pid=int(PID.read_text().strip())
            if alive(pid):
                return {"ok":True,"already_running":True,"pid":pid}
        except Exception: pass
    # Stop old v13622 autopilot so it doesn't spam duplicate rejects.
    try:
        import seed_approval_autopilot_v13622 as old
        old.stop()
    except Exception:
        pass
    p=subprocess.Popen([sys.executable,"seed_approval_autopilot_v13623.py","daemon"],stdout=LOG.open("a"),stderr=LOG.open("a"))
    PID.write_text(str(p.pid))
    return {"ok":True,"pid":p.pid}

def stop():
    pid=None; stopped=False
    if PID.exists():
        try:
            pid=int(PID.read_text().strip())
            if alive(pid): os.kill(pid,signal.SIGTERM); stopped=True
            PID.unlink(missing_ok=True)
        except Exception: pass
    event({"event":"daemon_stopped","pid":pid,"stopped":stopped})
    return {"ok":True,"stopped":stopped,"pid":pid}

def status():
    pid=None; al=False
    if PID.exists():
        try: pid=int(PID.read_text().strip()); al=alive(pid)
        except Exception: pass
    recent=[]
    if EVENTS.exists():
        for line in EVENTS.read_text(errors="ignore").splitlines()[-10:]:
            try: recent.append(json.loads(line))
            except Exception: pass
    import seed_approval_resolver_v13623 as resolver
    return {"created_at":now(),"version":VERSION,"ok":True,"alive":al,"pid":pid,"settings":settings(),"effective_approval_status":resolver.effective_status(),"recent_events":recent}

def test():
    return {"ok": True, "dry_run": resolve_once(False), "status": status()}

if __name__=="__main__":
    cmd=sys.argv[1] if len(sys.argv)>1 else "status"
    if cmd=="daemon": daemon()
    elif cmd=="start": print(json.dumps(start(),indent=4,ensure_ascii=False))
    elif cmd=="stop": print(json.dumps(stop(),indent=4,ensure_ascii=False))
    elif cmd in {"once","apply"}: print(json.dumps(resolve_once(True),indent=4,ensure_ascii=False))
    elif cmd in {"dry-run","preview"}: print(json.dumps(resolve_once(False),indent=4,ensure_ascii=False))
    elif cmd=="test": print(json.dumps(test(),indent=4,ensure_ascii=False))
    else: print(json.dumps(status(),indent=4,ensure_ascii=False))
