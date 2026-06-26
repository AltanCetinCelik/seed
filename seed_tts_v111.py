import json,shutil,subprocess,sys
from pathlib import Path
from datetime import datetime
SETTINGS=Path("seed_tts_v111_settings.json")
DEFAULT={"version":"v111.1.0","engine":"auto","mode":"normal","rate":185,"piper_binary":"","piper_model":"","voice":"","timeout_seconds":90}
def now(): return datetime.now().isoformat(timespec="seconds")
def settings():
    if SETTINGS.exists():
        try:
            d=DEFAULT.copy(); d.update(json.loads(SETTINGS.read_text(errors="ignore"))); d["version"]="v111.1.0"; return d
        except Exception: pass
    SETTINGS.write_text(json.dumps(DEFAULT,indent=4)); return DEFAULT.copy()
def save(d): d["version"]="v111.1.0"; SETTINGS.write_text(json.dumps(d,indent=4)); return d
def detect(): return {"say":shutil.which("say"),"piper":shutil.which("piper"),"piper_model_exists":bool(settings().get("piper_model") and Path(settings().get("piper_model")).exists())}
def readiness():
    d=detect()
    if d["piper"] and d["piper_model_exists"]: return {"ready":True,"engine":"piper","level":"configured"}
    if d["say"]: return {"ready":True,"engine":"macos_say","level":"fallback"}
    return {"ready":False,"engine":"none","level":"missing"}
def say(text):
    s=settings(); text=str(text)[:1200]; d=detect(); piper=s.get("piper_binary") or d["piper"]
    if piper and s.get("piper_model") and Path(s["piper_model"]).exists() and s.get("engine") in {"auto","piper"}:
        pr=subprocess.run([piper,"--model",s["piper_model"],"--output_file","/tmp/seed_tts.wav"],input=text,capture_output=True,text=True,timeout=int(s["timeout_seconds"]))
        return {"ok":pr.returncode==0,"engine":"piper","stderr":pr.stderr[-1000:],"audio":"/tmp/seed_tts.wav"}
    cmd=["say","-r",str(s.get("rate",185))]
    if s.get("voice"): cmd+=["-v",s["voice"]]
    cmd.append(text); pr=subprocess.run(cmd,capture_output=True,text=True,timeout=int(s["timeout_seconds"]))
    return {"ok":pr.returncode==0,"engine":"macos_say","stderr":pr.stderr[-1000:]}
def status(): return {"created_at":now(),"version":"v111.1.0","ok":True,"detect":detect(),"settings":settings(),"readiness":readiness(),"recommendations":[] if readiness()["engine"]=="piper" else ["Piper not configured; macOS say is official fallback."]}
if __name__=="__main__":
    a=sys.argv[1] if len(sys.argv)>1 else "status"
    print(json.dumps(say(" ".join(sys.argv[2:])) if a=="say" else status(),indent=4,ensure_ascii=False))
