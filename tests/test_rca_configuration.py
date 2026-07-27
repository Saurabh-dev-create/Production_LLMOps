from inspect import signature

from rca_agent.rca import analyze_incident


def test_analyze_incident_supports_experiment_configuration():
    parameters = signature(analyze_incident).parameters

    assert parameters["prompt_version"].default == "v2"
    assert parameters["use_rag"].default is True
    assert parameters["model"].default == "gpt-4.1-mini"
    assert parameters["max_retries"].default == 3
