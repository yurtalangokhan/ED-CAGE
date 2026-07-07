from pathlib import Path

from ed_cage.checks.reliability.kubernetes_replica_policy_check import (
    KubernetesReplicaPolicyCheck,
)
from ed_cage.domain.enums import CheckStatus, Severity
from ed_cage.domain.models import GovernanceRule, ProjectContext


def test_kubernetes_replica_policy_check_passes_when_replicas_meet_minimum(
    tmp_path: Path,
) -> None:
    _write_manifest(tmp_path, _deployment_manifest(replicas=2))

    finding = KubernetesReplicaPolicyCheck().evaluate(
        rule=_build_rule(),
        context=_build_context(tmp_path),
    )

    assert finding.status == CheckStatus.PASSED
    assert finding.evidence[0].data["evaluated_workloads"] == 1


def test_kubernetes_replica_policy_check_fails_when_replicas_below_minimum(
    tmp_path: Path,
) -> None:
    _write_manifest(tmp_path, _deployment_manifest(replicas=1))

    finding = KubernetesReplicaPolicyCheck().evaluate(
        rule=_build_rule(),
        context=_build_context(tmp_path),
    )

    assert finding.status == CheckStatus.FAILED

    violations = finding.evidence[0].data["violations"]
    assert violations[0]["reason"] == "replica_count_below_minimum"
    assert violations[0]["replicas"] == 1


def test_kubernetes_replica_policy_check_skips_non_critical_workload(
    tmp_path: Path,
) -> None:
    _write_manifest(tmp_path, _deployment_manifest(name="non-critical", replicas=1))

    finding = KubernetesReplicaPolicyCheck().evaluate(
        rule=_build_rule(critical_workload_names=["critical-api"]),
        context=_build_context(tmp_path),
    )

    assert finding.status == CheckStatus.SKIPPED
    assert finding.evidence[0].data["evaluated_workloads"] == 0


def _build_rule(
    critical_workload_names: list[str] | None = None,
) -> GovernanceRule:
    return GovernanceRule(
        id="REL-001",
        title="Critical Kubernetes workloads should define multiple replicas",
        category="reliability",
        severity=Severity.HIGH,
        target="kubernetes",
        check_type="kubernetes_replica_policy",
        params={
            "manifest_paths": ["k8s"],
            "file_patterns": ["*.yaml"],
            "required_for_kinds": ["Deployment", "StatefulSet"],
            "minimum_replicas": 2,
            "critical_workload_names": critical_workload_names or [],
        },
    )


def _build_context(repository_path: Path) -> ProjectContext:
    return ProjectContext(
        project_name="test",
        repository_path=repository_path,
        config_path=repository_path / "configs" / "ed-cage.yaml",
        services=[],
    )


def _write_manifest(tmp_path: Path, content: str) -> None:
    manifest_dir = tmp_path / "k8s"
    manifest_dir.mkdir(exist_ok=True)
    manifest_file = manifest_dir / "deployment.yaml"
    manifest_file.write_text(content, encoding="utf-8")


def _deployment_manifest(name: str = "critical-api", replicas: int = 2) -> str:
    return f"""
apiVersion: apps/v1
kind: Deployment
metadata:
  name: {name}
spec:
  replicas: {replicas}
  selector:
    matchLabels:
      app: {name}
  template:
    metadata:
      labels:
        app: {name}
    spec:
      containers:
        - name: app
          image: app:1.0.0
"""