import html
def esc(v): return html.escape(str(v))
def render_v70_panel(bundle):
    v70=bundle.get("v70",{}) or {}; data=v70.get("data",v70) if isinstance(v70,dict) else {}; cards=data.get("cards",[]) if isinstance(data,dict) else []
    cards_html="".join(f"<div class='event'><div class='time'>{esc(c.get('status'))}</div><div class='body'><strong>{esc(c.get('title'))}</strong><br>{esc(c.get('summary'))}</div></div>" for c in cards)
    nav_html="".join(f"<span class='pill'>{esc(x)}</span>" for x in ["Home","Agent HQ","Memory","Workflows","Models","Aider","Repo Fusion","Voice","Browser","Settings"])
    phrase_html="".join(f"<span class='pill'>{esc(x)}</span>" for x in ["check yourself","show models","benchmark models","review memories","compare Hermes Moltbot OpenClaw","open dashboard","what should we improve next"])
    return f"""<section class='card full' id='seed-v70'><h2>Seed v70 — One-of-a-kind Companion OS</h2><p class='small'>Natural UX, model-aware routing, clean repo fusion, memory review, real Aider loop, voice/browser/multichannel paths, and product polish.</p><div class='metric-row'><div class='metric'><div class='label'>v70 OK</div><div class='value'>{esc(data.get('ok'))}</div></div><div class='metric'><div class='label'>Models</div><div class='value' style='font-size:13px'>{esc(data.get('model_status'))}</div></div><div class='metric'><div class='label'>Fusion</div><div class='value' style='font-size:13px'>{esc(data.get('fusion_status'))}</div></div><div class='metric'><div class='label'>UX</div><div class='value' style='font-size:13px'>Natural</div></div></div><h3>Product Navigation</h3><div style='display:flex;flex-wrap:wrap;gap:8px;margin:10px 0 18px 0;'>{nav_html}</div><h3>Talk naturally</h3><div style='display:flex;flex-wrap:wrap;gap:8px;margin:10px 0 18px 0;'>{phrase_html}</div><h3>System Cards</h3><div class='timeline'>{cards_html}</div></section>"""
def render_control_plane_ui(bundle):
    from seed_control_plane_ui_v60 import render_control_plane_ui as base_render
    doc=base_render(bundle); panel=render_v70_panel(bundle)
    return doc.replace('<section class="card full" id="seed-v60">', panel+'\n<section class="card full" id="seed-v60">',1) if '<section class="card full" id="seed-v60">' in doc else doc.replace("</main>", panel+"\n</main>",1)
