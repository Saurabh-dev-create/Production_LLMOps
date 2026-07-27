from evaluator import experiment_runner


def fake_analyzer(
    incident_data,
    prompt_version="v2",
    use_rag=True,
    model="gpt-4.1-mini",
):
    return {
        "root_cause": (
            "The API provider returned HTTP 429 because its rate "
            "limit and quota were exceeded."
        ),
        "severity": "medium",
        "recommended_actions": [
            "Retry requests using exponential backoff.",
            "Review the provider quota.",
        ],
        "_metadata": {
            "usage": {
                "prompt_tokens": 120,
                "completion_tokens": 80,
                "total_tokens": 200,
            },
            "estimated_cost_usd": 0.00012,
        },
    }


def test_experiment_runner_executes_offline(tmp_path, monkeypatch):
    output_file = tmp_path / "experiment_results.json"
    report_file = tmp_path / "evaluation_report.md"

    monkeypatch.setattr(
        experiment_runner,
        "OUTPUT_FILE",
        output_file,
    )
    monkeypatch.setattr(
        experiment_runner,
        "REPORT_FILE",
        report_file,
    )
    monkeypatch.setattr(
        experiment_runner,
        "RESULTS_DIR",
        tmp_path,
    )

    summary = experiment_runner.run_experiments(
        max_cases=1,
        analyzer=fake_analyzer,
    )

    assert len(summary["experiments"]) == 4
    assert all(
        experiment["num_cases"] == 1
        for experiment in summary["experiments"]
    )

    assert output_file.exists()
    assert report_file.exists()

    report = report_file.read_text(encoding="utf-8")

    assert "# Production LLMOps Evaluation Report" in report
    assert "Experiment Leaderboard" in report

    for experiment in summary["experiments"]:
        assert experiment["total_prompt_tokens"] == 120
        assert experiment["total_completion_tokens"] == 80
        assert experiment["total_tokens"] == 200
        assert experiment["estimated_total_cost_usd"] == 0.00012
        assert experiment["average_latency_ms"] >= 0

        case = experiment["cases"][0]

        assert case["metrics"]["prompt_tokens"] == 120
        assert case["metrics"]["completion_tokens"] == 80
        assert case["metrics"]["total_tokens"] == 200
        assert case["metrics"]["estimated_cost_usd"] == 0.00012
        assert case["metrics"]["latency_ms"] >= 0
