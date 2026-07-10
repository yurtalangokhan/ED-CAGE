# ED-CAGE

**ED-CAGE** stands for **Event-Driven Continuous Architecture Governance Engine**.

ED-CAGE is a Python-based framework for **evidence-driven continuous architecture governance and evaluation**. It evaluates software systems against architecture rules, repository conventions, deployment artifacts, security practices, API contract quality, runtime service evidence, and observability expectations.

The framework produces machine-readable governance reports, normalized evidence records, category-weighted governance scores, maturity bands, and remediation-oriented governance actions.

---

## Key Features

- YAML-based governance rules
- Static, runtime, and mixed evaluation modes
- Evidence-driven governance findings
- Category-weighted governance scoring
- Maturity-band interpretation
- Rule filtering by ID, category, severity, target, and check type
- Scenario-based governance evaluation
- JSON and Markdown report generation
- JSONL evidence registry
- Governance action recommendations
- Case-study batch evaluation
- External tool adapters for OPA, kube-linter, and Trivy

---

## Evaluation Modes

| Mode | Description |
|---|---|
| `static` | Evaluates repository files, architecture catalog, dependencies, Docker Compose, Kubernetes manifests, security patterns, and external tool evidence. |
| `runtime` | Evaluates running services through health endpoints, OpenAPI/Swagger documents, API policies, and metrics endpoints. |
| `mixed` | Runs all applicable static and runtime checks. |

---

## Repository Structure

```text
ED-CAGE/
├── src/ed_cage/                 # Framework source code
├── configs/
│   ├── rules/                   # Governance rule definitions
│   ├── cases/                   # Case-study configuration files
│   ├── policies/                # Policy-as-code assets
│   └── scenarios/               # Scenario-based evaluation definitions
├── case-studies/                # Open-source systems used for evaluation
├── scripts/                     # Batch evaluation and table generation scripts
├── tests/                       # Unit tests
├── docs/                        # Supporting documentation
├── examples/                    # Example assets
├── outputs/                     # Generated reports and evidence registries
├── docker-compose.tools.yml     # Optional external governance tools
├── pyproject.toml
└── README.md
```

---

## Requirements

### Required

- Python `3.11+`
- Git
- Python virtual environment
- PowerShell, Bash, or another terminal

### Optional

- Docker
- Docker Compose
- Kubernetes / kind / minikube
- `kubectl`
- OPA
- kube-linter
- Trivy

OPA, kube-linter, and Trivy can be used through the provided `docker-compose.tools.yml`.

---

## Installation

Clone the repository:

```bash
git clone https://github.com/yurtalangokhan/ED-CAGE.git
cd ED-CAGE
```

Create and activate a virtual environment.

Windows PowerShell:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
```

Linux/macOS:

```bash
python -m venv .venv
source .venv/bin/activate
```

Install ED-CAGE:

```bash
pip install -e .
```

Install development dependencies:

```bash
pip install -e ".[dev]"
```

Verify the CLI:

```bash
ed-cage --help
```

---

## Basic Usage

Validate a configuration:

```bash
ed-cage validate-config --config configs/ed-cage.yaml
```

Run a governance scan:

```bash
ed-cage scan --config configs/ed-cage.yaml
```

Run static checks only:

```bash
ed-cage scan --config configs/ed-cage.yaml --execution-mode static
```

Run runtime checks only:

```bash
ed-cage scan --config configs/ed-cage.yaml --execution-mode runtime
```

Run a scan with explicit output filenames:

```bash
ed-cage scan \
  --config configs/ed-cage.yaml \
  --report-filename governance-report.json \
  --markdown-report-filename governance-report.md
```

---

## Rule Filtering

Run a single rule:

```bash
ed-cage scan --config configs/ed-cage.yaml --rule-id SVC-001
```

Run multiple rules:

```bash
ed-cage scan --config configs/ed-cage.yaml --rule-id REPO-001,SVC-001
```

Run by category:

```bash
ed-cage scan --config configs/ed-cage.yaml --category security
```

Run by severity:

```bash
ed-cage scan --config configs/ed-cage.yaml --severity high,critical
```

Run by check type:

```bash
ed-cage scan --config configs/ed-cage.yaml --check-type http_health_endpoint
```

---

## Governance Rule Catalog

The default rule set covers repository, architecture, dependency, deployment, security, reliability, API, service, observability, and external tool checks.

| Area | Rule IDs | Purpose |
|---|---|---|
| Repository | `REPO-001`, `REPO-002` | Checks required project files such as `README.md` and `pyproject.toml`. |
| Architecture | `ARCH-001` to `ARCH-003` | Checks ADRs, quality attribute scenarios, and critical service declarations. |
| Dependency | `DEPEN-001` to `DEPEN-003` | Checks declared dependencies, circular dependencies, and external dependency metadata. |
| Docker Compose | `CMP-001` to `CMP-003` | Checks Compose file existence, healthchecks, and container isolation/security risks. |
| Kubernetes Deployment | `DEP-001` to `DEP-008` | Checks manifests, image tags, resource requests/limits, probes, privileged containers, and non-root execution. |
| Reliability | `REL-001` to `REL-005` | Checks replica policy, timeout policy, retry policy, circuit breaker policy, and bounded retries. |
| Security | `SEC-001` to `SEC-003` | Checks obvious secrets, Ingress TLS, and external service exposure. |
| Service Runtime | `SVC-001` to `SVC-003` | Checks health endpoints, OpenAPI/Swagger availability, and metrics endpoint availability. |
| API Contract | `API-001` to `API-006` | Checks API metadata, operation IDs, success/error responses, schemas, and security schemes. |
| Observability | `OBS-001` to `OBS-004` | Checks Prometheus compatibility and required request/error/latency metric groups. |
| External Tools | `TOOL-OPA-001`, `TOOL-K8S-001`, `TOOL-TRIVY-001` | Integrates OPA, kube-linter, and Trivy as evidence-producing governance tools. |

Detailed rule definitions are available under:

```text
configs/rules/
```

---

## Reports and Evidence

Each scan generates:

```text
governance-report.json
governance-report.md
evidence/evidence-registry.jsonl
```

The JSON report includes:

- Run metadata
- Findings
- Normalized evidence
- Rule status summaries
- Severity summaries
- Category-level scores
- Overall governance score
- Maturity band
- Governance gate result
- Recommended governance actions

The Markdown report is intended for human review. The JSON report and JSONL evidence registry are intended for automation, traceability, and downstream analysis.

---

## Scoring and Maturity Bands

ED-CAGE computes category-level scores and an overall governance score.

Formula:

```text
sum(category_score * category_weight) / sum(category_weight)
```

Default maturity interpretation:

| Score Range | Maturity Band |
|---:|---|
| 0-39.99 | Initial Governance |
| 40-59.99 | Emerging Governance |
| 60-74.99 | Managed Governance |
| 75-89.99 | Governed Architecture |
| 90-100 | Continuously Governed Architecture |

Category weights and maturity bands are configurable per project or case study.

---

## External Tool Adapters

ED-CAGE can normalize external tool results into governance findings.

Start optional tool containers:

```bash
docker compose -f docker-compose.tools.yml up
```

| Tool | Governance Use |
|---|---|
| OPA | Policy-as-code checks for architecture catalog governance. |
| kube-linter | Kubernetes manifest production-readiness and security checks. |
| Trivy | Filesystem, IaC misconfiguration, and secret-related security evidence. |

External tool findings appear in static governance reports when the related rules are applicable and enabled.

---

## Case Study Evaluation

ED-CAGE includes case-study configurations for open-source microservice systems.

### Static Evaluation

Run all configured static case studies:

```bash
python scripts/run_static_case_evaluations.py
```

Run one static case:

```bash
python scripts/run_static_case_evaluations.py \
  --config configs/cases/online-boutique-static.yaml
```

Static outputs are generated under:

```text
outputs/case-studies/<case-study>/static/
```

Summary files:

```text
outputs/case-studies/static-evaluation-summary.json
outputs/case-studies/static-evaluation-summary.md
```

### Runtime Evaluation

Start the target system first. Then run:

```bash
python scripts/run_runtime_case_evaluations.py
```

Run one runtime case:

```bash
python scripts/run_runtime_case_evaluations.py \
  --config configs/cases/train-ticket-runtime.yaml
```

Runtime outputs are generated under:

```text
outputs/case-studies/<case-study>/runtime/
```

Summary files:

```text
outputs/case-studies/runtime-evaluation-summary.json
outputs/case-studies/runtime-evaluation-summary.md
```

---

## Adding a New Case Study

To evaluate a new repository, create a case-specific configuration and, when needed, a service catalog and architecture catalog.

### 1. Add or reference the target repository

Recommended layout:

```text
case-studies/<new-case-study>/
```

You may either clone the target repository under `case-studies/` or point `repository_path` to an external local path.

### 2. Create a service catalog

Create:

```text
configs/cases/service-catalogs/<new-case-study>-services.yaml
```

Example:

```yaml
services:
  - name: orders-service
    base_url: http://127.0.0.1:8081
    health_endpoints:
      - /actuator/health
      - /health
    openapi_paths:
      - /v3/api-docs
      - /v2/api-docs
      - /swagger.json
      - /openapi.json
    metrics_paths:
      - /actuator/prometheus
      - /metrics
    tags:
      - domain-service
      - orders
    metadata:
      owner: orders-team
      criticality: high
```

Use runtime URLs that are reachable from the machine running ED-CAGE.

### 3. Create an architecture catalog when dependency checks are needed

Create:

```text
configs/cases/architecture-catalogs/<new-case-study>-service-architecture.yaml
```

Example:

```yaml
services:
  - name: orders-service
    criticality: high
    dependencies:
      - payments-service
      - orders-db

external_dependencies:
  - name: payment-provider
    owner: payments-team
    sla: 99.9
```

Use this catalog for dependency and architecture governance rules such as critical service declaration, declared dependencies, circular dependency detection, and external dependency metadata.

### 4. Create a static configuration

Create:

```text
configs/cases/<new-case-study>-static.yaml
```

Minimum example:

```yaml
project_name: new-case-study-static
repository_path: case-studies/<new-case-study>
rules_path: configs/rules
services_path: configs/cases/service-catalogs/<new-case-study>-services.yaml
actions_path: configs/actions.yaml
scenarios_path: configs/scenarios/case-studies
output_path: outputs/case-studies/<new-case-study>/static
evidence_registry_path: outputs/case-studies/<new-case-study>/static/evidence/evidence-registry.jsonl
architecture_catalog_path: configs/cases/architecture-catalogs/<new-case-study>-service-architecture.yaml

execution_mode: static

governance_gate:
  minimum_score: 65
  fail_on_error: false
  fail_on_critical: false
  fail_on_high: false
  fail_on_medium: false
  fail_on_any_failure: false
```

Disable non-applicable rules explicitly. For example, if the system has Docker Compose but no Kubernetes manifests:

```yaml
disabled_rule_ids:
  - DEP-001
  - DEP-002
  - DEP-003
  - DEP-004
  - DEP-005
  - DEP-006
  - DEP-007
  - DEP-008
  - SEC-002
  - SEC-003
  - TOOL-K8S-001
```

This prevents technology-mismatch false negatives.

### 5. Create a runtime configuration

Create:

```text
configs/cases/<new-case-study>-runtime.yaml
```

Example:

```yaml
project_name: new-case-study-runtime
repository_path: case-studies/<new-case-study>
rules_path: configs/rules
services_path: configs/cases/service-catalogs/<new-case-study>-services.yaml
actions_path: configs/actions.yaml
scenarios_path: configs/scenarios/case-studies
output_path: outputs/case-studies/<new-case-study>/runtime
evidence_registry_path: outputs/case-studies/<new-case-study>/runtime/evidence/evidence-registry.jsonl

execution_mode: runtime

governance_gate:
  minimum_score: 65
  fail_on_error: false
  fail_on_critical: false
  fail_on_high: false
  fail_on_medium: false
  fail_on_any_failure: false
```

Before running runtime evaluation, make sure the target services are running and the configured ports are reachable.

### 6. Validate and run

Validate the configuration:

```bash
ed-cage validate-config --config configs/cases/<new-case-study>-static.yaml
```

Run static evaluation:

```bash
ed-cage scan --config configs/cases/<new-case-study>-static.yaml --execution-mode static
```

Run runtime evaluation:

```bash
ed-cage scan --config configs/cases/<new-case-study>-runtime.yaml --execution-mode runtime
```

### 7. Interpret applicability

Not every rule applies to every system. For credible evaluation:

- Disable Kubernetes rules for non-Kubernetes systems.
- Disable Docker Compose rules for systems without Compose files.
- Exclude HTTP runtime rules for gRPC-only services unless HTTP endpoints are available.
- Prefer documenting rule exclusions in the case configuration.
- Keep generated reports and evidence registries with the evaluation artifact.

---

## Scenario-Based Evaluation

Run a scenario:

```bash
ed-cage run-scenario \
  --config configs/ed-cage.yaml \
  --scenario configs/scenarios/repository_baseline.yaml
```

Scenario reports are written to the configured output directory.

---

## Paper-Ready Tables

Generate Markdown and CSV tables from evaluation outputs:

```bash
python scripts/generate_paper_evaluation_tables.py
```

Default output directory:

```text
outputs/case-studies/paper-tables/
```

Generated tables include case-study systems, governance scores, category scores, governance gaps, and excluded rules.

---

## Development

Run tests:

```bash
pytest
```

Run linting:

```bash
ruff check .
```

Run type checking:

```bash
mypy src
```

---

## Main Concepts

| Concept | Description |
|---|---|
| Governance Rule | YAML-defined architectural or operational expectation. |
| Check | Executable logic that evaluates a rule. |
| Evidence | Observed data collected during evaluation. |
| Finding | Result of evaluating one governance rule. |
| Action | Recommended remediation generated from a finding. |
| Scenario | Focused governance evaluation profile. |
| Governance Gate | Pass/fail policy over score and findings. |
| Maturity Band | Qualitative interpretation of the governance score. |

---

## Current Scope

ED-CAGE currently focuses on:

- Continuous architecture governance
- Static repository and deployment evaluation
- Runtime service evidence evaluation
- API documentation governance
- Observability evidence checks
- Architecture catalog and dependency governance
- Policy-as-code and external tool evidence integration

The framework is intended for research, experimentation, and extensible governance automation.

---

## License

No license has been published yet. Add a license file before distributing or reusing this project outside its current research and development context.

---

## Citation

If you use ED-CAGE in academic work, cite the repository and the related publication when available:

```text
ED-CAGE: An Evidence-Driven Continuous Architecture Governance and Evaluation Framework.
https://github.com/yurtalangokhan/ED-CAGE
```
