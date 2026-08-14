# Ingress 502 Troubleshooting Runbook

## Symptoms

- HTTP 502 responses
- Ingress reports bad gateway
- Upstream service has no healthy endpoints
- External traffic cannot reach the application

## Common Causes

- No healthy backend endpoints
- Service selector mismatch
- Incorrect service port
- Application readiness failure
- Backend connection failure

## Troubleshooting Steps

1. Inspect ingress controller logs.
2. Verify service endpoints.
3. Check service selectors and ports.
4. Verify backend pod readiness.
5. Test backend connectivity directly.

## Recommended Actions

- Restore healthy backend endpoints.
- Correct service selectors or ports.
- Fix application readiness problems.
- Correct ingress backend configuration.
