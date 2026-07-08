from pathlib import Path

from ed_cage.checks.common.kubernetes_manifest_paths import (
    describe_kubernetes_manifest_path_source,
    resolve_kubernetes_manifest_paths,
)
from ed_cage.domain.enums import Severity
from ed_cage.domain.models import GovernanceRule, ProjectContext


def test_resolver_prefers_context_kubernetes_manifest_paths(
    tmp_path: Path,
) -> None:
    rule_path = tmp_path / "examples" / "kubernetes"
    rule_path.mkdir(parents=True)

    context_path = tmp_path / "case-k8s"
    context_path.mkdir()

    rule = _build_rule(
        manifest_paths=[
            "examples/kubernetes",
        ]
    )

    context = _build_context(tmp_path)
    context.kubernetes_manifest_paths = [context_path]

    paths = resolve_kubernetes_manifest_paths(
        rule=rule,
        context=context,
        existing_only=True,
    )

    assert paths == [context_path.resolve()]


def test_resolver_falls_back_to_rule_manifest_paths(
    tmp_path: Path,
) -> None:
    manifest_dir = tmp_path / "custom-manifests"
    manifest_dir.mkdir()

    rule = _build_rule(
        manifest_paths=[
            "custom-manifests",
        ]
    )

    context = _build_context(tmp_path)

    paths = resolve_kubernetes_manifest_paths(
        rule=rule,
        context=context,
        existing_only=True,
    )

    assert paths == [manifest_dir.resolve()]


def test_resolver_can_return_non_existing_candidates(
    tmp_path: Path,
) -> None:
    rule = _build_rule(
        manifest_paths=[
            "missing-manifests",
        ]
    )

    context = _build_context(tmp_path)

    paths = resolve_kubernetes_manifest_paths(
        rule=rule,
        context=context,
        existing_only=False,
    )

    assert paths == [
        (tmp_path / "missing-manifests").resolve()
    ]


def test_describe_manifest_path_source_prefers_project_context(
    tmp_path: Path,
) -> None:
    context_path = tmp_path / "case-k8s"

    rule = _build_rule(
        manifest_paths=[
            "examples/kubernetes",
        ]
    )

    context = _build_context(tmp_path)
    context.kubernetes_manifest_paths = [context_path]

    description = describe_kubernetes_manifest_path_source(
        rule=rule,
        context=context,
    )

    assert description["source"] == "project_context"
    assert description["context_manifest_paths"] == [
        str(context_path)
    ]
    assert description["rule_manifest_paths"] == [
        "examples/kubernetes"
    ]


def test_describe_manifest_path_source_uses_rule_or_default(
    tmp_path: Path,
) -> None:
    rule = _build_rule(
        manifest_paths=[
            "examples/kubernetes",
        ]
    )

    context = _build_context(tmp_path)

    description = describe_kubernetes_manifest_path_source(
        rule=rule,
        context=context,
    )

    assert description["source"] == "rule_or_default"
    assert description["context_manifest_paths"] == []
    assert description["rule_manifest_paths"] == [
        "examples/kubernetes"
    ]


def _build_rule(manifest_paths: list[str]) -> GovernanceRule:
    return GovernanceRule(
        id="DEP-001",
        title="Kubernetes manifests must exist",
        description="Kubernetes manifests should exist.",
        category="deployment",
        severity=Severity.HIGH,
        target="kubernetes",
        check_type="kubernetes_manifests_exist",
        params={
            "manifest_paths": manifest_paths,
        },
    )


def _build_context(repository_path: Path) -> ProjectContext:
    return ProjectContext(
        project_name="test",
        repository_path=repository_path,
        config_path=repository_path / "ed-cage.yaml",
        services=[],
    )