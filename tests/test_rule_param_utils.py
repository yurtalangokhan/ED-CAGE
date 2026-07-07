from ed_cage.checks.common.rule_param_utils import (
    get_float_param,
    get_int_set_param,
    get_string_list_param,
    normalize_relative_path,
)


def test_get_string_list_param_returns_default_when_missing() -> None:
    result = get_string_list_param(
        params={},
        key="allowed_paths",
        default=["/health"],
    )

    assert result == ["/health"]


def test_get_string_list_param_normalizes_relative_paths() -> None:
    result = get_string_list_param(
        params={
            "allowed_paths": [
                "health",
                "/ready",
            ]
        },
        key="allowed_paths",
        default=["/health"],
        normalize_as_relative_path=True,
    )

    assert result == ["/health", "/ready"]


def test_get_int_set_param_returns_configured_values() -> None:
    result = get_int_set_param(
        params={
            "expected_status_codes": [
                200,
                "204",
            ]
        },
        key="expected_status_codes",
        default={200},
    )

    assert result == {200, 204}


def test_get_float_param_returns_configured_value() -> None:
    result = get_float_param(
        params={
            "timeout_seconds": "2.5",
        },
        key="timeout_seconds",
        default=3.0,
    )

    assert result == 2.5


def test_normalize_relative_path_adds_leading_slash() -> None:
    assert normalize_relative_path("health") == "/health"


def test_normalize_relative_path_keeps_existing_leading_slash() -> None:
    assert normalize_relative_path("/health") == "/health"