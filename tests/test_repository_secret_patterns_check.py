from pathlib import Path

from ed_cage.checks.security.repository_secret_patterns_check import (
    RepositorySecretPatternsCheck,
)
from ed_cage.domain.enums import CheckStatus, Severity
from ed_cage.domain.models import GovernanceRule, ProjectContext


def test_repository_secret_patterns_check_passes_when_no_secret_found(
    tmp_path: Path,
) -> None:
    source_file = tmp_path / "app.py"
    source_file.write_text(
        "print('hello world')\n",
        encoding="utf-8",
    )

    finding = RepositorySecretPatternsCheck().evaluate(
        rule=_build_rule(),
        context=_build_context(tmp_path),
    )

    assert finding.status == CheckStatus.PASSED
    assert finding.evidence[0].data["scanned_file_count"] == 1
    assert finding.evidence[0].data["violations"] == []


def test_repository_secret_patterns_check_fails_when_secret_found(
    tmp_path: Path,
) -> None:
    source_file = tmp_path / "settings.env"
    fake_key = "AKIA" + "1234567890ABCDEF"
    source_file.write_text(
        f"AWS_ACCESS_KEY_ID={fake_key}\n",
        encoding="utf-8",
    )

    finding = RepositorySecretPatternsCheck().evaluate(
        rule=_build_rule(),
        context=_build_context(tmp_path),
    )

    assert finding.status == CheckStatus.FAILED

    violations = finding.evidence[0].data["violations"]
    assert len(violations) == 1
    assert violations[0]["pattern_name"] == "aws_access_key_id"
    assert violations[0]["line_number"] == 1


def test_repository_secret_patterns_check_respects_exclude_paths(
    tmp_path: Path,
) -> None:
    excluded_dir = tmp_path / "excluded"
    excluded_dir.mkdir()

    fake_key = "AKIA" + "1234567890ABCDEF"
    source_file = excluded_dir / "settings.env"
    source_file.write_text(
        f"AWS_ACCESS_KEY_ID={fake_key}\n",
        encoding="utf-8",
    )

    finding = RepositorySecretPatternsCheck().evaluate(
        rule=_build_rule(exclude_paths=["excluded"]),
        context=_build_context(tmp_path),
    )

    assert finding.status == CheckStatus.PASSED
    assert finding.evidence[0].data["scanned_file_count"] == 0


def _build_rule(exclude_paths: list[str] | None = None) -> GovernanceRule:
    return GovernanceRule(
        id="SEC-001",
        title="Repository must not contain obvious secrets",
        category="security",
        severity=Severity.CRITICAL,
        target="repository",
        check_type="repository_secret_patterns",
        params={
            "include_paths": ["."],
            "exclude_paths": exclude_paths or [],
            "file_patterns": ["*"],
            "max_file_size_bytes": 1048576,
            "secret_patterns": [
                {
                    "name": "aws_access_key_id",
                    "regex": "AKIA[0-9A-Z]{16}",
                }
            ],
        },
    )


def _build_context(repository_path: Path) -> ProjectContext:
    return ProjectContext(
        project_name="test",
        repository_path=repository_path,
        config_path=repository_path / "configs" / "ed-cage.yaml",
        services=[],
    )