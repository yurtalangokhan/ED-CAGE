from collections import Counter

from ed_cage.domain.enums import CheckStatus, Severity
from ed_cage.domain.models import GovernanceFinding, GovernanceScore


class GovernanceScorer:
    def __init__(self) -> None:
        self.severity_weights: dict[Severity, float] = {
            Severity.INFO: 1.0,
            Severity.LOW: 2.0,
            Severity.MEDIUM: 3.0,
            Severity.HIGH: 5.0,
            Severity.CRITICAL: 8.0,
        }

    def calculate(self, findings: list[GovernanceFinding]) -> GovernanceScore:
        status_counts = Counter(finding.status.value for finding in findings)
        severity_counts = Counter(finding.severity.value for finding in findings)

        achieved_score = 0.0
        max_score = 0.0
        skipped_findings = 0

        for finding in findings:
            if finding.status == CheckStatus.SKIPPED:
                skipped_findings += 1
                continue

            weight = self.severity_weights.get(finding.severity, 1.0)
            max_score += weight

            if finding.status == CheckStatus.PASSED:
                achieved_score += weight

        score = 100.0 if max_score == 0 else round((achieved_score / max_score) * 100, 2)

        return GovernanceScore(
            score=score,
            achieved_score=round(achieved_score, 2),
            max_score=round(max_score, 2),
            total_findings=len(findings),
            evaluated_findings=len(findings) - skipped_findings,
            skipped_findings=skipped_findings,
            status_summary={
                status.value: int(status_counts.get(status.value, 0)) for status in CheckStatus
            },
            severity_summary={
                severity.value: int(severity_counts.get(severity.value, 0)) for severity in Severity
            },
        )