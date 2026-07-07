from typing import Protocol

from ed_cage.domain.models import GovernanceRule


class RuleProvider(Protocol):
    def load_rules(self) -> list[GovernanceRule]:
        raise NotImplementedError