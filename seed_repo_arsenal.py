import json
from datetime import datetime

try:
    from seed_config import SEED_REPO_ARSENAL_STATE_FILE
except Exception:
    SEED_REPO_ARSENAL_STATE_FILE = "seed_repo_arsenal_state.json"

try:
    from seed_companion_os import append_companion_os_event
    COMPANION_OS_AVAILABLE = True
except Exception:
    COMPANION_OS_AVAILABLE = False


def now_timestamp():
    return datetime.now().isoformat(timespec="seconds")


REPO_ARSENAL = [
    {
        "id": "langgraph",
        "name": "LangGraph",
        "category": "agent_graph",
        "best_for": ["stateful agents", "multi-step workflows", "agent graph orchestration"],
        "risk": "diagnostic_or_code_dependency",
        "approval_required": True,
        "status": "candidate",
        "integration_level": "map_only",
        "notes": "Good candidate for structured agent graphs. Do not rewrite Seed around it yet."
    },
    {
        "id": "mastra",
        "name": "Mastra",
        "category": "agent_framework",
        "best_for": ["agent app framework", "tool workflows", "TypeScript agent stack"],
        "risk": "code_dependency",
        "approval_required": True,
        "status": "candidate",
        "integration_level": "map_only",
        "notes": "Useful reference for agent architecture, especially if moving some layers to TS later."
    },
    {
        "id": "mem0",
        "name": "Mem0",
        "category": "memory",
        "best_for": ["long-term AI memory", "memory extraction", "personal memory layer"],
        "risk": "memory_write",
        "approval_required": True,
        "status": "candidate",
        "integration_level": "upgrade_path",
        "notes": "Possible upgrade from JSON semantic memory."
    },
    {
        "id": "qdrant",
        "name": "Qdrant",
        "category": "vector_store",
        "best_for": ["local vector search", "semantic retrieval", "memory/document search"],
        "risk": "local_service",
        "approval_required": True,
        "status": "candidate",
        "integration_level": "upgrade_path",
        "notes": "Good local vector DB candidate."
    },
    {
        "id": "pgvector",
        "name": "pgvector",
        "category": "vector_store",
        "best_for": ["Postgres vector search", "structured + semantic memory"],
        "risk": "database_dependency",
        "approval_required": True,
        "status": "candidate",
        "integration_level": "upgrade_path",
        "notes": "Good if Seed later uses Postgres."
    },
    {
        "id": "llamaindex",
        "name": "LlamaIndex",
        "category": "retrieval",
        "best_for": ["document retrieval", "RAG pipelines", "indexing uploaded docs"],
        "risk": "code_dependency",
        "approval_required": True,
        "status": "candidate",
        "integration_level": "upgrade_path",
        "notes": "Useful for document registry/search upgrades."
    },
    {
        "id": "livekit_agents",
        "name": "LiveKit Agents",
        "category": "voice",
        "best_for": ["realtime voice agents", "audio sessions", "WebRTC voice"],
        "risk": "external_service_or_local_audio",
        "approval_required": True,
        "status": "candidate",
        "integration_level": "future",
        "notes": "Do not enable always-listening. Push-to-talk or explicit session first."
    },
    {
        "id": "pipecat",
        "name": "Pipecat",
        "category": "voice",
        "best_for": ["voice pipeline", "STT/TTS orchestration", "realtime assistant audio"],
        "risk": "local_audio_pipeline",
        "approval_required": True,
        "status": "candidate",
        "integration_level": "future",
        "notes": "Voice pipeline candidate after privacy gates."
    },
    {
        "id": "faster_whisper",
        "name": "faster-whisper",
        "category": "stt",
        "best_for": ["local speech-to-text", "push-to-talk transcription"],
        "risk": "microphone_or_audio_processing",
        "approval_required": True,
        "status": "candidate",
        "integration_level": "future",
        "notes": "Only with explicit push-to-talk boundary."
    },
    {
        "id": "kokoro_tts",
        "name": "Kokoro TTS",
        "category": "tts",
        "best_for": ["local TTS", "lightweight voice output"],
        "risk": "local_audio_output",
        "approval_required": False,
        "status": "candidate",
        "integration_level": "future",
        "notes": "Possible TTS upgrade from macOS say."
    },
    {
        "id": "chatterbox_tts",
        "name": "Chatterbox TTS",
        "category": "tts",
        "best_for": ["expressive TTS", "voice personality layer"],
        "risk": "local_audio_output",
        "approval_required": False,
        "status": "candidate",
        "integration_level": "future",
        "notes": "Treat as interface only, not sentience."
    },
    {
        "id": "godot",
        "name": "Godot",
        "category": "avatar_world",
        "best_for": ["3D avatar", "interactive world", "local companion visual layer"],
        "risk": "large_dependency",
        "approval_required": True,
        "status": "candidate",
        "integration_level": "future",
        "notes": "Useful for real avatar/world, not required for v2 stable."
    },
    {
        "id": "openavatarchat",
        "name": "OpenAvatarChat",
        "category": "avatar",
        "best_for": ["avatar chat interface", "visual companion reference"],
        "risk": "external_code_dependency",
        "approval_required": True,
        "status": "candidate",
        "integration_level": "map_only",
        "notes": "Reference architecture for avatar chat."
    },
    {
        "id": "three_vrm",
        "name": "three-vrm",
        "category": "avatar",
        "best_for": ["browser VRM avatar", "web avatar rendering"],
        "risk": "frontend_dependency",
        "approval_required": True,
        "status": "candidate",
        "integration_level": "future",
        "notes": "Good if cockpit gets a browser avatar."
    },
    {
        "id": "librechat",
        "name": "LibreChat",
        "category": "product_ui",
        "best_for": ["multi-model chat UI reference", "production chat app patterns"],
        "risk": "large_app_dependency",
        "approval_required": True,
        "status": "reference",
        "integration_level": "map_only",
        "notes": "Reference, not something to merge into Seed blindly."
    },
    {
        "id": "anythingllm",
        "name": "AnythingLLM",
        "category": "product_ui",
        "best_for": ["local RAG app reference", "document chat product patterns"],
        "risk": "large_app_dependency",
        "approval_required": True,
        "status": "reference",
        "integration_level": "map_only",
        "notes": "Useful product reference."
    },
    {
        "id": "mcp",
        "name": "MCP servers",
        "category": "tool_protocol",
        "best_for": ["standardized tools", "file/search/browser/tool connectors"],
        "risk": "external_tool_access",
        "approval_required": True,
        "status": "candidate",
        "integration_level": "high_priority_future",
        "notes": "Best long-term tool connector layer."
    },
    {
        "id": "browser_use",
        "name": "browser-use",
        "category": "browser_control",
        "best_for": ["web automation", "browser tasks", "research with UI"],
        "risk": "external_web_action",
        "approval_required": True,
        "status": "candidate",
        "integration_level": "future",
        "notes": "Requires explicit approval, no account actions without permission."
    },
    {
        "id": "openhands",
        "name": "OpenHands",
        "category": "coding_agent",
        "best_for": ["repo coding agent", "issue solving", "local dev automation"],
        "risk": "file_write_and_shell",
        "approval_required": True,
        "status": "candidate",
        "integration_level": "future",
        "notes": "Must run in sandbox/branch with tests and rollback."
    },
    {
        "id": "swe_agent",
        "name": "SWE-agent",
        "category": "coding_agent",
        "best_for": ["software engineering tasks", "patch planning", "test-driven fixes"],
        "risk": "file_write_and_shell",
        "approval_required": True,
        "status": "candidate",
        "integration_level": "future",
        "notes": "Good model for Seed self-improvement workflow."
    },
    {
        "id": "aider",
        "name": "Aider",
        "category": "coding_assistant",
        "best_for": ["direct code edits", "git-aware pair programming"],
        "risk": "file_write",
        "approval_required": True,
        "status": "candidate",
        "integration_level": "future",
        "notes": "Approval required before edits."
    },
    {
        "id": "cline",
        "name": "Cline-style self-edit flow",
        "category": "coding_assistant",
        "best_for": ["IDE-assisted coding", "tool use with approval", "repo edits"],
        "risk": "file_write_and_shell",
        "approval_required": True,
        "status": "reference",
        "integration_level": "map_only",
        "notes": "Reference for approval-based edit UX."
    },
    {
        "id": "nemo_guardrails",
        "name": "NeMo Guardrails",
        "category": "safety",
        "best_for": ["conversation guardrails", "policy rails", "dialogue constraints"],
        "risk": "policy_dependency",
        "approval_required": True,
        "status": "candidate",
        "integration_level": "future",
        "notes": "Possible advanced safety layer."
    },
    {
        "id": "guardrails_ai",
        "name": "Guardrails AI",
        "category": "safety",
        "best_for": ["structured output validation", "schema guardrails"],
        "risk": "policy_dependency",
        "approval_required": True,
        "status": "candidate",
        "integration_level": "future",
        "notes": "Could validate JSON/plans/tool calls."
    },
    {
        "id": "langfuse",
        "name": "Langfuse",
        "category": "observability",
        "best_for": ["LLM traces", "observability", "prompt/run analytics"],
        "risk": "telemetry_external_or_local",
        "approval_required": True,
        "status": "candidate",
        "integration_level": "future",
        "notes": "Prefer local/private mode if used."
    },
    {
        "id": "opentelemetry",
        "name": "OpenTelemetry",
        "category": "observability",
        "best_for": ["system traces", "metrics", "distributed observability"],
        "risk": "telemetry",
        "approval_required": True,
        "status": "candidate",
        "integration_level": "future",
        "notes": "Useful for structured local diagnostics."
    }
]


def load_state():
    try:
        with open(SEED_REPO_ARSENAL_STATE_FILE, "r") as file:
            return json.load(file)
    except Exception:
        return {
            "created_at": now_timestamp(),
            "updated_at": now_timestamp(),
            "version": "v1.19.0",
            "repos": REPO_ARSENAL
        }


def save_state(state):
    state["updated_at"] = now_timestamp()
    with open(SEED_REPO_ARSENAL_STATE_FILE, "w") as file:
        json.dump(state, file, indent=4)


def initialize_repo_arsenal():
    state = load_state()
    existing = {item.get("id") for item in state.get("repos", [])}

    for repo in REPO_ARSENAL:
        if repo["id"] not in existing:
            state.setdefault("repos", []).append(repo)

    save_state(state)

    if COMPANION_OS_AVAILABLE:
        try:
            append_companion_os_event(
                "repo_arsenal_initialized",
                "Repo/tool arsenal initialized",
                {"repo_count": len(state.get("repos", []))},
                source="repo_arsenal",
                importance=4
            )
        except Exception:
            pass

    return state


def get_repo_arsenal():
    return initialize_repo_arsenal().get("repos", [])


def categories():
    cats = {}
    for repo in get_repo_arsenal():
        cats.setdefault(repo.get("category"), []).append(repo)
    return cats


def search_arsenal(query):
    q = query.lower().strip()
    results = []
    for repo in get_repo_arsenal():
        if q in json.dumps(repo).lower():
            results.append(repo)
    return results


def show_repo_arsenal():
    print("\n=== SEED REPO / TOOL ARSENAL ===")
    for category, repos in sorted(categories().items()):
        print(f"\n## {category}")
        for repo in repos:
            print(f"- {repo.get('name')} ({repo.get('id')}) [{repo.get('integration_level')}]")
            print(f"  Best for: {', '.join(repo.get('best_for', []))}")
            print(f"  Risk: {repo.get('risk')} | Approval: {repo.get('approval_required')}")


def show_tool_arsenal():
    show_repo_arsenal()


def show_repo_map():
    cats = categories()
    print("\n=== REPO ARSENAL MAP ===")
    print(f"Total entries: {len(get_repo_arsenal())}")
    for category, repos in sorted(cats.items()):
        print(f"- {category}: {len(repos)}")


def search_arsenal_interactive():
    query = input("Search arsenal: ").strip()
    results = search_arsenal(query)

    print("\n=== ARSENAL SEARCH ===")
    if not results:
        print("No matches.")
        return

    for repo in results:
        print(f"\n{repo.get('name')} ({repo.get('id')})")
        print(f"Category: {repo.get('category')}")
        print(f"Best for: {', '.join(repo.get('best_for', []))}")
        print(f"Risk: {repo.get('risk')}")
        print(f"Approval required: {repo.get('approval_required')}")
        print(repo.get("notes"))


def integration_readiness_data():
    repos = get_repo_arsenal()
    cats = categories()

    high_risk_without_approval = [
        repo for repo in repos
        if repo.get("risk") not in ["diagnostic", "local_audio_output", "read_only"]
        and repo.get("approval_required") is not True
    ]

    return {
        "created_at": now_timestamp(),
        "repo_count": len(repos),
        "category_count": len(cats),
        "categories": {key: len(value) for key, value in cats.items()},
        "high_risk_without_approval": high_risk_without_approval,
        "ready": len(repos) >= 20 and len(cats) >= 8 and not high_risk_without_approval
    }


def show_integration_readiness():
    data = integration_readiness_data()
    print("\n=== ARSENAL INTEGRATION READINESS ===")
    print(f"Ready: {data['ready']}")
    print(f"Repos/tools: {data['repo_count']}")
    print(f"Categories: {data['category_count']}")
    print("\nCategories:")
    for key, value in sorted(data["categories"].items()):
        print(f"- {key}: {value}")

    if data["high_risk_without_approval"]:
        print("\nHigh-risk entries without approval:")
        for repo in data["high_risk_without_approval"]:
            print(f"- {repo.get('name')}")


def get_repo_arsenal_context_for_prompt():
    data = integration_readiness_data()
    text = "=== REPO / TOOL ARSENAL CONTEXT ===\n"
    text += f"Entries: {data['repo_count']}\n"
    text += f"Categories: {data['category_count']}\n"
    text += f"Ready: {data['ready']}\n"
    text += "Categories:\n"
    for key, value in sorted(data["categories"].items()):
        text += f"- {key}: {value}\n"
    text += "\nRule: Seed may recommend and route tools, but must not install/run high-risk tools without approval.\n"
    return text


if __name__ == "__main__":
    show_repo_arsenal()
    show_integration_readiness()
