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