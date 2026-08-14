# Node NotReady Troubleshooting Runbook

## Symptoms

- Kubernetes node reports NotReady
- Kubelet stops reporting node status
- Pods may be evicted or rescheduled
- Workloads on the node become unavailable

## Common Causes

- Kubelet failure
- Node resource exhaustion
- Network connectivity failure
- Operating system failure
- Container runtime failure

## Troubleshooting Steps

1. Inspect node conditions.
2. Check kubelet status and logs.
3. Review node CPU, memory, and disk pressure.
4. Verify control-plane network connectivity.
5. Check the container runtime.

## Recommended Actions

- Restart or repair the kubelet.
- Resolve node resource pressure.
- Restore network connectivity.
- Cordon and drain unhealthy nodes.
- Replace the node when recovery is not practical.
