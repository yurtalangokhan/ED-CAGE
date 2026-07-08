import pytest

from ed_cage.application.check_registry import CheckRegistry
from ed_cage.domain.models import GovernanceFinding, GovernanceRule, ProjectContext


EXPECTED_DEFAULT_CHECK_TYPES = {
    "required_files",
    "http_health_endpoint",
    "openapi_spec",
    "openapi_document_policy",
    "metrics_endpoint",
    "prometheus_metrics_compatibility",
    "required_prometheus_metric_groups",
    "docker_compose_file_exists",
    "docker_compose_healthcheck_policy",
    "docker_compose_security_policy",
    "kubernetes_manifests_exist",
    "kubernetes_image_policy",
    "kubernetes_resource_policy",
    "kubernetes_probe",
    "kubernetes_security_context",
    "repository_secret_patterns",
    "kubernetes_ingress_tls",
    "kubernetes_service_exposure_policy",
    "kubernetes_replica_policy",
    "repository_configuration_patterns",
    "repository_required_paths",
    "architecture_catalog_policy",
    "external_tool",
}


def test_default_check_registry_contains_expected_check_types() -> None:
    registry = CheckRegistry.default()

    check_types = set(registry.check_types())

    assert check_types == EXPECTED_DEFAULT_CHECK_TYPES


def test_check_registry_returns_all_registered_checks() -> None:
    registry = CheckRegistry.default()

    checks = registry.all_checks()
    check_types = {check.check_type for check in checks}

    assert check_types == EXPECTED_DEFAULT_CHECK_TYPES
    assert len(checks) == len(EXPECTED_DEFAULT_CHECK_TYPES)


def test_check_registry_rejects_duplicate_check_types() -> None:
    with pytest.raises(ValueError, match="Duplicate check_type registered"):
        CheckRegistry(
            checks=[
                _DummyCheck("duplicate"),
                _DummyCheck("duplicate"),
            ]
        )


class _DummyCheck:
    def __init__(self, check_type: str) -> None:
        self._check_type = check_type

    @property
    def check_type(self) -> str:
        return self._check_type

    def evaluate(
        self,
        rule: GovernanceRule,
        context: ProjectContext,
    ) -> GovernanceFinding:
        raise NotImplementedError