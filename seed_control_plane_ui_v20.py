import html


def esc(value):
    return html.escape(str(value))


def render_v20_panel(bundle):
    v20 = bundle.get("v20", {}) or {}
    data = v20.get("data", v20) if isinstance(v20, dict) else {}
    modules = data.get("modules", {}) if isinstance(data, dict) else {}
    capabilities = data.get("major_capabilities", []) if isinstance(data, dict) else []

    module_html = ""
    for name, result in modules.items():
        ok = result.get("ok") if isinstance(result, dict) else None
        module_html += f"""
        <div class="event">
          <div class="time">module · ok={esc(ok)}</div>
          <div class="body"><strong>{esc(name)}</strong></div>
        </div>
        """

    cap_html = "".join(f"<li>{esc(item)}</li>" for item in capabilities)

    return f"""
<section class="card full" id="seed-v20">
  <h2>Seed v20 Sovereign Companion OS</h2>
  <p class="small">Unified local companion OS: memory, voice, tasks, MCP, Aider review, browser sandbox, project/life OS, world, avatar, council, self-improvement, multi-device.</p>

  <div class="metric-row">
    <div class="metric"><div class="label">v20 OK</div><div class="value">{esc(data.get("ok"))}</div></div>
    <div class="metric"><div class="label">Modules</div><div class="value">{esc(len(modules))}</div></div>
    <div class="metric"><div class="label">Capabilities</div><div class="value">{esc(len(capabilities))}</div></div>
    <div class="metric"><div class="label">Mode</div><div class="value" style="font-size:13px">manual tick / local first</div></div>
  </div>

  <h3>Capabilities</h3>
  <ul class="action-list">{cap_html}</ul>

  <h3>Subsystems</h3>
  <div class="timeline">{module_html}</div>
</section>
"""


def render_presence_panel(bundle):
    presence = bundle.get("presence", {}) or {}
    data = presence.get("data", presence) if isinstance(presence, dict) else {}
    status = data.get("status", {}) if isinstance(data, dict) else {}
    policy = data.get("policy", {}) if isinstance(data, dict) else {}
    pending = data.get("pending", []) if isinstance(data, dict) else []

    pending_html = ""
    for item in pending[:8]:
        pending_html += f"""
        <div class="event">
          <div class="time">{esc(item.get("reason"))} · priority={esc(item.get("priority"))}</div>
          <div class="body">{esc(item.get("message"))}</div>
        </div>
        """

    if not pending_html:
        pending_html = '<div class="event"><div class="body">No pending presence messages.</div></div>'

    return f"""
<section class="card full" id="seed-presence">
  <h2>Seed Presence Runtime</h2>
  <p class="small">Proactive mind loop: curiosity, continuity, rituals, warnings, companionship. Queue-only by default.</p>

  <div class="metric-row">
    <div class="metric"><div class="label">Enabled</div><div class="value">{esc(policy.get("presence_enabled"))}</div></div>
    <div class="metric"><div class="label">Focus</div><div class="value">{esc(policy.get("focus_mode"))}</div></div>
    <div class="metric"><div class="label">Today</div><div class="value">{esc(status.get("messages_today"))}</div></div>
    <div class="metric"><div class="label">Pending</div><div class="value">{esc(len(pending))}</div></div>
  </div>

  <h3>Pending Presence Messages</h3>
  <div class="timeline">{pending_html}</div>
</section>
"""


def render_control_plane_ui(bundle):
    from seed_control_plane_ui_v5 import render_control_plane_ui as base_render

    html_doc = base_render(bundle)
    panels = render_v20_panel(bundle) + "\n" + render_presence_panel(bundle)

    if '<section class="card full" id="operator-core">' in html_doc:
        return html_doc.replace(
            '<section class="card full" id="operator-core">',
            panels + '\n<section class="card full" id="operator-core">',
            1
        )

    return html_doc.replace("</main>", panels + "\n</main>", 1)
