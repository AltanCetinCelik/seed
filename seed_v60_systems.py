import json
from datetime import datetime
from pathlib import Path


STATE_FILE = Path("seed_v60_systems_state.json")


def now_timestamp():
    return datetime.now().isoformat(timespec="seconds")


def safe_card(title, fn):
    try:
        data = fn()
        ok = bool(data.get("ok", True)) if isinstance(data, dict) else True
        body = json.dumps(data, ensure_ascii=False)[:260]
        return {"title": title, "status": "ok" if ok else "warning", "body": body, "data": data}
    except Exception as error:
        return {"title": title, "status": "error", "body": str(error), "data": {"ok": False, "error": str(error)}}


def build_v60_state():
    cards = [
        safe_card("Model Manager", lambda: __import__("seed_model_manager_v60", fromlist=["build_pull_plan"]).build_pull_plan()),
        safe_card("Model Role Map", lambda: __import__("seed_model_manager_v60", fromlist=["build_role_map_from_benchmark"]).build_role_map_from_benchmark()),
        safe_card("Hermes/Moltbot/OpenClaw Fusion", lambda: __import__("seed_hermes_moltbot_fusion_v60", fromlist=["build_fusion_report"]).build_fusion_report()),
        safe_card("Memory Auto Extractor", lambda: __import__("seed_memory_auto_extractor_v60", fromlist=["extract_candidates"]).extract_candidates(limit=20)),
        safe_card("Presence 2.0 Rituals", lambda: __import__("seed_presence_rituals_v60", fromlist=["build_rituals"]).build_rituals()),
        safe_card("Daily Brief", lambda: __import__("seed_presence_rituals_v60", fromlist=["daily_brief"]).daily_brief()),
        safe_card("Natural Command Palette", lambda: __import__("seed_command_palette_v60", fromlist=["build_palette"]).build_palette()),
        safe_card("Aider Self-Improvement Loop", lambda: {"ok": True, "module": "seed_aider_self_improvement_v60"}),
    ]

    state = {
        "created_at": now_timestamp(),
        "version": "v60.0.0",
        "ok": all(c["status"] != "error" for c in cards),
        "cards": cards,
        "principle": "Natural conversation first; slash commands are hidden debug plumbing.",
    }

    STATE_FILE.write_text(json.dumps(state, indent=4))
    return state


def show_v60_status():
    data = build_v60_state()
    print("\n=== SEED v60 REAL INTELLIGENCE + UX FUSION ===")
    print(f"OK: {data['ok']}")
    for card in data["cards"]:
        print(f"- {card['title']}: {card['status']}")


if __name__ == "__main__":
    show_v60_status()
