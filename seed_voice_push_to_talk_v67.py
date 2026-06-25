import json, shutil
from pathlib import Path
from datetime import datetime
VOICE_FILE=Path("seed_voice_push_to_talk_v67.json")
def avail(name):
    try: __import__(name); return True
    except Exception: return False
def voice_status():
    data={"created_at":datetime.now().isoformat(timespec="seconds"),"version":"v70.0.0","ok":True,"tools":{"sox_rec":shutil.which("rec"),"ffmpeg":shutil.which("ffmpeg"),"faster_whisper":avail("faster_whisper"),"macos_say":shutil.which("say")},"path":"record -> transcribe -> natural intent route -> optional say -> journal"}; VOICE_FILE.write_text(json.dumps(data,indent=4)); return data
def show_voice_ptt_status(): print(json.dumps(voice_status(),indent=4))
def show_voice_record(): print("Voice recording path is scaffolded. Install sox/ffmpeg for recording.")
if __name__=="__main__": show_voice_ptt_status()
