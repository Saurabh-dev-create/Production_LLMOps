# ImagePullBackOff Troubleshooting Runbook

## Symptoms
- Pod status shows ImagePullBackOff
- Container image cannot be pulled

## Common Causes
- Incorrect image name or tag
- Private registry authentication failure
- Registry outage
- Network connectivity issues

## Troubleshooting Steps
1. Verify the image name and tag.
2. Check imagePullSecrets configuration.
3. Test registry accessibility.
4. Review pod events.

## Recommended Actions
- Correct the image reference.
- Update registry credentials.
- Retry deployment.