import html


def esc(value):
    return html.escape(str(value))


def render_agent_hq_panel(bundle):
    v30 = bundle.get("v30", {}) or {}
    data = v30.get("data", v30) if isinstance(v30, dict) else {}

    agents = data.get("agents", {}) if isinstance(data, dict) else {}
    next_items = data.get("next_best_integrations", []) if isinstance(data, dict) else []
    top = data.get("scoreboard_top", []) if isinstance(data, dict) else []

    agent_html = ""
    for name, spec in agents.items():
        agent_html += f"""
        <div class="event">
          <div class="time">{esc(spec.get("status"))} · risk={esc(spec.get("risk"))}</div>
          <div class="body"><strong>{esc(name)}</strong><br>{esc(spec.get("mission"))}</div>
        </div>
        """

    next_html = ""
    for item in next_items[:8]:
        next_html += f"""
        <div class="event">
          <div class="time">score={esc(item.get("priority_score"))} · risk={esc(item.get("risk"))}</div>
          <div class="body"><strong>{esc(item.get("name"))}</strong><br>{esc(", ".join(item.get("adapters", [])))}</div>
        </div>
        """

    if not next_html:
        next_html = '<div class="event"><div class="body">Run /repo-assimilate or /agent-hq to build integration plans.</div></div>'

    return f"""
<section class="card full" id="seed-agent-hq-v30">
  <h2>Seed v30 Agent HQ</h2>
  <p class="small">Repo assimilation + controlled agent headquarters: Aider, Browser, Memory, Voice, MCP, OpenHands, SWE, UI, Letta, Interpreter.</p>

  <div class="metric-row">
    <div class="metric"><div class="label">v30 OK</div><div class="value">{esc(data.get("ok"))}</div></div>
    <div class="metric"><div class="label">Agents</div><div class="value">{esc(len(agents))}</div></div>
    <div class="metric"><div class="label">Top Plans</div><div class="value">{esc(len(next_items))}</div></div>
    <div class="metric"><div class="label">Rules</div><div class="value" style="font-size:13px">sandbox / approve / gate</div></div>
  </div>

  <h3>Agent HQ</h3>
  <div class="timeline">{agent_html}</div>

  <h3>Next Best Repo Integrations</h3>
  <div class="timeline">{next_html}</div>
</section>
"""


def render_control_plane_ui(bundle):
    from seed_control_plane_ui_v20 import render_control_plane_ui as base_render

    html_doc = base_render(bundle)
    panel = render_agent_hq_panel(bundle)

    if '<section class="card full" id="seed-v20">' in html_doc:
        return html_doc.replace(
            '<section class="card full" id="seed-v20">',
            panel + '\n<section class="card full" id="seed-v20">',
            1
        )

    return html_doc.replace("</main>", panel + "\n</main>", 1)
