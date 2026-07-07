from pathlib import Path

from ed_cage.adapters.filesystem.yaml_rule_provider import YamlRuleProvider
from ed_cage.application.runner import GovernanceRunner
from ed_cage.checks.repository.required_files_check import RequiredFilesCheck
from ed_cage.checks.service.http_health_endpoint_check import HttpHealthEndpointCheck
from ed_cage.domain.enums import CheckStatus
from ed_cage.domain.models import ProjectContext


def test_runner_executes_registered_rules() -> None:
    context = ProjectContext(
        project_name="ed-cage",
        repository_path=Path(".").resolve(),
        config_path=Path("configs/ed-cage.yaml").resolve(),
        services=[],
    )

    rule_provider = YamlRuleProvider(Path("configs/rules"))

    runner = GovernanceRunner(
        rule_provider=rule_provider,
        checks=[
            RequiredFilesCheck(),
            HttpHealthEndpointCheck(),
        ],
    )

    result = runner.run(context)

    assert len(result.findings) >= 1
    assert all(
        finding.status in {
            CheckStatus.PASSED,
            CheckStatus.FAILED,
            CheckStatus.SKIPPED,
            CheckStatus.ERROR,
        }
        for finding in result.findings
    )