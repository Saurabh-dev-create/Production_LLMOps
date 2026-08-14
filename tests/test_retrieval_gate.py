from evaluator import evaluate_retrieval


def fake_query_builder(incident_data):
    return incident_data.get(
        "status",
        "",
    )


def perfect_retriever(query, k=2):
    mapping = {
        case_name: source
        for case_name, source
        in evaluate_retrieval.EXPECTED_SOURCES.items()
    }

    cases = evaluate_retrieval.load_cases()

    for case in cases:
        if (
            case["incident_data"].get("status")
            == query
        ):
            expected = mapping[case["name"]]

            return [
                {
                    "source": expected,
                    "score": 1.0,
                    "content": "",
                }
            ]

    return []


def test_retrieval_threshold_constants():
    assert (
        evaluate_retrieval.MIN_TOP1_ACCURACY
        == 0.80
    )

    assert (
        evaluate_retrieval.MIN_TOP2_ACCURACY
        == 0.95
    )


def test_retrieval_evaluation_returns_metrics(
    monkeypatch,
):
    cases = [
        {
            "name": "api_rate_limit_case",
            "incident_data": {
                "status": "api-rate-limit",
            },
        },
        {
            "name": "disk_full_case",
            "incident_data": {
                "status": "disk-full",
            },
        },
    ]

    expected_by_query = {
        "api-rate-limit":
            "api_rate_limit_runbook.md",
        "disk-full":
            "disk_full_runbook.md",
    }

    def retriever(query, k=2):
        return [
            {
                "source":
                    expected_by_query[query],
                "score": 0.9,
                "content": "",
            }
        ]

    monkeypatch.setattr(
        evaluate_retrieval,
        "load_cases",
        lambda: cases,
    )

    result = (
        evaluate_retrieval.evaluate_retrieval(
            retriever=retriever,
            query_builder=fake_query_builder,
            write_results=False,
        )
    )

    assert result["status"] == "PASS"

    assert (
        result["metrics"]["top1_accuracy"]
        == 1.0
    )

    assert (
        result["metrics"]["top2_accuracy"]
        == 1.0
    )


def test_retrieval_gate_fails_below_threshold(
    monkeypatch,
):
    cases = [
        {
            "name": "api_rate_limit_case",
            "incident_data": {
                "status": "case-one",
            },
        },
        {
            "name": "disk_full_case",
            "incident_data": {
                "status": "case-two",
            },
        },
    ]

    def retriever(query, k=2):
        return [
            {
                "source": "wrong_runbook.md",
                "score": 0.1,
                "content": "",
            }
        ]

    monkeypatch.setattr(
        evaluate_retrieval,
        "load_cases",
        lambda: cases,
    )

    result = (
        evaluate_retrieval.evaluate_retrieval(
            retriever=retriever,
            query_builder=fake_query_builder,
            write_results=False,
        )
    )

    assert result["status"] == "FAIL"

    assert (
        result["metrics"]["top1_accuracy"]
        == 0.0
    )

    assert (
        result["metrics"]["top2_accuracy"]
        == 0.0
    )
