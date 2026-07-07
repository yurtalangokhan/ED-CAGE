from pathlib import Path
from typing import Any

import yaml

from ed_cage.domain.models import ServiceDefinition


class YamlServiceCatalogProvider:
    def __init__(self, services_path: Path) -> None:
        self.services_path = services_path

    def load_services(self) -> list[ServiceDefinition]:
        if not self.services_path.exists():
            return []

        with self.services_path.open("r", encoding="utf-8") as file:
            raw_data: dict[str, Any] = yaml.safe_load(file) or {}

        raw_services = raw_data.get("services", [])

        if not isinstance(raw_services, list):
            raise ValueError(f"'services' must be a list in {self.services_path}")

        return [ServiceDefinition.model_validate(raw_service) for raw_service in raw_services]