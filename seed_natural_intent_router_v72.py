import json
def norm(x): return " ".join(str(x or "").strip().lower().split())
# v73.1 voice once precedence
try:
    from seed_live_voice_v731 import handle_voice_command_v731
except Exception:
    handle_voice_command_v731 = None

def handle_natural_intent_v72(user_message):
    raw=str(user_message or "").strip(); text=norm(raw)
    if handle_voice_command_v731:
        handled_voice = handle_voice_command_v731(raw)
        if handled_voice == "handled": return "handled"
    if not text or raw.startswith("/"): return None
    if any(p in text for p in ["presence policy","your rules","emotion settings","fake emotion","simulated emotion"]):
        from seed_presence_policy_v72 import show_policy; show_policy(); return "handled"
    if "my friend said" in text:
        from seed_friend_advice_ingestor_v72 import add_advice
        advice=raw.split("my friend said",1)[1].strip()
        print(json.dumps(add_advice(advice),indent=4,ensure_ascii=False)); return "handled"
    if any(p in text for p in ["friend advice","use my friend's advice"]):
        from seed_friend_advice_ingestor_v72 import show_advice; show_advice(); return "handled"
    if any(p in text for p in ["advice backlog","use friend advice"]):
        from seed_friend_advice_ingestor_v72 import show_advice_backlog; show_advice_backlog(); return "handled"
    if any(p in text for p in ["repo patterns","use the repos","hermes patterns","moltbot patterns","openclaw patterns"]):
        from seed_repo_pattern_extractor_v72 import show_repo_patterns; show_repo_patterns(); return "handled"
    if any(p in text for p in ["avatar","your face","your mood","visual state"]):
        from seed_avatar_state_v72 import show_avatar; show_avatar(); return "handled"
    if any(p in text for p in ["what did you notice","presence inbox","notices"]):
        from seed_presence_inbox_v72 import show_presence_inbox; show_presence_inbox(); return "handled"
    if any(p in text for p in ["curiosity","be curious","what are you curious about"]):
        from seed_curiosity_engine_v72 import show_curiosity; show_curiosity(); return "handled"
    if any(p in text for p in ["voice session","voice foundation","voice status"]):
        from seed_voice_session_v72 import show_voice_session; show_voice_session(); return "handled"
    if any(p in text for p in ["v72 status","presence max status"]):
        from seed_v72_systems import show_v72_status; show_v72_status(); return "handled"
    return None
