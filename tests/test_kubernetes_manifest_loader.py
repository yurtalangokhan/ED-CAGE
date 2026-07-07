from pathlib import Path

from ed_cage.adapters.filesystem.kubernetes_manifest_loader import KubernetesManifestLoader


def test_kubernetes_manifest_loader_loads_kubernetes_manifests(tmp_path: Path) -> None:
    manifest_dir = tmp_path / "k8s"
    manifest_dir.mkdir()

    manifest_file = manifest_dir / "deployment.yaml"
    manifest_file.write_text(
        """
apiVersion: apps/v1
kind: Deployment
metadata:
  name: test-service
spec:
  template:
    spec:
      containers:
        - name: app
          image: app:1.0.0
---
apiVersion: v1
kind: Service
metadata:
  name: test-service
spec:
  selector:
    app: test-service
""",
        encoding="utf-8",
    )

    result = KubernetesManifestLoader(tmp_path).load(
        manifest_paths=["k8s"],
        file_patterns=["*.yaml"],
    )

    assert len(result.manifests) == 2
    assert result.manifests[0].kind == "Deployment"
    assert result.manifests[0].name == "test-service"
    assert result.manifests[0].resource_id == "Deployment/test-service"
    assert result.errors == []


def test_kubernetes_manifest_loader_records_yaml_parse_errors(tmp_path: Path) -> None:
    manifest_dir = tmp_path / "k8s"
    manifest_dir.mkdir()

    manifest_file = manifest_dir / "broken.yaml"
    manifest_file.write_text(
        """
apiVersion: apps/v1
kind: Deployment
metadata:
  name: broken
  labels:
    app: broken
    invalid: [not-closed
""",
        encoding="utf-8",
    )

    result = KubernetesManifestLoader(tmp_path).load(
        manifest_paths=["k8s"],
        file_patterns=["*.yaml"],
    )

    assert result.manifests == []
    assert len(result.errors) == 1
    assert "YAML parse error" in result.errors[0].message