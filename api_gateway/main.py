from fastapi import FastAPI
from langgraph_workflow.workflow import build_workflow

app = FastAPI(
    title="Kubernetes Incident AI Copilot",
    description="AI-powered Kubernetes incident detection and root cause analysis",
    version="1.0.0"
)

workflow = build_workflow()


@app.get("/")
def root():
    return {
        "message": "Kubernetes Incident AI Copilot is running"
    }


@app.post("/analyze")
def analyze_incident():
    """
    Execute the full workflow and return structured results.
    """
    result = workflow.invoke({})

    return {
        "incident_data": result.get("incident_data"),
        "rca_result": result.get("rca_result"),
        "remediation_plan": result.get("remediation_plan"),
        "report": result.get("report"),
    }