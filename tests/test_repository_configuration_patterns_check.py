from pathlib import Path

from ed_cage.checks.reliability.repository_configuration_patterns_check import (
    RepositoryConfigurationPatternsCheck,
)
from ed_cage.domain.enums import CheckStatus, Severity
from ed_cage.domain.models import GovernanceRule, ProjectContext


def test_repository_configuration_patterns_check_passes_when_required_group_found(
    tmp_path: Path,
) -> None:
    config_file = tmp_path / "application.yaml"
    config_file.write_text(
        """
resilience4j:
  retry:
    instances:
      service-a:
        maxAttempts: 3
        waitDuration: 500ms
""",
        encoding="utf-8",
    )

    finding = RepositoryConfigurationPatternsCheck().evaluate(
        rule=_build_rule(
            required_pattern_groups={
                "retry_policy": {
                    "patterns": [
                        "(?i)retry",
                    ]
                }
            }
        ),
        context=_build_context(tmp_path),
    )

    assert finding.status == CheckStatus.PASSED

    matched_groups = finding.evidence[0].data["matched_groups"]
    assert matched_groups["retry_policy"]


def test_repository_configuration_patterns_check_fails_when_required_group_missing(
    tmp_path: Path,
) -> None:
    config_file = tmp_path / "application.yaml"
    config_file.write_text(
        """
server:
  port: 8080
""",
        encoding="utf-8",
    )

    finding = RepositoryConfigurationPatternsCheck().evaluate(
        rule=_build_rule(
            required_pattern_groups={
                "circuit_breaker_policy": {
                    "patterns": [
                        "(?i)circuitbreaker",
                    ]
                }
            }
        ),
        context=_build_context(tmp_path),
    )

    assert finding.status == CheckStatus.FAILED

    missing_groups = finding.evidence[0].data["missing_groups"]
    assert missing_groups == ["circuit_breaker_policy"]


def test_repository_configuration_patterns_check_requires_all_groups(
    tmp_path: Path,
) -> None:
    config_file = tmp_path / "application.yaml"
    config_file.write_text(
        """
resilience4j:
  retry:
    instances:
      service-a:
        maxAttempts: 3
""",
        encoding="utf-8",
    )

    finding = RepositoryConfigurationPatternsCheck().evaluate(
        rule=_build_rule(
            required_pattern_groups={
                "retry_attempt_bound": {
                    "patterns": [
                        "(?i)maxAttempts",
                    ]
                },
                "retry_backoff": {
                    "patterns": [
                        "(?i)waitDuration",
                    ]
                },
            }
        ),
        context=_build_context(tmp_path),
    )

    assert finding.status == CheckStatus.FAILED

    missing_groups = finding.evidence[0].data["missing_groups"]
    assert missing_groups == ["retry_backoff"]


def _build_rule(required_pattern_groups: dict[str, object]) -> GovernanceRule:
    return GovernanceRule(
        id="REL-003",
        title="Services should define retry policy",
        category="reliability",
        severity=Severity.MEDIUM,
        target="repository",
        check_type="repository_configuration_patterns",
        params={
            "include_paths": ["."],
            "exclude_paths": [],
            "file_patterns": ["*.yaml", "*.yml"],
            "max_file_size_bytes": 1048576,
            "required_pattern_groups": required_pattern_groups,
        },
    )


def _build_context(repository_path: Path) -> ProjectContext:
    return ProjectContext(
        project_name="test",
        repository_path=repository_path,
        config_path=repository_path / "configs" / "ed-cage.yaml",
        services=[],
    )