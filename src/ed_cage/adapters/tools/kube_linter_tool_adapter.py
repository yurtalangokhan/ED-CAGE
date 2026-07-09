import json
from pathlib import Path
from typing import Any, Literal, Protocol

from ed_cage.adapters.tools.command_line_tool_runner import (
    CommandLineExecutionResult,
    CommandLineToolRunner,
)
from ed_cage.domain.enums import ToolExecutionStatus
from ed_cage.domain.models import GovernanceRule, ProjectContext, ToolExecutionResult
from ed_cage.checks.common.kubernetes_manifest_paths import (
    describe_kubernetes_manifest_path_source,
    resolve_kubernetes_manifest_paths,
)


class CommandRunner(Protocol):
    def run(
        self,
        command: list[str],
        cwd: Path | None = None,
        timeout_seconds: int = 60,
    ) -> CommandLineExecutionResult:
        raise NotImplementedError


ExecutionMode = Literal["local", "docker"]


class KubeLinterToolAdapter:
    DEFAULT_MANIFEST_PATHS = [
        "k8s",
        "kubernetes",
        "deploy",
        "deployments",
        "manifests",
        "examples/kubernetes",
        "release",
    ]

    def __init__(
        self,
        runner: CommandRunner | None = None,
        compose_file: Path = Path("docker-compose.tools.yml"),
    ) -> None:
        self.runner = runner or CommandLineToolRunner()
        self.compose_file = compose_file

    @property
    def tool_name(self) -> str:
        return "kube_linter"

    def is_available(self) -> bool:
        return self._select_execution_mode() is not None

    def collect(
        self,
        rule: GovernanceRule,
        context: ProjectContext,
    ) -> ToolExecutionResult:
        timeout_seconds = int(rule.params.get("timeout_seconds", 60))
        execution_mode = self._select_execution_mode()

        if execution_mode is None:
            return ToolExecutionResult(
                tool_name=self.tool_name,
                status=ToolExecutionStatus.UNAVAILABLE,
                message=(
                    "KubeLinter executable is not available locally and Docker "
                    "Compose fallback is not available."
                ),
                resource=str(context.repository_path),
                summary={
                    "reason": "kube_linter_unavailable",
                    "compose_file": str(self.compose_file),
                },
            )

        target_paths = self._resolve_target_paths(rule, context)

        if not target_paths:
            return ToolExecutionResult(
                tool_name=self.tool_name,
                status=ToolExecutionStatus.SKIPPED,
                message="No Kubernetes manifest paths were found for KubeLinter.",
                resource=str(context.repository_path),
                summary={
                    "reason": "no_manifest_paths",
                    **describe_kubernetes_manifest_path_source(rule, context),
                },
            )

        command = self._build_lint_command(
            execution_mode=execution_mode,
            target_paths=target_paths,
        )

        execution_result = self.runner.run(
            command=command,
            timeout_seconds=timeout_seconds,
        )

        if execution_result.executable_not_found:
            return ToolExecutionResult(
                tool_name=self.tool_name,
                status=ToolExecutionStatus.UNAVAILABLE,
                message="KubeLinter executable is not available.",
                command=execution_result.command,
                exit_code=execution_result.exit_code,
                stdout=execution_result.stdout,
                stderr=execution_result.stderr,
                resource=str(context.repository_path),
                summary={
                    "execution_mode": execution_mode,
                },
            )

        if execution_result.timed_out:
            return ToolExecutionResult(
                tool_name=self.tool_name,
                status=ToolExecutionStatus.SKIPPED,
                message=(
                    "KubeLinter execution timed out and was skipped for "
                    "this evaluation run."
                ),
                command=execution_result.command,
                exit_code=execution_result.exit_code,
                stdout=execution_result.stdout,
                stderr=execution_result.stderr,
                resource=str(context.repository_path),
                summary={
                    "reason": "kube_linter_execution_timeout",
                    "execution_mode": execution_mode,
                },
            )

        findings = self._parse_kube_linter_findings(execution_result.stdout)

        if execution_result.exit_code not in {0, 1} and not findings:
            return ToolExecutionResult(
                tool_name=self.tool_name,
                status=ToolExecutionStatus.SKIPPED,
                message=(
                    "KubeLinter execution did not produce evaluable governance "
                    "findings and was skipped."
                ),
                command=execution_result.command,
                exit_code=execution_result.exit_code,
                stdout=execution_result.stdout,
                stderr=execution_result.stderr,
                resource=str(context.repository_path),
                summary={
                    "reason": "kube_linter_execution_not_evaluable",
                    "execution_mode": execution_mode,
                    "original_exit_code": execution_result.exit_code,
                },
            )

        return ToolExecutionResult(
            tool_name=self.tool_name,
            status=ToolExecutionStatus.SUCCESS,
            message=f"KubeLinter execution completed. Findings: {len(findings)}.",
            command=execution_result.command,
            exit_code=execution_result.exit_code,
            stdout=execution_result.stdout,
            stderr=execution_result.stderr,
            resource=str(context.repository_path),
            findings=findings,
            summary={
                "finding_count": len(findings),
                "execution_mode": execution_mode,
                "target_paths": [str(path) for path in target_paths],
            },
        )

    def _select_execution_mode(self) -> ExecutionMode | None:
        if self._is_local_kube_linter_available():
            return "local"

        if self._is_docker_compose_kube_linter_available():
            return "docker"

        return None

    def _is_local_kube_linter_available(self) -> bool:
        result = self.runner.run(
            command=["kube-linter", "lint", "--help"],
            timeout_seconds=10,
        )

        return result.exit_code == 0 and not result.executable_not_found

    def _is_docker_compose_kube_linter_available(self) -> bool:
        if not self.compose_file.exists():
            return False

        result = self.runner.run(
            command=[
                "docker",
                "compose",
                "-f",
                str(self.compose_file),
                "run",
                "--rm",
                "kube-linter",
                "lint",
                "--help",
            ],
            timeout_seconds=30,
        )

        return result.exit_code == 0 and not result.executable_not_found

    def _build_lint_command(
        self,
        execution_mode: ExecutionMode,
        target_paths: list[Path],
    ) -> list[str]:
        if execution_mode == "local":
            return [
                "kube-linter",
                "lint",
                *[str(path) for path in target_paths],
                "--format",
                "json",
            ]

        return [
            "docker",
            "compose",
            "-f",
            str(self.compose_file),
            "run",
            "--rm",
            "kube-linter",
            "lint",
            *[self._to_workspace_path(path) for path in target_paths],
            "--format",
            "json",
        ]

    def _resolve_target_paths(
        self,
        rule: GovernanceRule,
        context: ProjectContext,
    ) -> list[Path]:
        return resolve_kubernetes_manifest_paths(
            rule=rule,
            context=context,
            existing_only=True,
        )

    def _get_manifest_paths(self, rule: GovernanceRule) -> list[str]:
        raw_manifest_paths = rule.params.get(
            "manifest_paths",
            self.DEFAULT_MANIFEST_PATHS,
        )

        if not isinstance(raw_manifest_paths, list):
            return self.DEFAULT_MANIFEST_PATHS

        manifest_paths = [
            str(path).strip() for path in raw_manifest_paths if str(path).strip()
        ]

        return manifest_paths or self.DEFAULT_MANIFEST_PATHS

    def _to_workspace_path(self, host_path: Path) -> str:
        project_root = Path.cwd().resolve()
        resolved_path = host_path.resolve()

        try:
            relative_path = resolved_path.relative_to(project_root)
        except ValueError:
            raise ValueError(
                "Path is not under project root and cannot be mounted into "
                f"Docker Compose workspace: {resolved_path}"
            )

        return f"/workspace/{relative_path.as_posix()}"

    def _parse_kube_linter_findings(
        self,
        stdout: str,
    ) -> list[dict[str, Any]]:
        if not stdout.strip():
            return []

        try:
            payload = json.loads(stdout)
        except json.JSONDecodeError:
            return [
                {
                    "code": "kube_linter_output_parse_error",
                    "message": "KubeLinter JSON output could not be parsed.",
                    "resource": "kube_linter_stdout",
                }
            ]

        if self._summary_status_is_passed(payload):
            return []

        raw_findings = self._extract_raw_findings(payload)

        return [self._normalize_finding(raw_finding) for raw_finding in raw_findings]

    def _extract_raw_findings(self, payload: object) -> list[dict[str, Any]]:
        if isinstance(payload, list):
            return [item for item in payload if isinstance(item, dict)]

        if not isinstance(payload, dict):
            return []

        for key in [
            "Reports",
            "reports",
            "Findings",
            "findings",
            "Results",
            "results",
        ]:
            value = payload.get(key)

            if isinstance(value, list):
                return [item for item in value if isinstance(item, dict)]

        return []

    def _normalize_finding(self, item: dict[str, Any]) -> dict[str, Any]:
        check_name = self._first_present(
            item,
            ["Check", "check", "checkName", "check_name", "Name", "name"],
        )
        message = self._first_present(
            item,
            [
                "DiagnosticMessage",
                "diagnosticMessage",
                "message",
                "Message",
                "Description",
                "description",
            ],
        )
        remediation = self._first_present(
            item,
            ["Remediation", "remediation", "RemediationMessage"],
        )
        file_path = self._first_present(
            item,
            ["FilePath", "filePath", "file", "filename"],
        )
        line_number = self._first_present(
            item,
            ["LineNumber", "lineNumber", "line"],
        )

        resource = self._resource_from_object(item.get("Object") or item.get("object"))

        return {
            "code": str(check_name or "kube_linter_finding"),
            "message": str(message or "KubeLinter reported a finding."),
            "resource": resource or str(file_path or "kubernetes_manifest"),
            "remediation": remediation,
            "file_path": file_path,
            "line_number": line_number,
            "raw": item,
        }

    def _resource_from_object(self, value: object) -> str | None:
        if not isinstance(value, dict):
            return None

        namespace = value.get("Namespace") or value.get("namespace")
        kind = value.get("Kind") or value.get("kind")
        name = value.get("Name") or value.get("name")

        parts = [
            str(part) for part in [namespace, kind, name] if part not in {None, ""}
        ]

        if not parts:
            return None

        return "/".join(parts)

    def _first_present(
        self,
        item: dict[str, Any],
        keys: list[str],
    ) -> object | None:
        for key in keys:
            value = item.get(key)

            if value not in {None, ""}:
                return value

        return None

    def _summary_status_is_passed(self, payload: object) -> bool:
        if not isinstance(payload, dict):
            return False

        summary = payload.get("Summary") or payload.get("summary")

        if not isinstance(summary, dict):
            return False

        checks_status = summary.get("ChecksStatus") or summary.get("checksStatus")

        return str(checks_status).strip().lower() == "passed"
