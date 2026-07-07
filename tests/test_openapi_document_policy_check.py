from ed_cage.checks.api.openapi_document_policy_check import OpenApiDocumentPolicyCheck
from ed_cage.domain.enums import CheckStatus, Severity
from ed_cage.domain.models import GovernanceRule, ProjectContext, ServiceDefinition


def test_openapi_document_policy_check_passes_for_info_metadata(http_test_server) -> None:
    http_test_server.set_json_response(
        path="/openapi.json",
        status_code=200,
        payload=_valid_openapi_document(),
    )

    finding = OpenApiDocumentPolicyCheck().evaluate(
        rule=_build_rule("API-001", "require_info_metadata"),
        context=_build_context(http_test_server.base_url),
    )

    assert finding.status == CheckStatus.PASSED
    assert finding.evidence[0].data["attempts"][0]["success"] is True


def test_openapi_document_policy_check_fails_when_operation_id_missing(
    http_test_server,
) -> None:
    document = _valid_openapi_document()
    document["paths"]["/pets"]["get"].pop("operationId")

    http_test_server.set_json_response(
        path="/openapi.json",
        status_code=200,
        payload=document,
    )

    finding = OpenApiDocumentPolicyCheck().evaluate(
        rule=_build_rule("API-002", "require_operation_id"),
        context=_build_context(http_test_server.base_url),
    )

    assert finding.status == CheckStatus.FAILED

    attempt = finding.evidence[0].data["attempts"][0]
    assert attempt["failure_reason"] == "missing_operation_id"
    assert attempt["missing_operations"] == ["GET /pets"]


def test_openapi_document_policy_check_fails_when_error_response_missing(
    http_test_server,
) -> None:
    document = _valid_openapi_document()
    document["paths"]["/pets"]["get"]["responses"].pop("500")

    http_test_server.set_json_response(
        path="/openapi.json",
        status_code=200,
        payload=document,
    )

    finding = OpenApiDocumentPolicyCheck().evaluate(
        rule=_build_rule("API-004", "require_error_responses"),
        context=_build_context(http_test_server.base_url),
    )

    assert finding.status == CheckStatus.FAILED

    attempt = finding.evidence[0].data["attempts"][0]
    assert attempt["failure_reason"] == "missing_error_response"
    assert attempt["missing_operations"] == ["GET /pets"]


def test_openapi_document_policy_check_fails_when_response_schema_missing(
    http_test_server,
) -> None:
    document = _valid_openapi_document()
    document["paths"]["/pets"]["get"]["responses"]["200"].pop("content")

    http_test_server.set_json_response(
        path="/openapi.json",
        status_code=200,
        payload=document,
    )

    finding = OpenApiDocumentPolicyCheck().evaluate(
        rule=_build_rule("API-005", "require_operation_schemas"),
        context=_build_context(http_test_server.base_url),
    )

    assert finding.status == CheckStatus.FAILED

    attempt = finding.evidence[0].data["attempts"][0]
    assert attempt["failure_reason"] == "missing_operation_schema"
    assert attempt["missing_response_schema"] == ["GET /pets"]


def test_openapi_document_policy_check_fails_when_security_scheme_missing(
    http_test_server,
) -> None:
    document = _valid_openapi_document()
    document.pop("security")
    document.pop("components")

    http_test_server.set_json_response(
        path="/openapi.json",
        status_code=200,
        payload=document,
    )

    finding = OpenApiDocumentPolicyCheck().evaluate(
        rule=_build_rule("API-006", "require_security_scheme"),
        context=_build_context(http_test_server.base_url),
    )

    assert finding.status == CheckStatus.FAILED

    attempt = finding.evidence[0].data["attempts"][0]
    assert attempt["failure_reason"] == "missing_security_scheme_or_requirement"
    assert attempt["security_scheme_exists"] is False
    assert attempt["security_requirement_exists"] is False


def _build_rule(rule_id: str, policy: str) -> GovernanceRule:
    return GovernanceRule(
        id=rule_id,
        title=f"{rule_id} test rule",
        category="api",
        severity=Severity.MEDIUM,
        target="service",
        check_type="openapi_document_policy",
        params={
            "policy": policy,
            "allowed_paths": ["/openapi.json"],
            "expected_status_codes": [200],
            "timeout_seconds": 3,
        },
    )


def _build_context(base_url: str) -> ProjectContext:
    return ProjectContext(
        project_name="test",
        repository_path=".",
        config_path="configs/ed-cage.yaml",
        services=[
            ServiceDefinition(
                name="test-service",
                base_url=base_url,
                openapi_paths=["/openapi.json"],
            )
        ],
    )


def _valid_openapi_document() -> dict[str, object]:
    return {
        "openapi": "3.0.3",
        "info": {
            "title": "Test API",
            "version": "1.0.0",
        },
        "security": [
            {
                "bearerAuth": [],
            }
        ],
        "paths": {
            "/pets": {
                "get": {
                    "operationId": "listPets",
                    "responses": {
                        "200": {
                            "description": "OK",
                            "content": {
                                "application/json": {
                                    "schema": {
                                        "type": "array",
                                        "items": {
                                            "type": "object",
                                        },
                                    }
                                }
                            },
                        },
                        "500": {
                            "description": "Error",
                            "content": {
                                "application/json": {
                                    "schema": {
                                        "type": "object",
                                    }
                                }
                            },
                        },
                    },
                }
            }
        },
        "components": {
            "securitySchemes": {
                "bearerAuth": {
                    "type": "http",
                    "scheme": "bearer",
                }
            }
        },
    }