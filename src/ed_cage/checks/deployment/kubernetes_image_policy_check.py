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


class KubernetesImagePolicyCheck:
    @property
    def check_type(self) -> str:
        return "kubernetes_image_policy"

    def evaluate(
        self, rule: GovernanceRule, context: ProjectContext
    ) -> GovernanceFinding:
        manifest_paths = get_manifest_paths(rule.params)
        file_patterns = get_file_patterns(rule.params)

        disallowed_tags = self._get_string_set_param(
            params=rule.params,
            key="disallowed_tags",
            default={"latest"},
        )
        require_explicit_tag = bool(rule.params.get("require_explicit_tag", True))

        load_result = KubernetesManifestLoader(context.repository_path).load(
            manifest_paths=manifest_paths,
            file_patterns=file_patterns,
        )

        evaluated_containers = 0
        evaluated_images: list[dict[str, object]] = []
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
                image = str(container.get("image", "")).strip()
                image_tag = self._extract_image_tag(image)
                uses_digest = self._uses_digest(image)

                evaluated_image: dict[str, object] = {
                    "resource_id": manifest.resource_id,
                    "container_name": container_name,
                    "image": image,
                    "image_tag": image_tag,
                    "uses_digest": uses_digest,
                }
                evaluated_images.append(evaluated_image)

                if not image:
                    violations.append(
                        {
                            **evaluated_image,
                            "reason": "missing_image",
                        }
                    )
                    continue

                if require_explicit_tag and image_tag is None and not uses_digest:
                    violations.append(
                        {
                            **evaluated_image,
                            "reason": "missing_explicit_image_tag",
                        }
                    )
                    continue

                if image_tag is not None and image_tag in disallowed_tags:
                    violations.append(
                        {
                            **evaluated_image,
                            "reason": "latest_tag_is_not_allowed",
                            "disallowed_tags": sorted(disallowed_tags),
                        }
                    )

        evidence_data = {
            "manifest_paths": manifest_paths,
            "file_patterns": file_patterns,
            "manifest_count": len(load_result.manifests),
            "evaluated_containers": evaluated_containers,
            "evaluated_images": evaluated_images,
            "require_explicit_tag": require_explicit_tag,
            "disallowed_tags": sorted(disallowed_tags),
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
                message="No Kubernetes containers were applicable for image policy evaluation.",
                evidence_source="kubernetes-image-policy",
                evidence_message=(
                    "Kubernetes image policy evaluation skipped because no containers "
                    "were found."
                ),
                evidence_data=evidence_data,
            )

        evidence = [
            Evidence(
                source="kubernetes-image-policy",
                message="Kubernetes image policy evaluation completed.",
                data=evidence_data,
            )
        ]

        if violations:
            return GovernanceFinding(
                rule_id=rule.id,
                title=rule.title,
                severity=rule.severity,
                status=CheckStatus.FAILED,
                message=f"Kubernetes image policy violations detected: {len(violations)}.",
                evidence=evidence,
            )

        return GovernanceFinding(
            rule_id=rule.id,
            title=rule.title,
            severity=rule.severity,
            status=CheckStatus.PASSED,
            message="Container image policy passed for all evaluated containers.",
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

    def _extract_image_tag(self, image: str) -> str | None:
        if not image:
            return None

        image_without_digest = image.split("@", maxsplit=1)[0]
        last_slash_index = image_without_digest.rfind("/")
        last_colon_index = image_without_digest.rfind(":")

        if last_colon_index == -1:
            return None

        if last_colon_index < last_slash_index:
            return None

        tag = image_without_digest[last_colon_index + 1 :].strip()

        if not tag:
            return None

        return tag

    def _uses_digest(self, image: str) -> bool:
        return "@" in image and "sha256:" in image
