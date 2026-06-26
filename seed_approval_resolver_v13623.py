import json, os, re, sys, time
from pathlib import Path
from datetime import datetime

VERSION = "v136.2.3"
SUPPRESS = Path("seed_approval_resolver_v13623_suppressed.json")
EVENTS = Path("seed_approval_resolver_v13623_events.jsonl")

def now():
    return datetime.now().isoformat(timespec="seconds")

def event(row):
    row.setdefault("created_at", now())
    row.setdefault("version", VERSION)
    with EVENTS.open("a") as f:
        f.write(json.dumps(row, ensure_ascii=False) + "\n")
    return row

def load_suppressed():
    if SUPPRESS.exists():
        try:
            obj = json.loads(SUPPRESS.read_text(errors="ignore"))
            if isinstance(obj, dict):
                obj.setdefault("version", VERSION)
                obj.setdefault("suppressed", [])
                return obj
        except Exception:
            pass
    obj = {"version": VERSION, "created_at": now(), "suppressed": []}
    SUPPRESS.write_text(json.dumps(obj, indent=4, ensure_ascii=False))
    return obj

def save_suppressed(obj):
    obj["version"] = VERSION
    obj["updated_at"] = now()
    SUPPRESS.write_text(json.dumps(obj, indent=4, ensure_ascii=False))
    return obj

def rid(item):
    if not isinstance(item, dict):
        return None
    for k in ["request_id", "id", "approval_id", "uid"]:
        if item.get(k):
            return str(item.get(k))
    m = re.search(r"[a-f0-9]{12,}", json.dumps(item, ensure_ascii=False).lower())
    return m.group(0) if m else None

def app():
    import seed_action_approval_v107 as a
    return a

def raw_status():
    try:
        a = app()
        st = a.status()
        pending = []
        for key in ["pending", "requests", "items", "approvals"]:
            if isinstance(st.get(key), list):
                pending = st[key]
                break
        resolved_ids = set()
        approved_ids = set()
        auto_ids = set()
        for key in ["resolved", "rejected", "denied", "auto_resolved"]:
            if isinstance(st.get(key), list):
                for x in st[key]:
                    r = rid(x)
                    if r:
                        resolved_ids.add(r)
                        if key == "auto_resolved":
                            auto_ids.add(r)
        if isinstance(st.get("resolved_ids"), list):
            resolved_ids.update(map(str, st.get("resolved_ids")))
        if isinstance(st.get("approved_ids"), list):
            approved_ids.update(map(str, st.get("approved_ids")))
        if isinstance(st.get("approvals"), list):
            for x in st.get("approvals", []):
                r = rid(x)
                if r:
                    if x.get("approved") is True:
                        approved_ids.add(r)
                    elif x.get("approved") is False:
                        resolved_ids.add(r)
        return {
            "ok": True,
            "status": st,
            "pending": pending,
            "pending_count": int(st.get("pending_count", len(pending)) or 0),
            "resolved_ids": sorted(resolved_ids),
            "approved_ids": sorted(approved_ids),
            "auto_resolved_ids": sorted(auto_ids)
        }
    except Exception as e:
        return {"ok": False, "error": str(e), "pending": [], "pending_count": 0}

def suppressed_ids():
    return {str(x.get("request_id")) for x in load_suppressed().get("suppressed", []) if x.get("request_id")}

def suppress(request_id, reason="manual_suppress", item=None):
    if not request_id:
        return {"ok": False, "error": "missing request_id"}
    obj = load_suppressed()
    existing = {x.get("request_id") for x in obj.get("suppressed", [])}
    if request_id not in existing:
        obj["suppressed"].append({"request_id": str(request_id), "reason": reason, "item": item, "created_at": now(), "version": VERSION})
        save_suppressed(obj)
    row = {"ok": True, "request_id": str(request_id), "reason": reason}
    event({"event": "suppress", **row})
    return row

def call_reject(request_id, reason="seed approval resolver"):
    try:
        a = app()
    except Exception as e:
        return {"ok": False, "error": str(e)}
    tried = []
    for name in ["reject", "deny", "decline", "resolve"]:
        fn = getattr(a, name, None)
        if not callable(fn):
            continue
        patterns = [
            ((request_id,), {}),
            ((request_id, reason), {}),
            ((), {"request_id": request_id, "reason": reason}),
            ((), {"approval_id": request_id, "reason": reason}),
            ((), {"id": request_id, "reason": reason}),
        ]
        for args, kwargs in patterns:
            try:
                res = fn(*args, **kwargs)
                return {"ok": True, "function": name, "request_id": request_id, "result": res}
            except Exception as e:
                tried.append({"function": name, "args": list(args), "kwargs": kwargs, "error": str(e)})
    return {"ok": False, "error": "no reject function worked", "tried": tried}

def call_approve(request_id, reason="seed approval resolver"):
    try:
        a = app()
    except Exception as e:
        return {"ok": False, "error": str(e)}
    tried = []
    for name in ["approve", "allow", "grant"]:
        fn = getattr(a, name, None)
        if not callable(fn):
            continue
        patterns = [
            ((request_id,), {}),
            ((request_id, reason), {}),
            ((), {"request_id": request_id, "reason": reason}),
            ((), {"approval_id": request_id, "reason": reason}),
            ((), {"id": request_id, "reason": reason}),
        ]
        for args, kwargs in patterns:
            try:
                res = fn(*args, **kwargs)
                return {"ok": True, "function": name, "request_id": request_id, "result": res}
            except Exception as e:
                tried.append({"function": name, "args": list(args), "kwargs": kwargs, "error": str(e)})
    return {"ok": False, "error": "no approve function worked", "tried": tried}

def is_stale_empty_operator(item):
    if not isinstance(item, dict):
        return False
    action = str(item.get("action","")).lower()
    if action not in {"operator type", "operator key", "operator hotkey", "operator paste", "operator click"}:
        return False
    if item.get("command") or item.get("target"):
        return False
    try:
        created = datetime.fromisoformat(str(item.get("created_at","")))
        age = (datetime.now() - created).total_seconds() / 60
    except Exception:
        age = 999999
    return age >= 90

def effective_status():
    rs = raw_status()
    if not rs.get("ok"):
        return rs
    suppressed = suppressed_ids()
    resolved = set(rs.get("resolved_ids", [])) | suppressed
    effective = []
    filtered = []
    for item in rs.get("pending", []):
        request_id = rid(item)
        if request_id in resolved:
            filtered.append({"request_id": request_id, "reason": "resolved_or_suppressed", "item": item})
            continue
        effective.append(item)
    out = {
        "created_at": now(),
        "version": VERSION,
        "ok": True,
        "raw_pending_count": rs.get("pending_count"),
        "effective_pending_count": len(effective),
        "effective_pending": effective,
        "filtered": filtered,
        "suppressed_ids": sorted(suppressed),
        "resolved_ids": rs.get("resolved_ids", []),
        "raw": rs
    }
    return out

def repair_stale(apply=False):
    st = effective_status()
    actions = []
    for item in st.get("effective_pending", []):
        request_id = rid(item)
        if is_stale_empty_operator(item):
            row = {"request_id": request_id, "item": item, "decision": "reject_and_suppress", "applied": False}
            if apply:
                row["reject"] = call_reject(request_id, "Auto-rejected stale empty operator request by v136.2.3 resolver")
                row["suppress"] = suppress(request_id, "stale_empty_operator_request", item=item)
                row["applied"] = True
            actions.append(row)
    out = {"created_at": now(), "version": VERSION, "ok": True, "apply": apply, "before": st, "actions": actions}
    event({"event": "repair_stale", "apply": apply, "action_count": len(actions), "actions": actions})
    return out

def apply_reject_and_suppress(request_id):
    res = call_reject(request_id, "Rejected and suppressed by v136.2.3 resolver")
    sup = suppress(request_id, "manual_reject_and_suppress")
    event({"event": "reject_and_suppress", "request_id": request_id, "reject": res, "suppress": sup})
    return {"ok": bool(res.get("ok") or sup.get("ok")), "reject": res, "suppress": sup, "effective_status": effective_status()}

def apply_approve(request_id):
    res = call_approve(request_id, "Approved by v136.2.3 resolver")
    event({"event": "approve", "request_id": request_id, "result": res})
    return {"ok": bool(res.get("ok")), "approve": res, "effective_status": effective_status()}

def test():
    dry = repair_stale(False)
    st = effective_status()
    return {"ok": True, "dry_run_ok": dry.get("ok"), "effective_pending_count": st.get("effective_pending_count"), "raw_pending_count": st.get("raw_pending_count")}

if __name__ == "__main__":
    cmd = sys.argv[1] if len(sys.argv) > 1 else "status"
    if cmd == "raw":
        print(json.dumps(raw_status(), indent=4, ensure_ascii=False))
    elif cmd == "status":
        print(json.dumps(effective_status(), indent=4, ensure_ascii=False))
    elif cmd == "repair-stale":
        print(json.dumps(repair_stale("--apply" in sys.argv), indent=4, ensure_ascii=False))
    elif cmd == "suppress":
        print(json.dumps(suppress(sys.argv[2] if len(sys.argv)>2 else None, "manual"), indent=4, ensure_ascii=False))
    elif cmd == "reject":
        print(json.dumps(apply_reject_and_suppress(sys.argv[2] if len(sys.argv)>2 else None), indent=4, ensure_ascii=False))
    elif cmd == "approve":
        print(json.dumps(apply_approve(sys.argv[2] if len(sys.argv)>2 else None), indent=4, ensure_ascii=False))
    elif cmd == "test":
        print(json.dumps(test(), indent=4, ensure_ascii=False))
    else:
        print(json.dumps(effective_status(), indent=4, ensure_ascii=False))
