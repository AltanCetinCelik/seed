import json

from seed_llm import ask_llm
from seed_local_control import (
    LOCAL_SAFE_COMMANDS,
    LOCAL_ALLOWED_APPS,
    LOCAL_ALLOWED_FOLDERS,
    save_pending_action
)
from seed_presence import update_presence_after_action
from seed_computer_awareness import format_computer_snapshot


def extract_json_object(text):
    start = text.find("{")
    end = text.rfind("}")

    if start == -1 or end == -1 or end <= start:
        return None

    possible_json = text[start:end + 1]

    try:
        return json.loads(possible_json)
    except json.JSONDecodeError:
        return None


def build_action_proposal_prompt(goal):
    computer = format_computer_snapshot()

    return f"""
You are Seed's local action proposer.

Altan's goal:
{goal}

Computer snapshot:
{computer}

Allowed safe commands:
{json.dumps(LOCAL_SAFE_COMMANDS, indent=2)}

Allowed apps:
{json.dumps(LOCAL_ALLOWED_APPS, indent=2)}

Allowed folders:
{json.dumps(LOCAL_ALLOWED_FOLDERS, indent=2)}

Rules:
- Propose ONE local action only.
- Return JSON only.
- Do not propose forbidden or destructive commands.
- Prefer read-only diagnostic commands.
- If opening an app/folder is enough, propose open_app or open_folder.
- If action is not safe, set requires_approval true.
- Do not pretend you can see the screen.

JSON shape:
{{
  "action_type": "shell_command/open_app/open_folder/none",
  "command": "git status",
  "app": "Terminal",
  "folder": "~/Desktop/seed_private",
  "reason": "why this action helps",
  "risk": "read_only/diagnostic/write/dangerous/external",
  "requires_approval": false
}}
"""


def propose_local_action(goal, chat_state=None):
    print("\n=== LOCAL ACTION PROPOSAL ===")

    response = ask_llm(
        build_action_proposal_prompt(goal),
        task_type="debug",
        runtime_context=chat_state
    )

    parsed = extract_json_object(response)

    if parsed is None:
        print("Seed could not produce a valid JSON action proposal.")
        print(response)
        return None

    print(json.dumps(parsed, indent=4))

    if parsed.get("action_type") == "shell_command" and parsed.get("requires_approval"):
        pending = {
            "type": "shell_command",
            "command": parsed.get("command"),
            "risk": parsed.get("risk"),
            "reason": parsed.get("reason"),
            "approval_phrase": "RUN " + parsed.get("command", "")
        }

        save_pending_action(pending)
        update_presence_after_action("approval_required")
        print("\nSaved as pending action.")
        print(f"Approval phrase: {pending['approval_phrase']}")

    return parsed


def propose_local_action_interactive(chat_state=None):
    goal = input("Goal: ").strip()

    if goal == "":
        print("Goal cannot be empty.")
        return

    propose_local_action(goal, chat_state)