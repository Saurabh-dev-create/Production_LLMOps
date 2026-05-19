import os
import json
from dotenv import load_dotenv
from openai import OpenAI

from rag.retriever import retrieve_context
from prompts.loader import render_prompt

load_dotenv()


def analyze_incident(incident_data: dict) -> dict:
    """
    Analyze Kubernetes incident using retrieved runbook context
    and versioned prompt templates.
    """
    client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

    # Build a retrieval query from incident data
    query = (
        f"{incident_data.get('status', '')} "
        f"{incident_data.get('logs', '')[:200]}"
    )

    # Retrieve relevant runbook context
    retrieved_context = retrieve_context(query)

    # Render prompt from prompt registry
    prompt = render_prompt(
        "rca",
        version="v2",  # Change to "v1" to test the earlier prompt
        retrieved_context=retrieved_context,
        incident_data=json.dumps(incident_data, indent=2)
    )

    # Call OpenAI
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