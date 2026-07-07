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
    get_required_for_kinds,
)
from ed_cage.domain.enums import CheckStatus
from ed_cage.domain.models import (
    Evidence,
    GovernanceFinding,
    GovernanceRule,
    ProjectContext,
)


class KubernetesSecurityContextCheck:
    @property
    def check_type(self) -> str:
        return "kubernetes_security_context"

    def evaluate(
        self, rule: GovernanceRule, context: ProjectContext
    ) -> GovernanceFinding:
        manifest_paths = get_manifest_paths(rule.params)
        file_patterns = get_file_patterns(rule.params)
        required_for_kinds = get_required_for_kinds(
            params=rule.params,
            default=["Deployment", "StatefulSet", "DaemonSet", "Job", "CronJob", "Pod"],
        )
        policy = str(rule.params.get("policy", "")).strip()

        if policy not in {"disallow_privileged", "require_run_as_non_root"}:
            evidence = [
                Evidence(
                    source="kubernetes-security-context-policy",
                    message="Unsupported Kubernetes security context policy.",
                    data={
                        "policy": policy,
                        "supported_policies": [
                            "disallow_privileged",
                            "require_run_as_non_root",
                        ],
                    },
                )
            ]

            return GovernanceFinding(
                rule_id=rule.id,
                title=rule.title,
                severity=rule.severity,
                status=CheckStatus.ERROR,
                message=f"Unsupported Kubernetes security context policy: {policy}.",
                evidence=evidence,
            )

        load_result = KubernetesManifestLoader(context.repository_path).load(
            manifest_paths=manifest_paths,
            file_patterns=file_patterns,
        )

        evaluated_workloads = 0
        evaluated_containers = 0
        evaluated_resources: list[dict[str, object]] = []
        skipped_manifests: list[dict[str, object]] = []
        violations: list[dict[str, object]] = []

        for manifest in load_result.manifests:
            if manifest.kind not in required_for_kinds:
                skipped_manifests.append(
                    {
                        "resource_id": manifest.resource_id,
                        "reason": "kind_not_required_for_security_context_policy",
                        "kind": manifest.kind,
                    }
                )
                continue

            pod_spec = get_pod_spec(manifest.raw)

            if pod_spec is None:
                skipped_manifests.append(
                    {
                        "resource_id": manifest.resource_id,
                        "reason": "pod_spec_missing",
                        "kind": manifest.kind,
                    }
                )
                continue

            containers = get_all_containers(pod_spec)

            if not containers:
                skipped_manifests.append(
                    {
                        "resource_id": manifest.resource_id,
                        "reason": "containers_missing",
                        "kind": manifest.kind,
                    }
                )
                continue

            evaluated_workloads += 1
            pod_security_context = self._as_dict(pod_spec.get("securityContext"))

            for container in containers:
                if not isinstance(container, dict):
                    continue

                evaluated_containers += 1

                container_name = get_container_name(container)
                container_security_context = self._as_dict(
                    container.get("securityContext")
                )

                evaluated_resource: dict[str, object] = {
                    "resource_id": manifest.resource_id,
                    "container_name": container_name,
                    "policy": policy,
                    "pod_security_context": pod_security_context,
                    "container_security_context": container_security_context,
                }
                evaluated_resources.append(evaluated_resource)

                if policy == "disallow_privileged":
                    if container_security_context.get("privileged") is True:
                        violations.append(
                            {
                                **evaluated_resource,
                                "reason": "privileged_container_is_not_allowed",
                            }
                        )

                if policy == "require_run_as_non_root":
                    if not self._runs_as_non_root(
                        pod_security_context=pod_security_context,
                        container_security_context=container_security_context,
                    ):
                        violations.append(
                            {
                                **evaluated_resource,
                                "reason": "run_as_non_root_not_enforced",
                            }
                        )

        evidence_data = {
            "manifest_paths": manifest_paths,
            "file_patterns": file_patterns,
            "manifest_count": len(load_result.manifests),
            "required_for_kinds": sorted(required_for_kinds),
            "policy": policy,
            "evaluated_workloads": evaluated_workloads,
            "evaluated_containers": evaluated_containers,
            "evaluated_resources": evaluated_resources,
            "skipped_manifests": skipped_manifests,
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
                    "No Kubernetes workloads or containers were applicable for "
                    "security context evaluation."
                ),
                evidence_source="kubernetes-security-context-policy",
                evidence_message=(
                    "Kubernetes security context evaluation skipped because no applicable "
                    "resources were found."
                ),
                evidence_data=evidence_data,
            )

        evidence = [
            Evidence(
                source="kubernetes-security-context-policy",
                message="Kubernetes security context policy evaluation completed.",
                data=evidence_data,
            )
        ]

        if violations:
            return GovernanceFinding(
                rule_id=rule.id,
                title=rule.title,
                severity=rule.severity,
                status=CheckStatus.FAILED,
                message=f"Kubernetes security context policy violations detected: {len(violations)}.",
                evidence=evidence,
            )

        return GovernanceFinding(
            rule_id=rule.id,
            title=rule.title,
            severity=rule.severity,
            status=CheckStatus.PASSED,
            message=f"Kubernetes security context policy passed: {policy}.",
            evidence=evidence,
        )

    def _as_dict(self, value: object) -> dict[str, Any]:
        if isinstance(value, dict):
            return value

        return {}

    def _runs_as_non_root(
        self,
        pod_security_context: dict[str, Any],
        container_security_context: dict[str, Any],
    ) -> bool:
        container_run_as_non_root = container_security_context.get("runAsNonRoot")
        pod_run_as_non_root = pod_security_context.get("runAsNonRoot")

        if container_run_as_non_root is True:
            return True

        if container_run_as_non_root is False:
            return False

        if pod_run_as_non_root is True:
            return True

        if pod_run_as_non_root is False:
            return False

        container_run_as_user = container_security_context.get("runAsUser")
        pod_run_as_user = pod_security_context.get("runAsUser")

        if isinstance(container_run_as_user, int):
            return container_run_as_user > 0

        if isinstance(pod_run_as_user, int):
            return pod_run_as_user > 0

        return False
