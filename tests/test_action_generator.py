from datetime import UTC, datetime

from ed_cage.application.action_generator import GovernanceActionGenerator
from ed_cage.domain.enums import (
    ActionPriority,
    CheckStatus,
    GovernanceActionType,
    Severity,
)
from ed_cage.domain.models import (
    GovernanceActionDefinition,
    GovernanceFinding,
    GovernanceRunResult,
)


def test_action_generator_creates_action_for_matching_rule_id() -> None:
    result = _build_result(
        [
            GovernanceFinding(
                rule_id="SVC-001",
                title="Services must expose a health endpoint",
                severity=Severity.HIGH,
                status=CheckStatus.FAILED,
                message="Health endpoint check failed.",
                category="service",
                target="service",
                check_type="http_health_endpoint",
            )
        ]
    )

    definitions = [
        GovernanceActionDefinition(
            id="ACTION-SVC-001",
            rule_id="SVC-001",
            status=CheckStatus.FAILED,
            title="Add health endpoint",
            action_type=GovernanceActionType.REMEDIATION,
            priority=ActionPriority.HIGH,
            recommendation="Add a health endpoint.",
            implementation_hint="Expose /health.",
        )
    ]

    actions = GovernanceActionGenerator().generate(result, definitions)

    assert len(actions) == 1
    assert actions[0].action_id == "ACTION-SVC-001:SVC-001"
    assert actions[0].rule_id == "SVC-001"
    assert actions[0].priority == ActionPriority.HIGH
    assert actions[0].action_type == GovernanceActionType.REMEDIATION
    assert actions[0].recommendation == "Add a health endpoint."


def test_action_generator_does_not_create_action_for_passed_finding() -> None:
    result = _build_result(
        [
            GovernanceFinding(
                rule_id="SVC-001",
                title="Services must expose a health endpoint",
                severity=Severity.HIGH,
                status=CheckStatus.PASSED,
                message="Passed.",
            )
        ]
    )

    definitions = [
        GovernanceActionDefinition(
            id="ACTION-SVC-001",
            rule_id="SVC-001",
            title="Add health endpoint",
            recommendation="Add a health endpoint.",
        )
    ]

    actions = GovernanceActionGenerator().generate(result, definitions)

    assert actions == []


def test_action_generator_uses_default_action_when_no_definition_matches() -> None:
    result = _build_result(
        [
            GovernanceFinding(
                rule_id="CUSTOM-001",
                title="Custom failed rule",
                severity=Severity.CRITICAL,
                status=CheckStatus.FAILED,
                message="Custom rule failed.",
                category="custom",
            )
        ]
    )

    actions = GovernanceActionGenerator().generate(result, [])

    assert len(actions) == 1
    assert actions[0].action_id == "DEFAULT-FAILED:CUSTOM-001"
    assert actions[0].priority == ActionPriority.CRITICAL
    assert actions[0].action_type == GovernanceActionType.REMEDIATION


def test_action_generator_creates_default_investigation_action_for_error() -> None:
    result = _build_result(
        [
            GovernanceFinding(
                rule_id="ERR-001",
                title="Error rule",
                severity=Severity.MEDIUM,
                status=CheckStatus.ERROR,
                message="Unexpected error.",
            )
        ]
    )

    actions = GovernanceActionGenerator().generate(result, [])

    assert len(actions) == 1
    assert actions[0].action_id == "DEFAULT-ERROR:ERR-001"
    assert actions[0].priority == ActionPriority.MEDIUM
    assert actions[0].action_type == GovernanceActionType.INVESTIGATION


def test_action_generator_can_match_by_category_and_status() -> None:
    result = _build_result(
        [
            GovernanceFinding(
                rule_id="SVC-999",
                title="Generic service rule",
                severity=Severity.HIGH,
                status=CheckStatus.FAILED,
                message="Service rule failed.",
                category="service",
                target="service",
                check_type="custom_service_check",
            )
        ]
    )

    definitions = [
        GovernanceActionDefinition(
            id="ACTION-GENERIC-SERVICE-FAILED",
            category="service",
            status=CheckStatus.FAILED,
            title="Review service governance violation",
            action_type=GovernanceActionType.REMEDIATION,
            priority=ActionPriority.HIGH,
            recommendation="Review service-level governance violation.",
        )
    ]

    actions = GovernanceActionGenerator().generate(result, definitions)

    assert len(actions) == 1
    assert actions[0].action_id == "ACTION-GENERIC-SERVICE-FAILED:SVC-999"
    assert actions[0].rule_id == "SVC-999"


def _build_result(findings: list[GovernanceFinding]) -> GovernanceRunResult:
    return GovernanceRunResult(
        project_name="ed-cage",
        started_at=datetime.now(UTC),
        finished_at=datetime.now(UTC),
        findings=findings,
    )