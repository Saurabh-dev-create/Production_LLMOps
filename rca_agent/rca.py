import json
import os
import time

from dotenv import load_dotenv
from openai import OpenAI

from guardrails.schemas import RCAResponse
from observability.metrics.tracker import track_execution
from observability.tracing import traced_analysis
from prompts.loader import render_prompt
from rag.retriever import (
    build_retrieval_query,
    retrieve_context,
)


load_dotenv()


def analyze_incident(
    incident_data: dict,
    prompt_version: str = "v2",
    use_rag: bool = True,
    model: str = "gpt-4.1-mini",
    max_retries: int = 3,
) -> dict:
    """
    Analyze Kubernetes incident using:
    - optional RAG context
    - versioned prompt templates
    - Pydantic schema validation
    - automatic retry logic
    - LLM usage, latency, and cost metadata
    """
    client = OpenAI(
        api_key=os.getenv("OPENAI_API_KEY")
    )

    # Build retrieval query from diagnostic incident evidence.
    query = build_retrieval_query(
        incident_data
    )

    retrieved_context = (
        retrieve_context(query)
        if use_rag
        else "No additional runbook context was provided."
    )

    prompt = render_prompt(
        "rca",
        version=prompt_version,
        retrieved_context=retrieved_context,
        incident_data=json.dumps(
            incident_data,
            indent=2,
        ),
    )

    for attempt in range(1, max_retries + 1):
        try:
            print(
                f"RCA attempt {attempt}/{max_retries}"
            )

            start_time = time.time()

            response = traced_analysis(
                client.responses.create,
                model=model,
                input=prompt,
            )

            metrics = track_execution(
                start_time,
                response,
                model=model,
            )

            content = response.output_text.strip()

            if content.startswith("```"):
                lines = content.splitlines()
                content = "\n".join(
                    line
                    for line in lines
                    if not line.startswith("```")
                ).strip()

            parsed = json.loads(content)

            validated = RCAResponse(**parsed)

            result = validated.model_dump()

            input_tokens = int(
                metrics.get(
                    "input_tokens",
                    0,
                )
            )

            output_tokens = int(
                metrics.get(
                    "output_tokens",
                    0,
                )
            )

            result["_metadata"] = {
                "model": model,
                "usage": {
                    "prompt_tokens": input_tokens,
                    "completion_tokens": output_tokens,
                    "total_tokens": (
                        input_tokens + output_tokens
                    ),
                },
                "estimated_cost_usd": float(
                    metrics.get(
                        "estimated_cost_usd",
                        0.0,
                    )
                ),
                "inference_latency_seconds": float(
                    metrics.get(
                        "latency_seconds",
                        0.0,
                    )
                ),
            }

            return result

        except Exception as exc:
            print(
                f"Attempt {attempt} failed: {exc}"
            )

            if attempt == max_retries:
                raise

            prompt += """

IMPORTANT:
Your previous response was invalid.

Return ONLY valid JSON matching this exact schema:
{
  "root_cause": "...",
  "severity": "low|medium|high|critical",
  "confidence": 0.0,
  "recommended_actions": [
    "...",
    "..."
  ]
}
"""


if __name__ == "__main__":
    from pprint import pprint

    from collector_agent.collector import (
        collect_incident_data,
    )

    incident = collect_incident_data()

    analysis = analyze_incident(
        incident
    )

    pprint(analysis)
