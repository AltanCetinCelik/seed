import json
import platform
import subprocess
import sys
import time
import urllib.request
import webbrowser
from datetime import datetime


try:
    from seed_config import (
        SEED_COCKPIT_URL,
        SEED_COCKPIT_OPEN_BROWSER_TIMEOUT
    )
except Exception:
    SEED_COCKPIT_URL = "http://127.0.0.1:8770"
    SEED_COCKPIT_OPEN_BROWSER_TIMEOUT = 8


try:
    from seed_trace_engine import append_trace
    TRACE_AVAILABLE = True
except Exception:
    TRACE_AVAILABLE = False


_COCKPIT_PROCESS = None


def now_timestamp():
    return datetime.now().isoformat(timespec="seconds")


def url_reachable(url=SEED_COCKPIT_URL, timeout=1.2):
    try:
        request = urllib.request.Request(url, headers={"User-Agent": "Seed"})
        with urllib.request.urlopen(request, timeout=timeout) as response:
            return 200 <= response.status < 500
    except Exception:
        return False


def start_cockpit_background():
    global _COCKPIT_PROCESS

    if url_reachable():
        return {
            "ok": True,
            "already_running": True,
            "message": "Cockpit server already running."
        }

    command = [sys.executable, "seed_cockpit_server_runner.py"]

    try:
        _COCKPIT_PROCESS = subprocess.Popen(
            command,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL
        )

        for _ in range(int(SEED_COCKPIT_OPEN_BROWSER_TIMEOUT) * 2):
            if url_reachable():
                return {
                    "ok": True,
                    "already_running": False,
                    "pid": _COCKPIT_PROCESS.pid,
                    "message": "Cockpit server started."
                }
            time.sleep(0.5)

        return {
            "ok": False,
            "pid": getattr(_COCKPIT_PROCESS, "pid", None),
            "message": "Tried to start cockpit server, but URL did not become reachable.",
            "url": SEED_COCKPIT_URL
        }

    except Exception as error:
        return {
            "ok": False,
            "message": f"Failed to start cockpit server: {error}",
            "url": SEED_COCKPIT_URL
        }


def open_url(url=SEED_COCKPIT_URL):
    try:
        if platform.system().lower() == "darwin":
            result = subprocess.run(["open", url], capture_output=True, text=True)
            return {
                "ok": result.returncode == 0,
                "method": "macos_open",
                "returncode": result.returncode,
                "stderr": result.stderr[-1000:],
                "url": url
            }

        ok = webbrowser.open(url)
        return {
            "ok": bool(ok),
            "method": "python_webbrowser",
            "url": url
        }

    except Exception as error:
        return {
            "ok": False,
            "message": str(error),
            "url": url
        }


def open_cockpit_browser(start_server=True):
    server_result = {
        "ok": url_reachable(),
        "already_running": url_reachable(),
        "message": "Cockpit server reachable." if url_reachable() else "Cockpit server not reachable."
    }

    if start_server and not server_result["ok"]:
        server_result = start_cockpit_background()

    browser_result = None
    if server_result.get("ok"):
        browser_result = open_url(SEED_COCKPIT_URL)

    ok = bool(server_result.get("ok")) and bool(browser_result and browser_result.get("ok"))

    result = {
        "created_at": now_timestamp(),
        "ok": ok,
        "url": SEED_COCKPIT_URL,
        "server": server_result,
        "browser": browser_result,
        "spoken_message": None
    }

    if ok:
        result["spoken_message"] = "Cockpit is open in your browser."
    elif not server_result.get("ok"):
        result["spoken_message"] = (
            "I could not open Cockpit because the Cockpit server did not start. "
            "Try opening Seed Cockpit.command or run /cockpit2 from Seed CLI."
        )
    else:
        result["spoken_message"] = (
            "The Cockpit server is running, but macOS did not open the browser. "
            f"Open {SEED_COCKPIT_URL} manually."
        )

    if TRACE_AVAILABLE:
        try:
            append_trace(
                trace_type="tool_trace",
                title="Cockpit browser open action",
                summary=json.dumps(result, indent=2)[:3000],
                sources=["cockpit_browser_action"],
                decision="opened" if ok else "failed",
                risk="local_control"
            )
        except Exception:
            pass

    return result


def show_open_cockpit_browser():
    result = open_cockpit_browser(start_server=True)
    print("\n=== OPEN COCKPIT BROWSER ===")
    print(json.dumps(result, indent=4))
    print("\nSeed:")
    print(result.get("spoken_message"))


def is_cockpit_open_request(text):
    lowered = (text or "").lower()
    cockpit_words = ["cockpit", "dashboard", "control panel", "web ui", "web browser"]
    open_words = ["open", "launch", "start", "show", "bring up"]
    return any(w in lowered for w in cockpit_words) and any(w in lowered for w in open_words)


def maybe_handle_cockpit_voice_action(text):
    if not is_cockpit_open_request(text):
        return None

    result = open_cockpit_browser(start_server=True)
    return result.get("spoken_message") or "I tried to open Cockpit."


if __name__ == "__main__":
    show_open_cockpit_browser()
