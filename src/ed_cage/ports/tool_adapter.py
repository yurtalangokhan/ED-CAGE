from typing import Protocol

from ed_cage.domain.models import GovernanceRule, ProjectContext, ToolExecutionResult


class ToolAdapter(Protocol):
    @property
    def tool_name(self) -> str:
        raise NotImplementedError

    def is_available(self) -> bool:
        raise NotImplementedError

    def collect(
        self,
        rule: GovernanceRule,
        context: ProjectContext,
    ) -> ToolExecutionResult:
        raise NotImplementedError