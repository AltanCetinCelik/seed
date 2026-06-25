import json, re, webbrowser
def norm(t): return re.sub(r"\s+"," ",str(t or "").strip().lower())
def anyof(t,ps): return any(p in t for p in ps)
def handle_natural_intent_v70(user_message):
    raw=str(user_message or "").strip(); text=norm(raw)
    if not text or raw.startswith("/"): return None
    if anyof(text,["download models","pull models","install models","show models","model manager","what models"]):
        from seed_model_real_mode_v61 import show_model_real; show_model_real(); print("\nSay 'pull starter models' to let Seed run the Ollama pulls."); return "handled"
    if anyof(text,["pull starter models","download starter models"]):
        from seed_model_real_mode_v61 import show_model_pull_starter; show_model_pull_starter(); return "handled"
    if anyof(text,["benchmark models","model arena","test models"]):
        from seed_model_real_mode_v61 import show_model_arena; show_model_arena(); return "handled"
    if anyof(text,["which model","route model","model should handle"]):
        from seed_model_real_mode_v61 import route; print(json.dumps(route(raw),indent=4)); return "handled"
    if anyof(text,["clean fusion","fusion cleanup","hermes moltbot openclaw","compare hermes"]):
        from seed_fusion_lab_clean_v602 import show_clean_fusion; show_clean_fusion(); return "handled"
    if anyof(text,["review memories","memory inbox","show memory candidates"]):
        from seed_memory_review_inbox_v64 import show_memory_review; show_memory_review(); return "handled"
    if anyof(text,["save important memories","auto save memories"]):
        from seed_memory_review_inbox_v64 import show_memory_review_auto_save; show_memory_review_auto_save(); return "handled"
    if anyof(text,["what should we improve next","what now","daily brief"]):
        from seed_presence_operator_v66 import show_presence_operator; show_presence_operator(); return "handled"
    if anyof(text,["open dashboard","open control plane","show dashboard"]):
        print("Opening Seed Control Plane: http://127.0.0.1:8790"); webbrowser.open("http://127.0.0.1:8790"); return "handled"
    if anyof(text,["make a patch","create a patch","aider plan","improve yourself"]):
        from seed_real_aider_loop_v65 import create_real_aider_plan
        if " targeting " in text:
            before,after=raw.rsplit(" targeting ",1); goal=before; files=[x.strip() for x in after.split(",") if x.strip()]
        else: goal=raw; files=None
        print(json.dumps(create_real_aider_plan(goal,files),indent=4)); return "handled"
    return None
