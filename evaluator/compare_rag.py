import json
from pathlib import Path

from collector_agent.collector import collect_incident_data
from rca_agent.rca import analyze_incident
from rag.retriever import retrieve_context


def analyze_without_rag(incident_data):
    """
    Temporarily disable RAG by monkey-patching retrieve_context.
    """
    import rca_agent.rca as rca_module

    original = rca_module.retrieve_context
    rca_module.retrieve_context = lambda query: "No additional context."

    try:
        result = analyze_incident(incident_data)
    finally:
        rca_module.retrieve_context = original

    return result


def analyze_with_rag(incident_data):
    return analyze_incident(incident_data)


def compare_outputs():
    incident_data = collect_incident_data()

    print("Running baseline RCA (without RAG)...")
    baseline = analyze_without_rag(incident_data)

    print("Running RAG-enhanced RCA...")
    rag_result = analyze_with_rag(incident_data)

    output_dir = Path("evaluator/results")
    output_dir.mkdir(parents=True, exist_ok=True)

    (output_dir / "baseline_rca.json").write_text(
        json.dumps(baseline, indent=2),
        encoding="utf-8"
    )

    (output_dir / "rag_rca.json").write_text(
        json.dumps(rag_result, indent=2),
        encoding="utf-8"
    )

    print("\nResults saved to evaluator/results/")
    print("- baseline_rca.json")
    print("- rag_rca.json")


if __name__ == "__main__":
    compare_outputs()