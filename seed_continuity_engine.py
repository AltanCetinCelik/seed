import json
from datetime import datetime


from seed_companion_os import (
    load_companion_os_state,
    save_companion_os_state,
    append_companion_os_event,
    append_companion_os_journal,
    add_companion_os_timeline_event,
    add_memory_garden_artifact,
    calculate_companion_os_v2_score,
    load_companion_os_events
)


try:
    from seed_config import CONTINUITY_RECALL_LIMIT, CONTINUITY_PACK_TIMELINE_LIMIT
except Exception:
    CONTINUITY_RECALL_LIMIT = 12
    CONTINUITY_PACK_TIMELINE_LIMIT = 20


try:
    from seed_llm import ask_llm
    LLM_AVAILABLE = True
except Exception:
    LLM_AVAILABLE = False


try:
    from seed_memory import memories
    OLD_MEMORY_AVAILABLE = True
except Exception:
    memories = []
    OLD_MEMORY_AVAILABLE = False


try:
    from seed_memory_backend import search_layered_memory, add_layered_memory
    MEMORY_BACKEND_AVAILABLE = True
except Exception:
    MEMORY_BACKEND_AVAILABLE = False


try:
    from seed_document_registry import get_document_registry_context_for_prompt
    DOCUMENT_REGISTRY_AVAILABLE = True
except Exception:
    DOCUMENT_REGISTRY_AVAILABLE = False


try:
    from seed_trace_engine import append_trace
    TRACE_AVAILABLE = True
except Exception:
    TRACE_AVAILABLE = False


def now_timestamp():
    return datetime.now().isoformat(timespec="seconds")


def show_timeline(limit=CONTINUITY_PACK_TIMELINE_LIMIT):
    state = load_companion_os_state()
    timeline = state.get("continuity", {}).get("timeline", [])[-limit:]

    print("\n=== LIFE TIMELINE ===")

    if not timeline:
        print("No timeline events.")
        return

    for item in timeline:
        print(f"\n{item.get('created_at')} — {item.get('title')}")
        print(f"Type: {item.get('type')}")
        print(f"Importance: {item.get('importance')}")
        print(f"Note: {item.get('note')}")


def add_timeline_event_interactive():
    print("\n=== ADD LIFE TIMELINE EVENT ===")

    title = input("Title: ").strip()
    event_type = input("Type: ").strip()
    note = input("Note: ").strip()
    importance = input("Importance 1-5: ").strip()

    if title == "":
        print("Title cannot be empty.")
        return

    try:
        importance_value = int(importance)
    except ValueError:
        importance_value = 3

    add_companion_os_timeline_event(
        title=title,
        event_type=event_type or "general",
        note=note,
        importance=importance_value
    )

    if MEMORY_BACKEND_AVAILABLE:
        try:
            add_layered_memory(
                layer="timeline",
                content=f"{title}: {note}",
                source="continuity_engine",
                importance=importance_value,
                tags=[event_type or "general"]
            )
        except Exception:
            pass

    print("Timeline event added.")


def timeline_recall(query, limit=CONTINUITY_RECALL_LIMIT):
    state = load_companion_os_state()
    timeline = state.get("continuity", {}).get("timeline", [])

    query_words = [
        word.lower()
        for word in query.split()
        if len(word) >= 3
    ]

    results = []

    for item in timeline:
        haystack = json.dumps(item).lower()
        score = item.get("importance", 1)

        for word in query_words:
            if word in haystack:
                score += 3

        if score > item.get("importance", 1):
            results.append({
                "score": score,
                "item": item
            })

    results.sort(key=lambda result: result["score"], reverse=True)
    return results[:limit]


def recall_timeline_interactive():
    query = input("Timeline recall query: ").strip()

    if query == "":
        print("Query cannot be empty.")
        return

    results = timeline_recall(query)

    print("\n=== TIMELINE RECALL ===")

    if not results:
        print("No timeline matches.")
        return

    for result in results:
        item = result["item"]
        print(f"\nScore {result['score']} — {item.get('title')}")
        print(f"Type: {item.get('type')}")
        print(f"Created: {item.get('created_at')}")
        print(f"Note: {item.get('note')}")


def show_shared_history():
    state = load_companion_os_state()

    print("\n=== SHARED HISTORY ===")
    print(f"Title: {state['continuity'].get('shared_history_title')}")
    print(f"Mission: {state.get('mission')}")
    print(f"Truth: {state.get('truth')}")

    print("\nRelationship notes:")
    for note in state["continuity"].get("relationship_notes", []):
        print(f"- {note}")

    print("\nRecent timeline:")
    for item in state["continuity"].get("timeline", [])[-12:]:
        print(f"- {item.get('title')} [{item.get('type')}]")


def build_continuity_context(user_prompt=""):
    state = load_companion_os_state()
    score = calculate_companion_os_v2_score(save=False)
    events = load_companion_os_events(limit=15)

    old_memory_sample = memories[-20:] if OLD_MEMORY_AVAILABLE else []

    layered_results = []
    if MEMORY_BACKEND_AVAILABLE and user_prompt:
        try:
            layered_results = search_layered_memory(user_prompt, limit=8)
        except Exception:
            layered_results = []

    document_context = ""
    if DOCUMENT_REGISTRY_AVAILABLE:
        try:
            document_context = get_document_registry_context_for_prompt(user_prompt)
        except Exception as error:
            document_context = f"Document registry unavailable: {error}"

    return {
        "mission": state.get("mission"),
        "truth": state.get("truth"),
        "timeline": state["continuity"].get("timeline", [])[-CONTINUITY_PACK_TIMELINE_LIMIT:],
        "relationship_notes": state["continuity"].get("relationship_notes", []),
        "recall_packs": state["continuity"].get("recall_packs", [])[-5:],
        "growth_arcs": state["growth"].get("active_arcs", []),
        "quests": state["growth"].get("quests", []),
        "rituals": state["growth"].get("rituals", []),
        "world": state.get("world", {}),
        "v2_score": score,
        "events": events,
        "old_memory_sample": old_memory_sample,
        "layered_results": layered_results,
        "document_context": document_context
    }


def build_recall_pack(chat_state=None):
    context = build_continuity_context()

    if not LLM_AVAILABLE:
        response = json.dumps(context, indent=2)[:5000]
    else:
        prompt = f"""
You are Seed's Continuity Engine.

Build a recall pack for User and Seed.

Seed is not alive or conscious.
Seed is a local companion system that grows through memory, timeline, rituals, quests, world state, and approved actions.

Context:
{json.dumps(context, indent=2)}

Output:
1. Where we are
2. What changed recently
3. Important timeline/memory points
4. Active arcs
5. Active quests/rituals
6. What Seed should remember going forward
7. One concrete next action
"""

        response = ask_llm(prompt, task_type="memory", runtime_context=chat_state)

    state = load_companion_os_state()
    pack = {
        "created_at": now_timestamp(),
        "content": response
    }

    state["continuity"].setdefault("recall_packs", []).append(pack)
    save_companion_os_state(state)

    append_companion_os_journal("Continuity recall pack", response)

    append_companion_os_event(
        "recall_pack_generated",
        "Continuity recall pack generated",
        {
            "created_at": pack["created_at"]
        },
        source="continuity_engine",
        importance=4
    )

    if TRACE_AVAILABLE:
        try:
            append_trace(
                trace_type="memory_trace",
                title="Continuity recall pack generated",
                summary=response,
                sources=["continuity_engine", "companion_os_timeline", "memory_backend"],
                decision="generated",
                risk="low"
            )
        except Exception:
            pass

    print("\n=== CONTINUITY RECALL PACK ===")
    print(response)

    return response


def where_were_we(chat_state=None):
    context = build_continuity_context()

    if not LLM_AVAILABLE:
        response = "We are building Seed into User's local companion system, with continuity, memory, world, safety, and approved agency."
    else:
        prompt = f"""
Answer User: where were we?

Use only Seed continuity context.
Do not pretend consciousness.
Do not overclaim.

Context:
{json.dumps(context, indent=2)}

Answer with:
- what we were building
- why it mattered
- what changed recently
- next concrete move
"""

        response = ask_llm(prompt, task_type="chat", runtime_context=chat_state)

    print("\n" + response)
    return response


def what_changed(chat_state=None):
    context = build_continuity_context()

    if not LLM_AVAILABLE:
        response = json.dumps({
            "recent_timeline": context["timeline"][-8:],
            "events": context["events"][-8:]
        }, indent=2)
    else:
        prompt = f"""
Answer User: what changed recently in Seed?

Use timeline, events, recall packs, and v2 score.
Do not hallucinate.

Context:
{json.dumps(context, indent=2)}
"""

        response = ask_llm(prompt, task_type="debug", runtime_context=chat_state)

    print("\n" + response)
    return response


def answer_from_continuity(question, chat_state=None):
    context = build_continuity_context(question)

    if not LLM_AVAILABLE:
        return "Continuity answer unavailable because LLM is not available."

    prompt = f"""
You are Seed's Continuity Engine.

Answer this question using shared history, timeline, memory layers, documents, quests, rituals, and v2 state.

Question:
{question}

Context:
{json.dumps(context, indent=2)}

Rules:
- Seed is not alive or conscious.
- Be direct and specific.
- If context does not support an answer, say so.
- Tie answer to User and Seed's shared journey when relevant.
"""

    response = ask_llm(prompt, task_type="chat", runtime_context=chat_state)

    if TRACE_AVAILABLE:
        try:
            append_trace(
                trace_type="answer_trace",
                title="Continuity answer generated",
                summary=f"Question: {question}\n\nAnswer: {response[:1200]}",
                sources=["continuity_engine", "timeline", "memory_backend", "document_registry"],
                decision="answered",
                risk="low"
            )
        except Exception:
            pass

    return response


def continuity_answer_interactive(chat_state=None):
    question = input("Continuity question: ").strip()

    if question == "":
        print("Question cannot be empty.")
        return

    response = answer_from_continuity(question, chat_state=chat_state)
    print("\n" + response)


def show_recall_packs():
    state = load_companion_os_state()
    packs = state["continuity"].get("recall_packs", [])

    print("\n=== RECALL PACKS ===")

    if not packs:
        print("No recall packs yet.")
        return

    for pack in packs[-5:]:
        print(f"\n{pack.get('created_at')}")
        print(pack.get("content"))


def create_life_timeline_summary(chat_state=None):
    state = load_companion_os_state()

    if not LLM_AVAILABLE:
        summary = json.dumps(state["continuity"].get("timeline", []), indent=2)
    else:
        prompt = f"""
Create a Life Timeline summary for Seed and User.

Timeline:
{json.dumps(state["continuity"].get("timeline", []), indent=2)}

Relationship notes:
{json.dumps(state["continuity"].get("relationship_notes", []), indent=2)}

Output:
- origin
- major phases
- current phase
- unresolved threads
- what Seed should remember
"""

        summary = ask_llm(prompt, task_type="memory", runtime_context=chat_state)

    append_companion_os_journal("Life Timeline summary", summary)

    print("\n=== LIFE TIMELINE SUMMARY ===")
    print(summary)

    return summary


def get_continuity_context_for_prompt(user_prompt=""):
    context = build_continuity_context(user_prompt)

    text = "=== CONTINUITY ENGINE CONTEXT ===\n"
    text += f"Mission: {context.get('mission')}\n"
    text += f"Timeline events: {len(context.get('timeline', []))}\n"
    text += f"Recall packs: {len(context.get('recall_packs', []))}\n"
    text += f"Relationship notes: {len(context.get('relationship_notes', []))}\n"

    text += "\nRecent timeline:\n"
    for item in context.get("timeline", [])[-8:]:
        text += f"- {item.get('title')} [{item.get('type')}]: {item.get('note')}\n"

    text += "\nActive arcs:\n"
    for arc in context.get("growth_arcs", []):
        if arc.get("status") == "active":
            text += f"- {arc.get('title')}: {arc.get('success_condition')}\n"

    if context.get("layered_results"):
        text += "\nRelevant layered memories:\n"
        for result in context.get("layered_results", []):
            item = result.get("item", {})
            text += f"- {result.get('layer')} | score {result.get('score')}: {item.get('content')}\n"

    if context.get("document_context"):
        text += "\n" + context.get("document_context") + "\n"

    text += """
Continuity rule:
Use this to answer questions like where were we, what changed, why Seed exists, what are we becoming, and what should Seed remember.
Continuity is symbolic system state, not consciousness.
"""

    return text


if __name__ == "__main__":
    show_shared_history()
    show_timeline()
