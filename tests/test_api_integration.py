from fastapi.testclient import TestClient
from unittest.mock import patch

from api_gateway.main import app

client = TestClient(app)


def test_analyze_endpoint_returns_expected_structure():
    mock_result = {
        "incident_data": {
            "pod_name": "test-pod",
            "namespace": "default",
            "status": "CrashLoopBackOff",
            "restart_count": 5,
        },
        "rca_result": {
            "root_cause": "Container exits immediately.",
            "severity": "high",
            "confidence": 0.97,
            "recommended_actions": [
                "Restart the deployment."
            ],
        },
        "remediation_plan": {
            "actions": [
                {
                    "description": "Restart the deployment.",
                    "risk": "safe",
                    "requires_approval": False,
                }
            ]
        },
        "report": "Sample incident report",
    }

    with patch("api_gateway.main.workflow.invoke", return_value=mock_result):
        response = client.post("/analyze")

    assert response.status_code == 200

    data = response.json()

    assert "incident_data" in data
    assert "rca_result" in data
    assert "remediation_plan" in data
    assert "report" in data

    assert data["incident_data"]["pod_name"] == "test-pod"
    assert data["rca_result"]["severity"] == "high"