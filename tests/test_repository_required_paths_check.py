from pathlib import Path

from ed_cage.checks.architecture.repository_required_paths_check import (
    RepositoryRequiredPathsCheck,
)
from ed_cage.domain.enums import CheckStatus, Severity
from ed_cage.domain.models import GovernanceRule, ProjectContext


def test_repository_required_paths_check_passes_when_required_directory_exists(
    tmp_path: Path,
) -> None:
    adr_dir = tmp_path / "docs" / "adr"
    adr_dir.mkdir(parents=True)

    finding = RepositoryRequiredPathsCheck().evaluate(
        rule=_build_rule(
            required_paths=[
                {
                    "path": "docs/adr",
                    "type": "directory",
                }
            ]
        ),
        context=_build_context(tmp_path),
    )

    assert finding.status == CheckStatus.PASSED


def test_repository_required_paths_check_fails_when_required_file_missing(
    tmp_path: Path,
) -> None:
    finding = RepositoryRequiredPathsCheck().evaluate(
        rule=_build_rule(
            required_paths=[
                {
                    "path": "docs/quality-attributes/scenarios.yaml",
                    "type": "file",
                }
            ]
        ),
        context=_build_context(tmp_path),
    )

    assert finding.status == CheckStatus.FAILED

    violations = finding.evidence[0].data["violations"]
    assert violations[0]["reason"] == "path_does_not_exist"


def _build_rule(required_paths: list[dict[str, object]]) -> GovernanceRule:
    return GovernanceRule(
        id="ARCH-001",
        title="ADR directory must exist",
        category="architecture",
        severity=Severity.MEDIUM,
        target="repository",
        check_type="repository_required_paths",
        params={
            "required_paths": required_paths,
        },
    )


def _build_context(repository_path: Path) -> ProjectContext:
    return ProjectContext(
        project_name="test",
        repository_path=repository_path,
        config_path=repository_path / "configs" / "ed-cage.yaml",
        services=[],
    )