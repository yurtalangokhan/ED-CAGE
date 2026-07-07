from dataclasses import dataclass
from typing import Any


HTTP_METHODS = {
    "get",
    "put",
    "post",
    "delete",
    "options",
    "head",
    "patch",
    "trace",
}


@dataclass(frozen=True)
class OpenApiOperation:
    path: str
    method: str
    operation: dict[str, Any]

    @property
    def operation_ref(self) -> str:
        return f"{self.method.upper()} {self.path}"


def is_openapi_document(document: object) -> bool:
    if not isinstance(document, dict):
        return False

    return "openapi" in document or "swagger" in document


def get_openapi_version(document: dict[str, Any]) -> str | None:
    if document.get("openapi") is not None:
        return str(document["openapi"])

    if document.get("swagger") is not None:
        return str(document["swagger"])

    return None


def get_operations(document: dict[str, Any]) -> list[OpenApiOperation]:
    paths = document.get("paths")

    if not isinstance(paths, dict):
        return []

    operations: list[OpenApiOperation] = []

    for path, path_item in paths.items():
        if not isinstance(path_item, dict):
            continue

        for method, operation in path_item.items():
            if method.lower() not in HTTP_METHODS:
                continue

            if not isinstance(operation, dict):
                continue

            operations.append(
                OpenApiOperation(
                    path=str(path),
                    method=str(method).lower(),
                    operation=operation,
                )
            )

    return operations


def has_info_metadata(document: dict[str, Any]) -> bool:
    info = document.get("info")

    if not isinstance(info, dict):
        return False

    title = info.get("title")
    version = info.get("version")

    return _is_non_empty_string(title) and _is_non_empty_string(version)


def operation_has_operation_id(operation: OpenApiOperation) -> bool:
    operation_id = operation.operation.get("operationId")

    return _is_non_empty_string(operation_id)


def operation_has_success_response(operation: OpenApiOperation) -> bool:
    responses = operation.operation.get("responses")

    if not isinstance(responses, dict):
        return False

    return any(str(status_code).startswith("2") for status_code in responses)


def operation_has_error_response(operation: OpenApiOperation) -> bool:
    responses = operation.operation.get("responses")

    if not isinstance(responses, dict):
        return False

    return any(
        str(status_code).startswith(("4", "5")) or str(status_code).lower() == "default"
        for status_code in responses
    )


def operation_has_response_schema(operation: OpenApiOperation) -> bool:
    responses = operation.operation.get("responses")

    if not isinstance(responses, dict):
        return False

    success_response_codes = [
        str(status_code)
        for status_code in responses
        if str(status_code).startswith("2")
    ]

    if not success_response_codes:
        return False

    for status_code in success_response_codes:
        response = responses.get(status_code)

        if not _response_has_schema(response):
            return False

    return True


def operation_request_body_has_schema_if_present(operation: OpenApiOperation) -> bool:
    request_body = operation.operation.get("requestBody")

    if request_body is None:
        return True

    if not isinstance(request_body, dict):
        return False

    content = request_body.get("content")

    if not isinstance(content, dict):
        return False

    for media_type in content.values():
        if not isinstance(media_type, dict):
            continue

        if isinstance(media_type.get("schema"), dict):
            return True

    return False


def has_security_scheme(document: dict[str, Any]) -> bool:
    components = document.get("components")

    if not isinstance(components, dict):
        return False

    security_schemes = components.get("securitySchemes")

    return isinstance(security_schemes, dict) and bool(security_schemes)


def has_security_requirement(document: dict[str, Any]) -> bool:
    global_security = document.get("security")

    if isinstance(global_security, list) and bool(global_security):
        return True

    for operation in get_operations(document):
        operation_security = operation.operation.get("security")

        if isinstance(operation_security, list) and bool(operation_security):
            return True

    return False


def _response_has_schema(response: object) -> bool:
    if not isinstance(response, dict):
        return False

    content = response.get("content")

    if not isinstance(content, dict):
        return False

    for media_type in content.values():
        if not isinstance(media_type, dict):
            continue

        if isinstance(media_type.get("schema"), dict):
            return True

    return False


def _is_non_empty_string(value: object) -> bool:
    return isinstance(value, str) and bool(value.strip())