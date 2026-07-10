# ED-CAGE Governance Report

## Run Information

- Run ID: `4cf97153-60e1-48a9-9020-436418822bea`
- Project: **online-boutique-runtime**
- Started at: `2026-07-08T15:36:45.681941+00:00`
- Finished at: `2026-07-08T15:36:49.846803+00:00`
- Overall result: **FAILED**
- Governance score: **16.67 / 100**
- Achieved score: `60.0`
- Max score: `360.0`
- Evaluated findings: `13`
- Skipped findings: `0`

## Governance Gate

- Gate result: **FAILED**
- Actual score: `16.67`
- Minimum score: `70.00`

### Gate Reason(s)

- Governance score 16.67 is below minimum score 70.00.

## Recommended Actions

| Rule ID | Priority | Type | Action | Recommendation |
|---|---|---|---|---|
| API-001 | medium | documentation | Add OpenAPI metadata | Define info.title and info.version in the OpenAPI document. |
| API-002 | medium | documentation | Add operationId to OpenAPI operations | Define operationId for every OpenAPI operation. |
| API-003 | medium | documentation | Add success responses to OpenAPI operations | Define at least one 2xx success response for every OpenAPI operation. |
| API-004 | medium | documentation | Add error responses to OpenAPI operations | Define 4xx or 5xx error responses for every OpenAPI operation. |
| API-005 | medium | documentation | Add request and response schemas | Define request and response schemas for OpenAPI operations where applicable. |
| API-006 | high | documentation | Define OpenAPI security scheme | Define securitySchemes and security requirements in the OpenAPI document. |
| SVC-003 | high | remediation | Expose a metrics endpoint | Expose a reachable metrics endpoint for the service. |
| OBS-001 | high | remediation | Expose Prometheus-compatible metrics | Expose metrics in Prometheus text exposition format. |
| OBS-002 | medium | remediation | Add request count metric | Expose a request count or throughput metric for the service. |
| OBS-003 | medium | remediation | Add request duration metric | Expose a request duration or latency metric for the service. |
| OBS-004 | medium | remediation | Add error or failure metric | Expose a metric that enables error or failure rate calculation. |
| SVC-002 | medium | documentation | Expose an OpenAPI specification | Expose a reachable OpenAPI or Swagger specification endpoint for the service. |

### ACTION-API-001-INFO-METADATA:API-001

- Rule ID: `API-001`
- Finding status: `failed`
- Severity: `medium`
- Priority: `medium`
- Action type: `documentation`
- Recommendation: Define info.title and info.version in the OpenAPI document.
- Implementation hint: Add the info object with title and version fields to the OpenAPI specification.
- Tags: `api, openapi, contract`

### ACTION-API-002-OPERATION-ID:API-002

- Rule ID: `API-002`
- Finding status: `failed`
- Severity: `medium`
- Priority: `medium`
- Action type: `documentation`
- Recommendation: Define operationId for every OpenAPI operation.
- Implementation hint: Add stable and unique operationId values such as getOrder, createPayment or listUsers.
- Tags: `api, openapi, client-generation`

### ACTION-API-003-SUCCESS-RESPONSES:API-003

- Rule ID: `API-003`
- Finding status: `failed`
- Severity: `medium`
- Priority: `medium`
- Action type: `documentation`
- Recommendation: Define at least one 2xx success response for every OpenAPI operation.
- Implementation hint: Add response codes such as 200, 201, 202 or 204 with descriptions and schemas where applicable.
- Tags: `api, openapi, responses`

### ACTION-API-004-ERROR-RESPONSES:API-004

- Rule ID: `API-004`
- Finding status: `failed`
- Severity: `medium`
- Priority: `medium`
- Action type: `documentation`
- Recommendation: Define 4xx or 5xx error responses for every OpenAPI operation.
- Implementation hint: Add response codes such as 400, 401, 403, 404 and 500 with standard error schema.
- Tags: `api, openapi, error-handling`

### ACTION-API-005-SCHEMAS:API-005

- Rule ID: `API-005`
- Finding status: `failed`
- Severity: `medium`
- Priority: `medium`
- Action type: `documentation`
- Recommendation: Define request and response schemas for OpenAPI operations where applicable.
- Implementation hint: Use components.schemas and reference them from requestBody and responses.content.*.schema.
- Tags: `api, openapi, schema`

### ACTION-API-006-SECURITY-SCHEME:API-006

- Rule ID: `API-006`
- Finding status: `failed`
- Severity: `high`
- Priority: `high`
- Action type: `documentation`
- Recommendation: Define securitySchemes and security requirements in the OpenAPI document.
- Implementation hint: Add components.securitySchemes and global or operation-level security requirements.
- Tags: `api, security, openapi`

### ACTION-SVC-003-METRICS-ENDPOINT:SVC-003

- Rule ID: `SVC-003`
- Finding status: `failed`
- Severity: `high`
- Priority: `high`
- Action type: `remediation`
- Recommendation: Expose a reachable metrics endpoint for the service.
- Implementation hint: Provide /metrics or /actuator/prometheus and return HTTP 200 with non-empty metrics content.
- Tags: `service, observability, metrics`

### ACTION-OBS-001-PROMETHEUS-COMPATIBILITY:OBS-001

- Rule ID: `OBS-001`
- Finding status: `failed`
- Severity: `high`
- Priority: `high`
- Action type: `remediation`
- Recommendation: Expose metrics in Prometheus text exposition format.
- Implementation hint: Use Micrometer Prometheus registry, OpenTelemetry Collector Prometheus exporter, or native Prometheus client libraries.
- Tags: `observability, prometheus, metrics`

### ACTION-OBS-002-REQUEST-COUNT-METRIC:OBS-002

- Rule ID: `OBS-002`
- Finding status: `failed`
- Severity: `medium`
- Priority: `medium`
- Action type: `remediation`
- Recommendation: Expose a request count or throughput metric for the service.
- Implementation hint: Provide a metric such as http_requests_total, http_server_requests_seconds_count or equivalent.
- Tags: `observability, throughput, metrics`

### ACTION-OBS-003-REQUEST-DURATION-METRIC:OBS-003

- Rule ID: `OBS-003`
- Finding status: `failed`
- Severity: `medium`
- Priority: `medium`
- Action type: `remediation`
- Recommendation: Expose a request duration or latency metric for the service.
- Implementation hint: Provide a metric such as http_request_duration_seconds, http_server_requests_seconds or equivalent.
- Tags: `observability, latency, performance`

### ACTION-OBS-004-ERROR-METRIC:OBS-004

- Rule ID: `OBS-004`
- Finding status: `failed`
- Severity: `medium`
- Priority: `medium`
- Action type: `remediation`
- Recommendation: Expose a metric that enables error or failure rate calculation.
- Implementation hint: Provide a metric such as errors_total or expose request count metrics with status/code labels that include 5xx responses.
- Tags: `observability, reliability, error-rate`

### ACTION-SVC-002-OPENAPI-SPEC:SVC-002

- Rule ID: `SVC-002`
- Finding status: `failed`
- Severity: `medium`
- Priority: `medium`
- Action type: `documentation`
- Recommendation: Expose a reachable OpenAPI or Swagger specification endpoint for the service.
- Implementation hint: Provide /openapi.json, /swagger.json or /v3/api-docs. The response should be valid JSON and include either an openapi or swagger version field.
- Tags: `service, api-governance, openapi`

## Status Summary

| Status | Count |
|---|---:|
| passed | 1 |
| failed | 12 |
| skipped | 0 |
| error | 0 |

## Severity Summary

| Severity | Count |
|---|---:|
| info | 0 |
| low | 0 |
| medium | 9 |
| high | 4 |
| critical | 0 |

## Findings

| Rule ID | Severity | Status | Message |
|---|---|---|---|
| API-001 | medium | failed | OpenAPI policy 'require_info_metadata' failed for service(s): frontend |
| API-002 | medium | failed | OpenAPI policy 'require_operation_id' failed for service(s): frontend |
| API-003 | medium | failed | OpenAPI policy 'require_success_responses' failed for service(s): frontend |
| API-004 | medium | failed | OpenAPI policy 'require_error_responses' failed for service(s): frontend |
| API-005 | medium | failed | OpenAPI policy 'require_operation_schemas' failed for service(s): frontend |
| API-006 | high | failed | OpenAPI policy 'require_security_scheme' failed for service(s): frontend |
| SVC-003 | high | failed | Metrics endpoint check failed for service(s): frontend |
| OBS-001 | high | failed | Prometheus metrics compatibility check failed for service(s): frontend |
| OBS-002 | medium | failed | Required Prometheus metric group check failed for service(s): frontend |
| OBS-003 | medium | failed | Required Prometheus metric group check failed for service(s): frontend |
| OBS-004 | medium | failed | Required Prometheus metric group check failed for service(s): frontend |
| SVC-001 | high | passed | All services expose at least one reachable health endpoint. |
| SVC-002 | medium | failed | OpenAPI specification check failed for service(s): frontend |

## Evidence Details

### API-001 — OpenAPI document must define API metadata

- Severity: `medium`
- Status: `failed`
- Category: `api`
- Target: `service`
- Check type: `openapi_document_policy`
- Message: OpenAPI policy 'require_info_metadata' failed for service(s): frontend

#### Raw Evidence

##### Raw Evidence 1

- Source: `frontend`
- Message: Service does not satisfy OpenAPI policy: require_info_metadata.

```json
{
  "service": "frontend",
  "base_url": "http://127.0.0.1:8080",
  "candidate_paths": [
    "/openapi.json",
    "/swagger.json"
  ],
  "expected_status_codes": [
    200
  ],
  "policy": "require_info_metadata",
  "attempts": [
    {
      "url": "http://127.0.0.1:8080/openapi.json",
      "status_code": 404,
      "expected_status_codes": [
        200
      ],
      "policy": "require_info_metadata",
      "success": false,
      "failure_reason": "unexpected_status_code"
    },
    {
      "url": "http://127.0.0.1:8080/swagger.json",
      "status_code": 404,
      "expected_status_codes": [
        200
      ],
      "policy": "require_info_metadata",
      "success": false,
      "failure_reason": "unexpected_status_code"
    }
  ]
}
```

#### Normalized Evidence

| Source Type | Source Name | Resource | Compliant | Observed | Expected |
|---|---|---|---|---|---|
| http | frontend | http://127.0.0.1:8080/openapi.json | False | 404 | [200] |
| http | frontend | http://127.0.0.1:8080/swagger.json | False | 404 | [200] |

### API-002 — OpenAPI operations must define operationId

- Severity: `medium`
- Status: `failed`
- Category: `api`
- Target: `service`
- Check type: `openapi_document_policy`
- Message: OpenAPI policy 'require_operation_id' failed for service(s): frontend

#### Raw Evidence

##### Raw Evidence 1

- Source: `frontend`
- Message: Service does not satisfy OpenAPI policy: require_operation_id.

```json
{
  "service": "frontend",
  "base_url": "http://127.0.0.1:8080",
  "candidate_paths": [
    "/openapi.json",
    "/swagger.json"
  ],
  "expected_status_codes": [
    200
  ],
  "policy": "require_operation_id",
  "attempts": [
    {
      "url": "http://127.0.0.1:8080/openapi.json",
      "status_code": 404,
      "expected_status_codes": [
        200
      ],
      "policy": "require_operation_id",
      "success": false,
      "failure_reason": "unexpected_status_code"
    },
    {
      "url": "http://127.0.0.1:8080/swagger.json",
      "status_code": 404,
      "expected_status_codes": [
        200
      ],
      "policy": "require_operation_id",
      "success": false,
      "failure_reason": "unexpected_status_code"
    }
  ]
}
```

#### Normalized Evidence

| Source Type | Source Name | Resource | Compliant | Observed | Expected |
|---|---|---|---|---|---|
| http | frontend | http://127.0.0.1:8080/openapi.json | False | 404 | [200] |
| http | frontend | http://127.0.0.1:8080/swagger.json | False | 404 | [200] |

### API-003 — OpenAPI operations must define success responses

- Severity: `medium`
- Status: `failed`
- Category: `api`
- Target: `service`
- Check type: `openapi_document_policy`
- Message: OpenAPI policy 'require_success_responses' failed for service(s): frontend

#### Raw Evidence

##### Raw Evidence 1

- Source: `frontend`
- Message: Service does not satisfy OpenAPI policy: require_success_responses.

```json
{
  "service": "frontend",
  "base_url": "http://127.0.0.1:8080",
  "candidate_paths": [
    "/openapi.json",
    "/swagger.json"
  ],
  "expected_status_codes": [
    200
  ],
  "policy": "require_success_responses",
  "attempts": [
    {
      "url": "http://127.0.0.1:8080/openapi.json",
      "status_code": 404,
      "expected_status_codes": [
        200
      ],
      "policy": "require_success_responses",
      "success": false,
      "failure_reason": "unexpected_status_code"
    },
    {
      "url": "http://127.0.0.1:8080/swagger.json",
      "status_code": 404,
      "expected_status_codes": [
        200
      ],
      "policy": "require_success_responses",
      "success": false,
      "failure_reason": "unexpected_status_code"
    }
  ]
}
```

#### Normalized Evidence

| Source Type | Source Name | Resource | Compliant | Observed | Expected |
|---|---|---|---|---|---|
| http | frontend | http://127.0.0.1:8080/openapi.json | False | 404 | [200] |
| http | frontend | http://127.0.0.1:8080/swagger.json | False | 404 | [200] |

### API-004 — OpenAPI operations must define error responses

- Severity: `medium`
- Status: `failed`
- Category: `api`
- Target: `service`
- Check type: `openapi_document_policy`
- Message: OpenAPI policy 'require_error_responses' failed for service(s): frontend

#### Raw Evidence

##### Raw Evidence 1

- Source: `frontend`
- Message: Service does not satisfy OpenAPI policy: require_error_responses.

```json
{
  "service": "frontend",
  "base_url": "http://127.0.0.1:8080",
  "candidate_paths": [
    "/openapi.json",
    "/swagger.json"
  ],
  "expected_status_codes": [
    200
  ],
  "policy": "require_error_responses",
  "attempts": [
    {
      "url": "http://127.0.0.1:8080/openapi.json",
      "status_code": 404,
      "expected_status_codes": [
        200
      ],
      "policy": "require_error_responses",
      "success": false,
      "failure_reason": "unexpected_status_code"
    },
    {
      "url": "http://127.0.0.1:8080/swagger.json",
      "status_code": 404,
      "expected_status_codes": [
        200
      ],
      "policy": "require_error_responses",
      "success": false,
      "failure_reason": "unexpected_status_code"
    }
  ]
}
```

#### Normalized Evidence

| Source Type | Source Name | Resource | Compliant | Observed | Expected |
|---|---|---|---|---|---|
| http | frontend | http://127.0.0.1:8080/openapi.json | False | 404 | [200] |
| http | frontend | http://127.0.0.1:8080/swagger.json | False | 404 | [200] |

### API-005 — OpenAPI operations should define request and response schemas

- Severity: `medium`
- Status: `failed`
- Category: `api`
- Target: `service`
- Check type: `openapi_document_policy`
- Message: OpenAPI policy 'require_operation_schemas' failed for service(s): frontend

#### Raw Evidence

##### Raw Evidence 1

- Source: `frontend`
- Message: Service does not satisfy OpenAPI policy: require_operation_schemas.

```json
{
  "service": "frontend",
  "base_url": "http://127.0.0.1:8080",
  "candidate_paths": [
    "/openapi.json",
    "/swagger.json"
  ],
  "expected_status_codes": [
    200
  ],
  "policy": "require_operation_schemas",
  "attempts": [
    {
      "url": "http://127.0.0.1:8080/openapi.json",
      "status_code": 404,
      "expected_status_codes": [
        200
      ],
      "policy": "require_operation_schemas",
      "success": false,
      "failure_reason": "unexpected_status_code"
    },
    {
      "url": "http://127.0.0.1:8080/swagger.json",
      "status_code": 404,
      "expected_status_codes": [
        200
      ],
      "policy": "require_operation_schemas",
      "success": false,
      "failure_reason": "unexpected_status_code"
    }
  ]
}
```

#### Normalized Evidence

| Source Type | Source Name | Resource | Compliant | Observed | Expected |
|---|---|---|---|---|---|
| http | frontend | http://127.0.0.1:8080/openapi.json | False | 404 | [200] |
| http | frontend | http://127.0.0.1:8080/swagger.json | False | 404 | [200] |

### API-006 — API security scheme should be defined

- Severity: `high`
- Status: `failed`
- Category: `api`
- Target: `service`
- Check type: `openapi_document_policy`
- Message: OpenAPI policy 'require_security_scheme' failed for service(s): frontend

#### Raw Evidence

##### Raw Evidence 1

- Source: `frontend`
- Message: Service does not satisfy OpenAPI policy: require_security_scheme.

```json
{
  "service": "frontend",
  "base_url": "http://127.0.0.1:8080",
  "candidate_paths": [
    "/openapi.json",
    "/swagger.json"
  ],
  "expected_status_codes": [
    200
  ],
  "policy": "require_security_scheme",
  "attempts": [
    {
      "url": "http://127.0.0.1:8080/openapi.json",
      "status_code": 404,
      "expected_status_codes": [
        200
      ],
      "policy": "require_security_scheme",
      "success": false,
      "failure_reason": "unexpected_status_code"
    },
    {
      "url": "http://127.0.0.1:8080/swagger.json",
      "status_code": 404,
      "expected_status_codes": [
        200
      ],
      "policy": "require_security_scheme",
      "success": false,
      "failure_reason": "unexpected_status_code"
    }
  ]
}
```

#### Normalized Evidence

| Source Type | Source Name | Resource | Compliant | Observed | Expected |
|---|---|---|---|---|---|
| http | frontend | http://127.0.0.1:8080/openapi.json | False | 404 | [200] |
| http | frontend | http://127.0.0.1:8080/swagger.json | False | 404 | [200] |

### SVC-003 — Services must expose a metrics endpoint

- Severity: `high`
- Status: `failed`
- Category: `observability`
- Target: `service`
- Check type: `metrics_endpoint`
- Message: Metrics endpoint check failed for service(s): frontend

#### Raw Evidence

##### Raw Evidence 1

- Source: `frontend`
- Message: Service does not expose a reachable metrics endpoint.

```json
{
  "service": "frontend",
  "base_url": "http://127.0.0.1:8080",
  "candidate_paths": [
    "/metrics"
  ],
  "expected_status_codes": [
    200
  ],
  "attempts": [
    {
      "url": "http://127.0.0.1:8080/metrics",
      "status_code": 404,
      "expected_status_codes": [
        200
      ],
      "success": false,
      "failure_reason": "unexpected_status_code"
    }
  ]
}
```

#### Normalized Evidence

| Source Type | Source Name | Resource | Compliant | Observed | Expected |
|---|---|---|---|---|---|
| http | frontend | http://127.0.0.1:8080/metrics | False | 404 | [200] |

### OBS-001 — Metrics endpoint must be Prometheus-compatible

- Severity: `high`
- Status: `failed`
- Category: `observability`
- Target: `service`
- Check type: `prometheus_metrics_compatibility`
- Message: Prometheus metrics compatibility check failed for service(s): frontend

#### Raw Evidence

##### Raw Evidence 1

- Source: `frontend`
- Message: Service does not expose Prometheus-compatible metrics.

```json
{
  "service": "frontend",
  "base_url": "http://127.0.0.1:8080",
  "candidate_paths": [
    "/metrics"
  ],
  "expected_status_codes": [
    200
  ],
  "attempts": [
    {
      "url": "http://127.0.0.1:8080/metrics",
      "status_code": 404,
      "expected_status_codes": [
        200
      ],
      "success": false,
      "failure_reason": "unexpected_status_code"
    }
  ]
}
```

#### Normalized Evidence

| Source Type | Source Name | Resource | Compliant | Observed | Expected |
|---|---|---|---|---|---|
| http | frontend | http://127.0.0.1:8080/metrics | False | 404 | [200] |

### OBS-002 — Metrics must include request count metric

- Severity: `medium`
- Status: `failed`
- Category: `observability`
- Target: `service`
- Check type: `required_prometheus_metric_groups`
- Message: Required Prometheus metric group check failed for service(s): frontend

#### Raw Evidence

##### Raw Evidence 1

- Source: `frontend`
- Message: Service does not expose required Prometheus metric group(s).

```json
{
  "service": "frontend",
  "base_url": "http://127.0.0.1:8080",
  "candidate_paths": [
    "/metrics"
  ],
  "expected_status_codes": [
    200
  ],
  "required_metric_groups": {
    "request_count": {
      "description": "Metric representing request count or throughput.",
      "patterns": [
        "^http_server_requests_seconds_count$",
        "^http_requests_total$",
        "^http_request_total$",
        "^requests_total$",
        "^grpc_server_handled_total$"
      ]
    }
  },
  "attempts": [
    {
      "url": "http://127.0.0.1:8080/metrics",
      "status_code": 404,
      "expected_status_codes": [
        200
      ],
      "success": false,
      "failure_reason": "unexpected_status_code"
    }
  ]
}
```

#### Normalized Evidence

| Source Type | Source Name | Resource | Compliant | Observed | Expected |
|---|---|---|---|---|---|
| http | frontend | http://127.0.0.1:8080/metrics | False | 404 | [200] |

### OBS-003 — Metrics must include request duration metric

- Severity: `medium`
- Status: `failed`
- Category: `observability`
- Target: `service`
- Check type: `required_prometheus_metric_groups`
- Message: Required Prometheus metric group check failed for service(s): frontend

#### Raw Evidence

##### Raw Evidence 1

- Source: `frontend`
- Message: Service does not expose required Prometheus metric group(s).

```json
{
  "service": "frontend",
  "base_url": "http://127.0.0.1:8080",
  "candidate_paths": [
    "/metrics"
  ],
  "expected_status_codes": [
    200
  ],
  "required_metric_groups": {
    "request_duration": {
      "description": "Metric representing request duration or latency.",
      "patterns": [
        "^http_server_requests_seconds$",
        "^http_server_requests_seconds_sum$",
        "^http_request_duration_seconds$",
        "^http_request_duration_seconds_sum$",
        "^request_duration_seconds$"
      ]
    }
  },
  "attempts": [
    {
      "url": "http://127.0.0.1:8080/metrics",
      "status_code": 404,
      "expected_status_codes": [
        200
      ],
      "success": false,
      "failure_reason": "unexpected_status_code"
    }
  ]
}
```

#### Normalized Evidence

| Source Type | Source Name | Resource | Compliant | Observed | Expected |
|---|---|---|---|---|---|
| http | frontend | http://127.0.0.1:8080/metrics | False | 404 | [200] |

### OBS-004 — Metrics must include error or failure metric

- Severity: `medium`
- Status: `failed`
- Category: `observability`
- Target: `service`
- Check type: `required_prometheus_metric_groups`
- Message: Required Prometheus metric group check failed for service(s): frontend

#### Raw Evidence

##### Raw Evidence 1

- Source: `frontend`
- Message: Service does not expose required Prometheus metric group(s).

```json
{
  "service": "frontend",
  "base_url": "http://127.0.0.1:8080",
  "candidate_paths": [
    "/metrics"
  ],
  "expected_status_codes": [
    200
  ],
  "required_metric_groups": {
    "error_metric": {
      "description": "Metric representing error or failure count.",
      "patterns": [
        "^http_server_requests_seconds_count$",
        "^http_requests_total$",
        "^errors_total$",
        "^request_errors_total$",
        "^failures_total$"
      ]
    }
  },
  "attempts": [
    {
      "url": "http://127.0.0.1:8080/metrics",
      "status_code": 404,
      "expected_status_codes": [
        200
      ],
      "success": false,
      "failure_reason": "unexpected_status_code"
    }
  ]
}
```

#### Normalized Evidence

| Source Type | Source Name | Resource | Compliant | Observed | Expected |
|---|---|---|---|---|---|
| http | frontend | http://127.0.0.1:8080/metrics | False | 404 | [200] |

### SVC-001 — Services must expose a health endpoint

- Severity: `high`
- Status: `passed`
- Category: `service`
- Target: `service`
- Check type: `http_health_endpoint`
- Message: All services expose at least one reachable health endpoint.

#### Raw Evidence

##### Raw Evidence 1

- Source: `frontend`
- Message: Service has a reachable health endpoint.

```json
{
  "service": "frontend",
  "base_url": "http://127.0.0.1:8080",
  "candidate_paths": [
    "/_healthz",
    "/health"
  ],
  "expected_status_codes": [
    200,
    204
  ],
  "attempts": [
    {
      "url": "http://127.0.0.1:8080/_healthz",
      "status_code": 200,
      "expected_status_codes": [
        200,
        204
      ],
      "success": true
    }
  ]
}
```

#### Normalized Evidence

| Source Type | Source Name | Resource | Compliant | Observed | Expected |
|---|---|---|---|---|---|
| http | frontend | http://127.0.0.1:8080/_healthz | True | 200 | [200, 204] |

### SVC-002 — Services must expose an OpenAPI specification

- Severity: `medium`
- Status: `failed`
- Category: `service`
- Target: `service`
- Check type: `openapi_spec`
- Message: OpenAPI specification check failed for service(s): frontend

#### Raw Evidence

##### Raw Evidence 1

- Source: `frontend`
- Message: Service does not expose a valid OpenAPI specification.

```json
{
  "service": "frontend",
  "base_url": "http://127.0.0.1:8080",
  "candidate_paths": [
    "/openapi.json",
    "/swagger.json"
  ],
  "expected_status_codes": [
    200
  ],
  "attempts": [
    {
      "url": "http://127.0.0.1:8080/openapi.json",
      "status_code": 404,
      "expected_status_codes": [
        200
      ],
      "success": false,
      "failure_reason": "unexpected_status_code"
    },
    {
      "url": "http://127.0.0.1:8080/swagger.json",
      "status_code": 404,
      "expected_status_codes": [
        200
      ],
      "success": false,
      "failure_reason": "unexpected_status_code"
    }
  ]
}
```

#### Normalized Evidence

| Source Type | Source Name | Resource | Compliant | Observed | Expected |
|---|---|---|---|---|---|
| http | frontend | http://127.0.0.1:8080/openapi.json | False | 404 | [200] |
| http | frontend | http://127.0.0.1:8080/swagger.json | False | 404 | [200] |
