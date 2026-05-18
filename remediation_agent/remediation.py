def generate_remediation_plan(rca_result: dict) -> dict:
    """
    Convert RCA output into a structured remediation plan.
    """
    recommended_actions = rca_result.get("recommended_actions", [])

    actions = []

    for action in recommended_actions:
        action_lower = action.lower()

        # Simple risk classification rules
        if any(keyword in action_lower for keyword in ["rollback","roll back","delete", "scale down"]):
            risk = "risky"
            requires_approval = True
        else:
            risk = "safe"
            requires_approval = False

        actions.append({
            "description": action,
            "risk": risk,
            "requires_approval": requires_approval
        })

    return {"actions": actions}


if __name__ == "__main__":
    sample_rca = {
        "root_cause": "Container exits immediately with exit code 1.",
        "severity": "high",
        "confidence": 0.98,
        "recommended_actions": [
            "Inspect the container startup command.",
            "Restart the deployment crash-demo.",
            "Roll back to the previous deployment version."
        ]
    }

    from pprint import pprint
    pprint(generate_remediation_plan(sample_rca))
