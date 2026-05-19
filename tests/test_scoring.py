from evaluator.scoring import (
    keyword_overlap_score,
    severity_score,
    overall_score,
)


def test_keyword_overlap_score():
    score = keyword_overlap_score(
        "Application failed during startup command",
        ["application", "startup", "command"]
    )
    assert score == 1.0


def test_severity_score():
    assert severity_score("high", "high") == 1.0
    assert severity_score("medium", "high") == 0.0


def test_overall_score():
    result = {
        "root_cause": "Application failed during startup command",
        "severity": "high",
        "recommended_actions": [
            "Inspect logs",
            "Redeploy application"
        ]
    }

    expected = {
        "root_cause_keywords": ["application", "startup", "command"],
        "severity": "high",
        "recommended_action_keywords": ["logs", "redeploy"]
    }

    scores = overall_score(result, expected)

    assert scores["overall_score"] > 0.9