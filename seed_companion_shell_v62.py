from datetime import datetime
def snapshot():
    d={"version":"v70.0.0"}
    try:
        from seed_latency_probe import run_latency_probe; d["latency"]=run_latency_probe().get("results",{})
    except Exception as e: d["latency_error"]=str(e)
    try:
        from seed_task_hygiene_v302 import task_stats; d["tasks"]=task_stats()
    except Exception as e: d["task_error"]=str(e)
    try:
        from seed_agent_hq_v30 import build_agent_hq_fast; d["agent_hq"]=build_agent_hq_fast()
    except Exception as e: d["agent_hq_error"]=str(e)
    try:
        from seed_model_real_mode_v61 import load_role_map; d["models"]=load_role_map()
    except Exception as e: d["model_error"]=str(e)
    try:
        from seed_presence_operator_v66 import best_next_move; d["next_move"]=best_next_move()
    except Exception: d["next_move"]={"message":"Improve Seed's natural UX and model routing."}
    return d
def print_home():
    s=snapshot(); l=s.get("latency",{}); t=s.get("tasks",{}); h=s.get("agent_hq",{}); m=s.get("models",{}).get("role_map",{}); n=s.get("next_move",{})
    print("\n"+"═"*72); print("Seed is ready."); print("Natural companion mode is active."); print("═"*72)
    print(f"Latency: prompt={l.get('prompt_build_ms')}ms fast_context={l.get('fast_context_ms')}ms"); print(f"Agent HQ: {h.get('agent_count')} agents"); print(f"Tasks: {t.get('ready_real')} real ready, {t.get('ready_test_or_gate')} test/gate")
    print(f"Model router: fast={m.get('fast_chat')} coding={m.get('coding')} reasoning={m.get('reasoning')}"); print(f"Next useful move: {n.get('message')}")
    print("─"*72); print("Try: check yourself | show models | benchmark models | clean fusion | review memories | open dashboard | what should we improve next"); print("═"*72)
def companion_loop():
    from seed_commands import handle_chat_command
    hist=[]; state={}; print_home()
    while True:
        try: msg=input("\nYou: ").strip()
        except KeyboardInterrupt: print("\nSeed paused."); break
        if not msg: continue
        if msg.lower() in {"exit","quit","/exit"}: print("Returning."); break
        if msg.lower() in {"home","status","seed home"}: print_home(); continue
        try:
            result=handle_chat_command(msg,hist,state)
            if result not in {"handled",None}: print(result)
        except Exception as e: print(f"Seed hit an error: {e}")
if __name__=="__main__": companion_loop()
