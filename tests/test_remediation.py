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
    assert result["actions"][0]["risk"] == "safe"
    assert result["actions"][1]["risk"] == "risky"
    assert result["actions"][1]["requires_approval"] is True