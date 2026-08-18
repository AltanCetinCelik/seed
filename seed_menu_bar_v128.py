import json,stat
from pathlib import Path
from datetime import datetime
LAUNCHER=Path("Seed Control.command")
def now(): return datetime.now().isoformat(timespec="seconds")
def install_launcher():
    LAUNCHER.write_text('#!/bin/zsh\ncd "$HOME/Desktop/seed" || exit 1\npython seed_dashboard_v106.py start\npython seed_v123_130_mega.py status\n')
    LAUNCHER.chmod(LAUNCHER.stat().st_mode | stat.S_IXUSR)
    return {"ok":True,"path":str(LAUNCHER)}
def status(): return {"created_at":now(),"version":"v128.0.0","ok":True,"installed":LAUNCHER.exists(),"launcher":install_launcher(),"commands":["dashboard","status","gate","backup"]}
if __name__=="__main__":
    import json; print(json.dumps(status(),indent=4))
