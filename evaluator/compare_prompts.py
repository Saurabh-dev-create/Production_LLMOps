import argparse
import json
import sys
from pathlib import Path
from typing import Any

from evaluator.check_thresholds import (
    RegressionThresholds,
    evaluate_regression,
)


DEFAULT_RESULTS_PATH = Path(
    "evaluator/results/experiment_results.json"
)


def load_experiment_results(
    results_path: Path,
) -> dict[str, Any]:
    if not results_path.exists():
        raise FileNotFoundError(
            f"{results_path} not found. Run "
            "'python -m evaluator.experiment_runner' first."
        )

    try:
        data = json.loads(
            results_path.read_text(encoding="utf-8")
        )
    except json.JSONDecodeError as exc:
        raise ValueError(
            f"{results_path} contains invalid JSON"
        ) from exc

    if not isinstance(data, dict):
        raise TypeError(
            "Experiment results must contain a JSON object"
        )

    return data


def get_experiments(
    data: dict[str, Any],
) -> list[dict[str, Any]]:
    experiments = data.get("experiments")

    if not isinstance(experiments, list):
        raise KeyError(
            "Experiment results are missing an "
            "'experiments' list"
        )

    return experiments


def find_experiment(
    experiments: list[dict[str, Any]],
    experiment_name: str,
) -> dict[str, Any]:
    for experiment in experiments:
        if experiment.get("experiment_name") == experiment_name:
            return experiment

    available_names = sorted(
        str(experiment.get("experiment_name"))
        for experiment in experiments
        if experiment.get("experiment_name")
    )

    available_text = (
        ", ".join(available_names)
        if available_names
        else "none"
    )

    raise ValueError(
        f"Experiment '{experiment_name}' was not found. "
        f"Available experiments: {available_text}"
    )


def calculate_percentage_change(
    baseline_value: float,
    candidate_value: float,
) -> float | None:
    if baseline_value == 0:
        if candidate_value == 0:
            return 0.0
        return None

    return (
        (candidate_value - baseline_value)
        / baseline_value
    ) * 100


def format_percentage(
    value: float | None,
) -> str:
    if value is None:
        return "undefined"

    return f"{value:+.2f}%"


def compare_experiments(
    baseline: dict[str, Any],
    candidate: dict[str, Any],
    thresholds: RegressionThresholds | None = None,
) -> dict[str, Any]:
    result = evaluate_regression(
        baseline=baseline,
        candidate=candidate,
        thresholds=thresholds,
    )

    result["baseline_experiment"] = baseline.get(
        "experiment_name",
        "unknown",
    )
    result["candidate_experiment"] = candidate.get(
        "experiment_name",
        "unknown",
    )

    return result


def print_regression_report(
    result: dict[str, Any],
) -> None:
    quality = result["quality"]
    latency = result["latency"]
    cost = result["cost"]

    score_change = (
        quality["candidate"] - quality["baseline"]
    )

    latency_change = calculate_percentage_change(
        latency["baseline_ms"],
        latency["candidate_ms"],
    )

    cost_change = calculate_percentage_change(
        cost["baseline_usd"],
        cost["candidate_usd"],
    )

    print()
    print("Prompt Regression Report")
    print("=" * 48)
    print(
        f"Baseline : "
        f"{result['baseline_experiment']}"
    )
    print(
        f"Candidate: "
        f"{result['candidate_experiment']}"
    )

    print()
    print("Quality")
    print("-" * 48)
    print(
        f"Baseline : {quality['baseline']:.4f}"
    )
    print(
        f"Candidate: {quality['candidate']:.4f}"
    )
    print(f"Change   : {score_change:+.4f}")
    print(f"Status   : {quality['status']}")

    print()
    print("Latency")
    print("-" * 48)
    print(
        f"Baseline : "
        f"{latency['baseline_ms']:.2f} ms"
    )
    print(
        f"Candidate: "
        f"{latency['candidate_ms']:.2f} ms"
    )
    print(
        f"Change   : "
        f"{format_percentage(latency_change)}"
    )
    print(f"Status   : {latency['status']}")

    print()
    print("Cost")
    print("-" * 48)
    print(
        f"Baseline : "
        f"${cost['baseline_usd']:.6f}"
    )
    print(
        f"Candidate: "
        f"${cost['candidate_usd']:.6f}"
    )
    print(
        f"Change   : "
        f"{format_percentage(cost_change)}"
    )
    print(f"Status   : {cost['status']}")

    print()
    print("Overall Result")
    print("-" * 48)
    print(result["status"])


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description=(
            "Compare a candidate prompt experiment "
            "against a baseline experiment."
        )
    )

    parser.add_argument(
        "--baseline",
        required=True,
        help="Approved baseline experiment name",
    )
    parser.add_argument(
        "--candidate",
        required=True,
        help="Candidate experiment name",
    )
    parser.add_argument(
        "--results-file",
        type=Path,
        default=DEFAULT_RESULTS_PATH,
        help=(
            "Path to experiment results JSON "
            f"(default: {DEFAULT_RESULTS_PATH})"
        ),
    )
    parser.add_argument(
        "--max-score-drop",
        type=float,
        default=None,
        help="Maximum allowed absolute score drop",
    )
    parser.add_argument(
        "--max-latency-increase",
        type=float,
        default=None,
        help=(
            "Maximum allowed latency increase ratio, "
            "for example 0.25 for 25%%"
        ),
    )
    parser.add_argument(
        "--max-cost-increase",
        type=float,
        default=None,
        help=(
            "Maximum allowed cost increase ratio, "
            "for example 0.20 for 20%%"
        ),
    )

    return parser.parse_args()


def build_thresholds(
    args: argparse.Namespace,
) -> RegressionThresholds:
    defaults = RegressionThresholds()

    return RegressionThresholds(
        min_overall_score=defaults.min_overall_score,
        max_score_drop=(
            args.max_score_drop
            if args.max_score_drop is not None
            else defaults.max_score_drop
        ),
        max_latency_increase_ratio=(
            args.max_latency_increase
            if args.max_latency_increase is not None
            else defaults.max_latency_increase_ratio
        ),
        max_cost_increase_ratio=(
            args.max_cost_increase
            if args.max_cost_increase is not None
            else defaults.max_cost_increase_ratio
        ),
    )

def compare_prompts(
    baseline_name: str = "prompt_v1_without_rag",
    candidate_name: str = "prompt_v2_without_rag",
    results_path: Path = DEFAULT_RESULTS_PATH,
    thresholds: RegressionThresholds | None = None,
) -> dict[str, Any]:
    """
    Compare two named experiments from an existing results file.

    This function preserves the original public API name while using
    the new regression-gate implementation.
    """

    data = load_experiment_results(results_path)
    experiments = get_experiments(data)

    baseline = find_experiment(
        experiments,
        baseline_name,
    )
    candidate = find_experiment(
        experiments,
        candidate_name,
    )

    result = compare_experiments(
        baseline=baseline,
        candidate=candidate,
        thresholds=thresholds,
    )

    return result

def main() -> None:
    args = parse_args()

    try:
        result = compare_prompts(
        baseline_name=args.baseline,
        candidate_name=args.candidate,
        results_path=args.results_file,
        thresholds=build_thresholds(args),
    )

        print_regression_report(result)

    except (
        FileNotFoundError,
        ValueError,
        TypeError,
        KeyError,
    ) as exc:
        print(f"Error: {exc}", file=sys.stderr)
        sys.exit(2)

    if result["status"] == "FAIL":
        sys.exit(1)


if __name__ == "__main__":
    main()
