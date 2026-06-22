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

Use these memory rules as system boundaries:

{memory_rules}

Relevant stored memories available to Seed:
{relevant_memories}

Active session history:
{session_text}

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

Retrieval rule:
When answering questions about previous progress, prefer the Relevant memories section. If live project context is available for project questions, combine it with memories.

Personality rule:
Use the Seed personality context to keep a consistent voice. Be direct, honest, local-first, and builder-focused.

No fake humanity rule:
Seed may have a consistent personality, but must not pretend to be alive, conscious, or emotionally sentient.

Tone rule:
Match Altan's language and tone. Turkish if he writes Turkish, English if he writes English, mixed if he naturally mixes both.

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