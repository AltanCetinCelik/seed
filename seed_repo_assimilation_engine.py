import json
from datetime import datetime
from pathlib import Path


try:
    from seed_config import SEED_REPO_ASSIMILATION_FILE
except Exception:
    SEED_REPO_ASSIMILATION_FILE = "seed_repo_assimilation_report.json"


SEARCH_ROOTS = [
    Path("third_party_repos"),
    Path("seed/third_party_repos"),
    Path.home() / "Desktop" / "seed" / "third_party_repos",
    Path.home() / "Desktop" / "seed",
]


def now_timestamp():
    return datetime.now().isoformat(timespec="seconds")


def looks_like_repo(path):
    path = Path(path)
    return (
        (path / ".git").exists()
        or (path / "README.md").exists()
        or (path / "pyproject.toml").exists()
        or (path / "package.json").exists()
    )


def discover_repos(max_repos=120):
    found = []
    seen = set()

    for root in SEARCH_ROOTS:
        if not root.exists():
            continue

        if looks_like_repo(root):
            key = str(root.resolve())
            if key not in seen:
                found.append(root)
                seen.add(key)

        for child in root.iterdir():
            if child.is_dir() and looks_like_repo(child):
                key = str(child.resolve())
                if key not in seen:
                    found.append(child)
                    seen.add(key)

    return found[:max_repos]


def match_known_adapter(repo_name, registry):
    lowered = repo_name.lower()
    adapters = registry.get("adapters", {})

    matches = []
    for name, spec in adapters.items():
        hints = spec.get("repo_hint", [])
        if any(h.lower() in lowered for h in hints):
            matches.append(name)

    return matches


def build_repo_assimilation_report():
    from seed_external_adapter_registry import build_adapter_registry
    from seed_repo_pattern_extractor import extract_repo_patterns
    from seed_repo_risk_scanner import scan_repo_risks

    registry = build_adapter_registry()
    repos = discover_repos()

    items = []
    for repo in repos:
        patterns = extract_repo_patterns(repo)
        risks = scan_repo_risks(repo)
        matches = match_known_adapter(repo.name, registry)

        items.append({
            "repo": str(repo),
            "name": repo.name,
            "known_adapter_matches": matches,
            "patterns": patterns,
            "risks": risks
        })

    report = {
        "created_at": now_timestamp(),
        "version": "v30.0.0",
        "ok": True,
        "repo_count": len(items),
        "items": items,
        "method": "adapter_first_pattern_extraction",
        "rules": {
            "do_not_copy_repos_blindly": True,
            "extract_patterns_first": True,
            "sandbox_high_risk_repos": True,
            "promote_only_after_gates": True
        }
    }

    with open(SEED_REPO_ASSIMILATION_FILE, "w") as file:
        json.dump(report, file, indent=4)

    return report


def show_repo_assimilation():
    report = build_repo_assimilation_report()
    print("\n=== SEED REPO ASSIMILATION ENGINE v30 ===")
    print(f"Repos found: {report['repo_count']}")

    for item in report["items"][:30]:
        pats = ", ".join(item["patterns"].get("patterns", [])) or "no strong pattern"
        risk = item["risks"].get("risk_level")
        matches = ", ".join(item["known_adapter_matches"]) or "unmatched"
        print(f"- {item['name']}: risk={risk}, adapters={matches}, patterns={pats}")


if __name__ == "__main__":
    show_repo_assimilation()
