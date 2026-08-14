# Memory Pressure Troubleshooting Runbook

## Symptoms

- Increasing application memory consumption
- Node or container memory pressure
- Application performance degradation
- Risk of OOMKilled termination

## Common Causes

- Application memory leak
- Unexpected workload growth
- Insufficient memory allocation
- Unbounded caches
- Excessive in-memory data

## Troubleshooting Steps

1. Review memory utilization over time.
2. Identify memory-intensive containers.
3. Inspect application memory behavior.
4. Check memory requests and limits.
5. Review cache and workload growth.

## Recommended Actions

- Fix application memory leaks.
- Configure bounded caches.
- Increase memory allocation when justified.
- Scale workloads appropriately.
- Configure memory utilization alerts.
