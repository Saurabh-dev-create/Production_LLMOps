import json
from pathlib import Path

from evaluator.datasets.loader import load_dataset
from evaluator.reporting import write_markdown_report
from evaluator.scoring import overall_score


RESULTS_PATH = Path(
    "evaluator/results/experiment_results.json"
)

REPORT_PATH = Path(
    "evaluator/results/evaluation_report.md"
)


def build_expected_lookup() -> dict[str, dict]:
    dataset = load_dataset()

    return {
        case["name"]: case["expected"]
        for case in dataset
    }


def rescore_results() -> dict:
    if not RESULTS_PATH.exists():
        raise FileNotFoundError(
            f"{RESULTS_PATH} not found"
        )

    data = json.loads(
        RESULTS_PATH.read_text(
            encoding="utf-8"
        )
    )

    expected_lookup = build_expected_lookup()

    for experiment in data["experiments"]:
        case_scores = []

        for case in experiment["cases"]:
            case_name = case["name"]

            if case_name not in expected_lookup:
                raise KeyError(
                    f"No expected result found for "
                    f"{case_name}"
                )

            scores = overall_score(
                case["result"],
                expected_lookup[case_name],
            )

            case["scores"] = scores

            case_scores.append(
                scores["overall_score"]
            )

        experiment["average_overall_score"] = round(
            sum(case_scores) / len(case_scores),
            3,
        )

    ranked_experiments = sorted(
        data["experiments"],
        key=lambda experiment: (
            experiment["average_overall_score"]
        ),
        reverse=True,
    )

    data["experiments"] = ranked_experiments

    data["best_experiment"] = (
        ranked_experiments[0]["config"]["name"]
    )

    RESULTS_PATH.write_text(
        json.dumps(
            data,
            indent=2,
        ),
        encoding="utf-8",
    )

    write_markdown_report(
        data,
        REPORT_PATH,
    )

    return data


if __name__ == "__main__":
    results = rescore_results()

    print("\nRE-SCORED BENCHMARK")
    print("=" * 90)

    for experiment in results["experiments"]:
        config = experiment["config"]

        print(
            f"{config['name']:28} "
            f"| score="
            f"{experiment['average_overall_score']:.3f} "
            f"| latency="
            f"{experiment['average_latency_ms']:.2f}ms "
            f"| tokens="
            f"{experiment['total_tokens']} "
            f"| cost=$"
            f"{experiment['estimated_total_cost_usd']:.6f}"
        )

    print()
    print(
        "Best experiment:",
        results["best_experiment"],
    )
