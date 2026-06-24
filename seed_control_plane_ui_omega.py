import html
import json


def esc(value):
    return html.escape(str(value))


def chip(text):
    return f'<button class="cmd" onclick="copyText({json.dumps(text)})">{esc(text)}</button>'


def render_omega_panel(bundle):
    integration = bundle.get("integration_fusion", {}) or {}
    omega = bundle.get("omega_plan", {}) or {}
    repo_dna = bundle.get("repo_dna", {}) or {}
    actions = bundle.get("control_actions", {}) or {}

    top = integration.get("top_10", []) or []
    waves = omega.get("waves", {}) or {}
    action_ids = list((actions.get("actions", {}) or {}).keys())

    top_html = ""
    for item in top[:8]:
        top_html += f'''
        <div class="event">
          <div class="time">{esc(item.get("category"))} · score {esc(item.get("score"))} · {esc(item.get("status"))}</div>
          <div class="body"><strong>{esc(item.get("name"))}</strong> — {esc(item.get("why"))}</div>
        </div>
        '''

    waves_html = ""
    for wave, items in waves.items():
        waves_html += f"<h3>{esc(wave)}</h3>"
        for item in items:
            waves_html += f'''
            <div class="event">
              <div class="time">risk={esc(item.get("risk"))}</div>
              <div class="body"><strong>{esc(item.get("name"))}</strong> — {esc(item.get("why"))}</div>
            </div>
            '''

    actions_html = "".join(
        f'<button class="cmd" onclick="runAction({json.dumps(action_id)})">run {esc(action_id)}</button>'
        for action_id in action_ids
    )

    return f'''
<section class="card full" id="omega">
  <h2>Omega Integration</h2>
  <p class="small">Repo DNA + friend advice + repo/tool references converted into a controlled integration backlog.</p>
  <div class="metric-row">
    <div class="metric"><div class="label">Python files</div><div class="value">{esc(repo_dna.get("python_file_count"))}</div></div>
    <div class="metric"><div class="label">Commands</div><div class="value">{esc(repo_dna.get("command_count"))}</div></div>
    <div class="metric"><div class="label">Candidates</div><div class="value">{esc(integration.get("candidate_count"))}</div></div>
    <div class="metric"><div class="label">Next build</div><div class="value" style="font-size:13px">{esc(omega.get("next_big_build"))}</div></div>
  </div>

  <h3>Control Actions</h3>
  <div class="cmd-grid">{actions_html}</div>

  <h3>Top Integrations</h3>
  <div class="timeline">{top_html or '<div class="event"><div class="body">No integration candidates yet.</div></div>'}</div>

  <h3>Build Waves</h3>
  <div class="timeline">{waves_html or '<div class="event"><div class="body">No waves yet.</div></div>'}</div>
</section>

<script>
function runAction(actionId) {{
  fetch("/api/action/" + actionId, {{
    method: "POST",
    headers: {{
      "X-Seed-Action": "local-control-plane"
    }}
  }})
  .then(r => r.json())
  .then(data => {{
    const toast = document.getElementById("toast");
    toast.style.display = "block";
    toast.innerText = actionId + ": " + (data.ok ? "OK" : "FAILED");
    setTimeout(() => toast.style.display = "none", 2500);
    console.log(data);
  }})
  .catch(err => {{
    const toast = document.getElementById("toast");
    toast.style.display = "block";
    toast.innerText = actionId + ": ERROR";
    setTimeout(() => toast.style.display = "none", 2500);
    console.error(err);
  }});
}}
</script>
'''


def render_control_plane_ui(bundle):
    from seed_control_plane_ui import render_control_plane_ui as base_render

    html_doc = base_render(bundle)
    omega_panel = render_omega_panel(bundle)

    if '<div class="card full" id="api">' in html_doc:
        return html_doc.replace('<div class="card full" id="api">', omega_panel + '\n<div class="card full" id="api">', 1)

    return html_doc.replace("</main>", omega_panel + "\n</main>", 1)
