from pathlib import Path

from ed_cage.adapters.filesystem.yaml_service_catalog_provider import YamlServiceCatalogProvider


def test_empty_service_catalog_can_be_loaded(tmp_path: Path) -> None:
    services_file = tmp_path / "services.yaml"
    services_file.write_text("services: []", encoding="utf-8")

    provider = YamlServiceCatalogProvider(services_file)

    services = provider.load_services()

    assert services == []


def test_service_catalog_with_mock_service_can_be_loaded(tmp_path: Path) -> None:
    services_file = tmp_path / "services.yaml"
    services_file.write_text(
        """
services:
  - name: mock-service
    base_url: http://127.0.0.1:8080
    health_endpoints:
      - /health
      - /ready
    tags:
      - local
      - demo
    metadata:
      owner: architecture-team
""",
        encoding="utf-8",
    )

    provider = YamlServiceCatalogProvider(services_file)

    services = provider.load_services()

    assert len(services) == 1
    assert services[0].name == "mock-service"
    assert services[0].base_url == "http://127.0.0.1:8080"
    assert services[0].health_endpoints == ["/health", "/ready"]
    assert services[0].tags == ["local", "demo"]
    assert services[0].metadata["owner"] == "architecture-team"