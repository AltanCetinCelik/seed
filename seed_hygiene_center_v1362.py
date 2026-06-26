import json, os, re, sys, glob, shutil
from pathlib import Path
from datetime import datetime
SNAPSHOT_DIR=Path("seed_hygiene_snapshots_v1362"); REPORT=Path("seed_hygiene_center_v1362_report.json"); EVENTS=Path("seed_hygiene_center_v1362_events.jsonl")
def now(): return datetime.now().isoformat(timespec="seconds")
def jdump(o,p): Path(p).write_text(json.dumps(o,indent=4,ensure_ascii=False)); return o
def event(r):
    r.setdefault("created_at",now()); r.setdefault("version","v136.2.0")
    with EVENTS.open("a") as f: f.write(json.dumps(r,ensure_ascii=False)+"\n")
    return r
def call(mod,fn="status",*a,**k):
    try:
        m=__import__(mod,fromlist=[fn])
        return {"ok":True,"data":getattr(m,fn)(*a,**k)}
    except Exception as e: return {"ok":False,"error":str(e)}
def extract_answer(ev):
    stack=[ev] if isinstance(ev,dict) else []
    if stack:
        if isinstance(ev.get("runtime"),dict): stack.append(ev["runtime"])
        if isinstance(ev.get("event"),dict): stack.append(ev["event"])
        if isinstance(ev.get("result"),dict): stack.append(ev["result"])
    for c in stack:
        for obj in [c.get("result"),c]:
            if isinstance(obj,dict) and isinstance(obj.get("session"),dict) and obj["session"].get("answer"):
                s=obj["session"]
                return {"last_answer":s.get("answer"),"last_intent":(s.get("intent") or {}).get("intent"),"last_transcript":s.get("input"),"last_event_at":s.get("created_at") or c.get("created_at")}
    return {}
def runtime_scan():
    out={"ok":True,"alive":False,"pid":None,"last_answer":None,"last_intent":None,"total_event_lines":0,"log_bytes":0}
    r=call("seed_voice_runtime_v136","runtime_status")
    if r["ok"]:
        d=r["data"]; out["raw"]=d; out["alive"]=bool(d.get("alive")); out["pid"]=d.get("pid")
        for ev in reversed(d.get("recent_events",[])):
            x=extract_answer(ev)
            if x.get("last_answer"): out.update(x); break
    p=Path("seed_voice_runtime_v136_events.jsonl")
    if p.exists(): out["total_event_lines"]=len(p.read_text(errors="ignore").splitlines()); out["log_bytes"]=p.stat().st_size
    return out
def approval_scan():
    out={"ok":True,"pending_count":0,"pending":[],"available_functions":[]}
    r=call("seed_action_approval_v107","status")
    if not r["ok"]: out.update({"ok":False,"error":r["error"]}); return out
    st=r["data"]; out["raw"]=st; out["pending_count"]=int(st.get("pending_count",0) or 0)
    for k in ["pending","requests","items","approvals"]:
        if isinstance(st.get(k),list): out["pending"]=st[k]; break
    try:
        import seed_action_approval_v107 as app
        out["available_functions"]=sorted([x for x in dir(app) if not x.startswith("_") and callable(getattr(app,x,None))])
    except Exception: pass
    return out
def scan_task_files():
    rows=[]
    for pat in ["*task*.json","*task*.jsonl","*tasks*.json","*tasks*.jsonl"]:
        for p in glob.glob(pat):
            path=Path(p)
            if path.is_file() and path.stat().st_size<10_000_000:
                try:
                    txt=path.read_text(errors="ignore")
                    if "task_" in txt or "Test Seed task" in txt: rows.append({"file":p,"preview":txt[:1000]})
                except Exception: pass
    test=[r for r in rows if "test" in r["preview"].lower()]
    return {"file_scan":rows,"open_count":len(rows),"test_task_count":len(test),"test_tasks":test}
def task_scan():
    out={"ok":True,"open_count":0,"test_task_count":0,"test_tasks":[],"available_functions":[]}
    r=call("seed_tasks_v99","status")
    if not r["ok"]: out["module_error"]=r["error"]; out.update(scan_task_files()); return out
    st=r["data"]; out["raw"]=st; open_tasks=[]
    for k in ["open","tasks","open_tasks","items"]:
        if isinstance(st.get(k),list): open_tasks=st[k]; break
    out["open_count"]=len(open_tasks)
    out["test_tasks"]=[t for t in open_tasks if "test" in json.dumps(t,ensure_ascii=False).lower() or "task_1782420721955" in json.dumps(t)]
    out["test_task_count"]=len(out["test_tasks"])
    try:
        import seed_tasks_v99 as tasks
        out["available_functions"]=sorted([x for x in dir(tasks) if not x.startswith("_") and callable(getattr(tasks,x,None))])
    except Exception: pass
    return out
def memory_files():
    out=[]
    for pat in ["seed_memory_garden3*.jsonl","seed_memory_garden3*.json","seed_memory*.jsonl","seed_memory*.json","memory_garden*.jsonl","memory_garden*.json"]:
        for p in glob.glob(pat):
            path=Path(p)
            if path.is_file() and path.stat().st_size<20_000_000: out.append(str(path))
    return sorted(set(out))
def walk(obj):
    res=[]
    if isinstance(obj,dict):
        if "memory_id" in obj or (isinstance(obj.get("memory"),dict) and "memory_id" in obj["memory"]): res.append(obj)
        for v in obj.values(): res+=walk(v)
    elif isinstance(obj,list):
        for x in obj: res+=walk(x)
    return res
def read_records(path):
    rows=[]
    try: txt=path.read_text(errors="ignore")
    except Exception: return rows
    if path.suffix==".jsonl":
        for l in txt.splitlines():
            try:
                o=json.loads(l)
                if isinstance(o,dict): rows.append(o)
            except Exception: pass
    else:
        try: rows+=walk(json.loads(txt))
        except Exception: pass
    return rows
def shadow_index(records):
    seen={}; shadow={}
    for rec in records:
        mid=rec.get("memory_id") or rec.get("memory",{}).get("memory_id")
        if not mid: continue
        seen[mid]=seen.get(mid,0)+1
        key=mid if seen[mid]==1 else f"{mid}__dup{seen[mid]}"
        shadow[key]={"original_memory_id":mid,"duplicate_index":seen[mid],"summary":rec.get("summary") or rec.get("memory",{}).get("summary"),"source":rec.get("source") or rec.get("memory",{}).get("source"),"created_at":rec.get("created_at") or rec.get("memory",{}).get("created_at")}
    Path("seed_memory_hygiene_v1362_shadow_index.json").write_text(json.dumps(shadow,indent=4,ensure_ascii=False))
    return "seed_memory_hygiene_v1362_shadow_index.json"
def memory_scan():
    out={"ok":True,"memory_count":None,"by_type":{},"candidate_files":[],"duplicate_memory_ids":{},"duplicate_count":0,"records_seen":0}
    r=call("seed_memory_garden3_v112","status")
    if r["ok"]: out["raw_status"]=r["data"]; out["memory_count"]=r["data"].get("count"); out["by_type"]=r["data"].get("by_type",{})
    files=memory_files(); out["candidate_files"]=files; rec=[]
    for p in files: rec+=read_records(Path(p))
    out["records_seen"]=len(rec); ids={}
    for x in rec:
        mid=x.get("memory_id") or x.get("memory",{}).get("memory_id")
        if mid: ids.setdefault(mid,[]).append(x)
    dups={k:v for k,v in ids.items() if len(v)>1}
    out["duplicate_memory_ids"]={k:len(v) for k,v in dups.items()}; out["duplicate_count"]=sum(len(v)-1 for v in dups.values())
    out["shadow_index"]=shadow_index(rec)
    return out
def line_count(p):
    try: return len(p.read_text(errors="ignore").splitlines())
    except Exception: return 0
def log_scan():
    rows=[]
    for pat in ["*.log","*events*.jsonl","*transcripts*.jsonl","*sessions*.jsonl"]:
        for p in glob.glob(pat):
            path=Path(p)
            if path.is_file(): rows.append({"file":str(path),"bytes":path.stat().st_size,"lines":line_count(path)})
    rows=sorted(rows,key=lambda x:x["bytes"],reverse=True)
    return {"ok":True,"file_count":len(rows),"total_bytes":sum(x["bytes"] for x in rows),"large_logs":[x for x in rows if x["bytes"]>1_000_000 or x["lines"]>2000],"files":rows[:30]}
def snapshot():
    SNAPSHOT_DIR.mkdir(exist_ok=True); folder=SNAPSHOT_DIR/datetime.now().strftime("%Y%m%d_%H%M%S"); folder.mkdir(parents=True,exist_ok=True); copied=[]
    for pat in ["seed_*settings*.json","seed_*state*.json","seed_*report*.json","seed_*events*.jsonl","seed_*task*.json*","seed_*approval*.json*","seed_memory*.json*"]:
        for p in glob.glob(pat):
            src=Path(p)
            if src.is_file() and src.stat().st_size<15_000_000:
                try: shutil.copy2(src, folder/src.name); copied.append(str(src))
                except Exception: pass
    meta={"created_at":now(),"version":"v136.2.0","folder":str(folder),"copied":copied}
    (folder/"snapshot_meta.json").write_text(json.dumps(meta,indent=4,ensure_ascii=False)); event({"event":"snapshot","folder":str(folder),"copied_count":len(copied)})
    return {"ok":True,**meta}
def score(d):
    s=100; reasons=[]
    if not d["runtime"].get("alive"): s-=10; reasons.append("voice_runtime_not_alive")
    pc=d["approval"].get("pending_count") or 0
    if pc: s-=min(25,pc*15); reasons.append(f"{pc}_pending_approval")
    tc=d["tasks"].get("test_task_count") or 0
    if tc: s-=min(20,tc*15); reasons.append(f"{tc}_test_task")
    dc=d["memory"].get("duplicate_count") or 0
    if dc: s-=min(20,dc*4); reasons.append(f"{dc}_duplicate_memory_entries")
    if d["logs"].get("large_logs"): s-=5; reasons.append("large_logs")
    s=max(0,s); return {"score":s,"reasons":reasons,"grade":"clean" if s>=90 else "needs_review" if s>=70 else "dirty"}
def suggestions(d):
    out=[]
    if d["approval"].get("pending_count"): out.append({"type":"approval_review","severity":"medium","message":"Pending approval exists. Review before more autonomy.","command":"python seed_hygiene_center_v1362.py approvals"})
    if d["tasks"].get("test_task_count"): out.append({"type":"old_test_task","severity":"low","message":"Old test task exists. Review before closing.","command":"python seed_hygiene_center_v1362.py tasks"})
    if d["memory"].get("duplicate_count"): out.append({"type":"duplicate_memory_id","severity":"medium","message":"Duplicate memory IDs detected. Shadow index generated safely.","command":"python seed_hygiene_center_v1362.py memory"})
    if d["logs"].get("large_logs"): out.append({"type":"large_logs","severity":"low","message":"Large logs found. Safe trimming available.","command":"python seed_hygiene_center_v1362.py apply-safe"})
    return out
def scan():
    d={"created_at":now(),"version":"v136.2.0","runtime":runtime_scan(),"approval":approval_scan(),"tasks":task_scan(),"memory":memory_scan(),"logs":log_scan()}
    d["hygiene"]=score(d); d["suggestions"]=suggestions(d); jdump(d,REPORT); return d
def apply_safe():
    before=scan(); snap=snapshot(); actions=[]
    try:
        import seed_runtime_polish_v1361 as p
        actions.append({"action":"trim_runtime_log","result":p.clean_logs(500)})
    except Exception as e: actions.append({"action":"trim_runtime_log","ok":False,"error":str(e)})
    mem=memory_scan(); actions.append({"action":"build_memory_shadow_index","ok":True,"shadow_index":mem.get("shadow_index"),"duplicate_count":mem.get("duplicate_count")})
    after=scan(); row={"created_at":now(),"version":"v136.2.0","ok":True,"snapshot":snap,"actions":actions,"before_score":before["hygiene"],"after_score":after["hygiene"]}; event({"event":"apply_safe","actions":actions,"before_score":before["hygiene"],"after_score":after["hygiene"]}); return row
def text_report():
    d=scan(); lines=["Seed v136.2 Hygiene Center",f"Hygiene score: {d['hygiene']['score']}/100 ({d['hygiene']['grade']})",f"Reasons: {', '.join(d['hygiene']['reasons']) or 'none'}",f"Voice runtime: {'alive' if d['runtime'].get('alive') else 'stopped'} pid={d['runtime'].get('pid')}",f"Last intent: {d['runtime'].get('last_intent')}",f"Last answer: {d['runtime'].get('last_answer')}",f"Approvals pending: {d['approval'].get('pending_count')}",f"Open tasks: {d['tasks'].get('open_count')} / test tasks: {d['tasks'].get('test_task_count')}",f"Memory count: {d['memory'].get('memory_count')} / duplicate memory entries: {d['memory'].get('duplicate_count')}",f"Logs: {d['logs'].get('file_count')} files / {d['logs'].get('total_bytes')} bytes"]
    if d["suggestions"]:
        lines.append("Suggestions:"); [lines.append(f"- [{s['severity']}] {s['message']} ({s['command']})") for s in d["suggestions"]]
    return "\n".join(lines)
def test():
    d=scan(); sn=snapshot(); return {"created_at":now(),"version":"v136.2.0","ok":True,"scan_ok":"hygiene" in d,"snapshot_ok":sn.get("ok"),"score":d.get("hygiene"),"safe_actions":["snapshot","trim_runtime_log","build_memory_shadow_index"]}
if __name__=="__main__":
    cmd=sys.argv[1] if len(sys.argv)>1 else "status"
    if cmd in {"status","scan"}: print(json.dumps(scan(),indent=4,ensure_ascii=False))
    elif cmd=="text": print(text_report())
    elif cmd=="snapshot": print(json.dumps(snapshot(),indent=4,ensure_ascii=False))
    elif cmd=="apply-safe": print(json.dumps(apply_safe(),indent=4,ensure_ascii=False))
    elif cmd=="memory": print(json.dumps(memory_scan(),indent=4,ensure_ascii=False))
    elif cmd=="tasks": print(json.dumps(task_scan(),indent=4,ensure_ascii=False))
    elif cmd=="approvals": print(json.dumps(approval_scan(),indent=4,ensure_ascii=False))
    elif cmd=="logs": print(json.dumps(log_scan(),indent=4,ensure_ascii=False))
    elif cmd=="test": print(json.dumps(test(),indent=4,ensure_ascii=False))
    else: print(text_report())
