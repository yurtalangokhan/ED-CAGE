from __future__ import annotations

import argparse
import json
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any

import yaml


EXCLUDED_DIR_NAMES = {
    ".git",
    ".github",
    ".idea",
    ".vscode",
    ".venv",
    "venv",
    "env",
    "__pycache__",
    ".pytest_cache",
    ".mypy_cache",
    ".ruff_cache",
    "node_modules",
    "outputs",
    "dist",
    "build",
    "target",
    ".gradle",
}

KUBERNETES_WORKLOAD_KINDS = {
    "Deployment",
    "StatefulSet",
    "DaemonSet",
    "ReplicaSet",
    "ReplicationController",
    "Job",
    "CronJob",
}

INTERESTING_KINDS = {
    "Deployment",
    "StatefulSet",
    "DaemonSet",
    "Job",
    "CronJob",
    "Service",
    "Ingress",
    "ConfigMap",
    "Secret",
    "Namespace",
    "PersistentVolumeClaim",
    "ServiceAccount",
    "Role",
    "RoleBinding",
    "ClusterRole",
    "ClusterRoleBinding",
    "HorizontalPodAutoscaler",
}


def main() -> None:
    args = _parse_args()

    repo_path = Path(args.repo).resolve()

    if not repo_path.exists():
        raise SystemExit(f"Repository path does not exist: {repo_path}")

    if not repo_path.is_dir():
        raise SystemExit(f"Repository path is not a directory: {repo_path}")

    result = discover_kubernetes_manifest_paths(
        repo_path=repo_path,
        top=args.top,
    )

    print_discovery_summary(result)

    if args.output:
        output_path = Path(args.output).resolve()
        output_path.parent.mkdir(parents=True, exist_ok=True)
        output_path.write_text(
            json.dumps(result, indent=2, ensure_ascii=False),
            encoding="utf-8",
        )
        print()
        print(f"Discovery report written to: {output_path}")


def _parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Discover likely Kubernetes manifest paths in a repository."
    )
    parser.add_argument(
        "--repo",
        required=True,
        help="Repository path to scan.",
    )
    parser.add_argument(
        "--top",
        type=int,
        default=20,
        help="Number of top candidate directories to print.",
    )
    parser.add_argument(
        "--output",
        help="Optional JSON output path.",
    )

    return parser.parse_args()


def discover_kubernetes_manifest_paths(
    repo_path: Path,
    top: int,
) -> dict[str, Any]:
    yaml_files = list(_iter_yaml_files(repo_path))

    candidate_stats: dict[str, dict[str, Any]] = defaultdict(
        lambda: {
            "path": "",
            "file_count": 0,
            "kubernetes_document_count": 0,
            "workload_count": 0,
            "service_count": 0,
            "ingress_count": 0,
            "kind_counts": Counter(),
            "files": [],
            "parse_errors": [],
        }
    )

    total_kubernetes_documents = 0
    total_parse_errors = 0

    for yaml_file in yaml_files:
        relative_parent = _relative_path(yaml_file.parent, repo_path)
        group = candidate_stats[relative_parent]
        group["path"] = relative_parent
        group["file_count"] += 1

        documents, parse_error = _load_yaml_documents(yaml_file)

        if parse_error is not None:
            total_parse_errors += 1
            group["parse_errors"].append(
                {
                    "file": _relative_path(yaml_file, repo_path),
                    "message": parse_error,
                }
            )
            continue

        file_kubernetes_documents: list[dict[str, Any]] = []

        for document_index, document in enumerate(documents):
            if not _is_kubernetes_manifest(document):
                continue

            kind = str(document.get("kind", "")).strip()
            metadata = document.get("metadata", {})

            if not isinstance(metadata, dict):
                metadata = {}

            name = str(metadata.get("name", "unknown")).strip()

            total_kubernetes_documents += 1
            group["kubernetes_document_count"] += 1
            group["kind_counts"][kind] += 1

            if kind in KUBERNETES_WORKLOAD_KINDS:
                group["workload_count"] += 1

            if kind == "Service":
                group["service_count"] += 1

            if kind == "Ingress":
                group["ingress_count"] += 1

            file_kubernetes_documents.append(
                {
                    "document_index": document_index,
                    "kind": kind,
                    "name": name,
                }
            )

        if file_kubernetes_documents:
            group["files"].append(
                {
                    "file": _relative_path(yaml_file, repo_path),
                    "documents": file_kubernetes_documents,
                }
            )

    candidates = [
        _serialize_candidate(candidate)
        for candidate in candidate_stats.values()
        if candidate["kubernetes_document_count"] > 0
    ]

    candidates = sorted(
        candidates,
        key=lambda item: (
            item["kubernetes_document_count"],
            item["workload_count"],
            item["service_count"],
            item["ingress_count"],
            item["file_count"],
        ),
        reverse=True,
    )

    return {
        "repository_path": str(repo_path),
        "yaml_file_count": len(yaml_files),
        "kubernetes_document_count": total_kubernetes_documents,
        "parse_error_count": total_parse_errors,
        "top_candidate_count": min(top, len(candidates)),
        "top_candidates": candidates[:top],
        "all_candidates": candidates,
    }


def _iter_yaml_files(repo_path: Path) -> list[Path]:
    files: list[Path] = []

    for path in repo_path.rglob("*"):
        if not path.is_file():
            continue

        if path.suffix.lower() not in {".yaml", ".yml"}:
            continue

        if _is_excluded(path, repo_path):
            continue

        files.append(path)

    return sorted(files)


def _is_excluded(path: Path, repo_path: Path) -> bool:
    try:
        relative_parts = path.relative_to(repo_path).parts
    except ValueError:
        return True

    return any(part in EXCLUDED_DIR_NAMES for part in relative_parts)


def _load_yaml_documents(path: Path) -> tuple[list[Any], str | None]:
    try:
        content = path.read_text(encoding="utf-8")
        documents = list(yaml.safe_load_all(content))
        return documents, None
    except yaml.YAMLError as exc:
        return [], f"YAML parse error: {exc}"
    except UnicodeDecodeError as exc:
        return [], f"Unicode decode error: {exc}"
    except OSError as exc:
        return [], f"File read error: {exc}"


def _is_kubernetes_manifest(document: object) -> bool:
    if not isinstance(document, dict):
        return False

    api_version = document.get("apiVersion")
    kind = document.get("kind")
    metadata = document.get("metadata")

    if not isinstance(api_version, str):
        return False

    if not isinstance(kind, str):
        return False

    if not isinstance(metadata, dict):
        return False

    return kind in INTERESTING_KINDS or bool(metadata.get("name"))


def _serialize_candidate(candidate: dict[str, Any]) -> dict[str, Any]:
    kind_counts = candidate["kind_counts"]

    return {
        "path": candidate["path"],
        "file_count": candidate["file_count"],
        "kubernetes_document_count": candidate["kubernetes_document_count"],
        "workload_count": candidate["workload_count"],
        "service_count": candidate["service_count"],
        "ingress_count": candidate["ingress_count"],
        "kind_counts": dict(sorted(kind_counts.items())),
        "files": candidate["files"],
        "parse_error_count": len(candidate["parse_errors"]),
        "parse_errors": candidate["parse_errors"],
    }


def _relative_path(path: Path, base_path: Path) -> str:
    try:
        return path.relative_to(base_path).as_posix()
    except ValueError:
        return path.as_posix()


def print_discovery_summary(result: dict[str, Any]) -> None:
    print()
    print("Kubernetes manifest discovery")
    print("=============================")
    print(f"Repository: {result['repository_path']}")
    print(f"YAML files scanned: {result['yaml_file_count']}")
    print(f"Kubernetes documents found: {result['kubernetes_document_count']}")
    print(f"YAML parse errors: {result['parse_error_count']}")
    print()

    candidates = result["top_candidates"]

    if not candidates:
        print("No Kubernetes manifest candidates were found.")
        return

    print("Top candidate paths")
    print("-------------------")

    for index, candidate in enumerate(candidates, start=1):
        print(
            f"{index:02d}. {candidate['path']} | "
            f"docs={candidate['kubernetes_document_count']} | "
            f"files={candidate['file_count']} | "
            f"workloads={candidate['workload_count']} | "
            f"services={candidate['service_count']} | "
            f"ingress={candidate['ingress_count']}"
        )

        kind_counts = candidate["kind_counts"]

        if kind_counts:
            kinds = ", ".join(
                f"{kind}:{count}"
                for kind, count in kind_counts.items()
            )
            print(f"    kinds: {kinds}")

        if candidate["parse_error_count"]:
            print(f"    parse_errors: {candidate['parse_error_count']}")

    print()
    print("Use project-root-relative paths in ED-CAGE config, for example:")
    print("  kubernetes_manifest_paths:")
    print("    - case-studies/<case-name>/<candidate-path>")


if __name__ == "__main__":
    main()