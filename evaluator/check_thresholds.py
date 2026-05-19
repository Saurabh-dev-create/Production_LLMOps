import json
import sys
from pathlib import Path

# Minimum acceptable score
MIN_OVERALL_SCORE = 0.70


def check_thresholds():
    report_path = Path("evaluator/results/evaluation_report.json")

    if not report_path.exists():
        raise FileNotFoundError(
            "evaluation_report.json not found. Run 'python -m evaluator.run_evaluation' first."
        )

    data = json.loads(report_path.read_text(encoding="utf-8"))

    avg_score = data["average_overall_score"]

    print(f"Average Overall Score: {avg_score}")
    print(f"Minimum Required Score: {MIN_OVERALL_SCORE}")

    if avg_score < MIN_OVERALL_SCORE:
        print("❌ Evaluation failed: score below threshold.")
        sys.exit(1)

    print("✅ Evaluation passed.")


if __name__ == "__main__":
    check_thresholds()