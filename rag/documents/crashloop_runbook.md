# CrashLoopBackOff Troubleshooting Runbook

## Symptoms
- Pod status shows CrashLoopBackOff
- Container repeatedly restarts

## Common Causes
- Application exits with non-zero status
- Invalid startup command
- Missing environment variables
- Dependency failures

## Troubleshooting Steps
1. Review container logs using `kubectl logs`.
2. Inspect pod events using `kubectl describe pod`.
3. Verify the container command and arguments.
4. Check required environment variables.
5. Validate external dependencies.

## Recommended Actions
- Fix the startup command.
- Correct application configuration.
- Redeploy the workload.