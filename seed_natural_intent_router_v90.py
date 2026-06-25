import re

def norm(text):
    return " ".join(str(text or "").strip().lower().split())

def handle_natural_intent_v90(user_message):
    raw = str(user_message or "").strip()
    text = norm(raw)
    if not text or raw.startswith("/"):
        return None

    if text in {"v90 status", "garden status", "memory garden status"}:
        from seed_memory_garden_v90 import show_status
        show_status()
        return "handled"

    if text in {"review notes", "review organism notes", "memory garden review", "garden review"}:
        from seed_memory_garden_v90 import show_review
        show_review(False)
        return "handled"

    if text in {"digest notes", "digest organism notes", "garden digest", "clean notes"}:
        from seed_memory_garden_v90 import show_review
        show_review(True)
        return "handled"

    if text in {"show memories", "garden memories", "promoted memories"}:
        from seed_memory_garden_v90 import show_memories
        show_memories(20)
        return "handled"

    if text in {"promote latest", "promote latest note", "promote latest candidate"}:
        from seed_memory_garden_v90 import promote_latest_candidate
        print(promote_latest_candidate())
        return "handled"

    m = re.match(r"promote note\s+(.+)$", raw, flags=re.I)
    if m:
        from seed_memory_garden_v90 import promote_note
        print(promote_note(m.group(1).strip()))
        return "handled"

    m = re.match(r"archive note\s+(.+)$", raw, flags=re.I)
    if m:
        from seed_memory_garden_v90 import archive_note
        print(archive_note(m.group(1).strip()))
        return "handled"

    if text in {"day summary", "garden summary", "memory summary"}:
        from seed_memory_garden_v90 import daily_summary
        print(daily_summary()["summary"])
        return "handled"

    return None
