import json
import shutil
import subprocess
from datetime import datetime
from pathlib import Path

VOICE_DIR = Path("seed_voice_v73")
VOICE_DIR.mkdir(exist_ok=True)
JOURNAL = Path("seed_voice_journal_v73.jsonl")

def now_timestamp():
    return datetime.now().isoformat(timespec="seconds")

def _has_faster_whisper():
    try:
        import faster_whisper  # noqa
        return True
    except Exception:
        return False

def voice_tools():
    return {
        "ffmpeg": shutil.which("ffmpeg"),
        "macos_say": shutil.which("say"),
        "faster_whisper": _has_faster_whisper()
    }

def record_audio(seconds=5):
    ffmpeg = shutil.which("ffmpeg")
    if not ffmpeg:
        raise RuntimeError("ffmpeg not found")
    out = VOICE_DIR / f"voice_{datetime.now().strftime('%Y%m%d_%H%M%S')}.wav"
    cmd = [ffmpeg, "-y", "-f", "avfoundation", "-i", ":0", "-t", str(seconds), "-ar", "16000", "-ac", "1", str(out)]
    proc = subprocess.run(cmd, capture_output=True, text=True, timeout=seconds + 25)
    if proc.returncode != 0:
        raise RuntimeError(proc.stderr[-1200:])
    return out

def transcribe_audio(path):
    try:
        from faster_whisper import WhisperModel
    except Exception as error:
        raise RuntimeError(f"faster_whisper unavailable: {error}")
    model = WhisperModel("base", device="cpu", compute_type="int8")
    segments, info = model.transcribe(str(path), beam_size=1)
    text = " ".join(seg.text.strip() for seg in segments).strip()
    return {"text": text, "language": getattr(info, "language", None)}

def speak(text):
    say = shutil.which("say")
    if not say:
        return False
    subprocess.run([say, str(text)[:900]], timeout=60)
    return True

def log_voice(row):
    row["created_at"] = now_timestamp()
    with JOURNAL.open("a") as f:
        f.write(json.dumps(row, ensure_ascii=False) + "\n")

def voice_once(seconds=5, speak_reply=True):
    print(f"Recording {seconds}s...")
    audio = record_audio(seconds)
    print(f"Recorded: {audio}")
    transcript = transcribe_audio(audio)
    text = transcript.get("text", "")
    print(f"Transcript: {text}")
    reply = ""
    try:
        from seed_local_chat_v701 import choose_role, model_fallbacks, call_ollama
        role = choose_role(text)
        model = model_fallbacks(role)[0]
        print(f"Using {model} for voice/{role}.")
        reply = call_ollama(model, role, text)
        print(f"Seed: {reply}")
        if speak_reply:
            speak(reply)
    except Exception as error:
        reply = f"Voice routed transcript, but chat failed: {error}"
        print(reply)
    log_voice({"audio": str(audio), "transcript": text, "reply": reply})
    return {"ok": True, "audio": str(audio), "transcript": text, "reply": reply}

def show_voice_live_status():
    print("\n=== SEED v73 LIVE VOICE ===")
    print(json.dumps({"created_at": now_timestamp(), "version": "v73.0.0", "ok": True, "tools": voice_tools(), "commands": ["voice once", "voice once 8", "voice status"]}, indent=4, ensure_ascii=False))
    return "handled"

if __name__ == "__main__":
    show_voice_live_status()
