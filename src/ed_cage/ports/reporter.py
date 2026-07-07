from typing import Protocol

from ed_cage.domain.models import GovernanceRunResult


class ResultReporter(Protocol):
    def report(self, result: GovernanceRunResult) -> None:
        raise NotImplementedError