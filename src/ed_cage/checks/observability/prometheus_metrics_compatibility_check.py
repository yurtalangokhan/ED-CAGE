import httpx

from ed_cage.checks.common.http_utils import (
    build_http_error_attempt,
    build_url,
    is_successful_attempt,
)
from ed_cage.checks.common.prometheus_utils import (
    is_prometheus_compatible,
    parse_prometheus_metric_names,
)
from ed_cage.checks.common.rule_param_utils import (
    get_float_param,
    get_int_set_param,
    get_string_list_param,
)
from ed_cage.domain.enums import CheckStatus
from ed_cage.domain.models import Evidence, GovernanceFinding, GovernanceRule, ProjectContext


class PrometheusMetricsCompatibilityCheck:
    @property
    def check_type(self) -> str:
        return "prometheus_metrics_compatibility"

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
            default=["/metrics", "/actuator/prometheus"],
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
                candidate_paths = service.metrics_paths or allowed_paths
                service_passed = False
                attempts: list[dict[str, object]] = []

                for path in candidate_paths:
                    url = build_url(service.base_url, path)

                    try:
                        response = client.get(url)
                        attempt = self._evaluate_response(
                            url=url,
                            status_code=response.status_code,
                            response_text=response.text,
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
                            "Service exposes Prometheus-compatible metrics."
                            if service_passed
                            else "Service does not expose Prometheus-compatible metrics."
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
                message=f"Prometheus metrics compatibility check failed for service(s): {', '.join(failed_services)}",
                evidence=evidence,
            )

        return GovernanceFinding(
            rule_id=rule.id,
            title=rule.title,
            severity=rule.severity,
            status=CheckStatus.PASSED,
            message="All services expose Prometheus-compatible metrics.",
            evidence=evidence,
        )

    def _evaluate_response(
        self,
        url: str,
        status_code: int,
        response_text: str,
        expected_status_codes: set[int],
    ) -> dict[str, object]:
        base_attempt: dict[str, object] = {
            "url": url,
            "status_code": status_code,
            "expected_status_codes": sorted(expected_status_codes),
        }

        if status_code not in expected_status_codes:
            return {
                **base_attempt,
                "success": False,
                "failure_reason": "unexpected_status_code",
            }

        metric_names = parse_prometheus_metric_names(response_text)

        if not is_prometheus_compatible(response_text):
            return {
                **base_attempt,
                "success": False,
                "failure_reason": "not_prometheus_compatible",
                "metric_count": 0,
            }

        return {
            **base_attempt,
            "success": True,
            "failure_reason": None,
            "metric_count": len(metric_names),
            "metric_names_sample": sorted(metric_names)[:20],
        }