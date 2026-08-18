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
