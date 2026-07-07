from typing import Protocol

from ed_cage.domain.models import ScenarioDefinition


class ScenarioProvider(Protocol):
    def load_scenario(self) -> ScenarioDefinition:
        raise NotImplementedError