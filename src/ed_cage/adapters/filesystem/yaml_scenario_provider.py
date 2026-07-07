from pathlib import Path
from typing import Any

import yaml

from ed_cage.domain.models import ScenarioDefinition


class YamlScenarioProvider:
    def __init__(self, scenario_path: Path) -> None:
        self.scenario_path = scenario_path

    def load_scenario(self) -> ScenarioDefinition:
        if not self.scenario_path.exists():
            raise FileNotFoundError(f"Scenario file not found: {self.scenario_path}")

        with self.scenario_path.open("r", encoding="utf-8") as file:
            raw_data: dict[str, Any] = yaml.safe_load(file) or {}

        return ScenarioDefinition.model_validate(raw_data)