def norm(t): return " ".join(str(t or "").strip().lower().split())
def handle_natural_intent_v89(user_message):
    raw=str(user_message or "").strip(); text=norm(raw)
    if not text or raw.startswith("/"): return None
    if text in {"v89 status","organism status","seed organism status"}:
        __import__("seed_v89_systems",fromlist=["show_v89_status"]).show_v89_status(); return "handled"
    if text in {"start organism","start organism mode","be organism","start always listening","start ambient mode"}:
        __import__("seed_organism_v89",fromlist=["start_organism"]).start_organism(); return "handled"
    if text in {"stop organism","stop organism mode","stop always listening","stop ambient mode"}:
        __import__("seed_organism_v89",fromlist=["stop_organism"]).stop_organism(); return "handled"
    if text in {"avatar","open avatar","start avatar"}:
        print(__import__("seed_avatar_v89",fromlist=["start_server"]).start_server()); return "handled"
    if text in {"notes","organism notes","show notes"}:
        __import__("seed_organism_notes_v89",fromlist=["show_notes"]).show_notes(10); return "handled"
    if text in {"note stats","organism note stats"}:
        __import__("seed_organism_notes_v89",fromlist=["show_stats"]).show_stats(); return "handled"
    if text in {"hear once","ambient hearing once"}:
        print(__import__("seed_ambient_hearing_v89",fromlist=["process_chunk"]).process_chunk()); return "handled"
    if text in {"see once","ambient vision once"}:
        print(__import__("seed_ambient_vision_v89",fromlist=["process_screen"]).process_screen()); return "handled"
    return None
