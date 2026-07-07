from typing import Protocol

from ed_cage.domain.models import GovernanceActionDefinition


class ActionProvider(Protocol):
    def load_actions(self) -> list[GovernanceActionDefinition]:
        raise NotImplementedError