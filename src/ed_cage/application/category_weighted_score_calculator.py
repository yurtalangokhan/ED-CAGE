from __future__ import annotations

from collections import Counter, defaultdict
from dataclasses import dataclass

from ed_cage.domain.enums import CheckStatus
from ed_cage.domain.models import (
    CategoryGovernanceScore,
    GovernanceFinding,
    GovernanceScore,
    ScoringConfig,
)


@dataclass(frozen=True)
class _CategoryAccumulator:
    category: str
    findings: list[GovernanceFinding]


class CategoryWeightedScoreCalculator:
    def calculate(
        self,
        findings: list[GovernanceFinding],
        scoring_config: ScoringConfig,
    ) -> GovernanceScore:
        status_summary = self._count_statuses(findings)
        severity_summary = self._count_severities(findings)

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

        category_accumulators = self._group_by_category(applicable_findings)

        category_details: list[CategoryGovernanceScore] = []
        category_scores: dict[str, float] = {}
        category_weights: dict[str, float] = {}

        weighted_score_sum = 0.0
        weight_sum = 0.0

        for category, accumulator in sorted(category_accumulators.items()):
            category_score = self._calculate_category_score(
                findings=accumulator.findings,
                scoring_config=scoring_config,
            )
            category_weight = self._get_category_weight(
                category=category,
                scoring_config=scoring_config,
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
                    findings=accumulator.findings,
                )
            )

        overall_score = 0.0

        if weight_sum > 0:
            overall_score = weighted_score_sum / weight_sum

        overall_score = round(overall_score, 2)
        achieved_score = round(weighted_score_sum, 2)
        max_score = round(weight_sum * 100.0, 2)

        return GovernanceScore(
            score=overall_score,
            achieved_score=achieved_score,
            max_score=max_score,
            total_findings=len(findings),
            evaluated_findings=len(applicable_findings),
            skipped_findings=len(skipped_findings),
            status_summary=status_summary,
            severity_summary=severity_summary,
            maturity_band=self._resolve_maturity_band(
                score=overall_score,
                scoring_config=scoring_config,
            ),
            category_scores=category_scores,
            category_weights=category_weights,
            category_details=category_details,
            applicable_rule_count=len(applicable_findings),
            not_applicable_rule_count=len(skipped_findings),
            weighted_score_explanation={
                "formula": "sum(category_score * category_weight) / sum(category_weight)",
                "weighted_score_sum": round(weighted_score_sum, 2),
                "weight_sum": round(weight_sum, 2),
                "status_scores": scoring_config.status_scores,
            },
        )

    def _calculate_category_score(
        self,
        findings: list[GovernanceFinding],
        scoring_config: ScoringConfig,
    ) -> float:
        if not findings:
            return 0.0

        achieved_score = 0.0

        for finding in findings:
            achieved_score += self._get_status_score(
                status=finding.status,
                scoring_config=scoring_config,
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

    def _group_by_category(
        self,
        findings: list[GovernanceFinding],
    ) -> dict[str, _CategoryAccumulator]:
        grouped_findings: dict[str, list[GovernanceFinding]] = defaultdict(list)

        for finding in findings:
            category = self._normalize_category(finding.category)
            grouped_findings[category].append(finding)

        return {
            category: _CategoryAccumulator(
                category=category,
                findings=category_findings,
            )
            for category, category_findings in grouped_findings.items()
        }

    def _normalize_category(self, category: str | None) -> str:
        if category is None:
            return "uncategorized"

        normalized_category = category.strip().lower()

        if not normalized_category:
            return "uncategorized"

        return normalized_category

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

    def _count_statuses(
        self,
        findings: list[GovernanceFinding],
    ) -> dict[str, int]:
        counter = Counter(finding.status.value for finding in findings)
        return dict(sorted(counter.items()))

    def _count_severities(
        self,
        findings: list[GovernanceFinding],
    ) -> dict[str, int]:
        counter = Counter(finding.severity.value for finding in findings)
        return dict(sorted(counter.items()))