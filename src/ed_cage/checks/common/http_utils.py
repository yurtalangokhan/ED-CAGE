from urllib.parse import urljoin

import httpx


def build_url(base_url: str, path: str) -> str:
    normalized_base_url = f"{base_url.rstrip('/')}/"
    normalized_path = path.lstrip("/")

    return urljoin(normalized_base_url, normalized_path)


def build_success_attempt(
    url: str,
    status_code: int,
    expected_status_codes: set[int],
) -> dict[str, object]:
    return {
        "url": url,
        "status_code": status_code,
        "expected_status_codes": sorted(expected_status_codes),
        "success": status_code in expected_status_codes,
    }


def build_http_error_attempt(
    url: str,
    exc: httpx.HTTPError,
) -> dict[str, object]:
    return {
        "url": url,
        "error": str(exc),
        "success": False,
        "failure_reason": "http_error",
    }


def is_successful_attempt(attempt: dict[str, object]) -> bool:
    return bool(attempt.get("success"))