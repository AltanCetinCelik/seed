from seed_config import (
    SKILL_AUTO_RUN_RISKS,
    SKILL_APPROVAL_RISKS
)


def risk_allows_auto_run(risk):
    return risk in SKILL_AUTO_RUN_RISKS


def risk_requires_approval(risk):
    return risk in SKILL_APPROVAL_RISKS


def approval_phrase_for_capability(capability_id):
    return f"APPROVE {capability_id}"


def describe_permission(capability):
    risk = capability.get("risk", "unknown")
    capability_id = capability.get("id", "unknown")

    if risk_allows_auto_run(risk):
        return {
            "allowed": True,
            "requires_approval": False,
            "message": "This capability may run automatically because it is read-only or diagnostic."
        }

    if risk_requires_approval(risk):
        phrase = approval_phrase_for_capability(capability_id)

        return {
            "allowed": False,
            "requires_approval": True,
            "approval_phrase": phrase,
            "message": f"This capability requires explicit approval: {phrase}"
        }

    return {
        "allowed": False,
        "requires_approval": True,
        "approval_phrase": approval_phrase_for_capability(capability_id),
        "message": "Unknown risk level. Approval required."
    }