import re
from typing import Iterable


SEVERITY_ORDER = {
    "low": 0,
    "medium": 1,
    "high": 2,
    "critical": 3,
}


KEYWORD_ALIASES = {
    "refused": {
        "refused",
        "refusal",
        "connection refused",
        "connection failure",
        "failed to connect",
        "failing to connect",
    },
    "cleanup": {
        "cleanup",
        "clean up",
        "remove unused",
        "delete unused",
        "free up disk space",
    },
    "authentication": {
        "authentication",
        "credentials",
        "access permissions",
        "image pull secret",
        "image pull secrets",
        "registry access",
    },
    "repository": {
        "repository",
        "registry",
        "container registry",
        "image registry",
    },
    "startup": {
        "startup",
        "initialization",
        "initialisation",
        "entrypoint",
        "container start",
    },
    "redeploy": {
        "redeploy",
        "restart deployment",
        "restart the deployment",
        "rollout restart",
    },
    "reschedule": {
        "reschedule",
        "rescheduling",
        "evict",
        "eviction",
        "drain the node",
        "draining the node",
    },
    "storageclass": {
        "storageclass",
        "storage class",
    },
    "coredns": {
        "coredns",
        "dns service",
        "dns resolver",
    },
}


def normalize_text(text: str) -> str:
    """
    Normalize text for deterministic comparison.
    """
    text = text.lower().strip()
    text = re.sub(r"[\-_]+", " ", text)
    text = re.sub(r"\s+", " ", text)

    return text


def _normalized_phrases(
    keyword: str,
) -> set[str]:
    """
    Return the expected keyword plus known acceptable aliases.
    """
    normalized_keyword = normalize_text(keyword)

    aliases = KEYWORD_ALIASES.get(
        normalized_keyword,
        set(),
    )

    phrases = {
        normalized_keyword,
        *(
            normalize_text(alias)
            for alias in aliases
        ),
    }

    return phrases


def keyword_matches(
    text: str,
    keyword: str,
) -> bool:
    """
    Return True when an expected keyword or one of its accepted
    deterministic aliases appears in the text.
    """
    normalized_text = normalize_text(text)

    return any(
        phrase in normalized_text
        for phrase in _normalized_phrases(keyword)
    )


def keyword_overlap_score(
    text: str,
    expected_keywords: list[str],
) -> float:
    """
    Return a score between 0.0 and 1.0 based on how many expected
    concepts appear in the generated text.

    Each expected keyword may match either its literal form or an
    explicitly configured deterministic alias.
    """
    if not expected_keywords:
        return 1.0

    matches = sum(
        1
        for keyword in expected_keywords
        if keyword_matches(text, keyword)
    )

    return matches / len(expected_keywords)


def severity_score(
    actual: str,
    expected: str,
) -> float:
    """
    Score severity using ordinal distance.

    Exact match:
        1.0

    One level away:
        0.5

    Two or more levels away:
        0.0
    """
    actual_normalized = normalize_text(actual)
    expected_normalized = normalize_text(expected)

    if actual_normalized == expected_normalized:
        return 1.0

    if (
        actual_normalized not in SEVERITY_ORDER
        or expected_normalized not in SEVERITY_ORDER
    ):
        return 0.0

    distance = abs(
        SEVERITY_ORDER[actual_normalized]
        - SEVERITY_ORDER[expected_normalized]
    )

    if distance == 1:
        return 0.5

    return 0.0


def recommended_actions_score(
    actions: list[str],
    expected_keywords: list[str],
) -> float:
    """
    Score recommended actions using deterministic concept overlap.
    """
    combined_text = " ".join(actions)

    return keyword_overlap_score(
        combined_text,
        expected_keywords,
    )


def overall_score(
    result: dict,
    expected: dict,
) -> dict:
    """
    Compute deterministic RCA evaluation metrics.
    """
    root_score = keyword_overlap_score(
        result.get(
            "root_cause",
            "",
        ),
        expected.get(
            "root_cause_keywords",
            [],
        ),
    )

    sev_score = severity_score(
        result.get(
            "severity",
            "",
        ),
        expected.get(
            "severity",
            "",
        ),
    )

    action_score = recommended_actions_score(
        result.get(
            "recommended_actions",
            [],
        ),
        expected.get(
            "recommended_action_keywords",
            [],
        ),
    )

    final_score = (
        root_score
        + sev_score
        + action_score
    ) / 3

    return {
        "root_cause_score": round(
            root_score,
            3,
        ),
        "severity_score": round(
            sev_score,
            3,
        ),
        "recommended_actions_score": round(
            action_score,
            3,
        ),
        "overall_score": round(
            final_score,
            3,
        ),
    }


if __name__ == "__main__":
    sample_result = {
        "root_cause": (
            "The application failed to connect to the database "
            "during initialization."
        ),
        "severity": "high",
        "recommended_actions": [
            "Inspect logs.",
            "Verify database credentials.",
            "Restart the deployment.",
        ],
    }

    expected = {
        "root_cause_keywords": [
            "application",
            "refused",
            "startup",
        ],
        "severity": "critical",
        "recommended_action_keywords": [
            "logs",
            "authentication",
            "redeploy",
        ],
    }

    from pprint import pprint

    pprint(
        overall_score(
            sample_result,
            expected,
        )
    )
