from pathlib import Path
from typing import Any

from ed_cage.domain.models import GovernanceRule, ProjectContext


DEFAULT_KUBERNETES_MANIFEST_PATHS = [
    "k8s",
    "kubernetes",
    "deploy",
    "deployments",
    "manifests",
    "examples/kubernetes",
    "release",
]


def resolve_kubernetes_manifest_paths(
    rule: GovernanceRule,
    context: ProjectContext,
    *,
    existing_only: bool = True,
) -> list[Path]:
    """
    Resolve Kubernetes manifest paths for governance checks.

    Resolution priority:
    1. ProjectContext.kubernetes_manifest_paths
    2. rule.params.manifest_paths
    3. DEFAULT_KUBERNETES_MANIFEST_PATHS under repository_path

    existing_only=True:
        Return only paths that currently exist.

    existing_only=False:
        Return configured candidate paths even if they do not exist.
        This is useful for DEP-001-like checks that must fail when
        required manifests are missing.
    """

    if context.kubernetes_manifest_paths:
        return _filter_existing_paths(
            paths=[path.resolve() for path in context.kubernetes_manifest_paths],
            existing_only=existing_only,
        )

    configured_paths = _get_manifest_paths_from_rule(rule)

    resolved_paths: list[Path] = []

    for manifest_path in configured_paths:
        candidate_path = Path(manifest_path)

        if candidate_path.is_absolute():
            resolved_path = candidate_path.resolve()
        else:
            resolved_path = (context.repository_path / candidate_path).resolve()

        resolved_paths.append(resolved_path)

    return _filter_existing_paths(
        paths=resolved_paths,
        existing_only=existing_only,
    )


def describe_kubernetes_manifest_path_source(
    rule: GovernanceRule,
    context: ProjectContext,
) -> dict[str, Any]:
    if context.kubernetes_manifest_paths:
        return {
            "source": "project_context",
            "context_manifest_paths": [
                str(path)
                for path in context.kubernetes_manifest_paths
            ],
            "rule_manifest_paths": _get_manifest_paths_from_rule(rule),
        }

    return {
        "source": "rule_or_default",
        "context_manifest_paths": [],
        "rule_manifest_paths": _get_manifest_paths_from_rule(rule),
    }


def _get_manifest_paths_from_rule(rule: GovernanceRule) -> list[str]:
    raw_paths = rule.params.get(
        "manifest_paths",
        DEFAULT_KUBERNETES_MANIFEST_PATHS,
    )

    if not isinstance(raw_paths, list):
        return DEFAULT_KUBERNETES_MANIFEST_PATHS

    paths = [
        str(path).strip()
        for path in raw_paths
        if str(path).strip()
    ]

    return paths or DEFAULT_KUBERNETES_MANIFEST_PATHS


def _filter_existing_paths(
    paths: list[Path],
    *,
    existing_only: bool,
) -> list[Path]:
    if not existing_only:
        return paths

    return [
        path
        for path in paths
        if path.exists()
    ]