from langgraph_workflow.workflow import build_workflow


def test_build_workflow():
    app = build_workflow()
    assert app is not None