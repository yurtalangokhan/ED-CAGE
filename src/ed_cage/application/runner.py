from datetime import UTC, datetime

from ed_cage.application.evidence_normalizer import EvidenceNormalizer
from ed_cage.application.rule_filter import GovernanceRuleFilter
from ed_cage.application.scoring import GovernanceScorer
from ed_cage.domain.enums import CheckStatus
from ed_cage.domain.models import (
    GovernanceFinding,
    GovernanceRunResult,
    GovernanceRule,
    ProjectContext,
    RuleFilterCriteria,
)
from ed_cage.ports.check import GovernanceCheck
from ed_cage.ports.rule_provider import RuleProvider


class GovernanceRunner:
    def __init__(
        self,
        rule_provider: RuleProvider,
        checks: list[GovernanceCheck],
        scorer: GovernanceScorer | None = None,
        rule_filter: GovernanceRuleFilter | None = None,
        evidence_normalizer: EvidenceNormalizer | None = None,
    ) -> None:
        self.rule_provider = rule_provider
        self.checks = {check.check_type: check for check in checks}
        self.scorer = scorer or GovernanceScorer()
        self.rule_filter = rule_filter or GovernanceRuleFilter()
        self.evidence_normalizer = evidence_normalizer or EvidenceNormalizer()

    def run(
        self,
        context: ProjectContext,
        filter_criteria: RuleFilterCriteria | None = None,
    ) -> GovernanceRunResult:
        started_at = datetime.now(UTC)
        rules = self.rule_provider.load_rules()
        rules = self.rule_filter.apply(rules, filter_criteria)

        findings: list[GovernanceFinding] = []

        for rule in rules:
            if not rule.enabled:
                findings.append(self._skipped_finding(rule, "Rule is disabled."))
                continue

            check = self.checks.get(rule.check_type)

            if check is None:
                findings.append(
                    self._skipped_finding(
                        rule,
                        f"No check implementation registered for check_type='{rule.check_type}'.",
                    )
                )
                continue

            try:
                finding = check.evaluate(rule, context)
                findings.append(self._enrich_finding_with_rule_metadata(finding, rule))
            except Exception as exc:
                findings.append(self._error_finding(rule, exc))

        normalized_findings = self.evidence_normalizer.normalize_findings(findings)

        finished_at = datetime.now(UTC)
        score = self.scorer.calculate(normalized_findings)

        return GovernanceRunResult(
            project_name=context.project_name,
            started_at=started_at,
            finished_at=finished_at,
            findings=normalized_findings,
            score=score,
        )

    def _enrich_finding_with_rule_metadata(
        self,
        finding: GovernanceFinding,
        rule: GovernanceRule,
    ) -> GovernanceFinding:
        return finding.model_copy(
            update={
                "category": rule.category,
                "target": rule.target,
                "check_type": rule.check_type,
            }
        )

    def _skipped_finding(self, rule: GovernanceRule, message: str) -> GovernanceFinding:
        return GovernanceFinding(
            rule_id=rule.id,
            title=rule.title,
            severity=rule.severity,
            status=CheckStatus.SKIPPED,
            message=message,
            category=rule.category,
            target=rule.target,
            check_type=rule.check_type,
            evidence=[],
        )

    def _error_finding(self, rule: GovernanceRule, exc: Exception) -> GovernanceFinding:
        return GovernanceFinding(
            rule_id=rule.id,
            title=rule.title,
            severity=rule.severity,
            status=CheckStatus.ERROR,
            message=f"Unexpected check execution error: {exc}",
            category=rule.category,
            target=rule.target,
            check_type=rule.check_type,
            evidence=[],
        )