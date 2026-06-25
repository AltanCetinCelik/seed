import json
from pathlib import Path


IMPORTANT_NAMES = [
    "README.md", "README.rst", "README.txt",
    "docs", "examples", "example", "cookbook",
    "pyproject.toml", "package.json", "requirements.txt"
]


KEYWORDS = {
    "agent": ["agent", "planner", "executor", "tool", "workflow"],
    "memory": ["memory", "vector", "embedding", "recall", "rag"],
    "voice": ["voice", "audio", "stt", "tts", "realtime", "transcript"],
    "browser": ["browser", "web", "playwright", "selenium"],
    "coding": ["patch", "diff", "git", "test", "repo", "code"],
    "mcp": ["mcp", "tool server", "jsonrpc", "protocol"],
    "ui": ["dashboard", "webui", "frontend", "workspace"],
    "risk": ["shell", "subprocess", "docker", "exec", "delete", "rm -rf", "token", "browser"]
}


def read_small(path, max_chars=12000):
    try:
        return Path(path).read_text(errors="ignore")[:max_chars]
    except Exception:
        return ""


def find_docs(repo_path, max_files=30):
    repo = Path(repo_path)
    files = []

    for name in IMPORTANT_NAMES:
        p = repo / name
        if p.is_file():
            files.append(p)
        elif p.is_dir():
            for child in list(p.rglob("*"))[:max_files]:
                if child.is_file() and child.suffix.lower() in {".md", ".rst", ".txt", ".py", ".ts", ".js"}:
                    files.append(child)

    for child in repo.glob("*.md"):
        if child not in files:
            files.append(child)

    return files[:max_files]


def keyword_hits(text):
    low = text.lower()
    out = {}
    for category, words in KEYWORDS.items():
        out[category] = sum(low.count(w) for w in words)
    return out


def extract_repo_patterns(repo_path):
    repo = Path(repo_path)
    docs = find_docs(repo)
    combined = ""

    doc_summaries = []
    for doc in docs:
        text = read_small(doc)
        combined += "\n" + text[:4000]
        doc_summaries.append({
            "path": str(doc),
            "chars": len(text),
            "hits": keyword_hits(text)
        })

    hits = keyword_hits(combined)

    patterns = []
    if hits["agent"] > 0:
        patterns.append("agent orchestration")
    if hits["memory"] > 0:
        patterns.append("memory / RAG")
    if hits["voice"] > 0:
        patterns.append("voice / realtime")
    if hits["browser"] > 0:
        patterns.append("browser automation")
    if hits["coding"] > 0:
        patterns.append("coding executor")
    if hits["mcp"] > 0:
        patterns.append("MCP/tool protocol")
    if hits["ui"] > 0:
        patterns.append("dashboard/workspace UI")

    return {
        "repo": str(repo),
        "name": repo.name,
        "docs_found": len(docs),
        "keyword_hits": hits,
        "patterns": patterns,
        "doc_summaries": doc_summaries[:10]
    }


if __name__ == "__main__":
    import sys
    print(json.dumps(extract_repo_patterns(sys.argv[1] if len(sys.argv) > 1 else "."), indent=4))
