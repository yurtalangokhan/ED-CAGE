import json
from pathlib import Path

from ed_cage.application.evaluation_aggregator import EvaluationAggregator


def test_evaluation_aggregator_aggregates_static_and_runtime_reports(
    tmp_path: Path,
) -> None:
    _write_scenario_report(
        report_file=tmp_path
        / "outputs"
        / "case-studies"
        / "online-boutique"
        / "static"
        / "scenario-report.json",
        project_name="online-boutique-static",
        scenario_id="CASE-ONLINE-BOUTIQUE-STATIC",
        scenario_passed=True,
        gate_passed=False,
        score=55.0,
        findings=[
            {
                "rule_id": "DEP-001",
                "title": "Kubernetes manifests must exist",
                "severity": "medium",
                "status": "failed",
                "category": "deployment",
                "target": "kubernetes",
                "check_type": "kubernetes_manifests_exist",
                "message": "Manifest missing.",
            },
            {
                "rule_id": "DEP-002",
                "title": "Container image must not use latest tag",
                "severity": "high",
                "status": "skipped",
                "category": "deployment",
                "target": "kubernetes",
                "check_type": "kubernetes_image_policy",
                "message": "No containers.",
            },
        ],
    )

    _write_scenario_report(
        report_file=tmp_path
        / "outputs"
        / "case-studies"
        / "online-boutique"
        / "runtime"
        / "scenario-report.json",
        project_name="online-boutique-runtime",
        scenario_id="CASE-ONLINE-BOUTIQUE-RUNTIME",
        scenario_passed=True,
        gate_passed=True,
        score=95.0,
        findings=[
            {
                "rule_id": "SVC-001",
                "title": "Services must expose a health endpoint",
                "severity": "high",
                "status": "passed",
                "category": "service",
                "target": "service",
                "check_type": "http_health_endpoint",
                "message": "Health endpoint reachable.",
            }
        ],
    )

    result = EvaluationAggregator().aggregate(
        reports_root=tmp_path / "outputs" / "case-studies",
    )

    assert result["case_count"] == 2
    assert result["summary"]["static_case_count"] == 1
    assert result["summary"]["runtime_case_count"] == 1
    assert result["summary"]["average_governance_score"] == 75.0
    assert result["summary"]["scenario_passed_count"] == 2
    assert result["summary"]["governance_gate_passed_count"] == 1
    assert result["summary"]["total_findings"] == 3
    assert result["summary"]["total_failed_or_error_findings"] == 1
    assert result["summary"]["total_skipped_findings"] == 1

    rule_matrix = {
        item["rule_id"]: item["case_statuses"]
        for item in result["rule_matrix"]
    }

    assert rule_matrix["DEP-001"]["online-boutique:static"] == "failed"
    assert rule_matrix["SVC-001"]["online-boutique:runtime"] == "passed"


def _write_scenario_report(
    report_file: Path,
    project_name: str,
    scenario_id: str,
    scenario_passed: bool,
    gate_passed: bool,
    score: float,
    findings: list[dict[str, object]],
) -> None:
    report_file.parent.mkdir(parents=True, exist_ok=True)

    report = {
        "summary": {
            "scenario_passed": scenario_passed,
            "governance_gate_passed": gate_passed,
            "governance_score": score,
            "finding_count": len(findings),
            "action_count": 0,
        },
        "scenario_result": {
            "scenario_id": scenario_id,
            "scenario_name": scenario_id,
            "governance_run_id": "run-001",
            "passed": scenario_passed,
            "assertions": [],
        },
        "governance_summary": {
            "run_id": "run-001",
            "project_name": project_name,
            "score": {
                "score": score,
            },
            "gate_result": {
                "passed": gate_passed,
            },
            "finding_count": len(findings),
            "action_count": 0,
            "findings": findings,
            "actions": [],
        },
    }

    report_file.write_text(
        json.dumps(report, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )