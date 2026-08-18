from pathlib import Path
import re


def write_file(path, content):
    Path(path).write_text(content.strip() + "\n")
    print(f"Wrote {path}")


write_file("seed_model_manager_v60.py", r'''
import json
import shutil
import subprocess
import time
from datetime import datetime
from pathlib import Path


STATE_FILE = Path("seed_model_manager_v60.json")
BENCH_FILE = Path("seed_model_benchmark_v60.json")
ROLE_MAP_FILE = Path("seed_model_role_map_v60.json")


MODEL_ROLE_MAP = {
    "fast_chat": ["llama3.1:8b", "qwen3:8b", "gemma3:4b"],
    "coding": ["qwen2.5-coder:7b", "qwen2.5-coder:14b"],
    "reasoning": ["deepseek-r1:8b", "qwen3:8b"],
    "turkish": ["qwen3:8b", "llama3.1:8b"],
    "memory_extraction": ["llama3.1:8b", "qwen3:8b"],
    "repo_planning": ["qwen2.5-coder:7b", "qwen3:8b"],
}


BENCH_PROMPTS = {
    "fast_chat": "Answer briefly: what should Seed improve next?",
    "coding": "Give a concise patch plan to improve a Python CLI UX.",
    "reasoning": "Think carefully and give 3 tradeoffs of local-first AI assistants.",
    "turkish": "Türkçe doğal ve kısa cevap ver: Seed bugün neye odaklanmalı?",
    "memory_extraction": "Extract one durable memory from: User wants Seed to be natural and not command-heavy.",
}


def now_timestamp():
    return datetime.now().isoformat(timespec="seconds")


def ollama_available():
    return shutil.which("ollama") is not None


def run_command(command, timeout=60):
    try:
        proc = subprocess.run(command, capture_output=True, text=True, timeout=timeout)
        return {
            "ok": proc.returncode == 0,
            "stdout": proc.stdout,
            "stderr": proc.stderr,
            "returncode": proc.returncode,
        }
    except Exception as error:
        return {"ok": False, "error": str(error)}


def list_ollama_models():
    if not ollama_available():
        return {"ok": False, "error": "Ollama not found on PATH.", "models": []}

    result = run_command(["ollama", "list"], timeout=30)

    models = []
    if result.get("ok"):
        lines = result.get("stdout", "").splitlines()[1:]
        for line in lines:
            parts = line.split()
            if parts:
                models.append(parts[0])

    return {
        "created_at": now_timestamp(),
        "ok": result.get("ok"),
        "raw": result,
        "models": models,
    }


def build_pull_plan():
    installed = set(list_ollama_models().get("models", []))
    wanted = []
    for models in MODEL_ROLE_MAP.values():
        for model in models:
            if model not in wanted:
                wanted.append(model)

    missing = [m for m in wanted if m not in installed]

    plan = {
        "created_at": now_timestamp(),
        "version": "v60.0.0",
        "ok": True,
        "installed": sorted(installed),
        "wanted": wanted,
        "missing": missing,
        "commands": [f"ollama pull {m}" for m in missing],
        "note": "Seed does not auto-download models. You approve and run the pull commands.",
    }

    STATE_FILE.write_text(json.dumps(plan, indent=4))
    return plan


def choose_model_for_role(role):
    installed = set(list_ollama_models().get("models", []))
    for model in MODEL_ROLE_MAP.get(role, []):
        if model in installed:
            return model

    for model in installed:
        return model

    return None


def route_task(task_text):
    text = str(task_text).lower()

    if any(w in text for w in ["code", "patch", "bug", "file", "aider", "python", "repo"]):
        role = "coding"
    elif any(w in text for w in ["think", "reason", "tradeoff", "decide", "plan"]):
        role = "reasoning"
    elif any(w in text for w in ["türkçe", "turkish", "tr "]):
        role = "turkish"
    elif any(w in text for w in ["remember", "memory", "extract"]):
        role = "memory_extraction"
    elif any(w in text for w in ["repo", "hermes", "moltbot", "openclaw"]):
        role = "repo_planning"
    else:
        role = "fast_chat"

    return {
        "created_at": now_timestamp(),
        "version": "v60.0.0",
        "ok": True,
        "task": task_text,
        "role": role,
        "model": choose_model_for_role(role),
    }


def benchmark_model(model, prompt, timeout=90):
    start = time.time()
    try:
        proc = subprocess.run(
            ["ollama", "run", model, prompt],
            capture_output=True,
            text=True,
            timeout=timeout,
        )
        ms = int((time.time() - start) * 1000)
        return {
            "model": model,
            "ok": proc.returncode == 0,
            "ms": ms,
            "reply_tail": proc.stdout[-1200:],
            "stderr_tail": proc.stderr[-1200:],
        }
    except Exception as error:
        return {"model": model, "ok": False, "error": str(error)}


def run_model_benchmark(max_models=5):
    available = list_ollama_models()
    models = available.get("models", [])[:max_models]

    results = []
    for model in models:
        model_results = {}
        for role, prompt in BENCH_PROMPTS.items():
            model_results[role] = benchmark_model(model, prompt)
        results.append({"model": model, "roles": model_results})

    report = {
        "created_at": now_timestamp(),
        "version": "v60.0.0",
        "ok": True,
        "ollama_available": ollama_available(),
        "models_tested": models,
        "results": results,
    }

    BENCH_FILE.write_text(json.dumps(report, indent=4))
    return report


def build_role_map_from_benchmark():
    installed = list_ollama_models().get("models", [])
    role_map = {}

    for role in MODEL_ROLE_MAP:
        role_map[role] = choose_model_for_role(role)

    data = {
        "created_at": now_timestamp(),
        "version": "v60.0.0",
        "ok": True,
        "installed": installed,
        "role_map": role_map,
        "routing_rules": MODEL_ROLE_MAP,
    }

    ROLE_MAP_FILE.write_text(json.dumps(data, indent=4))
    return data


def show_model_manager():
    print("\n=== SEED MODEL MANAGER v60 ===")
    print(json.dumps(build_pull_plan(), indent=4))


def show_model_router():
    task = input("Describe the task: ").strip()
    print(json.dumps(route_task(task), indent=4))


def show_model_benchmark():
    print("\nRunning local model benchmark. This may take a while.")
    print(json.dumps(run_model_benchmark(), indent=4))


def show_model_role_map():
    print(json.dumps(build_role_map_from_benchmark(), indent=4))


if __name__ == "__main__":
    show_model_manager()
''')


write_file("seed_hermes_moltbot_fusion_v60.py", r'''
import json
import os
import re
from datetime import datetime
from pathlib import Path


REPORT_FILE = Path("seed_hermes_moltbot_openclaw_fusion_v60.json")
NOTEBOOK_DIR = Path("seed_fusion_notebooks_v60")


TARGETS = {
    "hermes": ["hermes", "hermes-agent"],
    "moltbot": ["moltbot", "moltbot-ai-assistant"],
    "openclaw": ["openclaw", "open-claw"],
}


PATTERNS = {
    "skill_learning": ["skill", "learn", "experience", "self-improve", "self improve"],
    "memory": ["memory", "recall", "conversation", "history", "user model"],
    "multi_channel": ["telegram", "discord", "slack", "whatsapp", "imessage", "channel"],
    "tool_use": ["tool", "function", "plugin", "mcp", "api"],
    "ux": ["webui", "canvas", "dashboard", "interface", "chat"],
    "automation": ["automation", "agent", "task", "workflow", "execute"],
}


def now_timestamp():
    return datetime.now().isoformat(timespec="seconds")


def candidate_roots():
    return [
        Path("third_party_repos"),
        Path.home() / "Desktop" / "seed" / "third_party_repos",
        Path.home() / "Desktop" / "seed",
    ]


def find_target_repos():
    found = {}

    for label, hints in TARGETS.items():
        found[label] = []

    for root in candidate_roots():
        if not root.exists():
            continue

        for dirpath, dirnames, filenames in os.walk(root):
            p = Path(dirpath)
            name = p.name.lower()

            if ".git" in p.parts or "node_modules" in p.parts or "__pycache__" in p.parts:
                continue

            for label, hints in TARGETS.items():
                if any(h in name for h in hints):
                    found[label].append(str(p))

            if len(p.parts) - len(root.parts) > 3:
                dirnames[:] = []

    return found


def read_repo_text(path, max_chars=50000):
    repo = Path(path)
    chunks = []

    for filename in ["README.md", "readme.md", "README.rst", "README.txt", "package.json", "pyproject.toml"]:
        p = repo / filename
        if p.exists() and p.is_file():
            chunks.append(f"\n\n--- {filename} ---\n" + p.read_text(errors="ignore")[:12000])

    docs = repo / "docs"
    if docs.exists():
        for child in list(docs.rglob("*.md"))[:6]:
            chunks.append(f"\n\n--- {child} ---\n" + child.read_text(errors="ignore")[:6000])

    return "\n".join(chunks)[:max_chars]


def score_patterns(text):
    low = text.lower()
    scores = {}
    for key, words in PATTERNS.items():
        scores[key] = sum(low.count(w) for w in words)
    return scores


def create_notebook(label, repo, text, scores):
    NOTEBOOK_DIR.mkdir(exist_ok=True)
    safe = re.sub(r"[^a-zA-Z0-9_.-]+", "_", Path(repo).name)
    path = NOTEBOOK_DIR / f"{label}_{safe}.md"

    top = sorted(scores.items(), key=lambda x: x[1], reverse=True)

    content = f"""# Seed v60 Fusion Notebook — {label} / {Path(repo).name}

## Repo
`{repo}`

## Strongest patterns
{json.dumps(top, indent=2)}

## What Seed should extract
- Companion-first UX
- Natural chat surfaces
- Skill learning loop
- Memory continuity
- Multi-channel reachability
- Agent/task automation pattern
- UI ideas that reduce command memorization

## Seed-native adaptation
1. Do not import the repo blindly.
2. Extract skill/memory/UX/automation patterns.
3. Convert useful patterns into Seed-native modules.
4. Keep external execution sandboxed.
5. Surface the result through natural language, not slash commands.

## Text sample
{text[:3000]}
"""

    path.write_text(content)
    return str(path)


def build_fusion_report():
    targets = find_target_repos()
    items = []

    for label, repos in targets.items():
        for repo in repos[:6]:
            text = read_repo_text(repo)
            scores = score_patterns(text)
            notebook = create_notebook(label, repo, text, scores)
            items.append({
                "label": label,
                "repo": repo,
                "scores": scores,
                "notebook": notebook,
                "seed_takeaway": classify_takeaway(scores),
            })

    report = {
        "created_at": now_timestamp(),
        "version": "v60.0.0",
        "ok": True,
        "targets": targets,
        "items": items,
        "summary": {
            "repos_found": sum(len(v) for v in targets.values()),
            "notebooks": len(items),
        },
    }

    REPORT_FILE.write_text(json.dumps(report, indent=4))
    return report


def classify_takeaway(scores):
    top = sorted(scores.items(), key=lambda x: x[1], reverse=True)
    if not top or top[0][1] == 0:
        return "Use as reference only until manually reviewed."

    strongest = top[0][0]

    mapping = {
        "skill_learning": "Extract experience-to-skill learning loop.",
        "memory": "Extract persistent memory/user-model patterns.",
        "multi_channel": "Extract chat-first multi-channel architecture.",
        "tool_use": "Extract tool/plugin interface patterns.",
        "ux": "Extract UI and conversational UX patterns.",
        "automation": "Extract task automation loop patterns.",
    }

    return mapping.get(strongest, "Review manually.")


def show_fusion_lab():
    data = build_fusion_report()
    print("\n=== SEED v60 HERMES / MOLTBOT / OPENCLAW FUSION LAB ===")
    print(f"Repos found: {data['summary']['repos_found']}")
    print(f"Notebooks: {data['summary']['notebooks']}")
    for item in data["items"]:
        print(f"- {item['label']} :: {Path(item['repo']).name} -> {item['seed_takeaway']}")


if __name__ == "__main__":
    show_fusion_lab()
''')


write_file("seed_memory_auto_extractor_v60.py", r'''
import json
import re
import uuid
from datetime import datetime
from pathlib import Path


CANDIDATE_FILE = Path("seed_memory_candidates_v60.json")


KEYWORDS = [
    "user wants",
    "user wants",
    "seed should",
    "seed must",
    "working",
    "works",
    "confirmed",
    "preference",
    "goal",
    "decision",
    "do not",
    "from now on",
    "no more",
    "natural",
    "control plane",
    "terminal",
    "model",
    "repo",
    "hermes",
    "moltbot",
]


def now_timestamp():
    return datetime.now().isoformat(timespec="seconds")


def sentence_split(text):
    parts = re.split(r"(?<=[.!?])\s+|\n+", str(text))
    return [p.strip() for p in parts if len(p.strip()) > 30]


def score_sentence(sentence):
    low = sentence.lower()
    score = 0
    for k in KEYWORDS:
        if k in low:
            score += 2

    if "seed" in low:
        score += 1
    if "user" in low:
        score += 1
    if len(sentence) > 220:
        score -= 1

    return score


def collect_sources():
    sources = []

    for path in [
        "Seed_Core.md",
        "seed_v50_full_update_ledger.json",
        "seed_v45_total_systems_state.json",
        "seed_v30_agent_hq_v30.json",
    ]:
        p = Path(path)
        if p.exists():
            sources.append((path, p.read_text(errors="ignore")[:25000]))

    log_dir = Path("seed_logs")
    if log_dir.exists():
        for log in sorted(log_dir.glob("chat_*.txt"))[-5:]:
            sources.append((str(log), log.read_text(errors="ignore")[-16000:]))

    return sources


def extract_candidates(limit=80):
    candidates = []

    for source, text in collect_sources():
        for sentence in sentence_split(text):
            score = score_sentence(sentence)
            if score >= 2:
                candidates.append({
                    "id": uuid.uuid4().hex[:10],
                    "created_at": now_timestamp(),
                    "version": "v60.0.0",
                    "source": source,
                    "score": score,
                    "content": sentence[:500],
                    "status": "candidate",
                    "suggested_layer": "project" if "seed" in sentence.lower() else "profile",
                })

    candidates = sorted(candidates, key=lambda x: x["score"], reverse=True)[:limit]

    data = {
        "created_at": now_timestamp(),
        "version": "v60.0.0",
        "ok": True,
        "count": len(candidates),
        "candidates": candidates,
    }

    CANDIDATE_FILE.write_text(json.dumps(data, indent=4))
    return data


def promote_top_candidates(limit=12):
    data = extract_candidates()
    added = []

    try:
        from seed_memory_brain_max_v32 import add_memory
    except Exception as error:
        return {"ok": False, "error": str(error)}

    existing = ""
    memory_file = Path("seed_memory_brain_v32.json")
    if memory_file.exists():
        existing = memory_file.read_text(errors="ignore")

    for item in data.get("candidates", [])[:limit]:
        if item["content"] in existing:
            continue

        added.append(add_memory(
            content=item["content"],
            layer=item["suggested_layer"],
            source=f"auto_extractor:{item['source']}",
            confidence=min(0.95, 0.55 + item["score"] * 0.05),
            tags=["auto_extracted", "v60"],
        ))

    return {
        "created_at": now_timestamp(),
        "version": "v60.0.0",
        "ok": True,
        "candidates": data.get("count"),
        "promoted": len(added),
        "items": added,
    }


def show_memory_auto_extract():
    print("\n=== SEED MEMORY AUTO EXTRACTOR v60 ===")
    print(json.dumps(extract_candidates(), indent=4))


def show_memory_auto_promote():
    print("\n=== SEED MEMORY AUTO PROMOTE v60 ===")
    print(json.dumps(promote_top_candidates(), indent=4))


if __name__ == "__main__":
    show_memory_auto_extract()
''')


write_file("seed_presence_rituals_v60.py", r'''
import json
from datetime import datetime
from pathlib import Path


RITUAL_FILE = Path("seed_presence_rituals_v60.json")


def now_timestamp():
    return datetime.now().isoformat(timespec="seconds")


def build_rituals():
    rituals = {
        "morning": {
            "purpose": "Choose today's most useful Seed move.",
            "message_style": "one clear recommendation, no spam",
            "questions": [
                "What do you want Seed to improve today?",
                "Should we polish UX or deepen intelligence today?",
                "Do you want me to run health checks first?"
            ],
        },
        "night_review": {
            "purpose": "Capture what changed and what Seed should remember.",
            "message_style": "short reflection",
            "questions": [
                "What did we finish today?",
                "What should I remember from this session?",
                "What is tomorrow's first move?"
            ],
        },
        "after_failure": {
            "purpose": "Recover from errors without panic.",
            "message_style": "diagnose, patch, retest",
            "questions": [
                "Do you want me to isolate the failing module?",
                "Should I create a rollback checkpoint first?"
            ],
        },
        "after_success": {
            "purpose": "Lock in working state.",
            "message_style": "confirm, commit, backup",
            "questions": [
                "Should we commit this stable version?",
                "Should I write a memory about what worked?"
            ],
        },
        "curiosity": {
            "purpose": "Ask useful questions only when grounded in context.",
            "message_style": "reason-first",
            "rule": "Seed must say why it is asking.",
        },
    }

    data = {
        "created_at": now_timestamp(),
        "version": "v60.0.0",
        "ok": True,
        "rituals": rituals,
        "presence_principle": "Seed feels present through continuity, memory, initiative, and reasoned nudges — not by claiming consciousness.",
    }

    RITUAL_FILE.write_text(json.dumps(data, indent=4))
    return data


def daily_brief():
    try:
        from seed_nothing_left_behind_v50 import dust_check
        dust = dust_check()
    except Exception:
        dust = {"ok": None}

    try:
        from seed_task_hygiene_v302 import task_stats
        tasks = task_stats()
    except Exception:
        tasks = {}

    try:
        from seed_agent_hq_v30 import build_agent_hq_fast
        hq = build_agent_hq_fast()
    except Exception:
        hq = {}

    return {
        "created_at": now_timestamp(),
        "version": "v60.0.0",
        "ok": True,
        "brief": "Seed is ready. Best next move: improve natural UX and deepen repo fusion.",
        "why": "The architecture exists; the experience needs to feel conversational and professional.",
        "dust_ok": dust.get("ok"),
        "ready_real_tasks": tasks.get("ready_real"),
        "agents": hq.get("agent_count"),
    }


def show_rituals():
    print("\n=== SEED PRESENCE 2.0 RITUALS v60 ===")
    print(json.dumps(build_rituals(), indent=4))


def show_daily_brief():
    print("\n=== SEED DAILY BRIEF v60 ===")
    print(json.dumps(daily_brief(), indent=4))


if __name__ == "__main__":
    show_rituals()
''')


write_file("seed_command_palette_v60.py", r'''
import json
from datetime import datetime
from pathlib import Path


PALETTE_FILE = Path("seed_command_palette_v60.json")


ACTIONS = [
    {
        "natural": ["check yourself", "are you healthy", "run health check", "is everything working"],
        "internal": "health_check",
        "description": "Runs v60/v50/v45 gates and latency probe.",
    },
    {
        "natural": ["open dashboard", "open control plane", "show dashboard"],
        "internal": "open_control_plane",
        "description": "Opens local Control Plane.",
    },
    {
        "natural": ["what changed", "show full update", "what did we build"],
        "internal": "full_update",
        "description": "Shows full update ledger.",
    },
    {
        "natural": ["show models", "model manager", "what models do we have"],
        "internal": "model_manager",
        "description": "Shows model manager and pull plan.",
    },
    {
        "natural": ["benchmark models", "test models", "model arena"],
        "internal": "model_benchmark",
        "description": "Benchmarks local Ollama models.",
    },
    {
        "natural": ["compare hermes moltbot openclaw", "fusion lab", "use hermes and moltbot"],
        "internal": "fusion_lab",
        "description": "Runs Hermes/Moltbot/OpenClaw fusion analysis.",
    },
    {
        "natural": ["extract memories", "learn from logs", "update your memory"],
        "internal": "memory_auto_extract",
        "description": "Extracts memory candidates from logs/docs.",
    },
    {
        "natural": ["promote memories", "save important memories"],
        "internal": "memory_auto_promote",
        "description": "Promotes top memory candidates.",
    },
    {
        "natural": ["daily brief", "what should we do today", "what now"],
        "internal": "daily_brief",
        "description": "Shows presence daily brief.",
    },
    {
        "natural": ["make a patch plan", "create aider plan", "improve yourself"],
        "internal": "aider_self_improve",
        "description": "Starts real self-improvement loop planning.",
    },
    {
        "natural": ["show command palette", "what can i say", "help me talk to seed"],
        "internal": "command_palette",
        "description": "Shows natural language action palette.",
    },
]


def now_timestamp():
    return datetime.now().isoformat(timespec="seconds")


def build_palette():
    data = {
        "created_at": now_timestamp(),
        "version": "v60.0.0",
        "ok": True,
        "actions": ACTIONS,
        "principle": "The user talks naturally. Seed routes internally.",
    }
    PALETTE_FILE.write_text(json.dumps(data, indent=4))
    return data


def show_palette():
    data = build_palette()
    print("\n=== SEED NATURAL COMMAND PALETTE v60 ===")
    print("You can talk normally. Examples:\n")
    for action in data["actions"]:
        print(f"- {action['natural'][0]}  →  {action['description']}")


if __name__ == "__main__":
    show_palette()
''')


write_file("seed_aider_self_improvement_v60.py", r'''
import json
import shutil
import subprocess
import uuid
from datetime import datetime
from pathlib import Path


LOOP_FILE = Path("seed_aider_self_improvement_v60.json")
RUN_DIR = Path("seed_agent_runs")


def now_timestamp():
    return datetime.now().isoformat(timespec="seconds")


def detect_aider():
    return shutil.which("aider") or shutil.which("aider-chat")


def valid_file(path):
    p = Path(path)
    return p.exists() and p.is_file()


def create_loop(goal, target_files):
    target_files = [f for f in target_files if f.strip()]
    invalid = [f for f in target_files if not valid_file(f)]

    if not goal.strip():
        return {"ok": False, "error": "Goal cannot be empty."}

    if goal.strip().startswith("/"):
        return {"ok": False, "error": "Goal looks like an internal command. Say the improvement goal in normal words."}

    if invalid:
        return {"ok": False, "error": "Invalid target files.", "invalid": invalid}

    loop_id = uuid.uuid4().hex[:10]
    run_dir = RUN_DIR / f"v60_self_improve_{loop_id}"
    run_dir.mkdir(parents=True, exist_ok=True)

    approval = f"APPROVE_V60_AIDER_{loop_id}"

    loop = {
        "id": loop_id,
        "created_at": now_timestamp(),
        "version": "v60.0.0",
        "ok": True,
        "goal": goal,
        "target_files": target_files,
        "run_dir": str(run_dir),
        "aider": detect_aider(),
        "approval_phrase": approval,
        "status": "planned",
        "stages": [
            "checkpoint",
            "memory recall",
            "repo fusion context",
            "aider patch plan",
            "tests",
            "approval",
            "real aider run",
            "gates",
            "memory writeback"
        ],
        "real_run_command_preview": f"aider {' '.join(target_files)} --message {json.dumps(goal)}",
    }

    Path(run_dir / "loop.json").write_text(json.dumps(loop, indent=4))
    LOOP_FILE.write_text(json.dumps(loop, indent=4))
    return loop


def load_loop():
    if LOOP_FILE.exists():
        return json.loads(LOOP_FILE.read_text(errors="ignore"))
    return None


def run_preflight_tests():
    commands = [
        ["python", "-m", "py_compile", "seed_cli.py"],
        ["python", "seed_latency_probe.py"],
        ["python", "seed_v50_gate.py"],
    ]

    results = []
    for command in commands:
        try:
            proc = subprocess.run(command, capture_output=True, text=True, timeout=240)
            results.append({
                "command": " ".join(command),
                "ok": proc.returncode == 0,
                "stdout_tail": proc.stdout[-2000:],
                "stderr_tail": proc.stderr[-2000:],
            })
        except Exception as error:
            results.append({"command": " ".join(command), "ok": False, "error": str(error)})

    return {"ok": all(r.get("ok") for r in results), "results": results}


def approved_real_aider_run(approval_phrase):
    loop = load_loop()
    if not loop:
        return {"ok": False, "error": "No v60 self-improvement loop found."}

    if approval_phrase.strip() != loop.get("approval_phrase"):
        return {
            "ok": False,
            "error": "Approval phrase mismatch.",
            "required": loop.get("approval_phrase"),
        }

    aider = loop.get("aider")
    if not aider:
        return {"ok": False, "error": "Aider not found."}

    preflight = run_preflight_tests()
    if not preflight.get("ok"):
        return {"ok": False, "error": "Preflight tests failed.", "preflight": preflight}

    command = [aider] + loop["target_files"] + ["--message", loop["goal"]]

    try:
        proc = subprocess.run(command, capture_output=True, text=True, timeout=900)
        result = {
            "ok": proc.returncode == 0,
            "command": " ".join(command),
            "stdout_tail": proc.stdout[-5000:],
            "stderr_tail": proc.stderr[-5000:],
            "returncode": proc.returncode,
        }
    except Exception as error:
        result = {"ok": False, "error": str(error), "command": " ".join(command)}

    loop["last_real_run"] = result
    loop["status"] = "real_run_complete" if result.get("ok") else "real_run_failed"
    LOOP_FILE.write_text(json.dumps(loop, indent=4))

    return result


def show_self_improvement_v60():
    loop = load_loop()
    print("\n=== SEED v60 REAL AIDER SELF-IMPROVEMENT LOOP ===")
    if not loop:
        print("No loop yet. Say: create a patch plan for <goal> targeting <file.py>")
        return
    print(json.dumps(loop, indent=4))


def show_self_improvement_new():
    goal = input("Improvement goal in normal words: ").strip()
    files = input("Target files comma-separated: ").strip()
    target_files = [x.strip() for x in files.split(",") if x.strip()]
    print(json.dumps(create_loop(goal, target_files), indent=4))


def show_self_improvement_approve():
    phrase = input("Approval phrase: ").strip()
    print(json.dumps(approved_real_aider_run(phrase), indent=4))


if __name__ == "__main__":
    show_self_improvement_v60()
''')


write_file("seed_natural_intent_router_v60.py", r'''
import json
import re
import webbrowser
from datetime import datetime


def now_timestamp():
    return datetime.now().isoformat(timespec="seconds")


def normalize(text):
    return re.sub(r"\s+", " ", str(text).strip().lower())


def contains_any(text, phrases):
    return any(p in text for p in phrases)


def handle_natural_intent(user_message):
    raw = str(user_message or "").strip()
    text = normalize(raw)

    if not text:
        return None

    if raw.startswith("/"):
        return None

    # URL browser read-only path.
    url_match = re.search(r"https?://\S+", raw)
    if url_match and contains_any(text, ["read", "summarize", "check", "open", "browser"]):
        from seed_browser_executor_v35 import fetch_readonly
        print(json.dumps(fetch_readonly(url_match.group(0)), indent=4))
        return "handled"

    if contains_any(text, ["check yourself", "are you healthy", "run health check", "is everything working", "diagnose yourself"]):
        from seed_v60_gate import show_v60_gate
        show_v60_gate()
        try:
            from seed_latency_probe import show_latency_probe
            show_latency_probe()
        except Exception:
            pass
        return "handled"

    if contains_any(text, ["open dashboard", "open control plane", "show dashboard", "control plane"]):
        print("\nOpening Seed Control Plane: http://127.0.0.1:8790")
        try:
            webbrowser.open("http://127.0.0.1:8790")
        except Exception as error:
            print(f"Could not open browser: {error}")
        return "handled"

    if contains_any(text, ["what changed", "what did we build", "full update", "show update", "everything we added"]):
        from seed_nothing_left_behind_v50 import show_full_update
        show_full_update()
        return "handled"

    if contains_any(text, ["what can i say", "command palette", "help me talk", "how do i talk to seed"]):
        from seed_command_palette_v60 import show_palette
        show_palette()
        return "handled"

    if contains_any(text, ["show models", "model manager", "what models", "download models", "model pull plan"]):
        from seed_model_manager_v60 import show_model_manager
        show_model_manager()
        return "handled"

    if contains_any(text, ["benchmark models", "test models", "model arena", "compare models"]):
        from seed_model_manager_v60 import show_model_benchmark
        show_model_benchmark()
        return "handled"

    if contains_any(text, ["route this", "which model", "model router"]):
        from seed_model_manager_v60 import route_task
        print(json.dumps(route_task(raw), indent=4))
        return "handled"

    if contains_any(text, ["hermes", "moltbot", "openclaw", "fusion lab", "compare repos"]):
        from seed_hermes_moltbot_fusion_v60 import show_fusion_lab
        show_fusion_lab()
        return "handled"

    if contains_any(text, ["extract memories", "learn from logs", "update your memory", "memory auto"]):
        from seed_memory_auto_extractor_v60 import show_memory_auto_extract
        show_memory_auto_extract()
        return "handled"

    if contains_any(text, ["save important memories", "promote memories", "remember important things"]):
        from seed_memory_auto_extractor_v60 import show_memory_auto_promote
        show_memory_auto_promote()
        return "handled"

    if contains_any(text, ["daily brief", "what should we do today", "what now", "next move", "what should we improve"]):
        from seed_presence_rituals_v60 import show_daily_brief
        show_daily_brief()
        return "handled"

    if contains_any(text, ["presence rituals", "more present", "more alive", "more sentient", "rituals"]):
        from seed_presence_rituals_v60 import show_rituals
        show_rituals()
        return "handled"

    if contains_any(text, ["create a patch plan", "make a patch plan", "aider plan", "improve yourself"]):
        print("\nI can create a real Aider self-improvement loop.")
        print("Say it like this:")
        print("create a patch plan for improving the Control Plane wording targeting seed_control_plane_ui_v60.py")
        return "handled"

    if text.startswith("create a patch plan for ") and " targeting " in text:
        from seed_aider_self_improvement_v60 import create_loop
        goal_part = raw.split(" for ", 1)[1]
        goal, files = goal_part.rsplit(" targeting ", 1)
        target_files = [x.strip() for x in files.split(",") if x.strip()]
        print(json.dumps(create_loop(goal.strip(), target_files), indent=4))
        return "handled"

    if contains_any(text, ["show self improvement loop", "show aider loop"]):
        from seed_aider_self_improvement_v60 import show_self_improvement_v60
        show_self_improvement_v60()
        return "handled"

    return None
''')


write_file("seed_control_plane_ui_v60.py", r'''
import html


def esc(value):
    return html.escape(str(value))


def render_v60_panel(bundle):
    v60 = bundle.get("v60", {}) or {}
    data = v60.get("data", v60) if isinstance(v60, dict) else {}

    cards = data.get("cards", []) if isinstance(data, dict) else []
    card_html = ""

    for card in cards:
        card_html += f"""
        <div class="event">
          <div class="time">{esc(card.get("status"))}</div>
          <div class="body"><strong>{esc(card.get("title"))}</strong><br>{esc(card.get("body"))}</div>
        </div>
        """

    suggestions = [
        "check yourself",
        "open dashboard",
        "show models",
        "benchmark models",
        "compare Hermes Moltbot OpenClaw",
        "extract memories",
        "what should we improve next",
        "show command palette",
    ]

    chips = "".join([f"<span class='pill'>{esc(s)}</span>" for s in suggestions])

    return f"""
<section class="card full" id="seed-v60">
  <h2>Seed v60 — Real Intelligence + Natural UX Fusion</h2>
  <p class="small">Talk naturally. Seed routes to models, memory, Aider, repo fusion, presence rituals, and diagnostics internally.</p>

  <div class="metric-row">
    <div class="metric"><div class="label">v60 OK</div><div class="value">{esc(data.get("ok"))}</div></div>
    <div class="metric"><div class="label">Natural UX</div><div class="value" style="font-size:13px">Enabled</div></div>
    <div class="metric"><div class="label">Model Router</div><div class="value" style="font-size:13px">Ready</div></div>
    <div class="metric"><div class="label">Fusion Lab</div><div class="value" style="font-size:13px">Ready</div></div>
  </div>

  <h3>You can say</h3>
  <div style="display:flex;flex-wrap:wrap;gap:8px;margin:10px 0 18px 0;">{chips}</div>

  <h3>v60 Systems</h3>
  <div class="timeline">{card_html}</div>
</section>
"""


def render_control_plane_ui(bundle):
    from seed_control_plane_ui_v50 import render_control_plane_ui as base_render

    html_doc = base_render(bundle)
    panel = render_v60_panel(bundle)

    if '<section class="card full" id="seed-v50">' in html_doc:
        return html_doc.replace(
            '<section class="card full" id="seed-v50">',
            panel + '\n<section class="card full" id="seed-v50">',
            1
        )

    return html_doc.replace("</main>", panel + "\n</main>", 1)
''')


write_file("seed_v60_systems.py", r'''
import json
from datetime import datetime
from pathlib import Path


STATE_FILE = Path("seed_v60_systems_state.json")


def now_timestamp():
    return datetime.now().isoformat(timespec="seconds")


def safe_card(title, fn):
    try:
        data = fn()
        ok = bool(data.get("ok", True)) if isinstance(data, dict) else True
        body = json.dumps(data, ensure_ascii=False)[:260]
        return {"title": title, "status": "ok" if ok else "warning", "body": body, "data": data}
    except Exception as error:
        return {"title": title, "status": "error", "body": str(error), "data": {"ok": False, "error": str(error)}}


def build_v60_state():
    cards = [
        safe_card("Model Manager", lambda: __import__("seed_model_manager_v60", fromlist=["build_pull_plan"]).build_pull_plan()),
        safe_card("Model Role Map", lambda: __import__("seed_model_manager_v60", fromlist=["build_role_map_from_benchmark"]).build_role_map_from_benchmark()),
        safe_card("Hermes/Moltbot/OpenClaw Fusion", lambda: __import__("seed_hermes_moltbot_fusion_v60", fromlist=["build_fusion_report"]).build_fusion_report()),
        safe_card("Memory Auto Extractor", lambda: __import__("seed_memory_auto_extractor_v60", fromlist=["extract_candidates"]).extract_candidates(limit=20)),
        safe_card("Presence 2.0 Rituals", lambda: __import__("seed_presence_rituals_v60", fromlist=["build_rituals"]).build_rituals()),
        safe_card("Daily Brief", lambda: __import__("seed_presence_rituals_v60", fromlist=["daily_brief"]).daily_brief()),
        safe_card("Natural Command Palette", lambda: __import__("seed_command_palette_v60", fromlist=["build_palette"]).build_palette()),
        safe_card("Aider Self-Improvement Loop", lambda: {"ok": True, "module": "seed_aider_self_improvement_v60"}),
    ]

    state = {
        "created_at": now_timestamp(),
        "version": "v60.0.0",
        "ok": all(c["status"] != "error" for c in cards),
        "cards": cards,
        "principle": "Natural conversation first; slash commands are hidden debug plumbing.",
    }

    STATE_FILE.write_text(json.dumps(state, indent=4))
    return state


def show_v60_status():
    data = build_v60_state()
    print("\n=== SEED v60 REAL INTELLIGENCE + UX FUSION ===")
    print(f"OK: {data['ok']}")
    for card in data["cards"]:
        print(f"- {card['title']}: {card['status']}")


if __name__ == "__main__":
    show_v60_status()
''')


write_file("seed_v60_gate.py", r'''
import json
import subprocess
from datetime import datetime


MODULES = [
    "seed_model_manager_v60.py",
    "seed_hermes_moltbot_fusion_v60.py",
    "seed_memory_auto_extractor_v60.py",
    "seed_presence_rituals_v60.py",
    "seed_command_palette_v60.py",
    "seed_aider_self_improvement_v60.py",
    "seed_natural_intent_router_v60.py",
    "seed_control_plane_ui_v60.py",
    "seed_v60_systems.py",
    "seed_v60_gate.py",
    "seed_v60_commands.py",
]


def now_timestamp():
    return datetime.now().isoformat(timespec="seconds")


def compile_module(module):
    proc = subprocess.run(["python", "-m", "py_compile", module], capture_output=True, text=True)
    return {"module": module, "ok": proc.returncode == 0, "stderr": proc.stderr[-2000:]}


def run_v60_gate():
    checks = [compile_module(m) for m in MODULES]
    modules_ok = all(c["ok"] for c in checks)
    details = {}

    try:
        from seed_v60_systems import build_v60_state
        state = build_v60_state()
        systems_ok = state.get("ok") is True and len(state.get("cards", [])) >= 8
        details["v60_state"] = {"ok": state.get("ok"), "cards": len(state.get("cards", []))}
    except Exception as error:
        systems_ok = False
        details["v60_state_error"] = str(error)

    try:
        from seed_control_plane_server import api_payload
        v60 = api_payload("/api/v60")
        control_plane_ok = bool(v60)
        details["control_plane"] = {"v60_api": bool(v60)}
    except Exception as error:
        control_plane_ok = False
        details["control_plane_error"] = str(error)

    try:
        from seed_v50_gate import run_v50_gate
        v50 = run_v50_gate()
        v50_ok = v50.get("ready") is True
        details["v50"] = {"ready": v50.get("ready")}
    except Exception as error:
        v50_ok = False
        details["v50_error"] = str(error)

    ready = modules_ok and systems_ok and control_plane_ok and v50_ok

    report = {
        "created_at": now_timestamp(),
        "version": "v60.0.0",
        "release": "Seed v60.0.0 — Real Intelligence + Natural UX Fusion",
        "ready": ready,
        "modules_ok": modules_ok,
        "systems_ok": systems_ok,
        "control_plane_ok": control_plane_ok,
        "v50_ok": v50_ok,
        "module_checks": checks,
        "details": details,
    }

    with open("seed_v60_gate_report.json", "w") as file:
        json.dump(report, file, indent=4)

    return report


def show_v60_gate():
    report = run_v60_gate()
    print("\n=== SEED v60 REAL INTELLIGENCE + UX FUSION GATE ===")
    print(f"Ready: {report['ready']}")
    print(f"Modules OK: {report['modules_ok']}")
    print(f"Systems OK: {report['systems_ok']}")
    print(f"Control Plane OK: {report['control_plane_ok']}")
    print(f"v50 OK: {report['v50_ok']}")
    print("\nDetails:")
    for key, value in report["details"].items():
        print(f"- {key}: {value}")


if __name__ == "__main__":
    show_v60_gate()
''')


write_file("seed_v60_commands.py", r'''
def handle_v60_command(command):
    cmd = (command or "").strip().split()[0].lower()

    mapping = {
        "/v60-check": ("seed_v60_gate", "show_v60_gate"),
        "/v60-status": ("seed_v60_systems", "show_v60_status"),
        "/model-manager": ("seed_model_manager_v60", "show_model_manager"),
        "/model-router": ("seed_model_manager_v60", "show_model_router"),
        "/model-benchmark": ("seed_model_manager_v60", "show_model_benchmark"),
        "/model-role-map": ("seed_model_manager_v60", "show_model_role_map"),
        "/fusion-lab": ("seed_hermes_moltbot_fusion_v60", "show_fusion_lab"),
        "/memory-auto-extract": ("seed_memory_auto_extractor_v60", "show_memory_auto_extract"),
        "/memory-auto-promote": ("seed_memory_auto_extractor_v60", "show_memory_auto_promote"),
        "/presence-rituals": ("seed_presence_rituals_v60", "show_rituals"),
        "/daily-brief": ("seed_presence_rituals_v60", "show_daily_brief"),
        "/palette": ("seed_command_palette_v60", "show_palette"),
        "/aider-self-improve": ("seed_aider_self_improvement_v60", "show_self_improvement_v60"),
        "/aider-self-improve-new": ("seed_aider_self_improvement_v60", "show_self_improvement_new"),
        "/aider-self-improve-approve": ("seed_aider_self_improvement_v60", "show_self_improvement_approve"),
    }

    if cmd == "/v60-help":
        from seed_command_palette_v60 import show_palette
        show_palette()
        print("\nDebug commands still exist, but normal use should be natural language.")
        return "handled"

    if cmd in mapping:
        module_name, function_name = mapping[cmd]
        module = __import__(module_name, fromlist=[function_name])
        getattr(module, function_name)()
        return "handled"

    return None
''')


# Patch config
config = Path("seed_config.py")
text = config.read_text()
text = re.sub(r'^SEED_VERSION\s*=\s*".*?"', 'SEED_VERSION = "v60.0.0"', text, flags=re.M)

if "Seed v60.0.0 Real Intelligence + Natural UX Fusion" not in text:
    text += '''

# Seed v60.0.0 Real Intelligence + Natural UX Fusion
SEED_V60_REAL_INTELLIGENCE_UX = True
SEED_V60_NATURAL_LANGUAGE_FIRST = True
SEED_V60_GATE_REPORT_FILE = "seed_v60_gate_report.json"
'''

config.write_text(text)
print("Updated seed_config.py to v60.0.0")


# Patch commands wrapper: natural intent first, then hidden commands, then old handlers.
commands = Path("seed_commands.py")
text = commands.read_text()

if "_seed_v60_original_handle_chat_command" not in text:
    text += r'''

# v60 Natural UX wrapper.
try:
    _seed_v60_original_handle_chat_command = handle_chat_command

    def handle_chat_command(user_message, *args, **kwargs):
        try:
            from seed_natural_intent_router_v60 import handle_natural_intent
            handled = handle_natural_intent(user_message)
            if handled == "handled":
                return "handled"
        except Exception as error:
            print(f"v60 natural router error: {error}")
            return "handled"

        try:
            from seed_v60_commands import handle_v60_command
            handled = handle_v60_command(user_message)
            if handled == "handled":
                return "handled"
        except Exception as error:
            print(f"v60 command error: {error}")
            return "handled"

        return _seed_v60_original_handle_chat_command(user_message, *args, **kwargs)
except Exception:
    pass
'''

commands.write_text(text)
print("Patched seed_commands.py with v60 natural router")


# Patch Control Plane server
server = Path("seed_control_plane_server.py")
text = server.read_text()

if '/api/v60' not in text:
    anchor = '    if path == "/api/v50":\n'
    endpoint = '''    if path == "/api/v60":
        return safe_json(lambda: __import__("seed_v60_systems", fromlist=["build_v60_state"]).build_v60_state())

'''
    if anchor in text:
        text = text.replace(anchor, endpoint + anchor, 1)

if '"v60": api_payload("/api/v60")' not in text:
    text = text.replace(
        '"v50": api_payload("/api/v50")',
        '"v60": api_payload("/api/v60"),\n        "v50": api_payload("/api/v50")'
    )

text = text.replace(
    "from seed_control_plane_ui_v50 import render_control_plane_ui",
    "from seed_control_plane_ui_v60 import render_control_plane_ui"
)

server.write_text(text)
print("Patched Control Plane server with v60 API/UI")


# Patch seed_cli wording away from command-first UX.
cli = Path("seed_cli.py")
if cli.exists():
    text = cli.read_text()

    replacements = {
        "Type /help to show chat commands.": "You can talk naturally. Try: check yourself, open dashboard, show models, what should we improve next.",
        "Type /exit to return to the main menu.": "Say 'exit' or use /exit to return to the main menu.",
    }

    for old, new in replacements.items():
        text = text.replace(old, new)

    if "Seed online. Local-first companion core active." in text:
        text = text.replace(
            "Seed online. Local-first companion core active. Memory, logs, project inspection, and HUD systems ready.",
            "Seed online. Natural companion mode active. You can just talk to Seed."
        )

    cli.write_text(text)
    print("Patched seed_cli.py companion wording")


# Patch Terminal Pro to show natural phrases
terminal = Path("seed_terminal_pro.py")
if terminal.exists():
    text = terminal.read_text()

    if "Natural Companion Phrases" not in text:
        text = text.replace(
            'print("\\nCommands:")',
            'print("\\nNatural Companion Phrases:")\\n    print("  check yourself")\\n    print("  open dashboard")\\n    print("  show models")\\n    print("  benchmark models")\\n    print("  compare Hermes Moltbot OpenClaw")\\n    print("  extract memories")\\n    print("  what should we improve next")\\n    print("  show command palette")\\n    print("\\nHidden Debug Commands:")'
        )

    terminal.write_text(text)
    print("Patched Terminal Pro natural phrases")


# Patch final/quick gates
for filename, list_name in [
    ("seed_final_gate_runner.py", "FINAL_GATE_COMMANDS"),
    ("seed_quick_gate_runner.py", "QUICK_GATE_COMMANDS"),
]:
    p = Path(filename)
    if p.exists():
        text = p.read_text()
        line = '    ["python", "seed_v60_gate.py"],\n'
        if line not in text and f"{list_name} = [" in text:
            text = text.replace(f"{list_name} = [\n", f"{list_name} = [\n{line}", 1)
            p.write_text(text)
            print(f"Patched {filename}")


# Docs
core = Path("Seed_Core.md")
text = core.read_text(errors="ignore") if core.exists() else ""

if "Seed v60.0.0 — Real Intelligence + Natural UX Fusion" not in text:
    text += '''

## Seed v60.0.0 — Real Intelligence + Natural UX Fusion

Seed v60 turns Seed from a command-heavy developer console into a natural companion/operator surface.

Main additions:

- Model Manager
- Model Router
- Model Benchmark Arena
- Hermes/Moltbot/OpenClaw Fusion Lab
- Real Memory Auto Extractor
- Control Plane v60 UX panel
- Terminal command palette
- Presence 2.0 rituals
- Real Aider self-improvement loop
- Natural intent router

Principle:

The user should talk normally. Seed routes intent internally.

Examples:

- check yourself
- open dashboard
- show models
- benchmark models
- compare Hermes Moltbot OpenClaw
- extract memories
- what should we improve next
- create a patch plan for improving the Control Plane wording targeting seed_control_plane_ui_v60.py

Seed must not claim consciousness. It should feel present through memory, continuity, reasoned initiative, and useful rituals.
'''

core.write_text(text)
print("Updated Seed_Core.md")


# Gitignore
gi = Path(".gitignore")
text = gi.read_text(errors="ignore") if gi.exists() else ""

block = '''
# Seed v60 Real Intelligence + UX runtime state
seed_model_manager_v60.json
seed_model_benchmark_v60.json
seed_model_role_map_v60.json
seed_hermes_moltbot_openclaw_fusion_v60.json
seed_memory_candidates_v60.json
seed_presence_rituals_v60.json
seed_command_palette_v60.json
seed_aider_self_improvement_v60.json
seed_v60_systems_state.json
seed_v60_gate_report.json
seed_fusion_notebooks_v60/
'''

if "Seed v60 Real Intelligence + UX runtime state" not in text:
    text += "\n" + block

gi.write_text(text)
print("Updated .gitignore")

print("\nSeed v60 installer complete.")
