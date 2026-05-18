from notifier.notifier import format_incident_report


def test_format_incident_report():
    incident = {
        "pod_name": "test-pod",
        "namespace": "default",
        "status": "CrashLoopBackOff",
        "restart_count": 3,
    }

    rca = {
        "root_cause": "Container exits immediately.",
        "severity": "high",
        "confidence": 0.95,
    }

    remediation = {
        "actions": [
            {
                "description": "Restart deployment.",
                "risk": "safe",
                "requires_approval": False,
            }
        ]
    }

    report = format_incident_report(
        incident,
        rca,
        remediation
    )

    assert "KUBERNETES INCIDENT REPORT" in report
    assert "test-pod" in report
    assert "Container exits immediately." in report
    assert "Restart deployment." in report