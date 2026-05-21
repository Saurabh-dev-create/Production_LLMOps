from remediation_agent.remediation import generate_remediation_plan


def test_generate_remediation_plan():
    rca_result = {
        "recommended_actions": [
            "Restart the deployment.",
            "Roll back to previous version."
        ]
    }

    result = generate_remediation_plan(rca_result)

    assert len(result["actions"]) == 2

    # Restart is safe
    assert result["actions"][0]["risk"] == "safe"
    assert result["actions"][0]["requires_approval"] is False

    # Rollback is medium risk and requires approval
    assert result["actions"][1]["risk"] == "medium"
    assert result["actions"][1]["requires_approval"] is True