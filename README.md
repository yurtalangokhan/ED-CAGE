# ED-CAGE

**ED-CAGE** stands for **Event-Driven Continuous Architecture Governance Engine**.

ED-CAGE is a Python-based framework for **continuous architecture governance and evaluation**. It evaluates software systems against architecture rules, governance policies, quality-attribute expectations, deployment practices, API documentation requirements, runtime service evidence, and engineering best practices.

The framework is designed for evidence-driven governance: every scan produces machine-readable findings, normalized evidence, governance actions, score summaries, and maturity-band results.

---

## Key Capabilities

- YAML-based governance rule definition
- Static and runtime governance evaluation
- Evidence-driven governance findings
- Category-weighted governance scoring
- Maturity-band based evaluation
- Rule filtering by ID, category, severity, target, and check type
- Scenario-based governance evaluation
- JSON and Markdown report generation
- Evidence registry output in JSONL format
- Governance action recommendation generation
- Case-study batch evaluation scripts
- Tool-adapter integration for policy and infrastructure evidence

---

## Evaluation Modes

ED-CAGE supports three execution modes:

| Mode | Purpose |
|---|---|
| `static` | Evaluates repository, architecture catalog, dependency, deployment, security, Kubernetes, Docker Compose, and policy-as-code evidence. |
| `runtime` | Evaluates running services through health endpoints, OpenAPI/Swagger documents, and metrics/observability endpoints. |
| `mixed` | Runs both static and runtime applicable governance checks. |

---

## Repository Structure

```text
ED-CAGE/
├── src/ed_cage/                 # Framework source code
├── configs/                     # Rules, actions, services, scenarios and case configs
│   ├── rules/                   # Governance rule definitions
│   ├── cases/                   # Case-study specific configuration files
│   └── scenarios/               # Scenario-based evaluation definitions
├── case-studies/                # Open-source systems used for evaluation
├── scripts/                     # Batch evaluation and paper table generation scripts
├── tests/                       # Unit tests
├── docs/                        # Supporting documentation
├── examples/                    # Example assets
├── outputs/                     # Generated reports and evidence registries
├── docker-compose.tools.yml     # Optional external tool containers
├── pyproject.toml               # Python package and development configuration
└── README.md
```

---

## Requirements

### Required

- Python `3.11+`
- Git
- PowerShell, Bash, or another terminal
- Python virtual environment

### Optional External Tools

Some static governance checks can use external tools through Docker:

- Open Policy Agent (OPA)
- kube-linter
- Trivy

These are configured through `docker-compose.tools.yml`.

### Optional Runtime Dependencies

Runtime evaluation requires the target system to be running locally or remotely and reachable from the machine running ED-CAGE.

For Kubernetes-based case studies, you may also need:

- Docker Desktop
- Kubernetes / kind / minikube
- `kubectl`

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

Install ED-CAGE in editable mode:

```bash
pip install -e .
```

For development dependencies:

```bash
pip install -e ".[dev]"
```

Validate the CLI installation:

```bash
ed-cage --help
```

---

## Configuration

ED-CAGE uses YAML configuration files. A project configuration defines the repository under evaluation, rule paths, service catalog, output location, governance gate, scoring settings, and execution mode.

Example configuration fields:

```yaml
project_name: my-system
repository_path: .
rules_path: configs/rules
services_path: configs/services.yaml
actions_path: configs/actions.yaml
scenarios_path: configs/scenarios
output_path: outputs
evidence_registry_path: outputs/evidence/evidence-registry.jsonl
execution_mode: mixed
```

Validate a configuration:

```bash
ed-cage validate-config --config configs/ed-cage.yaml
```

---

## Running a Governance Scan

Run a default scan:

```bash
ed-cage scan --config configs/ed-cage.yaml
```

Run with an explicit report filename:

```bash
ed-cage scan \
  --config configs/ed-cage.yaml \
  --report-filename governance-report.json \
  --markdown-report-filename governance-report.md
```

Run only static checks:

```bash
ed-cage scan --config configs/ed-cage.yaml --execution-mode static
```

Run only runtime checks:

```bash
ed-cage scan --config configs/ed-cage.yaml --execution-mode runtime
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
ed-cage scan --config configs/ed-cage.yaml --category service
```

Run by severity:

```bash
ed-cage scan --config configs/ed-cage.yaml --severity high,medium
```

Run by check type:

```bash
ed-cage scan --config configs/ed-cage.yaml --check-type http_health_endpoint
```

---

## Scenario-Based Evaluation

Scenarios define focused governance evaluations and assertions.

Run a scenario:

```bash
ed-cage run-scenario \
  --config configs/ed-cage.yaml \
  --scenario configs/scenarios/repository_baseline.yaml
```

Scenario runs generate normal governance reports and an additional scenario report.

---

## Case Study Evaluation

ED-CAGE includes case-study configurations for open-source microservice systems.

### Static Evaluation

Run static evaluation for all configured case studies:

```bash
python scripts/run_static_case_evaluations.py
```

Run a specific static case:

```bash
python scripts/run_static_case_evaluations.py \
  --config configs/cases/online-boutique-static.yaml
```

Static outputs are written under:

```text
outputs/case-studies/<case-study>/static/
```

A summary is generated at:

```text
outputs/case-studies/static-evaluation-summary.json
outputs/case-studies/static-evaluation-summary.md
```

### Runtime Evaluation

Start the target system first. Then run:

```bash
python scripts/run_runtime_case_evaluations.py
```

Run a specific runtime case:

```bash
python scripts/run_runtime_case_evaluations.py \
  --config configs/cases/train-ticket-runtime.yaml
```

Runtime outputs are written under:

```text
outputs/case-studies/<case-study>/runtime/
```

A runtime summary is generated at:

```text
outputs/case-studies/runtime-evaluation-summary.json
outputs/case-studies/runtime-evaluation-summary.md
```

---

## External Tool Adapters

ED-CAGE can integrate external tools as governance evidence sources.

Start optional tool containers:

```bash
docker compose -f docker-compose.tools.yml up
```

The provided tool compose file includes:

| Tool | Purpose |
|---|---|
| OPA | Policy-as-code evaluation |
| kube-linter | Kubernetes manifest best-practice checks |
| Trivy | Misconfiguration, secret, and security scanning evidence |

Tool outputs are normalized into ED-CAGE governance findings and evidence records when applicable.

---

## Reports and Evidence

Each scan produces:

```text
governance-report.json
governance-report.md
evidence/evidence-registry.jsonl
```

The JSON report includes:

- Run metadata
- Findings
- Rule status
- Severity and category summaries
- Normalized evidence
- Governance score
- Maturity band
- Governance gate result
- Recommended governance actions

The Markdown report is intended for human review. The JSON report and JSONL evidence registry are intended for automation, traceability, and downstream analysis.

---

## Scoring and Maturity

ED-CAGE computes category-level and overall governance scores.

The overall score is calculated as:

```text
sum(category_score * category_weight) / sum(category_weight)
```

Typical maturity bands:

| Score Range | Maturity Band |
|---:|---|
| 0-39.99 | Initial Governance |
| 40-59.99 | Emerging Governance |
| 60-74.99 | Managed Governance |
| 75-89.99 | Governed Architecture |
| 90-100 | Continuously Governed Architecture |

Category weights can be configured per project or case study.

---

## Paper-Ready Evaluation Tables

Generate paper-ready Markdown and CSV tables from evaluation summaries:

```bash
python scripts/generate_paper_evaluation_tables.py
```

Default output directory:

```text
outputs/case-studies/paper-tables/
```

Generated tables include:

- Case study systems
- Governance score results
- Category-level scores
- Top governance gaps
- Excluded or not-applicable rules

---

## Development

Install development dependencies:

```bash
pip install -e ".[dev]"
```

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
| Governance Rule | A YAML-defined policy or architectural expectation. |
| Check | Executable logic that evaluates a rule against repository, service, deployment, or runtime evidence. |
| Evidence | Observed data collected during governance evaluation. |
| Finding | Result of evaluating one governance rule. |
| Action | Recommended remediation or improvement generated from a finding. |
| Scenario | A focused evaluation profile with assertions. |
| Governance Gate | Pass/fail policy applied to the governance score and findings. |
| Maturity Band | Qualitative interpretation of the governance score. |

---

## Current Scope

ED-CAGE currently focuses on:

- Continuous architecture governance
- Static architecture and repository evaluation
- Runtime service evidence evaluation
- API documentation governance
- Deployment and infrastructure governance
- Observability evidence checks
- Policy-as-code and tool-adapter based governance evidence

The framework is intended for research, experimentation, and extensible governance automation.

---

## License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.

---

## Citation

If you use ED-CAGE in academic work, cite the framework repository and related publication once available:

```text
ED-CAGE: An Evidence-Driven Continuous Architecture Governance and Evaluation Framework.
https://github.com/yurtalangokhan/ED-CAGE
```
