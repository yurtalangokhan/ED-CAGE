from ed_cage.application.scoring import GovernanceScorer
from ed_cage.domain.enums import CheckStatus, Severity
from ed_cage.domain.models import GovernanceFinding, ScoringConfig


def test_governance_scorer_returns_100_when_all_findings_passed() -> None:
    findings = [
        GovernanceFinding(
            rule_id="TEST-001",
            title="Medium passed",
            severity=Severity.MEDIUM,
            status=CheckStatus.PASSED,
            message="Passed.",
            category="security",
        ),
        GovernanceFinding(
            rule_id="TEST-002",
            title="High passed",
            severity=Severity.HIGH,
            status=CheckStatus.PASSED,
            message="Passed.",
            category="security",
        ),
    ]

    score = GovernanceScorer().calculate(findings)

    assert score.score == 100.0
    assert score.achieved_score == 130.0
    assert score.max_score == 130.0
    assert score.evaluated_findings == 2
    assert score.skipped_findings == 0
    assert score.maturity_band == "Continuously Governed Architecture"
    assert score.category_scores == {"security": 100.0}
    assert score.category_weights == {"security": 1.3}


def test_governance_scorer_penalizes_failed_findings() -> None:
    findings = [
        GovernanceFinding(
            rule_id="TEST-001",
            title="Medium passed",
            severity=Severity.MEDIUM,
            status=CheckStatus.PASSED,
            message="Passed.",
            category="security",
        ),
        GovernanceFinding(
            rule_id="TEST-002",
            title="High failed",
            severity=Severity.HIGH,
            status=CheckStatus.FAILED,
            message="Failed.",
            category="security",
        ),
    ]

    score = GovernanceScorer().calculate(findings)

    assert score.score == 50.0
    assert score.achieved_score == 65.0
    assert score.max_score == 130.0
    assert score.evaluated_findings == 2
    assert score.skipped_findings == 0
    assert score.maturity_band == "Emerging Governance"
    assert score.category_scores == {"security": 50.0}


def test_governance_scorer_excludes_skipped_findings_from_score() -> None:
    findings = [
        GovernanceFinding(
            rule_id="TEST-001",
            title="Medium passed",
            severity=Severity.MEDIUM,
            status=CheckStatus.PASSED,
            message="Passed.",
            category="security",
        ),
        GovernanceFinding(
            rule_id="TEST-002",
            title="High skipped",
            severity=Severity.HIGH,
            status=CheckStatus.SKIPPED,
            message="Skipped.",
            category="deployment",
        ),
    ]

    score = GovernanceScorer().calculate(findings)

    assert score.score == 100.0
    assert score.achieved_score == 130.0
    assert score.max_score == 130.0
    assert score.evaluated_findings == 1
    assert score.skipped_findings == 1
    assert score.applicable_rule_count == 1
    assert score.not_applicable_rule_count == 1
    assert "deployment" not in score.category_scores


def test_governance_scorer_returns_100_when_no_findings_are_evaluated() -> None:
    score = GovernanceScorer().calculate([])

    assert score.score == 100.0
    assert score.achieved_score == 0.0
    assert score.max_score == 0.0
    assert score.evaluated_findings == 0
    assert score.skipped_findings == 0
    assert score.maturity_band == "Continuously Governed Architecture"


def test_governance_scorer_calculates_category_weighted_score() -> None:
    findings = [
        GovernanceFinding(
            rule_id="SEC-001",
            title="Security passed",
            severity=Severity.HIGH,
            status=CheckStatus.PASSED,
            message="Passed.",
            category="security",
        ),
        GovernanceFinding(
            rule_id="SEC-002",
            title="Security failed",
            severity=Severity.HIGH,
            status=CheckStatus.FAILED,
            message="Failed.",
            category="security",
        ),
        GovernanceFinding(
            rule_id="REL-001",
            title="Reliability passed",
            severity=Severity.MEDIUM,
            status=CheckStatus.PASSED,
            message="Passed.",
            category="reliability",
        ),
    ]
    scoring_config = ScoringConfig(
        category_weights={
            "security": 2.0,
            "reliability": 1.0,
        }
    )

    score = GovernanceScorer(scoring_config).calculate(findings)

    assert score.category_scores == {
        "reliability": 100.0,
        "security": 50.0,
    }
    assert score.category_weights == {
        "reliability": 1.0,
        "security": 2.0,
    }
    assert score.score == 66.67
    assert score.achieved_score == 200.0
    assert score.max_score == 300.0
    assert score.maturity_band == "Managed Governance"