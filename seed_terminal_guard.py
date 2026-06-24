SHELL_PREFIXES = (
    "cd ",
    "python ",
    "python3 ",
    "git ",
    "pip ",
    "uv ",
    "brew ",
    "npm ",
    "node ",
    "aider ",
    "cp ",
    "mv ",
    "rm ",
    "mkdir ",
    "cat ",
    "echo ",
    "lsof ",
    "kill ",
)


def looks_like_terminal_block(text):
    if not text:
        return False

    lines = [line.strip() for line in text.splitlines() if line.strip()]
    if not lines:
        return False

    hits = 0
    for line in lines:
        if line.startswith(SHELL_PREFIXES):
            hits += 1
        if line.endswith("\\"):
            hits += 1
        if "python seed_" in line:
            hits += 1
        if line.startswith("(base) "):
            hits += 2

    return hits >= 1 and not text.strip().startswith("/")


def terminal_block_message(text):
    return (
        "\n=== TERMINAL COMMAND DETECTED ===\n"
        "This looks like a macOS Terminal command, not a Seed chat command.\n\n"
        "Run it in Terminal, not inside Seed Talk mode.\n\n"
        "Seed chat commands start with '/', for example:\n"
        "- /v50-check\n"
        "- /final-gates\n"
        "- /operator-status\n\n"
        "If you want, paste terminal output back here after running it.\n"
    )
