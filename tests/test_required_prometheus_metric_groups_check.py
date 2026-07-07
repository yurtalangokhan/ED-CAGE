from ed_cage.checks.observability.required_prometheus_metric_groups_check import (
    RequiredPrometheusMetricGroupsCheck,
)
from ed_cage.domain.enums import CheckStatus, Severity
from ed_cage.domain.models import GovernanceRule, ProjectContext, ServiceDefinition


def test_required_prometheus_metric_groups_check_passes_when_metric_exists(
    http_test_server,
) -> None:
    http_test_server.set_text_response(
        path="/metrics",
        status_code=200,
        body="""
http_requests_total{status="200"} 42
http_request_duration_seconds_sum 1.5
""",
    )

    finding = RequiredPrometheusMetricGroupsCheck().evaluate(
        rule=_build_rule(
            required_metric_groups={
                "request_count": {
                    "patterns": [
                        "^http_requests_total$",
                    ]
                }
            }
        ),
        context=_build_context(http_test_server.base_url),
    )

    assert finding.status == CheckStatus.PASSED

    attempts = finding.evidence[0].data["attempts"]
    assert attempts[0]["success"] is True
    assert attempts[0]["matched_groups"] == {
        "request_count": ["http_requests_total"],
    }


def test_required_prometheus_metric_groups_check_fails_when_metric_is_missing(
    http_test_server,
) -> None:
    http_test_server.set_text_response(
        path="/metrics",
        status_code=200,
        body="process_cpu_seconds_total 12.5\n",
    )

    finding = RequiredPrometheusMetricGroupsCheck().evaluate(
        rule=_build_rule(
            required_metric_groups={
                "request_count": {
                    "patterns": [
                        "^http_requests_total$",
                    ]
                }
            }
        ),
        context=_build_context(http_test_server.base_url),
    )

    assert finding.status == CheckStatus.FAILED

    attempts = finding.evidence[0].data["attempts"]
    assert attempts[0]["success"] is False
    assert attempts[0]["missing_groups"] == ["request_count"]


def test_required_prometheus_metric_groups_check_detects_error_signal_from_status_label(
    http_test_server,
) -> None:
    http_test_server.set_text_response(
        path="/metrics",
        status_code=200,
        body='http_requests_total{status="500"} 2\n',
    )

    finding = RequiredPrometheusMetricGroupsCheck().evaluate(
        rule=_build_rule(
            required_metric_groups={
                "error_metric": {
                    "patterns": [
                        "^errors_total$",
                    ]
                }
            }
        ),
        context=_build_context(http_test_server.base_url),
    )

    assert finding.status == CheckStatus.PASSED

    attempts = finding.evidence[0].data["attempts"]
    assert attempts[0]["success"] is True
    assert attempts[0]["matched_groups"] == {
        "error_metric": ["status_or_code_5xx_label_detected"],
    }


def _build_rule(required_metric_groups: dict[str, object]) -> GovernanceRule:
    return GovernanceRule(
        id="OBS-002",
        title="Metrics must include request count metric",
        category="observability",
        severity=Severity.MEDIUM,
        target="service",
        check_type="required_prometheus_metric_groups",
        params={
            "allowed_paths": ["/metrics"],
            "expected_status_codes": [200],
            "timeout_seconds": 3,
            "required_metric_groups": required_metric_groups,
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
                metrics_paths=["/metrics"],
            )
        ],
    )