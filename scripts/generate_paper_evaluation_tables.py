from __future__ import annotations

import argparse
import csv
import json
from pathlib import Path
from typing import Any


DEFAULT_SUMMARY_PATH = Path("outputs/case-studies/static-evaluation-summary.json")
DEFAULT_OUTPUT_DIR = Path("outputs/case-studies/paper-tables")

SEVERITY_RANK = {
    "critical": 0,
    "high": 1,
    "medium": 2,
    "low": 3,
    "info": 4,
}

CASE_DISPLAY_NAMES = {
    "spring-petclinic-microservices-static": "Spring PetClinic Microservices",
    "online-boutique-static": "Online Boutique",
    "train-ticket-static": "Train Ticket",
}

CASE_ARCHITECTURE_STYLES = {
    "spring-petclinic-microservices-static": "Microservices",
    "online-boutique-static": "Microservices",
    "train-ticket-static": "Microservices",
}


def main() -> None:
    args = _parse_args()

    summary_path = Path(args.summary).resolve()
    output_dir = Path(args.output_dir).resolve()

    summary = _load_json(summary_path)
    cases = _get_cases(summary)

    output_dir.mkdir(parents=True, exist_ok=True)

    tables = [
        (
            "table-1-case-study-systems",
            "Table 1. Case Study Systems",
            _build_case_study_system_rows(cases),
        ),
        (
            "table-2-governance-score-results",
            "Table 2. Category-Weighted Governance Score Results",
            _build_governance_score_rows(cases),
        ),
        (
            "table-3-category-level-scores",
            "Table 3. Category-Level Governance Scores",
            _build_category_score_rows(cases),
        ),
        (
            "table-4-top-governance-gaps",
            "Table 4. Top Governance Gaps",
            _build_top_governance_gap_rows(
                cases=cases,
                top_gaps_per_case=args.top_gaps_per_case,
            ),
        ),
        (
            "table-5-excluded-rules",
            "Table 5. Excluded / Not Applicable Rules",
            _build_excluded_rule_rows(cases),
        ),
    ]

    for filename_stem, _, rows in tables:
        _write_table(
            output_dir=output_dir,
            filename_stem=filename_stem,
            rows=rows,
        )

    _write_combined_markdown(
        output_dir=output_dir,
        tables=[
            (title, rows)
            for _, title, rows in tables
        ],
    )

    print(f"Paper-ready tables written to: {output_dir}")


def _parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Generate paper-ready evaluation tables from ED-CAGE summary."
    )
    parser.add_argument(
        "--summary",
        default=str(DEFAULT_SUMMARY_PATH),
        help="Path to static-evaluation-summary.json.",
    )
    parser.add_argument(
        "--output-dir",
        default=str(DEFAULT_OUTPUT_DIR),
        help="Directory where Markdown and CSV tables will be written.",
    )
    parser.add_argument(
        "--top-gaps-per-case",
        type=int,
        default=8,
        help="Maximum failed findings to include per case in the top gaps table.",
    )

    return parser.parse_args()


def _load_json(path: Path) -> dict[str, Any]:
    if not path.exists():
        raise FileNotFoundError(f"Summary file not found: {path}")

    data = json.loads(path.read_text(encoding="utf-8"))

    if not isinstance(data, dict):
        raise ValueError(f"Expected JSON object in summary file: {path}")

    return data


def _get_cases(summary: dict[str, Any]) -> list[dict[str, Any]]:
    cases = summary.get("cases", [])

    if not isinstance(cases, list):
        raise ValueError("Summary field 'cases' must be a list.")

    return [
        case
        for case in cases
        if isinstance(case, dict)
    ]


def _build_case_study_system_rows(
    cases: list[dict[str, Any]],
) -> list[dict[str, str]]:
    rows: list[dict[str, str]] = []

    for case in cases:
        project_name = _get_project_name(case)

        rows.append(
            {
                "System": _get_display_name(project_name),
                "Architecture Style": CASE_ARCHITECTURE_STYLES.get(
                    project_name,
                    "Microservices",
                ),
                "Deployment Artifact Profile": _infer_deployment_artifact_profile(
                    case
                ),
                "Evaluated Mode": "Static",
                "Applicable Governance Categories": _join_values(
                    sorted(_get_category_scores(case).keys())
                ),
                "Applicable Rules": str(case.get("applicable_rule_count", 0)),
                "Not Applicable Rules": str(
                    case.get("not_applicable_rule_count", 0)
                ),
            }
        )

    return rows


def _build_governance_score_rows(
    cases: list[dict[str, Any]],
) -> list[dict[str, str]]:
    rows: list[dict[str, str]] = []

    for case in cases:
        project_name = _get_project_name(case)
        status_counts = _get_dict(case, "status_counts")

        rows.append(
            {
                "System": _get_display_name(project_name),
                "Overall Score": _format_score(case.get("overall_score")),
                "Maturity Band": str(case.get("maturity_band") or "-"),
                "Applicable Rules": str(case.get("applicable_rule_count", 0)),
                "Not Applicable Rules": str(
                    case.get("not_applicable_rule_count", 0)
                ),
                "Passed Findings": str(status_counts.get("passed", 0)),
                "Failed Findings": str(status_counts.get("failed", 0)),
                "Skipped Findings": str(status_counts.get("skipped", 0)),
                "Error Findings": str(status_counts.get("error", 0)),
            }
        )

    return rows


def _build_category_score_rows(
    cases: list[dict[str, Any]],
) -> list[dict[str, str]]:
    rows: list[dict[str, str]] = []

    for case in cases:
        project_name = _get_project_name(case)
        category_scores = _get_category_scores(case)
        category_weights = _get_dict(case, "category_weights")

        for category in sorted(category_scores):
            rows.append(
                {
                    "System": _get_display_name(project_name),
                    "Category": category,
                    "Category Score": _format_score(category_scores[category]),
                    "Category Weight": _format_score(
                        category_weights.get(category, 1.0)
                    ),
                }
            )

    return rows


def _build_top_governance_gap_rows(
    cases: list[dict[str, Any]],
    top_gaps_per_case: int,
) -> list[dict[str, str]]:
    rows: list[dict[str, str]] = []

    for case in cases:
        project_name = _get_project_name(case)
        report_path = Path(str(case.get("report_path", "")))

        if not report_path.exists():
            rows.append(
                {
                    "System": _get_display_name(project_name),
                    "Rule ID": "-",
                    "Category": "-",
                    "Severity": "-",
                    "Finding Title": "Report file not found.",
                    "Finding Message": str(report_path),
                }
            )
            continue

        report = _load_json(report_path)
        findings = report.get("findings", [])

        if not isinstance(findings, list):
            continue

        failed_findings = [
            finding
            for finding in findings
            if isinstance(finding, dict)
            and finding.get("status") in {"failed", "error"}
        ]

        failed_findings.sort(
            key=lambda finding: (
                SEVERITY_RANK.get(str(finding.get("severity")), 99),
                str(finding.get("rule_id")),
            )
        )

        for finding in failed_findings[:top_gaps_per_case]:
            rows.append(
                {
                    "System": _get_display_name(project_name),
                    "Rule ID": str(finding.get("rule_id", "-")),
                    "Category": str(finding.get("category", "-")),
                    "Severity": str(finding.get("severity", "-")),
                    "Finding Title": str(finding.get("title", "-")),
                    "Finding Message": str(finding.get("message", "-")),
                }
            )

    return rows


def _build_excluded_rule_rows(
    cases: list[dict[str, Any]],
) -> list[dict[str, str]]:
    rows: list[dict[str, str]] = []

    for case in cases:
        project_name = _get_project_name(case)
        excluded_rule_ids = case.get("excluded_rule_ids", [])

        if not isinstance(excluded_rule_ids, list) or not excluded_rule_ids:
            rows.append(
                {
                    "System": _get_display_name(project_name),
                    "Excluded Rule ID": "-",
                    "Reason": "No excluded rule.",
                }
            )
            continue

        for rule_id in excluded_rule_ids:
            rows.append(
                {
                    "System": _get_display_name(project_name),
                    "Excluded Rule ID": str(rule_id),
                    "Reason": _infer_exclusion_reason(str(rule_id)),
                }
            )

    return rows


def _write_table(
    output_dir: Path,
    filename_stem: str,
    rows: list[dict[str, str]],
) -> None:
    _write_markdown_table(
        path=output_dir / f"{filename_stem}.md",
        rows=rows,
    )
    _write_csv_table(
        path=output_dir / f"{filename_stem}.csv",
        rows=rows,
    )


def _write_markdown_table(
    path: Path,
    rows: list[dict[str, str]],
) -> None:
    if not rows:
        path.write_text("_No data._\n", encoding="utf-8")
        return

    headers = list(rows[0].keys())
    lines = [
        "| " + " | ".join(headers) + " |",
        "| " + " | ".join("---" for _ in headers) + " |",
    ]

    for row in rows:
        lines.append(
            "| "
            + " | ".join(_escape_markdown(row.get(header, "")) for header in headers)
            + " |"
        )

    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def _write_csv_table(
    path: Path,
    rows: list[dict[str, str]],
) -> None:
    if not rows:
        path.write_text("", encoding="utf-8")
        return

    headers = list(rows[0].keys())

    with path.open("w", encoding="utf-8", newline="") as csv_file:
        writer = csv.DictWriter(csv_file, fieldnames=headers)
        writer.writeheader()
        writer.writerows(rows)


def _write_combined_markdown(
    output_dir: Path,
    tables: list[tuple[str, list[dict[str, str]]]],
) -> None:
    lines: list[str] = [
        "# ED-CAGE Paper-Ready Static Evaluation Tables",
        "",
    ]

    for title, rows in tables:
        lines.append(f"## {title}")
        lines.append("")

        if rows:
            headers = list(rows[0].keys())
            lines.append("| " + " | ".join(headers) + " |")
            lines.append("| " + " | ".join("---" for _ in headers) + " |")

            for row in rows:
                lines.append(
                    "| "
                    + " | ".join(
                        _escape_markdown(row.get(header, ""))
                        for header in headers
                    )
                    + " |"
                )
        else:
            lines.append("_No data._")

        lines.append("")

    (output_dir / "paper-ready-static-evaluation-tables.md").write_text(
        "\n".join(lines),
        encoding="utf-8",
    )


def _infer_deployment_artifact_profile(case: dict[str, Any]) -> str:
    applied_rule_ids = set(_get_rule_ids(case, "passed_rule_ids"))
    applied_rule_ids.update(_get_rule_ids(case, "failed_rule_ids"))

    has_compose = any(rule_id.startswith("CMP-") for rule_id in applied_rule_ids)
    has_kubernetes = any(rule_id.startswith("DEP-") for rule_id in applied_rule_ids)

    if has_compose and has_kubernetes:
        return "Docker Compose + Kubernetes manifests"

    if has_compose:
        return "Docker Compose"

    if has_kubernetes:
        return "Kubernetes manifests"

    return "Repository and architecture catalog"


def _infer_exclusion_reason(rule_id: str) -> str:
    normalized_rule_id = rule_id.strip().upper()

    if normalized_rule_id.startswith("CMP-"):
        return "Docker Compose governance not applicable to this case artifact profile."

    if normalized_rule_id.startswith("DEP-"):
        return "Kubernetes governance not applicable to this case artifact profile."

    if normalized_rule_id in {"TOOL-K8S-001", "TOOL-TRIVY-001"}:
        return "Kubernetes/IaC tool governance not applicable to this case artifact profile."

    if normalized_rule_id in {"SEC-002", "SEC-003", "REL-001"}:
        return "Kubernetes-specific runtime/deployment evidence not available for this case."

    if normalized_rule_id == "REPO-002":
        return "Python-specific project metadata rule not applicable to this case technology stack."

    return "Disabled by case-specific applicability configuration."


def _get_project_name(case: dict[str, Any]) -> str:
    return str(case.get("project_name") or Path(str(case.get("config_path"))).stem)


def _get_display_name(project_name: str) -> str:
    return CASE_DISPLAY_NAMES.get(project_name, project_name)


def _get_category_scores(case: dict[str, Any]) -> dict[str, float]:
    raw_category_scores = case.get("category_scores", {})

    if not isinstance(raw_category_scores, dict):
        return {}

    category_scores: dict[str, float] = {}

    for category, score in raw_category_scores.items():
        if isinstance(score, int | float):
            category_scores[str(category)] = float(score)

    return category_scores


def _get_dict(case: dict[str, Any], key: str) -> dict[str, Any]:
    value = case.get(key, {})

    if isinstance(value, dict):
        return value

    return {}


def _get_rule_ids(case: dict[str, Any], key: str) -> list[str]:
    value = case.get(key, [])

    if not isinstance(value, list):
        return []

    return [
        str(item)
        for item in value
    ]


def _join_values(values: list[str]) -> str:
    if not values:
        return "-"

    return ", ".join(values)


def _format_score(value: Any) -> str:
    if isinstance(value, int | float):
        return f"{value:.2f}"

    return "-"


def _escape_markdown(value: str) -> str:
    return value.replace("|", "\\|").replace("\n", " ")


if __name__ == "__main__":
    main()