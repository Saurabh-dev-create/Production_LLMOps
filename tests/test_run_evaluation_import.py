from evaluator.run_evaluation import run_evaluation


def test_run_evaluation_exists():
    assert callable(run_evaluation)