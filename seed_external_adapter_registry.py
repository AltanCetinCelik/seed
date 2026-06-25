import json
from datetime import datetime


try:
    from seed_config import SEED_EXTERNAL_ADAPTER_REGISTRY_FILE
except Exception:
    SEED_EXTERNAL_ADAPTER_REGISTRY_FILE = "seed_external_adapter_registry.json"


def now_timestamp():
    return datetime.now().isoformat(timespec="seconds")


ADAPTERS = {
    "aider": {
        "agent": "code_executor",
        "repo_hint": ["aider"],
        "seed_role": "first real patch executor",
        "risk": "medium",
        "promotion": "dry-run -> diff review -> tests -> approval -> real patch",
        "core_modules": ["seed_aider_review_v7.py", "seed_aider_patch_flow.py"]
    },
    "langgraph": {
        "agent": "workflow_runtime",
        "repo_hint": ["langgraph"],
        "seed_role": "durable workflow graph brain",
        "risk": "medium",
        "promotion": "Seed-native workflow first, then optional LangGraph backend",
        "core_modules": ["seed_workflow_graph_v9.py"]
    },
    "mcp": {
        "agent": "tool_marketplace",
        "repo_hint": ["mcp", "modelcontextprotocol"],
        "seed_role": "skill protocol and tool permission layer",
        "risk": "medium",
        "promotion": "allowlist tools only",
        "core_modules": ["seed_mcp_marketplace_v11.py", "seed_mcp_skill_server.py"]
    },
    "mem0": {
        "agent": "memory_agent",
        "repo_hint": ["mem0"],
        "seed_role": "memory extraction and personalization patterns",
        "risk": "medium",
        "promotion": "extractor adapter before backend migration",
        "core_modules": ["seed_memory_engine_v2.py"]
    },
    "qdrant": {
        "agent": "vector_memory_backend",
        "repo_hint": ["qdrant"],
        "seed_role": "semantic memory search backend",
        "risk": "low",
        "promotion": "optional local backend",
        "core_modules": ["seed_memory_engine_v2.py"]
    },
    "browser-use": {
        "agent": "browser_agent",
        "repo_hint": ["browser-use", "browser_use"],
        "seed_role": "read-only browser sandbox executor",
        "risk": "high",
        "promotion": "read-only first, no forms/accounts/purchases without approval",
        "core_modules": ["seed_browser_sandbox_v10.py"]
    },
    "openhands": {
        "agent": "heavy_code_agent",
        "repo_hint": ["openhands"],
        "seed_role": "broad coding agent sandbox",
        "risk": "high",
        "promotion": "sandbox only until Aider loop is stable",
        "core_modules": ["seed_openhands_sandbox_v12.py"]
    },
    "swe-agent": {
        "agent": "repo_repair_agent",
        "repo_hint": ["swe-agent", "mini-swe-agent", "swe_agent"],
        "seed_role": "issue-fixing and benchmarkable repair loop",
        "risk": "high",
        "promotion": "sandbox compare against Aider",
        "core_modules": []
    },
    "cline": {
        "agent": "approval_ux_reference",
        "repo_hint": ["cline"],
        "seed_role": "human-in-loop command/browser/code approval UX",
        "risk": "medium",
        "promotion": "copy UX pattern, not execution blindly",
        "core_modules": []
    },
    "open-interpreter": {
        "agent": "computer_control_reference",
        "repo_hint": ["open-interpreter", "interpreter"],
        "seed_role": "computer-control harness reference",
        "risk": "very_high",
        "promotion": "never direct arbitrary shell; sandbox only",
        "core_modules": []
    },
    "letta": {
        "agent": "stateful_companion_reference",
        "repo_hint": ["letta"],
        "seed_role": "stateful agent and memory architecture ideas",
        "risk": "medium",
        "promotion": "borrow state model concepts",
        "core_modules": []
    },
    "livekit": {
        "agent": "voice_runtime",
        "repo_hint": ["livekit"],
        "seed_role": "production voice agent architecture",
        "risk": "medium",
        "promotion": "later realtime voice service",
        "core_modules": ["seed_voice_runtime_v6.py"]
    },
    "pipecat": {
        "agent": "voice_pipeline",
        "repo_hint": ["pipecat"],
        "seed_role": "realtime voice/multimodal pipeline",
        "risk": "medium",
        "promotion": "push-to-talk before realtime",
        "core_modules": ["seed_voice_runtime_v6.py"]
    },
    "open-webui": {
        "agent": "ui_reference",
        "repo_hint": ["open-webui", "open_webui"],
        "seed_role": "self-hosted local UI patterns",
        "risk": "low",
        "promotion": "borrow UI/workspace ideas",
        "core_modules": []
    },
    "anythingllm": {
        "agent": "workspace_rag_reference",
        "repo_hint": ["anythingllm", "anything-llm"],
        "seed_role": "workspace/docs/agent UX patterns",
        "risk": "low",
        "promotion": "borrow workspace/document pattern",
        "core_modules": []
    },
    "khoj": {
        "agent": "second_brain_reference",
        "repo_hint": ["khoj"],
        "seed_role": "personal second-brain assistant patterns",
        "risk": "low",
        "promotion": "borrow personal knowledge UX",
        "core_modules": []
    }
}


def build_adapter_registry():
    registry = {
        "created_at": now_timestamp(),
        "version": "v30.0.0",
        "ok": True,
        "adapter_first": True,
        "no_blind_installs": True,
        "sandbox_first": True,
        "adapters": ADAPTERS,
        "promotion_loop": [
            "discover repo",
            "extract patterns",
            "score usefulness",
            "scan risk",
            "create adapter plan",
            "sandbox",
            "test gates",
            "manual approval",
            "promote to core"
        ]
    }

    with open(SEED_EXTERNAL_ADAPTER_REGISTRY_FILE, "w") as file:
        json.dump(registry, file, indent=4)

    return registry


def show_adapter_registry():
    data = build_adapter_registry()
    print("\n=== SEED EXTERNAL ADAPTER REGISTRY v30 ===")
    for name, spec in data["adapters"].items():
        print(f"- {name}: {spec['seed_role']} risk={spec['risk']}")


if __name__ == "__main__":
    show_adapter_registry()
