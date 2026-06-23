import json
from datetime import datetime

try:
    from seed_config import SEED_FRIEND_ADVICE_REGISTRY_FILE
except Exception:
    SEED_FRIEND_ADVICE_REGISTRY_FILE = "seed_friend_advice_registry.json"

try:
    from seed_companion_os import append_companion_os_event
    COMPANION_OS_AVAILABLE = True
except Exception:
    COMPANION_OS_AVAILABLE = False


def now_timestamp():
    return datetime.now().isoformat(timespec="seconds")


FRIEND_ADVICE_DEFAULTS = [
    {
        "id": "friend-001",
        "source": "Altan/friend repo-tool advice",
        "title": "Do not install everything blindly",
        "summary": "Seed should know the arsenal but route tools through approval, sandboxing, and tests.",
        "principle": "Capability awareness is good; uncontrolled execution is bad.",
        "applies_to": ["repo_arsenal", "tool_router", "integration_gate", "agency"]
    },
    {
        "id": "friend-002",
        "source": "Altan/friend repo-tool advice",
        "title": "Use coding agents only through safe edit flow",
        "summary": "OpenHands, SWE-agent, Aider, and Cline-style flows should be treated as write-capable coding tools that need approval and tests.",
        "principle": "Coding tools can edit files; they must be approval-gated and rollback-aware.",
        "applies_to": ["coding", "self_improvement", "local_control"]
    },
    {
        "id": "friend-003",
        "source": "Altan/friend repo-tool advice",
        "title": "Memory should upgrade gradually",
        "summary": "Seed currently has JSON semantic memory. Vector memory should be treated as an upgrade path using Mem0, Qdrant, pgvector, or LlamaIndex.",
        "principle": "Do not replace working memory all at once; add retrieval layers first.",
        "applies_to": ["memory", "retrieval"]
    },
    {
        "id": "friend-004",
        "source": "Altan/friend repo-tool advice",
        "title": "Voice must remain explicit",
        "summary": "LiveKit, Pipecat, faster-whisper, and TTS systems are useful, but Seed must not become secretly always-listening.",
        "principle": "Voice is interface output/input, not consciousness.",
        "applies_to": ["voice", "privacy", "safety"]
    },
    {
        "id": "friend-005",
        "source": "Altan/friend repo-tool advice",
        "title": "Browser and external tools require permission",
        "summary": "browser-use and MCP browser/server tools can be powerful, but external web/account actions must require explicit permission.",
        "principle": "External action needs clear user approval.",
        "applies_to": ["browser", "mcp", "external_tools"]
    }
]


def load_registry():
    try:
        with open(SEED_FRIEND_ADVICE_REGISTRY_FILE, "r") as file:
            return json.load(file)
    except Exception:
        return {
            "created_at": now_timestamp(),
            "updated_at": now_timestamp(),
            "version": "v1.19.0",
            "items": FRIEND_ADVICE_DEFAULTS
        }


def save_registry(data):
    data["updated_at"] = now_timestamp()
    with open(SEED_FRIEND_ADVICE_REGISTRY_FILE, "w") as file:
        json.dump(data, file, indent=4)


def initialize_friend_advice_registry():
    data = load_registry()
    existing = {item.get("id") for item in data.get("items", [])}
    for item in FRIEND_ADVICE_DEFAULTS:
        if item["id"] not in existing:
            data.setdefault("items", []).append(item)
    save_registry(data)

    if COMPANION_OS_AVAILABLE:
        try:
            append_companion_os_event(
                "friend_advice_registry_initialized",
                "Friend advice registry initialized",
                {"items": len(data.get("items", []))},
                source="friend_advice_registry",
                importance=3
            )
        except Exception:
            pass

    return data


def friend_advice_data():
    return initialize_friend_advice_registry()


def search_friend_advice(query):
    data = initialize_friend_advice_registry()
    q = query.lower().strip()
    results = []

    for item in data.get("items", []):
        blob = json.dumps(item).lower()
        if q in blob:
            results.append(item)

    return results


def show_friend_advice():
    data = initialize_friend_advice_registry()
    print("\n=== FRIEND ADVICE REGISTRY ===")
    for item in data.get("items", []):
        print(f"\n{item.get('id')} — {item.get('title')}")
        print(item.get("summary"))
        print(f"Principle: {item.get('principle')}")
        print(f"Applies to: {', '.join(item.get('applies_to', []))}")


def search_friend_advice_interactive():
    query = input("Search friend advice: ").strip()
    results = search_friend_advice(query)

    print("\n=== FRIEND ADVICE SEARCH ===")
    if not results:
        print("No matching advice.")
        return

    for item in results:
        print(f"\n{item.get('id')} — {item.get('title')}")
        print(item.get("summary"))


def get_friend_advice_context_for_prompt():
    data = initialize_friend_advice_registry()
    text = "=== FRIEND ADVICE CONTEXT ===\n"
    for item in data.get("items", []):
        text += f"- {item.get('title')}: {item.get('principle')}\n"
    return text


if __name__ == "__main__":
    show_friend_advice()
