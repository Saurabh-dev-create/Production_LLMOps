from evaluator.scoring import (
    keyword_matches,
    keyword_overlap_score,
    severity_score,
)


def test_keyword_alias_refusal_matches_refused():
    text = (
        "The application is failing to connect to Postgres "
        "because the connection was refused."
    )

    assert keyword_matches(
        text,
        "refused",
    )


def test_keyword_alias_cleanup_matches_clean_up():
    text = (
        "Clean up unused files to free up disk space."
    )

    assert keyword_matches(
        text,
        "cleanup",
    )


def test_keyword_alias_registry_matches_repository():
    text = (
        "Verify that the image exists in the container registry."
    )

    assert keyword_matches(
        text,
        "repository",
    )


def test_keyword_alias_credentials_matches_authentication():
    text = (
        "Check registry credentials and image pull secrets."
    )

    assert keyword_matches(
        text,
        "authentication",
    )


def test_keyword_overlap_uses_aliases():
    text = (
        "The container registry rejected access because "
        "credentials are invalid."
    )

    score = keyword_overlap_score(
        text,
        [
            "repository",
            "authentication",
        ],
    )

    assert score == 1.0


def test_exact_severity_match_scores_one():
    assert severity_score(
        "high",
        "high",
    ) == 1.0


def test_adjacent_severity_gets_partial_credit():
    assert severity_score(
        "high",
        "critical",
    ) == 0.5

    assert severity_score(
        "medium",
        "high",
    ) == 0.5


def test_distant_severity_gets_zero():
    assert severity_score(
        "low",
        "critical",
    ) == 0.0


def test_unknown_severity_gets_zero():
    assert severity_score(
        "unknown",
        "high",
    ) == 0.0
