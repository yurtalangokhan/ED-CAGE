from typing import Protocol

from ed_cage.domain.models import GovernanceFinding, GovernanceRule, ProjectContext


class GovernanceCheck(Protocol):
    @property
    def check_type(self) -> str:
        raise NotImplementedError

    def evaluate(self, rule: GovernanceRule, context: ProjectContext) -> GovernanceFinding:
        raise NotImplementedError