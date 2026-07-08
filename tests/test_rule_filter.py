from ed_cage.application.rule_filter import GovernanceRuleFilter
from ed_cage.domain.enums import ExecutionMode, Severity
from ed_cage.domain.models import GovernanceRule, RuleFilterCriteria


def test_rule_filter_returns_all_rules_when_no_criteria_are_defined() -> None:
    rules = _build_rules()

    filtered_rules = GovernanceRuleFilter().apply(
        rules=rules,
        criteria=RuleFilterCriteria(),
    )

    assert len(filtered_rules) == 3


def test_rule_filter_filters_by_rule_id() -> None:
    rules = _build_rules()

    filtered_rules = GovernanceRuleFilter().apply(
        rules=rules,
        criteria=RuleFilterCriteria(rule_ids=["SVC-001"]),
    )

    assert len(filtered_rules) == 1
    assert filtered_rules[0].id == "SVC-001"


def test_rule_filter_filters_by_multiple_rule_ids() -> None:
    rules = _build_rules()

    filtered_rules = GovernanceRuleFilter().apply(
        rules=rules,
        criteria=RuleFilterCriteria(rule_ids=["REPO-001", "SVC-001"]),
    )

    assert [rule.id for rule in filtered_rules] == ["REPO-001", "SVC-001"]


def test_rule_filter_filters_by_category() -> None:
    rules = _build_rules()

    filtered_rules = GovernanceRuleFilter().apply(
        rules=rules,
        criteria=RuleFilterCriteria(categories=["service"]),
    )

    assert len(filtered_rules) == 1
    assert filtered_rules[0].id == "SVC-001"


def test_rule_filter_filters_by_severity() -> None:
    rules = _build_rules()

    filtered_rules = GovernanceRuleFilter().apply(
        rules=rules,
        criteria=RuleFilterCriteria(severities=[Severity.HIGH]),
    )

    assert len(filtered_rules) == 1
    assert filtered_rules[0].id == "SVC-001"


def test_rule_filter_filters_by_check_type() -> None:
    rules = _build_rules()

    filtered_rules = GovernanceRuleFilter().apply(
        rules=rules,
        criteria=RuleFilterCriteria(check_types=["required_files"]),
    )

    assert len(filtered_rules) == 2
    assert [rule.id for rule in filtered_rules] == ["REPO-001", "REPO-002"]


def test_rule_filter_filters_by_target() -> None:
    rules = _build_rules()

    filtered_rules = GovernanceRuleFilter().apply(
        rules=rules,
        criteria=RuleFilterCriteria(targets=["repository"]),
    )

    assert len(filtered_rules) == 2
    assert [rule.id for rule in filtered_rules] == ["REPO-001", "REPO-002"]


def test_rule_filter_applies_and_between_different_criteria() -> None:
    rules = _build_rules()

    filtered_rules = GovernanceRuleFilter().apply(
        rules=rules,
        criteria=RuleFilterCriteria(
            categories=["repository"],
            severities=[Severity.HIGH],
        ),
    )

    assert filtered_rules == []


def test_rule_filter_filters_security_category() -> None:
    rules = [
        _build_rule(
            rule_id="DEP-007",
            category="security",
            check_type="kubernetes_security_context",
        ),
        _build_rule(
            rule_id="DEP-008",
            category="security",
            check_type="kubernetes_security_context",
        ),
        _build_rule(
            rule_id="SEC-001",
            category="security",
            check_type="repository_secret_patterns",
        ),
        _build_rule(
            rule_id="API-001",
            category="api",
            check_type="openapi_document_policy",
        ),
    ]

    filtered_rules = GovernanceRuleFilter().apply(
        rules=rules,
        criteria=RuleFilterCriteria(
            categories=["security"],
        ),
    )

    assert [rule.id for rule in filtered_rules] == [
        "DEP-007",
        "DEP-008",
        "SEC-001",
    ]


def test_rule_filter_filters_reliability_category() -> None:
    rules = [
        _build_rule(
            rule_id="REL-001",
            category="reliability",
            check_type="kubernetes_replica_policy",
            target="kubernetes",
        ),
        _build_rule(
            rule_id="REL-002",
            category="reliability",
            check_type="repository_configuration_patterns",
            target="repository",
        ),
        _build_rule(
            rule_id="SEC-001",
            category="security",
            check_type="repository_secret_patterns",
            target="repository",
        ),
    ]

    filtered_rules = GovernanceRuleFilter().apply(
        rules=rules,
        criteria=RuleFilterCriteria(
            categories=["reliability"],
        ),
    )

    assert [rule.id for rule in filtered_rules] == [
        "REL-001",
        "REL-002",
    ]


def test_rule_filter_static_mode_excludes_runtime_checks() -> None:
    rules = [
        _build_rule(
            rule_id="SVC-001",
            category="service",
            check_type="http_health_endpoint",
            target="service",
        ),
        _build_rule(
            rule_id="REL-001",
            category="reliability",
            check_type="kubernetes_replica_policy",
            target="kubernetes",
        ),
        _build_rule(
            rule_id="ARCH-001",
            category="architecture",
            check_type="repository_required_paths",
            target="repository",
        ),
    ]

    filtered_rules = GovernanceRuleFilter().apply(
        rules=rules,
        criteria=RuleFilterCriteria(
            execution_mode=ExecutionMode.STATIC,
        ),
    )

    assert [rule.id for rule in filtered_rules] == [
        "REL-001",
        "ARCH-001",
    ]


def test_rule_filter_runtime_mode_includes_only_runtime_checks() -> None:
    rules = [
        _build_rule(
            rule_id="SVC-001",
            category="service",
            check_type="http_health_endpoint",
            target="service",
        ),
        _build_rule(
            rule_id="API-001",
            category="api",
            check_type="openapi_document_policy",
            target="service",
        ),
        _build_rule(
            rule_id="REL-001",
            category="reliability",
            check_type="kubernetes_replica_policy",
            target="kubernetes",
        ),
    ]

    filtered_rules = GovernanceRuleFilter().apply(
        rules=rules,
        criteria=RuleFilterCriteria(
            execution_mode=ExecutionMode.RUNTIME,
        ),
    )

    assert [rule.id for rule in filtered_rules] == [
        "SVC-001",
        "API-001",
    ]


def test_rule_filter_mixed_mode_includes_static_and_runtime_checks() -> None:
    rules = [
        _build_rule(
            rule_id="SVC-001",
            category="service",
            check_type="http_health_endpoint",
            target="service",
        ),
        _build_rule(
            rule_id="REL-001",
            category="reliability",
            check_type="kubernetes_replica_policy",
            target="kubernetes",
        ),
    ]

    filtered_rules = GovernanceRuleFilter().apply(
        rules=rules,
        criteria=RuleFilterCriteria(
            execution_mode=ExecutionMode.MIXED,
        ),
    )

    assert [rule.id for rule in filtered_rules] == [
        "SVC-001",
        "REL-001",
    ]


def test_rule_filter_excludes_disabled_rule_ids() -> None:
    rules = [
        _build_rule("DEP-001"),
        _build_rule("DEP-002"),
        _build_rule("SEC-001"),
    ]

    filtered_rules = GovernanceRuleFilter().apply(
        rules=rules,
        criteria=RuleFilterCriteria(
            disabled_rule_ids=[
                "DEP-001",
                "DEP-002",
            ],
        ),
    )

    assert [rule.id for rule in filtered_rules] == ["SEC-001"]


def test_rule_filter_disabled_rule_ids_are_case_insensitive() -> None:
    rules = [
        _build_rule("DEP-001"),
        _build_rule("SEC-001"),
    ]

    filtered_rules = GovernanceRuleFilter().apply(
        rules=rules,
        criteria=RuleFilterCriteria(
            disabled_rule_ids=[
                "dep-001",
            ],
        ),
    )

    assert [rule.id for rule in filtered_rules] == ["SEC-001"]


def test_rule_filter_disabled_rule_ids_override_requested_rule_ids() -> None:
    rules = [
        _build_rule("DEP-001"),
        _build_rule("SEC-001"),
    ]

    filtered_rules = GovernanceRuleFilter().apply(
        rules=rules,
        criteria=RuleFilterCriteria(
            rule_ids=[
                "DEP-001",
                "SEC-001",
            ],
            disabled_rule_ids=[
                "DEP-001",
            ],
        ),
    )

    assert [rule.id for rule in filtered_rules] == ["SEC-001"]


def _build_rules() -> list[GovernanceRule]:
    return [
        _build_rule(
            rule_id="REPO-001",
            title="Repository must contain README",
            category="repository",
            severity=Severity.MEDIUM,
            target="repository",
            check_type="required_files",
        ),
        _build_rule(
            rule_id="REPO-002",
            title="Repository must contain pyproject",
            category="repository",
            severity=Severity.MEDIUM,
            target="repository",
            check_type="required_files",
        ),
        _build_rule(
            rule_id="SVC-001",
            title="Services must expose a health endpoint",
            category="service",
            severity=Severity.HIGH,
            target="service",
            check_type="http_health_endpoint",
        ),
    ]


def _build_rule(
    rule_id: str,
    title: str | None = None,
    category: str = "repository",
    check_type: str = "required_files",
    severity: Severity = Severity.MEDIUM,
    target: str = "repository",
) -> GovernanceRule:
    return GovernanceRule(
        id=rule_id,
        title=title or f"{rule_id} test rule",
        description=f"{rule_id} test description",
        category=category,
        severity=severity,
        target=target,
        check_type=check_type,
        enabled=True,
        params={},
    )