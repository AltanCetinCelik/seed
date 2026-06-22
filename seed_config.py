SEED_VERSION = "v1.12.0"

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