from enum import StrEnum


class Severity(StrEnum):
    INFO = "info"
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class CheckStatus(StrEnum):
    PASSED = "passed"
    FAILED = "failed"
    SKIPPED = "skipped"
    ERROR = "error"


class GovernanceActionType(StrEnum):
    REMEDIATION = "remediation"
    INVESTIGATION = "investigation"
    DOCUMENTATION = "documentation"
    CONFIGURATION = "configuration"


class ActionPriority(StrEnum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"

class ExecutionMode(StrEnum):
    STATIC = "static"
    RUNTIME = "runtime"
    MIXED = "mixed"

class ToolExecutionStatus(StrEnum):
    SUCCESS = "success"
    FAILED = "failed"
    SKIPPED = "skipped"
    ERROR = "error"
    UNAVAILABLE = "unavailable"