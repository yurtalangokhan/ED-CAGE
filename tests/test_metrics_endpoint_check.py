from ed_cage.checks.observability.metrics_endpoint_check import MetricsEndpointCheck
from ed_cage.domain.enums import CheckStatus, Severity
from ed_cage.domain.models import GovernanceRule, ProjectContext, ServiceDefinition


def test_metrics_endpoint_check_passes_when_endpoint_returns_non_empty_body(
    http_test_server,
) -> None:
    http_test_server.set_text_response(
        path="/metrics",
        status_code=200,
        body="metric_one 1\n",
    )

    finding = MetricsEndpointCheck().evaluate(
        rule=_build_rule(),
        context=_build_context(http_test_server.base_url),
    )

    assert finding.status == CheckStatus.PASSED

    attempts = finding.evidence[0].data["attempts"]
    assert attempts[0]["success"] is True
    assert attempts[0]["response_size_bytes"] > 0


def test_metrics_endpoint_check_fails_when_endpoint_is_missing(
    http_test_server,
) -> None:
    finding = MetricsEndpointCheck().evaluate(
        rule=_build_rule(),
        context=_build_context(http_test_server.base_url),
    )

    assert finding.status == CheckStatus.FAILED

    attempts = finding.evidence[0].data["attempts"]
    assert attempts[0]["success"] is False
    assert attempts[0]["failure_reason"] == "unexpected_status_code"


def _build_rule() -> GovernanceRule:
    return GovernanceRule(
        id="SVC-003",
        title="Services must expose a metrics endpoint",
        category="observability",
        severity=Severity.HIGH,
        target="service",
        check_type="metrics_endpoint",
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