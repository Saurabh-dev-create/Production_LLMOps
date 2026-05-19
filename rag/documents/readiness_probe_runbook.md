# Readiness Probe Failure Troubleshooting Runbook

## Symptoms
- Pod is running but not Ready
- Readiness probe failures

## Common Causes
- Incorrect probe path or port
- Slow application startup
- Dependency not available

## Troubleshooting Steps
1. Review probe configuration.
2. Check application logs.
3. Validate service dependencies.

## Recommended Actions
- Fix readiness probe configuration.
- Increase initialDelaySeconds.
- Resolve dependency issues.