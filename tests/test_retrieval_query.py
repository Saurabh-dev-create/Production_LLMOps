from rag.retriever import build_retrieval_query


def test_query_includes_status_events_and_logs():
    incident = {
        "status": "Degraded",
        "events": [
            "External API returned HTTP 429",
        ],
        "logs": (
            "Rate limit exceeded for upstream model provider"
        ),
    }

    query = build_retrieval_query(incident)

    assert "Degraded" in query
    assert "HTTP 429" in query
    assert "Rate limit exceeded" in query


def test_pending_scheduling_contains_cpu_evidence():
    incident = {
        "status": "Pending",
        "events": [
            "0/6 nodes are available: insufficient cpu",
            "Preemption is not helpful for scheduling",
        ],
        "logs": "",
    }

    query = build_retrieval_query(incident)

    assert "Pending" in query
    assert "insufficient cpu" in query
    assert "Preemption" in query


def test_pending_pvc_contains_storage_evidence():
    incident = {
        "status": "Pending",
        "events": [
            "PersistentVolumeClaim is not bound",
            "No persistent volumes available for this claim",
        ],
        "logs": "",
    }

    query = build_retrieval_query(incident)

    assert "PersistentVolumeClaim" in query
    assert "persistent volumes" in query


def test_query_handles_missing_optional_fields():
    query = build_retrieval_query(
        {
            "status": "OOMKilled",
        }
    )

    assert query == "OOMKilled"


def test_query_ignores_empty_values():
    query = build_retrieval_query(
        {
            "status": "",
            "events": [],
            "logs": "",
        }
    )

    assert query == ""
