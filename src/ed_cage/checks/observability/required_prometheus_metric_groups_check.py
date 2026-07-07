from typing import Any

import httpx

from ed_cage.checks.common.http_utils import (
    build_http_error_attempt,
    build_url,
    is_successful_attempt,
)
from ed_cage.checks.common.prometheus_utils import (
    find_metric_name_matches,
    has_error_signal,
    parse_prometheus_metric_names,
)
from ed_cage.checks.common.rule_param_utils import (
    get_float_param,
    get_int_set_param,
    get_string_list_param,
)
from ed_cage.domain.enums import CheckStatus
from ed_cage.domain.models import Evidence, GovernanceFinding, GovernanceRule, ProjectContext


class RequiredPrometheusMetricGroupsCheck:
    @property
    def check_type(self) -> str:
        return "required_prometheus_metric_groups"

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
        required_metric_groups = self._get_required_metric_groups(rule)

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
                            required_metric_groups=required_metric_groups,
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
                            "Service exposes required Prometheus metric group(s)."
                            if service_passed
                            else "Service does not expose required Prometheus metric group(s)."
                        ),
                        data={
                            "service": service.name,
                            "base_url": service.base_url,
                            "candidate_paths": candidate_paths,
                            "expected_status_codes": sorted(expected_status_codes),
                            "required_metric_groups": required_metric_groups,
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
                message=f"Required Prometheus metric group check failed for service(s): {', '.join(failed_services)}",
                evidence=evidence,
            )

        return GovernanceFinding(
            rule_id=rule.id,
            title=rule.title,
            severity=rule.severity,
            status=CheckStatus.PASSED,
            message="All services expose required Prometheus metric group(s).",
            evidence=evidence,
        )

    def _evaluate_response(
        self,
        url: str,
        status_code: int,
        response_text: str,
        expected_status_codes: set[int],
        required_metric_groups: dict[str, dict[str, Any]],
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

        if not metric_names:
            return {
                **base_attempt,
                "success": False,
                "failure_reason": "no_prometheus_metrics_found",
                "metric_count": 0,
            }

        matched_groups: dict[str, list[str]] = {}
        missing_groups: list[str] = []

        for group_name, group_config in required_metric_groups.items():
            patterns = group_config.get("patterns", [])

            if not isinstance(patterns, list):
                patterns = []

            normalized_patterns = [str(pattern) for pattern in patterns]

            if group_name == "error_metric":
                if has_error_signal(response_text, metric_names, normalized_patterns):
                    matched_groups[group_name] = self._find_error_metric_matches(
                        response_text=response_text,
                        metric_names=metric_names,
                        patterns=normalized_patterns,
                    )
                else:
                    missing_groups.append(group_name)

                continue

            matches = find_metric_name_matches(
                metric_names=metric_names,
                patterns=normalized_patterns,
            )

            if matches:
                matched_groups[group_name] = matches
            else:
                missing_groups.append(group_name)

        return {
            **base_attempt,
            "success": not missing_groups,
            "failure_reason": None if not missing_groups else "required_metric_groups_missing",
            "metric_count": len(metric_names),
            "matched_groups": matched_groups,
            "missing_groups": missing_groups,
            "metric_names_sample": sorted(metric_names)[:20],
        }

    def _get_required_metric_groups(
        self,
        rule: GovernanceRule,
    ) -> dict[str, dict[str, Any]]:
        raw_groups = rule.params.get("required_metric_groups", {})

        if not isinstance(raw_groups, dict):
            return {}

        normalized_groups: dict[str, dict[str, Any]] = {}

        for group_name, group_config in raw_groups.items():
            if not isinstance(group_config, dict):
                continue

            normalized_groups[str(group_name)] = group_config

        return normalized_groups

    def _find_error_metric_matches(
        self,
        response_text: str,
        metric_names: set[str],
        patterns: list[str],
    ) -> list[str]:
        metric_matches = find_metric_name_matches(
            metric_names=metric_names,
            patterns=patterns,
        )

        if metric_matches:
            return metric_matches

        if 'status="5' in response_text or 'code="5' in response_text:
            return ["status_or_code_5xx_label_detected"]

        if 'outcome="SERVER_ERROR"' in response_text:
            return ["server_error_outcome_label_detected"]

        if 'exception="' in response_text:
            return ["exception_label_detected"]

        return []