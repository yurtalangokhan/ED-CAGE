# ED-CAGE

ED-CAGE stands for **Event-Driven Continuous Architecture Governance Engine**.

It is a Python-based framework for continuous architecture governance. The goal is to evaluate software systems continuously against architectural rules, quality attributes, governance policies and engineering best practices.

## Initial Capabilities

Current bootstrap version supports:

- YAML-based governance rules
- Rule loading from filesystem
- Pluggable governance checks
- Rich console reporting
- CLI execution
- Repository-level required file checks

## Reports

ED-CAGE generates a machine-readable JSON report after each scan.

Default report path:

``text
outputs/governance-report.json

## Run

``bash
ed-cage scan --report-filename local-report.json

## Rule Filtering

ED-CAGE supports targeted governance scans by rule ID, category, severity, check type and target.

Run a single rule:

``bash
ed-cage scan --rule-id SVC-001
ed-cage scan --rule-id REPO-001,SVC-001
ed-cage scan --category service


