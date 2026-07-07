from ed_cage.checks.common.openapi_utils import (
    get_operations,
    has_info_metadata,
    has_security_requirement,
    has_security_scheme,
    is_openapi_document,
    operation_has_error_response,
    operation_has_operation_id,
    operation_has_response_schema,
    operation_has_success_response,
)


def test_is_openapi_document_returns_true_for_openapi_document() -> None:
    assert is_openapi_document({"openapi": "3.0.3"}) is True


def test_get_operations_extracts_http_operations() -> None:
    document = {
        "openapi": "3.0.3",
        "paths": {
            "/pets": {
                "get": {
                    "operationId": "listPets",
                    "responses": {
                        "200": {
                            "description": "OK",
                        }
                    },
                },
                "parameters": [],
            }
        },
    }

    operations = get_operations(document)

    assert len(operations) == 1
    assert operations[0].operation_ref == "GET /pets"


def test_openapi_operation_policy_helpers() -> None:
    operation = get_operations(_valid_document())[0]

    assert operation_has_operation_id(operation) is True
    assert operation_has_success_response(operation) is True
    assert operation_has_error_response(operation) is True
    assert operation_has_response_schema(operation) is True


def test_has_info_metadata() -> None:
    assert has_info_metadata(_valid_document()) is True


def test_has_security_scheme_and_requirement() -> None:
    document = _valid_document()

    assert has_security_scheme(document) is True
    assert has_security_requirement(document) is True


def _valid_document() -> dict[str, object]:
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
                                    }
                                }
                            },
                        },
                        "500": {
                            "description": "Error",
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