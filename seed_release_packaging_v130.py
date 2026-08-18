import json,shutil,stat
from pathlib import Path
from datetime import datetime
def now(): return datetime.now().isoformat(timespec="seconds")
def write_cli():
    p=Path("seed"); p.write_text('#!/usr/bin/env python3\nimport sys,subprocess\ncmd=sys.argv[1] if len(sys.argv)>1 else "status"\nmap={"status":["python","seed_v123_130_mega.py","status"],"gate":["python","seed_v123_130_gate.py"],"dashboard":["python","seed_dashboard_v106.py","start"],"avatar":["python","seed_avatar2_v129.py","start"],"backup":["python","seed_release_packaging_v130.py","backup"]}\nsubprocess.run(map.get(cmd,["python","seed_v123_130_mega.py","status"]))\n'); p.chmod(0o755); return {"ok":True,"path":str(p)}
def backup():
    dest=Path.home()/("Desktop/seed_backup_v130_"+datetime.now().strftime("%Y%m%d_%H%M%S"))
    shutil.copytree(Path("."),dest,ignore=shutil.ignore_patterns("__pycache__",".git","third_party_repos"))
    return {"ok":True,"path":str(dest)}
def status(): return {"created_at":now(),"version":"v130.0.0","ok":True,"cli":write_cli(),"commands":["./seed status","./seed gate","./seed dashboard","./seed avatar","./seed backup"]}
if __name__=="__main__":
    import sys; print(json.dumps(backup() if len(sys.argv)>1 and sys.argv[1]=="backup" else status(),indent=4))
