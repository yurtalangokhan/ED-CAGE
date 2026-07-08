from ed_cage.adapters.filesystem.kubernetes_manifest_loader import (
    KubernetesManifestLoader,
)
from ed_cage.checks.common.kubernetes_manifest_paths import (
    resolve_kubernetes_manifest_paths,
)
from ed_cage.checks.common.kubernetes_utils import get_file_patterns
from ed_cage.domain.enums import CheckStatus
from ed_cage.domain.models import (
    Evidence,
    GovernanceFinding,
    GovernanceRule,
    ProjectContext,
)


class KubernetesManifestsExistCheck:
    @property
    def check_type(self) -> str:
        return "kubernetes_manifests_exist"

    def evaluate(
        self, rule: GovernanceRule, context: ProjectContext
    ) -> GovernanceFinding:
        candidate_manifest_paths = resolve_kubernetes_manifest_paths(
            rule=rule,
            context=context,
            existing_only=False,
        )
        existing_manifest_paths = [
            path
            for path in candidate_manifest_paths
            if path.exists()
        ]

        file_patterns = get_file_patterns(rule.params)
        minimum_manifest_count = int(rule.params.get("minimum_manifest_count", 1))

        load_result = KubernetesManifestLoader(context.repository_path).load(
            manifest_paths=existing_manifest_paths,
            file_patterns=file_patterns,
        )

        manifest_summaries = [
            {
                "resource_id": manifest.resource_id,
                "kind": manifest.kind,
                "name": manifest.name,
                "namespace": manifest.namespace,
                "path": str(manifest.path),
                "document_index": manifest.document_index,
            }
            for manifest in load_result.manifests
        ]

        errors = [
            {
                "path": str(error.path),
                "message": error.message,
            }
            for error in load_result.errors
        ]

        evidence = [
            Evidence(
                source="kubernetes-manifest-loader",
                message="Kubernetes manifest discovery completed.",
                data={
                    "candidate_manifest_paths": [
                        str(path)
                        for path in candidate_manifest_paths
                    ],
                    "existing_manifest_paths": [
                        str(path)
                        for path in existing_manifest_paths
                    ],
                    "file_patterns": file_patterns,
                    "searched_paths": [
                        str(path)
                        for path in load_result.searched_paths
                    ],
                    "candidate_files": [
                        str(path)
                        for path in load_result.candidate_files
                    ],
                    "manifest_count": len(load_result.manifests),
                    "minimum_manifest_count": minimum_manifest_count,
                    "manifests": manifest_summaries,
                    "errors": errors,
                },
            )
        ]

        if len(load_result.manifests) < minimum_manifest_count:
            return GovernanceFinding(
                rule_id=rule.id,
                title=rule.title,
                severity=rule.severity,
                status=CheckStatus.FAILED,
                message=(
                    "Kubernetes manifest discovery failed. "
                    f"Expected at least {minimum_manifest_count} manifest(s), "
                    f"found {len(load_result.manifests)}."
                ),
                evidence=evidence,
            )

        return GovernanceFinding(
            rule_id=rule.id,
            title=rule.title,
            severity=rule.severity,
            status=CheckStatus.PASSED,
            message=f"Kubernetes manifests found: {len(load_result.manifests)}.",
            evidence=evidence,
        )