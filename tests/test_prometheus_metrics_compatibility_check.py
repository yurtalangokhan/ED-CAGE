from ed_cage.checks.observability.prometheus_metrics_compatibility_check import (
    PrometheusMetricsCompatibilityCheck,
)
from ed_cage.domain.enums import CheckStatus, Severity
from ed_cage.domain.models import GovernanceRule, ProjectContext, ServiceDefinition


def test_prometheus_metrics_compatibility_check_passes_for_prometheus_text(
    http_test_server,
) -> None:
    http_test_server.set_text_response(
        path="/metrics",
        status_code=200,
        body="""
# HELP http_requests_total Total requests.
# TYPE http_requests_total counter
http_requests_total{status="200"} 42
""",
    )

    finding = PrometheusMetricsCompatibilityCheck().evaluate(
        rule=_build_rule(),
        context=_build_context(http_test_server.base_url),
    )

    assert finding.status == CheckStatus.PASSED

    attempts = finding.evidence[0].data["attempts"]
    assert attempts[0]["success"] is True
    assert attempts[0]["metric_count"] == 1
    assert attempts[0]["metric_names_sample"] == ["http_requests_total"]


def test_prometheus_metrics_compatibility_check_fails_for_non_prometheus_text(
    http_test_server,
) -> None:
    http_test_server.set_text_response(
        path="/metrics",
        status_code=200,
        body="hello world",
    )

    finding = PrometheusMetricsCompatibilityCheck().evaluate(
        rule=_build_rule(),
        context=_build_context(http_test_server.base_url),
    )

    assert finding.status == CheckStatus.FAILED

    attempts = finding.evidence[0].data["attempts"]
    assert attempts[0]["success"] is False
    assert attempts[0]["failure_reason"] == "not_prometheus_compatible"


def _build_rule() -> GovernanceRule:
    return GovernanceRule(
        id="OBS-001",
        title="Metrics endpoint must be Prometheus-compatible",
        category="observability",
        severity=Severity.HIGH,
        target="service",
        check_type="prometheus_metrics_compatibility",
        params={
            "allowed_paths": ["/metrics"],
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
                metrics_paths=["/metrics"],
            )
        ],
    )