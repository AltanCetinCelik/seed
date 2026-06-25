def norm(text): return " ".join(str(text or "").strip().lower().split())
def handle_natural_intent_v74(user_message):
    raw=str(user_message or "").strip(); text=norm(raw)
    if not text or raw.startswith("/"): return None
    if any(p in text for p in ["v74 status","embodied status","companion status"]):
        from seed_v74_systems import show_v74_status; show_v74_status(); return "handled"
    if any(p in text for p in ["open avatar panel","embodied panel","open companion panel","avatar web panel","companion dashboard"]):
        from seed_embodied_companion_server_v74 import run_server; run_server(open_ui=True); return "handled"
    if any(p in text for p in ["memory actions","memory review actions","review memory candidates"]):
        from seed_memory_actions_v74 import show_memory_actions; show_memory_actions(); return "handled"
    if any(p in text for p in ["action tasks","task board","convert tasks"]):
        from seed_action_tasks_v74 import show_action_tasks; show_action_tasks(); return "handled"
    if any(p in text for p in ["avatar panel state","embodied state"]):
        from seed_avatar_panel_v74 import show_avatar_panel; show_avatar_panel(); return "handled"
    return None
