from datetime import UTC, datetime
from pathlib import Path

from ed_cage.domain.models import (
    EvidenceRegistryRecord,
    EvidenceRegistryWriteResult,
    GovernanceRunResult,
)


class JsonlEvidenceRegistry:
    def __init__(self, registry_path: Path) -> None:
        self.registry_path = registry_path

    def store(self, result: GovernanceRunResult) -> EvidenceRegistryWriteResult:
        self.registry_path.parent.mkdir(parents=True, exist_ok=True)
        self.registry_path.touch(exist_ok=True)

        records = self._build_records(result)

        if not records:
            return EvidenceRegistryWriteResult(
                path=self.registry_path,
                records_written=0,
            )

        with self.registry_path.open("a", encoding="utf-8") as file:
            for record in records:
                file.write(record.model_dump_json() + "\n")

        return EvidenceRegistryWriteResult(
            path=self.registry_path,
            records_written=len(records),
        )

    def _build_records(
        self,
        result: GovernanceRunResult,
    ) -> list[EvidenceRegistryRecord]:
        records: list[EvidenceRegistryRecord] = []
        created_at = datetime.now(UTC)

        for finding in result.findings:
            for evidence in finding.normalized_evidence:
                records.append(
                    EvidenceRegistryRecord(
                        run_id=result.run_id,
                        project_name=result.project_name,
                        rule_id=finding.rule_id,
                        finding_title=finding.title,
                        finding_status=finding.status,
                        severity=finding.severity,
                        source_type=evidence.source_type,
                        source_name=evidence.source_name,
                        resource=evidence.resource,
                        observed_value=evidence.observed_value,
                        expected_value=evidence.expected_value,
                        compliant=evidence.compliant,
                        message=evidence.message,
                        raw_data=evidence.raw_data,
                        metadata={
                            **evidence.metadata,
                            "gate_passed": (
                                result.gate_result.passed
                                if result.gate_result is not None
                                else None
                            ),
                            "governance_score": (
                                result.score.score if result.score is not None else None
                            ),
                        },
                        created_at=created_at,
                    )
                )

        return records