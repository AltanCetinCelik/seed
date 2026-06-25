import json
import re
import webbrowser
from datetime import datetime


def now_timestamp():
    return datetime.now().isoformat(timespec="seconds")


def normalize(text):
    return re.sub(r"\s+", " ", str(text).strip().lower())


def contains_any(text, phrases):
    return any(p in text for p in phrases)


def handle_natural_intent(user_message):
    raw = str(user_message or "").strip()
    text = normalize(raw)

    if not text:
        return None

    if raw.startswith("/"):
        return None

    # URL browser read-only path.
    url_match = re.search(r"https?://\S+", raw)
    if url_match and contains_any(text, ["read", "summarize", "check", "open", "browser"]):
        from seed_browser_executor_v35 import fetch_readonly
        print(json.dumps(fetch_readonly(url_match.group(0)), indent=4))
        return "handled"

    if contains_any(text, ["check yourself", "are you healthy", "run health check", "is everything working", "diagnose yourself"]):
        from seed_v60_gate import show_v60_gate
        show_v60_gate()
        try:
            from seed_latency_probe import show_latency_probe
            show_latency_probe()
        except Exception:
            pass
        return "handled"

    if contains_any(text, ["open dashboard", "open control plane", "show dashboard", "control plane"]):
        print("\nOpening Seed Control Plane: http://127.0.0.1:8790")
        try:
            webbrowser.open("http://127.0.0.1:8790")
        except Exception as error:
            print(f"Could not open browser: {error}")
        return "handled"

    if contains_any(text, ["what changed", "what did we build", "full update", "show update", "everything we added"]):
        from seed_nothing_left_behind_v50 import show_full_update
        show_full_update()
        return "handled"

    if contains_any(text, ["what can i say", "command palette", "help me talk", "how do i talk to seed"]):
        from seed_command_palette_v60 import show_palette
        show_palette()
        return "handled"

    if contains_any(text, ["show models", "model manager", "what models", "download models", "model pull plan"]):
        from seed_model_manager_v60 import show_model_manager
        show_model_manager()
        return "handled"

    if contains_any(text, ["benchmark models", "test models", "model arena", "compare models"]):
        from seed_model_manager_v60 import show_model_benchmark
        show_model_benchmark()
        return "handled"

    if contains_any(text, ["route this", "which model", "model router"]):
        from seed_model_manager_v60 import route_task
        print(json.dumps(route_task(raw), indent=4))
        return "handled"

    if contains_any(text, ["hermes", "moltbot", "openclaw", "fusion lab", "compare repos"]):
        from seed_hermes_moltbot_fusion_v60 import show_fusion_lab
        show_fusion_lab()
        return "handled"

    if contains_any(text, ["extract memories", "learn from logs", "update your memory", "memory auto"]):
        from seed_memory_auto_extractor_v60 import show_memory_auto_extract
        show_memory_auto_extract()
        return "handled"

    if contains_any(text, ["save important memories", "promote memories", "remember important things"]):
        from seed_memory_auto_extractor_v60 import show_memory_auto_promote
        show_memory_auto_promote()
        return "handled"

    if contains_any(text, ["daily brief", "what should we do today", "what now", "next move", "what should we improve"]):
        from seed_presence_rituals_v60 import show_daily_brief
        show_daily_brief()
        return "handled"

    if contains_any(text, ["presence rituals", "more present", "more alive", "more sentient", "rituals"]):
        from seed_presence_rituals_v60 import show_rituals
        show_rituals()
        return "handled"

    if contains_any(text, ["create a patch plan", "make a patch plan", "aider plan", "improve yourself"]):
        print("\nI can create a real Aider self-improvement loop.")
        print("Say it like this:")
        print("create a patch plan for improving the Control Plane wording targeting seed_control_plane_ui_v60.py")
        return "handled"

    if text.startswith("create a patch plan for ") and " targeting " in text:
        from seed_aider_self_improvement_v60 import create_loop
        goal_part = raw.split(" for ", 1)[1]
        goal, files = goal_part.rsplit(" targeting ", 1)
        target_files = [x.strip() for x in files.split(",") if x.strip()]
        print(json.dumps(create_loop(goal.strip(), target_files), indent=4))
        return "handled"

    if contains_any(text, ["show self improvement loop", "show aider loop"]):
        from seed_aider_self_improvement_v60 import show_self_improvement_v60
        show_self_improvement_v60()
        return "handled"

    return None
