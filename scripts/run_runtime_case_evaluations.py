from __future__ import annotations

import argparse
import json
import shutil
import subprocess
from collections import Counter
from pathlib import Path
from typing import Any

import yaml


DEFAULT_RUNTIME_CASE_CONFIGS = [
    "configs/cases/spring-petclinic-microservices-runtime.yaml",
    "configs/cases/online-boutique-runtime.yaml",
    "configs/cases/train-ticket-runtime.yaml",
]

SUMMARY_OUTPUT_DIR = Path("outputs/case-studies")
SUMMARY_JSON_PATH = SUMMARY_OUTPUT_DIR / "runtime-evaluation-summary.json"
SUMMARY_MARKDOWN_PATH = SUMMARY_OUTPUT_DIR / "runtime-evaluation-summary.md"


def main() -> None:
    args = _parse_args()

    config_paths = [
        Path(config_path).resolve()
        for config_path in (args.config or DEFAULT_RUNTIME_CASE_CONFIGS)
    ]

    results: list[dict[str, Any]] = []

    for config_path in config_paths:
        print()
        print("=" * 90)
        print(f"Running runtime case evaluation: {config_path}")
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

        results.append(
            _build_case_result(
                config_path=config_path,
                report_path=report_path,
                return_code=return_code,
            )
        )

        if return_code != 0 and args.stop_on_failure:
            break

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
        description="Run ED-CAGE runtime evaluation for configured case studies."
    )
    parser.add_argument(
        "--config",
        action="append",
        help=(
            "Runtime case config path. Can be passed multiple times. "
            "Defaults to all runtime case configs."
        ),
    )
    parser.add_argument(
        "--stop-on-failure",
        action="store_true",
        help="Stop batch execution when a case scan command fails.",
    )
    parser.add_argument(
        "--no-force-execution-mode",
        action="store_false",
        dest="force_execution_mode",
        help="Do not append --execution-mode runtime to scan commands.",
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
                "runtime",
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
        "success": report_path.exists(),
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
                "skipped_rule_ids": [],
                "error_rule_ids": [],
                "overall_score": None,
                "maturity_band": None,
                "category_scores": {},
                "category_weights": {},
                "applicable_rule_count": 0,
                "not_applicable_rule_count": 0,
                "gate_passed": None,
                "gate_reasons": [],
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
    skipped_rule_ids: list[str] = []
    error_rule_ids: list[str] = []

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
        elif status == "passed":
            passed_rule_ids.append(rule_id)
        elif status == "skipped":
            skipped_rule_ids.append(rule_id)
        elif status == "error":
            error_rule_ids.append(rule_id)

    score = report.get("score", {})

    if not isinstance(score, dict):
        score = {}

    gate_result = report.get("gate_result", {})

    if not isinstance(gate_result, dict):
        gate_result = {}

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
            "skipped_rule_ids": sorted(set(skipped_rule_ids)),
            "error_rule_ids": sorted(set(error_rule_ids)),
            "overall_score": score.get("score"),
            "maturity_band": score.get("maturity_band"),
            "category_scores": score.get("category_scores", {}),
            "category_weights": score.get("category_weights", {}),
            "applicable_rule_count": score.get("applicable_rule_count", 0),
            "not_applicable_rule_count": score.get("not_applicable_rule_count", 0),
            "gate_passed": gate_result.get("passed"),
            "gate_reasons": gate_result.get("reasons", []),
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
        "# ED-CAGE Runtime Case Evaluation Summary",
        "",
        f"- Case count: {summary['case_count']}",
        f"- Successful cases: {summary['successful_case_count']}",
        f"- Failed cases: {summary['failed_case_count']}",
        "",
        "| Case | Score | Maturity | Applicable | Not Applicable | Findings | Passed | Failed | Skipped | Error | Report |",
        "|---|---:|---|---:|---:|---:|---:|---:|---:|---:|---|",
    ]

    for case_result in summary["cases"]:
        project_name = case_result.get("project_name") or Path(
            case_result["config_path"]
        ).stem

        status_counts = case_result.get("status_counts", {})
        overall_score = case_result.get("overall_score")
        score_text = (
            f"{overall_score:.2f}"
            if isinstance(overall_score, int | float)
            else "-"
        )

        lines.append(
            "| "
            f"{project_name} | "
            f"{score_text} | "
            f"{case_result.get('maturity_band') or '-'} | "
            f"{case_result.get('applicable_rule_count', 0)} | "
            f"{case_result.get('not_applicable_rule_count', 0)} | "
            f"{case_result.get('finding_count', 0)} | "
            f"{status_counts.get('passed', 0)} | "
            f"{status_counts.get('failed', 0)} | "
            f"{status_counts.get('skipped', 0)} | "
            f"{status_counts.get('error', 0)} | "
            f"`{case_result.get('report_path')}` |"
        )

    lines.append("")
    lines.append("## Failed Runtime Rules by Case")
    lines.append("")

    for case_result in summary["cases"]:
        project_name = case_result.get("project_name") or Path(
            case_result["config_path"]
        ).stem
        failed_rule_ids = case_result.get("failed_rule_ids", [])

        lines.append(f"### {project_name}")
        lines.append("")

        if not failed_rule_ids:
            lines.append("- No failed runtime rules.")
        else:
            for rule_id in failed_rule_ids:
                lines.append(f"- {rule_id}")

        lines.append("")

    lines.append("## Error Runtime Rules by Case")
    lines.append("")

    for case_result in summary["cases"]:
        project_name = case_result.get("project_name") or Path(
            case_result["config_path"]
        ).stem
        error_rule_ids = case_result.get("error_rule_ids", [])

        lines.append(f"### {project_name}")
        lines.append("")

        if not error_rule_ids:
            lines.append("- No error runtime rules.")
        else:
            for rule_id in error_rule_ids:
                lines.append(f"- {rule_id}")

        lines.append("")

    lines.append("## Category Scores by Case")
    lines.append("")

    for case_result in summary["cases"]:
        project_name = case_result.get("project_name") or Path(
            case_result["config_path"]
        ).stem
        category_scores = case_result.get("category_scores", {})

        lines.append(f"### {project_name}")
        lines.append("")

        if not category_scores:
            lines.append("- No category score was produced.")
            lines.append("")
            continue

        lines.append("| Category | Score | Weight |")
        lines.append("|---|---:|---:|")

        category_weights = case_result.get("category_weights", {})

        for category, category_score in sorted(category_scores.items()):
            category_weight = category_weights.get(category, 1.0)
            lines.append(
                f"| {category} | "
                f"{category_score:.2f} | "
                f"{category_weight:.2f} |"
            )

        lines.append("")

    return "\n".join(lines)


def _print_summary(summary: dict[str, Any]) -> None:
    print()
    print("=" * 90)
    print("Runtime evaluation summary")
    print("=" * 90)

    for case_result in summary["cases"]:
        project_name = case_result.get("project_name") or Path(
            case_result["config_path"]
        ).stem
        status_counts = case_result.get("status_counts", {})
        overall_score = case_result.get("overall_score")
        score_text = (
            f"{overall_score:.2f}"
            if isinstance(overall_score, int | float)
            else "-"
        )

        print(
            f"{project_name}: "
            f"score={score_text}, "
            f"maturity={case_result.get('maturity_band') or '-'}, "
            f"applicable={case_result.get('applicable_rule_count', 0)}, "
            f"not_applicable={case_result.get('not_applicable_rule_count', 0)}, "
            f"findings={case_result.get('finding_count', 0)}, "
            f"passed={status_counts.get('passed', 0)}, "
            f"failed={status_counts.get('failed', 0)}, "
            f"skipped={status_counts.get('skipped', 0)}, "
            f"error={status_counts.get('error', 0)}"
        )

    print()
    print(f"Summary JSON: {SUMMARY_JSON_PATH}")
    print(f"Summary Markdown: {SUMMARY_MARKDOWN_PATH}")


if __name__ == "__main__":
    main()