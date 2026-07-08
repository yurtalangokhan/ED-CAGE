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


class TrivyToolAdapter:
    DEFAULT_SCANNERS = ["misconfig"]
    DEFAULT_SKIP_DIRS = [
        ".git",
        ".venv",
        "venv",
        "env",
        "__pycache__",
        ".pytest_cache",
        ".mypy_cache",
        ".ruff_cache",
        "outputs",
        "case-studies",
        "node_modules",
        "dist",
        "build",
    ]
    DEFAULT_SKIP_FILES = [
        ".gitignore",
        ".env",
        ".env.example",
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
        return "trivy"

    def is_available(self) -> bool:
        return self._select_execution_mode() is not None

    def collect(
        self,
        rule: GovernanceRule,
        context: ProjectContext,
    ) -> ToolExecutionResult:
        timeout_seconds = int(rule.params.get("timeout_seconds", 180))
        execution_mode = self._select_execution_mode()

        if execution_mode is None:
            return ToolExecutionResult(
                tool_name=self.tool_name,
                status=ToolExecutionStatus.UNAVAILABLE,
                message=(
                    "Trivy executable is not available locally and Docker Compose "
                    "fallback is not available."
                ),
                resource=str(context.repository_path),
                summary={
                    "reason": "trivy_unavailable",
                    "compose_file": str(self.compose_file),
                },
            )

        scan_type = str(rule.params.get("scan_type", "filesystem")).strip().lower()

        if scan_type != "filesystem":
            return ToolExecutionResult(
                tool_name=self.tool_name,
                status=ToolExecutionStatus.ERROR,
                message=f"Unsupported Trivy scan_type: {scan_type}.",
                resource=str(context.repository_path),
                summary={
                    "reason": "unsupported_scan_type",
                    "scan_type": scan_type,
                },
            )

        target_path = self._resolve_target_path(rule, context)

        if not target_path.exists():
            return ToolExecutionResult(
                tool_name=self.tool_name,
                status=ToolExecutionStatus.SKIPPED,
                message=f"Trivy target path does not exist: {target_path}.",
                resource=str(target_path),
                summary={
                    "reason": "target_path_missing",
                    "target_path": str(target_path),
                    **describe_kubernetes_manifest_path_source(rule, context),
                },
            )

        scanners = self._get_scanners(rule)
        skip_dirs = self._resolve_skip_dirs(rule, context)
        skip_files = self._resolve_skip_files(rule, context)
        trivy_timeout = str(rule.params.get("trivy_timeout", "10m")).strip()

        command = self._build_scan_command(
            execution_mode=execution_mode,
            target_path=target_path,
            scanners=scanners,
            skip_dirs=skip_dirs,
            skip_files=skip_files,
            trivy_timeout=trivy_timeout,
        )

        execution_result = self.runner.run(
            command=command,
            timeout_seconds=timeout_seconds,
        )

        if execution_result.executable_not_found:
            return ToolExecutionResult(
                tool_name=self.tool_name,
                status=ToolExecutionStatus.UNAVAILABLE,
                message="Trivy executable is not available.",
                command=execution_result.command,
                exit_code=execution_result.exit_code,
                stdout=execution_result.stdout,
                stderr=execution_result.stderr,
                resource=str(target_path),
                summary={
                    "execution_mode": execution_mode,
                },
            )

        if execution_result.timed_out:
            return ToolExecutionResult(
                tool_name=self.tool_name,
                status=ToolExecutionStatus.ERROR,
                message="Trivy execution timed out.",
                command=execution_result.command,
                exit_code=execution_result.exit_code,
                stdout=execution_result.stdout,
                stderr=execution_result.stderr,
                resource=str(target_path),
                summary={
                    "reason": "timeout",
                    "execution_mode": execution_mode,
                    "scan_type": scan_type,
                    "scanners": scanners,
                    "target_path": str(target_path),
                    "skip_dirs": [str(path) for path in skip_dirs],
                    "skip_files": [str(path) for path in skip_files],
                    "trivy_timeout": trivy_timeout,
                },
            )

        findings = self._parse_trivy_findings(execution_result.stdout)

        if execution_result.exit_code not in {0, 1} and not findings:
            return ToolExecutionResult(
                tool_name=self.tool_name,
                status=ToolExecutionStatus.ERROR,
                message="Trivy execution failed.",
                command=execution_result.command,
                exit_code=execution_result.exit_code,
                stdout=execution_result.stdout,
                stderr=execution_result.stderr,
                resource=str(target_path),
                summary={
                    "reason": "trivy_non_zero_exit",
                    "execution_mode": execution_mode,
                    "scan_type": scan_type,
                    "scanners": scanners,
                    "target_path": str(target_path),
                    "skip_dirs": [str(path) for path in skip_dirs],
                    "skip_files": [str(path) for path in skip_files],
                    "trivy_timeout": trivy_timeout,
                },
            )

        return ToolExecutionResult(
            tool_name=self.tool_name,
            status=ToolExecutionStatus.SUCCESS,
            message=f"Trivy filesystem scan completed. Findings: {len(findings)}.",
            command=execution_result.command,
            exit_code=execution_result.exit_code,
            stdout=execution_result.stdout,
            stderr=execution_result.stderr,
            resource=str(target_path),
            findings=findings,
            summary={
                "finding_count": len(findings),
                "execution_mode": execution_mode,
                "scan_type": scan_type,
                "scanners": scanners,
                "target_path": str(target_path),
                "skip_dirs": [str(path) for path in skip_dirs],
                "skip_files": [str(path) for path in skip_files],
                "trivy_timeout": trivy_timeout,
            },
        )

    def _select_execution_mode(self) -> ExecutionMode | None:
        if self._is_local_trivy_available():
            return "local"

        if self._is_docker_compose_trivy_available():
            return "docker"

        return None

    def _is_local_trivy_available(self) -> bool:
        result = self.runner.run(
            command=["trivy", "--version"],
            timeout_seconds=10,
        )

        return result.exit_code == 0 and not result.executable_not_found

    def _is_docker_compose_trivy_available(self) -> bool:
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
                "trivy",
                "--version",
            ],
            timeout_seconds=30,
        )

        return result.exit_code == 0 and not result.executable_not_found

    def _build_scan_command(
        self,
        execution_mode: ExecutionMode,
        target_path: Path,
        scanners: list[str],
        skip_dirs: list[Path],
        skip_files: list[Path],
        trivy_timeout: str,
    ) -> list[str]:
        if execution_mode == "local":
            command = [
                "trivy",
                "fs",
                "--scanners",
                ",".join(scanners),
                "--format",
                "json",
                "--quiet",
            ]

            for skip_dir in skip_dirs:
                command.extend(["--skip-dirs", str(skip_dir)])

            for skip_file in skip_files:
                command.extend(["--skip-files", str(skip_file)])

            command.append(str(target_path))

            return command

        command = [
            "docker",
            "compose",
            "-f",
            str(self.compose_file),
            "run",
            "--rm",
            "trivy",
            "fs",
            "--scanners",
            ",".join(scanners),
            "--format",
            "json",
            "--quiet",
            "--timeout",
            trivy_timeout,
        ]

        for skip_dir in skip_dirs:
            command.extend(["--skip-dirs", self._to_workspace_path(skip_dir)])

        for skip_file in skip_files:
            command.extend(["--skip-files", self._to_workspace_path(skip_file)])

        command.append(self._to_workspace_path(target_path))

        return command

    def _resolve_target_path(
        self,
        rule: GovernanceRule,
        context: ProjectContext,
    ) -> Path:
        if context.kubernetes_manifest_paths:
            existing_manifest_paths = [
                path.resolve()
                for path in context.kubernetes_manifest_paths
                if path.exists()
            ]

            if existing_manifest_paths:
                return existing_manifest_paths[0]

            return context.kubernetes_manifest_paths[0].resolve()

        raw_target_path = str(rule.params.get("target_path", ".")).strip()
        target_path = Path(raw_target_path)

        if target_path.is_absolute():
            return target_path.resolve()

        return (context.repository_path / target_path).resolve()

    def _resolve_skip_dirs(
        self,
        rule: GovernanceRule,
        context: ProjectContext,
    ) -> list[Path]:
        raw_skip_dirs = rule.params.get("skip_dirs", self.DEFAULT_SKIP_DIRS)

        if not isinstance(raw_skip_dirs, list):
            raw_skip_dirs = self.DEFAULT_SKIP_DIRS

        skip_dirs: list[Path] = []

        for raw_skip_dir in raw_skip_dirs:
            skip_dir_text = str(raw_skip_dir).strip()

            if not skip_dir_text:
                continue

            skip_dir_path = Path(skip_dir_text)

            if skip_dir_path.is_absolute():
                skip_dirs.append(skip_dir_path.resolve())
            else:
                skip_dirs.append((context.repository_path / skip_dir_path).resolve())

        return skip_dirs

    def _resolve_skip_files(
        self,
        rule: GovernanceRule,
        context: ProjectContext,
    ) -> list[Path]:
        raw_skip_files = rule.params.get("skip_files", self.DEFAULT_SKIP_FILES)

        if not isinstance(raw_skip_files, list):
            raw_skip_files = self.DEFAULT_SKIP_FILES

        skip_files: list[Path] = []

        for raw_skip_file in raw_skip_files:
            skip_file_text = str(raw_skip_file).strip()

            if not skip_file_text:
                continue

            skip_file_path = Path(skip_file_text)

            if skip_file_path.is_absolute():
                skip_files.append(skip_file_path.resolve())
            else:
                skip_files.append((context.repository_path / skip_file_path).resolve())

        return skip_files

    def _get_scanners(self, rule: GovernanceRule) -> list[str]:
        raw_scanners = rule.params.get("scanners", self.DEFAULT_SCANNERS)

        if not isinstance(raw_scanners, list):
            return self.DEFAULT_SCANNERS

        scanners = [
            str(scanner).strip() for scanner in raw_scanners if str(scanner).strip()
        ]

        return scanners or self.DEFAULT_SCANNERS

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

    def _parse_trivy_findings(self, stdout: str) -> list[dict[str, Any]]:
        if not stdout.strip():
            return []

        try:
            payload = json.loads(stdout)
        except json.JSONDecodeError:
            return [
                {
                    "code": "trivy_output_parse_error",
                    "message": "Trivy JSON output could not be parsed.",
                    "resource": "trivy_stdout",
                }
            ]

        if not isinstance(payload, dict):
            return []

        results = payload.get("Results")

        if not isinstance(results, list):
            return []

        findings: list[dict[str, Any]] = []

        for result in results:
            if not isinstance(result, dict):
                continue

            findings.extend(self._extract_misconfigurations(result))
            findings.extend(self._extract_secrets(result))

        return findings

    def _extract_misconfigurations(
        self,
        result: dict[str, Any],
    ) -> list[dict[str, Any]]:
        target = str(result.get("Target") or "unknown-target")
        misconfigurations = result.get("Misconfigurations")

        if not isinstance(misconfigurations, list):
            return []

        findings: list[dict[str, Any]] = []

        for item in misconfigurations:
            if not isinstance(item, dict):
                continue

            status = str(item.get("Status") or "").upper()

            if status and status not in {"FAIL", "FAILED"}:
                continue

            finding_id = (
                item.get("ID")
                or item.get("AVDID")
                or item.get("Type")
                or "trivy_misconfiguration"
            )

            findings.append(
                {
                    "code": str(finding_id),
                    "message": str(
                        item.get("Message")
                        or item.get("Title")
                        or item.get("Description")
                        or "Trivy reported a misconfiguration."
                    ),
                    "resource": str(
                        self._extract_misconfiguration_resource(item) or target
                    ),
                    "severity": item.get("Severity"),
                    "category": "misconfiguration",
                    "target": target,
                    "resolution": item.get("Resolution"),
                    "primary_url": item.get("PrimaryURL"),
                    "raw": item,
                }
            )

        return findings

    def _extract_secrets(
        self,
        result: dict[str, Any],
    ) -> list[dict[str, Any]]:
        target = str(result.get("Target") or "unknown-target")
        secrets = result.get("Secrets")

        if not isinstance(secrets, list):
            return []

        findings: list[dict[str, Any]] = []

        for item in secrets:
            if not isinstance(item, dict):
                continue

            finding_id = item.get("RuleID") or item.get("Category") or "trivy_secret"

            findings.append(
                {
                    "code": str(finding_id),
                    "message": str(
                        item.get("Title")
                        or item.get("Match")
                        or "Trivy reported a potential secret."
                    ),
                    "resource": target,
                    "severity": item.get("Severity"),
                    "category": "secret",
                    "target": target,
                    "start_line": item.get("StartLine"),
                    "end_line": item.get("EndLine"),
                    "raw": item,
                }
            )

        return findings

    def _extract_misconfiguration_resource(
        self,
        item: dict[str, Any],
    ) -> str | None:
        cause_metadata = item.get("CauseMetadata")

        if not isinstance(cause_metadata, dict):
            return None

        resource = cause_metadata.get("Resource")

        if resource:
            return str(resource)

        start_line = cause_metadata.get("StartLine")
        end_line = cause_metadata.get("EndLine")

        if start_line is not None and end_line is not None:
            return f"lines:{start_line}-{end_line}"

        if start_line is not None:
            return f"line:{start_line}"

        return None
