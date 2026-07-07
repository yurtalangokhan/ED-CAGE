from pathlib import Path

from ed_cage.adapters.filesystem.yaml_scenario_provider import YamlScenarioProvider
from ed_cage.domain.enums import CheckStatus


def test_yaml_scenario_provider_loads_scenario(tmp_path: Path) -> None:
    scenario_file = tmp_path / "scenario.yaml"
    scenario_file.write_text(
        """
scenario_id: SCN-TEST
name: Test scenario
description: Test scenario description.

filter_criteria:
  categories:
    - repository

expected:
  gate_passed: true
  minimum_score: 100
  finding_count: 1
  action_count: 0
  findings:
    - rule_id: REPO-001
      status: passed
""",
        encoding="utf-8",
    )

    scenario = YamlScenarioProvider(scenario_file).load_scenario()

    assert scenario.scenario_id == "SCN-TEST"
    assert scenario.name == "Test scenario"
    assert scenario.filter_criteria.categories == ["repository"]
    assert scenario.expected.gate_passed is True
    assert scenario.expected.minimum_score == 100
    assert scenario.expected.finding_count == 1
    assert scenario.expected.action_count == 0
    assert len(scenario.expected.findings) == 1
    assert scenario.expected.findings[0].rule_id == "REPO-001"
    assert scenario.expected.findings[0].status == CheckStatus.PASSED