# ED-CAGE Governance Report

## Run Information

- Run ID: `0bf0839b-bf51-43e7-a53c-aa02b65fa6cf`
- Project: **spring-petclinic-microservices-runtime**
- Started at: `2026-07-08T13:25:53.967234+00:00`
- Finished at: `2026-07-08T13:25:59.516579+00:00`
- Overall result: **FAILED**
- Governance score: **52.78 / 100**
- Achieved score: `190.0`
- Max score: `360.0`
- Evaluated findings: `13`
- Skipped findings: `0`

## Governance Gate

- Gate result: **FAILED**
- Actual score: `52.78`
- Minimum score: `70.00`

### Gate Reason(s)

- Governance score 52.78 is below minimum score 70.00.

## Recommended Actions

| Rule ID | Priority | Type | Action | Recommendation |
|---|---|---|---|---|
| API-001 | medium | documentation | Add OpenAPI metadata | Define info.title and info.version in the OpenAPI document. |
| API-002 | medium | documentation | Add operationId to OpenAPI operations | Define operationId for every OpenAPI operation. |
| API-003 | medium | documentation | Add success responses to OpenAPI operations | Define at least one 2xx success response for every OpenAPI operation. |
| API-004 | medium | documentation | Add error responses to OpenAPI operations | Define 4xx or 5xx error responses for every OpenAPI operation. |
| API-005 | medium | documentation | Add request and response schemas | Define request and response schemas for OpenAPI operations where applicable. |
| API-006 | high | documentation | Define OpenAPI security scheme | Define securitySchemes and security requirements in the OpenAPI document. |
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
| passed | 6 |
| failed | 7 |
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
| API-001 | medium | failed | OpenAPI policy 'require_info_metadata' failed for service(s): api-gateway, customers-service, visits-service, vets-service |
| API-002 | medium | failed | OpenAPI policy 'require_operation_id' failed for service(s): api-gateway, customers-service, visits-service, vets-service |
| API-003 | medium | failed | OpenAPI policy 'require_success_responses' failed for service(s): api-gateway, customers-service, visits-service, vets-service |
| API-004 | medium | failed | OpenAPI policy 'require_error_responses' failed for service(s): api-gateway, customers-service, visits-service, vets-service |
| API-005 | medium | failed | OpenAPI policy 'require_operation_schemas' failed for service(s): api-gateway, customers-service, visits-service, vets-service |
| API-006 | high | failed | OpenAPI policy 'require_security_scheme' failed for service(s): api-gateway, customers-service, visits-service, vets-service |
| SVC-003 | high | passed | All services expose a reachable metrics endpoint. |
| OBS-001 | high | passed | All services expose Prometheus-compatible metrics. |
| OBS-002 | medium | passed | All services expose required Prometheus metric group(s). |
| OBS-003 | medium | passed | All services expose required Prometheus metric group(s). |
| OBS-004 | medium | passed | All services expose required Prometheus metric group(s). |
| SVC-001 | high | passed | All services expose at least one reachable health endpoint. |
| SVC-002 | medium | failed | OpenAPI specification check failed for service(s): api-gateway, customers-service, visits-service, vets-service |

## Evidence Details

### API-001 — OpenAPI document must define API metadata

- Severity: `medium`
- Status: `failed`
- Category: `api`
- Target: `service`
- Check type: `openapi_document_policy`
- Message: OpenAPI policy 'require_info_metadata' failed for service(s): api-gateway, customers-service, visits-service, vets-service

#### Raw Evidence

##### Raw Evidence 1

- Source: `api-gateway`
- Message: Service does not satisfy OpenAPI policy: require_info_metadata.

```json
{
  "service": "api-gateway",
  "base_url": "http://127.0.0.1:8080",
  "candidate_paths": [
    "/v3/api-docs",
    "/openapi.json"
  ],
  "expected_status_codes": [
    200
  ],
  "policy": "require_info_metadata",
  "attempts": [
    {
      "url": "http://127.0.0.1:8080/v3/api-docs",
      "status_code": 404,
      "expected_status_codes": [
        200
      ],
      "policy": "require_info_metadata",
      "success": false,
      "failure_reason": "unexpected_status_code"
    },
    {
      "url": "http://127.0.0.1:8080/openapi.json",
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

##### Raw Evidence 2

- Source: `customers-service`
- Message: Service does not satisfy OpenAPI policy: require_info_metadata.

```json
{
  "service": "customers-service",
  "base_url": "http://127.0.0.1:8081",
  "candidate_paths": [
    "/v3/api-docs",
    "/openapi.json"
  ],
  "expected_status_codes": [
    200
  ],
  "policy": "require_info_metadata",
  "attempts": [
    {
      "url": "http://127.0.0.1:8081/v3/api-docs",
      "status_code": 404,
      "expected_status_codes": [
        200
      ],
      "policy": "require_info_metadata",
      "success": false,
      "failure_reason": "unexpected_status_code"
    },
    {
      "url": "http://127.0.0.1:8081/openapi.json",
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

##### Raw Evidence 3

- Source: `visits-service`
- Message: Service does not satisfy OpenAPI policy: require_info_metadata.

```json
{
  "service": "visits-service",
  "base_url": "http://127.0.0.1:8082",
  "candidate_paths": [
    "/v3/api-docs",
    "/openapi.json"
  ],
  "expected_status_codes": [
    200
  ],
  "policy": "require_info_metadata",
  "attempts": [
    {
      "url": "http://127.0.0.1:8082/v3/api-docs",
      "status_code": 404,
      "expected_status_codes": [
        200
      ],
      "policy": "require_info_metadata",
      "success": false,
      "failure_reason": "unexpected_status_code"
    },
    {
      "url": "http://127.0.0.1:8082/openapi.json",
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

##### Raw Evidence 4

- Source: `vets-service`
- Message: Service does not satisfy OpenAPI policy: require_info_metadata.

```json
{
  "service": "vets-service",
  "base_url": "http://127.0.0.1:8083",
  "candidate_paths": [
    "/v3/api-docs",
    "/openapi.json"
  ],
  "expected_status_codes": [
    200
  ],
  "policy": "require_info_metadata",
  "attempts": [
    {
      "url": "http://127.0.0.1:8083/v3/api-docs",
      "status_code": 404,
      "expected_status_codes": [
        200
      ],
      "policy": "require_info_metadata",
      "success": false,
      "failure_reason": "unexpected_status_code"
    },
    {
      "url": "http://127.0.0.1:8083/openapi.json",
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
| http | api-gateway | http://127.0.0.1:8080/v3/api-docs | False | 404 | [200] |
| http | api-gateway | http://127.0.0.1:8080/openapi.json | False | 404 | [200] |
| http | customers-service | http://127.0.0.1:8081/v3/api-docs | False | 404 | [200] |
| http | customers-service | http://127.0.0.1:8081/openapi.json | False | 404 | [200] |
| http | visits-service | http://127.0.0.1:8082/v3/api-docs | False | 404 | [200] |
| http | visits-service | http://127.0.0.1:8082/openapi.json | False | 404 | [200] |
| http | vets-service | http://127.0.0.1:8083/v3/api-docs | False | 404 | [200] |
| http | vets-service | http://127.0.0.1:8083/openapi.json | False | 404 | [200] |

### API-002 — OpenAPI operations must define operationId

- Severity: `medium`
- Status: `failed`
- Category: `api`
- Target: `service`
- Check type: `openapi_document_policy`
- Message: OpenAPI policy 'require_operation_id' failed for service(s): api-gateway, customers-service, visits-service, vets-service

#### Raw Evidence

##### Raw Evidence 1

- Source: `api-gateway`
- Message: Service does not satisfy OpenAPI policy: require_operation_id.

```json
{
  "service": "api-gateway",
  "base_url": "http://127.0.0.1:8080",
  "candidate_paths": [
    "/v3/api-docs",
    "/openapi.json"
  ],
  "expected_status_codes": [
    200
  ],
  "policy": "require_operation_id",
  "attempts": [
    {
      "url": "http://127.0.0.1:8080/v3/api-docs",
      "status_code": 404,
      "expected_status_codes": [
        200
      ],
      "policy": "require_operation_id",
      "success": false,
      "failure_reason": "unexpected_status_code"
    },
    {
      "url": "http://127.0.0.1:8080/openapi.json",
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

##### Raw Evidence 2

- Source: `customers-service`
- Message: Service does not satisfy OpenAPI policy: require_operation_id.

```json
{
  "service": "customers-service",
  "base_url": "http://127.0.0.1:8081",
  "candidate_paths": [
    "/v3/api-docs",
    "/openapi.json"
  ],
  "expected_status_codes": [
    200
  ],
  "policy": "require_operation_id",
  "attempts": [
    {
      "url": "http://127.0.0.1:8081/v3/api-docs",
      "status_code": 404,
      "expected_status_codes": [
        200
      ],
      "policy": "require_operation_id",
      "success": false,
      "failure_reason": "unexpected_status_code"
    },
    {
      "url": "http://127.0.0.1:8081/openapi.json",
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

##### Raw Evidence 3

- Source: `visits-service`
- Message: Service does not satisfy OpenAPI policy: require_operation_id.

```json
{
  "service": "visits-service",
  "base_url": "http://127.0.0.1:8082",
  "candidate_paths": [
    "/v3/api-docs",
    "/openapi.json"
  ],
  "expected_status_codes": [
    200
  ],
  "policy": "require_operation_id",
  "attempts": [
    {
      "url": "http://127.0.0.1:8082/v3/api-docs",
      "status_code": 404,
      "expected_status_codes": [
        200
      ],
      "policy": "require_operation_id",
      "success": false,
      "failure_reason": "unexpected_status_code"
    },
    {
      "url": "http://127.0.0.1:8082/openapi.json",
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

##### Raw Evidence 4

- Source: `vets-service`
- Message: Service does not satisfy OpenAPI policy: require_operation_id.

```json
{
  "service": "vets-service",
  "base_url": "http://127.0.0.1:8083",
  "candidate_paths": [
    "/v3/api-docs",
    "/openapi.json"
  ],
  "expected_status_codes": [
    200
  ],
  "policy": "require_operation_id",
  "attempts": [
    {
      "url": "http://127.0.0.1:8083/v3/api-docs",
      "status_code": 404,
      "expected_status_codes": [
        200
      ],
      "policy": "require_operation_id",
      "success": false,
      "failure_reason": "unexpected_status_code"
    },
    {
      "url": "http://127.0.0.1:8083/openapi.json",
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
| http | api-gateway | http://127.0.0.1:8080/v3/api-docs | False | 404 | [200] |
| http | api-gateway | http://127.0.0.1:8080/openapi.json | False | 404 | [200] |
| http | customers-service | http://127.0.0.1:8081/v3/api-docs | False | 404 | [200] |
| http | customers-service | http://127.0.0.1:8081/openapi.json | False | 404 | [200] |
| http | visits-service | http://127.0.0.1:8082/v3/api-docs | False | 404 | [200] |
| http | visits-service | http://127.0.0.1:8082/openapi.json | False | 404 | [200] |
| http | vets-service | http://127.0.0.1:8083/v3/api-docs | False | 404 | [200] |
| http | vets-service | http://127.0.0.1:8083/openapi.json | False | 404 | [200] |

### API-003 — OpenAPI operations must define success responses

- Severity: `medium`
- Status: `failed`
- Category: `api`
- Target: `service`
- Check type: `openapi_document_policy`
- Message: OpenAPI policy 'require_success_responses' failed for service(s): api-gateway, customers-service, visits-service, vets-service

#### Raw Evidence

##### Raw Evidence 1

- Source: `api-gateway`
- Message: Service does not satisfy OpenAPI policy: require_success_responses.

```json
{
  "service": "api-gateway",
  "base_url": "http://127.0.0.1:8080",
  "candidate_paths": [
    "/v3/api-docs",
    "/openapi.json"
  ],
  "expected_status_codes": [
    200
  ],
  "policy": "require_success_responses",
  "attempts": [
    {
      "url": "http://127.0.0.1:8080/v3/api-docs",
      "status_code": 404,
      "expected_status_codes": [
        200
      ],
      "policy": "require_success_responses",
      "success": false,
      "failure_reason": "unexpected_status_code"
    },
    {
      "url": "http://127.0.0.1:8080/openapi.json",
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

##### Raw Evidence 2

- Source: `customers-service`
- Message: Service does not satisfy OpenAPI policy: require_success_responses.

```json
{
  "service": "customers-service",
  "base_url": "http://127.0.0.1:8081",
  "candidate_paths": [
    "/v3/api-docs",
    "/openapi.json"
  ],
  "expected_status_codes": [
    200
  ],
  "policy": "require_success_responses",
  "attempts": [
    {
      "url": "http://127.0.0.1:8081/v3/api-docs",
      "status_code": 404,
      "expected_status_codes": [
        200
      ],
      "policy": "require_success_responses",
      "success": false,
      "failure_reason": "unexpected_status_code"
    },
    {
      "url": "http://127.0.0.1:8081/openapi.json",
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

##### Raw Evidence 3

- Source: `visits-service`
- Message: Service does not satisfy OpenAPI policy: require_success_responses.

```json
{
  "service": "visits-service",
  "base_url": "http://127.0.0.1:8082",
  "candidate_paths": [
    "/v3/api-docs",
    "/openapi.json"
  ],
  "expected_status_codes": [
    200
  ],
  "policy": "require_success_responses",
  "attempts": [
    {
      "url": "http://127.0.0.1:8082/v3/api-docs",
      "status_code": 404,
      "expected_status_codes": [
        200
      ],
      "policy": "require_success_responses",
      "success": false,
      "failure_reason": "unexpected_status_code"
    },
    {
      "url": "http://127.0.0.1:8082/openapi.json",
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

##### Raw Evidence 4

- Source: `vets-service`
- Message: Service does not satisfy OpenAPI policy: require_success_responses.

```json
{
  "service": "vets-service",
  "base_url": "http://127.0.0.1:8083",
  "candidate_paths": [
    "/v3/api-docs",
    "/openapi.json"
  ],
  "expected_status_codes": [
    200
  ],
  "policy": "require_success_responses",
  "attempts": [
    {
      "url": "http://127.0.0.1:8083/v3/api-docs",
      "status_code": 404,
      "expected_status_codes": [
        200
      ],
      "policy": "require_success_responses",
      "success": false,
      "failure_reason": "unexpected_status_code"
    },
    {
      "url": "http://127.0.0.1:8083/openapi.json",
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
| http | api-gateway | http://127.0.0.1:8080/v3/api-docs | False | 404 | [200] |
| http | api-gateway | http://127.0.0.1:8080/openapi.json | False | 404 | [200] |
| http | customers-service | http://127.0.0.1:8081/v3/api-docs | False | 404 | [200] |
| http | customers-service | http://127.0.0.1:8081/openapi.json | False | 404 | [200] |
| http | visits-service | http://127.0.0.1:8082/v3/api-docs | False | 404 | [200] |
| http | visits-service | http://127.0.0.1:8082/openapi.json | False | 404 | [200] |
| http | vets-service | http://127.0.0.1:8083/v3/api-docs | False | 404 | [200] |
| http | vets-service | http://127.0.0.1:8083/openapi.json | False | 404 | [200] |

### API-004 — OpenAPI operations must define error responses

- Severity: `medium`
- Status: `failed`
- Category: `api`
- Target: `service`
- Check type: `openapi_document_policy`
- Message: OpenAPI policy 'require_error_responses' failed for service(s): api-gateway, customers-service, visits-service, vets-service

#### Raw Evidence

##### Raw Evidence 1

- Source: `api-gateway`
- Message: Service does not satisfy OpenAPI policy: require_error_responses.

```json
{
  "service": "api-gateway",
  "base_url": "http://127.0.0.1:8080",
  "candidate_paths": [
    "/v3/api-docs",
    "/openapi.json"
  ],
  "expected_status_codes": [
    200
  ],
  "policy": "require_error_responses",
  "attempts": [
    {
      "url": "http://127.0.0.1:8080/v3/api-docs",
      "status_code": 404,
      "expected_status_codes": [
        200
      ],
      "policy": "require_error_responses",
      "success": false,
      "failure_reason": "unexpected_status_code"
    },
    {
      "url": "http://127.0.0.1:8080/openapi.json",
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

##### Raw Evidence 2

- Source: `customers-service`
- Message: Service does not satisfy OpenAPI policy: require_error_responses.

```json
{
  "service": "customers-service",
  "base_url": "http://127.0.0.1:8081",
  "candidate_paths": [
    "/v3/api-docs",
    "/openapi.json"
  ],
  "expected_status_codes": [
    200
  ],
  "policy": "require_error_responses",
  "attempts": [
    {
      "url": "http://127.0.0.1:8081/v3/api-docs",
      "status_code": 404,
      "expected_status_codes": [
        200
      ],
      "policy": "require_error_responses",
      "success": false,
      "failure_reason": "unexpected_status_code"
    },
    {
      "url": "http://127.0.0.1:8081/openapi.json",
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

##### Raw Evidence 3

- Source: `visits-service`
- Message: Service does not satisfy OpenAPI policy: require_error_responses.

```json
{
  "service": "visits-service",
  "base_url": "http://127.0.0.1:8082",
  "candidate_paths": [
    "/v3/api-docs",
    "/openapi.json"
  ],
  "expected_status_codes": [
    200
  ],
  "policy": "require_error_responses",
  "attempts": [
    {
      "url": "http://127.0.0.1:8082/v3/api-docs",
      "status_code": 404,
      "expected_status_codes": [
        200
      ],
      "policy": "require_error_responses",
      "success": false,
      "failure_reason": "unexpected_status_code"
    },
    {
      "url": "http://127.0.0.1:8082/openapi.json",
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

##### Raw Evidence 4

- Source: `vets-service`
- Message: Service does not satisfy OpenAPI policy: require_error_responses.

```json
{
  "service": "vets-service",
  "base_url": "http://127.0.0.1:8083",
  "candidate_paths": [
    "/v3/api-docs",
    "/openapi.json"
  ],
  "expected_status_codes": [
    200
  ],
  "policy": "require_error_responses",
  "attempts": [
    {
      "url": "http://127.0.0.1:8083/v3/api-docs",
      "status_code": 404,
      "expected_status_codes": [
        200
      ],
      "policy": "require_error_responses",
      "success": false,
      "failure_reason": "unexpected_status_code"
    },
    {
      "url": "http://127.0.0.1:8083/openapi.json",
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
| http | api-gateway | http://127.0.0.1:8080/v3/api-docs | False | 404 | [200] |
| http | api-gateway | http://127.0.0.1:8080/openapi.json | False | 404 | [200] |
| http | customers-service | http://127.0.0.1:8081/v3/api-docs | False | 404 | [200] |
| http | customers-service | http://127.0.0.1:8081/openapi.json | False | 404 | [200] |
| http | visits-service | http://127.0.0.1:8082/v3/api-docs | False | 404 | [200] |
| http | visits-service | http://127.0.0.1:8082/openapi.json | False | 404 | [200] |
| http | vets-service | http://127.0.0.1:8083/v3/api-docs | False | 404 | [200] |
| http | vets-service | http://127.0.0.1:8083/openapi.json | False | 404 | [200] |

### API-005 — OpenAPI operations should define request and response schemas

- Severity: `medium`
- Status: `failed`
- Category: `api`
- Target: `service`
- Check type: `openapi_document_policy`
- Message: OpenAPI policy 'require_operation_schemas' failed for service(s): api-gateway, customers-service, visits-service, vets-service

#### Raw Evidence

##### Raw Evidence 1

- Source: `api-gateway`
- Message: Service does not satisfy OpenAPI policy: require_operation_schemas.

```json
{
  "service": "api-gateway",
  "base_url": "http://127.0.0.1:8080",
  "candidate_paths": [
    "/v3/api-docs",
    "/openapi.json"
  ],
  "expected_status_codes": [
    200
  ],
  "policy": "require_operation_schemas",
  "attempts": [
    {
      "url": "http://127.0.0.1:8080/v3/api-docs",
      "status_code": 404,
      "expected_status_codes": [
        200
      ],
      "policy": "require_operation_schemas",
      "success": false,
      "failure_reason": "unexpected_status_code"
    },
    {
      "url": "http://127.0.0.1:8080/openapi.json",
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

##### Raw Evidence 2

- Source: `customers-service`
- Message: Service does not satisfy OpenAPI policy: require_operation_schemas.

```json
{
  "service": "customers-service",
  "base_url": "http://127.0.0.1:8081",
  "candidate_paths": [
    "/v3/api-docs",
    "/openapi.json"
  ],
  "expected_status_codes": [
    200
  ],
  "policy": "require_operation_schemas",
  "attempts": [
    {
      "url": "http://127.0.0.1:8081/v3/api-docs",
      "status_code": 404,
      "expected_status_codes": [
        200
      ],
      "policy": "require_operation_schemas",
      "success": false,
      "failure_reason": "unexpected_status_code"
    },
    {
      "url": "http://127.0.0.1:8081/openapi.json",
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

##### Raw Evidence 3

- Source: `visits-service`
- Message: Service does not satisfy OpenAPI policy: require_operation_schemas.

```json
{
  "service": "visits-service",
  "base_url": "http://127.0.0.1:8082",
  "candidate_paths": [
    "/v3/api-docs",
    "/openapi.json"
  ],
  "expected_status_codes": [
    200
  ],
  "policy": "require_operation_schemas",
  "attempts": [
    {
      "url": "http://127.0.0.1:8082/v3/api-docs",
      "status_code": 404,
      "expected_status_codes": [
        200
      ],
      "policy": "require_operation_schemas",
      "success": false,
      "failure_reason": "unexpected_status_code"
    },
    {
      "url": "http://127.0.0.1:8082/openapi.json",
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

##### Raw Evidence 4

- Source: `vets-service`
- Message: Service does not satisfy OpenAPI policy: require_operation_schemas.

```json
{
  "service": "vets-service",
  "base_url": "http://127.0.0.1:8083",
  "candidate_paths": [
    "/v3/api-docs",
    "/openapi.json"
  ],
  "expected_status_codes": [
    200
  ],
  "policy": "require_operation_schemas",
  "attempts": [
    {
      "url": "http://127.0.0.1:8083/v3/api-docs",
      "status_code": 404,
      "expected_status_codes": [
        200
      ],
      "policy": "require_operation_schemas",
      "success": false,
      "failure_reason": "unexpected_status_code"
    },
    {
      "url": "http://127.0.0.1:8083/openapi.json",
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
| http | api-gateway | http://127.0.0.1:8080/v3/api-docs | False | 404 | [200] |
| http | api-gateway | http://127.0.0.1:8080/openapi.json | False | 404 | [200] |
| http | customers-service | http://127.0.0.1:8081/v3/api-docs | False | 404 | [200] |
| http | customers-service | http://127.0.0.1:8081/openapi.json | False | 404 | [200] |
| http | visits-service | http://127.0.0.1:8082/v3/api-docs | False | 404 | [200] |
| http | visits-service | http://127.0.0.1:8082/openapi.json | False | 404 | [200] |
| http | vets-service | http://127.0.0.1:8083/v3/api-docs | False | 404 | [200] |
| http | vets-service | http://127.0.0.1:8083/openapi.json | False | 404 | [200] |

### API-006 — API security scheme should be defined

- Severity: `high`
- Status: `failed`
- Category: `api`
- Target: `service`
- Check type: `openapi_document_policy`
- Message: OpenAPI policy 'require_security_scheme' failed for service(s): api-gateway, customers-service, visits-service, vets-service

#### Raw Evidence

##### Raw Evidence 1

- Source: `api-gateway`
- Message: Service does not satisfy OpenAPI policy: require_security_scheme.

```json
{
  "service": "api-gateway",
  "base_url": "http://127.0.0.1:8080",
  "candidate_paths": [
    "/v3/api-docs",
    "/openapi.json"
  ],
  "expected_status_codes": [
    200
  ],
  "policy": "require_security_scheme",
  "attempts": [
    {
      "url": "http://127.0.0.1:8080/v3/api-docs",
      "status_code": 404,
      "expected_status_codes": [
        200
      ],
      "policy": "require_security_scheme",
      "success": false,
      "failure_reason": "unexpected_status_code"
    },
    {
      "url": "http://127.0.0.1:8080/openapi.json",
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

##### Raw Evidence 2

- Source: `customers-service`
- Message: Service does not satisfy OpenAPI policy: require_security_scheme.

```json
{
  "service": "customers-service",
  "base_url": "http://127.0.0.1:8081",
  "candidate_paths": [
    "/v3/api-docs",
    "/openapi.json"
  ],
  "expected_status_codes": [
    200
  ],
  "policy": "require_security_scheme",
  "attempts": [
    {
      "url": "http://127.0.0.1:8081/v3/api-docs",
      "status_code": 404,
      "expected_status_codes": [
        200
      ],
      "policy": "require_security_scheme",
      "success": false,
      "failure_reason": "unexpected_status_code"
    },
    {
      "url": "http://127.0.0.1:8081/openapi.json",
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

##### Raw Evidence 3

- Source: `visits-service`
- Message: Service does not satisfy OpenAPI policy: require_security_scheme.

```json
{
  "service": "visits-service",
  "base_url": "http://127.0.0.1:8082",
  "candidate_paths": [
    "/v3/api-docs",
    "/openapi.json"
  ],
  "expected_status_codes": [
    200
  ],
  "policy": "require_security_scheme",
  "attempts": [
    {
      "url": "http://127.0.0.1:8082/v3/api-docs",
      "status_code": 404,
      "expected_status_codes": [
        200
      ],
      "policy": "require_security_scheme",
      "success": false,
      "failure_reason": "unexpected_status_code"
    },
    {
      "url": "http://127.0.0.1:8082/openapi.json",
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

##### Raw Evidence 4

- Source: `vets-service`
- Message: Service does not satisfy OpenAPI policy: require_security_scheme.

```json
{
  "service": "vets-service",
  "base_url": "http://127.0.0.1:8083",
  "candidate_paths": [
    "/v3/api-docs",
    "/openapi.json"
  ],
  "expected_status_codes": [
    200
  ],
  "policy": "require_security_scheme",
  "attempts": [
    {
      "url": "http://127.0.0.1:8083/v3/api-docs",
      "status_code": 404,
      "expected_status_codes": [
        200
      ],
      "policy": "require_security_scheme",
      "success": false,
      "failure_reason": "unexpected_status_code"
    },
    {
      "url": "http://127.0.0.1:8083/openapi.json",
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
| http | api-gateway | http://127.0.0.1:8080/v3/api-docs | False | 404 | [200] |
| http | api-gateway | http://127.0.0.1:8080/openapi.json | False | 404 | [200] |
| http | customers-service | http://127.0.0.1:8081/v3/api-docs | False | 404 | [200] |
| http | customers-service | http://127.0.0.1:8081/openapi.json | False | 404 | [200] |
| http | visits-service | http://127.0.0.1:8082/v3/api-docs | False | 404 | [200] |
| http | visits-service | http://127.0.0.1:8082/openapi.json | False | 404 | [200] |
| http | vets-service | http://127.0.0.1:8083/v3/api-docs | False | 404 | [200] |
| http | vets-service | http://127.0.0.1:8083/openapi.json | False | 404 | [200] |

### SVC-003 — Services must expose a metrics endpoint

- Severity: `high`
- Status: `passed`
- Category: `observability`
- Target: `service`
- Check type: `metrics_endpoint`
- Message: All services expose a reachable metrics endpoint.

#### Raw Evidence

##### Raw Evidence 1

- Source: `api-gateway`
- Message: Service exposes a reachable metrics endpoint.

```json
{
  "service": "api-gateway",
  "base_url": "http://127.0.0.1:8080",
  "candidate_paths": [
    "/actuator/prometheus",
    "/metrics"
  ],
  "expected_status_codes": [
    200
  ],
  "attempts": [
    {
      "url": "http://127.0.0.1:8080/actuator/prometheus",
      "status_code": 200,
      "expected_status_codes": [
        200
      ],
      "success": true,
      "failure_reason": null,
      "response_size_bytes": 14070
    }
  ]
}
```

##### Raw Evidence 2

- Source: `customers-service`
- Message: Service exposes a reachable metrics endpoint.

```json
{
  "service": "customers-service",
  "base_url": "http://127.0.0.1:8081",
  "candidate_paths": [
    "/actuator/prometheus",
    "/metrics"
  ],
  "expected_status_codes": [
    200
  ],
  "attempts": [
    {
      "url": "http://127.0.0.1:8081/actuator/prometheus",
      "status_code": 200,
      "expected_status_codes": [
        200
      ],
      "success": true,
      "failure_reason": null,
      "response_size_bytes": 26314
    }
  ]
}
```

##### Raw Evidence 3

- Source: `visits-service`
- Message: Service exposes a reachable metrics endpoint.

```json
{
  "service": "visits-service",
  "base_url": "http://127.0.0.1:8082",
  "candidate_paths": [
    "/actuator/prometheus",
    "/metrics"
  ],
  "expected_status_codes": [
    200
  ],
  "attempts": [
    {
      "url": "http://127.0.0.1:8082/actuator/prometheus",
      "status_code": 200,
      "expected_status_codes": [
        200
      ],
      "success": true,
      "failure_reason": null,
      "response_size_bytes": 25898
    }
  ]
}
```

##### Raw Evidence 4

- Source: `vets-service`
- Message: Service exposes a reachable metrics endpoint.

```json
{
  "service": "vets-service",
  "base_url": "http://127.0.0.1:8083",
  "candidate_paths": [
    "/actuator/prometheus",
    "/metrics"
  ],
  "expected_status_codes": [
    200
  ],
  "attempts": [
    {
      "url": "http://127.0.0.1:8083/actuator/prometheus",
      "status_code": 200,
      "expected_status_codes": [
        200
      ],
      "success": true,
      "failure_reason": null,
      "response_size_bytes": 22119
    }
  ]
}
```

#### Normalized Evidence

| Source Type | Source Name | Resource | Compliant | Observed | Expected |
|---|---|---|---|---|---|
| http | api-gateway | http://127.0.0.1:8080/actuator/prometheus | True | 200 | [200] |
| http | customers-service | http://127.0.0.1:8081/actuator/prometheus | True | 200 | [200] |
| http | visits-service | http://127.0.0.1:8082/actuator/prometheus | True | 200 | [200] |
| http | vets-service | http://127.0.0.1:8083/actuator/prometheus | True | 200 | [200] |

### OBS-001 — Metrics endpoint must be Prometheus-compatible

- Severity: `high`
- Status: `passed`
- Category: `observability`
- Target: `service`
- Check type: `prometheus_metrics_compatibility`
- Message: All services expose Prometheus-compatible metrics.

#### Raw Evidence

##### Raw Evidence 1

- Source: `api-gateway`
- Message: Service exposes Prometheus-compatible metrics.

```json
{
  "service": "api-gateway",
  "base_url": "http://127.0.0.1:8080",
  "candidate_paths": [
    "/actuator/prometheus",
    "/metrics"
  ],
  "expected_status_codes": [
    200
  ],
  "attempts": [
    {
      "url": "http://127.0.0.1:8080/actuator/prometheus",
      "status_code": 200,
      "expected_status_codes": [
        200
      ],
      "success": true,
      "failure_reason": null,
      "metric_count": 42,
      "metric_names_sample": [
        "application_ready_time_seconds",
        "application_started_time_seconds",
        "executor_active_threads",
        "executor_completed_tasks_total",
        "executor_pool_core_threads",
        "executor_pool_size_threads",
        "executor_queued_tasks",
        "http_server_requests_active_seconds_count",
        "http_server_requests_active_seconds_max",
        "http_server_requests_active_seconds_sum",
        "http_server_requests_seconds_count",
        "http_server_requests_seconds_max",
        "http_server_requests_seconds_sum",
        "jvm_buffer_count_buffers",
        "jvm_buffer_memory_used_bytes",
        "jvm_buffer_total_capacity_bytes",
        "jvm_classes_loaded_classes",
        "jvm_classes_unloaded_classes_total",
        "jvm_compilation_time_ms_total",
        "jvm_gc_memory_promoted_bytes_total"
      ]
    }
  ]
}
```

##### Raw Evidence 2

- Source: `customers-service`
- Message: Service exposes Prometheus-compatible metrics.

```json
{
  "service": "customers-service",
  "base_url": "http://127.0.0.1:8081",
  "candidate_paths": [
    "/actuator/prometheus",
    "/metrics"
  ],
  "expected_status_codes": [
    200
  ],
  "attempts": [
    {
      "url": "http://127.0.0.1:8081/actuator/prometheus",
      "status_code": 200,
      "expected_status_codes": [
        200
      ],
      "success": true,
      "failure_reason": null,
      "metric_count": 84,
      "metric_names_sample": [
        "application_ready_time_seconds",
        "application_started_time_seconds",
        "executor_active_threads",
        "executor_completed_tasks_total",
        "executor_pool_core_threads",
        "executor_pool_size_threads",
        "executor_queued_tasks",
        "hikaricp_connections",
        "hikaricp_connections_acquire_seconds_count",
        "hikaricp_connections_acquire_seconds_sum",
        "hikaricp_connections_active",
        "hikaricp_connections_creation_seconds_count",
        "hikaricp_connections_creation_seconds_max",
        "hikaricp_connections_creation_seconds_sum",
        "hikaricp_connections_idle",
        "hikaricp_connections_max",
        "hikaricp_connections_min",
        "hikaricp_connections_pending",
        "hikaricp_connections_timeout_total",
        "hikaricp_connections_usage_seconds_count"
      ]
    }
  ]
}
```

##### Raw Evidence 3

- Source: `visits-service`
- Message: Service exposes Prometheus-compatible metrics.

```json
{
  "service": "visits-service",
  "base_url": "http://127.0.0.1:8082",
  "candidate_paths": [
    "/actuator/prometheus",
    "/metrics"
  ],
  "expected_status_codes": [
    200
  ],
  "attempts": [
    {
      "url": "http://127.0.0.1:8082/actuator/prometheus",
      "status_code": 200,
      "expected_status_codes": [
        200
      ],
      "success": true,
      "failure_reason": null,
      "metric_count": 86,
      "metric_names_sample": [
        "application_ready_time_seconds",
        "application_started_time_seconds",
        "executor_active_threads",
        "executor_completed_tasks_total",
        "executor_pool_core_threads",
        "executor_pool_size_threads",
        "executor_queued_tasks",
        "hikaricp_connections",
        "hikaricp_connections_acquire_seconds_count",
        "hikaricp_connections_acquire_seconds_sum",
        "hikaricp_connections_active",
        "hikaricp_connections_creation_seconds_count",
        "hikaricp_connections_creation_seconds_max",
        "hikaricp_connections_creation_seconds_sum",
        "hikaricp_connections_idle",
        "hikaricp_connections_max",
        "hikaricp_connections_min",
        "hikaricp_connections_pending",
        "hikaricp_connections_timeout_total",
        "hikaricp_connections_usage_seconds_count"
      ]
    }
  ]
}
```

##### Raw Evidence 4

- Source: `vets-service`
- Message: Service exposes Prometheus-compatible metrics.

```json
{
  "service": "vets-service",
  "base_url": "http://127.0.0.1:8083",
  "candidate_paths": [
    "/actuator/prometheus",
    "/metrics"
  ],
  "expected_status_codes": [
    200
  ],
  "attempts": [
    {
      "url": "http://127.0.0.1:8083/actuator/prometheus",
      "status_code": 200,
      "expected_status_codes": [
        200
      ],
      "success": true,
      "failure_reason": null,
      "metric_count": 86,
      "metric_names_sample": [
        "application_ready_time_seconds",
        "application_started_time_seconds",
        "executor_active_threads",
        "executor_completed_tasks_total",
        "executor_pool_core_threads",
        "executor_pool_size_threads",
        "executor_queued_tasks",
        "hikaricp_connections",
        "hikaricp_connections_acquire_seconds_count",
        "hikaricp_connections_acquire_seconds_sum",
        "hikaricp_connections_active",
        "hikaricp_connections_creation_seconds_count",
        "hikaricp_connections_creation_seconds_max",
        "hikaricp_connections_creation_seconds_sum",
        "hikaricp_connections_idle",
        "hikaricp_connections_max",
        "hikaricp_connections_min",
        "hikaricp_connections_pending",
        "hikaricp_connections_timeout_total",
        "hikaricp_connections_usage_seconds_count"
      ]
    }
  ]
}
```

#### Normalized Evidence

| Source Type | Source Name | Resource | Compliant | Observed | Expected |
|---|---|---|---|---|---|
| http | api-gateway | http://127.0.0.1:8080/actuator/prometheus | True | 200 | [200] |
| http | customers-service | http://127.0.0.1:8081/actuator/prometheus | True | 200 | [200] |
| http | visits-service | http://127.0.0.1:8082/actuator/prometheus | True | 200 | [200] |
| http | vets-service | http://127.0.0.1:8083/actuator/prometheus | True | 200 | [200] |

### OBS-002 — Metrics must include request count metric

- Severity: `medium`
- Status: `passed`
- Category: `observability`
- Target: `service`
- Check type: `required_prometheus_metric_groups`
- Message: All services expose required Prometheus metric group(s).

#### Raw Evidence

##### Raw Evidence 1

- Source: `api-gateway`
- Message: Service exposes required Prometheus metric group(s).

```json
{
  "service": "api-gateway",
  "base_url": "http://127.0.0.1:8080",
  "candidate_paths": [
    "/actuator/prometheus",
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
      "url": "http://127.0.0.1:8080/actuator/prometheus",
      "status_code": 200,
      "expected_status_codes": [
        200
      ],
      "success": true,
      "failure_reason": null,
      "metric_count": 42,
      "matched_groups": {
        "request_count": [
          "http_server_requests_seconds_count"
        ]
      },
      "missing_groups": [],
      "metric_names_sample": [
        "application_ready_time_seconds",
        "application_started_time_seconds",
        "executor_active_threads",
        "executor_completed_tasks_total",
        "executor_pool_core_threads",
        "executor_pool_size_threads",
        "executor_queued_tasks",
        "http_server_requests_active_seconds_count",
        "http_server_requests_active_seconds_max",
        "http_server_requests_active_seconds_sum",
        "http_server_requests_seconds_count",
        "http_server_requests_seconds_max",
        "http_server_requests_seconds_sum",
        "jvm_buffer_count_buffers",
        "jvm_buffer_memory_used_bytes",
        "jvm_buffer_total_capacity_bytes",
        "jvm_classes_loaded_classes",
        "jvm_classes_unloaded_classes_total",
        "jvm_compilation_time_ms_total",
        "jvm_gc_memory_promoted_bytes_total"
      ]
    }
  ]
}
```

##### Raw Evidence 2

- Source: `customers-service`
- Message: Service exposes required Prometheus metric group(s).

```json
{
  "service": "customers-service",
  "base_url": "http://127.0.0.1:8081",
  "candidate_paths": [
    "/actuator/prometheus",
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
      "url": "http://127.0.0.1:8081/actuator/prometheus",
      "status_code": 200,
      "expected_status_codes": [
        200
      ],
      "success": true,
      "failure_reason": null,
      "metric_count": 84,
      "matched_groups": {
        "request_count": [
          "http_server_requests_seconds_count"
        ]
      },
      "missing_groups": [],
      "metric_names_sample": [
        "application_ready_time_seconds",
        "application_started_time_seconds",
        "executor_active_threads",
        "executor_completed_tasks_total",
        "executor_pool_core_threads",
        "executor_pool_size_threads",
        "executor_queued_tasks",
        "hikaricp_connections",
        "hikaricp_connections_acquire_seconds_count",
        "hikaricp_connections_acquire_seconds_sum",
        "hikaricp_connections_active",
        "hikaricp_connections_creation_seconds_count",
        "hikaricp_connections_creation_seconds_max",
        "hikaricp_connections_creation_seconds_sum",
        "hikaricp_connections_idle",
        "hikaricp_connections_max",
        "hikaricp_connections_min",
        "hikaricp_connections_pending",
        "hikaricp_connections_timeout_total",
        "hikaricp_connections_usage_seconds_count"
      ]
    }
  ]
}
```

##### Raw Evidence 3

- Source: `visits-service`
- Message: Service exposes required Prometheus metric group(s).

```json
{
  "service": "visits-service",
  "base_url": "http://127.0.0.1:8082",
  "candidate_paths": [
    "/actuator/prometheus",
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
      "url": "http://127.0.0.1:8082/actuator/prometheus",
      "status_code": 200,
      "expected_status_codes": [
        200
      ],
      "success": true,
      "failure_reason": null,
      "metric_count": 86,
      "matched_groups": {
        "request_count": [
          "http_server_requests_seconds_count"
        ]
      },
      "missing_groups": [],
      "metric_names_sample": [
        "application_ready_time_seconds",
        "application_started_time_seconds",
        "executor_active_threads",
        "executor_completed_tasks_total",
        "executor_pool_core_threads",
        "executor_pool_size_threads",
        "executor_queued_tasks",
        "hikaricp_connections",
        "hikaricp_connections_acquire_seconds_count",
        "hikaricp_connections_acquire_seconds_sum",
        "hikaricp_connections_active",
        "hikaricp_connections_creation_seconds_count",
        "hikaricp_connections_creation_seconds_max",
        "hikaricp_connections_creation_seconds_sum",
        "hikaricp_connections_idle",
        "hikaricp_connections_max",
        "hikaricp_connections_min",
        "hikaricp_connections_pending",
        "hikaricp_connections_timeout_total",
        "hikaricp_connections_usage_seconds_count"
      ]
    }
  ]
}
```

##### Raw Evidence 4

- Source: `vets-service`
- Message: Service exposes required Prometheus metric group(s).

```json
{
  "service": "vets-service",
  "base_url": "http://127.0.0.1:8083",
  "candidate_paths": [
    "/actuator/prometheus",
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
      "url": "http://127.0.0.1:8083/actuator/prometheus",
      "status_code": 200,
      "expected_status_codes": [
        200
      ],
      "success": true,
      "failure_reason": null,
      "metric_count": 86,
      "matched_groups": {
        "request_count": [
          "http_server_requests_seconds_count"
        ]
      },
      "missing_groups": [],
      "metric_names_sample": [
        "application_ready_time_seconds",
        "application_started_time_seconds",
        "executor_active_threads",
        "executor_completed_tasks_total",
        "executor_pool_core_threads",
        "executor_pool_size_threads",
        "executor_queued_tasks",
        "hikaricp_connections",
        "hikaricp_connections_acquire_seconds_count",
        "hikaricp_connections_acquire_seconds_sum",
        "hikaricp_connections_active",
        "hikaricp_connections_creation_seconds_count",
        "hikaricp_connections_creation_seconds_max",
        "hikaricp_connections_creation_seconds_sum",
        "hikaricp_connections_idle",
        "hikaricp_connections_max",
        "hikaricp_connections_min",
        "hikaricp_connections_pending",
        "hikaricp_connections_timeout_total",
        "hikaricp_connections_usage_seconds_count"
      ]
    }
  ]
}
```

#### Normalized Evidence

| Source Type | Source Name | Resource | Compliant | Observed | Expected |
|---|---|---|---|---|---|
| http | api-gateway | http://127.0.0.1:8080/actuator/prometheus | True | 200 | [200] |
| http | customers-service | http://127.0.0.1:8081/actuator/prometheus | True | 200 | [200] |
| http | visits-service | http://127.0.0.1:8082/actuator/prometheus | True | 200 | [200] |
| http | vets-service | http://127.0.0.1:8083/actuator/prometheus | True | 200 | [200] |

### OBS-003 — Metrics must include request duration metric

- Severity: `medium`
- Status: `passed`
- Category: `observability`
- Target: `service`
- Check type: `required_prometheus_metric_groups`
- Message: All services expose required Prometheus metric group(s).

#### Raw Evidence

##### Raw Evidence 1

- Source: `api-gateway`
- Message: Service exposes required Prometheus metric group(s).

```json
{
  "service": "api-gateway",
  "base_url": "http://127.0.0.1:8080",
  "candidate_paths": [
    "/actuator/prometheus",
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
      "url": "http://127.0.0.1:8080/actuator/prometheus",
      "status_code": 200,
      "expected_status_codes": [
        200
      ],
      "success": true,
      "failure_reason": null,
      "metric_count": 42,
      "matched_groups": {
        "request_duration": [
          "http_server_requests_seconds_sum"
        ]
      },
      "missing_groups": [],
      "metric_names_sample": [
        "application_ready_time_seconds",
        "application_started_time_seconds",
        "executor_active_threads",
        "executor_completed_tasks_total",
        "executor_pool_core_threads",
        "executor_pool_size_threads",
        "executor_queued_tasks",
        "http_server_requests_active_seconds_count",
        "http_server_requests_active_seconds_max",
        "http_server_requests_active_seconds_sum",
        "http_server_requests_seconds_count",
        "http_server_requests_seconds_max",
        "http_server_requests_seconds_sum",
        "jvm_buffer_count_buffers",
        "jvm_buffer_memory_used_bytes",
        "jvm_buffer_total_capacity_bytes",
        "jvm_classes_loaded_classes",
        "jvm_classes_unloaded_classes_total",
        "jvm_compilation_time_ms_total",
        "jvm_gc_memory_promoted_bytes_total"
      ]
    }
  ]
}
```

##### Raw Evidence 2

- Source: `customers-service`
- Message: Service exposes required Prometheus metric group(s).

```json
{
  "service": "customers-service",
  "base_url": "http://127.0.0.1:8081",
  "candidate_paths": [
    "/actuator/prometheus",
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
      "url": "http://127.0.0.1:8081/actuator/prometheus",
      "status_code": 200,
      "expected_status_codes": [
        200
      ],
      "success": true,
      "failure_reason": null,
      "metric_count": 84,
      "matched_groups": {
        "request_duration": [
          "http_server_requests_seconds_sum"
        ]
      },
      "missing_groups": [],
      "metric_names_sample": [
        "application_ready_time_seconds",
        "application_started_time_seconds",
        "executor_active_threads",
        "executor_completed_tasks_total",
        "executor_pool_core_threads",
        "executor_pool_size_threads",
        "executor_queued_tasks",
        "hikaricp_connections",
        "hikaricp_connections_acquire_seconds_count",
        "hikaricp_connections_acquire_seconds_sum",
        "hikaricp_connections_active",
        "hikaricp_connections_creation_seconds_count",
        "hikaricp_connections_creation_seconds_max",
        "hikaricp_connections_creation_seconds_sum",
        "hikaricp_connections_idle",
        "hikaricp_connections_max",
        "hikaricp_connections_min",
        "hikaricp_connections_pending",
        "hikaricp_connections_timeout_total",
        "hikaricp_connections_usage_seconds_count"
      ]
    }
  ]
}
```

##### Raw Evidence 3

- Source: `visits-service`
- Message: Service exposes required Prometheus metric group(s).

```json
{
  "service": "visits-service",
  "base_url": "http://127.0.0.1:8082",
  "candidate_paths": [
    "/actuator/prometheus",
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
      "url": "http://127.0.0.1:8082/actuator/prometheus",
      "status_code": 200,
      "expected_status_codes": [
        200
      ],
      "success": true,
      "failure_reason": null,
      "metric_count": 86,
      "matched_groups": {
        "request_duration": [
          "http_server_requests_seconds_sum"
        ]
      },
      "missing_groups": [],
      "metric_names_sample": [
        "application_ready_time_seconds",
        "application_started_time_seconds",
        "executor_active_threads",
        "executor_completed_tasks_total",
        "executor_pool_core_threads",
        "executor_pool_size_threads",
        "executor_queued_tasks",
        "hikaricp_connections",
        "hikaricp_connections_acquire_seconds_count",
        "hikaricp_connections_acquire_seconds_sum",
        "hikaricp_connections_active",
        "hikaricp_connections_creation_seconds_count",
        "hikaricp_connections_creation_seconds_max",
        "hikaricp_connections_creation_seconds_sum",
        "hikaricp_connections_idle",
        "hikaricp_connections_max",
        "hikaricp_connections_min",
        "hikaricp_connections_pending",
        "hikaricp_connections_timeout_total",
        "hikaricp_connections_usage_seconds_count"
      ]
    }
  ]
}
```

##### Raw Evidence 4

- Source: `vets-service`
- Message: Service exposes required Prometheus metric group(s).

```json
{
  "service": "vets-service",
  "base_url": "http://127.0.0.1:8083",
  "candidate_paths": [
    "/actuator/prometheus",
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
      "url": "http://127.0.0.1:8083/actuator/prometheus",
      "status_code": 200,
      "expected_status_codes": [
        200
      ],
      "success": true,
      "failure_reason": null,
      "metric_count": 86,
      "matched_groups": {
        "request_duration": [
          "http_server_requests_seconds_sum"
        ]
      },
      "missing_groups": [],
      "metric_names_sample": [
        "application_ready_time_seconds",
        "application_started_time_seconds",
        "executor_active_threads",
        "executor_completed_tasks_total",
        "executor_pool_core_threads",
        "executor_pool_size_threads",
        "executor_queued_tasks",
        "hikaricp_connections",
        "hikaricp_connections_acquire_seconds_count",
        "hikaricp_connections_acquire_seconds_sum",
        "hikaricp_connections_active",
        "hikaricp_connections_creation_seconds_count",
        "hikaricp_connections_creation_seconds_max",
        "hikaricp_connections_creation_seconds_sum",
        "hikaricp_connections_idle",
        "hikaricp_connections_max",
        "hikaricp_connections_min",
        "hikaricp_connections_pending",
        "hikaricp_connections_timeout_total",
        "hikaricp_connections_usage_seconds_count"
      ]
    }
  ]
}
```

#### Normalized Evidence

| Source Type | Source Name | Resource | Compliant | Observed | Expected |
|---|---|---|---|---|---|
| http | api-gateway | http://127.0.0.1:8080/actuator/prometheus | True | 200 | [200] |
| http | customers-service | http://127.0.0.1:8081/actuator/prometheus | True | 200 | [200] |
| http | visits-service | http://127.0.0.1:8082/actuator/prometheus | True | 200 | [200] |
| http | vets-service | http://127.0.0.1:8083/actuator/prometheus | True | 200 | [200] |

### OBS-004 — Metrics must include error or failure metric

- Severity: `medium`
- Status: `passed`
- Category: `observability`
- Target: `service`
- Check type: `required_prometheus_metric_groups`
- Message: All services expose required Prometheus metric group(s).

#### Raw Evidence

##### Raw Evidence 1

- Source: `api-gateway`
- Message: Service exposes required Prometheus metric group(s).

```json
{
  "service": "api-gateway",
  "base_url": "http://127.0.0.1:8080",
  "candidate_paths": [
    "/actuator/prometheus",
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
      "url": "http://127.0.0.1:8080/actuator/prometheus",
      "status_code": 200,
      "expected_status_codes": [
        200
      ],
      "success": true,
      "failure_reason": null,
      "metric_count": 42,
      "matched_groups": {
        "error_metric": [
          "http_server_requests_seconds_count"
        ]
      },
      "missing_groups": [],
      "metric_names_sample": [
        "application_ready_time_seconds",
        "application_started_time_seconds",
        "executor_active_threads",
        "executor_completed_tasks_total",
        "executor_pool_core_threads",
        "executor_pool_size_threads",
        "executor_queued_tasks",
        "http_server_requests_active_seconds_count",
        "http_server_requests_active_seconds_max",
        "http_server_requests_active_seconds_sum",
        "http_server_requests_seconds_count",
        "http_server_requests_seconds_max",
        "http_server_requests_seconds_sum",
        "jvm_buffer_count_buffers",
        "jvm_buffer_memory_used_bytes",
        "jvm_buffer_total_capacity_bytes",
        "jvm_classes_loaded_classes",
        "jvm_classes_unloaded_classes_total",
        "jvm_compilation_time_ms_total",
        "jvm_gc_memory_promoted_bytes_total"
      ]
    }
  ]
}
```

##### Raw Evidence 2

- Source: `customers-service`
- Message: Service exposes required Prometheus metric group(s).

```json
{
  "service": "customers-service",
  "base_url": "http://127.0.0.1:8081",
  "candidate_paths": [
    "/actuator/prometheus",
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
      "url": "http://127.0.0.1:8081/actuator/prometheus",
      "status_code": 200,
      "expected_status_codes": [
        200
      ],
      "success": true,
      "failure_reason": null,
      "metric_count": 84,
      "matched_groups": {
        "error_metric": [
          "http_server_requests_seconds_count"
        ]
      },
      "missing_groups": [],
      "metric_names_sample": [
        "application_ready_time_seconds",
        "application_started_time_seconds",
        "executor_active_threads",
        "executor_completed_tasks_total",
        "executor_pool_core_threads",
        "executor_pool_size_threads",
        "executor_queued_tasks",
        "hikaricp_connections",
        "hikaricp_connections_acquire_seconds_count",
        "hikaricp_connections_acquire_seconds_sum",
        "hikaricp_connections_active",
        "hikaricp_connections_creation_seconds_count",
        "hikaricp_connections_creation_seconds_max",
        "hikaricp_connections_creation_seconds_sum",
        "hikaricp_connections_idle",
        "hikaricp_connections_max",
        "hikaricp_connections_min",
        "hikaricp_connections_pending",
        "hikaricp_connections_timeout_total",
        "hikaricp_connections_usage_seconds_count"
      ]
    }
  ]
}
```

##### Raw Evidence 3

- Source: `visits-service`
- Message: Service exposes required Prometheus metric group(s).

```json
{
  "service": "visits-service",
  "base_url": "http://127.0.0.1:8082",
  "candidate_paths": [
    "/actuator/prometheus",
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
      "url": "http://127.0.0.1:8082/actuator/prometheus",
      "status_code": 200,
      "expected_status_codes": [
        200
      ],
      "success": true,
      "failure_reason": null,
      "metric_count": 86,
      "matched_groups": {
        "error_metric": [
          "http_server_requests_seconds_count"
        ]
      },
      "missing_groups": [],
      "metric_names_sample": [
        "application_ready_time_seconds",
        "application_started_time_seconds",
        "executor_active_threads",
        "executor_completed_tasks_total",
        "executor_pool_core_threads",
        "executor_pool_size_threads",
        "executor_queued_tasks",
        "hikaricp_connections",
        "hikaricp_connections_acquire_seconds_count",
        "hikaricp_connections_acquire_seconds_sum",
        "hikaricp_connections_active",
        "hikaricp_connections_creation_seconds_count",
        "hikaricp_connections_creation_seconds_max",
        "hikaricp_connections_creation_seconds_sum",
        "hikaricp_connections_idle",
        "hikaricp_connections_max",
        "hikaricp_connections_min",
        "hikaricp_connections_pending",
        "hikaricp_connections_timeout_total",
        "hikaricp_connections_usage_seconds_count"
      ]
    }
  ]
}
```

##### Raw Evidence 4

- Source: `vets-service`
- Message: Service exposes required Prometheus metric group(s).

```json
{
  "service": "vets-service",
  "base_url": "http://127.0.0.1:8083",
  "candidate_paths": [
    "/actuator/prometheus",
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
      "url": "http://127.0.0.1:8083/actuator/prometheus",
      "status_code": 200,
      "expected_status_codes": [
        200
      ],
      "success": true,
      "failure_reason": null,
      "metric_count": 86,
      "matched_groups": {
        "error_metric": [
          "http_server_requests_seconds_count"
        ]
      },
      "missing_groups": [],
      "metric_names_sample": [
        "application_ready_time_seconds",
        "application_started_time_seconds",
        "executor_active_threads",
        "executor_completed_tasks_total",
        "executor_pool_core_threads",
        "executor_pool_size_threads",
        "executor_queued_tasks",
        "hikaricp_connections",
        "hikaricp_connections_acquire_seconds_count",
        "hikaricp_connections_acquire_seconds_sum",
        "hikaricp_connections_active",
        "hikaricp_connections_creation_seconds_count",
        "hikaricp_connections_creation_seconds_max",
        "hikaricp_connections_creation_seconds_sum",
        "hikaricp_connections_idle",
        "hikaricp_connections_max",
        "hikaricp_connections_min",
        "hikaricp_connections_pending",
        "hikaricp_connections_timeout_total",
        "hikaricp_connections_usage_seconds_count"
      ]
    }
  ]
}
```

#### Normalized Evidence

| Source Type | Source Name | Resource | Compliant | Observed | Expected |
|---|---|---|---|---|---|
| http | api-gateway | http://127.0.0.1:8080/actuator/prometheus | True | 200 | [200] |
| http | customers-service | http://127.0.0.1:8081/actuator/prometheus | True | 200 | [200] |
| http | visits-service | http://127.0.0.1:8082/actuator/prometheus | True | 200 | [200] |
| http | vets-service | http://127.0.0.1:8083/actuator/prometheus | True | 200 | [200] |

### SVC-001 — Services must expose a health endpoint

- Severity: `high`
- Status: `passed`
- Category: `service`
- Target: `service`
- Check type: `http_health_endpoint`
- Message: All services expose at least one reachable health endpoint.

#### Raw Evidence

##### Raw Evidence 1

- Source: `api-gateway`
- Message: Service has a reachable health endpoint.

```json
{
  "service": "api-gateway",
  "base_url": "http://127.0.0.1:8080",
  "candidate_paths": [
    "/actuator/health"
  ],
  "expected_status_codes": [
    200,
    204
  ],
  "attempts": [
    {
      "url": "http://127.0.0.1:8080/actuator/health",
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

##### Raw Evidence 2

- Source: `customers-service`
- Message: Service has a reachable health endpoint.

```json
{
  "service": "customers-service",
  "base_url": "http://127.0.0.1:8081",
  "candidate_paths": [
    "/actuator/health"
  ],
  "expected_status_codes": [
    200,
    204
  ],
  "attempts": [
    {
      "url": "http://127.0.0.1:8081/actuator/health",
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

##### Raw Evidence 3

- Source: `visits-service`
- Message: Service has a reachable health endpoint.

```json
{
  "service": "visits-service",
  "base_url": "http://127.0.0.1:8082",
  "candidate_paths": [
    "/actuator/health"
  ],
  "expected_status_codes": [
    200,
    204
  ],
  "attempts": [
    {
      "url": "http://127.0.0.1:8082/actuator/health",
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

##### Raw Evidence 4

- Source: `vets-service`
- Message: Service has a reachable health endpoint.

```json
{
  "service": "vets-service",
  "base_url": "http://127.0.0.1:8083",
  "candidate_paths": [
    "/actuator/health"
  ],
  "expected_status_codes": [
    200,
    204
  ],
  "attempts": [
    {
      "url": "http://127.0.0.1:8083/actuator/health",
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
| http | api-gateway | http://127.0.0.1:8080/actuator/health | True | 200 | [200, 204] |
| http | customers-service | http://127.0.0.1:8081/actuator/health | True | 200 | [200, 204] |
| http | visits-service | http://127.0.0.1:8082/actuator/health | True | 200 | [200, 204] |
| http | vets-service | http://127.0.0.1:8083/actuator/health | True | 200 | [200, 204] |

### SVC-002 — Services must expose an OpenAPI specification

- Severity: `medium`
- Status: `failed`
- Category: `service`
- Target: `service`
- Check type: `openapi_spec`
- Message: OpenAPI specification check failed for service(s): api-gateway, customers-service, visits-service, vets-service

#### Raw Evidence

##### Raw Evidence 1

- Source: `api-gateway`
- Message: Service does not expose a valid OpenAPI specification.

```json
{
  "service": "api-gateway",
  "base_url": "http://127.0.0.1:8080",
  "candidate_paths": [
    "/v3/api-docs",
    "/openapi.json"
  ],
  "expected_status_codes": [
    200
  ],
  "attempts": [
    {
      "url": "http://127.0.0.1:8080/v3/api-docs",
      "status_code": 404,
      "expected_status_codes": [
        200
      ],
      "success": false,
      "failure_reason": "unexpected_status_code"
    },
    {
      "url": "http://127.0.0.1:8080/openapi.json",
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

##### Raw Evidence 2

- Source: `customers-service`
- Message: Service does not expose a valid OpenAPI specification.

```json
{
  "service": "customers-service",
  "base_url": "http://127.0.0.1:8081",
  "candidate_paths": [
    "/v3/api-docs",
    "/openapi.json"
  ],
  "expected_status_codes": [
    200
  ],
  "attempts": [
    {
      "url": "http://127.0.0.1:8081/v3/api-docs",
      "status_code": 404,
      "expected_status_codes": [
        200
      ],
      "success": false,
      "failure_reason": "unexpected_status_code"
    },
    {
      "url": "http://127.0.0.1:8081/openapi.json",
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

##### Raw Evidence 3

- Source: `visits-service`
- Message: Service does not expose a valid OpenAPI specification.

```json
{
  "service": "visits-service",
  "base_url": "http://127.0.0.1:8082",
  "candidate_paths": [
    "/v3/api-docs",
    "/openapi.json"
  ],
  "expected_status_codes": [
    200
  ],
  "attempts": [
    {
      "url": "http://127.0.0.1:8082/v3/api-docs",
      "status_code": 404,
      "expected_status_codes": [
        200
      ],
      "success": false,
      "failure_reason": "unexpected_status_code"
    },
    {
      "url": "http://127.0.0.1:8082/openapi.json",
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

##### Raw Evidence 4

- Source: `vets-service`
- Message: Service does not expose a valid OpenAPI specification.

```json
{
  "service": "vets-service",
  "base_url": "http://127.0.0.1:8083",
  "candidate_paths": [
    "/v3/api-docs",
    "/openapi.json"
  ],
  "expected_status_codes": [
    200
  ],
  "attempts": [
    {
      "url": "http://127.0.0.1:8083/v3/api-docs",
      "status_code": 404,
      "expected_status_codes": [
        200
      ],
      "success": false,
      "failure_reason": "unexpected_status_code"
    },
    {
      "url": "http://127.0.0.1:8083/openapi.json",
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
| http | api-gateway | http://127.0.0.1:8080/v3/api-docs | False | 404 | [200] |
| http | api-gateway | http://127.0.0.1:8080/openapi.json | False | 404 | [200] |
| http | customers-service | http://127.0.0.1:8081/v3/api-docs | False | 404 | [200] |
| http | customers-service | http://127.0.0.1:8081/openapi.json | False | 404 | [200] |
| http | visits-service | http://127.0.0.1:8082/v3/api-docs | False | 404 | [200] |
| http | visits-service | http://127.0.0.1:8082/openapi.json | False | 404 | [200] |
| http | vets-service | http://127.0.0.1:8083/v3/api-docs | False | 404 | [200] |
| http | vets-service | http://127.0.0.1:8083/openapi.json | False | 404 | [200] |
