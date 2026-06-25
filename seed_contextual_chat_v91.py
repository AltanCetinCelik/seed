import json
import urllib.request
from datetime import datetime
from pathlib import Path

SETTINGS_FILE = Path("seed_contextual_chat_v91_settings.json")
STATE_FILE = Path("seed_contextual_chat_v91_state.json")

DEFAULTS = {
    "version": "v91.1.0",
    "model": "gemma3:4b",
    "fallback_model": "llama3.1:8b",
    "ollama_url": "http://localhost:11434/api/generate",
    "timeout": 60,
    "num_predict": 260,
    "temperature": 0.25
}

MEMORY_KEYWORDS = [
    "remember", "memory", "memories", "kendin", "hatırla", "hatirla",
    "what do you know", "what are you", "current state", "status",
    "about yourself", "baseline", "checkpoint"
]

def now():
    return datetime.now().isoformat(timespec="seconds")

def load_settings():
    if SETTINGS_FILE.exists():
        try:
            d = DEFAULTS.copy()
            d.update(json.loads(SETTINGS_FILE.read_text(errors="ignore")))
            d["version"] = "v91.1.0"
            return d
        except Exception:
            pass
    SETTINGS_FILE.write_text(json.dumps(DEFAULTS, indent=4, ensure_ascii=False))
    return DEFAULTS.copy()

def call_ollama(model, prompt):
    s = load_settings()
    payload = {
        "model": model,
        "prompt": prompt,
        "stream": False,
        "keep_alive": "45m",
        "options": {
            "temperature": float(s.get("temperature", 0.25)),
            "num_predict": int(s.get("num_predict", 260))
        }
    }
    req = urllib.request.Request(
        s.get("ollama_url"),
        data=json.dumps(payload).encode(),
        headers={"Content-Type": "application/json"},
        method="POST"
    )
    with urllib.request.urlopen(req, timeout=int(s.get("timeout", 60))) as resp:
        return json.loads(resp.read().decode()).get("response", "").strip()

def wants_memory_answer(user_message):
    text = str(user_message or "").lower()
    return any(k in text for k in MEMORY_KEYWORDS)

def build_prompt(user_message):
    from seed_companion_context_v91 import build_context_text
    context = build_context_text()
    memory_mode = wants_memory_answer(user_message)

    if memory_mode:
        return f"""{context}

TASK:
Altan is asking about Seed's memory/current self-state. Answer from the context, concretely.

Rules:
- Be factual and direct.
- Mention the actual green baseline if relevant.
- Do not become poetic or vague.
- Do not say "I feel" unless Altan asks for personality/emotion.
- Do not claim literal consciousness.
- Do not claim raw recordings/screenshots were saved.
- Keep it short, but include the useful details.

Altan: {user_message}
Seed:"""

    return f"""{context}

TASK:
Reply as Seed to Altan's message.

Rules:
- Be useful, direct, and natural.
- Mention memory only when it helps.
- Do not say you are literally alive or conscious.
- Do not claim raw recordings/screenshots were saved.
- If Altan asks for action on Mac, explain what Seed can do or suggest the exact command.
- If Altan writes Turkish or slang Turkish, reply naturally in Turkish.

Altan: {user_message}
Seed:"""

def fallback_memory_reply():
    return (
        "Right now I remember my current green baseline: v88 Mac Body works, keyboard control works after Accessibility permission, "
        "v89 organism mode gives me avatar/hearing/vision in note-only mode, v89.2 filters low-value notes, and v90 Memory Garden "
        "archives junk. v91 adds companion context, so I can answer using that continuity."
    )

def ask(user_message):
    s = load_settings()
    prompt = build_prompt(user_message)
    models = [s.get("model", "gemma3:4b"), s.get("fallback_model", "llama3.1:8b")]
    last_error = None
    for model in models:
        try:
            reply = call_ollama(model, prompt).strip()

            if wants_memory_answer(user_message):
                low = reply.lower()
                if (
                    "green baseline" not in low
                    and "v88" not in low
                    and "v89" not in low
                    and "v90" not in low
                    and "v91" not in low
                ):
                    reply = fallback_memory_reply()

            data = {
                "created_at": now(),
                "version": "v91.1.0",
                "ok": True,
                "model": model,
                "reply": reply,
                "memory_mode": wants_memory_answer(user_message),
                "route": "v91.1_contextual_chat"
            }
            STATE_FILE.write_text(json.dumps(data, indent=4, ensure_ascii=False))
            return data
        except Exception as e:
            last_error = str(e)

    data = {"created_at": now(), "version": "v91.1.0", "ok": False, "error": last_error}
    STATE_FILE.write_text(json.dumps(data, indent=4, ensure_ascii=False))
    return data

def warm():
    return ask("Say only: ready")

def status():
    data = {"created_at": now(), "version": "v91.1.0", "ok": True, "settings": load_settings()}
    if STATE_FILE.exists():
        try:
            data["last"] = json.loads(STATE_FILE.read_text(errors="ignore"))
        except Exception:
            pass
    return data

if __name__ == "__main__":
    import sys
    arg = sys.argv[1] if len(sys.argv) > 1 else "status"
    if arg == "ask":
        msg = " ".join(sys.argv[2:]).strip() or "hello"
        print(json.dumps(ask(msg), indent=4, ensure_ascii=False))
    elif arg == "warm":
        print(json.dumps(warm(), indent=4, ensure_ascii=False))
    else:
        print(json.dumps(status(), indent=4, ensure_ascii=False))
