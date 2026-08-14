# API Rate Limit Troubleshooting Runbook

## Symptoms

- HTTP 429 responses
- Rate limit exceeded errors
- Upstream model or API provider rejects requests
- Application requests are throttled

## Common Causes

- Provider request quota exceeded
- Excessive request concurrency
- Traffic spikes
- Missing client-side throttling
- Retry loops generating excessive requests

## Troubleshooting Steps

1. Inspect HTTP response codes for 429 errors.
2. Review request volume and concurrency.
3. Check provider rate-limit and quota usage.
4. Inspect retry behavior.
5. Review provider rate-limit headers when available.

## Recommended Actions

- Implement exponential backoff.
- Add request throttling and rate limiting.
- Reduce unnecessary retries.
- Queue requests during traffic spikes.
- Request higher provider quota when appropriate.
