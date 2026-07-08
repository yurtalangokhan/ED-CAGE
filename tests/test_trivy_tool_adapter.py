import json
from pathlib import Path

import pytest

from ed_cage.adapters.tools.command_line_tool_runner import CommandLineExecutionResult
from ed_cage.adapters.tools.trivy_tool_adapter import TrivyToolAdapter
from ed_cage.domain.enums import Severity, ToolExecutionStatus
from ed_cage.domain.models import GovernanceRule, ProjectContext


class FakeLocalTrivyRunner:
    def __init__(self, scan_stdout: str, scan_exit_code: int = 0) -> None:
        self.scan_stdout = scan_stdout
        self.scan_exit_code = scan_exit_code
        self.commands: list[list[str]] = []

    def run(
        self,
        command: list[str],
        cwd: Path | None = None,
        timeout_seconds: int = 60,
    ) -> CommandLineExecutionResult:
        self.commands.append(command)

        if command == ["trivy", "--version"]:
            return CommandLineExecutionResult(
                command=command,
                exit_code=0,
                stdout="Version: fake",
                stderr="",
            )

        return CommandLineExecutionResult(
            command=command,
            exit_code=self.scan_exit_code,
            stdout=self.scan_stdout,
            stderr="",
        )


class FakeDockerFallbackTrivyRunner:
    def __init__(self, scan_stdout: str, scan_exit_code: int = 0) -> None:
        self.scan_stdout = scan_stdout
        self.scan_exit_code = scan_exit_code
        self.commands: list[list[str]] = []

    def run(
        self,
        command: list[str],
        cwd: Path | None = None,
        timeout_seconds: int = 60,
    ) -> CommandLineExecutionResult:
        self.commands.append(command)

        if command == ["trivy", "--version"]:
            return CommandLineExecutionResult(
                command=command,
                exit_code=None,
                stdout="",
                stderr="not found",
                executable_not_found=True,
            )

        if self._is_docker_compose_version_command(command):
            return CommandLineExecutionResult(
                command=command,
                exit_code=0,
                stdout="Version: fake docker trivy",
                stderr="",
            )

        if self._is_docker_compose_scan_command(command):
            return CommandLineExecutionResult(
                command=command,
                exit_code=self.scan_exit_code,
                stdout=self.scan_stdout,
                stderr="",
            )

        return CommandLineExecutionResult(
            command=command,
            exit_code=1,
            stdout="",
            stderr=f"Unexpected command: {command}",
        )

    def _is_docker_compose_version_command(self, command: list[str]) -> bool:
        return (
            len(command) == 8
            and command[0] == "docker"
            and command[1] == "compose"
            and command[2] == "-f"
            and command[4] == "run"
            and command[5] == "--rm"
            and command[6] == "trivy"
            and command[7] == "--version"
        )

    def _is_docker_compose_scan_command(self, command: list[str]) -> bool:
        return (
            len(command) >= 12
            and command[0] == "docker"
            and command[1] == "compose"
            and command[2] == "-f"
            and command[4] == "run"
            and command[5] == "--rm"
            and command[6] == "trivy"
            and command[7] == "fs"
            and "--format" in command
            and "json" in command
            and "--timeout" in command
        )


def test_trivy_adapter_passes_when_no_findings(tmp_path: Path) -> None:
    scan_stdout = json.dumps(
        {
            "SchemaVersion": 2,
            "Results": [],
        }
    )

    adapter = TrivyToolAdapter(runner=FakeLocalTrivyRunner(scan_stdout=scan_stdout))

    result = adapter.collect(
        rule=_build_rule(),
        context=_build_context(tmp_path),
    )

    assert result.status == ToolExecutionStatus.SUCCESS
    assert result.findings == []
    assert result.summary["finding_count"] == 0


def test_trivy_adapter_parses_misconfiguration_findings(tmp_path: Path) -> None:
    scan_stdout = json.dumps(
        {
            "SchemaVersion": 2,
            "Results": [
                {
                    "Target": "deployment.yaml",
                    "Class": "config",
                    "Type": "kubernetes",
                    "Misconfigurations": [
                        {
                            "ID": "KSV001",
                            "AVDID": "AVD-KSV-0001",
                            "Title": "Process can elevate its own privileges",
                            "Description": "Privilege escalation should be disabled.",
                            "Message": "Container allows privilege escalation.",
                            "Resolution": "Set allowPrivilegeEscalation to false.",
                            "Severity": "HIGH",
                            "Status": "FAIL",
                            "CauseMetadata": {
                                "Resource": "Deployment/app",
                                "StartLine": 10,
                                "EndLine": 20,
                            },
                        }
                    ],
                }
            ],
        }
    )

    adapter = TrivyToolAdapter(runner=FakeLocalTrivyRunner(scan_stdout=scan_stdout))

    result = adapter.collect(
        rule=_build_rule(),
        context=_build_context(tmp_path),
    )

    assert result.status == ToolExecutionStatus.SUCCESS
    assert result.findings[0]["code"] == "KSV001"
    assert result.findings[0]["category"] == "misconfiguration"
    assert result.findings[0]["resource"] == "Deployment/app"
    assert result.findings[0]["severity"] == "HIGH"


def test_trivy_adapter_parses_secret_findings(tmp_path: Path) -> None:
    scan_stdout = json.dumps(
        {
            "SchemaVersion": 2,
            "Results": [
                {
                    "Target": ".env",
                    "Class": "secret",
                    "Secrets": [
                        {
                            "RuleID": "aws-access-key-id",
                            "Category": "AWS",
                            "Severity": "CRITICAL",
                            "Title": "AWS Access Key ID",
                            "StartLine": 1,
                            "EndLine": 1,
                        }
                    ],
                }
            ],
        }
    )

    adapter = TrivyToolAdapter(runner=FakeLocalTrivyRunner(scan_stdout=scan_stdout))

    result = adapter.collect(
        rule=_build_rule(),
        context=_build_context(tmp_path),
    )

    assert result.status == ToolExecutionStatus.SUCCESS
    assert result.findings[0]["code"] == "aws-access-key-id"
    assert result.findings[0]["category"] == "secret"
    assert result.findings[0]["resource"] == ".env"
    assert result.findings[0]["severity"] == "CRITICAL"


def test_trivy_adapter_uses_docker_compose_fallback(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.chdir(tmp_path)

    compose_file = tmp_path / "docker-compose.tools.yml"
    compose_file.write_text("services: {}\n", encoding="utf-8")

    scan_stdout = json.dumps(
        {
            "SchemaVersion": 2,
            "Results": [],
        }
    )

    fake_runner = FakeDockerFallbackTrivyRunner(scan_stdout=scan_stdout)

    adapter = TrivyToolAdapter(
        runner=fake_runner,
        compose_file=compose_file,
    )

    result = adapter.collect(
        rule=_build_rule(),
        context=_build_context(tmp_path),
    )

    assert result.status == ToolExecutionStatus.SUCCESS
    assert result.summary["execution_mode"] == "docker"

    assert any(
        command[:6]
        == [
            "docker",
            "compose",
            "-f",
            str(compose_file),
            "run",
            "--rm",
        ]
        for command in fake_runner.commands
    )


def _build_rule() -> GovernanceRule:
    return GovernanceRule(
        id="TOOL-TRIVY-001",
        title="Repository should pass Trivy filesystem security baseline",
        description="Trivy should scan repository for misconfigurations and secrets.",
        category="security",
        severity=Severity.CRITICAL,
        target="repository",
        check_type="external_tool",
        params={
            "tool": "trivy",
            "scan_type": "filesystem",
            "target_path": ".",
            "scanners": [
                "misconfig",
            ],
            "skip_dirs": [
                ".git",
                ".venv",
                "outputs",
                "case-studies",
            ],
            "skip_files": [
                ".gitignore",
                ".env",
                ".env.example",
            ],
            "trivy_timeout": "10m",
            "timeout_seconds": 180,
        },
    )


def _build_context(repository_path: Path) -> ProjectContext:
    return ProjectContext(
        project_name="test",
        repository_path=repository_path,
        config_path=repository_path / "ed-cage.yaml",
        services=[],
    )


def test_trivy_adapter_prefers_context_manifest_path(
    tmp_path: Path,
) -> None:
    context_manifest_dir = tmp_path / "custom-k8s"
    context_manifest_dir.mkdir()

    (context_manifest_dir / "deployment.yaml").write_text(
        """
apiVersion: apps/v1
kind: Deployment
metadata:
  name: app
spec:
  selector:
    matchLabels:
      app: app
  template:
    metadata:
      labels:
        app: app
    spec:
      containers:
        - name: app
          image: app:1.0.0
""",
        encoding="utf-8",
    )

    scan_stdout = json.dumps(
        {
            "SchemaVersion": 2,
            "Results": [],
        }
    )

    fake_runner = FakeLocalTrivyRunner(scan_stdout=scan_stdout)

    adapter = TrivyToolAdapter(runner=fake_runner)

    context = _build_context(tmp_path)
    context.kubernetes_manifest_paths = [context_manifest_dir]

    result = adapter.collect(
        rule=_build_rule(),
        context=context,
    )

    assert result.status == ToolExecutionStatus.SUCCESS
    assert result.summary["target_path"] == str(context_manifest_dir.resolve())
