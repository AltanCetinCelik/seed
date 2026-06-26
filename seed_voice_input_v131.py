import json, shutil, subprocess, sys, time
from pathlib import Path
from datetime import datetime
SETTINGS=Path("seed_voice_input_v131_settings.json")
LOG=Path("seed_voice_input_v131_transcripts.jsonl")
TEMP=Path("seed_voice_temp_v131")
DEFAULT={"version":"v131.1.0","faster_whisper_model":"","language":"auto","record_seconds":5,"sample_rate":16000,"store_raw_audio":False,"delete_audio_after_transcribe":True,"timeout_seconds":180,"avfoundation_audio_device":":0","audio_device_index":"0","min_transcript_chars":8,"min_transcript_words":2,"bad_transcript_phrases":["you","thank you","thanks","okay","ok",".","uh","um","hmm"],"repeat_if_empty":True}
def now(): return datetime.now().isoformat(timespec="seconds")
def has(mod):
    import importlib.util
    return importlib.util.find_spec(mod) is not None
def settings():
    if SETTINGS.exists():
        try:
            d=DEFAULT.copy(); d.update(json.loads(SETTINGS.read_text(errors="ignore"))); d["version"]="v131.1.0"; return d
        except Exception: pass
    SETTINGS.write_text(json.dumps(DEFAULT,indent=4,ensure_ascii=False)); return DEFAULT.copy()
def save(d): d["version"]="v131.1.0"; SETTINGS.write_text(json.dumps(d,indent=4,ensure_ascii=False)); return d
def detect(): return {"ffmpeg":shutil.which("ffmpeg"),"faster_whisper":has("faster_whisper"),"sounddevice":has("sounddevice")}
def readiness():
    s=settings(); d=detect()
    if d["faster_whisper"] and s.get("faster_whisper_model"): return {"ready":True,"engine":"faster_whisper","level":"configured_or_downloadable"}
    if d["faster_whisper"]: return {"ready":False,"engine":"faster_whisper","level":"installed_not_configured"}
    return {"ready":False,"engine":"none","level":"missing_engine"}
def setup_model(model="base"):
    s=settings(); s["faster_whisper_model"]=model; save(s); return status()
def configure(**kwargs):
    s=settings()
    for k,v in kwargs.items():
        if k in s and v not in {None,""}:
            if k in {"record_seconds","sample_rate","timeout_seconds","min_transcript_chars","min_transcript_words"}:
                try: v=int(v)
                except Exception: pass
            if k in {"store_raw_audio","delete_audio_after_transcribe","repeat_if_empty"}:
                v=str(v).lower() in {"1","true","yes","on"}
            s[k]=v
    save(s); return status()
def validate(text):
    try:
        import seed_voice_calibration_v1351 as cal
        return cal.validate_transcript(text)
    except Exception:
        t=str(text or "").strip()
        return {"ok":bool(t and t.lower()!="you" and len(t)>=8),"text":t,"reason":None if t and t.lower()!="you" and len(t)>=8 else "bad_transcript"}
def record_audio(seconds=None):
    s=settings(); TEMP.mkdir(exist_ok=True); seconds=int(seconds or s.get("record_seconds",5))
    path=TEMP/f"seed_voice_{int(time.time()*1000)}.wav"
    if not shutil.which("ffmpeg"): return {"ok":False,"error":"ffmpeg missing"}
    cmd=["ffmpeg","-y","-f","avfoundation","-i",s.get("avfoundation_audio_device",":0"),"-t",str(seconds),"-ar",str(s.get("sample_rate",16000)),"-ac","1",str(path)]
    p=subprocess.run(cmd,capture_output=True,text=True,timeout=seconds+40)
    res={"ok":p.returncode==0,"path":str(path),"device":s.get("avfoundation_audio_device",":0"),"stderr":p.stderr[-1800:]}
    if path.exists(): res["size_bytes"]=path.stat().st_size
    return res
def transcribe_file(audio_path):
    p=Path(audio_path); s=settings(); r=readiness()
    if not p.exists(): return {"ok":False,"error":"audio file not found","path":str(p)}
    if not r["ready"]: return {"ok":False,"error":"voice input not configured","readiness":r,"path":str(p)}
    try:
        from faster_whisper import WhisperModel
        model=WhisperModel(s["faster_whisper_model"],device="auto",compute_type="auto")
        segs,info=model.transcribe(str(p),language=None if s.get("language")=="auto" else s.get("language"))
        raw=" ".join(seg.text.strip() for seg in segs).strip()
        val=validate(raw)
        row={"created_at":now(),"version":"v131.1.0","ok":val.get("ok",False),"engine":"faster_whisper","text":raw if val.get("ok") else "","raw_text":raw,"validation":val,"language":getattr(info,"language",None)}
        if not val.get("ok"): row["error"]="bad_or_empty_transcript"
    except Exception as e:
        row={"created_at":now(),"version":"v131.1.0","ok":False,"error":str(e)}
    with LOG.open("a") as f: f.write(json.dumps(row,ensure_ascii=False)+"\n")
    if s.get("delete_audio_after_transcribe",True) and not s.get("store_raw_audio",False):
        try: p.unlink(missing_ok=True); row["audio_deleted"]=True
        except Exception: pass
    return row
def listen_once(seconds=None, repeats=None):
    s=settings(); repeats=int(repeats if repeats is not None else (2 if s.get("repeat_if_empty",True) else 1))
    attempts=[]
    for i in range(max(1,repeats)):
        rec=record_audio(seconds)
        if not rec.get("ok"): return {"ok":False,"stage":"record","attempt":i+1,"record":rec,"status":status()}
        tr=transcribe_file(rec["path"])
        attempts.append({"record":rec,"transcript":tr})
        if tr.get("ok"): return {"ok":True,"stage":"transcribe","attempts":attempts,"transcript":tr}
    return {"ok":False,"stage":"bad_transcript","attempts":attempts,"message":"I could not hear clearly. Try another mic device or speak closer."}
def test():
    return {"created_at":now(),"version":"v131.1.0","ok":True,"readiness":readiness(),"validation":{"you":validate("You"),"good":validate("Seed status how many systems are green")},"privacy":{"store_raw_audio":settings().get("store_raw_audio"),"delete_audio_after_transcribe":settings().get("delete_audio_after_transcribe")}}
def status():
    return {"created_at":now(),"version":"v131.1.0","ok":True,"detect":detect(),"readiness":readiness(),"settings":settings(),"validation_tests":{"you":validate("You"),"good":validate("Seed status how many systems are green")}}
if __name__=="__main__":
    a=sys.argv[1] if len(sys.argv)>1 else "status"
    if a=="setup-model": print(json.dumps(setup_model(sys.argv[2] if len(sys.argv)>2 else "base"),indent=4,ensure_ascii=False))
    elif a=="configure":
        args=dict(x.split("=",1) for x in sys.argv[2:] if "=" in x); print(json.dumps(configure(**args),indent=4,ensure_ascii=False))
    elif a=="record": print(json.dumps(record_audio(int(sys.argv[2]) if len(sys.argv)>2 else None),indent=4,ensure_ascii=False))
    elif a=="transcribe": print(json.dumps(transcribe_file(sys.argv[2]),indent=4,ensure_ascii=False))
    elif a=="listen-once": print(json.dumps(listen_once(int(sys.argv[2]) if len(sys.argv)>2 and sys.argv[2].isdigit() else None),indent=4,ensure_ascii=False))
    elif a=="test": print(json.dumps(test(),indent=4,ensure_ascii=False))
    else: print(json.dumps(status(),indent=4,ensure_ascii=False))
