# ED-CAGE Governance Report

## Run Information

- Run ID: `1b3c8ae1-cc59-46de-a9d4-76a4b9a43f99`
- Project: **train-ticket-runtime**
- Started at: `2026-07-09T09:04:20.657635+00:00`
- Finished at: `2026-07-09T09:04:25.338305+00:00`
- Overall result: **FAILED**
- Governance score: **37.04 / 100**
- Achieved score: `133.34`
- Max score: `360.0`
- Evaluated findings: `13`
- Skipped findings: `0`

## Governance Gate

- Gate result: **FAILED**
- Actual score: `37.04`
- Minimum score: `65.00`

### Gate Reason(s)

- Governance score 37.04 is below minimum score 65.00.

## Recommended Actions

| Rule ID | Priority | Type | Action | Recommendation |
|---|---|---|---|---|
| API-005 | medium | documentation | Add request and response schemas | Define request and response schemas for OpenAPI operations where applicable. |
| API-006 | high | documentation | Define OpenAPI security scheme | Define securitySchemes and security requirements in the OpenAPI document. |
| SVC-003 | high | remediation | Expose a metrics endpoint | Expose a reachable metrics endpoint for the service. |
| OBS-001 | high | remediation | Expose Prometheus-compatible metrics | Expose metrics in Prometheus text exposition format. |
| OBS-002 | medium | remediation | Add request count metric | Expose a request count or throughput metric for the service. |
| OBS-003 | medium | remediation | Add request duration metric | Expose a request duration or latency metric for the service. |
| OBS-004 | medium | remediation | Add error or failure metric | Expose a metric that enables error or failure rate calculation. |
| SVC-001 | high | remediation | Add a reachable health endpoint | Expose at least one reachable health, readiness or liveness endpoint for the service. |

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

### ACTION-SVC-001-HEALTH-ENDPOINT:SVC-001

- Rule ID: `SVC-001`
- Finding status: `failed`
- Severity: `high`
- Priority: `high`
- Action type: `remediation`
- Recommendation: Expose at least one reachable health, readiness or liveness endpoint for the service.
- Implementation hint: Use /health, /ready, /live or /actuator/health. The endpoint should return HTTP 200 or 204 when the service is healthy.
- Tags: `service, healthcheck, runtime-governance`

## Status Summary

| Status | Count |
|---|---:|
| passed | 5 |
| failed | 8 |
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
| API-001 | medium | passed | All services satisfy OpenAPI policy: require_info_metadata. |
| API-002 | medium | passed | All services satisfy OpenAPI policy: require_operation_id. |
| API-003 | medium | passed | All services satisfy OpenAPI policy: require_success_responses. |
| API-004 | medium | passed | All services satisfy OpenAPI policy: require_error_responses. |
| API-005 | medium | failed | OpenAPI policy 'require_operation_schemas' failed for service(s): ts-travel-service, ts-order-service |
| API-006 | high | failed | OpenAPI policy 'require_security_scheme' failed for service(s): ts-travel-service, ts-order-service |
| SVC-003 | high | failed | Metrics endpoint check failed for service(s): ts-travel-service, ts-order-service |
| OBS-001 | high | failed | Prometheus metrics compatibility check failed for service(s): ts-travel-service, ts-order-service |
| OBS-002 | medium | failed | Required Prometheus metric group check failed for service(s): ts-travel-service, ts-order-service |
| OBS-003 | medium | failed | Required Prometheus metric group check failed for service(s): ts-travel-service, ts-order-service |
| OBS-004 | medium | failed | Required Prometheus metric group check failed for service(s): ts-travel-service, ts-order-service |
| SVC-001 | high | failed | Health endpoint check failed for service(s): ts-travel-service, ts-order-service |
| SVC-002 | medium | passed | All services expose a valid OpenAPI specification. |

## Evidence Details

### API-001 — OpenAPI document must define API metadata

- Severity: `medium`
- Status: `passed`
- Category: `api`
- Target: `service`
- Check type: `openapi_document_policy`
- Message: All services satisfy OpenAPI policy: require_info_metadata.

#### Raw Evidence

##### Raw Evidence 1

- Source: `ts-travel-service`
- Message: Service satisfies OpenAPI policy: require_info_metadata.

```json
{
  "service": "ts-travel-service",
  "base_url": "http://127.0.0.1:12346",
  "candidate_paths": [
    "/v2/api-docs",
    "/v3/api-docs",
    "/swagger.json",
    "/openapi.json"
  ],
  "expected_status_codes": [
    200
  ],
  "policy": "require_info_metadata",
  "attempts": [
    {
      "url": "http://127.0.0.1:12346/v2/api-docs",
      "status_code": 200,
      "expected_status_codes": [
        200
      ],
      "policy": "require_info_metadata",
      "success": true,
      "failure_reason": null,
      "operation_count": 24,
      "spec_version": "2.0"
    }
  ]
}
```

##### Raw Evidence 2

- Source: `ts-order-service`
- Message: Service satisfies OpenAPI policy: require_info_metadata.

```json
{
  "service": "ts-order-service",
  "base_url": "http://127.0.0.1:12031",
  "candidate_paths": [
    "/v2/api-docs",
    "/v3/api-docs",
    "/swagger.json",
    "/openapi.json"
  ],
  "expected_status_codes": [
    200
  ],
  "policy": "require_info_metadata",
  "attempts": [
    {
      "url": "http://127.0.0.1:12031/v2/api-docs",
      "status_code": 200,
      "expected_status_codes": [
        200
      ],
      "policy": "require_info_metadata",
      "success": true,
      "failure_reason": null,
      "operation_count": 27,
      "spec_version": "2.0"
    }
  ]
}
```

#### Normalized Evidence

| Source Type | Source Name | Resource | Compliant | Observed | Expected |
|---|---|---|---|---|---|
| http | ts-travel-service | http://127.0.0.1:12346/v2/api-docs | True | 200 | [200] |
| http | ts-order-service | http://127.0.0.1:12031/v2/api-docs | True | 200 | [200] |

### API-002 — OpenAPI operations must define operationId

- Severity: `medium`
- Status: `passed`
- Category: `api`
- Target: `service`
- Check type: `openapi_document_policy`
- Message: All services satisfy OpenAPI policy: require_operation_id.

#### Raw Evidence

##### Raw Evidence 1

- Source: `ts-travel-service`
- Message: Service satisfies OpenAPI policy: require_operation_id.

```json
{
  "service": "ts-travel-service",
  "base_url": "http://127.0.0.1:12346",
  "candidate_paths": [
    "/v2/api-docs",
    "/v3/api-docs",
    "/swagger.json",
    "/openapi.json"
  ],
  "expected_status_codes": [
    200
  ],
  "policy": "require_operation_id",
  "attempts": [
    {
      "url": "http://127.0.0.1:12346/v2/api-docs",
      "status_code": 200,
      "expected_status_codes": [
        200
      ],
      "policy": "require_operation_id",
      "success": true,
      "failure_reason": null,
      "missing_operations": [],
      "operation_count": 24,
      "spec_version": "2.0"
    }
  ]
}
```

##### Raw Evidence 2

- Source: `ts-order-service`
- Message: Service satisfies OpenAPI policy: require_operation_id.

```json
{
  "service": "ts-order-service",
  "base_url": "http://127.0.0.1:12031",
  "candidate_paths": [
    "/v2/api-docs",
    "/v3/api-docs",
    "/swagger.json",
    "/openapi.json"
  ],
  "expected_status_codes": [
    200
  ],
  "policy": "require_operation_id",
  "attempts": [
    {
      "url": "http://127.0.0.1:12031/v2/api-docs",
      "status_code": 200,
      "expected_status_codes": [
        200
      ],
      "policy": "require_operation_id",
      "success": true,
      "failure_reason": null,
      "missing_operations": [],
      "operation_count": 27,
      "spec_version": "2.0"
    }
  ]
}
```

#### Normalized Evidence

| Source Type | Source Name | Resource | Compliant | Observed | Expected |
|---|---|---|---|---|---|
| http | ts-travel-service | http://127.0.0.1:12346/v2/api-docs | True | 200 | [200] |
| http | ts-order-service | http://127.0.0.1:12031/v2/api-docs | True | 200 | [200] |

### API-003 — OpenAPI operations must define success responses

- Severity: `medium`
- Status: `passed`
- Category: `api`
- Target: `service`
- Check type: `openapi_document_policy`
- Message: All services satisfy OpenAPI policy: require_success_responses.

#### Raw Evidence

##### Raw Evidence 1

- Source: `ts-travel-service`
- Message: Service satisfies OpenAPI policy: require_success_responses.

```json
{
  "service": "ts-travel-service",
  "base_url": "http://127.0.0.1:12346",
  "candidate_paths": [
    "/v2/api-docs",
    "/v3/api-docs",
    "/swagger.json",
    "/openapi.json"
  ],
  "expected_status_codes": [
    200
  ],
  "policy": "require_success_responses",
  "attempts": [
    {
      "url": "http://127.0.0.1:12346/v2/api-docs",
      "status_code": 200,
      "expected_status_codes": [
        200
      ],
      "policy": "require_success_responses",
      "success": true,
      "failure_reason": null,
      "missing_operations": [],
      "operation_count": 24,
      "spec_version": "2.0"
    }
  ]
}
```

##### Raw Evidence 2

- Source: `ts-order-service`
- Message: Service satisfies OpenAPI policy: require_success_responses.

```json
{
  "service": "ts-order-service",
  "base_url": "http://127.0.0.1:12031",
  "candidate_paths": [
    "/v2/api-docs",
    "/v3/api-docs",
    "/swagger.json",
    "/openapi.json"
  ],
  "expected_status_codes": [
    200
  ],
  "policy": "require_success_responses",
  "attempts": [
    {
      "url": "http://127.0.0.1:12031/v2/api-docs",
      "status_code": 200,
      "expected_status_codes": [
        200
      ],
      "policy": "require_success_responses",
      "success": true,
      "failure_reason": null,
      "missing_operations": [],
      "operation_count": 27,
      "spec_version": "2.0"
    }
  ]
}
```

#### Normalized Evidence

| Source Type | Source Name | Resource | Compliant | Observed | Expected |
|---|---|---|---|---|---|
| http | ts-travel-service | http://127.0.0.1:12346/v2/api-docs | True | 200 | [200] |
| http | ts-order-service | http://127.0.0.1:12031/v2/api-docs | True | 200 | [200] |

### API-004 — OpenAPI operations must define error responses

- Severity: `medium`
- Status: `passed`
- Category: `api`
- Target: `service`
- Check type: `openapi_document_policy`
- Message: All services satisfy OpenAPI policy: require_error_responses.

#### Raw Evidence

##### Raw Evidence 1

- Source: `ts-travel-service`
- Message: Service satisfies OpenAPI policy: require_error_responses.

```json
{
  "service": "ts-travel-service",
  "base_url": "http://127.0.0.1:12346",
  "candidate_paths": [
    "/v2/api-docs",
    "/v3/api-docs",
    "/swagger.json",
    "/openapi.json"
  ],
  "expected_status_codes": [
    200
  ],
  "policy": "require_error_responses",
  "attempts": [
    {
      "url": "http://127.0.0.1:12346/v2/api-docs",
      "status_code": 200,
      "expected_status_codes": [
        200
      ],
      "policy": "require_error_responses",
      "success": true,
      "failure_reason": null,
      "missing_operations": [],
      "operation_count": 24,
      "spec_version": "2.0"
    }
  ]
}
```

##### Raw Evidence 2

- Source: `ts-order-service`
- Message: Service satisfies OpenAPI policy: require_error_responses.

```json
{
  "service": "ts-order-service",
  "base_url": "http://127.0.0.1:12031",
  "candidate_paths": [
    "/v2/api-docs",
    "/v3/api-docs",
    "/swagger.json",
    "/openapi.json"
  ],
  "expected_status_codes": [
    200
  ],
  "policy": "require_error_responses",
  "attempts": [
    {
      "url": "http://127.0.0.1:12031/v2/api-docs",
      "status_code": 200,
      "expected_status_codes": [
        200
      ],
      "policy": "require_error_responses",
      "success": true,
      "failure_reason": null,
      "missing_operations": [],
      "operation_count": 27,
      "spec_version": "2.0"
    }
  ]
}
```

#### Normalized Evidence

| Source Type | Source Name | Resource | Compliant | Observed | Expected |
|---|---|---|---|---|---|
| http | ts-travel-service | http://127.0.0.1:12346/v2/api-docs | True | 200 | [200] |
| http | ts-order-service | http://127.0.0.1:12031/v2/api-docs | True | 200 | [200] |

### API-005 — OpenAPI operations should define request and response schemas

- Severity: `medium`
- Status: `failed`
- Category: `api`
- Target: `service`
- Check type: `openapi_document_policy`
- Message: OpenAPI policy 'require_operation_schemas' failed for service(s): ts-travel-service, ts-order-service

#### Raw Evidence

##### Raw Evidence 1

- Source: `ts-travel-service`
- Message: Service does not satisfy OpenAPI policy: require_operation_schemas.

```json
{
  "service": "ts-travel-service",
  "base_url": "http://127.0.0.1:12346",
  "candidate_paths": [
    "/v2/api-docs",
    "/v3/api-docs",
    "/swagger.json",
    "/openapi.json"
  ],
  "expected_status_codes": [
    200
  ],
  "policy": "require_operation_schemas",
  "attempts": [
    {
      "url": "http://127.0.0.1:12346/v2/api-docs",
      "status_code": 200,
      "expected_status_codes": [
        200
      ],
      "policy": "require_operation_schemas",
      "success": false,
      "failure_reason": "missing_operation_schema",
      "missing_response_schema": [
        "GET /actuator",
        "GET /actuator/health",
        "GET /actuator/health/**",
        "GET /actuator/info",
        "GET /api/v1/travelservice/admin_trip",
        "GET /api/v1/travelservice/routes/{tripId}",
        "GET /api/v1/travelservice/train_types/{tripId}",
        "POST /api/v1/travelservice/trip_detail",
        "GET /api/v1/travelservice/trips",
        "POST /api/v1/travelservice/trips",
        "PUT /api/v1/travelservice/trips",
        "POST /api/v1/travelservice/trips/left",
        "POST /api/v1/travelservice/trips/left_parallel",
        "POST /api/v1/travelservice/trips/routes",
        "GET /api/v1/travelservice/trips/{tripId}",
        "DELETE /api/v1/travelservice/trips/{tripId}",
        "GET /api/v1/travelservice/welcome",
        "GET /error",
        "HEAD /error",
        "POST /error",
        "PUT /error",
        "DELETE /error",
        "OPTIONS /error",
        "PATCH /error"
      ],
      "missing_request_schema": [],
      "operation_count": 24,
      "spec_version": "2.0"
    },
    {
      "url": "http://127.0.0.1:12346/v3/api-docs",
      "status_code": 403,
      "expected_status_codes": [
        200
      ],
      "policy": "require_operation_schemas",
      "success": false,
      "failure_reason": "unexpected_status_code"
    },
    {
      "url": "http://127.0.0.1:12346/swagger.json",
      "status_code": 403,
      "expected_status_codes": [
        200
      ],
      "policy": "require_operation_schemas",
      "success": false,
      "failure_reason": "unexpected_status_code"
    },
    {
      "url": "http://127.0.0.1:12346/openapi.json",
      "status_code": 403,
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

##### Raw Evidence 2

- Source: `ts-order-service`
- Message: Service does not satisfy OpenAPI policy: require_operation_schemas.

```json
{
  "service": "ts-order-service",
  "base_url": "http://127.0.0.1:12031",
  "candidate_paths": [
    "/v2/api-docs",
    "/v3/api-docs",
    "/swagger.json",
    "/openapi.json"
  ],
  "expected_status_codes": [
    200
  ],
  "policy": "require_operation_schemas",
  "attempts": [
    {
      "url": "http://127.0.0.1:12031/v2/api-docs",
      "status_code": 200,
      "expected_status_codes": [
        200
      ],
      "policy": "require_operation_schemas",
      "success": false,
      "failure_reason": "missing_operation_schema",
      "missing_response_schema": [
        "GET /actuator",
        "GET /actuator/health",
        "GET /actuator/health/**",
        "GET /actuator/info",
        "GET /api/v1/orderservice/order",
        "POST /api/v1/orderservice/order",
        "PUT /api/v1/orderservice/order",
        "POST /api/v1/orderservice/order/admin",
        "PUT /api/v1/orderservice/order/admin",
        "GET /api/v1/orderservice/order/orderPay/{orderId}",
        "GET /api/v1/orderservice/order/price/{orderId}",
        "POST /api/v1/orderservice/order/query",
        "POST /api/v1/orderservice/order/refresh",
        "GET /api/v1/orderservice/order/security/{checkDate}/{accountId}",
        "GET /api/v1/orderservice/order/status/{orderId}/{status}",
        "POST /api/v1/orderservice/order/tickets",
        "GET /api/v1/orderservice/order/{orderId}",
        "DELETE /api/v1/orderservice/order/{orderId}",
        "GET /api/v1/orderservice/order/{travelDate}/{trainNumber}",
        "GET /api/v1/orderservice/welcome",
        "GET /error",
        "HEAD /error",
        "POST /error",
        "PUT /error",
        "DELETE /error",
        "OPTIONS /error",
        "PATCH /error"
      ],
      "missing_request_schema": [],
      "operation_count": 27,
      "spec_version": "2.0"
    },
    {
      "url": "http://127.0.0.1:12031/v3/api-docs",
      "status_code": 403,
      "expected_status_codes": [
        200
      ],
      "policy": "require_operation_schemas",
      "success": false,
      "failure_reason": "unexpected_status_code"
    },
    {
      "url": "http://127.0.0.1:12031/swagger.json",
      "status_code": 403,
      "expected_status_codes": [
        200
      ],
      "policy": "require_operation_schemas",
      "success": false,
      "failure_reason": "unexpected_status_code"
    },
    {
      "url": "http://127.0.0.1:12031/openapi.json",
      "status_code": 403,
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
| http | ts-travel-service | http://127.0.0.1:12346/v2/api-docs | False | 200 | [200] |
| http | ts-travel-service | http://127.0.0.1:12346/v3/api-docs | False | 403 | [200] |
| http | ts-travel-service | http://127.0.0.1:12346/swagger.json | False | 403 | [200] |
| http | ts-travel-service | http://127.0.0.1:12346/openapi.json | False | 403 | [200] |
| http | ts-order-service | http://127.0.0.1:12031/v2/api-docs | False | 200 | [200] |
| http | ts-order-service | http://127.0.0.1:12031/v3/api-docs | False | 403 | [200] |
| http | ts-order-service | http://127.0.0.1:12031/swagger.json | False | 403 | [200] |
| http | ts-order-service | http://127.0.0.1:12031/openapi.json | False | 403 | [200] |

### API-006 — API security scheme should be defined

- Severity: `high`
- Status: `failed`
- Category: `api`
- Target: `service`
- Check type: `openapi_document_policy`
- Message: OpenAPI policy 'require_security_scheme' failed for service(s): ts-travel-service, ts-order-service

#### Raw Evidence

##### Raw Evidence 1

- Source: `ts-travel-service`
- Message: Service does not satisfy OpenAPI policy: require_security_scheme.

```json
{
  "service": "ts-travel-service",
  "base_url": "http://127.0.0.1:12346",
  "candidate_paths": [
    "/v2/api-docs",
    "/v3/api-docs",
    "/swagger.json",
    "/openapi.json"
  ],
  "expected_status_codes": [
    200
  ],
  "policy": "require_security_scheme",
  "attempts": [
    {
      "url": "http://127.0.0.1:12346/v2/api-docs",
      "status_code": 200,
      "expected_status_codes": [
        200
      ],
      "policy": "require_security_scheme",
      "success": false,
      "failure_reason": "missing_security_scheme_or_requirement",
      "security_scheme_exists": false,
      "security_requirement_exists": false,
      "operation_count": 24,
      "spec_version": "2.0"
    },
    {
      "url": "http://127.0.0.1:12346/v3/api-docs",
      "status_code": 403,
      "expected_status_codes": [
        200
      ],
      "policy": "require_security_scheme",
      "success": false,
      "failure_reason": "unexpected_status_code"
    },
    {
      "url": "http://127.0.0.1:12346/swagger.json",
      "status_code": 403,
      "expected_status_codes": [
        200
      ],
      "policy": "require_security_scheme",
      "success": false,
      "failure_reason": "unexpected_status_code"
    },
    {
      "url": "http://127.0.0.1:12346/openapi.json",
      "status_code": 403,
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

##### Raw Evidence 2

- Source: `ts-order-service`
- Message: Service does not satisfy OpenAPI policy: require_security_scheme.

```json
{
  "service": "ts-order-service",
  "base_url": "http://127.0.0.1:12031",
  "candidate_paths": [
    "/v2/api-docs",
    "/v3/api-docs",
    "/swagger.json",
    "/openapi.json"
  ],
  "expected_status_codes": [
    200
  ],
  "policy": "require_security_scheme",
  "attempts": [
    {
      "url": "http://127.0.0.1:12031/v2/api-docs",
      "status_code": 200,
      "expected_status_codes": [
        200
      ],
      "policy": "require_security_scheme",
      "success": false,
      "failure_reason": "missing_security_scheme_or_requirement",
      "security_scheme_exists": false,
      "security_requirement_exists": false,
      "operation_count": 27,
      "spec_version": "2.0"
    },
    {
      "url": "http://127.0.0.1:12031/v3/api-docs",
      "status_code": 403,
      "expected_status_codes": [
        200
      ],
      "policy": "require_security_scheme",
      "success": false,
      "failure_reason": "unexpected_status_code"
    },
    {
      "url": "http://127.0.0.1:12031/swagger.json",
      "status_code": 403,
      "expected_status_codes": [
        200
      ],
      "policy": "require_security_scheme",
      "success": false,
      "failure_reason": "unexpected_status_code"
    },
    {
      "url": "http://127.0.0.1:12031/openapi.json",
      "status_code": 403,
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
| http | ts-travel-service | http://127.0.0.1:12346/v2/api-docs | False | 200 | [200] |
| http | ts-travel-service | http://127.0.0.1:12346/v3/api-docs | False | 403 | [200] |
| http | ts-travel-service | http://127.0.0.1:12346/swagger.json | False | 403 | [200] |
| http | ts-travel-service | http://127.0.0.1:12346/openapi.json | False | 403 | [200] |
| http | ts-order-service | http://127.0.0.1:12031/v2/api-docs | False | 200 | [200] |
| http | ts-order-service | http://127.0.0.1:12031/v3/api-docs | False | 403 | [200] |
| http | ts-order-service | http://127.0.0.1:12031/swagger.json | False | 403 | [200] |
| http | ts-order-service | http://127.0.0.1:12031/openapi.json | False | 403 | [200] |

### SVC-003 — Services must expose a metrics endpoint

- Severity: `high`
- Status: `failed`
- Category: `observability`
- Target: `service`
- Check type: `metrics_endpoint`
- Message: Metrics endpoint check failed for service(s): ts-travel-service, ts-order-service

#### Raw Evidence

##### Raw Evidence 1

- Source: `ts-travel-service`
- Message: Service does not expose a reachable metrics endpoint.

```json
{
  "service": "ts-travel-service",
  "base_url": "http://127.0.0.1:12346",
  "candidate_paths": [
    "/actuator/prometheus",
    "/actuator/metrics",
    "/metrics"
  ],
  "expected_status_codes": [
    200
  ],
  "attempts": [
    {
      "url": "http://127.0.0.1:12346/actuator/prometheus",
      "status_code": 403,
      "expected_status_codes": [
        200
      ],
      "success": false,
      "failure_reason": "unexpected_status_code"
    },
    {
      "url": "http://127.0.0.1:12346/actuator/metrics",
      "status_code": 403,
      "expected_status_codes": [
        200
      ],
      "success": false,
      "failure_reason": "unexpected_status_code"
    },
    {
      "url": "http://127.0.0.1:12346/metrics",
      "status_code": 403,
      "expected_status_codes": [
        200
      ],
      "success": false,
      "failure_reason": "unexpected_status_code"
    }
  ]
}
```

##### Raw Evidence 2

- Source: `ts-order-service`
- Message: Service does not expose a reachable metrics endpoint.

```json
{
  "service": "ts-order-service",
  "base_url": "http://127.0.0.1:12031",
  "candidate_paths": [
    "/actuator/prometheus",
    "/actuator/metrics",
    "/metrics"
  ],
  "expected_status_codes": [
    200
  ],
  "attempts": [
    {
      "url": "http://127.0.0.1:12031/actuator/prometheus",
      "status_code": 403,
      "expected_status_codes": [
        200
      ],
      "success": false,
      "failure_reason": "unexpected_status_code"
    },
    {
      "url": "http://127.0.0.1:12031/actuator/metrics",
      "status_code": 403,
      "expected_status_codes": [
        200
      ],
      "success": false,
      "failure_reason": "unexpected_status_code"
    },
    {
      "url": "http://127.0.0.1:12031/metrics",
      "status_code": 403,
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
| http | ts-travel-service | http://127.0.0.1:12346/actuator/prometheus | False | 403 | [200] |
| http | ts-travel-service | http://127.0.0.1:12346/actuator/metrics | False | 403 | [200] |
| http | ts-travel-service | http://127.0.0.1:12346/metrics | False | 403 | [200] |
| http | ts-order-service | http://127.0.0.1:12031/actuator/prometheus | False | 403 | [200] |
| http | ts-order-service | http://127.0.0.1:12031/actuator/metrics | False | 403 | [200] |
| http | ts-order-service | http://127.0.0.1:12031/metrics | False | 403 | [200] |

### OBS-001 — Metrics endpoint must be Prometheus-compatible

- Severity: `high`
- Status: `failed`
- Category: `observability`
- Target: `service`
- Check type: `prometheus_metrics_compatibility`
- Message: Prometheus metrics compatibility check failed for service(s): ts-travel-service, ts-order-service

#### Raw Evidence

##### Raw Evidence 1

- Source: `ts-travel-service`
- Message: Service does not expose Prometheus-compatible metrics.

```json
{
  "service": "ts-travel-service",
  "base_url": "http://127.0.0.1:12346",
  "candidate_paths": [
    "/actuator/prometheus",
    "/actuator/metrics",
    "/metrics"
  ],
  "expected_status_codes": [
    200
  ],
  "attempts": [
    {
      "url": "http://127.0.0.1:12346/actuator/prometheus",
      "status_code": 403,
      "expected_status_codes": [
        200
      ],
      "success": false,
      "failure_reason": "unexpected_status_code"
    },
    {
      "url": "http://127.0.0.1:12346/actuator/metrics",
      "status_code": 403,
      "expected_status_codes": [
        200
      ],
      "success": false,
      "failure_reason": "unexpected_status_code"
    },
    {
      "url": "http://127.0.0.1:12346/metrics",
      "status_code": 403,
      "expected_status_codes": [
        200
      ],
      "success": false,
      "failure_reason": "unexpected_status_code"
    }
  ]
}
```

##### Raw Evidence 2

- Source: `ts-order-service`
- Message: Service does not expose Prometheus-compatible metrics.

```json
{
  "service": "ts-order-service",
  "base_url": "http://127.0.0.1:12031",
  "candidate_paths": [
    "/actuator/prometheus",
    "/actuator/metrics",
    "/metrics"
  ],
  "expected_status_codes": [
    200
  ],
  "attempts": [
    {
      "url": "http://127.0.0.1:12031/actuator/prometheus",
      "status_code": 403,
      "expected_status_codes": [
        200
      ],
      "success": false,
      "failure_reason": "unexpected_status_code"
    },
    {
      "url": "http://127.0.0.1:12031/actuator/metrics",
      "status_code": 403,
      "expected_status_codes": [
        200
      ],
      "success": false,
      "failure_reason": "unexpected_status_code"
    },
    {
      "url": "http://127.0.0.1:12031/metrics",
      "status_code": 403,
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
| http | ts-travel-service | http://127.0.0.1:12346/actuator/prometheus | False | 403 | [200] |
| http | ts-travel-service | http://127.0.0.1:12346/actuator/metrics | False | 403 | [200] |
| http | ts-travel-service | http://127.0.0.1:12346/metrics | False | 403 | [200] |
| http | ts-order-service | http://127.0.0.1:12031/actuator/prometheus | False | 403 | [200] |
| http | ts-order-service | http://127.0.0.1:12031/actuator/metrics | False | 403 | [200] |
| http | ts-order-service | http://127.0.0.1:12031/metrics | False | 403 | [200] |

### OBS-002 — Metrics must include request count metric

- Severity: `medium`
- Status: `failed`
- Category: `observability`
- Target: `service`
- Check type: `required_prometheus_metric_groups`
- Message: Required Prometheus metric group check failed for service(s): ts-travel-service, ts-order-service

#### Raw Evidence

##### Raw Evidence 1

- Source: `ts-travel-service`
- Message: Service does not expose required Prometheus metric group(s).

```json
{
  "service": "ts-travel-service",
  "base_url": "http://127.0.0.1:12346",
  "candidate_paths": [
    "/actuator/prometheus",
    "/actuator/metrics",
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
      "url": "http://127.0.0.1:12346/actuator/prometheus",
      "status_code": 403,
      "expected_status_codes": [
        200
      ],
      "success": false,
      "failure_reason": "unexpected_status_code"
    },
    {
      "url": "http://127.0.0.1:12346/actuator/metrics",
      "status_code": 403,
      "expected_status_codes": [
        200
      ],
      "success": false,
      "failure_reason": "unexpected_status_code"
    },
    {
      "url": "http://127.0.0.1:12346/metrics",
      "status_code": 403,
      "expected_status_codes": [
        200
      ],
      "success": false,
      "failure_reason": "unexpected_status_code"
    }
  ]
}
```

##### Raw Evidence 2

- Source: `ts-order-service`
- Message: Service does not expose required Prometheus metric group(s).

```json
{
  "service": "ts-order-service",
  "base_url": "http://127.0.0.1:12031",
  "candidate_paths": [
    "/actuator/prometheus",
    "/actuator/metrics",
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
      "url": "http://127.0.0.1:12031/actuator/prometheus",
      "status_code": 403,
      "expected_status_codes": [
        200
      ],
      "success": false,
      "failure_reason": "unexpected_status_code"
    },
    {
      "url": "http://127.0.0.1:12031/actuator/metrics",
      "status_code": 403,
      "expected_status_codes": [
        200
      ],
      "success": false,
      "failure_reason": "unexpected_status_code"
    },
    {
      "url": "http://127.0.0.1:12031/metrics",
      "status_code": 403,
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
| http | ts-travel-service | http://127.0.0.1:12346/actuator/prometheus | False | 403 | [200] |
| http | ts-travel-service | http://127.0.0.1:12346/actuator/metrics | False | 403 | [200] |
| http | ts-travel-service | http://127.0.0.1:12346/metrics | False | 403 | [200] |
| http | ts-order-service | http://127.0.0.1:12031/actuator/prometheus | False | 403 | [200] |
| http | ts-order-service | http://127.0.0.1:12031/actuator/metrics | False | 403 | [200] |
| http | ts-order-service | http://127.0.0.1:12031/metrics | False | 403 | [200] |

### OBS-003 — Metrics must include request duration metric

- Severity: `medium`
- Status: `failed`
- Category: `observability`
- Target: `service`
- Check type: `required_prometheus_metric_groups`
- Message: Required Prometheus metric group check failed for service(s): ts-travel-service, ts-order-service

#### Raw Evidence

##### Raw Evidence 1

- Source: `ts-travel-service`
- Message: Service does not expose required Prometheus metric group(s).

```json
{
  "service": "ts-travel-service",
  "base_url": "http://127.0.0.1:12346",
  "candidate_paths": [
    "/actuator/prometheus",
    "/actuator/metrics",
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
      "url": "http://127.0.0.1:12346/actuator/prometheus",
      "status_code": 403,
      "expected_status_codes": [
        200
      ],
      "success": false,
      "failure_reason": "unexpected_status_code"
    },
    {
      "url": "http://127.0.0.1:12346/actuator/metrics",
      "status_code": 403,
      "expected_status_codes": [
        200
      ],
      "success": false,
      "failure_reason": "unexpected_status_code"
    },
    {
      "url": "http://127.0.0.1:12346/metrics",
      "status_code": 403,
      "expected_status_codes": [
        200
      ],
      "success": false,
      "failure_reason": "unexpected_status_code"
    }
  ]
}
```

##### Raw Evidence 2

- Source: `ts-order-service`
- Message: Service does not expose required Prometheus metric group(s).

```json
{
  "service": "ts-order-service",
  "base_url": "http://127.0.0.1:12031",
  "candidate_paths": [
    "/actuator/prometheus",
    "/actuator/metrics",
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
      "url": "http://127.0.0.1:12031/actuator/prometheus",
      "status_code": 403,
      "expected_status_codes": [
        200
      ],
      "success": false,
      "failure_reason": "unexpected_status_code"
    },
    {
      "url": "http://127.0.0.1:12031/actuator/metrics",
      "status_code": 403,
      "expected_status_codes": [
        200
      ],
      "success": false,
      "failure_reason": "unexpected_status_code"
    },
    {
      "url": "http://127.0.0.1:12031/metrics",
      "status_code": 403,
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
| http | ts-travel-service | http://127.0.0.1:12346/actuator/prometheus | False | 403 | [200] |
| http | ts-travel-service | http://127.0.0.1:12346/actuator/metrics | False | 403 | [200] |
| http | ts-travel-service | http://127.0.0.1:12346/metrics | False | 403 | [200] |
| http | ts-order-service | http://127.0.0.1:12031/actuator/prometheus | False | 403 | [200] |
| http | ts-order-service | http://127.0.0.1:12031/actuator/metrics | False | 403 | [200] |
| http | ts-order-service | http://127.0.0.1:12031/metrics | False | 403 | [200] |

### OBS-004 — Metrics must include error or failure metric

- Severity: `medium`
- Status: `failed`
- Category: `observability`
- Target: `service`
- Check type: `required_prometheus_metric_groups`
- Message: Required Prometheus metric group check failed for service(s): ts-travel-service, ts-order-service

#### Raw Evidence

##### Raw Evidence 1

- Source: `ts-travel-service`
- Message: Service does not expose required Prometheus metric group(s).

```json
{
  "service": "ts-travel-service",
  "base_url": "http://127.0.0.1:12346",
  "candidate_paths": [
    "/actuator/prometheus",
    "/actuator/metrics",
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
      "url": "http://127.0.0.1:12346/actuator/prometheus",
      "status_code": 403,
      "expected_status_codes": [
        200
      ],
      "success": false,
      "failure_reason": "unexpected_status_code"
    },
    {
      "url": "http://127.0.0.1:12346/actuator/metrics",
      "status_code": 403,
      "expected_status_codes": [
        200
      ],
      "success": false,
      "failure_reason": "unexpected_status_code"
    },
    {
      "url": "http://127.0.0.1:12346/metrics",
      "status_code": 403,
      "expected_status_codes": [
        200
      ],
      "success": false,
      "failure_reason": "unexpected_status_code"
    }
  ]
}
```

##### Raw Evidence 2

- Source: `ts-order-service`
- Message: Service does not expose required Prometheus metric group(s).

```json
{
  "service": "ts-order-service",
  "base_url": "http://127.0.0.1:12031",
  "candidate_paths": [
    "/actuator/prometheus",
    "/actuator/metrics",
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
      "url": "http://127.0.0.1:12031/actuator/prometheus",
      "status_code": 403,
      "expected_status_codes": [
        200
      ],
      "success": false,
      "failure_reason": "unexpected_status_code"
    },
    {
      "url": "http://127.0.0.1:12031/actuator/metrics",
      "status_code": 403,
      "expected_status_codes": [
        200
      ],
      "success": false,
      "failure_reason": "unexpected_status_code"
    },
    {
      "url": "http://127.0.0.1:12031/metrics",
      "status_code": 403,
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
| http | ts-travel-service | http://127.0.0.1:12346/actuator/prometheus | False | 403 | [200] |
| http | ts-travel-service | http://127.0.0.1:12346/actuator/metrics | False | 403 | [200] |
| http | ts-travel-service | http://127.0.0.1:12346/metrics | False | 403 | [200] |
| http | ts-order-service | http://127.0.0.1:12031/actuator/prometheus | False | 403 | [200] |
| http | ts-order-service | http://127.0.0.1:12031/actuator/metrics | False | 403 | [200] |
| http | ts-order-service | http://127.0.0.1:12031/metrics | False | 403 | [200] |

### SVC-001 — Services must expose a health endpoint

- Severity: `high`
- Status: `failed`
- Category: `service`
- Target: `service`
- Check type: `http_health_endpoint`
- Message: Health endpoint check failed for service(s): ts-travel-service, ts-order-service

#### Raw Evidence

##### Raw Evidence 1

- Source: `ts-travel-service`
- Message: Service does not have a reachable health endpoint.

```json
{
  "service": "ts-travel-service",
  "base_url": "http://127.0.0.1:12346",
  "candidate_paths": [
    "/actuator/health",
    "/health"
  ],
  "expected_status_codes": [
    200,
    204
  ],
  "attempts": [
    {
      "url": "http://127.0.0.1:12346/actuator/health",
      "status_code": 403,
      "expected_status_codes": [
        200,
        204
      ],
      "success": false
    },
    {
      "url": "http://127.0.0.1:12346/health",
      "status_code": 403,
      "expected_status_codes": [
        200,
        204
      ],
      "success": false
    }
  ]
}
```

##### Raw Evidence 2

- Source: `ts-order-service`
- Message: Service does not have a reachable health endpoint.

```json
{
  "service": "ts-order-service",
  "base_url": "http://127.0.0.1:12031",
  "candidate_paths": [
    "/actuator/health",
    "/health"
  ],
  "expected_status_codes": [
    200,
    204
  ],
  "attempts": [
    {
      "url": "http://127.0.0.1:12031/actuator/health",
      "status_code": 403,
      "expected_status_codes": [
        200,
        204
      ],
      "success": false
    },
    {
      "url": "http://127.0.0.1:12031/health",
      "status_code": 403,
      "expected_status_codes": [
        200,
        204
      ],
      "success": false
    }
  ]
}
```

#### Normalized Evidence

| Source Type | Source Name | Resource | Compliant | Observed | Expected |
|---|---|---|---|---|---|
| http | ts-travel-service | http://127.0.0.1:12346/actuator/health | False | 403 | [200, 204] |
| http | ts-travel-service | http://127.0.0.1:12346/health | False | 403 | [200, 204] |
| http | ts-order-service | http://127.0.0.1:12031/actuator/health | False | 403 | [200, 204] |
| http | ts-order-service | http://127.0.0.1:12031/health | False | 403 | [200, 204] |

### SVC-002 — Services must expose an OpenAPI specification

- Severity: `medium`
- Status: `passed`
- Category: `service`
- Target: `service`
- Check type: `openapi_spec`
- Message: All services expose a valid OpenAPI specification.

#### Raw Evidence

##### Raw Evidence 1

- Source: `ts-travel-service`
- Message: Service exposes a valid OpenAPI specification.

```json
{
  "service": "ts-travel-service",
  "base_url": "http://127.0.0.1:12346",
  "candidate_paths": [
    "/v2/api-docs",
    "/v3/api-docs",
    "/swagger.json",
    "/openapi.json"
  ],
  "expected_status_codes": [
    200
  ],
  "attempts": [
    {
      "url": "http://127.0.0.1:12346/v2/api-docs",
      "status_code": 200,
      "expected_status_codes": [
        200
      ],
      "success": true,
      "failure_reason": null,
      "spec_version": "2.0",
      "title": "Api Documentation",
      "path_count": 15
    }
  ]
}
```

##### Raw Evidence 2

- Source: `ts-order-service`
- Message: Service exposes a valid OpenAPI specification.

```json
{
  "service": "ts-order-service",
  "base_url": "http://127.0.0.1:12031",
  "candidate_paths": [
    "/v2/api-docs",
    "/v3/api-docs",
    "/swagger.json",
    "/openapi.json"
  ],
  "expected_status_codes": [
    200
  ],
  "attempts": [
    {
      "url": "http://127.0.0.1:12031/v2/api-docs",
      "status_code": 200,
      "expected_status_codes": [
        200
      ],
      "success": true,
      "failure_reason": null,
      "spec_version": "2.0",
      "title": "Api Documentation",
      "path_count": 17
    }
  ]
}
```

#### Normalized Evidence

| Source Type | Source Name | Resource | Compliant | Observed | Expected |
|---|---|---|---|---|---|
| http | ts-travel-service | http://127.0.0.1:12346/v2/api-docs | True | 200 | [200] |
| http | ts-order-service | http://127.0.0.1:12031/v2/api-docs | True | 200 | [200] |
