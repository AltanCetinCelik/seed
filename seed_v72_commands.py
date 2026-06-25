def handle_v72_command(command):
    cmd=(command or "").strip().split()[0].lower()
    mapping={
      "/v72-check":("seed_v72_gate","show_v72_gate"),"/v72-status":("seed_v72_systems","show_v72_status"),
      "/presence-policy":("seed_presence_policy_v72","show_policy"),"/add-advice":("seed_friend_advice_ingestor_v72","show_add_advice"),
      "/friend-advice":("seed_friend_advice_ingestor_v72","show_advice"),"/advice-backlog":("seed_friend_advice_ingestor_v72","show_advice_backlog"),
      "/repo-patterns":("seed_repo_pattern_extractor_v72","show_repo_patterns"),"/avatar":("seed_avatar_state_v72","show_avatar"),
      "/presence-inbox":("seed_presence_inbox_v72","show_presence_inbox"),"/curiosity":("seed_curiosity_engine_v72","show_curiosity"),
      "/voice-session":("seed_voice_session_v72","show_voice_session")}
    if cmd=="/v72-help": print("v72 debug: /v72-check /v72-status /presence-policy /add-advice /friend-advice /advice-backlog /repo-patterns /avatar /presence-inbox /curiosity /voice-session"); return "handled"
    if cmd in mapping:
        m,f=mapping[cmd]; mod=__import__(m,fromlist=[f]); getattr(mod,f)(); return "handled"
    return None
