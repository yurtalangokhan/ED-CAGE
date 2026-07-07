import json
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any


class EvaluationAggregator:
    def aggregate(self, reports_root: Path) -> dict[str, Any]:
        report_files = self._find_report_files(reports_root)

        case_results = [
            self._load_case_result(report_file)
            for report_file in report_files
        ]

        return {
            "reports_root": str(reports_root),
            "case_count": len(case_results),
            "summary": self._build_summary(case_results),
            "cases": case_results,
            "category_summary": self._build_category_summary(case_results),
            "rule_matrix": self._build_rule_matrix(case_results),
        }

    def _find_report_files(self, reports_root: Path) -> list[Path]:
        all_reports = sorted(reports_root.rglob("scenario-report.json"))

        # Yeni output yapısında sadece static/runtime altındaki raporları alıyoruz.
        # Eski root-level scenario-report.json dosyaları aggregation'a karışmasın.
        filtered_reports = [
            report_file
            for report_file in all_reports
            if report_file.parent.name in {"static", "runtime"}
        ]

        if filtered_reports:
            return filtered_reports

        return all_reports

    def _load_case_result(self, report_file: Path) -> dict[str, Any]:
        raw_report = json.loads(report_file.read_text(encoding="utf-8"))

        top_summary = self._as_dict(raw_report.get("summary"))
        scenario_result = self._as_dict(raw_report.get("scenario_result"))
        governance_summary = self._as_dict(raw_report.get("governance_summary"))

        findings = self._as_list_of_dicts(governance_summary.get("findings"))
        actions = self._as_list_of_dicts(governance_summary.get("actions"))

        score = self._resolve_governance_score(
            top_summary=top_summary,
            governance_summary=governance_summary,
        )
        gate_passed = self._resolve_governance_gate_passed(
            top_summary=top_summary,
            governance_summary=governance_summary,
        )

        case_study, execution_mode = self._infer_case_and_mode(report_file)

        project_name = str(
            governance_summary.get("project_name")
            or f"{case_study}-{execution_mode}"
        )

        scenario_id = str(scenario_result.get("scenario_id", "unknown-scenario"))
        scenario_name = str(scenario_result.get("scenario_name", scenario_id))

        status_counts = self._count_by(findings, "status")
        severity_counts = self._count_by(findings, "severity")
        category_counts = self._count_by(findings, "category")

        failed_or_error_findings = [
            finding
            for finding in findings
            if finding.get("status") in {"failed", "error"}
        ]

        skipped_findings = [
            finding
            for finding in findings
            if finding.get("status") == "skipped"
        ]

        return {
            "case_study": case_study,
            "execution_mode": execution_mode,
            "project_name": project_name,
            "scenario_id": scenario_id,
            "scenario_name": scenario_name,
            "report_file": str(report_file),
            "scenario_passed": bool(top_summary.get("scenario_passed", False)),
            "governance_gate_passed": gate_passed,
            "governance_score": score,
            "finding_count": len(findings),
            "action_count": len(actions),
            "status_counts": status_counts,
            "severity_counts": severity_counts,
            "category_counts": category_counts,
            "failed_or_error_findings": [
                self._compact_finding(finding)
                for finding in failed_or_error_findings
            ],
            "skipped_findings": [
                self._compact_finding(finding)
                for finding in skipped_findings
            ],
            "actions": [
                self._compact_action(action)
                for action in actions
            ],
        }

    def _build_summary(self, case_results: list[dict[str, Any]]) -> dict[str, Any]:
        if not case_results:
            return {
                "case_count": 0,
                "static_case_count": 0,
                "runtime_case_count": 0,
                "average_governance_score": None,
                "scenario_passed_count": 0,
                "governance_gate_passed_count": 0,
                "total_findings": 0,
                "total_actions": 0,
                "total_failed_or_error_findings": 0,
                "total_skipped_findings": 0,
            }

        numeric_scores = [
            float(case_result["governance_score"])
            for case_result in case_results
            if self._is_number(case_result.get("governance_score"))
        ]

        average_score = (
            round(sum(numeric_scores) / len(numeric_scores), 2)
            if numeric_scores
            else None
        )

        return {
            "case_count": len(case_results),
            "static_case_count": sum(
                1 for case_result in case_results
                if case_result.get("execution_mode") == "static"
            ),
            "runtime_case_count": sum(
                1 for case_result in case_results
                if case_result.get("execution_mode") == "runtime"
            ),
            "average_governance_score": average_score,
            "scenario_passed_count": sum(
                1 for case_result in case_results
                if case_result["scenario_passed"]
            ),
            "governance_gate_passed_count": sum(
                1 for case_result in case_results
                if case_result["governance_gate_passed"] is True
            ),
            "total_findings": sum(
                int(case_result["finding_count"])
                for case_result in case_results
            ),
            "total_actions": sum(
                int(case_result["action_count"])
                for case_result in case_results
            ),
            "total_failed_or_error_findings": sum(
                len(case_result["failed_or_error_findings"])
                for case_result in case_results
            ),
            "total_skipped_findings": sum(
                len(case_result["skipped_findings"])
                for case_result in case_results
            ),
        }

    def _build_category_summary(
        self,
        case_results: list[dict[str, Any]],
    ) -> list[dict[str, Any]]:
        category_status_counts: dict[str, Counter[str]] = defaultdict(Counter)

        for case_result in case_results:
            report_file = Path(str(case_result["report_file"]))
            raw_report = json.loads(report_file.read_text(encoding="utf-8"))
            governance_summary = self._as_dict(raw_report.get("governance_summary"))
            findings = self._as_list_of_dicts(governance_summary.get("findings"))

            for finding in findings:
                category = str(finding.get("category") or "unknown")
                status = str(finding.get("status") or "unknown")
                category_status_counts[category][status] += 1

        return [
            {
                "category": category,
                "status_counts": dict(status_counts),
            }
            for category, status_counts in sorted(category_status_counts.items())
        ]

    def _build_rule_matrix(
        self,
        case_results: list[dict[str, Any]],
    ) -> list[dict[str, Any]]:
        rule_case_statuses: dict[str, dict[str, str]] = defaultdict(dict)

        for case_result in case_results:
            report_file = Path(str(case_result["report_file"]))
            raw_report = json.loads(report_file.read_text(encoding="utf-8"))
            governance_summary = self._as_dict(raw_report.get("governance_summary"))
            findings = self._as_list_of_dicts(governance_summary.get("findings"))

            case_column = (
                f"{case_result['case_study']}:{case_result['execution_mode']}"
            )

            for finding in findings:
                rule_id = str(finding.get("rule_id", "unknown-rule"))
                status = str(finding.get("status", "unknown"))
                rule_case_statuses[rule_id][case_column] = status

        return [
            {
                "rule_id": rule_id,
                "case_statuses": case_statuses,
            }
            for rule_id, case_statuses in sorted(rule_case_statuses.items())
        ]

    def _resolve_governance_score(
        self,
        top_summary: dict[str, Any],
        governance_summary: dict[str, Any],
    ) -> float | None:
        summary_score = self._to_float_or_none(top_summary.get("governance_score"))

        if summary_score is not None:
            return summary_score

        score = self._as_dict(governance_summary.get("score"))

        return self._to_float_or_none(score.get("score"))

    def _resolve_governance_gate_passed(
        self,
        top_summary: dict[str, Any],
        governance_summary: dict[str, Any],
    ) -> bool | None:
        if isinstance(top_summary.get("governance_gate_passed"), bool):
            return bool(top_summary["governance_gate_passed"])

        gate_result = self._as_dict(governance_summary.get("gate_result"))

        if isinstance(gate_result.get("passed"), bool):
            return bool(gate_result["passed"])

        return None

    def _infer_case_and_mode(self, report_file: Path) -> tuple[str, str]:
        execution_mode = report_file.parent.name

        if execution_mode in {"static", "runtime"}:
            case_study = report_file.parent.parent.name
            return case_study, execution_mode

        return report_file.parent.name, "unknown"

    def _compact_finding(self, finding: dict[str, Any]) -> dict[str, Any]:
        return {
            "rule_id": finding.get("rule_id"),
            "title": finding.get("title"),
            "category": finding.get("category"),
            "severity": finding.get("severity"),
            "status": finding.get("status"),
            "message": finding.get("message"),
        }

    def _compact_action(self, action: dict[str, Any]) -> dict[str, Any]:
        return {
            "action_id": action.get("action_id"),
            "rule_id": action.get("rule_id"),
            "priority": action.get("priority"),
            "action_type": action.get("action_type"),
            "title": action.get("title"),
        }

    def _count_by(
        self,
        items: list[dict[str, Any]],
        key: str,
    ) -> dict[str, int]:
        return dict(
            Counter(
                str(item.get(key) or "unknown")
                for item in items
            )
        )

    def _as_dict(self, value: object) -> dict[str, Any]:
        if isinstance(value, dict):
            return value

        return {}

    def _as_list_of_dicts(self, value: object) -> list[dict[str, Any]]:
        if not isinstance(value, list):
            return []

        return [
            item
            for item in value
            if isinstance(item, dict)
        ]

    def _is_number(self, value: object) -> bool:
        return isinstance(value, (int, float)) and not isinstance(value, bool)
    
    def _to_float_or_none(self, value: object) -> float | None:
        if isinstance(value, bool):
            return None

        if isinstance(value, (int, float)):
            return float(value)

        return None