import json
from datetime import datetime
from pathlib import Path
OUT=Path("seed_voice_session_v72.json")
def now(): return datetime.now().isoformat(timespec="seconds")
def voice_session_status():
    try:
        from seed_voice_push_to_talk_v67 import voice_status
        base=voice_status()
    except Exception as e: base={"ok":False,"error":str(e)}
    data={"created_at":now(),"version":"v72.0.0","ok":True,"base_voice":base,"next_steps":["test microphone recording","route transcript into context-aware chat","optional macOS say output","save transcript","later wake word"]}
    OUT.write_text(json.dumps(data,indent=4,ensure_ascii=False)); return data
def show_voice_session(): print("\n=== SEED VOICE SESSION v72 ==="); print(json.dumps(voice_session_status(),indent=4,ensure_ascii=False))
if __name__ == "__main__": show_voice_session()
