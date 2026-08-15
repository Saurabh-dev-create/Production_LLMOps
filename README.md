# Production LLMOps-Powered Kubernetes Incident Copilot

A Kubernetes incident analysis system built to explore how LLMs can be used safely and measurably in an operational workflow.

The project collects diagnostic information from Kubernetes workloads, retrieves relevant troubleshooting runbooks, uses an LLM to perform root cause analysis, validates the generated response, and produces a safety-checked remediation plan.

The other half of the project is the LLMOps layer around that workflow: prompt versioning, RAG evaluation, regression testing, tracing, token and cost tracking, and CI quality gates.

---

## Why I Built This

Generating an LLM response is easy.

Trusting that response during a Kubernetes incident is a different problem.

For an operational system I wanted to answer questions such as:

- Is the diagnosis grounded in actual incident evidence?
- Did retrieval select the correct runbook?
- Did a prompt change improve the system or make it worse?
- Is the model returning the structure downstream components expect?
- How much does each analysis cost?
- How long does inference take?
- Can a risky remediation be prevented from executing automatically?
- Can these checks run as part of CI instead of relying on manual testing?

This repository is my attempt to build those concerns into the system rather than treating the LLM call as the finished product.

---

## What the System Does

At a high level:

```text
Kubernetes workload
        |
        v
Collector Agent
        |
        | pod state
        | events
        | logs
        v
RAG Retrieval
        |
        | relevant operational runbooks
        v
RCA Agent
        |
        | OpenAI model
        | versioned prompt
        | retrieved context
        v
Structured Validation
        |
        | Pydantic schema
        | retry on invalid output
        v
Remediation Planner
        |
        | risk classification
        | approval controls
        v
Notifier / Incident Report
```

LangGraph coordinates the main workflow:

```text
collect -> rca -> remediation -> notify
```

The resulting workflow is also exposed through a FastAPI API.

---

## Architecture

```text
                         +----------------------+
                         |  Kubernetes Cluster  |
                         +----------+-----------+
                                    |
                                    v
                         +----------------------+
                         |   Collector Agent    |
                         |----------------------|
                         | Pod status           |
                         | Restart count        |
                         | Kubernetes events    |
                         | Container logs       |
                         +----------+-----------+
                                    |
                                    v
                    +-------------------------------+
                    |        RAG Retrieval          |
                    |-------------------------------|
                    | Operational runbooks          |
                    | OpenAI embeddings             |
                    | Chroma vector store           |
                    +---------------+---------------+
                                    |
                                    v
                         +----------------------+
                         |      RCA Agent       |
                         |----------------------|
                         | Prompt registry      |
                         | Prompt version       |
                         | Retrieved context    |
                         | OpenAI inference     |
                         +----------+-----------+
                                    |
                                    v
                         +----------------------+
                         |     Guardrails       |
                         |----------------------|
                         | Schema validation    |
                         | Retry handling       |
                         | Safety checks        |
                         +----------+-----------+
                                    |
                                    v
                         +----------------------+
                         | Remediation Planner  |
                         +----------+-----------+
                                    |
                                    v
                         +----------------------+
                         | Incident Reporting   |
                         +----------------------+

        ---------------------------------------------------------
        Cross-cutting LLMOps layer
        ---------------------------------------------------------
        LangSmith tracing
        Prompt experiments
        RAG evaluation
        Regression testing
        Token / latency / cost metrics
        GitHub Actions quality gates
        ---------------------------------------------------------
```

---

## Collector Agent

The collector uses the Kubernetes Python client to inspect a workload and turn Kubernetes diagnostic information into structured input for the analysis pipeline.

It currently collects:

- pod name
- namespace
- container state
- restart count
- Kubernetes events
- recent container logs

The idea is to give the RCA system evidence from the cluster instead of asking the model to diagnose an incident from a generic error string.

The default collector can work with a kubeconfig-backed cluster such as a local Kubernetes environment or EKS.

---

## Retrieval-Augmented RCA

The RCA agent uses retrieval-augmented generation so that troubleshooting knowledge does not have to come entirely from the model.

Operational runbooks live under:

```text
rag/documents/
```

The knowledge base currently includes runbooks for incidents such as:

```text
CrashLoopBackOff
OOMKilled
NodeNotReady
FailedScheduling
Pending Pods
Memory Pressure
High CPU
Disk Full
DNS failures
Readiness probe failures
ImagePullBackOff
Ingress 502
Service timeouts
Database connection failures
API rate limits
```

During ingestion the documents are chunked, embedded, and stored in a persistent Chroma vector store.

At incident time the retriever builds a query using useful diagnostic evidence, particularly:

```text
pod/container status
Kubernetes events
container logs
```

The most relevant runbook chunks are then included in the RCA prompt.

This keeps the diagnosis closer to the operational knowledge supplied to the system.

---

## RCA Agent

The RCA agent combines:

```text
incident evidence
        +
retrieved runbook context
        +
versioned RCA prompt
        |
        v
      LLM
```

The model currently returns a structured diagnosis containing fields such as:

```json
{
  "root_cause": "...",
  "severity": "high",
  "confidence": 0.85,
  "recommended_actions": [
    "...",
    "..."
  ]
}
```

The output is not immediately trusted.

It is parsed and validated against a Pydantic schema before it is passed to downstream components.

If the model returns malformed JSON or an invalid schema, the RCA agent retries the request with explicit formatting instructions.

---

## Prompt Versioning

Prompts are kept outside the application logic:

```text
prompts/
└── rca/
    ├── v1.txt
    └── v2.txt
```

The RCA agent accepts the prompt version as configuration:

```python
analyze_incident(
    incident_data,
    prompt_version="v2",
)
```

This makes prompt changes testable rather than silently replacing instructions inside application code.

The evaluation framework can compare prompt versions against the same benchmark cases before a new version is accepted.

---

## RAG Evaluation

One of the main goals of this project was to test retrieval separately from generation.

The repository contains a retrieval evaluation pipeline that checks whether the correct operational runbook appears in the retrieved results for known incidents.

This matters because a good model cannot reliably produce a grounded diagnosis if retrieval gives it the wrong context.

The evaluation layer records retrieval results and uses them as a CI quality gate.

### Current retrieval benchmark

```text
Golden cases:        15
Top-1 accuracy:      93.3%
Top-2 accuracy:     100.0%
Mean reciprocal rank: 0.9667
```

In practical terms, the expected runbook was present within the first two retrieved documents for every benchmark case in the current dataset.

---

## LLM Evaluation

The project also contains a golden dataset for evaluating RCA behavior.

Evaluation is used to compare:

- prompt versions
- RAG vs non-RAG analysis
- root-cause quality
- severity classification
- remediation recommendations
- latency
- estimated inference cost

Experiment results are written to:

```text
evaluator/results/
```

Examples include:

```text
experiment_results.json
prompt_comparison.json
retrieval_evaluation.json
evaluation_report.json
evaluation_report.md
```

The purpose is not to claim that a single score proves model quality. The evaluation suite is primarily a regression mechanism: when prompts, retrieval, or model configuration change, I want a repeatable way to detect whether known cases became worse.


## LLM Evaluation & Experimentation

The platform includes an automated evaluation pipeline for comparing prompt and RAG configurations across a reusable Kubernetes incident dataset.

The benchmark below evaluates **15 incident scenarios across four experiment configurations**, comparing:

- Prompt V1 vs Prompt V2
- RAG enabled vs disabled
- RCA quality score
- Inference latency
- Token consumption
- Estimated LLM cost

The evaluation pipeline automatically ranks experiments and identifies the best-performing configuration instead of relying on manual prompt selection.

![LLMOps Evaluation Benchmark](docs/images/llmops-evaluation-benchmark.png)

In this evaluation run, **Prompt V1 with RAG** ranked first with an aggregate score of **0.770** across 15 incident scenarios. The report also preserves per-incident results for cases including OOMKilled, CrashLoopBackOff, DNS failures, readiness failures, high CPU, database connectivity failures, and API rate limiting.

---

### Experiment Comparison

The evaluation framework compares prompt versions and RAG configurations using the same incident cases, making changes measurable across quality, latency, token usage, and estimated inference cost.

![LLM Evaluation Experiment Leaderboard](docs/images/llm-evaluation-leaderboard.png)

The leaderboard provides a repeatable way to compare candidate configurations and identify regress

### Benchmark Comparison

The benchmark compares candidate LLM configurations across response quality, latency, token usage, and estimated inference cost, making the quality/cost trade-off visible before configuration promotion.

![LLM Benchmark Summary](docs/images/llm-benchmark-summary.png)

## CI Quality Gates

GitHub Actions runs conventional tests as well as LLM-specific quality checks.

The LLMOps evaluation workflow contains two independent gates:

```text
Prompt Quality Gate
RAG Retrieval Gate
```
### Automated Prompt Regression Gate

LLM quality is enforced through CI/CD using an automated prompt regression gate. Every relevant change can be evaluated before promotion, helping prevent prompt or workflow changes from silently degrading incident-analysis quality.

![Prompt Regression Gate](docs/images/prompt-regression-gate-runs.png)

### Prompt Quality Gate

The prompt gate runs regression tests and compares an approved baseline against a candidate configuration.

A degraded candidate can therefore fail CI instead of being promoted simply because its output looks reasonable in a manual test.

### CI/CD Quality Gates for LLM and RAG Changes

The delivery pipeline validates both **prompt quality** and **RAG retrieval quality** before accepting changes. GitHub Actions runs independent quality gates so regressions in model behavior or retrieval performance can fail CI before reaching production.

![LLMOps Quality Gates](docs/images/llmops-quality-gates.png)

The CI pipeline runs regression tests, generates deterministic experiment results, executes the prompt quality gate, and publishes evaluation artifacts. A regression can therefore fail the pipeline instead of being discovered after deployment.

![Prompt Quality Gate CI Pipeline](docs/images/prompt-quality-gate-ci.png)

### RAG Impact Analysis

RAG effectiveness is evaluated per incident rather than assumed to improve every RCA. The evaluation pipeline compares identical incident scenarios with and without retrieval and classifies the impact as **HELPED**, **HURT**, or **NEUTRAL**.

![RAG Impact Analysis](docs/images/rag-impact-analysis.png)

This analysis exposed cases where retrieved context degraded RCA quality, providing evidence for retrieval tuning, runbook expansion, and selective RAG usage instead of enabling retrieval blindly for every incident.

### RAG Retrieval Gate

The retrieval job:

```text
installs dependencies
        |
        v
verifies API configuration
        |
        v
rebuilds the vector store
        |
        v
runs retrieval evaluation
        |
        v
applies retrieval thresholds
        |
        v
uploads evaluation artifacts
```

This was an important design choice for the project: RAG changes are treated as testable software changes.

---

### RAG-Grounded Root Cause Analysis

The RCA agent retrieves Kubernetes troubleshooting runbooks and injects the relevant operational context into the LLM analysis.

![RAG CrashLoopBackOff Runbook Trace](docs/images/rag-crashloop-runbook-trace.png)

This trace demonstrates a CrashLoopBackOff investigation grounded with troubleshooting symptoms and operational runbook context rather than relying solely on the model's internal knowledge.

## Safety and Remediation Guardrails

The remediation component converts RCA recommendations into a structured remediation plan.

Before the plan is returned, centralized safety checks classify actions according to risk.

Potentially high-impact actions can require human approval rather than being treated the same as low-risk diagnostic recommendations.

This separation is intentional:

```text
LLM recommendation
        |
        v
structured remediation plan
        |
        v
safety policy
        |
        +---- low risk ----> allowed
        |
        +---- high risk ---> approval required
```

The current implementation focuses on **planning and approval controls**, rather than blindly allowing the LLM to modify a cluster.

---

## LangGraph Orchestration

The incident response pipeline is implemented as a LangGraph state machine.

The shared workflow state contains:

```text
incident_data
rca_result
remediation_plan
report
```

Nodes execute sequentially:

```text
collect
   |
   v
rca
   |
   v
remediation
   |
   v
notify
   |
   v
END
```

Keeping the stages separate makes each component easier to test and allows the workflow to evolve without putting the entire incident-response process inside one function.

---

## LangSmith Tracing

LLM calls are instrumented with LangSmith.

The RCA inference path is traced under:

```text
k8s_incident_analysis
```

This makes it possible to inspect individual executions and see what context was supplied to the model, what it returned, and how long the operation took.

This became particularly useful while testing different runbooks and prompt versions because the behavior could be inspected at the individual trace level instead of relying only on terminal output.

### LLM Observability & Tracing

LLM-powered incident analysis is instrumented with LangSmith tracing, providing visibility into the prompts, retrieved runbook context, model execution, and RCA workflow.

![LangSmith Kubernetes Incident Trace](docs/images/langsmith-incident-trace.png)

The trace below shows an OOMKilled incident analysis where Kubernetes runbook context is supplied to the RCA workflow, making the AI investigation observable and auditable rather than operating as a black box.

### AI-Powered Root Cause Analysis

The RCA agent analyzes Kubernetes incident context and produces structured operational guidance including the detected root cause, severity, confidence score, and recommended remediation actions.

![OOMKilled AI Root Cause Analysis](docs/images/oomkilled-ai-rca.png)

In this OOMKilled scenario, the system identified an insufficient container memory limit as the likely root cause and recommended memory resource adjustments and application-level memory investigation. The inference path also records model usage, token consumption, latency, and estimated cost for LLMOps observability.

## Token, Cost and Latency Observability

Each RCA execution records operational metadata including:

```text
model
input tokens
output tokens
total tokens
inference latency
estimated API cost
timestamp
```

Metrics are persisted under:

```text
observability/logs/
```

The project also generates simple operational charts for:

```text
token usage
latency
estimated cost
```

This makes LLM behavior observable as an operational dependency rather than treating model calls as a black box.

### Production LLM Observability

Every AI-driven incident analysis is traced through LangSmith, providing execution-level visibility into model calls and inference latency.

![Production LLM Traces](docs/images/langsmith-production-traces.png)

Multiple Kubernetes incident-analysis runs are captured successfully with per-request latency, enabling production debugging and performance analysis of the LLM pipeline.

## API Gateway

The workflow is exposed through FastAPI.

Current endpoints:

```text
GET  /
POST /analyze
```

`POST /analyze` is wired to invoke the LangGraph workflow and expose the accumulated incident response state:

```json
{
  "incident_data": {},
  "rca_result": {},
  "remediation_plan": {},
  "report": "..."
}
```

FastAPI also provides interactive OpenAPI/Swagger documentation at:

```text
/docs
```

### Incident Analysis API

The platform exposes the AI incident-analysis workflow through a FastAPI REST API, providing a simple integration point for Kubernetes monitoring, alerting, and automation systems.

![Kubernetes Incident Analysis API](docs/images/incident-analysis-api.png)

The `POST /analyze` endpoint triggers the end-to-end incident analysis workflow and returns structured RCA results, allowing the LLMOps pipeline to be consumed programmatically rather than only through local scripts.

## Testing

The project uses pytest for unit, integration, regression, retrieval, safety, and configuration tests.

Current local test suite:

```text
70 passed
```

Tests cover areas including:

```text
API behavior
Collector imports
RCA configuration
RAG ingestion
RAG retrieval
retrieval metadata
retrieval queries
golden datasets
evaluation scoring
experiment execution
prompt comparison
regression thresholds
remediation behavior
safety policies
Pydantic schemas
workflow imports
notification formatting
```

The external APIs and Kubernetes interactions are mocked where appropriate so that most of the test suite remains deterministic.

---

## Repository Structure

```text
Production_LLMOps/
│
├── api_gateway/
│   └── main.py
│
├── collector_agent/
│   └── collector.py
│
├── rca_agent/
│   └── rca.py
│
├── remediation_agent/
│   └── remediation.py
│
├── notifier/
│   └── notifier.py
│
├── langgraph_workflow/
│   └── workflow.py
│
├── rag/
│   ├── documents/
│   ├── vector_store/
│   ├── ingest.py
│   └── retriever.py
│
├── prompts/
│   ├── loader.py
│   └── rca/
│       ├── v1.txt
│       └── v2.txt
│
├── evaluator/
│   ├── datasets/
│   ├── results/
│   ├── experiment_runner.py
│   ├── evaluate_retrieval.py
│   ├── compare_prompts.py
│   ├── compare_rag.py
│   ├── scoring.py
│   └── check_thresholds.py
│
├── guardrails/
│   ├── schemas.py
│   └── safety.py
│
├── observability/
│   ├── tracing.py
│   ├── metrics/
│   ├── logs/
│   └── dashboard/
│
├── incident_scenarios/
│   └── crashloop.yaml
│
├── helm/
│   ├── Chart.yaml
│   ├── values.yaml
│   └── templates/
│
├── tests/
│
├── .github/workflows/
│   ├── ci.yml
│   └── evaluation.yml
│
├── requirements.txt
└── README.md
```

---

## Running Locally

### Clone the repository

```bash
git clone <repository-url>
cd Production_LLMOps
```

### Create a virtual environment

```bash
python3 -m venv .venv
source .venv/bin/activate
```

### Install dependencies

```bash
python -m pip install --upgrade pip
pip install -r requirements.txt
```

### Environment configuration

Create a local `.env` file with the credentials required by the integrations you intend to use.

For example:

```text
OPENAI_API_KEY=...
```

LangSmith tracing can also be configured through the corresponding LangSmith environment variables.

Do not commit `.env` or API keys to the repository.

---

## Build the RAG Vector Store

Run:

```bash
python -m rag.ingest
```

This processes the operational runbooks and builds the local Chroma vector store.

The generated vector store is stored under:

```text
rag/vector_store/
```

## Testing & Validation

The project includes automated tests covering the LLMOps workflow, regression controls, API behavior, RAG components, and supporting platform logic.

The current test suite completes successfully with **42 tests passing**, while regression-threshold checks are validated before changes progress through the delivery workflow.

![Automated Test Suite](docs/images/automated-test-suite.png)

## Run the Tests

```bash
python -m pytest -q
```

Current result:

```text
70 passed
```

---

## Run the API

```bash
uvicorn api_gateway.main:app --host 0.0.0.0 --port 8000
```

Then open:

```text
http://localhost:8000/docs
```

to use the Swagger interface.

---

## Run Retrieval Evaluation

```bash
python -m evaluator.evaluate_retrieval
```

The evaluation output is written under:

```text
evaluator/results/
```

---

## Kubernetes Deployment

A Helm chart is included under:

```text
helm/
```

The chart provides parameterized Kubernetes resources for deploying the application.

Example:

```bash
helm install incident-copilot ./helm
```

Values can be customized through:

```text
helm/values.yaml
```

---

## Technology Stack

| Area | Technology |
|---|---|
| Language | Python 3.12 |
| API | FastAPI |
| Agent orchestration | LangGraph |
| LLM | OpenAI |
| RAG | Chroma |
| Embeddings | OpenAI Embeddings |
| LLM tracing | LangSmith |
| Validation | Pydantic |
| Kubernetes integration | Kubernetes Python Client |
| Testing | pytest |
| CI/CD | GitHub Actions |
| Deployment | Kubernetes / Helm |
| Observability | LangSmith + custom metrics |
| Prompt management | Version-controlled prompt registry |

---

## Proof of Work

Screenshots throughout this README show the system running across CI quality gates, retrieval evaluation, LangSmith tracing, grounded RCA execution, API documentation, and LLM observability.

---

## Current Limitations

This is an engineering project rather than a production incident-management product.

Some deliberate limitations remain:

- remediation focuses on plan generation and approval controls rather than unrestricted autonomous cluster modification
- the current collector targets a specific workload through a label selector
- the evaluation dataset is intentionally small and designed for regression testing rather than claiming broad model accuracy
- operational runbooks are maintained locally
- authentication and multi-user access control are outside the current API scope
- production deployment would require additional secret management, authentication, network controls, and availability design

These boundaries are intentional. For incident response, I prefer a system that exposes where human approval is required rather than presenting unrestricted autonomous remediation as a feature.

---

## What I Learned

The biggest lesson from this project was that building an LLM application and operating one are different problems.

The LLM call itself became a relatively small part of the system.

Most of the engineering work ended up around it:

```text
retrieval quality
prompt management
structured outputs
validation
retry behavior
evaluation
regression detection
tracing
cost visibility
latency
safety controls
CI/CD
```

That is also why the project evolved from a Kubernetes RCA script into an LLMOps project.

---

## Project Status

The core workflow, RAG pipeline, evaluation framework, prompt experiments, safety controls, observability, API layer, Helm packaging, automated tests, and CI quality gates are implemented.

Further work will focus on hardening integrations and improving the operational experience rather than adding autonomous behavior simply for the sake of automation.
