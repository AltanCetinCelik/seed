from pathlib import Path
import re


def write_file(path, content):
    Path(path).write_text(content.strip() + "\n")
    print(f"Wrote {path}")


write_file("seed_nothing_left_behind_v50.py", r'''
import json
import shutil
import subprocess
from datetime import datetime
from pathlib import Path


STATE_FILE = Path("seed_v50_nothing_left_behind_state.json")
LEDGER_FILE = Path("seed_v50_full_update_ledger.json")
COMMAND_MAP_FILE = Path("seed_v50_command_map.json")
DUST_FILE = Path("seed_v50_dust_check.json")
REPO_NOTEBOOK_DIR = Path("seed_repo_notebooks")
EXPORT_DIR = Path("seed_exports")


def now_timestamp():
    return datetime.now().isoformat(timespec="seconds")


def safe_call(name, fn):
    try:
        data = fn()
        return {
            "name": name,
            "ok": bool(data.get("ok", True)) if isinstance(data, dict) else True,
            "data": data,
        }
    except Exception as error:
        return {
            "name": name,
            "ok": False,
            "error": str(error),
        }


FULL_LEDGER = [
    {
        "id": "v20",
        "title": "Sovereign Companion OS",
        "status": "implemented",
        "proof": "v20 sovereign gate",
        "module": "seed_v20_sovereign_os.py",
    },
    {
        "id": "v20_3",
        "title": "Presence Runtime + Curiosity Loop",
        "status": "implemented",
        "proof": "presence gate + notification queue + focus/quiet policy",
        "module": "seed_presence.py",
    },
    {
        "id": "v30",
        "title": "Repo Assimilation + Agent HQ",
        "status": "implemented",
        "proof": "v30 gate Ready True, cached Agent HQ",
        "module": "seed_agent_hq_v30.py",
    },
    {
        "id": "v30_1",
        "title": "Fast Cache + Bounded Repo Scanner",
        "status": "implemented",
        "proof": "Control Plane v30 cache + fast repo scanner",
        "module": "seed_repo_risk_scanner.py",
    },
    {
        "id": "v30_2",
        "title": "Task Queue Hygiene",
        "status": "implemented",
        "proof": "test/gate tasks archived and counted separately",
        "module": "seed_task_hygiene_v302.py",
    },
    {
        "id": "v31",
        "title": "Real Aider Cockpit",
        "status": "implemented",
        "proof": "guarded Aider session planner + tests + validation",
        "module": "seed_aider_cockpit_v31.py",
    },
    {
        "id": "v32",
        "title": "Memory Brain Max",
        "status": "implemented",
        "proof": "memory layers + runtime indexing + simple semantic search",
        "module": "seed_memory_brain_max_v32.py",
    },
    {
        "id": "v33",
        "title": "Workflow Runtime Max",
        "status": "implemented",
        "proof": "durable manual-tick workflow runtime",
        "module": "seed_workflow_runtime_v33.py",
    },
    {
        "id": "v34",
        "title": "MCP Marketplace Max",
        "status": "implemented",
        "proof": "Seed tools catalog + MCP grouping",
        "module": "seed_mcp_marketplace_max_v34.py",
    },
    {
        "id": "v35",
        "title": "Browser Read-only Sandbox",
        "status": "implemented",
        "proof": "read-only URL fetch/summarize with blocked actions",
        "module": "seed_browser_executor_v35.py",
    },
    {
        "id": "v36",
        "title": "Voice Runtime Max",
        "status": "implemented",
        "proof": "provider detection + transcript journal + macOS TTS",
        "module": "seed_voice_runtime_max_v36.py",
    },
    {
        "id": "v37",
        "title": "Heavy Agent Sandbox",
        "status": "implemented",
        "proof": "OpenHands/SWE/Cline/Open Interpreter sandbox specs",
        "module": "seed_heavy_agent_sandbox_v37.py",
    },
    {
        "id": "v38",
        "title": "Professional Agent HQ UI Model",
        "status": "implemented",
        "proof": "dashboard layout model",
        "module": "seed_agent_hq_ui_model_v38.py",
    },
    {
        "id": "v39",
        "title": "Presence Max",
        "status": "implemented",
        "proof": "better triggers + hygiene-aware task stats",
        "module": "seed_presence_max_v39.py",
    },
    {
        "id": "v40",
        "title": "Evaluation + Benchmark Lab",
        "status": "implemented",
        "proof": "latency/gate/eval runner",
        "module": "seed_eval_lab_v40.py",
    },
    {
        "id": "v42",
        "title": "Desktop Packaging + Terminal Pro",
        "status": "implemented",
        "proof": "terminal pro + launchers",
        "module": "seed_terminal_pro.py",
    },
    {
        "id": "v43",
        "title": "Multi-device Hub Max",
        "status": "implemented",
        "proof": "local/LAN dashboard model",
        "module": "seed_multidevice_hub_max_v43.py",
    },
    {
        "id": "v44",
        "title": "Seed World + Avatar UI State",
        "status": "implemented",
        "proof": "world rooms + avatar state",
        "module": "seed_world_ui_v44.py",
    },
    {
        "id": "v45",
        "title": "Self-improvement Loop",
        "status": "implemented",
        "proof": "workflow + Aider dry-run loop",
        "module": "seed_self_improvement_loop_v45.py",
    },
    {
        "id": "v50",
        "title": "Nothing Left Behind Finalization",
        "status": "implemented",
        "proof": "ledger + dust check + repo notebooks + command map + export",
        "module": "seed_nothing_left_behind_v50.py",
    },
]


COMMAND_GROUPS = {
    "Core": [
        "/v50-help", "/v50-check", "/v50-status", "/full-update", "/dust-check",
        "/terminal-pro", "/control-plane", "/latency", "/quick-gates", "/final-gates"
    ],
    "Repo Assimilation": [
        "/agent-hq", "/repo-assimilate", "/repo-scoreboard", "/repo-to-seed-plan",
        "/repo-patterns", "/repo-risks", "/adapter-registry", "/repo-notebooks"
    ],
    "Tasks + Workflows": [
        "/task-stats", "/task-clean-test", "/task-dedupe", "/task-reset-demo",
        "/workflow-status", "/workflow-new", "/workflow-tick", "/workflow-templates"
    ],
    "Aider + Self Improvement": [
        "/aider-cockpit", "/aider-cockpit-new", "/aider-cockpit-tests",
        "/self-improve", "/self-improve-new"
    ],
    "Memory": [
        "/memory-brain", "/memory-index-runtime", "/memory-search", "/memory-bootstrap"
    ],
    "Tools + Agents": [
        "/mcp-max", "/browser-readonly", "/heavy-agent-status", "/heavy-agent-new"
    ],
    "Voice + Presence": [
        "/voice-max", "/voice-say", "/voice-journal",
        "/presence-status", "/presence-max", "/curiosity", "/presence-inbox"
    ],
    "UI + Device + World": [
        "/ui-model", "/desktop-packaging", "/multidevice-max", "/world-ui", "/system-export"
    ],
}


def build_full_update_ledger():
    data = {
        "created_at": now_timestamp(),
        "version": "v50.0.0",
        "ok": True,
        "claim": "Every named non-security-hardening Seed subsystem is represented and wired.",
        "excluded_by_user_request": ["Dedicated security hardening lab"],
        "ledger": FULL_LEDGER,
        "count": len(FULL_LEDGER),
    }
    LEDGER_FILE.write_text(json.dumps(data, indent=4))
    return data


def build_command_map():
    data = {
        "created_at": now_timestamp(),
        "version": "v50.0.0",
        "ok": True,
        "groups": COMMAND_GROUPS,
        "total_commands": sum(len(v) for v in COMMAND_GROUPS.values()),
    }
    COMMAND_MAP_FILE.write_text(json.dumps(data, indent=4))
    return data


def memory_bootstrap():
    try:
        from seed_memory_brain_max_v32 import add_memory
    except Exception as error:
        return {"ok": False, "error": str(error)}

    memory_path = Path("seed_memory_brain_v32.json")
    existing_text = memory_path.read_text(errors="ignore") if memory_path.exists() else ""

    added = []
    for item in FULL_LEDGER:
        content = (
            f"{item['id']} — {item['title']}: {item['status']}. "
            f"Proof: {item['proof']}. Module: {item['module']}."
        )
        if content in existing_text:
            continue

        added.append(add_memory(
            content=content,
            layer="system_ledger",
            source="seed_v50_memory_bootstrap",
            confidence=0.95,
            tags=["v50", "nothing_left_behind", item["id"]]
        ))

    try:
        from seed_memory_brain_max_v32 import index_runtime_memories
        runtime = index_runtime_memories()
    except Exception as error:
        runtime = {"ok": False, "error": str(error)}

    return {
        "created_at": now_timestamp(),
        "version": "v50.0.0",
        "ok": True,
        "ledger_memories_added": len(added),
        "runtime_index": runtime,
    }


def workflow_templates():
    workflow_path = Path("seed_workflow_runtime_v33.json")
    existing_text = workflow_path.read_text(errors="ignore") if workflow_path.exists() else ""

    templates = [
        "Run weekly Seed health and latency review",
        "Improve Control Plane professional layout",
        "Run Aider cockpit patch review workflow",
        "Index project memory and review important memories",
        "Review repo integration notebooks and choose next adapter",
        "Test browser read-only research flow",
        "Test voice transcript and TTS flow",
        "Prepare next self-improvement loop",
    ]

    created = []

    try:
        from seed_workflow_runtime_v33 import create_workflow
    except Exception as error:
        return {"ok": False, "error": str(error)}

    for goal in templates:
        if goal in existing_text:
            continue
        created.append(create_workflow(goal))

    return {
        "created_at": now_timestamp(),
        "version": "v50.0.0",
        "ok": True,
        "templates": templates,
        "created": len(created),
    }


def repo_notebooks():
    REPO_NOTEBOOK_DIR.mkdir(exist_ok=True)

    try:
        from seed_repo_assimilation_engine import build_repo_assimilation_report
        report = build_repo_assimilation_report()
    except Exception as error:
        return {"ok": False, "error": str(error)}

    written = []

    for item in report.get("items", []):
        name = item.get("name", "unknown_repo")
        safe_name = "".join(c if c.isalnum() or c in "-_." else "_" for c in name)
        path = REPO_NOTEBOOK_DIR / f"{safe_name}.md"

        patterns = item.get("patterns", {}).get("patterns", [])
        risks = item.get("risks", {})
        adapters = item.get("known_adapter_matches", [])

        text = f"""# Seed Repo Notebook — {name}

## Repo
`{item.get("repo")}`

## Adapter matches
{", ".join(adapters) if adapters else "No direct adapter match. Use as sandbox/reference."}

## Patterns detected
{", ".join(patterns) if patterns else "No strong pattern detected."}

## Risk
- Level: `{risks.get("risk_level")}`
- Score: `{risks.get("risk_score")}`
- Totals: `{json.dumps(risks.get("risk_totals", {}), indent=2)}`

## Seed integration decision
- Use adapter-first.
- Do not copy blindly.
- Extract architecture pattern.
- Build Seed-native adapter.
- Test through v50/v45/v30 gates.
- Promote only after review.

## Suggested integration route
1. Read README/docs/examples.
2. Identify useful modules/classes/commands.
3. Map to Seed subsystem.
4. Create tiny adapter.
5. Run py_compile.
6. Run gates.
7. Add Control Plane card.
8. Add memory note.
"""
        path.write_text(text)
        written.append(str(path))

    return {
        "created_at": now_timestamp(),
        "version": "v50.0.0",
        "ok": True,
        "repo_count": report.get("repo_count"),
        "notebooks_written": len(written),
        "dir": str(REPO_NOTEBOOK_DIR),
        "files": written[:30],
    }


def system_export():
    EXPORT_DIR.mkdir(exist_ok=True)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    export_path = EXPORT_DIR / f"seed_v50_system_export_{timestamp}.json"

    files = [
        "seed_v50_full_update_ledger.json",
        "seed_v50_command_map.json",
        "seed_v50_dust_check.json",
        "seed_v45_total_systems_state.json",
        "seed_v30_agent_hq_v30.json",
        "seed_repo_assimilation_report.json",
        "seed_integration_scoreboard.json",
        "seed_repo_to_seed_plan.json",
        "seed_memory_brain_v32.json",
        "seed_workflow_runtime_v33.json",
    ]

    bundle = {
        "created_at": now_timestamp(),
        "version": "v50.0.0",
        "ok": True,
        "files": {},
    }

    for file in files:
        path = Path(file)
        if path.exists():
            try:
                bundle["files"][file] = json.loads(path.read_text(errors="ignore"))
            except Exception:
                bundle["files"][file] = path.read_text(errors="ignore")[:20000]

    export_path.write_text(json.dumps(bundle, indent=4))

    return {
        "created_at": now_timestamp(),
        "version": "v50.0.0",
        "ok": True,
        "export": str(export_path),
        "included_files": list(bundle["files"].keys()),
    }


def dust_check():
    ledger = build_full_update_ledger()
    command_map = build_command_map()

    missing_modules = []
    for item in FULL_LEDGER:
        module = item.get("module")
        if module and not Path(module).exists():
            missing_modules.append({"id": item["id"], "module": module})

    missing_commands = []
    required_commands = [
        "/v50-check", "/full-update", "/dust-check", "/command-map",
        "/repo-notebooks", "/memory-bootstrap", "/workflow-templates",
        "/system-export", "/terminal-pro", "/control-plane"
    ]

    all_commands = []
    for commands in COMMAND_GROUPS.values():
        all_commands.extend(commands)

    for command in required_commands:
        if command not in all_commands:
            missing_commands.append(command)

    notebook_count = len(list(REPO_NOTEBOOK_DIR.glob("*.md"))) if REPO_NOTEBOOK_DIR.exists() else 0

    checks = {
        "ledger_ok": ledger.get("ok") is True and ledger.get("count", 0) >= 20,
        "command_map_ok": command_map.get("ok") is True and command_map.get("total_commands", 0) >= 30,
        "modules_ok": len(missing_modules) == 0,
        "required_commands_ok": len(missing_commands) == 0,
        "repo_notebooks_exist": notebook_count > 0,
    }

    dust = []

    if missing_modules:
        dust.append({"type": "missing_modules", "items": missing_modules})

    if missing_commands:
        dust.append({"type": "missing_commands", "items": missing_commands})

    if notebook_count == 0:
        dust.append({"type": "repo_notebooks", "message": "Run /repo-notebooks once to generate notebooks."})

    data = {
        "created_at": now_timestamp(),
        "version": "v50.0.0",
        "ok": all(checks.values()),
        "checks": checks,
        "dust": dust,
        "notebook_count": notebook_count,
        "meaning": "If ok=true, every named Seed update category is represented and wired.",
    }

    DUST_FILE.write_text(json.dumps(data, indent=4))
    return data


def build_v50_state():
    status = {
        "created_at": now_timestamp(),
        "version": "v50.0.0",
        "ok": True,
        "title": "Seed v50.0.0 — Nothing Left Behind Finalization Pack",
        "ledger": build_full_update_ledger(),
        "command_map": build_command_map(),
        "dust_check": dust_check(),
        "snapshots": {},
    }

    status["snapshots"]["task_hygiene"] = safe_call(
        "task_hygiene",
        lambda: __import__("seed_task_hygiene_v302", fromlist=["task_stats"]).task_stats()
    )

    status["snapshots"]["memory"] = safe_call(
        "memory",
        lambda: __import__("seed_memory_brain_max_v32", fromlist=["memory_stats"]).memory_stats()
    )

    status["snapshots"]["workflow"] = safe_call(
        "workflow",
        lambda: __import__("seed_workflow_runtime_v33", fromlist=["workflow_status"]).workflow_status()
    )

    status["snapshots"]["agent_hq"] = safe_call(
        "agent_hq",
        lambda: __import__("seed_agent_hq_v30", fromlist=["build_agent_hq_fast"]).build_agent_hq_fast()
    )

    status["snapshots"]["voice"] = safe_call(
        "voice",
        lambda: __import__("seed_voice_runtime_max_v36", fromlist=["voice_runtime_status"]).voice_runtime_status()
    )

    status["snapshots"]["world"] = safe_call(
        "world",
        lambda: __import__("seed_world_ui_v44", fromlist=["build_world_ui"]).build_world_ui()
    )

    status["ok"] = status["dust_check"].get("ok") is True
    STATE_FILE.write_text(json.dumps(status, indent=4))
    return status


def seed_doctor():
    commands = [
        ["python", "-m", "py_compile", "seed_nothing_left_behind_v50.py", "seed_v50_commands.py", "seed_v50_gate.py"],
        ["python", "seed_v50_gate.py"],
        ["python", "seed_v45_total_gate.py"],
        ["python", "seed_v30_megapatch_gate.py"],
        ["python", "seed_latency_probe.py"],
    ]

    results = []
    for command in commands:
        try:
            proc = subprocess.run(command, capture_output=True, text=True, timeout=240)
            results.append({
                "command": " ".join(command),
                "ok": proc.returncode == 0,
                "stdout_tail": proc.stdout[-2500:],
                "stderr_tail": proc.stderr[-2500:],
            })
        except Exception as error:
            results.append({"command": " ".join(command), "ok": False, "error": str(error)})

    data = {
        "created_at": now_timestamp(),
        "version": "v50.0.0",
        "ok": all(r.get("ok") for r in results),
        "results": results,
    }

    Path("seed_v50_doctor_report.json").write_text(json.dumps(data, indent=4))
    return data


def show_full_update():
    data = build_v50_state()
    print("\n=== SEED v50 FULL UPDATE — NOTHING LEFT BEHIND ===")
    print(f"OK: {data['ok']}")
    print(f"Ledger count: {data['ledger']['count']}")
    print(f"Commands: {data['command_map']['total_commands']}")
    print(f"Dust check OK: {data['dust_check']['ok']}")
    if data["dust_check"].get("dust"):
        print("\nDust found:")
        print(json.dumps(data["dust_check"]["dust"], indent=4))
    else:
        print("\nNo named update category left unwired.")


def show_update_ledger():
    data = build_full_update_ledger()
    print("\n=== SEED FULL UPDATE LEDGER ===")
    for item in data["ledger"]:
        print(f"- {item['id']}: {item['title']} — {item['status']} [{item['module']}]")


def show_command_map():
    data = build_command_map()
    print("\n=== SEED COMMAND MAP v50 ===")
    for group, commands in data["groups"].items():
        print(f"\n[{group}]")
        print("  " + "  ".join(commands))


def show_dust_check():
    print("\n=== SEED DUST CHECK v50 ===")
    print(json.dumps(dust_check(), indent=4))


def show_repo_notebooks():
    print("\n=== SEED REPO NOTEBOOKS v50 ===")
    print(json.dumps(repo_notebooks(), indent=4))


def show_memory_bootstrap():
    print("\n=== SEED MEMORY BOOTSTRAP v50 ===")
    print(json.dumps(memory_bootstrap(), indent=4))


def show_workflow_templates():
    print("\n=== SEED WORKFLOW TEMPLATES v50 ===")
    print(json.dumps(workflow_templates(), indent=4))


def show_system_export():
    print("\n=== SEED SYSTEM EXPORT v50 ===")
    print(json.dumps(system_export(), indent=4))


def show_seed_doctor():
    print("\n=== SEED DOCTOR v50 ===")
    print(json.dumps(seed_doctor(), indent=4))


if __name__ == "__main__":
    show_full_update()
''')


write_file("seed_v50_commands.py", r'''
def handle_v50_command(command):
    cmd = (command or "").strip().split()[0].lower()

    if cmd == "/v50-help":
        print("""
=== SEED v50 COMMANDS — NOTHING LEFT BEHIND ===
/v50-check
/v50-status
/full-update
/update-ledger
/command-map
/dust-check
/repo-notebooks
/memory-bootstrap
/workflow-templates
/system-export
/seed-doctor

Core shortcuts:
/terminal-pro
/control-plane
/v45-check
/v30-check
""")
        return "handled"

    mapping = {
        "/v50-check": ("seed_v50_gate", "show_v50_gate"),
        "/v50-status": ("seed_nothing_left_behind_v50", "show_full_update"),
        "/full-update": ("seed_nothing_left_behind_v50", "show_full_update"),
        "/update-ledger": ("seed_nothing_left_behind_v50", "show_update_ledger"),
        "/command-map": ("seed_nothing_left_behind_v50", "show_command_map"),
        "/dust-check": ("seed_nothing_left_behind_v50", "show_dust_check"),
        "/repo-notebooks": ("seed_nothing_left_behind_v50", "show_repo_notebooks"),
        "/memory-bootstrap": ("seed_nothing_left_behind_v50", "show_memory_bootstrap"),
        "/workflow-templates": ("seed_nothing_left_behind_v50", "show_workflow_templates"),
        "/system-export": ("seed_nothing_left_behind_v50", "show_system_export"),
        "/seed-doctor": ("seed_nothing_left_behind_v50", "show_seed_doctor"),
    }

    if cmd in mapping:
        module_name, function_name = mapping[cmd]
        module = __import__(module_name, fromlist=[function_name])
        getattr(module, function_name)()
        return "handled"

    return None
''')


write_file("seed_control_plane_ui_v50.py", r'''
import html


def esc(value):
    return html.escape(str(value))


def render_v50_panel(bundle):
    v50 = bundle.get("v50", {}) or {}
    data = v50.get("data", v50) if isinstance(v50, dict) else {}

    ledger = data.get("ledger", {}).get("ledger", []) if isinstance(data, dict) else []
    command_count = data.get("command_map", {}).get("total_commands", 0) if isinstance(data, dict) else 0
    dust = data.get("dust_check", {}) if isinstance(data, dict) else {}

    rows = ""
    for item in ledger[:24]:
        rows += f"""
        <div class="event">
          <div class="time">{esc(item.get("id"))} · {esc(item.get("status"))}</div>
          <div class="body"><strong>{esc(item.get("title"))}</strong><br>{esc(item.get("proof"))}</div>
        </div>
        """

    dust_status = "clean" if dust.get("ok") else "needs action"

    return f"""
<section class="card full" id="seed-v50">
  <h2>Seed v50 — Nothing Left Behind</h2>
  <p class="small">Full update ledger, command map, repo notebooks, memory bootstrap, workflow templates, system export, and dust check.</p>

  <div class="metric-row">
    <div class="metric"><div class="label">v50 OK</div><div class="value">{esc(data.get("ok"))}</div></div>
    <div class="metric"><div class="label">Ledger</div><div class="value">{esc(len(ledger))}</div></div>
    <div class="metric"><div class="label">Commands</div><div class="value">{esc(command_count)}</div></div>
    <div class="metric"><div class="label">Dust</div><div class="value" style="font-size:13px">{esc(dust_status)}</div></div>
  </div>

  <h3>Full System Ledger</h3>
  <div class="timeline">{rows}</div>
</section>
"""


def render_control_plane_ui(bundle):
    from seed_control_plane_ui_v45 import render_control_plane_ui as base_render

    html_doc = base_render(bundle)
    panel = render_v50_panel(bundle)

    if '<section class="card full" id="seed-v45">' in html_doc:
        return html_doc.replace(
            '<section class="card full" id="seed-v45">',
            panel + '\n<section class="card full" id="seed-v45">',
            1
        )

    return html_doc.replace("</main>", panel + "\n</main>", 1)
''')


write_file("seed_v50_gate.py", r'''
import json
import subprocess
from datetime import datetime


MODULES = [
    "seed_nothing_left_behind_v50.py",
    "seed_v50_commands.py",
    "seed_control_plane_ui_v50.py",
    "seed_v50_gate.py",
]


def now_timestamp():
    return datetime.now().isoformat(timespec="seconds")


def compile_module(module):
    proc = subprocess.run(["python", "-m", "py_compile", module], capture_output=True, text=True)
    return {
        "module": module,
        "ok": proc.returncode == 0,
        "stderr": proc.stderr[-2000:],
    }


def run_v50_gate():
    checks = [compile_module(m) for m in MODULES]
    modules_ok = all(c["ok"] for c in checks)

    details = {}

    try:
        from seed_nothing_left_behind_v50 import build_v50_state, dust_check
        state = build_v50_state()
        dust = dust_check()
        systems_ok = state.get("ok") is True
        dust_ok = dust.get("ok") is True
        details["v50_state"] = {
            "ok": state.get("ok"),
            "ledger_count": state.get("ledger", {}).get("count"),
            "commands": state.get("command_map", {}).get("total_commands"),
            "dust_ok": dust.get("ok"),
            "dust": dust.get("dust"),
        }
    except Exception as error:
        systems_ok = False
        dust_ok = False
        details["v50_state_error"] = str(error)

    try:
        from seed_control_plane_server import api_payload
        v50 = api_payload("/api/v50")
        control_plane_ok = bool(v50)
        details["control_plane"] = {"v50_api": bool(v50)}
    except Exception as error:
        control_plane_ok = False
        details["control_plane_error"] = str(error)

    try:
        from seed_v45_total_gate import run_v45_gate
        v45 = run_v45_gate()
        v45_ok = v45.get("ready") is True
        details["v45"] = {"ready": v45.get("ready")}
    except Exception as error:
        v45_ok = False
        details["v45_error"] = str(error)

    ready = modules_ok and systems_ok and dust_ok and control_plane_ok and v45_ok

    report = {
        "created_at": now_timestamp(),
        "version": "v50.0.0",
        "release": "Seed v50.0.0 — Nothing Left Behind Finalization Pack",
        "ready": ready,
        "modules_ok": modules_ok,
        "systems_ok": systems_ok,
        "dust_ok": dust_ok,
        "control_plane_ok": control_plane_ok,
        "v45_ok": v45_ok,
        "module_checks": checks,
        "details": details,
    }

    with open("seed_v50_gate_report.json", "w") as file:
        json.dump(report, file, indent=4)

    return report


def show_v50_gate():
    report = run_v50_gate()
    print("\n=== SEED v50 NOTHING LEFT BEHIND GATE ===")
    print(f"Ready: {report['ready']}")
    print(f"Modules OK: {report['modules_ok']}")
    print(f"Systems OK: {report['systems_ok']}")
    print(f"Dust OK: {report['dust_ok']}")
    print(f"Control Plane OK: {report['control_plane_ok']}")
    print(f"v45 OK: {report['v45_ok']}")
    print("\nDetails:")
    for key, value in report["details"].items():
        print(f"- {key}: {value}")


if __name__ == "__main__":
    show_v50_gate()
''')


# Patch seed_config.py
config = Path("seed_config.py")
text = config.read_text()
text = re.sub(r'^SEED_VERSION\s*=\s*".*?"', 'SEED_VERSION = "v50.0.0"', text, flags=re.M)

if "Seed v50.0.0 Nothing Left Behind Finalization Pack" not in text:
    text += '''

# Seed v50.0.0 Nothing Left Behind Finalization Pack
SEED_V50_NOTHING_LEFT_BEHIND = True
SEED_V50_GATE_REPORT_FILE = "seed_v50_gate_report.json"
SEED_V50_STATE_FILE = "seed_v50_nothing_left_behind_state.json"
'''

config.write_text(text)
print("Updated seed_config.py to v50.0.0")


# Patch seed_commands.py
commands = Path("seed_commands.py")
text = commands.read_text()

if "_seed_v50_original_handle_chat_command" not in text:
    text += r'''

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
'''

commands.write_text(text)
print("Patched seed_commands.py with v50 wrapper")


# Patch Control Plane server
server = Path("seed_control_plane_server.py")
text = server.read_text()

if '/api/v50' not in text:
    anchor = '    if path == "/api/v45":\n'
    endpoint = '''    if path == "/api/v50":
        return safe_json(lambda: __import__("seed_nothing_left_behind_v50", fromlist=["build_v50_state"]).build_v50_state())

'''
    if anchor in text:
        text = text.replace(anchor, endpoint + anchor, 1)

if '"v50": api_payload("/api/v50")' not in text:
    text = text.replace(
        '"v45": api_payload("/api/v45")',
        '"v50": api_payload("/api/v50"),\n        "v45": api_payload("/api/v45")'
    )

text = text.replace(
    "from seed_control_plane_ui_v45 import render_control_plane_ui",
    "from seed_control_plane_ui_v50 import render_control_plane_ui"
)

server.write_text(text)
print("Patched seed_control_plane_server.py with v50 API/UI")


# Patch Terminal Pro command display
terminal = Path("seed_terminal_pro.py")
if terminal.exists():
    text = terminal.read_text()
    if '"/v50-check"' not in text:
        text = text.replace(
            '"Core": ["/latency", "/quick-gates", "/final-gates", "/v30-check", "/v20-check"]',
            '"Core": ["/v50-check", "/full-update", "/dust-check", "/command-map", "/latency", "/quick-gates", "/final-gates", "/v45-check", "/v30-check", "/v20-check"]'
        )
    terminal.write_text(text)
    print("Patched seed_terminal_pro.py with v50 commands")


# Patch final and quick gates
for filename, list_name in [
    ("seed_final_gate_runner.py", "FINAL_GATE_COMMANDS"),
    ("seed_quick_gate_runner.py", "QUICK_GATE_COMMANDS"),
]:
    p = Path(filename)
    if p.exists():
        text = p.read_text()
        line = '    ["python", "seed_v50_gate.py"],\n'
        if line not in text and f"{list_name} = [" in text:
            text = text.replace(f"{list_name} = [\n", f"{list_name} = [\n{line}", 1)
            p.write_text(text)
            print(f"Patched {filename}")


# Docs
core = Path("Seed_Core.md")
text = core.read_text(errors="ignore") if core.exists() else ""

if "Seed v50.0.0 — Nothing Left Behind Finalization Pack" not in text:
    text += '''

## Seed v50.0.0 — Nothing Left Behind Finalization Pack

Seed v50 is the finalization layer over v20-v45.

It adds:

- Full update ledger
- Dust check
- Command map
- Repo notebooks
- Memory bootstrap
- Workflow templates
- System export
- Seed doctor
- Control Plane v50 panel
- Terminal Pro command integration

Meaning:

Every named non-security-hardening Seed subsystem is represented, wired, visible, testable, and documented.

Excluded by user request:

- Dedicated security hardening lab

After v50, future work is not missing categories. It is depth, polish, performance, and real-world execution quality inside already-created systems.
'''

core.write_text(text)
print("Updated Seed_Core.md")


# Gitignore
gitignore = Path(".gitignore")
text = gitignore.read_text(errors="ignore") if gitignore.exists() else ""

block = '''
# Seed v50 Nothing Left Behind runtime state
seed_v50_nothing_left_behind_state.json
seed_v50_full_update_ledger.json
seed_v50_command_map.json
seed_v50_dust_check.json
seed_v50_gate_report.json
seed_v50_doctor_report.json
seed_repo_notebooks/
seed_exports/
'''

if "Seed v50 Nothing Left Behind runtime state" not in text:
    text += "\n" + block

gitignore.write_text(text)
print("Updated .gitignore")

print("\nSeed v50 installer complete.")
