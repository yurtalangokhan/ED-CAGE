from pathlib import Path

from ed_cage.checks.deployment.docker_compose_file_exists_check import (
    DockerComposeFileExistsCheck,
)
from ed_cage.checks.reliability.docker_compose_healthcheck_policy_check import (
    DockerComposeHealthcheckPolicyCheck,
)
from ed_cage.checks.security.docker_compose_security_policy_check import (
    DockerComposeSecurityPolicyCheck,
)
from ed_cage.domain.enums import CheckStatus, Severity
from ed_cage.domain.models import GovernanceRule, ProjectContext


def test_docker_compose_file_exists_check_passes_when_compose_file_exists(
    tmp_path: Path,
) -> None:
    _write_compose_file(
        tmp_path,
        """
services:
  api:
    image: api:latest
""",
    )

    finding = DockerComposeFileExistsCheck().evaluate(
        rule=_build_rule("CMP-001", "docker_compose_file_exists"),
        context=_build_context(tmp_path),
    )

    assert finding.status == CheckStatus.PASSED


def test_docker_compose_file_exists_check_fails_when_compose_file_missing(
    tmp_path: Path,
) -> None:
    finding = DockerComposeFileExistsCheck().evaluate(
        rule=_build_rule("CMP-001", "docker_compose_file_exists"),
        context=_build_context(tmp_path),
    )

    assert finding.status == CheckStatus.FAILED


def test_docker_compose_healthcheck_policy_passes_when_services_have_healthchecks(
    tmp_path: Path,
) -> None:
    _write_compose_file(
        tmp_path,
        """
services:
  api:
    image: api:latest
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8080/actuator/health"]
      interval: 10s
      timeout: 5s
      retries: 3
""",
    )

    finding = DockerComposeHealthcheckPolicyCheck().evaluate(
        rule=_build_rule("CMP-002", "docker_compose_healthcheck_policy"),
        context=_build_context(tmp_path),
    )

    assert finding.status == CheckStatus.PASSED


def test_docker_compose_healthcheck_policy_fails_when_service_missing_healthcheck(
    tmp_path: Path,
) -> None:
    _write_compose_file(
        tmp_path,
        """
services:
  api:
    image: api:latest
""",
    )

    finding = DockerComposeHealthcheckPolicyCheck().evaluate(
        rule=_build_rule("CMP-002", "docker_compose_healthcheck_policy"),
        context=_build_context(tmp_path),
    )

    assert finding.status == CheckStatus.FAILED
    assert finding.evidence[0].data["violations"][0]["reason"] == "missing_healthcheck"


def test_docker_compose_security_policy_passes_for_safe_service(
    tmp_path: Path,
) -> None:
    _write_compose_file(
        tmp_path,
        """
services:
  api:
    image: api:latest
""",
    )

    finding = DockerComposeSecurityPolicyCheck().evaluate(
        rule=_build_rule("CMP-003", "docker_compose_security_policy"),
        context=_build_context(tmp_path),
    )

    assert finding.status == CheckStatus.PASSED


def test_docker_compose_security_policy_fails_for_privileged_service(
    tmp_path: Path,
) -> None:
    _write_compose_file(
        tmp_path,
        """
services:
  api:
    image: api:latest
    privileged: true
""",
    )

    finding = DockerComposeSecurityPolicyCheck().evaluate(
        rule=_build_rule("CMP-003", "docker_compose_security_policy"),
        context=_build_context(tmp_path),
    )

    assert finding.status == CheckStatus.FAILED
    assert finding.evidence[0].data["violations"][0]["reason"] == "privileged_container"


def test_docker_compose_security_policy_fails_for_host_network_mode(
    tmp_path: Path,
) -> None:
    _write_compose_file(
        tmp_path,
        """
services:
  api:
    image: api:latest
    network_mode: host
""",
    )

    finding = DockerComposeSecurityPolicyCheck().evaluate(
        rule=_build_rule("CMP-003", "docker_compose_security_policy"),
        context=_build_context(tmp_path),
    )

    assert finding.status == CheckStatus.FAILED
    assert finding.evidence[0].data["violations"][0]["reason"] == "host_network_mode"


def _write_compose_file(
    repository_path: Path,
    content: str,
) -> None:
    (repository_path / "docker-compose.yml").write_text(
        content.strip(),
        encoding="utf-8",
    )


def _build_rule(
    rule_id: str,
    check_type: str,
) -> GovernanceRule:
    return GovernanceRule(
        id=rule_id,
        title=f"{rule_id} test rule",
        description=f"{rule_id} test description",
        category="deployment",
        severity=Severity.HIGH,
        target="docker-compose",
        check_type=check_type,
        enabled=True,
        params={
            "compose_files": [
                "docker-compose.yml",
            ],
        },
    )


def _build_context(repository_path: Path) -> ProjectContext:
    return ProjectContext(
        project_name="test",
        repository_path=repository_path,
        config_path=repository_path / "ed-cage.yaml",
        services=[],
    )