import json, shutil, subprocess
from datetime import datetime
def now(): return datetime.now().isoformat(timespec="seconds")
def status(): return {"created_at":now(),"version":"v101.0.0","ok":True,"aider":shutil.which("aider"),"mode":"plan_and_dry_run_first"}
def plan(req): return {"ok":True,"request":req,"steps":["git status","plan","ask approval","edit/diff","test","commit only after green"]}
if __name__=="__main__":
    import sys
    print(json.dumps(plan(" ".join(sys.argv[2:])) if len(sys.argv)>1 and sys.argv[1]=="plan" else status(),indent=4,ensure_ascii=False))
