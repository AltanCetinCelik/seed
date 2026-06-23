import json
import os
from datetime import datetime


try:
    from seed_config import SEED_OS_MIGRATION_REPORT_FILE
except Exception:
    SEED_OS_MIGRATION_REPORT_FILE = "seed_os_migration_report.json"


from seed_companion_os import (
    load_companion_os_state,
    save_companion_os_state,
    append_companion_os_event,
    append_companion_os_journal,
    add_companion_os_timeline_event,
    add_memory_garden_artifact
)


def now_timestamp():
    return datetime.now().isoformat(timespec="seconds")


def safe_load_json(path, default=None):
    if default is None:
        default = {}

    try:
        with open(path, "r") as file:
            return json.load(file)
    except FileNotFoundError:
        return default
    except json.JSONDecodeError:
        return default


def safe_read_text(path):
    try:
        with open(path, "r") as file:
            return file.read()
    except FileNotFoundError:
        return ""
    except OSError:
        return ""


def save_report(report):
    with open(SEED_OS_MIGRATION_REPORT_FILE, "w") as file:
        json.dump(report, file, indent=4)


def load_report():
    return safe_load_json(SEED_OS_MIGRATION_REPORT_FILE, {
        "created_at": now_timestamp(),
        "runs": []
    })


def migration_preview():
    files = {
        "seed_memory.json": os.path.exists("seed_memory.json"),
        "seed_journal.txt": os.path.exists("seed_journal.txt"),
        "seed_companion_growth.json": os.path.exists("seed_companion_growth.json"),
        "seed_presence_state.json": os.path.exists("seed_presence_state.json"),
        "seed_evolution_foundry.json": os.path.exists("seed_evolution_foundry.json"),
        "seed_local_actions.jsonl": os.path.exists("seed_local_actions.jsonl"),
        "seed_code_map.json": os.path.exists("seed_code_map.json"),
        "seed_research/open_source_dna.json": os.path.exists("seed_research/open_source_dna.json")
    }

    return files


def show_migration_preview():
    print("\n=== COMPANION OS MIGRATION PREVIEW ===")

    files = migration_preview()

    for path, exists in files.items():
        print(f"{'YES' if exists else 'NO '} — {path}")


def state_has_import(state, import_key):
    return import_key in state.setdefault("migrations", {}).get("completed", [])


def mark_import_done(state, import_key, details=None):
    if details is None:
        details = {}

    state.setdefault("migrations", {})
    state["migrations"].setdefault("completed", [])
    state["migrations"].setdefault("details", {})

    if import_key not in state["migrations"]["completed"]:
        state["migrations"]["completed"].append(import_key)

    state["migrations"]["details"][import_key] = {
        "imported_at": now_timestamp(),
        "details": details
    }


def import_seed_memory():
    state = load_companion_os_state()

    if state_has_import(state, "seed_memory_json"):
        return {"source": "seed_memory.json", "status": "skipped_already_imported"}

    old_memories = safe_load_json("seed_memory.json", [])

    if not isinstance(old_memories, list):
        old_memories = []

    layer_counts = {}

    for memory in old_memories:
        memory_type = memory.get("type", "general")
        content = memory.get("content", "")
        importance = memory.get("importance", 3)
        created_at = memory.get("created_at", now_timestamp())

        if memory_type in ["technical_progress", "mistake"]:
            layer = "project"
        elif memory_type in ["reflection", "personal_rule"]:
            layer = "identity_mirror"
        elif memory_type in ["seed_identity", "seed_boundary"]:
            layer = "core"
        elif memory_type in ["job_goal"]:
            layer = "project"
        else:
            layer = "relationship"

        state["memory"]["layers"].setdefault(layer, [])
        state["memory"]["layers"][layer].append({
            "created_at": created_at,
            "source": "seed_memory.json",
            "old_type": memory_type,
            "content": content,
            "importance": importance
        })

        layer_counts[layer] = layer_counts.get(layer, 0) + 1

    mark_import_done(state, "seed_memory_json", {
        "imported_count": len(old_memories),
        "layer_counts": layer_counts
    })

    save_companion_os_state(state)

    append_companion_os_event(
        "migration_memory_imported",
        "Old Seed memory imported into Companion OS layers",
        {
            "count": len(old_memories),
            "layer_counts": layer_counts
        },
        source="os_migrations",
        importance=5
    )

    return {
        "source": "seed_memory.json",
        "status": "imported",
        "count": len(old_memories),
        "layer_counts": layer_counts
    }


def import_seed_journal():
    state = load_companion_os_state()

    if state_has_import(state, "seed_journal_txt"):
        return {"source": "seed_journal.txt", "status": "skipped_already_imported"}

    text = safe_read_text("seed_journal.txt")
    lines = [line.strip() for line in text.splitlines() if line.strip()]

    imported_count = 0

    if text.strip():
        state["memory"]["layers"].setdefault("timeline", [])
        state["memory"]["layers"]["timeline"].append({
            "created_at": now_timestamp(),
            "source": "seed_journal.txt",
            "content": text[-12000:],
            "importance": 4
        })

        add_companion_os_timeline_event(
            title="Old Seed journal imported",
            event_type="journal_import",
            note="Seed's previous journal was imported into Companion OS memory.",
            importance=4
        )

        imported_count = len(lines)

    mark_import_done(state, "seed_journal_txt", {
        "line_count": imported_count
    })

    save_companion_os_state(state)

    append_companion_os_event(
        "migration_journal_imported",
        "Old Seed journal imported",
        {"line_count": imported_count},
        source="os_migrations",
        importance=4
    )

    return {
        "source": "seed_journal.txt",
        "status": "imported",
        "line_count": imported_count
    }


def import_companion_growth():
    state = load_companion_os_state()

    if state_has_import(state, "seed_companion_growth_json"):
        return {"source": "seed_companion_growth.json", "status": "skipped_already_imported"}

    growth = safe_load_json("seed_companion_growth.json", {})

    if not growth:
        return {"source": "seed_companion_growth.json", "status": "missing"}

    imported = {
        "arcs": 0,
        "quests": 0,
        "rituals": 0,
        "milestones": 0
    }

    for arc in growth.get("growth_arcs", []):
        title = arc.get("title", "")

        if title and title not in [existing.get("title") for existing in state["growth"]["active_arcs"]]:
            state["growth"]["active_arcs"].append(arc)
            imported["arcs"] += 1

    for quest in growth.get("quests", []):
        title = quest.get("title", "")

        if title and title not in [existing.get("title") for existing in state["growth"]["quests"]]:
            state["growth"]["quests"].append(quest)
            imported["quests"] += 1

    for ritual in growth.get("rituals", []):
        title = ritual.get("title", "")

        if title and title not in [existing.get("title") for existing in state["growth"]["rituals"]]:
            state["growth"]["rituals"].append(ritual)
            imported["rituals"] += 1

    for milestone in growth.get("milestones", [])[-20:]:
        add_companion_os_timeline_event(
            title=milestone.get("title", "Companion growth milestone"),
            event_type=milestone.get("type", "growth_milestone"),
            note=milestone.get("note", ""),
            importance=milestone.get("importance", 3)
        )
        imported["milestones"] += 1

    if growth.get("why_seed_exists"):
        state["continuity"]["relationship_notes"].append(growth.get("why_seed_exists"))

    if growth.get("companion_truth"):
        state["continuity"]["relationship_notes"].append(growth.get("companion_truth"))

    old_garden = growth.get("memory_garden", {})
    garden = state["world"]["memory_garden"]

    for key in ["seeds", "trees", "stones", "lights"]:
        garden[key] = max(garden.get(key, 0), old_garden.get(key, 0))

    for artifact in old_garden.get("artifacts", []):
        name = artifact.get("name", "")

        if name and name not in [existing.get("name") for existing in garden.get("artifacts", [])]:
            garden["artifacts"].append(artifact)

    mark_import_done(state, "seed_companion_growth_json", imported)
    save_companion_os_state(state)

    append_companion_os_event(
        "migration_growth_imported",
        "Companion Growth OS imported",
        imported,
        source="os_migrations",
        importance=5
    )

    return {
        "source": "seed_companion_growth.json",
        "status": "imported",
        "details": imported
    }


def import_presence_state():
    state = load_companion_os_state()

    if state_has_import(state, "seed_presence_state_json"):
        return {"source": "seed_presence_state.json", "status": "skipped_already_imported"}

    presence = safe_load_json("seed_presence_state.json", {})

    if not presence:
        return {"source": "seed_presence_state.json", "status": "missing"}

    state["presence"]["mode"] = presence.get("presence_mode", state["presence"]["mode"])
    state["presence"]["attention"] = presence.get("attention", state["presence"]["attention"])
    state["presence"]["energy"] = presence.get("energy", state["presence"].get("energy", 70))
    state["presence"]["room"] = presence.get("current_room", state["presence"]["room"])

    mark_import_done(state, "seed_presence_state_json", {
        "mode": state["presence"]["mode"],
        "attention": state["presence"]["attention"]
    })

    save_companion_os_state(state)

    append_companion_os_event(
        "migration_presence_imported",
        "Presence OS state imported",
        {
            "mode": state["presence"]["mode"],
            "attention": state["presence"]["attention"]
        },
        source="os_migrations",
        importance=3
    )

    return {
        "source": "seed_presence_state.json",
        "status": "imported"
    }


def import_foundry_state():
    state = load_companion_os_state()

    if state_has_import(state, "seed_evolution_foundry_json"):
        return {"source": "seed_evolution_foundry.json", "status": "skipped_already_imported"}

    foundry = safe_load_json("seed_evolution_foundry.json", {})

    if not foundry:
        return {"source": "seed_evolution_foundry.json", "status": "missing"}

    proposals = foundry.get("proposals", [])

    state["self_improvement"].setdefault("foundry_proposals", [])
    state["self_improvement"]["foundry_proposals"].extend(proposals[-20:])

    if foundry.get("active_mission"):
        state["continuity"]["relationship_notes"].append(foundry.get("active_mission"))

    mark_import_done(state, "seed_evolution_foundry_json", {
        "proposal_count": len(proposals)
    })

    save_companion_os_state(state)

    append_companion_os_event(
        "migration_foundry_imported",
        "Evolution Foundry state imported",
        {"proposal_count": len(proposals)},
        source="os_migrations",
        importance=4
    )

    return {
        "source": "seed_evolution_foundry.json",
        "status": "imported",
        "proposal_count": len(proposals)
    }


def import_local_actions():
    state = load_companion_os_state()

    if state_has_import(state, "seed_local_actions_jsonl"):
        return {"source": "seed_local_actions.jsonl", "status": "skipped_already_imported"}

    path = "seed_local_actions.jsonl"

    if not os.path.exists(path):
        return {"source": path, "status": "missing"}

    actions = []

    with open(path, "r") as file:
        for line in file:
            try:
                actions.append(json.loads(line))
            except json.JSONDecodeError:
                continue

    for action in actions[-50:]:
        state["trust"]["permission_traces"].append({
            "created_at": action.get("created_at", now_timestamp()),
            "action": action.get("command") or action.get("app") or action.get("path") or action.get("type"),
            "decision": "historical_local_action",
            "reason": "Imported from Local Control OS action history.",
            "risk": "historical"
        })

    mark_import_done(state, "seed_local_actions_jsonl", {
        "action_count": len(actions)
    })

    save_companion_os_state(state)

    append_companion_os_event(
        "migration_local_actions_imported",
        "Local Control action history imported",
        {"action_count": len(actions)},
        source="os_migrations",
        importance=4
    )

    return {
        "source": path,
        "status": "imported",
        "action_count": len(actions)
    }


def import_code_map():
    state = load_companion_os_state()

    if state_has_import(state, "seed_code_map_json"):
        return {"source": "seed_code_map.json", "status": "skipped_already_imported"}

    code_map = safe_load_json("seed_code_map.json", {})

    if not code_map:
        return {"source": "seed_code_map.json", "status": "missing"}

    state["self_improvement"]["dependency_graph"] = code_map

    mark_import_done(state, "seed_code_map_json", {
        "file_count": code_map.get("file_count", 0)
    })

    save_companion_os_state(state)

    append_companion_os_event(
        "migration_code_map_imported",
        "Code map imported into Companion OS",
        {"file_count": code_map.get("file_count", 0)},
        source="os_migrations",
        importance=4
    )

    return {
        "source": "seed_code_map.json",
        "status": "imported",
        "file_count": code_map.get("file_count", 0)
    }


def import_open_source_dna():
    state = load_companion_os_state()

    if state_has_import(state, "open_source_dna_json"):
        return {"source": "seed_research/open_source_dna.json", "status": "skipped_already_imported"}

    dna = safe_load_json("seed_research/open_source_dna.json", {})

    if not dna:
        return {"source": "seed_research/open_source_dna.json", "status": "missing"}

    repo_count = 0

    if isinstance(dna, dict):
        repos = dna.get("repos", [])
        repo_count = len(repos) if isinstance(repos, list) else 0

    state["repo_dna_imported"] = {
        "imported_at": now_timestamp(),
        "repo_count": repo_count
    }

    mark_import_done(state, "open_source_dna_json", {
        "repo_count": repo_count
    })

    save_companion_os_state(state)

    append_companion_os_event(
        "migration_dna_imported",
        "Open-source DNA data imported",
        {"repo_count": repo_count},
        source="os_migrations",
        importance=4
    )

    return {
        "source": "seed_research/open_source_dna.json",
        "status": "imported",
        "repo_count": repo_count
    }


def migrate_all():
    print("\n=== COMPANION OS FULL MIGRATION ===")

    report = load_report()

    run = {
        "created_at": now_timestamp(),
        "results": []
    }

    migration_functions = [
        import_seed_memory,
        import_seed_journal,
        import_companion_growth,
        import_presence_state,
        import_foundry_state,
        import_local_actions,
        import_code_map,
        import_open_source_dna
    ]

    for function in migration_functions:
        try:
            result = function()
        except Exception as error:
            result = {
                "source": function.__name__,
                "status": "error",
                "error": str(error)
            }

        run["results"].append(result)
        print(f"{result.get('source')}: {result.get('status')}")

    report.setdefault("runs", []).append(run)
    save_report(report)

    append_companion_os_journal(
        "Companion OS migration run",
        json.dumps(run, indent=2)
    )

    append_companion_os_event(
        "os_migration_completed",
        "Companion OS migration completed",
        {"result_count": len(run["results"])},
        source="os_migrations",
        importance=5
    )

    print(f"\nMigration report saved: {SEED_OS_MIGRATION_REPORT_FILE}")

    return run


def show_migration_report():
    report = load_report()

    print("\n=== OS MIGRATION REPORT ===")

    runs = report.get("runs", [])

    if not runs:
        print("No migration runs yet.")
        return

    for run in runs[-5:]:
        print(f"\nRun: {run.get('created_at')}")

        for result in run.get("results", []):
            print(f"- {result.get('source')}: {result.get('status')}")


if __name__ == "__main__":
    show_migration_preview()
