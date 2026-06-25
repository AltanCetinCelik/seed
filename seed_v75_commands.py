def handle_v75_command(command):
    text=str(command or "").strip(); cmd=text.split()[0].lower() if text else ""
    mapping={"/v75-check":("seed_v75_gate","show_v75_gate"),"/v75-status":("seed_v75_systems","show_v75_status"),"/self-state":("seed_self_state_v741","show_self_state"),"/memory-review":("seed_memory_review_v75","show_memory_review"),"/accepted-memories":("seed_memory_review_v75","show_accepted_memories")}
    if cmd=="/v75-help":
        print("v75: /v75-check /v75-status /self-state /memory-review /accepted-memories")
        return "handled"
    if cmd in mapping:
        m,f=mapping[cmd]; mod=__import__(m,fromlist=[f]); getattr(mod,f)(); return "handled"
    return None
