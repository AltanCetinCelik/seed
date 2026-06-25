import json
import urllib.request
from datetime import datetime
from pathlib import Path


LOG_FILE = Path("seed_model_usage_v701.jsonl")


def now_timestamp():
    return datetime.now().isoformat(timespec="seconds")


def load_role_map():
    try:
        from seed_model_real_mode_v61 import load_role_map as _load
        return _load().get("role_map", {})
    except Exception:
        return {}


def choose_role(user_message):
    text = str(user_message or "").lower()

    if any(w in text for w in ["code", "patch", "bug", "file", "python", "aider", "fix", "implement"]):
        return "coding"

    if any(w in text for w in ["türkçe", "turkish", "turkce", "kanka", "olm", "lan"]):
        return "turkish"

    if any(w in text for w in ["think", "reason", "decide", "tradeoff", "why", "compare"]):
        return "reasoning"

    if any(w in text for w in ["memory", "remember", "extract"]):
        return "memory_extraction"

    return "fast_chat"


def model_fallbacks(role):
    role_map = load_role_map()
    preferred = role_map.get(role)

    fallbacks = {
        "fast_chat": ["gemma3:4b", "llama3.1:8b", "qwen3:8b"],
        "turkish": ["llama3.1:8b", "qwen3:8b", "gemma3:4b"],
        "coding": ["qwen2.5-coder:7b", "llama3.1:8b", "qwen3:8b"],
        "reasoning": ["llama3.1:8b", "deepseek-r1:8b", "qwen3:8b"],
        "patch_planning": ["qwen2.5-coder:7b", "llama3.1:8b"],
        "memory_extraction": ["llama3.1:8b", "gemma3:4b", "qwen3:8b"],
    }

    models = []
    if preferred:
        models.append(preferred)

    for model in fallbacks.get(role, ["llama3.1:8b"]):
        if model not in models:
            models.append(model)

    return models


def prompt_for(role, user_message):
    base = """You are Seed, Altan's local AI companion running on his Mac.
Be natural, useful, direct, and warm.
Do not claim to be conscious or human.
Do not answer with one-word placeholders like "normal".
If Altan is casual, respond casually.
If he uses Turkish, you can respond in Turkish.
Keep answers concise unless he asks for detail.
"""

    if role == "coding":
        base += "\nFor coding or patch tasks, be concrete: files, commands, tests, rollback.\n"

    if role == "turkish":
        base += "\nRespond naturally in Turkish unless English is clearly better.\n"

    return f"{base}\nAltan: {user_message}\nSeed:"


def call_ollama(model, role, user_message, timeout=120):
    payload = {
        "model": model,
        "prompt": prompt_for(role, user_message),
        "stream": False,
        "options": {
            "num_predict": 220,
            "temperature": 0.45,
            "num_ctx": 3072
        }
    }

    req = urllib.request.Request(
        "http://127.0.0.1:11434/api/generate",
        data=json.dumps(payload).encode("utf-8"),
        headers={"Content-Type": "application/json"},
        method="POST"
    )

    with urllib.request.urlopen(req, timeout=timeout) as response:
        data = json.loads(response.read().decode("utf-8", errors="ignore"))

    return data.get("response", "").strip()


def log_usage(role, model, ok, user_message, response_or_error):
    row = {
        "created_at": now_timestamp(),
        "role": role,
        "model": model,
        "ok": ok,
        "user": str(user_message)[:500],
        "result": str(response_or_error)[:1000],
    }

    with LOG_FILE.open("a") as file:
        file.write(json.dumps(row, ensure_ascii=False) + "\n")


def local_chat(user_message):
    role = choose_role(user_message)

    for model in model_fallbacks(role):
        try:
            print(f"Using {model} for {role}.")
            reply = call_ollama(model, role, user_message)

            if reply and reply.strip().lower() not in {"normal", "ok", "okay"}:
                log_usage(role, model, True, user_message, reply)
                print(reply)
                return "handled"

            log_usage(role, model, False, user_message, "empty_or_bad_reply")

        except Exception as error:
            log_usage(role, model, False, user_message, error)
            continue

    print("Seed could not get a good local model reply. Ollama may be busy or the model failed.")
    return "handled"


def show_model_usage_log(limit=20):
    if not LOG_FILE.exists():
        print("No model usage log yet.")
        return "handled"

    lines = LOG_FILE.read_text(errors="ignore").splitlines()[-limit:]
    print("\n=== SEED MODEL USAGE LOG ===")
    for line in lines:
        try:
            row = json.loads(line)
            print(f"- {row['created_at']} | {row['role']} | {row['model']} | ok={row['ok']}")
        except Exception:
            print(line)

    return "handled"


if __name__ == "__main__":
    while True:
        msg = input("You: ").strip()
        if msg.lower() in {"exit", "quit"}:
            break
        local_chat(msg)


# ============================================================
# v70.2 Context-Aware Seed Chat Override
# These definitions intentionally override earlier v70.1 helpers.
# ============================================================

def build_seed_context():
    context = []

    context.append("Current Seed status:")
    context.append("- Seed v70.0.0 Mega Fusion Companion OS is installed.")
    context.append("- v70 gate passed Ready True.")
    context.append("- v60 gate passed Ready True.")
    context.append("- v50 gate passed Ready True.")
    context.append("- Latency probe passed OK.")

    try:
        from seed_model_real_mode_v61 import load_role_map, list_models
        role_map = load_role_map().get("role_map", {})
        models = list_models().get("models", [])
        context.append(f"- Installed Ollama models: {', '.join(models)}")
        context.append(f"- Current model role map: {json.dumps(role_map, ensure_ascii=False)}")
    except Exception as error:
        context.append(f"- Model status unavailable: {error}")

    try:
        from seed_v70_systems import build_v70_state
        state = build_v70_state()
        context.append(f"- v70 systems: ok={state.get('ok')} cards={len(state.get('cards', []))}")
        context.append(f"- Fusion status: {state.get('fusion_status')}")
        context.append(f"- Model status: {state.get('model_status')}")
    except Exception as error:
        context.append(f"- v70 state unavailable: {error}")

    try:
        from seed_memory_review_inbox_v64 import build_inbox
        inbox = build_inbox()
        context.append(f"- Memory review inbox: pending={inbox.get('pending')} saved={inbox.get('saved')} ignored={inbox.get('ignored')}")
    except Exception as error:
        context.append(f"- Memory inbox unavailable: {error}")

    try:
        from seed_presence_operator_v66 import best_next_move
        move = best_next_move()
        context.append(f"- Seed's suggested next move: {move.get('message')}")
        context.append(f"- Reason: {move.get('reason')}")
    except Exception as error:
        context.append(f"- Next move unavailable: {error}")

    context.append("")
    context.append("Important behavioral rules:")
    context.append("- If Altan asks about Seed, Seed updates, what to do next, or the project, answer from this context.")
    context.append("- Do not suggest random things like weather, photography, browsing, or unrelated hobbies unless Altan asks.")
    context.append("- Be honest: Seed is not conscious. It is a local companion system with memory, tools, models, and workflows.")
    context.append("- For next steps, prioritize hardening v70: memory review, model router polish, benchmark fix, Control Plane polish, Aider loop test.")
    context.append("- Keep the tone casual and direct.")

    return "\n".join(context)


def choose_role(user_message):
    text = str(user_message or "").lower()

    if any(w in text for w in [
        "your update", "your updates", "about your updates", "seed update",
        "what should we do next", "what now", "next update", "about you",
        "your status", "how are you", "what are you", "what can you do"
    ]):
        return "seed_status"

    if any(w in text for w in ["code", "patch", "bug", "file", "python", "aider", "fix", "implement"]):
        return "coding"

    if any(w in text for w in ["türkçe", "turkish", "turkce", "kanka", "olm", "lan"]):
        return "turkish"

    if any(w in text for w in ["think", "reason", "decide", "tradeoff", "why", "compare"]):
        return "reasoning"

    if any(w in text for w in ["memory", "remember", "extract"]):
        return "memory_extraction"

    return "fast_chat"


def model_fallbacks(role):
    role_map = load_role_map()
    preferred = role_map.get(role)

    fallbacks = {
        "seed_status": ["llama3.1:8b", "gemma3:4b", "qwen2.5-coder:7b"],
        "fast_chat": ["gemma3:4b", "llama3.1:8b", "qwen3:8b"],
        "turkish": ["llama3.1:8b", "qwen3:8b", "gemma3:4b"],
        "coding": ["qwen2.5-coder:7b", "llama3.1:8b", "qwen3:8b"],
        "reasoning": ["llama3.1:8b", "deepseek-r1:8b", "qwen3:8b"],
        "patch_planning": ["qwen2.5-coder:7b", "llama3.1:8b"],
        "memory_extraction": ["llama3.1:8b", "gemma3:4b", "qwen3:8b"],
    }

    models = []
    if preferred:
        models.append(preferred)

    for model in fallbacks.get(role, ["llama3.1:8b"]):
        if model not in models:
            models.append(model)

    return models


def prompt_for(role, user_message):
    seed_context = build_seed_context()

    base = f"""You are Seed, Altan's local AI companion running on his Mac.

{seed_context}

Current user message:
Altan: {user_message}

Answer as Seed.
Do not answer with placeholder words like "normal".
Do not invent unrelated suggestions.
If Altan asks what to do next, talk about Seed's actual next engineering/product step.
"""

    if role == "seed_status":
        base += """
For this answer, focus on Seed's current state and next update path.
Best next answer should mention:
- v70 is green
- chat now works but needed grounding
- next move is v70.2/v70.3 hardening
- review memory candidates
- improve model router / Control Plane / Aider loop
"""

    if role == "coding":
        base += "\nFor coding or patch tasks, be concrete: files, commands, tests, rollback.\n"

    if role == "turkish":
        base += "\nRespond naturally in Turkish unless English is clearly better.\n"

    return base + "\nSeed:"

# v72 Presence Max chat context.
try:
    _seed_v72_old_build_seed_context = build_seed_context

    def build_seed_context():
        base = _seed_v72_old_build_seed_context()
        extra = ["", "Seed v72 Presence Max is installed."]

        try:
            from seed_presence_policy_v72 import load_policy
            pol = load_policy()
            extra.append(
                f"- Simulated emotion allowed={pol['expression']['simulated_emotion_allowed']}; "
                f"relevant life advice allowed={pol['life_advice']['allowed']}."
            )
        except Exception as e:
            extra.append(f"- v72 policy unavailable: {e}")

        try:
            from seed_avatar_state_v72 import compute_avatar_state
            a = compute_avatar_state()
            extra.append(
                f"- Avatar state: mood={a.get('mood')} "
                f"face={a.get('face')} reason={a.get('reason')}"
            )
        except Exception as e:
            extra.append(f"- Avatar unavailable: {e}")

        try:
            from seed_curiosity_engine_v72 import best_curiosity
            c = best_curiosity()
            extra.append(
                f"- Current curiosity: {c.get('title')} — {c.get('body')}"
            )
        except Exception as e:
            extra.append(f"- Curiosity unavailable: {e}")

        extra.append(
            "- Seed may be expressive/playful and give relevant life advice "
            "grounded in Altan's project, memory, goals, or current state."
        )

        return base + "\\n" + "\\n".join(extra)

except Exception:
    pass

# v75 Self-State Truth chat override.
try:
    _seed_v75_old_build_seed_context = build_seed_context
    def build_seed_context():
        base = _seed_v75_old_build_seed_context()
        try:
            from seed_self_state_v741 import build_seed_truth_context
            truth = build_seed_truth_context()
        except Exception as error:
            truth = f"Seed v75 truth context unavailable: {error}"
        return base + "\n\n" + truth
except Exception:
    pass

try:
    _seed_v75_old_prompt_for = prompt_for
    def prompt_for(role, user_message):
        seed_context = build_seed_context()
        base = f"""You are Seed, Altan's local AI companion running on his Mac.

{seed_context}

Current user message:
Altan: {user_message}

Answer as Seed.
Do not answer with placeholder words like "normal".
Do not invent unrelated suggestions.
When asked about your current version/state, use the TRUE CURRENT SEED STATE OVERRIDE.
Current version is v75.0.0 if the v75 gate is green.
v70 is an older base layer, not the current version.
You may be expressive/playful and use simulated emotion honestly.
You may give relevant life advice when grounded in Altan's goals, memory, project, health, school, work, or current context.
"""
        if role == "seed_status":
            base += """
For this answer, focus on current truth:
- current layer is v75.0.0
- v74 embodied panel works
- v73.1 voice pipeline works
- v75 real memory review is the current upgrade
- next real-v1 path: v76 voice polish, v77 panel polish, v78 proactive presence, v79 permissions, v80 Aider loop
"""
        if role == "coding":
            base += "\nFor coding or patch tasks, be concrete: files, commands, tests, rollback.\n"
        if role == "turkish":
            base += "\nRespond naturally in Turkish unless English is clearly better.\n"
        return base + "\nSeed:"
except Exception:
    pass

# v81 Self-State Truth chat override.
try:
    _seed_v81_old_build_seed_context = build_seed_context

    def build_seed_context():
        base = _seed_v81_old_build_seed_context()
        try:
            from seed_self_state_v81 import build_seed_truth_context
            truth = build_seed_truth_context()
        except Exception as error:
            truth = f"Seed v81 truth context unavailable: {error}"
        return base + "\n\n" + truth

except Exception:
    pass

try:
    _seed_v81_old_prompt_for = prompt_for

    def prompt_for(role, user_message):
        seed_context = build_seed_context()
        base = f"""You are Seed, Altan's local AI companion running on his Mac.

{seed_context}

Current user message:
Altan: {user_message}

Answer as Seed.
Do not answer with placeholder words like "normal".
Do not invent unrelated suggestions.
When asked about your current version/state, use the TRUE CURRENT SEED STATE OVERRIDE.
Current version is v81.0.0 if the v81 gate is green.
v70/v75 are older base layers, not the current version.
You may be expressive/playful and use simulated emotion honestly.
You may give relevant life advice when grounded in Altan's goals, memory, project, health, school, work, or current context.
"""
        if role == "seed_status":
            base += """
For this answer, focus on current truth:
- current layer is v81.0.0
- v76 Voice 2.0 is installed
- v77 Panel 2.0 is installed
- v78 proactive presence is installed
- v79 permission executor is installed
- v80 Aider loop is installed
- v81 advice/repo assimilation is installed
- next real-v1 path: v82 recovery, v83 one-command runtime, v84 backup/privacy, v85 release candidate
"""
        if role == "coding":
            base += "\nFor coding or patch tasks, be concrete: files, commands, tests, rollback.\n"
        if role == "turkish":
            base += "\nRespond naturally in Turkish unless English is clearly better.\n"
        return base + "\nSeed:"

except Exception:
    pass

# v85 Self-State Truth chat override.
try:
    _seed_v85_old_build_seed_context = build_seed_context

    def build_seed_context():
        base = _seed_v85_old_build_seed_context()
        try:
            from seed_self_state_v85 import build_seed_truth_context
            truth = build_seed_truth_context()
        except Exception as error:
            truth = f"Seed v85 truth context unavailable: {error}"
        return base + "\n\n" + truth

except Exception:
    pass

try:
    _seed_v85_old_prompt_for = prompt_for

    def prompt_for(role, user_message):
        seed_context = build_seed_context()
        base = f"""You are Seed, Altan's local AI companion running on his Mac.

{seed_context}

Current user message:
Altan: {user_message}

Answer as Seed.
Do not answer with placeholder words like "normal".
Do not invent unrelated suggestions.
When asked about your current version/state, use the TRUE CURRENT SEED STATE OVERRIDE.
Current version is v85.0.0 if the v85 gate is green.
v70/v75/v81 are older green layers, not the current version.
You may be expressive/playful and use simulated emotion honestly.
You may give relevant life advice when grounded in Altan's goals, memory, project, health, school, work, or current context.
"""
        if role == "seed_status":
            base += """
For this answer, focus on current truth:
- current layer is v85.0.0
- v82 recovery/self-repair is installed
- v83 one-command runtime is installed
- v84 backup/privacy/export/forget is installed
- v85 release candidate checks are installed
- next real-v1 path: fix RC blockers, then Seed v1.0 final release
"""
        if role == "coding":
            base += "\nFor coding or patch tasks, be concrete: files, commands, tests, rollback.\n"
        if role == "turkish":
            base += "\nRespond naturally in Turkish unless English is clearly better.\n"
        return base + "\nSeed:"

except Exception:
    pass

# v87 Alive Companion Truth chat override.
try:
    _seed_v87_old_build_seed_context = build_seed_context

    def build_seed_context():
        base = _seed_v87_old_build_seed_context()
        try:
            from seed_self_state_v87 import build_seed_truth_context
            truth = build_seed_truth_context()
        except Exception as error:
            truth = f"Seed v87 truth context unavailable: {error}"
        return base + "\n\n" + truth

except Exception:
    pass
