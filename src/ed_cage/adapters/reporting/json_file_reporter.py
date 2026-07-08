import json
from pathlib import Path

from ed_cage.domain.models import GovernanceRunResult
from ed_cage.adapters.reporting.json_safety import to_json_safe

class JsonFileReporter:
    def __init__(
        self,
        output_path: Path,
        filename: str = "governance-report.json",
    ) -> None:
        self.output_path = output_path
        self.filename = filename

    def report(self, result: GovernanceRunResult) -> None:
        self.output_path.mkdir(parents=True, exist_ok=True)

        report_file = self.output_path / self.filename

        report_data = result.model_dump(mode="json")

        report_file.write_text(
            json.dumps( to_json_safe(report_data), ensure_ascii=False, indent=2, default=str),
            encoding="utf-8",
        )