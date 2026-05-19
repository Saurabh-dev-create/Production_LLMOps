import json
from pathlib import Path


def generate_markdown_report():
    input_file = Path("evaluator/results/evaluation_report.json")
    output_file = Path("evaluator/results/evaluation_report.md")

    if not input_file.exists():
        raise FileNotFoundError(
            "evaluation_report.json not found. Run 'python -m evaluator.run_evaluation' first."
        )

    data = json.loads(input_file.read_text(encoding="utf-8"))

    avg_score = data["average_overall_score"]
    num_cases = data["num_cases"]

    # Simple pass/fail threshold
    status = "PASS" if avg_score >= 0.70 else "FAIL"

    lines = [
        "# Evaluation Report",
        "",
        f"**Average Overall Score:** {avg_score}",
        f"**Number of Cases:** {num_cases}",
        f"**Status:** {status}",
        "",
        "## Case Results",
        ""
    ]

    for case in data["cases"]:
        name = case["name"]
        scores = case["scores"]

        lines.extend([
            f"### {name}",
            "",
            f"- Root Cause Score: {scores['root_cause_score']}",
            f"- Severity Score: {scores['severity_score']}",
            f"- Recommended Actions Score: {scores['recommended_actions_score']}",
            f"- Overall Score: {scores['overall_score']}",
            ""
        ])

    lines.extend([
        "## Recommendations",
        "",
        "- Improve prompts if scores are consistently below target.",
        "- Expand the golden dataset with more incident categories.",
        "- Add stricter thresholds in CI/CD.",
        ""
    ])

    output_file.write_text("\n".join(lines), encoding="utf-8")

    print(f"Markdown report generated: {output_file}")

    return output_file


if __name__ == "__main__":
    generate_markdown_report()