# Service Timeout Troubleshooting Runbook

## Symptoms

- Requests to another service time out
- Increased application latency
- Upstream dependency requests fail
- Inter-service communication becomes unreliable

## Common Causes

- Unhealthy upstream service
- Network connectivity problems
- Excessive application latency
- Resource saturation
- Incorrect timeout configuration

## Troubleshooting Steps

1. Test connectivity to the upstream service.
2. Check upstream service health and endpoints.
3. Review request latency metrics.
4. Inspect network policies.
5. Review application and upstream logs.

## Recommended Actions

- Restore upstream service health.
- Fix network connectivity.
- Scale overloaded services.
- Optimize slow operations.
- Tune timeout and retry settings appropriately.
