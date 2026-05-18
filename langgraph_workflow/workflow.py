from typing import TypedDict

from langgraph.graph import StateGraph, END

from collector_agent.collector import collect_incident_data
from rca_agent.rca import analyze_incident
from remediation_agent.remediation import generate_remediation_plan
from notifier.notifier import send_notification


class WorkflowState(TypedDict, total=False):
    incident_data: dict
    rca_result: dict
    remediation_plan: dict
    report: str


def collect_node(state: WorkflowState) -> WorkflowState:
    incident_data = collect_incident_data()
    return {"incident_data": incident_data}


def rca_node(state: WorkflowState) -> WorkflowState:
    rca_result = analyze_incident(state["incident_data"])
    return {"rca_result": rca_result}


def remediation_node(state: WorkflowState) -> WorkflowState:
    remediation_plan = generate_remediation_plan(state["rca_result"])
    return {"remediation_plan": remediation_plan}


def notifier_node(state: WorkflowState) -> WorkflowState:
    report = send_notification(
        state["incident_data"],
        state["rca_result"],
        state["remediation_plan"]
    )
    return {"report": report}


def build_workflow():
    graph = StateGraph(WorkflowState)

    graph.add_node("collect", collect_node)
    graph.add_node("rca", rca_node)
    graph.add_node("remediation", remediation_node)
    graph.add_node("notify", notifier_node)

    graph.set_entry_point("collect")
    graph.add_edge("collect", "rca")
    graph.add_edge("rca", "remediation")
    graph.add_edge("remediation", "notify")
    graph.add_edge("notify", END)

    return graph.compile()


if __name__ == "__main__":
    app = build_workflow()
    result = app.invoke({})
    print("\nWorkflow completed successfully.")