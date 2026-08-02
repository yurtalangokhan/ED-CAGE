from pathlib import Path
from typing import Any

import yaml

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


def test_spring_monitoring_services_are_ignored_by_exact_service_name(
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
  grafana-server:
    image: grafana/grafana:latest
  prometheus-server:
    image: prom/prometheus:latest
  tracing-server:
    image: openzipkin/zipkin:latest
  admin-server:
    image: admin-server:latest
""",
    )

    ignored_services = [
        "grafana",
        "grafana-server",
        "prometheus",
        "prometheus-server",
        "tracing-server",
        "admin-server",
    ]
    finding = DockerComposeHealthcheckPolicyCheck().evaluate(
        rule=_build_rule(
            "CMP-002",
            "docker_compose_healthcheck_policy",
            params={"ignored_services": ignored_services},
        ),
        context=_build_context(tmp_path),
    )

    assert finding.status == CheckStatus.PASSED
    evidence_data = finding.evidence[0].data
    assert evidence_data["ignored_services"] == ignored_services
    assert evidence_data["service_count"] == 1
    assert evidence_data["service_evaluations"][0]["service"] == "api"
    assert evidence_data["violations"] == []


def test_cmp002_default_rule_contains_spring_monitoring_service_names() -> None:
    repository_root = Path(__file__).resolve().parents[1]
    rule_file = repository_root / "configs" / "rules" / "docker_compose_baseline.yaml"
    payload = yaml.safe_load(rule_file.read_text(encoding="utf-8"))

    cmp002 = next(
        rule
        for rule in payload["rules"]
        if rule["id"] == "CMP-002"
    )
    ignored_services = set(cmp002["params"]["ignored_services"])

    assert {
        "grafana",
        "grafana-server",
        "prometheus",
        "prometheus-server",
        "tracing-server",
        "admin-server",
    }.issubset(ignored_services)


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
    params: dict[str, Any] | None = None,
) -> GovernanceRule:
    rule_params: dict[str, Any] = {
        "compose_files": [
            "docker-compose.yml",
        ],
    }
    if params:
        rule_params.update(params)

    return GovernanceRule(
        id=rule_id,
        title=f"{rule_id} test rule",
        description=f"{rule_id} test description",
        category="deployment",
        severity=Severity.HIGH,
        target="docker-compose",
        check_type=check_type,
        enabled=True,
        params=rule_params,
    )


def _build_context(repository_path: Path) -> ProjectContext:
    return ProjectContext(
        project_name="test",
        repository_path=repository_path,
        config_path=repository_path / "ed-cage.yaml",
        services=[],
    )
