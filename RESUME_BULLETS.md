# Resume Bullets

- Initialized an enterprise-grade repository for an AI-powered Kubernetes Incident Copilot with modular agents, CI/CD, and Kubernetes deployment support.

- Simulated real Kubernetes failures, including CrashLoopBackOff, to generate operational data for an AI-driven incident response platform.

- Developed a Kubernetes Collector Agent using the Python Kubernetes client to extract pod status, events, and logs as structured input for AI-driven root cause analysis.

- Developed an AI-powered Root Cause Analysis agent that used OpenAI models to generate structured diagnoses, severity ratings, confidence scores, and remediation recommendations for Kubernetes incidents.

- Developed a notification service that transformed AI analysis and remediation plans into human-readable incident reports

- Orchestrated a multi-agent Kubernetes incident response workflow using LangGraph to automate data collection, AI-based root cause analysis, remediation planning, and reporting

- Developed a FastAPI-based API Gateway exposing a LangGraph-powered Kubernetes incident response workflow via REST endpoints and interactive Swagger documentation

- Built integration tests using pytest and mocking to validate API contracts and end-to-end workflow behaviour

- Packaged the application into a Helm chart to enable parameterized, repeatable Kubernetes deployments

- Built a RAG knowledge base using operational runbooks to provide grounded AI recommendations for Kubernetes incident analysis

- Implemented a retrieval-augmented generation pipeline that converted operational runbooks into vector embeddings stored in ChromaDB.

- Developed a semantic retriever that queried ChromaDB to fetch relevant troubleshooting runbooks for retrieval-augmented root cause analysis

- Integrated a RAG pipeline into the RCA Agent to ground Kubernetes root cause analysis in vectorized troubleshooting runbooks

- Developed an evaluation framework to compare baseline and RAG-enhanced root cause analysis and quantify improvements in groundedness and actionability

- Created a benchmark dataset of Kubernetes incidents and expected outcomes to support automated LLM evaluation and regression testing

- Implemented automated scoring functions to evaluate AI-generated root cause analyses using keyword overlap and severity accuracy metrics

- Developed an automated evaluation runner that benchmarked AI-generated root cause analyses and produced detailed quality reports

- Generated Markdown evaluation reports with per-case scoring and automated pass/fail summaries

- Implemented evaluation thresholds that automatically fail CI when model quality scores fall below target levels

- Integrated automated LLM evaluation, reporting, and quality gates into GitHub Actions CI/CD pipelines

- Built a centralized prompt registry with version-controlled templates for production LLM workflows