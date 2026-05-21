import json
from pathlib import Path
from statistics import mean


LOG_FILE = Path("observability/logs/metrics.json")


def generate_report():
    """
    Generate summary report from metrics logs.
    """
    if not LOG_FILE.exists():
        print("No metrics logs found.")
        return

    with open(LOG_FILE, "r") as f:
        logs = json.load(f)

    if not logs:
        print("Metrics log is empty.")
        return

    avg_latency = mean(
        log["latency_seconds"] for log in logs
    )

    total_cost = sum(
        log["estimated_cost_usd"] for log in logs
    )

    total_input_tokens = sum(
        log["input_tokens"] for log in logs
    )

    total_output_tokens = sum(
        log["output_tokens"] for log in logs
    )

    print("=" * 60)
    print("OBSERVABILITY REPORT")
    print("=" * 60)

    print(f"Total Executions: {len(logs)}")
    print(f"Average Latency: {avg_latency:.2f}s")
    print(f"Total Input Tokens: {total_input_tokens}")
    print(f"Total Output Tokens: {total_output_tokens}")
    print(f"Estimated Total Cost: ${total_cost:.6f}")


if __name__ == "__main__":
    generate_report()