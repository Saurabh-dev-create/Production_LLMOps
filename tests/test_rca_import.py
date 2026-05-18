from rca_agent.rca import analyze_incident


def test_rca_function_exists():
    assert callable(analyze_incident)