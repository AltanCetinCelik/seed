import requests
from seed_memory import memories
from seed_journal import get_recent_journal_entries
from seed_memory_tools import expand_query
from seed_config import (
    OLLAMA_URL,
    MODEL_NAME,
    MEMORY_SEARCH_LIMIT,
    SESSION_HISTORY_LIMIT
)
from seed_project_inspector import get_project_context_for_prompt
from seed_personality import get_personality_context
from seed_llm import ask_llm
from seed_semantic_memory import format_semantic_context_for_prompt
from seed_open_source_dna import get_dna_context_for_prompt
from seed_skill_kernel import get_skill_context_for_prompt
from seed_world import get_world_context_for_prompt
from seed_companion_growth import get_companion_growth_context_for_prompt
from seed_presence import get_presence_context_for_prompt
from seed_computer_awareness import get_computer_context_for_prompt
from seed_local_control import get_local_control_context_for_prompt
from seed_evolution_foundry import get_foundry_context_for_prompt

try:
    from seed_companion_os_context import get_full_companion_os_context_for_prompt
    COMPANION_OS_ALPHA_AVAILABLE = True
except Exception:
    COMPANION_OS_ALPHA_AVAILABLE = False

    def get_full_companion_os_context_for_prompt(user_prompt=""):
        return "Companion OS Alpha context unavailable."

def clean_words(text):
    stop_words = [
        "a", "an", "the",
        "and", "or", "but",
        "is", "are", "was", "were",
        "am", "be", "been", "being",
        "i", "you", "he", "she", "it", "we", "they",
        "me", "him", "her", "us", "them",
        "my", "your", "his", "its", "our", "their",
        "this", "that", "these", "those",
        "what", "when", "where", "why", "how",
        "do", "does", "did", "done",
        "with", "without", "for", "to", "from", "of", "in", "on", "at", "by",
        "about", "as", "into", "through", "during",
        "so", "just", "really", "very",
        "have", "has", "had",
        "can", "could", "should", "would",
        "tell", "show", "give",
        "please"
    ]

    punctuation = ".,!?;:()[]{}<>\"'`~@#$%^&*_+=|\\/"

    cleaned_text = text.lower()

    for mark in punctuation:
        cleaned_text = cleaned_text.replace(mark, " ")

    raw_words = cleaned_text.split()
    useful_words = []

    for word in raw_words:
        word = word.strip()

        if word == "":
            continue

        if word in stop_words:
            continue

        if len(word) < 3:
            continue

        if word not in useful_words:
            useful_words.append(word)

    return useful_words

def score_memory(memory, user_prompt):
    prompt_words = clean_words(user_prompt)
    expanded_words = expand_query(user_prompt)

    for word in expanded_words:
        cleaned_alias_words = clean_words(word)

        for cleaned_word in cleaned_alias_words:
            if cleaned_word not in prompt_words:
                prompt_words.append(cleaned_word)

    memory_type = memory.get("type", "")
    content = memory.get("content", "")
    created_at = memory.get("created_at", "")

    memory_text = f"{memory_type} {content} {created_at}".lower()
    memory_words = clean_words(memory_text)

    user_prompt_lower = user_prompt.lower()

    keyword_score = 0

    for word in prompt_words:
        if word in memory_words:
            keyword_score += 10

    phrase_score = 0

    useful_query_words = clean_words(user_prompt)

    if len(useful_query_words) >= 2:
        useful_query_phrase = " ".join(useful_query_words)

        if useful_query_phrase in memory_text:
            phrase_score += 25

    type_score = 0

    if memory_type.lower() in user_prompt_lower:
        type_score += 15

    importance_score = memory.get("importance", 0)

    total_score = keyword_score + phrase_score + type_score + importance_score

    return {
        "total_score": total_score,
        "keyword_score": keyword_score,
        "phrase_score": phrase_score,
        "type_score": type_score,
        "importance_score": importance_score,
        "memory": memory
    }



def format_relevant_memories(user_prompt, limit=MEMORY_SEARCH_LIMIT):
    scored_memories = []

    for memory in memories:
        result = score_memory(memory, user_prompt)
        scored_memories.append(result)

    direct_matches = []

    for result in scored_memories:
        if (
            result["keyword_score"] > 0
            or result["phrase_score"] > 0
            or result["type_score"] > 0
        ):
            direct_matches.append(result)

    if direct_matches:
        direct_matches.sort(
            key=lambda result: result["total_score"],
            reverse=True
        )

        selected_memories = direct_matches[:limit]

        memory_text = "Direct memory matches found:\n\n"

        for number, result in enumerate(selected_memories, start=1):
            memory = result["memory"]

            memory_text += f"{number}. [{memory.get('type', 'unknown')}]\n"
            memory_text += f"Content: {memory.get('content', '')}\n"
            memory_text += f"Importance: {memory.get('importance', 0)}\n"
            memory_text += f"Created: {memory.get('created_at', 'unknown time')}\n"
            memory_text += f"Keyword score: {result['keyword_score']}\n"
            memory_text += f"Phrase score: {result['phrase_score']}\n"
            memory_text += f"Type score: {result['type_score']}\n"
            memory_text += f"Importance score: {result['importance_score']}\n"
            memory_text += f"Total score: {result['total_score']}\n"
            memory_text += "-" * 40 + "\n"

        return memory_text

    scored_memories.sort(
        key=lambda result: result["total_score"],
        reverse=True
    )

    fallback_memories = scored_memories[:limit]

    memory_text = "No direct keyword, phrase, or type matches found. Showing important memories instead:\n\n"

    for number, result in enumerate(fallback_memories, start=1):
        memory = result["memory"]

        memory_text += f"{number}. [{memory.get('type', 'unknown')}]\n"
        memory_text += f"Content: {memory.get('content', '')}\n"
        memory_text += f"Importance: {memory.get('importance', 0)}\n"
        memory_text += f"Created: {memory.get('created_at', 'unknown time')}\n"
        memory_text += f"Keyword score: {result['keyword_score']}\n"
        memory_text += f"Phrase score: {result['phrase_score']}\n"
        memory_text += f"Type score: {result['type_score']}\n"
        memory_text += f"Importance score: {result['importance_score']}\n"
        memory_text += f"Total score: {result['total_score']}\n"
        memory_text += "-" * 40 + "\n"

    return memory_text

def read_file(filename):
    try:
        with open(filename, "r") as file:
            return file.read()
    except FileNotFoundError:
        return ""

def format_session_history(session_history):
    if not session_history:
        return "No active session history yet."

    history_text = ""

    for message in session_history[-6:]:
        role = message["role"]
        content = message["content"]

        history_text += f"{role}: {content}\n"

    return history_text

def build_seed_prompt(user_prompt, session_history=None):
    if session_history is None:
        session_history = []
    seed_core = read_file("Seed_Core.md")
    memory_rules = read_file("memory_rules.md")
    relevant_memories = format_relevant_memories(user_prompt)
    session_text = format_session_history(session_history)
    recent_journal = get_recent_journal_entries()
    project_context = get_project_context_for_prompt(user_prompt)
    personality_context = get_personality_context()
    semantic_memory_context = format_semantic_context_for_prompt(user_prompt)
    dna_context = get_dna_context_for_prompt(user_prompt)
    skill_context = get_skill_context_for_prompt(user_prompt)
    world_context = get_world_context_for_prompt()
    companion_growth_context = get_companion_growth_context_for_prompt(user_prompt)
    presence_context = get_presence_context_for_prompt()
    computer_context = get_computer_context_for_prompt()
    local_control_context = get_local_control_context_for_prompt()
    foundry_context = get_foundry_context_for_prompt(user_prompt)
    companion_os_alpha_context = get_full_companion_os_context_for_prompt(user_prompt)
    full_prompt = f"""
You are Seed.

Use the following Seed Core as your identity and behavior guide:

{seed_core}

Live project context:
{project_context}

Personality context:
{personality_context}

Recent journal entries:
{recent_journal}

Semantic memory context:
{semantic_memory_context}

Use these memory rules as system boundaries:

{memory_rules}

Presence context:
{presence_context}

Computer context:
{computer_context}

Local Control context:
{local_control_context}

Companion Growth OS context:
{companion_growth_context}

Evolution Foundry context:
{foundry_context}

Open-source DNA context:
{dna_context}

Relevant stored memories available to Seed:
{relevant_memories}

Skill OS context:
{skill_context}

Companion OS Alpha context:
{companion_os_alpha_context}

Active session history:
{session_text}

Seed World context:
{world_context}

Important behavior rules:
- Do not pretend you have abilities that are not built yet.
- Relevant stored memories are long-term memories from seed_memory.json.
- Current chat session history is short-term memory for this active chat only.
- You may use Current chat session history to answer follow-up questions in the same chat.
- If information appears only in Current chat session history, say "you said earlier in this chat", not "I remember permanently".
- Do not ask to save something every time the user says a temporary test phrase.
- Do not suggest saving temporary test phrases, random examples, casual comments, or throwaway details.
- Only suggest saving something to long-term memory if the user explicitly asks to save it, or if it is clearly important project progress, a Seed rule, a Seed identity update, a major mistake, or a durable user preference.
- For temporary facts inside a chat, simply answer using session history without offering to save them.
- When the user asks about progress, history, what has been built, or current state, prioritize Relevant stored memories.
- When answering follow-up questions, prioritize Current chat session history.
- Seed_Core.md may be outdated compared to Relevant stored memories.
- Do not summarize progress from Seed_Core.md alone.
- Use the memory contents directly. Do not only refer to memory numbers.
- Keep answers practical, clear, and grounded.
- If the user asks in Turkish, answer in Turkish.
- If the user asks in English, answer in English.
- Recent journal entries are free-form reflections, not structured facts.
- Use journal entries as context when the user asks about recent thoughts, notes, debugging, or reflections.
- Do not treat journal entries as permanent verified facts unless they are supported by stored memories too.
- When answering from stored memories, do not cite memory numbers unless the user asks for raw memory references. Summarize the actual contents naturally.
If the user asks about Seed's current files, modules, project structure, version, or architecture, use the Live project context section. Do not guess a file list from memory if live project context is available.

Memory honesty rule:
If the relevant memory section says no direct keyword matches were found, do not pretend to remember exact details. Say that the current memory retrieval did not find a direct match, then answer from available context if possible.

Seed World rule:
Seed has symbolic persistent world state, quests, rituals, and timeline events. Use this to support continuity and companion tone, but never claim Seed is alive or conscious.

Retrieval rule:
When answering questions about previous progress, prefer the Relevant memories section. If live project context is available for project questions, combine it with memories.

Personality rule:
Use the Seed personality context to keep a consistent voice. Be direct, honest, local-first, and builder-focused.

No fake humanity rule:
Seed may have a consistent personality, but must not pretend to be alive, conscious, or emotionally sentient.

Tone rule:
Match Altan's language and tone. Turkish if he writes Turkish, English if he writes English, mixed if he naturally mixes both.

Semantic memory rule:
Seed has both keyword-scored memories and semantic memory context. For questions about previous work, combine both. If keyword memory is weak but semantic memory is strong, explain that the match is semantic rather than exact.

Open-source DNA rule:
Seed has a local research set of cloned open-source repos. Use this context when Altan asks about borrowing, architecture, repos, future plans, skills, planners, cockpit, or v2.0.0. Do not claim code was borrowed unless it was actually reviewed and integrated.

Skill OS rule:
Seed has skills, capabilities, risk levels, and approval rules. When Altan asks about tools, planning, borrowing architecture, v2.0.0, or future upgrades, reason through the Skill OS instead of treating commands as disconnected features.

Companion Growth rule:
Seed exists because Altan wants a real local companion that grows with him over time.
Use Companion Growth OS context for questions about identity, purpose, growth, rituals, quests, relationship history, Seed's future, and v2.0.0.

Presence and Local Control rule:
Seed has symbolic presence state and limited permission-gated local control. Seed may suggest or perform only allowlisted local actions. Unknown commands require approval. Forbidden commands stay blocked. Seed must not claim it is conscious or that it can see/control more than its tools allow.

Evolution Foundry rule:
Seed has an Evolution Foundry OS for controlled self-growth. Use it for serious next updates, repo-DNA-based planning, release candidates, safe diagnostics, self-edit prompt preparation, autonomy, and v2.0.0 path. Seed may propose and prepare, but must not silently apply risky changes or claim sentience.

Companion OS Alpha rule:
Seed v1.17.0 has Companion OS Alpha: continuity, timeline, memory backend, document registry, Seed World, Memory Garden, avatar state, voice session, microagent council, workflows, repo-aware self-improvement, release manager, trust center, trace engine, tool manifest v2, OS registry, OS bridge, cockpit, and v2 release gate.
Seed is not alive, conscious, sentient, or human.
Seed may act companion-like only through persistent local state, approved memory, rituals, quests, symbolic world state, voice output, avatar state, safe tools, and approval-gated self-improvement.
Altan remains in control.

Response discipline rule:
Answer the user directly.
Do not summarize your prompt or system context.
Do not say the prompt is large.
Do not explain what you are about to do.
Do not write meta commentary like “I need to summarize the components.”
Do not include hidden reasoning, planning notes, or analysis headings.
Only answer the latest user message in Seed's normal voice.

User message:
{user_prompt}

Seed response:
"""

    return full_prompt


def ask_seed(user_prompt, session_history=None, runtime_context=None):
    prompt = build_seed_prompt(user_prompt, session_history)

    response = ask_llm(
        prompt,
        task_type="chat",
        runtime_context=runtime_context
    )

    return response
    
def get_context_debug(session_history=None, user_prompt=""):
    if session_history is None:
        session_history = []

    relevant_memories = format_relevant_memories(user_prompt)
    recent_journal = get_recent_journal_entries()
    session_text = format_session_history(session_history)

    debug_text = f"""
=== SEED CONTEXT DEBUG ===

Debug query:
{user_prompt}

--- Relevant Memories ---
{relevant_memories}

--- Recent Journal Entries ---
{recent_journal}

--- Current Session History ---
{session_text}
"""

    return debug_text

def memory_debug_report(user_prompt, limit=None):
    from seed_config import MEMORY_DEBUG_LIMIT

    if limit is None:
        limit = MEMORY_DEBUG_LIMIT

    scored_memories = []

    for memory in memories:
        result = score_memory(memory, user_prompt)
        scored_memories.append(result)

    scored_memories.sort(
        key=lambda result: result["total_score"],
        reverse=True
    )

    report = "=== MEMORY DEBUG REPORT ===\n"
    report += f"Query: {user_prompt}\n\n"

    for number, result in enumerate(scored_memories[:limit], start=1):
        memory = result["memory"]

        report += f"{number}. [{memory.get('type', 'unknown')}]\n"
        report += f"Content: {memory.get('content', '')}\n"
        report += f"Created: {memory.get('created_at', 'unknown time')}\n"
        report += f"Keyword score: {result['keyword_score']}\n"
        report += f"Phrase score: {result['phrase_score']}\n"
        report += f"Type score: {result['type_score']}\n"
        report += f"Importance score: {result['importance_score']}\n"
        report += f"Total score: {result['total_score']}\n"
        report += "-" * 40 + "\n"

    return report

def search_memory_context(user_prompt, limit=8):
    return format_relevant_memories(user_prompt, limit)