import json
import time
from datetime import datetime
from pathlib import Path
from pprint import pprint


MODEL_PRICING = {
    "gpt-4.1-mini": {
        "input_per_million": 0.40,
        "output_per_million": 1.60
    }
}

LOG_FILE = Path("observability/logs/metrics.json")


def calculate_cost(model: str, input_tokens: int, output_tokens: int) -> float:
    """
    Estimate API cost based on token usage.
    """
    pricing = MODEL_PRICING.get(model)

    if not pricing:
        return 0.0

    input_cost = (
        input_tokens / 1_000_000
    ) * pricing["input_per_million"]

    output_cost = (
        output_tokens / 1_000_000
    ) * pricing["output_per_million"]

    return round(input_cost + output_cost, 6)


def save_metrics(metrics: dict):
    """
    Persist metrics to JSON log file.
    """
    LOG_FILE.parent.mkdir(parents=True, exist_ok=True)

    existing_logs = []

    if LOG_FILE.exists():
        try:
            with open(LOG_FILE, "r") as f:
                existing_logs = json.load(f)
        except json.JSONDecodeError:
            existing_logs = []

    existing_logs.append(metrics)

    with open(LOG_FILE, "w") as f:
        json.dump(existing_logs, f, indent=2)


def track_execution(start_time, response, model="gpt-4.1-mini"):
    """
    Track latency, token usage, and estimated cost.
    """
    latency = round(time.time() - start_time, 2)

    usage = response.usage

    input_tokens = getattr(usage, "input_tokens", 0)
    output_tokens = getattr(usage, "output_tokens", 0)

    estimated_cost = calculate_cost(
        model,
        input_tokens,
        output_tokens
    )

    metrics = {
        "timestamp": datetime.utcnow().isoformat(),
        "model": model,
        "latency_seconds": latency,
        "input_tokens": input_tokens,
        "output_tokens": output_tokens,
        "estimated_cost_usd": estimated_cost
    }

    save_metrics(metrics)

    pprint(metrics)

    return metrics