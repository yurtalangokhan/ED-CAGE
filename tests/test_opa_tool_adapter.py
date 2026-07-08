import json
from pathlib import Path
import pytest

from ed_cage.adapters.tools.command_line_tool_runner import CommandLineExecutionResult
from ed_cage.adapters.tools.opa_tool_adapter import OpaToolAdapter
from ed_cage.domain.enums import Severity, ToolExecutionStatus
from ed_cage.domain.models import GovernanceRule, ProjectContext



class FakeOpaRunner:
    def __init__(self, eval_stdout: str, eval_exit_code: int = 0) -> None:
        self.eval_stdout = eval_stdout
        self.eval_exit_code = eval_exit_code
        self.commands: list[list[str]] = []

    def run(
        self,
        command: list[str],
        cwd: Path | None = None,
        timeout_seconds: int = 60,
    ) -> CommandLineExecutionResult:
        self.commands.append(command)

        if command == ["opa", "version"]:
            return CommandLineExecutionResult(
                command=command,
                exit_code=0,
                stdout="Version: fake",
                stderr="",
            )

        return CommandLineExecutionResult(
            command=command,
            exit_code=self.eval_exit_code,
            stdout=self.eval_stdout,
            stderr="",
        )


def test_opa_tool_adapter_reports_success_without_findings(tmp_path: Path) -> None:
    policy_path = _write_policy(tmp_path)
    catalog_path = _write_catalog(tmp_path)

    opa_stdout = json.dumps(
        {
            "result": [
                {
                    "expressions": [
                        {
                            "value": [],
                        }
                    ]
                }
            ]
        }
    )

    adapter = OpaToolAdapter(
        runner=FakeOpaRunner(eval_stdout=opa_stdout)
    )

    result = adapter.collect(
        rule=_build_rule(policy_path),
        context=_build_context(tmp_path, catalog_path),
    )

    assert result.status == ToolExecutionStatus.SUCCESS
    assert result.findings == []
    assert result.summary["finding_count"] == 0


def test_opa_tool_adapter_parses_policy_findings(tmp_path: Path) -> None:
    policy_path = _write_policy(tmp_path)
    catalog_path = _write_catalog(tmp_path)

    opa_stdout = json.dumps(
        {
            "result": [
                {
                    "expressions": [
                        {
                            "value": [
                                {
                                    "code": "service_owner_missing",
                                    "message": "Service owner is missing.",
                                    "resource": "service-a",
                                }
                            ],
                        }
                    ]
                }
            ]
        }
    )

    adapter = OpaToolAdapter(
        runner=FakeOpaRunner(eval_stdout=opa_stdout)
    )

    result = adapter.collect(
        rule=_build_rule(policy_path),
        context=_build_context(tmp_path, catalog_path),
    )

    assert result.status == ToolExecutionStatus.SUCCESS
    assert result.findings[0]["code"] == "service_owner_missing"
    assert result.findings[0]["resource"] == "service-a"


def test_opa_tool_adapter_fails_when_catalog_is_missing(tmp_path: Path) -> None:
    policy_path = _write_policy(tmp_path)
    missing_catalog_path = tmp_path / "missing-catalog.yaml"

    adapter = OpaToolAdapter(
        runner=FakeOpaRunner(eval_stdout="")
    )

    result = adapter.collect(
        rule=_build_rule(policy_path),
        context=_build_context(tmp_path, missing_catalog_path),
    )

    assert result.status == ToolExecutionStatus.FAILED
    assert result.findings[0]["code"] == "architecture_catalog_missing"


def test_opa_tool_adapter_errors_when_policy_is_missing(tmp_path: Path) -> None:
    catalog_path = _write_catalog(tmp_path)
    missing_policy_path = tmp_path / "missing-policy.rego"

    adapter = OpaToolAdapter(
        runner=FakeOpaRunner(eval_stdout="")
    )

    result = adapter.collect(
        rule=_build_rule(missing_policy_path),
        context=_build_context(tmp_path, catalog_path),
    )

    assert result.status == ToolExecutionStatus.ERROR
    assert result.summary["reason"] == "policy_file_missing"


def _write_policy(tmp_path: Path) -> Path:
    policy_path = tmp_path / "architecture_catalog.rego"
    policy_path.write_text(
        """
package ed_cage.architecture

import rego.v1

deny := []
""",
        encoding="utf-8",
    )

    return policy_path


def _write_catalog(tmp_path: Path) -> Path:
    catalog_path = tmp_path / "service-architecture.yaml"
    catalog_path.write_text(
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

    return catalog_path


def _build_rule(policy_path: Path) -> GovernanceRule:
    return GovernanceRule(
        id="TOOL-OPA-001",
        title="Architecture catalog must satisfy OPA policy-as-code baseline",
        description="Architecture catalog must comply with Rego policy.",
        category="architecture",
        severity=Severity.HIGH,
        target="architecture-catalog",
        check_type="external_tool",
        params={
            "tool": "opa",
            "input_type": "architecture_catalog",
            "policy_path": str(policy_path),
            "query": "data.ed_cage.architecture.deny",
        },
    )


def _build_context(
    repository_path: Path,
    catalog_path: Path,
) -> ProjectContext:
    return ProjectContext(
        project_name="test",
        repository_path=repository_path,
        config_path=repository_path / "ed-cage.yaml",
        services=[],
        architecture_catalog_path=catalog_path,
    )

def test_opa_tool_adapter_uses_docker_compose_when_local_opa_is_missing(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.chdir(tmp_path)

    policy_path = _write_policy(tmp_path)
    catalog_path = _write_catalog(tmp_path)

    compose_file = tmp_path / "docker-compose.tools.yml"
    compose_file.write_text("services: {}\n", encoding="utf-8")

    opa_stdout = json.dumps(
        {
            "result": [
                {
                    "expressions": [
                        {
                            "value": [],
                        }
                    ]
                }
            ]
        }
    )

    fake_runner = FakeDockerFallbackOpaRunner(eval_stdout=opa_stdout)

    adapter = OpaToolAdapter(
        runner=fake_runner,
        compose_file=compose_file,
    )

    result = adapter.collect(
        rule=_build_rule(policy_path),
        context=_build_context(tmp_path, catalog_path),
    )

    assert result.status == ToolExecutionStatus.SUCCESS
    assert result.summary["execution_mode"] == "docker"

    assert any(
        command[:6] == [
            "docker",
            "compose",
            "-f",
            str(compose_file),
            "run",
            "--rm",
        ]
        for command in fake_runner.commands
    )


class FakeDockerFallbackOpaRunner:
    def __init__(self, eval_stdout: str) -> None:
        self.eval_stdout = eval_stdout
        self.commands: list[list[str]] = []

    def run(
        self,
        command: list[str],
        cwd: Path | None = None,
        timeout_seconds: int = 60,
    ) -> CommandLineExecutionResult:
        self.commands.append(command)

        if command == ["opa", "version"]:
            return CommandLineExecutionResult(
                command=command,
                exit_code=None,
                stdout="",
                stderr="not found",
                executable_not_found=True,
            )

        if self._is_docker_compose_opa_version_command(command):
            return CommandLineExecutionResult(
                command=command,
                exit_code=0,
                stdout="Version: fake docker opa",
                stderr="",
            )

        if self._is_docker_compose_opa_eval_command(command):
            return CommandLineExecutionResult(
                command=command,
                exit_code=0,
                stdout=self.eval_stdout,
                stderr="",
            )

        return CommandLineExecutionResult(
            command=command,
            exit_code=1,
            stdout="",
            stderr=f"Unexpected command: {command}",
        )

    def _is_docker_compose_opa_version_command(self, command: list[str]) -> bool:
        return (
            len(command) >= 8
            and command[0] == "docker"
            and command[1] == "compose"
            and command[2] == "-f"
            and command[4] == "run"
            and command[5] == "--rm"
            and command[6] == "opa"
            and command[7] == "version"
        )

    def _is_docker_compose_opa_eval_command(self, command: list[str]) -> bool:
        return (
            len(command) >= 9
            and command[0] == "docker"
            and command[1] == "compose"
            and command[2] == "-f"
            and command[4] == "run"
            and command[5] == "--rm"
            and command[6] == "opa"
            and command[7] == "eval"
        )