import re

def norm(text):
    return " ".join(str(text or "").strip().lower().split())

def handle_natural_intent_v85(user_message):
    raw = str(user_message or "").strip()
    text = norm(raw)
    if not text or raw.startswith("/"):
        return None

    if any(p in text for p in ["v85 status", "real v1 prep status", "v1 prep status"]):
        from seed_v85_systems import show_v85_status
        show_v85_status()
        return "handled"

    if any(p in text for p in ["v85 self state", "real v1 state", "what version are you"]):
        from seed_self_state_v85 import show_self_state
        show_self_state()
        return "handled"

    if any(p in text for p in ["recovery check", "self repair check", "health check"]):
        from seed_recovery_v82 import show_recovery
        show_recovery()
        return "handled"

    if "mark green checkpoint" in text:
        from seed_recovery_v82 import mark_last_green
        print("\n=== SEED v82 GREEN CHECKPOINT ===")
        print(mark_last_green("natural_command_green_checkpoint"))
        return "handled"

    if "recovery notes" in text:
        from seed_recovery_v82 import write_rollback_notes
        print("\n=== SEED v82 RECOVERY NOTES ===")
        print(write_rollback_notes())
        return "handled"

    if any(p in text for p in ["runtime status", "one command runtime"]):
        from seed_runtime_v83 import show_runtime
        show_runtime()
        return "handled"

    if any(p in text for p in ["seed start", "start seed runtime", "start runtime"]):
        from seed_runtime_v83 import seed_start
        seed_start(run_gate=False)
        return "handled"

    if any(p in text for p in ["stop seed runtime", "stop runtime"]):
        from seed_runtime_v83 import stop_panel
        print(stop_panel())
        return "handled"

    if any(p in text for p in ["backup seed", "create backup", "backup project"]):
        from seed_privacy_backup_v84 import backup_project
        print("\n=== SEED v84 BACKUP ===")
        print(backup_project("natural"))
        return "handled"

    if any(p in text for p in ["list backups", "show backups"]):
        from seed_privacy_backup_v84 import list_backups
        import json
        print("\n=== SEED v84 BACKUPS ===")
        print(json.dumps(list_backups(), indent=4, ensure_ascii=False))
        return "handled"

    if any(p in text for p in ["export memory", "memory export"]):
        from seed_privacy_backup_v84 import export_memory
        print("\n=== SEED v84 MEMORY EXPORT ===")
        print(export_memory())
        return "handled"

    m = re.search(r"\bforget memory\s+(.+)$", raw, flags=re.I)
    if m:
        from seed_privacy_backup_v84 import forget_keyword
        print("\n=== SEED v84 FORGET MEMORY ===")
        print(forget_keyword(m.group(1).strip()))
        return "handled"

    if any(p in text for p in ["privacy status", "backup status"]):
        from seed_privacy_backup_v84 import show_privacy
        show_privacy()
        return "handled"

    if any(p in text for p in ["release candidate", "rc report"]):
        from seed_release_candidate_v85 import show_release_candidate
        show_release_candidate(full=False)
        return "handled"

    if any(p in text for p in ["full release candidate", "full rc report", "fresh install simulation"]):
        from seed_release_candidate_v85 import show_release_candidate
        show_release_candidate(full=True)
        return "handled"

    return None
