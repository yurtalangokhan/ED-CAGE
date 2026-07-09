from pathlib import Path
import pytest
from ed_cage.config import load_project_config


def test_load_project_config() -> None:
    config = load_project_config(Path("configs/ed-cage.yaml"))

    assert config.project_name == "ed-cage"
    assert config.repository_path.exists()
    assert config.rules_path.exists()


def test_load_project_config_resolves_architecture_catalog_path(tmp_path: Path) -> None:
    config_file = tmp_path / "ed-cage.yaml"
    config_file.write_text(
        """
project_name: test
repository_path: .
rules_path: configs/rules
services_path: configs/services.yaml
actions_path: configs/actions.yaml
scenarios_path: configs/scenarios
output_path: outputs
evidence_registry_path: outputs/evidence/evidence-registry.jsonl
architecture_catalog_path: configs/cases/architecture-catalogs/test-service-architecture.yaml
""",
        encoding="utf-8",
    )

    config = load_project_config(config_file)

    assert config.architecture_catalog_path is not None
    assert config.architecture_catalog_path.is_absolute()
    assert config.architecture_catalog_path.as_posix().endswith(
        "configs/cases/architecture-catalogs/test-service-architecture.yaml"
    )


def test_config_resolves_kubernetes_manifest_paths(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.chdir(tmp_path)

    config_dir = tmp_path / "configs"
    config_dir.mkdir()

    config_path = config_dir / "ed-cage.yaml"
    config_path.write_text(
        """
    project_name: test-project
    repository_path: .
    rules_path: configs/rules
    output_path: outputs/governance-report.json
    evidence_registry_path: outputs/evidence/evidence-registry.jsonl
    kubernetes_manifest_paths:
    - examples/kubernetes
    """,
        encoding="utf-8",
    )

    config = load_project_config(config_path)

    assert len(config.kubernetes_manifest_paths) == 1
    assert (
        config.kubernetes_manifest_paths[0].as_posix().endswith("examples/kubernetes")
    )


def test_load_project_config_reads_scoring_config(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.chdir(tmp_path)

    config_dir = tmp_path / "configs"
    config_dir.mkdir()

    config_path = config_dir / "ed-cage.yaml"
    config_path.write_text(
        """
project_name: test-project
repository_path: .
rules_path: configs/rules
output_path: outputs
evidence_registry_path: outputs/evidence/evidence-registry.jsonl
scoring:
  category_weights:
    security: 2.5
    reliability: 1.5
  maturity_bands:
    - name: Custom Governance
      min_score: 0.0
      max_score: 100.0
""",
        encoding="utf-8",
    )

    config = load_project_config(config_path)

    assert config.scoring.category_weights["security"] == 2.5
    assert config.scoring.category_weights["reliability"] == 1.5
    assert config.scoring.maturity_bands[0].name == "Custom Governance"
