# High CPU Troubleshooting Runbook

## Symptoms

- High CPU utilization
- Increased request latency
- Application response degradation
- CPU throttling

## Common Causes

- Traffic spikes
- Expensive application operations
- Infinite loops
- Insufficient CPU resources
- Excessive concurrency

## Troubleshooting Steps

1. Review CPU utilization metrics.
2. Identify CPU-intensive pods or processes.
3. Compare CPU usage with request traffic.
4. Check CPU requests and limits.
5. Inspect application traces and profiles.

## Recommended Actions

- Optimize CPU-intensive operations.
- Increase CPU requests or limits when justified.
- Scale replicas horizontally.
- Apply autoscaling.
- Investigate abnormal application loops.
