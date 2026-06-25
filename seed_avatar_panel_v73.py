import json
import html as html_lib
import webbrowser
from datetime import datetime
from pathlib import Path

HTML_FILE = Path("seed_avatar_panel_v73.html")

def now_timestamp():
    return datetime.now().isoformat(timespec="seconds")

def build_avatar_panel():
    try:
        from seed_avatar_state_v72 import compute_avatar_state
        avatar = compute_avatar_state()
    except Exception as error:
        avatar = {"mood": "cautious", "color": "red", "face": "alert", "reason": str(error)}
    color = html_lib.escape(str(avatar.get("color", "blue")))
    mood = html_lib.escape(str(avatar.get("mood", "curious")))
    face = html_lib.escape(str(avatar.get("face", "curious")))
    reason = html_lib.escape(str(avatar.get("reason", "Seed is checking its state.")))
    html = f"""<!doctype html><html><head><meta charset='utf-8'><title>Seed Avatar v73</title>
<style>
body{{margin:0;background:#080808;color:#eee;font-family:-apple-system,BlinkMacSystemFont,Segoe UI,sans-serif;display:flex;align-items:center;justify-content:center;min-height:100vh}}
.card{{width:560px;border:1px solid #333;border-radius:28px;padding:34px;background:linear-gradient(145deg,#111,#181818);box-shadow:0 0 60px rgba(0,0,0,.6)}}
.orb{{width:180px;height:180px;border-radius:50%;margin:0 auto 24px;background:{color};box-shadow:0 0 90px {color};display:flex;align-items:center;justify-content:center;font-size:58px}}
.row{{opacity:.82;margin:10px 0}} .label{{color:#999}} h1{{text-align:center;margin:0 0 14px}} .reason{{line-height:1.45;background:#0d0d0d;border-radius:18px;padding:18px;margin-top:22px}}
</style></head><body><div class='card'><div class='orb'>✦</div><h1>Seed Avatar</h1><div class='row'><span class='label'>Mood:</span> {mood}</div><div class='row'><span class='label'>Face:</span> {face}</div><div class='row'><span class='label'>Color:</span> {color}</div><div class='row'><span class='label'>Updated:</span> {now_timestamp()}</div><div class='reason'>{reason}</div></div></body></html>"""
    HTML_FILE.write_text(html)
    return {"ok": True, "file": str(HTML_FILE), "avatar": avatar}

def open_avatar_panel():
    data = build_avatar_panel()
    webbrowser.open(Path(data["file"]).resolve().as_uri())
    print(f"Opened {data['file']}")
    return "handled"

def show_avatar_panel():
    print(json.dumps(build_avatar_panel(), indent=4, ensure_ascii=False))
    return "handled"

if __name__ == "__main__":
    show_avatar_panel()
