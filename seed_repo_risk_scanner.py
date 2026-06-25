import json
import os
from pathlib import Path


RISK_TERMS = {
    "arbitrary_shell": ["subprocess.run", "os.system", "shell=True", "exec(", "eval("],
    "delete": ["rm -rf", "shutil.rmtree", "unlink(", "delete"],
    "network": ["requests.", "httpx.", "websocket", "socket.", "fetch("],
    "browser_action": ["playwright", "selenium", "browser", "click(", "fill("],
    "secret_handling": ["api_key", "token", "secret", ".env", "authorization"],
    "docker": ["docker", "container", "compose"],
    "git_write": ["git commit", "git push", "git reset", "git checkout"]
}

IGNORE_DIRS = {
    ".git", "node_modules", ".venv", "venv", "__pycache__", ".next", "dist",
    "build", ".cache", ".mypy_cache", ".pytest_cache", "target", ".turbo",
    "site-packages"
}

ALLOWED_SUFFIXES = {".py", ".js", ".ts", ".sh", ".md", ".toml", ".json", ".yml", ".yaml"}


def iter_candidate_files(repo_path, max_files=120):
    repo = Path(repo_path)
    count = 0

    for root, dirs, files in os.walk(repo):
        dirs[:] = [d for d in dirs if d not in IGNORE_DIRS and not d.startswith(".git")]

        for filename in files:
            path = Path(root) / filename

            if path.suffix.lower() not in ALLOWED_SUFFIXES:
                continue

            yield path
            count += 1

            if count >= max_files:
                return


def scan_file(path, max_chars=12000):
    try:
        text = Path(path).read_text(errors="ignore")[:max_chars].lower()
    except Exception:
        return {}

    hits = {}
    for risk, terms in RISK_TERMS.items():
        count = sum(text.count(term.lower()) for term in terms)
        if count:
            hits[risk] = count
    return hits


def scan_repo_risks(repo_path, max_files=120):
    repo = Path(repo_path)
    totals = {}
    files = []

    for path in iter_candidate_files(repo, max_files=max_files):
        hits = scan_file(path)
        if hits:
            files.append({"path": str(path), "hits": hits})
            for k, v in hits.items():
                totals[k] = totals.get(k, 0) + v

    risk_score = 0
    weights = {
        "arbitrary_shell": 5,
        "delete": 5,
        "network": 2,
        "browser_action": 3,
        "secret_handling": 4,
        "docker": 2,
        "git_write": 4
    }

    for risk, count in totals.items():
        risk_score += weights.get(risk, 1) * count

    if risk_score >= 60:
        level = "high"
    elif risk_score >= 20:
        level = "medium"
    else:
        level = "low"

    return {
        "repo": str(repo),
        "name": repo.name,
        "risk_level": level,
        "risk_score": risk_score,
        "risk_totals": totals,
        "files_scanned_limit": max_files,
        "risky_files_sample": files[:12],
        "policy": {
            "adapter_first": True,
            "sandbox_first": level in {"medium", "high"},
            "no_blind_core_import": True
        }
    }


if __name__ == "__main__":
    import sys
    print(json.dumps(scan_repo_risks(sys.argv[1] if len(sys.argv) > 1 else "."), indent=4))
