import json, re, shutil, subprocess, sys, time
from pathlib import Path
from datetime import datetime

VOICE_SETTINGS = Path("seed_voice_input_v131_settings.json")
CAL_LOG = Path("seed_voice_calibration_v1351.jsonl")
TEMP = Path("seed_voice_temp_v131")
DEFAULT_PATCH = {
    "avfoundation_audio_device": ":0",
    "audio_device_index": "0",
    "min_transcript_chars": 8,
    "min_transcript_words": 2,
    "bad_transcript_phrases": ["you", "thank you", "thanks", "okay", "ok", ".", "uh", "um", "hmm"],
    "repeat_if_empty": True,
    "mean_volume_warn_below_db": -45.0,
    "max_volume_warn_below_db": -35.0
}
def now(): return datetime.now().isoformat(timespec="seconds")
def read_settings():
    if VOICE_SETTINGS.exists():
        try: d=json.loads(VOICE_SETTINGS.read_text(errors="ignore"))
        except Exception: d={}
    else: d={}
    for k,v in DEFAULT_PATCH.items():
        d.setdefault(k,v)
    d["version"]="v131.1.0"
    VOICE_SETTINGS.write_text(json.dumps(d,indent=4,ensure_ascii=False))
    return d
def save_settings(d):
    d["version"]="v131.1.0"; VOICE_SETTINGS.write_text(json.dumps(d,indent=4,ensure_ascii=False)); return d
def log(row):
    row.setdefault("created_at",now()); row.setdefault("version","v135.1.0")
    with CAL_LOG.open("a") as f: f.write(json.dumps(row,ensure_ascii=False)+"\n")
    return row
def list_devices():
    if not shutil.which("ffmpeg"): return {"ok":False,"error":"ffmpeg missing"}
    p=subprocess.run(["ffmpeg","-f","avfoundation","-list_devices","true","-i",""],capture_output=True,text=True,timeout=15)
    raw=(p.stderr or "")+"\n"+(p.stdout or "")
    audio=[]; in_audio=False
    for line in raw.splitlines():
        if "AVFoundation audio devices" in line: in_audio=True; continue
        if "AVFoundation video devices" in line: in_audio=False
        if in_audio:
            m=re.search(r"\[(\d+)\]\s+(.+)$", line.strip())
            if m: audio.append({"index":m.group(1),"name":m.group(2).strip()})
    return {"ok":True,"audio_devices":audio,"raw":raw[-4000:],"current":read_settings().get("avfoundation_audio_device",":0")}
def set_device(index):
    d=read_settings(); idx=str(index).strip().lstrip(":")
    d["audio_device_index"]=idx; d["avfoundation_audio_device"]=":"+idx
    return {"ok":True,"settings":save_settings(d)}
def set_language(language="auto"):
    language=str(language).strip().lower()
    if language not in {"auto","en","tr"}: return {"ok":False,"error":"language must be auto, en, or tr"}
    d=read_settings(); d["language"]=language
    return {"ok":True,"settings":save_settings(d)}
def validate_transcript(text):
    s=read_settings(); t=str(text or "").strip(); low=re.sub(r"\s+"," ",t.lower()).strip()
    words=[w for w in re.findall(r"[\wçğıöşüİı]+", low) if w]
    bad=set(str(x).lower().strip() for x in s.get("bad_transcript_phrases",[]))
    reason=None
    if not t: reason="empty"
    elif low in bad: reason="known_hallucination"
    elif len(t)<int(s.get("min_transcript_chars",8)): reason="too_short"
    elif len(words)<int(s.get("min_transcript_words",2)): reason="too_few_words"
    elif len(words)>1 and len(set(words))==1: reason="repeated_single_word"
    return {"ok":reason is None,"text":t,"normalized":low,"word_count":len(words),"char_count":len(t),"reason":reason}
def volume_report(path):
    if not shutil.which("ffmpeg"): return {"ok":False,"error":"ffmpeg missing"}
    p=subprocess.run(["ffmpeg","-hide_banner","-i",str(path),"-af","volumedetect","-f","null","-"],capture_output=True,text=True,timeout=40)
    raw=p.stderr or ""; mean=None; maxv=None
    m=re.search(r"mean_volume:\s*(-?\d+(?:\.\d+)?) dB", raw)
    if m: mean=float(m.group(1))
    m=re.search(r"max_volume:\s*(-?\d+(?:\.\d+)?) dB", raw)
    if m: maxv=float(m.group(1))
    s=read_settings(); warning=[]
    if mean is not None and mean<float(s.get("mean_volume_warn_below_db",-45.0)): warning.append("mean_volume_low")
    if maxv is not None and maxv<float(s.get("max_volume_warn_below_db",-35.0)): warning.append("max_volume_low")
    return {"ok":p.returncode==0,"mean_volume_db":mean,"max_volume_db":maxv,"warning":warning,"raw":raw[-1500:]}
def record_sample(seconds=5, keep=False):
    s=read_settings(); TEMP.mkdir(exist_ok=True)
    path=TEMP/f"seed_calibration_{int(time.time()*1000)}.wav"
    if not shutil.which("ffmpeg"): return {"ok":False,"error":"ffmpeg missing"}
    cmd=["ffmpeg","-y","-f","avfoundation","-i",s.get("avfoundation_audio_device",":0"),"-t",str(int(seconds)),"-ar",str(s.get("sample_rate",16000)),"-ac","1",str(path)]
    p=subprocess.run(cmd,capture_output=True,text=True,timeout=int(seconds)+40)
    res={"ok":p.returncode==0,"path":str(path),"device":s.get("avfoundation_audio_device",":0"),"seconds":int(seconds),"stderr":p.stderr[-2500:]}
    if p.returncode==0 and path.exists():
        res["size_bytes"]=path.stat().st_size; res["volume"]=volume_report(path)
    if not keep and path.exists():
        try: path.unlink(); res["audio_deleted"]=True
        except Exception: res["audio_deleted"]=False
    log({"event":"record_sample","result":res}); return res
def transcribe_test(seconds=6, keep=False):
    rec=record_sample(seconds, keep=True)
    if not rec.get("ok"): return {"ok":False,"stage":"record","record":rec}
    try:
        import seed_voice_input_v131 as vi
        tr=vi.transcribe_file(rec["path"])
    except Exception as e:
        tr={"ok":False,"error":str(e)}
    val=validate_transcript(tr.get("text") or tr.get("raw_text") or "")
    if not keep:
        try: Path(rec["path"]).unlink(missing_ok=True); rec["audio_deleted"]=True
        except Exception: pass
    out={"ok":tr.get("ok",False) and val.get("ok",False),"record":rec,"transcript":tr,"validation":val}
    log({"event":"transcribe_test","result":out}); return out
def status():
    return {"created_at":now(),"version":"v135.1.0","ok":True,"settings":read_settings(),"devices":list_devices(),"validation_tests":{"you":validate_transcript("You"),"good":validate_transcript("Seed status how many systems are green")}}
if __name__=="__main__":
    a=sys.argv[1] if len(sys.argv)>1 else "status"
    if a=="devices": print(json.dumps(list_devices(),indent=4,ensure_ascii=False))
    elif a=="set-device": print(json.dumps(set_device(sys.argv[2]),indent=4,ensure_ascii=False))
    elif a=="set-language": print(json.dumps(set_language(sys.argv[2] if len(sys.argv)>2 else "auto"),indent=4,ensure_ascii=False))
    elif a=="validate": print(json.dumps(validate_transcript(" ".join(sys.argv[2:])),indent=4,ensure_ascii=False))
    elif a=="record-test": print(json.dumps(record_sample(int(sys.argv[2]) if len(sys.argv)>2 else 5, "--keep" in sys.argv),indent=4,ensure_ascii=False))
    elif a=="transcribe-test": print(json.dumps(transcribe_test(int(sys.argv[2]) if len(sys.argv)>2 else 6, "--keep" in sys.argv),indent=4,ensure_ascii=False))
    else: print(json.dumps(status(),indent=4,ensure_ascii=False))
