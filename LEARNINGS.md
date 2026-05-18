# Learnings

## Repository Initialization
- Created modular architecture for multi-agent LLMOps project
- Configured virtual environment and CI pipeline

### CrashLoopBackOff
Occurs when a container repeatedly exits and Kubernetes backs off before restarting it.

### Kubernetes Python Client
Used CoreV1Api to retrieve pod information, events, and logs programmatically.

### Structured LLM Output
Used JSON-only prompting and parsing to generate machine-readable root cause analysis.

- Unit tests exposed a phrase-matching issue where "roll back" was not recognized as a risky action. Added support for multiple wording variations.

Built a reusable report formatter for incident summaries and remediation plans

Used LangGraph StateGraph to coordinate multi-step AI workflows

Exposed the LangGraph workflow through a REST API using FastAPI and automatic Swagger documentation