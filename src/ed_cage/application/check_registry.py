from ed_cage.checks.deployment.kubernetes_image_policy_check import KubernetesImagePolicyCheck
from ed_cage.checks.deployment.kubernetes_manifests_exist_check import (
    KubernetesManifestsExistCheck,
)
from ed_cage.checks.deployment.kubernetes_probe_check import KubernetesProbeCheck
from ed_cage.checks.deployment.kubernetes_resource_policy_check import (
    KubernetesResourcePolicyCheck,
)
from ed_cage.checks.deployment.kubernetes_security_context_check import (
    KubernetesSecurityContextCheck,
)
from ed_cage.checks.observability.metrics_endpoint_check import MetricsEndpointCheck
from ed_cage.checks.observability.prometheus_metrics_compatibility_check import (
    PrometheusMetricsCompatibilityCheck,
)
from ed_cage.checks.observability.required_prometheus_metric_groups_check import (
    RequiredPrometheusMetricGroupsCheck,
)
from ed_cage.checks.repository.required_files_check import RequiredFilesCheck
from ed_cage.checks.service.http_health_endpoint_check import HttpHealthEndpointCheck
from ed_cage.checks.service.openapi_spec_check import OpenApiSpecCheck
from ed_cage.ports.check import GovernanceCheck
from ed_cage.checks.api.openapi_document_policy_check import OpenApiDocumentPolicyCheck
from ed_cage.checks.security.kubernetes_ingress_tls_check import KubernetesIngressTlsCheck
from ed_cage.checks.security.kubernetes_service_exposure_policy_check import (
    KubernetesServiceExposurePolicyCheck,
)
from ed_cage.checks.security.repository_secret_patterns_check import (
    RepositorySecretPatternsCheck,
)
from ed_cage.checks.reliability.kubernetes_replica_policy_check import (
    KubernetesReplicaPolicyCheck,
)
from ed_cage.checks.reliability.repository_configuration_patterns_check import (
    RepositoryConfigurationPatternsCheck,
)
from ed_cage.checks.architecture.architecture_catalog_policy_check import (
    ArchitectureCatalogPolicyCheck,
)
from ed_cage.checks.architecture.repository_required_paths_check import (
    RepositoryRequiredPathsCheck,
)

from ed_cage.application.tool_adapter_registry import ToolAdapterRegistry
from ed_cage.checks.tools.external_tool_check import ExternalToolCheck


class CheckRegistry:
    def __init__(self, checks: list[GovernanceCheck]) -> None:
        self._checks = checks
        self._validate_unique_check_types()

    @classmethod
    def default(cls) -> "CheckRegistry":
        return cls(
            checks=[
                RequiredFilesCheck(),
                HttpHealthEndpointCheck(),
                OpenApiSpecCheck(),
                OpenApiDocumentPolicyCheck(),
                MetricsEndpointCheck(),
                PrometheusMetricsCompatibilityCheck(),
                RequiredPrometheusMetricGroupsCheck(),
                KubernetesManifestsExistCheck(),
                KubernetesImagePolicyCheck(),
                KubernetesResourcePolicyCheck(),
                KubernetesProbeCheck(),
                KubernetesSecurityContextCheck(),
                RepositorySecretPatternsCheck(),
                KubernetesIngressTlsCheck(),
                KubernetesServiceExposurePolicyCheck(),
                KubernetesReplicaPolicyCheck(),
                RepositoryConfigurationPatternsCheck(),
                RepositoryRequiredPathsCheck(),
                ArchitectureCatalogPolicyCheck(),
                ExternalToolCheck(ToolAdapterRegistry.default()),
              
            ]
        )

    def all_checks(self) -> list[GovernanceCheck]:
        return list(self._checks)

    def check_types(self) -> list[str]:
        return sorted(check.check_type for check in self._checks)

    def _validate_unique_check_types(self) -> None:
        seen: set[str] = set()

        for check in self._checks:
            if check.check_type in seen:
                raise ValueError(f"Duplicate check_type registered: {check.check_type}")

            seen.add(check.check_type)