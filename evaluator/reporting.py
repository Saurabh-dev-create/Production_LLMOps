from pathlib import Path


def format_experiment_name(config: dict) -> str:
    prompt_version = config["prompt_version"].upper()
    rag_status = "with RAG" if config["use_rag"] else "without RAG"

    return f"Prompt {prompt_version} {rag_status}"


def generate_markdown_report(summary: dict) -> str:
    experiments = summary["experiments"]

    if not experiments:
        raise ValueError("summary must contain at least one experiment")

    dataset_size = max(
        experiment["num_cases"]
        for experiment in experiments
    )

    lines = [
        "# Production LLMOps Evaluation Report",
        "",
        "## Summary",
        "",
        f"- **Dataset size:** {dataset_size} incident(s)",
        f"- **Experiments evaluated:** {len(experiments)}",
        f"- **Best experiment:** `{summary['best_experiment']}`",
        "",
        "## Experiment Leaderboard",
        "",
        "| Rank | Experiment | Prompt | RAG | Model | Score | Cases |",
        "|---:|---|---|---|---|---:|---:|",
    ]

    for rank, experiment in enumerate(experiments, start=1):
        config = experiment["config"]

        lines.append(
            "| "
            f"{rank} | "
            f"{format_experiment_name(config)} | "
            f"{config['prompt_version']} | "
            f"{'Enabled' if config['use_rag'] else 'Disabled'} | "
            f"{config['model']} | "
            f"{experiment['average_overall_score']:.3f} | "
            f"{experiment['num_cases']} |"
        )

    best_experiment = experiments[0]

    lines.extend(
        [
            "",
            "## Best Experiment",
            "",
            f"**{format_experiment_name(best_experiment['config'])}**",
            "",
            f"- Score: `{best_experiment['average_overall_score']:.3f}`",
            f"- Model: `{best_experiment['config']['model']}`",
            f"- Cases evaluated: `{best_experiment['num_cases']}`",
            "",
            "## Case Breakdown",
            "",
            "| Incident | Overall Score |",
            "|---|---:|",
        ]
    )

    for case in best_experiment["cases"]:
        lines.append(
            f"| {case['name']} | "
            f"{case['scores']['overall_score']:.3f} |"
        )

    lines.extend(
        [
            "",
            "---",
            "",
            "_Generated automatically by the Production LLMOps "
            "evaluation pipeline._",
            "",
        ]
    )

    return "\n".join(lines)


def write_markdown_report(
    summary: dict,
    output_path: Path,
) -> Path:
    output_path.parent.mkdir(parents=True, exist_ok=True)

    report = generate_markdown_report(summary)

    output_path.write_text(
        report,
        encoding="utf-8",
    )

    return output_path
