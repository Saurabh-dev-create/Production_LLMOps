# Database Connection Failure Troubleshooting Runbook

## Symptoms

- Connection refused errors
- Database connection timeouts
- Application startup failures
- CrashLoopBackOff caused by database dependency failure

## Common Causes

- Database service unavailable
- Incorrect host or port
- Invalid credentials
- DNS resolution failure
- Network policy blocking connectivity
- Database connection pool exhaustion

## Troubleshooting Steps

1. Verify the database service is running.
2. Test connectivity to the database host and port.
3. Verify service DNS resolution.
4. Check database credentials and secrets.
5. Review network policies and security rules.
6. Inspect database logs and connection limits.

## Recommended Actions

- Restore database availability.
- Correct database connection configuration.
- Fix credentials or secrets.
- Correct network connectivity.
- Tune connection pool limits when necessary.
