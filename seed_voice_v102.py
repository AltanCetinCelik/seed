import json, subprocess, shutil
from pathlib import Path
from datetime import datetime
SET=Path("seed_voice_v102_settings.json"); DEFAULT={"version":"v102.0.0","mode":"normal","rate":185}
def now(): return datetime.now().isoformat(timespec="seconds")
def settings():
    if SET.exists():
        try:
            d=DEFAULT.copy(); d.update(json.loads(SET.read_text(errors="ignore"))); return d
        except Exception: pass
    SET.write_text(json.dumps(DEFAULT,indent=4)); return DEFAULT.copy()
def mode(m):
    d=settings(); d["mode"]=m; d["rate"]=155 if m=="night" else 205 if m=="excited" else 165 if m=="quiet" else 185; SET.write_text(json.dumps(d,indent=4)); return d
def speak(t):
    s=settings(); p=subprocess.run(["say","-r",str(s["rate"]),t[:900]],capture_output=True,text=True,timeout=80); return {"ok":p.returncode==0,"stderr":p.stderr}
def status(): return {"created_at":now(),"version":"v102.0.0","ok":True,"say":shutil.which("say"),"settings":settings()}
if __name__=="__main__":
    import sys
    if len(sys.argv)>2 and sys.argv[1]=="say": print(json.dumps(speak(" ".join(sys.argv[2:])),indent=4))
    elif len(sys.argv)>2 and sys.argv[1]=="mode": print(json.dumps(mode(sys.argv[2]),indent=4))
    else: print(json.dumps(status(),indent=4))
