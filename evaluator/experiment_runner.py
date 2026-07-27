import json
from dataclasses import asdict, dataclass
from pathlib import Path

from evaluator.scoring import overall_score
from rca_agent.rca import analyze_incident
from evaluator.datasets.loader import load_dataset

RESULTS_DIR = Path("evaluator/results")
OUTPUT_FILE = RESULTS_DIR / "experiment_results.json"


@dataclass(frozen=True)
class ExperimentConfig:
    name: str
    prompt_version: str
    use_rag: bool
    model: str = "gpt-4.1-mini"


EXPERIMENTS = [
    ExperimentConfig(
        name="prompt_v1_without_rag",
        prompt_version="v1",
        use_rag=False,
    ),
    ExperimentConfig(
        name="prompt_v2_without_rag",
        prompt_version="v2",
        use_rag=False,
    ),
    ExperimentConfig(
        name="prompt_v1_with_rag",
        prompt_version="v1",
        use_rag=True,
    ),
    ExperimentConfig(
        name="prompt_v2_with_rag",
        prompt_version="v2",
        use_rag=True,
    ),
]





def run_single_experiment(
    config: ExperimentConfig,
    dataset: list[dict],
    analyzer=analyze_incident,
) -> dict:
    case_results = []

    for case in dataset:
        print(f"  Evaluating case: {case['name']}")

        result = analyzer(
            case["incident_data"],
            prompt_version=config.prompt_version,
            use_rag=config.use_rag,
            model=config.model,
        )

        scores = overall_score(result, case["expected"])

        case_results.append(
            {
                "name": case["name"],
                "scores": scores,
                "result": result,
            }
        )

    average_score = sum(
        item["scores"]["overall_score"]
        for item in case_results
    ) / len(case_results)

    return {
        "config": asdict(config),
        "average_overall_score": round(average_score, 3),
        "num_cases": len(case_results),
        "cases": case_results,
    }


def run_experiments(max_cases: int | None = None,
                    analyzer=analyze_incident,) -> dict:
    dataset = load_dataset()
    if max_cases is not None:
       if max_cases < 1:
         raise ValueError("max_cases must be at least 1")

       dataset = dataset[:max_cases]

    RESULTS_DIR.mkdir(parents=True, exist_ok=True)

    experiment_results = []

    for config in EXPERIMENTS:
        print(f"\nRunning experiment: {config.name}")

        experiment_results.append(
            run_single_experiment(config, dataset,analyzer=analyzer)
        )

    ranked_results = sorted(
        experiment_results,
        key=lambda item: item["average_overall_score"],
        reverse=True,
    )

    summary = {
        "best_experiment": ranked_results[0]["config"]["name"],
        "experiments": ranked_results,
    }

    OUTPUT_FILE.write_text(
        json.dumps(summary, indent=2),
        encoding="utf-8",
    )

    print("\nExperiment run complete.")
    print(f"Best experiment: {summary['best_experiment']}")
    print(f"Results saved to: {OUTPUT_FILE}")

    return summary


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(
        description="Run prompt and RAG experiments."
    )
    parser.add_argument(
        "--max-cases",
        type=int,
        default=None,
        help="Limit the number of incident cases.",
    )

    args = parser.parse_args()
    run_experiments(max_cases=args.max_cases)
