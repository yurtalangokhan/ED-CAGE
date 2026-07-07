import json
from datetime import UTC, datetime
from pathlib import Path

from ed_cage.adapters.filesystem.jsonl_evidence_registry import JsonlEvidenceRegistry
from ed_cage.application.gate import GovernanceGateEvaluator
from ed_cage.application.scoring import GovernanceScorer
from ed_cage.domain.enums import CheckStatus, Severity
from ed_cage.domain.models import (
    GovernanceFinding,
    GovernanceGatePolicy,
    GovernanceRunResult,
    NormalizedEvidence,
)


def test_jsonl_evidence_registry_writes_normalized_evidence_records(tmp_path: Path) -> None:
    result = _build_result()

    registry_path = tmp_path / "evidence" / "evidence-registry.jsonl"

    write_result = JsonlEvidenceRegistry(registry_path=registry_path).store(result)

    assert write_result.records_written == 1
    assert write_result.path == registry_path
    assert registry_path.exists()

    lines = registry_path.read_text(encoding="utf-8").splitlines()

    assert len(lines) == 1

    record = json.loads(lines[0])

    assert record["run_id"] == result.run_id
    assert record["project_name"] == "ed-cage"
    assert record["rule_id"] == "SVC-001"
    assert record["finding_status"] == "passed"
    assert record["severity"] == "high"
    assert record["source_type"] == "http"
    assert record["source_name"] == "mock-service"
    assert record["resource"] == "http://127.0.0.1:8080/health"
    assert record["observed_value"] == 200
    assert record["expected_value"] == [200, 204]
    assert record["compliant"] is True
    assert record["metadata"]["gate_passed"] is True
    assert record["metadata"]["governance_score"] == 100.0


def test_jsonl_evidence_registry_appends_records(tmp_path: Path) -> None:
    registry_path = tmp_path / "evidence" / "evidence-registry.jsonl"
    registry = JsonlEvidenceRegistry(registry_path=registry_path)

    first_result = _build_result()
    second_result = _build_result()

    registry.store(first_result)
    registry.store(second_result)

    lines = registry_path.read_text(encoding="utf-8").splitlines()

    assert len(lines) == 2

    first_record = json.loads(lines[0])
    second_record = json.loads(lines[1])

    assert first_record["run_id"] == first_result.run_id
    assert second_record["run_id"] == second_result.run_id
    assert first_record["run_id"] != second_record["run_id"]


def test_jsonl_evidence_registry_creates_empty_file_when_no_evidence_exists(
    tmp_path: Path,
) -> None:
    result = GovernanceRunResult(
        project_name="ed-cage",
        started_at=datetime.now(UTC),
        finished_at=datetime.now(UTC),
        findings=[],
        score=GovernanceScorer().calculate([]),
    )

    registry_path = tmp_path / "evidence" / "evidence-registry.jsonl"

    write_result = JsonlEvidenceRegistry(registry_path=registry_path).store(result)

    assert write_result.records_written == 0
    assert registry_path.exists()
    assert registry_path.read_text(encoding="utf-8") == ""


def _build_result() -> GovernanceRunResult:
    finding = GovernanceFinding(
        rule_id="SVC-001",
        title="Services must expose a health endpoint",
        severity=Severity.HIGH,
        status=CheckStatus.PASSED,
        message="All services expose at least one reachable health endpoint.",
        normalized_evidence=[
            NormalizedEvidence(
                rule_id="SVC-001",
                source_type="http",
                source_name="mock-service",
                resource="http://127.0.0.1:8080/health",
                observed_value=200,
                expected_value=[200, 204],
                compliant=True,
                message="Service has a reachable health endpoint.",
                raw_data={
                    "url": "http://127.0.0.1:8080/health",
                    "status_code": 200,
                    "success": True,
                },
                metadata={
                    "finding_status": "passed",
                    "base_url": "http://127.0.0.1:8080",
                },
            )
        ],
    )

    result = GovernanceRunResult(
        project_name="ed-cage",
        started_at=datetime.now(UTC),
        finished_at=datetime.now(UTC),
        findings=[finding],
        score=GovernanceScorer().calculate([finding]),
    )

    result.gate_result = GovernanceGateEvaluator().evaluate(
        result=result,
        policy=GovernanceGatePolicy(minimum_score=80),
    )

    return result