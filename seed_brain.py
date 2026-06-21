import requests
from seed_memory import memories
from seed_journal import get_recent_journal_entries
from seed_memory_tools import expand_query



OLLAMA_URL = "http://localhost:11434/api/generate"
MODEL_NAME = "llama3.1:8b"



def clean_words(text):
    stop_words = [
        "what", "did", "we", "the", "a", "an", "to", "of", "and",
        "or", "is", "are", "was", "were", "about", "with", "in",
        "on", "for", "so", "far", "just", "me", "my", "our"
    ]

    cleaned_text = text.lower()

    for symbol in [".", ",", "?", "!", ":", ";", "(", ")", "[", "]", "{", "}", "/", "\\"]:
        cleaned_text = cleaned_text.replace(symbol, " ")

    words = cleaned_text.split()

    useful_words = []

    for word in words:
        if word not in stop_words and len(word) > 2:
            useful_words.append(word)

    return useful_words


def score_memory(memory, user_prompt):
    prompt_words = clean_words(user_prompt)
    expanded_words = expand_query(user_prompt)
    prompt_words.extend(expanded_words)
    unique_prompt_words = []

    for word in prompt_words:
        if word not in unique_prompt_words:
            unique_prompt_words.append(word)

    prompt_words = unique_prompt_words
    memory_text = (
        memory.get("type", "") + " " +
        memory.get("content", "") + " " +
        memory.get("created_at", "")
    ).lower()

    keyword_score = 0

    for word in prompt_words:
        if word in memory_text:
            keyword_score += 10

    importance_score = memory.get("importance", 0)

    total_score = keyword_score + importance_score

    return {
        "total_score": total_score,
        "keyword_score": keyword_score,
        "memory": memory
    }

def format_relevant_memories(user_prompt, limit=8):
    if not memories:
        return "No stored memories yet."

    scored_memories = []

    for memory in memories:
        scored_memory = score_memory(memory, user_prompt)

        if scored_memory["keyword_score"] > 0:
            scored_memories.append(scored_memory)

    if not scored_memories:
        important_memories = sorted(
            memories,
            key=lambda memory: memory.get("importance", 0),
            reverse=True
        )[:limit]

        memory_text = "No direct keyword matches found. Showing important memories instead:\n"

        for number, memory in enumerate(important_memories, start=1):
            memory_text += (
                f"{number}. "
                f"[{memory.get('type', 'unknown_type')}] "
                f"{memory.get('content', 'no content')} "
                f"Importance: {memory.get('importance', 'unknown')} "
                f"Created: {memory.get('created_at', 'unknown time')}\n"
            )

        return memory_text

    sorted_memories = sorted(
        scored_memories,
        key=lambda item: item["total_score"],
        reverse=True
    )

    selected_memories = sorted_memories[:limit]

    memory_text = ""

    for number, item in enumerate(selected_memories, start=1):
        memory = item["memory"]

        memory_text += (
        f"{number}. "
        f"[{memory.get('type', 'unknown_type')}] "
        f"{memory.get('content', 'no content')} "
        f"Importance: {memory.get('importance', 'unknown')} "
        f"Keyword score: {item.get('keyword_score', 'unknown')} "
        f"Total score: {item.get('total_score', 'unknown')} "
        f"Created: {memory.get('created_at', 'unknown time')}\n"
     )
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

    full_prompt = f"""
You are Seed.

Use the following Seed Core as your identity and behavior guide:

{seed_core}

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


User message:
{user_prompt}

Seed response:
"""

    return full_prompt


def ask_seed(user_prompt, session_history=None):
    prompt = build_seed_prompt(user_prompt, session_history)

    payload = {
        "model": MODEL_NAME,
        "prompt": prompt,
        "stream": False
    }

    try:
        response = requests.post(OLLAMA_URL, json=payload)
        response.raise_for_status()
        data = response.json()
        return data["response"]

    except requests.exceptions.ConnectionError:
        return "Seed brain is not connected. Make sure Ollama is running."

    except requests.exceptions.RequestException as error:
        return f"Seed brain error: {error}"
    
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

def search_memory_context(user_prompt, limit=8):
    return format_relevant_memories(user_prompt, limit)