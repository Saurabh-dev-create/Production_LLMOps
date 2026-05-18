def format_incident_report(incident_data, rca_result, remediation_plan):
    """
    Build a human-readable incident report.
    """
    report = []
    report.append("=" * 80)
    report.append("🚨 KUBERNETES INCIDENT REPORT")
    report.append("=" * 80)

    # Incident Summary
    report.append(f"Pod: {incident_data['pod_name']}")
    report.append(f"Namespace: {incident_data['namespace']}")
    report.append(f"Status: {incident_data['status']}")
    report.append(f"Restart Count: {incident_data['restart_count']}")
    report.append("")

    # RCA
    report.append("🧠 ROOT CAUSE ANALYSIS")
    report.append(f"Root Cause: {rca_result['root_cause']}")
    report.append(f"Severity: {rca_result['severity']}")
    report.append(f"Confidence: {rca_result['confidence']}")
    report.append("")

    # Remediation
    report.append("🛠️ REMEDIATION PLAN")
    for idx, action in enumerate(remediation_plan["actions"], start=1):
        approval = "Yes" if action["requires_approval"] else "No"
        report.append(
            f"{idx}. {action['description']} "
            f"(Risk: {action['risk']}, Approval Required: {approval})"
        )

    report.append("")
    report.append("=" * 80)

    return "\n".join(report)


def send_notification(incident_data, rca_result, remediation_plan):
    """
    Print the incident report to the console.
    """
    report = format_incident_report(
        incident_data,
        rca_result,
        remediation_plan
    )
    print(report)
    return report


if __name__ == "__main__":
    sample_incident = {
        "pod_name": "crash-demo-abc123",
        "namespace": "default",
        "status": "CrashLoopBackOff",
        "restart_count": 7,
    }

    sample_rca = {
        "root_cause": "Container exits immediately with exit code 1.",
        "severity": "high",
        "confidence": 0.98,
    }

    sample_remediation = {
        "actions": [
            {
                "description": "Inspect startup command.",
                "risk": "safe",
                "requires_approval": False,
            },
            {
                "description": "Roll back deployment.",
                "risk": "risky",
                "requires_approval": True,
            },
        ]
    }

    send_notification(
        sample_incident,
        sample_rca,
        sample_remediation
    )