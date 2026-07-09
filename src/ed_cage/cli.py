from pathlib import Path

import typer
from rich.console import Console
from rich.table import Table

from ed_cage.adapters.console.rich_reporter import RichConsoleReporter
from ed_cage.adapters.filesystem.jsonl_evidence_registry import JsonlEvidenceRegistry
from ed_cage.adapters.filesystem.yaml_action_provider import YamlActionProvider
from ed_cage.adapters.filesystem.yaml_rule_provider import YamlRuleProvider
from ed_cage.adapters.filesystem.yaml_scenario_provider import YamlScenarioProvider
from ed_cage.adapters.filesystem.yaml_service_catalog_provider import (
    YamlServiceCatalogProvider,
)
from ed_cage.adapters.reporting.composite_reporter import CompositeReporter
from ed_cage.adapters.reporting.json_file_reporter import JsonFileReporter
from ed_cage.adapters.reporting.markdown_file_reporter import MarkdownFileReporter
from ed_cage.application.action_generator import GovernanceActionGenerator
from ed_cage.application.gate import GovernanceGateEvaluator
from ed_cage.application.runner import GovernanceRunner
from ed_cage.application.scenario_runner import ScenarioRunner
from ed_cage.config import ProjectConfig, load_project_config
from ed_cage.domain.enums import Severity, ExecutionMode
from ed_cage.domain.models import (
    GovernanceRunResult,
    ProjectContext,
    RuleFilterCriteria,
    ScenarioRunResult,
)
from ed_cage.domain.models import EvidenceRegistryWriteResult
from ed_cage.application.check_registry import CheckRegistry
from ed_cage.adapters.reporting.scenario_json_file_reporter import (
    ScenarioJsonFileReporter,
)
from ed_cage.adapters.reporting.evaluation_summary_reporter import (
    EvaluationSummaryReporter,
)
from ed_cage.application.evaluation_aggregator import EvaluationAggregator
from ed_cage.application.scoring import GovernanceScorer

app = typer.Typer(
    name="ed-cage",
    help="ED-CAGE: Event-Driven Continuous Architecture Governance Engine",
)


@app.command()
def validate_config(
    config_path: Path = typer.Option(
        Path("configs/ed-cage.yaml"),
        "--config",
        "-c",
        help="Path to ED-CAGE project configuration file.",
    )
) -> None:
    config = load_project_config(config_path)

    typer.echo(f"Config is valid for project: {config.project_name}")
    typer.echo(f"Repository path: {config.repository_path}")
    typer.echo(f"Rules path: {config.rules_path}")
    typer.echo(f"Services path: {config.services_path}")
    typer.echo(f"Actions path: {config.actions_path}")
    typer.echo(f"Scenarios path: {config.scenarios_path}")
    typer.echo(f"Output path: {config.output_path}")
    typer.echo(f"Evidence registry path: {config.evidence_registry_path}")
    typer.echo(f"Minimum governance score: {config.governance_gate.minimum_score}")
    typer.echo("Scoring category weights:")
    for category_name, category_weight in sorted(
        config.scoring.category_weights.items()
    ):
        typer.echo(f" - {category_name}: {category_weight}")

    typer.echo("Maturity bands:")
    for maturity_band in config.scoring.maturity_bands:
        typer.echo(
            f" - {maturity_band.name}: "
            f"{maturity_band.min_score}-{maturity_band.max_score}"
        )
    typer.echo(f"Execution mode: {config.execution_mode.value}")
    typer.echo(f"Fail on error: {config.governance_gate.fail_on_error}")
    typer.echo(f"Fail on critical: {config.governance_gate.fail_on_critical}")
    typer.echo(f"Fail on high: {config.governance_gate.fail_on_high}")
    typer.echo(f"Fail on medium: {config.governance_gate.fail_on_medium}")
    typer.echo(f"Fail on any failure: {config.governance_gate.fail_on_any_failure}")
    if config.architecture_catalog_path is not None:
        typer.echo(f"Architecture catalog path: {config.architecture_catalog_path}")

    if config.kubernetes_manifest_paths:
        typer.echo("Kubernetes manifest paths:")
    if config.disabled_rule_ids:
        typer.echo("Disabled rule ids:")
        for rule_id in config.disabled_rule_ids:
            typer.echo(f" - {rule_id}")

    for manifest_path in config.kubernetes_manifest_paths:
        typer.echo(f"  - {manifest_path}")


@app.command()
def scan(
    config_path: Path = typer.Option(
        Path("configs/ed-cage.yaml"),
        "--config",
        "-c",
        help="Path to ED-CAGE project configuration file.",
    ),
    report_filename: str = typer.Option(
        "governance-report.json",
        "--report-filename",
        help="JSON report filename.",
    ),
    markdown_report_filename: str = typer.Option(
        "governance-report.md",
        "--markdown-report-filename",
        help="Markdown report filename.",
    ),
    rule_id: str | None = typer.Option(
        None,
        "--rule-id",
        help="Comma-separated rule IDs to execute. Example: REPO-001,SVC-001",
    ),
    category: str | None = typer.Option(
        None,
        "--category",
        help="Comma-separated rule categories to execute. Example: repository,service",
    ),
    severity: str | None = typer.Option(
        None,
        "--severity",
        help="Comma-separated severities to execute. Example: medium,high",
    ),
    check_type: str | None = typer.Option(
        None,
        "--check-type",
        help="Comma-separated check types to execute. Example: required_files,http_health_endpoint",
    ),
    target: str | None = typer.Option(
        None,
        "--target",
        help="Comma-separated rule targets to execute. Example: repository,service",
    ),
    execution_mode: str = typer.Option(
        "mixed",
        "--execution-mode",
        help="Execution mode: static, runtime or mixed.",
    ),
) -> None:
    config = load_project_config(config_path)

    filter_criteria = RuleFilterCriteria(
        rule_ids=_parse_csv_option(rule_id),
        categories=_parse_csv_option(category),
        severities=_parse_severity_option(severity),
        check_types=_parse_csv_option(check_type),
        targets=_parse_csv_option(target),
        execution_mode=_parse_execution_mode(execution_mode),
    )

    result = _execute_governance_run(
        config=config,
        config_path=config_path,
        filter_criteria=filter_criteria,
    )

    evidence_registry_result = _store_evidence(config, result)

    _report_governance_result(
        config=config,
        result=result,
        report_filename=report_filename,
        markdown_report_filename=markdown_report_filename,
    )

    typer.echo(f"JSON report written to: {config.output_path / report_filename}")
    typer.echo(
        f"Markdown report written to: {config.output_path / markdown_report_filename}"
    )

    if result.score is not None:
        typer.echo(f"Governance maturity: {result.score.maturity_band}")
        typer.echo(f"Category-weighted score: {result.score.score:.2f} / 100")
    typer.echo(
        "Evidence registry updated: "
        f"{evidence_registry_result.path} "
        f"({evidence_registry_result.records_written} record(s))"
    )

    if result.gate_result is not None and not result.gate_result.passed:
        typer.echo(
            "Governance gate: FAILED "
            "(reported as a governance signal; scan completed successfully)"
        )


@app.command("run-scenario")
def run_scenario(
    scenario_path: Path = typer.Option(
        Path("configs/scenarios/repository_baseline.yaml"),
        "--scenario",
        "-s",
        help="Path to scenario YAML file.",
    ),
    config_path: Path = typer.Option(
        Path("configs/ed-cage.yaml"),
        "--config",
        "-c",
        help="Path to ED-CAGE project configuration file.",
    ),
    report_filename: str = typer.Option(
        "governance-report.json",
        "--report-filename",
        help="JSON report filename.",
    ),
    markdown_report_filename: str = typer.Option(
        "governance-report.md",
        "--markdown-report-filename",
        help="Markdown report filename.",
    ),
) -> None:
    config = load_project_config(config_path)
    scenario = YamlScenarioProvider(scenario_path).load_scenario()

    result = _execute_governance_run(
        config=config,
        config_path=config_path,
        filter_criteria=scenario.filter_criteria,
    )

    evidence_registry_result = _store_evidence(config, result)

    _report_governance_result(
        config=config,
        result=result,
        report_filename=report_filename,
        markdown_report_filename=markdown_report_filename,
    )

    scenario_result = ScenarioRunner().run(
        scenario=scenario,
        result=result,
    )
    _print_scenario_result(scenario_result)

    if result.gate_result is not None:
        gate_label = "PASSED" if result.gate_result.passed else "FAILED"
        typer.echo(f"Governance gate in scenario run: {gate_label}")

    if result.score is not None:
        typer.echo(f"Governance score in scenario run: {result.score.score:.2f} / 100")

    scenario_report_file = ScenarioJsonFileReporter(
        output_path=config.output_path,
    ).report(
        scenario_result=scenario_result,
        governance_result=result,
    )

    typer.echo(f"Scenario report written to: {scenario_report_file}")

    typer.echo(f"JSON report written to: {config.output_path / report_filename}")
    typer.echo(
        f"Markdown report written to: {config.output_path / markdown_report_filename}"
    )
    typer.echo(
        "Evidence registry updated: "
        f"{evidence_registry_result.path} "
        f"({evidence_registry_result.records_written} record(s))"
    )

    if not scenario_result.passed:
        raise typer.Exit(code=1)

    if result.gate_result is not None and not result.gate_result.passed:
        raise typer.Exit(code=1)


def _execute_governance_run(
    config: ProjectConfig,
    config_path: Path,
    filter_criteria: RuleFilterCriteria,
) -> GovernanceRunResult:
    services = YamlServiceCatalogProvider(config.services_path).load_services()

    context = ProjectContext(
        project_name=config.project_name,
        repository_path=config.repository_path,
        config_path=config_path.resolve(),
        services=services,
        metadata=config.metadata,
        architecture_catalog_path=config.architecture_catalog_path,
        kubernetes_manifest_paths=config.kubernetes_manifest_paths,
    )

    rule_provider = YamlRuleProvider(config.rules_path)

    runner = GovernanceRunner(
        rule_provider=rule_provider,
        checks=CheckRegistry.default().all_checks(),
        scorer=GovernanceScorer(config.scoring),
    )

    effective_filter_criteria = _merge_config_filter_criteria(
        filter_criteria=filter_criteria,
        config=config,
    )

    result = runner.run(
        context=context,
        filter_criteria=effective_filter_criteria,
    )

    result = _attach_config_applicability_summary(
        result=result,
        config=config,
    )

    gate_result = GovernanceGateEvaluator().evaluate(
        result=result,
        policy=config.governance_gate,
    )
    result.gate_result = gate_result

    action_definitions = YamlActionProvider(config.actions_path).load_actions()
    result.actions = GovernanceActionGenerator().generate(
        result=result,
        action_definitions=action_definitions,
    )

    return result

def _attach_config_applicability_summary(
    result: GovernanceRunResult,
    config: ProjectConfig,
) -> GovernanceRunResult:
    if result.score is None:
        return result

    excluded_rule_ids = _deduplicate_rule_ids(config.disabled_rule_ids)

    if not excluded_rule_ids:
        return result

    weighted_score_explanation = {
        **result.score.weighted_score_explanation,
        "excluded_rule_ids": excluded_rule_ids,
        "excluded_rule_count": len(excluded_rule_ids),
        "excluded_rule_reason": "disabled_by_case_config",
    }

    result.score = result.score.model_copy(
        update={
            "not_applicable_rule_count": (
                result.score.not_applicable_rule_count
                + len(excluded_rule_ids)
            ),
            "weighted_score_explanation": weighted_score_explanation,
        }
    )

    return result


def _deduplicate_rule_ids(rule_ids: list[str]) -> list[str]:
    normalized_rule_ids: list[str] = []
    seen: set[str] = set()

    for rule_id in rule_ids:
        normalized_rule_id = rule_id.strip()

        if not normalized_rule_id:
            continue

        dedup_key = normalized_rule_id.upper()

        if dedup_key in seen:
            continue

        seen.add(dedup_key)
        normalized_rule_ids.append(normalized_rule_id)

    return normalized_rule_ids

def _store_evidence(
    config: ProjectConfig,
    result: GovernanceRunResult,
) -> EvidenceRegistryWriteResult:
    return JsonlEvidenceRegistry(
        registry_path=config.evidence_registry_path,
    ).store(result)


def _report_governance_result(
    config: ProjectConfig,
    result: GovernanceRunResult,
    report_filename: str,
    markdown_report_filename: str,
) -> None:
    reporter = CompositeReporter(
        reporters=[
            RichConsoleReporter(),
            JsonFileReporter(
                output_path=config.output_path,
                filename=report_filename,
            ),
            MarkdownFileReporter(
                output_path=config.output_path,
                filename=markdown_report_filename,
            ),
        ]
    )

    reporter.report(result)


def _print_scenario_result(scenario_result: ScenarioRunResult) -> None:
    console = Console()

    console.print()
    console.print("[bold]ED-CAGE Scenario Result[/bold]")
    console.print(f"Scenario ID: [bold]{scenario_result.scenario_id}[/bold]")
    console.print(f"Scenario name: {scenario_result.scenario_name}")
    console.print(f"Governance run ID: {scenario_result.governance_run_id}")
    console.print(
        "[bold green]Scenario: PASSED[/bold green]"
        if scenario_result.passed
        else "[bold red]Scenario: FAILED[/bold red]"
    )
    console.print()

    table = Table(title="Scenario Assertions")
    table.add_column("Assertion", style="bold")
    table.add_column("Status")
    table.add_column("Message")

    for assertion in scenario_result.assertions:
        table.add_row(
            assertion.name,
            "[green]passed[/green]" if assertion.passed else "[red]failed[/red]",
            assertion.message,
        )

    console.print(table)
    console.print()


def _merge_config_filter_criteria(
    filter_criteria: RuleFilterCriteria,
    config: ProjectConfig,
) -> RuleFilterCriteria:
    merged_disabled_rule_ids = [
        *filter_criteria.disabled_rule_ids,
        *config.disabled_rule_ids,
    ]

    normalized_disabled_rule_ids: list[str] = []
    seen: set[str] = set()

    for rule_id in merged_disabled_rule_ids:
        normalized_rule_id = rule_id.strip()

        if not normalized_rule_id:
            continue

        dedup_key = normalized_rule_id.upper()

        if dedup_key in seen:
            continue

        seen.add(dedup_key)
        normalized_disabled_rule_ids.append(normalized_rule_id)

    execution_mode = filter_criteria.execution_mode

    if execution_mode == ExecutionMode.MIXED:
        execution_mode = config.execution_mode

    return filter_criteria.model_copy(
        update={
            "disabled_rule_ids": normalized_disabled_rule_ids,
            "execution_mode": execution_mode,
        }
    )


def _merge_config_disabled_rule_ids(
    filter_criteria: RuleFilterCriteria,
    disabled_rule_ids: list[str],
) -> RuleFilterCriteria:
    merged_disabled_rule_ids = [
        *filter_criteria.disabled_rule_ids,
        *disabled_rule_ids,
    ]

    normalized_disabled_rule_ids: list[str] = []
    seen: set[str] = set()

    for rule_id in merged_disabled_rule_ids:
        normalized_rule_id = rule_id.strip()

        if not normalized_rule_id:
            continue

        dedup_key = normalized_rule_id.upper()

        if dedup_key in seen:
            continue

        seen.add(dedup_key)
        normalized_disabled_rule_ids.append(normalized_rule_id)

    return filter_criteria.model_copy(
        update={
            "disabled_rule_ids": normalized_disabled_rule_ids,
        }
    )


def _parse_csv_option(value: str | None) -> list[str]:
    if value is None:
        return []

    return [item.strip() for item in value.split(",") if item.strip()]


def _parse_severity_option(value: str | None) -> list[Severity]:
    raw_values = _parse_csv_option(value)
    severities: list[Severity] = []

    for raw_value in raw_values:
        try:
            severities.append(Severity(raw_value.lower()))
        except ValueError as exc:
            valid_values = ", ".join(severity.value for severity in Severity)
            raise typer.BadParameter(
                f"Invalid severity '{raw_value}'. Valid values: {valid_values}"
            ) from exc

    return severities


def _parse_execution_mode(value: str) -> ExecutionMode:
    normalized_value = value.strip().lower()

    try:
        return ExecutionMode(normalized_value)
    except ValueError as exc:
        allowed_values = ", ".join(mode.value for mode in ExecutionMode)
        raise typer.BadParameter(
            f"Invalid execution mode: {value}. Allowed values: {allowed_values}"
        ) from exc


@app.command("aggregate-evaluation")
def aggregate_evaluation(
    reports_root: Path = typer.Option(
        Path("outputs/case-studies"),
        "--reports-root",
        help="Root directory containing case-study scenario-report.json files.",
    ),
    output_path: Path = typer.Option(
        Path("outputs/evaluation"),
        "--output-path",
        help="Directory where aggregated evaluation reports will be written.",
    ),
) -> None:
    aggregation_result = EvaluationAggregator().aggregate(
        reports_root=reports_root,
    )

    if aggregation_result["case_count"] == 0:
        typer.echo(f"No scenario-report.json files were found under: {reports_root}")
        raise typer.Exit(code=1)

    json_file, markdown_file = EvaluationSummaryReporter(
        output_path=output_path,
    ).report(aggregation_result)

    typer.echo(f"Evaluation JSON summary written to: {json_file}")
    typer.echo(f"Evaluation Markdown summary written to: {markdown_file}")
