import inspect

try:
    import uvicorn
except Exception as error:
    print(f"uvicorn unavailable: {error}")
    raise SystemExit(1)

try:
    from seed_config import SEED_COCKPIT_HOST, SEED_COCKPIT_PORT
except Exception:
    SEED_COCKPIT_HOST = "127.0.0.1"
    SEED_COCKPIT_PORT = 8770


def find_cockpit_app():
    import seed_companion_cockpit as cockpit

    # Direct app object if module exposes one.
    if hasattr(cockpit, "app"):
        app = getattr(cockpit, "app")
        if app is not None:
            return app

    # Known factory name candidates.
    candidates = [
        "create_app",
        "create_cockpit_app",
        "create_companion_cockpit_app",
        "create_companion_cockpit",
        "build_app",
        "build_cockpit_app"
    ]

    for name in candidates:
        func = getattr(cockpit, name, None)
        if callable(func):
            try:
                sig = inspect.signature(func)
                if len(sig.parameters) == 0:
                    return func()
            except Exception:
                try:
                    return func()
                except Exception:
                    pass

    # Last-resort scan for a no-arg function that returns something app-like.
    for name in dir(cockpit):
        if "app" in name.lower() or "cockpit" in name.lower():
            func = getattr(cockpit, name, None)
            if callable(func):
                try:
                    sig = inspect.signature(func)
                    if len(sig.parameters) == 0:
                        maybe_app = func()
                        if maybe_app is not None:
                            return maybe_app
                except Exception:
                    pass

    raise RuntimeError("Could not find cockpit FastAPI app or app factory in seed_companion_cockpit.py")


if __name__ == "__main__":
    app = find_cockpit_app()
    print(f"Starting Seed Cockpit on http://{SEED_COCKPIT_HOST}:{SEED_COCKPIT_PORT}")
    uvicorn.run(app, host=SEED_COCKPIT_HOST, port=int(SEED_COCKPIT_PORT), log_level="warning")
