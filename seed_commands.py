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
from seed_companion_growth import (
    show_growth_status,
    show_why_seed_exists,
    show_companion_contract,
    show_growth_arcs,
    add_growth_arc_interactive,
    complete_growth_arc_interactive,
    show_rituals,
    run_ritual_interactive,
    show_quests,
    add_quest_interactive,
    complete_quest_interactive,
    show_milestones,
    add_milestone_interactive,
    show_memory_garden,
    show_identity_mirror,
    add_mirror_interactive,
    generate_identity_mirror,
    generate_companion_pulse,
    show_repo_influences
)

from seed_presence import (
    show_presence_state,
    set_presence_mode_interactive,
    set_emergency_lock
)
from seed_computer_awareness import (
    show_computer_snapshot,
    refresh_computer_snapshot
)
from seed_local_control import (
    show_local_control_status,
    run_shell_interactive,
    open_app_interactive,
    open_folder_interactive,
    show_pending_action,
    approve_pending_action,
    reject_pending_action,
    show_action_history
)
from seed_event_bus import show_events, add_manual_event
from seed_code_map import build_code_map, show_code_map
from seed_action_proposer import propose_local_action_interactive
from seed_evolution_foundry import (
    show_foundry_status,
    show_autonomy,
    set_autonomy_level_interactive,
    set_foundry_stop,
    generate_evolution_proposals,
    show_evolution_proposals,
    promote_proposal_to_release_candidate,
    show_release_candidates,
    approve_release_candidate_interactive,
    reject_release_candidate_interactive,
    generate_self_edit_prompt_from_candidate,
    run_foundry_diagnostics,
    generate_companion_evolution_pulse,
    show_foundry_journal
)

try:
    from seed_companion_os_commands import (
        handle_companion_os_command,
        print_companion_os_help
    )
    COMPANION_OS_COMMANDS_AVAILABLE = True
except Exception:
    COMPANION_OS_COMMANDS_AVAILABLE = False

    def handle_companion_os_command(command, chat_state=None):
        return None

    def print_companion_os_help():
        pass


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
    print("/companion = show Companion Growth OS")
    print("/seed-why = explain why Seed exists")
    print("/companion-contract = show companion contract")
    print("/growth-arcs = show growth arcs")
    print("/growth-arc-add = add growth arc")
    print("/growth-arc-done = complete growth arc")
    print("/rituals = show companion rituals")
    print("/ritual-run = run companion ritual")
    print("/quests = show companion quests")
    print("/quest-add = add companion quest")
    print("/quest-done = complete companion quest")
    print("/milestones = show companion milestones")
    print("/milestone-add = add companion milestone")
    print("/memory-garden = show memory garden")
    print("/mirror = show identity mirror")
    print("/mirror-add = add mirror observation")
    print("/mirror-generate = generate identity mirror")
    print("/companion-pulse = generate companion pulse")
    print("/repo-influences = show how cloned repos shape Seed")
    print("/presence = show Seed presence state")
    print("/presence-mode = set Seed presence mode")
    print("/computer = show computer snapshot")
    print("/computer-refresh = refresh computer snapshot")
    print("/local-control = show local control status")
    print("/local-shell = run safe/approval-gated local shell command")
    print("/open-app = open allowlisted app")
    print("/open-folder = open allowlisted folder")
    print("/propose-action = Seed proposes one local action for a goal")
    print("/pending-action = show pending local action")
    print("/action-approve = approve pending local action")
    print("/action-reject = reject pending local action")
    print("/action-history = show local action history")
    print("/local-lock = enable emergency local control lock")
    print("/local-unlock = disable emergency local control lock")
    print("/foundry = show Evolution Foundry OS")
    print("/autonomy = show Seed autonomy ladder")
    print("/autonomy-set = set autonomy level")
    print("/foundry-stop = enable Foundry emergency stop")
    print("/foundry-start = disable Foundry emergency stop")
    print("/evolve = generate monstrous evolution proposals")
    print("/evolution-proposals = show recent proposals")
    print("/candidate-new = promote proposal to release candidate")
    print("/candidates = show release candidates")
    print("/candidate-approve = approve candidate as plan")
    print("/candidate-reject = reject candidate")
    print("/candidate-self-edit-prompt = generate self-edit prompt from candidate")
    print("/foundry-diagnostics = run safe Foundry diagnostics")
    print("/evolution-pulse = generate companion evolution pulse")
    print("/foundry-journal = show Foundry journal")
    print("/events = show runtime event stream")
    print("/event-add = add runtime event")
    print("/code-map-build = build repo-aware code map")
    print("/code-map = show repo-aware code map")
    print_companion_os_help()

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
    
    if command == "/companion":
        show_growth_status()
        return "handled"

    if command == "/seed-why":
        show_why_seed_exists()
        return "handled"

    if command == "/companion-contract":
        show_companion_contract()
        return "handled"

    if command == "/growth-arcs":
        show_growth_arcs()
        return "handled"

    if command == "/growth-arc-add":
        add_growth_arc_interactive()
        return "handled"

    if command == "/growth-arc-done":
        complete_growth_arc_interactive()
        return "handled"

    if command == "/rituals":
        show_rituals()
        return "handled"

    if command == "/ritual-run":
        run_ritual_interactive(chat_state)
        return "handled"

    if command == "/quests":
        show_quests()
        return "handled"

    if command == "/quest-add":
        add_quest_interactive()
        return "handled"

    if command == "/quest-done":
        complete_quest_interactive()
        return "handled"

    if command == "/milestones":
        show_milestones()
        return "handled"

    if command == "/milestone-add":
        add_milestone_interactive()
        return "handled"

    if command == "/memory-garden":
        show_memory_garden()
        return "handled"

    if command == "/mirror":
        show_identity_mirror()
        return "handled"

    if command == "/mirror-add":
        add_mirror_interactive()
        return "handled"

    if command == "/mirror-generate":
        generate_identity_mirror(chat_state)
        return "handled"

    if command == "/companion-pulse":
        generate_companion_pulse(chat_state)
        return "handled"

    if command == "/repo-influences":
        show_repo_influences()
        return "handled"
    
    if command == "/presence":
        show_presence_state()
        return "handled"

    if command == "/presence-mode":
        set_presence_mode_interactive()
        return "handled"

    if command == "/computer":
        show_computer_snapshot()
        return "handled"

    if command == "/computer-refresh":
        refresh_computer_snapshot()
        return "handled"

    if command == "/local-control":
        show_local_control_status()
        return "handled"

    if command == "/local-shell":
        run_shell_interactive()
        return "handled"

    if command == "/open-app":
        open_app_interactive()
        return "handled"

    if command == "/open-folder":
        open_folder_interactive()
        return "handled"

    if command == "/propose-action":
        propose_local_action_interactive(chat_state)
        return "handled"

    if command == "/pending-action":
        show_pending_action()
        return "handled"

    if command == "/action-approve":
        approve_pending_action()
        return "handled"

    if command == "/action-reject":
        reject_pending_action()
        return "handled"

    if command == "/action-history":
        show_action_history()
        return "handled"

    if command == "/local-lock":
        set_emergency_lock(True)
        print("Emergency local control lock enabled.")
        return "handled"

    if command == "/local-unlock":
        set_emergency_lock(False)
        print("Emergency local control lock disabled.")
        return "handled"
    
    if command == "/foundry":
        show_foundry_status()
        return "handled"

    if command == "/autonomy":
        show_autonomy()
        return "handled"

    if command == "/autonomy-set":
        set_autonomy_level_interactive()
        return "handled"

    if command == "/foundry-stop":
        set_foundry_stop(True)
        print("Evolution Foundry emergency stop enabled.")
        return "handled"

    if command == "/foundry-start":
        set_foundry_stop(False)
        print("Evolution Foundry emergency stop disabled.")
        return "handled"

    if command == "/evolve":
        generate_evolution_proposals(chat_state)
        return "handled"

    if command == "/evolution-proposals":
        show_evolution_proposals()
        return "handled"

    if command == "/candidate-new":
        promote_proposal_to_release_candidate(chat_state=chat_state)
        return "handled"

    if command == "/candidates":
        show_release_candidates()
        return "handled"

    if command == "/candidate-approve":
        approve_release_candidate_interactive()
        return "handled"

    if command == "/candidate-reject":
        reject_release_candidate_interactive()
        return "handled"

    if command == "/candidate-self-edit-prompt":
        generate_self_edit_prompt_from_candidate()
        return "handled"

    if command == "/foundry-diagnostics":
        run_foundry_diagnostics(chat_state)
        return "handled"

    if command == "/evolution-pulse":
        generate_companion_evolution_pulse(chat_state)
        return "handled"

    if command == "/foundry-journal":
        show_foundry_journal()
        return "handled"
    
    if command == "/events":
        show_events()
        return "handled"

    if command == "/event-add":
        add_manual_event()
        return "handled"

    if command == "/code-map-build":
        build_code_map()
        return "handled"

    if command == "/code-map":
        show_code_map()
        return "handled"

    companion_os_result = handle_companion_os_command(command, chat_state)

    if companion_os_result == "handled":
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
# v20.3 Presence Runtime command wrapper.
try:
    _seed_v203_original_handle_chat_command = handle_chat_command

    def handle_chat_command(user_message, *args, **kwargs):
        try:
            from seed_presence_commands import handle_presence_command
            handled = handle_presence_command(user_message)
            if handled == "handled":
                return "handled"
        except Exception as error:
            print(f"Presence command error: {error}")
            return "handled"

        return _seed_v203_original_handle_chat_command(user_message, *args, **kwargs)
except Exception:
    pass

# v30 Agent HQ command wrapper.
try:
    _seed_v30_original_handle_chat_command = handle_chat_command

    def handle_chat_command(user_message, *args, **kwargs):
        try:
            from seed_v30_commands import handle_v30_command
            handled = handle_v30_command(user_message)
            if handled == "handled":
                return "handled"
        except Exception as error:
            print(f"v30 command error: {error}")
            return "handled"

        return _seed_v30_original_handle_chat_command(user_message, *args, **kwargs)
except Exception:
    pass


# v45 Total Systems command wrapper.
try:
    _seed_v45_original_handle_chat_command = handle_chat_command

    def handle_chat_command(user_message, *args, **kwargs):
        try:
            from seed_v45_commands import handle_v45_command
            handled = handle_v45_command(user_message)
            if handled == "handled":
                return "handled"
        except Exception as error:
            print(f"v45 command error: {error}")
            return "handled"

        return _seed_v45_original_handle_chat_command(user_message, *args, **kwargs)
except Exception:
    pass


# v50 Nothing Left Behind command wrapper.
try:
    _seed_v50_original_handle_chat_command = handle_chat_command

    def handle_chat_command(user_message, *args, **kwargs):
        try:
            from seed_v50_commands import handle_v50_command
            handled = handle_v50_command(user_message)
            if handled == "handled":
                return "handled"
        except Exception as error:
            print(f"v50 command error: {error}")
            return "handled"

        return _seed_v50_original_handle_chat_command(user_message, *args, **kwargs)
except Exception:
    pass


# v60 Natural UX wrapper.
try:
    _seed_v60_original_handle_chat_command = handle_chat_command

    def handle_chat_command(user_message, *args, **kwargs):
        try:
            from seed_natural_intent_router_v60 import handle_natural_intent
            handled = handle_natural_intent(user_message)
            if handled == "handled":
                return "handled"
        except Exception as error:
            print(f"v60 natural router error: {error}")
            return "handled"

        try:
            from seed_v60_commands import handle_v60_command
            handled = handle_v60_command(user_message)
            if handled == "handled":
                return "handled"
        except Exception as error:
            print(f"v60 command error: {error}")
            return "handled"

        return _seed_v60_original_handle_chat_command(user_message, *args, **kwargs)
except Exception:
    pass

# v70 Mega Fusion natural router and debug commands.
try:
    _seed_v70_original_handle_chat_command = handle_chat_command
    def handle_chat_command(user_message, *args, **kwargs):
        try:
            from seed_natural_intent_router_v70 import handle_natural_intent_v70
            handled = handle_natural_intent_v70(user_message)
            if handled == "handled": return "handled"
        except Exception as error:
            print(f"v70 natural router error: {error}"); return "handled"
        try:
            from seed_v70_commands import handle_v70_command
            handled = handle_v70_command(user_message)
            if handled == "handled": return "handled"
        except Exception as error:
            print(f"v70 command error: {error}"); return "handled"
        return _seed_v70_original_handle_chat_command(user_message, *args, **kwargs)
except Exception:
    pass

# v70.1 Real Chat Router
# If older Seed logic falls through to "normal", route normal conversation to Ollama.
try:
    _seed_v701_previous_handle_chat_command = handle_chat_command

    def handle_chat_command(user_message, *args, **kwargs):
        text = str(user_message or "").strip()

        if text.lower() in {"model usage", "show model usage", "model log"}:
            from seed_local_chat_v701 import show_model_usage_log
            return show_model_usage_log()

        result = _seed_v701_previous_handle_chat_command(user_message, *args, **kwargs)

        if result == "handled":
            return "handled"

        if result is None or str(result).strip().lower() in {"", "normal", "none"}:
            from seed_local_chat_v701 import local_chat
            return local_chat(user_message)

        return result

except Exception:
    pass

# v72 Presence Max router.
try:
    _seed_v72_previous_handle_chat_command = handle_chat_command
    def handle_chat_command(user_message, *args, **kwargs):
        try:
            from seed_natural_intent_router_v72 import handle_natural_intent_v72
            handled = handle_natural_intent_v72(user_message)
            if handled == "handled": return "handled"
        except Exception as error:
            print(f"v72 natural router error: {error}"); return "handled"
        try:
            from seed_v72_commands import handle_v72_command
            handled = handle_v72_command(user_message)
            if handled == "handled": return "handled"
        except Exception as error:
            print(f"v72 command error: {error}"); return "handled"
        return _seed_v72_previous_handle_chat_command(user_message,*args,**kwargs)
except Exception:
    pass

# v73 Action Presence router.
try:
    _seed_v73_previous_handle_chat_command = handle_chat_command
    def handle_chat_command(user_message, *args, **kwargs):
        try:
            from seed_natural_intent_router_v73 import handle_natural_intent_v73
            handled = handle_natural_intent_v73(user_message)
            if handled == "handled": return "handled"
        except Exception as error:
            print(f"v73 natural router error: {error}"); return "handled"
        try:
            from seed_v73_commands import handle_v73_command
            handled = handle_v73_command(user_message)
            if handled == "handled": return "handled"
        except Exception as error:
            print(f"v73 command error: {error}"); return "handled"
        return _seed_v73_previous_handle_chat_command(user_message,*args,**kwargs)
except Exception:
    pass

# v73.1 Voice command router fix.
try:
    _seed_v731_previous_handle_chat_command = handle_chat_command

    def handle_chat_command(user_message, *args, **kwargs):
        try:
            from seed_live_voice_v731 import handle_voice_command_v731
            handled = handle_voice_command_v731(user_message)
            if handled == "handled":
                return "handled"
        except Exception as error:
            print(f"v73.1 voice router error: {error}")
            return "handled"

        return _seed_v731_previous_handle_chat_command(user_message, *args, **kwargs)

except Exception:
    pass

# v74 Embodied Companion router.
try:
    _seed_v74_previous_handle_chat_command = handle_chat_command

    def handle_chat_command(user_message, *args, **kwargs):
        try:
            from seed_natural_intent_router_v74 import handle_natural_intent_v74
            handled = handle_natural_intent_v74(user_message)
            if handled == "handled":
                return "handled"
        except Exception as error:
            print(f"v74 natural router error: {error}")
            return "handled"

        try:
            from seed_v74_commands import handle_v74_command
            handled = handle_v74_command(user_message)
            if handled == "handled":
                return "handled"
        except Exception as error:
            print(f"v74 command error: {error}")
            return "handled"

        return _seed_v74_previous_handle_chat_command(user_message, *args, **kwargs)

except Exception:
    pass

# v75 Self-truth + Real Memory router.
try:
    _seed_v75_previous_handle_chat_command = handle_chat_command
    def handle_chat_command(user_message, *args, **kwargs):
        try:
            from seed_natural_intent_router_v75 import handle_natural_intent_v75
            handled = handle_natural_intent_v75(user_message)
            if handled == "handled": return "handled"
        except Exception as error:
            print(f"v75 natural router error: {error}"); return "handled"
        try:
            from seed_v75_commands import handle_v75_command
            handled = handle_v75_command(user_message)
            if handled == "handled": return "handled"
        except Exception as error:
            print(f"v75 command error: {error}"); return "handled"
        return _seed_v75_previous_handle_chat_command(user_message, *args, **kwargs)
except Exception:
    pass

# v81 V1-alpha mega stack router.
try:
    _seed_v81_previous_handle_chat_command = handle_chat_command

    def handle_chat_command(user_message, *args, **kwargs):
        try:
            from seed_natural_intent_router_v81 import handle_natural_intent_v81
            handled = handle_natural_intent_v81(user_message)
            if handled == "handled":
                return "handled"
        except Exception as error:
            print(f"v81 natural router error: {error}")
            return "handled"

        try:
            from seed_v81_commands import handle_v81_command
            handled = handle_v81_command(user_message)
            if handled == "handled":
                return "handled"
        except Exception as error:
            print(f"v81 command error: {error}")
            return "handled"

        return _seed_v81_previous_handle_chat_command(user_message, *args, **kwargs)

except Exception:
    pass

# v85 Real-v1 prep router.
try:
    _seed_v85_previous_handle_chat_command = handle_chat_command

    def handle_chat_command(user_message, *args, **kwargs):
        try:
            from seed_natural_intent_router_v85 import handle_natural_intent_v85
            handled = handle_natural_intent_v85(user_message)
            if handled == "handled":
                return "handled"
        except Exception as error:
            print(f"v85 natural router error: {error}")
            return "handled"

        try:
            from seed_v85_commands import handle_v85_command
            handled = handle_v85_command(user_message)
            if handled == "handled":
                return "handled"
        except Exception as error:
            print(f"v85 command error: {error}")
            return "handled"

        return _seed_v85_previous_handle_chat_command(user_message, *args, **kwargs)

except Exception:
    pass

# v86 Wake word router.
try:
    _seed_v86_previous_handle_chat_command = handle_chat_command

    def handle_chat_command(user_message, *args, **kwargs):
        try:
            from seed_natural_intent_router_v86 import handle_natural_intent_v86
            handled = handle_natural_intent_v86(user_message)
            if handled == "handled":
                return "handled"
        except Exception as error:
            print(f"v86 natural router error: {error}")
            return "handled"

        try:
            from seed_v86_commands import handle_v86_command
            handled = handle_v86_command(user_message)
            if handled == "handled":
                return "handled"
        except Exception as error:
            print(f"v86 command error: {error}")
            return "handled"

        return _seed_v86_previous_handle_chat_command(user_message, *args, **kwargs)

except Exception:
    pass

# v87 Alive companion router.
try:
    _seed_v87_previous_handle_chat_command = handle_chat_command

    def handle_chat_command(user_message, *args, **kwargs):
        try:
            from seed_natural_intent_router_v87 import handle_natural_intent_v87
            handled = handle_natural_intent_v87(user_message)
            if handled == "handled":
                return "handled"
        except Exception as error:
            print(f"v87 natural router error: {error}")
            return "handled"

        try:
            from seed_v87_commands import handle_v87_command
            handled = handle_v87_command(user_message)
            if handled == "handled":
                return "handled"
        except Exception as error:
            print(f"v87 command error: {error}")
            return "handled"

        return _seed_v87_previous_handle_chat_command(user_message, *args, **kwargs)

except Exception:
    pass

# v87.1 wake conversation router.
try:
    _seed_v871_previous_handle_chat_command = handle_chat_command

    def handle_chat_command(user_message, *args, **kwargs):
        try:
            from seed_natural_intent_router_v871 import handle_natural_intent_v871
            handled = handle_natural_intent_v871(user_message)
            if handled == "handled":
                return "handled"
        except Exception as error:
            print(f"v87.1 natural router error: {error}")
            return "handled"

        return _seed_v871_previous_handle_chat_command(user_message, *args, **kwargs)

except Exception:
    pass

# v88 Mac body + fast wake router.
try:
    _seed_v88_previous_handle_chat_command = handle_chat_command

    def handle_chat_command(user_message, *args, **kwargs):
        try:
            from seed_natural_intent_router_v88 import handle_natural_intent_v88
            handled = handle_natural_intent_v88(user_message)
            if handled == "handled":
                return "handled"
        except Exception as error:
            print(f"v88 natural router error: {error}")
            return "handled"

        return _seed_v88_previous_handle_chat_command(user_message, *args, **kwargs)

except Exception:
    pass

# v89 organism router.
try:
    _seed_v89_previous_handle_chat_command = handle_chat_command
    def handle_chat_command(user_message, *args, **kwargs):
        try:
            from seed_natural_intent_router_v89 import handle_natural_intent_v89
            handled = handle_natural_intent_v89(user_message)
            if handled == "handled":
                return "handled"
        except Exception as error:
            print(f"v89 natural router error: {error}")
            return "handled"
        return _seed_v89_previous_handle_chat_command(user_message, *args, **kwargs)
except Exception:
    pass

# v90 memory garden router.
try:
    _seed_v90_previous_handle_chat_command = handle_chat_command

    def handle_chat_command(user_message, *args, **kwargs):
        try:
            from seed_natural_intent_router_v90 import handle_natural_intent_v90
            handled = handle_natural_intent_v90(user_message)
            if handled == "handled":
                return "handled"
        except Exception as error:
            print(f"v90 natural router error: {error}")
            return "handled"
        return _seed_v90_previous_handle_chat_command(user_message, *args, **kwargs)
except Exception:
    pass

# v91 companion context router.
try:
    _seed_v91_previous_handle_chat_command = handle_chat_command

    def handle_chat_command(user_message, *args, **kwargs):
        try:
            from seed_natural_intent_router_v91 import handle_natural_intent_v91
            handled = handle_natural_intent_v91(user_message)
            if handled == "handled":
                return "handled"
        except Exception as error:
            print(f"v91 natural router error: {error}")
            return "handled"
        return _seed_v91_previous_handle_chat_command(user_message, *args, **kwargs)
except Exception:
    pass

# v92-v106 mega router.
try:
    _seed_v92_106_previous_handle_chat_command = handle_chat_command
    def handle_chat_command(user_message, *args, **kwargs):
        try:
            from seed_natural_intent_router_v92_106 import handle_natural_intent_v92_106
            handled = handle_natural_intent_v92_106(user_message)
            if handled == "handled":
                return "handled"
        except Exception as error:
            print(f"v92-v106 natural router error: {error}")
            return "handled"
        return _seed_v92_106_previous_handle_chat_command(user_message, *args, **kwargs)
except Exception:
    pass
