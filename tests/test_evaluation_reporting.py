from evaluator.reporting import (
    generate_markdown_report,
    write_markdown_report,
)


def build_summary():
    return {
        "best_experiment": "prompt_v2_with_rag",
        "experiments": [
            {
                "config": {
                    "name": "prompt_v2_with_rag",
                    "prompt_version": "v2",
                    "use_rag": True,
                    "model": "gpt-4.1-mini",
                },
                "average_overall_score": 0.925,
                "average_latency_ms": 125.5,
                "total_prompt_tokens": 120,
                "total_completion_tokens": 80,
                "total_tokens": 200,
                "estimated_total_cost_usd": 0.00012,
                "num_cases": 1,
                "cases": [
                    {
                        "name": "api_rate_limit_case",
                        "scores": {
                            "overall_score": 0.925,
                        },
                        "metrics": {
                            "latency_ms": 125.5,
                            "prompt_tokens": 120,
                            "completion_tokens": 80,
                            "total_tokens": 200,
                            "estimated_cost_usd": 0.00012,
                        },
                        "result": {},
                    }
                ],
            },
            {
                "config": {
                    "name": "prompt_v1_without_rag",
                    "prompt_version": "v1",
                    "use_rag": False,
                    "model": "gpt-4.1-mini",
                },
                "average_overall_score": 0.700,
                "average_latency_ms": 98.25,
                "total_prompt_tokens": 100,
                "total_completion_tokens": 60,
                "total_tokens": 160,
                "estimated_total_cost_usd": 0.00009,
                "num_cases": 1,
                "cases": [
                    {
                        "name": "api_rate_limit_case",
                        "scores": {
                            "overall_score": 0.700,
                        },
                        "metrics": {
                            "latency_ms": 98.25,
                            "prompt_tokens": 100,
                            "completion_tokens": 60,
                            "total_tokens": 160,
                            "estimated_cost_usd": 0.00009,
                        },
                        "result": {},
                    }
                ],
            },
        ],
    }


def test_generate_markdown_report_contains_leaderboard():
    report = generate_markdown_report(build_summary())

    assert "# Production LLMOps Evaluation Report" in report
    assert "Prompt V2 with RAG" in report
    assert "prompt_v2_with_rag" in report
    assert "api_rate_limit_case" in report
    assert "0.925" in report

    assert "Latency (ms)" in report
    assert "Tokens" in report
    assert "Cost (USD)" in report
    assert "125.50" in report
    assert "200" in report
    assert "0.000120" in report


def test_write_markdown_report_creates_file(tmp_path):
    output_path = tmp_path / "evaluation_report.md"

    result = write_markdown_report(
        build_summary(),
        output_path,
    )

    assert result == output_path
    assert output_path.exists()

    report = output_path.read_text(encoding="utf-8")

    assert "Experiment Leaderboard" in report
    assert "Case Breakdown" in report
    assert "Estimated cost" in report


def test_generate_markdown_report_rejects_empty_experiments():
    summary = {
        "best_experiment": None,
        "experiments": [],
    }

    try:
        generate_markdown_report(summary)
    except ValueError as error:
        assert str(error) == (
            "summary must contain at least one experiment"
        )
    else:
        raise AssertionError("Expected ValueError")
