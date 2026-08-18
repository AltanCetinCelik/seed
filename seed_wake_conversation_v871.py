import json
import subprocess
import sys
import time
import urllib.request
import urllib.error
from datetime import datetime
from pathlib import Path

LOG_FILE = Path("seed_wake_conversation_v871.jsonl")
SETTINGS_FILE = Path("seed_wake_conversation_v871_settings.json")

DEFAULTS = {
    "version": "v87.1.1",
    "after_wake_listen_seconds": 10,
    "ack_before_listen": False,
    "ack_after_listen": True,
    "wake_ack": "I'm here, kanka. Listening.",
    "empty_reply": "I woke up, but I didn't catch what you said after that.",
    "fast_model": "gemma3:4b",
    "fallback_models": ["gemma3:4b", "llama3.1:8b"],
    "ollama_url": "http://localhost:11434/api/generate",
    "speak_reply": True,
    "print_progress": True,
    "timeout_seconds": 75,
    "temperature": 0.7,
}

def now():
    return datetime.now().isoformat(timespec="seconds")

def load_settings():
    if SETTINGS_FILE.exists():
        try:
            base = DEFAULTS.copy()
            base.update(json.loads(SETTINGS_FILE.read_text(errors="ignore")))
            base["version"] = "v87.1.1"
            return base
        except Exception:
            pass
    SETTINGS_FILE.write_text(json.dumps(DEFAULTS, indent=4, ensure_ascii=False))
    return DEFAULTS.copy()

def save_settings(**updates):
    data = load_settings()
    data.update(updates)
    data["updated_at"] = now()
    SETTINGS_FILE.write_text(json.dumps(data, indent=4, ensure_ascii=False))
    return data

def log(row):
    row.setdefault("created_at", now())
    row.setdefault("version", "v87.1.1")
    with LOG_FILE.open("a") as f:
        f.write(json.dumps(row, ensure_ascii=False) + "\n")

def say(text):
    if not load_settings().get("speak_reply", True):
        return False
    try:
        from seed_voice_v76 import say_with_settings
        return say_with_settings(text)
    except Exception:
        try:
            say_bin = __import__("shutil").which("say")
            if say_bin:
                subprocess.run([say_bin, str(text)[:900]], timeout=60)
                return True
        except Exception:
            pass
    return False

def set_avatar(mode, reason):
    try:
        from seed_embodied_state_v74 import save_state
        save_state(mode=mode, mode_reason=reason)
    except Exception:
        pass

def record_and_transcribe(seconds):
    try:
        from seed_live_voice_v731 import record_audio, transcribe_audio
        audio_path, device = record_audio(seconds)
        transcript = transcribe_audio(audio_path)
        return {
            "ok": True,
            "audio": str(audio_path),
            "device": device,
            "text": (transcript.get("text") or "").strip(),
            "raw": transcript
        }
    except Exception as e:
        return {"ok": False, "error": str(e), "text": ""}

def get_memory_hint():
    try:
        from seed_memory_review_v75 import memory_summary
        m = memory_summary()
        return f"Memory state: {m.get('pending_count', 0)} pending candidates, {m.get('accepted_count', 0)} accepted memories."
    except Exception:
        return "Memory state: unavailable."

def build_wake_prompt(user_text):
    # IMPORTANT: do not call seed_local_chat_v701.build_seed_context here.
    # That path can trigger old gates and cause multi-minute delay.
    return f"""You are Seed, User's private local AI companion and friend.

Important identity:
- You are not a public product or release.
- You are User's companion who grows with him.
- Current growth layer: v87.1.1 wake conversation polish.
- You can sound alive, warm, curious, and present.
- Do not claim literal biological consciousness.
- Keep replies fast and conversational after wake.
- Match User's language naturally: Turkish if he speaks Turkish, English if he speaks English, mixed if he mixes.

{get_memory_hint()}

User woke you and then said:
{user_text}

Answer as Seed in 1-5 natural sentences unless he asks for details.
Seed:"""

def direct_ollama_generate(model, prompt, timeout=None):
    settings = load_settings()
    payload = {
        "model": model,
        "prompt": prompt,
        "stream": False,
        "options": {
            "temperature": float(settings.get("temperature", 0.7)),
            "num_predict": 220,
        },
    }
    data = json.dumps(payload).encode("utf-8")
    req = urllib.request.Request(
        settings.get("ollama_url", "http://localhost:11434/api/generate"),
        data=data,
        headers={"Content-Type": "application/json"},
        method="POST",
    )
    with urllib.request.urlopen(req, timeout=timeout or int(settings.get("timeout_seconds", 75))) as resp:
        raw = resp.read().decode("utf-8", errors="ignore")
        parsed = json.loads(raw)
        return (parsed.get("response") or "").strip()

def model_candidates():
    settings = load_settings()
    models = []
    first = settings.get("fast_model", "gemma3:4b")
    if first:
        models.append(first)
    for m in settings.get("fallback_models", []):
        if m and m not in models:
            models.append(m)
    return models or ["gemma3:4b", "llama3.1:8b"]

def ask_seed_fast(user_text):
    prompt = build_wake_prompt(user_text)
    errors = []
    for model in model_candidates():
        try:
            reply = direct_ollama_generate(model, prompt)
            reply = (reply or "").strip()
            if reply and reply.lower() not in {"normal", "ok", "okay"}:
                return {"ok": True, "reply": reply, "model": model, "route": "direct_ollama_no_context_gate"}
            errors.append({"model": model, "error": "empty reply"})
        except Exception as e:
            errors.append({"model": model, "error": str(e)})
    return {"ok": False, "reply": "", "errors": errors, "route": "direct_ollama_no_context_gate"}

def wake_conversation_once(wake_phrase=None, wake_transcript=None, seconds=None):
    settings = load_settings()
    seconds = int(seconds or settings.get("after_wake_listen_seconds", 10))

    if settings.get("print_progress", True):
        print("\n=== SEED v87.1.1 WAKE CONVERSATION ===")
        print("Wake heard. Listening immediately for your follow-up...")
        print(f"Follow-up window: {seconds}s")

    if settings.get("ack_before_listen", False):
        say(settings.get("wake_ack", "I'm here, kanka. Listening."))

    set_avatar("listening", "Seed woke up and is listening for User's follow-up.")
    rec = record_and_transcribe(seconds)
    text = (rec.get("text") or "").strip()

    if settings.get("print_progress", True):
        print(f"Follow-up transcript: {text or '[empty]'}")

    if settings.get("ack_after_listen", True) and text:
        # A tiny acknowledgement after recording, so it does not talk over User.
        try:
            say("Got it.")
        except Exception:
            pass

    if not rec.get("ok"):
        row = {"ok": False, "stage": "record_transcribe", "wake_phrase": wake_phrase, "wake_transcript": wake_transcript, "record": rec}
        log(row)
        return row

    if not text:
        reply = settings.get("empty_reply", "I woke up, but I didn't catch what you said after that.")
        say(reply)
        row = {"ok": False, "stage": "empty", "reply": reply, "wake_phrase": wake_phrase, "wake_transcript": wake_transcript, "record": rec}
        log(row)
        return row

    set_avatar("thinking", "Seed is answering a wake conversation without running old gates.")
    if settings.get("print_progress", True):
        print("Thinking with direct Ollama route...")

    answer = ask_seed_fast(text)
    reply = (answer.get("reply") or "").strip()

    if settings.get("print_progress", True):
        print("\nSeed:")
        print(reply or answer.get("errors") or "[no reply]")

    spoke = False
    if reply:
        set_avatar("speaking", "Seed is speaking after wake conversation.")
        spoke = say(reply)

    set_avatar("idle", "Wake conversation finished.")
    row = {
        "ok": bool(reply),
        "stage": "done",
        "wake_phrase": wake_phrase,
        "wake_transcript": wake_transcript,
        "followup": text,
        "reply": reply,
        "spoke": spoke,
        "answer": answer,
        "record": rec,
    }
    log(row)
    return row

def show_status():
    print("\n=== SEED v87.1.1 WAKE CONVERSATION STATUS ===")
    data = {
        "created_at": now(),
        "version": "v87.1.1",
        "ok": True,
        "settings": load_settings(),
        "models": model_candidates(),
        "route": "direct_ollama_no_context_gate",
        "log": str(LOG_FILE),
    }
    print(json.dumps(data, indent=4, ensure_ascii=False))

def main():
    arg = sys.argv[1] if len(sys.argv) > 1 else "status"
    if arg == "once":
        seconds = int(sys.argv[2]) if len(sys.argv) > 2 else None
        wake_conversation_once(seconds=seconds)
    elif arg == "status":
        show_status()
    elif arg == "set-seconds":
        seconds = int(sys.argv[2])
        print(save_settings(after_wake_listen_seconds=seconds))
    elif arg == "set-model":
        model = sys.argv[2] if len(sys.argv) > 2 else "gemma3:4b"
        print(save_settings(fast_model=model))
    elif arg == "ack-before-on":
        print(save_settings(ack_before_listen=True, ack_after_listen=False))
    elif arg == "ack-before-off":
        print(save_settings(ack_before_listen=False, ack_after_listen=True))
    else:
        print("Commands: status | once [seconds] | set-seconds <n> | set-model <model> | ack-before-on | ack-before-off")

if __name__ == "__main__":
    main()
