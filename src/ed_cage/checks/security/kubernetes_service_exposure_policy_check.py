from typing import Any

from ed_cage.adapters.filesystem.kubernetes_manifest_loader import (
    KubernetesManifestLoader,
)
from ed_cage.domain.enums import CheckStatus
from ed_cage.domain.models import (
    Evidence,
    GovernanceFinding,
    GovernanceRule,
    ProjectContext,
)
from ed_cage.checks.common.kubernetes_manifest_paths import (
    resolve_kubernetes_manifest_paths,
)
from ed_cage.checks.common.kubernetes_utils import get_file_patterns


class KubernetesServiceExposurePolicyCheck:
    @property
    def check_type(self) -> str:
        return "kubernetes_service_exposure_policy"

    def evaluate(
        self, rule: GovernanceRule, context: ProjectContext
    ) -> GovernanceFinding:
        manifest_paths = resolve_kubernetes_manifest_paths(
            rule=rule,
            context=context,
            existing_only=True,
        )
        file_patterns = get_file_patterns(rule.params)
        disallowed_service_types = self._get_string_set_param(
            params=rule.params,
            key="disallowed_service_types",
            default={"NodePort", "LoadBalancer"},
        )
        allowed_external_service_names = self._get_string_set_param(
            params=rule.params,
            key="allowed_external_service_names",
            default=set(),
        )

        load_result = KubernetesManifestLoader(context.repository_path).load(
            manifest_paths=manifest_paths,
            file_patterns=file_patterns,
        )

        services = [
            manifest for manifest in load_result.manifests if manifest.kind == "Service"
        ]

        if not services:
            return GovernanceFinding(
                rule_id=rule.id,
                title=rule.title,
                severity=rule.severity,
                status=CheckStatus.SKIPPED,
                message="No Kubernetes Service resources were found.",
                evidence=[
                    Evidence(
                        source="kubernetes-service-exposure-policy",
                        message="No Service resources were available for exposure evaluation.",
                        data={
                            "manifest_paths": manifest_paths,
                            "file_patterns": file_patterns,
                            "manifest_count": len(load_result.manifests),
                            "service_count": 0,
                            "load_errors": [
                                {
                                    "path": str(error.path),
                                    "message": error.message,
                                }
                                for error in load_result.errors
                            ],
                        },
                    )
                ],
            )

        violations: list[dict[str, object]] = []

        for service in services:
            spec = self._get_dict(service.raw.get("spec"))
            service_type = str(spec.get("type", "ClusterIP"))

            if (
                service_type in disallowed_service_types
                and service.name not in allowed_external_service_names
            ):
                violations.append(
                    {
                        "resource_id": service.resource_id,
                        "service_name": service.name,
                        "service_type": service_type,
                        "reason": "external_service_type_not_allowed",
                    }
                )

        evidence = [
            Evidence(
                source="kubernetes-service-exposure-policy",
                message="Kubernetes Service exposure policy evaluation completed.",
                data={
                    "manifest_paths": manifest_paths,
                    "file_patterns": file_patterns,
                    "manifest_count": len(load_result.manifests),
                    "service_count": len(services),
                    "disallowed_service_types": sorted(disallowed_service_types),
                    "allowed_external_service_names": sorted(
                        allowed_external_service_names
                    ),
                    "violations": violations,
                    "load_errors": [
                        {
                            "path": str(error.path),
                            "message": error.message,
                        }
                        for error in load_result.errors
                    ],
                },
            )
        ]

        if violations:
            return GovernanceFinding(
                rule_id=rule.id,
                title=rule.title,
                severity=rule.severity,
                status=CheckStatus.FAILED,
                message=(
                    "Kubernetes Service exposure policy violations detected: "
                    f"{len(violations)}."
                ),
                evidence=evidence,
            )

        return GovernanceFinding(
            rule_id=rule.id,
            title=rule.title,
            severity=rule.severity,
            status=CheckStatus.PASSED,
            message="Kubernetes Service exposure policy passed.",
            evidence=evidence,
        )

    def _get_string_set_param(
        self,
        params: dict[str, Any],
        key: str,
        default: set[str],
    ) -> set[str]:
        raw_value = params.get(key, sorted(default))

        if not isinstance(raw_value, list):
            return default

        return {str(item) for item in raw_value}

    def _get_dict(self, value: object) -> dict[str, Any]:
        if not isinstance(value, dict):
            return {}

        return value
