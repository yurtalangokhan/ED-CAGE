from pathlib import Path

from ed_cage.application.tool_adapter_registry import ToolAdapterRegistry
from ed_cage.checks.tools.external_tool_check import ExternalToolCheck
from ed_cage.domain.enums import CheckStatus, Severity, ToolExecutionStatus
from ed_cage.domain.models import GovernanceRule, ProjectContext, ToolExecutionResult


class SuccessfulFakeToolAdapter:
    @property
    def tool_name(self) -> str:
        return "fake_tool"

    def is_available(self) -> bool:
        return True

    def collect(
        self,
        rule: GovernanceRule,
        context: ProjectContext,
    ) -> ToolExecutionResult:
        return ToolExecutionResult(
            tool_name=self.tool_name,
            status=ToolExecutionStatus.SUCCESS,
            message="Fake tool completed successfully.",
            findings=[],
        )


class FindingFakeToolAdapter:
    @property
    def tool_name(self) -> str:
        return "fake_tool"

    def is_available(self) -> bool:
        return True

    def collect(
        self,
        rule: GovernanceRule,
        context: ProjectContext,
    ) -> ToolExecutionResult:
        return ToolExecutionResult(
            tool_name=self.tool_name,
            status=ToolExecutionStatus.SUCCESS,
            message="Fake tool produced findings.",
            findings=[
                {
                    "id": "FAKE-001",
                    "message": "Fake violation.",
                }
            ],
        )


class UnavailableFakeToolAdapter:
    @property
    def tool_name(self) -> str:
        return "fake_tool"

    def is_available(self) -> bool:
        return False

    def collect(
        self,
        rule: GovernanceRule,
        context: ProjectContext,
    ) -> ToolExecutionResult:
        raise AssertionError("collect should not be called when tool is unavailable")


def test_external_tool_check_passes_when_tool_has_no_findings(tmp_path: Path) -> None:
    check = ExternalToolCheck(
        tool_registry=ToolAdapterRegistry(
            adapters=[SuccessfulFakeToolAdapter()]
        )
    )

    finding = check.evaluate(
        rule=_build_rule(),
        context=_build_context(tmp_path),
    )

    assert finding.status == CheckStatus.PASSED


def test_external_tool_check_fails_when_tool_produces_findings(tmp_path: Path) -> None:
    check = ExternalToolCheck(
        tool_registry=ToolAdapterRegistry(
            adapters=[FindingFakeToolAdapter()]
        )
    )

    finding = check.evaluate(
        rule=_build_rule(),
        context=_build_context(tmp_path),
    )

    assert finding.status == CheckStatus.FAILED
    assert finding.evidence[0].data["findings"][0]["id"] == "FAKE-001"


def test_external_tool_check_skips_when_adapter_is_not_registered(
    tmp_path: Path,
) -> None:
    check = ExternalToolCheck(
        tool_registry=ToolAdapterRegistry(adapters=[])
    )

    finding = check.evaluate(
        rule=_build_rule(),
        context=_build_context(tmp_path),
    )

    assert finding.status == CheckStatus.SKIPPED
    assert "not registered" in finding.message


def test_external_tool_check_skips_when_tool_is_unavailable(tmp_path: Path) -> None:
    check = ExternalToolCheck(
        tool_registry=ToolAdapterRegistry(
            adapters=[UnavailableFakeToolAdapter()]
        )
    )

    finding = check.evaluate(
        rule=_build_rule(),
        context=_build_context(tmp_path),
    )

    assert finding.status == CheckStatus.SKIPPED
    assert "not available" in finding.message


def _build_rule() -> GovernanceRule:
    return GovernanceRule(
        id="TOOL-001",
        title="External tool rule",
        category="tool",
        severity=Severity.HIGH,
        target="repository",
        check_type="external_tool",
        params={
            "tool": "fake_tool",
        },
    )


def _build_context(repository_path: Path) -> ProjectContext:
    return ProjectContext(
        project_name="test",
        repository_path=repository_path,
        config_path=repository_path / "configs" / "ed-cage.yaml",
        services=[],
    )