import pytest

from ed_cage.application.check_registry import CheckRegistry
from ed_cage.domain.models import GovernanceFinding, GovernanceRule, ProjectContext


def test_default_check_registry_contains_core_checks() -> None:
    registry = CheckRegistry.default()

    check_types = registry.check_types()

    assert "required_files" in check_types
    assert "http_health_endpoint" in check_types
    assert "openapi_spec" in check_types
    assert "openapi_document_policy" in check_types
    assert "metrics_endpoint" in check_types
    assert "prometheus_metrics_compatibility" in check_types
    assert "required_prometheus_metric_groups" in check_types
    assert "kubernetes_manifests_exist" in check_types
    assert "kubernetes_image_policy" in check_types
    assert "kubernetes_resource_policy" in check_types
    assert "kubernetes_probe" in check_types
    assert "kubernetes_security_context" in check_types
    assert "repository_secret_patterns" in check_types
    assert "kubernetes_ingress_tls" in check_types
    assert "kubernetes_service_exposure_policy" in check_types
    assert "kubernetes_replica_policy" in check_types
    assert "repository_configuration_patterns" in check_types
    assert "repository_required_paths" in check_types
    assert "architecture_catalog_policy" in check_types


def test_check_registry_returns_all_registered_checks() -> None:
    registry = CheckRegistry.default()

    checks = registry.all_checks()

    assert len(checks) == 19


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