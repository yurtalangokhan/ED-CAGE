from pathlib import Path

from ed_cage.adapters.filesystem.yaml_action_provider import YamlActionProvider
from ed_cage.domain.enums import ActionPriority, CheckStatus, GovernanceActionType


def test_yaml_action_provider_loads_actions(tmp_path: Path) -> None:
    actions_file = tmp_path / "actions.yaml"
    actions_file.write_text(
        """
actions:
  - id: ACTION-SVC-001
    rule_id: SVC-001
    status: failed
    title: Add health endpoint
    action_type: remediation
    priority: high
    recommendation: Add a health endpoint.
    implementation_hint: Expose /health.
    tags:
      - service
""",
        encoding="utf-8",
    )

    provider = YamlActionProvider(actions_file)

    actions = provider.load_actions()

    assert len(actions) == 1
    assert actions[0].id == "ACTION-SVC-001"
    assert actions[0].rule_id == "SVC-001"
    assert actions[0].status == CheckStatus.FAILED
    assert actions[0].action_type == GovernanceActionType.REMEDIATION
    assert actions[0].priority == ActionPriority.HIGH
    assert actions[0].tags == ["service"]


def test_yaml_action_provider_returns_empty_list_when_file_does_not_exist(
    tmp_path: Path,
) -> None:
    provider = YamlActionProvider(tmp_path / "missing-actions.yaml")

    actions = provider.load_actions()

    assert actions == []