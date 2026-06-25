import html


def esc(value):
    return html.escape(str(value))


def render_v45_panel(bundle):
    v45 = bundle.get("v45", {}) or {}
    data = v45.get("data", v45) if isinstance(v45, dict) else {}

    cards = data.get("cards", [])
    card_html = ""
    for card in cards:
        card_html += f"""
        <div class="event">
          <div class="time">{esc(card.get("status"))}</div>
          <div class="body"><strong>{esc(card.get("title"))}</strong><br>{esc(card.get("body"))}</div>
        </div>
        """

    return f"""
<section class="card full" id="seed-v45">
  <h2>Seed v45 Total Systems</h2>
  <p class="small">Everything except dedicated security hardening: Aider cockpit, Memory Max, Workflow Runtime, MCP Max, Browser, Voice, Heavy Agents, Eval Lab, Terminal Pro, Multi-device, World UI, Self-improvement loop.</p>

  <div class="metric-row">
    <div class="metric"><div class="label">v45 OK</div><div class="value">{esc(data.get("ok"))}</div></div>
    <div class="metric"><div class="label">Systems</div><div class="value">{esc(len(cards))}</div></div>
    <div class="metric"><div class="label">Terminal</div><div class="value" style="font-size:13px">Pro</div></div>
    <div class="metric"><div class="label">UI</div><div class="value" style="font-size:13px">Professional</div></div>
  </div>

  <h3>System Cards</h3>
  <div class="timeline">{card_html}</div>
</section>
"""


def render_control_plane_ui(bundle):
    from seed_control_plane_ui_v30 import render_control_plane_ui as base_render

    html_doc = base_render(bundle)
    panel = render_v45_panel(bundle)

    if '<section class="card full" id="seed-agent-hq-v30">' in html_doc:
        return html_doc.replace(
            '<section class="card full" id="seed-agent-hq-v30">',
            panel + '\n<section class="card full" id="seed-agent-hq-v30">',
            1
        )

    return html_doc.replace("</main>", panel + "\n</main>", 1)
