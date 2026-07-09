from collections import Counter, defaultdict

from ed_cage.domain.enums import CheckStatus, Severity
from ed_cage.domain.models import (
    CategoryGovernanceScore,
    GovernanceFinding,
    GovernanceScore,
    ScoringConfig,
)


class GovernanceScorer:
    def __init__(self, scoring_config: ScoringConfig | None = None) -> None:
        self.scoring_config = scoring_config or ScoringConfig()

    def calculate(
        self,
        findings: list[GovernanceFinding],
        scoring_config: ScoringConfig | None = None,
    ) -> GovernanceScore:
        effective_scoring_config = scoring_config or self.scoring_config

        status_counts = Counter(finding.status.value for finding in findings)
        severity_counts = Counter(finding.severity.value for finding in findings)

        applicable_findings = [
            finding
            for finding in findings
            if finding.status != CheckStatus.SKIPPED
        ]
        skipped_findings = [
            finding
            for finding in findings
            if finding.status == CheckStatus.SKIPPED
        ]

        grouped_findings = self._group_findings_by_category(applicable_findings)

        category_scores: dict[str, float] = {}
        category_weights: dict[str, float] = {}
        category_details: list[CategoryGovernanceScore] = []

        weighted_score_sum = 0.0
        weight_sum = 0.0

        for category in sorted(grouped_findings):
            category_findings = grouped_findings[category]
            category_score = self._calculate_category_score(
                findings=category_findings,
                scoring_config=effective_scoring_config,
            )
            category_weight = self._get_category_weight(
                category=category,
                scoring_config=effective_scoring_config,
            )

            category_scores[category] = category_score
            category_weights[category] = category_weight

            weighted_score_sum += category_score * category_weight
            weight_sum += category_weight

            category_details.append(
                self._build_category_detail(
                    category=category,
                    score=category_score,
                    weight=category_weight,
                    findings=category_findings,
                )
            )

        if weight_sum == 0.0:
            score = 100.0
            achieved_score = 0.0
            max_score = 0.0
        else:
            score = round(weighted_score_sum / weight_sum, 2)
            achieved_score = round(weighted_score_sum, 2)
            max_score = round(weight_sum * 100.0, 2)

        return GovernanceScore(
            score=score,
            achieved_score=achieved_score,
            max_score=max_score,
            total_findings=len(findings),
            evaluated_findings=len(applicable_findings),
            skipped_findings=len(skipped_findings),
            status_summary={
                status.value: int(status_counts.get(status.value, 0))
                for status in CheckStatus
            },
            severity_summary={
                severity.value: int(severity_counts.get(severity.value, 0))
                for severity in Severity
            },
            maturity_band=self._resolve_maturity_band(
                score=score,
                scoring_config=effective_scoring_config,
            ),
            category_scores=category_scores,
            category_weights=category_weights,
            category_details=category_details,
            applicable_rule_count=len(applicable_findings),
            not_applicable_rule_count=len(skipped_findings),
            weighted_score_explanation={
                "formula": (
                    "sum(category_score * category_weight) "
                    "/ sum(category_weight)"
                ),
                "weighted_score_sum": round(weighted_score_sum, 2),
                "weight_sum": round(weight_sum, 2),
                "status_scores": effective_scoring_config.status_scores,
            },
        )

    def _group_findings_by_category(
        self,
        findings: list[GovernanceFinding],
    ) -> dict[str, list[GovernanceFinding]]:
        grouped_findings: dict[str, list[GovernanceFinding]] = defaultdict(list)

        for finding in findings:
            grouped_findings[self._normalize_category(finding.category)].append(
                finding
            )

        return dict(grouped_findings)

    def _calculate_category_score(
        self,
        findings: list[GovernanceFinding],
        scoring_config: ScoringConfig,
    ) -> float:
        if not findings:
            return 0.0

        achieved_score = sum(
            self._get_status_score(
                status=finding.status,
                scoring_config=scoring_config,
            )
            for finding in findings
        )

        return round((achieved_score / len(findings)) * 100.0, 2)

    def _get_status_score(
        self,
        status: CheckStatus,
        scoring_config: ScoringConfig,
    ) -> float:
        return scoring_config.status_scores.get(status.value, 0.0)

    def _get_category_weight(
        self,
        category: str,
        scoring_config: ScoringConfig,
    ) -> float:
        return scoring_config.category_weights.get(category, 1.0)

    def _resolve_maturity_band(
        self,
        score: float,
        scoring_config: ScoringConfig,
    ) -> str:
        for maturity_band in scoring_config.maturity_bands:
            if maturity_band.min_score <= score <= maturity_band.max_score:
                return maturity_band.name

        return "Unknown"

    def _build_category_detail(
        self,
        category: str,
        score: float,
        weight: float,
        findings: list[GovernanceFinding],
    ) -> CategoryGovernanceScore:
        status_counts = Counter(finding.status for finding in findings)

        return CategoryGovernanceScore(
            category=category,
            score=score,
            weight=weight,
            applicable_rule_count=len(findings),
            passed_rule_count=status_counts[CheckStatus.PASSED],
            warning_rule_count=0,
            failed_rule_count=status_counts[CheckStatus.FAILED],
            error_rule_count=status_counts[CheckStatus.ERROR],
            skipped_rule_count=status_counts[CheckStatus.SKIPPED],
        )

    def _normalize_category(self, category: str | None) -> str:
        if category is None:
            return "uncategorized"

        normalized_category = category.strip().lower()

        if not normalized_category:
            return "uncategorized"

        return normalized_category