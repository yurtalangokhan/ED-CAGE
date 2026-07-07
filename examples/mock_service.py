from __future__ import annotations

import json
from http.server import BaseHTTPRequestHandler, HTTPServer


class MockServiceHandler(BaseHTTPRequestHandler):
    def do_GET(self) -> None:
        if self.path in {"/health", "/ready", "/live"}:
            self._send_json(
                status_code=200,
                payload={"status": "UP"},
            )
            return

        if self.path == "/openapi.json":
            self._send_json(
                status_code=200,
              payload={
                        "openapi": "3.0.3",
                        "info": {
                            "title": "Mock Service API",
                            "version": "1.0.0",
                        },
                        "security": [
                            {
                                "bearerAuth": [],
                            }
                        ],
                        "paths": {
                            "/health": {
                                "get": {
                                    "operationId": "getHealth",
                                    "summary": "Health endpoint",
                                    "responses": {
                                        "200": {
                                            "description": "Service is healthy",
                                            "content": {
                                                "application/json": {
                                                    "schema": {
                                                        "$ref": "#/components/schemas/HealthResponse",
                                                    }
                                                }
                                            },
                                        },
                                        "500": {
                                            "description": "Service is unhealthy",
                                            "content": {
                                                "application/json": {
                                                    "schema": {
                                                        "$ref": "#/components/schemas/ErrorResponse",
                                                    }
                                                }
                                            },
                                        },
                                    },
                                }
                            }
                        },
                        "components": {
                            "securitySchemes": {
                                "bearerAuth": {
                                    "type": "http",
                                    "scheme": "bearer",
                                    "bearerFormat": "JWT",
                                }
                            },
                            "schemas": {
                                "HealthResponse": {
                                    "type": "object",
                                    "properties": {
                                        "status": {
                                            "type": "string",
                                        }
                                    },
                                    "required": [
                                        "status",
                                    ],
                                },
                                "ErrorResponse": {
                                    "type": "object",
                                    "properties": {
                                        "error": {
                                            "type": "string",
                                        }
                                    },
                                    "required": [
                                        "error",
                                    ],
                                },
                            },
                        },
                    }
            )
            return

        if self.path == "/metrics":
            self._send_text(
                status_code=200,
                content_type="text/plain; version=0.0.4; charset=utf-8",
                body="""# HELP http_requests_total Total number of HTTP requests.
# TYPE http_requests_total counter
http_requests_total{method="GET",path="/health",status="200"} 42
http_requests_total{method="GET",path="/orders",status="500"} 2
# HELP http_request_duration_seconds HTTP request duration in seconds.
# TYPE http_request_duration_seconds histogram
http_request_duration_seconds_bucket{method="GET",path="/health",le="0.1"} 40
http_request_duration_seconds_bucket{method="GET",path="/health",le="0.5"} 42
http_request_duration_seconds_sum{method="GET",path="/health"} 1.8
http_request_duration_seconds_count{method="GET",path="/health"} 42
# HELP process_cpu_seconds_total Total user and system CPU time spent in seconds.
# TYPE process_cpu_seconds_total counter
process_cpu_seconds_total 12.5
""",
            )
            return

        self._send_json(
            status_code=404,
            payload={"error": "Not Found"},
        )

    def _send_json(self, status_code: int, payload: dict[str, object]) -> None:
        response_body = json.dumps(payload).encode("utf-8")

        self.send_response(status_code)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(response_body)))
        self.end_headers()
        self.wfile.write(response_body)

    def _send_text(
        self,
        status_code: int,
        content_type: str,
        body: str,
    ) -> None:
        response_body = body.encode("utf-8")

        self.send_response(status_code)
        self.send_header("Content-Type", content_type)
        self.send_header("Content-Length", str(len(response_body)))
        self.end_headers()
        self.wfile.write(response_body)

    def log_message(self, format: str, *args: object) -> None:
        return


def main() -> None:
    server = HTTPServer(("127.0.0.1", 8080), MockServiceHandler)
    print("Mock service is running on http://127.0.0.1:8080")
    print("Available endpoints: /health, /ready, /live, /openapi.json, /metrics")
    server.serve_forever()


if __name__ == "__main__":
    main()