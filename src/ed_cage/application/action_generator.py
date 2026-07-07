from ed_cage.domain.enums import (
    ActionPriority,
    CheckStatus,
    GovernanceActionType,
    Severity,
)
from ed_cage.domain.models import (
    GovernanceAction,
    GovernanceActionDefinition,
    GovernanceFinding,
    GovernanceRunResult,
)


class GovernanceActionGenerator:
    def generate(
        self,
        result: GovernanceRunResult,
        action_definitions: list[GovernanceActionDefinition],
    ) -> list[GovernanceAction]:
        actions: list[GovernanceAction] = []

        for finding in result.findings:
            if finding.status not in {CheckStatus.FAILED, CheckStatus.ERROR}:
                continue

            matching_definitions = [
                definition
                for definition in action_definitions
                if self._matches(definition, finding)
            ]

            if not matching_definitions:
                actions.append(self._build_default_action(finding))
                continue

            for definition in matching_definitions:
                actions.append(
                    self._build_action_from_definition(
                        finding=finding,
                        definition=definition,
                    )
                )

        return actions

    def _matches(
        self,
        definition: GovernanceActionDefinition,
        finding: GovernanceFinding,
    ) -> bool:
        if definition.rule_id is not None and definition.rule_id.upper() != finding.rule_id.upper():
            return False

        if definition.category is not None:
            if finding.category is None or definition.category.lower() != finding.category.lower():
                return False

        if definition.target is not None:
            if finding.target is None or definition.target.lower() != finding.target.lower():
                return False

        if definition.check_type is not None:
            if finding.check_type is None or definition.check_type.lower() != finding.check_type.lower():
                return False

        if definition.status is not None and definition.status != finding.status:
            return False

        if definition.severity is not None and definition.severity != finding.severity:
            return False

        return True

    def _build_action_from_definition(
        self,
        finding: GovernanceFinding,
        definition: GovernanceActionDefinition,
    ) -> GovernanceAction:
        return GovernanceAction(
            action_id=f"{definition.id}:{finding.rule_id}",
            rule_id=finding.rule_id,
            finding_status=finding.status,
            severity=finding.severity,
            title=definition.title,
            action_type=definition.action_type,
            priority=definition.priority,
            recommendation=definition.recommendation,
            implementation_hint=definition.implementation_hint,
            category=finding.category,
            target=finding.target,
            check_type=finding.check_type,
            references=definition.references,
            tags=definition.tags,
            metadata={
                **definition.metadata,
                "finding_message": finding.message,
                "source_action_definition": definition.id,
            },
        )

    def _build_default_action(
        self,
        finding: GovernanceFinding,
    ) -> GovernanceAction:
        if finding.status == CheckStatus.ERROR:
            return GovernanceAction(
                action_id=f"DEFAULT-ERROR:{finding.rule_id}",
                rule_id=finding.rule_id,
                finding_status=finding.status,
                severity=finding.severity,
                title="Investigate governance check error",
                action_type=GovernanceActionType.INVESTIGATION,
                priority=self._priority_from_severity(finding.severity),
                recommendation=(
                    "Investigate the governance check execution error and fix the "
                    "underlying configuration, dependency or implementation problem."
                ),
                implementation_hint=(
                    "Review the finding message, raw evidence, normalized evidence "
                    "and related check implementation."
                ),
                category=finding.category,
                target=finding.target,
                check_type=finding.check_type,
                tags=["default-action", "error"],
                metadata={
                    "finding_message": finding.message,
                    "generated_by": "default_action_generator",
                },
            )

        return GovernanceAction(
            action_id=f"DEFAULT-FAILED:{finding.rule_id}",
            rule_id=finding.rule_id,
            finding_status=finding.status,
            severity=finding.severity,
            title="Remediate governance rule violation",
            action_type=GovernanceActionType.REMEDIATION,
            priority=self._priority_from_severity(finding.severity),
            recommendation=(
                "Review the failed governance rule and remediate the architecture "
                "or configuration issue reported by ED-CAGE."
            ),
            implementation_hint=(
                "Use the finding message and normalized evidence to identify the "
                "non-compliant resource and expected value."
            ),
            category=finding.category,
            target=finding.target,
            check_type=finding.check_type,
            tags=["default-action", "remediation"],
            metadata={
                "finding_message": finding.message,
                "generated_by": "default_action_generator",
            },
        )

    def _priority_from_severity(self, severity: Severity) -> ActionPriority:
        match severity:
            case Severity.CRITICAL:
                return ActionPriority.CRITICAL
            case Severity.HIGH:
                return ActionPriority.HIGH
            case Severity.MEDIUM:
                return ActionPriority.MEDIUM
            case Severity.LOW | Severity.INFO:
                return ActionPriority.LOW

        return ActionPriority.MEDIUM