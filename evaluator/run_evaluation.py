import json
from pathlib import Path

from rca_agent.rca import analyze_incident
from evaluator.scoring import overall_score


def run_evaluation():
    dataset_path = Path("evaluator/datasets/golden_dataset.json")
    results_dir = Path("evaluator/results")
    results_dir.mkdir(parents=True, exist_ok=True)

    # Load golden dataset
    dataset = json.loads(dataset_path.read_text(encoding="utf-8"))

    report = []

    for case in dataset:
        print(f"Evaluating: {case['name']}")

        # Run RCA on the synthetic incident
        result = analyze_incident(case["incident_data"])

        # Score the result
        scores = overall_score(result, case["expected"])

        report.append({
            "name": case["name"],
            "scores": scores,
            "result": result
        })

    # Compute average overall score
    avg_score = (
        sum(item["scores"]["overall_score"] for item in report)
        / len(report)
    )

    summary = {
        "average_overall_score": round(avg_score, 3),
        "num_cases": len(report),
        "cases": report
    }

    output_file = results_dir / "evaluation_report.json"
    output_file.write_text(
        json.dumps(summary, indent=2),
        encoding="utf-8"
    )

    print("\nEvaluation complete.")
    print(f"Average Overall Score: {summary['average_overall_score']}")
    print(f"Report saved to: {output_file}")

    return summary


if __name__ == "__main__":
    run_evaluation()