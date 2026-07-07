from datetime import UTC, datetime
from pathlib import Path

from ed_cage.adapters.reporting.markdown_file_reporter import MarkdownFileReporter
from ed_cage.domain.enums import CheckStatus, Severity
from ed_cage.domain.models import Evidence, GovernanceFinding, GovernanceRunResult


def test_markdown_file_reporter_writes_governance_report(tmp_path: Path) -> None:
    result = GovernanceRunResult(
        project_name="ed-cage",
        started_at=datetime.now(UTC),
        finished_at=datetime.now(UTC),
        findings=[
            GovernanceFinding(
                rule_id="TEST-001",
                title="Test rule",
                severity=Severity.HIGH,
                status=CheckStatus.FAILED,
                message="Test failed.",
                evidence=[
                    Evidence(
                        source="test-source",
                        message="Test evidence message.",
                        data={
                            "expected": "valid architecture rule",
                            "actual": "invalid implementation",
                        },
                    )
                ],
            )
        ],
    )

    reporter = MarkdownFileReporter(
        output_path=tmp_path,
        filename="test-report.md",
    )

    reporter.report(result)

    report_file = tmp_path / "test-report.md"

    assert report_file.exists()

    report_content = report_file.read_text(encoding="utf-8")

    assert "# ED-CAGE Governance Report" in report_content
    assert "## Run Information" in report_content
    assert "## Status Summary" in report_content
    assert "## Severity Summary" in report_content
    assert "## Findings" in report_content
    assert "## Evidence Details" in report_content
    assert "TEST-001" in report_content
    assert "failed" in report_content
    assert "Test evidence message." in report_content