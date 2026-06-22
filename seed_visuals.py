import os
import glob
from datetime import datetime

from seed_config import (
    SEED_VERSION,
    MODEL_NAME,
    OLLAMA_URL,
    SEED_MODE,
    CHAT_LOG_DIR,
    VISUAL_THEME_NAME,
    VISUAL_ACCENT,
    VISUAL_SUCCESS_STYLE,
    VISUAL_WARNING_STYLE,
    EMBEDDING_MODEL, 
    MEMORY_EMBEDDINGS_FILE
)

from seed_memory import memories, ALLOWED_TYPES
from seed_journal import get_recent_journal_entries
from seed_project_inspector import get_python_modules, get_project_files
from seed_personality import get_hud_personality_lines
from seed_llm import get_llm_hud_lines
from seed_self_editor import load_pending_edit, get_editable_files
from seed_semantic_memory import load_embedding_cache
from seed_tool_kernel import TOOL_REGISTRY
from seed_open_source_dna import load_dna_data
from seed_skill_kernel import load_all_skills, get_all_capabilities

try:
    from rich.console import Console
    from rich.panel import Panel
    from rich.table import Table
    from rich.columns import Columns
    from rich.align import Align
    from rich.text import Text
    from rich import box

    

    RICH_AVAILABLE = True
except ImportError:
    RICH_AVAILABLE = False


def make_dna_panel():
    data = load_dna_data()
    audits = data.get("audits", {})

    table = Table.grid(padding=(0, 2))
    table.add_column(style="grey70")
    table.add_column(style="white")

    table.add_row("Repos found", f"{data.get('found_count')} / {data.get('repo_count')}")
    table.add_row("Audits", str(len(audits)))
    table.add_row("Research dir", "third_party_repos")
    table.add_row("Next use", "v1.12 skill/planner rewrite")

    return Panel(
        table,
        title="OPEN-SOURCE DNA",
        border_style=VISUAL_ACCENT,
        box=box.ROUNDED
    )

def count_memories_by_type():
    counts = {}

    for memory_type in ALLOWED_TYPES:
        counts[memory_type] = 0

    for memory in memories:
        memory_type = memory.get("type", "unknown")

        if memory_type not in counts:
            counts[memory_type] = 0

        counts[memory_type] += 1

    return counts


def get_latest_log_file():
    log_files = glob.glob(os.path.join(CHAT_LOG_DIR, "*.txt"))

    if not log_files:
        return None

    log_files.sort(key=os.path.getmtime, reverse=True)
    return log_files[0]


def get_log_count():
    log_files = glob.glob(os.path.join(CHAT_LOG_DIR, "*.txt"))
    return len(log_files)


def make_header(console):
    title = Text()
    title.append("SEED ", style=f"bold {VISUAL_ACCENT}")
    title.append(SEED_VERSION, style="bold white")
    title.append("  •  Local Companion System", style="grey70")

    subtitle = Text(
        "Memory-aware • Local-first • Ollama-powered • Built by Altan",
        style="grey70"
    )

    panel = Panel(
        Align.center(title + "\n" + subtitle),
        border_style=VISUAL_ACCENT,
        box=box.DOUBLE,
        padding=(1, 2)
    )

    console.print(panel)


def make_status_panel():
    table = Table.grid(padding=(0, 2))
    table.add_column(style="grey70")
    table.add_column(style="white")

    table.add_row("Version", SEED_VERSION)
    table.add_row("Mode", SEED_MODE)
    table.add_row("Model", MODEL_NAME)
    table.add_row("Ollama URL", OLLAMA_URL)
    table.add_row("Theme", VISUAL_THEME_NAME)
    table.add_row("Time", datetime.now().isoformat(timespec="seconds"))

    return Panel(
        table,
        title="SYSTEM STATUS",
        border_style=VISUAL_ACCENT,
        box=box.ROUNDED
    )


def make_memory_panel(chat_state=None):
    counts = count_memories_by_type()

    table = Table(box=box.SIMPLE_HEAVY)
    table.add_column("Type", style="grey70")
    table.add_column("Count", justify="right", style="white")

    pending_draft = "no"

    if chat_state is not None and chat_state.get("pending_memory_draft") is not None:
        pending_draft = "yes"

    table.add_row("pending_draft", pending_draft)

    for memory_type, count in counts.items():
        if count > 0:
            style = VISUAL_SUCCESS_STYLE
        else:
            style = "grey50"

        table.add_row(memory_type, f"[{style}]{count}[/{style}]")

    total = len(memories)

    return Panel(
        table,
        title=f"MEMORY CORE • total {total}",
        border_style=VISUAL_ACCENT,
        box=box.ROUNDED
    )


def make_project_panel():
    modules = get_python_modules()
    files = get_project_files()

    table = Table(box=box.SIMPLE)
    table.add_column("Python Modules", style="white")

    for module in modules[:12]:
        table.add_row(module)

    if len(modules) > 12:
        table.add_row(f"...and {len(modules) - 12} more")

    footer = f"\nTotal files: {len(files)} | Python modules: {len(modules)}"

    return Panel(
        table,
        title="PROJECT BODY",
        subtitle=footer,
        border_style=VISUAL_ACCENT,
        box=box.ROUNDED
    )


def make_journal_panel():
    journal_text = get_recent_journal_entries()

    return Panel(
        journal_text,
        title="RECENT JOURNAL",
        border_style=VISUAL_ACCENT,
        box=box.ROUNDED
    )


def make_log_panel(chat_state=None):
    current_log = None

    if chat_state is not None:
        current_log = chat_state.get("log_path")

    latest_log = get_latest_log_file()
    log_count = get_log_count()

    table = Table.grid(padding=(0, 1))
    table.add_column(style="grey70")
    table.add_column(style="white")

    table.add_row("Log files", str(log_count))
    table.add_row("Current log", current_log if current_log else "No active chat log")
    table.add_row("Latest log", latest_log if latest_log else "No logs found")

    return Panel(
        table,
        title="LOG SYSTEM",
        border_style=VISUAL_ACCENT,
        box=box.ROUNDED
    )


def make_commands_panel():
    table = Table(box=box.SIMPLE)
    table.add_column("Command", style=VISUAL_ACCENT)
    table.add_column("Purpose", style="grey70")

    commands = [
        ("/hud", "show this dashboard"),
        ("/status", "system status"),
        ("/config", "configuration"),
        ("/project", "project report"),
        ("/memory-debug", "memory scoring"),
        ("/summary", "session summary"),
        ("/log-read", "recent log lines"),
        ("/save", "save memory"),
        ("/journal", "write journal"),
        ("/exit", "leave chat")
    ]

    for command, purpose in commands:
        table.add_row(command, purpose)

    return Panel(
        table,
        title="COMMAND DECK",
        border_style=VISUAL_ACCENT,
        box=box.ROUNDED
    )

def make_agent_panel(chat_state=None):
    table = Table.grid(padding=(0, 2))
    table.add_column(style="grey70")
    table.add_column(style="white")

    pending_plan = "no"
    last_run = "no"
    last_review = "no"

    if chat_state is not None:
        if chat_state.get("pending_agent_plan") is not None:
            pending_plan = "yes"

        if chat_state.get("last_agent_run") is not None:
            last_run = "yes"

        if chat_state.get("last_self_review") is not None:
            last_review = "yes"

    table.add_row("Tools", str(len(TOOL_REGISTRY)))
    table.add_row("Pending plan", pending_plan)
    table.add_row("Last run", last_run)
    table.add_row("Self-review", last_review)
    table.add_row("Auto-run", "read-only only")

    return Panel(
        table,
        title="AGENT KERNEL",
        border_style=VISUAL_ACCENT,
        box=box.ROUNDED
    )

def make_personality_panel():
    table = Table.grid(padding=(0, 2))
    table.add_column(style="grey70")
    table.add_column(style="white")

    for label, value in get_hud_personality_lines():
        table.add_row(label, value)

    return Panel(
        table,
        title="PERSONALITY CORE",
        border_style=VISUAL_ACCENT,
        box=box.ROUNDED
    )

def make_llm_panel(chat_state=None):
    table = Table.grid(padding=(0, 2))
    table.add_column(style="grey70")
    table.add_column(style="white")

    for label, value in get_llm_hud_lines(chat_state):
        table.add_row(label, value)

    return Panel(
        table,
        title="LLM ENGINE",
        border_style=VISUAL_ACCENT,
        box=box.ROUNDED
    )

def make_self_edit_panel():
    pending_edit = load_pending_edit()
    editable_files = get_editable_files()

    table = Table.grid(padding=(0, 2))
    table.add_column(style="grey70")
    table.add_column(style="white")

    table.add_row("Editable files", str(len(editable_files)))

    if pending_edit is None:
        table.add_row("Pending edit", "none")
    else:
        table.add_row("Pending edit", pending_edit.get("target_path", "unknown"))
        table.add_row("Instruction", pending_edit.get("instruction", ""))

    table.add_row("Apply gate", "requires APPLY")
    table.add_row("Rollback", "latest backup available after edits")

    return Panel(
        table,
        title="SELF-EDIT KERNEL",
        border_style=VISUAL_ACCENT,
        box=box.ROUNDED
    )

def make_semantic_memory_panel():
    cache = load_embedding_cache()
    cached_count = len(cache.get("items", {}))

    table = Table.grid(padding=(0, 2))
    table.add_column(style="grey70")
    table.add_column(style="white")

    table.add_row("Embedding model", EMBEDDING_MODEL)
    table.add_row("Cache file", MEMORY_EMBEDDINGS_FILE)
    table.add_row("Memory count", str(len(memories)))
    table.add_row("Cached vectors", str(cached_count))

    if cached_count == 0:
        table.add_row("Status", "needs /memory-reindex")
    else:
        table.add_row("Status", "ready")

    return Panel(
        table,
        title="SEMANTIC MEMORY",
        border_style=VISUAL_ACCENT,
        box=box.ROUNDED
    )

def make_skill_os_panel(chat_state=None):
    skills = load_all_skills()
    capabilities = get_all_capabilities()

    pending_plan = "no"
    last_run = "no"

    if chat_state is not None:
        if chat_state.get("pending_skill_plan") is not None:
            pending_plan = "yes"

        if chat_state.get("last_skill_run") is not None:
            last_run = "yes"

    table = Table.grid(padding=(0, 2))
    table.add_column(style="grey70")
    table.add_column(style="white")

    table.add_row("Skills", str(len(skills)))
    table.add_row("Capabilities", str(len(capabilities)))
    table.add_row("Pending plan", pending_plan)
    table.add_row("Last run", last_run)
    table.add_row("Auto-run", "read-only/diagnostic")

    return Panel(
        table,
        title="SKILL OS",
        border_style=VISUAL_ACCENT,
        box=box.ROUNDED
    )

def show_seed_hud(chat_state=None):

    if not RICH_AVAILABLE:
        print("\nRich is not installed.")
        print("Run: python -m pip install rich")
        return

    console = Console()

    console.clear()
    make_header(console)

    self_edit_panel = make_self_edit_panel()
    llm_panel = make_llm_panel(chat_state)
    status_panel = make_status_panel()
    memory_panel = make_memory_panel(chat_state)
    project_panel = make_project_panel()
    log_panel = make_log_panel(chat_state)
    journal_panel = make_journal_panel()
    commands_panel = make_commands_panel()
    personality_panel = make_personality_panel()
    semantic_panel = make_semantic_memory_panel()
    agent_panel = make_agent_panel(chat_state)
    dna_panel = make_dna_panel()
    skill_os_panel = make_skill_os_panel(chat_state)

    console.print(
        Columns(
            [status_panel, memory_panel],
            equal=True,
            expand=True
        )
    )

    console.print(
        Columns(
            [agent_panel, dna_panel],
            equal=True,
            expand=True
        )
    )
    console.print(
        Columns(
            [skill_os_panel, dna_panel],
            equal=True,
            expand=True
        )
    )

    console.print(
        Columns(
            [llm_panel, semantic_panel],
            equal=True,
            expand=True
        )
    )

    console.print(
        Columns(
            [personality_panel, self_edit_panel],
            equal=True,
            expand=True
        )
    )

    console.print(
        Columns(
            [agent_panel, self_edit_panel],
            equal=True,
            expand=True
        )
    )

    console.print(
        Columns(
            [project_panel, log_panel],
            equal=True,
            expand=True
        )
    )

    console.print(journal_panel)
    console.print(commands_panel)
    console.print(
        Align.center(
            Text(
                "Seed HUD ready. Use /help for full command list.",
                style=f"bold {VISUAL_ACCENT}"
            )
        )
    )

def show_seed_hud_screen(chat_state=None):
    show_seed_hud(chat_state)

    if not RICH_AVAILABLE:
        return

    input("\nPress Enter to return...")