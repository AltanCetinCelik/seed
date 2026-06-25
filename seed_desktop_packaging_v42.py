import json
import os
from datetime import datetime
from pathlib import Path


PACKAGING_FILE = Path("seed_desktop_packaging_v42.json")


def now_timestamp():
    return datetime.now().isoformat(timespec="seconds")


def create_launchers():
    scripts = Path("seed_launchers")
    scripts.mkdir(exist_ok=True)

    (scripts / "seed_terminal.sh").write_text("""#!/bin/zsh
cd ~/Desktop/seed_private
python seed_cli.py
""")

    (scripts / "seed_control_plane.sh").write_text("""#!/bin/zsh
cd ~/Desktop/seed_private
python seed_control_plane_server.py
""")

    (scripts / "seed_terminal_pro.sh").write_text("""#!/bin/zsh
cd ~/Desktop/seed_private
python seed_terminal_pro.py
""")

    for file in scripts.glob("*.sh"):
        os.chmod(file, 0o755)

    data = {
        "created_at": now_timestamp(),
        "version": "v45.0.0",
        "ok": True,
        "launchers": [str(p) for p in scripts.glob("*.sh")],
        "control_plane_url": "http://127.0.0.1:8790",
        "next_packaging": ["macOS LaunchAgent", "menu bar app", "desktop notification bridge"]
    }

    PACKAGING_FILE.write_text(json.dumps(data, indent=4))
    return data


def show_packaging():
    print("\n=== SEED DESKTOP PACKAGING v42 ===")
    print(json.dumps(create_launchers(), indent=4))


if __name__ == "__main__":
    show_packaging()
