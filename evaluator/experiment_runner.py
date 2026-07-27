import json
from dataclasses import asdict, dataclass
from pathlib import Path

from evaluator.scoring import overall_score
from rca_agent.rca import analyze_incident
from evaluator.datasets.loader import load_dataset
from evaluator.reporting import write_markdown_report
from time import perf_counter

RESULTS_DIR = Path("evaluator/results")
OUTPUT_FILE = RESULTS_DIR / "experiment_results.json"
REPORT_FILE = RESULTS_DIR / "evaluation_report.md"

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
def extract_usage_metrics(result: dict) -> dict:
    metadata = result.get("_metadata", {})
    usage = metadata.get("usage", {})

    prompt_tokens = int(usage.get("prompt_tokens", 0))
    completion_tokens = int(usage.get("completion_tokens", 0))

    total_tokens = int(
        usage.get(
            "total_tokens",
            prompt_tokens + completion_tokens,
        )
    )

    estimated_cost_usd = float(
        metadata.get("estimated_cost_usd", 0.0)
    )

    return {
        "prompt_tokens": prompt_tokens,
        "completion_tokens": completion_tokens,
        "total_tokens": total_tokens,
        "estimated_cost_usd": round(
            estimated_cost_usd,
            6,
        ),
    }
def run_single_experiment(
    config: ExperimentConfig,
    dataset: list[dict],
    analyzer=analyze_incident,
) -> dict:
    case_results = []

    for case in dataset:
        print(f"  Evaluating case: {case['name']}")

        started_at = perf_counter()

        result = analyzer(
           case["incident_data"],
           prompt_version=config.prompt_version,
           use_rag=config.use_rag,
           model=config.model,
        )

        latency_ms = round(
           (perf_counter() - started_at) * 1000,
           2,
        )

        metrics = extract_usage_metrics(result)
        metrics["latency_ms"] = latency_ms

        scores = overall_score(result, case["expected"])

        case_results.append(
            {
                "name": case["name"],
                "scores": scores,
                "metrics": metrics,
                "result": result,
            }
        )

    average_score = sum(
        item["scores"]["overall_score"]
        for item in case_results
    ) / len(case_results)
    average_latency_ms = sum(
        item["metrics"]["latency_ms"]
        for item in case_results
    ) / len(case_results)

    total_prompt_tokens = sum(
        item["metrics"]["prompt_tokens"]
        for item in case_results
   )

    total_completion_tokens = sum(
        item["metrics"]["completion_tokens"]
        for item in case_results
   )

    total_tokens = sum(
        item["metrics"]["total_tokens"]
        for item in case_results
   )

    estimated_total_cost_usd = sum(
        item["metrics"]["estimated_cost_usd"]
        for item in case_results
  )

    return {
        "config": asdict(config),
        "average_overall_score": round(average_score, 3),
        "average_latency_ms": round(average_latency_ms, 2),
        "total_prompt_tokens": total_prompt_tokens,
        "total_completion_tokens": total_completion_tokens,
        "total_tokens": total_tokens,
          "estimated_total_cost_usd": round(
             estimated_total_cost_usd,
             6,
        ),
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
    write_markdown_report(
      summary,
      REPORT_FILE,
    )

    print("\nExperiment run complete.")
    print(f"Best experiment: {summary['best_experiment']}")
    print(f"Results saved to: {OUTPUT_FILE}")
    print(f"Markdown report saved to: {REPORT_FILE}")
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
