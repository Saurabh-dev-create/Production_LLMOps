import json
import sys
from pathlib import Path
from typing import Callable


RESULTS_DIR = Path("evaluator/results")
RESULTS_FILE = RESULTS_DIR / "retrieval_evaluation.json"

MIN_TOP1_ACCURACY = 0.80
MIN_TOP2_ACCURACY = 0.95


EXPECTED_SOURCES = {
    "api_rate_limit_case":
        "api_rate_limit_runbook.md",
    "database_connection_failure_case":
        "database_connection_runbook.md",
    "disk_full_case":
        "disk_full_runbook.md",
    "high_cpu_case":
        "high_cpu_runbook.md",
    "memory_pressure_case":
        "memory_pressure_runbook.md",
    "crashloopbackoff_case":
        "crashloop_runbook.md",
    "failed_scheduling_case":
        "failed_scheduling_runbook.md",
    "imagepullbackoff_case":
        "image_pull_backoff.md",
    "node_not_ready_case":
        "node_not_ready_runbook.md",
    "oomkilled_case":
        "oomkilled_runbook.md",
    "pvc_pending_case":
        "pending_pod_runbook.md",
    "readiness_probe_failure_case":
        "readiness_probe_runbook.md",
    "dns_failure_case":
        "dns_failure_runbook.md",
    "ingress_502_case":
        "ingress_502_runbook.md",
    "service_timeout_case":
        "service_timeout_runbook.md",
}


def load_cases() -> list[dict]:
    cases = []

    for path in sorted(
        Path("evaluator/datasets").rglob("*.json")
    ):
        data = json.loads(
            path.read_text(encoding="utf-8")
        )

        if (
            isinstance(data, dict)
            and "name" in data
            and "incident_data" in data
        ):
            cases.append(data)

    return cases


def evaluate_retrieval(
    retriever: Callable | None = None,
    query_builder: Callable | None = None,
    write_results: bool = True,
) -> dict:
    """
    Evaluate RAG retrieval independently from LLM generation.

    Returns structured Top-1 and Top-2 retrieval metrics so the
    result can be consumed by tests, CI, and reporting.
    """
    if retriever is None or query_builder is None:
        from rag.retriever import (
            build_retrieval_query,
            retrieve_documents,
        )

        retriever = retriever or retrieve_documents
        query_builder = query_builder or build_retrieval_query

    cases = load_cases()

    if not cases:
        raise ValueError(
            "No retrieval evaluation cases were found."
        )

    top1_hits = 0
    top2_hits = 0
    case_results = []

    print()
    print("RAG RETRIEVAL EVALUATION")
    print("=" * 100)

    for case in cases:
        name = case["name"]

        expected = EXPECTED_SOURCES.get(name)

        if expected is None:
            raise KeyError(
                f"No expected runbook configured for {name}"
            )

        query = query_builder(
            case["incident_data"]
        )

        documents = retriever(
            query,
            k=2,
        )

        sources = [
            document["source"]
            for document in documents
        ]

        top1_pass = (
            bool(sources)
            and sources[0] == expected
        )

        top2_pass = expected in sources

        if top1_pass:
            top1_hits += 1

        if top2_pass:
            top2_hits += 1

        retrieved_documents = [
            {
                "rank": index,
                "source": document["source"],
                "score": document.get(
                    "score",
                    0.0,
                ),
            }
            for index, document in enumerate(
                documents,
                start=1,
            )
        ]

        case_results.append(
            {
                "name": name,
                "expected_source": expected,
                "query": query,
                "retrieved": retrieved_documents,
                "top1_pass": top1_pass,
                "top2_pass": top2_pass,
            }
        )

        print()
        print(f"CASE     : {name}")
        print(f"EXPECTED : {expected}")
        print(f"QUERY    : {query}")

        for document in retrieved_documents:
            print(
                f"TOP {document['rank']:<2}   : "
                f"{document['source']} "
                f"(score={document['score']:.4f})"
            )

        print(
            "RESULT   : "
            f"Top-1={'PASS' if top1_pass else 'FAIL'} "
            f"Top-2={'PASS' if top2_pass else 'FAIL'}"
        )

    total = len(cases)

    top1_accuracy = top1_hits / total
    top2_accuracy = top2_hits / total

    top1_gate_passed = (
        top1_accuracy >= MIN_TOP1_ACCURACY
    )

    top2_gate_passed = (
        top2_accuracy >= MIN_TOP2_ACCURACY
    )

    gate_passed = (
        top1_gate_passed
        and top2_gate_passed
    )

    summary = {
        "status": (
            "PASS"
            if gate_passed
            else "FAIL"
        ),
        "thresholds": {
            "min_top1_accuracy":
                MIN_TOP1_ACCURACY,
            "min_top2_accuracy":
                MIN_TOP2_ACCURACY,
        },
        "metrics": {
            "total_cases": total,
            "top1_hits": top1_hits,
            "top2_hits": top2_hits,
            "top1_accuracy": round(
                top1_accuracy,
                4,
            ),
            "top2_accuracy": round(
                top2_accuracy,
                4,
            ),
        },
        "cases": case_results,
    }

    print()
    print("=" * 100)
    print("RETRIEVAL SUMMARY")
    print("=" * 100)

    print(
        f"Cases          : {total}"
    )

    print(
        f"Top-1 accuracy : "
        f"{top1_hits}/{total} "
        f"({top1_accuracy:.1%})"
    )

    print(
        f"Top-2 accuracy : "
        f"{top2_hits}/{total} "
        f"({top2_accuracy:.1%})"
    )

    print()
    print("QUALITY GATE")
    print("=" * 100)

    print(
        f"Top-1 threshold: "
        f"{MIN_TOP1_ACCURACY:.0%} "
        f"=> "
        f"{'PASS' if top1_gate_passed else 'FAIL'}"
    )

    print(
        f"Top-2 threshold: "
        f"{MIN_TOP2_ACCURACY:.0%} "
        f"=> "
        f"{'PASS' if top2_gate_passed else 'FAIL'}"
    )

    print(
        f"Overall result : "
        f"{summary['status']}"
    )

    if write_results:
        RESULTS_DIR.mkdir(
            parents=True,
            exist_ok=True,
        )

        RESULTS_FILE.write_text(
            json.dumps(
                summary,
                indent=2,
            ),
            encoding="utf-8",
        )

        print()
        print(
            f"Results saved to: {RESULTS_FILE}"
        )

    return summary


def main() -> None:
    try:
        result = evaluate_retrieval()

    except (
        FileNotFoundError,
        KeyError,
        TypeError,
        ValueError,
    ) as exc:
        print(
            f"Error: {exc}",
            file=sys.stderr,
        )
        sys.exit(2)

    if result["status"] == "FAIL":
        sys.exit(1)


if __name__ == "__main__":
    main()
