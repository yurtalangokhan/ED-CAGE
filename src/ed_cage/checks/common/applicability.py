from ed_cage.domain.enums import CheckStatus
from ed_cage.domain.models import Evidence, GovernanceFinding, GovernanceRule


def build_skipped_finding(
    rule: GovernanceRule,
    message: str,
    evidence_source: str,
    evidence_message: str,
    evidence_data: dict[str, object],
) -> GovernanceFinding:
    return GovernanceFinding(
        rule_id=rule.id,
        title=rule.title,
        severity=rule.severity,
        status=CheckStatus.SKIPPED,
        message=message,
        evidence=[
            Evidence(
                source=evidence_source,
                message=evidence_message,
                data=evidence_data,
            )
        ],
    )