import json,shutil,subprocess,sys
from datetime import datetime
from pathlib import Path
SETTINGS=Path("seed_stt_v110_settings.json")
DEFAULT={"version":"v110.1.0","engine":"auto","whisper_cpp_binary":"","model_path":"","faster_whisper_model":"","language":"auto","store_raw_audio":False,"timeout_seconds":120}
def now(): return datetime.now().isoformat(timespec="seconds")
def settings():
    if SETTINGS.exists():
        try:
            d=DEFAULT.copy(); d.update(json.loads(SETTINGS.read_text(errors="ignore"))); d["version"]="v110.1.0"; return d
        except Exception: pass
    SETTINGS.write_text(json.dumps(DEFAULT,indent=4)); return DEFAULT.copy()
def has(m):
    import importlib.util; return importlib.util.find_spec(m) is not None
def detect(): return {"whisper_cli":shutil.which("whisper-cli"),"whisper_main":shutil.which("main"),"ffmpeg":shutil.which("ffmpeg"),"faster_whisper":has("faster_whisper"),"python_whisper":has("whisper")}
def binary():
    s=settings(); return s.get("whisper_cpp_binary") if s.get("whisper_cpp_binary") and Path(s["whisper_cpp_binary"]).exists() else (shutil.which("whisper-cli") or shutil.which("main"))
def readiness():
    s=settings(); d=detect(); b=binary()
    if b and s.get("model_path") and Path(s["model_path"]).exists(): return {"ready":True,"engine":"whisper.cpp","level":"configured"}
    if d["faster_whisper"] and s.get("faster_whisper_model"): return {"ready":True,"engine":"faster_whisper","level":"configured_or_downloadable"}
    if d["faster_whisper"]: return {"ready":False,"engine":"faster_whisper","level":"installed_not_configured"}
    return {"ready":False,"engine":"none","level":"missing_engine"}
def recommendations():
    r=readiness(); rec=[]
    if r["level"]=="installed_not_configured": rec.append('Set faster_whisper_model in seed_stt_v110_settings.json, e.g. "base" or "small".')
    if not binary(): rec.append("Install whisper.cpp binary if you want native whisper.cpp path.")
    if not settings().get("model_path"): rec.append("For whisper.cpp set model_path to a local ggml model.")
    return rec
def transcribe(path):
    p=Path(path)
    if not p.exists(): return {"ok":False,"error":"audio file not found"}
    s=settings(); r=readiness()
    if r["engine"]=="whisper.cpp" and r["ready"]:
        cmd=[binary(),"-m",s["model_path"],"-f",str(p)]
        pr=subprocess.run(cmd,capture_output=True,text=True,timeout=int(s.get("timeout_seconds",120)))
        return {"ok":pr.returncode==0,"engine":"whisper.cpp","text":(pr.stdout+"\n"+pr.stderr)[-6000:],"cmd":cmd}
    if r["engine"]=="faster_whisper" and r["ready"]:
        try:
            from faster_whisper import WhisperModel
            model=WhisperModel(s["faster_whisper_model"],device="auto",compute_type="auto")
            segs,info=model.transcribe(str(p),language=None if s.get("language")=="auto" else s.get("language"))
            return {"ok":True,"engine":"faster_whisper","text":" ".join(seg.text.strip() for seg in segs),"language":getattr(info,"language",None)}
        except Exception as e: return {"ok":False,"engine":"faster_whisper","error":str(e)}
    return {"ok":False,"error":"STT installed but not configured","readiness":r,"status":status()}
def status(): return {"created_at":now(),"version":"v110.1.0","ok":True,"detect":detect(),"chosen_binary":binary(),"settings":settings(),"readiness":readiness(),"ready":readiness()["ready"],"recommendations":recommendations()}
def test(): return {"created_at":now(),"version":"v110.1.0","ok":True,"status":status()}
if __name__=="__main__":
    a=sys.argv[1] if len(sys.argv)>1 else "status"
    print(json.dumps(transcribe(sys.argv[2] if len(sys.argv)>2 else "") if a=="transcribe" else test() if a=="test" else status(),indent=4,ensure_ascii=False))
