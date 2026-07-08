from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any

import yaml

from ed_cage.domain.models import GovernanceRule, ProjectContext


DEFAULT_COMPOSE_FILES = [
    "docker-compose.yml",
    "docker-compose.yaml",
    "compose.yml",
    "compose.yaml",
]


@dataclass(frozen=True)
class DockerComposeDocument:
    path: Path
    relative_path: str
    content: dict[str, Any]


@dataclass(frozen=True)
class DockerComposeLoadResult:
    candidate_files: list[Path]
    existing_files: list[Path]
    missing_files: list[Path]
    documents: list[DockerComposeDocument]
    errors: list[dict[str, str]]


def load_docker_compose_files(
    rule: GovernanceRule,
    context: ProjectContext,
) -> DockerComposeLoadResult:
    candidate_files = _resolve_candidate_files(rule=rule, context=context)

    existing_files: list[Path] = []
    missing_files: list[Path] = []
    documents: list[DockerComposeDocument] = []
    errors: list[dict[str, str]] = []

    for candidate_file in candidate_files:
        if not candidate_file.exists() or not candidate_file.is_file():
            missing_files.append(candidate_file)
            continue

        existing_files.append(candidate_file)

        try:
            loaded_content = yaml.safe_load(
                candidate_file.read_text(encoding="utf-8")
            )
        except yaml.YAMLError as exc:
            errors.append(
                {
                    "path": _relative_path(context.repository_path, candidate_file),
                    "reason": "yaml_parse_error",
                    "message": str(exc),
                }
            )
            continue
        except OSError as exc:
            errors.append(
                {
                    "path": _relative_path(context.repository_path, candidate_file),
                    "reason": "file_read_error",
                    "message": str(exc),
                }
            )
            continue

        if not isinstance(loaded_content, dict):
            errors.append(
                {
                    "path": _relative_path(context.repository_path, candidate_file),
                    "reason": "invalid_compose_document",
                    "message": "Docker Compose document must be a YAML mapping.",
                }
            )
            continue

        documents.append(
            DockerComposeDocument(
                path=candidate_file,
                relative_path=_relative_path(context.repository_path, candidate_file),
                content=loaded_content,
            )
        )

    return DockerComposeLoadResult(
        candidate_files=candidate_files,
        existing_files=existing_files,
        missing_files=missing_files,
        documents=documents,
        errors=errors,
    )


def get_compose_services(
    document: DockerComposeDocument,
) -> dict[str, Any]:
    services = document.content.get("services", {})

    if not isinstance(services, dict):
        return {}

    return services


def stringify_paths(
    repository_path: Path,
    paths: list[Path],
) -> list[str]:
    return [
        _relative_path(repository_path, path)
        for path in paths
    ]


def _resolve_candidate_files(
    rule: GovernanceRule,
    context: ProjectContext,
) -> list[Path]:
    raw_compose_files = rule.params.get("compose_files", DEFAULT_COMPOSE_FILES)

    if not isinstance(raw_compose_files, list):
        raw_compose_files = DEFAULT_COMPOSE_FILES

    compose_files = [
        str(compose_file).strip()
        for compose_file in raw_compose_files
        if str(compose_file).strip()
    ]

    if not compose_files:
        compose_files = DEFAULT_COMPOSE_FILES

    resolved_files: list[Path] = []

    for compose_file in compose_files:
        raw_path = Path(compose_file)

        if raw_path.is_absolute():
            resolved_files.append(raw_path.resolve())
        else:
            resolved_files.append((context.repository_path / raw_path).resolve())

    return resolved_files


def _relative_path(repository_path: Path, path: Path) -> str:
    try:
        return str(path.relative_to(repository_path.resolve()))
    except ValueError:
        return str(path)