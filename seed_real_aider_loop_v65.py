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
