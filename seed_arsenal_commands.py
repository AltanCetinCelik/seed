def print_arsenal_help():
    print("/policy = show v5 execution policy")
    print("/policy-check = check action policy")
    print("/capability-graph = show capability graph")
    print("/capability-route = route text to capabilities")
    print("/task-list = show Task OS queue")
    print("/task-create = create manual task")
    print("/task-done = mark task done")
    print("/operator-goal = plan goal into task queue")
    print("/operator-status = show Operator Runtime status")
    print("/operator-tick = run one manual operator tick")
    print("/inbox = show operator inbox")
    print("/inbox-add = add note/goal to operator inbox")
    print("/v50-check = run v5 Operator Core gate")
    print("/event-bus = show Seed event bus")
    print("/service-status = show local Seed services")
    print("/service-start = start allowlisted local service")
    print("/service-stop = stop allowlisted local service")
    print("/mcp-client = call Seed MCP client self-test")
    print("/workflow-list = show workflow automation list")
    print("/workflow-run = run allowlisted workflow")
    print("/checkpoint-create = create rollback checkpoint")
    print("/checkpoint-status = show rollback checkpoints")
    print("/checkpoint-restore = restore checkpoint with token")
    print("/memory-distill = build runtime memory distill")
    print("/aider-patch-flow = create checkpointed Aider patch flow")
    print("/v40-check = run v4.0 runtime OS gate")
    print("/mcp-skill-server = show MCP skill server self-test")
    print("/mcp-manifest = generate MCP skill manifest")
    print("/aider-unlock-status = show Aider real unlock status")
    print("/aider-unlock-plan = create approved Aider dry-run/real plan")
    print("/aider-unlock-approve = approve latest Aider unlock plan")
    print("/aider-unlock-execute = execute approved Aider unlock plan")
    print("/integration-sandbox = create integration sandbox")
    print("/v36-check = run v3.6 real integration gate")
    print("/repo-dna = build and show Seed repo DNA")
    print("/integration-fusion = fuse repo references and friend advice")
    print("/omega-plan = show Omega integration plan")
    print("/control-actions = show/run local control plane actions")
    print("/voice-one-shot = run one-shot voice intent planner")
    print("/v35-check = run v3.5 Omega integration gate")
    print("/control-plane = start local control plane server in foreground")
    print("/control-plane-open = start control plane in background and open browser")
    print("/control-plane-status = show control plane status")
    print("/gate-matrix = run full gate matrix")
    print("/runtime-supervisor = show runtime supervisor")
    print("/timeline = show session timeline")
    print("/command-center = show v3 command center")
    print("/v30-check = run v3.0 control plane gate")
    print("/mission-control = show Seed mission control dashboard")
    print("/release-orchestrate = run safe release orchestrator")
    print("/voice-ux = show voice UX pack")
    print("/voice-transcript-add = add transcript journal item")
    print("/voice-transcripts = show transcript journal")
    print("/self-repair-plan = build read-only self-repair plan")
    print("/command-memory = show command memory")
    print("/command-suggest = suggest command stack")
    print("/app-manifest = show local app/tool manifest")
    print("/v29-check = run v2.9 mission control gate")
    print("/aider-status = show Aider bridge status")
    print("/aider-install-plan = show manual Aider install plan")
    print("/aider-preflight = run Aider preflight")
    print("/aider-plan = create manual-only Aider plan")
    print("/v28-check = run v2.8 Aider bridge gate")
    print("/executor-registry = show external executor registry")
    print("/executor-plan = create manual executor plan")
    print("/repo-doctor = run read-only repo doctor")
    print("/voice-upgrade-plan = show voice upgrade plan")
    print("/v27-check = run v2.7 executor bridge gate")
    print("/agent-operator = show supervised agent operator console")
    print("/agent-tools-real = detect real local agent tools")
    print("/agent-run-create = create supervised agent run")
    print("/agent-run-list = list supervised agent runs")
    print("/agent-run-show = show supervised agent run")
    print("/agent-run-approve = approve supervised agent run")
    print("/agent-run-execute = execute approved supervised agent run")
    print("/v26-check = run v2.6 supervised agent execution gate")
    print("/skills = show real Seed skills")
    print("/skill-run = run a real skill manually")
    print("/skill-history = show real skill history")
    print("/git-status = run git status skill")
    print("/git-diff = run git diff stat skill")
    print("/repo-summary = inspect Seed repo")
    print("/repo-todos = inspect TODO/FIXME/HACK markers")
    print("/fs-list = list project files")
    print("/fs-search = search project files")
    print("/safe-skill-diagnostic = run safe skill diagnostics")
    print("/coding-prep = prepare approval-gated coding-agent task")
    print("/v25-check = run v2.5 real skill gate")
    print("/seed-home = show smooth Seed home screen")
    print("/experience = show Seed experience modes")
    print("/mode = switch Seed experience mode")
    print("/reference-fusion = show repo/friend/internet reference fusion")
    print("/almost-perfect-plan = show Seed almost-perfect build plan")
    print("/smooth-ux = show smooth UX state")
    print("/v24-check = run v2.4 experience fusion gate")
    print("/semantic-index = build semantic memory/repo index")
    print("/semantic-search = semantic search memory/repo/docs")
    print("/semantic-add = add semantic memory note")
    print("/workflow-plan = show workflow brain plan")
    print("/workflow-context = show workflow brain context")
    print("/v23-check = run v2.3 real intelligence gate")
    print("/action-kernel = show registered verified actions")
    print("/action-test = run action kernel safe diagnostic")
    print("/action-history = show verified action history")
    print("/memory-index = build local memory/repo search index")
    print("/memory-search = search local memory/repo/docs")
    print("/memory-add = add local capability memory note")
    print("/mcp-gateway = show MCP gateway")
    print("/mcp-plan = build MCP plan")
    print("/coding-gateway = show coding-agent gateway")
    print("/coding-plan = build coding-agent plan")
    print("/browser-gateway = show browser-agent gateway")
    print("/browser-plan = build browser-agent plan")
    print("/voice-quality = classify voice transcript quality")
    print("/v22-check = run v2.2 mega capability gate")
    print("/open-cockpit = start/open Cockpit in browser")
    print("/active-voice-check = check real active voice readiness")
    print("/active-voice = start real active voice wake loop")
    print("/active-voice-once = record one voice command")
    print("/active-voice-devices = list macOS microphone devices")
    print("/active-voice-device = set macOS audio device")
    print("/active-voice-install-plan = show active voice install plan")
    print("/active-voice-history = show active voice history")
    print("/agent-tools = show installed/detected agent tool profiles")
    print("/agent-install-plan = show optional agent install plan")
    print("/agent-task = plan task and optionally queue agent approval")
    print("/agent-plan = show agent task plan without queueing")
    print("/agent-diagnostic = run safe agent diagnostics")
    print("/v21-check = run Seed v2.1 capability gate")
    print("/voice-command = start Seed v2.0 voice command bridge")
    print("/voice-command-check = check voice command bridge readiness")
    print("/voice-command-history = show voice command history")
    print("/voice-command-record-test = test optional recorded STT command")
    print("/voice-command-install-plan = show optional STT install plan")
    print("/voice-command-launcher = create desktop launcher files")
    print("/launcher-status = show desktop launcher status")
    print("/v2-stable-check = run Seed v2.0 stable release gate")
    print("/v2-lock = lock Seed v2.0 stable release if checks pass")
    print("/repo-arsenal = show known repo/tool arsenal")
    print("/tool-arsenal = same as repo arsenal")
    print("/repo-map = show arsenal categories")
    print("/repo-search = search arsenal")
    print("/tool-route = route task to best tool/capability")
    print("/capability-match = build capability plan")
    print("/sandbox-plan = build sandbox/approval plan")
    print("/integration-readiness = show arsenal readiness")
    print("/integration-gate = run v1.19 arsenal integration gate")
    print("/friend-advice = show friend advice registry")
    print("/friend-advice-search = search friend advice")


def handle_arsenal_command(command, chat_state=None):
    command = command.strip()

    if command == "/repo-arsenal" or command == "/tool-arsenal":
        from seed_repo_arsenal import show_repo_arsenal
        show_repo_arsenal()
        return "handled"

    if command == "/repo-map":
        from seed_repo_arsenal import show_repo_map
        show_repo_map()
        return "handled"

    if command == "/repo-search":
        from seed_repo_arsenal import search_arsenal_interactive
        search_arsenal_interactive()
        return "handled"

    if command == "/tool-route":
        from seed_tool_router import show_tool_route
        show_tool_route()
        return "handled"

    if command == "/capability-match":
        from seed_capability_planner import show_capability_match
        show_capability_match()
        return "handled"

    if command == "/sandbox-plan":
        from seed_capability_planner import show_sandbox_plan
        show_sandbox_plan()
        return "handled"

    if command == "/integration-readiness":
        from seed_repo_arsenal import show_integration_readiness
        show_integration_readiness()
        return "handled"

    if command == "/integration-gate":
        from seed_integration_gate import show_integration_gate
        show_integration_gate()
        return "handled"

    if command == "/friend-advice":
        from seed_friend_advice_registry import show_friend_advice
        show_friend_advice()
        return "handled"

    if command == "/friend-advice-search":
        from seed_friend_advice_registry import search_friend_advice_interactive
        search_friend_advice_interactive()
        return "handled"


    if command == "/voice-command":
        from seed_voice_command_bridge import voice_command_loop
        voice_command_loop()
        return "handled"

    if command == "/voice-command-check":
        from seed_voice_command_bridge import show_voice_command_check
        show_voice_command_check()
        return "handled"

    if command == "/voice-command-history":
        from seed_voice_command_bridge import show_voice_command_history
        show_voice_command_history()
        return "handled"

    if command == "/voice-command-record-test":
        from seed_voice_command_bridge import voice_command_record_test
        voice_command_record_test()
        return "handled"

    if command == "/voice-command-install-plan":
        from seed_voice_command_bridge import voice_command_install_plan
        voice_command_install_plan()
        return "handled"

    if command == "/voice-command-launcher":
        from seed_desktop_launcher import create_desktop_launchers
        create_desktop_launchers()
        return "handled"

    if command == "/launcher-status":
        from seed_desktop_launcher import show_launcher_status
        show_launcher_status()
        return "handled"

    if command == "/v2-stable-check":
        from seed_v2_stable_release import show_v2_stable_gate
        show_v2_stable_gate()
        return "handled"

    if command == "/v2-lock":
        from seed_v2_stable_release import lock_v2_stable_release
        lock_v2_stable_release()
        return "handled"



    if command == "/active-voice-check":
        from seed_active_voice_daemon import show_active_voice_check
        show_active_voice_check()
        return "handled"

    if command == "/active-voice":
        from seed_active_voice_daemon import active_voice_loop
        active_voice_loop()
        return "handled"

    if command == "/active-voice-once":
        from seed_active_voice_daemon import active_voice_once
        active_voice_once()
        return "handled"

    if command == "/active-voice-devices":
        from seed_active_voice_daemon import list_macos_audio_devices
        list_macos_audio_devices()
        return "handled"

    if command == "/active-voice-device":
        from seed_active_voice_daemon import set_audio_device_interactive
        set_audio_device_interactive()
        return "handled"

    if command == "/active-voice-install-plan":
        from seed_active_voice_daemon import active_voice_install_plan
        active_voice_install_plan()
        return "handled"

    if command == "/active-voice-history":
        from seed_active_voice_daemon import show_active_voice_history
        show_active_voice_history()
        return "handled"

    if command == "/agent-tools":
        from seed_agent_tool_profiles import show_agent_tool_profiles
        show_agent_tool_profiles()
        return "handled"

    if command == "/agent-install-plan":
        from seed_agent_tool_profiles import show_agent_install_plan
        show_agent_install_plan()
        return "handled"

    if command == "/agent-task":
        from seed_agent_orchestrator import run_agent_task_interactive
        run_agent_task_interactive()
        return "handled"

    if command == "/agent-plan":
        from seed_agent_orchestrator import show_agent_task_plan
        show_agent_task_plan()
        return "handled"

    if command == "/agent-diagnostic":
        from seed_agent_executor import show_agent_diagnostic
        show_agent_diagnostic()
        return "handled"

    if command == "/v21-check":
        from seed_v21_capability_gate import show_v21_gate
        show_v21_gate()
        return "handled"



    if command == "/open-cockpit":
        from seed_cockpit_browser_action import show_open_cockpit_browser
        show_open_cockpit_browser()
        return "handled"



    if command == "/action-kernel":
        from seed_action_kernel import show_action_kernel
        show_action_kernel()
        return "handled"

    if command == "/action-test":
        from seed_action_kernel import show_action_test
        show_action_test()
        return "handled"

    if command == "/action-history":
        from seed_action_kernel import show_action_history
        show_action_history()
        return "handled"

    if command == "/memory-index":
        from seed_capability_memory import show_memory_index
        show_memory_index()
        return "handled"

    if command == "/memory-search":
        from seed_capability_memory import show_memory_search
        show_memory_search()
        return "handled"

    if command == "/memory-add":
        from seed_capability_memory import show_memory_add
        show_memory_add()
        return "handled"

    if command == "/mcp-gateway":
        from seed_mcp_gateway import show_mcp_gateway
        show_mcp_gateway()
        return "handled"

    if command == "/mcp-plan":
        from seed_mcp_gateway import show_mcp_plan
        show_mcp_plan()
        return "handled"

    if command == "/coding-gateway":
        from seed_coding_agent_gateway import show_coding_gateway
        show_coding_gateway()
        return "handled"

    if command == "/coding-plan":
        from seed_coding_agent_gateway import show_coding_plan
        show_coding_plan()
        return "handled"

    if command == "/browser-gateway":
        from seed_browser_agent_gateway import show_browser_gateway
        show_browser_gateway()
        return "handled"

    if command == "/browser-plan":
        from seed_browser_agent_gateway import show_browser_plan
        show_browser_plan()
        return "handled"

    if command == "/voice-quality":
        from seed_voice_quality_router import show_voice_quality
        show_voice_quality()
        return "handled"

    if command == "/v22-check":
        from seed_v22_mega_gate import show_v22_gate
        show_v22_gate()
        return "handled"



    if command == "/semantic-index":
        from seed_semantic_memory import show_semantic_index
        show_semantic_index()
        return "handled"

    if command == "/semantic-search":
        from seed_semantic_memory import show_semantic_search
        show_semantic_search()
        return "handled"

    if command == "/semantic-add":
        from seed_semantic_memory import show_semantic_add
        show_semantic_add()
        return "handled"

    if command == "/workflow-plan":
        from seed_workflow_brain import show_workflow_plan
        show_workflow_plan()
        return "handled"

    if command == "/workflow-context":
        from seed_workflow_brain import show_workflow_context
        show_workflow_context()
        return "handled"

    if command == "/v23-check":
        from seed_v23_intelligence_gate import show_v23_gate
        show_v23_gate()
        return "handled"



    if command == "/seed-home":
        from seed_smooth_ux import show_seed_home
        show_seed_home()
        return "handled"

    if command == "/experience":
        from seed_experience_modes import show_experience_modes
        show_experience_modes()
        return "handled"

    if command == "/mode":
        from seed_experience_modes import show_set_mode
        show_set_mode()
        return "handled"

    if command == "/reference-fusion":
        from seed_reference_fusion import show_reference_fusion
        show_reference_fusion()
        return "handled"

    if command == "/almost-perfect-plan":
        from seed_reference_fusion import show_almost_perfect_plan
        show_almost_perfect_plan()
        return "handled"

    if command == "/smooth-ux":
        from seed_smooth_ux import show_smooth_ux
        show_smooth_ux()
        return "handled"

    if command == "/v24-check":
        from seed_v24_experience_gate import show_v24_gate
        show_v24_gate()
        return "handled"



    if command == "/skills":
        from seed_skill_kernel import show_skills
        show_skills()
        return "handled"

    if command == "/skill-run":
        from seed_skill_kernel import show_run_skill
        show_run_skill()
        return "handled"

    if command == "/skill-history":
        from seed_skill_kernel import show_skill_history
        show_skill_history()
        return "handled"

    if command == "/git-status":
        from seed_skill_kernel import run_skill
        import json
        print(json.dumps(run_skill("git", "status"), indent=4))
        return "handled"

    if command == "/git-diff":
        from seed_skill_kernel import run_skill
        import json
        print(json.dumps(run_skill("git", "diff_stat"), indent=4))
        return "handled"

    if command == "/repo-summary":
        from seed_skill_kernel import run_skill
        import json
        print(json.dumps(run_skill("repo", "summary"), indent=4))
        return "handled"

    if command == "/repo-todos":
        from seed_skill_kernel import run_skill
        import json
        print(json.dumps(run_skill("repo", "todos"), indent=4))
        return "handled"

    if command == "/fs-list":
        from seed_skill_kernel import run_skill
        import json
        print(json.dumps(run_skill("filesystem", "list", {"path": "."}), indent=4))
        return "handled"

    if command == "/fs-search":
        from seed_skill_kernel import run_skill
        import json
        query = input("Search files for: ").strip()
        print(json.dumps(run_skill("filesystem", "search", {"query": query, "path": "."}), indent=4))
        return "handled"

    if command == "/safe-skill-diagnostic":
        from seed_skill_kernel import run_skill
        import json
        print(json.dumps(run_skill("safe_shell", "diagnostic"), indent=4))
        return "handled"

    if command == "/coding-prep":
        from seed_skill_kernel import run_skill
        import json
        task = input("Coding task to prepare: ").strip()
        print(json.dumps(run_skill("coding_prep", "prepare", {"task": task}), indent=4))
        return "handled"

    if command == "/v25-check":
        from seed_v25_skill_gate import show_v25_gate
        show_v25_gate()
        return "handled"



    if command == "/agent-operator":
        from seed_agent_operator_console import show_agent_operator_home
        show_agent_operator_home()
        return "handled"

    if command == "/agent-tools-real":
        from seed_agent_run_lifecycle import show_agent_tools
        show_agent_tools()
        return "handled"

    if command == "/agent-run-create":
        from seed_agent_run_lifecycle import show_agent_run_create
        show_agent_run_create()
        return "handled"

    if command == "/agent-run-list":
        from seed_agent_run_lifecycle import show_agent_run_list
        show_agent_run_list()
        return "handled"

    if command == "/agent-run-show":
        from seed_agent_run_lifecycle import show_agent_run_show
        show_agent_run_show()
        return "handled"

    if command == "/agent-run-approve":
        from seed_agent_run_lifecycle import show_agent_run_approve
        show_agent_run_approve()
        return "handled"

    if command == "/agent-run-execute":
        from seed_agent_run_lifecycle import show_agent_run_execute
        show_agent_run_execute()
        return "handled"

    if command == "/v26-check":
        from seed_v26_agent_gate import show_v26_gate
        show_v26_gate()
        return "handled"



    if command == "/executor-registry":
        from seed_external_executor_bridge import show_executor_registry
        show_executor_registry()
        return "handled"

    if command == "/executor-plan":
        from seed_external_executor_bridge import show_executor_plan
        show_executor_plan()
        return "handled"

    if command == "/repo-doctor":
        from seed_repo_doctor import show_repo_doctor
        show_repo_doctor()
        return "handled"

    if command == "/voice-upgrade-plan":
        from seed_voice_upgrade_planner import show_voice_upgrade_plan
        show_voice_upgrade_plan()
        return "handled"

    if command == "/v27-check":
        from seed_v27_executor_gate import show_v27_gate
        show_v27_gate()
        return "handled"



    if command == "/aider-status":
        from seed_aider_bridge import show_aider_status
        show_aider_status()
        return "handled"

    if command == "/aider-install-plan":
        from seed_aider_bridge import show_aider_install_plan
        show_aider_install_plan()
        return "handled"

    if command == "/aider-preflight":
        from seed_aider_bridge import show_aider_preflight
        show_aider_preflight()
        return "handled"

    if command == "/aider-plan":
        from seed_aider_bridge import show_aider_plan
        show_aider_plan()
        return "handled"

    if command == "/v28-check":
        from seed_v28_aider_gate import show_v28_gate
        show_v28_gate()
        return "handled"



    if command == "/mission-control":
        from seed_mission_control import show_mission_control
        show_mission_control()
        return "handled"

    if command == "/release-orchestrate":
        from seed_release_orchestrator import show_release_orchestrator
        show_release_orchestrator()
        return "handled"

    if command == "/voice-ux":
        from seed_voice_ux_pack import show_voice_ux
        show_voice_ux()
        return "handled"

    if command == "/voice-transcript-add":
        from seed_voice_ux_pack import show_transcript_add
        show_transcript_add()
        return "handled"

    if command == "/voice-transcripts":
        from seed_voice_ux_pack import show_transcripts
        show_transcripts()
        return "handled"

    if command == "/self-repair-plan":
        from seed_self_repair_planner import show_self_repair_plan
        show_self_repair_plan()
        return "handled"

    if command == "/command-memory":
        from seed_command_memory import show_command_memory
        show_command_memory()
        return "handled"

    if command == "/command-suggest":
        from seed_command_memory import show_command_suggestions
        show_command_suggestions()
        return "handled"

    if command == "/app-manifest":
        from seed_local_app_manifest import show_app_manifest
        show_app_manifest()
        return "handled"

    if command == "/v29-check":
        from seed_v29_mission_gate import show_v29_gate
        show_v29_gate()
        return "handled"



    if command == "/control-plane":
        from seed_control_plane_server import run_control_plane
        run_control_plane()
        return "handled"

    if command == "/control-plane-open":
        from seed_control_plane_launcher import show_control_plane_open
        show_control_plane_open()
        return "handled"

    if command == "/control-plane-status":
        from seed_control_plane_launcher import show_control_plane_status
        show_control_plane_status()
        return "handled"

    if command == "/gate-matrix":
        from seed_gate_matrix import show_gate_matrix
        show_gate_matrix()
        return "handled"

    if command == "/runtime-supervisor":
        from seed_runtime_supervisor import show_runtime_supervisor
        show_runtime_supervisor()
        return "handled"

    if command == "/timeline":
        from seed_session_timeline import show_timeline
        show_timeline()
        return "handled"

    if command == "/command-center":
        from seed_command_center import show_command_center
        show_command_center()
        return "handled"

    if command == "/v30-check":
        from seed_v30_control_gate import show_v30_gate
        show_v30_gate()
        return "handled"



    if command == "/repo-dna":
        from seed_repo_dna_engine import show_repo_dna
        show_repo_dna()
        return "handled"

    if command == "/integration-fusion":
        from seed_integration_fusion_engine import show_integration_fusion
        show_integration_fusion()
        return "handled"

    if command == "/omega-plan":
        from seed_omega_planner import show_omega_plan
        show_omega_plan()
        return "handled"

    if command == "/control-actions":
        from seed_control_plane_actions import show_control_action
        show_control_action()
        return "handled"

    if command == "/voice-one-shot":
        from seed_voice_one_shot import show_voice_one_shot
        show_voice_one_shot()
        return "handled"

    if command == "/v35-check":
        from seed_v35_omega_gate import show_v35_gate
        show_v35_gate()
        return "handled"



    if command == "/mcp-skill-server":
        from seed_mcp_skill_server import show_mcp_skill_server
        show_mcp_skill_server()
        return "handled"

    if command == "/mcp-manifest":
        from seed_mcp_skill_manifest import show_mcp_manifest
        show_mcp_manifest()
        return "handled"

    if command == "/aider-unlock-status":
        from seed_aider_execution_unlock import show_aider_unlock_status
        show_aider_unlock_status()
        return "handled"

    if command == "/aider-unlock-plan":
        from seed_aider_execution_unlock import show_aider_unlock_plan
        show_aider_unlock_plan()
        return "handled"

    if command == "/aider-unlock-approve":
        from seed_aider_execution_unlock import show_aider_unlock_approve
        show_aider_unlock_approve()
        return "handled"

    if command == "/aider-unlock-execute":
        from seed_aider_execution_unlock import show_aider_unlock_execute
        show_aider_unlock_execute()
        return "handled"

    if command == "/integration-sandbox":
        from seed_integration_sandbox import show_sandbox_create
        show_sandbox_create()
        return "handled"

    if command == "/v36-check":
        from seed_v36_integration_gate import show_v36_gate
        show_v36_gate()
        return "handled"



    if command == "/event-bus":
        from seed_event_bus import show_event_bus
        show_event_bus()
        return "handled"

    if command == "/service-status":
        from seed_service_manager import show_service_status
        show_service_status()
        return "handled"

    if command == "/service-start":
        from seed_service_manager import show_service_start
        show_service_start()
        return "handled"

    if command == "/service-stop":
        from seed_service_manager import show_service_stop
        show_service_stop()
        return "handled"

    if command == "/mcp-client":
        from seed_mcp_client import show_mcp_client
        show_mcp_client()
        return "handled"

    if command == "/workflow-list":
        from seed_workflow_automation import show_workflows
        show_workflows()
        return "handled"

    if command == "/workflow-run":
        from seed_workflow_automation import show_workflow_run
        show_workflow_run()
        return "handled"

    if command == "/checkpoint-create":
        from seed_patch_rollback import show_checkpoint_create
        show_checkpoint_create()
        return "handled"

    if command == "/checkpoint-status":
        from seed_patch_rollback import show_checkpoint_status
        show_checkpoint_status()
        return "handled"

    if command == "/checkpoint-restore":
        from seed_patch_rollback import show_checkpoint_restore
        show_checkpoint_restore()
        return "handled"

    if command == "/memory-distill":
        from seed_memory_distiller import show_memory_distill
        show_memory_distill()
        return "handled"

    if command == "/aider-patch-flow":
        from seed_aider_patch_flow import show_aider_patch_flow
        show_aider_patch_flow()
        return "handled"

    if command == "/v40-check":
        from seed_v40_os_gate import show_v40_gate
        show_v40_gate()
        return "handled"



    if command == "/policy":
        from seed_execution_policy import show_policy
        show_policy()
        return "handled"

    if command == "/policy-check":
        from seed_execution_policy import show_policy_check
        show_policy_check()
        return "handled"

    if command == "/capability-graph":
        from seed_capability_graph import show_capability_graph
        show_capability_graph()
        return "handled"

    if command == "/capability-route":
        from seed_capability_graph import show_capability_route
        show_capability_route()
        return "handled"

    if command == "/task-list":
        from seed_task_os import show_task_list
        show_task_list()
        return "handled"

    if command == "/task-create":
        from seed_task_os import show_task_create
        show_task_create()
        return "handled"

    if command == "/task-done":
        from seed_task_os import show_task_done
        show_task_done()
        return "handled"

    if command == "/operator-goal":
        from seed_goal_engine import show_goal_plan
        show_goal_plan()
        return "handled"

    if command == "/operator-status":
        from seed_operator_runtime import show_operator_status
        show_operator_status()
        return "handled"

    if command == "/operator-tick":
        from seed_operator_runtime import show_operator_tick
        show_operator_tick()
        return "handled"

    if command == "/inbox":
        from seed_operator_inbox import show_inbox
        show_inbox()
        return "handled"

    if command == "/inbox-add":
        from seed_operator_inbox import show_inbox_add
        show_inbox_add()
        return "handled"

    if command == "/v50-check":
        from seed_v50_operator_gate import show_v50_gate
        show_v50_gate()
        return "handled"


    return None
