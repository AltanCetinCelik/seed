import json, os, signal, subprocess, sys, time
from pathlib import Path
from datetime import datetime

SETTINGS = Path("seed_voice_runtime_v136_settings.json")
STATE = Path("seed_voice_runtime_v136_state.json")
EVENTS = Path("seed_voice_runtime_v136_events.jsonl")
INBOX = Path("seed_voice_runtime_v136_inbox.jsonl")
PID = Path("seed_voice_runtime_v136.pid")
LOG = Path("seed_voice_runtime_v136.log")
PORT = 8816

DEFAULT = {
    "version": "v136.0.0",
    "mode": "push_to_talk",
    "voice_seconds": 5,
    "speak_default": True,
    "continuous_voice": False,
    "continuous_interval_seconds": 3,
    "require_wake_for_text": True,
    "max_runtime_events": 2000
}

def now():
    return datetime.now().isoformat(timespec="seconds")

def read_json(path, fallback):
    if path.exists():
        try:
            d=json.loads(path.read_text(errors="ignore"))
            if isinstance(d, dict):
                x=fallback.copy()
                x.update(d)
                x["version"]="v136.0.0"
                return x
        except Exception:
            pass
    path.write_text(json.dumps(fallback,indent=4,ensure_ascii=False))
    return fallback.copy()

def settings():
    return read_json(SETTINGS, DEFAULT)

def save_settings(d):
    d["version"]="v136.0.0"
    SETTINGS.write_text(json.dumps(d,indent=4,ensure_ascii=False))
    return d

def state():
    base={"version":"v136.0.0","created_at":now(),"alive":False,"pid":None,"last_event":None,"processed_inbox":0,"mode":settings().get("mode")}
    if STATE.exists():
        try:
            old=json.loads(STATE.read_text(errors="ignore"))
            if isinstance(old,dict):
                base.update(old)
        except Exception:
            pass
    base["version"]="v136.0.0"
    return base

def save_state(d):
    d["version"]="v136.0.0"
    d["updated_at"]=now()
    STATE.write_text(json.dumps(d,indent=4,ensure_ascii=False))
    return d

def log_event(row):
    row.setdefault("created_at",now())
    row.setdefault("version","v136.0.0")
    with EVENTS.open("a") as f:
        f.write(json.dumps(row,ensure_ascii=False)+"\n")
    st=state()
    st["last_event"]=row
    save_state(st)
    return row

def events(limit=50):
    if not EVENTS.exists():
        return []
    out=[]
    for line in EVENTS.read_text(errors="ignore").splitlines()[-limit:]:
        try:
            out.append(json.loads(line))
        except Exception:
            pass
    return out

def alive(pid):
    try:
        os.kill(int(pid),0)
        return True
    except Exception:
        return False

def normalize_text(text):
    try:
        import seed_voice_intent_normalizer_v1352 as normalizer
        return normalizer.normalize(text)
    except Exception as e:
        return {"ok":False,"raw_text":text,"normalized_text":text,"intent":"general","confidence":0.2,"error":str(e)}

def answer_text(text, speak_enabled=None, allow_bad_text=True):
    if speak_enabled is None:
        speak_enabled = bool(settings().get("speak_default", True))
    try:
        import seed_voice_conversation_v133 as conv
        result=conv.converse_text(text, speak_enabled=speak_enabled, allow_bad_text=allow_bad_text)
    except Exception as e:
        result={"ok":False,"error":str(e)}
    return result

def run_text(text, speak_enabled=None):
    intent=normalize_text(text)
    normalized=intent.get("normalized_text") or text
    result=answer_text(normalized, speak_enabled=speak_enabled, allow_bad_text=True)
    event=log_event({"event":"text_runtime","input":text,"intent":intent,"result":result})
    return {"ok":bool(result.get("ok")),"event":event,"intent":intent,"result":result}

def run_wake_text(text, speak_enabled=None):
    try:
        import seed_real_wake_v132 as wake
        match=wake.match_text(text)
    except Exception as e:
        match={"ok":False,"matched":False,"error":str(e)}
    if not match.get("matched"):
        event=log_event({"event":"wake_text_ignored","input":text,"wake":match})
        return {"ok":True,"ignored":True,"reason":"wake_not_matched","event":event}
    rest=match.get("rest") or text
    out=run_text(rest, speak_enabled=speak_enabled)
    out["wake"]=match
    event=log_event({"event":"wake_text_runtime","input":text,"wake":match,"runtime":out})
    return {"ok":bool(out.get("ok")),"event":event,"wake":match,"runtime":out}

def voice_once(seconds=None, speak_enabled=None):
    if speak_enabled is None:
        speak_enabled=bool(settings().get("speak_default", True))
    seconds=int(seconds or settings().get("voice_seconds",5))
    try:
        import seed_voice_conversation_v133 as conv
        result=conv.listen_and_answer(seconds=seconds, speak_enabled=speak_enabled)
    except TypeError:
        try:
            import seed_voice_conversation_v133 as conv
            result=conv.listen_and_answer(seconds, speak_enabled)
        except Exception as e:
            result={"ok":False,"error":str(e)}
    except Exception as e:
        result={"ok":False,"error":str(e)}
    event=log_event({"event":"voice_once","seconds":seconds,"speak_enabled":speak_enabled,"result":result})
    return {"ok":bool(result.get("ok")),"event":event,"result":result}

def enqueue_text(text):
    row={"created_at":now(),"version":"v136.0.0","type":"wake_text","text":text}
    with INBOX.open("a") as f:
        f.write(json.dumps(row,ensure_ascii=False)+"\n")
    return {"ok":True,"queued":row}

def read_inbox():
    if not INBOX.exists():
        return []
    rows=[]
    for line in INBOX.read_text(errors="ignore").splitlines():
        try:
            rows.append(json.loads(line))
        except Exception:
            pass
    return rows

def process_inbox_once():
    st=state()
    rows=read_inbox()
    start=int(st.get("processed_inbox",0) or 0)
    new=rows[start:]
    results=[]
    for row in new:
        text=row.get("text","")
        if row.get("type")=="wake_text":
            results.append(run_wake_text(text, speak_enabled=settings().get("speak_default",True)))
        else:
            results.append(run_text(text, speak_enabled=settings().get("speak_default",True)))
    st["processed_inbox"]=len(rows)
    save_state(st)
    return {"ok":True,"processed":len(new),"results":results}

def daemon(continuous=False):
    s=settings()
    s["continuous_voice"]=bool(continuous)
    s["mode"]="continuous_voice" if continuous else "push_to_talk"
    save_settings(s)
    save_state({"version":"v136.0.0","created_at":now(),"alive":True,"pid":os.getpid(),"mode":s["mode"],"processed_inbox":state().get("processed_inbox",0) or 0})
    log_event({"event":"daemon_started","mode":s["mode"],"pid":os.getpid()})
    while True:
        st=state()
        st["alive"]=True
        st["pid"]=os.getpid()
        st["heartbeat_at"]=now()
        save_state(st)
        try:
            process_inbox_once()
        except Exception as e:
            log_event({"event":"inbox_error","error":str(e)})
        if settings().get("continuous_voice"):
            try:
                voice_once(settings().get("voice_seconds",5), speak_enabled=settings().get("speak_default",True))
            except Exception as e:
                log_event({"event":"continuous_voice_error","error":str(e)})
            time.sleep(int(settings().get("continuous_interval_seconds",3)))
        else:
            time.sleep(1)

def start(continuous=False, speak=True):
    if PID.exists():
        try:
            pid=int(PID.read_text().strip())
            if alive(pid):
                return {"ok":True,"already_running":True,"pid":pid,"mode":state().get("mode")}
        except Exception:
            pass
    s=settings()
    s["speak_default"]=bool(speak)
    save_settings(s)
    args=[sys.executable,"seed_voice_runtime_v136.py","daemon"]
    if continuous:
        args.append("--continuous")
    p=subprocess.Popen(args,stdout=LOG.open("a"),stderr=LOG.open("a"))
    PID.write_text(str(p.pid))
    return {"ok":True,"pid":p.pid,"mode":"continuous_voice" if continuous else "push_to_talk"}

def stop():
    pid=None
    stopped=False
    if PID.exists():
        try:
            pid=int(PID.read_text().strip())
            if alive(pid):
                os.kill(pid, signal.SIGTERM)
                stopped=True
            PID.unlink(missing_ok=True)
        except Exception:
            pass
    st=state()
    st["alive"]=False
    st["pid"]=None
    save_state(st)
    log_event({"event":"daemon_stopped","pid":pid,"stopped":stopped})
    return {"ok":True,"stopped":stopped,"pid":pid}

def runtime_status():
    pid=None
    al=False
    if PID.exists():
        try:
            pid=int(PID.read_text().strip())
            al=alive(pid)
        except Exception:
            pass
    st=state()
    st["alive"]=al
    st["pid"]=pid
    save_state(st)
    return {
        "created_at":now(),
        "version":"v136.0.0",
        "ok":True,
        "alive":al,
        "pid":pid,
        "settings":settings(),
        "state":st,
        "recent_events":events(10)
    }

def test():
    a=run_text("Seet status, how many systems are green?", speak_enabled=False)
    b=run_wake_text("wake up status", speak_enabled=False)
    c=run_wake_text("pumpkin seed recipe", speak_enabled=False)
    d=enqueue_text("wake up status")
    e=process_inbox_once()
    return {
        "created_at":now(),
        "version":"v136.0.0",
        "ok": a.get("ok") is True and b.get("ok") is True and c.get("ignored") is True and e.get("ok") is True,
        "direct_text":a,
        "wake_text":b,
        "ignored":c,
        "enqueue":d,
        "process":e
    }

if __name__=="__main__":
    args=sys.argv[1:]
    cmd=args[0] if args else "status"
    no_speak="--no-speak" in args
    if cmd=="daemon":
        daemon("--continuous" in args)
    elif cmd=="start":
        print(json.dumps(start(continuous="--continuous" in args, speak=not no_speak),indent=4,ensure_ascii=False))
    elif cmd=="stop":
        print(json.dumps(stop(),indent=4,ensure_ascii=False))
    elif cmd=="once":
        secs=None
        for a in args[1:]:
            if a.isdigit():
                secs=int(a)
        print(json.dumps(voice_once(secs, speak_enabled=not no_speak),indent=4,ensure_ascii=False))
    elif cmd=="text":
        text=" ".join(a for a in args[1:] if a!="--no-speak")
        print(json.dumps(run_text(text, speak_enabled=not no_speak),indent=4,ensure_ascii=False))
    elif cmd=="wake-text":
        text=" ".join(a for a in args[1:] if a!="--no-speak")
        print(json.dumps(run_wake_text(text, speak_enabled=not no_speak),indent=4,ensure_ascii=False))
    elif cmd=="enqueue":
        text=" ".join(args[1:])
        print(json.dumps(enqueue_text(text),indent=4,ensure_ascii=False))
    elif cmd=="process":
        print(json.dumps(process_inbox_once(),indent=4,ensure_ascii=False))
    elif cmd=="test":
        print(json.dumps(test(),indent=4,ensure_ascii=False))
    else:
        print(json.dumps(runtime_status(),indent=4,ensure_ascii=False))
