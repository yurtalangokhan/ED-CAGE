import json
from datetime import UTC, datetime
from pathlib import Path

from ed_cage.adapters.reporting.json_file_reporter import JsonFileReporter
from ed_cage.domain.enums import CheckStatus, Severity
from ed_cage.domain.models import GovernanceFinding, GovernanceRunResult


def test_json_file_reporter_writes_governance_report(tmp_path: Path) -> None:
    result = GovernanceRunResult(
        project_name="ed-cage",
        started_at=datetime.now(UTC),
        finished_at=datetime.now(UTC),
        findings=[
            GovernanceFinding(
                rule_id="TEST-001",
                title="Test rule",
                severity=Severity.MEDIUM,
                status=CheckStatus.PASSED,
                message="Test passed.",
            )
        ],
    )

    reporter = JsonFileReporter(
        output_path=tmp_path,
        filename="test-report.json",
    )

    reporter.report(result)

    report_file = tmp_path / "test-report.json"

    assert report_file.exists()

    report_data = json.loads(report_file.read_text(encoding="utf-8"))

    assert report_data["project_name"] == "ed-cage"
    assert len(report_data["findings"]) == 1
    assert report_data["findings"][0]["rule_id"] == "TEST-001"
    assert report_data["findings"][0]["status"] == "passed"