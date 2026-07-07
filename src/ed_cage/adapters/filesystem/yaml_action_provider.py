from pathlib import Path
from typing import Any

import yaml

from ed_cage.domain.models import GovernanceActionDefinition


class YamlActionProvider:
    def __init__(self, actions_path: Path) -> None:
        self.actions_path = actions_path

    def load_actions(self) -> list[GovernanceActionDefinition]:
        if not self.actions_path.exists():
            return []

        with self.actions_path.open("r", encoding="utf-8") as file:
            raw_data: dict[str, Any] = yaml.safe_load(file) or {}

        raw_actions = raw_data.get("actions", [])

        if not isinstance(raw_actions, list):
            raise ValueError(f"'actions' must be a list in {self.actions_path}")

        return [
            GovernanceActionDefinition.model_validate(raw_action)
            for raw_action in raw_actions
        ]