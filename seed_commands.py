from seed_files import show_seed_core, show_memory_rules, show_first_contact
from seed_memory import (
    list_memories,
    delete_memory,
    save_memory_direct
)
from seed_journal import write_journal, read_journal
from seed_status import show_seed_status
from seed_brain import ask_seed, get_context_debug, search_memory_context, memory_debug_report
from seed_memory_tools import (
    list_memories_by_type,
    show_memory_stats,
    find_possible_duplicates
)
from seed_memory_suggester import suggest_memory
from seed_config import LOG_COMMAND_EVENTS
from seed_chat_logger import (
    log_system_event,
    log_command_event,
    log_developer_note,
    show_current_log_path,
    read_recent_log_lines
)
from seed_session_summarizer import (
    show_session_summary,
    save_last_summary_to_memory,
    save_last_summary_to_journal
)
from seed_project_inspector import (
    show_project_report,
    show_project_files,
    show_project_modules,
    show_version_info,
    save_project_report_to_memory
)
from seed_visuals import show_seed_hud_screen
from seed_personality import show_personality
from seed_llm import (
    show_llm_status,
    show_local_models,
    show_task_models,
    set_active_chat_model,
    set_task_model,
    test_llm,
    test_embedding
)

from seed_self_editor import (
    show_editable_files,
    show_file_for_edit,
    create_edit_proposal,
    show_pending_diff,
    apply_pending_edit,
    cancel_pending_edit,
    run_python_syntax_check,
    rollback_latest_edit
)
from seed_semantic_memory import (
    build_memory_embedding_index,
    format_semantic_results,
    format_semantic_context_for_prompt,
    show_semantic_memory_status
)

from seed_memory_intelligence import (
    smart_memory_capture_from_chat,
    show_pending_memory_draft,
    approve_pending_memory,
    reject_pending_memory
)

from seed_tool_kernel import show_tools, show_tool_result
from seed_agent import (
    create_agent_plan,
    show_pending_agent_plan,
    run_readonly_agent_plan,
    generate_self_review,
    show_boot_brief,
    show_agent_status
)

from seed_open_source_dna import (
    show_dna_status,
    scan_open_source_dna,
    audit_repo,
    audit_all_repos,
    generate_open_source_report,
    show_dna_report,
    show_borrow_map,
    show_repo_dna,
    build_borrow_candidate_index,
    show_borrow_candidates,
    show_borrow_candidate_file
)

from seed_skill_kernel import (
    bootstrap_default_skills,
    show_skills,
    show_skill_detail,
    show_skill_map,
    show_skill_audit
)
from seed_capability_runtime import (
    show_capability,
    show_capability_result
)
from seed_skill_planner import (
    create_skill_plan,
    show_pending_skill_plan,
    run_readonly_skill_plan
)

from seed_world import (
    show_world,
    show_timeline,
    show_quests,
    show_rituals,
    add_timeline_event,
    add_quest,
    complete_quest,
    adjust_world_after_event
)
from seed_cockpit import run_cockpit

def show_chat_help():
    print("\n=== CHAT COMMANDS ===")
    print("/help or /commands = show commands")
    print("/exit or /quit = return to main menu")
    print("/save = manually save a memory")
    print("/suggest = manually generate a memory suggestion")
    print("/autosuggest = toggle automatic memory suggestions on/off")
    print("/memories = list Seed memories")
    print("/search = search relevant memories")
    print("/search-type = list memories by type")
    print("/memory-stats or /stats = show memory statistics")
    print("/duplicates = find possible duplicate memories")
    print("/forget = delete memory by number")
    print("/journal = write a journal entry")
    print("/journal-read = read journal entries")
    print("/core = show Seed Core")
    print("/rules = show Memory Rules")
    print("/first-contact = show First Contact")
    print("/status = show Seed status")
    print("/debug = show current prompt context")
    print("/clear-session = clear temporary chat history")
    print("/config = show Seed configuration")
    print("/log = show current chat log path")
    print("/log-note = write a note into current chat log")
    print("/log-read = read recent lines from current chat log")
    print("/summary = summarize current chat session")
    print("/summary-save-memory = save last summary to memory")
    print("/summary-save-journal = save last summary to journal")
    print("/project = show Seed project report")
    print("/files = show project files")
    print("/modules = show Python modules")
    print("/version = show Seed version info")
    print("/project-save-memory = save project report to memory")
    print("/memory-debug = show detailed memory retrieval scoring")
    print("/hud = show Seed visual dashboard")
    print("/personality = show Seed personality profile")
    print("/llm = show LLM engine status")
    print("/models = list local Ollama models")
    print("/model = change active chat model")
    print("/model <name> = set active chat model directly")
    print("/task-models = show task model routing")
    print("/set-task-model = set model for a task route")
    print("/llm-test = test LLM route")
    print("/self-files = show files Seed is allowed to edit")
    print("/self-read = read an editable Seed file")
    print("/self-edit = create a self-edit proposal")
    print("/self-diff = show pending self-edit diff")
    print("/self-apply = apply pending self-edit after approval")
    print("/self-cancel = cancel pending self-edit")
    print("/self-test = run Python syntax checks")
    print("/self-rollback = restore latest self-edit backup")
    print("/embedding-test = test embedding engine")
    print("/memory-reindex = rebuild semantic memory embeddings")
    print("/semantic-memory = show semantic memory status")
    print("/semantic-search = semantic memory search")
    print("/semantic-context = show semantic context for a prompt")
    print("/save = smart memory capture")
    print("/save <text> = smart memory capture from one line")
    print("/save-manual = old manual memory save")
    print("/remember <text> = smart memory capture alias")
    print("/memory-draft = show pending smart memory draft")
    print("/memory-approve = approve pending smart memory draft")
    print("/memory-reject = reject pending smart memory draft")
    print("/boot = show Seed boot brief")
    print("/tools = show Seed tool kernel")
    print("/tool <name> = run one safe tool")
    print("/agent-status = show agent kernel status")
    print("/agent-plan <goal> = create agent plan")
    print("/agent-plan-show = show pending agent plan")
    print("/agent-run-readonly = run safe read-only plan steps")
    print("/self-review = generate Seed self-review report")
    print("/dna = show open-source DNA status")
    print("/dna-scan = scan cloned research repos")
    print("/dna-repo = show one repo DNA")
    print("/dna-audit = audit one repo with local LLM")
    print("/dna-audit-all = audit all cloned repos with local LLM")
    print("/dna-report-build = build open-source DNA report")
    print("/dna-report = show open-source DNA report")
    print("/borrow-map = show Seed borrow map")
    print("/borrow-candidates = scan code-pattern candidates")
    print("/borrow-view = view one borrow candidate file")
    print("/skill-bootstrap = create default Seed skill manifests")
    print("/skills = show Seed Skill OS")
    print("/skill <name> = show one skill")
    print("/skill-map = show skills and capabilities")
    print("/skill-audit = validate skill manifests")
    print("/capability <id> = show one capability")
    print("/capability-run <id> = run safe read-only/diagnostic capability")
    print("/skill-plan <goal> = create Skill OS plan")
    print("/skill-plan-show = show pending Skill OS plan")
    print("/skill-run-readonly = run read-only/diagnostic skill plan")
    print("/world = show Seed World")
    print("/timeline = show life timeline")
    print("/timeline-add = add timeline event")
    print("/quests = show quests")
    print("/quest-add = add quest")
    print("/quest-done = complete quest")
    print("/rituals = show rituals")
    print("/world-event = adjust world after symbolic event")
    print("/cockpit = launch local web cockpit")

def save_memory_from_chat():
    print("\n=== SAVE MEMORY FROM CHAT ===")

    memory_type = input("Memory type: ")
    content = input("Content: ")

    try:
        importance = int(input("Importance (1-5): "))
    except ValueError:
        print("Invalid importance. Please enter a number between 1 and 5.")
        return None

    saved = save_memory_direct(memory_type, content, importance)

    if saved:
        print("Memory saved from chat.")
        return {
            "type": memory_type,
            "content": content,
            "importance": importance
        }

    return None


def manual_memory_suggestion(session_history, chat_state):
    print("\n=== MANUAL MEMORY SUGGESTION ===")

    user_message = input("What happened / what did we do?: ")

    if user_message == "":
        print("Suggestion input cannot be empty.")
        return

    seed_answer = "Manual suggestion requested by user."

    suggestion = suggest_memory(user_message, seed_answer)

    if suggestion is None:
        print("No suggestion generated.")
        return

    print("\n=== SUGGESTED MEMORY ===")
    print(f"Type: {suggestion['type']}")
    print(f"Content: {suggestion['content']}")
    print(f"Importance: {suggestion['importance']}")

    choice = input("Save this memory? (y/n): ")

    if choice.lower() == "y":
        saved = save_memory_direct(
            suggestion["type"],
            suggestion["content"],
            suggestion["importance"]
        )

        if saved:
            print("Suggested memory saved.")
            log_system_event(
                chat_state.get("log_path"),
                (
                    f"Manually approved suggested memory: "
                    f"[{suggestion['type']}] "
                    f"{suggestion['content']} "
                    f"Importance: {suggestion['importance']}"
                )
            )

            session_history.append({
                "role": "System",
                "content": (
                    f"User manually approved and saved suggested memory: "
                    f"[{suggestion['type']}] "
                    f"{suggestion['content']} "
                    f"Importance: {suggestion['importance']}"
                )
            })
    else:
        print("Suggested memory skipped.")
        log_system_event(
            chat_state.get("log_path"),
            "Manual suggested memory skipped."
        )


def handle_memory_suggestion(user_message, seed_answer, session_history, chat_state=None):
    suggestion = suggest_memory(user_message, seed_answer)

    if suggestion is None:
        return

    print("\n=== SUGGESTED MEMORY ===")
    print(f"Type: {suggestion['type']}")
    print(f"Content: {suggestion['content']}")
    print(f"Importance: {suggestion['importance']}")

    choice = input("Save this memory? (y/n): ")

    if choice.lower() == "y":
        saved = save_memory_direct(
            suggestion["type"],
            suggestion["content"],
            suggestion["importance"]
        )

        if saved:
            print("Suggested memory saved.")

            session_history.append({
                "role": "System",
                "content": (
                    f"User approved and saved suggested memory: "
                    f"[{suggestion['type']}] "
                    f"{suggestion['content']} "
                    f"Importance: {suggestion['importance']}"
                )
            })

            if chat_state is not None:
                log_path = chat_state.get("log_path")
                log_system_event(
                    log_path,
                    (
                        f"Approved suggested memory: "
                        f"[{suggestion['type']}] "
                        f"{suggestion['content']} "
                        f"Importance: {suggestion['importance']}"
                    )
                )
    else:
        print("Suggested memory skipped.")

        if chat_state is not None:
            log_path = chat_state.get("log_path")
            log_system_event(log_path, "Suggested memory skipped.")


def handle_chat_command(user_message, session_history, chat_state):
    command = user_message.strip().lower()
    log_path = chat_state.get("log_path")

    if command.startswith("/") and LOG_COMMAND_EVENTS:
        log_command_event(log_path, command)

    if command in ["/exit", "/quit"]:
        print("Leaving Seed chat...")
        return "exit"
    if command == "/config":
        show_config()
        return "handled"

    if command in ["/help", "/commands"]:
        show_chat_help()
        return "handled"

    if command == "/autosuggest":
        chat_state["autosuggest_enabled"] = not chat_state["autosuggest_enabled"]

        if chat_state["autosuggest_enabled"]:
            print("Autosuggest is now ON.")
        else:
            print("Autosuggest is now OFF.")
        log_system_event(
            log_path,
            f"Autosuggest set to {chat_state['autosuggest_enabled']}"
        )

        return "handled"

    if command == "/save":
        smart_memory_capture_from_chat(chat_state, session_history)
        return "handled"

    if command.startswith("/save "):
        memory_text = user_message.strip()[len("/save "):]
        smart_memory_capture_from_chat(
            chat_state,
            session_history,
            initial_text=memory_text
        )
        return "handled"

    if command == "/remember":
        smart_memory_capture_from_chat(chat_state, session_history)
        return "handled"

    if command.startswith("/remember "):
        memory_text = user_message.strip()[len("/remember "):]
        smart_memory_capture_from_chat(
            chat_state,
            session_history,
            initial_text=memory_text
        )
        return "handled"

    if command == "/save-manual":
        saved_memory = save_memory_from_chat()

        if saved_memory is not None:
            session_history.append({
                "role": "System",
                "content": (
                    f"User manually saved a long-term memory: "
                    f"[{saved_memory['type']}] "
                    f"{saved_memory['content']} "
                    f"Importance: {saved_memory['importance']}"
                )
            })

            log_system_event(
                log_path,
                (
                    f"Manual memory saved: "
                    f"[{saved_memory['type']}] "
                    f"{saved_memory['content']} "
                    f"Importance: {saved_memory['importance']}"
                )
            )

        return "handled"

    if command == "/memory-draft":
        show_pending_memory_draft(chat_state)
        return "handled"

    if command == "/memory-approve":
        approve_pending_memory(chat_state, session_history)
        return "handled"

    if command == "/memory-reject":
        reject_pending_memory(chat_state)
        return "handled"

    if command == "/suggest":
        manual_memory_suggestion(session_history)
        return "handled"

    if command == "/memories":
        list_memories()
        return "handled"
    
    if command == "/memory-debug":
        debug_query = input("Memory debug query: ")
        print(memory_debug_report(debug_query))
        return "handled"
    
    if command == "/search":
        search_query = input("Search query: ")
        print("\n=== MEMORY SEARCH RESULTS ===")
        print(search_memory_context(search_query))
        return "handled"

    if command == "/search-type":
        memory_type = input("Memory type: ")
        list_memories_by_type(memory_type)
        return "handled"

    if command in ["/memory-stats", "/stats"]:
        show_memory_stats()
        return "handled"

    if command == "/duplicates":
        find_possible_duplicates()
        return "handled"

    if command == "/forget":
        print("\n=== FORGET MEMORY FROM CHAT ===")
        delete_memory()
        log_system_event(log_path, "Forget memory command used.")
        return "handled"

    if command == "/journal":
        journal_entry = write_journal()

        if journal_entry is not None:
            session_history.append({
                "role": "System",
                "content": (
                    f"User wrote this journal entry during this chat session: "
                    f"{journal_entry}"
                )
            })
            log_system_event(
                    log_path,
                    f"Journal entry written: {journal_entry}"
                )

        return "handled"

    if command == "/journal-read":
        read_journal()
        return "handled"

    if command == "/core":
        show_seed_core()
        return "handled"

    if command == "/rules":
        show_memory_rules()
        return "handled"

    if command == "/first-contact":
        show_first_contact()
        return "handled"
    
    if command == "/summary":
        show_session_summary(session_history, chat_state)
        return "handled"

    if command == "/summary-save-memory":
        save_last_summary_to_memory(chat_state)
        return "handled"

    if command == "/summary-save-journal":
        save_last_summary_to_journal(chat_state)
        return "handled"
    
    if command == "/log":
        show_current_log_path(log_path)
        return "handled"

    if command == "/log-note":
        log_developer_note(log_path)
        return "handled"

    if command == "/log-read":
        read_recent_log_lines(log_path)
        return "handled"
    
    if command == "/embedding-test":
        test_embedding()
        return "handled"

    if command == "/memory-reindex":
        build_memory_embedding_index()
        log_system_event(log_path, "Semantic memory reindex command used.")
        return "handled"

    if command == "/semantic-memory":
        show_semantic_memory_status()
        return "handled"

    if command == "/semantic-search":
        query = input("Semantic search query: ")
        print(format_semantic_results(query))
        return "handled"

    if command == "/semantic-context":
        query = input("Semantic context query: ")
        print(format_semantic_context_for_prompt(query))
        return "handled"

    if command == "/project":
        show_project_report()
        return "handled"

    if command == "/files":
        show_project_files()
        return "handled"

    if command == "/modules":
        show_project_modules()
        return "handled"

    if command == "/version":
        show_version_info()
        return "handled"

    if command == "/project-save-memory":
        save_project_report_to_memory(chat_state)
        return "handled"
    
    if command == "/llm":
        show_llm_status(chat_state)
        return "handled"

    if command == "/models":
        show_local_models()
        return "handled"

    if command == "/task-models":
        show_task_models(chat_state)
        return "handled"

    if command == "/model":
        changed = set_active_chat_model(chat_state)

        if changed:
            session_history.append({
                "role": "System",
                "content": f"Active chat model changed to {chat_state.get('active_model')}."
            })

            log_system_event(
                log_path,
                f"Active chat model changed to {chat_state.get('active_model')}."
            )

        return "handled"

    if command == "/self-files":
        show_editable_files()
        return "handled"

    if command == "/self-read":
        show_file_for_edit()
        return "handled"

    if command == "/self-edit":
        create_edit_proposal(chat_state)
        log_system_event(log_path, "Self-edit proposal command used.")
        return "handled"

    if command == "/self-diff":
        show_pending_diff()
        return "handled"

    if command == "/self-apply":
        edited_file = apply_pending_edit()

        if edited_file is not None:
            log_system_event(log_path, f"Self-edit applied to {edited_file}.")

        return "handled"

    if command == "/self-cancel":
        cancel_pending_edit()
        log_system_event(log_path, "Pending self-edit cancelled.")
        return "handled"

    if command == "/self-test":
        run_python_syntax_check()
        return "handled"

    if command == "/self-rollback":
        rollback_latest_edit()
        log_system_event(log_path, "Self-edit rollback command used.")
        return "handled"

    if command.startswith("/model "):
        requested_model = command.replace("/model ", "", 1).strip()
        changed = set_active_chat_model(chat_state, requested_model)

        if changed:
            session_history.append({
                "role": "System",
                "content": f"Active chat model changed to {chat_state.get('active_model')}."
            })

            log_system_event(
                log_path,
                f"Active chat model changed to {chat_state.get('active_model')}."
            )

        return "handled"

    if command == "/set-task-model":
        changed = set_task_model(chat_state)

        if changed:
            session_history.append({
                "role": "System",
                "content": "Seed task model routing was updated."
            })

            log_system_event(
                log_path,
                "Seed task model routing was updated."
            )

        return "handled"

    if command == "/llm-test":
        test_llm(chat_state)
        return "handled"

    if command == "/status":
        show_seed_status()
        return "handled"
    
    if command == "/personality":
        show_personality()
        return "handled"

    if command == "/hud":
        show_seed_hud_screen(chat_state)
        return "handled"

    if command == "/debug":
        debug_query = input("Debug query: ")
        print(get_context_debug(session_history, debug_query))
        return "handled"

    if command == "/clear-session":
        session_history.clear()
        print("Temporary session history cleared.")
        log_system_event(log_path, "Temporary session history cleared.")
        return "handled"

    if command == "/boot":
        show_boot_brief(chat_state)
        return "handled"

    if command == "/tools":
        show_tools()
        return "handled"

    if command.startswith("/tool "):
        tool_name = command.replace("/tool ", "", 1).strip()
        show_tool_result(tool_name, chat_state)
        return "handled"

    if command == "/agent-status":
        show_agent_status(chat_state)
        return "handled"

    if command.startswith("/agent-plan "):
        goal = user_message.strip()[len("/agent-plan "):]
        create_agent_plan(goal, chat_state)
        return "handled"

    if command == "/agent-plan":
        goal = input("Agent goal: ")
        create_agent_plan(goal, chat_state)
        return "handled"

    if command == "/agent-plan-show":
        show_pending_agent_plan(chat_state)
        return "handled"

    if command == "/agent-run-readonly":
        run_readonly_agent_plan(chat_state)
        return "handled"

    if command == "/self-review":
        generate_self_review(chat_state)
        return "handled"
    
    if command == "/dna":
        show_dna_status()
        return "handled"

    if command == "/dna-scan":
        scan_open_source_dna()
        return "handled"

    if command == "/dna-repo":
        repo_query = input("Repo name/folder: ")
        show_repo_dna(repo_query)
        return "handled"

    if command.startswith("/dna-repo "):
        repo_query = user_message.strip()[len("/dna-repo "):]
        show_repo_dna(repo_query)
        return "handled"

    if command == "/dna-audit":
        repo_query = input("Repo name/folder: ")
        audit_repo(repo_query, chat_state)
        return "handled"

    if command.startswith("/dna-audit "):
        repo_query = user_message.strip()[len("/dna-audit "):]
        audit_repo(repo_query, chat_state)
        return "handled"

    if command == "/dna-audit-all":
        confirmation = input("Audit all repos with local LLM? This may take time. Type AUDIT: ")

        if confirmation == "AUDIT":
            audit_all_repos(chat_state)
        else:
            print("DNA audit cancelled.")

            return "handled"

    if command == "/dna-report-build":
        generate_open_source_report()
        return "handled"

    if command == "/dna-report":
        show_dna_report()
        return "handled"

    if command == "/borrow-map":
        show_borrow_map()
        return "handled"

    if command == "/borrow-candidates":
        build_borrow_candidate_index()
        show_borrow_candidates()
        return "handled"

    if command == "/borrow-view":
        candidate_number = input("Candidate number: ")
        show_borrow_candidate_file(candidate_number)
        return "handled"
    
    if command == "/skill-bootstrap":
        bootstrap_default_skills()
        return "handled"

    if command == "/skills":
        show_skills()
        return "handled"

    if command == "/skill-map":
        show_skill_map()
        return "handled"

    if command == "/skill-audit":
        show_skill_audit()
        return "handled"

    if command.startswith("/skill "):
        skill_query = user_message.strip()[len("/skill "):]
        show_skill_detail(skill_query)
        return "handled"

    if command == "/skill":
        skill_query = input("Skill name/id: ")
        show_skill_detail(skill_query)
        return "handled"

    if command.startswith("/capability-run "):
        capability_query = user_message.strip()[len("/capability-run "):]
        show_capability_result(capability_query, chat_state)
        return "handled"

    if command == "/capability-run":
        capability_query = input("Capability id/name: ")
        show_capability_result(capability_query, chat_state)
        return "handled"

    if command.startswith("/capability "):
        capability_query = user_message.strip()[len("/capability "):]
        show_capability(capability_query)
        return "handled"

    if command == "/capability":
        capability_query = input("Capability id/name: ")
        show_capability(capability_query)
        return "handled"

    if command.startswith("/skill-plan "):
        goal = user_message.strip()[len("/skill-plan "):]
        create_skill_plan(goal, chat_state)
        return "handled"

    if command == "/skill-plan":
        goal = input("Skill plan goal: ")
        create_skill_plan(goal, chat_state)
        return "handled"

    if command == "/skill-plan-show":
        show_pending_skill_plan(chat_state)
        return "handled"

    if command == "/skill-run-readonly":
        run_readonly_skill_plan(chat_state)
        return "handled"

    if command.startswith("/borrow-view "):
        candidate_number = user_message.strip()[len("/borrow-view "):]
        show_borrow_candidate_file(candidate_number)
        return "handled"
    
    if command == "/world":
        show_world()
        return "handled"

    if command == "/timeline":
        show_timeline()
        return "handled"

    if command == "/timeline-add":
        print("\n=== ADD TIMELINE EVENT ===")
        title = input("Title: ")
        event_type = input("Type (general/project_milestone/reflection): ")
        note = input("Note: ")
        importance = input("Importance (1-5): ")

        try:
            importance_value = int(importance)
        except ValueError:
            importance_value = 3

        add_timeline_event(title, event_type, note, importance_value)
        print("Timeline event added.")
        return "handled"

    if command == "/quests":
        show_quests()
        return "handled"

    if command == "/quest-add":
        print("\n=== ADD QUEST ===")
        title = input("Title: ")
        quest_type = input("Type (project/growth/courage/focus/reflection): ")
        difficulty = input("Difficulty (1-5): ")
        reward = input("Reward: ")
        reason = input("Reason: ")

        try:
            difficulty_value = int(difficulty)
        except ValueError:
            difficulty_value = 3

        quest = add_quest(title, quest_type, difficulty_value, reward, reason)
        print(f"Quest added: {quest.get('id')}")
        return "handled"

    if command == "/quest-done":
        quest_id = input("Quest ID: ")
        quest = complete_quest(quest_id)

        if quest is None:
            print("Quest not found.")
        else:
            print(f"Quest completed: {quest.get('title')}")

        return "handled"

    if command == "/rituals":
        show_rituals()
        return "handled"

    if command == "/world-event":
        print("\nEvent types: memory_saved, quest_completed, reflection, project_milestone")
        event_type = input("Event type: ")
        adjust_world_after_event(event_type)
        print("World updated.")
        return "handled"

    if command == "/cockpit":
        run_cockpit()
        return "handled"

    if command.startswith("/"):
        print("Unknown command. Type /help to see available commands.")
        return "handled"

    return "normal"

def show_config():
    from seed_config import (
        SEED_VERSION,
        MODEL_NAME,
        OLLAMA_URL,
        MEMORY_SEARCH_LIMIT,
        RECENT_JOURNAL_LIMIT,
        SESSION_HISTORY_LIMIT,
        AUTOSUGGEST_DEFAULT,
        SEED_MODE
    )

    print("\n=== SEED CONFIG ===")
    print(f"Version: {SEED_VERSION}")
    print(f"Model: {MODEL_NAME}")
    print(f"Ollama URL: {OLLAMA_URL}")
    print(f"Memory search limit: {MEMORY_SEARCH_LIMIT}")
    print(f"Recent journal limit: {RECENT_JOURNAL_LIMIT}")
    print(f"Session history limit: {SESSION_HISTORY_LIMIT}")
    print(f"Autosuggest default: {AUTOSUGGEST_DEFAULT}")
    print(f"Mode: {SEED_MODE}")