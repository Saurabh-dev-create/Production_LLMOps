import json
from pathlib import Path

from collector_agent.collector import collect_incident_data
from rca_agent.rca import analyze_incident


RESULTS_DIR = Path("evaluator/results")


def analyze_without_rag(incident_data: dict) -> dict:
    """Run RCA without retrieved runbook context."""
    return analyze_incident(
        incident_data,
        use_rag=False,
    )


def analyze_with_rag(incident_data: dict) -> dict:
    """Run RCA with retrieved runbook context."""
    return analyze_incident(
        incident_data,
        use_rag=True,
    )


def compare_outputs() -> dict:
    incident_data = collect_incident_data()

    print("Running baseline RCA without RAG...")
    baseline = analyze_without_rag(incident_data)

    print("Running RAG-enhanced RCA...")
    rag_result = analyze_with_rag(incident_data)

    RESULTS_DIR.mkdir(parents=True, exist_ok=True)

    baseline_file = RESULTS_DIR / "baseline_rca.json"
    rag_file = RESULTS_DIR / "rag_rca.json"

    baseline_file.write_text(
        json.dumps(baseline, indent=2),
        encoding="utf-8",
    )

    rag_file.write_text(
        json.dumps(rag_result, indent=2),
        encoding="utf-8",
    )

    comparison = {
        "baseline": baseline,
        "rag": rag_result,
    }

    print("\nResults saved:")
    print(f"- {baseline_file}")
    print(f"- {rag_file}")

    return comparison


if __name__ == "__main__":
    compare_outputs()
