from ed_cage.domain.models import (
    GovernanceAction,
    GovernanceFinding,
    GovernanceRunResult,
    ScenarioAssertionResult,
    ScenarioDefinition,
    ScenarioExpectedAction,
    ScenarioExpectedFinding,
    ScenarioRunResult,
)


class ScenarioRunner:
    def run(
        self,
        scenario: ScenarioDefinition,
        result: GovernanceRunResult,
    ) -> ScenarioRunResult:
        assertions: list[ScenarioAssertionResult] = []

        assertions.extend(self._assert_gate_result(scenario, result))
        assertions.extend(self._assert_score(scenario, result))
        assertions.extend(self._assert_finding_count(scenario, result))
        assertions.extend(self._assert_action_count(scenario, result))
        assertions.extend(self._assert_expected_findings(scenario, result))
        assertions.extend(self._assert_expected_actions(scenario, result))

        passed = all(assertion.passed for assertion in assertions)

        return ScenarioRunResult(
            scenario_id=scenario.scenario_id,
            scenario_name=scenario.name,
            governance_run_id=result.run_id,
            passed=passed,
            assertions=assertions,
        )

    def _assert_gate_result(
        self,
        scenario: ScenarioDefinition,
        result: GovernanceRunResult,
    ) -> list[ScenarioAssertionResult]:
        expected_gate = scenario.expected.gate_passed

        if expected_gate is None:
            return []

        actual_gate = result.gate_result.passed if result.gate_result is not None else None
        passed = actual_gate == expected_gate

        return [
            ScenarioAssertionResult(
                name="gate_passed",
                passed=passed,
                message=(
                    "Gate result matched expected value."
                    if passed
                    else f"Expected gate_passed={expected_gate}, actual={actual_gate}."
                ),
                details={
                    "expected": expected_gate,
                    "actual": actual_gate,
                },
            )
        ]

    def _assert_score(
        self,
        scenario: ScenarioDefinition,
        result: GovernanceRunResult,
    ) -> list[ScenarioAssertionResult]:
        assertions: list[ScenarioAssertionResult] = []
        actual_score = result.score.score if result.score is not None else None

        if scenario.expected.minimum_score is not None:
            minimum_score = scenario.expected.minimum_score
            passed = actual_score is not None and actual_score >= minimum_score

            assertions.append(
                ScenarioAssertionResult(
                    name="minimum_score",
                    passed=passed,
                    message=(
                        "Governance score is greater than or equal to expected minimum."
                        if passed
                        else f"Expected score >= {minimum_score}, actual={actual_score}."
                    ),
                    details={
                        "expected_minimum": minimum_score,
                        "actual": actual_score,
                    },
                )
            )

        if scenario.expected.maximum_score is not None:
            maximum_score = scenario.expected.maximum_score
            passed = actual_score is not None and actual_score <= maximum_score

            assertions.append(
                ScenarioAssertionResult(
                    name="maximum_score",
                    passed=passed,
                    message=(
                        "Governance score is less than or equal to expected maximum."
                        if passed
                        else f"Expected score <= {maximum_score}, actual={actual_score}."
                    ),
                    details={
                        "expected_maximum": maximum_score,
                        "actual": actual_score,
                    },
                )
            )

        return assertions

    def _assert_finding_count(
        self,
        scenario: ScenarioDefinition,
        result: GovernanceRunResult,
    ) -> list[ScenarioAssertionResult]:
        expected_count = scenario.expected.finding_count

        if expected_count is None:
            return []

        actual_count = len(result.findings)
        passed = actual_count == expected_count

        return [
            ScenarioAssertionResult(
                name="finding_count",
                passed=passed,
                message=(
                    "Finding count matched expected value."
                    if passed
                    else f"Expected finding_count={expected_count}, actual={actual_count}."
                ),
                details={
                    "expected": expected_count,
                    "actual": actual_count,
                },
            )
        ]

    def _assert_action_count(
        self,
        scenario: ScenarioDefinition,
        result: GovernanceRunResult,
    ) -> list[ScenarioAssertionResult]:
        expected_count = scenario.expected.action_count

        if expected_count is None:
            return []

        actual_count = len(result.actions)
        passed = actual_count == expected_count

        return [
            ScenarioAssertionResult(
                name="action_count",
                passed=passed,
                message=(
                    "Action count matched expected value."
                    if passed
                    else f"Expected action_count={expected_count}, actual={actual_count}."
                ),
                details={
                    "expected": expected_count,
                    "actual": actual_count,
                },
            )
        ]

    def _assert_expected_findings(
        self,
        scenario: ScenarioDefinition,
        result: GovernanceRunResult,
    ) -> list[ScenarioAssertionResult]:
        assertions: list[ScenarioAssertionResult] = []

        for expected_finding in scenario.expected.findings:
            actual_finding = self._find_finding(result.findings, expected_finding.rule_id)

            if actual_finding is None:
                assertions.append(
                    ScenarioAssertionResult(
                        name=f"finding:{expected_finding.rule_id}",
                        passed=False,
                        message=f"Expected finding was not produced: {expected_finding.rule_id}.",
                        details={
                            "expected_rule_id": expected_finding.rule_id,
                        },
                    )
                )
                continue

            assertions.extend(
                self._assert_finding_properties(
                    expected_finding=expected_finding,
                    actual_finding=actual_finding,
                )
            )

        return assertions

    def _assert_finding_properties(
        self,
        expected_finding: ScenarioExpectedFinding,
        actual_finding: GovernanceFinding,
    ) -> list[ScenarioAssertionResult]:
        assertions: list[ScenarioAssertionResult] = []

        assertions.append(
            ScenarioAssertionResult(
                name=f"finding_exists:{expected_finding.rule_id}",
                passed=True,
                message=f"Expected finding was produced: {expected_finding.rule_id}.",
                details={
                    "rule_id": expected_finding.rule_id,
                },
            )
        )

        if expected_finding.status is not None:
            passed = actual_finding.status == expected_finding.status
            assertions.append(
                ScenarioAssertionResult(
                    name=f"finding_status:{expected_finding.rule_id}",
                    passed=passed,
                    message=(
                        "Finding status matched expected value."
                        if passed
                        else (
                            f"Expected status={expected_finding.status.value}, "
                            f"actual={actual_finding.status.value}."
                        )
                    ),
                    details={
                        "expected": expected_finding.status.value,
                        "actual": actual_finding.status.value,
                    },
                )
            )

        if expected_finding.severity is not None:
            passed = actual_finding.severity == expected_finding.severity
            assertions.append(
                ScenarioAssertionResult(
                    name=f"finding_severity:{expected_finding.rule_id}",
                    passed=passed,
                    message=(
                        "Finding severity matched expected value."
                        if passed
                        else (
                            f"Expected severity={expected_finding.severity.value}, "
                            f"actual={actual_finding.severity.value}."
                        )
                    ),
                    details={
                        "expected": expected_finding.severity.value,
                        "actual": actual_finding.severity.value,
                    },
                )
            )

        return assertions

    def _assert_expected_actions(
        self,
        scenario: ScenarioDefinition,
        result: GovernanceRunResult,
    ) -> list[ScenarioAssertionResult]:
        assertions: list[ScenarioAssertionResult] = []

        for expected_action in scenario.expected.actions:
            actual_action = self._find_action(result.actions, expected_action)

            if actual_action is None:
                assertions.append(
                    ScenarioAssertionResult(
                        name="action_expected",
                        passed=False,
                        message="Expected action was not generated.",
                        details=expected_action.model_dump(mode="json"),
                    )
                )
                continue

            assertions.extend(
                self._assert_action_properties(
                    expected_action=expected_action,
                    actual_action=actual_action,
                )
            )

        return assertions

    def _assert_action_properties(
        self,
        expected_action: ScenarioExpectedAction,
        actual_action: GovernanceAction,
    ) -> list[ScenarioAssertionResult]:
        assertions: list[ScenarioAssertionResult] = [
            ScenarioAssertionResult(
                name=f"action_exists:{actual_action.action_id}",
                passed=True,
                message=f"Expected action was generated: {actual_action.action_id}.",
                details={
                    "action_id": actual_action.action_id,
                    "rule_id": actual_action.rule_id,
                },
            )
        ]

        if expected_action.priority is not None:
            passed = actual_action.priority == expected_action.priority
            assertions.append(
                ScenarioAssertionResult(
                    name=f"action_priority:{actual_action.action_id}",
                    passed=passed,
                    message=(
                        "Action priority matched expected value."
                        if passed
                        else (
                            f"Expected priority={expected_action.priority.value}, "
                            f"actual={actual_action.priority.value}."
                        )
                    ),
                    details={
                        "expected": expected_action.priority.value,
                        "actual": actual_action.priority.value,
                    },
                )
            )

        if expected_action.action_type is not None:
            passed = actual_action.action_type == expected_action.action_type
            assertions.append(
                ScenarioAssertionResult(
                    name=f"action_type:{actual_action.action_id}",
                    passed=passed,
                    message=(
                        "Action type matched expected value."
                        if passed
                        else (
                            f"Expected action_type={expected_action.action_type.value}, "
                            f"actual={actual_action.action_type.value}."
                        )
                    ),
                    details={
                        "expected": expected_action.action_type.value,
                        "actual": actual_action.action_type.value,
                    },
                )
            )

        return assertions

    def _find_finding(
        self,
        findings: list[GovernanceFinding],
        rule_id: str,
    ) -> GovernanceFinding | None:
        for finding in findings:
            if finding.rule_id.upper() == rule_id.upper():
                return finding

        return None

    def _find_action(
        self,
        actions: list[GovernanceAction],
        expected_action: ScenarioExpectedAction,
    ) -> GovernanceAction | None:
        for action in actions:
            if expected_action.action_id is not None:
                if action.action_id.upper() != expected_action.action_id.upper():
                    continue

            if expected_action.rule_id is not None:
                if action.rule_id.upper() != expected_action.rule_id.upper():
                    continue

            return action

        return None