import json
from collections import Counter
from pathlib import Path

from ed_cage.domain.enums import CheckStatus, Severity
from ed_cage.domain.models import GovernanceFinding, GovernanceRunResult
from ed_cage.adapters.reporting.json_safety import to_json_safe

class MarkdownFileReporter:
    def __init__(
        self,
        output_path: Path,
        filename: str = "governance-report.md",
    ) -> None:
        self.output_path = output_path
        self.filename = filename

    def report(self, result: GovernanceRunResult) -> None:
        self.output_path.mkdir(parents=True, exist_ok=True)

        report_file = self.output_path / self.filename

        lines = self._build_markdown(result)

        report_file.write_text(
            "\n".join(lines),
            encoding="utf-8",
        )

    def _build_markdown(self, result: GovernanceRunResult) -> list[str]:
        status_counts = Counter(finding.status.value for finding in result.findings)
        severity_counts = Counter(finding.severity.value for finding in result.findings)

        lines: list[str] = []

        lines.append("# ED-CAGE Governance Report")
        lines.append("")
        lines.append("## Run Information")
        lines.append("")
        lines.append(f"- Run ID: `{result.run_id}`")
        lines.append(f"- Project: **{result.project_name}**")
        lines.append(f"- Started at: `{result.started_at.isoformat()}`")
        lines.append(f"- Finished at: `{result.finished_at.isoformat()}`")
        lines.append(f"- Overall result: **{self._overall_result(result)}**")

        if result.score is not None:
            lines.append(f"- Governance score: **{result.score.score:.2f} / 100**")
            lines.append(f"- Achieved score: `{result.score.achieved_score}`")
            lines.append(f"- Max score: `{result.score.max_score}`")
            lines.append(f"- Evaluated findings: `{result.score.evaluated_findings}`")
            lines.append(f"- Skipped findings: `{result.score.skipped_findings}`")

        lines.append("")

        self._append_gate_section(lines, result)
        self._append_actions_section(lines, result)

        lines.append("## Status Summary")
        lines.append("")
        lines.append("| Status | Count |")
        lines.append("|---|---:|")

        for status in CheckStatus:
            if result.score is not None:
                count = result.score.status_summary.get(status.value, 0)
            else:
                count = status_counts.get(status.value, 0)

            lines.append(f"| {status.value} | {count} |")

        lines.append("")
        lines.append("## Severity Summary")
        lines.append("")
        lines.append("| Severity | Count |")
        lines.append("|---|---:|")

        for severity in Severity:
            if result.score is not None:
                count = result.score.severity_summary.get(severity.value, 0)
            else:
                count = severity_counts.get(severity.value, 0)

            lines.append(f"| {severity.value} | {count} |")

        lines.append("")
        lines.append("## Findings")
        lines.append("")
        lines.append("| Rule ID | Severity | Status | Message |")
        lines.append("|---|---|---|---|")

        for finding in result.findings:
            lines.append(
                "| "
                f"{self._escape_table_cell(finding.rule_id)} | "
                f"{self._escape_table_cell(finding.severity.value)} | "
                f"{self._escape_table_cell(finding.status.value)} | "
                f"{self._escape_table_cell(finding.message)} |"
            )

        lines.append("")
        lines.append("## Evidence Details")
        lines.append("")

        if not result.findings:
            lines.append("No findings were produced.")
            lines.append("")
            return lines

        for finding in result.findings:
            lines.append(f"### {finding.rule_id} — {finding.title}")
            lines.append("")
            lines.append(f"- Severity: `{finding.severity.value}`")
            lines.append(f"- Status: `{finding.status.value}`")
            lines.append(f"- Category: `{finding.category}`")
            lines.append(f"- Target: `{finding.target}`")
            lines.append(f"- Check type: `{finding.check_type}`")
            lines.append(f"- Message: {finding.message}")
            lines.append("")

            self._append_raw_evidence(lines, finding)
            self._append_normalized_evidence(lines, finding)

        return lines

    def _append_actions_section(
        self,
        lines: list[str],
        result: GovernanceRunResult,
    ) -> None:
        lines.append("## Recommended Actions")
        lines.append("")

        if not result.actions:
            lines.append("No governance actions were generated.")
            lines.append("")
            return

        lines.append("| Rule ID | Priority | Type | Action | Recommendation |")
        lines.append("|---|---|---|---|---|")

        for action in result.actions:
            lines.append(
                "| "
                f"{self._escape_table_cell(action.rule_id)} | "
                f"{self._escape_table_cell(action.priority.value)} | "
                f"{self._escape_table_cell(action.action_type.value)} | "
                f"{self._escape_table_cell(action.title)} | "
                f"{self._escape_table_cell(action.recommendation)} |"
            )

        lines.append("")

        for action in result.actions:
            lines.append(f"### {action.action_id}")
            lines.append("")
            lines.append(f"- Rule ID: `{action.rule_id}`")
            lines.append(f"- Finding status: `{action.finding_status.value}`")
            lines.append(f"- Severity: `{action.severity.value}`")
            lines.append(f"- Priority: `{action.priority.value}`")
            lines.append(f"- Action type: `{action.action_type.value}`")
            lines.append(f"- Recommendation: {action.recommendation}")

            if action.implementation_hint:
                lines.append(f"- Implementation hint: {action.implementation_hint}")

            if action.tags:
                lines.append(f"- Tags: `{', '.join(action.tags)}`")

            lines.append("")

    def _append_raw_evidence(
        self,
        lines: list[str],
        finding: GovernanceFinding,
    ) -> None:
        lines.append("#### Raw Evidence")
        lines.append("")

        if not finding.evidence:
            lines.append("No raw evidence was collected for this finding.")
            lines.append("")
            return

        for index, evidence in enumerate(finding.evidence, start=1):
            lines.append(f"##### Raw Evidence {index}")
            lines.append("")
            lines.append(f"- Source: `{evidence.source}`")
            lines.append(f"- Message: {evidence.message}")
            lines.append("")
            lines.append("```json")
            lines.append(json.dumps(to_json_safe(evidence.data), ensure_ascii=False, indent=2))
            lines.append("```")
            lines.append("")

    def _append_normalized_evidence(
        self,
        lines: list[str],
        finding: GovernanceFinding,
    ) -> None:
        lines.append("#### Normalized Evidence")
        lines.append("")

        if not finding.normalized_evidence:
            lines.append("No normalized evidence was produced for this finding.")
            lines.append("")
            return

        lines.append("| Source Type | Source Name | Resource | Compliant | Observed | Expected |")
        lines.append("|---|---|---|---|---|---|")

        for evidence in finding.normalized_evidence:
            lines.append(
                "| "
                f"{self._escape_table_cell(evidence.source_type)} | "
                f"{self._escape_table_cell(evidence.source_name)} | "
                f"{self._escape_table_cell(evidence.resource)} | "
                f"{self._escape_table_cell(evidence.compliant)} | "
                f"{self._escape_table_cell(evidence.observed_value)} | "
                f"{self._escape_table_cell(evidence.expected_value)} |"
            )

        lines.append("")

    def _append_gate_section(
        self,
        lines: list[str],
        result: GovernanceRunResult,
    ) -> None:
        lines.append("## Governance Gate")
        lines.append("")

        if result.gate_result is None:
            lines.append("Governance gate was not evaluated.")
            lines.append("")
            return

        gate_result = result.gate_result

        gate_text = "PASSED" if gate_result.passed else "FAILED"

        lines.append(f"- Gate result: **{gate_text}**")
        lines.append(f"- Actual score: `{gate_result.actual_score:.2f}`")
        lines.append(f"- Minimum score: `{gate_result.minimum_score:.2f}`")

        if gate_result.blocking_findings:
            lines.append(f"- Blocking findings: `{', '.join(gate_result.blocking_findings)}`")

        lines.append("")

        if not gate_result.reasons:
            lines.append("No gate violation was detected.")
            lines.append("")
            return

        lines.append("### Gate Reason(s)")
        lines.append("")

        for reason in gate_result.reasons:
            lines.append(f"- {reason}")

        lines.append("")

    def _overall_result(self, result: GovernanceRunResult) -> str:
        if result.gate_result is not None:
            return "PASSED" if result.gate_result.passed else "FAILED"

        return "FAILED" if result.has_failures else "PASSED"

    def _escape_table_cell(self, value: object) -> str:
        return str(value).replace("|", "\\|").replace("\n", "<br>")