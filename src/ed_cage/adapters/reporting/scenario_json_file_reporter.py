import json
from pathlib import Path
from typing import Any

from ed_cage.domain.models import GovernanceRunResult, ScenarioRunResult


class ScenarioJsonFileReporter:
    def __init__(
        self,
        output_path: Path,
        filename: str = "scenario-report.json",
    ) -> None:
        self.output_path = output_path
        self.filename = filename

    def report(
        self,
        scenario_result: ScenarioRunResult,
        governance_result: GovernanceRunResult,
    ) -> Path:
        self.output_path.mkdir(parents=True, exist_ok=True)

        report_file = self.output_path / self.filename
        report_data = self._build_report_data(
            scenario_result=scenario_result,
            governance_result=governance_result,
        )

        report_file.write_text(
            json.dumps(report_data, ensure_ascii=False, indent=2),
            encoding="utf-8",
        )

        return report_file

    def _build_report_data(
        self,
        scenario_result: ScenarioRunResult,
        governance_result: GovernanceRunResult,
    ) -> dict[str, Any]:
        return {
            "summary": {
                "scenario_passed": scenario_result.passed,
                "governance_gate_passed": (
                    governance_result.gate_result.passed
                    if governance_result.gate_result is not None
                    else None
                ),
                "governance_score": (
                    governance_result.score.score
                    if governance_result.score is not None
                    else None
                ),
                "finding_count": len(governance_result.findings),
                "action_count": len(governance_result.actions),
            },
            "scenario_result": scenario_result.model_dump(mode="json"),
            "governance_summary": {
                "run_id": governance_result.run_id,
                "project_name": governance_result.project_name,
                "score": (
                    governance_result.score.model_dump(mode="json")
                    if governance_result.score is not None
                    else None
                ),
                "gate_result": (
                    governance_result.gate_result.model_dump(mode="json")
                    if governance_result.gate_result is not None
                    else None
                ),
                "finding_count": len(governance_result.findings),
                "action_count": len(governance_result.actions),
                "findings": [
                    {
                        "rule_id": finding.rule_id,
                        "title": finding.title,
                        "severity": finding.severity.value,
                        "status": finding.status.value,
                        "category": finding.category,
                        "target": finding.target,
                        "check_type": finding.check_type,
                        "message": finding.message,
                    }
                    for finding in governance_result.findings
                ],
                "actions": [
                    {
                        "action_id": action.action_id,
                        "rule_id": action.rule_id,
                        "priority": action.priority.value,
                        "action_type": action.action_type.value,
                        "title": action.title,
                        "recommendation": action.recommendation,
                    }
                    for action in governance_result.actions
                ],
            },
        }