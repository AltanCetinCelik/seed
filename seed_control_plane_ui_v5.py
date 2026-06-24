import html
import json


def esc(value):
    return html.escape(str(value))


def render_v5_panel(bundle):
    operator = bundle.get("operator", {}) or {}
    capability = bundle.get("capability_graph", {}) or {}
    policy = bundle.get("execution_policy", {}) or {}
    tasks = bundle.get("tasks", {}) or {}
    inbox = bundle.get("operator_inbox", {}) or {}

    task_items = tasks.get("tasks", []) or []
    task_html = ""

    for task in task_items[:12]:
        task_html += f'''
        <div class="event">
          <div class="time">{esc(task.get("status"))} · priority {esc(task.get("priority"))} · {esc(task.get("action_id"))}</div>
          <div class="body"><strong>{esc(task.get("title"))}</strong><br>{esc(task.get("id"))}</div>
        </div>
        '''

    inbox_items = inbox.get("items", []) if isinstance(inbox, dict) else []
    inbox_html = ""
    for item in inbox_items[-8:]:
        inbox_html += f'''
        <div class="event">
          <div class="time">{esc(item.get("created_at"))} · {esc(item.get("kind"))}</div>
          <div class="body">{esc(item.get("text"))}</div>
        </div>
        '''

    return f'''
<section class="card full" id="operator-core">
  <h2>Seed v5 Operator Core</h2>
  <p class="small">Goal → Task OS → Manual Operator Tick → Policy → Verified result.</p>

  <div class="metric-row">
    <div class="metric"><div class="label">Ready Tasks</div><div class="value">{esc(operator.get("ready_task_count"))}</div></div>
    <div class="metric"><div class="label">Total Tasks</div><div class="value">{esc(operator.get("total_task_count"))}</div></div>
    <div class="metric"><div class="label">Capability Nodes</div><div class="value">{esc(capability.get("node_count"))}</div></div>
    <div class="metric"><div class="label">Capability Edges</div><div class="value">{esc(capability.get("edge_count"))}</div></div>
  </div>

  <h3>Policy</h3>
  <div class="kv">
    <div><span>Manual tick only</span><span>{esc(operator.get("manual_tick_only"))}</span></div>
    <div><span>No arbitrary shell</span><span>{esc(policy.get("no_arbitrary_shell"))}</span></div>
    <div><span>No delete</span><span>{esc(policy.get("no_delete"))}</span></div>
    <div><span>No auto commit</span><span>{esc(policy.get("no_auto_commit"))}</span></div>
  </div>

  <h3>Task Queue</h3>
  <div class="timeline">{task_html or '<div class="event"><div class="body">No tasks yet. Create a goal with /operator-goal.</div></div>'}</div>

  <h3>Inbox</h3>
  <div class="timeline">{inbox_html or '<div class="event"><div class="body">No inbox items yet.</div></div>'}</div>
</section>
'''


def render_control_plane_ui(bundle):
    from seed_control_plane_ui_omega import render_control_plane_ui as base_render

    html_doc = base_render(bundle)
    panel = render_v5_panel(bundle)

    if '<section class="card full" id="omega">' in html_doc:
        return html_doc.replace('<section class="card full" id="omega">', panel + '\n<section class="card full" id="omega">', 1)

    return html_doc.replace("</main>", panel + "\n</main>", 1)
