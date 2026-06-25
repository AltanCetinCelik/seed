import json
from datetime import datetime
from pathlib import Path
POLICY_FILE = Path("seed_presence_policy_v72.json")
DEFAULT_POLICY = {
    "version": "v72.0.0",
    "spam": {"allow_proactive_presence": True, "min_minutes_between_proactive_messages": 45, "max_unprompted_messages_per_day": 6, "store_in_inbox_when_not_speaking": True},
    "expression": {"simulated_emotion_allowed": True, "style": "warm, playful, loyal, sharp, sometimes dramatic, never robotic", "note": "Seed may express simulated moods/personality. It should not seriously claim biological consciousness."},
    "life_advice": {"allowed": True, "require_relevance": True, "avoid_random_generic_advice": True},
    "curiosity": {"allowed": True, "can_ask_followups": True, "can_suggest_next_moves": True, "ground_in_project_or_user_context": True}
}
def now(): return datetime.now().isoformat(timespec="seconds")
def load_policy():
    if POLICY_FILE.exists():
        try:
            data=json.loads(POLICY_FILE.read_text(errors="ignore")); DEFAULT_POLICY.update(data)
        except Exception: pass
    DEFAULT_POLICY["updated_at"]=now(); POLICY_FILE.write_text(json.dumps(DEFAULT_POLICY, indent=4, ensure_ascii=False)); return DEFAULT_POLICY
def show_policy():
    print("\n=== SEED v72 PRESENCE POLICY ==="); print(json.dumps(load_policy(), indent=4, ensure_ascii=False))
if __name__ == "__main__": show_policy()
