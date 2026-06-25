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
def roots(): return [Path("third_party_repos"), Path.home()/"Desktop"/"seed_private"/"third_party_repos"]
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
