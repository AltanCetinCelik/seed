import json
from http.server import BaseHTTPRequestHandler, HTTPServer
from urllib.parse import urlparse


try:
    from seed_config import SEED_CONTROL_PLANE_HOST, SEED_CONTROL_PLANE_PORT
except Exception:
    SEED_CONTROL_PLANE_HOST = "127.0.0.1"
    SEED_CONTROL_PLANE_PORT = 8790


def safe_json(fn):
    try:
        return fn()
    except Exception as error:
        return {"ok": False, "error": str(error)}


def api_payload(path):
    if path == "/api/status":
        return safe_json(lambda: __import__("seed_runtime_supervisor", fromlist=["runtime_supervisor_snapshot"]).runtime_supervisor_snapshot())

    if path == "/api/mission":
        return safe_json(lambda: __import__("seed_mission_control", fromlist=["mission_control_snapshot"]).mission_control_snapshot())

    if path == "/api/gates":
        return safe_json(lambda: __import__("seed_gate_matrix", fromlist=["run_gate_matrix"]).run_gate_matrix())

    if path == "/api/commands":
        return safe_json(lambda: __import__("seed_command_center", fromlist=["build_command_center"]).build_command_center())

    if path == "/api/timeline":
        return safe_json(lambda: __import__("seed_session_timeline", fromlist=["build_session_timeline"]).build_session_timeline(limit=80))

    if path == "/api/voice":
        return safe_json(lambda: __import__("seed_voice_ux_pack", fromlist=["voice_ux_snapshot"]).voice_ux_snapshot())

    if path == "/api/agents":
        return safe_json(lambda: __import__("seed_agent_run_lifecycle", fromlist=["list_agent_runs"]).list_agent_runs(limit=20))

    if path == "/api/aider":
        return safe_json(lambda: __import__("seed_aider_bridge", fromlist=["detect_aider"]).detect_aider())

    if path == "/api/apps":
        return safe_json(lambda: __import__("seed_local_app_manifest", fromlist=["build_app_manifest"]).build_app_manifest())

    if path == "/api/repo-dna":
        return safe_json(lambda: __import__("seed_repo_dna_engine", fromlist=["build_repo_dna"]).build_repo_dna())

    if path == "/api/integration-fusion":
        return safe_json(lambda: __import__("seed_integration_fusion_engine", fromlist=["build_integration_fusion"]).build_integration_fusion())

    if path == "/api/omega-plan":
        return safe_json(lambda: __import__("seed_omega_planner", fromlist=["build_omega_plan"]).build_omega_plan())

    if path == "/api/control-actions":
        return safe_json(lambda: __import__("seed_control_plane_actions", fromlist=["action_catalog"]).action_catalog())


    if path == "/api/operator":
        return safe_json(lambda: __import__("seed_operator_runtime", fromlist=["operator_status"]).operator_status())

    if path == "/api/tasks":
        return safe_json(lambda: __import__("seed_task_os", fromlist=["list_tasks"]).list_tasks(limit=60))

    if path == "/api/capability-graph":
        return safe_json(lambda: __import__("seed_capability_graph", fromlist=["build_capability_graph"]).build_capability_graph())

    if path == "/api/execution-policy":
        return safe_json(lambda: __import__("seed_execution_policy", fromlist=["build_policy_manifest"]).build_policy_manifest())

    if path == "/api/operator-inbox":
        return safe_json(lambda: {"ok": True, "items": __import__("seed_operator_inbox", fromlist=["read_inbox"]).read_inbox(limit=30)})

    if path == "/api/home-bundle":
        return safe_json(build_home_bundle)

    return {"ok": False, "error": f"Unknown endpoint: {path}"}


def build_home_bundle():
    return {
        "status": api_payload("/api/status"),
        "mission": api_payload("/api/mission"),
        "commands": api_payload("/api/commands"),
        "timeline": api_payload("/api/timeline"),
        "voice": api_payload("/api/voice"),
        "agents": api_payload("/api/agents"),
        "aider": api_payload("/api/aider"),
        "apps": api_payload("/api/apps"),
        "repo_dna": api_payload("/api/repo-dna"),
        "integration_fusion": api_payload("/api/integration-fusion"),
        "omega_plan": api_payload("/api/omega-plan"),
        "control_actions": api_payload("/api/control-actions"),
        "operator": api_payload("/api/operator"),
        "tasks": api_payload("/api/tasks"),
        "capability_graph": api_payload("/api/capability-graph"),
        "execution_policy": api_payload("/api/execution-policy"),
        "operator_inbox": api_payload("/api/operator-inbox")
    }



def compact_home_bundle_for_ui(bundle):
    compact = dict(bundle)

    repo_dna = compact.get("repo_dna", {}) or {}
    compact["repo_dna"] = {
        "ok": repo_dna.get("ok"),
        "python_file_count": repo_dna.get("python_file_count"),
        "command_count": repo_dna.get("command_count"),
        "module_groups": {k: len(v) for k, v in (repo_dna.get("module_groups", {}) or {}).items()},
        "top_mentions": repo_dna.get("top_mentions", [])[:12],
        "dna_summary": repo_dna.get("dna_summary", {})
    }

    fusion = compact.get("integration_fusion", {}) or {}
    compact["integration_fusion"] = {
        "ok": fusion.get("ok"),
        "candidate_count": fusion.get("candidate_count"),
        "top_10": fusion.get("top_10", [])[:10],
        "policy": fusion.get("policy", {})
    }

    omega = compact.get("omega_plan", {}) or {}
    compact["omega_plan"] = {
        "ok": omega.get("ok"),
        "repo_stats": omega.get("repo_stats"),
        "waves": omega.get("waves"),
        "next_big_build": omega.get("next_big_build"),
        "rules": omega.get("rules", [])
    }

    timeline = compact.get("timeline", {}) or {}
    compact["timeline"] = {
        "ok": timeline.get("ok", True),
        "count": timeline.get("count"),
        "items": (timeline.get("items", []) or [])[-20:]
    }


    operator = compact.get("operator", {}) or {}
    compact["operator"] = {
        "ok": operator.get("ok"),
        "manual_tick_only": operator.get("manual_tick_only"),
        "ready_task_count": operator.get("ready_task_count"),
        "total_task_count": operator.get("total_task_count"),
        "next_task": operator.get("next_task")
    }

    tasks = compact.get("tasks", {}) or {}
    compact["tasks"] = {
        "ok": tasks.get("ok"),
        "count": tasks.get("count"),
        "tasks": (tasks.get("tasks", []) or [])[:20]
    }

    capability = compact.get("capability_graph", {}) or {}
    compact["capability_graph"] = {
        "ok": capability.get("ok"),
        "node_count": capability.get("node_count"),
        "edge_count": capability.get("edge_count"),
        "intent_routes": capability.get("intent_routes", {})
    }

    policy = compact.get("execution_policy", {}) or {}
    compact["execution_policy"] = {
        "ok": policy.get("ok"),
        "manual_tick_only": policy.get("manual_tick_only"),
        "no_arbitrary_shell": policy.get("no_arbitrary_shell"),
        "no_delete": policy.get("no_delete"),
        "no_auto_commit": policy.get("no_auto_commit")
    }

    inbox = compact.get("operator_inbox", {}) or {}
    compact["operator_inbox"] = {
        "ok": inbox.get("ok"),
        "items": (inbox.get("items", []) or [])[-12:]
    }

    return compact


def render_home():
    from seed_control_plane_ui_v5 import render_control_plane_ui
    return render_control_plane_ui(compact_home_bundle_for_ui(build_home_bundle()))


class SeedControlPlaneHandler(BaseHTTPRequestHandler):
    def _send(self, status, body, content_type):
        encoded = body.encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", content_type + "; charset=utf-8")
        self.send_header("Content-Length", str(len(encoded)))
        self.end_headers()
        self.wfile.write(encoded)

    def do_GET(self):
        parsed = urlparse(self.path)
        path = parsed.path

        if path == "/":
            self._send(200, render_home(), "text/html")
            return

        if path.startswith("/api/"):
            payload = api_payload(path)
            status = 200 if payload.get("ok", True) is not False else 404
            self._send(status, json.dumps(payload, indent=4), "application/json")
            return

        self._send(404, json.dumps({"ok": False, "error": "not found"}), "application/json")

    def do_POST(self):
        parsed = urlparse(self.path)
        path = parsed.path

        if path.startswith("/api/action/"):
            action_id = path.rsplit("/", 1)[-1]
            from seed_control_plane_actions import validate_action_header, run_allowed_action

            if not validate_action_header(self.headers):
                self._send(403, json.dumps({
                    "ok": False,
                    "error": "Missing or invalid Seed local action header."
                }, indent=4), "application/json")
                return

            payload = run_allowed_action(action_id)
            status = 200 if payload.get("ok") else 400
            self._send(status, json.dumps(payload, indent=4), "application/json")
            return

        self._send(404, json.dumps({"ok": False, "error": "not found"}), "application/json")

    def log_message(self, format, *args):
        print("[Seed Control Plane]", format % args)


def run_control_plane():
    server = HTTPServer((SEED_CONTROL_PLANE_HOST, int(SEED_CONTROL_PLANE_PORT)), SeedControlPlaneHandler)
    print(f"Seed Control Plane running at http://{SEED_CONTROL_PLANE_HOST}:{SEED_CONTROL_PLANE_PORT}")
    print("Local-only. Press Ctrl+C to stop.")
    server.serve_forever()


if __name__ == "__main__":
    run_control_plane()
