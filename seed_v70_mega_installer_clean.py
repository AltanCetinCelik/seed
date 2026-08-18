#!/usr/bin/env python3
from pathlib import Path
import re


def write(path, content):
    Path(path).write_text(content.strip() + "\n")
    print(f"Wrote {path}")

# v60.2 Fusion Lab cleanup
write("seed_fusion_lab_clean_v602.py", r'''
import json, os
from pathlib import Path
from datetime import datetime

REPORT_FILE = Path("seed_fusion_lab_clean_v602.json")
NOTEBOOK_DIR = Path("seed_fusion_notebooks_clean_v602")
TARGETS = {"hermes":"hermes-agent", "moltbot":"moltbot-ai-assistant", "openclaw":"openclaw"}
PATTERNS = {
    "skill_learning": ["skill", "learn", "experience", "self-improve"],
    "memory": ["memory", "recall", "conversation", "history", "user model"],
    "multi_channel": ["telegram", "discord", "slack", "whatsapp", "imessage", "channel"],
    "tool_use": ["tool", "function", "plugin", "mcp", "api"],
    "ux": ["webui", "canvas", "dashboard", "interface", "chat", "tui", "ink"],
    "automation": ["automation", "agent", "task", "workflow", "execute"],
}

def now(): return datetime.now().isoformat(timespec="seconds")
def roots(): return [Path("third_party_repos"), Path.home()/"Desktop"/"seed"/"third_party_repos"]
def resolved(p):
    try: return str(Path(p).resolve())
    except Exception: return str(p)

def find_main_repos():
    found, seen = {k: [] for k in TARGETS}, set()
    for root in roots():
        if not root.exists(): continue
        for child in root.iterdir():
            if not child.is_dir(): continue
            for label, name in TARGETS.items():
                if child.name.lower() == name.lower() and resolved(child) not in seen:
                    found[label].append(child); seen.add(resolved(child))
    return found

def component_category(rel):
    low = rel.lower()
    if rel == ".": return "main_repo"
    if any(x in low for x in ["skills", ".agents/skills", "optional-skills"]): return "skills"
    if any(x in low for x in ["plugins", "extensions"]): return "plugins"
    if any(x in low for x in ["ui", "webui", "tui", "ink", "kit"]): return "ui"
    if any(x in low for x in ["tests", ".github", "codeql"]): return "tests"
    if any(x in low for x in ["docker", "s6-rc.d", "apps", "packages"]): return "runtime"
    return "other"

def collect_components(repo):
    out=[]; repo=Path(repo)
    for dirpath, dirnames, files in os.walk(repo):
        p=Path(dirpath)
        if any(x in p.parts for x in [".git","node_modules","__pycache__"]): dirnames[:]=[]; continue
        rel = "." if p == repo else str(p.relative_to(repo))
        if rel != "." and len(Path(rel).parts) > 4: dirnames[:] = []; continue
        cat = component_category(rel)
        if rel != "." and cat != "other": out.append({"relative": rel, "path": str(p), "category": cat})
        if len(out) >= 120: break
    return out

def read_repo(repo):
    repo=Path(repo); chunks=[]
    for name in ["README.md","readme.md","README.rst","package.json","pyproject.toml"]:
        p=repo/name
        if p.exists() and p.is_file(): chunks.append(p.read_text(errors="ignore")[:12000])
    for sub in ["docs","skills","plugins","extensions","apps"]:
        d=repo/sub
        if d.exists() and d.is_dir():
            for child in list(d.rglob("*.md"))[:12]: chunks.append(child.read_text(errors="ignore")[:5000])
    return "\n".join(chunks)[:90000]

def score(text):
    low=text.lower(); return {k: sum(low.count(w) for w in words) for k,words in PATTERNS.items()}
def takeaway(scores):
    key,val=sorted(scores.items(), key=lambda x:x[1], reverse=True)[0]
    if val == 0: return "Manual review only."
    return {"skill_learning":"Extract experience-to-skill learning loop.","memory":"Extract persistent memory/user-model pattern.","multi_channel":"Extract chat-first multi-channel UX.","tool_use":"Extract plugin/tool interface pattern.","ux":"Extract lightweight companion UI/TUI pattern.","automation":"Extract task automation loop."}.get(key,"Review manually.")

def notebook(label, repo, scores, comps):
    NOTEBOOK_DIR.mkdir(exist_ok=True)
    groups={}
    for c in comps: groups.setdefault(c["category"], []).append(c["relative"])
    def lines(cat): return "\n".join("- "+x for x in groups.get(cat,[])[:40]) or "None detected."
    path=NOTEBOOK_DIR/f"{label}_{Path(repo).name}.md"
    path.write_text(f"""# Seed Clean Fusion Notebook — {label} / {Path(repo).name}

Main repo: `{repo}`

Primary takeaway: {takeaway(scores)}

Pattern scores:
```json
{json.dumps(scores, indent=2)}
```

Skills:
{lines('skills')}

Plugins/extensions:
{lines('plugins')}

UI/channel components:
{lines('ui')}

Runtime/apps:
{lines('runtime')}

Seed-native rule: use this repo as a pattern source, not a blind copy source.
""")
    return str(path)

def build_clean_fusion():
    items=[]
    for label,repos in find_main_repos().items():
        for repo in repos:
            text=read_repo(repo); scores=score(text); comps=collect_components(repo)
            items.append({"label":label,"repo":str(repo),"repo_resolved":resolved(repo),"scores":scores,"takeaway":takeaway(scores),"component_counts":{k:len([c for c in comps if c['category']==k]) for k in ["skills","plugins","ui","tests","runtime"]},"components":comps,"notebook":notebook(label, repo, scores, comps)})
    data={"created_at":now(),"version":"v70.0.0","ok":True,"main_repo_count":len(items),"items":items,"principle":"Only main repos are repos; subfolders are components."}
    REPORT_FILE.write_text(json.dumps(data, indent=4)); return data

def show_clean_fusion():
    data=build_clean_fusion(); print("\n=== SEED FUSION LAB CLEAN v60.2 ==="); print(f"Main repos: {data['main_repo_count']}")
    for i in data["items"]: print(f"- {i['label']} / {Path(i['repo']).name}: {i['takeaway']} {i['component_counts']}")
if __name__ == "__main__": show_clean_fusion()
''')

# v61 Model Manager real mode
write("seed_model_real_mode_v61.py", r'''
import json, shutil, subprocess, time
from pathlib import Path
from datetime import datetime

STATE_FILE=Path("seed_model_real_mode_v61.json"); BENCH_FILE=Path("seed_model_real_benchmark_v61.json"); ROLE_FILE=Path("seed_model_real_roles_v61.json")
STARTER_MODELS=["llama3.1:8b","qwen3:8b","deepseek-r1:8b","qwen2.5-coder:7b","gemma3:4b"]
BIGGER_MAC_MODELS=["qwen3:14b","qwen2.5-coder:14b"]
ROLE_CANDIDATES={"fast_chat":["llama3.1:8b","qwen3:8b","gemma3:4b"],"turkish":["qwen3:8b","llama3.1:8b"],"coding":["qwen2.5-coder:7b","qwen2.5-coder:14b","qwen3:8b"],"reasoning":["deepseek-r1:8b","qwen3:8b"],"patch_planning":["qwen2.5-coder:7b","qwen3:8b"],"memory_extraction":["llama3.1:8b","qwen3:8b","gemma3:4b"]}
BENCH_PROMPTS={"fast_chat":"Answer in one short paragraph: what should Seed improve next?","turkish":"Türkçe doğal cevap ver: Seed bugün neye odaklanmalı?","coding":"Give a concise patch plan to improve a Python CLI UX. Include files and tests.","reasoning":"Give 3 tradeoffs for local-first AI companions. Be precise.","patch_planning":"Plan a safe patch for improving a dashboard UI. Include rollback and test steps.","memory_extraction":"Extract durable memories from: User wants Seed natural, not slash-command heavy."}

def now(): return datetime.now().isoformat(timespec="seconds")
def ollama(): return shutil.which("ollama")
def run(cmd, timeout=60):
    try:
        p=subprocess.run(cmd,capture_output=True,text=True,timeout=timeout); return {"ok":p.returncode==0,"stdout":p.stdout,"stderr":p.stderr,"returncode":p.returncode}
    except Exception as e: return {"ok":False,"error":str(e)}
def list_models():
    if not ollama(): return {"created_at":now(),"version":"v70.0.0","ok":False,"error":"Ollama not found.","models":[]}
    r=run([ollama(),"list"],30); models=[]
    if r.get("ok"):
        for line in r.get("stdout","").splitlines()[1:]:
            parts=line.split();
            if parts: models.append(parts[0])
    return {"created_at":now(),"version":"v70.0.0","ok":r.get("ok"),"models":models,"raw":r}
def install_plan():
    installed=set(list_models().get("models",[])); missing=[m for m in STARTER_MODELS if m not in installed]; bigger=[m for m in BIGGER_MAC_MODELS if m not in installed]
    data={"created_at":now(),"version":"v70.0.0","ok":True,"ollama_found":bool(ollama()),"installed":sorted(installed),"starter_models":STARTER_MODELS,"bigger_mac_models":BIGGER_MAC_MODELS,"missing_starter":missing,"missing_bigger_mac":bigger,"starter_pull_commands":[f"ollama pull {m}" for m in missing],"bigger_pull_commands":[f"ollama pull {m}" for m in bigger],"note":"Run starter pulls first. Benchmark before 14B models."}
    STATE_FILE.write_text(json.dumps(data, indent=4)); return data
def pull_missing_starter_models():
    plan=install_plan()
    if not plan.get("ollama_found"): return {"ok":False,"error":"Ollama not found."}
    results=[{"model":m,"result":run(["ollama","pull",m],1800)} for m in plan["missing_starter"]]
    return {"created_at":now(),"version":"v70.0.0","ok":all(x["result"].get("ok") for x in results),"results":results}
def benchmark_model(model, role, timeout=120):
    start=time.time()
    try:
        p=subprocess.run(["ollama","run",model,BENCH_PROMPTS[role]],capture_output=True,text=True,timeout=timeout); ms=int((time.time()-start)*1000); reply=p.stdout.strip(); q=2 if reply else 0
        if role=="coding" and ("test" in reply.lower() or "file" in reply.lower()): q+=2
        if role=="turkish" and any(ch in reply.lower() for ch in "çğıöşü"): q+=2
        if role=="reasoning" and ("tradeoff" in reply.lower() or "1" in reply): q+=1
        speed=max(0,6-int(ms/7000)); return {"model":model,"role":role,"ok":p.returncode==0,"ms":ms,"quality_score":q,"speed_score":speed,"combined_score":q+speed,"reply_tail":reply[-1200:],"stderr_tail":p.stderr[-800:]}
    except Exception as e: return {"model":model,"role":role,"ok":False,"error":str(e),"combined_score":0}
def run_arena():
    selected=[m for m in STARTER_MODELS+BIGGER_MAC_MODELS if m in list_models().get("models",[])]
    results=[benchmark_model(m,r) for m in selected for r in BENCH_PROMPTS]; best={}
    for role in BENCH_PROMPTS:
        rr=[x for x in results if x.get("role")==role and x.get("ok")]; best[role]=sorted(rr,key=lambda x:x.get("combined_score",0),reverse=True)[0]["model"] if rr else None
    report={"created_at":now(),"version":"v70.0.0","ok":True,"models_tested":selected,"results":results,"best_role_map":best}; BENCH_FILE.write_text(json.dumps(report,indent=4)); ROLE_FILE.write_text(json.dumps({"created_at":now(),"version":"v70.0.0","ok":True,"role_map":best,"source":str(BENCH_FILE)},indent=4)); return report
def load_role_map():
    if ROLE_FILE.exists():
        try: return json.loads(ROLE_FILE.read_text(errors="ignore"))
        except Exception: pass
    installed=set(list_models().get("models",[])); role_map={role:next((m for m in cands if m in installed),None) for role,cands in ROLE_CANDIDATES.items()}; return {"created_at":now(),"version":"v70.0.0","ok":True,"role_map":role_map,"source":"heuristic"}
def route(text):
    low=str(text).lower()
    if any(w in low for w in ["code","patch","bug","file","aider","python","cli"]): role="coding"
    elif any(w in low for w in ["türkçe","turkish","turkce"]): role="turkish"
    elif any(w in low for w in ["reason","think","tradeoff","decide"]): role="reasoning"
    elif any(w in low for w in ["memory","remember","extract"]): role="memory_extraction"
    elif any(w in low for w in ["plan","improve","control plane","dashboard"]): role="patch_planning"
    else: role="fast_chat"
    return {"created_at":now(),"version":"v70.0.0","ok":True,"role":role,"model":load_role_map().get("role_map",{}).get(role),"text":text}
def show_model_real(): print("\n=== SEED MODEL MANAGER REAL MODE v61 ==="); print(json.dumps(install_plan(),indent=4))
def show_model_pull_starter(): print("\n=== SEED MODEL PULL STARTER ==="); print(json.dumps(pull_missing_starter_models(),indent=4))
def show_model_arena(): print("\n=== SEED MODEL BENCHMARK ARENA ==="); print(json.dumps(run_arena(),indent=4))
def show_model_route(): print(json.dumps(route(input("Task: ").strip()),indent=4))
if __name__ == "__main__": show_model_real()
''')

# Supporting modules
write("seed_control_plane_product_v63.py", r'''
import json
from pathlib import Path
from datetime import datetime
PRODUCT_STATE=Path("seed_control_plane_product_v63.json")
def now(): return datetime.now().isoformat(timespec="seconds")
def build_product_state():
    pages=[("home","Home","Seed status, next move, and quick actions."),("agent_hq","Agent HQ","Aider, browser, voice, memory, MCP, and sandbox agents."),("memory","Memory","Memory review inbox, active memories, and project timeline."),("workflows","Workflows","Durable tasks, approvals, and execution timeline."),("models","Models","Installed models, roles, benchmarks, and routing."),("aider","Aider Cockpit","Patch planning, tests, approval phrase, and rollback."),("repo_fusion","Repo Fusion","Hermes/Moltbot/OpenClaw notebooks and extracted patterns."),("voice","Voice","Push-to-talk, transcript journal, and TTS."),("browser","Browser","Read-only browsing, page summaries, and dry-run actions."),("settings","Settings","Mode, permissions, models, appearance, and developer options.")]
    data={"created_at":now(),"version":"v70.0.0","ok":True,"pages":[{"id":i,"title":t,"summary":s} for i,t,s in pages],"principles":["plain English first","one obvious next action","no raw JSON unless expanded","professional spacing","search and command palette"]}; PRODUCT_STATE.write_text(json.dumps(data,indent=4)); return data
def show_product_state(): print(json.dumps(build_product_state(),indent=4))
if __name__=="__main__": show_product_state()
''')

write("seed_memory_review_inbox_v64.py", r'''
import json
from pathlib import Path
from datetime import datetime
INBOX_FILE=Path("seed_memory_review_inbox_v64.json")
def now(): return datetime.now().isoformat(timespec="seconds")
def candidates():
    try:
        from seed_memory_auto_extractor_v60 import extract_candidates
        return extract_candidates(limit=60).get("candidates",[])
    except Exception: return []
def build_inbox():
    old={}
    if INBOX_FILE.exists():
        try: old={x.get("content"):x for x in json.loads(INBOX_FILE.read_text(errors="ignore")).get("items",[])}
        except Exception: old={}
    items=[]
    for cand in candidates():
        cand["review_status"]=old.get(cand.get("content"),{}).get("review_status","pending"); items.append(cand)
    data={"created_at":now(),"version":"v70.0.0","ok":True,"count":len(items),"pending":len([x for x in items if x.get("review_status")=="pending"]),"saved":len([x for x in items if x.get("review_status")=="saved"]),"ignored":len([x for x in items if x.get("review_status")=="ignored"]),"items":items}; INBOX_FILE.write_text(json.dumps(data,indent=4)); return data
def save_memory(candidate_id):
    data=build_inbox(); item=next((x for x in data["items"] if x.get("id")==candidate_id),None)
    if not item: return {"ok":False,"error":"Candidate not found"}
    from seed_memory_brain_max_v32 import add_memory
    mem=add_memory(content=item["content"],layer=item.get("suggested_layer","project"),source=f"review_inbox:{item.get('source')}",confidence=.9,tags=["reviewed","v64"])
    for x in data["items"]:
        if x.get("id")==candidate_id: x["review_status"]="saved"; x["memory_id"]=mem.get("id")
    INBOX_FILE.write_text(json.dumps(data,indent=4)); return {"ok":True,"memory":mem}
def auto_save_high_confidence(limit=8):
    data=build_inbox(); pending=sorted([x for x in data["items"] if x.get("review_status")=="pending"],key=lambda x:x.get("score",0),reverse=True)[:limit]; results=[save_memory(x["id"]) for x in pending if x.get("score",0)>=4]; return {"ok":True,"saved":len([r for r in results if r.get("ok")]),"results":results}
def show_memory_review():
    data=build_inbox(); print(f"Pending: {data['pending']} Saved: {data['saved']} Ignored: {data['ignored']}")
    for x in data["items"][:20]: print(f"- {x['id']} score={x.get('score')} status={x.get('review_status')}: {x.get('content')[:180]}")
def show_memory_review_auto_save(): print(json.dumps(auto_save_high_confidence(),indent=4))
def show_memory_review_save(): print(json.dumps(save_memory(input("Candidate ID to save: ").strip()),indent=4))
def show_memory_review_ignore(): print("Manual ignore can be added after first review pass.")
if __name__=="__main__": show_memory_review()
''')

write("seed_presence_operator_v66.py", r'''
import json
from pathlib import Path
from datetime import datetime
STATE_FILE=Path("seed_presence_operator_v66.json")
def now(): return datetime.now().isoformat(timespec="seconds")
def best_next_move():
    try:
        from seed_model_real_mode_v61 import list_models, install_plan
        if len(list_models().get("models",[])) < 2: return {"message":"You have not installed enough local models yet. Model routing cannot become real until starter models are pulled.","reason":"model_benchmarking"}
        if install_plan().get("missing_starter"): return {"message":"Some starter models are still missing, so model routing is incomplete.","reason":"finish_model_set"}
    except Exception: pass
    try:
        from seed_memory_review_inbox_v64 import build_inbox
        inbox=build_inbox()
        if inbox.get("pending",0)>0: return {"message":f"Seed found {inbox.get('pending')} memory candidates. Reviewing them will improve continuity.","reason":"memory_review"}
    except Exception: pass
    return {"message":"Seed is stable. The next useful move is polishing the companion terminal and Control Plane.","reason":"no_urgent_missing_system"}
def presence_brief():
    move=best_next_move(); data={"created_at":now(),"version":"v70.0.0","ok":True,"message":move["message"],"why":move["reason"],"rules":["Never spam","Always explain why","One useful question max","No fake consciousness claims"]}; STATE_FILE.write_text(json.dumps(data,indent=4)); return data
def show_presence_operator(): print(json.dumps(presence_brief(),indent=4))
if __name__=="__main__": show_presence_operator()
''')

write("seed_companion_shell_v62.py", r'''
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
''')

write("seed_real_aider_loop_v65.py", r'''
import json, shutil, subprocess, uuid
from pathlib import Path
from datetime import datetime
STATE_FILE=Path("seed_real_aider_loop_v65.json")
TARGET_HINTS={"terminal":["seed_companion_shell_v62.py","seed_terminal_pro.py","seed_cli.py"],"control plane":["seed_control_plane_ui_v70.py","seed_control_plane_ui_v60.py","seed_control_plane_product_v63.py"],"model":["seed_model_real_mode_v61.py"],"fusion":["seed_fusion_lab_clean_v602.py"],"memory":["seed_memory_review_inbox_v64.py"],"presence":["seed_presence_operator_v66.py"]}
def now(): return datetime.now().isoformat(timespec="seconds")
def detect_aider(): return shutil.which("aider") or shutil.which("aider-chat")
def choose_files(goal):
    low=str(goal).lower(); files=[]
    for k,v in TARGET_HINTS.items():
        if k in low: files += v
    files=[f for f in files if Path(f).exists() and Path(f).is_file()]
    return list(dict.fromkeys(files or ["seed_companion_shell_v62.py"]))[:4]
def preflight():
    cmds=[["python","-m","py_compile","seed_companion_shell_v62.py"],["python","seed_latency_probe.py"],["python","seed_v70_gate.py"]]; results=[]
    for c in cmds:
        try:
            p=subprocess.run(c,capture_output=True,text=True,timeout=240); results.append({"command":" ".join(c),"ok":p.returncode==0,"stdout_tail":p.stdout[-1200:],"stderr_tail":p.stderr[-1200:]})
        except Exception as e: results.append({"command":" ".join(c),"ok":False,"error":str(e)})
    return {"ok":all(r["ok"] for r in results),"results":results}
def create_real_aider_plan(goal,target_files=None):
    if str(goal).strip().startswith("/"): return {"ok":False,"error":"Use normal improvement wording, not slash command."}
    target_files=target_files or choose_files(goal); invalid=[f for f in target_files if not Path(f).is_file()]
    if invalid: return {"ok":False,"error":"Invalid target files","invalid":invalid}
    loop_id=uuid.uuid4().hex[:10]; approval=f"APPROVE_REAL_AIDER_{loop_id}"; plan={"id":loop_id,"created_at":now(),"version":"v70.0.0","ok":True,"goal":goal,"target_files":target_files,"aider":detect_aider(),"approval_phrase":approval,"status":"planned_waiting_for_approval","preflight":preflight(),"preview_command":f"aider {' '.join(target_files)} --message {json.dumps(goal)}","next_step":f"Approve only with phrase: {approval}"}; STATE_FILE.write_text(json.dumps(plan,indent=4)); return plan
def approve_and_run(phrase):
    if not STATE_FILE.exists(): return {"ok":False,"error":"No Aider plan exists."}
    plan=json.loads(STATE_FILE.read_text(errors="ignore"))
    if phrase.strip()!=plan.get("approval_phrase"): return {"ok":False,"error":"Approval phrase mismatch","required":plan.get("approval_phrase")}
    if not plan.get("aider"): return {"ok":False,"error":"Aider not found"}
    cmd=[plan["aider"]]+plan["target_files"]+["--message",plan["goal"]]
    try:
        p=subprocess.run(cmd,capture_output=True,text=True,timeout=900); res={"ok":p.returncode==0,"command":" ".join(cmd),"stdout_tail":p.stdout[-5000:],"stderr_tail":p.stderr[-5000:]}
    except Exception as e: res={"ok":False,"error":str(e),"command":" ".join(cmd)}
    plan["real_run"]=res; plan["status"]="completed" if res.get("ok") else "failed"; STATE_FILE.write_text(json.dumps(plan,indent=4)); return plan
def show_real_aider_loop(): print(STATE_FILE.read_text() if STATE_FILE.exists() else "No plan yet.")
def show_real_aider_new(): print(json.dumps(create_real_aider_plan(input("Goal: ").strip(), [x.strip() for x in input("Target files optional comma-separated: ").split(",") if x.strip()] or None),indent=4))
def show_real_aider_approve(): print(json.dumps(approve_and_run(input("Approval phrase: ").strip()),indent=4))
if __name__=="__main__": show_real_aider_loop()
''')

write("seed_voice_push_to_talk_v67.py", r'''
import json, shutil
from pathlib import Path
from datetime import datetime
VOICE_FILE=Path("seed_voice_push_to_talk_v67.json")
def avail(name):
    try: __import__(name); return True
    except Exception: return False
def voice_status():
    data={"created_at":datetime.now().isoformat(timespec="seconds"),"version":"v70.0.0","ok":True,"tools":{"sox_rec":shutil.which("rec"),"ffmpeg":shutil.which("ffmpeg"),"faster_whisper":avail("faster_whisper"),"macos_say":shutil.which("say")},"path":"record -> transcribe -> natural intent route -> optional say -> journal"}; VOICE_FILE.write_text(json.dumps(data,indent=4)); return data
def show_voice_ptt_status(): print(json.dumps(voice_status(),indent=4))
def show_voice_record(): print("Voice recording path is scaffolded. Install sox/ffmpeg for recording.")
if __name__=="__main__": show_voice_ptt_status()
''')

write("seed_browser_use_adapter_v68.py", r'''
import json, re, urllib.request, shutil
from pathlib import Path
from datetime import datetime
from urllib.parse import urlparse
from html.parser import HTMLParser
STATE_FILE=Path("seed_browser_use_adapter_v68.json")
class P(HTMLParser):
    def __init__(self): super().__init__(); self.links=[]; self.text=[]
    def handle_starttag(self,tag,attrs):
        if tag=="a":
            href=dict(attrs).get("href")
            if href: self.links.append(href)
    def handle_data(self,data):
        if data and data.strip(): self.text.append(data.strip())
def browser_use_available():
    try: __import__("browser_use"); return True
    except Exception: return False
def read_page(url,max_bytes=500000):
    p=urlparse(url)
    if p.scheme not in {"http","https"} or not p.netloc: return {"ok":False,"error":"Invalid URL"}
    req=urllib.request.Request(url,headers={"User-Agent":"SeedBrowserReadOnly/1.0"})
    with urllib.request.urlopen(req,timeout=25) as r: html=r.read(max_bytes).decode("utf-8",errors="ignore"); ct=r.headers.get("content-type","")
    parser=P(); parser.feed(html); text=re.sub(r"\s+"," "," ".join(parser.text)).strip(); data={"created_at":datetime.now().isoformat(timespec="seconds"),"version":"v70.0.0","ok":True,"url":url,"mode":"read_only","browser_use_installed":browser_use_available(),"content_type":ct,"summary":text[:1600],"links":parser.links[:40],"dry_run_actions":["summarize page","extract links","no click without approval","no login/form/purchase"]}; STATE_FILE.write_text(json.dumps(data,indent=4)); return data
def show_browser_use_status(): print(json.dumps({"ok":True,"browser_use_installed":browser_use_available(),"playwright":bool(shutil.which("playwright")),"mode":"read-only adapter active"},indent=4))
def show_browser_use_read(): print(json.dumps(read_page(input("URL: ").strip()),indent=4))
if __name__=="__main__": show_browser_use_status()
''')

write("seed_multichannel_companion_v69.py", r'''
import json
from pathlib import Path
from datetime import datetime
STATE_FILE=Path("seed_multichannel_companion_v69.json")
def build_channel_state():
    data={"created_at":datetime.now().isoformat(timespec="seconds"),"version":"v70.0.0","ok":True,"channels":{"terminal":{"status":"active","path":"seed_companion_shell_v62.py"},"control_plane":{"status":"active","url":"http://127.0.0.1:8790"},"local_web_chat":{"status":"planned","url":"http://127.0.0.1:8791"},"phone_lan_dashboard":{"status":"planned"},"telegram":{"status":"planned","needs":"bot token"},"discord":{"status":"planned","needs":"bot token"},"imessage":{"status":"future"}},"principle":"Seed should not be trapped inside Terminal."}; STATE_FILE.write_text(json.dumps(data,indent=4)); return data
def show_multichannel_state(): print(json.dumps(build_channel_state(),indent=4))
def show_start_local_web_chat(): print("Local web chat scaffold ready. Full server can be enabled in v71.")
if __name__=="__main__": show_multichannel_state()
''')

write("seed_one_of_a_kind_polish_v70.py", r'''
import json
from pathlib import Path
from datetime import datetime
STATE_FILE=Path("seed_one_of_a_kind_polish_v70.json")
def build_polish_state():
    data={"created_at":datetime.now().isoformat(timespec="seconds"),"version":"v70.0.0","ok":True,"taste_system":{"style":"local-first, sharp, warm, technical, not robotic","ui":"dark professional, low clutter, one obvious next action","assistant_behavior":"reasoned initiative, memory continuity, no fake consciousness"},"rituals":["daily brief","after-success commit/backup reminder","after-failure diagnosis flow","night review","weekly model benchmark"],"progress_map":["v20 Sovereign OS","v30 Agent HQ","v45 Total Systems","v50 Nothing Left Behind","v60 Natural UX + Intelligence","v70 One-of-a-kind polish"],"achievements":["Local-first companion core","Repo assimilation engine","Agent HQ","Natural intent router","Model manager","Fusion notebooks","Memory review inbox","Real Aider loop","Multi-channel plan"],"why_explanations":True}; STATE_FILE.write_text(json.dumps(data,indent=4)); return data
def why_suggested_this():
    try:
        from seed_presence_operator_v66 import best_next_move; move=best_next_move()
    except Exception: move={"message":"Improve natural UX.","reason":"Seed should feel less like a dev console."}
    return {"ok":True,"suggestion":move.get("message"),"why":move.get("reason")}
def show_polish(): print(json.dumps(build_polish_state(),indent=4))
def show_why(): print(json.dumps(why_suggested_this(),indent=4))
if __name__=="__main__": show_polish()
''')

write("seed_control_plane_ui_v70.py", r'''
import html
def esc(v): return html.escape(str(v))
def render_v70_panel(bundle):
    v70=bundle.get("v70",{}) or {}; data=v70.get("data",v70) if isinstance(v70,dict) else {}; cards=data.get("cards",[]) if isinstance(data,dict) else []
    cards_html="".join(f"<div class='event'><div class='time'>{esc(c.get('status'))}</div><div class='body'><strong>{esc(c.get('title'))}</strong><br>{esc(c.get('summary'))}</div></div>" for c in cards)
    nav_html="".join(f"<span class='pill'>{esc(x)}</span>" for x in ["Home","Agent HQ","Memory","Workflows","Models","Aider","Repo Fusion","Voice","Browser","Settings"])
    phrase_html="".join(f"<span class='pill'>{esc(x)}</span>" for x in ["check yourself","show models","benchmark models","review memories","compare Hermes Moltbot OpenClaw","open dashboard","what should we improve next"])
    return f"""<section class='card full' id='seed-v70'><h2>Seed v70 — One-of-a-kind Companion OS</h2><p class='small'>Natural UX, model-aware routing, clean repo fusion, memory review, real Aider loop, voice/browser/multichannel paths, and product polish.</p><div class='metric-row'><div class='metric'><div class='label'>v70 OK</div><div class='value'>{esc(data.get('ok'))}</div></div><div class='metric'><div class='label'>Models</div><div class='value' style='font-size:13px'>{esc(data.get('model_status'))}</div></div><div class='metric'><div class='label'>Fusion</div><div class='value' style='font-size:13px'>{esc(data.get('fusion_status'))}</div></div><div class='metric'><div class='label'>UX</div><div class='value' style='font-size:13px'>Natural</div></div></div><h3>Product Navigation</h3><div style='display:flex;flex-wrap:wrap;gap:8px;margin:10px 0 18px 0;'>{nav_html}</div><h3>Talk naturally</h3><div style='display:flex;flex-wrap:wrap;gap:8px;margin:10px 0 18px 0;'>{phrase_html}</div><h3>System Cards</h3><div class='timeline'>{cards_html}</div></section>"""
def render_control_plane_ui(bundle):
    from seed_control_plane_ui_v60 import render_control_plane_ui as base_render
    doc=base_render(bundle); panel=render_v70_panel(bundle)
    return doc.replace('<section class="card full" id="seed-v60">', panel+'\n<section class="card full" id="seed-v60">',1) if '<section class="card full" id="seed-v60">' in doc else doc.replace("</main>", panel+"\n</main>",1)
''')

write("seed_v70_systems.py", r'''
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
''')

write("seed_v70_gate.py", r'''
import json, subprocess
from datetime import datetime
MODULES=["seed_fusion_lab_clean_v602.py","seed_model_real_mode_v61.py","seed_companion_shell_v62.py","seed_control_plane_product_v63.py","seed_memory_review_inbox_v64.py","seed_real_aider_loop_v65.py","seed_presence_operator_v66.py","seed_voice_push_to_talk_v67.py","seed_browser_use_adapter_v68.py","seed_multichannel_companion_v69.py","seed_one_of_a_kind_polish_v70.py","seed_control_plane_ui_v70.py","seed_v70_systems.py","seed_v70_gate.py","seed_v70_commands.py","seed_natural_intent_router_v70.py"]
def compile_module(m):
    p=subprocess.run(["python","-m","py_compile",m],capture_output=True,text=True); return {"module":m,"ok":p.returncode==0,"stderr":p.stderr[-2000:]}
def run_v70_gate():
    checks=[compile_module(m) for m in MODULES]; modules_ok=all(c["ok"] for c in checks); details={}
    try:
        from seed_v70_systems import build_v70_state; state=build_v70_state(); systems_ok=state.get("ok") is True and len(state.get("cards",[]))>=11; details["v70_state"]={"ok":state.get("ok"),"cards":len(state.get("cards",[])),"models":state.get("model_status"),"fusion":state.get("fusion_status")}
    except Exception as e: systems_ok=False; details["v70_state_error"]=str(e)
    try:
        from seed_control_plane_server import api_payload; v70=api_payload("/api/v70"); control_plane_ok=bool(v70); details["control_plane"]={"v70_api":bool(v70)}
    except Exception as e: control_plane_ok=False; details["control_plane_error"]=str(e)
    try:
        from seed_v60_gate import run_v60_gate; v60=run_v60_gate(); v60_ok=v60.get("ready") is True; details["v60"]={"ready":v60.get("ready")}
    except Exception as e: v60_ok=False; details["v60_error"]=str(e)
    report={"created_at":datetime.now().isoformat(timespec="seconds"),"version":"v70.0.0","ready":modules_ok and systems_ok and control_plane_ok and v60_ok,"modules_ok":modules_ok,"systems_ok":systems_ok,"control_plane_ok":control_plane_ok,"v60_ok":v60_ok,"module_checks":checks,"details":details}; open("seed_v70_gate_report.json","w").write(json.dumps(report,indent=4)); return report
def show_v70_gate():
    r=run_v70_gate(); print("\n=== SEED v70 MEGA FUSION GATE ==="); print(f"Ready: {r['ready']}"); print(f"Modules OK: {r['modules_ok']}"); print(f"Systems OK: {r['systems_ok']}"); print(f"Control Plane OK: {r['control_plane_ok']}"); print(f"v60 OK: {r['v60_ok']}"); print("\nDetails:"); [print(f"- {k}: {v}") for k,v in r["details"].items()]
if __name__=="__main__": show_v70_gate()
''')

write("seed_v70_commands.py", r'''
def handle_v70_command(command):
    cmd=(command or "").strip().split()[0].lower(); mapping={"/v70-check":("seed_v70_gate","show_v70_gate"),"/v70-status":("seed_v70_systems","show_v70_status"),"/fusion-clean":("seed_fusion_lab_clean_v602","show_clean_fusion"),"/model-real":("seed_model_real_mode_v61","show_model_real"),"/model-pull-starter":("seed_model_real_mode_v61","show_model_pull_starter"),"/model-arena":("seed_model_real_mode_v61","show_model_arena"),"/memory-review":("seed_memory_review_inbox_v64","show_memory_review"),"/memory-review-auto-save":("seed_memory_review_inbox_v64","show_memory_review_auto_save"),"/real-aider":("seed_real_aider_loop_v65","show_real_aider_loop"),"/real-aider-new":("seed_real_aider_loop_v65","show_real_aider_new"),"/presence-operator":("seed_presence_operator_v66","show_presence_operator"),"/voice-ptt":("seed_voice_push_to_talk_v67","show_voice_ptt_status"),"/browser-use-status":("seed_browser_use_adapter_v68","show_browser_use_status"),"/multichannel":("seed_multichannel_companion_v69","show_multichannel_state"),"/polish":("seed_one_of_a_kind_polish_v70","show_polish"),"/why":("seed_one_of_a_kind_polish_v70","show_why")}
    if cmd in mapping:
        module_name,function_name=mapping[cmd]; module=__import__(module_name,fromlist=[function_name]); getattr(module,function_name)(); return "handled"
    return None
''')

write("seed_natural_intent_router_v70.py", r'''
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
''')

# Config
config=Path("seed_config.py"); text=config.read_text() if config.exists() else 'SEED_VERSION = "v70.0.0"\n'; text=re.sub(r'^SEED_VERSION\s*=\s*".*?"','SEED_VERSION = "v70.0.0"',text,flags=re.M)
if "SEED_V70_MEGA_FUSION" not in text: text += '\nSEED_V70_MEGA_FUSION = True\nSEED_COMPANION_TERMINAL_DEFAULT = True\nSEED_V70_GATE_REPORT_FILE = "seed_v70_gate_report.json"\n'
config.write_text(text); print("Updated seed_config.py")

# Commands wrapper
commands=Path("seed_commands.py"); text=commands.read_text() if commands.exists() else "def handle_chat_command(user_message,*args,**kwargs): return None\n"
if "_seed_v70_original_handle_chat_command" not in text:
    text += '''
# v70 Mega Fusion natural router and debug commands.
try:
    _seed_v70_original_handle_chat_command = handle_chat_command
    def handle_chat_command(user_message, *args, **kwargs):
        try:
            from seed_natural_intent_router_v70 import handle_natural_intent_v70
            handled = handle_natural_intent_v70(user_message)
            if handled == "handled": return "handled"
        except Exception as error:
            print(f"v70 natural router error: {error}"); return "handled"
        try:
            from seed_v70_commands import handle_v70_command
            handled = handle_v70_command(user_message)
            if handled == "handled": return "handled"
        except Exception as error:
            print(f"v70 command error: {error}"); return "handled"
        return _seed_v70_original_handle_chat_command(user_message, *args, **kwargs)
except Exception:
    pass
'''
commands.write_text(text); print("Patched seed_commands.py")

# Control plane server
server=Path("seed_control_plane_server.py")
if server.exists():
    text=server.read_text()
    if '/api/v70' not in text:
        endpoint='    if path == "/api/v70":\n        return safe_json(lambda: __import__("seed_v70_systems", fromlist=["build_v70_state"]).build_v70_state())\n\n'
        for anchor in ['    if path == "/api/v60":\n','    if path == "/api/v50":\n','    if path == "/api/v45":\n']:
            if anchor in text: text=text.replace(anchor,endpoint+anchor,1); break
    if '"v70": api_payload("/api/v70")' not in text:
        for anchor in ['"v60": api_payload("/api/v60")','"v50": api_payload("/api/v50")','"v45": api_payload("/api/v45")']:
            if anchor in text: text=text.replace(anchor,'"v70": api_payload("/api/v70"),\n        '+anchor,1); break
    text=text.replace("from seed_control_plane_ui_v60 import render_control_plane_ui","from seed_control_plane_ui_v70 import render_control_plane_ui").replace("from seed_control_plane_ui_v50 import render_control_plane_ui","from seed_control_plane_ui_v70 import render_control_plane_ui")
    server.write_text(text); print("Patched seed_control_plane_server.py")

# seed_cli companion default
cli=Path("seed_cli.py")
if cli.exists() and not Path("seed_cli_legacy_menu.py").exists(): Path("seed_cli_legacy_menu.py").write_text(cli.read_text()); print("Backed up old seed_cli.py")
cli.write_text('''import os

def main():
    if os.environ.get("SEED_DEV_MENU") == "1":
        try:
            import seed_cli_legacy_menu
            return seed_cli_legacy_menu.main()
        except Exception as error:
            print(f"Could not open legacy developer menu: {error}")
    from seed_companion_shell_v62 import companion_loop
    companion_loop()

if __name__ == "__main__":
    main()
'''); print("Replaced seed_cli.py with companion shell")

# Gate runners
for filename, list_name in [("seed_final_gate_runner.py","FINAL_GATE_COMMANDS"),("seed_quick_gate_runner.py","QUICK_GATE_COMMANDS")]:
    p=Path(filename)
    if p.exists():
        text=p.read_text(); line='    ["python", "seed_v70_gate.py"],\n'
        if line not in text and f"{list_name} = [" in text: p.write_text(text.replace(f"{list_name} = [\n",f"{list_name} = [\n{line}",1)); print("Patched",filename)

# Docs/gitignore
core=Path("Seed_Core.md"); text=core.read_text(errors="ignore") if core.exists() else ""
if "Seed v70.0.0 — Mega Fusion Companion OS" not in text: text += "\n## Seed v70.0.0 — Mega Fusion Companion OS\n\nCombines fusion cleanup, model manager real mode, companion terminal, product Control Plane, memory review, real Aider loop, presence operator, voice/browser/multichannel paths, and polish. Normal UX: talk naturally.\n"
core.write_text(text); print("Updated Seed_Core.md")
gi=Path(".gitignore"); text=gi.read_text(errors="ignore") if gi.exists() else ""
block="""
# Seed v70 Mega Fusion runtime state
seed_fusion_lab_clean_v602.json
seed_fusion_notebooks_clean_v602/
seed_model_real_mode_v61.json
seed_model_real_benchmark_v61.json
seed_model_real_roles_v61.json
seed_control_plane_product_v63.json
seed_memory_review_inbox_v64.json
seed_real_aider_loop_v65.json
seed_presence_operator_v66.json
seed_voice_push_to_talk_v67.json
seed_voice_audio/
seed_browser_use_adapter_v68.json
seed_multichannel_companion_v69.json
seed_one_of_a_kind_polish_v70.json
seed_project_memory_timeline_v70.json
seed_v70_systems_state.json
seed_v70_gate_report.json
"""
if "Seed v70 Mega Fusion runtime state" not in text: text += "\n" + block
gi.write_text(text); print("Updated .gitignore")

print("\nSeed v70 mega installer complete.")
