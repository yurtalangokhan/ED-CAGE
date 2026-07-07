from pathlib import Path

from ed_cage.checks.deployment.kubernetes_image_policy_check import KubernetesImagePolicyCheck
from ed_cage.checks.deployment.kubernetes_probe_check import KubernetesProbeCheck
from ed_cage.checks.deployment.kubernetes_resource_policy_check import (
    KubernetesResourcePolicyCheck,
)
from ed_cage.checks.deployment.kubernetes_security_context_check import (
    KubernetesSecurityContextCheck,
)
from ed_cage.checks.reliability.kubernetes_replica_policy_check import (
    KubernetesReplicaPolicyCheck,
)
from ed_cage.domain.enums import CheckStatus, Severity
from ed_cage.domain.models import GovernanceRule, ProjectContext


def test_kubernetes_image_policy_skips_when_no_manifests(tmp_path: Path) -> None:
    finding = KubernetesImagePolicyCheck().evaluate(
        rule=_build_rule("DEP-002", "kubernetes_image_policy"),
        context=_build_context(tmp_path),
    )

    assert finding.status == CheckStatus.SKIPPED


def test_kubernetes_resource_policy_skips_when_no_manifests(tmp_path: Path) -> None:
    finding = KubernetesResourcePolicyCheck().evaluate(
        rule=_build_rule(
            "DEP-003",
            "kubernetes_resource_policy",
            params={
                "policy": "require_requests",
            },
        ),
        context=_build_context(tmp_path),
    )

    assert finding.status == CheckStatus.SKIPPED


def test_kubernetes_probe_policy_skips_when_no_manifests(tmp_path: Path) -> None:
    finding = KubernetesProbeCheck().evaluate(
        rule=_build_rule(
            "DEP-005",
            "kubernetes_probe",
            params={
                "probe_type": "readinessProbe",
            },
        ),
        context=_build_context(tmp_path),
    )

    assert finding.status == CheckStatus.SKIPPED


def test_kubernetes_security_context_policy_skips_when_no_manifests(
    tmp_path: Path,
) -> None:
    finding = KubernetesSecurityContextCheck().evaluate(
        rule=_build_rule(
            "DEP-007",
            "kubernetes_security_context",
            severity=Severity.CRITICAL,
            params={
                "policy": "disallow_privileged",
            },
        ),
        context=_build_context(tmp_path),
    )

    assert finding.status == CheckStatus.SKIPPED


def test_kubernetes_replica_policy_skips_when_no_manifests(tmp_path: Path) -> None:
    finding = KubernetesReplicaPolicyCheck().evaluate(
        rule=_build_rule(
            "REL-001",
            "kubernetes_replica_policy",
            params={
                "required_for_kinds": ["Deployment", "StatefulSet"],
                "minimum_replicas": 2,
            },
        ),
        context=_build_context(tmp_path),
    )

    assert finding.status == CheckStatus.SKIPPED


def _build_rule(
    rule_id: str,
    check_type: str,
    severity: Severity = Severity.HIGH,
    params: dict[str, object] | None = None,
) -> GovernanceRule:
    return GovernanceRule(
        id=rule_id,
        title=f"{rule_id} test rule",
        category="deployment",
        severity=severity,
        target="kubernetes",
        check_type=check_type,
        params={
            "manifest_paths": ["k8s"],
            "file_patterns": ["*.yaml", "*.yml"],
            **(params or {}),
        },
    )


def _build_context(repository_path: Path) -> ProjectContext:
    return ProjectContext(
        project_name="test",
        repository_path=repository_path,
        config_path=repository_path / "configs" / "ed-cage.yaml",
        services=[],
    )