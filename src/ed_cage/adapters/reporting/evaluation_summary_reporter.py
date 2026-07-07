import json
from pathlib import Path
from typing import Any


class EvaluationSummaryReporter:
    def __init__(
        self,
        output_path: Path,
        json_filename: str = "evaluation-summary.json",
        markdown_filename: str = "evaluation-summary.md",
    ) -> None:
        self.output_path = output_path
        self.json_filename = json_filename
        self.markdown_filename = markdown_filename

    def report(self, aggregation_result: dict[str, Any]) -> tuple[Path, Path]:
        self.output_path.mkdir(parents=True, exist_ok=True)

        json_file = self.output_path / self.json_filename
        markdown_file = self.output_path / self.markdown_filename

        json_file.write_text(
            json.dumps(aggregation_result, ensure_ascii=False, indent=2),
            encoding="utf-8",
        )

        markdown_file.write_text(
            self._to_markdown(aggregation_result),
            encoding="utf-8",
        )

        return json_file, markdown_file

    def _to_markdown(self, aggregation_result: dict[str, Any]) -> str:
        summary = self._as_dict(aggregation_result.get("summary"))
        cases = self._as_list_of_dicts(aggregation_result.get("cases"))
        category_summary = self._as_list_of_dicts(
            aggregation_result.get("category_summary")
        )
        rule_matrix = self._as_list_of_dicts(aggregation_result.get("rule_matrix"))

        lines: list[str] = [
            "# ED-CAGE Evaluation Summary",
            "",
            "## Overall Summary",
            "",
            f"- Case count: {summary.get('case_count', 0)}",
            f"- Static case count: {summary.get('static_case_count', 0)}",
            f"- Runtime case count: {summary.get('runtime_case_count', 0)}",
            f"- Average governance score: {summary.get('average_governance_score')}",
            f"- Scenario passed count: {summary.get('scenario_passed_count', 0)}",
            f"- Governance gate passed count: {summary.get('governance_gate_passed_count', 0)}",
            f"- Total findings: {summary.get('total_findings', 0)}",
            f"- Total actions: {summary.get('total_actions', 0)}",
            f"- Failed/error findings: {summary.get('total_failed_or_error_findings', 0)}",
            f"- Skipped findings: {summary.get('total_skipped_findings', 0)}",
            "",
            "## Case Study Results",
            "",
            "| Case | Mode | Scenario | Scenario Passed | Gate Passed | Score | Findings | Actions | Failed/Error | Skipped |",
            "|---|---|---|---:|---:|---:|---:|---:|---:|---:|",
        ]

        for case_result in cases:
            failed_or_error_findings = self._as_list_of_dicts(
                case_result.get("failed_or_error_findings")
            )
            skipped_findings = self._as_list_of_dicts(
                case_result.get("skipped_findings")
            )

            lines.append(
                "| "
                f"{self._cell(case_result.get('case_study'))} | "
                f"{self._cell(case_result.get('execution_mode'))} | "
                f"{self._cell(case_result.get('scenario_id'))} | "
                f"{self._cell(case_result.get('scenario_passed'))} | "
                f"{self._cell(case_result.get('governance_gate_passed'))} | "
                f"{self._cell(case_result.get('governance_score'))} | "
                f"{self._cell(case_result.get('finding_count'))} | "
                f"{self._cell(case_result.get('action_count'))} | "
                f"{self._cell(len(failed_or_error_findings))} | "
                f"{self._cell(len(skipped_findings))} |"
            )

        lines.extend(
            [
                "",
                "## Category Summary",
                "",
                "| Category | Passed | Failed | Skipped | Error |",
                "|---|---:|---:|---:|---:|",
            ]
        )

        for category_result in category_summary:
            status_counts = self._as_dict(category_result.get("status_counts"))

            lines.append(
                "| "
                f"{self._cell(category_result.get('category'))} | "
                f"{self._cell(status_counts.get('passed', 0))} | "
                f"{self._cell(status_counts.get('failed', 0))} | "
                f"{self._cell(status_counts.get('skipped', 0))} | "
                f"{self._cell(status_counts.get('error', 0))} |"
            )

        lines.extend(
            [
                "",
                "## Failed or Error Findings by Case",
                "",
            ]
        )

        for case_result in cases:
            failed_or_error_findings = self._as_list_of_dicts(
                case_result.get("failed_or_error_findings")
            )

            lines.extend(
                [
                    f"### {self._cell(case_result.get('case_study'))} / {self._cell(case_result.get('execution_mode'))}",
                    "",
                ]
            )

            if not failed_or_error_findings:
                lines.extend(["No failed or error findings.", ""])
                continue

            lines.extend(
                [
                    "| Rule ID | Category | Severity | Status | Message |",
                    "|---|---|---|---|---|",
                ]
            )

            for finding in failed_or_error_findings:
                lines.append(
                    "| "
                    f"{self._cell(finding.get('rule_id'))} | "
                    f"{self._cell(finding.get('category'))} | "
                    f"{self._cell(finding.get('severity'))} | "
                    f"{self._cell(finding.get('status'))} | "
                    f"{self._cell(finding.get('message'))} |"
                )

            lines.append("")

        lines.extend(
            [
                "## Rule Matrix",
                "",
            ]
        )

        if rule_matrix:
            case_columns = [
                f"{case_result.get('case_study')}:{case_result.get('execution_mode')}"
                for case_result in cases
            ]

            lines.append(
                "| Rule ID | "
                + " | ".join(self._cell(case_column) for case_column in case_columns)
                + " |"
            )
            lines.append(
                "|---|"
                + "|".join("---" for _ in case_columns)
                + "|"
            )

            for rule_result in rule_matrix:
                case_statuses = self._as_dict(rule_result.get("case_statuses"))
                lines.append(
                    "| "
                    f"{self._cell(rule_result.get('rule_id'))} | "
                    + " | ".join(
                        self._cell(case_statuses.get(case_column, "-"))
                        for case_column in case_columns
                    )
                    + " |"
                )
        else:
            lines.append("No rule matrix data available.")

        lines.append("")

        return "\n".join(lines)

    def _cell(self, value: object) -> str:
        text = "" if value is None else str(value)

        return (
            text.replace("|", "\\|")
            .replace("\n", " ")
            .replace("\r", " ")
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