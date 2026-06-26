import hashlib,json
from datetime import datetime
from pathlib import Path
LEDGER=Path("seed_safety_ledger_v94.jsonl"); APPROVALS=Path("seed_action_approvals_v107.jsonl"); AUTO_RESOLVED=Path("seed_action_auto_resolved_v1221.jsonl")
SUPERSEDED_OBSERVE={"tool git.status","tool shell.pwd","git.status","shell.pwd"}
def now(): return datetime.now().isoformat(timespec="seconds")
def read_jsonl(path,limit=5000):
    if not Path(path).exists(): return []
    rows=[]
    for line in Path(path).read_text(errors="ignore").splitlines()[-limit:]:
        try: rows.append(json.loads(line))
        except Exception: pass
    return rows
def write_jsonl(path,row):
    row.setdefault("created_at",now()); row.setdefault("version","v107.6.0")
    with Path(path).open("a") as f:f.write(json.dumps(row,ensure_ascii=False)+"\n")
def request_id(row):
    raw="|".join(str(row.get(k,"")) for k in ["created_at","action","command","target"]); return hashlib.sha1(raw.encode()).hexdigest()[:12]
def approvals(): return read_jsonl(APPROVALS,5000)
def approved_ids(): return {r.get("request_id") for r in approvals() if r.get("approved") is True}
def resolved_ids(): return {r.get("request_id") for r in read_jsonl(AUTO_RESOLVED,5000)}
def is_superseded(row): return str(row.get("action","")).strip() in SUPERSEDED_OBSERVE and str(row.get("version",""))=="v94.0.0" and row.get("classification",{}).get("risk")=="risky"
def cleanup_stale():
    count=0
    for row in read_jsonl(LEDGER,5000):
        rid=row.get("request_id") or request_id(row)
        if is_superseded(row) and rid not in resolved_ids():
            write_jsonl(AUTO_RESOLVED,{"request_id":rid,"approved":False,"auto_resolved":True,"reason":"superseded_v94_0_observe_tool_false_block","action":row.get("action")}); count+=1
    return {"ok":True,"auto_resolved":count}
def pending(limit=30):
    cleanup_stale(); seen=approved_ids()|resolved_ids(); out=[]
    for row in reversed(read_jsonl(LEDGER,5000)):
        rid=row.get("request_id") or request_id(row)
        if rid in seen or is_superseded(row): continue
        c=row.get("classification",{})
        if row.get("need_approval") or (c.get("risk")=="risky" and not row.get("allowed")):
            item=dict(row); item["request_id"]=rid; out.append(item)
        if len(out)>=limit: break
    return out
def approve(rid,note="approved"):
    if not rid: return {"ok":False,"error":"missing request_id"}
    row={"request_id":rid,"approved":True,"note":note}; write_jsonl(APPROVALS,row); return {"ok":True,**row}
def reject(rid,note="rejected"):
    if not rid: return {"ok":False,"error":"missing request_id"}
    row={"request_id":rid,"approved":False,"note":note}; write_jsonl(APPROVALS,row); return {"ok":True,**row}
def status():
    p=pending()
    return {"created_at":now(),"version":"v107.6.0","ok":True,"pending_count":len(p),"pending":p[:10],"approvals":approvals()[-10:],"auto_resolved":read_jsonl(AUTO_RESOLVED,10),"note":"Stale v94.0 observe-tool false blocks are auto-resolved; risky actions still require approval."}
if __name__=="__main__":
    import sys
    a=sys.argv[1] if len(sys.argv)>1 else "status"
    if a=="approve": print(json.dumps(approve(sys.argv[2]," ".join(sys.argv[3:])),indent=4,ensure_ascii=False))
    elif a=="reject": print(json.dumps(reject(sys.argv[2]," ".join(sys.argv[3:])),indent=4,ensure_ascii=False))
    elif a=="cleanup": print(json.dumps(cleanup_stale(),indent=4,ensure_ascii=False))
    else: print(json.dumps(status(),indent=4,ensure_ascii=False))
