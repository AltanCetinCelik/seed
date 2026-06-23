
try:
    from seed_arsenal_commands import handle_arsenal_command, print_arsenal_help
    ARSENAL_COMMANDS_AVAILABLE = True
except Exception:
    ARSENAL_COMMANDS_AVAILABLE = False

    def handle_arsenal_command(command, chat_state=None):
        return None

    def print_arsenal_help():
        pass

import importlib


def call(module_name, function_name, *args):
    module = importlib.import_module(module_name)
    function = getattr(module, function_name)
    return function(*args)


def print_companion_os_help():
    print("\n=== Companion OS Alpha Commands ===")
    print("/companion-os = show Companion OS Alpha")
    print("/os-events = show Companion OS events")
    print("/os-journal = show Companion OS journal")
    print("/os-backup = backup Companion OS state")
    print("/os-registry = show OS command registry")
    print("/os-command-map = show command map")
    print("/os-command-owner = inspect command owner/risk")
    print("/os-risk-map = show command risk map")
    print("/os-registry-validate = validate registry")
    print("/os-migrate-preview = preview old Seed migration")
    print("/os-migrate = import old Seed state into Companion OS")
    print("/os-migrate-report = show migration report")
    print("/os-bridge-status = show OS bridge status")
    print("/os-bridge-events = bridge old event bus")
    print("/os-bridge-snapshots = bridge subsystem snapshots")
    print("/os-bridge-milestone = manually bridge milestone")
    print("/trace = show trace log")
    print("/trace-last = show last trace")
    print("/trace-stats = show trace stats")
    print("/why-did-you = explain from trace history")
    print("/tools-v2 = show Tool Manifest v2")
    print("/tool-v2 = inspect one tool")
    print("/tool-permissions = show tool approval policies")
    print("/tool-side-effects = show tool side effects")
    print("/tool-audit = audit tool manifest")
    print("/trust = show Trust Center")
    print("/guardian-review = Guardian review")
    print("/guardian-rules = show Guardian rules")
    print("/guardian-rule-add = add Guardian rule")
    print("/risk-report = show risk report")
    print("/safety-review = LLM safety review")
    print("/emergency-stop-all = enable global Companion OS emergency stop")
    print("/emergency-start-all = disable global Companion OS emergency stop")
    print("/fake-sentience-scan = scan core files for forbidden fake-sentience claims")
    print("/memory-backend = show memory backend")
    print("/memory-backend-set = set active memory backend")
    print("/layer-memory-add = add Companion OS layered memory")
    print("/layer-memory-search = search layered memory")
    print("/docs = show document registry")
    print("/doc-add = register approved local document")
    print("/doc-remove = remove registered document")
    print("/doc-summary = summarize registered document")
    print("/doc-search = search registered documents")
    print("/doc-context = show document context")
    print("/timeline-v2 = show Life Timeline")
    print("/timeline-add-v2 = add Life Timeline event")
    print("/timeline-recall = recall timeline")
    print("/shared-history = show shared history")
    print("/recall-pack = generate continuity recall pack")
    print("/recall-packs = show recall packs")
    print("/where-were-we = answer from continuity")
    print("/what-changed = answer recent changes")
    print("/continuity-answer = ask continuity engine")
    print("/life-timeline-summary = summarize life timeline")
    print("/workflow2-new = create durable workflow")
    print("/workflow2-show = show workflows")
    print("/workflow2-step-add = add workflow step")
    print("/workflow2-step-status = update workflow step")
    print("/workflow2-note = add workflow note")
    print("/workflow2-pause = pause workflow")
    print("/workflow2-resume = resume workflow")
    print("/workflow2-cancel = cancel workflow")
    print("/workflow2-complete = complete workflow")
    print("/council = run Microagent Council")
    print("/council-last = show last council")
    print("/council-history = show council history")
    print("/guardian-council-review = Guardian council review")
    print("/dependencies = build/show dependency graph")
    print("/impact-check = check file/module impact")
    print("/safe-tests = run safe compile tests")
    print("/upgrade-plan = create repo-aware upgrade plan")
    print("/patch-plan = create patch plan")
    print("/test-plan = create test plan")
    print("/release-manager = show release manager")
    print("/release-draft = draft release")
    print("/release-check = run release check")
    print("/release-notes = show latest release notes")
    print("/changelog = generate changelog")
    print("/save-milestone-text = print save-memory milestone text")
    print("/release-complete = mark release complete")
    print("/world2 = show Seed World")
    print("/garden2 = show Memory Garden")
    print("/world-events = show world events")
    print("/world-event = apply world event")
    print("/world-artifact = add world artifact")
    print("/world-place = change current world place")
    print("/world-explain = explain Seed World")
    print("/avatar = show avatar state")
    print("/avatar-mode = set avatar state")
    print("/avatar-for-mode = set avatar by mode")
    print("/avatar-test = test avatar state")
    print("/voice = show voice status")
    print("/voice-on = enable voice")
    print("/voice-off = disable voice")
    print("/voice-test = test voice")
    print("/voice-say = speak typed text")
    print("/voice-pulse = speak Companion OS pulse")
    print("/voice-ritual = speak ritual")
    print("/voice-history = show voice history")
    print("/cockpit2 = launch Companion OS cockpit")
    print("/v2-check = run v2 release gate")
    print("/v2-blockers = show v2 blockers")
    print("/v2-pass-report = show full v2 report")
    print("/v2-release-notes = draft v2 release notes")
    print("/agency-hardening = show Agency hardening status")
    print("/agency-queue = show approval queue")
    print("/agency-request = queue action approval request")
    print("/agency-approve = approve queued request without executing")
    print("/agency-reject = reject queued request")
    print("/agency-simulate = dry-run action simulation")
    print("/agency-simulations = show action simulation history")
    print("/autonomy-ladder = show autonomy ladder")
    print("/autonomy-set = set allowed autonomy level")
    print("/agency-emergency = show emergency bridge")
    print("/agency-tool-decision = explain tool decision")
    print("/self-hardening = show self-improvement hardening status")
    print("/module-health = build/show module health matrix")
    print("/test-matrix = run self-improvement test matrix")
    print("/repair-plan = build self-improvement repair plan")
    print("/release-readiness = build self-improvement release readiness report")
    print("/hardening-suite = run self-improvement hardening suite")
    print("/voice-hardening = show voice hardening status")
    print("/voice-hardening-suite = run voice hardening suite")
    print("/voice-privacy = run voice privacy check")
    print("/voice-capabilities = show voice capability report")
    print("/voice-session-start = start explicit voice session")
    print("/voice-session-end = end explicit voice session")
    print("/voice-sessions = show voice hardening sessions")
    print("/voice-transcript-add = add transcript placeholder")
    print("/voice-transcripts = show transcript placeholders")
    print("/voice-pulse-dry = dry-run voice pulse without speaking")
    print("/voice-ritual-check = dry-run voice ritual support")
    print("/voice-output-check = optional spoken output check")
    print("/cockpit-hardening = show cockpit hardening status")
    print("/cockpit-actions = show cockpit action definitions")
    print("/cockpit-action = run cockpit action from CLI")
    print("/cockpit-log = show cockpit action log")
    print("/cockpit-self-test = run cockpit hardening self-test")


def handle_companion_os_command(command, chat_state=None):
    try:
        arsenal_result = handle_arsenal_command(command, chat_state)
        if arsenal_result == "handled":
            return "handled"
    except Exception as error:
        print(f"Arsenal command error: {error}")
        return "handled"

    command = command.strip()

    no_arg_commands = {
        "/companion-os": ("seed_companion_os", "show_companion_os"),
        "/os-events": ("seed_companion_os", "show_companion_os_events"),
        "/os-journal": ("seed_companion_os", "show_companion_os_journal"),
        "/os-backup": ("seed_companion_os", "backup_companion_os_state"),

        "/os-registry": ("seed_os_registry", "show_os_registry"),
        "/os-command-map": ("seed_os_registry", "show_os_command_map"),
        "/os-command-owner": ("seed_os_registry", "show_os_command_owner"),
        "/os-risk-map": ("seed_os_registry", "show_os_risk_map"),
        "/os-registry-validate": ("seed_os_registry", "show_registry_validation"),

        "/os-migrate-preview": ("seed_os_migrations", "show_migration_preview"),
        "/os-migrate": ("seed_os_migrations", "migrate_all"),
        "/os-migrate-report": ("seed_os_migrations", "show_migration_report"),

        "/os-bridge-status": ("seed_os_bridge", "show_bridge_status"),
        "/os-bridge-events": ("seed_os_bridge", "bridge_legacy_event_bus"),
        "/os-bridge-snapshots": ("seed_os_bridge", "bridge_subsystem_snapshots"),
        "/os-bridge-milestone": ("seed_os_bridge", "bridge_milestone_interactive"),

        "/trace": ("seed_trace_engine", "show_trace_log"),
        "/trace-last": ("seed_trace_engine", "show_last_trace"),
        "/trace-stats": ("seed_trace_engine", "show_trace_stats"),
        "/why-did-you": ("seed_trace_engine", "why_did_you_interactive"),

        "/tools-v2": ("seed_tool_manifest_v2", "show_tools_v2"),
        "/tool-v2": ("seed_tool_manifest_v2", "show_tool_v2"),
        "/tool-permissions": ("seed_tool_manifest_v2", "show_tool_permissions"),
        "/tool-side-effects": ("seed_tool_manifest_v2", "show_tool_side_effects"),
        "/tool-audit": ("seed_tool_manifest_v2", "show_tool_audit"),

        "/trust": ("seed_trust_center", "show_trust_center"),
        "/guardian-review": ("seed_trust_center", "guardian_review_interactive"),
        "/guardian-rules": ("seed_trust_center", "show_guardian_rules"),
        "/guardian-rule-add": ("seed_trust_center", "add_guardian_rule_interactive"),
        "/risk-report": ("seed_trust_center", "show_risk_report"),
        "/emergency-stop-all": ("seed_trust_center", "emergency_stop_all"),
        "/emergency-start-all": ("seed_trust_center", "emergency_start_all"),
        "/fake-sentience-scan": ("seed_trust_center", "show_fake_sentience_scan"),
        "/why-action": ("seed_trust_center", "why_action_interactive"),

        "/memory-backend": ("seed_memory_backend", "show_memory_backend_status"),
        "/memory-backend-set": ("seed_memory_backend", "set_active_backend_interactive"),
        "/layer-memory-add": ("seed_memory_backend", "add_layered_memory_interactive"),
        "/layer-memory-search": ("seed_memory_backend", "search_layered_memory_interactive"),

        "/docs": ("seed_document_registry", "show_documents"),
        "/doc-add": ("seed_document_registry", "add_document_interactive"),
        "/doc-remove": ("seed_document_registry", "remove_document_interactive"),
        "/doc-search": ("seed_document_registry", "search_documents_interactive"),
        "/doc-context": ("seed_document_registry", "document_context_interactive"),

        "/timeline-v2": ("seed_continuity_engine", "show_timeline"),
        "/timeline-add-v2": ("seed_continuity_engine", "add_timeline_event_interactive"),
        "/timeline-recall": ("seed_continuity_engine", "recall_timeline_interactive"),
        "/shared-history": ("seed_continuity_engine", "show_shared_history"),
        "/recall-packs": ("seed_continuity_engine", "show_recall_packs"),
        "/life-timeline-summary": ("seed_continuity_engine", "create_life_timeline_summary"),

        "/workflow2-new": ("seed_workflow_engine", "create_workflow_interactive"),
        "/workflow2-show": ("seed_workflow_engine", "show_workflows"),
        "/workflow2-step-add": ("seed_workflow_engine", "add_workflow_step_interactive"),
        "/workflow2-step-status": ("seed_workflow_engine", "set_step_status_interactive"),
        "/workflow2-note": ("seed_workflow_engine", "add_workflow_note_interactive"),
        "/workflow2-pause": ("seed_workflow_engine", "pause_workflow_interactive"),
        "/workflow2-resume": ("seed_workflow_engine", "resume_workflow_interactive"),
        "/workflow2-cancel": ("seed_workflow_engine", "cancel_workflow_interactive"),
        "/workflow2-complete": ("seed_workflow_engine", "complete_workflow_interactive"),

        "/council-last": ("seed_microagent_council", "show_last_council"),
        "/council-history": ("seed_microagent_council", "show_council_history"),

        "/dependencies": ("seed_self_improvement_engine", "show_dependencies"),
        "/impact-check": ("seed_self_improvement_engine", "impact_check_interactive"),
        "/safe-tests": ("seed_self_improvement_engine", "show_safe_tests"),

        "/release-manager": ("seed_release_manager", "show_release_manager"),
        "/release-check": ("seed_release_manager", "show_release_check"),
        "/release-notes": ("seed_release_manager", "show_release_notes"),
        "/changelog": ("seed_release_manager", "generate_changelog"),
        "/save-milestone-text": ("seed_release_manager", "save_milestone_text"),
        "/release-complete": ("seed_release_manager", "mark_release_completed_interactive"),

        "/world2": ("seed_world_engine", "show_world"),
        "/garden2": ("seed_world_engine", "show_memory_garden"),
        "/world-events": ("seed_world_engine", "show_world_events"),
        "/world-event": ("seed_world_engine", "apply_world_event_interactive"),
        "/world-artifact": ("seed_world_engine", "add_world_artifact_interactive"),
        "/world-place": ("seed_world_engine", "set_world_place_interactive"),
        "/world-explain": ("seed_world_engine", "explain_world_state"),

        "/avatar": ("seed_avatar_state", "show_avatar_state"),
        "/avatar-mode": ("seed_avatar_state", "set_avatar_state_interactive"),
        "/avatar-for-mode": ("seed_avatar_state", "avatar_for_mode_interactive"),
        "/avatar-test": ("seed_avatar_state", "avatar_test"),

        "/voice": ("seed_voice_session", "show_voice_status"),
        "/voice-on": ("seed_voice_session", "voice_on"),
        "/voice-off": ("seed_voice_session", "voice_off"),
        "/voice-test": ("seed_voice_session", "voice_test"),
        "/voice-say": ("seed_voice_session", "speak_text_interactive"),
        "/voice-ritual": ("seed_voice_session", "voice_ritual"),
        "/voice-history": ("seed_voice_session", "show_voice_history"),

        "/cockpit2": ("seed_companion_cockpit", "run_companion_cockpit"),

        "/v2-check": ("seed_v2_release_gate", "show_v2_check"),
        "/v2-blockers": ("seed_v2_release_gate", "show_v2_blockers"),
        "/v2-pass-report": ("seed_v2_release_gate", "show_v2_pass_report"),
        "/v2-release-notes": ("seed_v2_release_gate", "generate_v2_release_notes"),
        "/agency-hardening": ("seed_agency_hardening", "show_agency_hardening_status"),
        "/agency-queue": ("seed_agency_hardening", "show_approval_queue"),
        "/agency-request": ("seed_agency_hardening", "request_action_approval_interactive"),
        "/agency-approve": ("seed_agency_hardening", "approve_request_interactive"),
        "/agency-reject": ("seed_agency_hardening", "reject_request_interactive"),
        "/agency-simulate": ("seed_agency_hardening", "simulate_action_interactive"),
        "/agency-simulations": ("seed_agency_hardening", "show_simulation_history"),
        "/autonomy-ladder": ("seed_agency_hardening", "show_autonomy_ladder"),
        "/autonomy-set": ("seed_agency_hardening", "set_autonomy_level_interactive"),
        "/agency-emergency": ("seed_agency_hardening", "show_emergency_bridge"),
        "/agency-tool-decision": ("seed_agency_hardening", "tool_decision_interactive"),
        "/self-hardening": ("seed_self_improvement_hardening", "show_self_improvement_hardening_status"),
        "/module-health": ("seed_self_improvement_hardening", "show_module_health_matrix"),
        "/test-matrix": ("seed_self_improvement_hardening", "show_test_matrix"),
        "/release-readiness": ("seed_self_improvement_hardening", "show_release_readiness_report"),
        "/voice-hardening": ("seed_voice_hardening", "show_voice_hardening_status"),
        "/voice-privacy": ("seed_voice_hardening", "show_voice_privacy_check"),
        "/voice-capabilities": ("seed_voice_hardening", "show_voice_capability_report"),
        "/voice-session-start": ("seed_voice_hardening", "start_voice_session_interactive"),
        "/voice-session-end": ("seed_voice_hardening", "end_voice_session_interactive"),
        "/voice-sessions": ("seed_voice_hardening", "show_voice_sessions"),
        "/voice-transcript-add": ("seed_voice_hardening", "add_transcript_placeholder_interactive"),
        "/voice-transcripts": ("seed_voice_hardening", "show_transcript_placeholders"),
        "/voice-ritual-check": ("seed_voice_hardening", "ritual_check"),
        "/voice-output-check": ("seed_voice_hardening", "voice_output_check_interactive"),
        "/cockpit-hardening": ("seed_cockpit_actions", "show_cockpit_hardening_status"),
        "/cockpit-actions": ("seed_cockpit_actions", "show_cockpit_actions"),
        "/cockpit-action": ("seed_cockpit_actions", "execute_cockpit_action_interactive"),
        "/cockpit-log": ("seed_cockpit_actions", "show_cockpit_action_log"),
        "/cockpit-self-test": ("seed_cockpit_actions", "show_cockpit_self_test"),
    }

    chat_commands = {
        "/safety-review": ("seed_trust_center", "safety_review"),
        "/doc-summary": ("seed_document_registry", "summarize_document_interactive"),
        "/recall-pack": ("seed_continuity_engine", "build_recall_pack"),
        "/where-were-we": ("seed_continuity_engine", "where_were_we"),
        "/what-changed": ("seed_continuity_engine", "what_changed"),
        "/continuity-answer": ("seed_continuity_engine", "continuity_answer_interactive"),
        "/council": ("seed_microagent_council", "council_interactive"),
        "/guardian-council-review": ("seed_microagent_council", "guardian_council_review_interactive"),
        "/upgrade-plan": ("seed_self_improvement_engine", "upgrade_plan_interactive"),
        "/patch-plan": ("seed_self_improvement_engine", "patch_plan_interactive"),
        "/test-plan": ("seed_self_improvement_engine", "test_plan_interactive"),
        "/release-draft": ("seed_release_manager", "draft_release_interactive"),
        "/voice-pulse": ("seed_voice_session", "voice_pulse"),
        "/repair-plan": ("seed_self_improvement_hardening", "show_repair_plan"),
        "/hardening-suite": ("seed_self_improvement_hardening", "run_self_improvement_hardening_suite"),
        "/voice-hardening-suite": ("seed_voice_hardening", "run_voice_hardening_suite"),
        "/voice-pulse-dry": ("seed_voice_hardening", "dry_run_voice_pulse"),
    }

    if command in no_arg_commands:
        module_name, function_name = no_arg_commands[command]
        call(module_name, function_name)
        return "handled"

    if command in chat_commands:
        module_name, function_name = chat_commands[command]
        call(module_name, function_name, chat_state)
        return "handled"

    return None
