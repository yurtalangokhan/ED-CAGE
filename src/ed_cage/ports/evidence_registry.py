from typing import Protocol

from ed_cage.domain.models import EvidenceRegistryWriteResult, GovernanceRunResult


class EvidenceRegistry(Protocol):
    def store(self, result: GovernanceRunResult) -> EvidenceRegistryWriteResult:
        raise NotImplementedError