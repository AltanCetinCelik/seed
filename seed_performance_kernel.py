import json
import time
from datetime import datetime


def now_timestamp():
    return datetime.now().isoformat(timespec="seconds")


def performance_status():
    started = time.time()

    from seed_context_accelerator import get_fast_companion_context
    context_start = time.time()
    ctx = get_fast_companion_context("performance check")
    context_ms = int((time.time() - context_start) * 1000)

    html_chars = None
    html_ms = None
    try:
        from seed_control_plane_server import render_home
        html_start = time.time()
        html = render_home()
        html_ms = int((time.time() - html_start) * 1000)
        html_chars = len(html)
    except Exception as error:
        html_chars = f"error: {error}"

    total_ms = int((time.time() - started) * 1000)

    return {
        "created_at": now_timestamp(),
        "version": "v5.1.0",
        "ok": True,
        "fast_context_chars": len(ctx),
        "fast_context_ms": context_ms,
        "control_plane_html_chars": html_chars,
        "control_plane_render_ms": html_ms,
        "total_ms": total_ms,
        "targets": {
            "fast_context_chars_under": 12000,
            "fast_context_ms_under": 500,
            "control_plane_html_chars_under": 120000
        }
    }


def show_performance_status():
    print("\n=== SEED PERFORMANCE KERNEL ===")
    print(json.dumps(performance_status(), indent=4))


if __name__ == "__main__":
    show_performance_status()
