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
