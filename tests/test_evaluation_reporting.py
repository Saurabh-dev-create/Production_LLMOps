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
                "num_cases": 1,
                "cases": [
                    {
                        "name": "api_rate_limit_case",
                        "scores": {
                            "overall_score": 0.925,
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
                "num_cases": 1,
                "cases": [
                    {
                        "name": "api_rate_limit_case",
                        "scores": {
                            "overall_score": 0.700,
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


def test_write_markdown_report_creates_file(tmp_path):
    output_path = tmp_path / "evaluation_report.md"

    result = write_markdown_report(
        build_summary(),
        output_path,
    )

    assert result == output_path
    assert output_path.exists()
    assert "Experiment Leaderboard" in output_path.read_text(
        encoding="utf-8"
    )
