import os
import json
from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()


def analyze_incident(incident_data: dict) -> dict:
    """
    Send incident data to an LLM and return structured RCA output.
    """
    client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

    prompt = f"""
You are a senior Kubernetes Site Reliability Engineer.

Analyze the following Kubernetes incident and respond ONLY with valid JSON.

Required JSON format:
{{
  "root_cause": "...",
  "severity": "low|medium|high|critical",
  "confidence": 0.0,
  "recommended_actions": [
    "...",
    "..."
  ]
}}

Incident Data:
{json.dumps(incident_data, indent=2)}
"""

    response = client.responses.create(
        model="gpt-4.1-mini",
        input=prompt
    )

    content = response.output_text.strip()

    # Remove Markdown fences if present
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