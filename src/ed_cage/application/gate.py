from ed_cage.domain.enums import CheckStatus, Severity
from ed_cage.domain.models import (
    GovernanceGatePolicy,
    GovernanceGateResult,
    GovernanceRunResult,
)


class GovernanceGateEvaluator:
    def evaluate(
        self,
        result: GovernanceRunResult,
        policy: GovernanceGatePolicy,
    ) -> GovernanceGateResult:
        actual_score = result.score.score if result.score is not None else 100.0

        reasons: list[str] = []
        blocking_findings: list[str] = []

        if actual_score < policy.minimum_score:
            reasons.append(
                f"Governance score {actual_score:.2f} is below minimum score "
                f"{policy.minimum_score:.2f}."
            )

        for finding in result.findings:
            if finding.status == CheckStatus.SKIPPED:
                continue

            if finding.status == CheckStatus.ERROR and policy.fail_on_error:
                self._add_blocking_finding(
                    reasons=reasons,
                    blocking_findings=blocking_findings,
                    rule_id=finding.rule_id,
                    reason=f"Execution error detected: {finding.rule_id}",
                )
                continue

            if finding.status != CheckStatus.FAILED:
                continue

            if policy.fail_on_any_failure:
                self._add_blocking_finding(
                    reasons=reasons,
                    blocking_findings=blocking_findings,
                    rule_id=finding.rule_id,
                    reason=f"Failure detected: {finding.rule_id}",
                )
                continue

            if finding.severity == Severity.CRITICAL and policy.fail_on_critical:
                self._add_blocking_finding(
                    reasons=reasons,
                    blocking_findings=blocking_findings,
                    rule_id=finding.rule_id,
                    reason=f"Blocking critical finding detected: {finding.rule_id}",
                )
                continue

            if finding.severity == Severity.HIGH and policy.fail_on_high:
                self._add_blocking_finding(
                    reasons=reasons,
                    blocking_findings=blocking_findings,
                    rule_id=finding.rule_id,
                    reason=f"Blocking high finding detected: {finding.rule_id}",
                )
                continue

            if finding.severity == Severity.MEDIUM and policy.fail_on_medium:
                self._add_blocking_finding(
                    reasons=reasons,
                    blocking_findings=blocking_findings,
                    rule_id=finding.rule_id,
                    reason=f"Blocking medium finding detected: {finding.rule_id}",
                )

        return GovernanceGateResult(
            passed=not reasons,
            actual_score=actual_score,
            minimum_score=policy.minimum_score,
            reasons=reasons,
            blocking_findings=blocking_findings,
        )

    def _add_blocking_finding(
        self,
        reasons: list[str],
        blocking_findings: list[str],
        rule_id: str,
        reason: str,
    ) -> None:
        reasons.append(reason)

        if rule_id not in blocking_findings:
            blocking_findings.append(rule_id)