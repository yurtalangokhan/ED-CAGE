from dataclasses import dataclass
from pathlib import Path
from typing import Any

import yaml


@dataclass(frozen=True)
class ArchitectureCatalogLoadResult:
    path: Path
    exists: bool
    catalog: dict[str, Any]
    errors: list[str]


class ArchitectureCatalogLoader:
    def __init__(self, repository_path: Path) -> None:
        self.repository_path = repository_path

    def load(self, catalog_path: str) -> ArchitectureCatalogLoadResult:
        resolved_path = self._resolve_path(catalog_path)

        if not resolved_path.exists():
            return ArchitectureCatalogLoadResult(
                path=resolved_path,
                exists=False,
                catalog={},
                errors=[f"Architecture catalog does not exist: {resolved_path}"],
            )

        try:
            content = resolved_path.read_text(encoding="utf-8")
            raw_catalog = yaml.safe_load(content) or {}
        except yaml.YAMLError as exc:
            return ArchitectureCatalogLoadResult(
                path=resolved_path,
                exists=True,
                catalog={},
                errors=[f"YAML parse error: {exc}"],
            )
        except OSError as exc:
            return ArchitectureCatalogLoadResult(
                path=resolved_path,
                exists=True,
                catalog={},
                errors=[f"File read error: {exc}"],
            )

        if not isinstance(raw_catalog, dict):
            return ArchitectureCatalogLoadResult(
                path=resolved_path,
                exists=True,
                catalog={},
                errors=["Architecture catalog root must be a YAML object."],
            )

        return ArchitectureCatalogLoadResult(
            path=resolved_path,
            exists=True,
            catalog=raw_catalog,
            errors=[],
        )

    def _resolve_path(self, catalog_path: str) -> Path:
        raw_path = Path(catalog_path)

        if raw_path.is_absolute():
            return raw_path.resolve()

        return (self.repository_path / raw_path).resolve()