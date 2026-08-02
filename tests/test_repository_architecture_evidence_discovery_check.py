from pathlib import Path

from ed_cage.checks.architecture.repository_architecture_evidence_discovery_check import (
    RepositoryArchitectureEvidenceDiscoveryCheck,
)
from ed_cage.domain.enums import CheckStatus, Severity
from ed_cage.domain.models import GovernanceRule, ProjectContext


def test_quality_scenario_uses_evidence_type_parameter(tmp_path: Path) -> None:
    scenario = tmp_path / "docs" / "quality-attributes" / "performance-scenario.md"
    scenario.parent.mkdir(parents=True)
    scenario.write_text(
        """
# Performance Scenario

## Source
A registered user

## Stimulus
Submits a search request

## Environment
Normal production load

## Artifact
Search API

## Response
The service returns matching results

## Response Measure
The 95th percentile latency remains below 500 ms

Quality attribute: performance
""".strip(),
        encoding="utf-8",
    )

    finding = RepositoryArchitectureEvidenceDiscoveryCheck().evaluate(
        rule=_quality_scenario_rule(),
        context=_context(tmp_path),
    )

    assert finding.status == CheckStatus.PASSED
    assert finding.evidence[0].data["evidence_type"] == "quality_scenario"
    discovered = finding.evidence[0].data["discovered_evidence"]
    assert discovered[0]["evidence_kind"] == "quality_scenario"


def test_single_design_decision_sentence_is_not_adr_evidence(tmp_path: Path) -> None:
    contributing = tmp_path / ".github" / "CONTRIBUTING.md"
    contributing.parent.mkdir(parents=True)
    contributing.write_text(
        "Contributors should discuss every important design decision in a pull request.",
        encoding="utf-8",
    )

    finding = RepositoryArchitectureEvidenceDiscoveryCheck().evaluate(
        rule=_adr_rule(),
        context=_context(tmp_path),
    )

    assert finding.status == CheckStatus.SKIPPED
    assert finding.evidence[0].data["discovered_evidence_count"] == 0


def test_structured_adr_is_discovered(tmp_path: Path) -> None:
    adr = tmp_path / "docs" / "adr" / "0001-use-event-streaming.md"
    adr.parent.mkdir(parents=True)
    adr.write_text(
        """
# ADR-0001: Use event streaming

## Status
Accepted

## Context
Services require asynchronous integration.

## Decision
Use an event-streaming platform for domain events.

## Consequences
Operational complexity increases, while temporal coupling decreases.
""".strip(),
        encoding="utf-8",
    )

    finding = RepositoryArchitectureEvidenceDiscoveryCheck().evaluate(
        rule=_adr_rule(),
        context=_context(tmp_path),
    )

    assert finding.status == CheckStatus.PASSED
    discovered = finding.evidence[0].data["discovered_evidence"]
    assert discovered[0]["evidence_kind"] == "adr"
    assert discovered[0]["confidence"] == "high"


def test_quality_scenario_phrase_alone_is_not_evidence(tmp_path: Path) -> None:
    document = tmp_path / "docs" / "architecture.md"
    document.parent.mkdir(parents=True)
    document.write_text(
        "The team may later document a quality attribute scenario for performance.",
        encoding="utf-8",
    )

    finding = RepositoryArchitectureEvidenceDiscoveryCheck().evaluate(
        rule=_quality_scenario_rule(),
        context=_context(tmp_path),
    )

    assert finding.status == CheckStatus.SKIPPED
    assert finding.evidence[0].data["discovered_evidence_count"] == 0


def test_legacy_evidence_kind_is_supported(tmp_path: Path) -> None:
    rule = _adr_rule()
    rule.params.pop("evidence_type")
    rule.params["evidence_kind"] = "adr"

    finding = RepositoryArchitectureEvidenceDiscoveryCheck().evaluate(
        rule=rule,
        context=_context(tmp_path),
    )

    assert finding.status == CheckStatus.SKIPPED
    assert finding.evidence[0].data["evidence_type"] == "adr"


def test_missing_evidence_type_returns_configuration_error(tmp_path: Path) -> None:
    rule = _adr_rule()
    rule.params.pop("evidence_type")

    finding = RepositoryArchitectureEvidenceDiscoveryCheck().evaluate(
        rule=rule,
        context=_context(tmp_path),
    )

    assert finding.status == CheckStatus.ERROR
    assert "requires the parameter 'evidence_type'" in finding.message


def _adr_rule() -> GovernanceRule:
    return GovernanceRule(
        id="ARCH-001",
        title="Architecture decision evidence should be discoverable",
        category="architecture",
        severity=Severity.MEDIUM,
        target="repository",
        check_type="repository_architecture_evidence_discovery",
        params={
            "evidence_type": "adr",
            "required": False,
            "include_paths": ["."],
            "exclude_paths": [".git", "node_modules", "target", "build", "dist", ".venv"],
            "file_patterns": ["*.md", "*.adoc", "*.rst", "*.txt", "*.yaml", "*.yml"],
            "candidate_paths": [
                "docs/adr",
                "docs/adrs",
                "adr",
                "adrs",
                "docs/architecture",
                "docs/architecture/decisions",
                "architecture/decisions",
                "docs/design",
                "docs/decisions",
                "decision-records",
                "design-decisions",
            ],
            "filename_indicators": [
                "adr",
                "adrs",
                "architecture-decision",
                "architecture-decision-record",
                "decision-record",
                "design-decision",
            ],
            "required_adr_marker_groups": ["context", "decision", "consequences"],
            "min_marker_count": 3,
        },
    )


def _quality_scenario_rule() -> GovernanceRule:
    return GovernanceRule(
        id="ARCH-002",
        title="Quality-attribute scenario evidence should be discoverable",
        category="architecture",
        severity=Severity.MEDIUM,
        target="repository",
        check_type="repository_architecture_evidence_discovery",
        params={
            "evidence_type": "quality_scenario",
            "required": False,
            "include_paths": ["."],
            "exclude_paths": [".git", "node_modules", "target", "build", "dist", ".venv"],
            "file_patterns": ["*.md", "*.adoc", "*.rst", "*.txt", "*.yaml", "*.yml", "*.json"],
            "candidate_paths": [
                "docs/quality-attributes",
                "docs/quality",
                "docs/scenarios",
                "docs/architecture",
                "docs/requirements",
                "docs/nfr",
                "requirements",
                "architecture",
                "design",
            ],
            "filename_indicators": [
                "scenario",
                "quality-attribute",
                "quality_attributes",
                "nfr",
                "non-functional",
                "nonfunctional",
            ],
            "scenario_markers": [
                "stimulus",
                "source",
                "environment",
                "artifact",
                "response",
                "response measure",
                "quality attribute scenario",
            ],
            "quality_attribute_markers": [
                "availability",
                "modifiability",
                "performance",
                "security",
                "reliability",
                "scalability",
                "maintainability",
            ],
            "min_scenario_marker_count": 3,
        },
    )


def _context(repository_path: Path) -> ProjectContext:
    return ProjectContext(
        project_name="test",
        repository_path=repository_path,
        config_path=repository_path / "configs" / "ed-cage.yaml",
        services=[],
    )
