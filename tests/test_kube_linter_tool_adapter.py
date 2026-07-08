import json
from pathlib import Path

import pytest

from ed_cage.adapters.tools.command_line_tool_runner import CommandLineExecutionResult
from ed_cage.adapters.tools.kube_linter_tool_adapter import KubeLinterToolAdapter
from ed_cage.domain.enums import Severity, ToolExecutionStatus
from ed_cage.domain.models import GovernanceRule, ProjectContext


class FakeLocalKubeLinterRunner:
    def __init__(self, lint_stdout: str, lint_exit_code: int = 0) -> None:
        self.lint_stdout = lint_stdout
        self.lint_exit_code = lint_exit_code
        self.commands: list[list[str]] = []

    def run(
        self,
        command: list[str],
        cwd: Path | None = None,
        timeout_seconds: int = 60,
    ) -> CommandLineExecutionResult:
        self.commands.append(command)

        if command == ["kube-linter", "lint", "--help"]:
            return CommandLineExecutionResult(
                command=command,
                exit_code=0,
                stdout="help",
                stderr="",
            )

        return CommandLineExecutionResult(
            command=command,
            exit_code=self.lint_exit_code,
            stdout=self.lint_stdout,
            stderr="",
        )


class FakeDockerFallbackKubeLinterRunner:
    def __init__(self, lint_stdout: str, lint_exit_code: int = 0) -> None:
        self.lint_stdout = lint_stdout
        self.lint_exit_code = lint_exit_code
        self.commands: list[list[str]] = []

    def run(
        self,
        command: list[str],
        cwd: Path | None = None,
        timeout_seconds: int = 60,
    ) -> CommandLineExecutionResult:
        self.commands.append(command)

        if command == ["kube-linter", "lint", "--help"]:
            return CommandLineExecutionResult(
                command=command,
                exit_code=None,
                stdout="",
                stderr="not found",
                executable_not_found=True,
            )

        if self._is_docker_compose_help_command(command):
            return CommandLineExecutionResult(
                command=command,
                exit_code=0,
                stdout="docker help",
                stderr="",
            )

        if self._is_docker_compose_lint_command(command):
            return CommandLineExecutionResult(
                command=command,
                exit_code=self.lint_exit_code,
                stdout=self.lint_stdout,
                stderr="",
            )

        return CommandLineExecutionResult(
            command=command,
            exit_code=1,
            stdout="",
            stderr=f"Unexpected command: {command}",
        )

    def _is_docker_compose_help_command(self, command: list[str]) -> bool:
        return (
            len(command) == 9
            and command[0] == "docker"
            and command[1] == "compose"
            and command[2] == "-f"
            and command[4] == "run"
            and command[5] == "--rm"
            and command[6] == "kube-linter"
            and command[7] == "lint"
            and command[8] == "--help"
        )

    def _is_docker_compose_lint_command(self, command: list[str]) -> bool:
        return (
            len(command) >= 11
            and command[0] == "docker"
            and command[1] == "compose"
            and command[2] == "-f"
            and command[4] == "run"
            and command[5] == "--rm"
            and command[6] == "kube-linter"
            and command[7] == "lint"
            and "--format" in command
            and "json" in command
        )


def test_kube_linter_adapter_passes_when_no_findings(tmp_path: Path) -> None:
    manifest_dir = _create_manifest_dir(tmp_path)
    lint_stdout = json.dumps({"Reports": []})

    adapter = KubeLinterToolAdapter(
        runner=FakeLocalKubeLinterRunner(lint_stdout=lint_stdout)
    )

    result = adapter.collect(
        rule=_build_rule(["manifests"]),
        context=_build_context(tmp_path),
    )

    assert result.status == ToolExecutionStatus.SUCCESS
    assert result.findings == []
    assert result.summary["finding_count"] == 0
    assert str(manifest_dir) in result.summary["target_paths"]


def test_kube_linter_adapter_parses_findings(tmp_path: Path) -> None:
    _create_manifest_dir(tmp_path)

    lint_stdout = json.dumps(
        {
            "Reports": [
                {
                    "Check": "no-liveness-probe",
                    "DiagnosticMessage": "Container has no liveness probe.",
                    "Remediation": "Add a livenessProbe.",
                    "Object": {
                        "Namespace": "default",
                        "Kind": "Deployment",
                        "Name": "app",
                    },
                    "FilePath": "manifests/app.yaml",
                    "LineNumber": 12,
                }
            ]
        }
    )

    adapter = KubeLinterToolAdapter(
        runner=FakeLocalKubeLinterRunner(
            lint_stdout=lint_stdout,
            lint_exit_code=1,
        )
    )

    result = adapter.collect(
        rule=_build_rule(["manifests"]),
        context=_build_context(tmp_path),
    )

    assert result.status == ToolExecutionStatus.SUCCESS
    assert result.findings[0]["code"] == "no-liveness-probe"
    assert result.findings[0]["resource"] == "default/Deployment/app"
    assert result.summary["finding_count"] == 1


def test_kube_linter_adapter_skips_when_no_manifest_paths_exist(
    tmp_path: Path,
) -> None:
    adapter = KubeLinterToolAdapter(runner=FakeLocalKubeLinterRunner(lint_stdout=""))

    result = adapter.collect(
        rule=_build_rule(["missing-manifests"]),
        context=_build_context(tmp_path),
    )

    assert result.status == ToolExecutionStatus.SKIPPED
    assert result.summary["reason"] == "no_manifest_paths"


def test_kube_linter_adapter_does_not_treat_checks_as_findings(
    tmp_path: Path,
) -> None:
    _create_manifest_dir(tmp_path)

    lint_stdout = json.dumps(
        {
            "Checks": [
                {
                    "name": "no-read-only-root-fs",
                    "description": "Check definition, not a finding.",
                    "template": "read-only-root-fs",
                },
                {
                    "name": "no-anti-affinity",
                    "description": "Check definition, not a finding.",
                    "template": "anti-affinity",
                },
            ],
            "Reports": None,
            "Summary": {
                "ChecksStatus": "Passed",
                "KubeLinterVersion": "0.8.3",
            },
        }
    )

    adapter = KubeLinterToolAdapter(
        runner=FakeLocalKubeLinterRunner(lint_stdout=lint_stdout)
    )

    result = adapter.collect(
        rule=_build_rule(["manifests"]),
        context=_build_context(tmp_path),
    )

    assert result.status == ToolExecutionStatus.SUCCESS
    assert result.findings == []
    assert result.summary["finding_count"] == 0


def test_kube_linter_adapter_uses_docker_compose_fallback(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.chdir(tmp_path)
    _create_manifest_dir(tmp_path)

    compose_file = tmp_path / "docker-compose.tools.yml"
    compose_file.write_text("services: {}\n", encoding="utf-8")

    lint_stdout = json.dumps({"Reports": []})
    fake_runner = FakeDockerFallbackKubeLinterRunner(lint_stdout=lint_stdout)

    adapter = KubeLinterToolAdapter(
        runner=fake_runner,
        compose_file=compose_file,
    )

    result = adapter.collect(
        rule=_build_rule(["manifests"]),
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


def _create_manifest_dir(tmp_path: Path) -> Path:
    manifest_dir = tmp_path / "manifests"
    manifest_dir.mkdir()

    (manifest_dir / "deployment.yaml").write_text(
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

    return manifest_dir


def _build_rule(manifest_paths: list[str]) -> GovernanceRule:
    return GovernanceRule(
        id="TOOL-K8S-001",
        title="Kubernetes manifests should pass KubeLinter governance baseline",
        description="KubeLinter should evaluate Kubernetes manifests.",
        category="deployment",
        severity=Severity.HIGH,
        target="kubernetes",
        check_type="external_tool",
        params={
            "tool": "kube_linter",
            "manifest_paths": manifest_paths,
            "timeout_seconds": 120,
        },
    )


def _build_context(repository_path: Path) -> ProjectContext:
    return ProjectContext(
        project_name="test",
        repository_path=repository_path,
        config_path=repository_path / "ed-cage.yaml",
        services=[],
    )


def test_kube_linter_adapter_prefers_context_manifest_paths(
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

    lint_stdout = json.dumps({"Reports": []})
    fake_runner = FakeLocalKubeLinterRunner(lint_stdout=lint_stdout)

    adapter = KubeLinterToolAdapter(runner=fake_runner)

    context = _build_context(tmp_path)
    context.kubernetes_manifest_paths = [context_manifest_dir]

    result = adapter.collect(
        rule=_build_rule(["missing-default-path"]),
        context=context,
    )

    assert result.status == ToolExecutionStatus.SUCCESS
    assert str(context_manifest_dir.resolve()) in result.summary["target_paths"]
