import json
import threading
from http.server import BaseHTTPRequestHandler, HTTPServer
from typing import Any

from ed_cage.checks.service.openapi_spec_check import OpenApiSpecCheck
from ed_cage.domain.enums import CheckStatus, Severity
from ed_cage.domain.models import GovernanceRule, ProjectContext, ServiceDefinition


def test_openapi_spec_check_passes_when_service_exposes_valid_openapi_spec() -> None:
    server = _start_test_server(
        routes={
            "/openapi.json": {
                "status_code": 200,
                "payload": {
                    "openapi": "3.0.3",
                    "info": {
                        "title": "Test API",
                        "version": "1.0.0",
                    },
                    "paths": {
                        "/health": {
                            "get": {
                                "responses": {
                                    "200": {
                                        "description": "OK"
                                    }
                                }
                            }
                        }
                    },
                },
            }
        }
    )

    try:
        base_url = f"http://127.0.0.1:{server.server_port}"

        finding = OpenApiSpecCheck().evaluate(
            rule=_build_rule(),
            context=_build_context(base_url),
        )

        assert finding.status == CheckStatus.PASSED
        assert finding.rule_id == "SVC-002"
        assert len(finding.evidence) == 1

        attempts = finding.evidence[0].data["attempts"]
        assert attempts[0]["success"] is True
        assert attempts[0]["spec_version"] == "3.0.3"
        assert attempts[0]["title"] == "Test API"
        assert attempts[0]["path_count"] == 1

    finally:
        server.shutdown()
        server.server_close()


def test_openapi_spec_check_fails_when_endpoint_returns_404() -> None:
    server = _start_test_server(routes={})

    try:
        base_url = f"http://127.0.0.1:{server.server_port}"

        finding = OpenApiSpecCheck().evaluate(
            rule=_build_rule(),
            context=_build_context(base_url),
        )

        assert finding.status == CheckStatus.FAILED
        attempts = finding.evidence[0].data["attempts"]
        assert attempts[0]["status_code"] == 404
        assert attempts[0]["success"] is False
        assert attempts[0]["failure_reason"] == "unexpected_status_code"

    finally:
        server.shutdown()
        server.server_close()


def test_openapi_spec_check_fails_when_json_is_not_openapi_document() -> None:
    server = _start_test_server(
        routes={
            "/openapi.json": {
                "status_code": 200,
                "payload": {
                    "message": "not an openapi document",
                },
            }
        }
    )

    try:
        base_url = f"http://127.0.0.1:{server.server_port}"

        finding = OpenApiSpecCheck().evaluate(
            rule=_build_rule(),
            context=_build_context(base_url),
        )

        assert finding.status == CheckStatus.FAILED
        attempts = finding.evidence[0].data["attempts"]
        assert attempts[0]["success"] is False
        assert attempts[0]["failure_reason"] == "missing_openapi_or_swagger_version"

    finally:
        server.shutdown()
        server.server_close()


def test_openapi_spec_check_is_skipped_when_no_services_defined() -> None:
    finding = OpenApiSpecCheck().evaluate(
        rule=_build_rule(),
        context=ProjectContext(
            project_name="test",
            repository_path=".",
            config_path="configs/ed-cage.yaml",
            services=[],
        ),
    )

    assert finding.status == CheckStatus.SKIPPED


def _build_rule() -> GovernanceRule:
    return GovernanceRule(
        id="SVC-002",
        title="Services must expose an OpenAPI specification",
        category="service",
        severity=Severity.MEDIUM,
        target="service",
        check_type="openapi_spec",
        params={
            "allowed_paths": ["/openapi.json"],
            "expected_status_codes": [200],
            "timeout_seconds": 3,
        },
    )


def _build_context(base_url: str) -> ProjectContext:
    return ProjectContext(
        project_name="test",
        repository_path=".",
        config_path="configs/ed-cage.yaml",
        services=[
            ServiceDefinition(
                name="test-service",
                base_url=base_url,
                openapi_paths=["/openapi.json"],
            )
        ],
    )


class _TestRequestHandler(BaseHTTPRequestHandler):
    routes: dict[str, dict[str, Any]] = {}

    def do_GET(self) -> None:
        route = self.routes.get(self.path)

        if route is None:
            self._send_json(
                status_code=404,
                payload={"error": "Not Found"},
            )
            return

        self._send_json(
            status_code=int(route["status_code"]),
            payload=route["payload"],
        )

    def _send_json(self, status_code: int, payload: object) -> None:
        response_body = json.dumps(payload).encode("utf-8")

        self.send_response(status_code)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(response_body)))
        self.end_headers()
        self.wfile.write(response_body)

    def log_message(self, format: str, *args: object) -> None:
        return


def _start_test_server(routes: dict[str, dict[str, Any]]) -> HTTPServer:
    handler_class = type(
        "ScenarioTestRequestHandler",
        (_TestRequestHandler,),
        {"routes": routes},
    )

    server = HTTPServer(("127.0.0.1", 0), handler_class)
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()

    return server