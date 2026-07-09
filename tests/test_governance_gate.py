from datetime import UTC, datetime

from ed_cage.application.gate import GovernanceGateEvaluator
from ed_cage.application.scoring import GovernanceScorer
from ed_cage.domain.enums import CheckStatus, Severity
from ed_cage.domain.models import (
    GovernanceFinding,
    GovernanceGatePolicy,
    GovernanceRunResult,
)


def _build_result(findings: list[GovernanceFinding]) -> GovernanceRunResult:
    score = GovernanceScorer().calculate(findings)

    return GovernanceRunResult(
        project_name="ed-cage",
        started_at=datetime.now(UTC),
        finished_at=datetime.now(UTC),
        findings=findings,
        score=score,
    )


def test_governance_gate_passes_when_score_is_above_threshold() -> None:
    result = _build_result(
        [
            GovernanceFinding(
                rule_id="TEST-001",
                title="Passed rule",
                severity=Severity.HIGH,
                status=CheckStatus.PASSED,
                message="Passed.",
            )
        ]
    )

    gate_result = GovernanceGateEvaluator().evaluate(
        result=result,
        policy=GovernanceGatePolicy(minimum_score=80),
    )

    assert gate_result.passed is True
    assert gate_result.reasons == []
    assert gate_result.blocking_findings == []


def test_governance_gate_fails_when_score_is_below_threshold() -> None:
    result = _build_result(
        [
            GovernanceFinding(
                rule_id="TEST-001",
                title="Medium passed",
                severity=Severity.MEDIUM,
                status=CheckStatus.PASSED,
                message="Passed.",
            ),
            GovernanceFinding(
                rule_id="TEST-002",
                title="High failed",
                severity=Severity.HIGH,
                status=CheckStatus.FAILED,
                message="Failed.",
            ),
        ]
    )

    gate_result = GovernanceGateEvaluator().evaluate(
        result=result,
        policy=GovernanceGatePolicy(
            minimum_score=80,
            fail_on_high=False,
        ),
    )

    assert gate_result.passed is False
    assert gate_result.actual_score == 50.0
    assert "Governance score 50.00 is below minimum score 80.00." in gate_result.reasons


def test_governance_gate_fails_on_high_finding_when_policy_requires_it() -> None:
    result = _build_result(
        [
            GovernanceFinding(
                rule_id="SVC-001",
                title="High failed",
                severity=Severity.HIGH,
                status=CheckStatus.FAILED,
                message="Failed.",
            )
        ]
    )

    gate_result = GovernanceGateEvaluator().evaluate(
        result=result,
        policy=GovernanceGatePolicy(
            minimum_score=0,
            fail_on_high=True,
        ),
    )

    assert gate_result.passed is False
    assert "SVC-001" in gate_result.blocking_findings
    assert "Blocking high finding detected: SVC-001" in gate_result.reasons


def test_governance_gate_ignores_skipped_findings() -> None:
    result = _build_result(
        [
            GovernanceFinding(
                rule_id="SVC-001",
                title="Skipped high rule",
                severity=Severity.HIGH,
                status=CheckStatus.SKIPPED,
                message="Skipped.",
            )
        ]
    )

    gate_result = GovernanceGateEvaluator().evaluate(
        result=result,
        policy=GovernanceGatePolicy(
            minimum_score=80,
            fail_on_high=True,
        ),
    )

    assert gate_result.passed is True
    assert gate_result.reasons == []
    assert gate_result.blocking_findings == []


def test_governance_gate_fails_on_error_when_policy_requires_it() -> None:
    result = _build_result(
        [
            GovernanceFinding(
                rule_id="ERR-001",
                title="Error rule",
                severity=Severity.LOW,
                status=CheckStatus.ERROR,
                message="Unexpected error.",
            )
        ]
    )

    gate_result = GovernanceGateEvaluator().evaluate(
        result=result,
        policy=GovernanceGatePolicy(
            minimum_score=0,
            fail_on_error=True,
        ),
    )

    assert gate_result.passed is False
    assert "ERR-001" in gate_result.blocking_findings
    assert "Execution error detected: ERR-001" in gate_result.reasons