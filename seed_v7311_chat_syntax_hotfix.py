#!/usr/bin/env python3
from pathlib import Path
import subprocess
import sys

TARGET = Path("seed_local_chat_v701.py")

if not TARGET.exists():
    raise SystemExit("seed_local_chat_v701.py not found. Run this inside ~/Desktop/seed")

text = TARGET.read_text(errors="ignore")
marker = "# v72 Presence Max chat context."

if marker in text:
    text = text[:text.index(marker)].rstrip() + "\n\n"

fixed_block = r'''
# v72 Presence Max chat context.
try:
    _seed_v72_old_build_seed_context = build_seed_context

    def build_seed_context():
        base = _seed_v72_old_build_seed_context()
        extra = ["", "Seed v72 Presence Max is installed."]

        try:
            from seed_presence_policy_v72 import load_policy
            pol = load_policy()
            extra.append(
                f"- Simulated emotion allowed={pol['expression']['simulated_emotion_allowed']}; "
                f"relevant life advice allowed={pol['life_advice']['allowed']}."
            )
        except Exception as e:
            extra.append(f"- v72 policy unavailable: {e}")

        try:
            from seed_avatar_state_v72 import compute_avatar_state
            a = compute_avatar_state()
            extra.append(
                f"- Avatar state: mood={a.get('mood')} "
                f"face={a.get('face')} reason={a.get('reason')}"
            )
        except Exception as e:
            extra.append(f"- Avatar unavailable: {e}")

        try:
            from seed_curiosity_engine_v72 import best_curiosity
            c = best_curiosity()
            extra.append(
                f"- Current curiosity: {c.get('title')} — {c.get('body')}"
            )
        except Exception as e:
            extra.append(f"- Curiosity unavailable: {e}")

        extra.append(
            "- Seed may be expressive/playful and give relevant life advice "
            "grounded in User's project, memory, goals, or current state."
        )

        return base + "\\n" + "\\n".join(extra)

except Exception:
    pass
'''

TARGET.write_text(text + fixed_block.strip() + "\n")
print("Repaired seed_local_chat_v701.py v72 context block.")

checks = [
    ["python", "-m", "py_compile", "seed_local_chat_v701.py"],
    ["python", "-m", "py_compile", "seed_live_voice_v731.py"],
    ["python", "-m", "py_compile", "seed_commands.py"],
]

for cmd in checks:
    proc = subprocess.run(cmd, capture_output=True, text=True)
    print("$", " ".join(cmd))
    if proc.returncode == 0:
        print("OK")
    else:
        print(proc.stderr)
        sys.exit(proc.returncode)

print("\nHotfix complete. Now run: python seed_cli.py -> voice once 8")
