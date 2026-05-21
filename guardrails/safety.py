def classify_action_risk(action: str) -> tuple[str, bool]:
    """
    Classify an action into a risk level and determine
    whether human approval is required.
    """
    action_lower = action.lower()

    # Critical-risk actions
    critical_keywords = [
        "delete",
        "remove",
        "destroy",
        "drop",
        "terminate namespace",
    ]

    # High-risk actions
    high_keywords = [
        "scale to zero",
        "shutdown",
        "disable",
    ]

    # Medium-risk actions
    medium_keywords = [
        "rollback",
        "roll back",
        "revert",
    ]

    for keyword in critical_keywords:
        if keyword in action_lower:
            return "critical", True

    for keyword in high_keywords:
        if keyword in action_lower:
            return "high", True

    for keyword in medium_keywords:
        if keyword in action_lower:
            return "medium", True

    # Default safe
    return "safe", False


def apply_safety_checks(remediation_plan: dict) -> dict:
    """
    Add risk classification and approval requirements to all actions.
    """
    for action in remediation_plan.get("actions", []):
        risk, requires_approval = classify_action_risk(
            action["description"]
        )

        action["risk"] = risk
        action["requires_approval"] = requires_approval

    return remediation_plan


if __name__ == "__main__":
    sample_plan = {
        "actions": [
            {"description": "Inspect application logs."},
            {"description": "Restart the deployment."},
            {"description": "Roll back to previous version."},
            {"description": "Delete the namespace."},
        ]
    }

    from pprint import pprint
    pprint(apply_safety_checks(sample_plan))