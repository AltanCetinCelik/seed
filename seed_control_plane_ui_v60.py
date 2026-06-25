import html


def esc(value):
    return html.escape(str(value))


def render_v60_panel(bundle):
    v60 = bundle.get("v60", {}) or {}
    data = v60.get("data", v60) if isinstance(v60, dict) else {}

    cards = data.get("cards", []) if isinstance(data, dict) else []
    card_html = ""

    for card in cards:
        card_html += f"""
        <div class="event">
          <div class="time">{esc(card.get("status"))}</div>
          <div class="body"><strong>{esc(card.get("title"))}</strong><br>{esc(card.get("body"))}</div>
        </div>
        """

    suggestions = [
        "check yourself",
        "open dashboard",
        "show models",
        "benchmark models",
        "compare Hermes Moltbot OpenClaw",
        "extract memories",
        "what should we improve next",
        "show command palette",
    ]

    chips = "".join([f"<span class='pill'>{esc(s)}</span>" for s in suggestions])

    return f"""
<section class="card full" id="seed-v60">
  <h2>Seed v60 — Real Intelligence + Natural UX Fusion</h2>
  <p class="small">Talk naturally. Seed routes to models, memory, Aider, repo fusion, presence rituals, and diagnostics internally.</p>

  <div class="metric-row">
    <div class="metric"><div class="label">v60 OK</div><div class="value">{esc(data.get("ok"))}</div></div>
    <div class="metric"><div class="label">Natural UX</div><div class="value" style="font-size:13px">Enabled</div></div>
    <div class="metric"><div class="label">Model Router</div><div class="value" style="font-size:13px">Ready</div></div>
    <div class="metric"><div class="label">Fusion Lab</div><div class="value" style="font-size:13px">Ready</div></div>
  </div>

  <h3>You can say</h3>
  <div style="display:flex;flex-wrap:wrap;gap:8px;margin:10px 0 18px 0;">{chips}</div>

  <h3>v60 Systems</h3>
  <div class="timeline">{card_html}</div>
</section>
"""


def render_control_plane_ui(bundle):
    from seed_control_plane_ui_v50 import render_control_plane_ui as base_render

    html_doc = base_render(bundle)
    panel = render_v60_panel(bundle)

    if '<section class="card full" id="seed-v50">' in html_doc:
        return html_doc.replace(
            '<section class="card full" id="seed-v50">',
            panel + '\n<section class="card full" id="seed-v50">',
            1
        )

    return html_doc.replace("</main>", panel + "\n</main>", 1)
