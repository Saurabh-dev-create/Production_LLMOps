import pytest

from evaluator.check_thresholds import (
    RegressionThresholds,
    calculate_increase_ratio,
    evaluate_regression,
)


def build_experiment(
    score=0.90,
    latency_ms=800.0,
    cost_usd=0.03,
):
    return {
        "average_overall_score": score,
        "average_latency_ms": latency_ms,
        "estimated_total_cost_usd": cost_usd,
    }


def test_candidate_passes_when_metrics_improve():
    baseline = build_experiment()
    candidate = build_experiment(
        score=0.93,
        latency_ms=750.0,
        cost_usd=0.028,
    )

    result = evaluate_regression(
        baseline,
        candidate,
    )

    assert result["status"] == "PASS"
    assert result["quality"]["status"] == "PASS"
    assert result["latency"]["status"] == "PASS"
    assert result["cost"]["status"] == "PASS"


def test_candidate_fails_when_score_drops_too_much():
    baseline = build_experiment(score=0.90)
    candidate = build_experiment(score=0.84)

    result = evaluate_regression(
        baseline,
        candidate,
    )

    assert result["status"] == "FAIL"
    assert result["quality"]["status"] == "FAIL"


def test_candidate_fails_when_latency_increases_too_much():
    baseline = build_experiment(latency_ms=800.0)
    candidate = build_experiment(latency_ms=1100.0)

    result = evaluate_regression(
        baseline,
        candidate,
    )

    assert result["status"] == "FAIL"
    assert result["latency"]["status"] == "FAIL"


def test_candidate_fails_when_cost_increases_too_much():
    baseline = build_experiment(cost_usd=0.03)
    candidate = build_experiment(cost_usd=0.04)

    result = evaluate_regression(
        baseline,
        candidate,
    )

    assert result["status"] == "FAIL"
    assert result["cost"]["status"] == "FAIL"


def test_exact_threshold_boundaries_pass():
    thresholds = RegressionThresholds(
        min_overall_score=0.25,
        max_score_drop=0.05,
        max_latency_increase_ratio=0.25,
        max_cost_increase_ratio=0.20,
    )

    baseline = build_experiment(
        score=0.90,
        latency_ms=800.0,
        cost_usd=0.03,
    )
    candidate = build_experiment(
        score=0.85,
        latency_ms=1000.0,
        cost_usd=0.036,
    )

    result = evaluate_regression(
        baseline,
        candidate,
        thresholds,
    )

    assert result["status"] == "PASS"


def test_candidate_fails_absolute_minimum_score():
    baseline = build_experiment(score=0.28)
    candidate = build_experiment(score=0.24)

    result = evaluate_regression(
        baseline,
        candidate,
    )

    assert result["status"] == "FAIL"
    assert result["quality"]["status"] == "FAIL"


def test_zero_baseline_with_increased_metric_fails():
    baseline = build_experiment(
        latency_ms=0.0,
        cost_usd=0.0,
    )
    candidate = build_experiment(
        latency_ms=10.0,
        cost_usd=0.001,
    )

    result = evaluate_regression(
        baseline,
        candidate,
    )

    assert result["status"] == "FAIL"
    assert result["latency"]["increase_ratio"] is None
    assert result["cost"]["increase_ratio"] is None


def test_calculate_increase_ratio():
    assert calculate_increase_ratio(100.0, 125.0) == 0.25
    assert calculate_increase_ratio(100.0, 90.0) == 0.0
    assert calculate_increase_ratio(0.0, 0.0) == 0.0
    assert calculate_increase_ratio(0.0, 1.0) is None


def test_negative_metric_is_rejected():
    with pytest.raises(ValueError):
        calculate_increase_ratio(
            baseline_value=-1.0,
            candidate_value=1.0,
        )


def test_missing_required_metric_is_rejected():
    baseline = build_experiment()
    candidate = {
        "average_overall_score": 0.90,
        "average_latency_ms": 800.0,
    }

    with pytest.raises(
        KeyError,
        match="estimated_total_cost_usd",
    ):
        evaluate_regression(
            baseline,
            candidate,
        )
