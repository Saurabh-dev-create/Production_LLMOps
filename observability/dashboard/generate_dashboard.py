import json
from pathlib import Path

import pandas as pd
import matplotlib.pyplot as plt


LOG_FILE = Path("observability/logs/metrics.json")
OUTPUT_DIR = Path("observability/dashboard/output")

OUTPUT_DIR.mkdir(parents=True, exist_ok=True)


def load_metrics():
    """
    Load metrics from JSON log.
    """
    if not LOG_FILE.exists():
        raise FileNotFoundError("metrics.json not found")

    with open(LOG_FILE, "r") as f:
        return json.load(f)


def generate_latency_chart(df):
    """
    Generate latency trend chart.
    """
    plt.figure(figsize=(8, 4))

    plt.plot(df.index, df["latency_seconds"], marker="o")

    plt.xlabel("Execution")
    plt.ylabel("Latency (seconds)")
    plt.title("LLM Response Latency")

    plt.tight_layout()

    plt.savefig(
        OUTPUT_DIR / "latency_chart.png"
    )

    plt.close()


def generate_token_chart(df):
    """
    Generate token usage chart.
    """
    plt.figure(figsize=(8, 4))

    plt.plot(df.index, df["input_tokens"], marker="o")
    plt.plot(df.index, df["output_tokens"], marker="o")

    plt.xlabel("Execution")
    plt.ylabel("Tokens")
    plt.title("Token Usage Per Execution")

    plt.legend([
        "Input Tokens",
        "Output Tokens"
    ])

    plt.tight_layout()

    plt.savefig(
        OUTPUT_DIR / "token_chart.png"
    )

    plt.close()


def generate_cost_chart(df):
    """
    Generate API cost chart.
    """
    plt.figure(figsize=(8, 4))

    plt.plot(
        df.index,
        df["estimated_cost_usd"],
        marker="o"
    )

    plt.xlabel("Execution")
    plt.ylabel("Cost (USD)")
    plt.title("Estimated API Cost")

    plt.tight_layout()

    plt.savefig(
        OUTPUT_DIR / "cost_chart.png"
    )

    plt.close()


def generate_dashboard():
    """
    Generate all observability charts.
    """
    metrics = load_metrics()

    df = pd.DataFrame(metrics)

    generate_latency_chart(df)
    generate_token_chart(df)
    generate_cost_chart(df)

    print("=" * 60)
    print("Dashboard generated successfully.")
    print("=" * 60)

    print(f"Charts saved to: {OUTPUT_DIR}")


if __name__ == "__main__":
    generate_dashboard()