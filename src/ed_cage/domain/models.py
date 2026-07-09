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
    ToolExecutionStatus,
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
    disabled_rule_ids: list[str] = Field(default_factory=list)
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
                self.disabled_rule_ids,
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

class ToolExecutionResult(BaseModel):
    tool_name: str
    status: ToolExecutionStatus
    message: str
    command: list[str] = Field(default_factory=list)
    exit_code: int | None = None
    stdout: str = ""
    stderr: str = ""
    resource: str | None = None
    findings: list[dict[str, Any]] = Field(default_factory=list)
    summary: dict[str, Any] = Field(default_factory=dict)
    metadata: dict[str, Any] = Field(default_factory=dict)

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


class MaturityBand(BaseModel):
    name: str
    min_score: float
    max_score: float


class ScoringConfig(BaseModel):
    status_scores: dict[str, float] = Field(
        default_factory=lambda: {
            "passed": 1.0,
            "warning": 0.5,
            "failed": 0.0,
            "error": 0.0,
        }
    )
    category_weights: dict[str, float] = Field(
        default_factory=lambda: {
            "architecture": 1.2,
            "dependency": 1.1,
            "deployment": 1.1,
            "reliability": 1.3,
            "security": 1.3,
            "observability": 1.2,
            "repository": 0.7,
            "api": 1.0,
        }
    )
    maturity_bands: list[MaturityBand] = Field(
        default_factory=lambda: [
            MaturityBand(
                name="Initial Governance",
                min_score=0.0,
                max_score=39.99,
            ),
            MaturityBand(
                name="Emerging Governance",
                min_score=40.0,
                max_score=59.99,
            ),
            MaturityBand(
                name="Managed Governance",
                min_score=60.0,
                max_score=74.99,
            ),
            MaturityBand(
                name="Governed Architecture",
                min_score=75.0,
                max_score=89.99,
            ),
            MaturityBand(
                name="Continuously Governed Architecture",
                min_score=90.0,
                max_score=100.0,
            ),
        ]
    )


class CategoryGovernanceScore(BaseModel):
    category: str
    score: float
    weight: float
    applicable_rule_count: int
    passed_rule_count: int = 0
    warning_rule_count: int = 0
    failed_rule_count: int = 0
    error_rule_count: int = 0
    skipped_rule_count: int = 0


class GovernanceScore(BaseModel):
    score: float
    achieved_score: float
    max_score: float
    total_findings: int
    evaluated_findings: int
    skipped_findings: int
    status_summary: dict[str, int] = Field(default_factory=dict)
    severity_summary: dict[str, int] = Field(default_factory=dict)

    maturity_band: str = "Unknown"
    category_scores: dict[str, float] = Field(default_factory=dict)
    category_weights: dict[str, float] = Field(default_factory=dict)
    category_details: list[CategoryGovernanceScore] = Field(default_factory=list)
    applicable_rule_count: int = 0
    not_applicable_rule_count: int = 0
    weighted_score_explanation: dict[str, Any] = Field(default_factory=dict)


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
    kubernetes_manifest_paths: list[Path] = Field(default_factory=list)




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
    
