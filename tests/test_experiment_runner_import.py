from evaluator.experiment_runner import (
    EXPERIMENTS,
    ExperimentConfig,
    run_experiments,
)


def test_experiment_runner_configuration_exists():
    assert len(EXPERIMENTS) == 4
    assert all(isinstance(item, ExperimentConfig) for item in EXPERIMENTS)
    assert callable(run_experiments)
