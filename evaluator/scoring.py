def normalize_text(text: str) -> str:
    return text.lower().strip()


def keyword_overlap_score(text: str, expected_keywords: list[str]) -> float:
    """
    Returns score between 0.0 and 1.0 based on how many expected
    keywords appear in the generated text.
    """
    if not expected_keywords:
        return 1.0

    text = normalize_text(text)

    matches = sum(
        1 for keyword in expected_keywords
        if keyword.lower() in text
    )

    return matches / len(expected_keywords)


def severity_score(actual: str, expected: str) -> float:
    """
    Exact match score for severity.
    """
    if normalize_text(actual) == normalize_text(expected):
        return 1.0
    return 0.0


def recommended_actions_score(actions: list[str], expected_keywords: list[str]) -> float:
    """
    Score based on keyword overlap across all recommended actions.
    """
    combined_text = " ".join(actions)
    return keyword_overlap_score(combined_text, expected_keywords)


def overall_score(result: dict, expected: dict) -> dict:
    """
    Compute all evaluation metrics.
    """
    root_score = keyword_overlap_score(
        result.get("root_cause", ""),
        expected.get("root_cause_keywords", [])
    )

    sev_score = severity_score(
        result.get("severity", ""),
        expected.get("severity", "")
    )

    action_score = recommended_actions_score(
        result.get("recommended_actions", []),
        expected.get("recommended_action_keywords", [])
    )

    final_score = (root_score + sev_score + action_score) / 3

    return {
        "root_cause_score": round(root_score, 3),
        "severity_score": round(sev_score, 3),
        "recommended_actions_score": round(action_score, 3),
        "overall_score": round(final_score, 3)
    }


if __name__ == "__main__":
    sample_result = {
        "root_cause": "The application exits during startup due to an invalid command.",
        "severity": "high",
        "recommended_actions": [
            "Inspect logs.",
            "Fix the startup command.",
            "Redeploy the application."
        ]
    }

    expected = {
        "root_cause_keywords": ["application", "startup", "command"],
        "severity": "high",
        "recommended_action_keywords": ["logs", "startup", "redeploy"]
    }

    from pprint import pprint
    pprint(overall_score(sample_result, expected))