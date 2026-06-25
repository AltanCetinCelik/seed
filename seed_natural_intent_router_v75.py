import re
def norm(text): return " ".join(str(text or "").strip().lower().split())
def handle_natural_intent_v75(user_message):
    raw=str(user_message or "").strip(); text=norm(raw)
    if not text or raw.startswith("/"): return None
    if any(p in text for p in ["v75 status","real memory status","self truth status"]):
        from seed_v75_systems import show_v75_status; show_v75_status(); return "handled"
    if any(p in text for p in ["self state","current version","what version are you","your real state","true state"]):
        from seed_self_state_v741 import show_self_state; show_self_state(); return "handled"
    if any(p in text for p in ["review memories","memory review","show memory candidates","memory candidates"]):
        from seed_memory_review_v75 import show_memory_review; show_memory_review(); return "handled"
    if any(p in text for p in ["accepted memories","show accepted memories","long term memories"]):
        from seed_memory_review_v75 import show_accepted_memories; show_accepted_memories(); return "handled"
    m=re.search(r"\b(save|accept|ignore|skip|later|edit)\s+memory\s+([a-zA-Z0-9_:-]+)\b", text)
    if m:
        from seed_memory_review_v75 import decide_memory
        res=decide_memory(m.group(2),action=m.group(1))
        print("\n=== SEED v75 MEMORY DECISION ===")
        print(f"{m.group(2)} -> {res.get('decision',{}).get('action',m.group(1))}")
        if res.get("memory"): print(f"Saved: {res['memory'].get('text')[:260]}")
        return "handled"
    return None
