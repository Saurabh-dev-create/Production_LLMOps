# Changelog


### Project Foundation
- Initialized repository structure
- Added Python dependencies
- Configured GitHub Actions CI

### Incident Simulation
- Added CrashLoopBackOff incident scenario
- Deployed faulty workload for testing

### Collector Agent
- Implemented Collector Agent to gather pod status, events, and logs

### Testing Configuration
- Added pytest.ini to configure project root in PYTHONPATH

### RCA Agent
- Implemented RCA Agent using OpenAI API for Kubernetes root cause analysis

### Remediation Agent
- Enhanced remediation risk classification to detect both "rollback" and "roll back"

### Notifier Agent
- Implemented console-based incident notification formatter

### Langraph Part
- Connected all agents using LangGraph orchestration

### API_Gateway
- Added FastAPI API Gateway with /analyze endpoint

### Integration
- Added integration tests for the /analyze API endpoint

### Helm
- Added Helm chart for Kubernetes deployment

### RAG BASE
- Started creating the RAG knowledge base structure
- Implemented RAG document ingestion pipeline using ChromaDB and OpenAI embeddings
- Implemented RAG retriever using Chroma vector search
- Integrated RAG retrieval into the RCA Agent
- Added evaluation script to compare RCA quality with and without RAG


### Evaluation
- Added golden dataset for automated RCA evaluation
- Implemented automated scoring functions for root cause, severity, and remediation quality
- Added automated evaluation runner that executes benchmark cases and generates reports
- Added Markdown report generation for evaluation results
- Added regression threshold checks to enforce minimum evaluation scores
- Added GitHub Actions pipeline for automated evaluation and regression checks


### Prompts
- Started Phase 4 by creating a centralized prompt registry
- Added versioned RCA prompt templates (v1 and v2)
- Integrated dynamic prompt loading into the RCA Agent
- Added automated prompt A/B testing and version comparison

### Adding Guardrails
- Added Pydantic schema for structured RCA validation
- Integrated Pydantic validation into the RCA Agent
- Added automatic retry logic for invalid JSON and schema validation failures