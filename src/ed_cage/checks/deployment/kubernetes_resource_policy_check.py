from typing import Any

from ed_cage.adapters.filesystem.kubernetes_manifest_loader import (
    KubernetesManifestLoader,
)
from ed_cage.checks.common.applicability import build_skipped_finding
from ed_cage.checks.common.kubernetes_manifest_paths import (
    resolve_kubernetes_manifest_paths,
)
from ed_cage.checks.common.kubernetes_utils import (
    get_all_containers,
    get_container_name,
    get_file_patterns,
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
        self,
        rule: GovernanceRule,
        context: ProjectContext,
    ) -> GovernanceFinding:
        manifest_paths = resolve_kubernetes_manifest_paths(
            rule=rule,
            context=context,
            existing_only=True,
        )
        file_patterns = get_file_patterns(rule.params)

        policy, configuration_error = self._resolve_policy(rule.params)
        if configuration_error is not None:
            evidence = [
                Evidence(
                    source="kubernetes-resource-policy",
                    message="Invalid Kubernetes resource policy configuration.",
                    data=configuration_error,
                )
            ]
            return GovernanceFinding(
                rule_id=rule.id,
                title=rule.title,
                severity=rule.severity,
                status=CheckStatus.ERROR,
                message=configuration_error["message"],
                evidence=evidence,
            )

        required_resources = self._get_string_set_param(
            params=rule.params,
            key="required_resources",
            default={"cpu", "memory"},
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
                message=(
                    "No Kubernetes containers were applicable for resource "
                    "policy evaluation."
                ),
                evidence_source="kubernetes-resource-policy",
                evidence_message=(
                    "Kubernetes resource policy evaluation skipped because no "
                    "containers were found."
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
                message=(
                    f"Kubernetes resource {resource_section} policy violations "
                    f"detected: {len(violations)}."
                ),
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

    def _resolve_policy(
        self,
        params: dict[str, Any],
    ) -> tuple[str, dict[str, object] | None]:
        """Resolve the canonical resource policy without silently changing intent.

        The canonical parameter is ``policy`` with one of:
        ``require_requests`` or ``require_limits``.

        ``required_resource_section`` is accepted as a backwards-compatible alias
        and maps ``requests``/``limits`` to the corresponding canonical policy.
        Conflicting canonical and legacy values are rejected as configuration
        errors instead of silently defaulting DEP-004 to request evaluation.
        """

        supported_policies = {"require_requests", "require_limits"}
        legacy_mapping = {
            "requests": "require_requests",
            "limits": "require_limits",
        }

        raw_policy = params.get("policy")
        raw_legacy_section = params.get("required_resource_section")

        canonical_policy: str | None = None
        if raw_policy is not None:
            canonical_policy = str(raw_policy).strip().lower()
            if canonical_policy not in supported_policies:
                return "require_requests", {
                    "message": (
                        "Unsupported Kubernetes resource policy: "
                        f"{canonical_policy}."
                    ),
                    "policy": canonical_policy,
                    "required_resource_section": raw_legacy_section,
                    "supported_policies": sorted(supported_policies),
                    "supported_legacy_sections": sorted(legacy_mapping),
                    "reason": "unsupported_policy",
                }

        legacy_policy: str | None = None
        if raw_legacy_section is not None:
            legacy_section = str(raw_legacy_section).strip().lower()
            legacy_policy = legacy_mapping.get(legacy_section)
            if legacy_policy is None:
                return "require_requests", {
                    "message": (
                        "Unsupported Kubernetes resource section: "
                        f"{legacy_section}."
                    ),
                    "policy": canonical_policy,
                    "required_resource_section": legacy_section,
                    "supported_policies": sorted(supported_policies),
                    "supported_legacy_sections": sorted(legacy_mapping),
                    "reason": "unsupported_legacy_resource_section",
                }

        if (
            canonical_policy is not None
            and legacy_policy is not None
            and canonical_policy != legacy_policy
        ):
            return "require_requests", {
                "message": (
                    "Conflicting Kubernetes resource policy parameters: "
                    f"policy={canonical_policy} and "
                    f"required_resource_section={raw_legacy_section}."
                ),
                "policy": canonical_policy,
                "required_resource_section": str(raw_legacy_section),
                "resolved_legacy_policy": legacy_policy,
                "supported_policies": sorted(supported_policies),
                "supported_legacy_sections": sorted(legacy_mapping),
                "reason": "conflicting_resource_policy_parameters",
            }

        if canonical_policy is not None:
            return canonical_policy, None
        if legacy_policy is not None:
            return legacy_policy, None

        # Backwards-compatible default for custom rules that omit both fields.
        return "require_requests", None

    def _get_string_set_param(
        self,
        params: dict[str, Any],
        key: str,
        default: set[str],
    ) -> set[str]:
        raw_value = params.get(key, sorted(default))
        if not isinstance(raw_value, list):
            return default
        return {
            str(item).strip()
            for item in raw_value
            if str(item).strip()
        }

    def _has_non_empty_value(self, value: object) -> bool:
        if value is None:
            return False
        if isinstance(value, str):
            return bool(value.strip())
        return True
