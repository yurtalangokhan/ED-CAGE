from ed_cage.domain.models import GovernanceRunResult
from ed_cage.ports.reporter import ResultReporter


class CompositeReporter:
    def __init__(self, reporters: list[ResultReporter]) -> None:
        self.reporters = reporters

    def report(self, result: GovernanceRunResult) -> None:
        for reporter in self.reporters:
            reporter.report(result)