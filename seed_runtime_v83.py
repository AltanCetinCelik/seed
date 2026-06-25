import json
import os
import signal
import subprocess
import sys
import time
from datetime import datetime
from pathlib import Path

STATE_FILE = Path("seed_runtime_v83_state.json")
LOG_FILE = Path("seed_runtime_v83_panel.log")
PID_FILE = Path("seed_runtime_v83_panel.pid")

def now():
    return datetime.now().isoformat(timespec="seconds")

def pid_alive(pid):
    try:
        os.kill(int(pid), 0)
        return True
    except Exception:
        return False

def runtime_status():
    pid = None
    if PID_FILE.exists():
        try:
            pid = int(PID_FILE.read_text().strip())
        except Exception:
            pid = None
    panel_alive = bool(pid and pid_alive(pid))
    data = {
        "created_at": now(),
        "version": "v83.0.0",
        "ok": True,
        "panel_pid": pid,
        "panel_alive": panel_alive,
        "panel_url": "http://127.0.0.1:8797",
        "script": "./seed",
        "fallback_script": "./seed_start.sh",
        "log_file": str(LOG_FILE),
    }
    STATE_FILE.write_text(json.dumps(data, indent=4))
    return data

def run_quick_gate():
    for gate in ["seed_v85_gate.py", "seed_v81_gate.py", "seed_v75_gate.py"]:
        if Path(gate).exists():
            try:
                proc = subprocess.run([sys.executable, gate], capture_output=True, text=True, timeout=120)
                print(proc.stdout[-4000:])
                if proc.returncode != 0:
                    print(proc.stderr[-4000:])
                    return False
                return True
            except Exception as e:
                print(f"Gate failed: {e}")
                return False
    print("No gate found.")
    return False

def start_panel(open_browser=True):
    if PID_FILE.exists():
        try:
            old_pid = int(PID_FILE.read_text().strip())
            if pid_alive(old_pid):
                print(f"Panel already running: http://127.0.0.1:8797 pid={old_pid}")
                return {"ok": True, "pid": old_pid, "already_running": True}
        except Exception:
            pass

    panel_file = "seed_panel_v77.py" if Path("seed_panel_v77.py").exists() else "seed_embodied_companion_server_v74.py"
    log = LOG_FILE.open("a")
    proc = subprocess.Popen([sys.executable, panel_file], stdout=log, stderr=log)
    PID_FILE.write_text(str(proc.pid))
    time.sleep(1)
    if open_browser:
        try:
            subprocess.Popen(["open", "http://127.0.0.1:8797"])
        except Exception:
            pass
    print(f"Started Seed panel pid={proc.pid}")
    print("Open: http://127.0.0.1:8797")
    return {"ok": True, "pid": proc.pid, "url": "http://127.0.0.1:8797"}

def stop_panel():
    if not PID_FILE.exists():
        print("No panel PID file.")
        return {"ok": True, "stopped": False}
    try:
        pid = int(PID_FILE.read_text().strip())
        if pid_alive(pid):
            os.kill(pid, signal.SIGTERM)
            time.sleep(0.5)
        PID_FILE.unlink(missing_ok=True)
        print(f"Stopped panel pid={pid}")
        return {"ok": True, "stopped": True, "pid": pid}
    except Exception as e:
        print(f"Stop failed: {e}")
        return {"ok": False, "error": str(e)}

def seed_start(run_gate=False):
    print("\n=== SEED v83 ONE-COMMAND RUNTIME ===")
    print("Starting Seed local companion runtime...")
    if run_gate:
        print("Running quick gate first...")
        run_quick_gate()
    return start_panel(open_browser=True)

def install_seed_script():
    script = Path("seed")
    script.write_text("""#!/usr/bin/env bash
cd "$(dirname "$0")"
python seed_runtime_v83.py start "$@"
""")
    script.chmod(0o755)
    fallback = Path("seed_start.sh")
    fallback.write_text("""#!/usr/bin/env bash
cd "$(dirname "$0")"
python seed_runtime_v83.py start "$@"
""")
    fallback.chmod(0o755)
    return {"ok": True, "script": str(script), "fallback": str(fallback)}

def show_runtime():
    print("\n=== SEED v83 ONE-COMMAND RUNTIME ===")
    print(json.dumps(runtime_status(), indent=4))
    print("\nCommands:")
    print("./seed")
    print("python seed_runtime_v83.py start")
    print("python seed_runtime_v83.py stop")
    print("python seed_runtime_v83.py status")

if __name__ == "__main__":
    arg = sys.argv[1] if len(sys.argv) > 1 else "status"
    if arg == "start":
        seed_start(run_gate="--gate" in sys.argv)
    elif arg == "stop":
        stop_panel()
    elif arg == "install-script":
        print(install_seed_script())
    else:
        show_runtime()
