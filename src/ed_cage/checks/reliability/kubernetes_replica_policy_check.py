from typing import Any

from ed_cage.adapters.filesystem.kubernetes_manifest_loader import KubernetesManifestLoader
from ed_cage.checks.common.applicability import build_skipped_finding
from ed_cage.checks.common.kubernetes_utils import (
    get_file_patterns,
    get_manifest_paths,
    get_required_for_kinds,
)
from ed_cage.domain.enums import CheckStatus
from ed_cage.domain.models import Evidence, GovernanceFinding, GovernanceRule, ProjectContext


class KubernetesReplicaPolicyCheck:
    @property
    def check_type(self) -> str:
        return "kubernetes_replica_policy"

    def evaluate(self, rule: GovernanceRule, context: ProjectContext) -> GovernanceFinding:
        manifest_paths = get_manifest_paths(rule.params)
        file_patterns = get_file_patterns(rule.params)
        required_for_kinds = get_required_for_kinds(
            params=rule.params,
            default=["Deployment", "StatefulSet"],
        )
        minimum_replicas = int(rule.params.get("minimum_replicas", 2))
        critical_workload_names = self._get_string_set_param(
            params=rule.params,
            key="critical_workload_names",
            default=set(),
        )

        load_result = KubernetesManifestLoader(context.repository_path).load(
            manifest_paths=manifest_paths,
            file_patterns=file_patterns,
        )

        evaluated_workloads = 0
        evaluated_replicas: list[dict[str, object]] = []
        violations: list[dict[str, object]] = []
        skipped_workloads: list[dict[str, object]] = []

        for manifest in load_result.manifests:
            if manifest.kind not in required_for_kinds:
                skipped_workloads.append(
                    {
                        "resource_id": manifest.resource_id,
                        "reason": "kind_not_required_for_replica_policy",
                        "kind": manifest.kind,
                    }
                )
                continue

            if critical_workload_names and manifest.name not in critical_workload_names:
                skipped_workloads.append(
                    {
                        "resource_id": manifest.resource_id,
                        "reason": "not_in_critical_workload_names",
                        "kind": manifest.kind,
                        "name": manifest.name,
                    }
                )
                continue

            evaluated_workloads += 1

            spec = manifest.raw.get("spec")

            evaluated_replica = {
                "resource_id": manifest.resource_id,
                "kind": manifest.kind,
                "name": manifest.name,
                "minimum_replicas": minimum_replicas,
            }

            if not isinstance(spec, dict):
                violations.append(
                    {
                        **evaluated_replica,
                        "reason": "spec_missing_or_invalid",
                    }
                )
                continue

            replicas = spec.get("replicas")

            if replicas is None:
                replicas = 1

            evaluated_replica = {
                **evaluated_replica,
                "replicas": replicas,
            }
            evaluated_replicas.append(evaluated_replica)

            if not isinstance(replicas, int):
                violations.append(
                    {
                        **evaluated_replica,
                        "reason": "replicas_is_not_integer",
                    }
                )
                continue

            if replicas < minimum_replicas:
                violations.append(
                    {
                        **evaluated_replica,
                        "reason": "replica_count_below_minimum",
                    }
                )

        evidence_data = {
            "manifest_paths": manifest_paths,
            "file_patterns": file_patterns,
            "manifest_count": len(load_result.manifests),
            "required_for_kinds": sorted(required_for_kinds),
            "minimum_replicas": minimum_replicas,
            "critical_workload_names": sorted(critical_workload_names),
            "evaluated_workloads": evaluated_workloads,
            "evaluated_replicas": evaluated_replicas,
            "skipped_workloads": skipped_workloads,
            "violations": violations,
            "load_errors": [
                {
                    "path": str(error.path),
                    "message": error.message,
                }
                for error in load_result.errors
            ],
        }

        if evaluated_workloads == 0:
            return build_skipped_finding(
                rule=rule,
                message="No Kubernetes workloads were applicable for replica policy evaluation.",
                evidence_source="kubernetes-replica-policy",
                evidence_message=(
                    "Kubernetes replica policy evaluation skipped because no applicable "
                    "workloads were found."
                ),
                evidence_data=evidence_data,
            )

        evidence = [
            Evidence(
                source="kubernetes-replica-policy",
                message="Kubernetes replica policy evaluation completed.",
                data=evidence_data,
            )
        ]

        if violations:
            return GovernanceFinding(
                rule_id=rule.id,
                title=rule.title,
                severity=rule.severity,
                status=CheckStatus.FAILED,
                message=f"Kubernetes replica policy violations detected: {len(violations)}.",
                evidence=evidence,
            )

        return GovernanceFinding(
            rule_id=rule.id,
            title=rule.title,
            severity=rule.severity,
            status=CheckStatus.PASSED,
            message="Kubernetes replica policy passed.",
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