import json
import time
from datetime import datetime


def now_timestamp():
    return datetime.now().isoformat(timespec="seconds")


def run_latency_probe():
    results = {}

    start = time.time()
    from seed_context_accelerator import get_fast_companion_context
    ctx = get_fast_companion_context("latency probe")
    results["fast_context_ms"] = int((time.time() - start) * 1000)
    results["fast_context_chars"] = len(ctx)

    start = time.time()
    from seed_chat_fastpath import fast_reply_for_message
    fast = fast_reply_for_message("what should we build next")
    results["fastpath_ms"] = int((time.time() - start) * 1000)
    results["fastpath_reply"] = fast

    start = time.time()
    from seed_brain import build_seed_prompt
    prompt = build_seed_prompt("what should we build next", [])
    results["prompt_build_ms"] = int((time.time() - start) * 1000)
    results["prompt_chars"] = len(prompt)

    return {
        "created_at": now_timestamp(),
        "version": "v5.2.0",
        "ok": (
            results["fast_context_ms"] < 800
            and results["prompt_build_ms"] < 1000
            and results["prompt_chars"] < 18000
        ),
        "results": results
    }


def show_latency_probe():
    report = run_latency_probe()
    print("\n=== SEED LATENCY PROBE ===")
    print(json.dumps(report, indent=4))


if __name__ == "__main__":
    show_latency_probe()
