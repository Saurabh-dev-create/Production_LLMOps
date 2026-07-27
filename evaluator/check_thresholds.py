import json
import sys
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any


DEFAULT_REPORT_PATH = Path(
    "evaluator/results/evaluation_report.json"
)

# Existing absolute quality gate
MIN_OVERALL_SCORE = 0.25

FLOAT_TOLERANCE = 1e-9

# Regression limits
MAX_SCORE_DROP = 0.05
MAX_LATENCY_INCREASE_RATIO = 0.25
MAX_COST_INCREASE_RATIO = 0.20


@dataclass(frozen=True)
class RegressionThresholds:
    """
    Acceptance limits used when comparing a candidate experiment
    against an approved baseline.
    """

    min_overall_score: float = MIN_OVERALL_SCORE
    max_score_drop: float = MAX_SCORE_DROP
    max_latency_increase_ratio: float = (
        MAX_LATENCY_INCREASE_RATIO
    )
    max_cost_increase_ratio: float = (
        MAX_COST_INCREASE_RATIO
    )


def calculate_increase_ratio(
    baseline_value: float,
    candidate_value: float,
) -> float | None:
    """
    Calculate the proportional increase from baseline to candidate.

    Returns:
        0.0 when the candidate did not increase.
        A positive ratio when the candidate increased.
        None when the baseline is zero and the candidate increased,
        because the percentage increase is undefined.
    """

    if baseline_value < 0 or candidate_value < 0:
        raise ValueError("Metric values cannot be negative")

    if candidate_value <= baseline_value:
        return 0.0

    if baseline_value == 0:
        return None

    return (
        candidate_value - baseline_value
    ) / baseline_value


def _read_metric(
    experiment: dict[str, Any],
    metric_name: str,
) -> float:
    if metric_name not in experiment:
        raise KeyError(
            f"Experiment is missing required metric: "
            f"{metric_name}"
        )

    value = experiment[metric_name]

    if not isinstance(value, (int, float)):
        raise TypeError(
            f"Metric '{metric_name}' must be numeric"
        )

    return float(value)


def _increase_gate_passed(
    increase_ratio: float | None,
    maximum_allowed_ratio: float,
) -> bool:
    if increase_ratio is None:
        return False

    return (
        increase_ratio
        <= maximum_allowed_ratio + FLOAT_TOLERANCE
    )


def evaluate_regression(
    baseline: dict[str, Any],
    candidate: dict[str, Any],
    thresholds: RegressionThresholds | None = None,
) -> dict[str, Any]:
    """
    Compare candidate experiment metrics against an approved baseline.

    The candidate fails when:

    - its quality score falls below the absolute minimum;
    - its quality score drops more than the allowed amount;
    - its latency increases beyond the allowed percentage;
    - its estimated cost increases beyond the allowed percentage.
    """

    thresholds = thresholds or RegressionThresholds()

    baseline_score = _read_metric(
        baseline,
        "average_overall_score",
    )
    candidate_score = _read_metric(
        candidate,
        "average_overall_score",
    )

    baseline_latency = _read_metric(
        baseline,
        "average_latency_ms",
    )
    candidate_latency = _read_metric(
        candidate,
        "average_latency_ms",
    )

    baseline_cost = _read_metric(
        baseline,
        "estimated_total_cost_usd",
    )
    candidate_cost = _read_metric(
        candidate,
        "estimated_total_cost_usd",
    )

    score_drop = max(
        baseline_score - candidate_score,
        0.0,
    )

    latency_increase_ratio = calculate_increase_ratio(
        baseline_latency,
        candidate_latency,
    )

    cost_increase_ratio = calculate_increase_ratio(
        baseline_cost,
        candidate_cost,
    )

    quality_passed = (
        candidate_score
        >= thresholds.min_overall_score - FLOAT_TOLERANCE
        and score_drop
        <= thresholds.max_score_drop + FLOAT_TOLERANCE
    )

    latency_passed = _increase_gate_passed(
        latency_increase_ratio,
        thresholds.max_latency_increase_ratio,
    )

    cost_passed = _increase_gate_passed(
        cost_increase_ratio,
        thresholds.max_cost_increase_ratio,
    )

    overall_passed = (
        quality_passed
        and latency_passed
        and cost_passed
    )

    return {
        "status": "PASS" if overall_passed else "FAIL",
        "thresholds": asdict(thresholds),
        "quality": {
            "status": (
                "PASS" if quality_passed else "FAIL"
            ),
            "baseline": baseline_score,
            "candidate": candidate_score,
            "score_drop": round(score_drop, 6),
            "minimum_score": (
                thresholds.min_overall_score
            ),
            "maximum_allowed_drop": (
                thresholds.max_score_drop
            ),
        },
        "latency": {
            "status": (
                "PASS" if latency_passed else "FAIL"
            ),
            "baseline_ms": baseline_latency,
            "candidate_ms": candidate_latency,
            "increase_ratio": (
                None
                if latency_increase_ratio is None
                else round(latency_increase_ratio, 6)
            ),
            "maximum_allowed_increase_ratio": (
                thresholds.max_latency_increase_ratio
            ),
        },
        "cost": {
            "status": (
                "PASS" if cost_passed else "FAIL"
            ),
            "baseline_usd": baseline_cost,
            "candidate_usd": candidate_cost,
            "increase_ratio": (
                None
                if cost_increase_ratio is None
                else round(cost_increase_ratio, 6)
            ),
            "maximum_allowed_increase_ratio": (
                thresholds.max_cost_increase_ratio
            ),
        },
    }


def check_thresholds(
    report_path: Path = DEFAULT_REPORT_PATH,
) -> None:
    """
    Preserve the original absolute-score CLI gate.

    The baseline-versus-candidate CLI will be connected after the
    regression comparison engine is fully tested.
    """

    if not report_path.exists():
        raise FileNotFoundError(
            f"{report_path} not found. Run "
            "'python -m evaluator.run_evaluation' first."
        )

    data = json.loads(
        report_path.read_text(encoding="utf-8")
    )

    average_score = _read_metric(
        data,
        "average_overall_score",
    )

    print(f"Average Overall Score: {average_score}")
    print(f"Minimum Required Score: {MIN_OVERALL_SCORE}")

    if average_score < MIN_OVERALL_SCORE:
        print(
            "Evaluation failed: score below threshold."
        )
        sys.exit(1)

    print("Evaluation passed.")


if __name__ == "__main__":
    check_thresholds()
