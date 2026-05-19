import json
from pathlib import Path

from rca_agent.rca import analyze_incident
from evaluator.scoring import overall_score


def evaluate_prompt_version(version: str) -> float:
    dataset_path = Path("evaluator/datasets/golden_dataset.json")
    dataset = json.loads(dataset_path.read_text(encoding="utf-8"))

    total = 0.0

    for case in dataset:
        result = analyze_incident(
            case["incident_data"],
            prompt_version=version
        )

        scores = overall_score(result, case["expected"])
        total += scores["overall_score"]

    return round(total / len(dataset), 3)


def compare_prompts():
    print("Evaluating prompt v1...")
    score_v1 = evaluate_prompt_version("v1")

    print("Evaluating prompt v2...")
    score_v2 = evaluate_prompt_version("v2")

    best_version = "v1" if score_v1 >= score_v2 else "v2"

    results = {
        "v1_score": score_v1,
        "v2_score": score_v2,
        "best_version": best_version
    }

    output_dir = Path("evaluator/results")
    output_dir.mkdir(parents=True, exist_ok=True)

    output_file = output_dir / "prompt_comparison.json"
    output_file.write_text(
        json.dumps(results, indent=2),
        encoding="utf-8"
    )

    print("\nPrompt Comparison Results")
    print(f"v1 Score: {score_v1}")
    print(f"v2 Score: {score_v2}")
    print(f"Best Version: {best_version}")
    print(f"Saved to: {output_file}")

    return results


if __name__ == "__main__":
    compare_prompts()