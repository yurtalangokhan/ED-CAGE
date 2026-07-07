from pathlib import Path

from ed_cage.checks.architecture.architecture_catalog_policy_check import (
    ArchitectureCatalogPolicyCheck,
)
from ed_cage.domain.enums import CheckStatus, Severity
from ed_cage.domain.models import GovernanceRule, ProjectContext


def test_architecture_catalog_policy_check_uses_context_catalog_override(
    tmp_path: Path,
) -> None:
    repository_path = tmp_path / "repository"
    repository_path.mkdir()

    external_catalog_path = tmp_path / "catalogs" / "service-architecture.yaml"
    external_catalog_path.parent.mkdir()

    external_catalog_path.write_text(
        """
critical_services:
  - service-a

services:
  - name: service-a
    owner: team-a
    criticality: high
    dependencies: []
""",
        encoding="utf-8",
    )

    finding = ArchitectureCatalogPolicyCheck().evaluate(
        rule=GovernanceRule(
            id="ARCH-003",
            title="Critical services must be declared",
            category="architecture",
            severity=Severity.HIGH,
            target="architecture-catalog",
            check_type="architecture_catalog_policy",
            params={
                "policy": "require_critical_services",
                "architecture_catalog_path": "configs/architecture/missing.yaml",
            },
        ),
        context=ProjectContext(
            project_name="test",
            repository_path=repository_path,
            config_path=repository_path / "configs" / "ed-cage.yaml",
            services=[],
            architecture_catalog_path=external_catalog_path,
        ),
    )

    assert finding.status == CheckStatus.PASSED
    assert finding.evidence[0].data["catalog_exists"] is True
    assert str(external_catalog_path) in str(finding.evidence[0].data["resolved_path"])