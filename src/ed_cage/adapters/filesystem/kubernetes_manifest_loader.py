from dataclasses import dataclass
from pathlib import Path
from typing import Any, Sequence

import yaml


@dataclass(frozen=True)
class KubernetesManifest:
    path: Path
    document_index: int
    api_version: str
    kind: str
    name: str
    namespace: str | None
    raw: dict[str, Any]

    @property
    def resource_id(self) -> str:
        namespace_part = f"{self.namespace}/" if self.namespace else ""
        return f"{self.kind}/{namespace_part}{self.name}"


@dataclass(frozen=True)
class KubernetesManifestLoadError:
    path: Path
    message: str


@dataclass(frozen=True)
class KubernetesManifestLoadResult:
    manifests: list[KubernetesManifest]
    errors: list[KubernetesManifestLoadError]
    searched_paths: list[Path]
    candidate_files: list[Path]


class KubernetesManifestLoader:
    def __init__(self, repository_path: Path) -> None:
        self.repository_path = repository_path.resolve()

    def load(
        self,
        manifest_paths: Sequence[str | Path],
        file_patterns: Sequence[str],
    ) -> KubernetesManifestLoadResult:
        searched_paths = [self._resolve_path(path) for path in manifest_paths]
        candidate_files = self._collect_candidate_files(
            searched_paths=searched_paths,
            file_patterns=file_patterns,
        )

        manifests: list[KubernetesManifest] = []
        errors: list[KubernetesManifestLoadError] = []

        for candidate_file in candidate_files:
            try:
                manifests.extend(self._load_file(candidate_file))
            except yaml.YAMLError as exc:
                errors.append(
                    KubernetesManifestLoadError(
                        path=candidate_file,
                        message=f"YAML parse error: {exc}",
                    )
                )
            except OSError as exc:
                errors.append(
                    KubernetesManifestLoadError(
                        path=candidate_file,
                        message=f"File read error: {exc}",
                    )
                )

        return KubernetesManifestLoadResult(
            manifests=manifests,
            errors=errors,
            searched_paths=searched_paths,
            candidate_files=candidate_files,
        )

    def _resolve_path(self, path: str | Path) -> Path:
        raw_path = Path(path)

        if raw_path.is_absolute():
            return raw_path.resolve()

        return (self.repository_path / raw_path).resolve()

    def _collect_candidate_files(
        self,
        searched_paths: Sequence[Path],
        file_patterns: Sequence[str],
    ) -> list[Path]:
        candidate_files: list[Path] = []
        seen: set[Path] = set()

        for searched_path in searched_paths:
            if searched_path.is_file():
                resolved_file = searched_path.resolve()

                if resolved_file not in seen:
                    candidate_files.append(resolved_file)
                    seen.add(resolved_file)

                continue

            if not searched_path.is_dir():
                continue

            for pattern in file_patterns:
                for candidate_file in searched_path.rglob(pattern):
                    resolved_file = candidate_file.resolve()

                    if resolved_file not in seen:
                        candidate_files.append(resolved_file)
                        seen.add(resolved_file)

        return sorted(candidate_files)

    def _load_file(self, path: Path) -> list[KubernetesManifest]:
        content = path.read_text(encoding="utf-8")
        documents = list(yaml.safe_load_all(content))
        manifests: list[KubernetesManifest] = []

        for index, document in enumerate(documents):
            if not self._is_kubernetes_manifest(document):
                continue

            metadata = document.get("metadata", {})

            if not isinstance(metadata, dict):
                metadata = {}

            manifests.append(
                KubernetesManifest(
                    path=path,
                    document_index=index,
                    api_version=str(document.get("apiVersion")),
                    kind=str(document.get("kind")),
                    name=str(metadata.get("name", "unknown")),
                    namespace=(
                        str(metadata["namespace"])
                        if metadata.get("namespace") is not None
                        else None
                    ),
                    raw=document,
                )
            )

        return manifests

    def _is_kubernetes_manifest(self, document: object) -> bool:
        if not isinstance(document, dict):
            return False

        return (
            isinstance(document.get("apiVersion"), str)
            and isinstance(document.get("kind"), str)
            and isinstance(document.get("metadata"), dict)
        )