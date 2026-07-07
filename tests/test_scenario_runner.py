from datetime import UTC, datetime

from ed_cage.application.scenario_runner import ScenarioRunner
from ed_cage.domain.enums import ActionPriority, CheckStatus, GovernanceActionType, Severity
from ed_cage.domain.models import (
    GovernanceAction,
    GovernanceFinding,
    GovernanceGateResult,
    GovernanceRunResult,
    GovernanceScore,
    ScenarioDefinition,
    ScenarioExpectedAction,
    ScenarioExpectedFinding,
    ScenarioExpectedOutcome,
)


def test_scenario_runner_passes_when_expected_results_match() -> None:
    scenario = ScenarioDefinition(
        scenario_id="SCN-001",
        name="Repository baseline",
        expected=ScenarioExpectedOutcome(
            gate_passed=True,
            minimum_score=100,
            maximum_score=100,
            finding_count=2,
            action_count=0,
            findings=[
                ScenarioExpectedFinding(rule_id="REPO-001", status=CheckStatus.PASSED),
                ScenarioExpectedFinding(rule_id="REPO-002", status=CheckStatus.PASSED),
            ],
        ),
    )

    result = _build_result(
        findings=[
            GovernanceFinding(
                rule_id="REPO-001",
                title="Repository must contain README",
                severity=Severity.MEDIUM,
                status=CheckStatus.PASSED,
                message="Passed.",
            ),
            GovernanceFinding(
                rule_id="REPO-002",
                title="Repository must contain pyproject",
                severity=Severity.MEDIUM,
                status=CheckStatus.PASSED,
                message="Passed.",
            ),
        ],
        score=100,
        gate_passed=True,
        actions=[],
    )

    scenario_result = ScenarioRunner().run(scenario, result)

    assert scenario_result.passed is True
    assert all(assertion.passed for assertion in scenario_result.assertions)


def test_scenario_runner_fails_when_expected_finding_is_missing() -> None:
    scenario = ScenarioDefinition(
        scenario_id="SCN-002",
        name="Missing finding scenario",
        expected=ScenarioExpectedOutcome(
            findings=[
                ScenarioExpectedFinding(rule_id="SVC-001", status=CheckStatus.FAILED),
            ],
        ),
    )

    result = _build_result(
        findings=[],
        score=100,
        gate_passed=True,
        actions=[],
    )

    scenario_result = ScenarioRunner().run(scenario, result)

    assert scenario_result.passed is False
    assert any(
        assertion.name == "finding:SVC-001" and not assertion.passed
        for assertion in scenario_result.assertions
    )


def test_scenario_runner_fails_when_score_is_below_expected_minimum() -> None:
    scenario = ScenarioDefinition(
        scenario_id="SCN-003",
        name="Minimum score scenario",
        expected=ScenarioExpectedOutcome(
            minimum_score=80,
        ),
    )

    result = _build_result(
        findings=[],
        score=70,
        gate_passed=True,
        actions=[],
    )

    scenario_result = ScenarioRunner().run(scenario, result)

    assert scenario_result.passed is False
    assert any(
        assertion.name == "minimum_score" and not assertion.passed
        for assertion in scenario_result.assertions
    )


def test_scenario_runner_validates_expected_action() -> None:
    scenario = ScenarioDefinition(
        scenario_id="SCN-004",
        name="Action scenario",
        expected=ScenarioExpectedOutcome(
            action_count=1,
            actions=[
                ScenarioExpectedAction(
                    rule_id="SVC-001",
                    priority=ActionPriority.HIGH,
                    action_type=GovernanceActionType.REMEDIATION,
                )
            ],
        ),
    )

    result = _build_result(
        findings=[],
        score=50,
        gate_passed=False,
        actions=[
            GovernanceAction(
                action_id="ACTION-SVC-001:SVC-001",
                rule_id="SVC-001",
                finding_status=CheckStatus.FAILED,
                severity=Severity.HIGH,
                title="Add health endpoint",
                action_type=GovernanceActionType.REMEDIATION,
                priority=ActionPriority.HIGH,
                recommendation="Add health endpoint.",
            )
        ],
    )

    scenario_result = ScenarioRunner().run(scenario, result)

    assert scenario_result.passed is True


def _build_result(
    findings: list[GovernanceFinding],
    score: float,
    gate_passed: bool,
    actions: list[GovernanceAction],
) -> GovernanceRunResult:
    return GovernanceRunResult(
        project_name="ed-cage",
        started_at=datetime.now(UTC),
        finished_at=datetime.now(UTC),
        findings=findings,
        score=GovernanceScore(
            score=score,
            achieved_score=score,
            max_score=100,
            total_findings=len(findings),
            evaluated_findings=len(findings),
            skipped_findings=0,
        ),
        gate_result=GovernanceGateResult(
            passed=gate_passed,
            actual_score=score,
            minimum_score=80,
        ),
        actions=actions,
    )