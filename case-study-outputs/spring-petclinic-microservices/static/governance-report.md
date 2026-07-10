# ED-CAGE Governance Report

## Run Information

- Run ID: `7b406db1-9c3c-421f-a0db-41d47ce094a9`
- Project: **spring-petclinic-microservices-static**
- Started at: `2026-07-08T12:31:55.948554+00:00`
- Finished at: `2026-07-08T12:31:58.309738+00:00`
- Overall result: **FAILED**
- Governance score: **73.58 / 100**
- Achieved score: `493.0`
- Max score: `670.0`
- Evaluated findings: `16`
- Skipped findings: `0`

## Governance Gate

- Gate result: **FAILED**
- Actual score: `73.58`
- Minimum score: `70.00`
- Blocking findings: `SEC-001`

### Gate Reason(s)

- Blocking critical finding detected: SEC-001

## Recommended Actions

| Rule ID | Priority | Type | Action | Recommendation |
|---|---|---|---|---|
| ARCH-001 | medium | documentation | Add Architecture Decision Records directory | Create an ADR directory and document significant architecture decisions. |
| ARCH-002 | high | documentation | Document quality attribute scenarios | Document quality attribute scenarios for architecture evaluation and governance. |
| CMP-002 | high | remediation | Remediate governance rule violation | Review the failed governance rule and remediate the architecture or configuration issue reported by ED-CAGE. |
| REL-005 | high | remediation | Bound retry attempts and backoff | Ensure retry policies define maximum attempts and wait/backoff duration. |
| SEC-001 | critical | remediation | Remove committed secrets | Remove detected secrets from the repository and rotate affected credentials. |

### ACTION-ARCH-001-ADR-DIRECTORY:ARCH-001

- Rule ID: `ARCH-001`
- Finding status: `failed`
- Severity: `medium`
- Priority: `medium`
- Action type: `documentation`
- Recommendation: Create an ADR directory and document significant architecture decisions.
- Implementation hint: Add docs/adr and create ADR files using a consistent template including status, context, decision and consequences.
- Tags: `architecture, adr, documentation`

### ACTION-ARCH-002-QUALITY-SCENARIOS:ARCH-002

- Rule ID: `ARCH-002`
- Finding status: `failed`
- Severity: `high`
- Priority: `high`
- Action type: `documentation`
- Recommendation: Document quality attribute scenarios for architecture evaluation and governance.
- Implementation hint: Add docs/quality-attributes/scenarios.yaml and define scenarios for availability, performance, security, modifiability and observability.
- Tags: `architecture, quality-attributes, scenarios`

### DEFAULT-FAILED:CMP-002

- Rule ID: `CMP-002`
- Finding status: `failed`
- Severity: `high`
- Priority: `high`
- Action type: `remediation`
- Recommendation: Review the failed governance rule and remediate the architecture or configuration issue reported by ED-CAGE.
- Implementation hint: Use the finding message and normalized evidence to identify the non-compliant resource and expected value.
- Tags: `default-action, remediation`

### ACTION-REL-005-BOUNDED-RETRY:REL-005

- Rule ID: `REL-005`
- Finding status: `failed`
- Severity: `high`
- Priority: `high`
- Action type: `remediation`
- Recommendation: Ensure retry policies define maximum attempts and wait/backoff duration.
- Implementation hint: Configure maxAttempts and waitDuration/backoff to prevent retry storms and cascading failures.
- Tags: `reliability, retry, backoff`

### ACTION-SEC-001-REMOVE-COMMITTED-SECRETS:SEC-001

- Rule ID: `SEC-001`
- Finding status: `failed`
- Severity: `critical`
- Priority: `critical`
- Action type: `remediation`
- Recommendation: Remove detected secrets from the repository and rotate affected credentials.
- Implementation hint: Move secrets to a secret management mechanism and purge leaked secrets from version history where necessary.
- Tags: `security, secrets, repository`

## Status Summary

| Status | Count |
|---|---:|
| passed | 11 |
| failed | 5 |
| skipped | 0 |
| error | 0 |

## Severity Summary

| Severity | Count |
|---|---:|
| info | 0 |
| low | 0 |
| medium | 3 |
| high | 11 |
| critical | 2 |

## Findings

| Rule ID | Severity | Status | Message |
|---|---|---|---|
| ARCH-001 | medium | failed | Required repository path violations detected: 1. |
| ARCH-002 | high | failed | Required repository path violations detected: 1. |
| ARCH-003 | high | passed | Architecture catalog policy passed: require_critical_services. |
| DEPEN-001 | high | passed | Architecture catalog policy passed: require_declared_dependencies. |
| DEPEN-002 | critical | passed | Architecture catalog policy passed: disallow_circular_dependencies. |
| DEPEN-003 | high | passed | Architecture catalog policy passed: require_external_dependency_metadata. |
| CMP-001 | high | passed | Docker Compose file exists and is parseable. |
| CMP-002 | high | failed | Docker Compose service healthcheck violations detected: 7. |
| CMP-003 | high | passed | Docker Compose security policy passed. |
| REL-002 | high | passed | Required repository configuration pattern group(s) were found. |
| REL-003 | medium | passed | Required repository configuration pattern group(s) were found. |
| REL-004 | high | passed | Required repository configuration pattern group(s) were found. |
| REL-005 | high | failed | Required repository configuration pattern group(s) missing: retry_attempt_bound. |
| REPO-001 | medium | passed | All required file(s) exist. |
| SEC-001 | critical | failed | Potential committed secrets detected: 1. |
| TOOL-OPA-001 | high | passed | External tool check passed: opa. |

## Evidence Details

### ARCH-001 — ADR directory must exist

- Severity: `medium`
- Status: `failed`
- Category: `architecture`
- Target: `repository`
- Check type: `repository_required_paths`
- Message: Required repository path violations detected: 1.

#### Raw Evidence

##### Raw Evidence 1

- Source: `repository-required-paths`
- Message: Repository required path evaluation completed.

```json
{
  "required_paths": [
    {
      "path": "docs/adr",
      "type": "directory"
    }
  ],
  "evaluated_paths": [
    {
      "path": "docs/adr",
      "resolved_path": "E:\\Repositories\\PythonProjects\\ED-CAGE\\case-studies\\spring-petclinic-microservices\\docs\\adr",
      "expected_type": "directory",
      "exists": false,
      "actual_type": "missing"
    }
  ],
  "violations": [
    {
      "path": "docs/adr",
      "expected_type": "directory",
      "reason": "path_does_not_exist"
    }
  ]
}
```

#### Normalized Evidence

| Source Type | Source Name | Resource | Compliant | Observed | Expected |
|---|---|---|---|---|---|
| generic | repository-required-paths | repository-required-paths | False | {'required_paths': [{'path': 'docs/adr', 'type': 'directory'}], 'evaluated_paths': [{'path': 'docs/adr', 'resolved_path': 'E:\\Repositories\\PythonProjects\\ED-CAGE\\case-studies\\spring-petclinic-microservices\\docs\\adr', 'expected_type': 'directory', 'exists': False, 'actual_type': 'missing'}], 'violations': [{'path': 'docs/adr', 'expected_type': 'directory', 'reason': 'path_does_not_exist'}]} | None |

### ARCH-002 — Quality attribute scenarios must be documented

- Severity: `high`
- Status: `failed`
- Category: `architecture`
- Target: `repository`
- Check type: `repository_required_paths`
- Message: Required repository path violations detected: 1.

#### Raw Evidence

##### Raw Evidence 1

- Source: `repository-required-paths`
- Message: Repository required path evaluation completed.

```json
{
  "required_paths": [
    {
      "path": "docs/quality-attributes/scenarios.yaml",
      "type": "file"
    }
  ],
  "evaluated_paths": [
    {
      "path": "docs/quality-attributes/scenarios.yaml",
      "resolved_path": "E:\\Repositories\\PythonProjects\\ED-CAGE\\case-studies\\spring-petclinic-microservices\\docs\\quality-attributes\\scenarios.yaml",
      "expected_type": "file",
      "exists": false,
      "actual_type": "missing"
    }
  ],
  "violations": [
    {
      "path": "docs/quality-attributes/scenarios.yaml",
      "expected_type": "file",
      "reason": "path_does_not_exist"
    }
  ]
}
```

#### Normalized Evidence

| Source Type | Source Name | Resource | Compliant | Observed | Expected |
|---|---|---|---|---|---|
| generic | repository-required-paths | repository-required-paths | False | {'required_paths': [{'path': 'docs/quality-attributes/scenarios.yaml', 'type': 'file'}], 'evaluated_paths': [{'path': 'docs/quality-attributes/scenarios.yaml', 'resolved_path': 'E:\\Repositories\\PythonProjects\\ED-CAGE\\case-studies\\spring-petclinic-microservices\\docs\\quality-attributes\\scenarios.yaml', 'expected_type': 'file', 'exists': False, 'actual_type': 'missing'}], 'violations': [{'path': 'docs/quality-attributes/scenarios.yaml', 'expected_type': 'file', 'reason': 'path_does_not_exist'}]} | None |

### ARCH-003 — Critical services must be declared

- Severity: `high`
- Status: `passed`
- Category: `architecture`
- Target: `architecture-catalog`
- Check type: `architecture_catalog_policy`
- Message: Architecture catalog policy passed: require_critical_services.

#### Raw Evidence

##### Raw Evidence 1

- Source: `architecture-catalog-policy`
- Message: Architecture catalog policy evaluation completed: require_critical_services.

```json
{
  "policy": "require_critical_services",
  "architecture_catalog_path": "E:\\Repositories\\PythonProjects\\ED-CAGE\\configs\\cases\\architecture-catalogs\\spring-petclinic-microservices-service-architecture.yaml",
  "resolved_path": "E:\\Repositories\\PythonProjects\\ED-CAGE\\configs\\cases\\architecture-catalogs\\spring-petclinic-microservices-service-architecture.yaml",
  "catalog_exists": true,
  "load_errors": [],
  "success": true,
  "failure_reason": null,
  "critical_services": [
    "api-gateway",
    "customers-service",
    "discovery-server"
  ],
  "service_count": 6
}
```

#### Normalized Evidence

| Source Type | Source Name | Resource | Compliant | Observed | Expected |
|---|---|---|---|---|---|
| generic | architecture-catalog-policy | architecture-catalog-policy | True | {'policy': 'require_critical_services', 'architecture_catalog_path': 'E:\\Repositories\\PythonProjects\\ED-CAGE\\configs\\cases\\architecture-catalogs\\spring-petclinic-microservices-service-architecture.yaml', 'resolved_path': 'E:\\Repositories\\PythonProjects\\ED-CAGE\\configs\\cases\\architecture-catalogs\\spring-petclinic-microservices-service-architecture.yaml', 'catalog_exists': True, 'load_errors': [], 'success': True, 'failure_reason': None, 'critical_services': ['api-gateway', 'customers-service', 'discovery-server'], 'service_count': 6} | None |

### DEPEN-001 — Service dependencies must be explicitly declared

- Severity: `high`
- Status: `passed`
- Category: `dependency`
- Target: `architecture-catalog`
- Check type: `architecture_catalog_policy`
- Message: Architecture catalog policy passed: require_declared_dependencies.

#### Raw Evidence

##### Raw Evidence 1

- Source: `architecture-catalog-policy`
- Message: Architecture catalog policy evaluation completed: require_declared_dependencies.

```json
{
  "policy": "require_declared_dependencies",
  "architecture_catalog_path": "E:\\Repositories\\PythonProjects\\ED-CAGE\\configs\\cases\\architecture-catalogs\\spring-petclinic-microservices-service-architecture.yaml",
  "resolved_path": "E:\\Repositories\\PythonProjects\\ED-CAGE\\configs\\cases\\architecture-catalogs\\spring-petclinic-microservices-service-architecture.yaml",
  "catalog_exists": true,
  "load_errors": [],
  "success": true,
  "failure_reason": null,
  "service_count": 6,
  "violations": []
}
```

#### Normalized Evidence

| Source Type | Source Name | Resource | Compliant | Observed | Expected |
|---|---|---|---|---|---|
| generic | architecture-catalog-policy | architecture-catalog-policy | True | {'policy': 'require_declared_dependencies', 'architecture_catalog_path': 'E:\\Repositories\\PythonProjects\\ED-CAGE\\configs\\cases\\architecture-catalogs\\spring-petclinic-microservices-service-architecture.yaml', 'resolved_path': 'E:\\Repositories\\PythonProjects\\ED-CAGE\\configs\\cases\\architecture-catalogs\\spring-petclinic-microservices-service-architecture.yaml', 'catalog_exists': True, 'load_errors': [], 'success': True, 'failure_reason': None, 'service_count': 6, 'violations': []} | None |

### DEPEN-002 — Circular service dependencies must not exist

- Severity: `critical`
- Status: `passed`
- Category: `dependency`
- Target: `architecture-catalog`
- Check type: `architecture_catalog_policy`
- Message: Architecture catalog policy passed: disallow_circular_dependencies.

#### Raw Evidence

##### Raw Evidence 1

- Source: `architecture-catalog-policy`
- Message: Architecture catalog policy evaluation completed: disallow_circular_dependencies.

```json
{
  "policy": "disallow_circular_dependencies",
  "architecture_catalog_path": "E:\\Repositories\\PythonProjects\\ED-CAGE\\configs\\cases\\architecture-catalogs\\spring-petclinic-microservices-service-architecture.yaml",
  "resolved_path": "E:\\Repositories\\PythonProjects\\ED-CAGE\\configs\\cases\\architecture-catalogs\\spring-petclinic-microservices-service-architecture.yaml",
  "catalog_exists": true,
  "load_errors": [],
  "success": true,
  "failure_reason": null,
  "service_count": 6,
  "graph": {
    "customers-service": [],
    "api-gateway": [
      "customers-service",
      "vets-service",
      "visits-service"
    ],
    "discovery-server": [],
    "config-server": [],
    "visits-service": [],
    "vets-service": []
  },
  "cycles": []
}
```

#### Normalized Evidence

| Source Type | Source Name | Resource | Compliant | Observed | Expected |
|---|---|---|---|---|---|
| generic | architecture-catalog-policy | architecture-catalog-policy | True | {'policy': 'disallow_circular_dependencies', 'architecture_catalog_path': 'E:\\Repositories\\PythonProjects\\ED-CAGE\\configs\\cases\\architecture-catalogs\\spring-petclinic-microservices-service-architecture.yaml', 'resolved_path': 'E:\\Repositories\\PythonProjects\\ED-CAGE\\configs\\cases\\architecture-catalogs\\spring-petclinic-microservices-service-architecture.yaml', 'catalog_exists': True, 'load_errors': [], 'success': True, 'failure_reason': None, 'service_count': 6, 'graph': {'customers-service': [], 'api-gateway': ['customers-service', 'vets-service', 'visits-service'], 'discovery-server': [], 'config-server': [], 'visits-service': [], 'vets-service': []}, 'cycles': []} | None |

### DEPEN-003 — External dependencies must define owner and SLA metadata

- Severity: `high`
- Status: `passed`
- Category: `dependency`
- Target: `architecture-catalog`
- Check type: `architecture_catalog_policy`
- Message: Architecture catalog policy passed: require_external_dependency_metadata.

#### Raw Evidence

##### Raw Evidence 1

- Source: `architecture-catalog-policy`
- Message: Architecture catalog policy evaluation completed: require_external_dependency_metadata.

```json
{
  "policy": "require_external_dependency_metadata",
  "architecture_catalog_path": "E:\\Repositories\\PythonProjects\\ED-CAGE\\configs\\cases\\architecture-catalogs\\spring-petclinic-microservices-service-architecture.yaml",
  "resolved_path": "E:\\Repositories\\PythonProjects\\ED-CAGE\\configs\\cases\\architecture-catalogs\\spring-petclinic-microservices-service-architecture.yaml",
  "catalog_exists": true,
  "load_errors": [],
  "success": true,
  "failure_reason": null,
  "service_count": 6,
  "evaluated_external_dependencies": 0,
  "required_metadata": [
    "owner",
    "sla"
  ],
  "violations": []
}
```

#### Normalized Evidence

| Source Type | Source Name | Resource | Compliant | Observed | Expected |
|---|---|---|---|---|---|
| generic | architecture-catalog-policy | architecture-catalog-policy | True | {'policy': 'require_external_dependency_metadata', 'architecture_catalog_path': 'E:\\Repositories\\PythonProjects\\ED-CAGE\\configs\\cases\\architecture-catalogs\\spring-petclinic-microservices-service-architecture.yaml', 'resolved_path': 'E:\\Repositories\\PythonProjects\\ED-CAGE\\configs\\cases\\architecture-catalogs\\spring-petclinic-microservices-service-architecture.yaml', 'catalog_exists': True, 'load_errors': [], 'success': True, 'failure_reason': None, 'service_count': 6, 'evaluated_external_dependencies': 0, 'required_metadata': ['owner', 'sla'], 'violations': []} | None |

### CMP-001 — Docker Compose file must exist

- Severity: `high`
- Status: `passed`
- Category: `deployment`
- Target: `docker-compose`
- Check type: `docker_compose_file_exists`
- Message: Docker Compose file exists and is parseable.

#### Raw Evidence

##### Raw Evidence 1

- Source: `docker-compose-file-exists`
- Message: Docker Compose file discovery completed.

```json
{
  "candidate_files": [
    "docker-compose.yml",
    "docker-compose.yaml",
    "compose.yml",
    "compose.yaml"
  ],
  "existing_files": [
    "docker-compose.yml"
  ],
  "missing_files": [
    "docker-compose.yaml",
    "compose.yml",
    "compose.yaml"
  ],
  "parse_errors": []
}
```

#### Normalized Evidence

| Source Type | Source Name | Resource | Compliant | Observed | Expected |
|---|---|---|---|---|---|
| filesystem | docker-compose-file-exists | docker-compose-file-exists | True | {'existing_files': ['docker-compose.yml'], 'missing_files': ['docker-compose.yaml', 'compose.yml', 'compose.yaml']} | ['compose.yaml', 'compose.yml', 'docker-compose.yaml', 'docker-compose.yml'] |

### CMP-002 — Docker Compose services should define healthchecks

- Severity: `high`
- Status: `failed`
- Category: `reliability`
- Target: `docker-compose`
- Check type: `docker_compose_healthcheck_policy`
- Message: Docker Compose service healthcheck violations detected: 7.

#### Raw Evidence

##### Raw Evidence 1

- Source: `docker-compose-healthcheck-policy`
- Message: Docker Compose healthcheck policy evaluation completed.

```json
{
  "candidate_files": [
    "docker-compose.yml",
    "docker-compose.yaml",
    "compose.yml",
    "compose.yaml"
  ],
  "existing_files": [
    "docker-compose.yml"
  ],
  "missing_files": [
    "docker-compose.yaml",
    "compose.yml",
    "compose.yaml"
  ],
  "parse_errors": [],
  "ignored_services": [
    "grafana",
    "prometheus",
    "tracing-server",
    "admin-server"
  ],
  "service_count": 9,
  "service_evaluations": [
    {
      "file": "docker-compose.yml",
      "service": "config-server",
      "has_healthcheck": true,
      "healthcheck_disabled": false,
      "has_test": true
    },
    {
      "file": "docker-compose.yml",
      "service": "discovery-server",
      "has_healthcheck": true,
      "healthcheck_disabled": false,
      "has_test": true
    },
    {
      "file": "docker-compose.yml",
      "service": "customers-service",
      "has_healthcheck": false,
      "healthcheck_disabled": false,
      "has_test": false
    },
    {
      "file": "docker-compose.yml",
      "service": "visits-service",
      "has_healthcheck": false,
      "healthcheck_disabled": false,
      "has_test": false
    },
    {
      "file": "docker-compose.yml",
      "service": "vets-service",
      "has_healthcheck": false,
      "healthcheck_disabled": false,
      "has_test": false
    },
    {
      "file": "docker-compose.yml",
      "service": "genai-service",
      "has_healthcheck": false,
      "healthcheck_disabled": false,
      "has_test": false
    },
    {
      "file": "docker-compose.yml",
      "service": "api-gateway",
      "has_healthcheck": false,
      "healthcheck_disabled": false,
      "has_test": false
    },
    {
      "file": "docker-compose.yml",
      "service": "grafana-server",
      "has_healthcheck": false,
      "healthcheck_disabled": false,
      "has_test": false
    },
    {
      "file": "docker-compose.yml",
      "service": "prometheus-server",
      "has_healthcheck": false,
      "healthcheck_disabled": false,
      "has_test": false
    }
  ],
  "violations": [
    {
      "file": "docker-compose.yml",
      "service": "customers-service",
      "reason": "missing_healthcheck"
    },
    {
      "file": "docker-compose.yml",
      "service": "visits-service",
      "reason": "missing_healthcheck"
    },
    {
      "file": "docker-compose.yml",
      "service": "vets-service",
      "reason": "missing_healthcheck"
    },
    {
      "file": "docker-compose.yml",
      "service": "genai-service",
      "reason": "missing_healthcheck"
    },
    {
      "file": "docker-compose.yml",
      "service": "api-gateway",
      "reason": "missing_healthcheck"
    },
    {
      "file": "docker-compose.yml",
      "service": "grafana-server",
      "reason": "missing_healthcheck"
    },
    {
      "file": "docker-compose.yml",
      "service": "prometheus-server",
      "reason": "missing_healthcheck"
    }
  ]
}
```

#### Normalized Evidence

| Source Type | Source Name | Resource | Compliant | Observed | Expected |
|---|---|---|---|---|---|
| filesystem | docker-compose-healthcheck-policy | docker-compose-healthcheck-policy | False | {'existing_files': ['docker-compose.yml'], 'missing_files': ['docker-compose.yaml', 'compose.yml', 'compose.yaml']} | ['compose.yaml', 'compose.yml', 'docker-compose.yaml', 'docker-compose.yml'] |

### CMP-003 — Docker Compose services must avoid privileged or host-level isolation

- Severity: `high`
- Status: `passed`
- Category: `security`
- Target: `docker-compose`
- Check type: `docker_compose_security_policy`
- Message: Docker Compose security policy passed.

#### Raw Evidence

##### Raw Evidence 1

- Source: `docker-compose-security-policy`
- Message: Docker Compose security policy evaluation completed.

```json
{
  "candidate_files": [
    "docker-compose.yml",
    "docker-compose.yaml",
    "compose.yml",
    "compose.yaml"
  ],
  "existing_files": [
    "docker-compose.yml"
  ],
  "missing_files": [
    "docker-compose.yaml",
    "compose.yml",
    "compose.yaml"
  ],
  "parse_errors": [],
  "disallowed_capabilities": [
    "ALL",
    "SYS_ADMIN",
    "NET_ADMIN"
  ],
  "service_count": 11,
  "service_evaluations": [
    {
      "file": "docker-compose.yml",
      "service": "config-server",
      "privileged": false,
      "network_mode": null,
      "pid": null,
      "ipc": null,
      "cap_add": []
    },
    {
      "file": "docker-compose.yml",
      "service": "discovery-server",
      "privileged": false,
      "network_mode": null,
      "pid": null,
      "ipc": null,
      "cap_add": []
    },
    {
      "file": "docker-compose.yml",
      "service": "customers-service",
      "privileged": false,
      "network_mode": null,
      "pid": null,
      "ipc": null,
      "cap_add": []
    },
    {
      "file": "docker-compose.yml",
      "service": "visits-service",
      "privileged": false,
      "network_mode": null,
      "pid": null,
      "ipc": null,
      "cap_add": []
    },
    {
      "file": "docker-compose.yml",
      "service": "vets-service",
      "privileged": false,
      "network_mode": null,
      "pid": null,
      "ipc": null,
      "cap_add": []
    },
    {
      "file": "docker-compose.yml",
      "service": "genai-service",
      "privileged": false,
      "network_mode": null,
      "pid": null,
      "ipc": null,
      "cap_add": []
    },
    {
      "file": "docker-compose.yml",
      "service": "api-gateway",
      "privileged": false,
      "network_mode": null,
      "pid": null,
      "ipc": null,
      "cap_add": []
    },
    {
      "file": "docker-compose.yml",
      "service": "tracing-server",
      "privileged": false,
      "network_mode": null,
      "pid": null,
      "ipc": null,
      "cap_add": []
    },
    {
      "file": "docker-compose.yml",
      "service": "admin-server",
      "privileged": false,
      "network_mode": null,
      "pid": null,
      "ipc": null,
      "cap_add": []
    },
    {
      "file": "docker-compose.yml",
      "service": "grafana-server",
      "privileged": false,
      "network_mode": null,
      "pid": null,
      "ipc": null,
      "cap_add": []
    },
    {
      "file": "docker-compose.yml",
      "service": "prometheus-server",
      "privileged": false,
      "network_mode": null,
      "pid": null,
      "ipc": null,
      "cap_add": []
    }
  ],
  "violations": []
}
```

#### Normalized Evidence

| Source Type | Source Name | Resource | Compliant | Observed | Expected |
|---|---|---|---|---|---|
| filesystem | docker-compose-security-policy | docker-compose-security-policy | True | {'existing_files': ['docker-compose.yml'], 'missing_files': ['docker-compose.yaml', 'compose.yml', 'compose.yaml']} | ['compose.yaml', 'compose.yml', 'docker-compose.yaml', 'docker-compose.yml'] |

### REL-002 — Services should define timeout policy

- Severity: `high`
- Status: `passed`
- Category: `reliability`
- Target: `repository`
- Check type: `repository_configuration_patterns`
- Message: Required repository configuration pattern group(s) were found.

#### Raw Evidence

##### Raw Evidence 1

- Source: `repository-configuration-patterns`
- Message: Repository configuration pattern scan completed.

```json
{
  "include_paths": [
    ".",
    "examples/reliability"
  ],
  "exclude_paths": [
    ".git",
    ".venv",
    "venv",
    "env",
    "__pycache__",
    ".pytest_cache",
    ".mypy_cache",
    ".ruff_cache",
    "outputs",
    "dist",
    "build",
    "node_modules"
  ],
  "file_patterns": [
    "*.yaml",
    "*.yml",
    "*.properties",
    "*.conf",
    "*.json",
    "*.xml"
  ],
  "candidate_file_count": 52,
  "scanned_file_count": 52,
  "skipped_file_count": 0,
  "max_file_size_bytes": 1048576,
  "required_groups": {
    "timeout_policy": {
      "description": "Timeout configuration for service calls.",
      "patterns": [
        "(?i)timeout",
        "(?i)connectTimeout",
        "(?i)readTimeout",
        "(?i)responseTimeout",
        "(?i)timeoutDuration",
        "(?i)timeLimiter"
      ]
    }
  },
  "matched_groups": {
    "timeout_policy": [
      {
        "path": "docker\\grafana\\dashboards\\grafana-petclinic-dashboard.json",
        "line_number": 226,
        "pattern": "(?i)timeout",
        "match_preview": "\"cacheTimeout\": null,"
      },
      {
        "path": "docker\\grafana\\dashboards\\grafana-petclinic-dashboard.json",
        "line_number": 307,
        "pattern": "(?i)timeout",
        "match_preview": "\"cacheTimeout\": null,"
      },
      {
        "path": "docker\\grafana\\dashboards\\grafana-petclinic-dashboard.json",
        "line_number": 389,
        "pattern": "(?i)timeout",
        "match_preview": "\"cacheTimeout\": null,"
      },
      {
        "path": "docker\\grafana\\dashboards\\grafana-petclinic-dashboard.json",
        "line_number": 471,
        "pattern": "(?i)timeout",
        "match_preview": "\"cacheTimeout\": null,"
      },
      {
        "path": "docker\\prometheus\\prometheus.yml",
        "line_number": 5,
        "pattern": "(?i)timeout",
        "match_preview": "# scrape_timeout is set to the global default (10s)."
      },
      {
        "path": "docker-compose.yml",
        "line_number": 12,
        "pattern": "(?i)timeout",
        "match_preview": "timeout: 5s"
      },
      {
        "path": "docker-compose.yml",
        "line_number": 27,
        "pattern": "(?i)timeout",
        "match_preview": "timeout: 3s"
      }
    ]
  },
  "missing_groups": [],
  "skipped_files_sample": []
}
```

#### Normalized Evidence

| Source Type | Source Name | Resource | Compliant | Observed | Expected |
|---|---|---|---|---|---|
| generic | repository-configuration-patterns | repository-configuration-patterns | True | {'include_paths': ['.', 'examples/reliability'], 'exclude_paths': ['.git', '.venv', 'venv', 'env', '__pycache__', '.pytest_cache', '.mypy_cache', '.ruff_cache', 'outputs', 'dist', 'build', 'node_modules'], 'file_patterns': ['*.yaml', '*.yml', '*.properties', '*.conf', '*.json', '*.xml'], 'candidate_file_count': 52, 'scanned_file_count': 52, 'skipped_file_count': 0, 'max_file_size_bytes': 1048576, 'required_groups': {'timeout_policy': {'description': 'Timeout configuration for service calls.', 'patterns': ['(?i)timeout', '(?i)connectTimeout', '(?i)readTimeout', '(?i)responseTimeout', '(?i)timeoutDuration', '(?i)timeLimiter']}}, 'matched_groups': {'timeout_policy': [{'path': 'docker\\grafana\\dashboards\\grafana-petclinic-dashboard.json', 'line_number': 226, 'pattern': '(?i)timeout', 'match_preview': '"cacheTimeout": null,'}, {'path': 'docker\\grafana\\dashboards\\grafana-petclinic-dashboard.json', 'line_number': 307, 'pattern': '(?i)timeout', 'match_preview': '"cacheTimeout": null,'}, {'path': 'docker\\grafana\\dashboards\\grafana-petclinic-dashboard.json', 'line_number': 389, 'pattern': '(?i)timeout', 'match_preview': '"cacheTimeout": null,'}, {'path': 'docker\\grafana\\dashboards\\grafana-petclinic-dashboard.json', 'line_number': 471, 'pattern': '(?i)timeout', 'match_preview': '"cacheTimeout": null,'}, {'path': 'docker\\prometheus\\prometheus.yml', 'line_number': 5, 'pattern': '(?i)timeout', 'match_preview': '# scrape_timeout is set to the global default (10s).'}, {'path': 'docker-compose.yml', 'line_number': 12, 'pattern': '(?i)timeout', 'match_preview': 'timeout: 5s'}, {'path': 'docker-compose.yml', 'line_number': 27, 'pattern': '(?i)timeout', 'match_preview': 'timeout: 3s'}]}, 'missing_groups': [], 'skipped_files_sample': []} | None |

### REL-003 — Services should define retry policy

- Severity: `medium`
- Status: `passed`
- Category: `reliability`
- Target: `repository`
- Check type: `repository_configuration_patterns`
- Message: Required repository configuration pattern group(s) were found.

#### Raw Evidence

##### Raw Evidence 1

- Source: `repository-configuration-patterns`
- Message: Repository configuration pattern scan completed.

```json
{
  "include_paths": [
    ".",
    "examples/reliability"
  ],
  "exclude_paths": [
    ".git",
    ".venv",
    "venv",
    "env",
    "__pycache__",
    ".pytest_cache",
    ".mypy_cache",
    ".ruff_cache",
    "outputs",
    "dist",
    "build",
    "node_modules"
  ],
  "file_patterns": [
    "*.yaml",
    "*.yml",
    "*.properties",
    "*.conf",
    "*.json",
    "*.xml"
  ],
  "candidate_file_count": 52,
  "scanned_file_count": 52,
  "skipped_file_count": 0,
  "max_file_size_bytes": 1048576,
  "required_groups": {
    "retry_policy": {
      "description": "Retry configuration for transient failures.",
      "patterns": [
        "(?i)retry",
        "(?i)retries",
        "(?i)resilience4j\\.retry",
        "(?i)spring\\.retry"
      ]
    }
  },
  "matched_groups": {
    "retry_policy": [
      {
        "path": "docker-compose.yml",
        "line_number": 13,
        "pattern": "(?i)retries",
        "match_preview": "retries: 10"
      },
      {
        "path": "docker-compose.yml",
        "line_number": 28,
        "pattern": "(?i)retries",
        "match_preview": "retries: 10"
      },
      {
        "path": "spring-petclinic-api-gateway\\src\\main\\resources\\application.yml",
        "line_number": 15,
        "pattern": "(?i)retry",
        "match_preview": "- name: Retry"
      },
      {
        "path": "spring-petclinic-api-gateway\\src\\main\\resources\\application.yml",
        "line_number": 17,
        "pattern": "(?i)retries",
        "match_preview": "retries: 1"
      }
    ]
  },
  "missing_groups": [],
  "skipped_files_sample": []
}
```

#### Normalized Evidence

| Source Type | Source Name | Resource | Compliant | Observed | Expected |
|---|---|---|---|---|---|
| generic | repository-configuration-patterns | repository-configuration-patterns | True | {'include_paths': ['.', 'examples/reliability'], 'exclude_paths': ['.git', '.venv', 'venv', 'env', '__pycache__', '.pytest_cache', '.mypy_cache', '.ruff_cache', 'outputs', 'dist', 'build', 'node_modules'], 'file_patterns': ['*.yaml', '*.yml', '*.properties', '*.conf', '*.json', '*.xml'], 'candidate_file_count': 52, 'scanned_file_count': 52, 'skipped_file_count': 0, 'max_file_size_bytes': 1048576, 'required_groups': {'retry_policy': {'description': 'Retry configuration for transient failures.', 'patterns': ['(?i)retry', '(?i)retries', '(?i)resilience4j\\.retry', '(?i)spring\\.retry']}}, 'matched_groups': {'retry_policy': [{'path': 'docker-compose.yml', 'line_number': 13, 'pattern': '(?i)retries', 'match_preview': 'retries: 10'}, {'path': 'docker-compose.yml', 'line_number': 28, 'pattern': '(?i)retries', 'match_preview': 'retries: 10'}, {'path': 'spring-petclinic-api-gateway\\src\\main\\resources\\application.yml', 'line_number': 15, 'pattern': '(?i)retry', 'match_preview': '- name: Retry'}, {'path': 'spring-petclinic-api-gateway\\src\\main\\resources\\application.yml', 'line_number': 17, 'pattern': '(?i)retries', 'match_preview': 'retries: 1'}]}, 'missing_groups': [], 'skipped_files_sample': []} | None |

### REL-004 — Services should define circuit breaker policy

- Severity: `high`
- Status: `passed`
- Category: `reliability`
- Target: `repository`
- Check type: `repository_configuration_patterns`
- Message: Required repository configuration pattern group(s) were found.

#### Raw Evidence

##### Raw Evidence 1

- Source: `repository-configuration-patterns`
- Message: Repository configuration pattern scan completed.

```json
{
  "include_paths": [
    ".",
    "examples/reliability"
  ],
  "exclude_paths": [
    ".git",
    ".venv",
    "venv",
    "env",
    "__pycache__",
    ".pytest_cache",
    ".mypy_cache",
    ".ruff_cache",
    "outputs",
    "dist",
    "build",
    "node_modules"
  ],
  "file_patterns": [
    "*.yaml",
    "*.yml",
    "*.properties",
    "*.conf",
    "*.json",
    "*.xml"
  ],
  "candidate_file_count": 52,
  "scanned_file_count": 52,
  "skipped_file_count": 0,
  "max_file_size_bytes": 1048576,
  "required_groups": {
    "circuit_breaker_policy": {
      "description": "Circuit breaker configuration for dependency isolation.",
      "patterns": [
        "(?i)circuitbreaker",
        "(?i)circuitBreaker",
        "(?i)resilience4j\\.circuitbreaker",
        "(?i)CircuitBreaker"
      ]
    }
  },
  "matched_groups": {
    "circuit_breaker_policy": [
      {
        "path": "spring-petclinic-api-gateway\\pom.xml",
        "line_number": 68,
        "pattern": "(?i)circuitbreaker",
        "match_preview": "<artifactId>spring-cloud-starter-circuitbreaker-reactor-resilience4j</artifactId>"
      },
      {
        "path": "spring-petclinic-api-gateway\\pom.xml",
        "line_number": 68,
        "pattern": "(?i)circuitBreaker",
        "match_preview": "<artifactId>spring-cloud-starter-circuitbreaker-reactor-resilience4j</artifactId>"
      },
      {
        "path": "spring-petclinic-api-gateway\\pom.xml",
        "line_number": 68,
        "pattern": "(?i)CircuitBreaker",
        "match_preview": "<artifactId>spring-cloud-starter-circuitbreaker-reactor-resilience4j</artifactId>"
      },
      {
        "path": "spring-petclinic-api-gateway\\src\\main\\resources\\application.yml",
        "line_number": 11,
        "pattern": "(?i)circuitbreaker",
        "match_preview": "- name: CircuitBreaker"
      },
      {
        "path": "spring-petclinic-api-gateway\\src\\main\\resources\\application.yml",
        "line_number": 11,
        "pattern": "(?i)circuitBreaker",
        "match_preview": "- name: CircuitBreaker"
      },
      {
        "path": "spring-petclinic-api-gateway\\src\\main\\resources\\application.yml",
        "line_number": 11,
        "pattern": "(?i)CircuitBreaker",
        "match_preview": "- name: CircuitBreaker"
      },
      {
        "path": "spring-petclinic-api-gateway\\src\\main\\resources\\application.yml",
        "line_number": 13,
        "pattern": "(?i)circuitbreaker",
        "match_preview": "name: defaultCircuitBreaker"
      },
      {
        "path": "spring-petclinic-api-gateway\\src\\main\\resources\\application.yml",
        "line_number": 13,
        "pattern": "(?i)circuitBreaker",
        "match_preview": "name: defaultCircuitBreaker"
      },
      {
        "path": "spring-petclinic-api-gateway\\src\\main\\resources\\application.yml",
        "line_number": 13,
        "pattern": "(?i)CircuitBreaker",
        "match_preview": "name: defaultCircuitBreaker"
      },
      {
        "path": "spring-petclinic-api-gateway\\src\\main\\resources\\application.yml",
        "line_number": 45,
        "pattern": "(?i)circuitbreaker",
        "match_preview": "- CircuitBreaker=name=genaiCircuitBreaker,fallbackUri=/fallback"
      },
      {
        "path": "spring-petclinic-api-gateway\\src\\main\\resources\\application.yml",
        "line_number": 45,
        "pattern": "(?i)circuitBreaker",
        "match_preview": "- CircuitBreaker=name=genaiCircuitBreaker,fallbackUri=/fallback"
      },
      {
        "path": "spring-petclinic-api-gateway\\src\\main\\resources\\application.yml",
        "line_number": 45,
        "pattern": "(?i)CircuitBreaker",
        "match_preview": "- CircuitBreaker=name=genaiCircuitBreaker,fallbackUri=/fallback"
      },
      {
        "path": "spring-petclinic-genai-service\\pom.xml",
        "line_number": 68,
        "pattern": "(?i)circuitbreaker",
        "match_preview": "<artifactId>spring-cloud-starter-circuitbreaker-reactor-resilience4j</artifactId>"
      },
      {
        "path": "spring-petclinic-genai-service\\pom.xml",
        "line_number": 68,
        "pattern": "(?i)circuitBreaker",
        "match_preview": "<artifactId>spring-cloud-starter-circuitbreaker-reactor-resilience4j</artifactId>"
      },
      {
        "path": "spring-petclinic-genai-service\\pom.xml",
        "line_number": 68,
        "pattern": "(?i)CircuitBreaker",
        "match_preview": "<artifactId>spring-cloud-starter-circuitbreaker-reactor-resilience4j</artifactId>"
      }
    ]
  },
  "missing_groups": [],
  "skipped_files_sample": []
}
```

#### Normalized Evidence

| Source Type | Source Name | Resource | Compliant | Observed | Expected |
|---|---|---|---|---|---|
| generic | repository-configuration-patterns | repository-configuration-patterns | True | {'include_paths': ['.', 'examples/reliability'], 'exclude_paths': ['.git', '.venv', 'venv', 'env', '__pycache__', '.pytest_cache', '.mypy_cache', '.ruff_cache', 'outputs', 'dist', 'build', 'node_modules'], 'file_patterns': ['*.yaml', '*.yml', '*.properties', '*.conf', '*.json', '*.xml'], 'candidate_file_count': 52, 'scanned_file_count': 52, 'skipped_file_count': 0, 'max_file_size_bytes': 1048576, 'required_groups': {'circuit_breaker_policy': {'description': 'Circuit breaker configuration for dependency isolation.', 'patterns': ['(?i)circuitbreaker', '(?i)circuitBreaker', '(?i)resilience4j\\.circuitbreaker', '(?i)CircuitBreaker']}}, 'matched_groups': {'circuit_breaker_policy': [{'path': 'spring-petclinic-api-gateway\\pom.xml', 'line_number': 68, 'pattern': '(?i)circuitbreaker', 'match_preview': '<artifactId>spring-cloud-starter-circuitbreaker-reactor-resilience4j</artifactId>'}, {'path': 'spring-petclinic-api-gateway\\pom.xml', 'line_number': 68, 'pattern': '(?i)circuitBreaker', 'match_preview': '<artifactId>spring-cloud-starter-circuitbreaker-reactor-resilience4j</artifactId>'}, {'path': 'spring-petclinic-api-gateway\\pom.xml', 'line_number': 68, 'pattern': '(?i)CircuitBreaker', 'match_preview': '<artifactId>spring-cloud-starter-circuitbreaker-reactor-resilience4j</artifactId>'}, {'path': 'spring-petclinic-api-gateway\\src\\main\\resources\\application.yml', 'line_number': 11, 'pattern': '(?i)circuitbreaker', 'match_preview': '- name: CircuitBreaker'}, {'path': 'spring-petclinic-api-gateway\\src\\main\\resources\\application.yml', 'line_number': 11, 'pattern': '(?i)circuitBreaker', 'match_preview': '- name: CircuitBreaker'}, {'path': 'spring-petclinic-api-gateway\\src\\main\\resources\\application.yml', 'line_number': 11, 'pattern': '(?i)CircuitBreaker', 'match_preview': '- name: CircuitBreaker'}, {'path': 'spring-petclinic-api-gateway\\src\\main\\resources\\application.yml', 'line_number': 13, 'pattern': '(?i)circuitbreaker', 'match_preview': 'name: defaultCircuitBreaker'}, {'path': 'spring-petclinic-api-gateway\\src\\main\\resources\\application.yml', 'line_number': 13, 'pattern': '(?i)circuitBreaker', 'match_preview': 'name: defaultCircuitBreaker'}, {'path': 'spring-petclinic-api-gateway\\src\\main\\resources\\application.yml', 'line_number': 13, 'pattern': '(?i)CircuitBreaker', 'match_preview': 'name: defaultCircuitBreaker'}, {'path': 'spring-petclinic-api-gateway\\src\\main\\resources\\application.yml', 'line_number': 45, 'pattern': '(?i)circuitbreaker', 'match_preview': '- CircuitBreaker=name=genaiCircuitBreaker,fallbackUri=/fallback'}, {'path': 'spring-petclinic-api-gateway\\src\\main\\resources\\application.yml', 'line_number': 45, 'pattern': '(?i)circuitBreaker', 'match_preview': '- CircuitBreaker=name=genaiCircuitBreaker,fallbackUri=/fallback'}, {'path': 'spring-petclinic-api-gateway\\src\\main\\resources\\application.yml', 'line_number': 45, 'pattern': '(?i)CircuitBreaker', 'match_preview': '- CircuitBreaker=name=genaiCircuitBreaker,fallbackUri=/fallback'}, {'path': 'spring-petclinic-genai-service\\pom.xml', 'line_number': 68, 'pattern': '(?i)circuitbreaker', 'match_preview': '<artifactId>spring-cloud-starter-circuitbreaker-reactor-resilience4j</artifactId>'}, {'path': 'spring-petclinic-genai-service\\pom.xml', 'line_number': 68, 'pattern': '(?i)circuitBreaker', 'match_preview': '<artifactId>spring-cloud-starter-circuitbreaker-reactor-resilience4j</artifactId>'}, {'path': 'spring-petclinic-genai-service\\pom.xml', 'line_number': 68, 'pattern': '(?i)CircuitBreaker', 'match_preview': '<artifactId>spring-cloud-starter-circuitbreaker-reactor-resilience4j</artifactId>'}]}, 'missing_groups': [], 'skipped_files_sample': []} | None |

### REL-005 — Retry policy must be bounded

- Severity: `high`
- Status: `failed`
- Category: `reliability`
- Target: `repository`
- Check type: `repository_configuration_patterns`
- Message: Required repository configuration pattern group(s) missing: retry_attempt_bound.

#### Raw Evidence

##### Raw Evidence 1

- Source: `repository-configuration-patterns`
- Message: Repository configuration pattern scan completed.

```json
{
  "include_paths": [
    ".",
    "examples/reliability"
  ],
  "exclude_paths": [
    ".git",
    ".venv",
    "venv",
    "env",
    "__pycache__",
    ".pytest_cache",
    ".mypy_cache",
    ".ruff_cache",
    "outputs",
    "dist",
    "build",
    "node_modules"
  ],
  "file_patterns": [
    "*.yaml",
    "*.yml",
    "*.properties",
    "*.conf",
    "*.json",
    "*.xml"
  ],
  "candidate_file_count": 52,
  "scanned_file_count": 52,
  "skipped_file_count": 0,
  "max_file_size_bytes": 1048576,
  "required_groups": {
    "retry_attempt_bound": {
      "description": "Maximum retry attempt configuration.",
      "patterns": [
        "(?i)maxAttempts",
        "(?i)maxRetryAttempts",
        "(?i)maximumAttempts"
      ]
    },
    "retry_backoff": {
      "description": "Retry wait duration or backoff configuration.",
      "patterns": [
        "(?i)waitDuration",
        "(?i)backoff",
        "(?i)backOff",
        "(?i)interval"
      ]
    }
  },
  "matched_groups": {
    "retry_attempt_bound": [],
    "retry_backoff": [
      {
        "path": "docker\\grafana\\dashboards\\grafana-petclinic-dashboard.json",
        "line_number": 87,
        "pattern": "(?i)interval",
        "match_preview": "\"intervalFactor\": 1,"
      },
      {
        "path": "docker\\grafana\\dashboards\\grafana-petclinic-dashboard.json",
        "line_number": 94,
        "pattern": "(?i)interval",
        "match_preview": "\"intervalFactor\": 1,"
      },
      {
        "path": "docker\\grafana\\dashboards\\grafana-petclinic-dashboard.json",
        "line_number": 175,
        "pattern": "(?i)interval",
        "match_preview": "\"interval\": \"\","
      },
      {
        "path": "docker\\grafana\\dashboards\\grafana-petclinic-dashboard.json",
        "line_number": 176,
        "pattern": "(?i)interval",
        "match_preview": "\"intervalFactor\": 1,"
      },
      {
        "path": "docker\\grafana\\dashboards\\grafana-petclinic-dashboard.json",
        "line_number": 183,
        "pattern": "(?i)interval",
        "match_preview": "\"interval\": \"\","
      },
      {
        "path": "docker\\grafana\\dashboards\\grafana-petclinic-dashboard.json",
        "line_number": 184,
        "pattern": "(?i)interval",
        "match_preview": "\"intervalFactor\": 1,"
      },
      {
        "path": "docker\\grafana\\dashboards\\grafana-petclinic-dashboard.json",
        "line_number": 250,
        "pattern": "(?i)interval",
        "match_preview": "\"interval\": null,"
      },
      {
        "path": "docker\\grafana\\dashboards\\grafana-petclinic-dashboard.json",
        "line_number": 289,
        "pattern": "(?i)interval",
        "match_preview": "\"intervalFactor\": 1,"
      },
      {
        "path": "docker\\grafana\\dashboards\\grafana-petclinic-dashboard.json",
        "line_number": 331,
        "pattern": "(?i)interval",
        "match_preview": "\"interval\": null,"
      },
      {
        "path": "docker\\grafana\\dashboards\\grafana-petclinic-dashboard.json",
        "line_number": 370,
        "pattern": "(?i)interval",
        "match_preview": "\"intervalFactor\": 1,"
      },
      {
        "path": "docker\\grafana\\dashboards\\grafana-petclinic-dashboard.json",
        "line_number": 413,
        "pattern": "(?i)interval",
        "match_preview": "\"interval\": null,"
      },
      {
        "path": "docker\\grafana\\dashboards\\grafana-petclinic-dashboard.json",
        "line_number": 452,
        "pattern": "(?i)interval",
        "match_preview": "\"intervalFactor\": 1,"
      },
      {
        "path": "docker\\grafana\\dashboards\\grafana-petclinic-dashboard.json",
        "line_number": 495,
        "pattern": "(?i)interval",
        "match_preview": "\"interval\": null,"
      },
      {
        "path": "docker\\grafana\\dashboards\\grafana-petclinic-dashboard.json",
        "line_number": 534,
        "pattern": "(?i)interval",
        "match_preview": "\"intervalFactor\": 1,"
      },
      {
        "path": "docker\\grafana\\dashboards\\grafana-petclinic-dashboard.json",
        "line_number": 596,
        "pattern": "(?i)interval",
        "match_preview": "\"intervalFactor\": 1,"
      },
      {
        "path": "docker\\grafana\\dashboards\\grafana-petclinic-dashboard.json",
        "line_number": 603,
        "pattern": "(?i)interval",
        "match_preview": "\"intervalFactor\": 1,"
      },
      {
        "path": "docker\\grafana\\dashboards\\grafana-petclinic-dashboard.json",
        "line_number": 610,
        "pattern": "(?i)interval",
        "match_preview": "\"intervalFactor\": 1,"
      },
      {
        "path": "docker\\grafana\\dashboards\\grafana-petclinic-dashboard.json",
        "line_number": 617,
        "pattern": "(?i)interval",
        "match_preview": "\"intervalFactor\": 1,"
      },
      {
        "path": "docker\\grafana\\dashboards\\grafana-petclinic-dashboard.json",
        "line_number": 671,
        "pattern": "(?i)interval",
        "match_preview": "\"value\": \"$__auto_interval_timeRange\""
      },
      {
        "path": "docker\\grafana\\dashboards\\grafana-petclinic-dashboard.json",
        "line_number": 680,
        "pattern": "(?i)interval",
        "match_preview": "\"value\": \"$__auto_interval_timeRange\""
      }
    ]
  },
  "missing_groups": [
    "retry_attempt_bound"
  ],
  "skipped_files_sample": []
}
```

#### Normalized Evidence

| Source Type | Source Name | Resource | Compliant | Observed | Expected |
|---|---|---|---|---|---|
| generic | repository-configuration-patterns | repository-configuration-patterns | False | {'include_paths': ['.', 'examples/reliability'], 'exclude_paths': ['.git', '.venv', 'venv', 'env', '__pycache__', '.pytest_cache', '.mypy_cache', '.ruff_cache', 'outputs', 'dist', 'build', 'node_modules'], 'file_patterns': ['*.yaml', '*.yml', '*.properties', '*.conf', '*.json', '*.xml'], 'candidate_file_count': 52, 'scanned_file_count': 52, 'skipped_file_count': 0, 'max_file_size_bytes': 1048576, 'required_groups': {'retry_attempt_bound': {'description': 'Maximum retry attempt configuration.', 'patterns': ['(?i)maxAttempts', '(?i)maxRetryAttempts', '(?i)maximumAttempts']}, 'retry_backoff': {'description': 'Retry wait duration or backoff configuration.', 'patterns': ['(?i)waitDuration', '(?i)backoff', '(?i)backOff', '(?i)interval']}}, 'matched_groups': {'retry_attempt_bound': [], 'retry_backoff': [{'path': 'docker\\grafana\\dashboards\\grafana-petclinic-dashboard.json', 'line_number': 87, 'pattern': '(?i)interval', 'match_preview': '"intervalFactor": 1,'}, {'path': 'docker\\grafana\\dashboards\\grafana-petclinic-dashboard.json', 'line_number': 94, 'pattern': '(?i)interval', 'match_preview': '"intervalFactor": 1,'}, {'path': 'docker\\grafana\\dashboards\\grafana-petclinic-dashboard.json', 'line_number': 175, 'pattern': '(?i)interval', 'match_preview': '"interval": "",'}, {'path': 'docker\\grafana\\dashboards\\grafana-petclinic-dashboard.json', 'line_number': 176, 'pattern': '(?i)interval', 'match_preview': '"intervalFactor": 1,'}, {'path': 'docker\\grafana\\dashboards\\grafana-petclinic-dashboard.json', 'line_number': 183, 'pattern': '(?i)interval', 'match_preview': '"interval": "",'}, {'path': 'docker\\grafana\\dashboards\\grafana-petclinic-dashboard.json', 'line_number': 184, 'pattern': '(?i)interval', 'match_preview': '"intervalFactor": 1,'}, {'path': 'docker\\grafana\\dashboards\\grafana-petclinic-dashboard.json', 'line_number': 250, 'pattern': '(?i)interval', 'match_preview': '"interval": null,'}, {'path': 'docker\\grafana\\dashboards\\grafana-petclinic-dashboard.json', 'line_number': 289, 'pattern': '(?i)interval', 'match_preview': '"intervalFactor": 1,'}, {'path': 'docker\\grafana\\dashboards\\grafana-petclinic-dashboard.json', 'line_number': 331, 'pattern': '(?i)interval', 'match_preview': '"interval": null,'}, {'path': 'docker\\grafana\\dashboards\\grafana-petclinic-dashboard.json', 'line_number': 370, 'pattern': '(?i)interval', 'match_preview': '"intervalFactor": 1,'}, {'path': 'docker\\grafana\\dashboards\\grafana-petclinic-dashboard.json', 'line_number': 413, 'pattern': '(?i)interval', 'match_preview': '"interval": null,'}, {'path': 'docker\\grafana\\dashboards\\grafana-petclinic-dashboard.json', 'line_number': 452, 'pattern': '(?i)interval', 'match_preview': '"intervalFactor": 1,'}, {'path': 'docker\\grafana\\dashboards\\grafana-petclinic-dashboard.json', 'line_number': 495, 'pattern': '(?i)interval', 'match_preview': '"interval": null,'}, {'path': 'docker\\grafana\\dashboards\\grafana-petclinic-dashboard.json', 'line_number': 534, 'pattern': '(?i)interval', 'match_preview': '"intervalFactor": 1,'}, {'path': 'docker\\grafana\\dashboards\\grafana-petclinic-dashboard.json', 'line_number': 596, 'pattern': '(?i)interval', 'match_preview': '"intervalFactor": 1,'}, {'path': 'docker\\grafana\\dashboards\\grafana-petclinic-dashboard.json', 'line_number': 603, 'pattern': '(?i)interval', 'match_preview': '"intervalFactor": 1,'}, {'path': 'docker\\grafana\\dashboards\\grafana-petclinic-dashboard.json', 'line_number': 610, 'pattern': '(?i)interval', 'match_preview': '"intervalFactor": 1,'}, {'path': 'docker\\grafana\\dashboards\\grafana-petclinic-dashboard.json', 'line_number': 617, 'pattern': '(?i)interval', 'match_preview': '"intervalFactor": 1,'}, {'path': 'docker\\grafana\\dashboards\\grafana-petclinic-dashboard.json', 'line_number': 671, 'pattern': '(?i)interval', 'match_preview': '"value": "$__auto_interval_timeRange"'}, {'path': 'docker\\grafana\\dashboards\\grafana-petclinic-dashboard.json', 'line_number': 680, 'pattern': '(?i)interval', 'match_preview': '"value": "$__auto_interval_timeRange"'}]}, 'missing_groups': ['retry_attempt_bound'], 'skipped_files_sample': []} | None |

### REPO-001 — Repository must contain README

- Severity: `medium`
- Status: `passed`
- Category: `repository`
- Target: `repository`
- Check type: `required_files`
- Message: All required file(s) exist.

#### Raw Evidence

##### Raw Evidence 1

- Source: `E:\Repositories\PythonProjects\ED-CAGE\case-studies\spring-petclinic-microservices`
- Message: Required repository files check passed.

```json
{
  "existing_files": [
    "README.md"
  ]
}
```

#### Normalized Evidence

| Source Type | Source Name | Resource | Compliant | Observed | Expected |
|---|---|---|---|---|---|
| filesystem | E:\Repositories\PythonProjects\ED-CAGE\case-studies\spring-petclinic-microservices | E:\Repositories\PythonProjects\ED-CAGE\case-studies\spring-petclinic-microservices | True | {'existing_files': ['README.md'], 'missing_files': []} | ['README.md'] |

### SEC-001 — Repository must not contain obvious secrets

- Severity: `critical`
- Status: `failed`
- Category: `security`
- Target: `repository`
- Check type: `repository_secret_patterns`
- Message: Potential committed secrets detected: 1.

#### Raw Evidence

##### Raw Evidence 1

- Source: `repository-secret-patterns`
- Message: Repository secret pattern scan completed.

```json
{
  "include_paths": [
    "."
  ],
  "exclude_paths": [
    ".git",
    ".venv",
    "venv",
    "env",
    "__pycache__",
    ".pytest_cache",
    ".mypy_cache",
    ".ruff_cache",
    "outputs",
    "dist",
    "build",
    "node_modules",
    "tests"
  ],
  "file_patterns": [
    "*"
  ],
  "candidate_file_count": 208,
  "scanned_file_count": 191,
  "skipped_file_count": 17,
  "max_file_size_bytes": 1048576,
  "secret_pattern_names": [
    "private_key",
    "aws_access_key_id",
    "github_token",
    "generic_secret_assignment"
  ],
  "violations": [
    {
      "path": "README.md",
      "line_number": 128,
      "pattern_name": "generic_secret_assignment",
      "match_preview": "API_***re"
    }
  ],
  "skipped_files_sample": [
    {
      "path": "E:\\Repositories\\PythonProjects\\ED-CAGE\\case-studies\\spring-petclinic-microservices\\.mvn\\wrapper\\maven-wrapper.jar",
      "reason": "binary_file"
    },
    {
      "path": "E:\\Repositories\\PythonProjects\\ED-CAGE\\case-studies\\spring-petclinic-microservices\\docs\\application-screenshot.png",
      "reason": "binary_file"
    },
    {
      "path": "E:\\Repositories\\PythonProjects\\ED-CAGE\\case-studies\\spring-petclinic-microservices\\docs\\grafana-custom-metrics-dashboard.png",
      "reason": "binary_file"
    },
    {
      "path": "E:\\Repositories\\PythonProjects\\ED-CAGE\\case-studies\\spring-petclinic-microservices\\docs\\microservices-architecture-diagram.jpg",
      "reason": "binary_file"
    },
    {
      "path": "E:\\Repositories\\PythonProjects\\ED-CAGE\\case-studies\\spring-petclinic-microservices\\docs\\spring-ai.png",
      "reason": "binary_file"
    },
    {
      "path": "E:\\Repositories\\PythonProjects\\ED-CAGE\\case-studies\\spring-petclinic-microservices\\spring-petclinic-api-gateway\\src\\main\\resources\\static\\fonts\\montserrat-webfont.eot",
      "reason": "binary_file"
    },
    {
      "path": "E:\\Repositories\\PythonProjects\\ED-CAGE\\case-studies\\spring-petclinic-microservices\\spring-petclinic-api-gateway\\src\\main\\resources\\static\\fonts\\montserrat-webfont.ttf",
      "reason": "binary_file"
    },
    {
      "path": "E:\\Repositories\\PythonProjects\\ED-CAGE\\case-studies\\spring-petclinic-microservices\\spring-petclinic-api-gateway\\src\\main\\resources\\static\\fonts\\montserrat-webfont.woff",
      "reason": "binary_file"
    },
    {
      "path": "E:\\Repositories\\PythonProjects\\ED-CAGE\\case-studies\\spring-petclinic-microservices\\spring-petclinic-api-gateway\\src\\main\\resources\\static\\fonts\\varela_round-webfont.eot",
      "reason": "binary_file"
    },
    {
      "path": "E:\\Repositories\\PythonProjects\\ED-CAGE\\case-studies\\spring-petclinic-microservices\\spring-petclinic-api-gateway\\src\\main\\resources\\static\\fonts\\varela_round-webfont.ttf",
      "reason": "binary_file"
    },
    {
      "path": "E:\\Repositories\\PythonProjects\\ED-CAGE\\case-studies\\spring-petclinic-microservices\\spring-petclinic-api-gateway\\src\\main\\resources\\static\\fonts\\varela_round-webfont.woff",
      "reason": "binary_file"
    },
    {
      "path": "E:\\Repositories\\PythonProjects\\ED-CAGE\\case-studies\\spring-petclinic-microservices\\spring-petclinic-api-gateway\\src\\main\\resources\\static\\images\\favicon.png",
      "reason": "binary_file"
    },
    {
      "path": "E:\\Repositories\\PythonProjects\\ED-CAGE\\case-studies\\spring-petclinic-microservices\\spring-petclinic-api-gateway\\src\\main\\resources\\static\\images\\pets.png",
      "reason": "binary_file"
    },
    {
      "path": "E:\\Repositories\\PythonProjects\\ED-CAGE\\case-studies\\spring-petclinic-microservices\\spring-petclinic-api-gateway\\src\\main\\resources\\static\\images\\platform-bg.png",
      "reason": "binary_file"
    },
    {
      "path": "E:\\Repositories\\PythonProjects\\ED-CAGE\\case-studies\\spring-petclinic-microservices\\spring-petclinic-api-gateway\\src\\main\\resources\\static\\images\\spring-logo-dataflow-mobile.png",
      "reason": "binary_file"
    },
    {
      "path": "E:\\Repositories\\PythonProjects\\ED-CAGE\\case-studies\\spring-petclinic-microservices\\spring-petclinic-api-gateway\\src\\main\\resources\\static\\images\\spring-logo-dataflow.png",
      "reason": "binary_file"
    },
    {
      "path": "E:\\Repositories\\PythonProjects\\ED-CAGE\\case-studies\\spring-petclinic-microservices\\spring-petclinic-api-gateway\\src\\main\\resources\\static\\images\\spring-pivotal-logo.png",
      "reason": "binary_file"
    }
  ]
}
```

#### Normalized Evidence

| Source Type | Source Name | Resource | Compliant | Observed | Expected |
|---|---|---|---|---|---|
| generic | repository-secret-patterns | repository-secret-patterns | False | {'include_paths': ['.'], 'exclude_paths': ['.git', '.venv', 'venv', 'env', '__pycache__', '.pytest_cache', '.mypy_cache', '.ruff_cache', 'outputs', 'dist', 'build', 'node_modules', 'tests'], 'file_patterns': ['*'], 'candidate_file_count': 208, 'scanned_file_count': 191, 'skipped_file_count': 17, 'max_file_size_bytes': 1048576, 'secret_pattern_names': ['private_key', 'aws_access_key_id', 'github_token', 'generic_secret_assignment'], 'violations': [{'path': 'README.md', 'line_number': 128, 'pattern_name': 'generic_secret_assignment', 'match_preview': 'API_***re'}], 'skipped_files_sample': [{'path': 'E:\\Repositories\\PythonProjects\\ED-CAGE\\case-studies\\spring-petclinic-microservices\\.mvn\\wrapper\\maven-wrapper.jar', 'reason': 'binary_file'}, {'path': 'E:\\Repositories\\PythonProjects\\ED-CAGE\\case-studies\\spring-petclinic-microservices\\docs\\application-screenshot.png', 'reason': 'binary_file'}, {'path': 'E:\\Repositories\\PythonProjects\\ED-CAGE\\case-studies\\spring-petclinic-microservices\\docs\\grafana-custom-metrics-dashboard.png', 'reason': 'binary_file'}, {'path': 'E:\\Repositories\\PythonProjects\\ED-CAGE\\case-studies\\spring-petclinic-microservices\\docs\\microservices-architecture-diagram.jpg', 'reason': 'binary_file'}, {'path': 'E:\\Repositories\\PythonProjects\\ED-CAGE\\case-studies\\spring-petclinic-microservices\\docs\\spring-ai.png', 'reason': 'binary_file'}, {'path': 'E:\\Repositories\\PythonProjects\\ED-CAGE\\case-studies\\spring-petclinic-microservices\\spring-petclinic-api-gateway\\src\\main\\resources\\static\\fonts\\montserrat-webfont.eot', 'reason': 'binary_file'}, {'path': 'E:\\Repositories\\PythonProjects\\ED-CAGE\\case-studies\\spring-petclinic-microservices\\spring-petclinic-api-gateway\\src\\main\\resources\\static\\fonts\\montserrat-webfont.ttf', 'reason': 'binary_file'}, {'path': 'E:\\Repositories\\PythonProjects\\ED-CAGE\\case-studies\\spring-petclinic-microservices\\spring-petclinic-api-gateway\\src\\main\\resources\\static\\fonts\\montserrat-webfont.woff', 'reason': 'binary_file'}, {'path': 'E:\\Repositories\\PythonProjects\\ED-CAGE\\case-studies\\spring-petclinic-microservices\\spring-petclinic-api-gateway\\src\\main\\resources\\static\\fonts\\varela_round-webfont.eot', 'reason': 'binary_file'}, {'path': 'E:\\Repositories\\PythonProjects\\ED-CAGE\\case-studies\\spring-petclinic-microservices\\spring-petclinic-api-gateway\\src\\main\\resources\\static\\fonts\\varela_round-webfont.ttf', 'reason': 'binary_file'}, {'path': 'E:\\Repositories\\PythonProjects\\ED-CAGE\\case-studies\\spring-petclinic-microservices\\spring-petclinic-api-gateway\\src\\main\\resources\\static\\fonts\\varela_round-webfont.woff', 'reason': 'binary_file'}, {'path': 'E:\\Repositories\\PythonProjects\\ED-CAGE\\case-studies\\spring-petclinic-microservices\\spring-petclinic-api-gateway\\src\\main\\resources\\static\\images\\favicon.png', 'reason': 'binary_file'}, {'path': 'E:\\Repositories\\PythonProjects\\ED-CAGE\\case-studies\\spring-petclinic-microservices\\spring-petclinic-api-gateway\\src\\main\\resources\\static\\images\\pets.png', 'reason': 'binary_file'}, {'path': 'E:\\Repositories\\PythonProjects\\ED-CAGE\\case-studies\\spring-petclinic-microservices\\spring-petclinic-api-gateway\\src\\main\\resources\\static\\images\\platform-bg.png', 'reason': 'binary_file'}, {'path': 'E:\\Repositories\\PythonProjects\\ED-CAGE\\case-studies\\spring-petclinic-microservices\\spring-petclinic-api-gateway\\src\\main\\resources\\static\\images\\spring-logo-dataflow-mobile.png', 'reason': 'binary_file'}, {'path': 'E:\\Repositories\\PythonProjects\\ED-CAGE\\case-studies\\spring-petclinic-microservices\\spring-petclinic-api-gateway\\src\\main\\resources\\static\\images\\spring-logo-dataflow.png', 'reason': 'binary_file'}, {'path': 'E:\\Repositories\\PythonProjects\\ED-CAGE\\case-studies\\spring-petclinic-microservices\\spring-petclinic-api-gateway\\src\\main\\resources\\static\\images\\spring-pivotal-logo.png', 'reason': 'binary_file'}]} | None |

### TOOL-OPA-001 — Architecture catalog must satisfy OPA policy-as-code baseline

- Severity: `high`
- Status: `passed`
- Category: `architecture`
- Target: `architecture-catalog`
- Check type: `external_tool`
- Message: External tool check passed: opa.

#### Raw Evidence

##### Raw Evidence 1

- Source: `external-tool:opa`
- Message: OPA policy evaluation completed. Findings: 0.

```json
{
  "tool_name": "opa",
  "status": "success",
  "message": "OPA policy evaluation completed. Findings: 0.",
  "command": [
    "opa",
    "eval",
    "--format",
    "json",
    "--data",
    "E:\\Repositories\\PythonProjects\\ED-CAGE\\configs\\policies\\architecture_catalog.rego",
    "--input",
    "E:\\Repositories\\PythonProjects\\ED-CAGE\\outputs\\tools\\opa\\opa-input-66698b2f-11be-45d6-89b2-851888810119.json",
    "data.ed_cage.architecture.deny"
  ],
  "exit_code": 0,
  "stdout": "{\n  \"result\": [\n    {\n      \"expressions\": [\n        {\n          \"value\": [],\n          \"text\": \"data.ed_cage.architecture.deny\",\n          \"location\": {\n            \"row\": 1,\n            \"col\": 1\n          }\n        }\n      ]\n    }\n  ]\n}\n",
  "stderr": "",
  "resource": "E:\\Repositories\\PythonProjects\\ED-CAGE\\configs\\cases\\architecture-catalogs\\spring-petclinic-microservices-service-architecture.yaml",
  "findings": [],
  "summary": {
    "policy_path": "E:\\Repositories\\PythonProjects\\ED-CAGE\\configs\\policies\\architecture_catalog.rego",
    "query": "data.ed_cage.architecture.deny",
    "finding_count": 0,
    "execution_mode": "local"
  },
  "metadata": {}
}
```

#### Normalized Evidence

| Source Type | Source Name | Resource | Compliant | Observed | Expected |
|---|---|---|---|---|---|
| generic | external-tool:opa | external-tool:opa | True | {'tool_name': 'opa', 'status': 'success', 'message': 'OPA policy evaluation completed. Findings: 0.', 'command': ['opa', 'eval', '--format', 'json', '--data', 'E:\\Repositories\\PythonProjects\\ED-CAGE\\configs\\policies\\architecture_catalog.rego', '--input', 'E:\\Repositories\\PythonProjects\\ED-CAGE\\outputs\\tools\\opa\\opa-input-66698b2f-11be-45d6-89b2-851888810119.json', 'data.ed_cage.architecture.deny'], 'exit_code': 0, 'stdout': '{\n  "result": [\n    {\n      "expressions": [\n        {\n          "value": [],\n          "text": "data.ed_cage.architecture.deny",\n          "location": {\n            "row": 1,\n            "col": 1\n          }\n        }\n      ]\n    }\n  ]\n}\n', 'stderr': '', 'resource': 'E:\\Repositories\\PythonProjects\\ED-CAGE\\configs\\cases\\architecture-catalogs\\spring-petclinic-microservices-service-architecture.yaml', 'findings': [], 'summary': {'policy_path': 'E:\\Repositories\\PythonProjects\\ED-CAGE\\configs\\policies\\architecture_catalog.rego', 'query': 'data.ed_cage.architecture.deny', 'finding_count': 0, 'execution_mode': 'local'}, 'metadata': {}} | None |
