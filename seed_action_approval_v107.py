import hashlib
import json
from datetime import datetime
from pathlib import Path

LEDGER = Path("seed_safety_ledger_v94.jsonl")
APPROVALS = Path("seed_action_approvals_v107.jsonl")

def now():
    return datetime.now().isoformat(timespec="seconds")

def read_jsonl(path, limit=1000):
    if not Path(path).exists():
        return []
    rows = []
    for line in Path(path).read_text(errors="ignore").splitlines()[-limit:]:
        try:
            rows.append(json.loads(line))
        except Exception:
            pass
    return rows

def write_jsonl(path, row):
    row.setdefault("created_at", now())
    row.setdefault("version", "v107.5.0")
    with Path(path).open("a") as f:
        f.write(json.dumps(row, ensure_ascii=False) + "\n")

def request_id(row):
    raw = "|".join(str(row.get(k, "")) for k in ["created_at", "action", "command", "target"])
    return hashlib.sha1(raw.encode()).hexdigest()[:12]

def approvals():
    return read_jsonl(APPROVALS, 5000)

def approved_ids():
    return {r.get("request_id") for r in approvals() if r.get("approved") is True}

def pending(limit=30):
    seen = approved_ids()
    out = []
    for row in reversed(read_jsonl(LEDGER, 5000)):
        c = row.get("classification", {})
        rid = row.get("request_id") or request_id(row)
        if rid in seen:
            continue
        if row.get("need_approval") or (c.get("risk") == "risky" and not row.get("allowed")):
            item = dict(row)
            item["request_id"] = rid
            out.append(item)
        if len(out) >= limit:
            break
    return out

def approve(rid, note="approved_from_dashboard"):
    if not rid:
        return {"ok": False, "error": "missing request_id"}
    row = {"request_id": rid, "approved": True, "note": note}
    write_jsonl(APPROVALS, row)
    return {"ok": True, **row}

def reject(rid, note="rejected_from_dashboard"):
    if not rid:
        return {"ok": False, "error": "missing request_id"}
    row = {"request_id": rid, "approved": False, "note": note}
    write_jsonl(APPROVALS, row)
    return {"ok": True, **row}

def status():
    p = pending()
    return {
        "created_at": now(),
        "version": "v107.5.0",
        "ok": True,
        "pending_count": len(p),
        "pending": p[:10],
        "approvals": approvals()[-10:],
        "note": "Approval center records approval decisions; it does not execute blocked actions automatically."
    }

if __name__ == "__main__":
    import sys
    arg = sys.argv[1] if len(sys.argv) > 1 else "status"
    if arg == "approve":
        print(json.dumps(approve(sys.argv[2], " ".join(sys.argv[3:]) or "manual"), indent=4, ensure_ascii=False))
    elif arg == "reject":
        print(json.dumps(reject(sys.argv[2], " ".join(sys.argv[3:]) or "manual"), indent=4, ensure_ascii=False))
    else:
        print(json.dumps(status(), indent=4, ensure_ascii=False))
