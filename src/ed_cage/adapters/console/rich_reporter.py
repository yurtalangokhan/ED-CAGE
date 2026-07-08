import json

from rich.console import Console
from rich.table import Table

from ed_cage.domain.enums import CheckStatus
from ed_cage.domain.models import GovernanceAction, GovernanceRunResult
from ed_cage.adapters.reporting.json_safety import to_json_safe


class RichConsoleReporter:
    def __init__(self) -> None:
        self.console = Console()

    def report(self, result: GovernanceRunResult) -> None:
        self.console.print()
        self.console.print("[bold]ED-CAGE Governance Report[/bold]")
        self.console.print(f"Run ID: [bold]{result.run_id}[/bold]")
        self.console.print(f"Project: [bold]{result.project_name}[/bold]")
        self.console.print(f"Started at: {result.started_at.isoformat()}")
        self.console.print(f"Finished at: {result.finished_at.isoformat()}")

        if result.score is not None:
            self.console.print(
                f"Governance score: [bold]{result.score.score:.2f} / 100[/bold]"
            )

        if result.gate_result is not None:
            self._print_gate_result(result)

        self.console.print()

        table = Table(title="Findings")
        table.add_column("Rule ID", style="bold")
        table.add_column("Severity")
        table.add_column("Status")
        table.add_column("Message")

        for finding in result.findings:
            table.add_row(
                finding.rule_id,
                finding.severity.value,
                self._format_status(finding.status),
                finding.message,
            )

        self.console.print(table)

        self._print_actions(result.actions)

        failed_or_error_findings = [
            finding
            for finding in result.findings
            if finding.status in {CheckStatus.FAILED, CheckStatus.ERROR}
        ]

        if failed_or_error_findings:
            self.console.print()
            self.console.print("[bold red]Evidence details[/bold red]")

            for finding in failed_or_error_findings:
                self.console.print()
                self.console.print(f"[bold]{finding.rule_id} - {finding.title}[/bold]")

                for evidence in finding.evidence:
                    self.console.print(f"Source: {evidence.source}")
                    self.console.print(f"Message: {evidence.message}")
                    self.console.print_json(
                        json.dumps(
                            to_json_safe(evidence.data),
                            ensure_ascii=False,
                            indent=2,
                        )
                    )

        self.console.print()

        if result.gate_result is not None:
            if result.gate_result.passed:
                self.console.print("[bold green]Governance gate: PASSED[/bold green]")
            else:
                self.console.print("[bold red]Governance gate: FAILED[/bold red]")
        elif result.has_failures:
            self.console.print("[bold red]Governance result: FAILED[/bold red]")
        else:
            self.console.print("[bold green]Governance result: PASSED[/bold green]")

    def _print_actions(self, actions: list[GovernanceAction]) -> None:
        if not actions:
            return

        self.console.print()
        table = Table(title="Recommended Actions")
        table.add_column("Rule ID", style="bold")
        table.add_column("Priority")
        table.add_column("Type")
        table.add_column("Action")
        table.add_column("Recommendation")

        for action in actions:
            table.add_row(
                action.rule_id,
                action.priority.value,
                action.action_type.value,
                action.title,
                action.recommendation,
            )

        self.console.print(table)

    def _print_gate_result(self, result: GovernanceRunResult) -> None:
        if result.gate_result is None:
            return

        gate_result = result.gate_result

        gate_text = "PASSED" if gate_result.passed else "FAILED"
        self.console.print(f"Governance gate: [bold]{gate_text}[/bold]")
        self.console.print(f"Minimum score: {gate_result.minimum_score:.2f}")

        if not gate_result.reasons:
            return

        self.console.print("Gate reason(s):")

        for reason in gate_result.reasons:
            self.console.print(f"- {reason}")

    def _format_status(self, status: CheckStatus) -> str:
        match status:
            case CheckStatus.PASSED:
                return "[green]passed[/green]"
            case CheckStatus.FAILED:
                return "[red]failed[/red]"
            case CheckStatus.ERROR:
                return "[bold red]error[/bold red]"
            case CheckStatus.SKIPPED:
                return "[yellow]skipped[/yellow]"

        return status.value
