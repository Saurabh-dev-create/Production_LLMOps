import json
from pathlib import Path


DATASET_ROOT = Path(__file__).parent


def load_dataset() -> list[dict]:
    dataset = []

    for category in sorted(DATASET_ROOT.iterdir()):
        if not category.is_dir():
            continue

        for incident_file in sorted(category.glob("*.json")):
            dataset.append(
                json.loads(
                    incident_file.read_text(
                        encoding="utf-8"
                    )
                )
            )

    return dataset


if __name__ == "__main__":
    print(f"Loaded {len(load_dataset())} incidents.")
