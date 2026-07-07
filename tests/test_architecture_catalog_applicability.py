from pathlib import Path

from ed_cage.checks.architecture.architecture_catalog_policy_check import (
    ArchitectureCatalogPolicyCheck,
)
from ed_cage.domain.enums import CheckStatus, Severity
from ed_cage.domain.models import GovernanceRule, ProjectContext


def test_architecture_catalog_policy_check_returns_failed_when_catalog_missing(
    tmp_path: Path,
) -> None:
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
                "architecture_catalog_path": "configs/architecture/service-architecture.yaml",
            },
        ),
        context=ProjectContext(
            project_name="test",
            repository_path=tmp_path,
            config_path=tmp_path / "configs" / "ed-cage.yaml",
            services=[],
        ),
    )

    assert finding.status == CheckStatus.FAILED
    assert finding.message == "Required architecture catalog does not exist."