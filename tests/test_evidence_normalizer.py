from ed_cage.application.evidence_normalizer import EvidenceNormalizer
from ed_cage.domain.enums import CheckStatus, Severity
from ed_cage.domain.models import Evidence, GovernanceFinding


def test_evidence_normalizer_normalizes_http_evidence() -> None:
    finding = GovernanceFinding(
        rule_id="SVC-001",
        title="Services must expose a health endpoint",
        severity=Severity.HIGH,
        status=CheckStatus.PASSED,
        message="All services expose at least one reachable health endpoint.",
        evidence=[
            Evidence(
                source="mock-service",
                message="Service has a reachable health endpoint.",
                data={
                    "service": "mock-service",
                    "base_url": "http://127.0.0.1:8080",
                    "candidate_paths": ["/health"],
                    "expected_status_codes": [200, 204],
                    "attempts": [
                        {
                            "url": "http://127.0.0.1:8080/health",
                            "status_code": 200,
                            "success": True,
                        }
                    ],
                },
            )
        ],
    )

    normalized_finding = EvidenceNormalizer().normalize_finding(finding)

    assert len(normalized_finding.normalized_evidence) == 1

    normalized = normalized_finding.normalized_evidence[0]

    assert normalized.rule_id == "SVC-001"
    assert normalized.source_type == "http"
    assert normalized.source_name == "mock-service"
    assert normalized.resource == "http://127.0.0.1:8080/health"
    assert normalized.observed_value == 200
    assert normalized.expected_value == [200, 204]
    assert normalized.compliant is True


def test_evidence_normalizer_normalizes_filesystem_evidence() -> None:
    finding = GovernanceFinding(
        rule_id="REPO-001",
        title="Repository must contain README",
        severity=Severity.MEDIUM,
        status=CheckStatus.FAILED,
        message="Missing required file(s): README.md",
        evidence=[
            Evidence(
                source="repository",
                message="Required repository files check failed.",
                data={
                    "missing_files": ["README.md"],
                    "existing_files": [],
                },
            )
        ],
    )

    normalized_finding = EvidenceNormalizer().normalize_finding(finding)

    assert len(normalized_finding.normalized_evidence) == 1

    normalized = normalized_finding.normalized_evidence[0]

    assert normalized.rule_id == "REPO-001"
    assert normalized.source_type == "filesystem"
    assert normalized.source_name == "repository"
    assert normalized.compliant is False
    assert normalized.observed_value == {
        "existing_files": [],
        "missing_files": ["README.md"],
    }
    assert normalized.expected_value == ["README.md"]


def test_evidence_normalizer_uses_generic_normalization_for_unknown_evidence() -> None:
    finding = GovernanceFinding(
        rule_id="GEN-001",
        title="Generic finding",
        severity=Severity.LOW,
        status=CheckStatus.PASSED,
        message="Generic rule passed.",
        evidence=[
            Evidence(
                source="generic-source",
                message="Generic evidence.",
                data={
                    "key": "value",
                },
            )
        ],
    )

    normalized_finding = EvidenceNormalizer().normalize_finding(finding)

    assert len(normalized_finding.normalized_evidence) == 1

    normalized = normalized_finding.normalized_evidence[0]

    assert normalized.rule_id == "GEN-001"
    assert normalized.source_type == "generic"
    assert normalized.source_name == "generic-source"
    assert normalized.compliant is True
    assert normalized.observed_value == {"key": "value"}