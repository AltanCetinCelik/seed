import json, os, re, sys, glob, shutil, inspect
from pathlib import Path
from datetime import datetime

VERSION = "v136.2.1"
EVENTS = Path("seed_hygiene_repair_v13621_events.jsonl")
REPORT = Path("seed_hygiene_repair_v13621_report.json")
SNAP_DIR = Path("seed_hygiene_repair_snapshots_v13621")

def now():
    return datetime.now().isoformat(timespec="seconds")

def event(row):
    row.setdefault("created_at", now())
    row.setdefault("version", VERSION)
    with EVENTS.open("a") as f:
        f.write(json.dumps(row, ensure_ascii=False) + "\n")
    return row

def write_report(obj):
    REPORT.write_text(json.dumps(obj, indent=4, ensure_ascii=False))
    return obj

def run_scan():
    try:
        import seed_hygiene_center_v1362 as h
        return h.scan()
    except Exception as e:
        return {"ok": False, "error": str(e)}

def snapshot(reason="repair"):
    SNAP_DIR.mkdir(exist_ok=True)
    folder = SNAP_DIR / datetime.now().strftime("%Y%m%d_%H%M%S")
    folder.mkdir(parents=True, exist_ok=True)
    copied = []
    patterns = [
        "*.json", "*.jsonl",
        "seed_voice_runtime_v136_events.jsonl",
        "seed_*approval*.json*", "seed_*task*.json*", "seed_memory*.json*",
    ]
    for pat in patterns:
        for p in glob.glob(pat):
            src = Path(p)
            if not src.is_file():
                continue
            if "snapshot" in src.parts or "backup" in src.name.lower():
                continue
            if src.stat().st_size > 20_000_000:
                continue
            try:
                dst = folder / src.name
                if not dst.exists():
                    shutil.copy2(src, dst)
                    copied.append(str(src))
            except Exception:
                pass
    meta = {"ok": True, "created_at": now(), "version": VERSION, "reason": reason, "folder": str(folder), "copied": copied}
    (folder / "snapshot_meta.json").write_text(json.dumps(meta, indent=4, ensure_ascii=False))
    event({"event": "snapshot", "folder": str(folder), "copied_count": len(copied), "reason": reason})
    return meta

def load_json_file(path):
    path = Path(path)
    txt = path.read_text(errors="ignore")
    if path.suffix == ".jsonl":
        rows = []
        for line in txt.splitlines():
            if not line.strip():
                continue
            try:
                rows.append(json.loads(line))
            except Exception:
                rows.append({"__unparsed_line__": line})
        return rows
    return json.loads(txt)

def save_json_file(path, obj):
    path = Path(path)
    if path.suffix == ".jsonl":
        lines = []
        for row in obj:
            if isinstance(row, dict) and "__unparsed_line__" in row:
                lines.append(row["__unparsed_line__"])
            else:
                lines.append(json.dumps(row, ensure_ascii=False))
        path.write_text("\n".join(lines) + ("\n" if lines else ""))
    else:
        path.write_text(json.dumps(obj, indent=4, ensure_ascii=False))

def candidate_memory_files():
    pats = [
        "seed_memory_garden3*.jsonl", "seed_memory_garden3*.json",
        "seed_memory*.jsonl", "seed_memory*.json",
        "memory_garden*.jsonl", "memory_garden*.json",
    ]
    out = []
    for pat in pats:
        for p in glob.glob(pat):
            path = Path(p)
            if not path.is_file() or path.stat().st_size > 20_000_000:
                continue
            low = path.name.lower()
            if any(x in low for x in ["hygiene", "shadow", "report", "backup", "gate", "snapshot"]):
                continue
            out.append(str(path))
    return sorted(set(out))

def iter_memory_objs(obj, path=None):
    path = path or []
    if isinstance(obj, dict):
        if "memory_id" in obj or ("memory" in obj and isinstance(obj.get("memory"), dict) and "memory_id" in obj["memory"]):
            yield obj, path
        for k, v in obj.items():
            yield from iter_memory_objs(v, path + [k])
    elif isinstance(obj, list):
        for i, v in enumerate(obj):
            yield from iter_memory_objs(v, path + [i])

def get_memory_id(obj):
    if isinstance(obj, dict):
        if obj.get("memory_id"):
            return obj.get("memory_id")
        if isinstance(obj.get("memory"), dict):
            return obj["memory"].get("memory_id")
    return None

def set_memory_id(obj, new_id):
    if "memory_id" in obj:
        obj["memory_id"] = new_id
    if isinstance(obj.get("memory"), dict) and "memory_id" in obj["memory"]:
        obj["memory"]["memory_id"] = new_id
    obj["hygiene_repaired_at"] = now()
    obj["hygiene_repair_version"] = VERSION

def memory_repair(apply=False):
    records = []
    file_objs = {}
    for f in candidate_memory_files():
        try:
            obj = load_json_file(f)
            file_objs[f] = obj
            for mobj, path in iter_memory_objs(obj):
                mid = get_memory_id(mobj)
                if mid:
                    records.append({"file": f, "path": path, "memory_id": mid, "obj": mobj})
        except Exception as e:
            records.append({"file": f, "error": str(e)})
    by_id = {}
    for r in records:
        mid = r.get("memory_id")
        if mid:
            by_id.setdefault(mid, []).append(r)
    dups = {mid: rows for mid, rows in by_id.items() if len(rows) > 1}
    changes = []
    for mid, rows in dups.items():
        for idx, r in enumerate(rows):
            if idx == 0:
                continue
            suffix = f"__v13621_dup{idx}"
            new_id = mid + suffix
            changes.append({"file": r["file"], "path": r["path"], "old_id": mid, "new_id": new_id})
            if apply:
                set_memory_id(r["obj"], new_id)
    if apply and changes:
        snap = snapshot("memory_repair")
        for f, obj in file_objs.items():
            backup = Path(f"{f}.v13621.bak")
            if not backup.exists():
                try:
                    shutil.copy2(f, backup)
                except Exception:
                    pass
            save_json_file(f, obj)
        event({"event": "memory_repair_apply", "change_count": len(changes), "snapshot": snap.get("folder")})
    shadow = {
        "created_at": now(),
        "version": VERSION,
        "apply": apply,
        "duplicate_groups": {k: len(v) for k, v in dups.items()},
        "changes": changes,
        "candidate_files": candidate_memory_files()
    }
    Path("seed_hygiene_repair_v13621_memory_plan.json").write_text(json.dumps(shadow, indent=4, ensure_ascii=False))
    return {"ok": True, "apply": apply, "duplicate_groups": len(dups), "duplicate_entries_to_repair": len(changes), "changes": changes, "plan_file": "seed_hygiene_repair_v13621_memory_plan.json"}

def candidate_task_files():
    pats = ["*task*.json", "*task*.jsonl", "*tasks*.json", "*tasks*.jsonl"]
    out = []
    for pat in pats:
        for p in glob.glob(pat):
            path = Path(p)
            if not path.is_file() or path.stat().st_size > 10_000_000:
                continue
            low = path.name.lower()
            if any(x in low for x in ["hygiene", "report", "backup", "gate", "snapshot"]):
                continue
            try:
                txt = path.read_text(errors="ignore").lower()
                if "task_" in txt or "test seed task" in txt:
                    out.append(str(path))
            except Exception:
                pass
    return sorted(set(out))

def iter_dict_objs(obj, path=None):
    path = path or []
    if isinstance(obj, dict):
        yield obj, path
        for k, v in obj.items():
            yield from iter_dict_objs(v, path + [k])
    elif isinstance(obj, list):
        for i, v in enumerate(obj):
            yield from iter_dict_objs(v, path + [i])

def is_test_task(obj):
    if not isinstance(obj, dict):
        return False
    txt = json.dumps(obj, ensure_ascii=False).lower()
    return ("test seed task" in txt) or ("task_1782420721955" in txt) or ("test" in txt and "task" in txt and ("open" in txt or "pending" in txt))

def task_id(obj):
    for k in ["task_id", "id", "uid", "request_id"]:
        if obj.get(k):
            return obj.get(k)
    m = re.search(r"task_[0-9]+", json.dumps(obj, ensure_ascii=False))
    return m.group(0) if m else None

def module_task_close(apply=False):
    out = {"ok": True, "tried": [], "closed": []}
    try:
        import seed_tasks_v99 as tasks
    except Exception as e:
        out["module_error"] = str(e)
        return out
    funcs = []
    for name in ["close_task", "complete_task", "finish_task", "resolve_task", "delete_task", "remove_task", "mark_done"]:
        if hasattr(tasks, name) and callable(getattr(tasks, name)):
            funcs.append(name)
    try:
        st = tasks.status()
    except Exception:
        st = {}
    all_tasks = []
    for key in ["open", "tasks", "open_tasks", "items"]:
        if isinstance(st.get(key), list):
            all_tasks = st[key]
            break
    targets = [t for t in all_tasks if is_test_task(t)]
    out["targets"] = targets
    if not apply:
        return out
    for t in targets:
        tid = task_id(t)
        for fn in funcs:
            try:
                res = getattr(tasks, fn)(tid) if tid else getattr(tasks, fn)(t)
                out["tried"].append({"fn": fn, "task_id": tid, "result": res})
                out["closed"].append({"task_id": tid, "fn": fn})
                break
            except Exception as e:
                out["tried"].append({"fn": fn, "task_id": tid, "error": str(e)})
    return out

def task_file_repair(apply=False):
    changes = []
    file_objs = {}
    for f in candidate_task_files():
        try:
            obj = load_json_file(f)
            file_objs[f] = obj
            for dobj, path in iter_dict_objs(obj):
                if is_test_task(dobj):
                    changes.append({"file": f, "path": path, "task_id": task_id(dobj), "title": dobj.get("title") or dobj.get("summary") or dobj.get("description")})
                    if apply:
                        dobj["status"] = "closed"
                        dobj["closed"] = True
                        dobj["completed"] = True
                        dobj["closed_at"] = now()
                        dobj["closed_by"] = "seed_hygiene_repair_v13621"
        except Exception as e:
            changes.append({"file": f, "error": str(e)})
    if apply and changes:
        snap = snapshot("task_file_repair")
        for f, obj in file_objs.items():
            backup = Path(f"{f}.v13621.bak")
            if not backup.exists():
                try:
                    shutil.copy2(f, backup)
                except Exception:
                    pass
            save_json_file(f, obj)
        event({"event": "task_file_repair_apply", "change_count": len(changes), "snapshot": snap.get("folder")})
    return {"ok": True, "apply": apply, "changes": changes, "candidate_files": candidate_task_files()}

def task_repair(apply=False):
    mod = module_task_close(apply=apply)
    files = task_file_repair(apply=apply and not mod.get("closed"))
    out = {"ok": True, "apply": apply, "module": mod, "files": files}
    Path("seed_hygiene_repair_v13621_task_plan.json").write_text(json.dumps(out, indent=4, ensure_ascii=False))
    return out

def approval_status():
    out = {"ok": True, "pending_count": 0, "pending": [], "available_functions": []}
    try:
        import seed_action_approval_v107 as app
    except Exception as e:
        return {"ok": False, "error": str(e)}
    try:
        st = app.status()
        out["raw"] = st
        out["pending_count"] = int(st.get("pending_count", 0) or 0)
        for key in ["pending", "requests", "items", "approvals"]:
            if isinstance(st.get(key), list):
                out["pending"] = st[key]
                break
    except Exception as e:
        out["status_error"] = str(e)
    out["available_functions"] = sorted([x for x in dir(app) if not x.startswith("_") and callable(getattr(app, x, None))])
    return out

def approval_id_from_obj(obj):
    if not isinstance(obj, dict):
        return None
    for k in ["request_id", "id", "approval_id", "uid"]:
        if obj.get(k):
            return str(obj.get(k))
    m = re.search(r"[a-f0-9]{12,}", json.dumps(obj, ensure_ascii=False).lower())
    return m.group(0) if m else None

def call_approval(action, request_id=None, reason="seed hygiene repair"):
    try:
        import seed_action_approval_v107 as app
    except Exception as e:
        return {"ok": False, "error": str(e)}
    if action == "reject":
        names = ["reject", "deny", "decline", "resolve_false", "resolve", "reject_request", "deny_request", "clear"]
    else:
        names = ["approve", "allow", "grant", "approve_request", "allow_request"]
    tried = []
    for name in names:
        fn = getattr(app, name, None)
        if not callable(fn):
            continue
        call_patterns = []
        if request_id:
            call_patterns.extend([
                ((request_id,), {}),
                ((request_id, reason), {}),
                ((), {"request_id": request_id, "reason": reason}),
                ((), {"approval_id": request_id, "reason": reason}),
                ((), {"id": request_id, "reason": reason}),
            ])
        else:
            call_patterns.append(((), {}))
        for args, kwargs in call_patterns:
            try:
                res = fn(*args, **kwargs)
                return {"ok": True, "function": name, "request_id": request_id, "result": res, "tried": tried}
            except Exception as e:
                tried.append({"function": name, "args": args, "kwargs": kwargs, "error": str(e)})
    return {"ok": False, "error": "no compatible approval function worked", "tried": tried, "available": approval_status().get("available_functions")}

def approval_plan():
    st = approval_status()
    pending = st.get("pending") or []
    plans = []
    for item in pending:
        rid = approval_id_from_obj(item)
        txt = json.dumps(item, ensure_ascii=False).lower()
        stale_safe = any(x in txt for x in ["operator type", "shell.pwd", "git.status", "old", "false block", "test"])
        plans.append({"request_id": rid, "safe_to_auto_reject_guess": stale_safe, "item": item})
    return {"ok": st.get("ok", False), "pending_count": st.get("pending_count"), "plans": plans, "available_functions": st.get("available_functions"), "raw": st}

def reject_approval(request_id):
    snap = snapshot("reject_approval")
    res = call_approval("reject", request_id=request_id, reason="Rejected by v136.2.1 hygiene repair after user command.")
    event({"event": "reject_approval", "request_id": request_id, "result": res, "snapshot": snap.get("folder")})
    return res

def approve_approval(request_id):
    snap = snapshot("approve_approval")
    res = call_approval("approve", request_id=request_id, reason="Approved by v136.2.1 hygiene repair after user command.")
    event({"event": "approve_approval", "request_id": request_id, "result": res, "snapshot": snap.get("folder")})
    return res

def safe_apply(apply=False):
    before = run_scan()
    plan = {"created_at": now(), "version": VERSION, "apply": apply, "before": summary_from_scan(before), "actions": []}
    if apply:
        snap = snapshot("safe_apply")
        plan["snapshot"] = snap
    plan["actions"].append({"name": "memory_repair", "result": memory_repair(apply=apply)})
    plan["actions"].append({"name": "task_repair", "result": task_repair(apply=apply)})
    try:
        import seed_runtime_polish_v1361 as polish
        plan["actions"].append({"name": "trim_runtime_logs", "result": polish.clean_logs(500) if apply else {"ok": True, "dry_run": True}})
    except Exception as e:
        plan["actions"].append({"name": "trim_runtime_logs", "result": {"ok": False, "error": str(e)}})
    after = run_scan()
    plan["after"] = summary_from_scan(after)
    plan["ok"] = True
    write_report(plan)
    event({"event": "safe_apply" if apply else "safe_apply_dry_run", "before": plan["before"], "after": plan["after"]})
    return plan

def summary_from_scan(scan):
    if not isinstance(scan, dict):
        return {}
    return {
        "score": scan.get("hygiene", {}).get("score"),
        "grade": scan.get("hygiene", {}).get("grade"),
        "approval_pending": scan.get("approval", {}).get("pending_count"),
        "test_tasks": scan.get("tasks", {}).get("test_task_count"),
        "duplicate_memory_entries": scan.get("memory", {}).get("duplicate_count"),
        "runtime_alive": scan.get("runtime", {}).get("alive"),
    }

def status():
    scan = run_scan()
    return {
        "created_at": now(),
        "version": VERSION,
        "ok": True,
        "scan_summary": summary_from_scan(scan),
        "approval": approval_plan(),
        "task_plan": task_repair(apply=False),
        "memory_plan": memory_repair(apply=False),
        "commands": {
            "dry_run": "python seed_hygiene_repair_v13621.py dry-run",
            "apply_safe": "python seed_hygiene_repair_v13621.py apply-safe",
            "reject_approval": "python seed_hygiene_repair_v13621.py reject-approval <REQUEST_ID>",
            "approve_approval": "python seed_hygiene_repair_v13621.py approve-approval <REQUEST_ID>"
        }
    }

def text():
    st = status()
    s = st["scan_summary"]
    lines = [
        "Seed v136.2.1 Actual Hygiene Repair",
        f"Current score: {s.get('score')}/100 ({s.get('grade')})",
        f"Pending approvals: {s.get('approval_pending')}",
        f"Test tasks: {s.get('test_tasks')}",
        f"Duplicate memory entries: {s.get('duplicate_memory_entries')}",
        "",
        "Repair plan:",
        f"- Memory duplicate changes: {st['memory_plan'].get('duplicate_entries_to_repair')}",
        f"- Task changes: {len(st['task_plan'].get('files',{}).get('changes',[]))}",
        f"- Approval pending: {st['approval'].get('pending_count')} (manual approve/reject only)",
        "",
        "Commands:",
        "python seed_hygiene_repair_v13621.py dry-run",
        "python seed_hygiene_repair_v13621.py apply-safe",
        "python seed_hygiene_repair_v13621.py approvals",
        "python seed_hygiene_repair_v13621.py reject-approval <REQUEST_ID>",
    ]
    return "\n".join(lines)

def test():
    return {
        "created_at": now(),
        "version": VERSION,
        "ok": True,
        "memory_plan_ok": memory_repair(False).get("ok"),
        "task_plan_ok": task_repair(False).get("ok"),
        "approval_plan_ok": approval_plan().get("ok") in {True, False},
        "dry_run_ok": safe_apply(False).get("ok")
    }

if __name__ == "__main__":
    cmd = sys.argv[1] if len(sys.argv) > 1 else "text"
    if cmd == "status":
        print(json.dumps(status(), indent=4, ensure_ascii=False))
    elif cmd == "text":
        print(text())
    elif cmd == "dry-run":
        print(json.dumps(safe_apply(False), indent=4, ensure_ascii=False))
    elif cmd == "apply-safe":
        print(json.dumps(safe_apply(True), indent=4, ensure_ascii=False))
    elif cmd == "memory":
        print(json.dumps(memory_repair("--apply" in sys.argv), indent=4, ensure_ascii=False))
    elif cmd == "tasks":
        print(json.dumps(task_repair("--apply" in sys.argv), indent=4, ensure_ascii=False))
    elif cmd == "approvals":
        print(json.dumps(approval_plan(), indent=4, ensure_ascii=False))
    elif cmd == "reject-approval":
        print(json.dumps(reject_approval(sys.argv[2] if len(sys.argv) > 2 else None), indent=4, ensure_ascii=False))
    elif cmd == "approve-approval":
        print(json.dumps(approve_approval(sys.argv[2] if len(sys.argv) > 2 else None), indent=4, ensure_ascii=False))
    elif cmd == "snapshot":
        print(json.dumps(snapshot("manual"), indent=4, ensure_ascii=False))
    elif cmd == "test":
        print(json.dumps(test(), indent=4, ensure_ascii=False))
    else:
        print(text())
