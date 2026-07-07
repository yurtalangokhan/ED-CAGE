from ed_cage.domain.enums import ExecutionMode, Severity
from ed_cage.domain.models import GovernanceRule, RuleFilterCriteria


class GovernanceRuleFilter:
    RUNTIME_CHECK_TYPES: set[str] = {
        "http_health_endpoint",
        "openapi_spec",
        "openapi_document_policy",
        "metrics_endpoint",
        "prometheus_metrics_compatibility",
        "required_prometheus_metric_groups",
    }

    def apply(
        self,
        rules: list[GovernanceRule],
        criteria: RuleFilterCriteria | None,
    ) -> list[GovernanceRule]:
        if criteria is None:
            return rules

        return [rule for rule in rules if self._matches(rule, criteria)]

    def _matches(
        self,
        rule: GovernanceRule,
        criteria: RuleFilterCriteria,
    ) -> bool:
        if not self._matches_execution_mode(rule, criteria.execution_mode):
            return False

        if criteria.rule_ids:
            accepted_rule_ids = {
                self._normalize_rule_id(rule_id) for rule_id in criteria.rule_ids
            }

            if self._normalize_rule_id(rule.id) not in accepted_rule_ids:
                return False

        if criteria.categories:
            accepted_categories = {
                self._normalize_text(category) for category in criteria.categories
            }

            if self._normalize_text(rule.category) not in accepted_categories:
                return False

        if criteria.severities:
            accepted_severities = self._normalize_severities(criteria.severities)

            if rule.severity not in accepted_severities:
                return False

        if criteria.check_types:
            accepted_check_types = {
                self._normalize_text(check_type) for check_type in criteria.check_types
            }

            if self._normalize_text(rule.check_type) not in accepted_check_types:
                return False

        if criteria.targets:
            accepted_targets = {
                self._normalize_text(target) for target in criteria.targets
            }

            if self._normalize_text(rule.target) not in accepted_targets:
                return False

        return True

    def _matches_execution_mode(
        self,
        rule: GovernanceRule,
        execution_mode: ExecutionMode,
    ) -> bool:
        normalized_check_type = self._normalize_text(rule.check_type)
        is_runtime_check = normalized_check_type in self.RUNTIME_CHECK_TYPES

        if execution_mode == ExecutionMode.STATIC:
            return not is_runtime_check

        if execution_mode == ExecutionMode.RUNTIME:
            return is_runtime_check

        return True

    def _normalize_rule_id(self, value: str) -> str:
        return value.strip().upper()

    def _normalize_text(self, value: str) -> str:
        return value.strip().lower()

    def _normalize_severities(
        self,
        severities: list[Severity],
    ) -> set[Severity]:
        return set(severities)