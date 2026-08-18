import json, os, signal, subprocess, sys, time, urllib.request
from datetime import datetime
from pathlib import Path
SETTINGS_FILE=Path("seed_ambient_hearing_v89_settings.json"); PID_FILE=Path("seed_ambient_hearing_v89.pid"); STOP_FILE=Path("seed_ambient_hearing_v89.stop"); LOG_FILE=Path("seed_ambient_hearing_v89.log"); STATUS_FILE=Path("seed_ambient_hearing_v89_status.json")
DEFAULTS={"version":"v89.0.0","enabled":True,"chunk_seconds":9,"gap_seconds":0.7,"min_importance_to_note":62,"model":"gemma3:4b","fallback_model":"llama3.1:8b","ollama_url":"http://localhost:11434/api/generate","delete_audio_after_transcription":True,"store_raw_transcripts":False,"ignore_short_under_words":3}
NOISE={"thank you","thanks","okay","ok","hello","hi","eat","see it","see the","you","seed","hey seed","wake up"}
def now(): return datetime.now().isoformat(timespec="seconds")
def settings():
    if SETTINGS_FILE.exists():
        try: d=DEFAULTS.copy(); d.update(json.loads(SETTINGS_FILE.read_text(errors="ignore"))); return d
        except Exception: pass
    SETTINGS_FILE.write_text(json.dumps(DEFAULTS,indent=4,ensure_ascii=False)); return DEFAULTS.copy()
def status(**kw):
    d={"created_at":now(),"version":"v89.0.0"}; d.update(kw); STATUS_FILE.write_text(json.dumps(d,indent=4,ensure_ascii=False)); return d
def avatar(mode,msg):
    try:
        from seed_avatar_v89 import set_avatar_state
        set_avatar_state(mode=mode,emotion=mode,message=msg,hearing=(mode=="listening"),thinking=(mode=="thinking"))
    except Exception: pass
def record_transcribe(sec):
    audio=None
    try:
        from seed_live_voice_v731 import record_audio, transcribe_audio
        audio,dev=record_audio(sec); tr=transcribe_audio(audio); return {"ok":True,"audio_path":str(audio),"device":dev,"text":(tr.get("text") or "").strip()}
    except Exception as e: return {"ok":False,"audio_path":str(audio) if audio else None,"error":str(e),"text":""}
    finally:
        try:
            if audio and settings().get("delete_audio_after_transcription",True): Path(audio).unlink(missing_ok=True)
        except Exception: pass
def meaningful(t):
    x=" ".join(str(t or "").lower().split())
    return bool(x) and x not in NOISE and len(x.split())>=int(settings().get("ignore_short_under_words",3))
def ask_model(text):
    s=settings()
    prompt = "Seed ambient hearing filter. User wants no audio saved and no raw transcript stored. Return ONLY JSON with importance 0-100, summary, question, tags. Heard: " + text
    last=""
    for m in [s.get("model"),s.get("fallback_model")]:
        try:
            payload={"model":m,"prompt":prompt,"stream":False,"keep_alive":"30m","options":{"temperature":0.2,"num_predict":220}}
            req=urllib.request.Request(s.get("ollama_url"),data=json.dumps(payload).encode(),headers={"Content-Type":"application/json"},method="POST")
            raw=json.loads(urllib.request.urlopen(req,timeout=50).read().decode()).get("response","")
            a=raw.find("{"); b=raw.rfind("}")
            if a>=0 and b>a: return json.loads(raw[a:b+1])
            last=raw[:200]
        except Exception as e: last=str(e)
    return {"importance":65,"summary":"Heard something possibly relevant: "+text[:180],"question":"","tags":["hearing"],"fallback":True,"error":last}
def process_chunk():
    s=settings(); avatar("listening","Seed is listening ambiently. Audio will be deleted.")
    rec=record_transcribe(int(s.get("chunk_seconds",9))); text=(rec.get("text") or "").strip(); print(f"[hearing] {text or '[empty]'}")
    if not rec.get("ok"): return status(ok=False,mode="error",error=rec.get("error"),audio_deleted=True)
    if not meaningful(text): return status(ok=True,mode="ignored",audio_deleted=True,raw_transcript_saved=False)
    avatar("thinking","Seed is deciding if heard info matters.")
    n=ask_model(text); imp=int(n.get("importance",0) or 0); stored=False
    if imp>=int(s.get("min_importance_to_note",62)) and n.get("summary"):
        from seed_organism_notes_v89 import add_note
        add_note("hearing",n.get("summary",""),imp,n.get("question",""),n.get("tags",["hearing"]),{"raw_transcript_saved":False}); stored=True
    return status(ok=True,mode="listening",stored=stored,importance=imp,audio_deleted=True,raw_transcript_saved=False)
def loop():
    STOP_FILE.unlink(missing_ok=True); print("=== Seed v89 ambient hearing: no audio saved ===")
    while not STOP_FILE.exists():
        if settings().get("enabled",True):
            try: print(process_chunk())
            except Exception as e: print({"ok":False,"error":str(e)})
        time.sleep(float(settings().get("gap_seconds",.7)))
def alive(pid):
    try: os.kill(int(pid),0); return True
    except Exception: return False
def start_daemon():
    if PID_FILE.exists():
        try:
            pid=int(PID_FILE.read_text().strip())
            if alive(pid): return {"ok":True,"already_running":True,"pid":pid}
        except Exception: pass
    STOP_FILE.unlink(missing_ok=True); log=LOG_FILE.open("a"); p=subprocess.Popen([sys.executable,"seed_ambient_hearing_v89.py","loop"],stdout=log,stderr=log); PID_FILE.write_text(str(p.pid)); return {"ok":True,"pid":p.pid,"log":str(LOG_FILE)}
def stop_daemon():
    STOP_FILE.write_text(now()); pid=None; stopped=False
    if PID_FILE.exists():
        try:
            pid=int(PID_FILE.read_text().strip())
            if alive(pid): os.kill(pid,signal.SIGTERM); stopped=True
            PID_FILE.unlink(missing_ok=True)
        except Exception: pass
    return {"ok":True,"pid":pid,"stopped":stopped}
def hearing_status():
    pid=None; a=False
    if PID_FILE.exists():
        try: pid=int(PID_FILE.read_text().strip()); a=alive(pid)
        except Exception: pass
    rt={}
    if STATUS_FILE.exists():
        try: rt=json.loads(STATUS_FILE.read_text(errors="ignore"))
        except Exception: pass
    return {"created_at":now(),"version":"v89.0.0","ok":True,"pid":pid,"alive":a,"settings":settings(),"runtime_status":rt}
if __name__=="__main__":
    a=sys.argv[1] if len(sys.argv)>1 else "status"
    if a=="start": print(start_daemon())
    elif a=="stop": print(stop_daemon())
    elif a=="loop": loop()
    elif a=="once": print(process_chunk())
    else: print(json.dumps(hearing_status(),indent=4,ensure_ascii=False))
