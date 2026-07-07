from typing import Any

from ed_cage.domain.enums import CheckStatus
from ed_cage.domain.models import Evidence, GovernanceFinding, NormalizedEvidence


class EvidenceNormalizer:
    def normalize_findings(
        self,
        findings: list[GovernanceFinding],
    ) -> list[GovernanceFinding]:
        return [self.normalize_finding(finding) for finding in findings]

    def normalize_finding(self, finding: GovernanceFinding) -> GovernanceFinding:
        normalized_evidence: list[NormalizedEvidence] = []

        for evidence in finding.evidence:
            normalized_evidence.extend(
                self._normalize_evidence(
                    finding=finding,
                    evidence=evidence,
                )
            )

        return finding.model_copy(
            update={
                "normalized_evidence": normalized_evidence,
            }
        )

    def _normalize_evidence(
        self,
        finding: GovernanceFinding,
        evidence: Evidence,
    ) -> list[NormalizedEvidence]:
        if self._looks_like_http_evidence(evidence):
            return self._normalize_http_evidence(finding, evidence)

        if self._looks_like_filesystem_evidence(evidence):
            return self._normalize_filesystem_evidence(finding, evidence)

        return [
            self._normalize_generic_evidence(
                finding=finding,
                evidence=evidence,
            )
        ]

    def _looks_like_http_evidence(self, evidence: Evidence) -> bool:
        attempts = evidence.data.get("attempts")
        return isinstance(attempts, list)

    def _looks_like_filesystem_evidence(self, evidence: Evidence) -> bool:
        return "missing_files" in evidence.data or "existing_files" in evidence.data

    def _normalize_http_evidence(
        self,
        finding: GovernanceFinding,
        evidence: Evidence,
    ) -> list[NormalizedEvidence]:
        attempts = evidence.data.get("attempts", [])
        expected_status_codes = evidence.data.get("expected_status_codes", [200, 204])

        if not isinstance(attempts, list):
            return [
                self._normalize_generic_evidence(
                    finding=finding,
                    evidence=evidence,
                )
            ]

        normalized_items: list[NormalizedEvidence] = []

        for attempt in attempts:
            if not isinstance(attempt, dict):
                continue

            url = self._get_optional_string(attempt, "url")
            success = attempt.get("success")
            status_code = attempt.get("status_code")
            error = attempt.get("error")

            observed_value: Any | None

            if status_code is not None:
                observed_value = status_code
            else:
                observed_value = error

            normalized_items.append(
                NormalizedEvidence(
                    rule_id=finding.rule_id,
                    source_type="http",
                    source_name=str(evidence.data.get("service", evidence.source)),
                    resource=url,
                    observed_value=observed_value,
                    expected_value=expected_status_codes,
                    compliant=bool(success) if success is not None else None,
                    message=evidence.message,
                    raw_data=attempt,
                    metadata={
                        "finding_status": finding.status.value,
                        "base_url": evidence.data.get("base_url"),
                        "candidate_paths": evidence.data.get("candidate_paths", []),
                    },
                )
            )

        if normalized_items:
            return normalized_items

        return [
            self._normalize_generic_evidence(
                finding=finding,
                evidence=evidence,
            )
        ]

    def _normalize_filesystem_evidence(
        self,
        finding: GovernanceFinding,
        evidence: Evidence,
    ) -> list[NormalizedEvidence]:
        missing_files = evidence.data.get("missing_files", [])
        existing_files = evidence.data.get("existing_files", [])

        if not isinstance(missing_files, list):
            missing_files = []

        if not isinstance(existing_files, list):
            existing_files = []

        expected_files = sorted({str(item) for item in [*missing_files, *existing_files]})

        return [
            NormalizedEvidence(
                rule_id=finding.rule_id,
                source_type="filesystem",
                source_name=evidence.source,
                resource=evidence.source,
                observed_value={
                    "existing_files": existing_files,
                    "missing_files": missing_files,
                },
                expected_value=expected_files,
                compliant=finding.status == CheckStatus.PASSED,
                message=evidence.message,
                raw_data=evidence.data,
                metadata={
                    "finding_status": finding.status.value,
                },
            )
        ]

    def _normalize_generic_evidence(
        self,
        finding: GovernanceFinding,
        evidence: Evidence,
    ) -> NormalizedEvidence:
        return NormalizedEvidence(
            rule_id=finding.rule_id,
            source_type="generic",
            source_name=evidence.source,
            resource=evidence.source,
            observed_value=evidence.data,
            expected_value=None,
            compliant=self._infer_compliance_from_status(finding.status),
            message=evidence.message,
            raw_data=evidence.data,
            metadata={
                "finding_status": finding.status.value,
            },
        )

    def _infer_compliance_from_status(self, status: CheckStatus) -> bool | None:
        match status:
            case CheckStatus.PASSED:
                return True
            case CheckStatus.FAILED | CheckStatus.ERROR:
                return False
            case CheckStatus.SKIPPED:
                return None

    def _get_optional_string(
        self,
        data: dict[str, Any],
        key: str,
    ) -> str | None:
        value = data.get(key)

        if value is None:
            return None

        return str(value)