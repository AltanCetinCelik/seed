import json
from pathlib import Path
from datetime import datetime
STATE=Path("seed_proactive_presence_v134_state.json")
EVENTS=Path("seed_proactive_presence_v134_events.jsonl")
DEFAULT={"version":"v134.0.0","enabled":True,"max_interruptions_per_day":3,"daily_reflection_enabled":True,"memory_curiosity_enabled":True}
def now(): return datetime.now().isoformat(timespec="seconds")
def state():
    if STATE.exists():
        try:
            d=DEFAULT.copy(); d.update(json.loads(STATE.read_text(errors="ignore"))); d["version"]="v134.0.0"; return d
        except Exception: pass
    STATE.write_text(json.dumps(DEFAULT,indent=4,ensure_ascii=False)); return DEFAULT.copy()
def event(row):
    row.setdefault("created_at",now()); row.setdefault("version","v134.0.0")
    with EVENTS.open("a") as f: f.write(json.dumps(row,ensure_ascii=False)+"\n")
    return row
def events(limit=20):
    if not EVENTS.exists(): return []
    out=[]
    for l in EVENTS.read_text(errors="ignore").splitlines()[-limit:]:
        try: out.append(json.loads(l))
        except Exception: pass
    return out
def signals():
    data={}
    try:
        import seed_tasks_v99 as t
        st=t.status(); op=st.get("open",st.get("tasks",[])); data["tasks"]={"ok":True,"open_count":len(op),"open":op[:3]}
    except Exception as e: data["tasks"]={"ok":False,"error":str(e),"open_count":0}
    try:
        import seed_memory_garden3_v112 as m
        st=m.status(); data["memory"]={"ok":True,"count":st.get("count",0),"by_type":st.get("by_type",{})}
    except Exception as e: data["memory"]={"ok":False,"error":str(e)}
    try:
        import seed_action_approval_v107 as a
        data["approval"]={"ok":True,"pending":a.status().get("pending_count",0)}
    except Exception as e: data["approval"]={"ok":False,"error":str(e),"pending":0}
    return data
def score():
    if not state().get("enabled",True): return {"ok":True,"score":0,"should_suggest":False,"reason":"disabled"}
    s=signals(); pts=0; reasons=[]
    if s["tasks"].get("open_count",0): pts+=35; reasons.append("open_tasks")
    if s["memory"].get("count",0)<5: pts+=20; reasons.append("memory_sparse")
    if s["approval"].get("pending",0): pts+=25; reasons.append("pending_approval")
    if not reasons: pts=10; reasons=["gentle_presence"]
    return {"ok":True,"score":pts,"should_suggest":pts>=25,"reasons":reasons,"signals":s}
def suggestion():
    sc=score()
    if not sc.get("should_suggest"): return {"ok":True,"suggested":False,"score":sc,"event":event({"event":"quiet_tick","score":sc})}
    reasons=sc.get("reasons",[])
    if "pending_approval" in reasons: text="Kanka, one real approval is waiting. Want to review it before giving Seed more autonomy?"
    elif "open_tasks" in reasons: text="Kanka, there is still an open task. Want Seed to close or archive the test task?"
    elif "memory_sparse" in reasons: text="Seed memory is still thin. Want to save this checkpoint as a milestone?"
    else: text="Small check-in: should Seed stay quiet or help plan the next improvement?"
    return {"ok":True,"suggested":True,"text":text,"score":sc,"event":event({"event":"suggestion","text":text,"score":sc})}
def reflection():
    row=event({"event":"reflection","text":"Daily Seed reflection generated.","signals":signals()})
    return {"ok":True,"reflection":row}
def status(): return {"created_at":now(),"version":"v134.0.0","ok":True,"state":state(),"score":score(),"latest":events(10)}
if __name__=="__main__":
    import sys
    a=sys.argv[1] if len(sys.argv)>1 else "status"
    if a=="suggest": print(json.dumps(suggestion(),indent=4,ensure_ascii=False))
    elif a=="reflect": print(json.dumps(reflection(),indent=4,ensure_ascii=False))
    else: print(json.dumps(status(),indent=4,ensure_ascii=False))
