from guardrails.safety import apply_safety_checks


def generate_remediation_plan(rca_result: dict) -> dict:
    """
    Convert RCA output into a structured remediation plan.
    Risk classification and approval requirements are applied
    using centralized safety guardrails.
    """
    recommended_actions = rca_result.get("recommended_actions", [])

    actions = []

    for action in recommended_actions:
        actions.append({
            "description": action
        })

    # Build the remediation plan
    plan = {
        "actions": actions
    }

    # Apply centralized safety checks
    return apply_safety_checks(plan)


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
