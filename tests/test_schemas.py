import pytest
from pydantic import ValidationError
from guardrails.schemas import RCAResponse


def test_valid_rca_response():
    response = RCAResponse(
        root_cause="Startup command failed",
        severity="high",
        confidence=0.95,
        recommended_actions=["Inspect logs"]
    )
    assert response.severity == "high"


def test_invalid_severity():
    with pytest.raises(ValidationError):
        RCAResponse(
            root_cause="Failure",
            severity="urgent",
            confidence=0.95,
            recommended_actions=["Inspect logs"]
        )