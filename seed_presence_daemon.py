import argparse
import time
from datetime import datetime


def run_loop(interval_seconds=300, force_first=False):
    from seed_presence import evaluate_presence_once

    print(f"Seed Presence Daemon started. interval={interval_seconds}s")

    first = True
    while True:
        result = evaluate_presence_once(force=(force_first and first))
        print(
            f"[{datetime.now().isoformat(timespec='seconds')}] "
            f"should_speak={result.get('should_speak')} "
            f"reason={result.get('reason')} "
            f"blocked_by={result.get('blocked_by')}"
        )
        first = False
        time.sleep(interval_seconds)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--interval", type=int, default=300)
    parser.add_argument("--once", action="store_true")
    parser.add_argument("--force", action="store_true")
    args = parser.parse_args()

    if args.once:
        from seed_presence import show_presence_tick
        show_presence_tick(force=args.force)
        return

    run_loop(interval_seconds=args.interval, force_first=args.force)


if __name__ == "__main__":
    main()
