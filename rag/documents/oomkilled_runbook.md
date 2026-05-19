# OOMKilled Troubleshooting Runbook

## Symptoms
- Container terminated with reason OOMKilled
- Frequent restarts

## Common Causes
- Memory limit too low
- Memory leak
- Unexpected workload spike

## Troubleshooting Steps
1. Review memory usage metrics.
2. Inspect application behavior.
3. Increase memory limits if appropriate.

## Recommended Actions
- Raise memory requests and limits.
- Fix memory leaks.
- Optimize application memory usage.