# Failed Scheduling Troubleshooting Runbook

## Symptoms
- Events include "FailedScheduling"

## Common Causes
- Resource constraints
- Taints and tolerations mismatch
- Affinity rules not satisfied

## Troubleshooting Steps
1. Review pod events.
2. Check node resources.
3. Validate tolerations and affinity.

## Recommended Actions
- Relax scheduling constraints.
- Add worker nodes.
- Adjust taints and tolerations.