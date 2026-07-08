import json
from pathlib import Path
from typing import Any, Literal, Protocol
from uuid import uuid4

import yaml

from ed_cage.adapters.tools.command_line_tool_runner import (
    CommandLineExecutionResult,
    CommandLineToolRunner,
)
from ed_cage.domain.enums import ToolExecutionStatus
from ed_cage.domain.models import GovernanceRule, ProjectContext, ToolExecutionResult


class CommandRunner(Protocol):
    def run(
        self,
        command: list[str],
        cwd: Path | None = None,
        timeout_seconds: int = 60,
    ) -> CommandLineExecutionResult:
        raise NotImplementedError


ExecutionMode = Literal["local", "docker"]


class OpaToolAdapter:
    def __init__(
        self,
        runner: CommandRunner | None = None,
        compose_file: Path = Path("docker-compose.tools.yml"),
    ) -> None:
        self.runner = runner or CommandLineToolRunner()
        self.compose_file = compose_file

    @property
    def tool_name(self) -> str:
        return "opa"

    def is_available(self) -> bool:
        return self._select_execution_mode() is not None

    def collect(
        self,
        rule: GovernanceRule,
        context: ProjectContext,
    ) -> ToolExecutionResult:
        input_type = str(
            rule.params.get("input_type", "architecture_catalog")
        ).strip()

        if input_type != "architecture_catalog":
            return ToolExecutionResult(
                tool_name=self.tool_name,
                status=ToolExecutionStatus.ERROR,
                message=f"Unsupported OPA input_type: {input_type}.",
                resource=str(context.repository_path),
                summary={
                    "input_type": input_type,
                    "reason": "unsupported_input_type",
                },
            )

        policy_path = self._resolve_policy_path(rule)

        if policy_path is None:
            return ToolExecutionResult(
                tool_name=self.tool_name,
                status=ToolExecutionStatus.ERROR,
                message="OPA rule is missing required parameter: policy_path.",
                resource=str(context.repository_path),
                summary={
                    "reason": "missing_policy_path",
                },
            )

        if not policy_path.exists():
            return ToolExecutionResult(
                tool_name=self.tool_name,
                status=ToolExecutionStatus.ERROR,
                message=f"OPA policy file does not exist: {policy_path}.",
                resource=str(policy_path),
                summary={
                    "reason": "policy_file_missing",
                    "policy_path": str(policy_path),
                },
            )

        input_path = self._resolve_architecture_catalog_path(rule, context)

        if not input_path.exists():
            return ToolExecutionResult(
                tool_name=self.tool_name,
                status=ToolExecutionStatus.FAILED,
                message=f"OPA input architecture catalog does not exist: {input_path}.",
                resource=str(input_path),
                findings=[
                    {
                        "code": "architecture_catalog_missing",
                        "message": "Architecture catalog file is required for OPA policy evaluation.",
                        "resource": str(input_path),
                    }
                ],
                summary={
                    "reason": "architecture_catalog_missing",
                    "input_path": str(input_path),
                },
            )

        input_data = self._load_input_data(input_path)

        if input_data is None:
            return ToolExecutionResult(
                tool_name=self.tool_name,
                status=ToolExecutionStatus.ERROR,
                message=f"OPA input architecture catalog could not be parsed: {input_path}.",
                resource=str(input_path),
                summary={
                    "reason": "architecture_catalog_parse_error",
                    "input_path": str(input_path),
                },
            )

        query = str(
            rule.params.get("query", "data.ed_cage.architecture.deny")
        ).strip()

        timeout_seconds = int(rule.params.get("timeout_seconds", 30))

        return self._evaluate_policy(
            policy_path=policy_path,
            input_data=input_data,
            query=query,
            timeout_seconds=timeout_seconds,
            resource=str(input_path),
        )

    def _evaluate_policy(
        self,
        policy_path: Path,
        input_data: dict[str, Any],
        query: str,
        timeout_seconds: int,
        resource: str,
    ) -> ToolExecutionResult:
        execution_mode = self._select_execution_mode()

        if execution_mode is None:
            return ToolExecutionResult(
                tool_name=self.tool_name,
                status=ToolExecutionStatus.UNAVAILABLE,
                message="OPA executable is not available locally and Docker Compose fallback is not available.",
                resource=resource,
                summary={
                    "reason": "opa_unavailable",
                    "compose_file": str(self.compose_file),
                },
            )

        temp_input_path: Path | None = None

        try:
            temp_input_path = self._write_temp_input(input_data)

            command = self._build_eval_command(
                execution_mode=execution_mode,
                policy_path=policy_path,
                input_path=temp_input_path,
                query=query,
            )

            execution_result = self.runner.run(
                command=command,
                timeout_seconds=timeout_seconds,
            )

            if execution_result.executable_not_found:
                return ToolExecutionResult(
                    tool_name=self.tool_name,
                    status=ToolExecutionStatus.UNAVAILABLE,
                    message="OPA executable is not available.",
                    command=execution_result.command,
                    exit_code=execution_result.exit_code,
                    stdout=execution_result.stdout,
                    stderr=execution_result.stderr,
                    resource=resource,
                    summary={
                        "execution_mode": execution_mode,
                    },
                )

            if execution_result.timed_out:
                return ToolExecutionResult(
                    tool_name=self.tool_name,
                    status=ToolExecutionStatus.ERROR,
                    message="OPA policy evaluation timed out.",
                    command=execution_result.command,
                    exit_code=execution_result.exit_code,
                    stdout=execution_result.stdout,
                    stderr=execution_result.stderr,
                    resource=resource,
                    summary={
                        "reason": "timeout",
                        "execution_mode": execution_mode,
                    },
                )

            if execution_result.exit_code != 0:
                return ToolExecutionResult(
                    tool_name=self.tool_name,
                    status=ToolExecutionStatus.ERROR,
                    message="OPA policy evaluation failed.",
                    command=execution_result.command,
                    exit_code=execution_result.exit_code,
                    stdout=execution_result.stdout,
                    stderr=execution_result.stderr,
                    resource=resource,
                    summary={
                        "reason": "opa_non_zero_exit",
                        "execution_mode": execution_mode,
                    },
                )

            findings = self._parse_opa_findings(execution_result.stdout)

            return ToolExecutionResult(
                tool_name=self.tool_name,
                status=ToolExecutionStatus.SUCCESS,
                message=(
                    "OPA policy evaluation completed. "
                    f"Findings: {len(findings)}."
                ),
                command=execution_result.command,
                exit_code=execution_result.exit_code,
                stdout=execution_result.stdout,
                stderr=execution_result.stderr,
                resource=resource,
                findings=findings,
                summary={
                    "policy_path": str(policy_path),
                    "query": query,
                    "finding_count": len(findings),
                    "execution_mode": execution_mode,
                },
            )

        finally:
            if temp_input_path is not None and temp_input_path.exists():
                temp_input_path.unlink()

    def _select_execution_mode(self) -> ExecutionMode | None:
        if self._is_local_opa_available():
            return "local"

        if self._is_docker_compose_opa_available():
            return "docker"

        return None

    def _is_local_opa_available(self) -> bool:
        result = self.runner.run(
            command=["opa", "version"],
            timeout_seconds=10,
        )

        return result.exit_code == 0 and not result.executable_not_found

    def _is_docker_compose_opa_available(self) -> bool:
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
                "opa",
                "version",
            ],
            timeout_seconds=30,
        )

        return result.exit_code == 0 and not result.executable_not_found

    def _build_eval_command(
        self,
        execution_mode: ExecutionMode,
        policy_path: Path,
        input_path: Path,
        query: str,
    ) -> list[str]:
        if execution_mode == "local":
            return [
                "opa",
                "eval",
                "--format",
                "json",
                "--data",
                str(policy_path),
                "--input",
                str(input_path),
                query,
            ]

        return [
            "docker",
            "compose",
            "-f",
            str(self.compose_file),
            "run",
            "--rm",
            "opa",
            "eval",
            "--format",
            "json",
            "--data",
            self._to_workspace_path(policy_path),
            "--input",
            self._to_workspace_path(input_path),
            query,
        ]

    def _write_temp_input(self, input_data: dict[str, Any]) -> Path:
        temp_dir = Path.cwd().resolve() / "outputs" / "tools" / "opa"
        temp_dir.mkdir(parents=True, exist_ok=True)

        temp_input_path = temp_dir / f"opa-input-{uuid4()}.json"

        temp_input_path.write_text(
            json.dumps(input_data, ensure_ascii=False),
            encoding="utf-8",
        )

        return temp_input_path

    def _to_workspace_path(self, host_path: Path) -> str:
        project_root = Path.cwd().resolve()
        resolved_path = host_path.resolve()

        try:
            relative_path = resolved_path.relative_to(project_root)
        except ValueError:
            raise ValueError(
                f"Path is not under project root and cannot be mounted into Docker Compose workspace: {resolved_path}"
            )

        return f"/workspace/{relative_path.as_posix()}"

    def _parse_opa_findings(self, stdout: str) -> list[dict[str, Any]]:
        if not stdout.strip():
            return []

        try:
            payload = json.loads(stdout)
        except json.JSONDecodeError:
            return [
                {
                    "code": "opa_output_parse_error",
                    "message": "OPA JSON output could not be parsed.",
                    "resource": "opa_stdout",
                }
            ]

        result_items = payload.get("result")

        if not isinstance(result_items, list) or not result_items:
            return []

        expressions = result_items[0].get("expressions")

        if not isinstance(expressions, list) or not expressions:
            return []

        value = expressions[0].get("value")

        if value is None:
            return []

        if isinstance(value, list):
            return [
                self._normalize_opa_finding(item)
                for item in value
            ]

        if isinstance(value, dict):
            if not value:
                return []

            return [self._normalize_opa_finding(value)]

        if isinstance(value, bool):
            if value:
                return [
                    {
                        "code": "opa_boolean_true_result",
                        "message": "OPA query returned true.",
                        "resource": "opa_query",
                    }
                ]

            return []

        return [
            {
                "code": "opa_non_structured_result",
                "message": str(value),
                "resource": "opa_query",
            }
        ]

    def _normalize_opa_finding(self, item: object) -> dict[str, Any]:
        if isinstance(item, dict):
            return item

        return {
            "code": "opa_finding",
            "message": str(item),
            "resource": "opa_query",
        }

    def _resolve_policy_path(self, rule: GovernanceRule) -> Path | None:
        raw_policy_path = rule.params.get("policy_path")

        if raw_policy_path is None:
            return None

        policy_path = Path(str(raw_policy_path))

        if policy_path.is_absolute():
            return policy_path.resolve()

        return (Path.cwd().resolve() / policy_path).resolve()

    def _resolve_architecture_catalog_path(
        self,
        rule: GovernanceRule,
        context: ProjectContext,
    ) -> Path:
        if context.architecture_catalog_path is not None:
            return context.architecture_catalog_path.resolve()

        raw_catalog_path = str(
            rule.params.get(
                "architecture_catalog_path",
                "configs/architecture/service-architecture.yaml",
            )
        )

        catalog_path = Path(raw_catalog_path)

        if catalog_path.is_absolute():
            return catalog_path.resolve()

        return (context.repository_path / catalog_path).resolve()

    def _load_input_data(self, input_path: Path) -> dict[str, Any] | None:
        try:
            if input_path.suffix.lower() == ".json":
                payload = json.loads(input_path.read_text(encoding="utf-8"))
            else:
                payload = yaml.safe_load(input_path.read_text(encoding="utf-8")) or {}
        except (OSError, json.JSONDecodeError, yaml.YAMLError):
            return None

        if not isinstance(payload, dict):
            return None

        return payload