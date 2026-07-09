from pathlib import Path

import yaml
from pydantic import BaseModel, Field

from ed_cage.domain.models import GovernanceGatePolicy, ScoringConfig
from ed_cage.domain.enums import ExecutionMode


class AppSettings(BaseModel):
    app_name: str = "ed-cage"
    environment: str = "local"


class ProjectConfig(BaseModel):
    project_name: str = "ed-cage"
    repository_path: Path = Path(".")
    rules_path: Path = Path("configs/rules")
    services_path: Path = Path("configs/services.yaml")
    actions_path: Path = Path("configs/actions.yaml")
    scenarios_path: Path = Path("configs/scenarios")
    output_path: Path = Path("outputs")
    evidence_registry_path: Path = Path("outputs/evidence/evidence-registry.jsonl")
    architecture_catalog_path: Path | None = None
    governance_gate: GovernanceGatePolicy = Field(default_factory=GovernanceGatePolicy)
    scoring: ScoringConfig = Field(default_factory=ScoringConfig)
    metadata: dict[str, str] = Field(default_factory=dict)
    kubernetes_manifest_paths: list[Path] = Field(default_factory=list)
    disabled_rule_ids: list[str] = Field(default_factory=list)
    execution_mode: ExecutionMode = ExecutionMode.MIXED
    
    


def load_project_config(config_path: Path) -> ProjectConfig:
    resolved_config_path = config_path.resolve()

    if not resolved_config_path.exists():
        raise FileNotFoundError(f"Config file does not exist: {resolved_config_path}")

    raw_config = yaml.safe_load(resolved_config_path.read_text(encoding="utf-8")) or {}

    if not isinstance(raw_config, dict):
        raise ValueError("Project config root must be a YAML object.")

    config = ProjectConfig(**raw_config)
    project_root = Path.cwd().resolve()

    raw_config["kubernetes_manifest_paths"] = _resolve_path_list(
        project_root=project_root,
        raw_paths=raw_config.get("kubernetes_manifest_paths"),
    )
    resolved_values = {
        "repository_path": _resolve_project_path(project_root, config.repository_path),
        "rules_path": _resolve_project_path(project_root, config.rules_path),
        "services_path": _resolve_project_path(project_root, config.services_path),
        "actions_path": _resolve_project_path(project_root, config.actions_path),
        "scenarios_path": _resolve_project_path(project_root, config.scenarios_path),
        "output_path": _resolve_project_path(project_root, config.output_path),
        "evidence_registry_path": _resolve_project_path(
            project_root,
            config.evidence_registry_path,
        ),
    }

    if config.architecture_catalog_path is not None:
        resolved_values["architecture_catalog_path"] = _resolve_project_path(
            project_root,
            config.architecture_catalog_path,
        )

    return config.model_copy(update=resolved_values)


def _resolve_project_path(project_root: Path, path: Path) -> Path:
    if path.is_absolute():
        return path.resolve()

    return (project_root / path).resolve()


def _resolve_path_list(
    project_root: Path,
    raw_paths: object,
) -> list[Path]:
    if raw_paths is None:
        return []

    if not isinstance(raw_paths, list):
        raise ValueError("Expected a list of paths.")

    resolved_paths: list[Path] = []

    for raw_path in raw_paths:
        path_text = str(raw_path).strip()

        if not path_text:
            continue

        path = Path(path_text)

        if path.is_absolute():
            resolved_paths.append(path.resolve())
        else:
            resolved_paths.append((project_root / path).resolve())

    return resolved_paths
