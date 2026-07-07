from typing import Any

from ed_cage.adapters.filesystem.kubernetes_manifest_loader import (
    KubernetesManifestLoader,
)
from ed_cage.checks.common.applicability import build_skipped_finding
from ed_cage.checks.common.kubernetes_utils import (
    get_all_containers,
    get_container_name,
    get_file_patterns,
    get_manifest_paths,
    get_pod_spec,
)
from ed_cage.domain.enums import CheckStatus
from ed_cage.domain.models import (
    Evidence,
    GovernanceFinding,
    GovernanceRule,
    ProjectContext,
)


class KubernetesResourcePolicyCheck:
    @property
    def check_type(self) -> str:
        return "kubernetes_resource_policy"

    def evaluate(
        self, rule: GovernanceRule, context: ProjectContext
    ) -> GovernanceFinding:
        manifest_paths = get_manifest_paths(rule.params)
        file_patterns = get_file_patterns(rule.params)
        policy = str(rule.params.get("policy", "require_requests")).strip().lower()

        required_resources = self._get_string_set_param(
            params=rule.params,
            key="required_resources",
            default={"cpu", "memory"},
        )

        if policy not in {"require_requests", "require_limits"}:
            evidence = [
                Evidence(
                    source="kubernetes-resource-policy",
                    message="Unsupported Kubernetes resource policy.",
                    data={
                        "policy": policy,
                        "supported_policies": [
                            "require_requests",
                            "require_limits",
                        ],
                    },
                )
            ]

            return GovernanceFinding(
                rule_id=rule.id,
                title=rule.title,
                severity=rule.severity,
                status=CheckStatus.ERROR,
                message=f"Unsupported Kubernetes resource policy: {policy}.",
                evidence=evidence,
            )

        resource_section = "requests" if policy == "require_requests" else "limits"

        load_result = KubernetesManifestLoader(context.repository_path).load(
            manifest_paths=manifest_paths,
            file_patterns=file_patterns,
        )

        evaluated_containers = 0
        evaluated_resources: list[dict[str, object]] = []
        violations: list[dict[str, object]] = []

        for manifest in load_result.manifests:
            pod_spec = get_pod_spec(manifest.raw)

            if pod_spec is None:
                continue

            containers = get_all_containers(pod_spec)

            for container in containers:
                if not isinstance(container, dict):
                    continue

                evaluated_containers += 1

                container_name = get_container_name(container)
                resources = container.get("resources")

                evaluated_resource: dict[str, object] = {
                    "resource_id": manifest.resource_id,
                    "container_name": container_name,
                    "policy": policy,
                    "resource_section": resource_section,
                    "required_resources": sorted(required_resources),
                }
                evaluated_resources.append(evaluated_resource)

                if not isinstance(resources, dict):
                    violations.append(
                        {
                            **evaluated_resource,
                            "reason": "resources_section_missing",
                        }
                    )
                    continue

                selected_resource_section = resources.get(resource_section)

                if not isinstance(selected_resource_section, dict):
                    violations.append(
                        {
                            **evaluated_resource,
                            "reason": f"{resource_section}_section_missing",
                            "missing_resources": sorted(required_resources),
                            "actual_values": {},
                        }
                    )
                    continue

                missing_resources = [
                    resource_name
                    for resource_name in sorted(required_resources)
                    if not self._has_non_empty_value(
                        selected_resource_section.get(resource_name)
                    )
                ]

                if missing_resources:
                    violations.append(
                        {
                            **evaluated_resource,
                            "reason": f"required_{resource_section}_missing",
                            "missing_resources": missing_resources,
                            "actual_values": {
                                resource_name: selected_resource_section.get(
                                    resource_name
                                )
                                for resource_name in sorted(required_resources)
                            },
                        }
                    )

        evidence_data = {
            "manifest_paths": manifest_paths,
            "file_patterns": file_patterns,
            "manifest_count": len(load_result.manifests),
            "evaluated_containers": evaluated_containers,
            "evaluated_resources": evaluated_resources,
            "policy": policy,
            "resource_section": resource_section,
            "required_resources": sorted(required_resources),
            "violations": violations,
            "load_errors": [
                {
                    "path": str(error.path),
                    "message": error.message,
                }
                for error in load_result.errors
            ],
        }

        if evaluated_containers == 0:
            return build_skipped_finding(
                rule=rule,
                message="No Kubernetes containers were applicable for resource policy evaluation.",
                evidence_source="kubernetes-resource-policy",
                evidence_message=(
                    "Kubernetes resource policy evaluation skipped because no containers "
                    "were found."
                ),
                evidence_data=evidence_data,
            )

        evidence = [
            Evidence(
                source="kubernetes-resource-policy",
                message="Kubernetes resource policy evaluation completed.",
                data=evidence_data,
            )
        ]

        if violations:
            return GovernanceFinding(
                rule_id=rule.id,
                title=rule.title,
                severity=rule.severity,
                status=CheckStatus.FAILED,
                message=f"Kubernetes resource {resource_section} policy violations detected: {len(violations)}.",
                evidence=evidence,
            )

        return GovernanceFinding(
            rule_id=rule.id,
            title=rule.title,
            severity=rule.severity,
            status=CheckStatus.PASSED,
            message=f"Kubernetes resource {resource_section} policy passed.",
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

        return {str(item).strip() for item in raw_value if str(item).strip()}

    def _has_non_empty_value(self, value: object) -> bool:
        if value is None:
            return False

        if isinstance(value, str):
            return bool(value.strip())

        return True
