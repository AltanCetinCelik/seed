SEED_VERSION = "v2.3.0"

SEED_V2_HARDENING_STATE_FILE = "seed_v2_hardening_state.json"
SEED_AGENCY_HARDENING_STATE_FILE = "seed_agency_hardening_state.json"
SEED_SELF_IMPROVEMENT_HARDENING_FILE = "seed_self_improvement_hardening.json"
SEED_VOICE_HARDENING_STATE_FILE = "seed_voice_hardening_state.json"
SEED_COCKPIT_HARDENING_STATE_FILE = "seed_cockpit_hardening_state.json"

V118_TARGET_SCORE = 85

V118_REQUIRED_MODULES = [
    "seed_v2_hardening_metrics.py",
    "seed_agency_hardening.py",
    "seed_self_improvement_hardening.py",
    "seed_voice_hardening.py",
    "seed_cockpit_actions.py"
]
SEED_MEMORY_BACKEND_STATE_FILE = "seed_memory_backend_state.json"

MEMORY_BACKEND_ACTIVE = "json_semantic"
MEMORY_BACKEND_VECTOR_READY = True
MEMORY_BACKEND_DOCUMENT_READY = True

V2_REQUIRED_MODULES = [
    "seed_companion_os.py",
    "seed_os_migrations.py",
    "seed_os_registry.py",
    "seed_os_bridge.py",
    "seed_trace_engine.py",
    "seed_tool_manifest_v2.py",
    "seed_trust_center.py",
    "seed_memory_backend.py",
    "seed_document_registry.py",
    "seed_continuity_engine.py",
    "seed_workflow_engine.py",
    "seed_microagent_council.py",
    "seed_self_improvement_engine.py",
    "seed_release_manager.py",
    "seed_world_engine.py",
    "seed_avatar_state.py",
    "seed_voice_session.py",
    "seed_companion_cockpit.py",
    "seed_companion_os_context.py",
    "seed_companion_os_commands.py",
    "seed_v2_release_gate.py"
    
]

SELF_IMPROVEMENT_TEST_COMMANDS = [
    "python -m py_compile seed_companion_os.py",
    "python -m py_compile seed_os_migrations.py",
    "python -m py_compile seed_os_registry.py",
    "python -m py_compile seed_os_bridge.py",
    "python -m py_compile seed_trace_engine.py",
    "python -m py_compile seed_tool_manifest_v2.py",
    "python -m py_compile seed_trust_center.py",
    "python -m py_compile seed_memory_backend.py",
    "python -m py_compile seed_document_registry.py",
    "python -m py_compile seed_continuity_engine.py",
    "python -m py_compile seed_workflow_engine.py",
    "python -m py_compile seed_microagent_council.py",
    "python -m py_compile seed_self_improvement_engine.py",
    "python -m py_compile seed_release_manager.py",
    "python -m py_compile seed_world_engine.py",
    "python -m py_compile seed_avatar_state.py",
    "python -m py_compile seed_voice_session.py",
    "python -m py_compile seed_companion_cockpit.py",
    "python -m py_compile seed_companion_os_context.py",
    "python -m py_compile seed_companion_os_commands.py",
    "python -m py_compile seed_v2_release_gate.py",
    "python -m py_compile seed_brain.py",
    "python -m py_compile seed_commands.py",
    "python -m py_compile seed_visuals.py",
    "python -m py_compile seed_config.py"
    "python -m py_compile seed_voice_hardening.py",
    "python -m py_compile seed_cockpit_actions.py",
]


DOCUMENT_REGISTRY_SUMMARY_CHAR_LIMIT = 12000
DOCUMENT_REGISTRY_SEARCH_LIMIT = 12
CONTINUITY_RECALL_LIMIT = 12
CONTINUITY_PACK_TIMELINE_LIMIT = 20

WORKFLOW_RECENT_LIMIT = 12
WORKFLOW_MAX_STEPS = 20

WORLD_EVENT_LIMIT = 30
AVATAR_ALLOWED_STATES = [
    "focused",
    "thinking",
    "guarding",
    "celebrating",
    "quiet",
    "listening",
    "building",
    "reflecting",
    "archiving"
]

VOICE_TTS_BACKEND = "macos_say"
VOICE_STT_BACKEND = "not_enabled"
VOICE_ALLOW_SPEAKING = True
VOICE_NO_ALWAYS_LISTENING = True

COCKPIT_REFRESH_SECONDS = 5

COUNCIL_AGENT_NAMES = [
    "Builder",
    "Guardian",
    "Archive",
    "Mentor",
    "Muse",
    "Operator"
]

SELF_IMPROVEMENT_TEST_COMMANDS = [
    "python -m py_compile seed_companion_os.py",
    "python -m py_compile seed_os_registry.py",
    "python -m py_compile seed_os_migrations.py",
    "python -m py_compile seed_os_bridge.py",
    "python -m py_compile seed_trace_engine.py",
    "python -m py_compile seed_tool_manifest_v2.py",
    "python -m py_compile seed_trust_center.py",
    "python -m py_compile seed_memory_backend.py",
    "python -m py_compile seed_document_registry.py",
    "python -m py_compile seed_continuity_engine.py"
]

RELEASE_MANAGER_RECENT_LIMIT = 8

SEED_COMPANION_OS_STATE_FILE = "seed_companion_os_state.json"
SEED_COMPANION_OS_EVENTS_FILE = "seed_companion_os_events.jsonl"
SEED_COMPANION_OS_JOURNAL_FILE = "seed_companion_os_journal.md"
SEED_COMPANION_OS_BACKUP_DIR = "seed_companion_os_backups"

SEED_OS_MIGRATION_REPORT_FILE = "seed_os_migration_report.json"
SEED_OS_REGISTRY_CACHE_FILE = "seed_os_registry_cache.json"
SEED_TRACE_LOG_FILE = "seed_trace_log.jsonl"
SEED_DOCUMENT_REGISTRY_FILE = "seed_document_registry.json"
SEED_VOICE_SESSION_FILE = "seed_voice_session.json"
SEED_RELEASE_MANAGER_FILE = "seed_release_manager.json"

COMPANION_OS_ENABLED = True
COMPANION_OS_CONTEXT_ENABLED = True

COMPANION_OS_COCKPIT_HOST = "127.0.0.1"
COMPANION_OS_COCKPIT_PORT = 8770

COMPANION_OS_V2_TARGET_SCORE = 85
COMPANION_OS_EVENT_LIMIT = 30
COMPANION_OS_TIMELINE_LIMIT = 30
COMPANION_OS_TRACE_LIMIT = 30
SEED_EVENTS_FILE = "seed_events.jsonl"
SEED_CODE_MAP_FILE = "seed_code_map.json"

CODE_MAP_IGNORE_DIRS = [
    ".git",
    "__pycache__",
    "seed_logs",
    "seed_edit_backups",
    "third_party_repos",
    ".venv",
    "venv",
    "node_modules"
]

RUNTIME_RECENT_EVENTS_LIMIT = 12
SEED_EVOLUTION_FOUNDRY_FILE = "seed_evolution_foundry.json"
SEED_RELEASE_CANDIDATES_FILE = "seed_release_candidates.json"
SEED_AUTONOMY_STATE_FILE = "seed_autonomy_state.json"
SEED_FOUNDRY_JOURNAL_FILE = "seed_foundry_journal.md"
SEED_FOUNDRY_SELF_EDIT_PROMPT_FILE = "seed_foundry_self_edit_prompt.md"

EVOLUTION_FOUNDRY_ENABLED = True
EVOLUTION_FOUNDRY_CONTEXT_ENABLED = True

FOUNDRY_PROPOSAL_COUNT = 5
FOUNDRY_RECENT_LIMIT = 8
FOUNDRY_DEFAULT_AUTONOMY_LEVEL = 2

FOUNDRY_SAFE_DIAGNOSTIC_COMMANDS = [
    "git status",
    "python --version",
    "ollama list"
]

SEED_PRESENCE_STATE_FILE = "seed_presence_state.json"
SEED_LOCAL_ACTIONS_FILE = "seed_local_actions.jsonl"
SEED_PENDING_ACTION_FILE = "seed_pending_action.json"
SEED_COMPUTER_SNAPSHOT_FILE = "seed_computer_snapshot.json"

PRESENCE_OS_ENABLED = True
LOCAL_CONTROL_ENABLED = True
LOCAL_CONTROL_CONTEXT_ENABLED = True

LOCAL_CONTROL_EMERGENCY_LOCK_DEFAULT = False

LOCAL_ALLOWED_APPS = [
    "Safari",
    "Terminal",
    "Visual Studio Code",
    "TextEdit",
    "Finder"
]

LOCAL_ALLOWED_FOLDERS = [
    "~/Desktop/seed_private",
    "~/Desktop",
    "~/Downloads"
]

LOCAL_SAFE_COMMANDS = [
    "pwd",
    "ls",
    "git status",
    "python --version",
    "which python",
    "ollama list",
    "df -h",
    "uptime"
]

LOCAL_DIAGNOSTIC_COMMANDS = [
    "git status",
    "python -m py_compile seed_cli.py",
    "ollama list"
]

LOCAL_FORBIDDEN_COMMAND_SUBSTRINGS = [
    "rm ",
    "rm-",
    "rm/",
    "sudo",
    "chmod",
    "chown",
    "mkfs",
    "diskutil erase",
    "dd ",
    "curl ",
    "wget ",
    "ssh ",
    "scp ",
    "rsync ",
    "killall",
    "pkill",
    "launchctl",
    "security ",
    "defaults write",
    "open /System",
    "open /Library",
    "osascript"
]
SEED_COMPANION_GROWTH_FILE = "seed_companion_growth.json"

COMPANION_GROWTH_ENABLED = True
COMPANION_GROWTH_CONTEXT_ENABLED = True

COMPANION_ARC_LIMIT = 8
COMPANION_QUEST_LIMIT = 8
COMPANION_MILESTONE_LIMIT = 12
COMPANION_MIRROR_LIMIT = 8

SEED_WORLD_FILE = "seed_world.json"
SEED_TIMELINE_FILE = "seed_life_timeline.json"
SEED_QUESTS_FILE = "seed_quests.json"
SEED_RITUALS_FILE = "seed_rituals.json"

COCKPIT_HOST = "127.0.0.1"
COCKPIT_PORT = 8765
COCKPIT_TITLE = "SEED Companion Cockpit"

SEED_WORLD_ENABLED = True
SEED_COCKPIT_ENABLED = True
SEED_SKILLS_DIR = "seed_skills"
SEED_SKILL_STATE_FILE = "seed_skill_state.json"

SKILL_OS_ENABLED = True
SKILL_CONTEXT_ENABLED = True
SKILL_PLAN_MAX_STEPS = 10

SKILL_AUTO_RUN_RISKS = [
    "read_only",
    "diagnostic"
]

SKILL_APPROVAL_RISKS = [
    "write",
    "dangerous",
    "external"
]
OPEN_SOURCE_DNA_ENABLED = True
DNA_CONTEXT_ENABLED = True

THIRD_PARTY_REPOS_DIR = "third_party_repos"
SEED_RESEARCH_DIR = "seed_research"

OPEN_SOURCE_DNA_FILE = "seed_research/open_source_dna.json"
OPEN_SOURCE_DNA_REPORT_FILE = "seed_research/OPEN_SOURCE_DNA_REPORT.md"
BORROW_CANDIDATES_FILE = "seed_research/borrow_candidates.json"

DNA_README_CHAR_LIMIT = 8000
DNA_KEY_FILE_LIMIT = 120
DNA_CANDIDATE_LIMIT = 500
DNA_CANDIDATE_MAX_FILE_BYTES = 300000
AGENT_KERNEL_ENABLED = True
AGENT_MAX_PLAN_STEPS = 8
AGENT_READONLY_AUTO_RUN = True

AGENT_ALLOWED_AUTO_TOOLS = [
    "system_snapshot",
    "project_report",
    "project_files",
    "project_modules",
    "memory_stats",
    "semantic_memory_status",
    "llm_status",
    "self_edit_status",
    "log_status"
]
MEMORY_CAPTURE_LLM_ENABLED = True
SMART_MEMORY_AUTO_REINDEX = True
SMART_MEMORY_DEFAULT_IMPORTANCE = 4

EMBEDDING_MODEL = "all-minilm"
MEMORY_EMBEDDINGS_FILE = "seed_memory_embeddings.json"

SEMANTIC_MEMORY_TOP_K = 8
SEMANTIC_MEMORY_MIN_SIMILARITY = 0.20
SEMANTIC_CONTEXT_ENABLED = True

OLLAMA_BASE_URL = "http://localhost:11434"
OLLAMA_GENERATE_URL = f"{OLLAMA_BASE_URL}/api/generate"
OLLAMA_TAGS_URL = f"{OLLAMA_BASE_URL}/api/tags"
OLLAMA_EMBED_URL = f"{OLLAMA_BASE_URL}/api/embed"

# Backward compatibility for older modules
OLLAMA_URL = OLLAMA_GENERATE_URL

DEFAULT_CHAT_MODEL = "llama3.1:8b"
DEFAULT_SUMMARY_MODEL = "llama3.1:8b"
DEFAULT_MEMORY_MODEL = "llama3.1:8b"
DEFAULT_DEBUG_MODEL = "llama3.1:8b"
DEFAULT_CODE_MODEL = "llama3.1:8b"

# Backward compatibility for older modules
MODEL_NAME = DEFAULT_CHAT_MODEL

LLM_TIMEOUT_SECONDS = 120
LLM_HEALTH_TIMEOUT_SECONDS = 3
LLM_NUM_CTX = 8192

LLM_TASK_CONFIG = {
    "chat": {
        "model": DEFAULT_CHAT_MODEL,
        "temperature": 0.45,
        "description": "Normal Seed conversation."
    },
    "summary": {
        "model": DEFAULT_SUMMARY_MODEL,
        "temperature": 0.25,
        "description": "Stable session/log summaries."
    },
    "memory": {
        "model": DEFAULT_MEMORY_MODEL,
        "temperature": 0.15,
        "description": "Strict memory extraction and memory review."
    },
    "debug": {
        "model": DEFAULT_DEBUG_MODEL,
        "temperature": 0.20,
        "description": "Careful bug diagnosis."
    },
    "code": {
        "model": DEFAULT_CODE_MODEL,
        "temperature": 0.25,
        "description": "Code generation and code review."
    }
}

MEMORY_SEARCH_LIMIT = 8
IMPORTANT_MEMORY_LIMIT = 5
RECENT_MEMORY_LIMIT = 5

RECENT_JOURNAL_LIMIT = 5
SESSION_HISTORY_LIMIT = 8

AUTOSUGGEST_DEFAULT = True

SEED_MODE = "local terminal"
LLM_STATUS = "connected through local Ollama when Ollama is running"

CHAT_LOG_DIR = "seed_logs"
CHAT_LOG_TAIL_LINES = 40
LOG_COMMAND_EVENTS = True

SUMMARY_MAX_LOG_LINES = 120
SUMMARY_MEMORY_TYPE = "technical_progress"
SUMMARY_IMPORTANCE = 5

PROJECT_ROOT = "."
PROJECT_REPORT_MEMORY_TYPE = "technical_progress"
PROJECT_REPORT_IMPORTANCE = 5

PROJECT_IGNORED_FOLDERS = [
    "__pycache__",
    ".git",
    "seed_logs"
]

PROJECT_IGNORED_FILES = [
    ".DS_Store"
]

PROJECT_CONTEXT_ENABLED = True
PROJECT_CONTEXT_FILE_LIMIT = 40

MEMORY_DEBUG_LIMIT = 12
MEMORY_DIRECT_MATCH_THRESHOLD = 1

VISUAL_THEME_NAME = "Seed Dark Amber"
VISUAL_ACCENT = "orange1"
VISUAL_PANEL_STYLE = "grey23"
VISUAL_SUCCESS_STYLE = "green"
VISUAL_WARNING_STYLE = "yellow"
VISUAL_ERROR_STYLE = "red"

PERSONALITY_CONTEXT_ENABLED = True
PERSONALITY_PROFILE_NAME = "Seed Companion Core"

SEED_PRIMARY_LANGUAGE_BEHAVIOR = "match_user"
SEED_PERSONALITY_MODE = "direct_local_companion"

PROJECT_IGNORED_FILES = [
    ".DS_Store",
    "ollama_test.py",
    "seed_brain_test.py",
    "seed_cli_backup_v01.py"
]

SELF_EDIT_BACKUP_DIR = "seed_edit_backups"
SELF_EDIT_PENDING_FILE = "seed_pending_edit.json"

SELF_EDIT_ALLOWED_EXTENSIONS = [
    ".py",
    ".md"
]

SELF_EDIT_PROTECTED_FILES = [
    "seed_memory.json",
    "seed_journal.txt",
    "seed_pending_edit.json"
]

SELF_EDIT_PROTECTED_FOLDERS = [
    ".git",
    "__pycache__",
    "seed_logs",
    "seed_edit_backups"
]


# v1.18.0 hardening modules must be part of the v2 release gate.
V118_REQUIRED_MODULES = [
    "seed_v2_hardening_metrics.py",
    "seed_agency_hardening.py",
    "seed_self_improvement_hardening.py",
    "seed_voice_hardening.py",
    "seed_cockpit_actions.py"
]

try:
    V2_REQUIRED_MODULES = list(dict.fromkeys(V2_REQUIRED_MODULES + V118_REQUIRED_MODULES))
except NameError:
    V2_REQUIRED_MODULES = list(V118_REQUIRED_MODULES)

# Keep release/safe tests aligned with the actual v2 module gate.
try:
    SELF_IMPROVEMENT_TEST_COMMANDS = list(dict.fromkeys(
        SELF_IMPROVEMENT_TEST_COMMANDS
        + [f"python -m py_compile {module}" for module in V2_REQUIRED_MODULES]
    ))
except NameError:
    SELF_IMPROVEMENT_TEST_COMMANDS = [
        f"python -m py_compile {module}" for module in V2_REQUIRED_MODULES
    ]




# Seed v1.19.0 Arsenal Integration Gate
SEED_REPO_ARSENAL_STATE_FILE = "seed_repo_arsenal_state.json"
SEED_FRIEND_ADVICE_REGISTRY_FILE = "seed_friend_advice_registry.json"
SEED_TOOL_ROUTER_TRACE_FILE = "seed_tool_router_trace.jsonl"
SEED_INTEGRATION_GATE_REPORT_FILE = "seed_integration_gate_report.json"

V119_REQUIRED_MODULES = [
    "seed_friend_advice_registry.py",
    "seed_repo_arsenal.py",
    "seed_tool_router.py",
    "seed_capability_planner.py",
    "seed_integration_gate.py",
    "seed_arsenal_commands.py"
]

try:
    V2_REQUIRED_MODULES = list(dict.fromkeys(V2_REQUIRED_MODULES + V119_REQUIRED_MODULES))
except NameError:
    V2_REQUIRED_MODULES = list(V119_REQUIRED_MODULES)

try:
    SELF_IMPROVEMENT_TEST_COMMANDS = list(dict.fromkeys(
        SELF_IMPROVEMENT_TEST_COMMANDS
        + [f"python -m py_compile {module}" for module in V119_REQUIRED_MODULES]
    ))
except NameError:
    SELF_IMPROVEMENT_TEST_COMMANDS = [
        f"python -m py_compile {module}" for module in V119_REQUIRED_MODULES
    ]




# Seed v2.0.0 Stable Companion OS + Voice Command Bridge
SEED_VOICE_COMMAND_STATE_FILE = "seed_voice_command_state.json"
SEED_VOICE_COMMAND_INPUT_AUDIO_FILE = "seed_voice_command_input.wav"
SEED_VOICE_COMMAND_TRANSCRIPT_FILE = "seed_voice_command_transcript.txt"
SEED_V2_STABLE_RELEASE_FILE = "seed_v2_stable_release.json"

VOICE_COMMAND_MODE = "push_to_talk"
VOICE_COMMAND_STT_BACKEND = "optional_faster_whisper"
VOICE_COMMAND_TYPED_FALLBACK = True
VOICE_COMMAND_NO_ALWAYS_LISTENING = True
VOICE_COMMAND_DEFAULT_RECORD_SECONDS = 6

V200_REQUIRED_MODULES = [
    "seed_voice_command_bridge.py",
    "seed_desktop_launcher.py",
    "seed_v2_stable_release.py"
]

try:
    V2_REQUIRED_MODULES = list(dict.fromkeys(V2_REQUIRED_MODULES + V200_REQUIRED_MODULES))
except NameError:
    V2_REQUIRED_MODULES = list(V200_REQUIRED_MODULES)

try:
    SELF_IMPROVEMENT_TEST_COMMANDS = list(dict.fromkeys(
        SELF_IMPROVEMENT_TEST_COMMANDS
        + [f"python -m py_compile {module}" for module in V200_REQUIRED_MODULES]
    ))
except NameError:
    SELF_IMPROVEMENT_TEST_COMMANDS = [
        f"python -m py_compile {module}" for module in V200_REQUIRED_MODULES
    ]




# Seed v2.1.0 Active Voice + Agent Arsenal Activation
SEED_ACTIVE_VOICE_STATE_FILE = "seed_active_voice_state.json"
SEED_ACTIVE_VOICE_INPUT_FILE = "seed_active_voice_input.wav"
SEED_ACTIVE_VOICE_COMMAND_FILE = "seed_active_voice_command.wav"
SEED_AGENT_TOOL_PROFILES_FILE = "seed_agent_tool_profiles.json"
SEED_AGENT_RUNS_DIR = "seed_agent_runs"
SEED_AGENT_ORCHESTRATOR_TRACE_FILE = "seed_agent_orchestrator_trace.jsonl"
SEED_V21_GATE_REPORT_FILE = "seed_v21_gate_report.json"

ACTIVE_VOICE_WAKE_WORDS = ["seed", "hey seed", "yo seed"]
ACTIVE_VOICE_LISTEN_SECONDS = 8
ACTIVE_VOICE_COMMAND_SECONDS = 8
ACTIVE_VOICE_NO_SECRET_ALWAYS_LISTENING = True
ACTIVE_VOICE_REQUIRE_EXPLICIT_LAUNCH = True

V21_REQUIRED_MODULES = [
    "seed_active_voice_daemon.py",
    "seed_agent_tool_profiles.py",
    "seed_agent_executor.py",
    "seed_agent_orchestrator.py",
    "seed_v21_capability_gate.py"
]

try:
    V2_REQUIRED_MODULES = list(dict.fromkeys(V2_REQUIRED_MODULES + V21_REQUIRED_MODULES))
except NameError:
    V2_REQUIRED_MODULES = list(V21_REQUIRED_MODULES)

try:
    SELF_IMPROVEMENT_TEST_COMMANDS = list(dict.fromkeys(
        SELF_IMPROVEMENT_TEST_COMMANDS
        + [f"python -m py_compile {module}" for module in V21_REQUIRED_MODULES]
    ))
except NameError:
    SELF_IMPROVEMENT_TEST_COMMANDS = [
        f"python -m py_compile {module}" for module in V21_REQUIRED_MODULES
    ]




# Seed v2.1.1 Voice Speed Hotfix
SEED_FAST_VOICE_CONTEXT_ENABLED = True
SEED_VOICE_FAST_MODE = True
SEED_VOICE_WHISPER_MODEL = "small"
SEED_VOICE_TRANSCRIBE_BEAM_SIZE = 5
SEED_VOICE_SKIP_HEAVY_CONTEXT_IN_VOICE = True

V211_REQUIRED_MODULES = [
    "seed_fast_voice_context.py"
]

try:
    V2_REQUIRED_MODULES = list(dict.fromkeys(V2_REQUIRED_MODULES + V211_REQUIRED_MODULES))
except NameError:
    V2_REQUIRED_MODULES = list(V211_REQUIRED_MODULES)

try:
    SELF_IMPROVEMENT_TEST_COMMANDS = list(dict.fromkeys(
        SELF_IMPROVEMENT_TEST_COMMANDS
        + [f"python -m py_compile {module}" for module in V211_REQUIRED_MODULES]
    ))
except NameError:
    SELF_IMPROVEMENT_TEST_COMMANDS = [
        f"python -m py_compile {module}" for module in V211_REQUIRED_MODULES
    ]




# Seed v2.1.2 Direct Active Voice Hotfix
ACTIVE_VOICE_DIRECT_COMMAND_MODE = True
ACTIVE_VOICE_WAKE_WORD_OPTIONAL = True
ACTIVE_VOICE_MIN_TRANSCRIPT_WORDS = 2
ACTIVE_VOICE_FUZZY_WAKE_WORDS = [
    "seed", "sead", "seat", "sit", "sid", "said", "see", "cede", "ceed",
    "hey seed", "yo seed"
]




# Seed v2.1.3 Voice Reliability Hotfix
SEED_ACTIVE_VOICE_TMP_DIR = "/tmp/seed_active_voice"
SEED_VOICE_VAD_FILTER = True
SEED_VOICE_CONDITION_ON_PREVIOUS_TEXT = False
ACTIVE_VOICE_CLARIFY_INCOMPLETE_TRANSCRIPTS = True
ACTIVE_VOICE_NO_FACT_INVENTION = True
ACTIVE_VOICE_INCOMPLETE_PHRASES = [
    "all right so tell me",
    "all right tell me",
    "so tell me",
    "tell me",
    "okay tell me",
    "alright tell me",
    "what about",
    "can you",
    "could you",
    "so",
    "and",
    "but"
]




# Seed v2.1.4 Voice Accuracy + Voice Brain Quality Hotfix
SEED_VOICE_AUDIO_CLEANUP_ENABLED = True
SEED_VOICE_LANGUAGE_HINT = None
SEED_VOICE_INITIAL_PROMPT = "Altan is talking to Seed, a local AI companion. Common words: Seed, Altan, Ollama, repo, GitHub, agent, browser, memory, voice, MacBook, Raspberry Pi, Turkish, English."
SEED_VOICE_LOW_CONFIDENCE_RERUN = True
SEED_VOICE_LOW_CONFIDENCE_MODEL = "small"
SEED_VOICE_MAX_SPOKEN_ANSWER_SENTENCES = 4
SEED_VOICE_QUALITY_MODE = True




# Seed v2.1.5 Cockpit Browser Action Hotfix
SEED_COCKPIT_URL = "http://127.0.0.1:8770"
SEED_COCKPIT_HOST = "127.0.0.1"
SEED_COCKPIT_PORT = 8770
SEED_COCKPIT_OPEN_BROWSER_TIMEOUT = 8

V215_REQUIRED_MODULES = [
    "seed_cockpit_server_runner.py",
    "seed_cockpit_browser_action.py"
]

try:
    V2_REQUIRED_MODULES = list(dict.fromkeys(V2_REQUIRED_MODULES + V215_REQUIRED_MODULES))
except NameError:
    V2_REQUIRED_MODULES = list(V215_REQUIRED_MODULES)

try:
    SELF_IMPROVEMENT_TEST_COMMANDS = list(dict.fromkeys(
        SELF_IMPROVEMENT_TEST_COMMANDS
        + [f"python -m py_compile {module}" for module in V215_REQUIRED_MODULES]
    ))
except NameError:
    SELF_IMPROVEMENT_TEST_COMMANDS = [
        f"python -m py_compile {module}" for module in V215_REQUIRED_MODULES
    ]




# Seed v2.2.0 Action Kernel + Memory Index + Tool Gateway Mega Update
SEED_ACTION_KERNEL_HISTORY_FILE = "seed_action_kernel_history.jsonl"
SEED_ACTION_KERNEL_STATE_FILE = "seed_action_kernel_state.json"
SEED_CAPABILITY_MEMORY_FILE = "seed_capability_memory.json"
SEED_CAPABILITY_MEMORY_INDEX_FILE = "seed_capability_memory_index.json"
SEED_MCP_GATEWAY_STATE_FILE = "seed_mcp_gateway_state.json"
SEED_CODING_GATEWAY_STATE_FILE = "seed_coding_gateway_state.json"
SEED_BROWSER_GATEWAY_STATE_FILE = "seed_browser_gateway_state.json"
SEED_VOICE_QUALITY_STATE_FILE = "seed_voice_quality_state.json"
SEED_V22_GATE_REPORT_FILE = "seed_v22_gate_report.json"

SEED_ACTION_KERNEL_VERIFY_RESULTS = True
SEED_ACTION_KERNEL_NO_FAKE_ACTIONS = True
SEED_TOOL_GATEWAYS_PLAN_ONLY_BY_DEFAULT = True
SEED_MEMORY_INDEX_MAX_FILES = 500
SEED_MEMORY_INDEX_MAX_FILE_BYTES = 250000
SEED_MEMORY_SEARCH_MAX_RESULTS = 8

V22_REQUIRED_MODULES = [
    "seed_action_kernel.py",
    "seed_capability_memory.py",
    "seed_mcp_gateway.py",
    "seed_coding_agent_gateway.py",
    "seed_browser_agent_gateway.py",
    "seed_voice_quality_router.py",
    "seed_v22_mega_gate.py"
]

try:
    V2_REQUIRED_MODULES = list(dict.fromkeys(V2_REQUIRED_MODULES + V22_REQUIRED_MODULES))
except NameError:
    V2_REQUIRED_MODULES = list(V22_REQUIRED_MODULES)

try:
    SELF_IMPROVEMENT_TEST_COMMANDS = list(dict.fromkeys(
        SELF_IMPROVEMENT_TEST_COMMANDS
        + [f"python -m py_compile {module}" for module in V22_REQUIRED_MODULES]
    ))
except NameError:
    SELF_IMPROVEMENT_TEST_COMMANDS = [
        f"python -m py_compile {module}" for module in V22_REQUIRED_MODULES
    ]




# Seed v2.3.0 Real Intelligence Layer
SEED_SEMANTIC_MEMORY_FILE = "seed_semantic_memory.json"
SEED_SEMANTIC_INDEX_FILE = "seed_semantic_index.json"
SEED_WORKFLOW_BRAIN_STATE_FILE = "seed_workflow_brain_state.json"
SEED_V23_GATE_REPORT_FILE = "seed_v23_gate_report.json"

SEED_EMBEDDING_PROVIDER = "ollama_then_local_fallback"
SEED_OLLAMA_EMBED_MODEL = "nomic-embed-text"
SEED_OLLAMA_EMBED_URL = "http://localhost:11434/api/embeddings"
SEED_SEMANTIC_INDEX_MAX_FILES = 700
SEED_SEMANTIC_INDEX_MAX_FILE_BYTES = 300000
SEED_SEMANTIC_SEARCH_RESULTS = 8
SEED_WORKFLOW_BRAIN_PLAN_ONLY_BY_DEFAULT = True

V23_REQUIRED_MODULES = [
    "seed_semantic_memory.py",
    "seed_workflow_brain.py",
    "seed_intelligence_context.py",
    "seed_v23_intelligence_gate.py"
]

try:
    V2_REQUIRED_MODULES = list(dict.fromkeys(V2_REQUIRED_MODULES + V23_REQUIRED_MODULES))
except NameError:
    V2_REQUIRED_MODULES = list(V23_REQUIRED_MODULES)

try:
    SELF_IMPROVEMENT_TEST_COMMANDS = list(dict.fromkeys(
        SELF_IMPROVEMENT_TEST_COMMANDS
        + [f"python -m py_compile {module}" for module in V23_REQUIRED_MODULES]
    ))
except NameError:
    SELF_IMPROVEMENT_TEST_COMMANDS = [
        f"python -m py_compile {module}" for module in V23_REQUIRED_MODULES
    ]

