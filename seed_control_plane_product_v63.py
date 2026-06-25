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
