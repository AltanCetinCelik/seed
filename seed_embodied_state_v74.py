import json
from datetime import datetime
from pathlib import Path

STATE_FILE = Path("seed_embodied_state_v74.json")
DEFAULT_STATE = {"version":"v74.0.0","mode":"idle","mode_reason":"Seed is online.","last_user":"","last_reply":"","last_transcript":"","last_model":None,"last_role":None,"session_count":0}

def now_timestamp(): return datetime.now().isoformat(timespec="seconds")

def load_state():
    if STATE_FILE.exists():
        try:
            data=json.loads(STATE_FILE.read_text(errors="ignore")); x=DEFAULT_STATE.copy(); x.update(data); return x
        except Exception: pass
    x=DEFAULT_STATE.copy(); x["created_at"]=now_timestamp(); STATE_FILE.write_text(json.dumps(x,indent=4,ensure_ascii=False)); return x

def save_state(**updates):
    x=load_state(); x.update(updates); x["updated_at"]=now_timestamp()
    if updates.get("last_user") or updates.get("last_reply") or updates.get("last_transcript"):
        x["session_count"]=int(x.get("session_count",0))+1
    STATE_FILE.write_text(json.dumps(x,indent=4,ensure_ascii=False)); return x

def set_mode(mode, reason=""): return save_state(mode=mode, mode_reason=reason)

def show_embodied_state():
    print("\n=== SEED v74 EMBODIED STATE ==="); print(json.dumps(load_state(), indent=4, ensure_ascii=False))
if __name__=="__main__": show_embodied_state()
