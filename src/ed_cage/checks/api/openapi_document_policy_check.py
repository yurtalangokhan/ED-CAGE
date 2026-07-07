from collections.abc import Callable
from typing import Any

import httpx

from ed_cage.checks.common.http_utils import (
    build_http_error_attempt,
    build_url,
    is_successful_attempt,
)
from ed_cage.checks.common.openapi_utils import (
    OpenApiOperation,
    get_openapi_version,
    get_operations,
    has_info_metadata,
    has_security_requirement,
    has_security_scheme,
    is_openapi_document,
    operation_has_error_response,
    operation_has_operation_id,
    operation_has_response_schema,
    operation_has_success_response,
    operation_request_body_has_schema_if_present,
)
from ed_cage.checks.common.rule_param_utils import (
    get_float_param,
    get_int_set_param,
    get_string_list_param,
)
from ed_cage.domain.enums import CheckStatus
from ed_cage.domain.models import Evidence, GovernanceFinding, GovernanceRule, ProjectContext


class OpenApiDocumentPolicyCheck:
    @property
    def check_type(self) -> str:
        return "openapi_document_policy"

    def evaluate(self, rule: GovernanceRule, context: ProjectContext) -> GovernanceFinding:
        if not context.services:
            return GovernanceFinding(
                rule_id=rule.id,
                title=rule.title,
                severity=rule.severity,
                status=CheckStatus.SKIPPED,
                message="No services are defined in the service catalog.",
                evidence=[],
            )

        policy = str(rule.params.get("policy", "")).strip()

        allowed_paths = get_string_list_param(
            params=rule.params,
            key="allowed_paths",
            default=["/openapi.json", "/swagger.json", "/v3/api-docs"],
            normalize_as_relative_path=True,
        )
        expected_status_codes = get_int_set_param(
            params=rule.params,
            key="expected_status_codes",
            default={200},
        )
        timeout_seconds = get_float_param(
            params=rule.params,
            key="timeout_seconds",
            default=3.0,
        )

        evidence: list[Evidence] = []
        failed_services: list[str] = []

        with httpx.Client(timeout=timeout_seconds, follow_redirects=True) as client:
            for service in context.services:
                candidate_paths = service.openapi_paths or allowed_paths
                service_passed = False
                attempts: list[dict[str, object]] = []

                for path in candidate_paths:
                    url = build_url(service.base_url, path)

                    try:
                        response = client.get(url)
                        attempt = self._evaluate_response(
                            url=url,
                            status_code=response.status_code,
                            response_json_loader=response.json,
                            expected_status_codes=expected_status_codes,
                            policy=policy,
                        )
                    except httpx.HTTPError as exc:
                        attempt = build_http_error_attempt(
                            url=url,
                            exc=exc,
                        )

                    attempts.append(attempt)

                    if is_successful_attempt(attempt):
                        service_passed = True
                        break

                evidence.append(
                    Evidence(
                        source=service.name,
                        message=(
                            f"Service satisfies OpenAPI policy: {policy}."
                            if service_passed
                            else f"Service does not satisfy OpenAPI policy: {policy}."
                        ),
                        data={
                            "service": service.name,
                            "base_url": service.base_url,
                            "candidate_paths": candidate_paths,
                            "expected_status_codes": sorted(expected_status_codes),
                            "policy": policy,
                            "attempts": attempts,
                        },
                    )
                )

                if not service_passed:
                    failed_services.append(service.name)

        if failed_services:
            return GovernanceFinding(
                rule_id=rule.id,
                title=rule.title,
                severity=rule.severity,
                status=CheckStatus.FAILED,
                message=f"OpenAPI policy '{policy}' failed for service(s): {', '.join(failed_services)}",
                evidence=evidence,
            )

        return GovernanceFinding(
            rule_id=rule.id,
            title=rule.title,
            severity=rule.severity,
            status=CheckStatus.PASSED,
            message=f"All services satisfy OpenAPI policy: {policy}.",
            evidence=evidence,
        )

    def _evaluate_response(
        self,
        url: str,
        status_code: int,
        response_json_loader: Callable[[], Any],
        expected_status_codes: set[int],
        policy: str,
    ) -> dict[str, object]:
        base_attempt: dict[str, object] = {
            "url": url,
            "status_code": status_code,
            "expected_status_codes": sorted(expected_status_codes),
            "policy": policy,
        }

        if status_code not in expected_status_codes:
            return {
                **base_attempt,
                "success": False,
                "failure_reason": "unexpected_status_code",
            }

        try:
            document = response_json_loader()
        except ValueError:
            return {
                **base_attempt,
                "success": False,
                "failure_reason": "invalid_json",
            }

        if not isinstance(document, dict) or not is_openapi_document(document):
            return {
                **base_attempt,
                "success": False,
                "failure_reason": "not_openapi_document",
            }

        return self._evaluate_policy(
            base_attempt=base_attempt,
            document=document,
            policy=policy,
        )

    def _evaluate_policy(
        self,
        base_attempt: dict[str, object],
        document: dict[str, Any],
        policy: str,
    ) -> dict[str, object]:
        operations = get_operations(document)

        policy_handlers = {
            "require_info_metadata": self._evaluate_require_info_metadata,
            "require_operation_id": self._evaluate_require_operation_id,
            "require_success_responses": self._evaluate_require_success_responses,
            "require_error_responses": self._evaluate_require_error_responses,
            "require_operation_schemas": self._evaluate_require_operation_schemas,
            "require_security_scheme": self._evaluate_require_security_scheme,
        }

        handler = policy_handlers.get(policy)

        if handler is None:
            return {
                **base_attempt,
                "success": False,
                "failure_reason": "unsupported_openapi_policy",
                "operation_count": len(operations),
                "spec_version": get_openapi_version(document),
            }

        policy_result = handler(document, operations)

        return {
            **base_attempt,
            **policy_result,
            "operation_count": len(operations),
            "spec_version": get_openapi_version(document),
        }

    def _evaluate_require_info_metadata(
        self,
        document: dict[str, Any],
        operations: list[OpenApiOperation],
    ) -> dict[str, object]:
        del operations

        passed = has_info_metadata(document)

        return {
            "success": passed,
            "failure_reason": None if passed else "missing_info_title_or_version",
        }

    def _evaluate_require_operation_id(
        self,
        document: dict[str, Any],
        operations: list[OpenApiOperation],
    ) -> dict[str, object]:
        del document

        missing_operations = [
            operation.operation_ref
            for operation in operations
            if not operation_has_operation_id(operation)
        ]

        return {
            "success": not missing_operations,
            "failure_reason": None if not missing_operations else "missing_operation_id",
            "missing_operations": missing_operations,
        }

    def _evaluate_require_success_responses(
        self,
        document: dict[str, Any],
        operations: list[OpenApiOperation],
    ) -> dict[str, object]:
        del document

        missing_operations = [
            operation.operation_ref
            for operation in operations
            if not operation_has_success_response(operation)
        ]

        return {
            "success": not missing_operations,
            "failure_reason": None if not missing_operations else "missing_success_response",
            "missing_operations": missing_operations,
        }

    def _evaluate_require_error_responses(
        self,
        document: dict[str, Any],
        operations: list[OpenApiOperation],
    ) -> dict[str, object]:
        del document

        missing_operations = [
            operation.operation_ref
            for operation in operations
            if not operation_has_error_response(operation)
        ]

        return {
            "success": not missing_operations,
            "failure_reason": None if not missing_operations else "missing_error_response",
            "missing_operations": missing_operations,
        }

    def _evaluate_require_operation_schemas(
        self,
        document: dict[str, Any],
        operations: list[OpenApiOperation],
    ) -> dict[str, object]:
        del document

        missing_response_schema = [
            operation.operation_ref
            for operation in operations
            if not operation_has_response_schema(operation)
        ]

        missing_request_schema = [
            operation.operation_ref
            for operation in operations
            if not operation_request_body_has_schema_if_present(operation)
        ]

        passed = not missing_response_schema and not missing_request_schema

        return {
            "success": passed,
            "failure_reason": None if passed else "missing_operation_schema",
            "missing_response_schema": missing_response_schema,
            "missing_request_schema": missing_request_schema,
        }

    def _evaluate_require_security_scheme(
        self,
        document: dict[str, Any],
        operations: list[OpenApiOperation],
    ) -> dict[str, object]:
        del operations

        security_scheme_exists = has_security_scheme(document)
        security_requirement_exists = has_security_requirement(document)
        passed = security_scheme_exists and security_requirement_exists

        return {
            "success": passed,
            "failure_reason": None if passed else "missing_security_scheme_or_requirement",
            "security_scheme_exists": security_scheme_exists,
            "security_requirement_exists": security_requirement_exists,
        }