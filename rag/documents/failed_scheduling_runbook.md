# Failed Scheduling Troubleshooting Runbook

## Symptoms

- Pod remains Pending because the Kubernetes scheduler cannot place it
- Pod events contain FailedScheduling
- Scheduler reports that zero or few nodes are available
- Events may report insufficient CPU or insufficient memory
- Preemption may report that it is not helpful for scheduling

## Common Causes

- Insufficient CPU or memory available on worker nodes
- Pod resource requests exceed available cluster capacity
- Node taints are not matched by pod tolerations
- Node affinity or anti-affinity rules cannot be satisfied
- Node selectors do not match available nodes
- Scheduling constraints prevent placement

## Troubleshooting Steps

1. Inspect pod events for FailedScheduling messages.
2. Review messages such as "0/N nodes are available".
3. Check for insufficient CPU or insufficient memory.
4. Compare pod resource requests with available node capacity.
5. Review node taints and pod tolerations.
6. Validate node selectors and affinity rules.
7. Review scheduler preemption messages.

## Recommended Actions

- Reduce excessive CPU or memory requests when appropriate.
- Add cluster capacity when existing nodes are resource constrained.
- Correct taints and tolerations.
- Fix node selectors or affinity rules.
- Relax unnecessary scheduling constraints.
- Add or scale worker nodes when capacity is insufficient.
