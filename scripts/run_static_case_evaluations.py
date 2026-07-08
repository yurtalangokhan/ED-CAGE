from __future__ import annotations

import argparse
import json
import shutil
import subprocess
from collections import Counter
from pathlib import Path
from typing import Any

import yaml


DEFAULT_STATIC_CASE_CONFIGS = [
    "configs/cases/spring-petclinic-microservices-static.yaml",
    "configs/cases/online-boutique-static.yaml",
    "configs/cases/train-ticket-static.yaml",
]

SUMMARY_OUTPUT_DIR = Path("outputs/case-studies")
SUMMARY_JSON_PATH = SUMMARY_OUTPUT_DIR / "static-evaluation-summary.json"
SUMMARY_MARKDOWN_PATH = SUMMARY_OUTPUT_DIR / "static-evaluation-summary.md"


def main() -> None:
    args = _parse_args()

    config_paths = [
        Path(config_path).resolve()
        for config_path in (args.config or DEFAULT_STATIC_CASE_CONFIGS)
    ]

    results: list[dict[str, Any]] = []

    for config_path in config_paths:
        print()
        print("=" * 90)
        print(f"Running static case evaluation: {config_path}")
        print("=" * 90)

        if not config_path.exists():
            results.append(
                {
                    "config_path": str(config_path),
                    "success": False,
                    "return_code": None,
                    "error": "config_not_found",
                }
            )
            print(f"Config not found: {config_path}")
            continue

        return_code = _run_ed_cage_scan(
            config_path=config_path,
            force_execution_mode=args.force_execution_mode,
        )

        report_path = _resolve_report_path(config_path)

        if return_code != 0 and args.stop_on_failure:
            results.append(
                _build_case_result(
                    config_path=config_path,
                    report_path=report_path,
                    return_code=return_code,
                )
            )
            break

        results.append(
            _build_case_result(
                config_path=config_path,
                report_path=report_path,
                return_code=return_code,
            )
        )

    summary = {
        "case_count": len(results),
        "successful_case_count": sum(1 for result in results if result["success"]),
        "failed_case_count": sum(1 for result in results if not result["success"]),
        "cases": results,
    }

    _write_summary(summary)
    _print_summary(summary)


def _parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Run ED-CAGE static evaluation for all configured case studies."
    )
    parser.add_argument(
        "--config",
        action="append",
        help="Case config path. Can be passed multiple times. Defaults to all static case configs.",
    )
    parser.add_argument(
        "--stop-on-failure",
        action="store_true",
        help="Stop batch execution when a case scan fails.",
    )
    parser.add_argument(
        "--no-force-execution-mode",
        action="store_false",
        dest="force_execution_mode",
        help="Do not append --execution-mode static to scan commands.",
    )
    parser.set_defaults(force_execution_mode=True)

    return parser.parse_args()


def _run_ed_cage_scan(
    config_path: Path,
    *,
    force_execution_mode: bool,
) -> int:
    executable = shutil.which("ed-cage") or "ed-cage"

    command = [
        executable,
        "scan",
        "--config",
        str(config_path),
    ]

    if force_execution_mode:
        command.extend(
            [
                "--execution-mode",
                "static",
            ]
        )

    completed_process = subprocess.run(
        command,
        check=False,
    )

    return completed_process.returncode


def _resolve_report_path(config_path: Path) -> Path:
    raw_config = yaml.safe_load(config_path.read_text(encoding="utf-8"))

    if not isinstance(raw_config, dict):
        raise ValueError(f"Invalid config file: {config_path}")

    raw_output_path = raw_config.get("output_path", "outputs")
    output_path = Path(str(raw_output_path))

    if not output_path.is_absolute():
        output_path = (Path.cwd() / output_path).resolve()

    if output_path.suffix.lower() == ".json":
        return output_path

    return output_path / "governance-report.json"


def _build_case_result(
    config_path: Path,
    report_path: Path,
    return_code: int | None,
) -> dict[str, Any]:
    result: dict[str, Any] = {
        "config_path": str(config_path),
        "report_path": str(report_path),
        "return_code": return_code,
        "success": return_code == 0 and report_path.exists(),
    }

    if not report_path.exists():
        result.update(
            {
                "error": "report_not_found",
                "project_name": None,
                "finding_count": 0,
                "status_counts": {},
                "severity_counts": {},
                "category_counts": {},
                "failed_rule_ids": [],
                "passed_rule_ids": [],
            }
        )
        return result

    report = json.loads(report_path.read_text(encoding="utf-8"))
    findings = report.get("findings", [])

    if not isinstance(findings, list):
        findings = []

    status_counts = Counter()
    severity_counts = Counter()
    category_counts = Counter()
    failed_rule_ids: list[str] = []
    passed_rule_ids: list[str] = []

    for finding in findings:
        if not isinstance(finding, dict):
            continue

        status = str(finding.get("status", "unknown"))
        severity = str(finding.get("severity", "unknown"))
        category = str(finding.get("category", "unknown"))
        rule_id = str(finding.get("rule_id", "unknown"))

        status_counts[status] += 1
        severity_counts[severity] += 1
        category_counts[category] += 1

        if status == "failed":
            failed_rule_ids.append(rule_id)

        if status == "passed":
            passed_rule_ids.append(rule_id)

    result.update(
        {
            "project_name": report.get("project_name"),
            "run_id": report.get("run_id"),
            "started_at": report.get("started_at"),
            "finished_at": report.get("finished_at"),
            "finding_count": len(findings),
            "status_counts": dict(sorted(status_counts.items())),
            "severity_counts": dict(sorted(severity_counts.items())),
            "category_counts": dict(sorted(category_counts.items())),
            "failed_rule_ids": sorted(set(failed_rule_ids)),
            "passed_rule_ids": sorted(set(passed_rule_ids)),
        }
    )

    return result


def _write_summary(summary: dict[str, Any]) -> None:
    SUMMARY_OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    SUMMARY_JSON_PATH.write_text(
        json.dumps(summary, indent=2, ensure_ascii=False),
        encoding="utf-8",
    )

    SUMMARY_MARKDOWN_PATH.write_text(
        _render_markdown_summary(summary),
        encoding="utf-8",
    )


def _render_markdown_summary(summary: dict[str, Any]) -> str:
    lines = [
        "# ED-CAGE Static Case Evaluation Summary",
        "",
        f"- Case count: {summary['case_count']}",
        f"- Successful cases: {summary['successful_case_count']}",
        f"- Failed cases: {summary['failed_case_count']}",
        "",
        "| Case | Findings | Passed | Failed | Warning | Skipped | Report |",
        "|---|---:|---:|---:|---:|---:|---|",
    ]

    for case_result in summary["cases"]:
        project_name = case_result.get("project_name") or Path(
            case_result["config_path"]
        ).stem

        status_counts = case_result.get("status_counts", {})

        lines.append(
            "| "
            f"{project_name} | "
            f"{case_result.get('finding_count', 0)} | "
            f"{status_counts.get('passed', 0)} | "
            f"{status_counts.get('failed', 0)} | "
            f"{status_counts.get('warning', 0)} | "
            f"{status_counts.get('skipped', 0)} | "
            f"`{case_result.get('report_path')}` |"
        )

    lines.append("")
    lines.append("## Failed Rules by Case")
    lines.append("")

    for case_result in summary["cases"]:
        project_name = case_result.get("project_name") or Path(
            case_result["config_path"]
        ).stem
        failed_rule_ids = case_result.get("failed_rule_ids", [])

        lines.append(f"### {project_name}")
        lines.append("")

        if not failed_rule_ids:
            lines.append("- No failed rules.")
        else:
            for rule_id in failed_rule_ids:
                lines.append(f"- {rule_id}")

        lines.append("")

    return "\n".join(lines)


def _print_summary(summary: dict[str, Any]) -> None:
    print()
    print("=" * 90)
    print("Static evaluation summary")
    print("=" * 90)

    for case_result in summary["cases"]:
        project_name = case_result.get("project_name") or Path(
            case_result["config_path"]
        ).stem
        status_counts = case_result.get("status_counts", {})

        print(
            f"{project_name}: "
            f"findings={case_result.get('finding_count', 0)}, "
            f"passed={status_counts.get('passed', 0)}, "
            f"failed={status_counts.get('failed', 0)}, "
            f"warning={status_counts.get('warning', 0)}, "
            f"skipped={status_counts.get('skipped', 0)}"
        )

    print()
    print(f"Summary JSON: {SUMMARY_JSON_PATH}")
    print(f"Summary Markdown: {SUMMARY_MARKDOWN_PATH}")


if __name__ == "__main__":
    main()