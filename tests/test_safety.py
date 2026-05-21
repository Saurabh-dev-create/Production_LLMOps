from guardrails.safety import (
    classify_action_risk,
    apply_safety_checks,
)


def test_classify_action_risk():
    assert classify_action_risk("Inspect logs") == ("safe", False)
    assert classify_action_risk("Roll back deployment") == ("medium", True)
    assert classify_action_risk("Delete namespace") == ("critical", True)


def test_apply_safety_checks():
    plan = {
        "actions": [
            {"description": "Delete namespace"}
        ]
    }

    result = apply_safety_checks(plan)

    assert result["actions"][0]["risk"] == "critical"
    assert result["actions"][0]["requires_approval"] is True