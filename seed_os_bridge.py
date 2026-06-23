import json
import os
from datetime import datetime


from seed_companion_os import (
    load_companion_os_state,
    save_companion_os_state,
    append_companion_os_event,
    append_companion_os_journal,
    add_companion_os_timeline_event,
    add_memory_garden_artifact,
    load_companion_os_events
)


try:
    from seed_event_bus import load_events as load_legacy_events
    LEGACY_EVENT_BUS_AVAILABLE = True
except Exception:
    LEGACY_EVENT_BUS_AVAILABLE = False


try:
    from seed_companion_growth import format_growth_status
    GROWTH_AVAILABLE = True
except Exception:
    GROWTH_AVAILABLE = False


try:
    from seed_presence import format_presence_state
    PRESENCE_AVAILABLE = True
except Exception:
    PRESENCE_AVAILABLE = False


try:
    from seed_evolution_foundry import format_foundry_status
    FOUNDRY_AVAILABLE = True
except Exception:
    FOUNDRY_AVAILABLE = False


try:
    from seed_local_control import format_local_control_status
    LOCAL_CONTROL_AVAILABLE = True
except Exception:
    LOCAL_CONTROL_AVAILABLE = False


try:
    from seed_skill_kernel import format_skill_map
    SKILL_AVAILABLE = True
except Exception:
    SKILL_AVAILABLE = False


try:
    from seed_open_source_dna import format_borrow_map
    DNA_AVAILABLE = True
except Exception:
    DNA_AVAILABLE = False


def now_timestamp():
    return datetime.now().isoformat(timespec="seconds")


def safe_call(function, fallback):
    try:
        return function()
    except Exception as error:
        return f"{fallback}: {error}"


def record_bridge_event(system, title, summary, importance=3, add_to_timeline=False):
    event = append_companion_os_event(
        event_type=f"{system}_bridge_event",
        title=title,
        details={
            "summary": summary
        },
        source="os_bridge",
        importance=importance
    )

    if add_to_timeline:
        add_companion_os_timeline_event(
            title=title,
            event_type=f"{system}_bridge_event",
            note=summary[:1000],
            importance=importance
        )

    return event


def bridge_manual_event():
    print("\n=== BRIDGE MANUAL EVENT INTO COMPANION OS ===")

    system = input("System/source: ").strip() or "manual"
    title = input("Title: ").strip()
    importance = input("Importance 1-5: ").strip()
    timeline = input("Also add to timeline? y/n: ").strip().lower()
    summary = input("Summary: ").strip()

    if not title:
        print("Title cannot be empty.")
        return

    try:
        importance_value = int(importance)
    except ValueError:
        importance_value = 3

    event = record_bridge_event(
        system=system,
        title=title,
        summary=summary,
        importance=importance_value,
        add_to_timeline=timeline == "y"
    )

    print(f"Bridge event recorded: {event.get('title')}")


def bridge_legacy_event_bus():
    if not LEGACY_EVENT_BUS_AVAILABLE:
        print("Legacy seed_event_bus not available.")
        return {
            "status": "missing_legacy_event_bus",
            "imported": 0
        }

    legacy_events = load_legacy_events()

    if not legacy_events:
        print("No legacy events to bridge.")
        return {
            "status": "no_events",
            "imported": 0
        }

    state = load_companion_os_state()
    bridged_ids = state.setdefault("bridge", {}).setdefault("legacy_event_ids", [])

    imported = 0

    for event in legacy_events:
        event_id = (
            f"{event.get('created_at')}|"
            f"{event.get('type')}|"
            f"{event.get('title')}"
        )

        if event_id in bridged_ids:
            continue

        append_companion_os_event(
            event_type=f"legacy_{event.get('type', 'event')}",
            title=event.get("title", "Legacy Seed event"),
            details={
                "legacy_event": event
            },
            source="legacy_event_bus",
            importance=event.get("importance", 3)
        )

        bridged_ids.append(event_id)
        imported += 1

    save_companion_os_state(state)

    append_companion_os_journal(
        "Legacy event bus bridged",
        f"Imported {imported} legacy events into Companion OS event stream."
    )

    print(f"Imported legacy events: {imported}")

    return {
        "status": "imported",
        "imported": imported
    }


def bridge_subsystem_snapshots():
    snapshots = []

    if GROWTH_AVAILABLE:
        snapshots.append({
            "system": "companion_growth",
            "content": safe_call(format_growth_status, "Companion Growth unavailable")
        })

    if PRESENCE_AVAILABLE:
        snapshots.append({
            "system": "presence",
            "content": safe_call(format_presence_state, "Presence unavailable")
        })

    if FOUNDRY_AVAILABLE:
        snapshots.append({
            "system": "evolution_foundry",
            "content": safe_call(format_foundry_status, "Foundry unavailable")
        })

    if LOCAL_CONTROL_AVAILABLE:
        snapshots.append({
            "system": "local_control",
            "content": safe_call(format_local_control_status, "Local Control unavailable")
        })

    if SKILL_AVAILABLE:
        snapshots.append({
            "system": "skill_os",
            "content": safe_call(format_skill_map, "Skill OS unavailable")
        })

    if DNA_AVAILABLE:
        snapshots.append({
            "system": "open_source_dna",
            "content": safe_call(format_borrow_map, "Open-source DNA unavailable")
        })

    state = load_companion_os_state()
    state.setdefault("bridge", {})
    state["bridge"]["last_subsystem_snapshot"] = {
        "created_at": now_timestamp(),
        "snapshots": snapshots
    }
    save_companion_os_state(state)

    append_companion_os_event(
        "subsystem_snapshots_bridged",
        "Subsystem snapshots bridged into Companion OS",
        {
            "snapshot_count": len(snapshots),
            "systems": [snapshot["system"] for snapshot in snapshots]
        },
        source="os_bridge",
        importance=4
    )

    append_companion_os_journal(
        "Subsystem snapshots bridged",
        json.dumps({
            "snapshot_count": len(snapshots),
            "systems": [snapshot["system"] for snapshot in snapshots]
        }, indent=2)
    )

    print(f"Subsystem snapshots bridged: {len(snapshots)}")

    return snapshots


def bridge_milestone(title, note, artifact_name=None, importance=4):
    add_companion_os_timeline_event(
        title=title,
        event_type="bridged_milestone",
        note=note,
        importance=importance
    )

    if artifact_name:
        add_memory_garden_artifact(
            name=artifact_name,
            meaning=note,
            artifact_type="bridged_milestone"
        )

    append_companion_os_event(
        "bridged_milestone",
        title,
        {"note": note, "artifact": artifact_name},
        source="os_bridge",
        importance=importance
    )


def bridge_milestone_interactive():
    print("\n=== BRIDGE MILESTONE ===")

    title = input("Milestone title: ").strip()
    note = input("Note: ").strip()
    artifact = input("Artifact name, optional: ").strip()
    importance = input("Importance 1-5: ").strip()

    if not title:
        print("Title required.")
        return

    try:
        importance_value = int(importance)
    except ValueError:
        importance_value = 4

    bridge_milestone(
        title=title,
        note=note,
        artifact_name=artifact or None,
        importance=importance_value
    )

    print("Milestone bridged.")


def format_bridge_status():
    state = load_companion_os_state()
    bridge = state.get("bridge", {})
    events = load_companion_os_events(limit=10)

    text = "=== COMPANION OS BRIDGE STATUS ===\n"
    text += f"Legacy event bus available: {LEGACY_EVENT_BUS_AVAILABLE}\n"
    text += f"Companion Growth available: {GROWTH_AVAILABLE}\n"
    text += f"Presence available: {PRESENCE_AVAILABLE}\n"
    text += f"Evolution Foundry available: {FOUNDRY_AVAILABLE}\n"
    text += f"Local Control available: {LOCAL_CONTROL_AVAILABLE}\n"
    text += f"Skill OS available: {SKILL_AVAILABLE}\n"
    text += f"Open-source DNA available: {DNA_AVAILABLE}\n"
    text += f"Bridged legacy event ids: {len(bridge.get('legacy_event_ids', []))}\n"

    last_snapshot = bridge.get("last_subsystem_snapshot")

    if last_snapshot:
        text += f"Last subsystem snapshot: {last_snapshot.get('created_at')}\n"
        text += f"Snapshot systems: {', '.join([s.get('system') for s in last_snapshot.get('snapshots', [])])}\n"
    else:
        text += "Last subsystem snapshot: none\n"

    text += "\nRecent Companion OS events:\n"
    for event in events:
        text += f"- {event.get('type')}: {event.get('title')}\n"

    return text


def show_bridge_status():
    print("\n" + format_bridge_status())


def get_bridge_context_for_prompt():
    return format_bridge_status() + """
Bridge rule:
The OS bridge connects old Seed systems into Companion OS timeline, events, traces, and world state.
Use bridge data to avoid treating Companion OS as disconnected from prior Seed history.
"""


if __name__ == "__main__":
    show_bridge_status()
