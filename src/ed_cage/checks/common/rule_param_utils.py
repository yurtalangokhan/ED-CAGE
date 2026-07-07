from typing import Any


def get_string_list_param(
    params: dict[str, Any],
    key: str,
    default: list[str],
    normalize_as_relative_path: bool = False,
) -> list[str]:
    raw_value = params.get(key, default)

    if not isinstance(raw_value, list) or not raw_value:
        return _normalize_string_list(
            values=default,
            normalize_as_relative_path=normalize_as_relative_path,
        )

    return _normalize_string_list(
        values=[str(item) for item in raw_value],
        normalize_as_relative_path=normalize_as_relative_path,
    )


def get_int_set_param(
    params: dict[str, Any],
    key: str,
    default: set[int],
) -> set[int]:
    raw_value = params.get(key, sorted(default))

    if not isinstance(raw_value, list) or not raw_value:
        return default

    return {int(item) for item in raw_value}


def get_float_param(
    params: dict[str, Any],
    key: str,
    default: float,
) -> float:
    raw_value = params.get(key, default)

    return float(raw_value)


def normalize_relative_path(path: str) -> str:
    return path if path.startswith("/") else f"/{path}"


def _normalize_string_list(
    values: list[str],
    normalize_as_relative_path: bool,
) -> list[str]:
    normalized: list[str] = []

    for value in values:
        if normalize_as_relative_path:
            normalized.append(normalize_relative_path(value))
        else:
            normalized.append(value)

    return normalized