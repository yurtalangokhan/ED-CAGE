from pathlib import Path

from ed_cage.adapters.reporting.evaluation_summary_reporter import (
    EvaluationSummaryReporter,
)


def test_evaluation_summary_reporter_writes_json_and_markdown(
    tmp_path: Path,
) -> None:
    aggregation_result = {
        "reports_root": "outputs/case-studies",
        "case_count": 1,
        "summary": {
            "case_count": 1,
            "static_case_count": 1,
            "runtime_case_count": 0,
            "average_governance_score": 55.0,
            "scenario_passed_count": 1,
            "governance_gate_passed_count": 0,
            "total_findings": 2,
            "total_actions": 1,
            "total_failed_or_error_findings": 1,
            "total_skipped_findings": 1,
        },
        "cases": [
            {
                "case_study": "online-boutique",
                "execution_mode": "static",
                "project_name": "online-boutique-static",
                "scenario_id": "CASE-ONLINE-BOUTIQUE-STATIC",
                "scenario_name": "Online Boutique static",
                "scenario_passed": True,
                "governance_gate_passed": False,
                "governance_score": 55.0,
                "finding_count": 2,
                "action_count": 1,
                "failed_or_error_findings": [
                    {
                        "rule_id": "DEP-001",
                        "category": "deployment",
                        "severity": "medium",
                        "status": "failed",
                        "message": "Manifest missing.",
                    }
                ],
                "skipped_findings": [
                    {
                        "rule_id": "DEP-002",
                        "category": "deployment",
                        "severity": "high",
                        "status": "skipped",
                        "message": "No containers.",
                    }
                ],
            }
        ],
        "category_summary": [
            {
                "category": "deployment",
                "status_counts": {
                    "failed": 1,
                    "skipped": 1,
                },
            }
        ],
        "rule_matrix": [
            {
                "rule_id": "DEP-001",
                "case_statuses": {
                    "online-boutique:static": "failed",
                },
            }
        ],
    }

    json_file, markdown_file = EvaluationSummaryReporter(
        output_path=tmp_path,
    ).report(aggregation_result)

    assert json_file.exists()
    assert markdown_file.exists()

    markdown = markdown_file.read_text(encoding="utf-8")

    assert "# ED-CAGE Evaluation Summary" in markdown
    assert "online-boutique" in markdown
    assert "DEP-001" in markdown