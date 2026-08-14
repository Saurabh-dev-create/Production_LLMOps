# Disk Full Troubleshooting Runbook

## Symptoms

- No space left on device
- Filesystem usage near 100 percent
- Applications cannot write files
- Logging or database operations fail

## Common Causes

- Excessive log growth
- Missing log rotation
- Temporary files accumulating
- Container image accumulation
- Insufficient disk capacity

## Troubleshooting Steps

1. Check filesystem utilization.
2. Identify the largest directories and files.
3. Inspect application and system logs.
4. Check container image and temporary-file usage.
5. Verify log rotation and retention policies.

## Recommended Actions

- Remove unnecessary files.
- Rotate and expire old logs.
- Clean unused container images.
- Increase disk capacity when appropriate.
- Configure disk utilization alerts.
