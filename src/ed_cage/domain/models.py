from datetime import datetime
from pathlib import Path
from typing import Any
from uuid import uuid4

from pydantic import BaseModel, Field, field_validator

from ed_cage.domain.enums import (
    ActionPriority,
    CheckStatus,
    GovernanceActionType,
    ExecutionMode,
    Severity,
)


def new_run_id() -> str:
    return str(uuid4())


class GovernanceRule(BaseModel):
    id: str
    title: str
    description: str = ""
    category: str
    severity: Severity = Severity.MEDIUM
    target: str
    check_type: str
    enabled: bool = True
    params: dict[str, Any] = Field(default_factory=dict)
    tags: list[str] = Field(default_factory=list)


class RuleFilterCriteria(BaseModel):
    rule_ids: list[str] = Field(default_factory=list)
    categories: list[str] = Field(default_factory=list)
    severities: list[Severity] = Field(default_factory=list)
    check_types: list[str] = Field(default_factory=list)
    targets: list[str] = Field(default_factory=list)
    execution_mode: ExecutionMode = ExecutionMode.MIXED

    @property
    def has_filters(self) -> bool:
        return any(
            [
                self.rule_ids,
                self.categories,
                self.severities,
                self.check_types,
                self.targets,
                self.execution_mode != ExecutionMode.MIXED,
            ]
        )


class ServiceDefinition(BaseModel):
    name: str
    base_url: str
    health_endpoints: list[str] = Field(default_factory=list)
    openapi_paths: list[str] = Field(default_factory=list)
    metrics_paths: list[str] = Field(default_factory=list)
    tags: list[str] = Field(default_factory=list)
    metadata: dict[str, Any] = Field(default_factory=dict)

    @field_validator("base_url")
    @classmethod
    def validate_base_url(cls, value: str) -> str:
        if not value.startswith(("http://", "https://")):
            raise ValueError("base_url must start with http:// or https://")
        return value.rstrip("/")

    @field_validator("health_endpoints", "openapi_paths", "metrics_paths")
    @classmethod
    def validate_relative_paths(cls, value: list[str]) -> list[str]:
        normalized: list[str] = []

        for path in value:
            if not path.startswith("/"):
                normalized.append(f"/{path}")
            else:
                normalized.append(path)

        return normalized


class Evidence(BaseModel):
    source: str
    message: str
    data: dict[str, Any] = Field(default_factory=dict)


class NormalizedEvidence(BaseModel):
    rule_id: str
    source_type: str
    source_name: str
    resource: str | None = None
    observed_value: Any | None = None
    expected_value: Any | None = None
    compliant: bool | None = None
    message: str
    raw_data: dict[str, Any] = Field(default_factory=dict)
    metadata: dict[str, Any] = Field(default_factory=dict)


class GovernanceFinding(BaseModel):
    rule_id: str
    title: str
    severity: Severity
    status: CheckStatus
    message: str
    category: str | None = None
    target: str | None = None
    check_type: str | None = None
    evidence: list[Evidence] = Field(default_factory=list)
    normalized_evidence: list[NormalizedEvidence] = Field(default_factory=list)


class GovernanceActionDefinition(BaseModel):
    id: str
    title: str
    recommendation: str
    implementation_hint: str = ""
    rule_id: str | None = None
    category: str | None = None
    target: str | None = None
    check_type: str | None = None
    status: CheckStatus | None = None
    severity: Severity | None = None
    action_type: GovernanceActionType = GovernanceActionType.REMEDIATION
    priority: ActionPriority = ActionPriority.MEDIUM
    references: list[str] = Field(default_factory=list)
    tags: list[str] = Field(default_factory=list)
    metadata: dict[str, Any] = Field(default_factory=dict)


class GovernanceAction(BaseModel):
    action_id: str
    rule_id: str
    finding_status: CheckStatus
    severity: Severity
    title: str
    action_type: GovernanceActionType
    priority: ActionPriority
    recommendation: str
    implementation_hint: str = ""
    category: str | None = None
    target: str | None = None
    check_type: str | None = None
    references: list[str] = Field(default_factory=list)
    tags: list[str] = Field(default_factory=list)
    metadata: dict[str, Any] = Field(default_factory=dict)


class GovernanceScore(BaseModel):
    score: float
    achieved_score: float
    max_score: float
    total_findings: int
    evaluated_findings: int
    skipped_findings: int
    status_summary: dict[str, int] = Field(default_factory=dict)
    severity_summary: dict[str, int] = Field(default_factory=dict)


class GovernanceGatePolicy(BaseModel):
    minimum_score: float = 80.0
    fail_on_error: bool = True
    fail_on_critical: bool = True
    fail_on_high: bool = True
    fail_on_medium: bool = False
    fail_on_any_failure: bool = False


class GovernanceGateResult(BaseModel):
    passed: bool
    actual_score: float
    minimum_score: float
    reasons: list[str] = Field(default_factory=list)
    blocking_findings: list[str] = Field(default_factory=list)


class EvidenceRegistryRecord(BaseModel):
    run_id: str
    project_name: str
    rule_id: str
    finding_title: str
    finding_status: CheckStatus
    severity: Severity
    source_type: str
    source_name: str
    resource: str | None = None
    observed_value: Any | None = None
    expected_value: Any | None = None
    compliant: bool | None = None
    message: str
    raw_data: dict[str, Any] = Field(default_factory=dict)
    metadata: dict[str, Any] = Field(default_factory=dict)
    created_at: datetime


class EvidenceRegistryWriteResult(BaseModel):
    path: Path
    records_written: int


class ScenarioExpectedFinding(BaseModel):
    rule_id: str
    status: CheckStatus | None = None
    severity: Severity | None = None


class ScenarioExpectedAction(BaseModel):
    rule_id: str | None = None
    action_id: str | None = None
    priority: ActionPriority | None = None
    action_type: GovernanceActionType | None = None


class ScenarioExpectedOutcome(BaseModel):
    gate_passed: bool | None = None
    minimum_score: float | None = None
    maximum_score: float | None = None
    finding_count: int | None = None
    action_count: int | None = None
    findings: list[ScenarioExpectedFinding] = Field(default_factory=list)
    actions: list[ScenarioExpectedAction] = Field(default_factory=list)


class ScenarioDefinition(BaseModel):
    scenario_id: str
    name: str
    description: str = ""
    filter_criteria: RuleFilterCriteria = Field(default_factory=RuleFilterCriteria)
    expected: ScenarioExpectedOutcome = Field(default_factory=ScenarioExpectedOutcome)
    metadata: dict[str, Any] = Field(default_factory=dict)


class ScenarioAssertionResult(BaseModel):
    name: str
    passed: bool
    message: str
    details: dict[str, Any] = Field(default_factory=dict)


class ScenarioRunResult(BaseModel):
    scenario_id: str
    scenario_name: str
    governance_run_id: str
    passed: bool
    assertions: list[ScenarioAssertionResult] = Field(default_factory=list)


class ProjectContext(BaseModel):
    project_name: str
    repository_path: Path
    config_path: Path
    architecture_catalog_path: Path | None = None
    services: list[ServiceDefinition] = Field(default_factory=list)
    metadata: dict[str, Any] = Field(default_factory=dict)


class GovernanceRunResult(BaseModel):
    run_id: str = Field(default_factory=new_run_id)
    project_name: str
    started_at: datetime
    finished_at: datetime
    findings: list[GovernanceFinding]
    score: GovernanceScore | None = None
    gate_result: GovernanceGateResult | None = None
    actions: list[GovernanceAction] = Field(default_factory=list)

    @property
    def has_failures(self) -> bool:
        return any(f.status in {CheckStatus.FAILED, CheckStatus.ERROR} for f in self.findings)