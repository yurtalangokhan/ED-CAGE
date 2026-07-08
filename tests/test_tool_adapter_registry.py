from ed_cage.application.tool_adapter_registry import ToolAdapterRegistry
from ed_cage.domain.enums import ToolExecutionStatus
from ed_cage.domain.models import GovernanceRule, ProjectContext, ToolExecutionResult


class FakeToolAdapter:
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
            message="fake result",
        )


def test_tool_adapter_registry_registers_and_gets_adapter() -> None:
    adapter = FakeToolAdapter()
    registry = ToolAdapterRegistry(adapters=[adapter])

    assert registry.get("fake_tool") is adapter
    assert registry.get("FAKE_TOOL") is adapter
    assert registry.names() == ["fake_tool"]


def test_tool_adapter_registry_returns_none_for_unknown_adapter() -> None:
    registry = ToolAdapterRegistry()

    assert registry.get("unknown") is None


def test_tool_adapter_registry_rejects_duplicate_adapter() -> None:
    adapter = FakeToolAdapter()
    registry = ToolAdapterRegistry(adapters=[adapter])

    try:
        registry.register(adapter)
    except ValueError as exc:
        assert "Duplicate tool adapter" in str(exc)
    else:
        raise AssertionError("Expected duplicate adapter registration to fail.")
    
def test_default_tool_adapter_registry_includes_opa_adapter() -> None:
    registry = ToolAdapterRegistry.default()

    assert "opa" in registry.names()

def test_default_tool_adapter_registry_includes_kube_linter_adapter() -> None:
    registry = ToolAdapterRegistry.default()

    assert "kube_linter" in registry.names()

def test_default_tool_adapter_registry_includes_trivy_adapter() -> None:
    registry = ToolAdapterRegistry.default()

    assert "trivy" in registry.names()