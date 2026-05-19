import os
import json
from dotenv import load_dotenv
from openai import OpenAI

from rag.retriever import retrieve_context

load_dotenv()


def analyze_incident(incident_data: dict) -> dict:
    """
    Analyze Kubernetes incident using retrieved runbook context.
    """
    client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

    # Build a retrieval query from incident data
    query = (
        f"{incident_data.get('status', '')} "
        f"{incident_data.get('logs', '')[:200]}"
    )

    # Retrieve relevant runbook context
    retrieved_context = retrieve_context(query)

    prompt = f"""
You are a senior Kubernetes Site Reliability Engineer.

Use the provided runbook context and incident data to perform root cause analysis.

RUNBOOK CONTEXT:
{retrieved_context}

INCIDENT DATA:
{json.dumps(incident_data, indent=2)}

Respond ONLY with valid JSON in this format:
{{
  "root_cause": "...",
  "severity": "low|medium|high|critical",
  "confidence": 0.0,
  "recommended_actions": [
    "...",
    "..."
  ]
}}
"""

    response = client.responses.create(
        model="gpt-4.1-mini",
        input=prompt
    )

    content = response.output_text.strip()

    # Remove markdown fences if present
    if content.startswith("```"):
        lines = content.splitlines()
        content = "\n".join(
            line for line in lines
            if not line.startswith("```")
        ).strip()

    return json.loads(content)


if __name__ == "__main__":
    from collector_agent.collector import collect_incident_data
    from pprint import pprint

    incident = collect_incident_data()
    analysis = analyze_incident(incident)

    pprint(analysis)