import os
import stat
import sys
from pathlib import Path
from datetime import datetime


def now_timestamp():
    return datetime.now().isoformat(timespec="seconds")


def repo_dir():
    return Path(__file__).resolve().parent


def desktop_dir():
    return Path.home() / "Desktop"


def write_executable(path, content):
    path.write_text(content)
    mode = path.stat().st_mode
    path.chmod(mode | stat.S_IXUSR | stat.S_IXGRP | stat.S_IXOTH)



def create_seed_active_voice_launcher():
    py = sys.executable
    repo = repo_dir()
    target = desktop_dir() / "Seed Active Voice.command"

    content = f"""#!/bin/zsh
cd "{repo}"
clear
echo "Starting Seed v2.1 Active Voice Listener..."
echo "This listener is explicit. No secret always-listening."
"{py}" seed_active_voice_daemon.py
echo ""
echo "Seed Active Voice closed."
read -k 1 "?Press any key to close..."
"""

    write_executable(target, content)
    return str(target)


def create_seed_voice_launcher():
    py = sys.executable
    repo = repo_dir()
    target = desktop_dir() / "Seed Voice Command.command"

    content = f'''#!/bin/zsh
cd "{repo}"
clear
echo "Starting Seed v2.0.0 Voice Command Bridge..."
echo "No always-listening. Explicit commands only."
"{py}" seed_voice_command_bridge.py
echo ""
echo "Seed Voice Command closed."
read -k 1 "?Press any key to close..."
'''

    write_executable(target, content)
    return str(target)


def create_seed_cli_launcher():
    py = sys.executable
    repo = repo_dir()
    target = desktop_dir() / "Seed CLI.command"

    content = f'''#!/bin/zsh
cd "{repo}"
clear
echo "Starting Seed CLI..."
"{py}" seed_cli.py
echo ""
echo "Seed CLI closed."
read -k 1 "?Press any key to close..."
'''

    write_executable(target, content)
    return str(target)


def create_seed_cockpit_launcher():
    py = sys.executable
    repo = repo_dir()
    target = desktop_dir() / "Seed Cockpit.command"

    content = f'''#!/bin/zsh
cd "{repo}"
clear
echo "Starting Seed CLI. Type /cockpit2 to launch cockpit."
"{py}" seed_cli.py
echo ""
echo "Seed Cockpit launcher closed."
read -k 1 "?Press any key to close..."
'''

    write_executable(target, content)
    return str(target)


def create_desktop_launchers():
    paths = [
        create_seed_voice_launcher(),
        create_seed_cli_launcher(),
        create_seed_cockpit_launcher()
    ]

    print("\n=== SEED DESKTOP LAUNCHERS CREATED ===")
    for path in paths:
        print(f"- {path}")

    print("\nUse:")
    print("- Double-click 'Seed Voice Command.command' for voice-command mode.")
    print("- Double-click 'Seed CLI.command' for normal Seed.")
    print("- Double-click 'Seed Cockpit.command' for Seed CLI and /cockpit2.")

    return paths


def show_launcher_status():
    names = [
        "Seed Voice Command.command",
        "Seed CLI.command",
        "Seed Cockpit.command"
    ]

    print("\n=== SEED LAUNCHER STATUS ===")
    for name in names:
        path = desktop_dir() / name
        print(f"- {name}: {'exists' if path.exists() else 'missing'}")


if __name__ == "__main__":
    create_desktop_launchers()
