# Pending Pod Troubleshooting Runbook

## Symptoms
- Pod remains in Pending state

## Common Causes
- Insufficient CPU or memory
- Unbound PersistentVolumeClaim
- Node selector mismatch
- Taints and tolerations mismatch

## Troubleshooting Steps
1. Review scheduling events.
2. Check cluster capacity.
3. Validate PVC status.
4. Verify affinity and tolerations.

## Recommended Actions
- Add cluster capacity.
- Fix PVC configuration.
- Adjust scheduling constraints.