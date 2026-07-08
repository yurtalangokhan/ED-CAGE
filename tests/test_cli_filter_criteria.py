from pathlib import Path

from ed_cage.cli import _merge_config_filter_criteria
from ed_cage.config import ProjectConfig
from ed_cage.domain.enums import ExecutionMode
from ed_cage.domain.models import RuleFilterCriteria


def test_merge_config_filter_criteria_uses_config_execution_mode_when_cli_is_mixed() -> None:
    criteria = RuleFilterCriteria(
        execution_mode=ExecutionMode.MIXED,
    )
    config = _build_config(
        execution_mode=ExecutionMode.STATIC,
    )

    merged = _merge_config_filter_criteria(
        filter_criteria=criteria,
        config=config,
    )

    assert merged.execution_mode == ExecutionMode.STATIC


def test_merge_config_filter_criteria_keeps_cli_execution_mode_when_explicit() -> None:
    criteria = RuleFilterCriteria(
        execution_mode=ExecutionMode.RUNTIME,
    )
    config = _build_config(
        execution_mode=ExecutionMode.STATIC,
    )

    merged = _merge_config_filter_criteria(
        filter_criteria=criteria,
        config=config,
    )

    assert merged.execution_mode == ExecutionMode.RUNTIME


def test_merge_config_filter_criteria_merges_disabled_rule_ids() -> None:
    criteria = RuleFilterCriteria(
        disabled_rule_ids=[
            "DEP-001",
        ],
    )
    config = _build_config(
        disabled_rule_ids=[
            "DEP-002",
            "dep-001",
        ],
    )

    merged = _merge_config_filter_criteria(
        filter_criteria=criteria,
        config=config,
    )

    assert merged.disabled_rule_ids == [
        "DEP-001",
        "DEP-002",
    ]


def _build_config(
    execution_mode: ExecutionMode = ExecutionMode.MIXED,
    disabled_rule_ids: list[str] | None = None,
) -> ProjectConfig:
    return ProjectConfig(
        project_name="test",
        repository_path=Path("."),
        rules_path=Path("configs/rules"),
        services_path=Path("configs/services.yaml"),
        actions_path=Path("configs/actions.yaml"),
        scenarios_path=Path("configs/scenarios"),
        output_path=Path("outputs"),
        evidence_registry_path=Path("outputs/evidence/evidence-registry.jsonl"),
        execution_mode=execution_mode,
        disabled_rule_ids=disabled_rule_ids or [],
    )