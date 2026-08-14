# DNS Failure Troubleshooting Runbook

## Symptoms

- Name resolution failures
- Temporary failure in name resolution
- Services cannot resolve Kubernetes DNS names
- Applications cannot reach dependencies by hostname

## Common Causes

- CoreDNS failure
- Incorrect DNS configuration
- Network connectivity problems
- Invalid service names
- DNS traffic blocked by network policy

## Troubleshooting Steps

1. Test DNS resolution from the affected pod.
2. Inspect CoreDNS pods and logs.
3. Verify service names and namespaces.
4. Check pod DNS configuration.
5. Review network policies affecting DNS traffic.

## Recommended Actions

- Restore CoreDNS health.
- Correct DNS configuration.
- Fix service names.
- Restore DNS network connectivity.
- Scale CoreDNS when capacity is insufficient.
