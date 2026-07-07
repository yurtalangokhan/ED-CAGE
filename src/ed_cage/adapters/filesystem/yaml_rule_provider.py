from pathlib import Path
from typing import Any

import yaml

from ed_cage.domain.models import GovernanceRule


class YamlRuleProvider:
    def __init__(self, rules_path: Path) -> None:
        self.rules_path = rules_path

    def load_rules(self) -> list[GovernanceRule]:
        if not self.rules_path.exists():
            raise FileNotFoundError(f"Rules path not found: {self.rules_path}")

        rules: list[GovernanceRule] = []

        for rule_file in sorted(self.rules_path.glob("*.yaml")):
            rules.extend(self._load_rule_file(rule_file))

        return rules

    def _load_rule_file(self, rule_file: Path) -> list[GovernanceRule]:
        with rule_file.open("r", encoding="utf-8") as file:
            raw_data: dict[str, Any] = yaml.safe_load(file) or {}

        raw_rules = raw_data.get("rules", [])

        if not isinstance(raw_rules, list):
            raise ValueError(f"'rules' must be a list in {rule_file}")

        return [GovernanceRule.model_validate(raw_rule) for raw_rule in raw_rules]