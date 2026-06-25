SEED_VERSION = "v70.0.0"

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




# Seed v2.4.0 Experience Fusion Layer
SEED_REFERENCE_FUSION_STATE_FILE = "seed_reference_fusion_state.json"
SEED_EXPERIENCE_MODE_FILE = "seed_experience_mode.json"
SEED_SMOOTH_UX_STATE_FILE = "seed_smooth_ux_state.json"
SEED_V24_GATE_REPORT_FILE = "seed_v24_gate_report.json"

SEED_DEFAULT_EXPERIENCE_MODE = "companion"
SEED_EXPERIENCE_NO_BLIND_INSTALLS = True
SEED_EXPERIENCE_APPROVAL_FOR_RISKY_TOOLS = True
SEED_EXPERIENCE_VOICE_STYLE = "short_direct_companion"
SEED_EXPERIENCE_REFERENCE_STACK_ENABLED = True

V24_REQUIRED_MODULES = [
    "seed_reference_fusion.py",
    "seed_experience_modes.py",
    "seed_smooth_ux.py",
    "seed_v24_experience_gate.py"
]

try:
    V2_REQUIRED_MODULES = list(dict.fromkeys(V2_REQUIRED_MODULES + V24_REQUIRED_MODULES))
except NameError:
    V2_REQUIRED_MODULES = list(V24_REQUIRED_MODULES)

try:
    SELF_IMPROVEMENT_TEST_COMMANDS = list(dict.fromkeys(
        SELF_IMPROVEMENT_TEST_COMMANDS
        + [f"python -m py_compile {module}" for module in V24_REQUIRED_MODULES]
    ))
except NameError:
    SELF_IMPROVEMENT_TEST_COMMANDS = [
        f"python -m py_compile {module}" for module in V24_REQUIRED_MODULES
    ]




# Seed v2.5.0 Real Skill System
SEED_SKILL_STATE_FILE = "seed_skill_state.json"
SEED_SKILL_HISTORY_FILE = "seed_skill_history.jsonl"
SEED_SKILL_APPROVAL_FILE = "seed_skill_approval_state.json"
SEED_SKILL_PROJECT_ROOT = "."
SEED_SKILL_MAX_READ_BYTES = 12000
SEED_SKILL_MAX_SEARCH_RESULTS = 20
SEED_SKILL_SAFE_TIMEOUT_SECONDS = 12
SEED_BROWSER_READ_MAX_BYTES = 150000
SEED_V25_GATE_REPORT_FILE = "seed_v25_gate_report.json"

SEED_SKILLS_NO_ARBITRARY_SHELL = True
SEED_SKILLS_NO_DELETE = True
SEED_SKILLS_NO_AUTO_COMMIT = True
SEED_SKILLS_APPROVAL_FOR_RISKY = True
SEED_SKILLS_VERIFY_RESULTS = True

V25_REQUIRED_MODULES = [
    "seed_skill_kernel.py",
    "seed_filesystem_skill.py",
    "seed_git_skill.py",
    "seed_repo_inspection_skill.py",
    "seed_safe_shell_skill.py",
    "seed_browser_skill.py",
    "seed_coding_prep_skill.py",
    "seed_v25_skill_gate.py"
]

try:
    V2_REQUIRED_MODULES = list(dict.fromkeys(V2_REQUIRED_MODULES + V25_REQUIRED_MODULES))
except NameError:
    V2_REQUIRED_MODULES = list(V25_REQUIRED_MODULES)

try:
    SELF_IMPROVEMENT_TEST_COMMANDS = list(dict.fromkeys(
        SELF_IMPROVEMENT_TEST_COMMANDS
        + [f"python -m py_compile {module}" for module in V25_REQUIRED_MODULES]
    ))
except NameError:
    SELF_IMPROVEMENT_TEST_COMMANDS = [
        f"python -m py_compile {module}" for module in V25_REQUIRED_MODULES
    ]




# Seed v2.6.0 Supervised Agent Execution Layer
SEED_AGENT_RUN_LIFECYCLE_DIR = "seed_agent_runs"
SEED_AGENT_RUN_STATE_FILE = "seed_agent_run_state.json"
SEED_AGENT_RUN_HISTORY_FILE = "seed_agent_run_history.jsonl"
SEED_AGENT_OPERATOR_STATE_FILE = "seed_agent_operator_state.json"
SEED_V26_GATE_REPORT_FILE = "seed_v26_gate_report.json"

SEED_AGENT_EXECUTION_SUPERVISED_ONLY = True
SEED_AGENT_EXECUTION_REQUIRE_APPROVAL = True
SEED_AGENT_EXECUTION_NO_AUTO_EDIT = True
SEED_AGENT_EXECUTION_NO_AUTO_COMMIT = True
SEED_AGENT_EXECUTION_NO_EXTERNAL_AGENT_BY_DEFAULT = True
SEED_AGENT_EXECUTION_SAFE_INTERNAL_ONLY = True

V26_REQUIRED_MODULES = [
    "seed_agent_run_lifecycle.py",
    "seed_agent_operator_console.py",
    "seed_v26_agent_gate.py"
]

try:
    V2_REQUIRED_MODULES = list(dict.fromkeys(V2_REQUIRED_MODULES + V26_REQUIRED_MODULES))
except NameError:
    V2_REQUIRED_MODULES = list(V26_REQUIRED_MODULES)

try:
    SELF_IMPROVEMENT_TEST_COMMANDS = list(dict.fromkeys(
        SELF_IMPROVEMENT_TEST_COMMANDS
        + [f"python -m py_compile {module}" for module in V26_REQUIRED_MODULES]
    ))
except NameError:
    SELF_IMPROVEMENT_TEST_COMMANDS = [
        f"python -m py_compile {module}" for module in V26_REQUIRED_MODULES
    ]




# Seed v2.7.0 Executor Bridge + Repo Doctor + Voice Upgrade Planner
SEED_EXECUTOR_BRIDGE_STATE_FILE = "seed_executor_bridge_state.json"
SEED_EXECUTOR_BRIDGE_HISTORY_FILE = "seed_executor_bridge_history.jsonl"
SEED_REPO_DOCTOR_REPORT_FILE = "seed_repo_doctor_report.json"
SEED_VOICE_UPGRADE_PLAN_FILE = "seed_voice_upgrade_plan.json"
SEED_V27_GATE_REPORT_FILE = "seed_v27_gate_report.json"

SEED_EXECUTOR_BRIDGE_NO_AUTO_INSTALL = True
SEED_EXECUTOR_BRIDGE_NO_EXTERNAL_RUN_BY_DEFAULT = True
SEED_EXECUTOR_BRIDGE_REQUIRE_APPROVAL = True
SEED_EXECUTOR_BRIDGE_MANUAL_COMMANDS_ONLY = True
SEED_REPO_DOCTOR_READ_ONLY = True
SEED_VOICE_UPGRADE_PLANNER_READ_ONLY = True

V27_REQUIRED_MODULES = [
    "seed_external_executor_bridge.py",
    "seed_repo_doctor.py",
    "seed_voice_upgrade_planner.py",
    "seed_v27_executor_gate.py"
]

try:
    V2_REQUIRED_MODULES = list(dict.fromkeys(V2_REQUIRED_MODULES + V27_REQUIRED_MODULES))
except NameError:
    V2_REQUIRED_MODULES = list(V27_REQUIRED_MODULES)

try:
    SELF_IMPROVEMENT_TEST_COMMANDS = list(dict.fromkeys(
        SELF_IMPROVEMENT_TEST_COMMANDS
        + [f"python -m py_compile {module}" for module in V27_REQUIRED_MODULES]
    ))
except NameError:
    SELF_IMPROVEMENT_TEST_COMMANDS = [
        f"python -m py_compile {module}" for module in V27_REQUIRED_MODULES
    ]




# Seed v2.8.0 Aider First Executor Bridge
SEED_AIDER_BRIDGE_STATE_FILE = "seed_aider_bridge_state.json"
SEED_AIDER_BRIDGE_HISTORY_FILE = "seed_aider_bridge_history.jsonl"
SEED_AIDER_RUNS_DIR = "seed_agent_runs"
SEED_V28_GATE_REPORT_FILE = "seed_v28_gate_report.json"

SEED_AIDER_NO_AUTO_INSTALL = True
SEED_AIDER_NO_AUTO_EXECUTE = True
SEED_AIDER_REQUIRE_APPROVAL = True
SEED_AIDER_REQUIRE_TARGET_FILES = True
SEED_AIDER_REQUIRE_CLEAN_GIT = False
SEED_AIDER_EXECUTION_LOCKED = True
SEED_AIDER_SAFE_DEFAULT_MODE = "plan_only"

V28_REQUIRED_MODULES = [
    "seed_aider_bridge.py",
    "seed_v28_aider_gate.py"
]

try:
    V2_REQUIRED_MODULES = list(dict.fromkeys(V2_REQUIRED_MODULES + V28_REQUIRED_MODULES))
except NameError:
    V2_REQUIRED_MODULES = list(V28_REQUIRED_MODULES)

try:
    SELF_IMPROVEMENT_TEST_COMMANDS = list(dict.fromkeys(
        SELF_IMPROVEMENT_TEST_COMMANDS
        + [f"python -m py_compile {module}" for module in V28_REQUIRED_MODULES]
    ))
except NameError:
    SELF_IMPROVEMENT_TEST_COMMANDS = [
        f"python -m py_compile {module}" for module in V28_REQUIRED_MODULES
    ]




# Seed v2.9.0 Mission Control MegaPack
SEED_MISSION_CONTROL_STATE_FILE = "seed_mission_control_state.json"
SEED_RELEASE_ORCHESTRATOR_REPORT_FILE = "seed_release_orchestrator_report.json"
SEED_VOICE_UX_STATE_FILE = "seed_voice_ux_state.json"
SEED_TRANSCRIPT_JOURNAL_FILE = "seed_transcript_journal.jsonl"
SEED_SELF_REPAIR_PLAN_FILE = "seed_self_repair_plan.json"
SEED_COMMAND_MEMORY_FILE = "seed_command_memory.json"
SEED_APP_MANIFEST_FILE = "seed_local_app_manifest.json"
SEED_V29_GATE_REPORT_FILE = "seed_v29_gate_report.json"

SEED_MISSION_CONTROL_READ_ONLY = True
SEED_RELEASE_ORCHESTRATOR_SAFE_ONLY = True
SEED_SELF_REPAIR_PLAN_ONLY = True
SEED_VOICE_UX_NO_SECRET_LISTENING = True
SEED_COMMAND_MEMORY_NO_AUTO_EXECUTE = True

V29_REQUIRED_MODULES = [
    "seed_mission_control.py",
    "seed_release_orchestrator.py",
    "seed_voice_ux_pack.py",
    "seed_self_repair_planner.py",
    "seed_command_memory.py",
    "seed_local_app_manifest.py",
    "seed_v29_mission_gate.py"
]

try:
    V2_REQUIRED_MODULES = list(dict.fromkeys(V2_REQUIRED_MODULES + V29_REQUIRED_MODULES))
except NameError:
    V2_REQUIRED_MODULES = list(V29_REQUIRED_MODULES)

try:
    SELF_IMPROVEMENT_TEST_COMMANDS = list(dict.fromkeys(
        SELF_IMPROVEMENT_TEST_COMMANDS
        + [f"python -m py_compile {module}" for module in V29_REQUIRED_MODULES]
    ))
except NameError:
    SELF_IMPROVEMENT_TEST_COMMANDS = [
        f"python -m py_compile {module}" for module in V29_REQUIRED_MODULES
    ]




# Seed v3.0.0 Jarvis Control Plane + Local Command Center
SEED_CONTROL_PLANE_HOST = "127.0.0.1"
SEED_CONTROL_PLANE_PORT = 8790
SEED_CONTROL_PLANE_URL = "http://127.0.0.1:8790"
SEED_CONTROL_PLANE_STATE_FILE = "seed_control_plane_state.json"
SEED_GATE_MATRIX_REPORT_FILE = "seed_gate_matrix_report.json"
SEED_RUNTIME_SUPERVISOR_STATE_FILE = "seed_runtime_supervisor_state.json"
SEED_SESSION_TIMELINE_FILE = "seed_session_timeline.json"
SEED_COMMAND_CENTER_FILE = "seed_command_center.json"
SEED_V30_GATE_REPORT_FILE = "seed_v30_gate_report.json"

SEED_CONTROL_PLANE_LOCAL_ONLY = True
SEED_CONTROL_PLANE_READ_ONLY_DEFAULT = True
SEED_CONTROL_PLANE_NO_REMOTE_BIND = True
SEED_CONTROL_PLANE_NO_SECRETS = True
SEED_CONTROL_PLANE_NO_AUTO_EXECUTE = True

V30_REQUIRED_MODULES = [
    "seed_gate_matrix.py",
    "seed_runtime_supervisor.py",
    "seed_session_timeline.py",
    "seed_command_center.py",
    "seed_control_plane_ui.py",
    "seed_control_plane_server.py",
    "seed_control_plane_launcher.py",
    "seed_v30_control_gate.py"
]

try:
    V2_REQUIRED_MODULES = list(dict.fromkeys(V2_REQUIRED_MODULES + V30_REQUIRED_MODULES))
except NameError:
    V2_REQUIRED_MODULES = list(V30_REQUIRED_MODULES)

try:
    SELF_IMPROVEMENT_TEST_COMMANDS = list(dict.fromkeys(
        SELF_IMPROVEMENT_TEST_COMMANDS
        + [f"python -m py_compile {module}" for module in V30_REQUIRED_MODULES]
    ))
except NameError:
    SELF_IMPROVEMENT_TEST_COMMANDS = [
        f"python -m py_compile {module}" for module in V30_REQUIRED_MODULES
    ]




# Seed v3.5.0 Omega Integration Pack
SEED_REPO_DNA_FILE = "seed_repo_dna.json"
SEED_INTEGRATION_FUSION_FILE = "seed_integration_fusion.json"
SEED_OMEGA_PLAN_FILE = "seed_omega_plan.json"
SEED_CONTROL_ACTION_HISTORY_FILE = "seed_control_action_history.jsonl"
SEED_VOICE_ONE_SHOT_HISTORY_FILE = "seed_voice_one_shot_history.jsonl"
SEED_V35_GATE_REPORT_FILE = "seed_v35_gate_report.json"

SEED_CONTROL_ACTION_REQUIRE_HEADER = True
SEED_CONTROL_ACTION_HEADER_NAME = "X-Seed-Action"
SEED_CONTROL_ACTION_HEADER_VALUE = "local-control-plane"
SEED_CONTROL_ACTION_ALLOWLIST_ONLY = True
SEED_OMEGA_NO_AUTO_INSTALL = True
SEED_OMEGA_NO_AUTO_EXTERNAL_EXECUTION = True
SEED_OMEGA_NO_AUTO_COMMIT = True
SEED_OMEGA_CONTROLLED_RISK = True

V35_REQUIRED_MODULES = [
    "seed_repo_dna_engine.py",
    "seed_integration_fusion_engine.py",
    "seed_omega_planner.py",
    "seed_control_plane_actions.py",
    "seed_voice_one_shot.py",
    "seed_control_plane_ui_omega.py",
    "seed_v35_omega_gate.py"
]

try:
    V2_REQUIRED_MODULES = list(dict.fromkeys(V2_REQUIRED_MODULES + V35_REQUIRED_MODULES))
except NameError:
    V2_REQUIRED_MODULES = list(V35_REQUIRED_MODULES)

try:
    SELF_IMPROVEMENT_TEST_COMMANDS = list(dict.fromkeys(
        SELF_IMPROVEMENT_TEST_COMMANDS
        + [f"python -m py_compile {module}" for module in V35_REQUIRED_MODULES]
    ))
except NameError:
    SELF_IMPROVEMENT_TEST_COMMANDS = [
        f"python -m py_compile {module}" for module in V35_REQUIRED_MODULES
    ]




# Seed v3.6.0 Real Integration Runtime
SEED_MCP_SKILL_SERVER_MANIFEST_FILE = "seed_mcp_skill_manifest.json"
SEED_MCP_SKILL_SERVER_STATE_FILE = "seed_mcp_skill_server_state.json"
SEED_AIDER_UNLOCK_STATE_FILE = "seed_aider_unlock_state.json"
SEED_AIDER_UNLOCK_HISTORY_FILE = "seed_aider_unlock_history.jsonl"
SEED_INTEGRATION_SANDBOX_STATE_FILE = "seed_integration_sandbox_state.json"
SEED_V36_GATE_REPORT_FILE = "seed_v36_gate_report.json"

SEED_MCP_SKILL_SERVER_LOCAL_ONLY = True
SEED_MCP_SKILL_SERVER_NO_ARBITRARY_SHELL = True
SEED_AIDER_REAL_EXECUTION_LOCKED_BY_DEFAULT = True
SEED_AIDER_DRY_RUN_FIRST = True
SEED_AIDER_REQUIRE_EXPLICIT_REAL_RUN_PHRASE = True
SEED_AIDER_REAL_RUN_PHRASE = "I UNDERSTAND AIDER CAN EDIT FILES"
SEED_AIDER_NO_AUTO_COMMITS = True
SEED_AIDER_NO_DIRTY_COMMITS = True
SEED_AIDER_TARGET_FILES_ONLY = True
SEED_INTEGRATION_SANDBOX_NO_AUTO_EXTERNAL_RUN = True

V36_REQUIRED_MODULES = [
    "seed_mcp_skill_server.py",
    "seed_mcp_skill_manifest.py",
    "seed_aider_execution_unlock.py",
    "seed_integration_sandbox.py",
    "seed_v36_integration_gate.py"
]

try:
    V2_REQUIRED_MODULES = list(dict.fromkeys(V2_REQUIRED_MODULES + V36_REQUIRED_MODULES))
except NameError:
    V2_REQUIRED_MODULES = list(V36_REQUIRED_MODULES)

try:
    SELF_IMPROVEMENT_TEST_COMMANDS = list(dict.fromkeys(
        SELF_IMPROVEMENT_TEST_COMMANDS
        + [f"python -m py_compile {module}" for module in V36_REQUIRED_MODULES]
    ))
except NameError:
    SELF_IMPROVEMENT_TEST_COMMANDS = [
        f"python -m py_compile {module}" for module in V36_REQUIRED_MODULES
    ]




# Seed v4.0.0 Runtime OS Upgrade
SEED_EVENT_BUS_FILE = "seed_event_bus.jsonl"
SEED_SERVICE_MANAGER_STATE_FILE = "seed_service_manager_state.json"
SEED_WORKFLOW_AUTOMATION_STATE_FILE = "seed_workflow_automation_state.json"
SEED_ROLLBACK_STATE_FILE = "seed_rollback_state.json"
SEED_MEMORY_DISTILL_FILE = "seed_memory_distill.json"
SEED_AIDER_PATCH_FLOW_STATE_FILE = "seed_aider_patch_flow_state.json"
SEED_V40_GATE_REPORT_FILE = "seed_v40_gate_report.json"
SEED_CHECKPOINT_DIR = "seed_checkpoints"

SEED_RUNTIME_OS_LOCAL_ONLY = True
SEED_RUNTIME_OS_NO_ARBITRARY_SHELL = True
SEED_RUNTIME_OS_NO_DELETE = True
SEED_RUNTIME_OS_NO_AUTO_COMMIT = True
SEED_RUNTIME_OS_APPROVAL_FOR_RESTORE = True
SEED_RUNTIME_OS_APPROVAL_FOR_AIDER_REAL = True

V40_REQUIRED_MODULES = [
    "seed_event_bus.py",
    "seed_service_manager.py",
    "seed_mcp_client.py",
    "seed_workflow_automation.py",
    "seed_patch_rollback.py",
    "seed_aider_patch_flow.py",
    "seed_memory_distiller.py",
    "seed_v40_os_gate.py"
]

try:
    V2_REQUIRED_MODULES = list(dict.fromkeys(V2_REQUIRED_MODULES + V40_REQUIRED_MODULES))
except NameError:
    V2_REQUIRED_MODULES = list(V40_REQUIRED_MODULES)

try:
    SELF_IMPROVEMENT_TEST_COMMANDS = list(dict.fromkeys(
        SELF_IMPROVEMENT_TEST_COMMANDS
        + [f"python -m py_compile {module}" for module in V40_REQUIRED_MODULES]
    ))
except NameError:
    SELF_IMPROVEMENT_TEST_COMMANDS = [
        f"python -m py_compile {module}" for module in V40_REQUIRED_MODULES
    ]




# Seed v5.0.0 Autonomous Operator Core
SEED_GOAL_ENGINE_STATE_FILE = "seed_goal_engine_state.json"
SEED_TASK_OS_FILE = "seed_task_os.json"
SEED_CAPABILITY_GRAPH_FILE = "seed_capability_graph.json"
SEED_EXECUTION_POLICY_FILE = "seed_execution_policy.json"
SEED_OPERATOR_RUNTIME_STATE_FILE = "seed_operator_runtime_state.json"
SEED_OPERATOR_INBOX_FILE = "seed_operator_inbox.jsonl"
SEED_V50_GATE_REPORT_FILE = "seed_v50_gate_report.json"

SEED_OPERATOR_MANUAL_TICK_ONLY = True
SEED_OPERATOR_NO_BACKGROUND_AUTONOMY = True
SEED_OPERATOR_NO_ARBITRARY_SHELL = True
SEED_OPERATOR_NO_DELETE = True
SEED_OPERATOR_NO_AUTO_COMMIT = True
SEED_OPERATOR_AIDER_DRY_RUN_FIRST = True
SEED_OPERATOR_CONTROLLED_RISK = True

V50_REQUIRED_MODULES = [
    "seed_execution_policy.py",
    "seed_capability_graph.py",
    "seed_task_os.py",
    "seed_goal_engine.py",
    "seed_operator_inbox.py",
    "seed_operator_runtime.py",
    "seed_control_plane_ui_v5.py",
    "seed_v50_operator_gate.py"
]

try:
    V2_REQUIRED_MODULES = list(dict.fromkeys(V2_REQUIRED_MODULES + V50_REQUIRED_MODULES))
except NameError:
    V2_REQUIRED_MODULES = list(V50_REQUIRED_MODULES)

try:
    SELF_IMPROVEMENT_TEST_COMMANDS = list(dict.fromkeys(
        SELF_IMPROVEMENT_TEST_COMMANDS
        + [f"python -m py_compile {module}" for module in V50_REQUIRED_MODULES]
    ))
except NameError:
    SELF_IMPROVEMENT_TEST_COMMANDS = [
        f"python -m py_compile {module}" for module in V50_REQUIRED_MODULES
    ]



# Seed v5.1.0 Performance Kernel
SEED_PERFORMANCE_KERNEL_ENABLED = True
SEED_FAST_CONTEXT_DEFAULT = True
SEED_HEAVY_CONTEXT_OPT_IN = True
SEED_V51_GATE_REPORT_FILE = "seed_v51_performance_gate.json"


# Seed v5.2 Fast Chat Runtime
SEED_FAST_CHAT_RUNTIME = True
SEED_FASTPATH_REPLIES = True
SEED_OLLAMA_TIMEOUT_CAP_SECONDS = 20



# Seed v20.0.0 Sovereign Companion OS MegaCore
SEED_V20_STATE_FILE = "seed_v20_sovereign_state.json"
SEED_V20_GATE_REPORT_FILE = "seed_v20_gate_report.json"
SEED_MEMORY_V2_FILE = "seed_memory_v2.json"
SEED_VOICE_RUNTIME_FILE = "seed_voice_runtime_v6.json"
SEED_WORKFLOW_GRAPH_FILE = "seed_workflow_graph_v9.json"
SEED_BROWSER_SANDBOX_FILE = "seed_browser_sandbox_v10.json"
SEED_MCP_MARKETPLACE_FILE = "seed_mcp_marketplace_v11.json"
SEED_OPENHANDS_SANDBOX_FILE = "seed_openhands_sandbox_v12.json"
SEED_PROJECT_LIFE_OS_FILE = "seed_project_life_os_v14.json"
SEED_WORLD_AVATAR_FILE = "seed_world_avatar_v16.json"
SEED_AGENT_COUNCIL_V17_FILE = "seed_agent_council_v17.json"
SEED_SELF_IMPROVEMENT_LAB_FILE = "seed_self_improvement_lab_v18.json"
SEED_MULTIDEVICE_HUB_FILE = "seed_multidevice_hub_v19.json"

SEED_V20_NO_BLIND_INSTALLS = True
SEED_V20_ADAPTER_FIRST = True
SEED_V20_SANDBOX_HIGH_RISK_TOOLS = True
SEED_V20_NO_ARBITRARY_SHELL = True
SEED_V20_NO_DELETE = True
SEED_V20_NO_AUTO_COMMIT = True
SEED_V20_MANUAL_TICK_ONLY = True
SEED_V20_LOCAL_FIRST = True

V20_REQUIRED_MODULES = [
    "seed_memory_engine_v2.py",
    "seed_voice_runtime_v6.py",
    "seed_workflow_graph_v9.py",
    "seed_browser_sandbox_v10.py",
    "seed_mcp_marketplace_v11.py",
    "seed_openhands_sandbox_v12.py",
    "seed_project_life_os_v14.py",
    "seed_world_avatar_v16.py",
    "seed_agent_council_v17.py",
    "seed_self_improvement_lab_v18.py",
    "seed_multidevice_hub_v19.py",
    "seed_v20_sovereign_os.py",
    "seed_control_plane_ui_v20.py",
    "seed_v20_sovereign_gate.py"
]

try:
    V2_REQUIRED_MODULES = list(dict.fromkeys(V2_REQUIRED_MODULES + V20_REQUIRED_MODULES))
except NameError:
    V2_REQUIRED_MODULES = list(V20_REQUIRED_MODULES)

try:
    SELF_IMPROVEMENT_TEST_COMMANDS = list(dict.fromkeys(
        SELF_IMPROVEMENT_TEST_COMMANDS
        + [f"python -m py_compile {module}" for module in V20_REQUIRED_MODULES]
    ))
except NameError:
    SELF_IMPROVEMENT_TEST_COMMANDS = [
        f"python -m py_compile {module}" for module in V20_REQUIRED_MODULES
    ]



# Seed v20.3 Presence Runtime + Curiosity Loop
SEED_PRESENCE_RUNTIME_ENABLED = True
SEED_PRESENCE_QUEUE_ONLY = True
SEED_PRESENCE_NO_RANDOM_CHATTER = True
SEED_PRESENCE_DEFAULT_INTERVAL_SECONDS = 300



# Seed v30.0.0 Repo Assimilation + Agent HQ MegaPatch
SEED_V30_STATE_FILE = "seed_v30_agent_hq_state.json"
SEED_V30_GATE_REPORT_FILE = "seed_v30_megapatch_gate.json"
SEED_REPO_ASSIMILATION_FILE = "seed_repo_assimilation_report.json"
SEED_REPO_SCOREBOARD_FILE = "seed_integration_scoreboard.json"
SEED_EXTERNAL_ADAPTER_REGISTRY_FILE = "seed_external_adapter_registry.json"
SEED_REPO_TO_SEED_PLAN_FILE = "seed_repo_to_seed_plan.json"
SEED_AGENT_HQ_FILE = "seed_agent_hq_v30.json"

SEED_V30_ADAPTER_FIRST = True
SEED_V30_NO_BLIND_INSTALLS = True
SEED_V30_SANDBOX_FIRST = True
SEED_V30_PROMOTE_ONLY_AFTER_GATES = True
SEED_V30_NO_DIRECT_EXTERNAL_AGENT_CORE_MUTATION = True

V30_REQUIRED_MODULES = [
    "seed_external_adapter_registry.py",
    "seed_repo_pattern_extractor.py",
    "seed_repo_risk_scanner.py",
    "seed_repo_assimilation_engine.py",
    "seed_integration_scoreboard.py",
    "seed_repo_to_seed_planner.py",
    "seed_agent_hq_v30.py",
    "seed_control_plane_ui_v30.py",
    "seed_v30_megapatch_gate.py",
    "seed_v30_commands.py"
]

try:
    V20_REQUIRED_MODULES = list(dict.fromkeys(V20_REQUIRED_MODULES + V30_REQUIRED_MODULES))
except NameError:
    V20_REQUIRED_MODULES = list(V30_REQUIRED_MODULES)



# Seed v45.0.0 Total Systems Implementation MegaPatch
SEED_V45_TOTAL_SYSTEMS = True
SEED_TERMINAL_PRO = True
SEED_CONTROL_PLANE_PROFESSIONAL = True
SEED_V45_GATE_REPORT_FILE = "seed_v45_total_gate.json"


# Seed v50.0.0 Nothing Left Behind Finalization Pack
SEED_V50_NOTHING_LEFT_BEHIND = True
SEED_V50_GATE_REPORT_FILE = "seed_v50_gate_report.json"
SEED_V50_STATE_FILE = "seed_v50_nothing_left_behind_state.json"


# Seed v60.0.0 Real Intelligence + Natural UX Fusion
SEED_V60_REAL_INTELLIGENCE_UX = True
SEED_V60_NATURAL_LANGUAGE_FIRST = True
SEED_V60_GATE_REPORT_FILE = "seed_v60_gate_report.json"

SEED_V70_MEGA_FUSION = True
SEED_COMPANION_TERMINAL_DEFAULT = True
SEED_V70_GATE_REPORT_FILE = "seed_v70_gate_report.json"
