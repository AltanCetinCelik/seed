def norm(s): return " ".join(str(s or "").strip().lower().split())
def handle_natural_intent_v92_106(user_message):
    t=norm(user_message)
    if t in {"seed start","start seed"}:
        import seed_supervisor_v92 as s; print(s.start()); return "handled"
    if t in {"seed stop","stop seed"}:
        import seed_supervisor_v92 as s; print(s.stop()); return "handled"
    if t in {"seed status","full status"}:
        import seed_supervisor_v92 as s; print(s.supervisor_status()); return "handled"
    if t in {"seed doctor","doctor"}:
        import seed_supervisor_v92 as s; print(s.doctor()); return "handled"
    if t in {"seed dashboard","dashboard"}:
        import seed_dashboard_v106 as d; print(d.start()); return "handled"
    return None
