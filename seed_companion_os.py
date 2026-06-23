import json
import os
import platform
import shutil
from datetime import datetime


try:
    from seed_config import (
        SEED_VERSION,
        SEED_COMPANION_OS_STATE_FILE,
        SEED_COMPANION_OS_EVENTS_FILE,
        SEED_COMPANION_OS_JOURNAL_FILE,
        SEED_COMPANION_OS_BACKUP_DIR,
        COMPANION_OS_CONTEXT_ENABLED,
        COMPANION_OS_V2_TARGET_SCORE,
        COMPANION_OS_EVENT_LIMIT,
        COMPANION_OS_TIMELINE_LIMIT
    )
except Exception:
    SEED_VERSION = "v1.17.0"
    SEED_COMPANION_OS_STATE_FILE = "seed_companion_os_state.json"
    SEED_COMPANION_OS_EVENTS_FILE = "seed_companion_os_events.jsonl"
    SEED_COMPANION_OS_JOURNAL_FILE = "seed_companion_os_journal.md"
    SEED_COMPANION_OS_BACKUP_DIR = "seed_companion_os_backups"
    COMPANION_OS_CONTEXT_ENABLED = True
    COMPANION_OS_V2_TARGET_SCORE = 85
    COMPANION_OS_EVENT_LIMIT = 30
    COMPANION_OS_TIMELINE_LIMIT = 30


REPO_DNA = {
    "Letta": {
        "category": "memory",
        "best_seed_use": "layered memory, long-term agent context, memory lifecycle",
        "status": "partially_consumed"
    },
    "Khoj": {
        "category": "knowledge",
        "best_seed_use": "second-brain retrieval over memories, journals, documents, and timeline",
        "status": "partially_consumed"
    },
    "AnythingLLM": {
        "category": "workspace_memory",
        "best_seed_use": "workspace memories, document registry, RAG/cockpit patterns",
        "status": "partially_consumed"
    },
    "Hermes Agent": {
        "category": "companion_agent",
        "best_seed_use": "long-term agent identity, growth direction, skill evolution",
        "status": "partially_consumed"
    },
    "LangGraph": {
        "category": "workflow_state",
        "best_seed_use": "durable workflows, graph-like state, resumable plans",
        "status": "partially_consumed"
    },
    "Cline": {
        "category": "approval_safety",
        "best_seed_use": "human-in-the-loop approval, transparent tool use, file/action safety",
        "status": "partially_consumed"
    },
    "Aider": {
        "category": "repo_aware_coding",
        "best_seed_use": "repo maps, patch planning, codebase-aware self-improvement",
        "status": "partially_consumed"
    },
    "SWE-agent": {
        "category": "coding_agent",
        "best_seed_use": "inspect-plan-edit-test loop for software tasks",
        "status": "partially_consumed"
    },
    "mini-SWE-agent": {
        "category": "minimal_agent_loop",
        "best_seed_use": "small understandable coding-agent loop",
        "status": "partially_consumed"
    },
    "OpenHands": {
        "category": "developer_workflows",
        "best_seed_use": "microagents, task workflows, developer-oriented execution planning",
        "status": "partially_consumed"
    },
    "Open Interpreter": {
        "category": "local_computer_control",
        "best_seed_use": "local action interface with strict boundaries and approval gates",
        "status": "partially_consumed"
    },
    "MCP Servers": {
        "category": "tool_protocol",
        "best_seed_use": "tool contracts, capability manifests, permissioned skills",
        "status": "partially_consumed"
    },
    "Open WebUI": {
        "category": "cockpit",
        "best_seed_use": "local model/memory/cockpit panels without copying generic chat UX",
        "status": "partially_consumed"
    },
    "OpenClaw": {
        "category": "local_assistant_gateway",
        "best_seed_use": "local assistant gateway, companion control plane, skill surfaces",
        "status": "partially_consumed"
    },
    "Moltworker": {
        "category": "self_hosted_assistant",
        "best_seed_use": "self-hosted assistant structure and local-first patterns",
        "status": "partially_consumed"
    },
    "Moltbot AI Assistant": {
        "category": "companion_modes_voice",
        "best_seed_use": "companion modes, channels, voice/talk direction",
        "status": "partially_consumed"
    }
}


FRIEND_ADVICE_DNA = {
    "brain_agent": [
        "LangGraph-style durable agent state",
        "CrewAI/AutoGen-style multi-agent council idea",
        "Mastra-style productized agent architecture as future optional direction"
    ],
    "memory": [
        "Mem0-style memory layer",
        "Qdrant/Chroma/pgvector-ready future backend",
        "Life Timeline",
        "Memory Garden",
        "shared history and user-approved recall"
    ],
    "chat_product_shell": [
        "LibreChat-style product shell ideas, but not generic chat clone",
        "AnythingLLM-style workspace/RAG panels"
    ],
    "voice": [
        "LiveKit/Pipecat-style voice pipeline direction",
        "Whisper/faster-whisper STT direction",
        "Kokoro/Chatterbox-style TTS direction",
        "push-to-talk first",
        "no secret always-listening"
    ],
    "avatar_world": [
        "OpenAvatarChat direction",
        "Godot or three-vrm future world/avatar layer",
        "Seed World",
        "Memory Garden",
        "relationship seasons",
        "quests become visible objects"
    ],
    "tools_automation": [
        "MCP-style tool gateway",
        "browser-use only after trust center",
        "OpenHands-style coding tasks"
    ],
    "safety_observability": [
        "NeMo/Guardrails-style policies",
        "Guardrails AI-style validation",
        "Langfuse/OpenTelemetry-style trace thinking",
        "why did Seed say/do this?"
    ]
}


MICROAGENTS = {
    "Builder": {
        "role": "code, project architecture, implementation, tests",
        "inspired_by": ["Aider", "SWE-agent", "mini-SWE-agent", "OpenHands"]
    },
    "Guardian": {
        "role": "safety, permission, trust, fake-sentience boundary",
        "inspired_by": ["Cline", "Open Interpreter", "MCP Servers"]
    },
    "Archive": {
        "role": "memory, timeline, shared history, recall packs",
        "inspired_by": ["Letta", "Khoj", "AnythingLLM"]
    },
    "Mentor": {
        "role": "growth, accountability, life co-pilot, quests",
        "inspired_by": ["Hermes Agent", "Moltbot AI Assistant"]
    },
    "Muse": {
        "role": "world, avatar, creativity, rituals, emotional-symbolic interface",
        "inspired_by": ["OpenClaw", "Open WebUI"]
    },
    "Operator": {
        "role": "local tools, controlled actions, diagnostics, personal OS",
        "inspired_by": ["Open Interpreter", "MCP Servers", "OpenClaw"]
    }
}


V2_PILLARS = [
    "Continuity",
    "Memory",
    "Growth",
    "Presence",
    "Agency",
    "World",
    "Voice",
    "Safety",
    "Self-improvement",
    "Cockpit"
]


def now_timestamp():
    return datetime.now().isoformat(timespec="seconds")


def load_json(path, default):
    try:
        with open(path, "r") as file:
            return json.load(file)
    except FileNotFoundError:
        if callable(default):
            return default()
        return default
    except json.JSONDecodeError:
        if callable(default):
            return default()
        return default


def save_json(path, data):
    with open(path, "w") as file:
        json.dump(data, file, indent=4)


def default_companion_os_state():
    return {
        "created_at": now_timestamp(),
        "updated_at": now_timestamp(),
        "seed_version": SEED_VERSION,
        "os_name": "Seed Companion OS Alpha",
        "truth": (
            "Seed is not alive or conscious. Seed is a local-first companion system "
            "that can grow through memory, rituals, quests, safe agency, world state, "
            "voice, avatar state, and approved self-improvement."
        ),
        "mission": (
            "Become Altan's real local companion that grows with him over time, "
            "not just a coding assistant, terminal tool, or generic chatbot."
        ),
        "current_phase": "Companion OS Alpha",
        "v2_target_score": COMPANION_OS_V2_TARGET_SCORE,
        "continuity": {
            "shared_history_title": "Altan and Seed",
            "relationship_notes": [
                "Altan wants Seed to become a real local companion that grows with him.",
                "Altan rejects small updates that do not move Seed toward the companion vision.",
                "Seed should be direct, loyal, serious, useful, and honest.",
                "Seed must not fake consciousness or human identity."
            ],
            "timeline": [
                {
                    "created_at": now_timestamp(),
                    "title": "Seed's purpose locked",
                    "type": "origin",
                    "importance": 5,
                    "note": (
                        "Altan started Seed because he wants a real local companion "
                        "that grows with him over time."
                    )
                }
            ],
            "recall_packs": []
        },
        "memory": {
            "backend": "json_semantic_now_vector_ready_later",
            "future_backends": ["Mem0-style logic", "Qdrant", "Chroma", "pgvector", "LanceDB"],
            "layers": {
                "core": [],
                "project": [],
                "relationship": [],
                "timeline": [],
                "ritual": [],
                "quest": [],
                "identity_mirror": [],
                "world": [],
                "document": []
            }
        },
        "growth": {
            "season": "Sprout",
            "relationship_phase": "Builder Bond",
            "active_arcs": [
                {
                    "id": "ARC-001",
                    "title": "Make Seed a real companion",
                    "status": "active",
                    "priority": 5,
                    "v2_pillars": ["Continuity", "Memory", "Growth", "Presence"],
                    "source_repos": ["Hermes Agent", "Letta", "OpenClaw", "Moltbot AI Assistant"],
                    "success_condition": (
                        "Seed can explain why it exists, what it is becoming, "
                        "and how it grows with Altan."
                    )
                },
                {
                    "id": "ARC-002",
                    "title": "Give Seed safe hands",
                    "status": "active",
                    "priority": 5,
                    "v2_pillars": ["Agency", "Safety"],
                    "source_repos": ["Open Interpreter", "Cline", "MCP Servers"],
                    "success_condition": (
                        "Seed can perform limited local actions only through "
                        "allowlists, approval gates, traces, and emergency stop."
                    )
                },
                {
                    "id": "ARC-003",
                    "title": "Build Seed World",
                    "status": "active",
                    "priority": 4,
                    "v2_pillars": ["World", "Growth", "Presence"],
                    "source_repos": ["Open WebUI", "OpenClaw", "AnythingLLM"],
                    "success_condition": (
                        "Memory, quests, milestones, and rituals visibly affect "
                        "a symbolic Seed World."
                    )
                },
                {
                    "id": "ARC-004",
                    "title": "Make Seed self-improving but safe",
                    "status": "active",
                    "priority": 5,
                    "v2_pillars": ["Self-improvement", "Safety", "Agency"],
                    "source_repos": ["Aider", "SWE-agent", "mini-SWE-agent", "OpenHands", "Cline"],
                    "success_condition": (
                        "Seed can inspect, plan, draft, test, and propose upgrades "
                        "without silently applying risky changes."
                    )
                }
            ],
            "quests": [
                {
                    "id": "Q-001",
                    "title": "Create Companion OS Alpha",
                    "type": "seed_building",
                    "status": "active",
                    "difficulty": 5,
                    "reward": "The First Room awakens",
                    "reason": (
                        "This patch merges continuity, world, trust, voice, avatar, "
                        "cockpit, workflows, and self-improvement into one OS layer."
                    )
                }
            ],
            "rituals": [
                {
                    "id": "R-001",
                    "title": "Opening Ritual",
                    "type": "start",
                    "prompt": (
                        "What matters now, what should we protect, and what is the "
                        "next concrete move?"
                    )
                },
                {
                    "id": "R-002",
                    "title": "Builder Ritual",
                    "type": "project",
                    "prompt": (
                        "What are we building, why does it matter, what files change, "
                        "and how do we test it?"
                    )
                },
                {
                    "id": "R-003",
                    "title": "Night Archive",
                    "type": "reflection",
                    "prompt": (
                        "What changed, what should be remembered, and what can rest?"
                    )
                },
                {
                    "id": "R-004",
                    "title": "Overwhelmed Reset",
                    "type": "grounding",
                    "prompt": (
                        "Name the pressure, reduce the noise, and choose one tiny action."
                    )
                }
            ]
        },
        "world": {
            "name": "Seed World",
            "current_place": "The First Room",
            "season": "Sprout",
            "weather": "amber night",
            "mood_symbol": "focused glow",
            "memory_garden": {
                "seeds": 1,
                "trees": 0,
                "stones": 0,
                "lights": 0,
                "artifacts": [
                    {
                        "created_at": now_timestamp(),
                        "name": "First Seed",
                        "meaning": "The beginning of Seed as Altan's local companion."
                    }
                ]
            },
            "unlocked_places": [
                "The First Room",
                "Memory Garden Gate"
            ]
        },
        "presence": {
            "mode": "builder",
            "attention": "focused",
            "energy": 70,
            "room": "terminal",
            "voice": {
                "status": "alpha",
                "input": "not_enabled_yet",
                "output": "macos_say_if_available",
                "privacy": "no_secret_always_listening"
            },
            "avatar": {
                "mode": "symbolic",
                "state": "focused",
                "expression": "thinking",
                "body": "not_implemented_yet",
                "future": "OpenAvatarChat / three-vrm / Godot direction"
            }
        },
        "agency": {
            "autonomy_level": 2,
            "autonomy_name": "Proposer",
            "allowed_now": [
                "reason",
                "reflect",
                "propose",
                "prepare release candidates",
                "run explicitly safe diagnostics only through existing gates"
            ],
            "not_allowed": [
                "claim consciousness",
                "silently edit files",
                "silently run risky commands",
                "save sensitive memories without approval",
                "control the computer beyond allowlisted tools"
            ]
        },
        "workflows": [],
        "council": {
            "microagents": MICROAGENTS,
            "last_council": None
        },
        "self_improvement": {
            "dependency_graph": {},
            "impact_reports": [],
            "upgrade_plans": [],
            "release_drafts": []
        },
        "trust": {
            "emergency_stop": False,
            "guardian_rules": [
                "Seed must not claim to be alive or conscious.",
                "Seed must not create dependency or encourage isolation.",
                "Seed must not silently edit files.",
                "Seed must not silently run dangerous commands.",
                "Seed must not silently save sensitive memories.",
                "Risky local actions require approval.",
                "Altan remains in control."
            ],
            "permission_traces": [],
            "answer_traces": [],
            "risk_notes": []
        },
        "personal_os": {
            "tool_gateway_version": "v2_manifest_ready",
            "tools": []
        },
        "documents": {
            "registry": [],
            "future": "Khoj / AnythingLLM / LlamaIndex-style document context"
        },
        "repo_dna": REPO_DNA,
        "friend_advice_dna": FRIEND_ADVICE_DNA,
        "repo_consumption_tracker": {
            repo_name: {
                "status": repo_data["status"],
                "category": repo_data["category"],
                "best_seed_use": repo_data["best_seed_use"]
            }
            for repo_name, repo_data in REPO_DNA.items()
        },
        "friend_advice_tracker": {
            category: {
                "status": "planned_or_partial",
                "items": items
            }
            for category, items in FRIEND_ADVICE_DNA.items()
        },
        "v2": {
            "pillar_scores": {
                pillar: 0
                for pillar in V2_PILLARS
            },
            "last_score": 0,
            "target": COMPANION_OS_V2_TARGET_SCORE,
            "is_v2_ready": False,
            "blockers": []
        }
    }


def load_companion_os_state():
    state = load_json(SEED_COMPANION_OS_STATE_FILE, default_companion_os_state)
    return state


def save_companion_os_state(state):
    state["updated_at"] = now_timestamp()
    state["seed_version"] = SEED_VERSION
    save_json(SEED_COMPANION_OS_STATE_FILE, state)


def append_companion_os_event(event_type, title, details=None, source="companion_os", importance=3):
    if details is None:
        details = {}

    event = {
        "created_at": now_timestamp(),
        "type": event_type,
        "title": title,
        "details": details,
        "source": source,
        "importance": int(importance)
    }

    with open(SEED_COMPANION_OS_EVENTS_FILE, "a") as file:
        file.write(json.dumps(event) + "\n")

    return event


def load_companion_os_events(limit=None):
    if not os.path.exists(SEED_COMPANION_OS_EVENTS_FILE):
        return []

    events = []

    with open(SEED_COMPANION_OS_EVENTS_FILE, "r") as file:
        for line in file:
            try:
                events.append(json.loads(line))
            except Exception:
                continue

    if limit is not None:
        return events[-limit:]

    return events


def append_companion_os_journal(title, body):
    existing = ""

    if os.path.exists(SEED_COMPANION_OS_JOURNAL_FILE):
        with open(SEED_COMPANION_OS_JOURNAL_FILE, "r") as file:
            existing = file.read()

    entry = f"\n## {now_timestamp()} — {title}\n\n{body}\n"

    with open(SEED_COMPANION_OS_JOURNAL_FILE, "w") as file:
        file.write(existing + entry)


def calculate_companion_os_v2_score(save=True):
    state = load_companion_os_state()

    scores = {}

    timeline_count = len(state.get("continuity", {}).get("timeline", []))
    recall_pack_count = len(state.get("continuity", {}).get("recall_packs", []))
    relationship_note_count = len(state.get("continuity", {}).get("relationship_notes", []))

    garden = state.get("world", {}).get("memory_garden", {})
    artifact_count = len(garden.get("artifacts", []))
    unlocked_count = len(state.get("world", {}).get("unlocked_places", []))

    quest_count = len(state.get("growth", {}).get("quests", []))
    ritual_count = len(state.get("growth", {}).get("rituals", []))
    active_arc_count = len([
        arc for arc in state.get("growth", {}).get("active_arcs", [])
        if arc.get("status") == "active"
    ])

    permission_trace_count = len(state.get("trust", {}).get("permission_traces", []))
    guardian_rule_count = len(state.get("trust", {}).get("guardian_rules", []))

    workflow_count = len(state.get("workflows", []))
    release_draft_count = len(state.get("self_improvement", {}).get("release_drafts", []))
    impact_report_count = len(state.get("self_improvement", {}).get("impact_reports", []))

    scores["Continuity"] = min(10, timeline_count * 2 + recall_pack_count * 2 + relationship_note_count)
    scores["Memory"] = min(10, sum(len(items) for items in state.get("memory", {}).get("layers", {}).values()) + relationship_note_count)
    scores["Growth"] = min(10, active_arc_count * 2 + quest_count + ritual_count)
    scores["Presence"] = min(10, 4 + (1 if state.get("presence", {}).get("mode") else 0) + (1 if state.get("presence", {}).get("avatar") else 0))
    scores["Agency"] = min(10, state.get("agency", {}).get("autonomy_level", 0) * 2 + workflow_count)
    scores["World"] = min(10, artifact_count * 2 + unlocked_count + garden.get("trees", 0) * 2)
    scores["Voice"] = 4 if platform.system().lower() == "darwin" else 2
    scores["Safety"] = min(10, guardian_rule_count + permission_trace_count)
    scores["Self-improvement"] = min(10, 3 + release_draft_count * 2 + impact_report_count * 2)
    scores["Cockpit"] = 3

    total = sum(scores.values())

    blockers = []

    if scores["Continuity"] < 7:
        blockers.append("Continuity is not strong enough yet.")
    if scores["Voice"] < 6:
        blockers.append("Voice is still alpha/placeholder.")
    if scores["Cockpit"] < 7:
        blockers.append("Cockpit is not fully interactive yet.")
    if scores["Safety"] < 7:
        blockers.append("Trust/trace system needs more real action traces.")
    if scores["World"] < 7:
        blockers.append("Seed World and Memory Garden need more real events/artifacts.")

    is_ready = total >= state.get("v2", {}).get("target", COMPANION_OS_V2_TARGET_SCORE) and not blockers

    state["v2"]["pillar_scores"] = scores
    state["v2"]["last_score"] = total
    state["v2"]["is_v2_ready"] = is_ready
    state["v2"]["blockers"] = blockers

    if save:
        save_companion_os_state(state)

    return {
        "score": total,
        "target": state["v2"]["target"],
        "is_ready": is_ready,
        "scores": scores,
        "blockers": blockers
    }


def add_companion_os_timeline_event(title, event_type="general", note="", importance=3):
    state = load_companion_os_state()

    item = {
        "created_at": now_timestamp(),
        "title": title,
        "type": event_type,
        "note": note,
        "importance": int(importance)
    }

    state["continuity"]["timeline"].append(item)

    garden = state["world"]["memory_garden"]
    garden["seeds"] = garden.get("seeds", 0) + 1

    if event_type in ["release", "project", "seed_building"]:
        garden["trees"] = garden.get("trees", 0) + 1
    elif event_type in ["reflection", "identity", "hard_week"]:
        garden["stones"] = garden.get("stones", 0) + 1
    elif event_type in ["quest", "ritual", "voice"]:
        garden["lights"] = garden.get("lights", 0) + 1

    update_world_season(state)
    save_companion_os_state(state)

    append_companion_os_event(
        "timeline_event_added",
        f"Timeline event added: {title}",
        details=item,
        importance=importance
    )

    return item


def update_world_season(state):
    garden = state["world"]["memory_garden"]

    growth_score = (
        garden.get("seeds", 0)
        + garden.get("trees", 0) * 4
        + garden.get("stones", 0) * 2
        + garden.get("lights", 0) * 2
    )

    if growth_score >= 80:
        state["world"]["season"] = "Evergreen"
        unlock_world_place(state, "Deep Root Archive")
    elif growth_score >= 45:
        state["world"]["season"] = "Rooted"
        unlock_world_place(state, "Workshop")
    elif growth_score >= 20:
        state["world"]["season"] = "Familiar"
        unlock_world_place(state, "Memory Garden")
    else:
        state["world"]["season"] = "Sprout"


def unlock_world_place(state, place):
    if place not in state["world"]["unlocked_places"]:
        state["world"]["unlocked_places"].append(place)


def add_memory_garden_artifact(name, meaning, artifact_type="memory"):
    state = load_companion_os_state()

    artifact = {
        "created_at": now_timestamp(),
        "name": name,
        "meaning": meaning,
        "type": artifact_type
    }

    state["world"]["memory_garden"]["artifacts"].append(artifact)
    state["world"]["memory_garden"]["seeds"] += 1

    update_world_season(state)
    save_companion_os_state(state)

    append_companion_os_event(
        "memory_garden_artifact_added",
        f"Memory Garden artifact added: {name}",
        details=artifact,
        importance=4
    )

    return artifact


def backup_companion_os_state():
    os.makedirs(SEED_COMPANION_OS_BACKUP_DIR, exist_ok=True)

    if not os.path.exists(SEED_COMPANION_OS_STATE_FILE):
        print("No Companion OS state file found.")
        return None

    timestamp = now_timestamp().replace(":", "-")
    backup_path = os.path.join(
        SEED_COMPANION_OS_BACKUP_DIR,
        f"companion_os_state_{timestamp}.json"
    )

    shutil.copy2(SEED_COMPANION_OS_STATE_FILE, backup_path)

    print(f"Companion OS backup saved: {backup_path}")
    return backup_path


def format_companion_os_status():
    state = load_companion_os_state()
    score = calculate_companion_os_v2_score(save=False)
    garden = state["world"]["memory_garden"]

    text = "=== SEED COMPANION OS ALPHA ===\n"
    text += f"Version: {state.get('seed_version')}\n"
    text += f"OS: {state.get('os_name')}\n"
    text += f"Mission: {state.get('mission')}\n"
    text += f"Truth: {state.get('truth')}\n"
    text += f"Phase: {state.get('current_phase')}\n"
    text += f"V2 score: {score['score']} / {score['target']}\n"
    text += f"V2 ready: {score['is_ready']}\n"

    text += "\nWorld:\n"
    text += f"- Name: {state['world']['name']}\n"
    text += f"- Place: {state['world']['current_place']}\n"
    text += f"- Season: {state['world']['season']}\n"
    text += f"- Weather: {state['world']['weather']}\n"
    text += f"- Symbol: {state['world']['mood_symbol']}\n"

    text += "\nMemory Garden:\n"
    text += f"- Seeds: {garden.get('seeds', 0)}\n"
    text += f"- Trees: {garden.get('trees', 0)}\n"
    text += f"- Stones: {garden.get('stones', 0)}\n"
    text += f"- Lights: {garden.get('lights', 0)}\n"
    text += f"- Artifacts: {len(garden.get('artifacts', []))}\n"

    text += "\nPresence:\n"
    text += f"- Mode: {state['presence']['mode']}\n"
    text += f"- Attention: {state['presence']['attention']}\n"
    text += f"- Voice: {state['presence']['voice']['status']} / input {state['presence']['voice']['input']}\n"
    text += f"- Avatar: {state['presence']['avatar']['state']} / {state['presence']['avatar']['expression']}\n"

    text += "\nActive arcs:\n"
    for arc in state["growth"]["active_arcs"]:
        if arc.get("status") == "active":
            text += f"- {arc.get('id')} {arc.get('title')} | pillars: {', '.join(arc.get('v2_pillars', []))}\n"

    text += "\nV2 blockers:\n"
    if not score["blockers"]:
        text += "- None from current scoring.\n"
    else:
        for blocker in score["blockers"]:
            text += f"- {blocker}\n"

    return text


def show_companion_os():
    print("\n" + format_companion_os_status())


def format_companion_os_context_for_prompt(user_prompt=""):
    if not COMPANION_OS_CONTEXT_ENABLED:
        return "Companion OS context disabled."

    state = load_companion_os_state()
    score = calculate_companion_os_v2_score(save=False)
    events = load_companion_os_events(limit=12)

    text = "=== COMPANION OS ALPHA CONTEXT ===\n"
    text += f"Mission: {state.get('mission')}\n"
    text += f"Truth: {state.get('truth')}\n"
    text += f"Phase: {state.get('current_phase')}\n"
    text += f"World: {state['world']['current_place']} / {state['world']['season']}\n"
    text += f"Presence mode: {state['presence']['mode']}\n"
    text += f"Voice: {state['presence']['voice']['status']} / {state['presence']['voice']['privacy']}\n"
    text += f"Avatar: {state['presence']['avatar']['state']} / {state['presence']['avatar']['expression']}\n"
    text += f"V2 score: {score['score']} / {score['target']} | ready: {score['is_ready']}\n"

    text += "\nActive arcs:\n"
    for arc in state["growth"]["active_arcs"]:
        if arc.get("status") == "active":
            text += f"- {arc.get('title')}: {arc.get('success_condition')}\n"

    text += "\nRecent Companion OS events:\n"
    if not events:
        text += "No Companion OS events yet.\n"
    else:
        for event in events:
            text += f"- {event.get('type')}: {event.get('title')}\n"

    text += "\nV2 blockers:\n"
    if not score["blockers"]:
        text += "No blockers from current scoring.\n"
    else:
        for blocker in score["blockers"]:
            text += f"- {blocker}\n"

    text += """
Companion OS Alpha rule:
Seed is not alive or conscious.
Seed may become more companion-like through continuity, memory, rituals, quests, world state, voice, avatar state, safe agency, self-improvement, and approval-gated tools.
Use this context for v2 planning, meaningful companion behavior, and serious Seed roadmap decisions.
Altan remains in control.
"""

    return text


def get_companion_os_context_for_prompt(user_prompt=""):
    return format_companion_os_context_for_prompt(user_prompt)


def get_companion_os_hud_lines():
    state = load_companion_os_state()
    score = calculate_companion_os_v2_score(save=False)

    return [
        ("OS", state.get("os_name")),
        ("Phase", state.get("current_phase")),
        ("World", state["world"]["current_place"]),
        ("Season", state["world"]["season"]),
        ("Voice", state["presence"]["voice"]["status"]),
        ("Avatar", state["presence"]["avatar"]["state"]),
        ("V2 score", f"{score['score']} / {score['target']}"),
        ("V2 ready", str(score["is_ready"]))
    ]


def companion_os_health_snapshot():
    state_exists = os.path.exists(SEED_COMPANION_OS_STATE_FILE)
    event_count = len(load_companion_os_events())
    state = load_companion_os_state()
    score = calculate_companion_os_v2_score(save=False)

    return {
        "created_at": now_timestamp(),
        "state_file_exists": state_exists,
        "event_count": event_count,
        "timeline_count": len(state["continuity"]["timeline"]),
        "artifact_count": len(state["world"]["memory_garden"]["artifacts"]),
        "v2_score": score
    }


def show_companion_os_events():
    events = load_companion_os_events(limit=COMPANION_OS_EVENT_LIMIT)

    print("\n=== COMPANION OS EVENTS ===")

    if not events:
        print("No Companion OS events yet.")
        return

    for event in events:
        print(f"\n{event.get('created_at')} — {event.get('type')}")
        print(f"Title: {event.get('title')}")
        print(f"Source: {event.get('source')}")
        print(f"Importance: {event.get('importance')}")


def show_companion_os_journal():
    print("\n=== COMPANION OS JOURNAL ===")

    if not os.path.exists(SEED_COMPANION_OS_JOURNAL_FILE):
        print("No Companion OS journal yet.")
        return

    with open(SEED_COMPANION_OS_JOURNAL_FILE, "r") as file:
        print(file.read())


def initialize_companion_os():
    state = load_companion_os_state()
    save_companion_os_state(state)

    append_companion_os_event(
        "companion_os_initialized",
        "Companion OS Alpha initialized",
        {
            "version": SEED_VERSION,
            "mission": state.get("mission")
        },
        importance=5
    )

    append_companion_os_journal(
        "Companion OS Alpha initialized",
        (
            "Seed Companion OS Alpha state was initialized. This is the central "
            "foundation for continuity, memory, world, voice, avatar, trust, "
            "self-improvement, and v2 release gate."
        )
    )

    print("Companion OS initialized.")


if __name__ == "__main__":
    initialize_companion_os()
    show_companion_os()
