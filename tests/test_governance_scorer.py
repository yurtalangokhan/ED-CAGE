from ed_cage.application.scoring import GovernanceScorer
from ed_cage.domain.enums import CheckStatus, Severity
from ed_cage.domain.models import GovernanceFinding


def test_governance_scorer_returns_100_when_all_findings_passed() -> None:
    findings = [
        GovernanceFinding(
            rule_id="TEST-001",
            title="Medium passed",
            severity=Severity.MEDIUM,
            status=CheckStatus.PASSED,
            message="Passed.",
        ),
        GovernanceFinding(
            rule_id="TEST-002",
            title="High passed",
            severity=Severity.HIGH,
            status=CheckStatus.PASSED,
            message="Passed.",
        ),
    ]

    score = GovernanceScorer().calculate(findings)

    assert score.score == 100.0
    assert score.achieved_score == 8.0
    assert score.max_score == 8.0
    assert score.evaluated_findings == 2
    assert score.skipped_findings == 0


def test_governance_scorer_penalizes_failed_findings() -> None:
    findings = [
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

    score = GovernanceScorer().calculate(findings)

    assert score.score == 37.5
    assert score.achieved_score == 3.0
    assert score.max_score == 8.0
    assert score.evaluated_findings == 2
    assert score.skipped_findings == 0


def test_governance_scorer_excludes_skipped_findings_from_score() -> None:
    findings = [
        GovernanceFinding(
            rule_id="TEST-001",
            title="Medium passed",
            severity=Severity.MEDIUM,
            status=CheckStatus.PASSED,
            message="Passed.",
        ),
        GovernanceFinding(
            rule_id="TEST-002",
            title="High skipped",
            severity=Severity.HIGH,
            status=CheckStatus.SKIPPED,
            message="Skipped.",
        ),
    ]

    score = GovernanceScorer().calculate(findings)

    assert score.score == 100.0
    assert score.achieved_score == 3.0
    assert score.max_score == 3.0
    assert score.evaluated_findings == 1
    assert score.skipped_findings == 1


def test_governance_scorer_returns_100_when_no_findings_are_evaluated() -> None:
    score = GovernanceScorer().calculate([])

    assert score.score == 100.0
    assert score.achieved_score == 0.0
    assert score.max_score == 0.0
    assert score.evaluated_findings == 0
    assert score.skipped_findings == 0