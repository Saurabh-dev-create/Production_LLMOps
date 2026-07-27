import pytest

from evaluator.experiment_runner import run_experiments


def test_run_experiments_rejects_zero_cases():
    with pytest.raises(ValueError, match="max_cases must be at least 1"):
        run_experiments(max_cases=0)
