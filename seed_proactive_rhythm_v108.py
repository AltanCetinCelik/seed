import json, os, signal, subprocess, sys, time, traceback
from datetime import datetime, timedelta
from pathlib import Path
SETTINGS=Path("seed_proactive_v108_settings.json"); EVENTS=Path("seed_proactive_v108_events.jsonl"); PID=Path("seed_proactive_v108.pid"); LOG=Path("seed_proactive_v108.log"); HEARTBEAT=Path("seed_proactive_v108_heartbeat.json")
DEFAULT={"version":"v108.1.0","enabled":True,"speak_enabled":False,"max_asks_per_day":3,"cooldown_minutes":90,"quiet_hours":{"start":1,"end":10},"tick_seconds":900,"self_heal":True}
PROMPTS=["Kanka, küçük kontrol: Seed tarafında şimdi memory, wake, dashboard, yoksa operator tarafını mı güçlendirelim?","Ben buradayım. Bugün Seed için bir sonraki küçük hedefi seçelim mi?","Açık task varsa toparlayayım mı, yoksa sessizce izlemeye devam mı?"]
def now(): return datetime.now().isoformat(timespec="seconds")
def settings():
    if SETTINGS.exists():
        try:
            d=DEFAULT.copy(); d.update(json.loads(SETTINGS.read_text(errors="ignore"))); d["version"]="v108.1.0"; return d
        except Exception: pass
    SETTINGS.write_text(json.dumps(DEFAULT,indent=4,ensure_ascii=False)); return DEFAULT.copy()
def save(d): d["version"]="v108.1.0"; SETTINGS.write_text(json.dumps(d,indent=4,ensure_ascii=False)); return d
def log(row):
    row.setdefault("created_at",now()); row.setdefault("version","v108.1.0")
    with EVENTS.open("a") as f: f.write(json.dumps(row,ensure_ascii=False)+"\n")
def heartbeat(event="alive"):
    row={"created_at":now(),"version":"v108.1.0","pid":os.getpid(),"event":event}; HEARTBEAT.write_text(json.dumps(row,indent=4,ensure_ascii=False)); return row
def events(limit=5000):
    if not EVENTS.exists(): return []
    out=[]
    for l in EVENTS.read_text(errors="ignore").splitlines()[-limit:]:
        try: out.append(json.loads(l))
        except Exception: pass
    return out
def quiet():
    q=settings().get("quiet_hours",{}); h=datetime.now().hour; a=int(q.get("start",1)); b=int(q.get("end",10)); return a<=h<b if a<b else h>=a or h<b
def asks_today():
    today=datetime.now().date().isoformat(); return [e for e in events() if e.get("event")=="ask" and str(e.get("created_at","")).startswith(today)]
def last_ask():
    xs=[e for e in events() if e.get("event")=="ask"]
    if not xs: return None
    try: return datetime.fromisoformat(xs[-1]["created_at"])
    except Exception: return None
def task_signal():
    try:
        import seed_tasks_v99 as t; st=t.status(); op=st.get("open",st.get("tasks",[])); return {"ok":True,"open_count":len(op),"open":op[:3]}
    except Exception as e: return {"ok":False,"open_count":0,"error":str(e)}
def should_ask(ignore_quiet=False, ignore_cooldown=False):
    s=settings()
    if not s.get("enabled",True): return {"ok":True,"should_ask":False,"reason":"disabled"}
    if quiet() and not ignore_quiet: return {"ok":True,"should_ask":False,"reason":"quiet_hours"}
    if len(asks_today())>=int(s.get("max_asks_per_day",3)): return {"ok":True,"should_ask":False,"reason":"max_asks_per_day"}
    la=last_ask()
    if la and datetime.now()-la < timedelta(minutes=int(s.get("cooldown_minutes",90))) and not ignore_cooldown: return {"ok":True,"should_ask":False,"reason":"cooldown"}
    ts=task_signal(); reasons=[]
    if ts.get("open_count",0)>0: reasons.append("open_tasks")
    if not reasons: reasons.append("gentle_checkin")
    return {"ok":True,"should_ask":True,"reason":reasons[0],"reasons":reasons,"signals":{"tasks":ts}}
def question(reason): return "Kanka, açık task var gibi. Bunu kapatalım mı, yoksa Seed bir sonraki planı mı çıkarsın?" if reason=="open_tasks" else PROMPTS[len(asks_today())%len(PROMPTS)]
def tick(speak=False, force=False):
    d=should_ask(force,force)
    if not d.get("should_ask"):
        row={"event":"tick","asked":False,"decision":d}; log(row); return {"ok":True,**row}
    q=question(d.get("reason")); row={"event":"ask","asked":True,"question":q,"decision":d,"speak":bool(speak or settings().get("speak_enabled",False))}
    if row["speak"]:
        try:
            import seed_tts_v111 as tts; row["tts"]=tts.say(q)
        except Exception as e: row["tts"]={"ok":False,"error":str(e)}
    log(row); return {"ok":True,**row}
def alive(pid):
    try: os.kill(int(pid),0); return True
    except Exception: return False
def daemon():
    log({"event":"daemon_started","pid":os.getpid()}); heartbeat("started")
    while True:
        try: heartbeat("tick"); tick()
        except Exception as e: log({"event":"daemon_error","error":str(e),"traceback":traceback.format_exc()[-2000:]})
        time.sleep(int(settings().get("tick_seconds",900)))
def start(speak=False):
    s=settings(); s["enabled"]=True
    if speak: s["speak_enabled"]=True
    save(s)
    if PID.exists():
        try:
            pid=int(PID.read_text().strip())
            if alive(pid): return {"ok":True,"already_running":True,"pid":pid,"heartbeat":heartbeat_status()}
            PID.unlink(missing_ok=True)
        except Exception: PID.unlink(missing_ok=True)
    p=subprocess.Popen([sys.executable,"seed_proactive_rhythm_v108.py","daemon"],stdout=LOG.open("a"),stderr=LOG.open("a")); PID.write_text(str(p.pid)); time.sleep(.4)
    return {"ok":True,"pid":p.pid,"alive":alive(p.pid),"heartbeat":heartbeat_status()}
def stop():
    pid=None; stopped=False; stale=False
    if PID.exists():
        try:
            pid=int(PID.read_text().strip())
            if alive(pid):
                os.kill(pid,signal.SIGTERM); time.sleep(.3); stopped=not alive(pid)
                if alive(pid): os.kill(pid,signal.SIGKILL); time.sleep(.2); stopped=not alive(pid)
            else: stale=True
            PID.unlink(missing_ok=True)
        except Exception: PID.unlink(missing_ok=True)
    log({"event":"daemon_stop_requested","pid":pid,"stopped":stopped,"stale_pid":stale})
    return {"ok":True,"stopped":stopped,"stale_pid":stale,"pid":pid}
def heartbeat_status():
    if not HEARTBEAT.exists(): return {"ok":False,"reason":"no_heartbeat"}
    try:
        h=json.loads(HEARTBEAT.read_text(errors="ignore")); age=(datetime.now()-datetime.fromisoformat(h["created_at"])).total_seconds(); h["age_seconds"]=round(age,1); h["fresh"]=age < max(120,int(settings().get("tick_seconds",900))*2); return {"ok":True,**h}
    except Exception as e: return {"ok":False,"error":str(e)}
def test():
    old=settings(); tmp=old.copy(); tmp.update({"enabled":True,"max_asks_per_day":99,"cooldown_minutes":0,"quiet_hours":{"start":25,"end":26}}); save(tmp); d=should_ask(); save(old); return {"ok":d.get("should_ask") in {True,False},"decision":d}
def status():
    pid=None; al=False
    if PID.exists():
        try: pid=int(PID.read_text().strip()); al=alive(pid)
        except Exception: pass
    return {"created_at":now(),"version":"v108.1.0","ok":True,"alive":al,"pid":pid,"heartbeat":heartbeat_status(),"settings":settings(),"today_asks":len(asks_today()),"decision_now":should_ask(),"last_events":events(10)}
if __name__=="__main__":
    a=sys.argv[1] if len(sys.argv)>1 else "status"
    if a=="daemon": daemon()
    elif a=="start": print(json.dumps(start("--speak" in sys.argv),indent=4,ensure_ascii=False))
    elif a=="stop": print(json.dumps(stop(),indent=4,ensure_ascii=False))
    elif a=="tick": print(json.dumps(tick("--speak" in sys.argv,"--force" in sys.argv),indent=4,ensure_ascii=False))
    elif a=="test": print(json.dumps(test(),indent=4,ensure_ascii=False))
    else: print(json.dumps(status(),indent=4,ensure_ascii=False))
