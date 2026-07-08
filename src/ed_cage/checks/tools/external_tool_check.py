from ed_cage.application.tool_adapter_registry import ToolAdapterRegistry
from ed_cage.domain.enums import CheckStatus, ToolExecutionStatus
from ed_cage.domain.models import Evidence, GovernanceFinding, GovernanceRule, ProjectContext


class ExternalToolCheck:
    def __init__(
        self,
        tool_registry: ToolAdapterRegistry | None = None,
    ) -> None:
        self.tool_registry = tool_registry or ToolAdapterRegistry.default()

    @property
    def check_type(self) -> str:
        return "external_tool"

    def evaluate(self, rule: GovernanceRule, context: ProjectContext) -> GovernanceFinding:
        tool_name = str(rule.params.get("tool", "")).strip()

        if not tool_name:
            return GovernanceFinding(
                rule_id=rule.id,
                title=rule.title,
                severity=rule.severity,
                status=CheckStatus.ERROR,
                message="External tool rule is missing required parameter: tool.",
                evidence=[
                    Evidence(
                        source="external-tool",
                        message="External tool rule configuration is invalid.",
                        data={
                            "params": rule.params,
                            "reason": "missing_tool_parameter",
                        },
                    )
                ],
            )

        adapter = self.tool_registry.get(tool_name)

        if adapter is None:
            return GovernanceFinding(
                rule_id=rule.id,
                title=rule.title,
                severity=rule.severity,
                status=CheckStatus.SKIPPED,
                message=f"External tool adapter is not registered: {tool_name}.",
                evidence=[
                    Evidence(
                        source="external-tool",
                        message="External tool adapter was not found in the registry.",
                        data={
                            "tool": tool_name,
                            "registered_tools": self.tool_registry.names(),
                        },
                    )
                ],
            )

        try:
            is_available = adapter.is_available()
        except Exception as exc:
            return GovernanceFinding(
                rule_id=rule.id,
                title=rule.title,
                severity=rule.severity,
                status=CheckStatus.ERROR,
                message=f"External tool availability check failed: {tool_name}.",
                evidence=[
                    Evidence(
                        source=f"external-tool:{tool_name}",
                        message="External tool availability check raised an exception.",
                        data={
                            "tool": tool_name,
                            "error": str(exc),
                        },
                    )
                ],
            )

        if not is_available:
            return GovernanceFinding(
                rule_id=rule.id,
                title=rule.title,
                severity=rule.severity,
                status=CheckStatus.SKIPPED,
                message=f"External tool is not available: {tool_name}.",
                evidence=[
                    Evidence(
                        source=f"external-tool:{tool_name}",
                        message="External tool is not installed or not reachable.",
                        data={
                            "tool": tool_name,
                        },
                    )
                ],
            )

        try:
            result = adapter.collect(rule=rule, context=context)
        except Exception as exc:
            return GovernanceFinding(
                rule_id=rule.id,
                title=rule.title,
                severity=rule.severity,
                status=CheckStatus.ERROR,
                message=f"External tool execution failed unexpectedly: {tool_name}.",
                evidence=[
                    Evidence(
                        source=f"external-tool:{tool_name}",
                        message="External tool adapter raised an exception.",
                        data={
                            "tool": tool_name,
                            "error": str(exc),
                        },
                    )
                ],
            )

        evidence = [
            Evidence(
                source=f"external-tool:{result.tool_name}",
                message=result.message,
                data=result.model_dump(mode="json"),
            )
        ]

        if result.status in {
            ToolExecutionStatus.SKIPPED,
            ToolExecutionStatus.UNAVAILABLE,
        }:
            return GovernanceFinding(
                rule_id=rule.id,
                title=rule.title,
                severity=rule.severity,
                status=CheckStatus.SKIPPED,
                message=result.message,
                evidence=evidence,
            )

        if result.status == ToolExecutionStatus.ERROR:
            return GovernanceFinding(
                rule_id=rule.id,
                title=rule.title,
                severity=rule.severity,
                status=CheckStatus.ERROR,
                message=result.message,
                evidence=evidence,
            )

        if result.status == ToolExecutionStatus.FAILED:
            return GovernanceFinding(
                rule_id=rule.id,
                title=rule.title,
                severity=rule.severity,
                status=CheckStatus.FAILED,
                message=result.message,
                evidence=evidence,
            )

        if result.findings:
            return GovernanceFinding(
                rule_id=rule.id,
                title=rule.title,
                severity=rule.severity,
                status=CheckStatus.FAILED,
                message=(
                    f"External tool produced governance finding(s): "
                    f"{len(result.findings)}."
                ),
                evidence=evidence,
            )

        return GovernanceFinding(
            rule_id=rule.id,
            title=rule.title,
            severity=rule.severity,
            status=CheckStatus.PASSED,
            message=f"External tool check passed: {result.tool_name}.",
            evidence=evidence,
        )