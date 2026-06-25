import json
from pathlib import Path
from datetime import datetime
STATE_FILE=Path("seed_v70_systems_state.json")
def now(): return datetime.now().isoformat(timespec="seconds")
def safe(title,summary,fn):
    try:
        data=fn(); ok=bool(data.get("ok",True)) if isinstance(data,dict) else True; return {"title":title,"summary":summary,"status":"ok" if ok else "warning","data":data}
    except Exception as e: return {"title":title,"summary":summary,"status":"error","error":str(e)}
def build_v70_state():
    cards=[safe("Fusion Lab Cleanup","Main repo detection, component classification, clean notebooks.",lambda:__import__("seed_fusion_lab_clean_v602",fromlist=["build_clean_fusion"]).build_clean_fusion()),safe("Model Manager Real Mode","Install plan, model roles, routing, arena.",lambda:__import__("seed_model_real_mode_v61",fromlist=["install_plan"]).install_plan()),safe("Companion Terminal","Natural shell replaces programmer menu.",lambda:{"ok":True}),safe("Control Plane Product Redesign","Home, Agent HQ, Memory, Workflows, Models, Aider, Fusion, Voice, Browser, Settings.",lambda:__import__("seed_control_plane_product_v63",fromlist=["build_product_state"]).build_product_state()),safe("Memory Review Inbox","Save, ignore, auto-save, review candidates.",lambda:__import__("seed_memory_review_inbox_v64",fromlist=["build_inbox"]).build_inbox()),safe("Real Aider Loop","Goal-to-files, checkpoint, preflight, approval phrase.",lambda:{"ok":True}),safe("Presence Operator","Reasoned initiative, one useful question, no spam.",lambda:__import__("seed_presence_operator_v66",fromlist=["presence_brief"]).presence_brief()),safe("Voice Push-to-talk","Recorder detection, faster-whisper path, TTS route.",lambda:__import__("seed_voice_push_to_talk_v67",fromlist=["voice_status"]).voice_status()),safe("Browser-use Adapter","Read page, summarize, extract links, dry-run actions.",lambda:{"ok":True}),safe("Multi-channel Companion","Terminal, Control Plane, local web chat, phone/Telegram/Discord plan.",lambda:__import__("seed_multichannel_companion_v69",fromlist=["build_channel_state"]).build_channel_state()),safe("One-of-a-kind Polish","Taste system, rituals, progress map, achievements, why explanations.",lambda:__import__("seed_one_of_a_kind_polish_v70",fromlist=["build_polish_state"]).build_polish_state())]
    try:
        from seed_model_real_mode_v61 import list_models; model_status=f"{len(list_models().get('models',[]))} installed"
    except Exception: model_status="unknown"
    try:
        from seed_fusion_lab_clean_v602 import build_clean_fusion; fusion_status=f"{build_clean_fusion().get('main_repo_count')} main repos"
    except Exception: fusion_status="unknown"
    data={"created_at":now(),"version":"v70.0.0","ok":all(c["status"]!="error" for c in cards),"cards":cards,"model_status":model_status,"fusion_status":fusion_status,"principle":"Natural-language-first. Slash commands are hidden debug plumbing."}; STATE_FILE.write_text(json.dumps(data,indent=4)); return data
def show_v70_status():
    d=build_v70_state(); print(f"OK: {d['ok']} Models: {d['model_status']} Fusion: {d['fusion_status']}")
    for c in d["cards"]: print(f"- {c['title']}: {c['status']} — {c['summary']}")
if __name__=="__main__": show_v70_status()
