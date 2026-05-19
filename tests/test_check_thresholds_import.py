from evaluator.check_thresholds import check_thresholds


def test_check_thresholds_exists():
    assert callable(check_thresholds)