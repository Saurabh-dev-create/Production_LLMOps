from evaluator.datasets.loader import load_dataset


def test_dataset_loader_loads_all_incidents():
    dataset = load_dataset()

    assert len(dataset) >= 15

    names = {case["name"] for case in dataset}

    assert "crashloopbackoff_case" in names
    assert "imagepullbackoff_case" in names
    assert "oomkilled_case" in names
    assert "node_not_ready_case" in names
    assert "database_connection_failure_case" in names
