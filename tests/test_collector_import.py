from collector_agent.collector import collect_incident_data


def test_collector_function_exists():
    assert callable(collect_incident_data)