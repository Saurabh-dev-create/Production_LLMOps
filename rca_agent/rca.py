import os
import json
import time
from dotenv import load_dotenv
from openai import OpenAI

from guardrails.schemas import RCAResponse
from rag.retriever import retrieve_context
from prompts.loader import render_prompt
from observability.tracing import traced_analysis
from observability.metrics.tracker import track_execution
load_dotenv()


def analyze_incident(
    incident_data: dict,
    prompt_version: str = "v2",
    use_rag: bool = True,
    model: str = "gpt-4.1-mini",
    max_retries: int = 3
) -> dict:
    """
    Analyze Kubernetes incident using:
    - RAG (retrieved runbook context)
    - Versioned prompt templates
    - Pydantic schema validation
    - Automatic retry logic
    """
    client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

    # Build retrieval query from incident data
    query = (
        f"{incident_data.get('status', '')} "
        f"{incident_data.get('logs', '')[:200]}"
    )

    # Retrieve relevant runbook context
    retrieved_context = (
          retrieve_context(query)
          if use_rag
          else "No additional runbook context was provided."
          )

    # Render prompt from the prompt registry
    prompt = render_prompt(
        "rca",
        version=prompt_version,
        retrieved_context=retrieved_context,
        incident_data=json.dumps(incident_data, indent=2)
    )

    # Retry loop
    for attempt in range(1, max_retries + 1):
        try:
            print(f"RCA attempt {attempt}/{max_retries}")
            start_time = time.time()
            # Call OpenAI
            response = traced_analysis(
              client.responses.create,
              model=model,
              input=prompt
              ) 
            metrics = track_execution(
            start_time,
            response,
            model=model
            )

            content = response.output_text.strip()

            # Remove markdown code fences if present
            if content.startswith("```"):
                lines = content.splitlines()
                content = "\n".join(
                    line for line in lines
                    if not line.startswith("```")
                ).strip()

            # Parse JSON
            parsed = json.loads(content)

            # Validate against Pydantic schema
            validated = RCAResponse(**parsed)

            # Return validated dictionary
            return validated.model_dump()

        except Exception as e:
            print(f"Attempt {attempt} failed: {e}")

            # Re-raise the exception after final attempt
            if attempt == max_retries:
                raise

            # Append corrective instructions for the next retry
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
    from collector_agent.collector import collect_incident_data
    from pprint import pprint

    incident = collect_incident_data()
    analysis = analyze_incident(incident)

    pprint(analysis)
