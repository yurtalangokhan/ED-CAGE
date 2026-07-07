from datetime import UTC, datetime
from pathlib import Path

from ed_cage.adapters.reporting.scenario_json_file_reporter import ScenarioJsonFileReporter
from ed_cage.domain.enums import CheckStatus, Severity
from ed_cage.domain.models import (
    GovernanceFinding,
    GovernanceRunResult,
    GovernanceScore,
    ScenarioAssertionResult,
    ScenarioRunResult,
)


def test_scenario_json_file_reporter_writes_report(tmp_path: Path) -> None:
    started_at = datetime(2026, 1, 1, 10, 0, 0, tzinfo=UTC)
    finished_at = datetime(2026, 1, 1, 10, 0, 1, tzinfo=UTC)

    scenario_result = ScenarioRunResult(
        scenario_id="SCN-001",
        scenario_name="Test scenario",
        governance_run_id="run-001",
        passed=True,
        assertions=[
            ScenarioAssertionResult(
                name="required finding",
                passed=True,
                message="Required finding exists.",
            )
        ],
    )

    governance_result = GovernanceRunResult(
        run_id="run-001",
        project_name="test-project",
        started_at=started_at,
        finished_at=finished_at,
        findings=[
            GovernanceFinding(
                rule_id="REPO-001",
                title="Repository must contain README",
                severity=Severity.MEDIUM,
                status=CheckStatus.PASSED,
                message="All required file(s) exist.",
                category="repository",
                target="repository",
                check_type="required_files",
            )
        ],
        score=GovernanceScore(
            score=100.0,
            achieved_score=3.0,
            max_score=3.0,
            total_findings=1,
            evaluated_findings=1,
            skipped_findings=0,
            status_summary={
                "passed": 1,
                "failed": 0,
                "skipped": 0,
                "error": 0,
            },
            severity_summary={
                "info": 0,
                "low": 0,
                "medium": 1,
                "high": 0,
                "critical": 0,
            },
        ),
    )

    report_file = ScenarioJsonFileReporter(
        output_path=tmp_path,
    ).report(
        scenario_result=scenario_result,
        governance_result=governance_result,
    )

    assert report_file.exists()

    report_content = report_file.read_text(encoding="utf-8")

    assert "SCN-001" in report_content
    assert "test-project" in report_content
    assert "REPO-001" in report_content
    assert '"scenario_passed": true' in report_content
    assert '"governance_gate_passed":' in report_content
    assert '"governance_score": 100.0' in report_content