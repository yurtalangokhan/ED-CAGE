from typing import Any

import httpx

from ed_cage.checks.common.http_utils import (
    build_http_error_attempt,
    build_url,
    is_successful_attempt,
)
from ed_cage.checks.common.rule_param_utils import (
    get_float_param,
    get_int_set_param,
    get_string_list_param,
)
from ed_cage.domain.enums import CheckStatus
from ed_cage.domain.models import Evidence, GovernanceFinding, GovernanceRule, ProjectContext


class OpenApiSpecCheck:
    @property
    def check_type(self) -> str:
        return "openapi_spec"

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
                            response=response,
                            expected_status_codes=expected_status_codes,
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
                            "Service exposes a valid OpenAPI specification."
                            if service_passed
                            else "Service does not expose a valid OpenAPI specification."
                        ),
                        data={
                            "service": service.name,
                            "base_url": service.base_url,
                            "candidate_paths": candidate_paths,
                            "expected_status_codes": sorted(expected_status_codes),
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
                message=f"OpenAPI specification check failed for service(s): {', '.join(failed_services)}",
                evidence=evidence,
            )

        return GovernanceFinding(
            rule_id=rule.id,
            title=rule.title,
            severity=rule.severity,
            status=CheckStatus.PASSED,
            message="All services expose a valid OpenAPI specification.",
            evidence=evidence,
        )

    def _evaluate_response(
        self,
        url: str,
        response: httpx.Response,
        expected_status_codes: set[int],
    ) -> dict[str, object]:
        base_attempt: dict[str, object] = {
            "url": url,
            "status_code": response.status_code,
            "expected_status_codes": sorted(expected_status_codes),
        }

        if response.status_code not in expected_status_codes:
            return {
                **base_attempt,
                "success": False,
                "failure_reason": "unexpected_status_code",
            }

        try:
            payload = response.json()
        except ValueError:
            return {
                **base_attempt,
                "success": False,
                "failure_reason": "invalid_json",
            }

        if not isinstance(payload, dict):
            return {
                **base_attempt,
                "success": False,
                "failure_reason": "json_payload_is_not_object",
            }

        spec_version = self._extract_spec_version(payload)

        if spec_version is None:
            return {
                **base_attempt,
                "success": False,
                "failure_reason": "missing_openapi_or_swagger_version",
                "document_keys": sorted(str(key) for key in payload.keys()),
            }

        return {
            **base_attempt,
            "success": True,
            "failure_reason": None,
            "spec_version": spec_version,
            "title": self._extract_title(payload),
            "path_count": self._count_paths(payload),
        }

    def _extract_spec_version(self, payload: dict[str, Any]) -> str | None:
        openapi_version = payload.get("openapi")
        swagger_version = payload.get("swagger")

        if openapi_version is not None:
            return str(openapi_version)

        if swagger_version is not None:
            return str(swagger_version)

        return None

    def _extract_title(self, payload: dict[str, Any]) -> str | None:
        info = payload.get("info")

        if not isinstance(info, dict):
            return None

        title = info.get("title")

        if title is None:
            return None

        return str(title)

    def _count_paths(self, payload: dict[str, Any]) -> int:
        paths = payload.get("paths")

        if not isinstance(paths, dict):
            return 0

        return len(paths)