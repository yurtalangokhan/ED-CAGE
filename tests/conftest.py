import json
import threading
from http.server import BaseHTTPRequestHandler, HTTPServer
from typing import Any

import pytest


class HttpTestServer:
    def __init__(self) -> None:
        self.routes: dict[str, dict[str, Any]] = {}
        self.server = self._start_server()

    @property
    def base_url(self) -> str:
        return f"http://127.0.0.1:{self.server.server_port}"

    def set_json_response(
        self,
        path: str,
        status_code: int,
        payload: object,
    ) -> None:
        self.routes[path] = {
            "status_code": status_code,
            "body": json.dumps(payload),
            "content_type": "application/json",
        }

    def set_text_response(
        self,
        path: str,
        status_code: int,
        body: str,
        content_type: str = "text/plain",
    ) -> None:
        self.routes[path] = {
            "status_code": status_code,
            "body": body,
            "content_type": content_type,
        }

    def shutdown(self) -> None:
        self.server.shutdown()
        self.server.server_close()

    def _start_server(self) -> HTTPServer:
        routes = self.routes

        class Handler(BaseHTTPRequestHandler):
            def do_GET(self) -> None:
                route = routes.get(self.path)

                if route is None:
                    self._send_response(
                        status_code=404,
                        body=json.dumps({"error": "Not Found"}),
                        content_type="application/json",
                    )
                    return

                self._send_response(
                    status_code=int(route["status_code"]),
                    body=str(route["body"]),
                    content_type=str(route["content_type"]),
                )

            def _send_response(
                self,
                status_code: int,
                body: str,
                content_type: str,
            ) -> None:
                response_body = body.encode("utf-8")

                self.send_response(status_code)
                self.send_header("Content-Type", content_type)
                self.send_header("Content-Length", str(len(response_body)))
                self.end_headers()
                self.wfile.write(response_body)

            def log_message(self, format: str, *args: object) -> None:
                return

        server = HTTPServer(("127.0.0.1", 0), Handler)
        thread = threading.Thread(target=server.serve_forever, daemon=True)
        thread.start()

        return server


@pytest.fixture
def http_test_server() -> HttpTestServer:
    server = HttpTestServer()

    try:
        yield server
    finally:
        server.shutdown()