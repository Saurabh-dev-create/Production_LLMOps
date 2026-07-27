import json

import pytest

from evaluator.compare_prompts import (
    calculate_percentage_change,
    compare_experiments,
    find_experiment,
    get_experiments,
    load_experiment_results,
)


def build_experiment(
    name,
    score=0.90,
    latency_ms=800.0,
    cost_usd=0.03,
):
    return {
        "experiment_name": name,
        "average_overall_score": score,
        "average_latency_ms": latency_ms,
        "estimated_total_cost_usd": cost_usd,
    }


def test_load_experiment_results(tmp_path):
    results_file = tmp_path / "results.json"
    expected = {
        "experiments": [
            build_experiment("baseline")
        ]
    }

    results_file.write_text(
        json.dumps(expected),
        encoding="utf-8",
    )

    assert load_experiment_results(
        results_file
    ) == expected


def test_missing_results_file_is_rejected(tmp_path):
    missing_file = tmp_path / "missing.json"

    with pytest.raises(FileNotFoundError):
        load_experiment_results(missing_file)


def test_get_experiments():
    experiments = [
        build_experiment("baseline"),
        build_experiment("candidate"),
    ]

    assert get_experiments(
        {"experiments": experiments}
    ) == experiments


def test_find_experiment():
    experiments = [
        build_experiment("baseline"),
        build_experiment("candidate"),
    ]

    result = find_experiment(
        experiments,
        "candidate",
    )

    assert result["experiment_name"] == "candidate"


def test_find_experiment_lists_available_names():
    experiments = [
        build_experiment("baseline"),
        build_experiment("candidate"),
    ]

    with pytest.raises(
        ValueError,
        match="baseline, candidate",
    ):
        find_experiment(
            experiments,
            "missing",
        )


def test_compare_experiments_passes():
    baseline = build_experiment(
        "prompt_v1_without_rag"
    )
    candidate = build_experiment(
        "prompt_v2_without_rag",
        score=0.92,
        latency_ms=750.0,
        cost_usd=0.028,
    )

    result = compare_experiments(
        baseline,
        candidate,
    )

    assert result["status"] == "PASS"
    assert (
        result["baseline_experiment"]
        == "prompt_v1_without_rag"
    )
    assert (
        result["candidate_experiment"]
        == "prompt_v2_without_rag"
    )


def test_compare_experiments_fails():
    baseline = build_experiment("baseline")
    candidate = build_experiment(
        "candidate",
        score=0.80,
        latency_ms=1200.0,
        cost_usd=0.05,
    )

    result = compare_experiments(
        baseline,
        candidate,
    )

    assert result["status"] == "FAIL"


def test_calculate_percentage_change():
    assert (
        calculate_percentage_change(
            100.0,
            125.0,
        )
        == 25.0
    )
    assert (
        calculate_percentage_change(
            100.0,
            80.0,
        )
        == -20.0
    )
    assert (
        calculate_percentage_change(
            0.0,
            0.0,
        )
        == 0.0
    )
    assert (
        calculate_percentage_change(
            0.0,
            1.0,
        )
        is None
    )
