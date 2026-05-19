import json
from pathlib import Path


def test_golden_dataset_exists_and_loads():
    dataset_path = Path("evaluator/datasets/golden_dataset.json")

    assert dataset_path.exists()

    data = json.loads(dataset_path.read_text(encoding="utf-8"))

    assert isinstance(data, list)
    assert len(data) >= 2
    assert "incident_data" in data[0]
    assert "expected" in data[0]