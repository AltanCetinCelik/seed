SEED_VERSION = "v1.6.0"

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