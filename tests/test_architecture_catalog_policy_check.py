from pathlib import Path

from ed_cage.checks.architecture.architecture_catalog_policy_check import (
    ArchitectureCatalogPolicyCheck,
)
from ed_cage.domain.enums import CheckStatus, Severity
from ed_cage.domain.models import GovernanceRule, ProjectContext


def test_architecture_catalog_policy_check_passes_when_critical_services_declared(
    tmp_path: Path,
) -> None:
    _write_catalog(tmp_path, _valid_catalog())

    finding = ArchitectureCatalogPolicyCheck().evaluate(
        rule=_build_rule("ARCH-003", "require_critical_services"),
        context=_build_context(tmp_path),
    )

    assert finding.status == CheckStatus.PASSED

    evidence_data = finding.evidence[0].data
    assert evidence_data["critical_services"] == ["service-a"]


def test_architecture_catalog_policy_check_fails_when_dependencies_missing(
    tmp_path: Path,
) -> None:
    _write_catalog(
        tmp_path,
        """
services:
  - name: service-a
    owner: team-a
""",
    )

    finding = ArchitectureCatalogPolicyCheck().evaluate(
        rule=_build_rule("DEPEN-001", "require_declared_dependencies"),
        context=_build_context(tmp_path),
    )

    assert finding.status == CheckStatus.FAILED

    violations = finding.evidence[0].data["violations"]
    assert violations[0]["reason"] == "dependencies_field_missing"


def test_architecture_catalog_policy_check_detects_circular_dependencies(
    tmp_path: Path,
) -> None:
    _write_catalog(
        tmp_path,
        """
services:
  - name: service-a
    dependencies:
      - name: service-b
        dependency_type: service
        external: false
  - name: service-b
    dependencies:
      - name: service-a
        dependency_type: service
        external: false
""",
    )

    finding = ArchitectureCatalogPolicyCheck().evaluate(
        rule=_build_rule("DEPEN-002", "disallow_circular_dependencies"),
        context=_build_context(tmp_path),
    )

    assert finding.status == CheckStatus.FAILED

    cycles = finding.evidence[0].data["cycles"]
    assert cycles


def test_architecture_catalog_policy_check_fails_when_external_metadata_missing(
    tmp_path: Path,
) -> None:
    _write_catalog(
        tmp_path,
        """
services:
  - name: service-a
    dependencies:
      - name: payment-gateway
        dependency_type: external-api
        external: true
        owner: vendor-team
""",
    )

    finding = ArchitectureCatalogPolicyCheck().evaluate(
        rule=_build_rule(
            rule_id="DEPEN-003",
            policy="require_external_dependency_metadata",
            params={
                "required_metadata": ["owner", "sla"],
            },
        ),
        context=_build_context(tmp_path),
    )

    assert finding.status == CheckStatus.FAILED

    violations = finding.evidence[0].data["violations"]
    assert violations[0]["missing_metadata"] == ["sla"]


def test_architecture_catalog_policy_check_passes_for_valid_catalog(
    tmp_path: Path,
) -> None:
    _write_catalog(tmp_path, _valid_catalog())

    for rule_id, policy in [
        ("ARCH-003", "require_critical_services"),
        ("DEPEN-001", "require_declared_dependencies"),
        ("DEPEN-002", "disallow_circular_dependencies"),
        ("DEPEN-003", "require_external_dependency_metadata"),
    ]:
        finding = ArchitectureCatalogPolicyCheck().evaluate(
            rule=_build_rule(rule_id, policy),
            context=_build_context(tmp_path),
        )

        assert finding.status == CheckStatus.PASSED


def _build_rule(
    rule_id: str,
    policy: str,
    params: dict[str, object] | None = None,
) -> GovernanceRule:
    return GovernanceRule(
        id=rule_id,
        title=f"{rule_id} test rule",
        category="architecture" if rule_id.startswith("ARCH") else "dependency",
        severity=Severity.HIGH,
        target="architecture-catalog",
        check_type="architecture_catalog_policy",
        params={
            "policy": policy,
            "architecture_catalog_path": "configs/architecture/service-architecture.yaml",
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


def _write_catalog(tmp_path: Path, content: str) -> None:
    catalog_dir = tmp_path / "configs" / "architecture"
    catalog_dir.mkdir(parents=True)

    catalog_file = catalog_dir / "service-architecture.yaml"
    catalog_file.write_text(content, encoding="utf-8")


def _valid_catalog() -> str:
    return """
critical_services:
  - service-a

services:
  - name: service-a
    owner: team-a
    criticality: high
    dependencies:
      - name: service-b
        dependency_type: service
        external: false
        owner: team-b
        sla: internal
      - name: payment-gateway
        dependency_type: external-api
        external: true
        owner: vendor-team
        sla: 99.9

  - name: service-b
    owner: team-b
    criticality: medium
    dependencies: []
"""