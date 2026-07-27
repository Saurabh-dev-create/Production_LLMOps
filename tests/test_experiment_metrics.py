from evaluator.experiment_runner import extract_usage_metrics


def test_extract_usage_metrics():
    result = {
        "_metadata": {
            "usage": {
                "prompt_tokens": 100,
                "completion_tokens": 50,
                "total_tokens": 150,
            },
            "estimated_cost_usd": 0.00025,
        }
    }

    metrics = extract_usage_metrics(result)

    assert metrics == {
        "prompt_tokens": 100,
        "completion_tokens": 50,
        "total_tokens": 150,
        "estimated_cost_usd": 0.00025,
    }


def test_extract_usage_metrics_defaults_to_zero():
    metrics = extract_usage_metrics(
        {
            "root_cause": "Example root cause",
            "severity": "low",
            "recommended_actions": [],
        }
    )

    assert metrics == {
        "prompt_tokens": 0,
        "completion_tokens": 0,
        "total_tokens": 0,
        "estimated_cost_usd": 0.0,
    }


def test_total_tokens_can_be_calculated_from_components():
    result = {
        "_metadata": {
            "usage": {
                "prompt_tokens": 75,
                "completion_tokens": 25,
            }
        }
    }

    metrics = extract_usage_metrics(result)

    assert metrics["total_tokens"] == 100
