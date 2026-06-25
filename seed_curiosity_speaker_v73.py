import json
import subprocess
import shutil
from datetime import datetime
from pathlib import Path

LOG = Path("seed_curiosity_spoken_v73.jsonl")

def now_timestamp():
    return datetime.now().isoformat(timespec="seconds")

def speak_text(text):
    say = shutil.which("say")
    if not say:
        return False
    subprocess.run([say, str(text)[:900]], timeout=60)
    return True

def build_spoken_curiosity(speak=False):
    try:
        from seed_curiosity_engine_v72 import best_curiosity
        c = best_curiosity()
    except Exception as error:
        c = {"title": "Curiosity unavailable", "body": str(error), "why": "error", "category": "error"}
    line = f"I noticed this: {c.get('title')}. {c.get('body')} Why I spoke: {c.get('why')}"
    row = {"created_at": now_timestamp(), "version": "v73.0.0", "ok": True, "speak": speak, "line": line, "curiosity": c}
    with LOG.open("a") as f:
        f.write(json.dumps(row, ensure_ascii=False) + "\n")
    if speak:
        speak_text(line)
    return row

def show_spoken_curiosity():
    row = build_spoken_curiosity(False)
    print("\n=== SEED v73 SPOKEN CURIOSITY ===")
    print(row["line"])
    return "handled"

def say_curiosity():
    row = build_spoken_curiosity(True)
    print(row["line"])
    return "handled"

if __name__ == "__main__":
    show_spoken_curiosity()
