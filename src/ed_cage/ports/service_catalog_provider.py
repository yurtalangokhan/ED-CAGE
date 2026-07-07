from typing import Protocol

from ed_cage.domain.models import ServiceDefinition


class ServiceCatalogProvider(Protocol):
    def load_services(self) -> list[ServiceDefinition]:
        raise NotImplementedError