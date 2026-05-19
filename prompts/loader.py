from pathlib import Path


def load_prompt(template_name: str, version: str = "v1") -> str:
    """
    Load a prompt template from prompts/<template_name>/<version>.txt

    Example:
        load_prompt("rca", "v2")
    """
    path = Path("prompts") / template_name / f"{version}.txt"

    if not path.exists():
        raise FileNotFoundError(f"Prompt template not found: {path}")

    return path.read_text(encoding="utf-8")


def render_prompt(template_name: str, version: str = "v1", **kwargs) -> str:
    """
    Load a prompt template and render placeholders.

    Example:
        render_prompt(
            "rca",
            version="v2",
            retrieved_context="...",
            incident_data="..."
        )
    """
    template = load_prompt(template_name, version)
    return template.format(**kwargs)


if __name__ == "__main__":
    rendered = render_prompt(
        "rca",
        version="v1",
        retrieved_context="Sample runbook context",
        incident_data='{"status": "CrashLoopBackOff"}'
    )

    print(rendered)