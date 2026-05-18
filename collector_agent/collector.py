from kubernetes import client, config


def collect_incident_data(label_selector="app=crash-demo", namespace="default"):
    """
    Collect incident data from Kubernetes pods.
    """
    # Load kubeconfig (works with WSL, Minikube, Kind, Docker Desktop, EKS)
    config.load_kube_config()

    v1 = client.CoreV1Api()

    # Find matching pods
    pods = v1.list_namespaced_pod(
        namespace=namespace,
        label_selector=label_selector
    )

    if not pods.items:
        raise Exception(f"No pods found for label selector: {label_selector}")

    pod = pods.items[0]
    pod_name = pod.metadata.name

    # Basic pod status
    container_status = pod.status.container_statuses[0]
    waiting_state = container_status.state.waiting

    status_reason = (
        waiting_state.reason
        if waiting_state
        else pod.status.phase
    )

    restart_count = container_status.restart_count

    # Events
    field_selector = (
        f"involvedObject.name={pod_name},"
        f"involvedObject.namespace={namespace}"
    )

    events_response = v1.list_namespaced_event(
        namespace=namespace,
        field_selector=field_selector
    )

    events = [
        event.message
        for event in events_response.items
    ]

    # Logs
    try:
        logs = v1.read_namespaced_pod_log(
            name=pod_name,
            namespace=namespace,
            tail_lines=50
        )
    except Exception as e:
        logs = f"Unable to fetch logs: {e}"

    # Final structured data
    incident_data = {
        "pod_name": pod_name,
        "namespace": namespace,
        "status": status_reason,
        "restart_count": restart_count,
        "events": events,
        "logs": logs
    }

    return incident_data


if __name__ == "__main__":
    data = collect_incident_data()
    from pprint import pprint
    pprint(data)