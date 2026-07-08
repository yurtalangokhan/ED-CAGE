from ed_cage.adapters.filesystem.kubernetes_manifest_loader import (
    KubernetesManifestLoader,
)
from ed_cage.checks.common.applicability import build_skipped_finding
from ed_cage.checks.common.kubernetes_utils import (
    get_all_containers,
    get_container_name,
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
from ed_cage.checks.common.kubernetes_manifest_paths import (
    resolve_kubernetes_manifest_paths,
)
from ed_cage.checks.common.kubernetes_utils import get_file_patterns


class KubernetesProbeCheck:
    @property
    def check_type(self) -> str:
        return "kubernetes_probe"

    def evaluate(
        self, rule: GovernanceRule, context: ProjectContext
    ) -> GovernanceFinding:
        manifest_paths = resolve_kubernetes_manifest_paths(
            rule=rule,
            context=context,
            existing_only=True,
        )
        file_patterns = get_file_patterns(rule.params)
        required_for_kinds = get_required_for_kinds(
            params=rule.params,
            default=["Deployment", "StatefulSet", "DaemonSet"],
        )
        probe_type = str(rule.params.get("probe_type", "readinessProbe")).strip()

        if probe_type not in {"readinessProbe", "livenessProbe", "startupProbe"}:
            evidence = [
                Evidence(
                    source="kubernetes-probe-policy",
                    message="Unsupported Kubernetes probe type.",
                    data={
                        "probe_type": probe_type,
                        "supported_probe_types": [
                            "readinessProbe",
                            "livenessProbe",
                            "startupProbe",
                        ],
                    },
                )
            ]

            return GovernanceFinding(
                rule_id=rule.id,
                title=rule.title,
                severity=rule.severity,
                status=CheckStatus.ERROR,
                message=f"Unsupported Kubernetes probe type: {probe_type}.",
                evidence=evidence,
            )

        load_result = KubernetesManifestLoader(context.repository_path).load(
            manifest_paths=manifest_paths,
            file_patterns=file_patterns,
        )

        evaluated_workloads = 0
        evaluated_containers = 0
        evaluated_probes: list[dict[str, object]] = []
        violations: list[dict[str, object]] = []
        skipped_manifests: list[dict[str, object]] = []

        for manifest in load_result.manifests:
            if manifest.kind not in required_for_kinds:
                skipped_manifests.append(
                    {
                        "resource_id": manifest.resource_id,
                        "reason": "kind_not_required_for_probe_policy",
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

            for container in containers:
                if not isinstance(container, dict):
                    continue

                evaluated_containers += 1
                container_name = get_container_name(container)
                probe = container.get(probe_type)

                evaluated_probe = {
                    "resource_id": manifest.resource_id,
                    "container_name": container_name,
                    "probe_type": probe_type,
                    "has_probe": isinstance(probe, dict),
                }
                evaluated_probes.append(evaluated_probe)

                if not isinstance(probe, dict):
                    violations.append(
                        {
                            **evaluated_probe,
                            "reason": f"{probe_type}_missing",
                            "missing_probe": probe_type,
                        }
                    )

        evidence_data = {
            "manifest_paths": manifest_paths,
            "file_patterns": file_patterns,
            "manifest_count": len(load_result.manifests),
            "required_for_kinds": sorted(required_for_kinds),
            "probe_type": probe_type,
            "evaluated_workloads": evaluated_workloads,
            "evaluated_containers": evaluated_containers,
            "evaluated_probes": evaluated_probes,
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
                message="No Kubernetes workloads were applicable for probe policy evaluation.",
                evidence_source="kubernetes-probe-policy",
                evidence_message=(
                    "Kubernetes probe policy evaluation skipped because no applicable "
                    "workloads or containers were found."
                ),
                evidence_data=evidence_data,
            )

        evidence = [
            Evidence(
                source="kubernetes-probe-policy",
                message="Kubernetes probe policy evaluation completed.",
                data=evidence_data,
            )
        ]

        if violations:
            return GovernanceFinding(
                rule_id=rule.id,
                title=rule.title,
                severity=rule.severity,
                status=CheckStatus.FAILED,
                message=f"Kubernetes {probe_type} policy violations detected: {len(violations)}.",
                evidence=evidence,
            )

        return GovernanceFinding(
            rule_id=rule.id,
            title=rule.title,
            severity=rule.severity,
            status=CheckStatus.PASSED,
            message=f"Kubernetes {probe_type} policy passed.",
            evidence=evidence,
        )
