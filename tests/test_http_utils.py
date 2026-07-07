import httpx

from ed_cage.checks.common.http_utils import (
    build_http_error_attempt,
    build_success_attempt,
    build_url,
    is_successful_attempt,
)


def test_build_url_combines_base_url_and_path() -> None:
    result = build_url(
        base_url="http://127.0.0.1:8080",
        path="/health",
    )

    assert result == "http://127.0.0.1:8080/health"


def test_build_url_handles_trailing_and_leading_slashes() -> None:
    result = build_url(
        base_url="http://127.0.0.1:8080/",
        path="health",
    )

    assert result == "http://127.0.0.1:8080/health"


def test_build_success_attempt_marks_success_when_status_code_matches() -> None:
    attempt = build_success_attempt(
        url="http://127.0.0.1:8080/health",
        status_code=200,
        expected_status_codes={200, 204},
    )

    assert attempt["success"] is True
    assert attempt["expected_status_codes"] == [200, 204]


def test_build_success_attempt_marks_failure_when_status_code_does_not_match() -> None:
    attempt = build_success_attempt(
        url="http://127.0.0.1:8080/health",
        status_code=500,
        expected_status_codes={200, 204},
    )

    assert attempt["success"] is False


def test_build_http_error_attempt() -> None:
    exc = httpx.ConnectError("connection refused")

    attempt = build_http_error_attempt(
        url="http://127.0.0.1:8080/health",
        exc=exc,
    )

    assert attempt["success"] is False
    assert attempt["failure_reason"] == "http_error"
    assert "connection refused" in str(attempt["error"])


def test_is_successful_attempt() -> None:
    assert is_successful_attempt({"success": True}) is True
    assert is_successful_attempt({"success": False}) is False
    assert is_successful_attempt({}) is False